from app.core.config import config
from psycopg2   import connect
from contextlib import contextmanager
from pymongo import MongoClient


def _get_conn():
    if not config.POSTGRES_DATABASE_URL:
        raise RuntimeError("Configure POSTGRES_URI ou POSTGRES_LOCAL.")
    return connect(config.POSTGRES_DATABASE_URL)

@contextmanager
def get_cursor():
    conn = _get_conn()
    cur = conn.cursor()
    
    try:
        yield conn, cur
        conn.commit()
    
    except Exception:
        conn.rollback()
        raise
    
    finally:
        cur.close()
        conn.close()


class _MongoDatabase:
    def __init__(self):
        self.client = None
        self.db = None

    def _connect(self):
        if self.db is not None:
            return
        if not config.MONGODB_DATABASE_URL:
            raise RuntimeError("Configure MONGODB_URI ou MONGODB_LOCAL.")
        if not config.MONGODB_DB:
            raise RuntimeError("Configure MONGODB_DB.")
        self.client = MongoClient(config.MONGODB_DATABASE_URL)
        self.db = self.client[config.MONGODB_DB]

    def get_collection(self, name: str):
        self._connect()
        return self.db[name]

mongo_conn = _MongoDatabase()
