import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from core.config import Config


class TestResultRepository:
    __test__ = False

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.path.join(Config.BASE_DIR, "autotest.sqlite3")
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
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
                CREATE TABLE IF NOT EXISTS test_runs (
                    run_id TEXT PRIMARY KEY,
                    module TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total INTEGER NOT NULL DEFAULT 0,
                    passed INTEGER NOT NULL DEFAULT 0,
                    failed INTEGER NOT NULL DEFAULT 0,
                    error INTEGER NOT NULL DEFAULT 0,
                    skipped INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    message TEXT
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
            self._apply_migrations(connection)

    def _column_names(self, connection: sqlite3.Connection, table_name: str) -> set:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {row[1] for row in rows}

    def _add_column_if_missing(self, connection: sqlite3.Connection, table_name: str, column_name: str, definition: str):
        if column_name not in self._column_names(connection, table_name):
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _apply_migrations(self, connection: sqlite3.Connection):
        self._add_column_if_missing(connection, "test_cases", "case_id", "TEXT")
        self._add_column_if_missing(connection, "test_cases", "steps", "TEXT")
        self._add_column_if_missing(connection, "test_cases", "expected_result", "TEXT")
        self._add_column_if_missing(connection, "test_cases", "updated_at", "TEXT")

        self._add_column_if_missing(connection, "test_results", "run_id", "TEXT")
        self._add_column_if_missing(connection, "test_results", "case_id", "TEXT")
        self._add_column_if_missing(connection, "test_results", "steps", "TEXT")
        self._add_column_if_missing(connection, "test_results", "expected_result", "TEXT")
        self._add_column_if_missing(connection, "test_results", "actual_result", "TEXT")
        self._add_column_if_missing(connection, "test_results", "error_message", "TEXT")
        self._add_column_if_missing(connection, "test_results", "screenshot_path", "TEXT")

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_test_cases_case_id_unique
            ON test_cases(case_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_run_id
            ON test_results(run_id)
            """
        )

    def save_case_and_result(self, payload: Dict[str, str]) -> int:
        run_id = payload.get("run_id") or f"{payload.get('module', 'test')}-{uuid.uuid4().hex[:12]}"
        contract_case_id = payload.get("case_id") or (
            f"{payload.get('module', 'test')}:{payload.get('page_key', '')}:{payload.get('element_key', '')}"
        )
        expected_result = payload.get("expected_result") or payload.get("expected", "")
        actual_result = payload.get("actual_result") or payload.get("actual", "")
        steps = payload.get("steps") or (
            f"1. Mở {payload.get('page_name', '')}. "
            f"2. Tìm {payload.get('element_name', '')}. "
            "3. So sánh Expected và Actual."
        )

        case_db_id = self.upsert_test_case(
            {
                "case_id": contract_case_id,
                "module": payload["module"],
                "page_key": payload.get("page_key", ""),
                "page_name": payload.get("page_name", ""),
                "element_key": payload.get("element_key", ""),
                "name": payload.get("element_name", payload.get("name", "")),
                "locator_type": payload.get("locator_type", ""),
                "locator_value": payload.get("locator_value", ""),
                "steps": steps,
                "expected_result": expected_result,
            }
        )
        result_payload = {
            "run_id": run_id,
            "case_id": contract_case_id,
            "module": payload["module"],
            "page_key": payload.get("page_key", ""),
            "page_name": payload.get("page_name", ""),
            "element_key": payload.get("element_key", ""),
            "name": payload.get("element_name", payload.get("name", "")),
            "steps": steps,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "status": payload.get("status", "ERROR"),
            "message": payload.get("message", ""),
            "error_message": payload.get("error_message", ""),
            "screenshot_path": payload.get("screenshot_path", ""),
            "test_case_db_id": case_db_id,
        }
        self.create_test_run(run_id=run_id, module=payload["module"], total=1)
        self.save_test_result(result_payload)
        self.finish_test_run(run_id, payload.get("status", "ERROR"), [result_payload], payload.get("message", ""))
        return case_db_id

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

    def upsert_test_case(self, payload: Dict[str, str]) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        case_id = payload["case_id"]
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO test_cases
                    (case_id, module, page_key, page_name, element_key, element_name,
                     locator_type, locator_value, expected, expected_result, steps, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    module = excluded.module,
                    page_key = excluded.page_key,
                    page_name = excluded.page_name,
                    element_key = excluded.element_key,
                    element_name = excluded.element_name,
                    locator_type = excluded.locator_type,
                    locator_value = excluded.locator_value,
                    expected = excluded.expected,
                    expected_result = excluded.expected_result,
                    steps = excluded.steps,
                    updated_at = excluded.updated_at
                """,
                (
                    case_id,
                    payload["module"],
                    payload.get("page_key", ""),
                    payload.get("page_name", ""),
                    payload.get("element_key", ""),
                    payload["name"],
                    payload.get("locator_type", ""),
                    payload.get("locator_value", ""),
                    payload["expected_result"],
                    payload["expected_result"],
                    payload["steps"],
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT id FROM test_cases WHERE case_id = ?",
                (case_id,),
            ).fetchone()
        return int(row[0])

    def create_test_run(self, run_id: str, module: str, total: int, status: str = "RUNNING") -> str:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO test_runs
                    (run_id, module, status, total, started_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, module, status, total, now),
            )
        return run_id

    def finish_test_run(self, run_id: str, status: str, results: List[Dict[str, str]], message: str = ""):
        now = datetime.now().isoformat(timespec="seconds")
        counts = {"PASSED": 0, "FAILED": 0, "ERROR": 0, "SKIPPED": 0}
        for result in results:
            counts[result.get("status", "ERROR")] = counts.get(result.get("status", "ERROR"), 0) + 1

        with self.connect() as connection:
            connection.execute(
                """
                UPDATE test_runs
                SET status = ?,
                    passed = ?,
                    failed = ?,
                    error = ?,
                    skipped = ?,
                    finished_at = ?,
                    message = ?
                WHERE run_id = ?
                """,
                (
                    status,
                    counts["PASSED"],
                    counts["FAILED"],
                    counts["ERROR"],
                    counts["SKIPPED"],
                    now,
                    message,
                    run_id,
                ),
            )

    def save_test_result(self, payload: Dict[str, str]) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO test_results
                    (test_case_id, run_id, case_id, module, page_key, page_name, element_key,
                     element_name, steps, expected, expected_result, actual, actual_result,
                     status, message, error_message, screenshot_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("test_case_db_id"),
                    payload["run_id"],
                    payload["case_id"],
                    payload["module"],
                    payload.get("page_key", ""),
                    payload.get("page_name", ""),
                    payload.get("element_key", ""),
                    payload["name"],
                    payload["steps"],
                    payload["expected_result"],
                    payload["expected_result"],
                    payload["actual_result"],
                    payload["actual_result"],
                    payload["status"],
                    payload.get("message", ""),
                    payload.get("error_message", ""),
                    payload.get("screenshot_path", ""),
                    now,
                ),
            )
        return int(cursor.lastrowid)

    def latest_run_results(self, run_id: str) -> List[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT case_id, element_name, steps, expected_result, actual_result,
                       status, error_message, screenshot_path, created_at
                FROM test_results
                WHERE run_id = ?
                ORDER BY id ASC
                """,
                (run_id,),
            ).fetchall()
        return [dict(row) for row in rows]
