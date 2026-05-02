from .config import DATABASE_URL
from psycopg2 import connect
from contextlib import contextmanager


def get_conn():
    return connect(DATABASE_URL)


@contextmanager
def get_cursor():
    conn = get_conn()
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