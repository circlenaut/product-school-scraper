# product_school_scraper/services/cleaning_service.py

import re
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
        "Discover where Product is heading next"
        # Add other boilerplate phrases here as needed
    ]

    # Escape all phrases for regex and join them with '|'
    escaped_phrases = [re.escape(phrase) for phrase in boilerplate_phrases]
    pattern = re.compile(
        r'\s*(' + '|'.join(escaped_phrases) + r')[\.\?!]*\s*',
        re.IGNORECASE
    )

    # Substitute matched phrases with a single space
    cleaned_text = pattern.sub(' ', text)

    # Replace multiple spaces with a single space and strip leading/trailing spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

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
        for nav_tag in page_content.find_all('nav'):
            nav_tag.decompose()
        for footer_tag in page_content.find_all('footer'):
            footer_tag.decompose()
        for header_tag in page_content.find_all('header'):
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