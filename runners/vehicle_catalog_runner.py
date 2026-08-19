"""Selenium runner cho module Danh mục xe (phần Linh).

- Tự dùng session Chrome hiện có; nếu bị chuyển về /login thì đăng nhập bằng Config.
- Check locator có thể tự mở modal Hãng/Mẫu trước khi tìm element.
- CRUD demo tập trung Create/Read + mapping Dropdown + cleanup best-effort.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Config
from core.driver_factory import DriverFactory
from pages.category_page import CategoryPage




PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CREDENTIAL_FILE = PROJECT_ROOT / ".autotest.env"


def _read_simple_env(path: Path) -> dict[str, str]:
    """Đọc file KEY=VALUE đơn giản, không cần python-dotenv."""
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


def _load_catalog_credentials() -> tuple[str, str]:
    """Lấy tài khoản test từ biến môi trường hoặc .autotest.env cục bộ."""
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


def _first_visible(driver, candidates):
    for by, value in candidates:
        try:
            for element in driver.find_elements(by, value):
                if element.is_displayed():
                    return element
        except Exception:
            continue
    return None


def _submit_login_form(driver, email_text: str, password_text: str, timeout: int = 15) -> bool:
    """Tự điền form login, hỗ trợ nhiều kiểu input/SPA và có fallback bằng JavaScript."""
    if not email_text or not password_text:
        print("[LOGIN] Thiếu email hoặc password.")
        return False

    wait = WebDriverWait(driver, timeout)

    # Chờ DOM load xong để tránh tìm input quá sớm.
    try:
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    except Exception:
        pass
    time.sleep(0.8)

    email_candidates = [
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[name='email']"),
        (By.CSS_SELECTOR, "input[id='email']"),
        (By.CSS_SELECTOR, "input[autocomplete='email']"),
        (By.CSS_SELECTOR, "input[placeholder*='plt.pro.vn']"),
        (By.CSS_SELECTOR, "input[placeholder*='Email']"),
        (By.CSS_SELECTOR, "input[placeholder*='email']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Email')]/following::input[1]"),
        (By.XPATH, "//input[contains(@placeholder,'plt.pro.vn')]"),
    ]

    password_candidates = [
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "input[id='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        (By.CSS_SELECTOR, "input[placeholder*='mật khẩu']"),
        (By.CSS_SELECTOR, "input[placeholder*='Mật khẩu']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Mật khẩu')]/following::input[1]"),
        (By.XPATH, "//input[@type='password']"),
    ]

    button_candidates = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(normalize-space(.),'Đăng nhập')]"),
        (By.XPATH, "//*[@role='button' and contains(normalize-space(.),'Đăng nhập')]"),
        (By.XPATH, "//button[contains(normalize-space(.),'Login')]"),
    ]

    end = time.monotonic() + max(5, timeout)
    email_el = password_el = button_el = None

    while time.monotonic() < end:
        email_el = _first_visible(driver, email_candidates)
        password_el = _first_visible(driver, password_candidates)
        button_el = _first_visible(driver, button_candidates)

        if email_el and password_el and button_el:
            break

        time.sleep(0.25)

    print(
        "[LOGIN] Element:",
        f"email={'OK' if email_el else 'MISS'}",
        f"password={'OK' if password_el else 'MISS'}",
        f"button={'OK' if button_el else 'MISS'}",
    )

    if not (email_el and password_el and button_el):
        return False

    def set_input_value(element, value: str) -> bool:
        """Nhập bằng Selenium; nếu SPA/React không nhận thì fallback bằng JS native setter."""
        try:
            element.click()
        except Exception:
            try:
                driver.execute_script("arguments[0].focus();", element)
            except Exception:
                pass

        try:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            element.send_keys(value)
        except Exception:
            try:
                element.clear()
                element.send_keys(value)
            except Exception:
                pass

        current = element.get_attribute("value") or ""
        if current == value:
            return True

        # React/Vue/SPA đôi khi bỏ qua clear()/send_keys(); dùng native setter + events.
        try:
            driver.execute_script(
                """
                const el = arguments[0];
                const value = arguments[1];

                const proto = Object.getPrototypeOf(el);
                const descriptor =
                    Object.getOwnPropertyDescriptor(proto, 'value') ||
                    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');

                if (descriptor && descriptor.set) {
                    descriptor.set.call(el, value);
                } else {
                    el.value = value;
                }

                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
                """,
                element,
                value,
            )
        except Exception:
            return False

        return (element.get_attribute("value") or "") == value

    email_ok = set_input_value(email_el, email_text)
    password_ok = set_input_value(password_el, password_text)

    print(
        "[LOGIN] Nhập dữ liệu:",
        f"email={'OK' if email_ok else 'FAIL'}",
        f"password={'OK' if password_ok else 'FAIL'}",
    )

    if not (email_ok and password_ok):
        return False

    # Cho SPA cập nhật state trước khi submit.
    time.sleep(0.4)

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});",
            button_el,
        )
    except Exception:
        pass

    try:
        _safe_click(driver, button_el)
    except Exception:
        try:
            password_el.send_keys(Keys.ENTER)
        except Exception:
            return False

    print("[LOGIN] Đã bấm Đăng nhập.")
    return True


def _log(worker, text: str, progress: int | None = None):
    if worker:
        worker.log_signal.emit(text)
        if progress is not None:
            worker.progress_signal.emit(progress)


def _step(expected: str, actual: str, passed: bool, note: str = "") -> dict[str, str]:
    return {
        "expected": expected,
        "actual": actual,
        "result": "PASS" if passed else "FAIL",
        "note": note,
    }


def _is_login(driver) -> bool:
    current = (driver.current_url or "").lower()
    if "/login" in current:
        return True
    try:
        return bool(driver.find_elements(By.CSS_SELECTOR, "input[type='password']"))
    except Exception:
        return False


def _login_if_needed(driver, target_url: str, worker=None, timeout: int = 25):
    _log(worker, f"[DANH MỤC XE] Mở {target_url}", 15)
    driver.get(target_url)

    # QUAN TRỌNG:
    # Fleet Console là SPA nên sau driver.get(target_url), URL có thể vẫn tạm thời
    # là /cars/catalog rồi vài nhịp sau mới redirect sang /login.
    # Code cũ check quá sớm nên tưởng đã đăng nhập và return luôn -> không nhập email/password.
    wait = WebDriverWait(driver, timeout)

    def page_state(d):
        if _is_login(d):
            return "login"
        try:
            if d.find_elements(*CategoryPage.PAGE_TITLE):
                return "catalog"
        except Exception:
            pass
        return False

    try:
        state = wait.until(page_state)
    except TimeoutException:
        # Fallback: kiểm tra lại URL/form lần cuối.
        state = "login" if _is_login(driver) else "unknown"

    print(f"[LOGIN] Trạng thái sau khi mở trang: {state} | URL={driver.current_url}")

    # Nếu đã có session và vào thẳng Danh mục xe thì không cần login.
    if state == "catalog" and not _is_login(driver):
        _log(worker, "[DANH MỤC XE] Session còn hiệu lực, không cần đăng nhập.", 30)
        return

    # Nếu chưa nhận diện được nhưng URL đã về login thì vẫn chạy login.
    if state != "login" and not _is_login(driver):
        raise RuntimeError(
            f"Không xác định được trạng thái trang sau khi mở {target_url}. "
            f"URL hiện tại: {driver.current_url}"
        )

    email_text, password_text = _load_catalog_credentials()
    if not email_text or not password_text:
        raise RuntimeError(
            "Thiếu tài khoản tự đăng nhập. Hãy tạo .autotest.env ở cùng cấp main.py "
            "với TEST_EMAIL và TEST_PASSWORD."
        )

    _log(worker, "[DANH MỤC XE] Chưa có session, đang tự đăng nhập...", 25)
    print(f"[LOGIN] Bắt đầu auto-login với email: {email_text}")

    if not _submit_login_form(driver, email_text, password_text, timeout=timeout):
        raise RuntimeError(
            "Không tự điền được form đăng nhập. "
            "Xem các dòng [LOGIN] trong Terminal để biết element nào bị MISS/FAIL."
        )

    # Chờ rời khỏi trang login sau khi đã bấm nút.
    try:
        wait.until(lambda d: not _is_login(d))
    except TimeoutException as exc:
        raise RuntimeError(
            "Đã nhập Email/Mật khẩu và bấm Đăng nhập nhưng vẫn còn ở trang login. "
            "Kiểm tra TEST_EMAIL/TEST_PASSWORD hoặc thông báo lỗi trên website."
        ) from exc

    # Firebase/SPA cần một nhịp để persist auth trước khi điều hướng lại.
    time.sleep(2.0)
    driver.get(target_url)

    try:
        wait.until(EC.presence_of_element_located(CategoryPage.PAGE_TITLE))
    except TimeoutException as exc:
        if _is_login(driver):
            raise RuntimeError(
                "Đăng nhập xong nhưng session chưa hợp lệ; kiểm tra tài khoản test hoặc chạy lại."
            ) from exc
        raise

    _log(worker, "[DANH MỤC XE] Đăng nhập xong, bắt đầu kiểm thử.", 35)


def _visible_modal(driver):
    for modal in driver.find_elements(By.CSS_SELECTOR, "div.ant-modal"):
        try:
            if modal.is_displayed():
                return modal
        except Exception:
            pass
    return None


def _safe_click(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def _choose_ant_option(driver, combo, text: str, timeout: int = 15) -> bool:
    """Chọn option Ant Design bằng text, không dùng Selenium Select."""
    try:
        combo.click()
    except Exception:
        driver.execute_script("arguments[0].click();", combo)

    try:
        combo.send_keys(Keys.CONTROL, "a")
        combo.send_keys(text)
    except Exception:
        pass

    wait = WebDriverWait(driver, timeout)

    def find_option(d):
        options = d.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option",
        )
        for option in options:
            try:
                if option.is_displayed() and option.text.strip().casefold() == text.strip().casefold():
                    return option
            except Exception:
                continue
        return False

    try:
        option = wait.until(find_option)
        _safe_click(driver, option)
        try:
            combo.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return True
    except TimeoutException:
        return False


def _section_has_text(driver, section_locator, text: str) -> bool:
    try:
        section = driver.find_element(*section_locator)
        return text.strip().casefold() in " ".join(section.text.split()).casefold()
    except Exception:
        return False


def _open_scope(driver, scope: str, timeout: int = 15):
    wait = WebDriverWait(driver, timeout)
    if scope == "brand_modal":
        button = wait.until(EC.element_to_be_clickable(CategoryPage.ADD_BRAND_BTN))
        _safe_click(driver, button)
        wait.until(lambda d: _visible_modal(d) is not None)
    elif scope == "model_modal":
        button = wait.until(EC.element_to_be_clickable(CategoryPage.ADD_MODEL_BTN))
        _safe_click(driver, button)
        wait.until(lambda d: _visible_modal(d) is not None)


def run_catalog_locator_test(
    worker=None,
    locator_type: str = "XPATH",
    locator_value: str = "",
    scope: str = "page",
    show_browser: bool = True,
):
    driver = None
    try:
        driver = DriverFactory.create_driver(headless=not show_browser, keep_session=True)
        _login_if_needed(driver, CategoryPage.URL, worker)
        _open_scope(driver, scope)

        by_map = {
            "XPATH": By.XPATH,
            "CSS": By.CSS_SELECTOR,
            "ID": By.ID,
            "NAME": By.NAME,
            "CLASS_NAME": By.CLASS_NAME,
            "TAG_NAME": By.TAG_NAME,
        }
        by = by_map.get(locator_type.upper(), By.XPATH)
        _log(worker, f"[LOCATOR] {locator_type}: {locator_value}", 60)
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, locator_value))
        )
        try:
            driver.execute_script(
                "arguments[0].style.outline='3px solid #2563eb';"
                "arguments[0].scrollIntoView({block:'center'});",
                element,
            )
        except Exception:
            pass
        _log(worker, "[LOCATOR] PASS - tìm thấy element.", 100)
        return {
            "status": "PASSED",
            "message": "Tìm thấy element với locator đã chọn.",
            "actual": (element.text or element.get_attribute("value") or element.tag_name)[:200],
        }
    except Exception as exc:
        return {
            "status": "FAILED",
            "message": f"Không tìm thấy element: {exc.__class__.__name__}",
            "error": str(exc),
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _cleanup_created_row(driver, section_locator, name: str, timeout: int = 8) -> str:
    """Cleanup best-effort. Không làm FAIL cả test nếu giao diện không có nút xóa."""
    try:
        section = driver.find_element(*section_locator)
        rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
        target = None
        for row in rows:
            if name.strip().casefold() in " ".join((row.text or "").split()).casefold():
                target = row
                break
        if target is None:
            return "Không thấy dòng để cleanup"

        buttons = target.find_elements(By.TAG_NAME, "button")
        if not buttons:
            return "Trang không có nút thao tác cleanup"
        _safe_click(driver, buttons[-1])
        WebDriverWait(driver, timeout).until(lambda d: _visible_modal(d) is not None)
        modal = _visible_modal(driver)
        if not modal:
            return "Không mở được modal chỉnh sửa"

        delete_buttons = modal.find_elements(
            By.XPATH,
            ".//button[.//span[contains(normalize-space(.),'Xóa')] or contains(normalize-space(.),'Xóa')]",
        )
        if not delete_buttons:
            # Đóng modal để không cản browser.
            close_buttons = modal.find_elements(By.CSS_SELECTOR, "button.ant-modal-close")
            if close_buttons:
                _safe_click(driver, close_buttons[0])
            return "Không có nút Xóa; cần cleanup thủ công"

        _safe_click(driver, delete_buttons[0])
        time.sleep(0.8)
        confirmations = driver.find_elements(
            By.XPATH,
            "//button[.//span[contains(normalize-space(.),'Xóa')] or normalize-space()='Xóa']",
        )
        for button in confirmations:
            try:
                if button.is_displayed():
                    _safe_click(driver, button)
                    break
            except Exception:
                pass
        return "Đã thử cleanup dữ liệu test"
    except Exception as exc:
        return f"Cleanup best-effort: {exc.__class__.__name__}"


def run_catalog_crud_test(
    worker=None,
    kind: str = "brand",
    name: str = "LINH_AUTO_TEST",
    brand: str = "VinFast",
    cleanup: bool = True,
    show_browser: bool = True,
):
    driver = None
    steps: list[dict[str, str]] = []
    try:
        driver = DriverFactory.create_driver(headless=not show_browser, keep_session=True)
        wait = WebDriverWait(driver, 18)
        _login_if_needed(driver, CategoryPage.URL, worker)

        is_model = kind == "model"
        group_label = "Mẫu xe" if is_model else "Hãng xe"
        add_locator = CategoryPage.ADD_MODEL_BTN if is_model else CategoryPage.ADD_BRAND_BTN
        name_locator = CategoryPage.MODEL_NAME_INPUT if is_model else CategoryPage.BRAND_NAME_INPUT
        create_locator = CategoryPage.CREATE_MODEL_BTN if is_model else CategoryPage.CREATE_BRAND_BTN
        section_locator = CategoryPage.MODEL_SECTION if is_model else CategoryPage.BRAND_SECTION

        _log(worker, f"[{group_label}] Mở form Thêm...", 45)
        add_button = wait.until(EC.element_to_be_clickable(add_locator))
        _safe_click(driver, add_button)
        wait.until(lambda d: _visible_modal(d) is not None)
        steps.append(_step("Mở được form Thêm", "Đã mở modal", True))

        name_input = wait.until(EC.visibility_of_element_located(name_locator))
        name_input.clear()
        name_input.send_keys(name)
        actual_name = name_input.get_attribute("value") or ""
        steps.append(_step(name, actual_name, actual_name.strip() == name.strip()))

        if is_model:
            _log(worker, "[Mẫu xe] Chọn Hãng liên kết...", 55)
            combo = wait.until(EC.visibility_of_element_located(CategoryPage.MODEL_BRAND_COMBO))
            selected = _choose_ant_option(driver, combo, brand)
            steps.append(
                _step(
                    brand,
                    brand if selected else "Không chọn được option",
                    selected,
                    "Ant Design dropdown",
                )
            )

        _log(worker, f"[{group_label}] Tạo dữ liệu test...", 65)
        create_button = wait.until(EC.presence_of_element_located(create_locator))
        _safe_click(driver, create_button)
        time.sleep(1.2)

        _log(worker, f"[{group_label}] Đối chiếu bảng...", 75)
        found = WebDriverWait(driver, 15).until(
            lambda d: _section_has_text(d, section_locator, name)
        )
        steps.append(
            _step(
                f"'{name}' xuất hiện trong bảng",
                "Có" if found else "Không thấy",
                bool(found),
            )
        )

        if is_model:
            section = driver.find_element(*CategoryPage.MODEL_SECTION)
            row_text = ""
            for row in section.find_elements(By.CSS_SELECTOR, "tbody tr"):
                line = " ".join((row.text or "").split())
                if name.casefold() in line.casefold():
                    row_text = line
                    break
            mapped = bool(row_text and brand.casefold() in row_text.casefold())
            steps.append(
                _step(
                    f"{name} thuộc Hãng {brand}",
                    row_text or "Không thấy dòng mẫu xe",
                    mapped,
                )
            )
        else:
            _log(worker, "[Hãng xe] Kiểm tra dropdown lọc Mẫu xe cập nhật...", 82)
            combo = wait.until(EC.presence_of_element_located(CategoryPage.MODEL_FILTER_COMBO))
            option_ok = _choose_ant_option(driver, combo, name)
            steps.append(
                _step(
                    f"Dropdown có Hãng '{name}'",
                    name if option_ok else "Không thấy option",
                    option_ok,
                )
            )
            try:
                combo.send_keys(Keys.ESCAPE)
            except Exception:
                pass

        cleanup_note = ""
        if cleanup:
            _log(worker, f"[{group_label}] Cleanup dữ liệu test...", 90)
            cleanup_note = _cleanup_created_row(driver, section_locator, name)

        passed = all(step["result"] == "PASS" for step in steps)
        return {
            "status": "PASSED" if passed else "FAILED",
            "message": f"{group_label}: {'PASS' if passed else 'có bước FAIL'}. {cleanup_note}".strip(),
            "steps": steps,
        }
    except Exception as exc:
        return {
            "status": "FAILED",
            "message": f"Selenium gặp lỗi: {exc.__class__.__name__}",
            "error": str(exc),
            "steps": steps,
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
