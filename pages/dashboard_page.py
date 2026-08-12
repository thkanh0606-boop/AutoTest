from selenium.webdriver.common.by import By

class DashboardPage:
    # --- LOCATORS ---
    PAGE_TITLE = (By.XPATH, "//h3[contains(text(),'Bảng điều khiển')]")
    LOGOUT_BUTTON = (By.XPATH, "//button[span[contains(text(),'Đăng xuất')]]")
    STAT_PICKUP_TODAY = (By.XPATH, "//span[contains(text(),'Nhận xe hôm nay')]/following-sibling::div")
    STAT_RETURN_TODAY = (By.XPATH, "//span[contains(text(),'Trả xe hôm nay')]/following-sibling::div")
    STAT_RENTING = (By.XPATH, "//span[contains(text(),'Đang thuê')]/following-sibling::div")
    STAT_OVERDUE = (By.XPATH, "//span[contains(text(),'Quá hạn trả xe')]/following-sibling::div")

    def __init__(self, driver):
        self.driver = driver

    def get_page_title(self):
        return self.driver.find_element(*self.PAGE_TITLE).text

    def logout(self):
        self.driver.find_element(*self.LOGOUT_BUTTON).click()