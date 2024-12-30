import sqlite3
from pathlib import Path

from product_school_scraper.utils.logger import logger


class SQLiteHandler:
    """
    Simple SQLite wrapper for storing/retrieving sitemap data.
    """

    def __init__(self, db_path: str = "data.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """
        Create the table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Example table for storing sitemaps
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sitemap_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE
                )
            """)
            conn.commit()
            # Table for storing scraping statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_stats (
                    key TEXT PRIMARY KEY,
                    value REAL
                )
            """)
            conn.commit()

    # CREATE
    def create_url(self, url: str):
        """
        Insert a single URL into the database (ignoring duplicates).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO sitemap_urls (url) VALUES (?)", (url,))
            except sqlite3.IntegrityError:
                logger.warning(f"Attempted to insert duplicate URL: {url}")
            conn.commit()

    def store_urls(self, urls: list[str]):
        """
        Insert a list of URLs, ignoring duplicates.
        """
        for url in urls:
            self.create_url(url)

    # READ
    def get_all_urls(self) -> list[str]:
        """
        Retrieve all stored URLs from the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM sitemap_urls")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def get_url_by_id(self, url_id: int) -> str | None:
        """
        Retrieve a single URL by ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM sitemap_urls WHERE id=?", (url_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    # UPDATE
    def update_url(self, url_id: int, new_url: str):
        """
        Update a URL by ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sitemap_urls SET url=? WHERE id=?", (new_url, url_id)
            )
            conn.commit()

    # DELETE
    def delete_url(self, url_id: int):
        """
        Delete a URL by ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sitemap_urls WHERE id=?", (url_id,))
            conn.commit()

    # Additional Methods for scraping_stats
    def get_stat(self, key: str) -> float | None:
        """
        Retrieve a statistical value by key.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM scraping_stats WHERE key=?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def set_stat(self, key: str, value: float) -> None:
        """
        Insert or update a statistical value by key.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scraping_stats (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
                (key, value),
            )
            conn.commit()
