import os
from datetime import datetime

import pytest

from core.config import Config
from core.driver_factory import DriverFactory
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def driver(request):
    _driver = DriverFactory.create_driver(headless=False)
    request.node.driver = _driver
    yield _driver
    _driver.quit()
    

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
import os
from datetime import datetime



@pytest.fixture(scope="function")
def logged_in_driver(driver):
    driver.get(Config.BASE_URL)
    login_page = LoginPage(driver)
    login_page.login(Config.TEST_EMAIL, Config.TEST_PASSWORD)
    return driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = getattr(item, "driver", None)
        if driver:
            screenshot_dir = os.path.join(os.getcwd(), "reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(screenshot_dir, f"FAIL_{item.name}_{timestamp}.png")
            driver.save_screenshot(file_path)

            print(f"\n[SCREENSHOT] Đã lưu ảnh lỗi tại: {file_path}")

            print(f"\n[SCREENSHOT] Saved failure screenshot: {file_path}")
