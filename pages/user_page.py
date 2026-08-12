from selenium.webdriver.common.by import By

class UserManagementPage:
    # --- LOCATORS ---
    PAGE_TITLE = (By.XPATH, "//h3[contains(text(),'Quản lý quyền truy cập')]")
    CREATE_USER_BTN = (By.XPATH, "//a[@href='/users/new']//button[span[contains(text(),'Tạo người dùng')]]")
    USER_TABLE = (By.XPATH, "//section[div/h4[contains(text(),'Danh bạ nhân sự')]]//div[contains(@class,'ant-table-wrapper')]")
    USER_TABLE_ROWS = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]/tr[contains(@class,'ant-table-row')]")
    USER_EMAIL_TEXT = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]//td[1]//strong")
    USER_UID_TEXT = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]//td[1]//div[contains(text(),'UID:')]")
    USER_ROLE_TAG = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]//td[2]//span[contains(@class,'ant-tag')]")
    USER_STATUS_BADGE = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]//td[3]//span[contains(@class,'ant-badge-status-text')]")
    PAGINATION_PREV_BTN = (By.XPATH, "//li[contains(@class,'ant-pagination-prev')]")
    PAGINATION_NEXT_BTN = (By.XPATH, "//li[contains(@class,'ant-pagination-next')]")
    PAGINATION_ITEM = (By.XPATH, "//li[contains(@class,'ant-pagination-item')]")

    def __init__(self, driver):
        self.driver = driver

    def click_create_user(self):
        self.driver.find_element(*self.CREATE_USER_BTN).click()