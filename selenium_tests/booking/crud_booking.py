import time
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    NoSuchElementException,
)

# SỬA: import từ đúng package
from selenium_tests.booking.login_helper import login, create_driver, BOOKING_URL

# =========================================================
# CONFIG
# =========================================================

WAIT_TIME = 30
SHORT_WAIT = 5

# Khai báo biến global để lưu ngày đã dùng khi tạo booking
USED_START = ""
USED_END = ""

# =========================================================
# TEST DATA
# =========================================================

RUN_ID = datetime.now().strftime("%H%M%S")

TEST_CUSTOMER_NAME = f"Nguyen Van Selenium {RUN_ID}"
TEST_PHONE = f"090{RUN_ID}"
TEST_EMAIL = f"booking.selenium.{RUN_ID}@gmail.com"

START_DT = (
    datetime.now()
    .replace(second=0, microsecond=0)
    + timedelta(days=1)
)
END_DT = START_DT + timedelta(days=2)

TEST_START_TEXT = START_DT.strftime("%d/%m/%Y %H:%M")
TEST_END_TEXT = END_DT.strftime("%d/%m/%Y %H:%M")

TEST_AMOUNT = "500000"
TEST_PICKUP = "Sân bay Tân Sơn Nhất"
TEST_RETURN = "Quận 1"
TEST_NOTE = f"Booking Selenium {RUN_ID}"

UPDATED_CUSTOMER_NAME = f"Nguyen Van Updated {RUN_ID}"
UPDATED_NOTE = f"Updated by Selenium {RUN_ID}"
UPDATED_AMOUNT = "600000"

# =========================================================
# LOCATORS (cập nhật nút "Tạo đơn thuê")
# =========================================================

CREATE_BOOKING_BUTTONS = [
    (By.XPATH, "//button[@aria-label='Tạo đơn thuê']"),
    (By.XPATH, "//button[.//span[normalize-space()='Tạo đơn thuê']]"),
    (By.XPATH, "//button[contains(@class, 'ant-btn-primary') and .//span[contains(text(), 'Tạo đơn thuê')]]"),
    (By.XPATH, "//button[contains(., 'Tạo đơn thuê')]"),
]

CAR_SELECT = (By.ID, "carId")
CUSTOMER_SELECT = (By.ID, "customerId")

CUSTOMER_NAME_FIELD = (By.ID, "customerName")
CUSTOMER_PHONE_FIELD = (By.ID, "customerPhoneNumber")
CUSTOMER_EMAIL_FIELD = (By.ID, "customerEmail")

START_DATE_FIELD = (By.ID, "startDate")
END_DATE_FIELD = (By.ID, "endDate")

PICKUP_LOCATION_FIELD = (By.ID, "pickupLocation")
RETURN_LOCATION_FIELD = (By.ID, "returnLocation")

STATUS_SELECT = (By.ID, "status")
RENTAL_AMOUNT_FIELD = (By.ID, "rentalAmount")
NOTE_FIELD = (By.ID, "note")

SAVE_BUTTON = (
    By.XPATH,
    "//button[@type='submit' and "
    "(.//span[contains(normalize-space(.),'Lưu')] "
    "or .//span[contains(normalize-space(.),'Tạo booking')] "
    "or .//span[contains(normalize-space(.),'Cập nhật')] "
    "or .//span[contains(normalize-space(.),'Tạo đơn thuê')])]"
)

ANT_DROPDOWN_OPTIONS = (
    By.CSS_SELECTOR,
    ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
    ".ant-select-item-option:not(.ant-select-item-option-disabled)"
)

TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")

CONFIRM_BUTTONS_XPATH = (
    "//div[contains(@class,'ant-popover') "
    "or contains(@class,'ant-modal')]"
    "//button["
    ".//span[normalize-space()='Xóa' "
    "or normalize-space()='OK' "
    "or normalize-space()='Đồng ý' "
    "or normalize-space()='Xác nhận']"
    " or normalize-space(.)='Xóa'"
    " or normalize-space(.)='OK'"
    " or normalize-space(.)='Đồng ý'"
    " or normalize-space(.)='Xác nhận'"
    "]"
)

