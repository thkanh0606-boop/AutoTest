
"""
diagnose_booking_page.py

Mục đích:
    Chẩn đoán trang Quản lý đặt xe (/bookings).

    Script sẽ:
    1. Mở trang /bookings.
    2. Kiểm tra session / đăng nhập nếu cần.
    3. In toàn bộ input hiện có sau khi trang load.
    4. In các button / link có text.
    5. Kiểm tra trực tiếp carId/customerId/status/paymentMethod.
    6. Tìm các nút có khả năng mở form "Thêm đặt xe".
    7. Tự động thử click các nút phù hợp.
    8. Sau khi mở form/modal/drawer:
       - Tìm customerId
       - Tìm carId
       - Tìm status
       - Tìm paymentMethod
    9. In HTML liên quan đến form.
   10. Chụp screenshot trước và sau khi mở form.

Chạy:
    python diagnose_booking_page.py
"""

import os
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# =========================================================
# IMPORT PROJECT
# =========================================================

from core.config import Config
from core.driver_factory import DriverFactory


# =========================================================
# CONFIG
# =========================================================

URL = "https://courses.plt.pro.vn/bookings"

TARGET_IDS = [
    "customerId",
    "carId",
    "status",
    "paymentMethod",
]

OUTPUT_HTML = os.path.join(
    Config.BASE_DIR,
    "diagnose_bookings_page_source.html",
)

SCREENSHOT_BEFORE = os.path.join(
    Config.BASE_DIR,
    "diagnose_bookings_before_modal.png",
)

SCREENSHOT_AFTER = os.path.join(
    Config.BASE_DIR,
    "diagnose_bookings_after_modal.png",
)


# =========================================================
# PRINT HELPERS
# =========================================================

def print_separator(title=""):
    print()
    print("=" * 80)

    if title:
        print(f" {title}")

    print("=" * 80)


def safe_text(element):
    try:
        return (element.text or "").strip()
    except Exception:
        return ""


def safe_visible(element):
    try:
        return element.is_displayed()
    except Exception:
        return False


# =========================================================
# LOGIN
# =========================================================

def login_if_needed(driver):
    """
    Kiểm tra xem trang hiện tại có form login hay không.

    Nếu có:
        - nhập email
        - nhập password
        - click submit
        - chờ rời khỏi /login

    Nếu không:
        giữ nguyên session hiện tại.
    """

    print_separator("KIỂM TRA LOGIN")

    try:
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[type='password'], "
                    "input[name='password']"
                )
            )
        )

        print("[INFO] Phát hiện form đăng nhập.")

    except Exception:
        print("[INFO] Không thấy form login.")
        print("[INFO] Có thể session hiện tại đã đăng nhập.")
        return

    wait = WebDriverWait(
        driver,
        Config.EXPLICIT_WAIT,
    )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='email'], "
                "input[name='email'], "
                "input[name='username'], "
                "input[type='text']"
            )
        )
    )

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    password = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='password'], "
                "input[name='password']"
            )
        )
    )

    email.clear()
    email.send_keys(Config.TEST_EMAIL)

    password.clear()
    password.send_keys(Config.TEST_PASSWORD)

    # -----------------------------------------------------
    # SUBMIT
    # -----------------------------------------------------

    submit = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit'], "
                "input[type='submit']"
            )
        )
    )

    print("[INFO] Đang click Đăng nhập...")

    submit.click()

    # -----------------------------------------------------
    # WAIT LOGIN
    # -----------------------------------------------------

    try:
        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            lambda d: "/login"
            not in (d.current_url or "").lower()
        )

        print(
            "[PASS] Đăng nhập thành công."
        )
        print(
            "[INFO] URL:",
            driver.current_url,
        )

    except Exception:
        print(
            "[ERROR] Không rời khỏi trang login."
        )

        print(
            "[ERROR] URL:",
            driver.current_url,
        )

        # In lỗi từ UI nếu có
        error_selectors = [
            ".ant-form-item-explain-error",
            ".ant-message-error",
            "[role='alert']",
        ]

        for selector in error_selectors:
            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector,
            )

            for element in elements:
                text = safe_text(element)

                if text:
                    print(
                        "[LOGIN ERROR]",
                        text,
                    )


# =========================================================
# WAIT PAGE
# =========================================================

