import os
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================================================
# FIX PYTHON PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORT PROJECT
# =========================================================

from core.config import Config
from core.driver_factory import DriverFactory


# =========================================================
# CONFIG
# =========================================================

LOGIN_URL = "https://courses.plt.pro.vn/login"
BOOKING_CREATE_URL = "https://courses.plt.pro.vn/bookings/new"

WAIT_TIME = 20


# =========================================================
# LOGIN
# =========================================================

def login(driver):
    """
    Đăng nhập hệ thống.

    Không test chức năng Login.
    Login chỉ là bước chuẩn bị để vào trang
    Quản lý đặt xe.
    """

    print()
    print("=" * 70)
    print("[LOGIN] BẮT ĐẦU ĐĂNG NHẬP")
    print("=" * 70)

    driver.get(LOGIN_URL)

    wait = WebDriverWait(
        driver,
        WAIT_TIME
    )

    print("[LOGIN] URL:", driver.current_url)

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='email'], "
                "input[name='email'], "
                "input[name='username'], "
                "input[placeholder='ban@plt.pro.vn']"
            )
        )
    )

    print("[LOGIN] Tìm thấy ô Email")

    email.clear()

    email.send_keys(
        Config.TEST_EMAIL
    )

    print(
        "[LOGIN] Đã nhập email:",
        Config.TEST_EMAIL
    )

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    password = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='password'], "
                "input[name='password'], "
                "input[placeholder='Nhập mật khẩu']"
            )
        )
    )

    print("[LOGIN] Tìm thấy ô Password")

    password.clear()

    password.send_keys(
        Config.TEST_PASSWORD
    )

    print("[LOGIN] Đã nhập password")

    # -----------------------------------------------------
    # BUTTON
    # -----------------------------------------------------

    login_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit'], "
                "input[type='submit']"
            )
        )
    )

    print("[LOGIN] Tìm thấy nút đăng nhập")

    login_button.click()

    print("[LOGIN] Đã click Đăng nhập")

    # -----------------------------------------------------
    # WAIT LOGIN
    # -----------------------------------------------------

    wait.until(
        lambda d:
        "/login" not in d.current_url.lower()
    )

    print("[LOGIN] PASS")

    print(
        "[LOGIN] URL sau login:",
        driver.current_url
    )

    print("=" * 70)


# =========================================================
# OPEN BOOKING CREATE PAGE
# =========================================================

def open_booking_create_page(driver):
    """
    Sau khi login:
        /bookings/new
    """

    print()
    print("=" * 70)
    print("[BOOKING] MỞ FORM TẠO ĐẶT XE")
    print("=" * 70)

    driver.get(
        BOOKING_CREATE_URL
    )

    wait = WebDriverWait(
        driver,
        WAIT_TIME
    )

    # -----------------------------------------------------
    # WAIT URL
    # -----------------------------------------------------

    wait.until(
        lambda d:
        "/bookings/new"
        in d.current_url.lower()
    )

    print(
        "[BOOKING] URL:",
        driver.current_url
    )

    # -----------------------------------------------------
    # WAIT MAIN
    # -----------------------------------------------------

    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "main"
            )
        )
    )

    print(
        "[BOOKING] Đã vào form tạo đặt xe"
    )

    print("=" * 70)


# =========================================================
# INSPECT INPUT
# =========================================================

def inspect_inputs(driver):
    """
    Tìm toàn bộ input trong form.
    """

    print()
    print("=" * 70)
    print("[INSPECT] INPUT TRONG FORM")
    print("=" * 70)

    inputs = driver.find_elements(
        By.CSS_SELECTOR,
        "input"
    )

    print(
        "[INSPECT] Tổng số input:",
        len(inputs)
    )

    for index, element in enumerate(
        inputs,
        start=1
    ):

        try:

            print()
            print(
                f"--- INPUT {index} ---"
            )

            print(
                "tag:",
                element.tag_name
            )

            print(
                "type:",
                element.get_attribute("type")
            )

            print(
                "id:",
                element.get_attribute("id")
            )

            print(
                "name:",
                element.get_attribute("name")
            )

            print(
                "placeholder:",
                element.get_attribute(
                    "placeholder"
                )
            )

            print(
                "aria-label:",
                element.get_attribute(
                    "aria-label"
                )
            )

            print(
                "value:",
                element.get_attribute(
                    "value"
                )
            )

        except Exception as error:

            print(
                "[WARN] Không đọc được input:",
                error
            )


# =========================================================
# INSPECT SELECT
# =========================================================

def inspect_selects(driver):
    """
    Tìm native select.
    """

    print()
    print("=" * 70)
    print("[INSPECT] SELECT")
    print("=" * 70)

    selects = driver.find_elements(
        By.CSS_SELECTOR,
        "select"
    )

    print(
        "[INSPECT] Tổng số select:",
        len(selects)
    )

    for index, select in enumerate(
        selects,
        start=1
    ):

        print()
        print(
            f"--- SELECT {index} ---"
        )

        print(
            "id:",
            select.get_attribute("id")
        )

        print(
            "name:",
            select.get_attribute("name")
        )

        print(
            "aria-label:",
            select.get_attribute(
                "aria-label"
            )
        )

        options = select.find_elements(
            By.TAG_NAME,
            "option"
        )

        print(
            "options:",
            len(options)
        )

        for option in options:

            text = (
                option.text or ""
            ).strip()

            if text:
                print(
                    "   -",
                    text
                )