LOADING_INDICATOR = (By.CSS_SELECTOR, ".ant-spin-spinning")
SUCCESS_NOTIFICATION = (By.CSS_SELECTOR, ".ant-notification-notice-success")
ERROR_NOTIFICATION = (By.CSS_SELECTOR, ".ant-notification-notice-error")
FORM_ERROR = (By.CSS_SELECTOR, ".ant-form-item-explain-error")

# =========================================================
# PRINT HELPERS
# =========================================================

def print_result(name, passed, message=""):
    if passed:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
    if message:
        print(f"       {message}")

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

# =========================================================
# BASIC HELPERS
# =========================================================

def wait_visible(driver, wait, locator):
    return wait.until(EC.visibility_of_element_located(locator))

def wait_clickable(driver, wait, locator):
    return wait.until(EC.element_to_be_clickable(locator))

def scroll_into_view(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
        element
    )
    time.sleep(0.2)

def get_value(driver, locator):
    try:
        element = driver.find_element(*locator)
        return element.get_attribute("value") or ""
    except Exception:
        return ""

# =========================================================
# POPUP HANDLING
# =========================================================

def close_open_popups(driver, wait=None):
    try:
        driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    except Exception:
        pass
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.3)

# =========================================================
# SAFE CLICK (có retry)
# =========================================================

def safe_click(driver, wait, element_or_locator, max_retries=3):
    for attempt in range(max_retries):
        try:
            if isinstance(element_or_locator, tuple):
                element = wait.until(EC.presence_of_element_located(element_or_locator))
            else:
                element = element_or_locator

            scroll_into_view(driver, element)
            close_open_popups(driver, wait)

            try:
                element.click()
                return element
            except (ElementClickInterceptedException, ElementNotInteractableException):
                driver.execute_script("arguments[0].click();", element)
                return element
        except Exception as e:
            print(f"[DEBUG] safe_click attempt {attempt+1} failed: {e}")
            close_open_popups(driver, wait)
            time.sleep(0.5)
    raise Exception(f"Không thể click sau {max_retries} lần")

# =========================================================
# OPEN CREATE FORM (cập nhật)
# =========================================================

def open_create_form(driver, wait):
    for locator in CREATE_BOOKING_BUTTONS:
        try:
            print(f"[DEBUG] Thử locator: {locator}")
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))
            safe_click(driver, wait, button)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(CAR_SELECT))
            print_result("Mở form Tạo đơn thuê", True)
            return True
        except Exception as e:
            print(f"[DEBUG] Lỗi với locator {locator}: {e}")
            continue

    # Fallback
    try:
        button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Tạo') or contains(., 'Tạo đơn thuê')]")
        driver.execute_script("arguments[0].click();", button)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(CAR_SELECT))
        print_result("Mở form Tạo đơn thuê (JS fallback)", True)
        return True
    except:
        pass

    print_result("Mở form Tạo đơn thuê", False, "Không tìm thấy nút Tạo đơn thuê")
    return False

# =========================================================
# ROBUST INPUT TEXT
# =========================================================

