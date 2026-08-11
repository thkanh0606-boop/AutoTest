from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from core.config import Config

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)

    def open_url(self, url: str):
        self.driver.get(url)

    def find(self, locator: tuple):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator: tuple):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator: tuple, text: str):
        element = self.find(locator)
        element.click()
        # Xóa triệt để dữ liệu cũ trong ô input
        element.send_keys(Keys.CONTROL + "a" if Keys.CONTROL else Keys.COMMAND + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text

    def get_current_url(self) -> str:
        """Lấy URL hiện tại của trình duyệt"""
        return self.driver.current_url

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """Kiểm tra phần tử có đang hiển thị hay không (dùng cho thông báo lỗi)"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False