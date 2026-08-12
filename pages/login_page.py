<<<<<<< HEAD
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from core.config import Config

class LoginPage(BasePage):
    # Bộ Selector đa năng bắt được cả ô Username (Text input) lẫn Email
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[name='username'], input[type='text'], input[type='email'], input[name='email'], #username, #email")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password")
    LOGIN_BTN = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button.btn-primary, .btn-login, .login-btn")
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger, .error-message, .invalid-feedback")

    def __init__(self, driver):
        super().__init__(driver)


    def load(self, url: str = None):
        target_url = url if url else Config.BASE_URL
        self.open_url(target_url)

    def execute_login(self, email: str, password: str):
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def get_error_message(self) -> str:
        try:
            return self.get_text(self.ERROR_MSG)
        except Exception:
            return ""
=======
import time
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from locators.pcm_locators import PCMLocators

class LoginPage(BasePage):
    def login(self, username, password, delay=1.0):
        # Nhập Username / Email
        email_el = self.wait.until(EC.element_to_be_clickable(PCMLocators.LOGIN_EMAIL_INPUT))
        self.highlight_element(email_el)
        email_el.clear()
        email_el.send_keys(username)
        time.sleep(delay)

        # Nhập Password
        pwd_el = self.wait.until(EC.element_to_be_clickable(PCMLocators.LOGIN_PASSWORD_INPUT))
        self.highlight_element(pwd_el)
        pwd_el.clear()
        pwd_el.send_keys(password)
        time.sleep(delay)

        # Click Submit
        btn_el = self.wait.until(EC.element_to_be_clickable(PCMLocators.LOGIN_SUBMIT_BTN))
        self.highlight_element(btn_el, color="green")
        btn_el.click()
        time.sleep(delay)
>>>>>>> 4a18db9 (Initial commit: Completed Selenium Pytest Automation Suite for PLT Courses)
