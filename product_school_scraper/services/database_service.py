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


def get_average_request_time(db_type: str = "sqlite") -> float | None:
    """
    Retrieve the average request time from the database.
    """
    db = DBFactory.get_db(db_type)
    avg_time = db.get_stat("average_request_time")
    if avg_time is not None:
        logger.debug(f"Retrieved average_request_time from DB: {avg_time:.4f} seconds")
    else:
        logger.debug("No average_request_time found in DB.")
    return avg_time


def set_average_request_time(avg_time: float, db_type: str = "sqlite") -> None:
    """
    Store the average request time in the database.
    """
    db = DBFactory.get_db(db_type)
    db.set_stat("average_request_time", avg_time)
    logger.debug(f"Set average_request_time in DB to: {avg_time:.4f} seconds")
