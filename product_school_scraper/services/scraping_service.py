import time
from pathlib import Path
from urllib.parse import urlparse

import pdfkit
import requests
from bs4 import BeautifulSoup

from product_school_scraper.factories.db_factory import DBFactory
from product_school_scraper.parsing.sitemap_parser import parse_sitemap
from product_school_scraper.services.cleaning_service import clean_html_content
from product_school_scraper.services.database_service import set_average_request_time
from product_school_scraper.utils.logger import logger


def _path_from_url(url: str) -> str:
    """
    Convert a URL to a filesystem-friendly string.
    e.g. "https://example.com/path/to/page"
         -> "example.com-path-to-page"
    """
    no_protocol = url.replace("http://", "").replace("https://", "")
    return no_protocol.replace("/", "-")


def _sanitize_filename(name: str) -> str:
    """
    Remove invalid characters (and extra spaces) to produce a filesystem-safe filename.
    E.g. "Valid_Name-123" -> "Valid_Name123"
         "Special!@#$%^&*()Chars" -> "SpecialChars"
    """
    invalid_chars = [
        "<",
        ">",
        ":",
        '"',
        "/",
        "\\",
        "|",
        "?",
        "*",
        "-",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "(",
        ")",
    ]
    for ch in invalid_chars:
        name = name.replace(ch, "")
    # Remove all whitespace
    name = name.strip().replace(" ", "")
    return name


def list_directories(sitemap_url: str) -> list[str] | None:
    """
    Parse the sitemap and list all unique top-level directories.
    Logs an error if parsing fails, returning None.
    """
    logger.info(f"Analyzing directories in sitemap: {sitemap_url}")
    try:
        urls = parse_sitemap(sitemap_url, directories=None)
    except Exception as e:
        logger.error(f"Error parsing sitemap: {e}")
        return None

    directories = set()
    for url in urls:
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        if path:
            top_dir = path.split("/")[0]
            if top_dir:
                directories.add(f"/{top_dir}/")

    sorted_dirs = sorted(directories)
    logger.info(f"Found {len(sorted_dirs)} unique top-level directories:")
    for directory in sorted_dirs:
        logger.info(f"Directory: {directory}")
    return sorted_dirs


