import re
import shutil
from pathlib import Path

from bs4 import BeautifulSoup

from product_school_scraper.utils.logger import logger


def remove_boilerplate_phrases(text: str) -> str:
    """
    Removes known repeated site-wide or marketing/housekeeping text along with surrounding whitespace and trailing punctuation.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text with boilerplate phrases removed.
    """
    boilerplate_phrases = [
        "For individualsFor teamsResourcesConferencesSee upcoming start dates",
        "Subscribe to The Product Blog",
        "By sharing your email, you agree to our Privacy Policy and Terms of Service",
        "Resources you might like",
        "Enjoyed the article? You might like this too",
        "Share this postYour EmailSubscribe",
        "Discover where Product is heading next",
        # Add other boilerplate phrases here as needed
    ]

    # Escape all phrases for regex and join them with '|'
    escaped_phrases = [re.escape(phrase) for phrase in boilerplate_phrases]
    pattern = re.compile(
        r"\s*(" + "|".join(escaped_phrases) + r")[\.\?!]*\s*",
        re.IGNORECASE,
    )

    # Substitute matched phrases with a single space
    cleaned_text = pattern.sub(" ", text)

    # Replace multiple spaces with a single space and strip leading/trailing spaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    logger.debug("Boilerplate phrases removed. Cleaned text: %s", cleaned_text)
    return cleaned_text


def fix_missing_space_after_period(text: str) -> str:
    """
    Inserts a space after a period if it's immediately followed by
    a letter/digit without any space. E.g. "word.Another" -> "word. Another"

    Args:
        text (str): The text to fix.

    Returns:
        str: The text with spaces fixed after periods.
    """
    # Regex explanation:
    # \.(?=[A-Za-z0-9]) means:
    #   - a literal period
    #   - that is followed (lookahead) by any letter or digit
    # We replace with ". " to insert a space.
    fixed_text = re.sub(r"\.(?=[A-Za-z0-9])", ". ", text)
    logger.debug("Fixed missing spaces after periods. Text: %s", fixed_text)
    return fixed_text


def clean_html_content(page_title: str, page_content: BeautifulSoup) -> str:
    """
    Strips out navigation/footer/boilerplate, normalizes whitespace,
    and returns the main textual content.

    Args:
        page_title (str): The title of the page being cleaned.
        page_content (BeautifulSoup): The BeautifulSoup object of the page content.

    Returns:
        str: The cleaned textual content.
    """
    try:
        logger.info(f"Cleaning page: {page_title}")

        # 1) Remove known boilerplate elements
        for nav_tag in page_content.find_all("nav"):
            nav_tag.decompose()
        for footer_tag in page_content.find_all("footer"):
            footer_tag.decompose()
        for header_tag in page_content.find_all("header"):
            header_tag.decompose()

        # 2) Focus on a main/article block if it exists
        main_content = page_content.find("main") or page_content
        raw_text = main_content.get_text()

        # 3) Normalize whitespace (collapse multiple spaces/newlines into one)
        cleaned_text = re.sub(r"\s+", " ", raw_text).strip()

        # 4) Remove repeated phrases
        cleaned_text = remove_boilerplate_phrases(cleaned_text)

        # 5) (Optional) Fix missing space after a period for cleaner text
        cleaned_text = fix_missing_space_after_period(cleaned_text)

        return cleaned_text

    except Exception as e:
        logger.error(f"Error cleaning page '{page_title}': {e}")
        return ""


def sanitize_filename(name: str) -> str:
    # Replace everything not a letter, digit, or underscore with '_'
    sanitized = re.sub(r"[^a-zA-Z0-9_]+", "_", name)
    # Collapse consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Strip leading/trailing underscores and spaces, then lowercase
    sanitized = sanitized.strip("_ ").lower()
    return sanitized


def rename_and_organize_files(
    pages_dir: str = "pages", output_dir: str = "cleaned_pages"
) -> None:
    """
    Rename text files based on their parent directory name and organize them
    in a new directory structure.

    Args:
        pages_dir: Source directory containing the pages
        output_dir: Target directory for renamed files
    """
    pages_path = Path(pages_dir)
    result_path = Path("result")
    output_path = result_path / output_dir

    # Create result and output directories if they don't exist
    result_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)

    # Counter for handling duplicate filenames
    filename_counter = {}

    for page_dir in pages_path.iterdir():
        if not page_dir.is_dir():
            continue

        # Get original directory name and sanitize it
        dir_name = page_dir.name
        sanitized_name = sanitize_filename(dir_name)

        # Look for .txt file in the directory
        txt_files = list(page_dir.glob("*.txt"))

        for txt_file in txt_files:
            # Handle potential duplicate filenames
            if sanitized_name in filename_counter:
                filename_counter[sanitized_name] += 1
                new_filename = (
                    f"{sanitized_name}_{filename_counter[sanitized_name]}.txt"
                )
            else:
                filename_counter[sanitized_name] = 0
                new_filename = f"{sanitized_name}.txt"

            # Copy file to new location with new name
            shutil.copy2(txt_file, output_path / new_filename)
            logger.info(f"Copied and renamed {txt_file} to {new_filename}")


def merge_text_files(
    pages_dir: str = "pages", output_filename: str = "merged_content.txt"
) -> None:
    pages_path = Path(pages_dir)
    result_path = Path("result")
    output_file = result_path / output_filename

    result_path.mkdir(exist_ok=True)

    all_content: list[str] = []

    for page_dir in pages_path.iterdir():
        if not page_dir.is_dir():
            continue

        txt_files = list(page_dir.glob("*.txt"))
        for txt_file in txt_files:
            try:
                with open(txt_file, encoding="utf-8") as f:
                    content = f.read()

                # Your test wants exactly:
                # "=== TestDir ===\n\nContent of file1.\n=== TestDir ===\n\nContent of file2.\n"
                # So let's do:
                header = f"=== {page_dir.name} ===\n\n"
                # Remove the file's *trailing* newline, then add exactly one
                final_chunk = header + content.rstrip("\n") + "\n"
                all_content.append(final_chunk)

                logger.info(f"Read content from {txt_file}")
            except Exception as e:
                logger.error(f"Error reading {txt_file}: {e}")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(all_content))
        logger.info(f"Successfully merged all content into {output_file}")
    except Exception as e:
        logger.error(f"Error writing merged content: {e}")
