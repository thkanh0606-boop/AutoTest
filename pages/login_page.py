import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://courses.plt.pro.vn/login"

    INPUT_EMAIL = (By.ID, "email")
    INPUT_PASSWORD = (By.ID, "password")
    
    # Sử dụng XPath chính xác từ thực tế của bạn
    BTN_LOGIN = (
        By.XPATH, 
        '//*[@id="root"]/div/div/div[2]/div/div/form/button | '
        '//button[@type="submit" and contains(., "Đăng nhập")]'
    )

    def navigate(self):
        self.open_url(self.URL)

    def login(self, email: str = "test@gmail.com", password: str = "123123"):
        self.navigate()
        time.sleep(0.5)
        
        self.send_keys(self.INPUT_EMAIL, email)
        self.send_keys(self.INPUT_PASSWORD, password)
        self.click(self.BTN_LOGIN)
        
        # Chờ tối đa 10s cho chuyển trang
        try:
            WebDriverWait(self.driver, 10).until(lambda d: "/login" not in d.current_url)
        except Exception:
            print(f"[WARN] URL sau login: {self.driver.current_url}")