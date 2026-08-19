import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from core.config import Config
from core.driver_factory import DriverFactory


# =========================================================
# CONFIG
# =========================================================

LOGIN_URL = "https://courses.plt.pro.vn/login"
BOOKING_CREATE_URL = "https://courses.plt.pro.vn/bookings/new"

WAIT_TIME = 30


# =========================================================
# DROPDOWN TRONG FORM TẠO ĐẶT XE
# KHÔNG TEST DROPDOWN NGÔN NGỮ
# =========================================================

DROPDOWNS = [
    {
        "name": "Chọn xe",
        "key": "booking_car_dropdown",
        "locator": (
            By.ID,
            "carId",
        ),
    },
    {
        "name": "Chọn khách",
        "key": "booking_customer_dropdown",
        "locator": (
            By.ID,
            "customerId",
        ),
    },
    {
        "name": "Trạng thái",
        "key": "booking_status_dropdown",
        "locator": (
            By.ID,
            "status",
        ),
    },
    {
        "name": "Phương thức thanh toán",
        "key": "booking_payment_method_dropdown",
        "locator": (
            By.ID,
            "paymentMethod",
        ),
    },
]


# =========================================================
# LOGIN
# =========================================================

def login(driver):
    """
    Login thật bằng email/password.

    Login chỉ là bước chuẩn bị để vào hệ thống.
    Không tính Login là test case.
    """

    wait = WebDriverWait(driver, WAIT_TIME)

    print()
    print("=" * 70)
    print("[LOGIN] BẮT ĐẦU ĐĂNG NHẬP")
    print("=" * 70)

    print("[LOGIN] URL hiện tại:", driver.current_url)

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='email'], "
                "input[name='email'], "
                "input[name='username'], "
                "input[placeholder='ban@plt.pro.vn']",
            )
        )
    )

    print("[LOGIN] Tìm thấy ô Email")

    email.clear()

    email.send_keys(
        Config.TEST_EMAIL
    )

    print(
        "[LOGIN] Đã nhập email:",
        Config.TEST_EMAIL,
    )

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    password = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='password'], "
                "input[name='password'], "
                "input[placeholder='Nhập mật khẩu']",
            )
        )
    )

    print("[LOGIN] Tìm thấy ô Password")

    password.clear()

    password.send_keys(
        Config.TEST_PASSWORD
    )

    print("[LOGIN] Đã nhập password")

    # -----------------------------------------------------
    # LOGIN BUTTON
    # -----------------------------------------------------

    login_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit']",
            )
        )
    )

    print("[LOGIN] Tìm thấy nút đăng nhập")

    login_button.click()

    print("[LOGIN] Đã click Đăng nhập")

    # -----------------------------------------------------
    # WAIT LOGIN COMPLETE
    # -----------------------------------------------------

    try:

        wait.until(
            lambda d: "/login"
            not in d.current_url.lower()
        )

    except TimeoutException:

        print(
            "[LOGIN] Không thoát khỏi trang login"
        )

        print(
            "[LOGIN] URL:",
            driver.current_url,
        )

        raise AssertionError(
            "Đăng nhập thất bại: "
            "vẫn đang ở trang /login"
        )

    print("[LOGIN] PASS")
    print(
        "[LOGIN] URL sau login:",
        driver.current_url,
    )

    print("=" * 70)


# =========================================================
# OPEN BOOKING CREATE PAGE
# =========================================================

