import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class StaffPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 8)

    def highlight(self, element, delay=0.2):
        try:
            self.driver.execute_script("arguments[0].style.border='3px solid red';", element)
            time.sleep(delay)
        except Exception:
            pass

    # --- LOCATORS ---
    PAGE_IDENTITY = (By.XPATH, "//table | //ul[contains(@class, 'ant-pagination')]")
    BTN_GO_TO_CREATE = (By.XPATH, "//a[contains(@href, '/users/new') or contains(@href, '/users/create')]//button | //button[span[contains(text(),'Thêm')]]")
    TABLE_ROWS = (By.XPATH, "//tbody/tr")
    DELETE_BUTTONS = (By.XPATH, "//button[@aria-label='Xóa'] | //table//button[contains(@class, 'ant-btn-text')]")
    PAGINATION_ITEMS = (By.XPATH, "//ul[contains(@class, 'ant-pagination')]//li[contains(@class, 'ant-pagination-item')]")
    
    # Form Thêm mới
    BTN_BACK = (By.XPATH, "//button[@aria-label='Quay lại']")
    INPUT_EMAIL = (By.XPATH, "//input[@id='email']")
    INPUT_PASSWORD = (By.XPATH, "//input[@id='password']")
    INPUT_CONFIRM_PASSWORD = (By.XPATH, "//input[@id='passwordConfirm']")
    SELECT_ROLE = (By.XPATH, "//input[@id='role']/ancestor::div[contains(@class, 'ant-select')]")
    SWITCH_IS_ACTIVE = (By.XPATH, "//button[@id='isActive']")
    BTN_CANCEL = (By.XPATH, "//button[span[text()='Hủy']]")
    BTN_SUBMIT = (By.XPATH, "//button[@type='submit' and span[contains(text(),'Thêm')]]")
    ERROR_MESSAGES = (By.XPATH, "//div[contains(@class,'ant-form-item-explain-error')]")

    # --- ACTION METHODS ---
    def is_page_loaded(self):
        try:
            self.wait.until(lambda d: "/users" in d.current_url and "/new" not in d.current_url and "/create" not in d.current_url)
            el = self.wait.until(EC.presence_of_element_located(self.PAGE_IDENTITY))
            self.highlight(el)
            return True
        except Exception:
            return False

    def click_add_staff_button(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_GO_TO_CREATE))
        self.highlight(btn)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def get_table_row_count(self):
        try:
            rows = self.wait.until(EC.presence_of_all_elements_located(self.TABLE_ROWS))
            if rows:
                self.highlight(rows[0])
            return len(rows)
        except Exception:
            return 0

    def get_pagination_count(self):
        try:
            items = self.driver.find_elements(*self.PAGINATION_ITEMS)
            if items:
                self.highlight(items[0])
            return len(items)
        except Exception:
            return 0

    def fill_create_form(self, email="", password="", confirm_password=""):
        if email != "":
            el_email = self.wait.until(EC.element_to_be_clickable(self.INPUT_EMAIL))
            self.highlight(el_email)
            el_email.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            el_email.send_keys(email)
            
        if password != "":
            el_pass = self.driver.find_element(*self.INPUT_PASSWORD)
            self.highlight(el_pass)
            el_pass.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            el_pass.send_keys(password)
            
        if confirm_password != "":
            el_confirm = self.driver.find_element(*self.INPUT_CONFIRM_PASSWORD)
            self.highlight(el_confirm)
            el_confirm.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            el_confirm.send_keys(confirm_password)

    def toggle_is_active_switch(self):
        switch_el = self.wait.until(EC.element_to_be_clickable(self.SWITCH_IS_ACTIVE))
        self.highlight(switch_el)
        switch_el.click()

    def submit_create_form(self):
        btn = self.driver.find_element(*self.BTN_SUBMIT)
        self.highlight(btn)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def click_back_button(self):
        """Xử lý click nút Quay lại an toàn bằng cả click thường lẫn JS click"""
        btn = self.wait.until(EC.presence_of_element_located(self.BTN_BACK))
        self.highlight(btn)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        try:
            btn.click()
        except Exception:
            # Fallback nếu bị che bởi ant-card-body
            self.driver.execute_script("arguments[0].click();", btn)

    def has_form_error_messages(self):
        try:
            errors = self.driver.find_elements(*self.ERROR_MESSAGES)
            return len(errors) > 0
        except Exception:
            return False