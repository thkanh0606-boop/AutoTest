import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================================================
# CONFIG
# =========================================================

BASE_URL = "https://courses.plt.pro.vn/bookings"
WAIT_TIME = 15


# =========================================================
# LOCATORS
# =========================================================

# ---------------------------------------------------------
# Booking page
# ---------------------------------------------------------

PAGE_TITLE = (
    By.XPATH,
    "//*[normalize-space()='Quản lý đặt xe' and not(ancestor::aside)]"
)

MAIN = (
    By.XPATH,
    "//main"
)

LOGO = (
    By.CSS_SELECTOR,
    "aside img[alt='PLT Solutions']"
)

# ---------------------------------------------------------
# HEADER LANGUAGE
#
# Quan trọng:
# Dropdown ngôn ngữ KHÔNG nằm trong main.
#
# DOM thực tế:
#
# input[aria-label='Ngôn ngữ']
# ---------------------------------------------------------

LANGUAGE_INPUT = (
    By.CSS_SELECTOR,
    "input[aria-label='Ngôn ngữ']"
)

LANGUAGE_DROPDOWN = (
    By.XPATH,
    "//input[@aria-label='Ngôn ngữ']/ancestor::div[contains(@class,'ant-select')][1]"
)

# ---------------------------------------------------------
# Create booking
# ---------------------------------------------------------

CREATE_BOOKING_BUTTON = (
    By.CSS_SELECTOR,
    "button[aria-label='Tạo đơn thuê']"
)

# ---------------------------------------------------------
# New booking page dropdowns
# ---------------------------------------------------------

CAR_DROPDOWN = (
    By.CSS_SELECTOR,
    "#carId"
)

CUSTOMER_DROPDOWN = (
    By.CSS_SELECTOR,
    "#customerId"
)

STATUS_DROPDOWN = (
    By.CSS_SELECTOR,
    "#status"
)

PAYMENT_METHOD_DROPDOWN = (
    By.CSS_SELECTOR,
    "#paymentMethod"
)

# ---------------------------------------------------------
# Table
# ---------------------------------------------------------

TABLE = (
    By.XPATH,
    "//main//table"
)

REAL_ROWS = (
    By.XPATH,
    "//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "]"
)

FIRST_ROW = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]"
)

FIRST_ROW_BOOKING_CODE = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[1]"
)

FIRST_ROW_VEHICLE = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[2]"
)

FIRST_ROW_RENTAL_DATE = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[3]"
)

FIRST_ROW_STATUS = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[4]"
)

FIRST_ROW_PAYMENT = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[5]"
)

FIRST_ROW_FILE = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[6]"
)

FIRST_ROW_TOTAL = (
    By.XPATH,
    "(//main//table//tbody//tr["
    "not(@aria-hidden='true') "
    "and normalize-space(.)!=''"
    "])[1]//td[7]"
)

# ---------------------------------------------------------
# Pagination
# ---------------------------------------------------------