def list_pages(
    sitemap_url: str, directories: list[str] | None = None, db_type: str = "sqlite"
) -> None:
    """
    Parse the sitemap, store the results in the chosen DB, and log them.
    """
    logger.info(f"Scraping sitemap at: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    logger.info(f"Found {len(urls)} URLs.")

    db = DBFactory.get_db(db_type)
    db.store_urls(urls)

    for url in urls:
        logger.info(f"URL: {url}")


def fetch_pages(
    sitemap_url: str,
    directories: list[str] | None = None,
    number_of_pages: int | None = None,
) -> None:
    """
    Fetch pages from the sitemap, saving each as .txt and .pdf.
    Sleeps 10s between requests, logs errors, and updates average request time.
    """
    logger.info(f"Fetching pages from sitemap: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    total_urls = len(urls)
    logger.info(f"Found {total_urls} URLs in the sitemap.")

    if number_of_pages is not None and number_of_pages < total_urls:
        urls = urls[:number_of_pages]
        logger.info(f"Limiting to {len(urls)} pages (per user request).")

    pages_dir = Path("pages")
    pages_dir.mkdir(parents=True, exist_ok=True)

    RATE_LIMIT_SECONDS = 10
    last_request_time = 0.0
    total_request_time = 0.0
    successful_requests = 0

    for index, url in enumerate(urls, start=1):
        # Rate-limit
        elapsed = time.time() - last_request_time
        sleep_time = RATE_LIMIT_SECONDS - elapsed
        if sleep_time > 0:
            logger.info(f"Sleeping {sleep_time:.2f}s before the next request ...")
            time.sleep(sleep_time)

        try:
            logger.info(f"Scraping URL #{index}: {url}")
            request_start_time = time.time()
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            request_duration = time.time() - request_start_time

            total_request_time += request_duration
            successful_requests += 1
            last_request_time = time.time()

            page_content = BeautifulSoup(response.text, "html.parser")
            title_tag = page_content.find("title")
            page_title = title_tag.text.strip() if title_tag else _path_from_url(url)

            safe_dir_name = _sanitize_filename(page_title) or _path_from_url(url)
            output_subdir = pages_dir / safe_dir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            base_name = f"page_{index:03}"
            pdf_path = output_subdir / f"{base_name}.pdf"
            txt_path = output_subdir / f"{base_name}.txt"

            # Clean + generate files
            try:
                cleaned_page = clean_html_content(page_title, page_content)
                pdfkit.from_url(url, str(pdf_path))
                logger.info(f"Saved PDF: {pdf_path}")

                txt_path.write_text(cleaned_page, encoding="utf-8")
                logger.info(f"Saved TXT: {txt_path}")
            except Exception as e:
                logger.error(f"Failed to save files for {base_name}: {e}")

        except requests.exceptions.RequestException as req_exc:
            logger.error(f"Error scraping URL #{index} ({url}): {req_exc}")
        except Exception as exc:
            logger.error(f"Unexpected error for URL #{index} ({url}): {exc}")

    logger.info("fetch_pages completed.")

    # Update average request time
    if successful_requests > 0:
        avg_time = total_request_time / successful_requests
        set_average_request_time(avg_time)
        logger.info(f"Average request time for this run: {avg_time:.4f} seconds")
    else:
        logger.warning("No successful requests to calculate average request time.")


def render_pdf_pages(
    sitemap_url: str,
    directories: list[str] | None = None,
    number_of_pages: int | None = None,
) -> None:
    """
    Fetch URLs from the sitemap, quickly get the page title, then render PDF directly via pdfkit.
    Sleeps 10s between requests, logs errors, but doesn't save .txt.
    """
    logger.info(f"Rendering PDFs directly from URL (wkhtmltopdf) for: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    total_urls = len(urls)
    logger.info(f"Found {total_urls} URLs in the sitemap.")

    if number_of_pages is not None and number_of_pages < total_urls:
        urls = urls[:number_of_pages]
        logger.info(f"Limiting to {len(urls)} pages (per user request).")

    pages_dir = Path("pages")
    pages_dir.mkdir(parents=True, exist_ok=True)

    RATE_LIMIT_SECONDS = 10
    last_request_time = 0.0

    for index, url in enumerate(urls, start=1):
        # Rate-limit
        elapsed = time.time() - last_request_time
        sleep_time = RATE_LIMIT_SECONDS - elapsed
        if sleep_time > 0:
            logger.info(f"Sleeping {sleep_time:.2f}s before the next request ...")
            time.sleep(sleep_time)

        try:
            logger.info(f"Scraping title for URL #{index}: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            last_request_time = time.time()

            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            page_title = title_tag.text.strip() if title_tag else _path_from_url(url)

            safe_dir_name = _sanitize_filename(page_title) or _path_from_url(url)
            output_subdir = pages_dir / safe_dir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            file_name = f"page_{str(index).zfill(3)}.pdf"
            output_path = output_subdir / file_name

            logger.info(f"Rendering PDF via from_url for: {url}")
            pdfkit.from_url(url, str(output_path))
            logger.info(f"Saved PDF: {output_path}")

        except requests.exceptions.RequestException as req_exc:
            logger.error(f"Network error for URL #{index} ({url}): {req_exc}")
        except Exception as exc:
            logger.error(f"Error generating PDF for URL #{index} ({url}): {exc}")

    logger.info("render_pdf_pages completed.")


def fetch_page(
    sitemap_url: str, directories: list[str] | None = None, target_page_number: int = 1
) -> None:
    """
    Fetch and process a single page by index in the sitemap.
    Raises RuntimeError on major failures (pdfkit, cleaning, or request errors).
    """
    logger.info(f"Fetching page {target_page_number} from sitemap: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    total_urls = len(urls)

    if not 1 <= target_page_number <= total_urls:
        error_msg = f"Invalid page number {target_page_number}. Must be between 1 and {total_urls}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    target_url = urls[target_page_number - 1]
    logger.info(f"Found target URL: {target_url}")

    pages_dir = Path("pages")
    pages_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Scraping URL: {target_url}")
        start_t = time.time()
        response = requests.get(target_url, timeout=15)
        response.raise_for_status()
        req_duration = time.time() - start_t

        page_content = BeautifulSoup(response.text, "html.parser")
        title_tag = page_content.find("title")
        page_title = title_tag.text.strip() if title_tag else _path_from_url(target_url)

        safe_dir_name = _sanitize_filename(page_title) or _path_from_url(target_url)
        output_subdir = pages_dir / safe_dir_name
        output_subdir.mkdir(parents=True, exist_ok=True)

        base_name = f"page_{target_page_number:03}"
        pdf_path = output_subdir / f"{base_name}.pdf"
        txt_path = output_subdir / f"{base_name}.txt"

        try:
            cleaned_page = clean_html_content(page_title, page_content)
            pdfkit.from_url(target_url, str(pdf_path))
            logger.info(f"Saved PDF: {pdf_path}")

            txt_path.write_text(cleaned_page, encoding="utf-8")
            logger.info(f"Saved TXT: {txt_path}")
        except Exception as e:
            err_msg = f"Failed to save files for {base_name}: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        set_average_request_time(req_duration)
        logger.info(f"Request duration: {req_duration:.4f} seconds")

    except requests.exceptions.RequestException as req_exc:
        error_msg = f"Error scraping URL ({target_url}): {req_exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError:
        # Already logged
        raise
    except Exception as exc:
        error_msg = f"Unexpected error for URL ({target_url}): {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info("fetch_page completed successfully.")
