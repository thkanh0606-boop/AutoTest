from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    def find_visible(self, locator: tuple):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.highlight_element(element)
        return element

    def click(self, locator: tuple):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.highlight_element(element, color="green")
        element.click()

    def type_text(self, locator: tuple, text: str):
        element = self.find(locator)
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text)

    def send_keys(self, locator: tuple, text: str):
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text

    def get_current_url(self) -> str:
        return self.driver.current_url

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def highlight_element(self, element, color="yellow", border="3px solid red"):
        try:
            original_style = element.get_attribute("style")
            new_style = f"background-color: {color}; border: {border}; {original_style}"
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, new_style)
        except Exception:
            pass