def clear_and_type(driver, wait, locator, value, field_name="", max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            close_open_popups(driver, wait)
            element = wait.until(EC.presence_of_element_located(locator))
            scroll_into_view(driver, element)

            try:
                wait.until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                pass

            try:
                element.click()
            except Exception:
                driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.2)

            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(value)
            element.send_keys(Keys.TAB)
            time.sleep(0.3)

            actual = get_value(driver, locator)
            if actual == value:
                if field_name:
                    print_result(field_name, True, f"Giá trị: {actual}")
                return True, actual
            else:
                driver.execute_script("arguments[0].value = arguments[1];", element, value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", element)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element)
                time.sleep(0.3)
                actual = get_value(driver, locator)
                if actual == value:
                    if field_name:
                        print_result(field_name, True, f"Giá trị (JS): {actual}")
                    return True, actual
        except Exception as e:
            print(f"[DEBUG] {field_name} attempt {attempt} ERROR: {e}")
            close_open_popups(driver, wait)
            time.sleep(0.5)

    if field_name:
        print_result(field_name, False, f"Không nhập được sau {max_retries} lần")
    return False, ""

# =========================================================
# ROBUST RENTAL AMOUNT
# =========================================================

def fill_rental_amount(driver, wait, amount, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            close_open_popups(driver, wait)
            element = wait.until(EC.presence_of_element_located(RENTAL_AMOUNT_FIELD))
            scroll_into_view(driver, element)

            try:
                wait.until(EC.element_to_be_clickable(RENTAL_AMOUNT_FIELD))
            except TimeoutException:
                pass

            try:
                element.click()
            except Exception:
                driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.2)

            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(amount)
            element.send_keys(Keys.TAB)
            time.sleep(0.3)

            actual = get_value(driver, RENTAL_AMOUNT_FIELD)
            digits = "".join(c for c in actual if c.isdigit())
            if digits == amount:
                print_result("Số tiền thuê", True, f"Giá trị: {actual}")
                return True
            else:
                driver.execute_script("arguments[0].value = arguments[1];", element, amount)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", element)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element)
                time.sleep(0.3)
                actual = get_value(driver, RENTAL_AMOUNT_FIELD)
                digits = "".join(c for c in actual if c.isdigit())
                if digits == amount:
                    print_result("Số tiền thuê", True, f"Giá trị (JS): {actual}")
                    return True
        except Exception as e:
            print(f"[DEBUG] fill_rental_amount attempt {attempt} ERROR: {e}")
            close_open_popups(driver, wait)
            time.sleep(0.5)

    print_result("Số tiền thuê", False, f"Không nhập được sau {max_retries} lần")
    return False

# =========================================================
# ANT DESIGN DATE PICKER
# =========================================================

def fill_date_picker(driver, wait, locator, value, field_name, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            close_open_popups(driver, wait)
            input_element = wait.until(EC.presence_of_element_located(locator))
            scroll_into_view(driver, input_element)

            try:
                input_element.click()
            except Exception:
                driver.execute_script("arguments[0].focus();", input_element)
            time.sleep(0.2)

            input_element.send_keys(Keys.CONTROL, "a")
            input_element.send_keys(Keys.BACKSPACE)
            input_element.send_keys(value)

            input_element.send_keys(Keys.TAB)
            time.sleep(0.5)
            close_open_popups(driver, wait)

            actual = input_element.get_attribute("value") or ""
            if actual == value:
                print_result(field_name, True, f"Giá trị: {actual}")
                return True
            else:
                input_element.click()
                time.sleep(0.2)
                input_element.send_keys(Keys.CONTROL, "a")
                input_element.send_keys(Keys.BACKSPACE)
                input_element.send_keys(value)
                input_element.send_keys(Keys.ENTER)
                time.sleep(0.5)
                close_open_popups(driver, wait)
                actual = input_element.get_attribute("value") or ""
                if actual == value:
                    print_result(field_name, True, f"Giá trị: {actual}")
                    return True

            print(f"[DEBUG] {field_name} attempt {attempt}: expected='{value}', actual='{actual}'")

        except Exception as e:
            print(f"[DEBUG] {field_name} attempt {attempt} ERROR: {e}")
            close_open_popups(driver, wait)
            time.sleep(0.5)

    try:
        input_element = driver.find_element(*locator)
        driver.execute_script("arguments[0].value = arguments[1];", input_element, value)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", input_element)
        time.sleep(0.5)
        actual = input_element.get_attribute("value") or ""
        if actual == value:
            print_result(field_name, True, f"Giá trị (JS): {actual}")
            return True
    except Exception:
        pass

    print_result(field_name, False, f"Không thể nhập sau {max_retries} lần")
    return False

# =========================================================
# ANT SELECT DROPDOWN
# =========================================================

def select_ant_dropdown(driver, wait, trigger_locator, field_name, keywords=None, required=False):
    try:
        close_open_popups(driver, wait)
        trigger = wait.until(EC.presence_of_element_located(trigger_locator))
        safe_click(driver, wait, trigger)

        try:
            wait.until(EC.presence_of_element_located(ANT_DROPDOWN_OPTIONS))
        except TimeoutException:
            msg = "Không có option hiển thị"
            print_result(field_name, False, msg)
            return False, ""

        options = driver.find_elements(*ANT_DROPDOWN_OPTIONS)
        visible_options = [opt for opt in options if opt.is_displayed()]

        if not visible_options:
            print_result(field_name, False, "Không có option hiển thị")
            return False, ""

        chosen = None
        if keywords:
            for option in visible_options:
                text = option.text.strip().lower()
                if all(kw.lower() in text for kw in keywords):
                    chosen = option
                    break
        if chosen is None:
            chosen = visible_options[0]

        option_text = chosen.text.strip()
        safe_click(driver, wait, chosen)
        close_open_popups(driver, wait)
        print_result(field_name, True, f"Đã chọn: {option_text}")
        return True, option_text

    except Exception as e:
        close_open_popups(driver, wait)
        print_result(field_name, False, str(e))
        return False, ""

# =========================================================
# DATE VALIDATION
# =========================================================

def parse_booking_datetime(value):
    value = value.strip()
    formats = ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def verify_booking_dates(driver, wait):
    try:
        start_element = wait.until(EC.presence_of_element_located(START_DATE_FIELD))
        end_element = wait.until(EC.presence_of_element_located(END_DATE_FIELD))
        start_value = start_element.get_attribute("value") or ""
        end_value = end_element.get_attribute("value") or ""

        print(f"       [DEBUG] Start date = {start_value}")
        print(f"       [DEBUG] End date   = {end_value}")

        if not start_value:
            print_result("Ngày nhận xe", False, "Không có giá trị")
            return False
        if not end_value:
            print_result("Ngày trả xe", False, "Không có giá trị")
            return False

        start_dt = parse_booking_datetime(start_value)
        end_dt = parse_booking_datetime(end_value)

        if start_dt is None:
            print_result("Ngày nhận xe", False, f"Không parse được: {start_value}")
            return False
        if end_dt is None:
            print_result("Ngày trả xe", False, f"Không parse được: {end_value}")
            return False

        valid = end_dt >= start_dt
        print_result("Kiểm tra ngày trả >= ngày nhận", valid, f"{start_value} -> {end_value}")
        return valid
    except Exception as e:
        print_result("Kiểm tra ngày trả >= ngày nhận", False, str(e))
        return False

# =========================================================
# WAIT FOR TABLE TO LOAD
# =========================================================

def wait_for_table_to_load(driver, wait, timeout=30):
    try:
        try:
            wait.until(EC.invisibility_of_element_located(LOADING_INDICATOR))
        except TimeoutException:
            pass
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*TABLE_ROWS)) > 0
        )
        return True
    except TimeoutException:
        return False

