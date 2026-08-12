import os
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.driver_factory import DriverFactory
from core.helpers.utils import get_logger
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
    return mapping.get(locator_type.lower(), By.CSS_SELECTOR)


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


def _compare_table_rows(expected: str, actual: str, trim: bool = True, case_sensitive: bool = True):
    expected_lines = _split_compare_lines(expected)
    actual_lines = _split_compare_lines(actual)
    actual_document = _normalize_text(actual, trim=trim, case_sensitive=case_sensitive)
    pairs = []

    for index, expected_line in enumerate(expected_lines, start=1):
        expected_compare = _normalize_text(expected_line, trim=trim, case_sensitive=case_sensitive)
        matching_actual = ""
        for actual_line in actual_lines:
            actual_line_compare = _normalize_text(actual_line, trim=trim, case_sensitive=case_sensitive)
            if expected_compare and expected_compare in actual_line_compare:
                matching_actual = actual_line
                break

        if not matching_actual and expected_compare in actual_document:
            matching_actual = expected_line

        pairs.append(
            {
                "index": index,
                "expected": expected_line,
                "actual": matching_actual,
                "status": "PASS" if matching_actual else "FAIL",
            }
        )

    status = "PASSED" if pairs and all(pair["status"] == "PASS" for pair in pairs) else "FAILED"
    return status, pairs


def _ensure_logged_in(driver, target_url: str):
    if "login" not in driver.current_url.lower():
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
    wait.until(lambda browser: "login" not in browser.current_url.lower())
    driver.get(target_url)


def _read_actual(driver, element, module: str) -> str:
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
    trim: bool = True,
    case_sensitive: bool = True,
    headless: bool = False,
    persist: bool = True,
):
    driver = None
    repository = TestResultRepository()

    try:
        if worker:
            worker.log_signal.emit(f"[LABEL/TEXT] Mở trang kiểm thử: {page_name}")
            worker.progress_signal.emit(20)

        driver = DriverFactory.create_driver(headless=headless, keep_session=True)
        driver.get(url)
        _ensure_logged_in(driver, url)

        if worker:
            worker.log_signal.emit(f"[LABEL/TEXT] Lấy text element: {element_name}")
            worker.progress_signal.emit(60)

        element = driver.find_element(_by(locator_type), locator_value)
        actual = _read_actual(driver, element, module)
        pairs = []
        if module in ("dropdown", "menu"):
            status, pairs = _compare_line_pairs(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )
        elif module == "table":
            status, pairs = _compare_table_rows(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )
        else:
            expected_compare = _normalize_text(expected, trim=trim, case_sensitive=case_sensitive)
            actual_compare = _normalize_text(actual, trim=trim, case_sensitive=case_sensitive)
            status = "PASSED" if actual_compare == expected_compare else "FAILED"
        message = "Expected khớp Actual" if status == "PASSED" else "Expected khác Actual"

    except Exception as error:
        actual = f"ERROR: {error}"
        status = "FAILED"
        message = "Không lấy được text từ Selenium"
        pairs = []

    finally:
        if driver:
            driver.quit()

    payload = {
        "module": module,
        "page_key": page_key,
        "page_name": page_name,
        "element_key": element_key,
        "element_name": element_name,
        "locator_type": locator_type,
        "locator_value": locator_value,
        "expected": expected,
        "actual": actual,
        "status": status,
        "message": message,
        "pairs": pairs,
        "database": repository.db_path,
    }

    if persist:
        payload["test_case_id"] = repository.save_case_and_result(payload)

    logger.info(
        "[LABEL/TEXT] page=%s element=%s expected=%s actual=%s status=%s",
        page_name,
        element_name,
        expected,
        actual,
        status,
    )

    if worker:
        worker.progress_signal.emit(100)
        worker.log_signal.emit(f"[LABEL/TEXT] {status}: {message}")

    return payload


def run_text_dropdown_test(worker=None, **kwargs):
    return run_label_text_test(worker=worker, **kwargs)


run_label_text_test.__test__ = False
run_text_dropdown_test.__test__ = False
