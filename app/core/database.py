from .config import config
from psycopg2 import connect
from contextlib import contextmanager


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