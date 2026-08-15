import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from core.driver_factory import DriverFactory

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
def ensure_user_page_ready(request):
    """
    Chạy trước MỖI testcase: Đảm bảo driver sống, luôn quay về trang Quản lý người dùng.
    Nếu bị out ra trang Login thì sẽ tự động đăng nhập lại.
    """
    driver = getattr(request.cls, "driver", None)
    if not driver:
        return

    # 1. Kiểm tra driver hỏng session -> Tạo lại
    try:
        _ = driver.current_url
    except (InvalidSessionIdException, WebDriverException):
        print("\n[HỆ THỐNG] Session đóng. Đang khởi tạo lại Driver...")
        driver = create_browser_instance()
        request.cls.driver = driver

    SIGN_OUT_LOCATOR = (By.XPATH, "//button[contains(., 'Sign out') or contains(., 'Đăng xuất')] | //*[contains(@class, 'anticon-logout')]")

    # 2. Xử lý Đăng nhập nếu bị văng ra trang Login
    try:
        if "login" in driver.current_url.lower() or len(driver.find_elements(*SIGN_OUT_LOCATOR)) == 0:
            driver.get(LOGIN_URL)
            wait = WebDriverWait(driver, 8)
            
            email_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email' or @id='email' or @name='email' or contains(@placeholder, 'email') or contains(@placeholder, 'ban@plt.pro.vn')]")))
            email_el.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            email_el.send_keys(USER_EMAIL)
            
            pass_el = driver.find_element(By.XPATH, "//input[@type='password' or @id='password' or @name='password' or contains(@placeholder, 'Password') or contains(@placeholder, 'mật khẩu')]")
            pass_el.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            pass_el.send_keys(USER_PASS)
            
            driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Log in') or contains(., 'Đăng nhập')]").click()
            wait.until(EC.presence_of_element_located(SIGN_OUT_LOCATOR))
    except Exception as e:
        print(f"\n[WARN Login]: {e}")

    # 3. Đảm bảo luôn đứng ở đúng trang Quản lý người dùng trước mỗi testcase
    try:
        if driver.current_url != TARGET_URL:
            driver.get(TARGET_URL)
            time.sleep(1)
    except Exception:
        pass