# tests/test_database_service.py
import pytest
from product_school_scraper.services.database_service import (
    show_all_urls,
    update_url,
    delete_url
)
from product_school_scraper.factories.db_factory import DBFactory
from product_school_scraper.database.sqlite_handler import SQLiteHandler
from unittest.mock import Mock

@pytest.fixture
def db_handler(tmp_path, mocker):
    db_path = tmp_path / "test.db"
    handler = SQLiteHandler(db_path=str(db_path))
    handler.store_urls(["https://example.com/page1", "https://example.com/page2"])
    return handler

def test_show_all_urls(db_handler, caplog, mocker):
    handler = db_handler
    mocker.patch('product_school_scraper.factories.db_factory.DBFactory.get_db', return_value=handler)
    show_all_urls()
    assert "Total URLs stored: 2" in caplog.text
    assert "https://example.com/page1" in caplog.text
    assert "https://example.com/page2" in caplog.text

def test_update_url(db_handler, caplog, mocker):
    handler = db_handler
    mocker.patch('product_school_scraper.factories.db_factory.DBFactory.get_db', return_value=handler)
    update_url(1, "https://example.com/updated_page1")
    assert handler.get_url_by_id(1) == "https://example.com/updated_page1"
    assert "Updated URL [ID=1] => https://example.com/updated_page1" in caplog.text

def test_delete_url(db_handler, caplog, mocker):
    handler = db_handler
    mocker.patch('product_school_scraper.factories.db_factory.DBFactory.get_db', return_value=handler)
    delete_url(1)
    assert handler.get_url_by_id(1) is None
    assert "Deleted URL [ID=1]" in caplog.text