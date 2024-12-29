from product_school_scraper.factories.db_factory import DBFactory
from product_school_scraper.utils.logger import logger

def show_all_urls(db_type: str = "sqlite"):
    db = DBFactory.get_db(db_type)
    urls = db.get_all_urls()
    logger.info(f"Total URLs stored: {len(urls)}")
    for url in urls:
        logger.info(url)

def update_url(url_id: int, new_url: str, db_type: str = "sqlite"):
    db = DBFactory.get_db(db_type)
    db.update_url(url_id, new_url)
    logger.info(f"Updated URL [ID={url_id}] => {new_url}")

def delete_url(url_id: int, db_type: str = "sqlite"):
    db = DBFactory.get_db(db_type)
    db.delete_url(url_id)
    logger.info(f"Deleted URL [ID={url_id}]")