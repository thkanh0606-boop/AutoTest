import os
import sqlite3
from datetime import datetime
from typing import Dict, Iterable

from core.config import Config


class TestResultRepository:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.path.join(Config.BASE_DIR, "autotest.sqlite3")
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module TEXT NOT NULL,
                    page_key TEXT NOT NULL,
                    page_name TEXT NOT NULL,
                    element_key TEXT NOT NULL,
                    element_name TEXT NOT NULL,
                    locator_type TEXT NOT NULL,
                    locator_value TEXT NOT NULL,
                    expected TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_case_id INTEGER,
                    module TEXT NOT NULL,
                    page_key TEXT NOT NULL,
                    page_name TEXT NOT NULL,
                    element_key TEXT NOT NULL,
                    element_name TEXT NOT NULL,
                    expected TEXT NOT NULL,
                    actual TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_case_and_result(self, payload: Dict[str, str]) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO test_cases
                    (module, page_key, page_name, element_key, element_name,
                     locator_type, locator_value, expected, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["module"],
                    payload["page_key"],
                    payload["page_name"],
                    payload["element_key"],
                    payload["element_name"],
                    payload["locator_type"],
                    payload["locator_value"],
                    payload["expected"],
                    now,
                ),
            )
            case_id = cursor.lastrowid
            connection.execute(
                """
                INSERT INTO test_results
                    (test_case_id, module, page_key, page_name, element_key,
                     element_name, expected, actual, status, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    payload["module"],
                    payload["page_key"],
                    payload["page_name"],
                    payload["element_key"],
                    payload["element_name"],
                    payload["expected"],
                    payload["actual"],
                    payload["status"],
                    payload["message"],
                    now,
                ),
            )
        return case_id

    def latest_results(self, module: str, limit: int = 10):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT page_name, element_name, expected, actual, status, message, created_at
                FROM test_results
                WHERE module = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (module, limit),
            ).fetchall()
        return [dict(row) for row in rows]
