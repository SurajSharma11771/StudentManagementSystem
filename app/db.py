import os
import sqlite3

try:
    import psycopg2
except ImportError:
    psycopg2 = None


DATABASE_URL = os.environ.get("DATABASE_URL")
SQLITE_PATH = "data/students.db"


def is_postgres():
    return bool(DATABASE_URL)


def connect():
    if is_postgres():
        if psycopg2 is None:
            raise ImportError("psycopg2 is not installed")
        return psycopg2.connect(DATABASE_URL)

    return sqlite3.connect(SQLITE_PATH)


def placeholder():
    if is_postgres():
        return "%s"
    return "?"