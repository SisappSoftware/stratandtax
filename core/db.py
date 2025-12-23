import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "database.db")


def get_db():
    """
    Devuelve una conexión SQLite con row_factory dict-like
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
