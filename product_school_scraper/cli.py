import logging

import fire

from product_school_scraper.utils.logger import logger
from product_school_scraper.services.scraping_service import (
    list_pages,
    fetch_pages,
    render_pdf_pages
)
from product_school_scraper.services.estimate_service import estimate_time
from product_school_scraper.services.database_service import (
    show_all_urls,
    update_url,
    delete_url
)
from product_school_scraper.services.verification_service import verify_pages

DEFAULT_SITEMAP_URL = "https://productschool.com/sitemap.xml"
DEFAULT_DIRECTORIES = ["/blog/"]

class ScraperCLI:
    def list_pages(self, sitemap_url: str = None, directory: str = None):
        url_to_use = sitemap_url or DEFAULT_SITEMAP_URL
        directories_to_use = [directory] if directory else DEFAULT_DIRECTORIES
        list_pages(url_to_use, directories_to_use)

    def estimate_time(self, sitemap_url: str = None, directory: str = None):
        url_to_use = sitemap_url or DEFAULT_SITEMAP_URL
        directories_to_use = [directory] if directory else DEFAULT_DIRECTORIES
        print(f'dirs: {directories_to_use}')
        estimate_time(url_to_use, directories_to_use)

    def fetch_pages(self, sitemap_url: str = None, directory: str = None, number_of_pages: int = None):
        url_to_use = sitemap_url or DEFAULT_SITEMAP_URL
        directories_to_use = [directory] if directory else DEFAULT_DIRECTORIES
        fetch_pages(url_to_use, directories_to_use, number_of_pages)

    def render_pdf(self, sitemap_url: str = None, directory: str = None, number_of_pages: int = None):
        """
        Render PDFs directly with wkhtmltopdf from each URL.
        
        Usage:
          poetry run product-school-scraper scraper render_pdf
          poetry run product-school-scraper scraper render_pdf --sitemap_url https://example.com/sitemap.xml
          poetry run product-school-scraper scraper render_pdf --number_of_pages 5
        """
        url_to_use = sitemap_url or DEFAULT_SITEMAP_URL
        directories_to_use = [directory] if directory else DEFAULT_DIRECTORIES
        render_pdf_pages(url_to_use, directories_to_use, number_of_pages)

    def verify(self, pages_dir: str = "pages"):
            """
            Verify that the downloaded pages are valid (PDF + text).
            
            Usage:
            poetry run product-school-scraper scraper verify
            poetry run product-school-scraper scraper verify --pages_dir some_other_directory
            """
            verify_pages(pages_dir)

class DatabaseCLI:
    def show_urls(self):
        show_all_urls()

    def update_url(self, url_id: int, new_url: str):
        update_url(url_id, new_url)

    def delete_url(self, url_id: int):
        delete_url(url_id)

class RootCLI:
    """
    The top-level CLI class. Fire will instantiate this class, 
    passing `verbose=True` if --verbose is given.
    """
    def __init__(self, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                handler.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            for handler in logger.handlers:
                handler.setLevel(logging.INFO)

        # Subcommands
        self.scraper = ScraperCLI()
        self.database = DatabaseCLI()

def run_cli():
    fire.Fire(RootCLI)