# =========================================================
# FIND ROW IN TABLE
# =========================================================

def find_booking_row(driver, wait, unique_texts, timeout=30, refresh_if_not_found=True):
    end_time = time.time() + timeout
    attempt = 0
    while time.time() < end_time:
        attempt += 1
        rows = driver.find_elements(*TABLE_ROWS)
        if not rows:
            print(f"[DEBUG] Không có row nào trong bảng (attempt {attempt})")
            wait_for_table_to_load(driver, wait, timeout=5)
            continue
        else:
            for row in rows:
                try:
                    text = row.text
                    if all(txt in text for txt in unique_texts):
                        return row
                except StaleElementReferenceException:
                    continue
        time.sleep(1)
        if refresh_if_not_found and (time.time() > end_time - timeout/2) and attempt > 3:
            print("[DEBUG] Chưa thấy row, thử refresh trang...")
            driver.refresh()
            time.sleep(2)
            try:
                wait.until(EC.presence_of_element_located(TABLE_ROWS))
            except:
                pass
    return None

def print_all_rows(driver):
    rows = driver.find_elements(*TABLE_ROWS)
    print("[DEBUG] Tất cả rows trong bảng:")
    if not rows:
        print("  (không có row nào)")
    for idx, row in enumerate(rows):
        print(f"  Row {idx+1}: {row.text[:200]}")

# =========================================================
# FIND ACTION BUTTON (EDIT/DELETE)
# =========================================================

def find_action_button(row, kind):
    labels = ["sửa", "edit"] if kind == "edit" else ["xóa", "delete"]
    try:
        buttons = row.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            aria = (button.get_attribute("aria-label") or "").lower()
            title = (button.get_attribute("title") or "").lower()
            html = (button.get_attribute("outerHTML") or "").lower()
            for label in labels:
                if label in aria or label in title or label in html:
                    return button
    except Exception:
        pass
    return None

# =========================================================
# CONFIRM DELETE
# =========================================================

