import os
import time
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from core.driver_factory import DriverFactory

# Cấu hình Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Cấu hình thông tin tài khoản và URL
LOGIN_URL = "https://courses.plt.pro.vn/login"
TARGET_URL = "https://courses.plt.pro.vn/users"
USER_EMAIL = "test@gmail.com"
USER_PASS = "123123"

def create_browser_instance():
    # Sử dụng DriverFactory chung của dự án
    return DriverFactory.create_driver(headless=False, keep_session=False)

@pytest.fixture(scope="class")
def setup_driver(request):
    driver = create_browser_instance()
    request.cls.driver = driver
    yield driver
    try:
        driver.quit()
    except Exception:
        pass

@pytest.fixture(scope="function", autouse=True)
def ensure_logged_in_and_on_users_page(request):
    driver = getattr(request.cls, "driver", None)
    if not driver:
        return

    try:
        _ = driver.current_url
    except (InvalidSessionIdException, WebDriverException):
        driver = create_browser_instance()
        request.cls.driver = driver

    wait = WebDriverWait(driver, 8)
    SIGN_OUT_LOCATOR = (By.XPATH, "//button[contains(., 'Đăng xuất') or contains(., 'Sign out')] | //*[contains(@class, 'logout')]")

    try:
        is_logged_in = len(driver.find_elements(*SIGN_OUT_LOCATOR)) > 0
        if "login" in driver.current_url.lower() or not is_logged_in:
            logging.info("Thực hiện đăng nhập tự động...")
            driver.get(LOGIN_URL)
            
            email_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email' or @id='email' or @name='email' or contains(@placeholder, 'email') or contains(@placeholder, 'ban@plt.pro.vn')]")))
            email_el.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            email_el.send_keys(USER_EMAIL)
            
            pass_el = driver.find_element(By.XPATH, "//input[@type='password' or @id='password' or @name='password' or contains(@placeholder, 'Password') or contains(@placeholder, 'mật khẩu')]")
            pass_el.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            pass_el.send_keys(USER_PASS)
            
            btn_login = driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Log in') or contains(., 'Đăng nhập')]")
            btn_login.click()
            time.sleep(1.5)
    except Exception as e:
        logging.warning(f"Lỗi đăng nhập: {e}")

    try:
        if TARGET_URL not in driver.current_url:
            driver.get(TARGET_URL)
            time.sleep(1)
    except Exception:
        pass

# --- HOOK CHUẨN CỦA PYTEST: pytest_runtest_makereport ---
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = getattr(item.cls, "driver", None) if item.cls else None
        if driver:
            screenshot_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            filename = f"{item.name}_{int(time.time())}.png"
            filepath = os.path.join(screenshot_dir, filename)
            driver.save_screenshot(filepath)
            logging.error(f"[FAIL EVIDENCE] Đã tự động chụp ảnh màn hình tại: {filepath}")