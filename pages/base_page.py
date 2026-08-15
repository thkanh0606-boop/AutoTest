import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from core.config import Config


class BasePage:
    def __init__(self, driver, timeout=None):
        self.driver = driver
        # Ưu tiên lấy timeout truyền vào, nếu không sẽ dùng Config từ main
        wait_time = timeout if timeout is not None else getattr(Config, 'EXPLICIT_WAIT', 20)
        self.wait = WebDriverWait(driver, wait_time)

    def open_url(self, url: str):
        self.driver.get(url)

    def find(self, locator: tuple):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator: tuple):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def find_visible(self, locator: tuple):
        """Tìm phần tử hiển thị, cuộn vào giữa màn hình và highlight viền đỏ"""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.highlight_element(element)
        return element

    def find_clickable(self, locator: tuple):
        """Tìm phần tử có thể click, cuộn vào màn hình và highlight"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.highlight_element(element, color="green")
        return element

    def click(self, locator: tuple):
        """Click an toàn hỗ trợ JS fallback nếu phần tử bị che"""
        element = self.find_clickable(locator)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator: tuple, text: str):
        """Nhập văn bản bằng Ctrl+A -> Backspace -> send_keys"""
        element = self.find_visible(locator)
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text)

    def send_keys(self, locator: tuple, text: str):
        """Nhập văn bản đơn giản theo tiêu chuẩn cũ"""
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text

    def get_current_url(self) -> str:
        return self.driver.current_url

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """Kiểm tra phần tử hiển thị nhanh không làm ngắt chương trình"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, Exception):
            return False

    def highlight_element(self, element, color="transparent", border="3px solid red"):
        """Vẽ viền đỏ xung quanh phần tử UI đang thao tác"""
        try:
            original_style = element.get_attribute("style") or ""
            new_style = f"background-color: {color}; border: {border}; {original_style}"
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, new_style)
            time.sleep(0.1)
        except Exception:
            pass