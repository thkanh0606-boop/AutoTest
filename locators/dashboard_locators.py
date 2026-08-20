from selenium.webdriver.common.by import By


class DashboardLocators:
    MAIN = (By.CSS_SELECTOR, "main")
    HEADER_TITLE = (By.XPATH, "//header//h3[normalize-space()='Bảng điều khiển vận hành']")
    HERO_TITLE = (By.XPATH, "//main//h1[normalize-space()='Dashboard']")
    HERO_SECTION = (By.XPATH, "//main//h1[normalize-space()='Dashboard']/ancestor::section")
    SYNC_BADGE = (By.XPATH, "//main//*[contains(normalize-space(), 'Đồng bộ Firestore')]")

    KPI_GRID_FIRST_ROW = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]")
    KPI_GRID_SECOND_ROW = (By.XPATH, "(//main//div[contains(@class, 'grid')])[2]")
    KPI_RENTED_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]/*[1]")
    KPI_READY_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]/*[2]")
    KPI_PICKUP_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]/*[3]")
    KPI_RETURN_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[1]/*[4]")
    KPI_OVERDUE_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[2]/*[1]")
    KPI_MAINTENANCE_CARD = (By.XPATH, "(//main//div[contains(@class, 'grid')])[2]/*[2]")

    QUICK_ACTIONS_SECTION = (By.XPATH, "//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section")
    QUICK_CREATE_BOOKING = (
        By.XPATH,
        "//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Tạo booking']]",
    )
    QUICK_BOOKING_LIST = (
        By.XPATH,
        "//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Xem danh sách booking']]",
    )
    QUICK_FLEET = (
        By.XPATH,
        "//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Kiểm tra đội xe']]",
    )
    QUICK_FINANCE = (
        By.XPATH,
        "//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Mở tài chính']]",
    )

    SIDEBAR_MENU = (By.CSS_SELECTOR, "ul[role='menu']")
    NAV_DASHBOARD = (By.CSS_SELECTOR, "li[data-menu-id$='/dashboard']")
    NAV_BOOKINGS = (By.CSS_SELECTOR, "li[data-menu-id$='/bookings']")
    NAV_CARS = (By.CSS_SELECTOR, "li[data-menu-id$='/cars']")
    NAV_FINANCE = (By.CSS_SELECTOR, "li[data-menu-id$='/finance']")

    BOOKING_LIST_SECTION = (By.XPATH, "//main//h4[normalize-space()='Các lượt bàn giao sắp tới']/ancestor::section")
    BUSINESS_SNAPSHOT_SECTION = (By.XPATH, "//main//h4[normalize-space()='Ảnh chụp nhanh kinh doanh']/ancestor::section")
    WORKFLOW_HEALTH_SECTION = (By.XPATH, "//main//h4[normalize-space()='Sức khỏe quy trình booking']/ancestor::section")
