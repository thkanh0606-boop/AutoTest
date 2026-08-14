import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from core.config import Config


class DriverFactory:
    _driver: webdriver.Chrome = None

    @classmethod
    def get_driver(cls, headless: bool = False, keep_session: bool = True) -> webdriver.Chrome:
        """GIỮ NGUYÊN CODE CŨ CỦA BẠN"""
        if cls._driver is None:
            cls._driver = cls.create_driver(headless=headless, keep_session=keep_session)
        else:
            try:
                _ = cls._driver.window_handles
            except Exception:
                cls._driver = cls.create_driver(headless=headless, keep_session=keep_session)
        return cls._driver

    @staticmethod
    def create_driver(headless: bool = False, keep_session: bool = True) -> webdriver.Chrome:
        """GIỮ NGUYÊN CODE CŨ CỦA BẠN"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")

        if keep_session:
            profile_path = os.path.join(Config.BASE_DIR, "chrome_profile")
            options.add_argument(f"--user-data-dir={profile_path}")

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1440,1200")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

        return driver

    @classmethod
    def quit_driver(cls) -> None:
        """GIỮ NGUYÊN CODE CŨ CỦA BẠN"""
        if cls._driver is not None:
            try:
                cls._driver.quit()
            except Exception:
                pass
            finally:
                cls._driver = None

    # =========================================================
    # BỔ SUNG THÊM CÁC HÀM CHO MODULE WEBSITE/PAGE/ELEMENT
    # =========================================================

    @classmethod
    def _convert_by(cls, locator_type: str):
        loc = str(locator_type).upper()
        if loc == "XPATH":
            return By.XPATH
        elif loc == "ID":
            return By.ID
        elif loc == "CSS":
            return By.CSS_SELECTOR
        elif loc == "NAME":
            return By.NAME
        return By.XPATH

    @classmethod
    def check_and_highlight(cls, url: str, locator_type: str, locator_value: str, fallback_type=None, fallback_value=None):
        """Thực hiện Check Locator, Tô sáng (Highlight) và hỗ trợ Fallback"""
        driver = cls.get_driver(keep_session=True)
        try:
            if driver.current_url != url:
                driver.get(url)

            element = None
            # 1. Thử locator chính
            try:
                by = cls._convert_by(locator_type)
                element = driver.find_element(by, locator_value)
            except Exception:
                # 2. Thử Locator Fallback nếu có
                if fallback_type and fallback_value:
                    by_fb = cls._convert_by(fallback_type)
                    element = driver.find_element(by_fb, fallback_value)

            if element:
                # Highlight viền đỏ, nền vàng
                driver.execute_script(
                    "arguments[0].setAttribute('style', 'border: 3px solid red; background: yellow !important;');", 
                    element
                )
                time.sleep(0.8)
                return True, "PASSED", None
            else:
                raise Exception("Không tìm thấy Element trên trang")

        except Exception as e:
            screenshot_path = cls.take_screenshot("error_locator")
            return False, str(e), screenshot_path

    @classmethod
    def scan_elements(cls, url: str):
        """Tự động quét (Scan) phát hiện các element trên trang"""
        driver = cls.get_driver(keep_session=True)
        if driver.current_url != url:
            driver.get(url)

        elements = driver.find_elements(By.XPATH, "//button | //input | //a")
        scanned = []
        for idx, elem in enumerate(elements[:10]):
            scanned.append({
                "key": f"scanned_elem_{idx+1}",
                "name": elem.text or elem.get_attribute("placeholder") or f"Auto Element {idx+1}",
                "type": "XPATH",
                "value": f"(//button | //input | //a)[{idx+1}]"
            })
        return scanned

    @classmethod
    def take_screenshot(cls, prefix="screenshot"):
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        if cls._driver:
            cls._driver.save_screenshot(filename)
        return filename