import requests
import time
from typing import List, Optional

import pdfkit
from pathlib import Path
from bs4 import BeautifulSoup

from product_school_scraper.parsing.sitemap_parser import parse_sitemap
from product_school_scraper.factories.db_factory import DBFactory
from product_school_scraper.services.cleaning_service import clean_html_content
from product_school_scraper.services.database_service import set_average_request_time
from product_school_scraper.utils.logger import logger

def list_pages(sitemap_url: str, directories: Optional[List[str]] = None, db_type: str = "sqlite") -> None:
    """
    Parse the sitemap, store the results in DB, and log them.
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
    directories: Optional[List[str]] = None,
    number_of_pages: int | None = None
) -> None:
    """
    Fetch pages from the sitemap, saving each as a .txt or .pdf. 
    Rate-limit: 1 request every 10 seconds (sequential).
    Tracks and stores the average request time upon successful completion.
    """
    logger.info(f"Fetching pages from sitemap: {sitemap_url}")

    urls = parse_sitemap(sitemap_url, directories)
    total_urls = len(urls)
    logger.info(f"Found {total_urls} URLs in the sitemap.")

    if number_of_pages is not None and number_of_pages < total_urls:
        urls = urls[:number_of_pages]
        logger.info(f"Limiting to {len(urls)} pages (per user request).")

    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)

    RATE_LIMIT_SECONDS = 10
    last_request_time = 0.0  

    # Variables to track request durations
    total_request_time = 0.0
    successful_requests = 0

    for index, url in enumerate(urls, start=1):
        # Rate-limit: wait if needed
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
            request_end_time = time.time()

            # Calculate request duration
            request_duration = request_end_time - request_start_time
            total_request_time += request_duration
            successful_requests += 1
            logger.debug(f"Request duration for URL #{index}: {request_duration:.4f} seconds")

            last_request_time = time.time()

            page_content = BeautifulSoup(response.text, "html.parser")
            title_tag = page_content.find("title")
            page_title = title_tag.text.strip() if title_tag else _path_from_url(url)

            safe_dir_name = _sanitize_filename(page_title) or _path_from_url(url)
            output_subdir = pages_dir / safe_dir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            # Build filename
            base_name = f"page_{index:03}"

            # Define file paths
            pdf_path = output_subdir / f"{base_name}.pdf"
            txt_path = output_subdir / f"{base_name}.txt"

            # Clean the page content
            cleaned_page = clean_html_content(page_title, page_content)

            try:
                # Generate and save PDF
                pdfkit.from_url(url, str(pdf_path))
                logger.info(f"Saved PDF: {pdf_path}")

                # Save TXT file
                txt_path.write_text(cleaned_page, encoding="utf-8")
                logger.info(f"Saved TXT: {txt_path}")

            except Exception as e:
                logger.error(f"Failed to save files for {base_name}: {e}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping URL #{index} ({url}): {e}")
        except Exception as exc:
            logger.error(f"Unexpected error for URL #{index} ({url}): {exc}")

    logger.info("fetch_pages completed.")

    # Calculate and store average request time if there were successful requests
    if successful_requests > 0:
        average_request_time = total_request_time / successful_requests
        set_average_request_time(average_request_time)
        logger.info(f"Average request time for this run: {average_request_time:.4f} seconds")
    else:
        logger.warning("No successful requests to calculate average request time.")


def render_pdf_pages(sitemap_url: str, directories: Optional[List[str]] = None, number_of_pages: int | None = None) -> None:
    """
    Similar to fetch_pages but uses pdfkit.from_url() for PDF rendering.
    Rate-limit: 1 request/10s, uses the page title for folder naming.
    """
    logger.info(f"Rendering PDFs directly from URL (wkhtmltopdf) for: {sitemap_url}")

    urls = parse_sitemap(sitemap_url, directories)
    total_urls = len(urls)
    logger.info(f"Found {total_urls} URLs in the sitemap.")

    if number_of_pages is not None and number_of_pages < total_urls:
        urls = urls[:number_of_pages]
        logger.info(f"Limiting to {len(urls)} pages (per user request).")

    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)

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
            # We do a quick GET to get the page title
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            last_request_time = time.time()

            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            page_title = title_tag.text.strip() if title_tag else _path_from_url(url)

            # Use a sanitized folder name
            safe_dir_name = _sanitize_filename(page_title) or _path_from_url(url)
            output_subdir = pages_dir / safe_dir_name
            output_subdir.mkdir(exist_ok=True)

            # Build filename
            file_name = f"page_{str(index).zfill(3)}.pdf"
            output_path = output_subdir / file_name

            logger.info(f"Rendering PDF via from_url for: {url}")
            # Instead of from_string(...)
            pdfkit.from_url(url, str(output_path))
            logger.info(f"Saved PDF: {output_path}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error for URL #{index} ({url}): {e}")
        except Exception as exc:
            logger.error(f"Error generating PDF for URL #{index} ({url}): {exc}")

    logger.info("render_pdf_pages completed.")


def _path_from_url(url: str) -> str:
    no_protocol = url.replace("http://", "").replace("https://", "")
    return no_protocol.replace("/", "-")

def _sanitize_filename(name: str) -> str:
    invalid_chars = ['<','>',':','"','/','\\','|','?','*']
    for ch in invalid_chars:
        name = name.replace(ch, '')
    return name.strip()