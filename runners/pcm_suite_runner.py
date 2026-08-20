"""Selenium scenarios for the built-in TestCase_PCM suite."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Config
from core.driver_factory import DriverFactory
from core.helpers.utils import capture_screenshot, get_logger
from pages.category_page import CategoryPage
from runners.text_dropdown_runner import _ensure_logged_in
from runners.vehicle_catalog_runner import run_catalog_crud_test


logger = get_logger()
STEP_DELAY = 1.6
CLOSE_DELAY = 3.0

SUPPORTED_SCENARIOS = {
    "login_admin_success", "login_staff_success", "login_wrong_password",
    "login_blank_email", "login_blank_password", "login_toggle_password",
    "dashboard_title", "dashboard_cards", "dashboard_sidebar", "dashboard_create_booking",
    "booking_table_headers", "booking_search", "booking_view_toggle", "booking_create_form",
    "booking_edit_draft", "booking_delete_draft", "booking_delete_protected",
    "fleet_table_headers", "fleet_dependent_model", "fleet_status_filter", "fleet_edit_form",
    "fleet_delete_flow", "fleet_stats", "fleet_booking_code",
    "catalog_create_brand", "catalog_create_model", "catalog_toggle_brand", "catalog_input_security",
    "user_duplicate_email", "user_role_form", "user_toggle_status",
}


class ScenarioFailure(AssertionError):
    pass


class ScenarioConfigurationError(RuntimeError):
    pass


def _visible(driver, xpath: str, timeout: int = 12):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )


def _clickable(driver, xpath: str, timeout: int = 12):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )


def _highlight(driver, element):
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});"
            "arguments[0].style.outline='3px solid #ef4444';"
            "arguments[0].style.outlineOffset='3px';",
            element,
        )
    except Exception:
        pass
    time.sleep(STEP_DELAY)


def _body_text(driver) -> str:
    return driver.find_element(By.TAG_NAME, "body").text or ""


def _normal(value: str) -> str:
    return " ".join((value or "").lower().split())


def _assert_contains(actual: str, expected_values: list[str]):
    normal_actual = _normal(actual)
    missing = [value for value in expected_values if _normal(value) not in normal_actual]
    if missing:
        raise ScenarioFailure(f"Thiếu nội dung: {', '.join(missing)}")


def _cancel_dialog(driver):
    candidates = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "//button[.//*[normalize-space()='Hủy'] or normalize-space()='Hủy' or @aria-label='Close']",
    )
    for button in candidates:
        if button.is_displayed():
            button.click()
            return
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass


def _open_and_login(driver, url: str):
    driver.get(url)
    _ensure_logged_in(driver, url)
    WebDriverWait(driver, Config.PAGE_LOAD_TIMEOUT).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(STEP_DELAY)


def _login_fields(driver):
    email = _visible(
        driver,
        "//input[@type='email' or @name='email' or @name='username' or @type='text'][1]",
    )
    password = _visible(driver, "//input[@type='password' or @name='password'][1]")
    submit = _clickable(driver, "//button[@type='submit'] | //input[@type='submit']")
    return email, password, submit


def _type(element, value: str):
    element.click()
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(Keys.BACKSPACE)
    if value:
        element.send_keys(value)


def _login_scenario(driver, key: str) -> str:
    driver.get(Config.BASE_URL)
    email, password, submit = _login_fields(driver)
    _highlight(driver, email)

    if key == "login_staff_success":
        username = os.getenv("TEST_STAFF_EMAIL", "").strip()
        secret = os.getenv("TEST_STAFF_PASSWORD", "").strip()
        if not username or not secret:
            raise ScenarioConfigurationError(
                "Thiếu TEST_STAFF_EMAIL/TEST_STAFF_PASSWORD cho TC02"
            )
    else:
        username, secret = Config.TEST_EMAIL, Config.TEST_PASSWORD

    if key == "login_wrong_password":
        secret = f"{secret}_WRONG"
    elif key == "login_blank_email":
        username = ""
    elif key == "login_blank_password":
        secret = ""

    _type(email, username)
    _type(password, secret)

    if key == "login_toggle_password":
        toggle = _clickable(
            driver,
            "//input[@type='password' or @name='password']/following::*[self::button or @role='button'][1]"
            " | //input[@type='password' or @name='password']/parent::*//button",
        )
        before = password.get_attribute("type")
        _highlight(driver, toggle)
        toggle.click()
        time.sleep(STEP_DELAY)
        after = password.get_attribute("type")
        if before == after:
            raise ScenarioFailure(f"Kiểu password không đổi: {before}")
        return f"type: {before} → {after}"

    _highlight(driver, submit)
    submit.click()
    time.sleep(2.5)

    if key in {"login_admin_success", "login_staff_success"}:
        if "login" in driver.current_url.lower():
            raise ScenarioFailure("Đăng nhập không điều hướng khỏi trang login")
        return driver.current_url

    if key in {"login_blank_email", "login_blank_password"}:
        target = email if key == "login_blank_email" else password
        invalid = driver.execute_script("return !arguments[0].validity.valid;", target)
        error_text = _body_text(driver)
        if not invalid and not any(word in _normal(error_text) for word in ("bắt buộc", "required", "vui lòng")):
            raise ScenarioFailure("Không thấy validation bắt buộc")
        return "HTML validation hoặc thông báo bắt buộc hiển thị"

    error_text = _body_text(driver)
    if "login" not in driver.current_url.lower():
        raise ScenarioFailure("Mật khẩu sai nhưng hệ thống vẫn cho đăng nhập")
    if not any(word in _normal(error_text) for word in ("sai", "không đúng", "invalid", "error", "thất bại")):
        raise ScenarioFailure("Vẫn ở login nhưng không thấy thông báo lỗi")
    return "Đăng nhập sai bị từ chối"


def _dashboard_scenario(driver, key: str) -> str:
    if key == "dashboard_title":
        element = _visible(
            driver,
            "//main//*[self::h1 or self::h2 or self::h3][contains(.,'Dashboard') or contains(.,'Bảng điều khiển')]",
        )
        _highlight(driver, element)
        return element.text

    if key == "dashboard_cards":
        body = _body_text(driver)
        labels = [
            "XE ĐANG CHO THUÊ", "XE SẴN SÀNG HÔM NAY", "NHẬN XE", "TRẢ XE",
            "BOOKING TRỄ HẠN", "BẢO DƯỠNG", "NHÂN SỰ",
        ]
        matches = [label for label in labels if _normal(label) in _normal(body)]
        number_elements = driver.find_elements(By.XPATH, "//main//*[self::span or self::div or self::p]")
        visible_numbers = [
            element for element in number_elements
            if element.is_displayed() and re.fullmatch(r"\d+", (element.text or "").strip())
        ]
        if len(matches) < 6 or len(visible_numbers) < 8:
            raise ScenarioFailure(
                f"Chỉ nhận diện {len(matches)} nhóm nhãn và {len(visible_numbers)} số liệu"
            )
        return f"{len(matches)} nhóm nhãn; {len(visible_numbers)} số liệu"

    if key == "dashboard_sidebar":
        sidebar = _visible(driver, "//aside | //ul[@role='menu']")
        text = sidebar.text
        _assert_contains(text, ["Dashboard", "Đặt xe", "Xe", "Danh mục xe", "Tài chính", "Người dùng"])
        links = sidebar.find_elements(By.XPATH, ".//a[@href]")
        hrefs = [link.get_attribute("href") for link in links]
        if len([href for href in hrefs if href]) < 6:
            raise ScenarioFailure("Menu chưa có đủ href điều hướng")
        _highlight(driver, sidebar)
        return " | ".join(hrefs)

    button = _clickable(
        driver,
        "//main//button[contains(.,'Tạo booking')] | //main//a[contains(.,'Tạo booking')]",
    )
    _highlight(driver, button)
    button.click()
    WebDriverWait(driver, 12).until(
        lambda d: "booking" in d.current_url.lower()
    )
    return driver.current_url


def _table_headers(driver) -> str:
    headers = [element.text.strip() for element in driver.find_elements(By.CSS_SELECTOR, "table thead th")]
    return " | ".join(value for value in headers if value)


def _booking_scenario(driver, key: str) -> str:
    if key == "booking_table_headers":
        actual = _table_headers(driver)
        _assert_contains(actual, ["Booking", "Xe", "Lịch trình", "Trạng thái", "Thanh toán", "Tệp", "Tổng tiền", "Thao tác"])
        return actual

    if key == "booking_search":
        page_text = _body_text(driver)
        codes = re.findall(r"BK-[A-Z0-9-]+", page_text, flags=re.IGNORECASE)
        if not codes:
            raise ScenarioFailure("Không có mã booking mẫu để tìm kiếm")
        code = codes[0]
        search = _visible(driver, "//input[@type='search' or contains(@placeholder,'Tìm') or contains(@placeholder,'Search')]")
        _highlight(driver, search)
        _type(search, code)
        search.send_keys(Keys.ENTER)
        time.sleep(2)
        if code.lower() not in _body_text(driver).lower():
            raise ScenarioFailure(f"Kết quả không chứa {code}")
        return code

    if key == "booking_view_toggle":
        list_button = _clickable(driver, "//button[contains(.,'Dạng danh sách')] | //*[@role='tab' and contains(.,'Danh sách')]")
        calendar_button = _clickable(driver, "//button[contains(.,'Dạng lịch')] | //*[@role='tab' and contains(.,'Lịch')]")
        _highlight(driver, calendar_button)
        calendar_button.click(); time.sleep(2)
        calendar_visible = bool(driver.find_elements(By.CSS_SELECTOR, ".ant-picker-calendar, [class*='calendar']"))
        list_button.click(); time.sleep(2)
        list_visible = bool(driver.find_elements(By.CSS_SELECTOR, "table, [class*='list']"))
        if not calendar_visible or not list_visible:
            raise ScenarioFailure(f"calendar={calendar_visible}, list={list_visible}")
        return "Dạng lịch và Dạng danh sách đều hiển thị"

    if key == "booking_create_form":
        button = _clickable(driver, "//button[contains(.,'Tạo booking') or contains(.,'Thêm booking')] | //a[contains(.,'Tạo booking')]")
        _highlight(driver, button); button.click(); time.sleep(2)
        form = _visible(driver, "//form | //div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]")
        inputs = form.find_elements(By.XPATH, ".//input | .//*[@role='combobox'] | .//textarea")
        if len(inputs) < 3:
            raise ScenarioFailure(f"Form chỉ có {len(inputs)} trường")
        return f"Form tạo booking có {len(inputs)} trường"

    row_state = "Nháp" if key in {"booking_edit_draft", "booking_delete_draft"} else ""
    if key in {"booking_edit_draft", "booking_delete_draft"}:
        row = _visible(driver, f"//tbody/tr[contains(.,'{row_state}')][1]")
        action_text = "Sửa" if key == "booking_edit_draft" else "Xóa"
        action = row.find_elements(
            By.XPATH,
            f".//button[contains(@aria-label,'{action_text}') or contains(@title,'{action_text}') or contains(.,'{action_text}')]",
        )
        if not action:
            raise ScenarioFailure(f"Không thấy nút {action_text} trên booking Nháp")
        _highlight(driver, action[0]); action[0].click(); time.sleep(1.5)
        dialog = _visible(driver, "//form | //div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]")
        result = dialog.text
        _cancel_dialog(driver)
        return result

    protected = _visible(driver, "//tbody/tr[contains(.,'Đã xác nhận') or contains(.,'Đã thanh toán')][1]")
    delete_buttons = protected.find_elements(
        By.XPATH, ".//button[contains(@aria-label,'Xóa') or contains(@title,'Xóa') or contains(.,'Xóa')]"
    )
    if delete_buttons and any(button.is_enabled() for button in delete_buttons):
        raise ScenarioFailure("Booking đã xác nhận vẫn có nút Xóa khả dụng")
    return "Không có nút Xóa khả dụng"


def _fleet_scenario(driver, key: str) -> str:
    if key == "fleet_table_headers":
        actual = _table_headers(driver)
        _assert_contains(actual, ["Ảnh", "Xe", "Thông số", "Trạng thái", "Đơn đang thuê", "Thao tác"])
        return actual

    if key == "fleet_dependent_model":
        add = _clickable(driver, "//button[contains(normalize-space(.),'Thêm xe')]")
        _highlight(driver, add); add.click(); time.sleep(1.5)
        form = _visible(driver, "//form | //div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]")
        combos = form.find_elements(By.XPATH, ".//*[@role='combobox']")
        if len(combos) < 2:
            raise ScenarioFailure("Không thấy dropdown Hãng xe và Mẫu xe")
        combos[0].click(); time.sleep(1)
        options = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option")
        if not options:
            raise ScenarioFailure("Dropdown Hãng xe không có dữ liệu")
        options[0].click(); time.sleep(1.5)
        combos[1].click(); time.sleep(1)
        model_options = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option")
        if not model_options:
            raise ScenarioFailure("Dropdown Mẫu xe không cập nhật")
        _cancel_dialog(driver)
        return f"Hãng có dữ liệu; Mẫu xe có {len(model_options)} option"

    if key == "fleet_status_filter":
        trigger = _clickable(driver, "//th[contains(.,'Trạng thái')]//*[contains(@class,'filter-trigger')] | //*[@role='combobox'][contains(@aria-label,'trạng thái')]")
        _highlight(driver, trigger); trigger.click(); time.sleep(1)
        overlay = _body_text(driver)
        _assert_contains(overlay, ["Sẵn sàng", "Đang vệ sinh", "Đang bảo dưỡng"])
        return "Sẵn sàng | Đang vệ sinh | Đang bảo dưỡng"

    if key == "fleet_edit_form":
        edit = _clickable(driver, "(//tbody//button[contains(@aria-label,'Chỉnh sửa') or contains(@title,'Sửa')])[1]")
        _highlight(driver, edit); edit.click(); time.sleep(1.5)
        form_text = _visible(driver, "//form | //div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]").text
        _assert_contains(form_text, ["Năm", "Màu", "Nhiên liệu"])
        _cancel_dialog(driver)
        return form_text

    if key == "fleet_delete_flow":
        delete = _clickable(driver, "(//tbody//button[contains(@aria-label,'Xóa') or contains(@title,'Xóa')])[1]")
        _highlight(driver, delete); delete.click(); time.sleep(1)
        confirm = _visible(driver, "//*[contains(@class,'ant-popconfirm') or contains(@class,'ant-modal')][contains(.,'Xóa')]")
        text = confirm.text
        _cancel_dialog(driver)
        return text

    if key == "fleet_stats":
        body = _body_text(driver)
        values = []
        for label in ("Tất cả xe", "Sẵn sàng hôm nay", "Đang bảo dưỡng"):
            label_element = _visible(driver, f"//*[contains(normalize-space(.),'{label}')][1]")
            candidates = label_element.find_elements(By.XPATH, "following::*[position() <= 12]")
            number = next(
                (
                    int(candidate.text.strip())
                    for candidate in candidates
                    if re.fullmatch(r"\d+", (candidate.text or "").strip())
                ),
                None,
            )
            if number is None:
                raise ScenarioFailure(f"Không đọc được KPI {label}")
            values.append(number)
        rows = len(driver.find_elements(By.CSS_SELECTOR, "tbody tr.ant-table-row, tbody tr"))
        if values[0] < rows:
            raise ScenarioFailure(f"Tổng số xe {values[0]} nhỏ hơn {rows} dòng hiển thị")
        return f"KPI={values}; rows={rows}; page={len(body)} chars"

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    for row in rows:
        text = row.text
        if "đang thuê" in _normal(text) and re.search(r"BK-[A-Z0-9-]+", text, re.I):
            _highlight(driver, row)
            return text
    raise ScenarioFailure(
        "Không thấy xe nào ở trạng thái 'Đang thuê' có mã booking (BK-...) trong "
        "dữ liệu hiện tại. Đây là assertion phụ thuộc dữ liệu: cần có ít nhất 1 xe "
        "đang được thuê (tạo qua module Đặt xe) tại thời điểm chạy để kiểm tra được."
    )


def _catalog_scenario(case: dict) -> dict | None:
    key = case["scenario_key"]
    stamp = datetime.now().strftime("%H%M%S")
    if key == "catalog_create_brand":
        return run_catalog_crud_test(kind="brand", name=f"AUTO_BRAND_{stamp}", cleanup=True, show_browser=True)
    if key == "catalog_create_model":
        return run_catalog_crud_test(kind="model", name=f"AUTO_MODEL_{stamp}", brand="VinFast", cleanup=True, show_browser=True)
    return None


def _catalog_ui_scenario(driver, key: str) -> str:
    if key == "catalog_toggle_brand":
        row = _visible(driver, "(//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]//tbody/tr)[1]")
        edit = row.find_elements(By.XPATH, ".//button[contains(@aria-label,'Sửa') or contains(@title,'Sửa') or contains(.,'Sửa')]")
        if not edit:
            raise ScenarioFailure("Không thấy nút chỉnh sửa hãng")
        _highlight(driver, edit[0]); edit[0].click(); time.sleep(1)
        switch = _visible(driver, "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]//*[@role='switch'] | //div[contains(@class,'ant-modal')]//button[contains(@class,'ant-switch')]")
        before = switch.get_attribute("aria-checked") or switch.get_attribute("class")
        switch.click(); time.sleep(1); switch.click()
        _cancel_dialog(driver)
        return f"Đã đổi và khôi phục switch; initial={before}"

    add = _clickable(driver, CategoryPage.ADD_BRAND_BTN[1])
    _highlight(driver, add); add.click()
    input_element = _visible(driver, CategoryPage.BRAND_NAME_INPUT[1])
    suspicious = "AUTO_<script>' OR 1=1 --"
    _type(input_element, suspicious)
    value = input_element.get_attribute("value") or ""
    if value != suspicious:
        raise ScenarioFailure("Input làm biến đổi dữ liệu trước khi submit")
    table_before = bool(driver.find_elements(*CategoryPage.BRAND_TABLE))
    _cancel_dialog(driver)
    table_after = bool(driver.find_elements(*CategoryPage.BRAND_TABLE))
    if not table_before or not table_after:
        raise ScenarioFailure("Bảng hãng xe bị mất sau dữ liệu đặc biệt")
    return "Chuỗi được giữ như text; DOM bảng vẫn an toàn; không submit dữ liệu"


def _user_scenario(driver, key: str) -> str:
    create = "//a[contains(@href,'/users/new')]//button | //button[contains(.,'Tạo người dùng')]"
    if key in {"user_duplicate_email", "user_role_form"}:
        button = _clickable(driver, create)
        _highlight(driver, button); button.click(); time.sleep(1.5)
        form = _visible(driver, "//form")

        if key == "user_role_form":
            role = _visible(driver, "//form//*[contains(.,'Vai trò')]/following::*[@role='combobox'][1] | //form//*[@role='combobox'][1]")
            role.click(); time.sleep(1)
            options = " ".join(element.text for element in driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option"))
            _assert_contains(options, ["Quản Trị Viên", "Nhân Viên"])
            return options

        email = _visible(driver, "//form//input[@type='email' or @name='email']")
        _type(email, Config.TEST_EMAIL)
        submit = _clickable(driver, "//form//button[@type='submit']")
        submit.click(); time.sleep(2)
        body = _body_text(driver)
        if not any(word in _normal(body) for word in ("đã tồn tại", "trùng", "already exists", "duplicate")):
            raise ScenarioFailure("Không thấy lỗi email trùng")
        return "Email trùng bị từ chối"

    row = _visible(driver, "(//tbody/tr)[1]")
    switch_candidates = row.find_elements(By.XPATH, ".//*[@role='switch'] | .//button[contains(@class,'ant-switch')]")
    if not switch_candidates:
        raise ScenarioFailure("Không thấy điều khiển trạng thái người dùng")
    switch = switch_candidates[0]
    before = switch.get_attribute("aria-checked") or switch.get_attribute("class")
    _highlight(driver, switch); switch.click(); time.sleep(1.2); switch.click()
    return f"Đã đổi và khôi phục; initial={before}"


def run_pcm_scenario(case: dict, stop_requested=None, driver=None) -> dict:
    """Execute one built-in PCM scenario and return a suite-result payload."""
    started = datetime.now()
    key = case.get("scenario_key", "")
    if key not in SUPPORTED_SCENARIOS:
        finished = datetime.now()
        return {
            "case_id": case.get("tc_id", ""), "title": case.get("title", ""),
            "module": case.get("module", ""), "page_key": case.get("page_key", ""),
            "expected": case.get("expected", ""), "actual": "",
            "status": "ERROR", "message": "Scenario chưa được hỗ trợ",
            "error_message": f"Scenario chưa được ánh xạ: {key}", "screenshot_path": "",
            "log_text": f"CONFIG ERROR: {key}",
            "started_at": started.isoformat(timespec="seconds"),
            "finished_at": finished.isoformat(timespec="seconds"),
            "duration_ms": int((finished - started).total_seconds() * 1000),
        }
    direct_catalog = _catalog_scenario(case)
    if direct_catalog is not None:
        finished = datetime.now()
        return {
            "case_id": case.get("tc_id", ""), "title": case.get("title", ""),
            "module": case.get("module", ""), "page_key": case.get("page_key", ""),
            "expected": case.get("expected", ""), "actual": direct_catalog.get("message", ""),
            "status": direct_catalog.get("status", "ERROR"), "message": direct_catalog.get("message", ""),
            "error_message": direct_catalog.get("error", ""), "screenshot_path": "",
            "log_text": str(direct_catalog.get("steps", "")),
            "started_at": started.isoformat(timespec="seconds"),
            "finished_at": finished.isoformat(timespec="seconds"),
            "duration_ms": int((finished - started).total_seconds() * 1000),
        }

    own_driver = False
    if driver is None:
        own_driver = True

    actual = ""
    status = "ERROR"
    message = ""
    error_message = ""
    screenshot_path = ""
    logs = [f"SCENARIO {key}"]
    try:
        is_login = key.startswith("login_")
        if driver is None:
            driver = DriverFactory.create_driver(headless=False, keep_session=not is_login)
        if stop_requested and stop_requested():
            status, message = "SKIPPED", "Đã dừng trước khi chạy scenario"
        elif is_login:
            actual = _login_scenario(driver, key)
            status, message = "PASSED", "Scenario đăng nhập đạt assertion"
        else:
            _open_and_login(driver, case["url"])
            if key.startswith("dashboard_"):
                actual = _dashboard_scenario(driver, key)
            elif key.startswith("booking_"):
                actual = _booking_scenario(driver, key)
            elif key.startswith("fleet_"):
                actual = _fleet_scenario(driver, key)
            elif key.startswith("catalog_"):
                actual = _catalog_ui_scenario(driver, key)
            elif key.startswith("user_"):
                actual = _user_scenario(driver, key)
            else:
                raise ScenarioConfigurationError(f"Scenario chưa được ánh xạ: {key}")
            status, message = "PASSED", "Scenario đạt toàn bộ assertion"
        logs.append(f"ACTUAL {actual}")
        logs.append(f"RESULT {status}")
    except ScenarioFailure as error:
        status, message, error_message = "FAILED", "Expected không khớp trạng thái PCM", str(error)
        logs.append(f"ASSERTION FAILED: {error}")
        if driver:
            screenshot_path = capture_screenshot(driver, case.get("tc_id", key))
    except ScenarioConfigurationError as error:
        status, message, error_message = "ERROR", "Thiếu cấu hình để chạy scenario", str(error)
        logs.append(f"CONFIG ERROR: {error}")
    except Exception as error:
        status, message, error_message = "ERROR", "Selenium không thực hiện được scenario", str(error)
        logs.append(f"RUNTIME ERROR: {error}")
        logger.exception("[PCM SUITE] %s", key)
        if driver:
            screenshot_path = capture_screenshot(driver, case.get("tc_id", key))
    finally:
        if driver and own_driver:
            time.sleep(CLOSE_DELAY)
            driver.quit()

    finished = datetime.now()
    return {
        "case_id": case.get("tc_id", ""), "title": case.get("title", ""),
        "module": case.get("module", ""), "page_key": case.get("page_key", ""),
        "expected": case.get("expected", ""), "actual": actual,
        "status": status, "message": message, "error_message": error_message,
        "screenshot_path": screenshot_path, "log_text": "\n".join(logs),
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
        "duration_ms": int((finished - started).total_seconds() * 1000),
    }
