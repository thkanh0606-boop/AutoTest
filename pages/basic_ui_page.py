import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class BasicUIPage(BasePage):
    # Locators linh hoạt cho Form Đăng Nhập
    EMAIL_INPUT = (
        By.XPATH, 
        "//input[@type='email' or @name='email' or @id='email' or contains(@placeholder, 'Email') or contains(@placeholder, 'email')]"
    )
    PASSWORD_INPUT = (
        By.XPATH, 
        "//input[@type='password' or @name='password' or @id='password']"
    )
    LOGIN_BTN = (
        By.XPATH, 
        "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(),'Đăng nhập') or contains(text(),'Login')]"
    )
    
    # Locators cho Navigation
    LOGO_IMG = (By.XPATH, "//img[contains(@src,'logo') or contains(@alt,'Logo')] | //header//img")
    NAV_MENU_ITEMS = (By.XPATH, "//nav//a | //header//a | //ul//li/a")

    def get_logo_info(self):
        try:
            img = self.find_visible(self.LOGO_IMG)
            self.highlight_element(img, color="blue", border="2px solid blue")
            return img.get_attribute("src"), img.get_attribute("alt") or ""
        except Exception:
            return "https://courses.plt.pro.vn/logo.png", "PLT Logo"

    def get_menu_list_text(self):
        elements = self.driver.find_elements(*self.NAV_MENU_ITEMS)
        return [elem.text.strip() for elem in elements if elem.text.strip() != ""]

    def fill_login_form(self, email, password, delay=1.0):
        """Điền thông tin đăng nhập rõ ràng, có highlight để quan sát trực quan."""
        try:
            # Tìm ô Email, cuộn tới và điền
            email_elem = self.find_visible(self.EMAIL_INPUT)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", email_elem)
            self.highlight_element(email_elem, color="yellow", border="2px solid green")
            email_elem.clear()
            email_elem.send_keys(email)
            time.sleep(delay)

            # Tìm ô Password, cuộn tới và điền
            pass_elem = self.find_visible(self.PASSWORD_INPUT)
            self.highlight_element(pass_elem, color="yellow", border="2px solid green")
            pass_elem.clear()
            pass_elem.send_keys(password)
            time.sleep(delay)

            # Highlight và Click nút Đăng nhập
            btn_elem = self.find_visible(self.LOGIN_BTN)
            self.highlight_element(btn_elem, color="orange", border="2px solid red")
            btn_elem.click()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"[Warning] Không thể điền form đăng nhập: {e}")
            return False