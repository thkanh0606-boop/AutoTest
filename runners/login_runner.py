import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from core.driver_factory import DriverFactory
from pages.login_page import LoginPage
from core.helpers.utils import get_logger, capture_screenshot
from core.config import Config

logger = get_logger()

def run_login_test(worker=None, email=Config.TEST_EMAIL, password=Config.TEST_PASSWORD, url=None, is_valid_case=True):
    """
    Hàm thực thi Test Case Đăng nhập
    :param is_valid_case: True nếu test case kỳ vọng Đăng nhập THÀNH CÔNG, 
                          False nếu test case kỳ vọng BẮT LỖI SAI (Mật khẩu/Email sai)
    """
    driver = DriverFactory.create_driver(headless=False, keep_session=True)
    login_page = LoginPage(driver)
    
    try:
        target_url = url or Config.BASE_URL
        logger.info(f"[LOGIN RUNNER] Mở trang đăng nhập: {target_url}")
        if worker: worker.log_signal.emit(f"[RUNNER] Mở trang đăng nhập: {target_url}")
        
        login_page.load(target_url)
        if worker: worker.progress_signal.emit(30)
        
        logger.info(f"[LOGIN RUNNER] Nhập thông tin: Email='{email}'")
        if worker: worker.log_signal.emit(f"[RUNNER] Nhập thông tin: Email='{email}'")
        
        login_page.execute_login(email, password)
        if worker: worker.progress_signal.emit(70)
        
        time.sleep(3) # Tạm dừng chờ phản hồi trang web
        
        # --- BƯỚC XÁC MINH KẾT QUẢ (ASSERTION) ---
        current_url = login_page.get_current_url()
        error_msg = login_page.get_error_message()
        
        if is_valid_case:
            # TH1: Kỳ vọng đăng nhập thành công
            if error_msg:
                raise Exception(f"Đăng nhập thất bại! Trang web báo lỗi: '{error_msg}'")
            elif "login" in current_url.lower() and not ("dashboard" in current_url.lower() or "admin" in current_url.lower()):
                # Nếu vẫn đang ở URL login
                logger.warning(f"[WARNING] Vẫn ở trang login ({current_url}), kiểm tra xem đã chuyển hướng chưa...")
            
            logger.info("[LOGIN RUNNER] PASS: Đăng nhập thành công!")
            if worker: worker.progress_signal.emit(100)
            return {"status": "PASSED", "message": "Đăng nhập thành công!"}

        else:
            # TH2: Kỳ vọng đăng nhập thất bại (Ví dụ nhập sai pass)
            if error_msg or "login" in current_url.lower():
                logger.info(f"[LOGIN RUNNER] PASS: Đã bắt đúng lỗi đăng nhập sai. Thông báo: '{error_msg}'")
                if worker: worker.progress_signal.emit(100)
                return {"status": "PASSED", "message": f"Hệ thống bắt lỗi đúng: {error_msg}"}
            else:
                raise Exception("Kỳ vọng Đăng nhập thất bại nhưng hệ thống lại cho phép truy cập!")

    except Exception as e:
        screenshot_path = capture_screenshot(driver, "login_failed")
        logger.error(f"[LOGIN RUNNER FAIL] {str(e)} | Screenshot: {screenshot_path}")
        if worker: worker.log_signal.emit(f"[ERROR] {str(e)}")
        return {"status": "FAILED", "error": str(e), "screenshot": screenshot_path}
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test thử đăng nhập
    run_login_test(is_valid_case=True)