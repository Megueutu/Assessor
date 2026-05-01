from .config import DATABASE_URL
from psycopg2 import connect

def get_conn():
    return connect(DATABASE_URL)