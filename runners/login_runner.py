import sys
import os
# Tự động thêm thư mục gốc của project vào hệ thống tìm kiếm module của Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from core.driver_factory import DriverFactory
from pages.login_page import LoginPage
from core.helpers.utils import get_logger, capture_screenshot
from core.config import Config

logger = get_logger()

def run_login_test(worker=None, email=Config.TEST_EMAIL, password=Config.TEST_PASSWORD):
    driver = DriverFactory.create_driver(headless=False)
    login_page = LoginPage(driver)
    
    try:
        logger.info("[LOGIN RUNNER] Mở trang đăng nhập...")
        if worker: worker.log_signal.emit("[RUNNER] Mở trang đăng nhập...")
        
        login_page.load()
        if worker: worker.progress_signal.emit(40)
        
        logger.info(f"[LOGIN RUNNER] Nhập thông tin đăng nhập: {email}")
        if worker: worker.log_signal.emit(f"[RUNNER] Thực thi đăng nhập: {email}")
        
        login_page.execute_login(email, password)
        if worker: worker.progress_signal.emit(80)
        
        print("[INFO] Đã bấm Đăng nhập, đang tạm dừng 5 giây để bạn quan sát...")
        time.sleep(10)
        
        logger.info("[LOGIN RUNNER] Đăng nhập hoàn tất thành công.")
        return {"status": "PASSED", "message": "Login executed successfully"}
        
    except Exception as e:
        screenshot_path = capture_screenshot(driver, "login_failed")
        logger.error(f"[LOGIN RUNNER FAIL] {str(e)} | Screenshot: {screenshot_path}")
        return {"status": "FAILED", "error": str(e), "screenshot": screenshot_path}
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_login_test()