def confirm_delete(driver, wait):
    try:
        buttons = WebDriverWait(driver, 5).until(
            lambda d: [b for b in d.find_elements(By.XPATH, CONFIRM_BUTTONS_XPATH) if b.is_displayed()] or False
        )
        for button in buttons:
            try:
                safe_click(driver, wait, button)
                return True
            except Exception:
                continue
    except TimeoutException:
        pass
    return False

# =========================================================
# DELETE BOOKING BY NAME (cleanup)
# =========================================================

def delete_booking_by_name(driver, wait, name):
    row = find_booking_row(driver, wait, [name], timeout=5, refresh_if_not_found=False)
    if row is None:
        return False
    delete_btn = find_action_button(row, "delete")
    if delete_btn is None:
        return False
    try:
        safe_click(driver, wait, delete_btn)
        time.sleep(0.5)
        confirmed = confirm_delete(driver, wait)
        time.sleep(1)
        return confirmed
    except Exception:
        return False

# =========================================================
# DETECT ERROR MESSAGES
# =========================================================

def is_error_present(driver):
    try:
        errors = driver.find_elements(*ERROR_NOTIFICATION)
        if errors and any(e.is_displayed() for e in errors):
            return True
    except:
        pass
    try:
        errors = driver.find_elements(*FORM_ERROR)
        if errors and any(e.is_displayed() for e in errors):
            return True
    except:
        pass
    return False

def get_error_text(driver):
    try:
        errors = driver.find_elements(*ERROR_NOTIFICATION)
        for e in errors:
            if e.is_displayed():
                return e.text
    except:
        pass
    try:
        errors = driver.find_elements(*FORM_ERROR)
        for e in errors:
            if e.is_displayed():
                return e.text
    except:
        pass
    return ""

# =========================================================
# CREATE BOOKING VỚI XỬ LÝ TRÙNG LỊCH
# =========================================================

def create_booking(driver, wait):
    global USED_START, USED_END

    print_header("CREATE BOOKING")

    max_attempts = 2
    attempt = 0
    start_dt = START_DT
    end_dt = END_DT

    while attempt < max_attempts:
        attempt += 1
        print(f"\n[INFO] Lần thử tạo booking #{attempt}")

        if not open_create_form(driver, wait):
            return False

        start_text = start_dt.strftime("%d/%m/%Y %H:%M")
        end_text = end_dt.strftime("%d/%m/%Y %H:%M")
        print(f"[INFO] Ngày nhận: {start_text}, Ngày trả: {end_text}")

        required_ok = True

        # DATE
        date_ok = verify_booking_dates(driver, wait)
        if not date_ok:
            start_ok = fill_date_picker(driver, wait, START_DATE_FIELD, start_text, "Ngày nhận xe")
            if not start_ok:
                required_ok = False
            time.sleep(1)
            end_ok = fill_date_picker(driver, wait, END_DATE_FIELD, end_text, "Ngày trả xe")
            if not end_ok:
                required_ok = False
            date_ok = verify_booking_dates(driver, wait)
            if not date_ok:
                required_ok = False

        # CAR
        car_ok, _ = select_ant_dropdown(driver, wait, CAR_SELECT, "Chọn xe")
        if not car_ok:
            required_ok = False

        # CUSTOMER SELECT (optional)
        select_ant_dropdown(driver, wait, CUSTOMER_SELECT, "Chọn khách hàng", required=False)

        # CUSTOMER INFO
        name_ok, _ = clear_and_type(driver, wait, CUSTOMER_NAME_FIELD, TEST_CUSTOMER_NAME, "Tên khách hàng")
        if not name_ok:
            required_ok = False

        phone_ok, _ = clear_and_type(driver, wait, CUSTOMER_PHONE_FIELD, TEST_PHONE, "Số điện thoại")
        if not phone_ok:
            required_ok = False

        email_ok, _ = clear_and_type(driver, wait, CUSTOMER_EMAIL_FIELD, TEST_EMAIL, "Email")

        pickup_ok, _ = clear_and_type(driver, wait, PICKUP_LOCATION_FIELD, TEST_PICKUP, "Điểm nhận xe")
        return_ok, _ = clear_and_type(driver, wait, RETURN_LOCATION_FIELD, TEST_RETURN, "Điểm trả xe")

        select_ant_dropdown(driver, wait, STATUS_SELECT, "Trạng thái", keywords=["Nháp"], required=False)

        amount_ok = fill_rental_amount(driver, wait, TEST_AMOUNT)
        if not amount_ok:
            required_ok = False

        note_ok, _ = clear_and_type(driver, wait, NOTE_FIELD, TEST_NOTE, "Ghi chú")

        if not required_ok:
            print_result("CREATE BOOKING", False, "Form chưa hợp lệ, không submit")
            return False

        # Submit
        try:
            close_open_popups(driver, wait)
            save_button = wait_clickable(driver, wait, SAVE_BUTTON)
            safe_click(driver, wait, save_button)

            time.sleep(2)

            if is_error_present(driver):
                error_text = get_error_text(driver)
                print(f"[INFO] Lỗi khi submit: {error_text}")
                if "trùng" in error_text.lower() or "overlap" in error_text.lower() or "đã có" in error_text.lower():
                    print("[INFO] Phát hiện trùng lịch, sẽ thử lại với ngày khác.")
                    start_dt += timedelta(days=2)
                    end_dt += timedelta(days=2)
                    # Đóng form
                    try:
                        driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Hủy')]]").click()
                    except:
                        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Hủy')]]"))
                    time.sleep(1)
                    continue
                else:
                    print_result("CREATE BOOKING", False, f"Lỗi: {error_text}")
                    return False
            else:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(SUCCESS_NOTIFICATION)
                    )
                except:
                    pass
                time.sleep(2)
                wait_for_table_to_load(driver, wait, timeout=10)
                print_result("CREATE BOOKING", True, f"Đã submit booking (lần thử {attempt})")
                USED_START = start_text
                USED_END = end_text
                return True

        except Exception as e:
            print_result("CREATE BOOKING", False, str(e))
            return False

    print_result("CREATE BOOKING", False, f"Thất bại sau {max_attempts} lần thử")
    return False

