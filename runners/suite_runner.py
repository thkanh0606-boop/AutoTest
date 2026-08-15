from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import QThread, Signal
from selenium.webdriver.common.by import By

from core.config import Config
from core.helpers.utils import capture_screenshot, get_logger
from core.suite_loader import PAGE_MODULE_NAMES, PAGE_URLS
from core.test_contract import TestContract
from core.test_result_repository import TestResultRepository
from runners.text_dropdown_runner import run_label_text_test


logger = get_logger()

# Delays apply only to Test Suite runs. Other test builders keep their current
# speed because run_label_text_test defaults these optional delays to zero.
_PAGE_LOAD_DELAY = 3
_ACTION_DELAY = 2
_CLOSE_DELAY = 4


def _page_url(page_key: str) -> str:
    page = TestContract.page_map().get(page_key)
    return page.url if page else PAGE_URLS.get(page_key, Config.BASE_URL)


def _normalise_path(value: str) -> str:
    path = urlparse(value).path if "://" in value else value
    path = "/" + path.strip("/") if path.strip("/") else "/"
    return path.lower()


def _run_page_open_check(page_key: str) -> tuple[bool, str]:
    """Compatibility helper used by tests and simple route checks."""
    case = {
        "tc_id": "ROUTE-CHECK",
        "page_key": page_key,
        "url": _page_url(page_key),
        "target_path": urlparse(_page_url(page_key)).path,
        "module": PAGE_MODULE_NAMES.get(page_key, page_key or "General"),
    }
    payload = _run_route_smoke(case)
    return payload["status"] == "PASSED", payload["message"]


def _run_route_smoke(case: dict, stop_requested=None) -> dict:
    """Validate route and visible DOM; opening Chrome alone is never a PASS."""
    from core.driver_factory import DriverFactory

    started = datetime.now()
    started_at = started.isoformat(timespec="seconds")
    driver = None
    screenshot_path = ""
    actual = ""
    error_message = ""
    status = "ERROR"
    message = "Không thể khởi chạy kiểm tra trang"
    target_url = case.get("url") or _page_url(case.get("page_key", ""))
    target_path = case.get("target_path") or urlparse(target_url).path

    try:
        keep_session = case.get("page_key") != "plt_login"
        driver = DriverFactory.create_driver(headless=False, keep_session=keep_session)
        driver.get(target_url)
        time.sleep(_PAGE_LOAD_DELAY)
        if stop_requested and stop_requested():
            status = "SKIPPED"
            message = "Đã dừng trước khi assertion"
        else:
            body = driver.find_element(By.TAG_NAME, "body")
            driver.execute_script("window.scrollTo({top: 160, behavior: 'smooth'});")
            time.sleep(_ACTION_DELAY)
            actual_url = driver.current_url or ""
            actual_path = _normalise_path(actual_url)
            expected_path = _normalise_path(target_path)
            body_visible = bool(body.is_displayed())
            route_matches = actual_path == expected_path
            actual = f"URL={actual_url}; body_visible={body_visible}"
            if route_matches and body_visible:
                status = "PASSED"
                message = f"URL và nội dung trang hợp lệ: {actual_url}"
            else:
                status = "FAILED"
                message = (
                    f"Expected path {expected_path}, actual {actual_path}; "
                    f"body_visible={body_visible}"
                )
                screenshot_path = capture_screenshot(driver, case.get("tc_id", "route_smoke"))
    except Exception as error:
        error_message = str(error)
        actual = f"ERROR: {error}"
        status = "ERROR"
        message = f"Không lấy được URL/DOM từ Selenium: {error}"
        logger.exception("[SUITE ROUTE ERROR] %s", case.get("tc_id", ""))
        if driver:
            screenshot_path = capture_screenshot(driver, case.get("tc_id", "route_smoke"))
    finally:
        if driver:
            time.sleep(_CLOSE_DELAY)
            driver.quit()

    finished = datetime.now()
    return {
        "case_id": case.get("tc_id", ""),
        "title": case.get("title", ""),
        "module": case.get("module") or case.get("area") or "General",
        "page_key": case.get("page_key", ""),
        "expected": case.get("expected") or f"URL chứa {target_path} và body hiển thị",
        "actual": actual,
        "status": status,
        "message": message,
        "error_message": error_message,
        "screenshot_path": screenshot_path,
        "log_text": f"OPEN {target_url}\nASSERT path={target_path}\n{message}",
        "started_at": started_at,
        "finished_at": finished.isoformat(timespec="seconds"),
        "duration_ms": int((finished - started).total_seconds() * 1000),
    }


