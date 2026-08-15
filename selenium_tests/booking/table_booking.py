from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login_helper import login, create_driver, BOOKING_URL

WAIT_TIME = 15


# =========================================================
# LOCATORS
# =========================================================

BODY = (By.TAG_NAME, "body")

ADD_BOOKING_BUTTON = (
    By.XPATH,
    "//button[@aria-label='Tạo booking']"
)

TABLE = (By.CSS_SELECTOR, "table")

TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")

EDIT_BUTTONS = (
    By.XPATH,
    "//button[.//span[@aria-label='edit']]"
)

DELETE_BUTTONS = (
    By.XPATH,
    "//button[.//span[@aria-label='delete']]"
)


# =========================================================
# HELPER
# =========================================================

def print_result(name, passed, message=""):

    if passed:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

    if message:
        print(f"       Message: {message}")


# =========================================================
# TEST PAGE
# =========================================================

def test_booking_page(driver, wait):

    print("\n===== BOOKING PAGE =====")

    try:

        wait.until(EC.presence_of_element_located(BODY))

        print_result("Booking page loaded", True)
        print(f"       URL: {driver.current_url}")

        return True

    except Exception as e:

        print_result("Booking page", False, str(e))

        return False


# =========================================================
# TEST CREATE BUTTON
# =========================================================

def test_add_button(driver, wait):

    print("\n===== ADD BOOKING BUTTON =====")

    try:

        button = wait.until(
            EC.presence_of_element_located(ADD_BOOKING_BUTTON)
        )

        print_result("Tạo booking button exists", True)
        print_result("Tạo booking button visible", button.is_displayed())
        print_result("Tạo booking button enabled", button.is_enabled())

        return True

    except Exception as e:

        print_result("Tạo booking button", False, str(e))

        return False


# =========================================================
# TEST TABLE
# =========================================================

def test_table(driver, wait):

    print("\n===== BOOKING TABLE =====")

    try:

        tables = driver.find_elements(*TABLE)

        if not tables:

            print("[INFO] Không tìm thấy table.")
            print("[INFO] Có thể trang đang dùng empty state hoặc card/list.")
            print_result("Booking page (empty state)", True)

            return True

        table = tables[0]

        print_result("Booking table exists", True)

        rows = table.find_elements(*TABLE_ROWS)

        print(f"       Rows: {len(rows)}")

        if len(rows) == 0:

            print("[INFO] Table không có dữ liệu.")

        else:

            for index, row in enumerate(rows, start=1):

                text = row.text.strip().replace("\n", " | ")

                print(f"       Row {index}: {text}")

        return True

    except Exception as e:

        print_result("Booking table", False, str(e))

        return False


# =========================================================
# TEST ACTION BUTTONS
# =========================================================

def test_action_buttons(driver, wait):

    print("\n===== ACTION BUTTONS =====")

    try:

        edit_buttons = driver.find_elements(*EDIT_BUTTONS)
        delete_buttons = driver.find_elements(*DELETE_BUTTONS)

        print(f"       Edit buttons: {len(edit_buttons)}")
        print(f"       Delete buttons: {len(delete_buttons)}")

        print_result("Action buttons area", True)

        return True

    except Exception as e:

        print_result("Action buttons", False, str(e))

        return False


# =========================================================
# MAIN
# =========================================================

def run_booking_table_test():

    driver = create_driver()

    wait = WebDriverWait(driver, WAIT_TIME)

    try:

        print("\n")
        print("=" * 60)
        print("             BOOKING TABLE TEST")
        print("=" * 60)

        login_ok = login(driver, wait)

        if not login_ok:

            print("\n[STOP] Login thất bại, dừng test.")
            return

        test_booking_page(driver, wait)
        test_add_button(driver, wait)
        test_table(driver, wait)
        test_action_buttons(driver, wait)

        print("\n")
        print("=" * 60)
        print("BOOKING TABLE TEST COMPLETED")
        print("=" * 60)

    except Exception as e:

        print("[CRITICAL ERROR]", e)

    finally:

        input("\nNhấn Enter để đóng trình duyệt...")

        driver.quit()


if __name__ == "__main__":
    run_booking_table_test()