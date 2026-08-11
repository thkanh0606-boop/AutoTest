import os
import logging
from datetime import datetime
from core.config import Config

def get_logger(name: str = "EngineLogger") -> logging.Logger:
    """Tạo Logger ghi log song song ra Console và File"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # File Handler
        log_file = os.path.join(Config.LOG_DIR, f"execution_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)
        
    return logger

def capture_screenshot(driver, test_name: str) -> str:
    """Chụp ảnh màn hình khi có lỗi và lưu vào thư mục image/"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{test_name}_{timestamp}.png"
    file_path = os.path.join(Config.IMAGE_DIR, file_name)
    
    try:
        driver.save_screenshot(file_path)
        return file_path
    except Exception as e:
        return f"Lỗi chụp screenshot: {str(e)}"