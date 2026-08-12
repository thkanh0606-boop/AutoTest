import pytest

from core.driver_factory import DriverFactory

@pytest.fixture(scope="function")
def driver():
    """Fixture tạo và đóng WebDriver tự động cho từng test case của PyTest"""
    _driver = DriverFactory.create_driver(headless=False)
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
def driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless") # Mở comment nếu muốn chạy ngầm
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    request.node.driver = driver
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """Fixture dùng chung cho Test Case 2 & 3: Đã đăng nhập sẵn."""
    driver.get("https://courses.plt.pro.vn/login")
    login_page = LoginPage(driver)
    
    # Thực hiện login
    login_page.login("test@gmail.com", "123123", delay=0.5)
    time.sleep(2)
    return driver





# Hook tự động chụp ảnh màn hình khi Test bị Fail
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # Chỉ xử lý trong giai đoạn call (thực thi test case)
    if report.when == "call" and report.failed:
        driver = getattr(item, "driver", None)
        if driver:
            screenshot_dir = os.path.join(os.getcwd(), "reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = item.name
            file_name = f"FAIL_{test_name}_{timestamp}.png"
            file_path = os.path.join(screenshot_dir, file_name)
            
            driver.save_screenshot(file_path)
            print(f"\n[SCREENSHOT] Đã lưu ảnh lỗi tại: {file_path}")