class SuiteWorker(QThread):
    """Run one grouped Test Suite without blocking the desktop UI."""

    progress_signal = Signal(int, int, str)
    result_signal = Signal(int, str, str)
    detail_signal = Signal(int, dict)
    run_started_signal = Signal(str)
    summary_signal = Signal(dict)
    finished_signal = Signal()
    log_signal = Signal(str)

    def __init__(
        self,
        cases: list[dict],
        suite_id: int = 0,
        suite_name: str = "Ad-hoc Suite",
        run_mode: str = "Selected",
        db_path: str | None = None,
    ):
        super().__init__()
        self.cases = cases
        self.suite_id = suite_id
        self.suite_name = suite_name
        self.run_mode = run_mode
        self.db_path = db_path
        self.run_id = ""
        self._is_stopped = False

    def run(self):
        repository = TestResultRepository(self.db_path)
        total = len(self.cases)
        self.run_id = repository.start_suite_run(
            self.suite_id, self.suite_name, self.run_mode, total
        )
        self.run_started_signal.emit(self.run_id)
        self.progress_signal.emit(0, total, "[SUITE] Bắt đầu chạy...")

        try:
            for index, case in enumerate(self.cases):
                if self._is_stopped:
                    break

                tc_id = case.get("tc_id", f"Case-{index + 1}")
                self.progress_signal.emit(index, total, f"Đang chạy {tc_id}...")
                try:
                    payload = self._run_case(case)
                except Exception as error:
                    logger.exception("[SUITE CASE ERROR] %s", tc_id)
                    now = datetime.now().isoformat(timespec="seconds")
                    payload = self._base_payload(
                        case,
                        status="ERROR",
                        message="Runner phát sinh lỗi ngoài dự kiến",
                        actual=f"ERROR: {error}",
                        error_message=str(error),
                        started_at=now,
                        finished_at=now,
                    )

                repository.save_suite_result(self.run_id, index, payload)
                self.detail_signal.emit(index, payload)
                self.result_signal.emit(index, payload["status"], payload["message"])
                self.progress_signal.emit(
                    index + 1, total, f"{tc_id} → {payload['status']}"
                )

            if self._is_stopped:
                summary = repository.finish_suite_run(
                    self.run_id, status="STOPPED", message="Dừng bởi người dùng"
                )
            else:
                summary = repository.finish_suite_run(self.run_id)
                self.progress_signal.emit(total, total, "Hoàn tất toàn bộ Test Suite.")
            self.summary_signal.emit(summary)
        except Exception as error:
            logger.exception("[SUITE ERROR]")
            summary = repository.finish_suite_run(
                self.run_id, status="ERROR", message=str(error)
            )
            self.summary_signal.emit(summary)
            self.progress_signal.emit(0, total, f"[LỖI] {error}")
        finally:
            self.finished_signal.emit()

    def _base_payload(self, case: dict, **updates) -> dict:
        payload = {
            "case_id": case.get("tc_id", ""),
            "title": case.get("title", ""),
            "module": case.get("module") or case.get("area") or "General",
            "page_key": case.get("page_key", ""),
            "expected": case.get("expected", ""),
            "actual": "",
            "status": "ERROR",
            "message": "",
            "error_message": "",
            "screenshot_path": "",
            "log_text": "",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "duration_ms": 0,
        }
        payload.update(updates)
        return payload

    def _run_case(self, case: dict) -> dict:
        if case.get("action_type") == "pcm_scenario":
            from runners.pcm_suite_runner import run_pcm_scenario

            return run_pcm_scenario(case, stop_requested=lambda: self._is_stopped)

        if case.get("action_type") == "route_smoke":
            return _run_route_smoke(case, stop_requested=lambda: self._is_stopped)

        locator_value = case.get("locator_value", "")
        locator_type = case.get("locator_type", "")
        if not locator_value or not locator_type:
            return self._base_payload(
                case,
                status="SKIPPED",
                message="TC chưa có locator/action tự động; không đánh PASS giả.",
                log_text=(
                    "SKIP: Dữ liệu Excel chỉ mô tả nghiệp vụ. "
                    "Cần bổ sung locator_type, locator_value và action_type."
                ),
            )

        started = datetime.now()
        module = case.get("test_type") or case.get("module_type") or "ui"
        page_key = case.get("page_key", "")
        payload = run_label_text_test(
            worker=None,
            module=module,
            url=case.get("url") or _page_url(page_key),
            page_key=page_key,
            page_name=case.get("module") or case.get("area", ""),
            element_key=case.get("element_key") or case.get("tc_id", ""),
            element_name=case.get("title", ""),
            locator_type=locator_type,
            locator_value=locator_value,
            expected=case.get("expected", ""),
            case_id=case.get("tc_id", ""),
            steps=case.get("steps", ""),
            expected_result=case.get("expected_result") or case.get("expected", ""),
            action_type=case.get("action_type", "text_equals"),
            target_path=case.get("target_path", ""),
            headless=False,
            persist=False,
            step_delay=_ACTION_DELAY,
            close_delay=_CLOSE_DELAY,
        )
        finished = datetime.now()
        status = payload.get("status", "ERROR")
        if status not in {"PASSED", "FAILED", "ERROR", "SKIPPED"}:
            status = "ERROR"
        return self._base_payload(
            case,
            actual=payload.get("actual", ""),
            status=status,
            message=payload.get("message", ""),
            error_message=payload.get("error_message", ""),
            screenshot_path=payload.get("screenshot_path", ""),
            log_text=(
                f"OPEN {case.get('url') or _page_url(page_key)}\n"
                f"LOCATOR {locator_type}={locator_value}\n"
                f"EXPECTED {case.get('expected', '')}\n"
                f"ACTUAL {payload.get('actual', '')}\n"
                f"RESULT {status}"
            ),
            started_at=started.isoformat(timespec="seconds"),
            finished_at=finished.isoformat(timespec="seconds"),
            duration_ms=int((finished - started).total_seconds() * 1000),
        )

    def stop(self):
        self._is_stopped = True
