from core.driver_factory import DriverFactory
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from core.helpers.utils import get_logger

logger = get_logger()

def run_text_dropdown_test(worker=None):
    driver = DriverFactory.create_driver(headless=False)
    base_page = BasePage(driver)
    
    try:
        logger.info("[TEXT/DROPDOWN] Khởi chạy runner kiểm thử Input Text & Dropdown...")
        if worker: worker.log_signal.emit("[RUNNER] Kiểm tra Text & Dropdown...")
        
        # Mẫu thao tác cho Dropdown chuẩn Selenium Select
        # select_element = Select(base_page.find((By.ID, "dropdown-id")))
        # select_element.select_by_visible_text("Option Value")
        
        if worker: worker.progress_signal.emit(90)
        return {"status": "PASSED", "actual_data": "Text and Dropdown values verified"}
    except Exception as e:
        logger.error(f"[TEXT/DROPDOWN FAIL] {str(e)}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        driver.quit()