def wait_page_loaded(driver):
    """
    Chờ document load hoàn tất.
    """

    wait = WebDriverWait(
        driver,
        Config.EXPLICIT_WAIT,
    )

    wait.until(
        lambda d:
        d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    # Chờ thêm một chút cho React / Ant Design render.
    time.sleep(2)


# =========================================================
# PRINT PAGE INFO
# =========================================================

def print_page_info(driver):
    print_separator("PAGE STATE")

    print(
        "URL:",
        driver.current_url,
    )

    print(
        "Title:",
        driver.title,
    )


# =========================================================
# PRINT ALL INPUTS
# =========================================================

def print_all_inputs(driver, title):
    print_separator(title)

    inputs = driver.find_elements(
        By.TAG_NAME,
        "input",
    )

    print(
        f"Tổng số input: {len(inputs)}"
    )

    if not inputs:
        print("[INFO] Không có input nào.")

    for index, element in enumerate(
        inputs,
        start=1,
    ):
        try:
            print(
                f"\n[{index}]"
            )

            print(
                "  tag:",
                element.tag_name,
            )

            print(
                "  id:",
                repr(
                    element.get_attribute("id")
                ),
            )

            print(
                "  name:",
                repr(
                    element.get_attribute("name")
                ),
            )

            print(
                "  role:",
                repr(
                    element.get_attribute("role")
                ),
            )

            print(
                "  type:",
                repr(
                    element.get_attribute("type")
                ),
            )

            print(
                "  class:",
                repr(
                    element.get_attribute("class")
                ),
            )

            print(
                "  placeholder:",
                repr(
                    element.get_attribute(
                        "placeholder"
                    )
                ),
            )

            print(
                "  aria-label:",
                repr(
                    element.get_attribute(
                        "aria-label"
                    )
                ),
            )

            print(
                "  readonly:",
                repr(
                    element.get_attribute(
                        "readonly"
                    )
                ),
            )

            print(
                "  visible:",
                safe_visible(element),
            )

        except Exception as error:
            print(
                "  [ERROR]",
                error,
            )


# =========================================================
# FIND TARGET IDS
# =========================================================

def find_target_elements(driver, title):
    print_separator(title)

    found_any = False

    for target_id in TARGET_IDS:
        elements = driver.find_elements(
            By.ID,
            target_id,
        )

        visible_elements = [
            element
            for element in elements
            if safe_visible(element)
        ]

        print(
            f"{target_id}: "
            f"total={len(elements)}, "
            f"visible={len(visible_elements)}"
        )

        for element in visible_elements:
            found_any = True

            print(
                "  -> tag:",
                element.tag_name,
            )

            print(
                "  -> role:",
                element.get_attribute("role"),
            )

            print(
                "  -> class:",
                element.get_attribute("class"),
            )

            print(
                "  -> aria-expanded:",
                element.get_attribute(
                    "aria-expanded"
                ),
            )

    if not found_any:
        print(
            "[INFO] Không tìm thấy target element "
            "visible trên trang hiện tại."
        )


# =========================================================
# PRINT CLICKABLE ELEMENTS
# =========================================================

def print_clickable_elements(driver):
    print_separator(
        "BUTTON / LINK / ROLE=BUTTON"
    )

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "button, a, [role='button']",
    )

    print(
        f"Tổng clickable element: {len(elements)}"
    )

    for index, element in enumerate(
        elements,
        start=1,
    ):
        try:
            if not safe_visible(element):
                continue

            text = safe_text(element)

            aria_label = (
                element.get_attribute(
                    "aria-label"
                )
                or ""
            ).strip()

            title = (
                element.get_attribute(
                    "title"
                )
                or ""
            ).strip()

            if (
                not text
                and not aria_label
                and not title
            ):
                continue

            print(
                f"\n[{index}]"
            )

            print(
                "  tag:",
                element.tag_name,
            )

            print(
                "  text:",
                repr(text),
            )

            print(
                "  aria-label:",
                repr(aria_label),
            )

            print(
                "  title:",
                repr(title),
            )

            print(
                "  class:",
                repr(
                    element.get_attribute(
                        "class"
                    )
                ),
            )

        except Exception:
            continue


# =========================================================
# FIND CREATE BOOKING BUTTON
# =========================================================

def find_create_booking_buttons(driver):
    """
    Tìm các button có khả năng mở form tạo booking.

    Không chỉ phụ thuộc vào đúng một text.
    """

    print_separator(
        "TÌM NÚT MỞ FORM THÊM ĐẶT XE"
    )

    candidates = []

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "button, "
        "[role='button'], "
        "a",
    )

    keywords = [
        "thêm đặt xe",
        "thêm",
        "tạo mới",
        "tạo",
        "đặt xe",
        "create",
        "add",
        "new",
    ]

    for element in elements:
        try:
            if not safe_visible(element):
                continue

            text = safe_text(
                element
            ).lower()

            aria_label = (
                element.get_attribute(
                    "aria-label"
                )
                or ""
            ).lower()

            title = (
                element.get_attribute(
                    "title"
                )
                or ""
            ).lower()

            combined = (
                f"{text} "
                f"{aria_label} "
                f"{title}"
            )

            if any(
                keyword in combined
                for keyword in keywords
            ):
                candidates.append(
                    element
                )

        except Exception:
            continue

    print(
        f"Tìm thấy {len(candidates)} candidate."
    )

    for index, element in enumerate(
        candidates,
        start=1,
    ):
        print(
            f"[{index}] "
            f"text={safe_text(element)!r} "
            f"tag={element.tag_name} "
            f"class={element.get_attribute('class')!r}"
        )

    return candidates


