import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class UserManagementPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 8)

    def highlight(self, element, delay=0.2):
        """Tạo khung viền đỏ nổi bật khi tương tác"""
        try:
            self.driver.execute_script("arguments[0].style.border='3px solid red';", element)
            time.sleep(delay)
        except Exception:
            pass

    # --- LOCATORS BỔ SUNG KHẢ NĂNG NHẬN DIỆN DIỄN RỘNG ---
    BTN_SIGN_OUT = (By.XPATH, "//button[contains(., 'Sign out') or contains(., 'Đăng xuất')] | //*[contains(@class, 'anticon-logout')]")
    
    # Mở rộng Xpath tìm nút Add User theo nhiều cách hiển thị UI khác nhau
    BTN_OPEN_CREATE_MODAL_XPATHS = [
        "//button[contains(., 'Add') or contains(., 'Create') or contains(., 'Thêm') or contains(., 'New')]",
        "//button[contains(@class, 'ant-btn-primary')]",
        "//*[contains(@class, 'anticon-plus')]/ancestor::button",
        "//div[contains(@class, 'header')]//button"
    ]
    
    MODAL_CREATE_USER = (By.XPATH, "//div[contains(@class, 'ant-modal') or contains(@class, 'modal') or contains(@role, 'dialog')]")
    INPUT_EMAIL = (By.XPATH, "//form//input[@id='email' or @name='email' or @type='email' or contains(@placeholder, 'email')]")
    INPUT_PASSWORD = (By.XPATH, "//form//input[@id='password' or @name='password' or @type='password']")
    INPUT_CONFIRM_PASSWORD = (By.XPATH, "//form//input[@id='confirmPassword' or @name='confirmPassword' or contains(@id, 'confirm')]")
    BTN_SUBMIT_FORM = (By.XPATH, "//div[contains(@class, 'modal') or contains(@role, 'dialog')]//button[@type='submit' or contains(., 'OK') or contains(., 'Save') or contains(., 'Lưu')]")
    
    INPUT_SEARCH = (By.XPATH, "//input[contains(@placeholder, 'Search') or contains(@placeholder, 'Tìm kiếm')]")
    STATUS_BADGES = (By.XPATH, "//span[contains(@class, 'badge') or contains(@class, 'ant-tag') or text()='Active' or text()='Hoạt động']")
    TABLE_ROWS = (By.XPATH, "//tbody/tr")

    def is_sign_out_button_visible(self):
        try:
            elements = self.driver.find_elements(*self.BTN_SIGN_OUT)
            if elements:
                self.highlight(elements[0])
                return True
            return False
        except Exception:
            return False

    def open_create_user_form(self):
        """Mở Modal Create User với cơ chế tự động thử nhiều Xpath"""
        if len(self.driver.find_elements(*self.MODAL_CREATE_USER)) > 0:
            return

        button_found = None
        for xpath in self.BTN_OPEN_CREATE_MODAL_XPATHS:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        button_found = el
                        break
                if button_found:
                    break
            except Exception:
                continue

        if button_found:
            self.highlight(button_found)
            button_found.click()
            try:
                modal = self.wait.until(EC.visibility_of_element_located(self.MODAL_CREATE_USER))
                self.highlight(modal)
            except Exception:
                pass
        else:
            raise Exception("Không tìm thấy nút 'Add User / Create' trên giao diện.")

    def fill_user_form(self, email="", password="", confirm_password=""):
        if email:
            field = self.wait.until(EC.element_to_be_clickable(self.INPUT_EMAIL))
            self.highlight(field)
            field.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            field.send_keys(email)
        if password:
            try:
                field = self.driver.find_element(*self.INPUT_PASSWORD)
                self.highlight(field)
                field.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
                field.send_keys(password)
            except Exception:
                pass
        if confirm_password:
            try:
                field = self.driver.find_element(*self.INPUT_CONFIRM_PASSWORD)
                self.highlight(field)
                field.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
                field.send_keys(confirm_password)
            except Exception:
                pass

    def submit_form(self):
        try:
            btn = self.driver.find_element(*self.BTN_SUBMIT_FORM)
            self.highlight(btn)
            btn.click()
        except Exception:
            pass

    def search_user(self, keyword):
        try:
            search_box = self.wait.until(EC.element_to_be_clickable(self.INPUT_SEARCH))
            self.highlight(search_box)
            search_box.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            search_box.send_keys(keyword)
        except Exception:
            pass

    def get_table_row_count(self):
        try:
            rows = self.wait.until(EC.presence_of_all_elements_located(self.TABLE_ROWS))
            if rows:
                self.highlight(rows[0])
            return len(rows)
        except Exception:
            return 0

    def get_active_users_count(self):
        badges = self.driver.find_elements(*self.STATUS_BADGES)
        for badge in badges[:3]:
            self.highlight(badge, delay=0.1)
        return len(badges)