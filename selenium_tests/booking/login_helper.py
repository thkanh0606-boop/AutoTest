from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOGIN_URL = "https://courses.plt.pro.vn/login"
BOOKING_URL = "https://courses.plt.pro.vn/bookings"

TEST_EMAIL = "test@gmail.com"
TEST_PASSWORD = "123123"

WAIT_TIME = 15


# =========================================================
# LOCATORS
# =========================================================

EMAIL_INPUT = (By.ID, "email")
PASSWORD_INPUT = (By.ID, "password")
LOGIN_SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")


# =========================================================
# CREATE DRIVER
# =========================================================

def create_driver():
    """Tạo Chrome driver và maximize window."""

    driver = webdriver.Chrome()
    driver.maximize_window()

    return driver


# =========================================================
# LOGIN
# =========================================================

def login(driver, wait):
    """
    Thực hiện login vào https://courses.plt.pro.vn/login
    và điều hướng sang trang /bookings.

    Trả về True nếu thành công, False nếu thất bại.
    """

    try:

        driver.get(LOGIN_URL)

        # Email
        email_field = wait.until(
            EC.visibility_of_element_located(EMAIL_INPUT)
        )
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)

        # Password
        password_field = wait.until(
            EC.visibility_of_element_located(PASSWORD_INPUT)
        )
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)

        # Nút Đăng nhập
        submit_button = wait.until(
            EC.element_to_be_clickable(LOGIN_SUBMIT_BUTTON)
        )
        submit_button.click()

        # Chờ rời khỏi trang /login
        wait.until(EC.url_changes(LOGIN_URL))

        current_url = driver.current_url

        if "/login" in current_url:
            print("[LOGIN] FAIL: Vẫn còn ở trang /login sau khi submit")
            return False

        # Truy cập trang booking
        driver.get(BOOKING_URL)

        wait.until(EC.url_contains("/bookings"))

        print("[LOGIN] PASS")
        print("[BOOKING] PAGE OPENED")

        return True

    except Exception as e:

        print(f"[LOGIN] FAIL: {e}")

        return False


# =========================================================
# MAIN (chạy độc lập để kiểm tra login)
# =========================================================

def run_login_test():

    driver = create_driver()

    wait = WebDriverWait(driver, WAIT_TIME)

    try:

        print("\n")
        print("=" * 60)
        print("             LOGIN TEST")
        print("=" * 60)

        result = login(driver, wait)

        print("\n")
        print("=" * 60)
        print("LOGIN TEST COMPLETED")
        print("=" * 60)
        print(f"RESULT : {'PASS' if result else 'FAIL'}")

    except Exception as e:

        print("[CRITICAL ERROR]", e)

    finally:

        input("\nNhấn Enter để đóng trình duyệt...")

        driver.quit()


if __name__ == "__main__":
    run_login_test()