# =========================================================
# CLICK CREATE BOOKING
# =========================================================

def click_create_booking(driver):
    """
    Thử mở form thêm booking.

    Nếu tìm thấy nhiều candidate:
        thử từng candidate cho đến khi
        carId/customerId/status/paymentMethod
        xuất hiện.
    """

    candidates = find_create_booking_buttons(
        driver
    )

    if not candidates:
        print(
            "[WARN] Không tìm thấy nút "
            "mở form thêm booking."
        )
        return False

    for index, element in enumerate(
        candidates,
        start=1,
    ):
        try:
            print()
            print(
                f"[INFO] Thử click candidate #{index}: "
                f"{safe_text(element)!r}"
            )

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    behavior: 'instant',
                    block: 'center'
                });
                """,
                element,
            )

            time.sleep(0.5)

            try:
                element.click()

            except Exception:
                print(
                    "[WARN] click() lỗi -> "
                    "dùng JavaScript click."
                )

                driver.execute_script(
                    "arguments[0].click();",
                    element,
                )

            time.sleep(2)

            # Kiểm tra target fields
            found = False

            for target_id in TARGET_IDS:
                visible = [
                    x
                    for x in driver.find_elements(
                        By.ID,
                        target_id,
                    )
                    if safe_visible(x)
                ]

                if visible:
                    found = True
                    break

            # Kiểm tra modal/drawer
            modal_visible = bool(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    ".ant-modal:not(.ant-modal-hidden)"
                )
            )

            drawer_visible = bool(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    ".ant-drawer-open"
                )
            )

            print(
                "[INFO] modal visible:",
                modal_visible,
            )

            print(
                "[INFO] drawer visible:",
                drawer_visible,
            )

            print(
                "[INFO] target fields visible:",
                found,
            )

            if found:
                print(
                    "[PASS] Đã mở được form "
                    "chứa booking fields."
                )
                return True

        except Exception as error:
            print(
                f"[WARN] Candidate #{index} lỗi:",
                error,
            )

    print(
        "[FAIL] Đã thử các candidate nhưng "
        "không tìm thấy form booking."
    )

    return False


# =========================================================
# PRINT TARGET DETAILS
# =========================================================

def print_target_details(driver):
    print_separator(
        "CHI TIẾT BOOKING FORM"
    )

    for target_id in TARGET_IDS:
        elements = driver.find_elements(
            By.ID,
            target_id,
        )

        visible_elements = [
            element
            for element in elements
            if safe_visible(element)
        ]

        print(
            f"\n### {target_id}"
        )

        print(
            "Total:",
            len(elements),
        )

        print(
            "Visible:",
            len(visible_elements),
        )

        for element in visible_elements:
            print(
                "tag:",
                element.tag_name,
            )

            print(
                "role:",
                element.get_attribute("role"),
            )

            print(
                "class:",
                element.get_attribute("class"),
            )

            print(
                "aria-expanded:",
                element.get_attribute(
                    "aria-expanded"
                ),
            )

            print(
                "aria-haspopup:",
                element.get_attribute(
                    "aria-haspopup"
                ),
            )

            print(
                "readonly:",
                element.get_attribute(
                    "readonly"
                ),
            )

            print(
                "outerHTML:"
            )

            try:
                html = driver.execute_script(
                    "return arguments[0].outerHTML;",
                    element,
                )

                print(html)

            except Exception as error:
                print(
                    "[ERROR]",
                    error,
                )


# =========================================================
# PRINT COMBOBOXES
# =========================================================

def print_comboboxes(driver):
    print_separator(
        "TẤT CẢ COMBOBOX"
    )

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='combobox']",
    )

    print(
        f"Tổng combobox: {len(elements)}"
    )

    for index, element in enumerate(
        elements,
        start=1,
    ):
        try:
            print(
                f"\n[{index}]"
            )

            print(
                "id:",
                element.get_attribute("id"),
            )

            print(
                "name:",
                element.get_attribute("name"),
            )

            print(
                "class:",
                element.get_attribute("class"),
            )

            print(
                "aria-expanded:",
                element.get_attribute(
                    "aria-expanded"
                ),
            )

            print(
                "visible:",
                safe_visible(element),
            )

        except Exception:
            continue


# =========================================================
# SEARCH PAGE SOURCE
# =========================================================

def inspect_page_source(driver):
    print_separator(
        "KIỂM TRA PAGE SOURCE"
    )

    source = driver.page_source or ""

    for target_id in TARGET_IDS:
        print(
            f"'{target_id}' trong HTML:",
            target_id in source,
        )

    print(
        "'ant-modal' trong HTML:",
        "ant-modal" in source,
    )

    print(
        "'ant-drawer' trong HTML:",
        "ant-drawer" in source,
    )

    try:
        with open(
            OUTPUT_HTML,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(source)

        print(
            "\n[INFO] Đã lưu page source:"
        )

        print(
            OUTPUT_HTML
        )

    except Exception as error:
        print(
            "[ERROR] Không lưu được page source:",
            error,
        )


# =========================================================
# SCREENSHOT
# =========================================================

def save_screenshot(
    driver,
    path,
):
    try:
        driver.save_screenshot(path)

        print(
            "[INFO] Screenshot:",
            path,
        )

    except Exception as error:
        print(
            "[ERROR] Không chụp được screenshot:",
            error,
        )


# =========================================================
# MAIN
# =========================================================

def main():

    driver = None

    print_separator(
        "START BOOKING PAGE DIAGNOSTIC"
    )

    try:

        # -------------------------------------------------
        # CREATE DRIVER
        # -------------------------------------------------

        print(
            "[INFO] Creating Chrome driver..."
        )

        driver = DriverFactory.create_driver(
            headless=False,
            keep_session=True,
        )

        # -------------------------------------------------
        # OPEN PAGE
        # -------------------------------------------------

        print(
            "[INFO] Opening:",
            URL,
        )

        driver.get(URL)

        wait_page_loaded(driver)

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login_if_needed(
            driver
        )

        # Sau login mở lại booking page
        if (
            "/bookings"
            not in (driver.current_url or "")
        ):
            print(
                "[INFO] Điều hướng lại /bookings..."
            )

            driver.get(URL)

        wait_page_loaded(driver)

        # -------------------------------------------------
        # PAGE INFO
        # -------------------------------------------------

        print_page_info(
            driver
        )

        # -------------------------------------------------
        # BEFORE MODAL
        # -------------------------------------------------

        print_all_inputs(
            driver,
            "INPUT TRƯỚC KHI MỞ FORM",
        )

        find_target_elements(
            driver,
            "TARGET IDS TRƯỚC KHI MỞ FORM",
        )

        print_comboboxes(
            driver
        )

        print_clickable_elements(
            driver
        )

        inspect_page_source(
            driver
        )

        save_screenshot(
            driver,
            SCREENSHOT_BEFORE,
        )

        # -------------------------------------------------
        # OPEN BOOKING FORM
        # -------------------------------------------------

        opened = click_create_booking(
            driver
        )

        # -------------------------------------------------
        # AFTER MODAL
        # -------------------------------------------------

        if opened:

            wait_page_loaded(
                driver
            )

            print_separator(
                "SAU KHI MỞ FORM BOOKING"
            )

            print_page_info(
                driver
            )

            print_all_inputs(
                driver,
                "INPUT SAU KHI MỞ FORM",
            )

            find_target_elements(
                driver,
                "TARGET IDS SAU KHI MỞ FORM",
            )

            print_target_details(
                driver
            )

            print_comboboxes(
                driver
            )

            inspect_page_source(
                driver
            )

            save_screenshot(
                driver,
                SCREENSHOT_AFTER,
            )

        else:

            print_separator(
                "KHÔNG MỞ ĐƯỢC FORM BOOKING"
            )

            print(
                "Hãy kiểm tra danh sách button "
                "được in ở phía trên."
            )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print_separator(
            "KẾT LUẬN"
        )

        target_status = {}

        for target_id in TARGET_IDS:

            visible = [
                element
                for element in driver.find_elements(
                    By.ID,
                    target_id,
                )
                if safe_visible(element)
            ]

            target_status[target_id] = bool(
                visible
            )

        for target_id, exists in target_status.items():

            if exists:
                print(
                    f"[FOUND] {target_id}"
                )
            else:
                print(
                    f"[NOT FOUND] {target_id}"
                )

        print()
        print(
            "Nếu các field FOUND sau khi mở form, "
            "thì nguyên nhân lỗi Selenium hiện tại "
            "rất có thể là runner đang cố tìm "
            "carId/customerId/status/paymentMethod "
            "ngay khi vừa vào /bookings, thay vì "
            "click 'Thêm đặt xe' trước."
        )

        print()
        print(
            "=== DIAGNOSTIC FINISHED ==="
        )

        input(
            "\nNhấn Enter để đóng trình duyệt..."
        )

    except Exception as error:

        print_separator(
            "FATAL ERROR"
        )

        print(
            type(error).__name__
        )

        print(
            str(error)
        )

    finally:

        if driver:

            try:
                DriverFactory.quit_driver(
                    driver
                )

            except Exception:

                try:
                    driver.quit()

                except Exception:
                    pass


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
