from typing import List, Optional

from product_school_scraper.parsing.sitemap_parser import parse_sitemap
from product_school_scraper.utils.helper import format_seconds
from product_school_scraper.utils.logger import logger
from product_school_scraper.services.database_service import get_average_request_time

# Constants
RATE_LIMIT_SECONDS = 10  # Time to wait between requests
DEFAULT_OVERHEAD_SECONDS = 10.0  # Base overhead time
DEFAULT_AVERAGE_REQUEST_TIME = 1.0  # Default average request time in seconds

def estimate_time(sitemap_url: str, directories: Optional[List[str]] = None) -> None:
    """
    Estimate how long a full scrape will take based on average request time,
    rate limit, and overhead.
    """
    logger.info(f"Estimating time for sitemap at: {sitemap_url}")
    urls = parse_sitemap(sitemap_url, directories)
    num_urls = len(urls)

    # Fetch average request time from DB
    average_request_time = get_average_request_time()
    if average_request_time is None:
        average_request_time = DEFAULT_AVERAGE_REQUEST_TIME
        logger.info(f"No average request time found in DB. Using default: {average_request_time:.2f} seconds")
    else:
        logger.info(f"Average request time from DB: {average_request_time:.2f} seconds")

    # Calculate per request time
    # Since the scraper enforces a RATE_LIMIT_SECONDS delay between requests,
    # the total time per request is max(RATE_LIMIT_SECONDS, average_request_time)
    per_request_time = max(RATE_LIMIT_SECONDS, average_request_time)

    # Calculate total time
    total_requests_time = num_urls * per_request_time
    total_time_seconds = total_requests_time + DEFAULT_OVERHEAD_SECONDS

    # Format the total estimated time
    formatted_total_time = format_seconds(total_time_seconds)

    logger.info(f"Number of URLs: {num_urls}")
    logger.info(f"Rate limit: {RATE_LIMIT_SECONDS} seconds per request")
    logger.info(f"Average request time: {average_request_time:.2f} seconds")
    logger.info(f"Per request time (max): {per_request_time:.2f} seconds")
    logger.info(f"Estimated total requests time: {format_seconds(total_requests_time)}")
    logger.info(f"Total estimated time w/ overhead: {formatted_total_time}")