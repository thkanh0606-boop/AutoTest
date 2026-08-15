"""Helper dùng chung để thao tác với giao diện Ant Design bằng Selenium.

Trang thực tế (courses.plt.pro.vn) dùng component Ant Design cho toàn bộ
dropdown/modal/thông báo. Đây KHÔNG phải thẻ <select> gốc nên không thể dùng
`selenium.webdriver.support.ui.Select`. Các hàm ở đây tập trung xử lý đúng
hành vi Ant Design (mở panel option, chọn theo text, chờ modal/toast...) và
được dùng lại bởi cả runner lẫn test pytest để tránh lặp code.

Chiến lược locator ở đây ưu tiên "label-anchored" (tìm control theo nhãn hiển
thị) và `normalize-space(.)` thay vì `text()` thuần, vì nhãn nút trong app có
thể được bọc trong <span> hoặc không tuỳ trang - dùng normalize-space(.) so
khớp toàn bộ text hậu duệ sẽ ổn định với cả hai kiểu render.
"""

from __future__ import annotations

import os
import random
import time
from pathlib import Path
from typing import Iterable, Optional

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Config

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_CREDENTIAL_FILE = PROJECT_ROOT / ".autotest.env"


# ---------------------------------------------------------------------------
# Credentials / đăng nhập
# ---------------------------------------------------------------------------

def _read_simple_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    except Exception:
        return {}
    return values


def load_credentials() -> tuple[str, str]:
    """Lấy tài khoản test từ biến môi trường, .autotest.env, hoặc Config (fallback)."""
    local = _read_simple_env(LOCAL_CREDENTIAL_FILE)
    email = (
        os.getenv("AUTOTEST_EMAIL")
        or os.getenv("TEST_EMAIL")
        or local.get("AUTOTEST_EMAIL")
        or local.get("TEST_EMAIL")
        or Config.TEST_EMAIL
        or ""
    ).strip()
    password = (
        os.getenv("AUTOTEST_PASSWORD")
        or os.getenv("TEST_PASSWORD")
        or local.get("AUTOTEST_PASSWORD")
        or local.get("TEST_PASSWORD")
        or Config.TEST_PASSWORD
        or ""
    )
    return email, password


def first_visible(driver, candidates: Iterable[tuple[str, str]]):
    for by, value in candidates:
        try:
            for element in driver.find_elements(by, value):
                if element.is_displayed():
                    return element
        except Exception:
            continue
    return None


def is_login_page(driver) -> bool:
    current = (driver.current_url or "").lower()
    if "/login" in current:
        return True
    try:
        return bool(driver.find_elements(By.CSS_SELECTOR, "input[type='password']"))
    except Exception:
        return False


def submit_login_form(driver, email_text: str, password_text: str, timeout: int = 15) -> bool:
    if not email_text or not password_text:
        return False

    email_candidates = [
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[name='email']"),
        (By.CSS_SELECTOR, "input[autocomplete='email']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Email')]/following::input[1]"),
    ]
    password_candidates = [
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Mật khẩu')]/following::input[1]"),
    ]
    button_candidates = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(normalize-space(.),'Đăng nhập')]"),
        (By.XPATH, "//button[contains(normalize-space(.),'Login')]"),
    ]

    end = time.monotonic() + max(5, timeout)
    email_el = password_el = button_el = None
    while time.monotonic() < end:
        email_el = first_visible(driver, email_candidates)
        password_el = first_visible(driver, password_candidates)
        button_el = first_visible(driver, button_candidates)
        if email_el and password_el and button_el:
            break
        time.sleep(0.2)

    if not (email_el and password_el and button_el):
        return False

    email_el.click()
    email_el.clear()
    email_el.send_keys(email_text)
    password_el.click()
    password_el.clear()
    password_el.send_keys(password_text)
    safe_click(driver, button_el)
    return True


