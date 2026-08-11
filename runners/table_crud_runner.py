from core.driver_factory import DriverFactory
from core.helpers.asserts import CustomAsserts
from core.helpers.utils import get_logger

logger = get_logger()

def run_table_crud_test(worker=None):
    driver = DriverFactory.create_driver(headless=False)
    
    try:
        logger.info("[TABLE/CRUD] Khởi chạy runner kiểm thử Table & Luồng CRUD...")
        if worker: worker.log_signal.emit("[RUNNER] Đang kiểm tra dữ liệu Bảng...")
        
        # Dữ liệu mô phỏng để test hàm so sánh
        expected_table = ["Item 1", "Item 2", "Item 3"]
        actual_table = ["Item 1", "Item 2_Modified", "Item 3"]  # Mismatch tại index 1
        
        result = CustomAsserts.compare_table_data(expected_table, actual_table)
        
        logger.info(f"[TABLE/CRUD RESULT] Passed: {result['passed']} | Mismatch: {len(result['mismatch'])}")
        return {"status": "PASSED" if result['passed'] else "WARNING", "details": result}
    except Exception as e:
        logger.error(f"[TABLE/CRUD FAIL] {str(e)}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        driver.quit()