def open_booking_create_page(driver):
    """
    Mở trang tạo đặt xe.

    Flow:

        /bookings/new
              ↓
        nếu bị redirect /login
              ↓
        login
              ↓
        /bookings/new
    """

    wait = WebDriverWait(
        driver,
        WAIT_TIME,
    )

    print()
    print("=" * 70)
    print("[BOOKING] MỞ FORM TẠO ĐẶT XE")
    print("=" * 70)

    # -----------------------------------------------------
    # MỞ TRANG
    # -----------------------------------------------------

    driver.get(
        BOOKING_CREATE_URL
    )

    print(
        "[BOOKING] Requested URL:",
        BOOKING_CREATE_URL,
    )

    # -----------------------------------------------------
    # CHỜ TRANG PHẢN HỒI
    # -----------------------------------------------------

    try:

        wait.until(
            lambda d: (
                "/bookings/new"
                in d.current_url.lower()
                or "/login"
                in d.current_url.lower()
            )
        )

    except TimeoutException:

        raise AssertionError(
            "Không thể mở trang tạo đặt xe"
        )

    print(
        "[BOOKING] URL sau khi mở:",
        driver.current_url,
    )

    # -----------------------------------------------------
    # NẾU CHƯA LOGIN
    # -----------------------------------------------------

    if "/login" in driver.current_url.lower():

        print(
            "[BOOKING] Chưa đăng nhập."
        )

        print(
            "[BOOKING] Tiến hành login..."
        )

        login(driver)

        # -------------------------------------------------
        # SAU LOGIN QUAY LẠI BOOKING
        # -------------------------------------------------

        driver.get(
            BOOKING_CREATE_URL
        )

        print(
            "[BOOKING] Quay lại:",
            BOOKING_CREATE_URL,
        )

    # -----------------------------------------------------
    # CHỜ ĐÚNG URL
    # -----------------------------------------------------

    wait.until(
        lambda d: (
            "/bookings/new"
            in d.current_url.lower()
        )
    )

    # -----------------------------------------------------
    # CHỜ MAIN
    # -----------------------------------------------------

    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "main",
            )
        )
    )

    print(
        "[BOOKING] Đã vào form tạo đặt xe"
    )

    print(
        "[BOOKING] Current URL:",
        driver.current_url,
    )

    print("=" * 70)


# =========================================================
# OPEN DROPDOWN
# =========================================================

