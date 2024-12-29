from typing import List, Optional

from product_school_scraper.parsing.sitemap_parser import parse_sitemap
from product_school_scraper.utils.logger import logger

REQUESTS_PER_SECOND = 10
DEFAULT_OVERHEAD_SECONDS = 1.0

def estimate_time(sitemap_url: str, directories: Optional[List[str]] = None) -> None:
    """
    Estimate how long a full scrape will take given 10 requests/sec + overhead.
    """
    logger.info(f"Estimating time for sitemap at: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    num_urls = len(urls)

    best_case_seconds = num_urls / REQUESTS_PER_SECOND
    total_time_seconds = best_case_seconds + DEFAULT_OVERHEAD_SECONDS

    logger.info(f"Number of URLs: {num_urls}")
    logger.info(f"Best-case time: {best_case_seconds:.2f} seconds")
    logger.info(f"Total time w/ overhead: {total_time_seconds:.2f} seconds")