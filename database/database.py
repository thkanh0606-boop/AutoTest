import sqlite3
from pathlib import Path


# =========================================================
# DATABASE CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "autotest.db"


# =========================================================
# GET CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# INIT DATABASE
# =========================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    # =====================================================
    # WEBSITE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL
        )
    """)

    # =====================================================
    # PAGE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            FOREIGN KEY (website_id)
                REFERENCES websites(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    connection.close()