# =========================================================
# INSPECT ANT SELECT
# =========================================================

def inspect_ant_selects(driver):
    """
    Tìm các component Ant Design Select.

    Không click để tránh làm thay đổi form.
    """

    print()
    print("=" * 70)
    print("[INSPECT] ANT DESIGN SELECT")
    print("=" * 70)

    selectors = [
        ".ant-select",
        ".ant-select-selector",
        "[role='combobox']"
    ]

    elements = []

    for selector in selectors:

        found = driver.find_elements(
            By.CSS_SELECTOR,
            selector
        )

        for element in found:

            if element not in elements:
                elements.append(
                    element
                )

    print(
        "[INSPECT] Tổng component:",
        len(elements)
    )

    for index, element in enumerate(
        elements,
        start=1
    ):

        try:

            print()
            print(
                f"--- ANT SELECT {index} ---"
            )

            print(
                "tag:",
                element.tag_name
            )

            print(
                "id:",
                element.get_attribute(
                    "id"
                )
            )

            print(
                "class:",
                element.get_attribute(
                    "class"
                )
            )

            print(
                "aria-label:",
                element.get_attribute(
                    "aria-label"
                )
            )

            print(
                "role:",
                element.get_attribute(
                    "role"
                )
            )

            print(
                "text:",
                (
                    element.text or ""
                ).strip()
            )

        except Exception as error:

            print(
                "[WARN] Không đọc được:",
                error
            )


# =========================================================
# INSPECT BUTTONS
# =========================================================

def inspect_buttons(driver):
    """
    Tìm các button trong form.
    """

    print()
    print("=" * 70)
    print("[INSPECT] BUTTON")
    print("=" * 70)

    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        "button"
    )

    print(
        "[INSPECT] Tổng số button:",
        len(buttons)
    )

    for index, button in enumerate(
        buttons,
        start=1
    ):

        try:

            text = (
                button.text or ""
            ).strip()

            print()
            print(
                f"--- BUTTON {index} ---"
            )

            print(
                "text:",
                text
            )

            print(
                "type:",
                button.get_attribute(
                    "type"
                )
            )

            print(
                "id:",
                button.get_attribute(
                    "id"
                )
            )

            print(
                "class:",
                button.get_attribute(
                    "class"
                )
            )

        except Exception as error:

            print(
                "[WARN] Không đọc được:",
                error
            )


# =========================================================
# INSPECT LABELS
# =========================================================

def inspect_labels(driver):
    """
    Tìm label và text liên quan đến form.
    """

    print()
    print("=" * 70)
    print("[INSPECT] LABEL")
    print("=" * 70)

    labels = driver.find_elements(
        By.CSS_SELECTOR,
        "label"
    )

    print(
        "[INSPECT] Tổng số label:",
        len(labels)
    )

    for index, label in enumerate(
        labels,
        start=1
    ):

        try:

            text = (
                label.text or ""
            ).strip()

            if not text:
                continue

            print(
                f"{index}. {text}"
            )

            print(
                "   for:",
                label.get_attribute(
                    "for"
                )
            )

        except Exception:
            pass


# =========================================================
# INSPECT FORM
# =========================================================

def inspect_booking_form(driver):

    print()
    print()
    print("#" * 70)
    print("# BẮT ĐẦU INSPECT FORM TẠO ĐẶT XE")
    print("#" * 70)

    inspect_labels(driver)

    inspect_inputs(driver)

    inspect_selects(driver)

    inspect_ant_selects(driver)

    inspect_buttons(driver)

    print()
    print("#" * 70)
    print("# INSPECT HOÀN TẤT")
    print("#" * 70)


# =========================================================
# MAIN
# =========================================================

def main():

    driver = None

    try:

        print()
        print("=" * 70)
        print("AUTO TEST - INSPECT BOOKING CREATE FORM")
        print("=" * 70)

        # -------------------------------------------------
        # CREATE DRIVER
        # -------------------------------------------------

        driver = DriverFactory.create_driver(
            headless=False,
            keep_session=False
        )

        print(
            "[DRIVER] Chrome đã khởi động"
        )

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login(driver)

        # -------------------------------------------------
        # OPEN BOOKING FORM
        # -------------------------------------------------

        open_booking_create_page(
            driver
        )

        # -------------------------------------------------
        # INSPECT
        # -------------------------------------------------

        inspect_booking_form(
            driver
        )

        # -------------------------------------------------
        # GIỮ TRÌNH DUYỆT 5 GIÂY
        # -------------------------------------------------

        print()
        print(
            "[INFO] Giữ Chrome 5 giây..."
        )

        time.sleep(5)

    except Exception as error:

        print()
        print("=" * 70)
        print("[ERROR]")
        print(error)
        print("=" * 70)

        raise

    finally:

        if driver:

            try:

                driver.quit()

                print(
                    "[DRIVER] Chrome đã đóng"
                )

            except Exception:
                pass


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()