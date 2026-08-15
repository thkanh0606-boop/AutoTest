from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class BasePage:
    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find_visible(self, locator):
        """Tìm element hiển thị trên màn hình"""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def find_clickable(self, locator):
        """Tìm element có thể click được"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def click(self, locator):
        """Click an toàn hỗ trợ JS fallback nếu bị che"""
        element = self.find_clickable(locator)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys(self, locator, text):
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def is_element_visible(self, locator, timeout=5):
        """Kiểm tra sự tồn tại của element nhanh mà không crash test"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False