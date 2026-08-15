from selenium.webdriver.common.by import By

class CarManagementLocators:
    # 1. Search & Filter
    SEARCH_INPUT = (By.XPATH, "//input[@placeholder='Tìm kiếm biển số...']")
    SEARCH_BUTTON = (By.XPATH, "//button[@id='btn-search']")
    
    # 2. CRUD Buttons
    ADD_CAR_BTN = (By.XPATH, "//button[contains(text(), 'Thêm xe')]")
    SAVE_BTN = (By.XPATH, "//button[@type='submit' and contains(text(), 'Lưu')]")
    CANCEL_BTN = (By.XPATH, "//button[contains(text(), 'Hủy')]")
    
    # 3. Form Inputs (Dropdown Hãng-Mẫu)
    BRAND_DROPDOWN = (By.XPATH, "//select[@name='brand_id']")
    MODEL_DROPDOWN = (By.XPATH, "//select[@name='model_id']") # Phụ thuộc vào Brand
    LICENSE_PLATE_INPUT = (By.XPATH, "//input[@name='license_plate']")
    COLOR_INPUT = (By.XPATH, "//input[@name='color']")
    PRICE_INPUT = (By.XPATH, "//input[@name='price_per_day']")
    STATUS_DROPDOWN = (By.XPATH, "//select[@name='car_status']")
    
    # 4. Table & Actions
    CAR_TABLE = (By.XPATH, "//table[@id='car-table']")
    FIRST_ROW_EDIT_BTN = (By.XPATH, "//table[@id='car-table']/tbody/tr[1]//button[contains(@class, 'btn-edit')]")
    FIRST_ROW_DELETE_BTN = (By.XPATH, "//table[@id='car-table']/tbody/tr[1]//button[contains(@class, 'btn-delete')]")
    CONFIRM_DELETE_BTN = (By.XPATH, "//div[@class='modal']//button[contains(text(), 'Đồng ý')]")
    
    # 5. Validation Messages
    MSG_SUCCESS = (By.XPATH, "//div[contains(@class, 'toast-success')]")
    ERR_DUPLICATE_PLATE = (By.XPATH, "//span[contains(text(), 'Biển số đã tồn tại')]")
    ERR_DELETE_RENTED = (By.XPATH, "//span[contains(text(), 'Không thể xóa xe đang trong trạng thái thuê')]")