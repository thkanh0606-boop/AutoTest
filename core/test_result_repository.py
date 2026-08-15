import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from core.config import Config


class TestResultRepository:
    __test__ = False

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.path.join(Config.BASE_DIR, "autotest.sqlite3")
        self.init_db()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

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
            self._init_suite_tables(connection)

    def _init_suite_tables(self, connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suite_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                source_path TEXT NOT NULL DEFAULT '',
                case_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suite_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_id INTEGER NOT NULL,
                case_order INTEGER NOT NULL,
                case_id TEXT NOT NULL,
                title TEXT NOT NULL,
                module TEXT NOT NULL,
                page_key TEXT NOT NULL,
                expected TEXT NOT NULL,
                source_sheet TEXT NOT NULL DEFAULT '',
                payload_json TEXT NOT NULL,
                FOREIGN KEY(suite_id) REFERENCES suite_definitions(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suite_runs (
                run_id TEXT PRIMARY KEY,
                suite_id INTEGER,
                suite_name TEXT NOT NULL,
                run_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                total INTEGER NOT NULL DEFAULT 0,
                passed INTEGER NOT NULL DEFAULT 0,
                failed INTEGER NOT NULL DEFAULT 0,
                error INTEGER NOT NULL DEFAULT 0,
                skipped INTEGER NOT NULL DEFAULT 0,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                message TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(suite_id) REFERENCES suite_definitions(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suite_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                result_index INTEGER NOT NULL,
                case_id TEXT NOT NULL,
                title TEXT NOT NULL,
                module TEXT NOT NULL,
                page_key TEXT NOT NULL,
                expected TEXT NOT NULL,
                actual TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                error_message TEXT NOT NULL DEFAULT '',
                screenshot_path TEXT NOT NULL DEFAULT '',
                log_text TEXT NOT NULL DEFAULT '',
                started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(run_id) REFERENCES suite_runs(run_id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_suite_cases_suite_id ON suite_cases(suite_id, case_order)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_suite_runs_started ON suite_runs(started_at DESC)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_suite_results_run ON suite_results(run_id, result_index)"
        )

    def _column_names(self, connection: sqlite3.Connection, table_name: str) -> set:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {row[1] for row in rows}

    def _add_column_if_missing(
        self, connection: sqlite3.Connection, table_name: str, column_name: str, definition: str
    ):
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
        self.finish_test_run(
            run_id, payload.get("status", "ERROR"), [result_payload], payload.get("message", "")
        )
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

    def create_test_run(
        self, run_id: str, module: str, total: int, status: str = "RUNNING"
    ) -> str:
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

    def finish_test_run(
        self, run_id: str, status: str, results: List[Dict[str, str]], message: str = ""
    ):
        now = datetime.now().isoformat(timespec="seconds")
        counts = {"PASSED": 0, "FAILED": 0, "ERROR": 0, "SKIPPED": 0}
        for result in results:
            counts[result.get("status", "ERROR")] = (
                counts.get(result.get("status", "ERROR"), 0) + 1
            )

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

    # ------------------------------------------------------------------
    # Test Suite definitions, grouped runs and reports
    # ------------------------------------------------------------------
    def save_suite_definition(
        self,
        name: str,
        cases: List[dict],
        source_path: str = "",
        suite_key: str = "",
    ) -> int:
        stable_source = os.path.abspath(source_path) if source_path else name
        stable_key = suite_key or uuid.uuid5(uuid.NAMESPACE_URL, stable_source).hex
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO suite_definitions
                    (suite_key, name, source_path, case_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(suite_key) DO UPDATE SET
                    name = excluded.name,
                    source_path = excluded.source_path,
                    case_count = excluded.case_count,
                    updated_at = excluded.updated_at
                """,
                (stable_key, name, source_path, len(cases), now, now),
            )
            suite_id = int(
                connection.execute(
                    "SELECT id FROM suite_definitions WHERE suite_key = ?", (stable_key,)
                ).fetchone()[0]
            )
            connection.execute("DELETE FROM suite_cases WHERE suite_id = ?", (suite_id,))
            for index, case in enumerate(cases):
                module = (
                    case.get("module") or case.get("area") or case.get("page_key") or "General"
                )
                connection.execute(
                    """
                    INSERT INTO suite_cases
                        (suite_id, case_order, case_id, title, module, page_key,
                         expected, source_sheet, payload_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        suite_id,
                        index,
                        str(case.get("tc_id") or case.get("case_id") or f"CASE-{index + 1:03d}"),
                        str(case.get("title", "")),
                        str(module),
                        str(case.get("page_key", "")),
                        str(case.get("expected", "")),
                        str(case.get("source_sheet", "")),
                        json.dumps(case, ensure_ascii=False),
                    ),
                )
        return suite_id

    def list_suite_definitions(self) -> List[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, suite_key, name, source_path, case_count, created_at, updated_at
                FROM suite_definitions
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def suite_definition(self, suite_id: int) -> Optional[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM suite_definitions WHERE id = ?", (suite_id,)
            ).fetchone()
        return dict(row) if row else None

    def suite_cases(self, suite_id: int) -> List[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT payload_json FROM suite_cases
                WHERE suite_id = ? ORDER BY case_order
                """,
                (suite_id,),
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def remove_suite_definition_by_source(self, source_path: str) -> bool:
        """Remove a source-backed suite from the picker while preserving run history."""
        absolute_source = os.path.normcase(os.path.normpath(os.path.abspath(source_path)))
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id, source_path FROM suite_definitions WHERE source_path <> ''"
            ).fetchall()
            suite_ids = [
                int(row[0])
                for row in rows
                if os.path.normcase(os.path.normpath(os.path.abspath(row[1]))) == absolute_source
            ]
            if not suite_ids:
                return False
            for suite_id in suite_ids:
                connection.execute(
                    "UPDATE suite_runs SET suite_id = NULL WHERE suite_id = ?", (suite_id,)
                )
                connection.execute("DELETE FROM suite_cases WHERE suite_id = ?", (suite_id,))
                connection.execute("DELETE FROM suite_definitions WHERE id = ?", (suite_id,))
        return True

    def start_suite_run(self, suite_id: int, suite_name: str, run_mode: str, total: int) -> str:
        run_id = f"suite-{uuid.uuid4().hex[:16]}"
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO suite_runs
                    (run_id, suite_id, suite_name, run_mode, status, total, started_at)
                VALUES (?, ?, ?, ?, 'RUNNING', ?, ?)
                """,
                (run_id, suite_id, suite_name, run_mode, total, now),
            )
        return run_id

    def save_suite_result(self, run_id: str, result_index: int, payload: dict) -> int:
        started_at = payload.get("started_at") or datetime.now().isoformat(timespec="seconds")
        finished_at = payload.get("finished_at") or datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO suite_results
                    (run_id, result_index, case_id, title, module, page_key,
                     expected, actual, status, message, error_message,
                     screenshot_path, log_text, started_at, finished_at, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    result_index,
                    payload.get("case_id", ""),
                    payload.get("title", ""),
                    payload.get("module", "General"),
                    payload.get("page_key", ""),
                    payload.get("expected", ""),
                    payload.get("actual", ""),
                    payload.get("status", "ERROR"),
                    payload.get("message", ""),
                    payload.get("error_message", ""),
                    payload.get("screenshot_path", ""),
                    payload.get("log_text", ""),
                    started_at,
                    finished_at,
                    int(payload.get("duration_ms", 0)),
                ),
            )
        return int(cursor.lastrowid)

    def finish_suite_run(self, run_id: str, status: str = "", message: str = "") -> dict:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            counts = {
                row["status"]: row["count"]
                for row in connection.execute(
                    "SELECT status, COUNT(*) AS count FROM suite_results WHERE run_id = ? GROUP BY status",
                    (run_id,),
                ).fetchall()
            }
            run = connection.execute(
                "SELECT started_at FROM suite_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            started = datetime.fromisoformat(run["started_at"]) if run else datetime.now()
            duration_ms = max(0, int((datetime.now() - started).total_seconds() * 1000))
            passed = counts.get("PASSED", 0)
            failed = counts.get("FAILED", 0)
            error = counts.get("ERROR", 0)
            skipped = counts.get("SKIPPED", 0)
            effective_status = status or (
                "FAILED" if failed or error else "PASSED_WITH_SKIPS" if skipped else "PASSED"
            )
            connection.execute(
                """
                UPDATE suite_runs SET status = ?, passed = ?, failed = ?, error = ?,
                    skipped = ?, finished_at = ?, duration_ms = ?, message = ?
                WHERE run_id = ?
                """,
                (
                    effective_status,
                    passed,
                    failed,
                    error,
                    skipped,
                    now,
                    duration_ms,
                    message,
                    run_id,
                ),
            )
            summary = connection.execute(
                "SELECT * FROM suite_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return dict(summary) if summary else {}

    def list_suite_runs(
        self,
        suite_name: str = "",
        status: str = "",
        module: str = "",
        limit: int = 200,
    ) -> List[dict]:
        conditions = []
        parameters: List[object] = []
        if suite_name and suite_name != "Tất cả":
            conditions.append("r.suite_name = ?")
            parameters.append(suite_name)
        if status and status != "Tất cả":
            conditions.append("r.status = ?")
            parameters.append(status)
        if module and module != "Tất cả":
            conditions.append(
                "EXISTS (SELECT 1 FROM suite_results x WHERE x.run_id = r.run_id AND x.module = ?)"
            )
            parameters.append(module)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        parameters.append(limit)
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"""
                SELECT r.* FROM suite_runs r
                {where}
                ORDER BY r.started_at DESC LIMIT ?
                """,
                parameters,
            ).fetchall()
        return [dict(row) for row in rows]

    def list_runs(
        self,
        suite_name: str = None,
        status: str = None,
        module: str = None,
        limit: int = 200,
    ) -> List[dict]:
        """Tương thích trực tiếp với gọi hàm list_runs(...) trên UI TestSuitePage."""
        return self.list_suite_runs(
            suite_name=suite_name or "",
            status=status or "",
            module=module or "",
            limit=limit,
        )

    def suite_run(self, run_id: str) -> Optional[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM suite_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return dict(row) if row else None

    def suite_run_results(self, run_id: str, status: str = "", module: str = "") -> List[dict]:
        conditions = ["run_id = ?"]
        parameters: List[object] = [run_id]
        if status and status != "Tất cả":
            conditions.append("status = ?")
            parameters.append(status)
        if module and module != "Tất cả":
            conditions.append("module = ?")
            parameters.append(module)
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"""
                SELECT * FROM suite_results
                WHERE {' AND '.join(conditions)}
                ORDER BY result_index
                """,
                parameters,
            ).fetchall()
        return [dict(row) for row in rows]

    def suite_run_module_summary(self, run_id: str) -> List[dict]:
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT module, COUNT(*) AS total,
                    SUM(CASE WHEN status = 'PASSED' THEN 1 ELSE 0 END) AS passed,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed,
                    SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) AS error,
                    SUM(CASE WHEN status = 'SKIPPED' THEN 1 ELSE 0 END) AS skipped,
                    SUM(duration_ms) AS duration_ms
                FROM suite_results WHERE run_id = ?
                GROUP BY module ORDER BY module COLLATE NOCASE
                """,
                (run_id,),
            ).fetchall()
        return [dict(row) for row in rows]
