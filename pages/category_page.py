"""Page Object cho Fleet Console - Danh mục xe.

Phần việc của Linh: Hãng xe / Mẫu xe, locator, dropdown và CRUD.
Locator ưu tiên theo text/section ổn định của Ant Design thay vì id sinh động.
"""

try:
    from selenium.webdriver.common.by import By
except ModuleNotFoundError:  # Cho phép chạy unit test import/locator khi chưa cài Selenium.
    class By:
        XPATH = "xpath"
        CSS_SELECTOR = "css selector"
        ID = "id"
        NAME = "name"
        CLASS_NAME = "class name"
        TAG_NAME = "tag name"



class CategoryPage:
    URL = "https://courses.plt.pro.vn/cars/catalog"

    PAGE_TITLE = (By.XPATH, "//h3[normalize-space()='Danh mục xe']")
    STAT_TOTAL_BRANDS = (
        By.XPATH,
        "//span[contains(normalize-space(.),'Tổng số hãng')]/following-sibling::div[1]",
    )
    STAT_ACTIVE_BRANDS = (
        By.XPATH,
        "//span[contains(normalize-space(.),'Hãng đang hoạt động')]/following-sibling::div[1]",
    )
    STAT_TOTAL_MODELS = (
        By.XPATH,
        "//span[contains(normalize-space(.),'Tổng số mẫu xe')]/following-sibling::div[1]",
    )

    BRAND_SECTION = (
        By.XPATH,
        "//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]",
    )
    BRAND_TABLE = (
        By.XPATH,
        "//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]//table",
    )
    ADD_BRAND_BTN = (
        By.XPATH,
        "//button[.//span[normalize-space()='Thêm hãng xe']]",
    )
    BRAND_NAME_INPUT = (
        By.XPATH,
        "(//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "[.//*[contains(normalize-space(.),'Thêm hãng xe')]]//input[not(@type='checkbox')])[1]",
    )
    CREATE_BRAND_BTN = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "//button[.//span[normalize-space()='Tạo hãng xe']]",
    )

    MODEL_SECTION = (
        By.XPATH,
        "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]",
    )
    MODEL_TABLE = (
        By.XPATH,
        "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//table",
    )
    MODEL_FILTER_COMBO = (
        By.XPATH,
        "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//*[@role='combobox'][1]",
    )
    ADD_MODEL_BTN = (
        By.XPATH,
        "//button[.//span[normalize-space()='Thêm mẫu xe']]",
    )
    MODEL_BRAND_COMBO = (
        By.XPATH,
        "(//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "[.//*[contains(normalize-space(.),'Thêm mẫu xe')]]//*[@role='combobox'])[1]",
    )
    MODEL_NAME_INPUT = (
        By.XPATH,
        "(//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "[.//*[contains(normalize-space(.),'Thêm mẫu xe')]]//input[not(@role='combobox')])[1]",
    )
    CREATE_MODEL_BTN = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "//button[.//span[normalize-space()='Tạo mẫu xe']]",
    )

    BRAND_LOCATORS = {
        "Bảng danh sách hãng xe": ("XPATH", BRAND_TABLE[1]),
        "Nút Thêm hãng xe": ("XPATH", ADD_BRAND_BTN[1]),
        "Ô tên hãng xe (modal)": ("XPATH", BRAND_NAME_INPUT[1]),
        "Nút Tạo hãng xe (modal)": ("XPATH", CREATE_BRAND_BTN[1]),
    }

    MODEL_LOCATORS = {
        "Bảng danh sách mẫu xe": ("XPATH", MODEL_TABLE[1]),
        "Nút Thêm mẫu xe": ("XPATH", ADD_MODEL_BTN[1]),
        "Dropdown lọc hãng": ("XPATH", MODEL_FILTER_COMBO[1]),
        "Dropdown chọn hãng (modal)": ("XPATH", MODEL_BRAND_COMBO[1]),
        "Ô tên mẫu xe (modal)": ("XPATH", MODEL_NAME_INPUT[1]),
        "Nút Tạo mẫu xe (modal)": ("XPATH", CREATE_MODEL_BTN[1]),
    }

    def __init__(self, driver):
        self.driver = driver
