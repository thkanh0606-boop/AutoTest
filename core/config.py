import os

class Config:
    BASE_URL = "https://courses.plt.pro.vn/login"
    TEST_EMAIL = "test@gmail.com"
    TEST_PASSWORD = "123123"
    
    # Timeouts (giây)
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    PAGE_LOAD_TIMEOUT = 30
    
    # Đường dẫn thư mục xuất dữ liệu (Evidence)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMAGE_DIR = os.path.join(BASE_DIR, "image")
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    @classmethod
    def init_folders(cls):
        """Tự động tạo thư mục log và image nếu chưa tồn tại"""
        os.makedirs(cls.IMAGE_DIR, exist_ok=True)
        os.makedirs(cls.LOG_DIR, exist_ok=True)

Config.init_folders()