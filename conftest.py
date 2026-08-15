import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.driver_factory import DriverFactory


LOGIN_URL = "https://courses.plt.pro.vn/login"
BOOKING_URL = "https://courses.plt.pro.vn/bookings"

TEST_EMAIL = "test@gmail.com"
TEST_PASSWORD = "123123"

WAIT_TIME = 20


def login(driver):
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, WAIT_TIME)

    email = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[placeholder='ban@plt.pro.vn']"
            )
        )
    )
    email.clear()
    email.send_keys(TEST_EMAIL)

    password = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[placeholder='Nhập mật khẩu']"
            )
        )
    )
    password.clear()
    password.send_keys(TEST_PASSWORD)

    button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit']"
            )
        )
    )
    button.click()

    wait.until(
        lambda d: "/login" not in d.current_url.lower()
    )

    print("[LOGIN] PASS")
    print("[LOGIN] URL:", driver.current_url)


@pytest.fixture
def driver():
    driver = None

    try:
        driver = DriverFactory.create_driver(
            headless=False,
            keep_session=False
        )

        login(driver)

        driver.get(BOOKING_URL)

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            lambda d: "/bookings" in d.current_url.lower()
        )

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, "//main")
            )
        )

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, "//main//table")
            )
        )

        print("[BOOKING] PASS")
        print("[BOOKING] URL:", driver.current_url)

        yield driver

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass