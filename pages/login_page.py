import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Config
from pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL_INPUT = (
        By.CSS_SELECTOR,
        "input[name='username'], input[type='text'], input[type='email'], input[name='email'], #username, #email",
    )
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password")
    LOGIN_BTN = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button.btn-primary, .btn-login, .login-btn")
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger, .error-message, .invalid-feedback")

    def load(self, url: str = None):
        self.open_url(url or Config.BASE_URL)

    def execute_login(self, email: str, password: str):
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def _already_inside_app(self) -> bool:
        return "login" not in self.driver.current_url.lower() or bool(self.driver.find_elements(By.CSS_SELECTOR, "main"))

    def login(self, username: str, password: str, delay: float = 0):
        try:
            email_el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.EMAIL_INPUT))
        except Exception:
            if self._already_inside_app():
                return True
            raise

        self.highlight_element(email_el)
        email_el.clear()
        email_el.send_keys(username)
        if delay:
            time.sleep(delay)

        pwd_el = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT))
        self.highlight_element(pwd_el)
        pwd_el.clear()
        pwd_el.send_keys(password)
        if delay:
            time.sleep(delay)

        btn_el = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN))
        self.highlight_element(btn_el, color="green")
        btn_el.click()
        if delay:
            time.sleep(delay)
        return True

    def get_error_message(self) -> str:
        try:
            return self.get_text(self.ERROR_MSG)
        except Exception:
            return ""
