import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Config
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://courses.plt.pro.vn/login"

    # Locators linh hoạt kết hợp cả ID thực tế lẫn CSS Selector rộng
    INPUT_EMAIL = (
        By.XPATH,
        "//input[@id='email' or @name='email' or @type='email' or contains(@placeholder, 'email') or contains(@placeholder, 'ban@plt.pro.vn')]"
    )
    INPUT_PASSWORD = (
        By.XPATH,
        "//input[@id='password' or @name='password' or @type='password' or contains(@placeholder, 'mật khẩu')]"
    )
    BTN_LOGIN = (
        By.XPATH,
        '//*[@id="root"]/div/div/div[2]/div/div/form/button | //button[@type="submit" and (contains(., "Đăng nhập") or contains(., "Log in"))]'
    )
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger, .error-message, .invalid-feedback")

    def navigate(self, url: str = None):
        """Mở trang đăng nhập"""
        target_url = url or getattr(Config, 'BASE_URL', self.URL)
        self.open_url(target_url)

    def load(self, url: str = None):
        """Alias tương thích cho navigate()"""
        self.navigate(url)

    def _already_inside_app(self) -> bool:
        """Kiểm tra xem người dùng đã ở bên trong hệ thống chưa"""
        return "login" not in self.driver.current_url.lower() or bool(self.driver.find_elements(By.CSS_SELECTOR, "main"))

    def login(self, email: str = "test@gmail.com", password: str = "123123", delay: float = 0):
        """Thực hiện đăng nhập an toàn, có hỗ trợ highlight và kiểm tra session sẵn"""
        try:
            email_el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.INPUT_EMAIL))
        except Exception:
            if self._already_inside_app():
                return True
            self.navigate()
            email_el = self.wait.until(EC.element_to_be_clickable(self.INPUT_EMAIL))

        self.highlight_element(email_el)
        email_el.clear()
        email_el.send_keys(email)
        if delay:
            time.sleep(delay)

        pwd_el = self.wait.until(EC.element_to_be_clickable(self.INPUT_PASSWORD))
        self.highlight_element(pwd_el)
        pwd_el.clear()
        pwd_el.send_keys(password)
        if delay:
            time.sleep(delay)

        btn_el = self.wait.until(EC.element_to_be_clickable(self.BTN_LOGIN))
        self.highlight_element(btn_el, color="green")
        btn_el.click()
        if delay:
            time.sleep(delay)

        # Chờ tối đa 10s cho quá trình chuyển trang hoàn tất
        try:
            WebDriverWait(self.driver, 10).until(lambda d: "/login" not in d.current_url.lower())
        except Exception:
            print(f"[WARN] URL sau login: {self.driver.current_url}")

        return True

    def execute_login(self, email: str, password: str):
        """Rút gọn cho các script test cũ"""
        self.login(email=email, password=password)

    def get_error_message(self) -> str:
        """Lấy thông báo lỗi khi đăng nhập thất bại"""
        try:
            return self.get_text(self.ERROR_MSG)
        except Exception:
            return ""