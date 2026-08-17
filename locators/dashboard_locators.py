from selenium.webdriver.common.by import By


class DashboardLocators:
    MAIN = (By.CSS_SELECTOR, "main")
    HEADER_TITLE = (By.XPATH, "//header//h3[normalize-space()='Tổng quan']")
    HERO_TITLE = HEADER_TITLE
    HERO_SECTION = (By.XPATH, "//header[.//h3[normalize-space()='Tổng quan']]")
    SYNC_BADGE = (By.XPATH, "//header//*[contains(normalize-space(), 'Hôm nay')]")

    KPI_GRID_FIRST_ROW = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]")
    KPI_GRID_SECOND_ROW = (By.XPATH, "(//main//div[contains(@class, 'grid')])[2]")
    KPI_PICKUP_CARD = (By.XPATH, "//main//button[.//span[normalize-space()='Nhận xe hôm nay']]")
    KPI_RETURN_CARD = (By.XPATH, "//main//button[.//span[normalize-space()='Trả xe hôm nay']]")
    KPI_OVERDUE_CARD = (By.XPATH, "//main//button[.//span[normalize-space()='Quá hạn trả']]")
    KPI_READY_CARD = (By.XPATH, "//main//button[.//span[normalize-space()='Xe sẵn sàng']]")
    KPI_DRAFT_CARD = (By.XPATH, "//main//*[normalize-space()='Nháp']/ancestor::div[contains(@class, 'rounded')][1]")
    KPI_CONFIRMED_CARD = (By.XPATH, "//main//*[normalize-space()='Đã xác nhận']/ancestor::div[contains(@class, 'rounded')][1]")
    KPI_RENTED_CARD = (By.XPATH, "//main//*[normalize-space()='Đang thuê']/ancestor::div[contains(@class, 'rounded')][1]")
    KPI_COMPLETED_CARD = (By.XPATH, "//main//*[normalize-space()='Hoàn tất']/ancestor::div[contains(@class, 'rounded')][1]")
    KPI_MAINTENANCE_CARD = (By.XPATH, "//main//*[normalize-space()='Sửa chữa']/ancestor::section[1]")

    QUICK_ACTIONS_SECTION = (By.XPATH, "//main//button[normalize-space()='Tạo đơn thuê']")
    QUICK_CREATE_BOOKING = (
        By.XPATH,
        "//main//button[normalize-space()='Tạo đơn thuê']",
    )
    QUICK_BOOKING_LIST = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Đơn thuê']",
    )
    QUICK_CUSTOMERS = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Khách hàng']",
    )
    QUICK_FLEET = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Xe']",
    )
    QUICK_CATALOG = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Danh mục xe']",
    )
    QUICK_FINANCE = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Tài chính']",
    )
    QUICK_USERS = (
        By.XPATH,
        "//aside//li[@role='menuitem' and normalize-space()='Nhân sự']",
    )

    SIDEBAR_MENU = (By.CSS_SELECTOR, "ul[role='menu']")
    NAV_DASHBOARD = (By.XPATH, "//aside//li[@role='menuitem' and normalize-space()='Tổng quan']")
    NAV_BOOKINGS = QUICK_BOOKING_LIST
    NAV_CUSTOMERS = QUICK_CUSTOMERS
    NAV_CARS = QUICK_FLEET
    NAV_CATALOG = QUICK_CATALOG
    NAV_FINANCE = QUICK_FINANCE
    NAV_USERS = QUICK_USERS

    BOOKING_LIST_SECTION = (By.XPATH, "//main//section[.//h4[normalize-space()='Lượt giao nhận sắp tới']]")
    BUSINESS_SNAPSHOT_SECTION = (By.XPATH, "//main//section[.//h4[normalize-space()='Tiền']]")
    WORKFLOW_HEALTH_SECTION = (By.XPATH, "//main//section[.//h4[normalize-space()='Đội xe']]")
