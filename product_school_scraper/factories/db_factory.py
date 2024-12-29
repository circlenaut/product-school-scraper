from product_school_scraper.database.sqlite_handler import SQLiteHandler

class DBFactory:
    """
    A simple factory to return DB handler instances.
    In future, you could add other DB types (e.g., PostgresHandler).
    """
    
    @staticmethod
    def get_db(db_type: str):
        if db_type == "sqlite":
            return SQLiteHandler()
        else:
            raise ValueError(f"Unsupported DB type: {db_type}")