from pathlib import Path

import pypdf

from product_school_scraper.utils.logger import logger

def verify_pages(pages_dir: str = "pages"):
    """
    Verifies that each subdirectory in `pages_dir` contains:
      1) A valid PDF file (parsable by PyPDF).
      2) A non-empty text file.

    Logs debug information for each file and an info-level summary.
    
    Args:
        pages_dir (str): The path to the directory where pages are saved.
    """
    pages_path = Path(pages_dir)
    if not pages_path.exists() or not pages_path.is_dir():
        logger.error(f"Directory '{pages_dir}' does not exist or is not a directory.")
        return

    logger.info(f"Starting verification of pages in '{pages_dir}'...")

    total_dirs_checked = 0
    empty_text_count = 0
    invalid_pdf_count = 0
    total_pdf_count = 0
    total_txt_count = 0

    # Walk through each subdirectory in 'pages'
    for item in pages_path.iterdir():
        if item.is_dir():
            # Each subdirectory corresponds to a single page or group of pages
            total_dirs_checked += 1
            logger.debug(f"Checking directory: {item.name}")

            # Gather all PDF and TXT files in the current subdirectory
            pdf_files = list(item.glob("*.pdf"))
            txt_files = list(item.glob("*.txt"))

            for pdf_file in pdf_files:
                total_pdf_count += 1
                if not _is_valid_pdf(pdf_file):
                    logger.debug(f"Invalid PDF: {pdf_file}")
                    invalid_pdf_count += 1
                else:
                    logger.debug(f"Valid PDF: {pdf_file}")

            for txt_file in txt_files:
                total_txt_count += 1
                if not _has_content(txt_file):
                    logger.debug(f"Empty or very small text file: {txt_file}")
                    empty_text_count += 1
                else:
                    logger.debug(f"Non-empty text file: {txt_file}")

    # Summary logs
    logger.info("Verification summary:")
    logger.info(f"  Directories checked: {total_dirs_checked}")
    logger.info(f"  PDF files found: {total_pdf_count}, Invalid: {invalid_pdf_count}")
    logger.info(f"  TXT files found: {total_txt_count}, Empty: {empty_text_count}")
    logger.info("Verification complete.")


def _is_valid_pdf(pdf_path: Path) -> bool:
    """
    Check if the PDF can be opened and has at least one page.
    """
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        return False

    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            # If there's an error in parsing, an exception will be raised.
            # Checking if it has at least 1 page:
            num_pages = len(reader.pages)
            return num_pages > 0
    except Exception as e:
        logger.debug(f"PDF read error on '{pdf_path}': {e}")
        return False


def _has_content(txt_path: Path, min_length: int = 10) -> bool:
    """
    Check if a text file is not empty (above `min_length`).
    """
    if not txt_path.exists():
        return False

    content = txt_path.read_text(encoding="utf-8").strip()
    return len(content) >= min_length