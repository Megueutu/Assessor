from app.core.config import config
from psycopg2   import connect
from contextlib import contextmanager
from pymongo import MongoClient


def _get_conn():
    return connect(config.PSQL_DATABASE_URL)

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


class MongoDatabase:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URI)
        self.db = self.client.get_database()

    def get_collection(self, name: str):
        return self.db[name]


mongo_conn = MongoDatabase()