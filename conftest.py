import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

# Cấu hình thông tin tài khoản và URL
LOGIN_URL = "https://courses.plt.pro.vn/login"
TARGET_URL = "https://courses.plt.pro.vn/users"
USER_EMAIL = "test@gmail.com"  # <--- Thay Email chuẩn của bạn
USER_PASS = "123123"         # <--- Thay Pass chuẩn của bạn

def create_browser_instance():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver

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
            
            email_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email' or @id='email' or @name='email' or contains(@placeholder, 'email')]")))
            email_el.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            email_el.send_keys(USER_EMAIL)
            
            pass_el = driver.find_element(By.XPATH, "//input[@type='password' or @id='password' or @name='password' or contains(@placeholder, 'Password')]")
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