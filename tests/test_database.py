import logging
import sqlite3
from unittest.mock import MagicMock, Mock

import pytest

from product_school_scraper.database.sqlite_handler import SQLiteHandler


@pytest.fixture
def db_handler(tmp_path):
    db_path = tmp_path / "test.db"
    handler = SQLiteHandler(db_path=str(db_path))
    return handler


def test_init_db(db_handler):
    handler = db_handler
    db_path = handler.db_path
    assert db_path.exists()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sitemap_urls'"
    )
    table = cursor.fetchone()
    assert table is not None
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='scraping_stats'"
    )
    stats_table = cursor.fetchone()
    assert stats_table is not None
    conn.close()


def test_create_url(db_handler):
    handler = db_handler
    handler.create_url("https://example.com/page1")
    urls = handler.get_all_urls()
    assert "https://example.com/page1" in urls


def test_create_duplicate_url(db_handler, caplog):
    handler = db_handler
    # Create a URL
    handler.create_url("https://example.com/page1")
    # Attempt to create the same URL again (should be ignored)
    with caplog.at_level(logging.WARNING):
        handler.create_url("https://example.com/page1")

    # Assert that the warning was logged
    assert "Attempted to insert duplicate URL: https://example.com/page1" in caplog.text

    # Ensure only one instance of the URL exists
    urls = handler.get_all_urls()
    assert urls.count("https://example.com/page1") == 1


def test_store_urls(db_handler):
    handler = db_handler
    urls = ["https://example.com/page1", "https://example.com/page2"]
    handler.store_urls(urls)
    stored_urls = handler.get_all_urls()
    assert len(stored_urls) == 2
    assert "https://example.com/page1" in stored_urls
    assert "https://example.com/page2" in stored_urls


def test_get_url_by_id(db_handler):
    handler = db_handler
    handler.create_url("https://example.com/page1")
    url = handler.get_url_by_id(1)
    assert url == "https://example.com/page1"
    non_existent = handler.get_url_by_id(999)
    assert non_existent is None


def test_update_url(db_handler):
    handler = db_handler
    handler.create_url("https://example.com/page1")
    handler.update_url(1, "https://example.com/updated_page1")
    url = handler.get_url_by_id(1)
    assert url == "https://example.com/updated_page1"


def test_delete_url(db_handler):
    handler = db_handler
    handler.create_url("https://example.com/page1")
    handler.delete_url(1)
    url = handler.get_url_by_id(1)
    assert url is None


def test_get_stat(db_handler):
    handler = db_handler
    handler.set_stat("average_request_time", 2.5)
    stat = handler.get_stat("average_request_time")
    assert stat == 2.5


def test_set_stat_update(db_handler):
    handler = db_handler
    handler.set_stat("average_request_time", 2.5)
    handler.set_stat("average_request_time", 3.5)
    stat = handler.get_stat("average_request_time")
    assert stat == 3.5


def test_set_stat_exception(mocker, db_handler):
    handler = db_handler

    # Create a MagicMock for connection, supporting context manager
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = (
        mock_conn  # Ensure context manager protocol is supported
    )

    # Create a Mock for cursor
    mock_cursor = Mock()
    mock_cursor.execute.side_effect = (
        sqlite3.IntegrityError
    )  # Set side effect to raise IntegrityError

    # Set cursor() to return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Patch 'sqlite3.connect' in 'sqlite_handler.py' to return the mock connection
    mocker.patch(
        "product_school_scraper.database.sqlite_handler.sqlite3.connect",
        return_value=mock_conn,
    )

    # Attempt to set a stat that causes IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        handler.set_stat("invalid_key", 1.0)

    # Assert that execute was called (without checking the exact SQL string)
    mock_cursor.execute.assert_called_once()
