from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import Config
from core.driver_factory import DriverFactory


LOGIN_URL = "https://courses.plt.pro.vn/login"
BOOKING_URL = "https://courses.plt.pro.vn/bookings"


def test_open_booking():

    driver = DriverFactory.create_driver(
        headless=False,
        keep_session=False
    )

    try:
        driver.get(LOGIN_URL)

        wait = WebDriverWait(driver, 20)

        email = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[placeholder='ban@plt.pro.vn']"
                )
            )
        )

        email.clear()
        email.send_keys(Config.TEST_EMAIL)

        password = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[placeholder='Nhập mật khẩu']"
                )
            )
        )

        password.clear()
        password.send_keys(Config.TEST_PASSWORD)

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button[type='submit']"
                )
            )
        ).click()

        wait.until(
            lambda d: "/login" not in d.current_url.lower()
        )

        driver.get(BOOKING_URL)

        wait.until(
            lambda d: "/bookings" in d.current_url.lower()
        )

        print("BOOKING OPEN:", driver.current_url)

    finally:
        driver.quit()