def login_if_needed(driver, target_url: str, page_ready_locator=None, worker=None, timeout: int = 25):
    """Điều hướng tới target_url; nếu bị đá về /login thì tự đăng nhập bằng
    .autotest.env / biến môi trường rồi quay lại target_url."""
    log(worker, f"Mở {target_url}", 10)
    driver.get(target_url)

    if not is_login_page(driver):
        return

    email_text, password_text = load_credentials()
    if not email_text or not password_text:
        raise RuntimeError(
            "Thiếu tài khoản tự đăng nhập. Hãy tạo file .autotest.env ở thư mục gốc "
            "dự án (cùng cấp main.py) với TEST_EMAIL và TEST_PASSWORD."
        )

    log(worker, "Chưa có session, đang tự đăng nhập...", 20)
    if not submit_login_form(driver, email_text, password_text, timeout=timeout):
        raise RuntimeError("Không tìm thấy đầy đủ ô Email / Mật khẩu / nút Đăng nhập trên form.")

    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(lambda d: not is_login_page(d))
    except TimeoutException as exc:
        raise RuntimeError(
            "Đăng nhập không thành công. Kiểm tra lại TEST_EMAIL/TEST_PASSWORD trong .autotest.env."
        ) from exc

    time.sleep(2.0)  # SPA cần một nhịp để persist auth trước khi điều hướng lại
    driver.get(target_url)

    if page_ready_locator is not None:
        try:
            wait.until(EC.presence_of_element_located(page_ready_locator))
        except TimeoutException as exc:
            if is_login_page(driver):
                raise RuntimeError(
                    "Đăng nhập xong nhưng session chưa hợp lệ; kiểm tra tài khoản test hoặc chạy lại."
                ) from exc
            raise

    log(worker, "Đăng nhập xong, bắt đầu kiểm thử.", 30)


# ---------------------------------------------------------------------------
# Tiện ích chung (log, click an toàn, modal, dropdown Ant Design)
# ---------------------------------------------------------------------------

def log(worker, text: str, progress: Optional[int] = None):
    if worker:
        worker.log_signal.emit(text)
        if progress is not None:
            worker.progress_signal.emit(progress)


def step(expected: str, actual: str, passed: bool, note: str = "") -> dict:
    return {
        "expected": expected,
        "actual": actual,
        "result": "PASS" if passed else "FAIL",
        "note": note,
    }


def safe_click(driver, element):
    """Click bình thường; nếu bị che (overlay/loading) thì click bằng JS."""
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def visible_modal(driver):
    for modal in driver.find_elements(By.CSS_SELECTOR, "div.ant-modal"):
        try:
            if modal.is_displayed():
                return modal
        except Exception:
            pass
    return None


def wait_for_loading_to_clear(driver, timeout: int = 10):
    """Chờ các spinner/skeleton loading của Ant Design biến mất trước khi thao tác,
    để tránh ElementClickIntercepted khi bảng/ảnh còn đang tải."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: not any(
                el.is_displayed()
                for el in d.find_elements(
                    By.CSS_SELECTOR, ".ant-spin-spinning, .ant-skeleton-active"
                )
            )
        )
    except TimeoutException:
        pass


def choose_ant_option(driver, combo, text: str, timeout: int = 15) -> bool:
    """Chọn option trong dropdown Ant Design (Select) theo text hiển thị.
    KHÔNG dùng selenium.webdriver.support.ui.Select vì đây không phải <select> gốc.
    """
    safe_click(driver, combo)

    try:
        combo.send_keys(Keys.CONTROL, "a")
        combo.send_keys(text)
    except Exception:
        pass

    wait = WebDriverWait(driver, timeout)

    def find_option(d):
        options = d.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option, "
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item",
        )
        for option in options:
            try:
                if option.is_displayed() and text.strip().casefold() in option.text.strip().casefold():
                    return option
            except Exception:
                continue
        return False

    try:
        option = wait.until(find_option)
        safe_click(driver, option)
        try:
            combo.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return True
    except TimeoutException:
        return False


def choose_ant_option_first(driver, combo, timeout: int = 15) -> Optional[str]:
    """Mở dropdown và chọn OPTION ĐẦU TIÊN đang hiển thị (không phụ thuộc dữ liệu
    thật của hệ thống). Trả về text option đã chọn, hoặc None nếu không có option."""
    safe_click(driver, combo)
    wait = WebDriverWait(driver, timeout)

    def find_first(d):
        options = d.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
            ".ant-select-item-option:not(.ant-select-item-option-disabled)",
        )
        visible = [o for o in options if o.is_displayed()]
        return visible[0] if visible else False

    try:
        option = wait.until(find_first)
    except TimeoutException:
        return None

    text = (option.text or "").strip()
    safe_click(driver, option)
    try:
        combo.send_keys(Keys.ESCAPE)
    except Exception:
        pass
    return text or None


def form_item_by_label(driver, label_text: str, timeout: int = 10):
    """Trả về container .ant-form-item chứa nhãn khớp `label_text`.
    Tránh phụ thuộc vào tên thuộc tính name/id nội bộ (không thể biết chắc khi
    không truy cập được DOM trực tiếp) — bám theo nhãn hiển thị cho người dùng,
    vốn ổn định hơn khi UI đổi cấu trúc HTML nội bộ.
    """
    xpath = (
        "//*[self::label or contains(@class,'ant-form-item-label')]"
        f"[contains(normalize-space(.), \"{label_text}\")]"
        "/ancestor::*[contains(@class,'ant-form-item')][1]"
    )
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def text_input_in_item(item):
    try:
        return item.find_element(By.CSS_SELECTOR, "input:not([type='hidden']), textarea")
    except NoSuchElementException:
        return None


def select_trigger_in_item(item):
    for css in (
        ".ant-select-selector",
        ".ant-select",
        ".ant-picker",
        "[role='combobox']",
    ):
        try:
            return item.find_element(By.CSS_SELECTOR, css)
        except NoSuchElementException:
            continue
    return None


def field_error_text(item) -> str:
    try:
        el = item.find_element(By.CSS_SELECTOR, ".ant-form-item-explain-error")
        return (el.text or "").strip()
    except NoSuchElementException:
        return ""


def wait_for_any_message(driver, timeout: int = 10) -> str:
    """Chờ và trả về nội dung thông báo toast/alert Ant Design đầu tiên xuất hiện
    (message/notification/alert), bất kể class chính xác là gì."""
    wait = WebDriverWait(driver, timeout)
    selector = (
        ".ant-message-notice-content, .ant-notification-notice-message, "
        ".ant-notification-notice-description, .ant-alert-message"
    )

    def find_text(d):
        for el in d.find_elements(By.CSS_SELECTOR, selector):
            try:
                if el.is_displayed() and (el.text or "").strip():
                    return el.text.strip()
            except Exception:
                continue
        return False

    try:
        return wait.until(find_text)
    except TimeoutException:
        return ""


# ---------------------------------------------------------------------------
# Dữ liệu test độc lập / khôi phục được
# ---------------------------------------------------------------------------

def generate_unique_plate(prefix: str = "88") -> str:
    """Sinh biển số duy nhất theo mỗi lần chạy để test Create/Search/Update/Delete
    không bao giờ đụng dữ liệu thật hay dữ liệu để lại từ lần chạy trước - đảm bảo
    dữ liệu test có thể dọn dẹp / khôi phục độc lập giữa các lần chạy."""
    letters = "ABCKLMNPSTUVXYZ"
    letter = random.choice(letters)
    # Dùng millisecond hiện tại để tối đa hoá tính duy nhất giữa các lần chạy liên tiếp.
    ms = int(time.time() * 1000) % 100000
    return f"{prefix}{letter}-{ms // 100:03d}.{ms % 100:02d}"


def find_row_by_plate(driver, table_locator, plate: str, timeout: int = 10):
    wait = WebDriverWait(driver, timeout)
    try:
        table = wait.until(EC.presence_of_element_located(table_locator))
    except TimeoutException:
        return None
    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        try:
            if plate.strip().casefold() in " ".join((row.text or "").split()).casefold():
                return row
        except Exception:
            continue
    return None


def extract_table_rows(driver, table_locator, timeout: int = 10) -> list[str]:
    """Đọc toàn bộ text từng dòng của bảng — dùng cho so sánh mismatch/missing/unexpected."""
    wait = WebDriverWait(driver, timeout)
    try:
        table = wait.until(EC.presence_of_element_located(table_locator))
    except TimeoutException:
        return []
    rows = []
    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        try:
            rows.append(" ".join((row.text or "").split()))
        except Exception:
            continue
    return rows
