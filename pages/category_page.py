from selenium.webdriver.common.by import By

class CategoryPage:
    # --- LOCATORS ---
    PAGE_TITLE = (By.XPATH, "//h3[contains(text(),'Danh mục xe')]")
    STAT_TOTAL_BRANDS = (By.XPATH, "//span[contains(text(),'Tổng số hãng')]/following-sibling::div")
    STAT_ACTIVE_BRANDS = (By.XPATH, "//span[contains(text(),'Hãng đang hoạt động')]/following-sibling::div")
    STAT_TOTAL_MODELS = (By.XPATH, "//span[contains(text(),'Tổng số mẫu xe')]/following-sibling::div")
    ADD_BRAND_BTN = (By.XPATH, "//button[span[contains(text(),'Thêm hãng xe')]]")
    BRAND_TABLE = (By.XPATH, "//h4[contains(text(),'Danh sách hãng xe')]/ancestor::section//div[contains(@class,'ant-table-wrapper')]")
    BRAND_TABLE_ROWS = (By.XPATH, "//h4[contains(text(),'Danh sách hãng xe')]/ancestor::section//tbody[contains(@class,'ant-table-tbody')]/tr[contains(@class,'ant-table-row')]")
    EDIT_BRAND_BTN = (By.XPATH, "//button[span[contains(text(),'Chỉnh sửa')]]")
    MODEL_SECTION_TITLE = (By.XPATH, "//h4[contains(text(),'Danh sách mẫu xe')]")
    MODEL_BRAND_FILTER_SELECT = (By.ID, "_r_d8_")

    def __init__(self, driver):
        self.driver = driver

    def click_add_brand(self):
        self.driver.find_element(*self.ADD_BRAND_BTN).click()