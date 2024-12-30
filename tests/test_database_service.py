import pytest

from product_school_scraper.database.sqlite_handler import SQLiteHandler
from product_school_scraper.services.database_service import (
    delete_url,
    get_average_request_time,
    set_average_request_time,
    show_all_urls,
    update_url,
)


@pytest.fixture
def db_handler(tmp_path):
    db_path = tmp_path / "test.db"
    handler = SQLiteHandler(db_path=str(db_path))
    handler.store_urls(["https://example.com/page1", "https://example.com/page2"])
    return handler


def test_show_all_urls(db_handler, caplog, mocker):
    handler = db_handler
    # Patch DBFactory.get_db within database_service.py to return the handler
    mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=handler,
    )
    show_all_urls()
    assert "Total URLs stored: 2" in caplog.text
    assert "https://example.com/page1" in caplog.text
    assert "https://example.com/page2" in caplog.text


def test_update_url(db_handler, caplog, mocker):
    handler = db_handler
    # Patch DBFactory.get_db within database_service.py to return the handler
    mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=handler,
    )
    update_url(1, "https://example.com/updated_page1")
    assert handler.get_url_by_id(1) == "https://example.com/updated_page1"
    assert "Updated URL [ID=1] => https://example.com/updated_page1" in caplog.text


def test_delete_url(db_handler, caplog, mocker):
    handler = db_handler
    # Patch DBFactory.get_db within database_service.py to return the handler
    mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=handler,
    )
    delete_url(1)
    assert handler.get_url_by_id(1) is None
    assert "Deleted URL [ID=1]" in caplog.text


def test_get_average_request_time_none(mocker):
    mock_db = mocker.Mock()
    mock_db.get_stat.return_value = None
    # Correctly patch DBFactory.get_db within database_service.py
    mock_factory = mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=mock_db,
    )
    # Correctly patch logger.debug within database_service.py
    mock_logger = mocker.patch(
        "product_school_scraper.services.database_service.logger.debug",
    )

    result = get_average_request_time()
    mock_factory.assert_called_once_with("sqlite")
    mock_db.get_stat.assert_called_once_with("average_request_time")
    mock_logger.assert_called_once_with("No average_request_time found in DB.")
    assert result is None


def test_get_average_request_time_exists(mocker):
    mock_db = mocker.Mock()
    mock_db.get_stat.return_value = 0.75
    # Correctly patch DBFactory.get_db within database_service.py
    mock_factory = mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=mock_db,
    )
    # Correctly patch logger.debug within database_service.py
    mock_logger = mocker.patch(
        "product_school_scraper.services.database_service.logger.debug",
    )

    result = get_average_request_time()
    mock_factory.assert_called_once_with("sqlite")
    mock_db.get_stat.assert_called_once_with("average_request_time")
    mock_logger.assert_called_once_with(
        "Retrieved average_request_time from DB: 0.7500 seconds"
    )
    assert result == 0.75


def test_set_average_request_time(mocker):
    mock_db = mocker.Mock()
    # Correctly patch DBFactory.get_db within database_service.py
    mock_factory = mocker.patch(
        "product_school_scraper.services.database_service.DBFactory.get_db",
        return_value=mock_db,
    )
    # Correctly patch logger.debug within database_service.py
    mock_logger = mocker.patch(
        "product_school_scraper.services.database_service.logger.debug",
    )

    set_average_request_time(1.2345)
    mock_factory.assert_called_once_with("sqlite")
    mock_db.set_stat.assert_called_once_with("average_request_time", 1.2345)
    mock_logger.assert_called_once_with(
        "Set average_request_time in DB to: 1.2345 seconds"
    )