def open_dropdown(driver, locator):
    """
    Click dropdown.

    Hỗ trợ:
        - Ant Design Select
        - input/select thông thường
    """

    wait = WebDriverWait(
        driver,
        WAIT_TIME,
    )

    element = wait.until(
        EC.presence_of_element_located(
            locator
        )
    )

    # -----------------------------------------------------
    # SCROLL
    # -----------------------------------------------------

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            behavior: 'instant',
            block: 'center'
        });
        """,
        element,
    )

    # -----------------------------------------------------
    # WAIT CLICKABLE
    # -----------------------------------------------------

    wait.until(
        EC.element_to_be_clickable(
            locator
        )
    )

    # -----------------------------------------------------
    # CLICK
    # -----------------------------------------------------

    try:

        element.click()

    except Exception:

        driver.execute_script(
            "arguments[0].click();",
            element,
        )

    return element


# =========================================================
# GET DROPDOWN OPTIONS
# =========================================================

def get_visible_dropdown_options(driver):
    """
    Đọc option của dropdown đang mở.

    Hỗ trợ:
        1. Ant Design
        2. role=listbox
        3. role=option
        4. select option
    """

    wait = WebDriverWait(
        driver,
        WAIT_TIME,
    )

    # -----------------------------------------------------
    # ANT DESIGN
    # -----------------------------------------------------

    try:

        wait.until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR,
                (
                    ".ant-select-dropdown"
                    ":not(.ant-select-dropdown-hidden) "
                    ".ant-select-item-option-content"
                ),
            )
        )

    except TimeoutException:
        pass

    options = driver.find_elements(
        By.CSS_SELECTOR,
        (
            ".ant-select-dropdown"
            ":not(.ant-select-dropdown-hidden) "
            ".ant-select-item-option-content"
        ),
    )

    # -----------------------------------------------------
    # ROLE LISTBOX
    # -----------------------------------------------------

    if not options:

        options = driver.find_elements(
            By.CSS_SELECTOR,
            (
                "[role='listbox']"
                ":not([aria-hidden='true']) "
                "[role='option']"
            ),
        )

    # -----------------------------------------------------
    # GENERIC ROLE OPTION
    # -----------------------------------------------------

    if not options:

        options = driver.find_elements(
            By.CSS_SELECTOR,
            "[role='option']",
        )

    # -----------------------------------------------------
    # READ TEXT
    # -----------------------------------------------------

    values = []

    for option in options:

        try:

            if not option.is_displayed():
                continue

            text = (
                option.text
                or ""
            ).strip()

            if (
                text
                and text not in values
            ):
                values.append(text)

        except Exception:
            continue

    return values


# =========================================================
# CLOSE DROPDOWN
# =========================================================

def close_dropdown(driver):
    """
    Đóng dropdown bằng ESC.
    """

    try:

        driver.execute_script(
            """
            document.dispatchEvent(
                new KeyboardEvent(
                    'keydown',
                    {
                        key: 'Escape',
                        code: 'Escape',
                        keyCode: 27,
                        which: 27,
                        bubbles: true
                    }
                )
            );
            """
        )

    except Exception:
        pass


# =========================================================
# CHECK DROPDOWN
# =========================================================

def check_dropdown(
    driver,
    dropdown,
):
    """
    Test một dropdown.
    """

    wait = WebDriverWait(
        driver,
        WAIT_TIME,
    )

    name = dropdown["name"]
    key = dropdown["key"]
    locator = dropdown["locator"]

    print()
    print("-" * 70)
    print(
        "[TEST DROPDOWN]",
        name,
    )
    print(
        "[KEY]",
        key,
    )
    print(
        "[LOCATOR]",
        locator,
    )

    # -----------------------------------------------------
    # FIND ELEMENT
    # -----------------------------------------------------

    element = wait.until(
        EC.presence_of_element_located(
            locator
        )
    )

    assert element.is_displayed(), (
        f"Dropdown '{name}' "
        f"không hiển thị"
    )

    print(
        "[PASS] Dropdown tồn tại:",
        name,
    )

    # -----------------------------------------------------
    # OPEN
    # -----------------------------------------------------

    open_dropdown(
        driver,
        locator,
    )

    print(
        "[PASS] Đã mở dropdown:",
        name,
    )

    # -----------------------------------------------------
    # READ OPTIONS
    # -----------------------------------------------------

    options = get_visible_dropdown_options(
        driver
    )

    print(
        "[OPTIONS]",
        len(options),
        "option",
    )

    for index, option in enumerate(
        options,
        start=1,
    ):

        print(
            f"   {index}. {option}"
        )

    # -----------------------------------------------------
    # ASSERT
    # -----------------------------------------------------

    assert options, (
        f"Dropdown '{name}' "
        f"không có option"
    )

    print(
        "[PASS] Dropdown có dữ liệu:",
        name,
    )

    # -----------------------------------------------------
    # CLOSE
    # -----------------------------------------------------

    close_dropdown(
        driver
    )

    print(
        "[PASS] Đã đóng dropdown:",
        name,
    )


# =========================================================
# FIXTURE
# =========================================================

@pytest.fixture
def driver():

    driver = None

    try:

        # -------------------------------------------------
        # CREATE DRIVER
        # -------------------------------------------------

        driver = DriverFactory.create_driver(
            headless=False,
            keep_session=False,
        )

        print()
        print(
            "[DRIVER] Chrome đã khởi động"
        )

        # -------------------------------------------------
        # OPEN + LOGIN + BOOKING
        # -------------------------------------------------

        open_booking_create_page(
            driver
        )

        yield driver

    finally:

        if driver:

            try:

                driver.quit()

                print(
                    "[DRIVER] Chrome đã đóng"
                )

            except Exception:
                pass


# =========================================================
# TEST
# =========================================================

@pytest.mark.booking
def test_create_booking_dropdowns(
    driver,
):
    """
    Test các dropdown trong form
    Tạo đặt xe.

    KHÔNG test:
        - Login
        - Dropdown Ngôn ngữ
        - Trang danh sách booking

    CHỈ test:

        Chọn xe
        Chọn khách
        Trạng thái
        Phương thức thanh toán
    """

    print()
    print("=" * 70)
    print(
        "TEST QUẢN LÝ ĐẶT XE - FORM TẠO ĐẶT XE"
    )
    print("=" * 70)

    for dropdown in DROPDOWNS:

        check_dropdown(
            driver,
            dropdown,
        )

    print()
    print("=" * 70)
    print(
        "ALL CREATE BOOKING DROPDOWNS PASSED"
    )
    print("=" * 70)