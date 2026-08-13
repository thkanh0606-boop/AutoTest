import os
import re
import sys
import csv
from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.driver_factory import DriverFactory
from core.helpers.utils import capture_screenshot, get_logger
from core.test_result_repository import TestResultRepository

logger = get_logger()


def _by(locator_type: str):
    mapping = {
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
    }
    return mapping.get((locator_type or "css").lower(), By.CSS_SELECTOR)


def _normalize_text(text: str, trim: bool = True, case_sensitive: bool = True):
    value = text or ""
    if trim:
        value = " ".join(value.split())
    if not case_sensitive:
        value = value.lower()
    return value


def _split_compare_lines(text: str):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _compare_line_pairs(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    expected_lines = _split_compare_lines(expected)
    actual_lines = _split_compare_lines(actual)
    pairs = []

    max_count = max(len(expected_lines), len(actual_lines))
    for index in range(max_count):
        expected_line = expected_lines[index] if index < len(expected_lines) else ""
        actual_line = actual_lines[index] if index < len(actual_lines) else ""
        expected_compare = _normalize_text(expected_line, trim=trim, case_sensitive=case_sensitive)
        actual_compare = _normalize_text(actual_line, trim=trim, case_sensitive=case_sensitive)
        pair_status = "PASS" if expected_compare == actual_compare and expected_line and actual_line else "FAIL"
        pairs.append(
            {
                "index": index + 1,
                "expected": expected_line,
                "actual": actual_line,
                "status": pair_status,
            }
        )

    status = "PASSED" if pairs and all(pair["status"] == "PASS" for pair in pairs) else "FAILED"
    return status, pairs


def _split_table_line(line: str):
    if "\t" in line:
        return [cell.strip() for cell in line.split("\t")]
    try:
        cells = next(csv.reader(StringIO(line)))
    except Exception:
        cells = [line]
    return [cell.strip() for cell in cells]


def _table_matrix(text: str):
    rows = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        cells = _split_table_line(line)
        while cells and not cells[-1]:
            cells.pop()
        if cells:
            rows.append(cells)
    return rows


def _table_text_from_element(element):
    table_rows = []
    row_elements = element.find_elements(By.CSS_SELECTOR, "tr, .ant-table-row")
    for row_element in row_elements:
        cell_elements = row_element.find_elements(By.CSS_SELECTOR, "th, td, .ant-table-cell")
        cells = [cell.text.strip() for cell in cell_elements if cell.text.strip()]
        if cells:
            table_rows.append("\t".join(cells))

    if table_rows:
        return "\n".join(table_rows)

    lines = [line.strip() for line in (element.text or "").splitlines() if line.strip()]
    return "\t".join(lines)


def _compare_table_rows(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    expected_rows = _table_matrix(expected)
    actual_rows = _table_matrix(actual)
    max_rows = max(len(expected_rows), len(actual_rows))
    pairs = []

    for row_index in range(max_rows):
        expected_cells = expected_rows[row_index] if row_index < len(expected_rows) else []
        actual_cells = actual_rows[row_index] if row_index < len(actual_rows) else []
        max_cells = max(len(expected_cells), len(actual_cells))
        for cell_index in range(max_cells):
            expected_cell = expected_cells[cell_index] if cell_index < len(expected_cells) else ""
            actual_cell = actual_cells[cell_index] if cell_index < len(actual_cells) else ""
            expected_compare = _normalize_text(expected_cell, trim=trim, case_sensitive=case_sensitive)
            actual_compare = _normalize_text(actual_cell, trim=trim, case_sensitive=case_sensitive)
            pair_status = "PASS" if expected_compare == actual_compare and expected_cell and actual_cell else "FAIL"
            pairs.append(
                {
                    "index": f"R{row_index + 1}C{cell_index + 1}",
                    "expected": expected_cell,
                    "actual": actual_cell,
                    "status": pair_status,
                }
            )

    status = "PASSED" if pairs and all(pair["status"] == "PASS" for pair in pairs) else "FAILED"
    return status, pairs


def _compare_contains_all(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    expected_lines = _split_compare_lines(expected)
    actual_compare = _normalize_text(actual, trim=trim, case_sensitive=case_sensitive)
    pairs = []

    for index, expected_line in enumerate(expected_lines, start=1):
        expected_compare = _normalize_text(expected_line, trim=trim, case_sensitive=case_sensitive)
        matched = bool(expected_compare and expected_compare in actual_compare)
        pairs.append(
            {
                "index": index,
                "expected": expected_line,
                "actual": expected_line if matched else actual,
                "status": "PASS" if matched else "FAIL",
            }
        )

    status = "PASSED" if pairs and all(pair["status"] == "PASS" for pair in pairs) else "FAILED"
    return status, pairs


def _compare_contains_all_has_number(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    status, pairs = _compare_contains_all(expected, actual, trim=trim, case_sensitive=case_sensitive)
    has_number = bool(re.search(r"\d+", actual or ""))
    pairs.append(
        {
            "index": len(pairs) + 1,
            "expected": "Có số liệu",
            "actual": "Có số liệu" if has_number else "Không thấy số liệu",
            "status": "PASS" if has_number else "FAIL",
        }
    )
    status = "PASSED" if all(pair["status"] == "PASS" for pair in pairs) else "FAILED"
    return status, pairs


def _compare_navigation_expected(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    expected_value = _normalize_text(expected, trim=trim, case_sensitive=case_sensitive)
    actual_value = _normalize_text(actual, trim=trim, case_sensitive=case_sensitive)
    if not expected_value:
        return "FAILED"
    if expected_value.startswith(("http://", "https://")):
        return "PASSED" if actual_value == expected_value else "FAILED"
    return "PASSED" if expected_value in actual_value else "FAILED"


def _login_form_visible(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password']"))
        )
        return True
    except Exception:
        return False


def _ensure_logged_in(driver, target_url: str):
    if not _login_form_visible(driver):
        return

    wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)
    email = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[name='username'], input[type='text']")
        )
    )
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
    email.clear()
    email.send_keys(Config.TEST_EMAIL)
    password.clear()
    password.send_keys(Config.TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button").click()
    wait.until(lambda browser: not _login_form_visible(browser))
    driver.get(target_url)


def _read_actual(driver, element, module: str, action_type: str = "text_equals", target_path: str = "") -> str:
    if action_type == "click_url_contains":
        WebDriverWait(driver, Config.EXPLICIT_WAIT).until(lambda _driver: element.is_displayed() and element.is_enabled())
        element.click()
        WebDriverWait(driver, Config.EXPLICIT_WAIT).until(EC.url_contains(target_path))
        return driver.current_url

    if action_type == "deep_link_url_contains":
        WebDriverWait(driver, Config.EXPLICIT_WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
        return driver.current_url

    if module == "dropdown":
        options = element.find_elements(By.TAG_NAME, "option")
        if options:
            return "\n".join(option.text.strip() for option in options if option.text.strip())

        try:
            element.click()
        except Exception:
            element.find_element(By.CSS_SELECTOR, "input[role='combobox']").click()
        WebDriverWait(driver, Config.EXPLICIT_WAIT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content")
            )
        )
        option_elements = driver.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content",
        )
        values = []
        for option in option_elements:
            text = option.text.strip()
            if text and text not in values:
                values.append(text)
        return "\n".join(values)

    if module == "image":
        return element.get_attribute("alt") or element.get_attribute("src") or "visible"

    if module == "table":
        return _table_text_from_element(element)

    if module == "ui":
        return "visible" if element.is_displayed() else "hidden"

    return element.text.strip()


def run_label_text_test(
    worker=None,
    module: str = "label",
    url: str = "",
    page_key: str = "",
    page_name: str = "",
    element_key: str = "",
    element_name: str = "",
    locator_type: str = "css",
    locator_value: str = "",
    expected: str = "",
    case_id: str = "",
    steps: str = "",
    expected_result: str = "",
    action_type: str = "text_equals",
    target_path: str = "",
    trim: bool = True,
    case_sensitive: bool = True,
    headless: bool = False,
    persist: bool = True,
):
    driver = None
    repository = TestResultRepository()
    screenshot_path = ""
    error_message = ""
    actual = ""
    status = "ERROR"
    message = ""
    pairs = []

    try:
        if worker:
            worker.log_signal.emit(f"[{module.upper()}] Mở trang kiểm thử: {page_name}")
            worker.progress_signal.emit(20)

        driver = DriverFactory.create_driver(headless=headless, keep_session=True)
        driver.get(url)
        _ensure_logged_in(driver, url)

        if worker:
            worker.log_signal.emit(f"[{module.upper()}] Kiểm tra element: {element_name}")
            worker.progress_signal.emit(60)

        element = driver.find_element(_by(locator_type), locator_value)
        actual = _read_actual(driver, element, module, action_type=action_type, target_path=target_path)

        if action_type in ("click_url_contains", "deep_link_url_contains"):
            status = _compare_navigation_expected(expected, actual, trim=trim, case_sensitive=case_sensitive)
        elif action_type == "contains_all":
            status, pairs = _compare_contains_all(expected, actual, trim=trim, case_sensitive=case_sensitive)
        elif action_type == "contains_all_has_number":
            status, pairs = _compare_contains_all_has_number(expected, actual, trim=trim, case_sensitive=case_sensitive)
        elif module in ("dropdown", "menu"):
            status, pairs = _compare_line_pairs(expected, actual, trim=trim, case_sensitive=case_sensitive)
        elif module == "table":
            status, pairs = _compare_table_rows(expected, actual, trim=trim, case_sensitive=case_sensitive)
        else:
            expected_compare = _normalize_text(expected, trim=trim, case_sensitive=case_sensitive)
            actual_compare = _normalize_text(actual, trim=trim, case_sensitive=case_sensitive)
            status = "PASSED" if actual_compare == expected_compare else "FAILED"

        if status == "PASSED":
            message = "Expected khớp Actual"
        elif not (expected or "").strip():
            message = "Expected Result đang trống"
        else:
            message = "Expected khác Actual"
        if status != "PASSED" and driver:
            screenshot_path = capture_screenshot(driver, case_id or element_key or module)

    except Exception as error:
        actual = f"ERROR: {error}"
        status = "ERROR"
        message = "Không lấy được dữ liệu từ Selenium"
        error_message = str(error)
        if driver:
            screenshot_path = capture_screenshot(driver, case_id or element_key or module)

    finally:
        if driver:
            driver.quit()

    effective_case_id = case_id or f"{module}:{page_key}:{element_key}"
    effective_expected_result = expected_result or expected
    effective_steps = steps or f"1. Mở {page_name}. 2. Tìm {element_name}. 3. So sánh Expected và Actual."
    payload = {
        "module": module,
        "page_key": page_key,
        "page_name": page_name,
        "element_key": element_key,
        "element_name": element_name,
        "locator_type": locator_type,
        "locator_value": locator_value,
        "expected": expected,
        "case_id": effective_case_id,
        "steps": effective_steps,
        "expected_result": effective_expected_result,
        "actual": actual,
        "actual_result": actual,
        "status": status,
        "message": message,
        "error_message": error_message,
        "screenshot_path": screenshot_path,
        "pairs": pairs,
        "database": repository.db_path,
    }

    if persist:
        payload["test_case_id"] = repository.save_case_and_result(payload)

    logger.info(
        "[%s] page=%s element=%s expected=%s actual=%s status=%s",
        module.upper(),
        page_name,
        element_name,
        expected,
        actual,
        status,
    )

    if worker:
        worker.progress_signal.emit(100)
        worker.log_signal.emit(f"[{module.upper()}] {status}: {message}")

    return payload


def run_text_dropdown_test(worker=None, **kwargs):
    return run_label_text_test(worker=worker, **kwargs)


run_label_text_test.__test__ = False
run_text_dropdown_test.__test__ = False