# =========================================================
# VERIFY CREATE (chỉ kiểm tra các trường hiển thị)
# =========================================================

def verify_create(driver, wait):
    print_header("VERIFY CREATE")
    wait_for_table_to_load(driver, wait, timeout=10)
    row = find_booking_row(driver, wait, [TEST_CUSTOMER_NAME, TEST_PHONE], timeout=30, refresh_if_not_found=True)
    if row is None:
        print_result("Verify CREATE", False, "Không tìm thấy booking vừa tạo")
        print_all_rows(driver)
        return False

    row_text = row.text
    print("\n       [DEBUG] Booking row:")
    print(row_text)

    checks = [
        ("Customer", TEST_CUSTOMER_NAME),
        ("Phone", TEST_PHONE),
    ]
    all_ok = True
    for name, expected in checks:
        passed = expected in row_text
        print_result(f"Verify {name}", passed, f"Expected: {expected}")
        all_ok &= passed

    amount_variants = [TEST_AMOUNT, "500.000", "500,000", "500 000"]
    amount_found = any(v in row_text for v in amount_variants)
    print_result("Verify Amount", amount_found, f"Expected: {TEST_AMOUNT}")
    all_ok &= amount_found

    print_result("VERIFY CREATE", all_ok)
    return all_ok

# =========================================================
# UPDATE BOOKING
# =========================================================

