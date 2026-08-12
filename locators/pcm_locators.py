from selenium.webdriver.common.by import By

class PCMLocators:
    # --- LOGIN LOCATORS ---
    LOGIN_EMAIL_INPUT = (
        By.XPATH, 
        "//input[@name='username' or @name='email' or @id='username' or @type='text' or @type='email']"
    )
    LOGIN_PASSWORD_INPUT = (
        By.XPATH, 
        "//input[@type='password']"
    )
    LOGIN_SUBMIT_BTN = (
        By.XPATH, 
        "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(), 'Đăng nhập') or contains(text(), 'Log in')]"
    )

    # --- NAVIGATION LOCATORS (Trích xuất chính xác từ HTML thực tế) ---
    # Menu Xe (/cars)
    NAV_VEHICLE = (
        By.XPATH, 
        "//li[contains(@data-menu-id, '/cars') and not(contains(@data-menu-id, '/catalog'))] | //span[text()='Xe']/parent::li"
    )
    
    # Menu Đặt xe (/bookings)
    NAV_BOOKING = (
        By.XPATH, 
        "//li[contains(@data-menu-id, '/bookings')] | //span[text()='Đặt xe']/parent::li"
    )

    # --- TABLE / LIST LOCATORS ---
    # Bảng dữ liệu hoặc danh mục xe/đặt xe
    BOOKING_TABLE_ROWS = (
        By.XPATH, 
        "//table//tbody/tr | //div[contains(@class, 'ant-table-row')] | //li[contains(@class, 'ant-menu-item')]"
    )