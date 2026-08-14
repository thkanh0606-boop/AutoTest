from selenium.webdriver.common.by import By

class FleetPage:
    # --- LOCATORS ---
    PAGE_TITLE = (By.XPATH, "//h3[contains(text(),'Trung tâm điều phối đội xe')]")
    ADD_VEHICLE_BTN = (By.XPATH, "//button[span[contains(text(),'Thêm xe mới')]]")
    STAT_TOTAL_VEHICLES = (By.XPATH, "//span[contains(text(),'Tổng số xe')]/following-sibling::div")
    STAT_READY_TODAY = (By.XPATH, "//span[contains(text(),'Sẵn sàng hôm nay')]/following-sibling::div")
    STAT_MAINTENANCE = (By.XPATH, "//span[contains(text(),'Đang bảo dưỡng')]/following-sibling::div")
    FLEET_TABLE = (By.XPATH, "//div[contains(@class,'ant-table-wrapper')]")
    FLEET_TABLE_ROWS = (By.XPATH, "//tbody[contains(@class,'ant-table-tbody')]/tr[contains(@class,'ant-table-row')]")
    FILTER_STATUS_BTN = (By.XPATH, "//th[contains(.,'Trạng thái')]//span[contains(@class,'ant-table-filter-trigger')]")
    EDIT_VEHICLE_BTN = (By.XPATH, "//button[@aria-label='Chỉnh sửa']")
    DELETE_VEHICLE_BTN = (By.XPATH, "//button[@aria-label='Xóa']")

    def __init__(self, driver):
        self.driver = driver

    def click_add_vehicle(self):
        self.driver.find_element(*self.ADD_VEHICLE_BTN).click()

    def get_vehicle_count(self):
        return len(self.driver.find_elements(*self.FLEET_TABLE_ROWS))