def update_booking(driver, wait):
    print_header("UPDATE BOOKING")
    row = find_booking_row(driver, wait, [TEST_CUSTOMER_NAME, TEST_PHONE], timeout=20, refresh_if_not_found=True)
    if row is None:
        print_result("Tìm booking UPDATE", False)
        print_all_rows(driver)
        return False

    edit_button = find_action_button(row, "edit")
    if edit_button is None:
        print_result("Tìm nút UPDATE", False, "Không tìm thấy nút Sửa")
        return False

    try:
        safe_click(driver, wait, edit_button)
        wait.until(EC.presence_of_element_located(CUSTOMER_NAME_FIELD))
        print_result("Mở form UPDATE", True)

        close_open_popups(driver, wait)

        name_ok, _ = clear_and_type(driver, wait, CUSTOMER_NAME_FIELD, UPDATED_CUSTOMER_NAME, "Update customer", max_retries=5)
        if not name_ok:
            print_result("UPDATE BOOKING", False, "Không nhập được tên mới")
            return False

        note_ok, _ = clear_and_type(driver, wait, NOTE_FIELD, UPDATED_NOTE, "Update note", max_retries=5)
        if not note_ok:
            print_result("UPDATE BOOKING", False, "Không nhập được ghi chú mới")
            return False

        amount_ok = fill_rental_amount(driver, wait, UPDATED_AMOUNT)
        if not amount_ok:
            try:
                element = driver.find_element(*RENTAL_AMOUNT_FIELD)
                driver.execute_script("arguments[0].value = arguments[1];", element, UPDATED_AMOUNT)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", element)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element)
                time.sleep(0.5)
                actual = get_value(driver, RENTAL_AMOUNT_FIELD)
                digits = "".join(c for c in actual if c.isdigit())
                if digits == UPDATED_AMOUNT:
                    amount_ok = True
                    print_result("Số tiền thuê", True, f"Giá trị (JS): {actual}")
                else:
                    print_result("UPDATE BOOKING", False, "Không cập nhật được số tiền")
                    return False
            except:
                print_result("UPDATE BOOKING", False, "Lỗi khi cập nhật số tiền")
                return False

        close_open_popups(driver, wait)
        save_button = wait_clickable(driver, wait, SAVE_BUTTON)
        safe_click(driver, wait, save_button)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(SUCCESS_NOTIFICATION)
            )
        except TimeoutException:
            try:
                wait.until(EC.invisibility_of_element_located(LOADING_INDICATOR))
            except:
                pass

        time.sleep(2)
        wait_for_table_to_load(driver, wait, timeout=10)
        print_result("UPDATE BOOKING", True, "Đã lưu thay đổi")
        return True

    except Exception as e:
        print_result("UPDATE BOOKING", False, str(e))
        return False

# =========================================================
# VERIFY UPDATE
# =========================================================

def verify_update(driver, wait):
    print_header("VERIFY UPDATE")
    wait_for_table_to_load(driver, wait, timeout=10)
    row = find_booking_row(driver, wait, [UPDATED_CUSTOMER_NAME], timeout=20, refresh_if_not_found=True)
    if row is None:
        print_result("VERIFY UPDATE", False, "Không tìm thấy booking sau UPDATE")
        print_all_rows(driver)
        return False

    row_text = row.text
    print("\n       [DEBUG] Updated row:")
    print(row_text)

    checks = [
        ("Updated customer", UPDATED_CUSTOMER_NAME),
    ]
    all_ok = True
    for name, expected in checks:
        passed = expected in row_text
        print_result(name, passed, f"Expected: {expected}")
        all_ok &= passed

    amount_variants = ["600000", "600.000", "600,000", "600 000"]
    amount_found = any(v in row_text for v in amount_variants)
    print_result("Updated amount", amount_found, f"Expected: {UPDATED_AMOUNT}")
    all_ok &= amount_found

    note_found = UPDATED_NOTE in row_text
    print_result("Updated note", note_found, f"Expected: {UPDATED_NOTE}")
    all_ok &= note_found

    print_result("VERIFY UPDATE", all_ok)
    return all_ok

# =========================================================
# DELETE BOOKING
# =========================================================

def delete_booking(driver, wait):
    print_header("DELETE BOOKING")
    row = find_booking_row(driver, wait, [UPDATED_CUSTOMER_NAME], timeout=15, refresh_if_not_found=True)
    if row is None:
        print_result("Tìm booking DELETE", False)
        print_all_rows(driver)
        return False

    delete_button = find_action_button(row, "delete")
    if delete_button is None:
        print_result("Tìm nút DELETE", False, "Không tìm thấy nút Xóa")
        return False

    try:
        safe_click(driver, wait, delete_button)
        time.sleep(0.5)
        confirmed = confirm_delete(driver, wait)
        print_result("Xác nhận DELETE", confirmed, "Đã xác nhận xóa" if confirmed else "Không thấy popup xác nhận")
        time.sleep(2)
        wait_for_table_to_load(driver, wait, timeout=10)
        print_result("DELETE BOOKING", True)
        return True
    except Exception as e:
        print_result("DELETE BOOKING", False, str(e))
        return False

# =========================================================
# VERIFY DELETE
# =========================================================

