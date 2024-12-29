# tests/test_db_factory.py
import pytest
from product_school_scraper.factories.db_factory import DBFactory
from product_school_scraper.database.sqlite_handler import SQLiteHandler

def test_get_sqlite_handler():
    db = DBFactory.get_db("sqlite")
    assert isinstance(db, SQLiteHandler)

def test_get_unsupported_db():
    with pytest.raises(ValueError) as excinfo:
        DBFactory.get_db("postgres")
    assert "Unsupported DB type: postgres" in str(excinfo.value)