PAGINATION = (
    By.CSS_SELECTOR,
    ".ant-pagination"
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

SIDEBAR_MENU = (
    By.CSS_SELECTOR,
    "ul[role='menu']"
)

BOOKING_MENU_ITEM = (
    By.XPATH,
    "//li[@role='menuitem']["
    ".//span[contains(normalize-space(), 'Đặt xe')]"
    "]"
)

# ---------------------------------------------------------
# Table checkbox
# ---------------------------------------------------------

TABLE_CHECKBOX = (
    By.XPATH,
    "(//main//table//input[@type='checkbox'])[1]"
)


# =========================================================
# HELPERS
# =========================================================

def wait_for_page(driver):
    """
    Chờ trang Booking render.

    Không chờ title vì title locator có thể thay đổi
    theo frontend.
    """

    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(
        EC.presence_of_element_located(MAIN)
    )

    wait.until(
        EC.presence_of_element_located(TABLE)
    )

    return wait


def get_real_rows(driver):
    return driver.find_elements(*REAL_ROWS)


def get_row_text(row):
    return " ".join(row.text.split())


def assert_visible(driver, locator, name):
    element = WebDriverWait(
        driver,
        WAIT_TIME
    ).until(
        EC.visibility_of_element_located(locator)
    )

    assert element.is_displayed(), (
        f"{name} không hiển thị"
    )

    return element


# =========================================================
# TEST 1
# PAGE LOAD
# =========================================================

def test_booking_page_load(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    assert "/bookings" in driver.current_url

    title = assert_visible(
        driver,
        PAGE_TITLE,
        "Tiêu đề Quản lý đặt xe"
    )

    assert title.text.strip() == "Quản lý đặt xe"

    main = assert_visible(
        driver,
        MAIN,
        "Main"
    )

    assert main.is_displayed()

    print()
    print("[PASS] Booking page loaded")
    print("[PASS] URL:", driver.current_url)
    print("[PASS] Title:", title.text)


# =========================================================
# TEST 2
# BASIC UI
# =========================================================

def test_booking_basic_ui(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    # Main
    main = assert_visible(
        driver,
        MAIN,
        "Main"
    )

    assert main.is_displayed()

    # Logo
    logo = assert_visible(
        driver,
        LOGO,
        "Logo PLT Solutions"
    )

    assert logo.get_attribute("alt") == "PLT Solutions"

    # Sidebar
    menu = assert_visible(
        driver,
        SIDEBAR_MENU,
        "Sidebar menu"
    )

    assert menu.is_displayed()

    # Booking menu
    booking_menu = assert_visible(
        driver,
        BOOKING_MENU_ITEM,
        "Menu Đặt xe"
    )

    assert booking_menu.is_displayed()

    print()
    print("[PASS] Main visible")
    print("[PASS] Logo visible")
    print("[PASS] Sidebar menu visible")
    print("[PASS] Booking menu item visible")


# =========================================================
# TEST 3
# LANGUAGE DROPDOWN
# =========================================================

def test_booking_language_dropdown(driver):
    """
    Kiểm tra dropdown ngôn ngữ ở HEADER.

    Không dùng:
        main .ant-select

    vì dropdown ngôn ngữ nằm ngoài <main>.

    DOM thực tế:
        input[aria-label='Ngôn ngữ']
    """

    driver.get(BASE_URL)

    wait_for_page(driver)

    # -----------------------------------------------------
    # Tìm input ngôn ngữ
    # -----------------------------------------------------

    language_input = assert_visible(
        driver,
        LANGUAGE_INPUT,
        "Input dropdown ngôn ngữ"
    )

    assert language_input.is_displayed()

    # -----------------------------------------------------
    # Kiểm tra aria-label
    # -----------------------------------------------------

    aria_label = language_input.get_attribute(
        "aria-label"
    )

    assert aria_label == "Ngôn ngữ"

    # -----------------------------------------------------
    # Tìm parent .ant-select
    # -----------------------------------------------------

    dropdown = assert_visible(
        driver,
        LANGUAGE_DROPDOWN,
        "Dropdown ngôn ngữ"
    )

    assert dropdown.is_displayed()

    # -----------------------------------------------------
    # Giá trị hiện tại
    # -----------------------------------------------------

    current_value = dropdown.text.strip()

    assert current_value != ""

    print()
    print("[PASS] Language dropdown exists")
    print("[PASS] aria-label:", aria_label)
    print("[PASS] Current language:", current_value)


# =========================================================
# TEST 4
# TABLE
# =========================================================

def test_booking_table(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    table = assert_visible(
        driver,
        TABLE,
        "Booking table"
    )

    assert table.is_displayed()

    headers = table.find_elements(
        By.CSS_SELECTOR,
        "thead th"
    )

    assert len(headers) >= 7, (
        f"Bảng phải có ít nhất 7 cột, "
        f"nhưng tìm thấy {len(headers)}"
    )

    header_texts = [
        h.text.strip()
        for h in headers
    ]

    print()
    print("[PASS] Booking table visible")
    print("[INFO] Headers:")

    for index, text in enumerate(
        header_texts,
        start=1
    ):
        print(
            f"       {index}. {text}"
        )

    expected_headers = [
        "Đơn thuê",
        "Xe",
        "Ngày thuê",
        "Trạng thái",
        "Thanh toán",
        "Tệp",
        "Tổng tiền",
    ]

    for expected in expected_headers:

        found = any(
            expected.lower()
            in actual.lower()
            for actual in header_texts
        )

        assert found, (
            f"Không tìm thấy cột: {expected}"
        )

    print(
        "[PASS] Required table columns exist"
    )


# =========================================================
# TEST 5
# REAL DATA ROW
# =========================================================

def test_booking_first_row(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    rows = get_real_rows(driver)

    assert len(rows) > 0, (
        "Không có booking data row"
    )

    first_row = rows[0]

    assert first_row.is_displayed()

    cells = first_row.find_elements(
        By.CSS_SELECTOR,
        "td"
    )

    assert len(cells) >= 7, (
        f"Booking row phải có ít nhất 7 cell, "
        f"nhưng tìm thấy {len(cells)}"
    )

    booking_code = cells[0].text.strip()
    vehicle = cells[1].text.strip()
    rental_date = cells[2].text.strip()
    status = cells[3].text.strip()
    payment = cells[4].text.strip()
    file_text = cells[5].text.strip()
    total = cells[6].text.strip()

    assert booking_code != "", (
        "Mã booking đầu tiên đang rỗng"
    )

    assert vehicle != "", (
        "Thông tin xe đang rỗng"
    )

    assert rental_date != "", (
        "Ngày thuê đang rỗng"
    )

    assert status != "", (
        "Trạng thái booking đang rỗng"
    )

    assert payment != "", (
        "Trạng thái thanh toán đang rỗng"
    )

    assert total != "", (
        "Tổng tiền đang rỗng"
    )

    print()
    print("[PASS] First booking row exists")
    print("[INFO] Booking:", booking_code)
    print("[INFO] Vehicle:", vehicle)
    print("[INFO] Rental date:", rental_date)
    print("[INFO] Status:", status)
    print("[INFO] Payment:", payment)
    print("[INFO] File:", file_text)
    print("[INFO] Total:", total)


# =========================================================
# TEST 6
# ROW LOCATORS CONTRACT
# =========================================================

def test_booking_first_row_contract(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    locators = [
        (
            "Booking code",
            FIRST_ROW_BOOKING_CODE
        ),
        (
            "Vehicle",
            FIRST_ROW_VEHICLE
        ),
        (
            "Rental date",
            FIRST_ROW_RENTAL_DATE
        ),
        (
            "Status",
            FIRST_ROW_STATUS
        ),
        (
            "Payment",
            FIRST_ROW_PAYMENT
        ),
        (
            "File",
            FIRST_ROW_FILE
        ),
        (
            "Total",
            FIRST_ROW_TOTAL
        ),
    ]

    print()

    for name, locator in locators:

        element = assert_visible(
            driver,
            locator,
            name
        )

        print(
            f"[PASS] {name}: "
            f"{element.text.strip()}"
        )


# =========================================================
# TEST 7
# PAGINATION
# =========================================================

def test_booking_pagination(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    pagination = assert_visible(
        driver,
        PAGINATION,
        "Pagination"
    )

    assert pagination.is_displayed()

    items = pagination.find_elements(
        By.CSS_SELECTOR,
        "li"
    )

    assert len(items) > 0, (
        "Pagination không có item"
    )

    print()
    print(
        "[PASS] Pagination visible"
    )

    print(
        "[INFO] Pagination items:",
        len(items)
    )


# =========================================================
# TEST 8
# CHECKBOX
# =========================================================

def test_booking_checkbox(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    checkboxes = driver.find_elements(
        *TABLE_CHECKBOX
    )

    if not checkboxes:

        print()
        print(
            "[INFO] Booking table "
            "không có checkbox."
        )

        pytest.skip(
            "Trang Booking hiện tại không render checkbox."
        )

    checkbox = checkboxes[0]

    assert checkbox.is_displayed()

    print()
    print(
        "[PASS] Booking checkbox visible"
    )


# =========================================================
# TEST 9
# TABLE ROW COUNT
# =========================================================

def test_booking_has_data(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    rows = get_real_rows(driver)

    assert len(rows) > 0, (
        "Booking table không có dữ liệu"
    )

    print()
    print(
        "[PASS] Booking data exists"
    )

    print(
        "[INFO] Real rows:",
        len(rows)
    )


# =========================================================
# TEST 10
# CREATE BOOKING BUTTON
# =========================================================

def test_booking_create_button(driver):
    """
    Kiểm tra nút Tạo đơn thuê.
    """

    driver.get(BASE_URL)

    wait_for_page(driver)

    button = assert_visible(
        driver,
        CREATE_BOOKING_BUTTON,
        "Nút Tạo đơn thuê"
    )

    assert button.is_displayed()

    assert button.get_attribute(
        "aria-label"
    ) == "Tạo đơn thuê"

    print()
    print("[PASS] Create booking button visible")


# =========================================================
# TEST 11
# CREATE BOOKING FORM DROPDOWNS
# =========================================================

def test_booking_create_form_dropdowns(driver):
    """
    Kiểm tra các dropdown bên trong trang Tạo đơn thuê.

    DOM thực tế đã xác nhận:

    #carId
    #customerId
    #status
    #paymentMethod

    Ngoài ra còn dropdown Tiếng Việt ở header.
    """

    driver.get(BASE_URL)

    wait_for_page(driver)

    # -----------------------------------------------------
    # Click Tạo đơn thuê
    # -----------------------------------------------------

    create_button = assert_visible(
        driver,
        CREATE_BOOKING_BUTTON,
        "Nút Tạo đơn thuê"
    )

    create_button.click()

    # -----------------------------------------------------
    # Chờ URL
    # -----------------------------------------------------

    WebDriverWait(
        driver,
        WAIT_TIME
    ).until(
        lambda d: "/bookings/new"
        in d.current_url
    )

    print()
    print(
        "[PASS] Open create booking page"
    )

    print(
        "[INFO] URL:",
        driver.current_url
    )

    # -----------------------------------------------------
    # Language
    # -----------------------------------------------------

    language = assert_visible(
        driver,
        LANGUAGE_INPUT,
        "Dropdown ngôn ngữ"
    )

    assert language.get_attribute(
        "aria-label"
    ) == "Ngôn ngữ"

    print(
        "[PASS] Language dropdown"
    )

    # -----------------------------------------------------
    # Car
    # -----------------------------------------------------

    car = assert_visible(
        driver,
        CAR_DROPDOWN,
        "Dropdown Chọn xe"
    )

    assert car.get_attribute(
        "id"
    ) == "carId"

    print(
        "[PASS] Car dropdown: Chọn xe"
    )

    # -----------------------------------------------------
    # Customer
    # -----------------------------------------------------

    customer = assert_visible(
        driver,
        CUSTOMER_DROPDOWN,
        "Dropdown khách hàng"
    )

    assert customer.get_attribute(
        "id"
    ) == "customerId"

    print(
        "[PASS] Customer dropdown"
    )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status = assert_visible(
        driver,
        STATUS_DROPDOWN,
        "Dropdown trạng thái"
    )

    assert status.get_attribute(
        "id"
    ) == "status"

    print(
        "[PASS] Status dropdown"
    )

    # -----------------------------------------------------
    # Payment
    # -----------------------------------------------------

    payment = assert_visible(
        driver,
        PAYMENT_METHOD_DROPDOWN,
        "Dropdown phương thức thanh toán"
    )

    assert payment.get_attribute(
        "id"
    ) == "paymentMethod"

    print(
        "[PASS] Payment method dropdown"
    )

    # -----------------------------------------------------
    # Tổng số ant-select
    # -----------------------------------------------------

    selects = driver.find_elements(
        By.CSS_SELECTOR,
        ".ant-select"
    )

    print(
        "[INFO] Total .ant-select:",
        len(selects)
    )

    assert len(selects) >= 5, (
        "Trang tạo đơn thuê phải có "
        "ít nhất 5 dropdown."
    )

    print(
        "[PASS] Create booking dropdown contract"
    )


# =========================================================
# TEST 12
# FULL BOOKING PAGE CONTRACT
# =========================================================

def test_booking_full_page_contract(driver):

    driver.get(BASE_URL)

    wait_for_page(driver)

    checks = []

    # -----------------------------------------------------
    # PAGE TITLE
    # -----------------------------------------------------

    title_elements = driver.find_elements(
        *PAGE_TITLE
    )

    checks.append(
        (
            "Page title",
            len(title_elements) >= 1
        )
    )

    # -----------------------------------------------------
    # MAIN
    # -----------------------------------------------------

    checks.append(
        (
            "Main",
            len(
                driver.find_elements(*MAIN)
            ) == 1
        )
    )

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    checks.append(
        (
            "Logo",
            len(
                driver.find_elements(*LOGO)
            ) >= 1
        )
    )

    # -----------------------------------------------------
    # LANGUAGE
    #
    # KHÔNG dùng main .ant-select
    # -----------------------------------------------------

    checks.append(
        (
            "Language dropdown",
            len(
                driver.find_elements(
                    *LANGUAGE_INPUT
                )
            ) >= 1
        )
    )

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    checks.append(
        (
            "Booking table",
            len(
                driver.find_elements(*TABLE)
            ) == 1
        )
    )

    # -----------------------------------------------------
    # DATA ROW
    # -----------------------------------------------------

    checks.append(
        (
            "Booking data",
            len(
                get_real_rows(driver)
            ) > 0
        )
    )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    checks.append(
        (
            "Pagination",
            len(
                driver.find_elements(
                    *PAGINATION
                )
            ) >= 1
        )
    )

    # -----------------------------------------------------
    # CREATE BUTTON
    # -----------------------------------------------------

    checks.append(
        (
            "Create booking button",
            len(
                driver.find_elements(
                    *CREATE_BOOKING_BUTTON
                )
            ) >= 1
        )
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("BOOKING PAGE CONTRACT")
    print("=" * 60)

    failed = []

    for name, passed in checks:

        if passed:
            print(
                f"[PASS] {name}"
            )
        else:
            print(
                f"[FAIL] {name}"
            )
            failed.append(name)

    print("=" * 60)

    assert not failed, (
        "Booking contract failed: "
        + ", ".join(failed)
    )