def verify_delete(driver, wait):
    print_header("VERIFY DELETE")
    time.sleep(2)
    wait_for_table_to_load(driver, wait, timeout=5)
    row = find_booking_row(driver, wait, [UPDATED_CUSTOMER_NAME], timeout=5, refresh_if_not_found=False)
    deleted = row is None
    print_result("Verify booking đã bị xóa", deleted, "Booking không còn trong bảng" if deleted else "Booking vẫn còn trong bảng")
    if not deleted:
        print_all_rows(driver)
    return deleted

# =========================================================
# CLEANUP
# =========================================================

def cleanup_test_data(driver, wait, booking_created):
    if not booking_created:
        return
    print("\n[INFO] Đang cleanup dữ liệu test...")
    deleted = False
    for name in [TEST_CUSTOMER_NAME, UPDATED_CUSTOMER_NAME]:
        if delete_booking_by_name(driver, wait, name):
            deleted = True
            print(f"[CLEANUP] Đã xóa booking '{name}'")
            break
    if not deleted:
        print("[CLEANUP] Không tìm thấy booking để xóa hoặc xóa thất bại.")

# =========================================================
# MAIN
# =========================================================

def run_crud_booking():
    driver = create_driver()
    wait = WebDriverWait(driver, WAIT_TIME)

    create_ok = False
    verify_create_ok = False
    update_ok = False
    verify_update_ok = False
    delete_ok = False
    verify_delete_ok = False
    booking_created = False

    try:
        print_header("BOOKING CRUD TEST")
        print("\n===== TEST DATA =====")
        print(f"Customer : {TEST_CUSTOMER_NAME}")
        print(f"Phone    : {TEST_PHONE}")
        print(f"Email    : {TEST_EMAIL}")
        print(f"Start    : {TEST_START_TEXT}")
        print(f"End      : {TEST_END_TEXT}")
        print(f"Amount   : {TEST_AMOUNT}")
        print(f"Pickup   : {TEST_PICKUP}")
        print(f"Return   : {TEST_RETURN}")
        print(f"Note     : {TEST_NOTE}")

        login_ok = login(driver, wait)
        print_result("LOGIN", login_ok)
        if not login_ok:
            print("\n[STOP] Login thất bại.")
            return

        try:
            driver.get(BOOKING_URL)
            wait.until(EC.url_contains("/bookings"))
            print_result("BOOKING PAGE", True, driver.current_url)
        except Exception as e:
            print_result("BOOKING PAGE", False, str(e))
            return

        create_ok = create_booking(driver, wait)
        booking_created = True
        if not create_ok:
            print("\n[STOP] CREATE thất bại.")
            return

        verify_create_ok = verify_create(driver, wait)
        if not verify_create_ok:
            print("\n[STOP] VERIFY CREATE thất bại.")
            return

        update_ok = update_booking(driver, wait)
        if not update_ok:
            print("\n[STOP] UPDATE thất bại.")
            return

        verify_update_ok = verify_update(driver, wait)
        if not verify_update_ok:
            print("\n[STOP] VERIFY UPDATE thất bại.")
            return

        delete_ok = delete_booking(driver, wait)
        if not delete_ok:
            print("\n[STOP] DELETE thất bại.")
            return

        verify_delete_ok = verify_delete(driver, wait)

    except Exception as e:
        print("\n[CRITICAL ERROR]")
        print(e)

    finally:
        cleanup_test_data(driver, wait, booking_created)

        print_header("BOOKING CRUD TEST COMPLETED")
        steps = [
            ("CREATE", create_ok),
            ("VERIFY CREATE", verify_create_ok),
            ("UPDATE", update_ok),
            ("VERIFY UPDATE", verify_update_ok),
            ("DELETE", delete_ok),
            ("VERIFY DELETE", verify_delete_ok),
        ]
        for name, status in steps:
            print(f"{name:15}: {'PASS' if status else 'FAIL'}")

        passed = sum(1 for _, status in steps if status)
        print(f"\nRESULT: {passed}/{len(steps)} STEPS PASS")
        overall = all(status for _, status in steps)
        print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
        print("=" * 60)

        input("\nNhấn Enter để đóng trình duyệt...")
        driver.quit()

if __name__ == "__main__":
    run_crud_booking()