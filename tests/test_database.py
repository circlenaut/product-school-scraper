# tests/test_database.py
import pytest
import sqlite3
from pathlib import Path
from product_school_scraper.database.sqlite_handler import SQLiteHandler

@pytest.fixture
def db_handler(tmp_path):
    db_path = tmp_path / "test.db"
    handler = SQLiteHandler(db_path=str(db_path))
    return handler, db_path

def test_init_db(db_handler):
    handler, db_path = db_handler
    assert db_path.exists()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sitemap_urls'")
    table = cursor.fetchone()
    assert table is not None
    conn.close()

def test_create_url(db_handler):
    handler, _ = db_handler
    handler.create_url("https://example.com/page1")
    urls = handler.get_all_urls()
    assert "https://example.com/page1" in urls

def test_create_duplicate_url(db_handler, mocker):
    handler, _ = db_handler
    handler.create_url("https://example.com/page1")
    handler.create_url("https://example.com/page1")  # Duplicate
    urls = handler.get_all_urls()
    assert urls.count("https://example.com/page1") == 1

def test_store_urls(db_handler):
    handler, _ = db_handler
    urls = ["https://example.com/page1", "https://example.com/page2"]
    handler.store_urls(urls)
    stored_urls = handler.get_all_urls()
    assert len(stored_urls) == 2
    assert "https://example.com/page1" in stored_urls
    assert "https://example.com/page2" in stored_urls

def test_get_url_by_id(db_handler):
    handler, _ = db_handler
    handler.create_url("https://example.com/page1")
    url = handler.get_url_by_id(1)
    assert url == "https://example.com/page1"
    non_existent = handler.get_url_by_id(999)
    assert non_existent is None

def test_update_url(db_handler):
    handler, _ = db_handler
    handler.create_url("https://example.com/page1")
    handler.update_url(1, "https://example.com/updated_page1")
    url = handler.get_url_by_id(1)
    assert url == "https://example.com/updated_page1"

def test_delete_url(db_handler):
    handler, _ = db_handler
    handler.create_url("https://example.com/page1")
    handler.delete_url(1)
    url = handler.get_url_by_id(1)
    assert url is None