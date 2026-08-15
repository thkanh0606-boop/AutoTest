import os
import re
import sys
import time
import csv
from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.driver_factory import DriverFactory
from core.helpers.utils import capture_screenshot, get_logger
from core.test_result_repository import TestResultRepository

logger = get_logger()


# =========================================================
# LOCATOR
# =========================================================

def _by(locator_type: str):
    mapping = {
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
    }

    return mapping.get(
        (locator_type or "css").lower(),
        By.CSS_SELECTOR,
    )


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def _normalize_text(
    text: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    value = text or ""

    if trim:
        value = " ".join(value.split())

    if not case_sensitive:
        value = value.lower()

    return value


def _split_compare_lines(text: str):
    return [
        line.strip()
        for line in (text or "").splitlines()
        if line.strip()
    ]


# =========================================================
# COMPARE LINE BY LINE
# =========================================================

def _compare_line_pairs(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    expected_lines = _split_compare_lines(expected)
    actual_lines = _split_compare_lines(actual)

    pairs = []

    max_count = max(
        len(expected_lines),
        len(actual_lines),
    )

    for index in range(max_count):
        expected_line = (
            expected_lines[index]
            if index < len(expected_lines)
            else ""
        )

        actual_line = (
            actual_lines[index]
            if index < len(actual_lines)
            else ""
        )

        expected_compare = _normalize_text(
            expected_line,
            trim=trim,
            case_sensitive=case_sensitive,
        )

        actual_compare = _normalize_text(
            actual_line,
            trim=trim,
            case_sensitive=case_sensitive,
        )

        pair_status = (
            "PASS"
            if (
                expected_compare == actual_compare
                and expected_line
                and actual_line
            )
            else "FAIL"
        )

        pairs.append(
            {
                "index": index + 1,
                "expected": expected_line,
                "actual": actual_line,
                "status": pair_status,
            }
        )

    status = (
        "PASSED"
        if pairs and all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


# =========================================================
# COMPARE UNORDERED LINES
# =========================================================

def _compare_unordered_lines(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    """
    So sánh 2 danh sách không phụ thuộc thứ tự.

    Dùng cho Dropdown Hãng của Danh mục xe vì mục tiêu là
    kiểm tra tính đồng bộ với danh sách Hãng đang hoạt động,
    không phải thứ tự hiển thị.
    """

    expected_lines = _split_compare_lines(expected)
    actual_lines = _split_compare_lines(actual)

    normalized_actual = [
        _normalize_text(
            value,
            trim=trim,
            case_sensitive=case_sensitive,
        )
        for value in actual_lines
    ]

    used_actual_indexes = set()
    pairs = []

    for expected_line in expected_lines:
        expected_compare = _normalize_text(
            expected_line,
            trim=trim,
            case_sensitive=case_sensitive,
        )

        matched_index = None

        for index, actual_compare in enumerate(
            normalized_actual
        ):
            if index in used_actual_indexes:
                continue

            if (
                expected_compare
                and expected_compare == actual_compare
            ):
                matched_index = index
                break

        if matched_index is None:
            pairs.append(
                {
                    "index": len(pairs) + 1,
                    "expected": expected_line,
                    "actual": "(thiếu trong dropdown)",
                    "status": "FAIL",
                }
            )
        else:
            used_actual_indexes.add(matched_index)

            pairs.append(
                {
                    "index": len(pairs) + 1,
                    "expected": expected_line,
                    "actual": actual_lines[matched_index],
                    "status": "PASS",
                }
            )

    # Option xuất hiện trong dropdown nhưng không thuộc danh sách Hãng active.
    for index, actual_line in enumerate(actual_lines):
        if index in used_actual_indexes:
            continue

        pairs.append(
            {
                "index": len(pairs) + 1,
                "expected": "(không mong đợi)",
                "actual": actual_line,
                "status": "FAIL",
            }
        )

    status = (
        "PASSED"
        if pairs and all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


# =========================================================
# TABLE HELPERS
# =========================================================

def _split_table_line(line: str):
    if "\t" in line:
        return [
            cell.strip()
            for cell in line.split("\t")
        ]

    try:
        cells = next(csv.reader(StringIO(line)))
    except Exception:
        cells = [line]

    return [
        cell.strip()
        for cell in cells
    ]


def _table_matrix(text: str):
    rows = []

    for line in (text or "").splitlines():
        if not line.strip():
            continue

        cells = _split_table_line(line)

        while cells and not cells[-1]:
            cells.pop()

        if cells:
            rows.append(cells)

    return rows


def _table_text_from_element(element):
    table_rows = []

    row_elements = element.find_elements(
        By.CSS_SELECTOR,
        "tr, .ant-table-row",
    )

    for row_element in row_elements:
        cell_elements = row_element.find_elements(
            By.CSS_SELECTOR,
            "th, td, .ant-table-cell",
        )

        cells = [
            cell.text.strip()
            for cell in cell_elements
            if cell.text.strip()
        ]

        if cells:
            table_rows.append(
                "\t".join(cells)
            )

    if table_rows:
        return "\n".join(table_rows)

    lines = [
        line.strip()
        for line in (element.text or "").splitlines()
        if line.strip()
    ]

    return "\t".join(lines)


def _compare_table_rows(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    expected_rows = _table_matrix(expected)
    actual_rows = _table_matrix(actual)

    max_rows = max(
        len(expected_rows),
        len(actual_rows),
    )

    pairs = []

    for row_index in range(max_rows):
        expected_cells = (
            expected_rows[row_index]
            if row_index < len(expected_rows)
            else []
        )

        actual_cells = (
            actual_rows[row_index]
            if row_index < len(actual_rows)
            else []
        )

        max_cells = max(
            len(expected_cells),
            len(actual_cells),
        )

        for cell_index in range(max_cells):
            expected_cell = (
                expected_cells[cell_index]
                if cell_index < len(expected_cells)
                else ""
            )

            actual_cell = (
                actual_cells[cell_index]
                if cell_index < len(actual_cells)
                else ""
            )

            expected_compare = _normalize_text(
                expected_cell,
                trim=trim,
                case_sensitive=case_sensitive,
            )

            actual_compare = _normalize_text(
                actual_cell,
                trim=trim,
                case_sensitive=case_sensitive,
            )

            pair_status = (
                "PASS"
                if (
                    expected_compare == actual_compare
                    and expected_cell
                    and actual_cell
                )
                else "FAIL"
            )

            pairs.append(
                {
                    "index": f"R{row_index + 1}C{cell_index + 1}",
                    "expected": expected_cell,
                    "actual": actual_cell,
                    "status": pair_status,
                }
            )

    status = (
        "PASSED"
        if pairs and all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


# =========================================================
# CONTAINS
# =========================================================

def _compare_contains_all(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    expected_lines = _split_compare_lines(expected)

    actual_compare = _normalize_text(
        actual,
        trim=trim,
        case_sensitive=case_sensitive,
    )

    pairs = []

    for index, expected_line in enumerate(
        expected_lines,
        start=1,
    ):
        expected_compare = _normalize_text(
            expected_line,
            trim=trim,
            case_sensitive=case_sensitive,
        )

        matched = bool(
            expected_compare
            and expected_compare in actual_compare
        )

        pairs.append(
            {
                "index": index,
                "expected": expected_line,
                "actual": expected_line if matched else actual,
                "status": "PASS" if matched else "FAIL",
            }
        )

    status = (
        "PASSED"
        if pairs and all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


def _compare_contains_all_has_number(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    status, pairs = _compare_contains_all(
        expected,
        actual,
        trim=trim,
        case_sensitive=case_sensitive,
    )

    has_number = bool(
        re.search(r"\d+", actual or "")
    )

    pairs.append(
        {
            "index": len(pairs) + 1,
            "expected": "Có số liệu",
            "actual": (
                "Có số liệu"
                if has_number
                else "Không thấy số liệu"
            ),
            "status": (
                "PASS"
                if has_number
                else "FAIL"
            ),
        }
    )

    status = (
        "PASSED"
        if all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


# =========================================================
# NAVIGATION
# =========================================================

def _compare_navigation_expected(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):
    expected_value = _normalize_text(
        expected,
        trim=trim,
        case_sensitive=case_sensitive,
    )

    actual_value = _normalize_text(
        actual,
        trim=trim,
        case_sensitive=case_sensitive,
    )

    if not expected_value:
        return "FAILED"

    if expected_value.startswith(
        ("http://", "https://")
    ):
        return (
            "PASSED"
            if actual_value == expected_value
            else "FAILED"
        )

    return (
        "PASSED"
        if expected_value in actual_value
        else "FAILED"
    )


# =========================================================
# LOGIN
# =========================================================

def _login_form_visible(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[type='password'], "
                    "input[name='password']",
                )
            )
        )

        return True

    except Exception:
        return False


def _ensure_logged_in(driver, target_url: str):
    if not _login_form_visible(driver):
        return

    wait = WebDriverWait(
        driver,
        Config.EXPLICIT_WAIT,
    )

    email = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='email'], "
                "input[name='email'], "
                "input[name='username'], "
                "input[type='text']",
            )
        )
    )

    password = driver.find_element(
        By.CSS_SELECTOR,
        "input[type='password'], input[name='password']",
    )

    email.clear()
    email.send_keys(Config.TEST_EMAIL)

    password.clear()
    password.send_keys(Config.TEST_PASSWORD)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit'], "
        "input[type='submit'], "
        "button",
    ).click()

    wait.until(
        lambda browser: not _login_form_visible(browser)
    )

    driver.get(target_url)


# =========================================================
# VEHICLE CATALOG - OLD LOGIC
# =========================================================

def _active_brand_names_from_catalog(driver):
    """
    Lấy tên các Hãng đang hoạt động trực tiếp từ bảng
    Danh mục xe.

    Giữ nguyên logic cũ.
    """

    heading_xpath = (
        "(//*[self::h1 or self::h2 or self::h3 or "
        "self::h4 or self::h5 or self::h6]"
        "[normalize-space()='Danh sách hãng xe'])[1]"
    )

    rows = driver.find_elements(
        By.XPATH,
        heading_xpath
        + "/following::table[1]//tbody/tr",
    )

    if not rows:
        rows = driver.find_elements(
            By.XPATH,
            heading_xpath
            + "/following::*[@role='row'][position()>1]",
        )

    active_names = []

    for row in rows:
        row_text = (row.text or "").strip()

        if not row_text:
            continue

        if "Đang hoạt động" not in row_text:
            continue

        if "Ngừng hoạt động" in row_text:
            continue

        cells = row.find_elements(
            By.CSS_SELECTOR,
            "td, [role='cell']",
        )

        first_cell_text = (
            cells[0].text
            if cells
            else row_text
        )

        lines = [
            line.strip()
            for line in (
                first_cell_text or ""
            ).splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        brand_name = lines[0]

        if (
            brand_name
            and brand_name not in active_names
        ):
            active_names.append(brand_name)

    return active_names


def _is_catalog_brand_dropdown(
    module: str,
    page_key: str,
    element_key: str,
) -> bool:
    return (
        module == "dropdown"
        and page_key == "plt_vehicle_catalog"
        and element_key == "catalog_brand_filter"
    )


# =========================================================
# NEW - BOOKING PAGE
# =========================================================

def _is_booking_page(
    module: str,
    page_key: str,
) -> bool:
    """
    Xác định test hiện tại có thuộc trang
    Quản lý đặt xe hay không.

    Không ảnh hưởng các page cũ.
    """

    return (
        page_key == "plt_booking"
        and module in (
            "dropdown",
            "label",
            "text",
            "menu",
            "ui",
            "table",
        )
    )


def _is_booking_dropdown(
    module: str,
    page_key: str,
    element_key: str,
) -> bool:
    """
    Xác định Dropdown thuộc trang Quản lý đặt xe.

    Không hard-code tên element để TestContract
    vẫn là nguồn dữ liệu chính.

    Vì vậy cả:
        - Dropdown trạng thái booking
        - Dropdown bộ lọc booking

    đều được xử lý.
    """

    return (
        module == "dropdown"
        and page_key == "plt_booking"
    )


def _booking_dropdown_log_name(
    element_key: str,
    element_name: str,
) -> str:
    """
    Tên hiển thị trong log cho Booking.
    """

    if element_name:
        return element_name

    if element_key:
        return element_key

    return "Booking Dropdown"


def _wait_booking_dropdown_options(driver):
    """
    Chờ option của dropdown Booking xuất hiện.

    Hỗ trợ Ant Design.

    Trả về danh sách WebElement.
    """

    wait = WebDriverWait(
        driver,
        Config.EXPLICIT_WAIT,
    )

    return wait.until(
        lambda browser: (
            browser.find_elements(
                By.CSS_SELECTOR,
                ".ant-select-dropdown:not("
                ".ant-select-dropdown-hidden"
                ") "
                ".ant-select-item-option-content",
            )
            or browser.find_elements(
                By.CSS_SELECTOR,
                ".ant-dropdown:not(.ant-dropdown-hidden) "
                "[role='option']",
            )
            or browser.find_elements(
                By.CSS_SELECTOR,
                "[role='listbox']:not([aria-hidden='true']) "
                "[role='option']",
            )
        )
    )


def _read_booking_dropdown(driver, element):
    """
    Đọc option của Dropdown thuộc trang Booking.

    Thứ tự xử lý:

    1. Native <select>
    2. Ant Design
    3. role=listbox
    4. ul/li
    5. Dropdown text trong element

    Hàm này chỉ được gọi khi:
        page_key == plt_booking
        module == dropdown
    """

    # -----------------------------------------------------
    # 1. Native SELECT
    # -----------------------------------------------------

    tag_name = (
        element.tag_name or ""
    ).lower()

    if tag_name == "select":
        options = element.find_elements(
            By.TAG_NAME,
            "option",
        )

        values = []

        for option in options:
            text = (
                option.text or ""
            ).strip()

            if text and text not in values:
                values.append(text)

        if values:
            return "\n".join(values)

    # -----------------------------------------------------
    # 2. Element bên trong là SELECT
    # -----------------------------------------------------

    try:
        nested_select = element.find_elements(
            By.CSS_SELECTOR,
            "select",
        )

        if nested_select:
            options = nested_select[0].find_elements(
                By.TAG_NAME,
                "option",
            )

            values = []

            for option in options:
                text = (
                    option.text or ""
                ).strip()

                if text and text not in values:
                    values.append(text)

            if values:
                return "\n".join(values)

    except Exception:
        pass

    # -----------------------------------------------------
    # 3. Click Booking dropdown
    # -----------------------------------------------------

    try:
        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            lambda _driver: (
                element.is_displayed()
                and element.is_enabled()
            )
        )

        try:
            element.click()
        except Exception:
            driver.execute_script(
                "arguments[0].click();",
                element,
            )

    except Exception as error:
        logger.warning(
            "[BOOKING DROPDOWN] "
            "Không click được element: %s",
            error,
        )

    # -----------------------------------------------------
    # 4. Ant Design
    # -----------------------------------------------------

    try:
        option_elements = _wait_booking_dropdown_options(
            driver
        )

        values = []

        for option in option_elements:
            text = (
                option.text or ""
            ).strip()

            if text and text not in values:
                values.append(text)

        if values:
            return "\n".join(values)

    except Exception:
        pass

    # -----------------------------------------------------
    # 5. Generic role=listbox
    # -----------------------------------------------------

    try:
        option_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "[role='listbox']:not([aria-hidden='true']) "
            "[role='option']",
        )

        values = []

        for option in option_elements:
            if not option.is_displayed():
                continue

            text = (
                option.text or ""
            ).strip()

            if text and text not in values:
                values.append(text)

        if values:
            return "\n".join(values)

    except Exception:
        pass

    # -----------------------------------------------------
    # 6. Generic dropdown ul/li
    # -----------------------------------------------------

    try:
        option_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "ul[role='listbox'] li, "
            ".dropdown-menu li, "
            ".select-options li",
        )

        values = []

        for option in option_elements:
            if not option.is_displayed():
                continue

            text = (
                option.text or ""
            ).strip()

            if text and text not in values:
                values.append(text)

        if values:
            return "\n".join(values)

    except Exception:
        pass

    # -----------------------------------------------------
    # 7. Fallback
    # -----------------------------------------------------

    return (
        element.text or ""
    ).strip()


# =========================================================
# READ ACTUAL
# =========================================================

def _read_actual(
    driver,
    element,
    module: str,
    action_type: str = "text_equals",
    target_path: str = "",
    page_key: str = "",
    element_key: str = "",
    element_name: str = "",
) -> str:

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    if action_type == "click_url_contains":
        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            lambda _driver: (
                element.is_displayed()
                and element.is_enabled()
            )
        )

        element.click()

        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            EC.url_contains(target_path)
        )

        return driver.current_url

    if action_type == "deep_link_url_contains":
        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "main")
            )
        )

        return driver.current_url

    # -----------------------------------------------------
    # BOOKING DROPDOWN
    # -----------------------------------------------------

    if _is_booking_dropdown(
        module,
        page_key,
        element_key,
    ):
        logger.info(
            "[BOOKING DROPDOWN] "
            "Đọc element: %s (%s)",
            _booking_dropdown_log_name(
                element_key,
                element_name,
            ),
            element_key,
        )

        return _read_booking_dropdown(
            driver,
            element,
        )

    # -----------------------------------------------------
    # GENERIC DROPDOWN
    # -----------------------------------------------------

    if module == "dropdown":
        options = element.find_elements(
            By.TAG_NAME,
            "option",
        )

        if options:
            return "\n".join(
                option.text.strip()
                for option in options
                if option.text.strip()
            )

        try:
            element.click()

        except Exception:
            try:
                element.find_element(
                    By.CSS_SELECTOR,
                    "input[role='combobox']",
                ).click()

            except Exception:
                pass

        try:
            WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
            ).until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".ant-select-dropdown:not("
                        ".ant-select-dropdown-hidden"
                        ") "
                        ".ant-select-item-option-content",
                    )
                )
            )
        except Exception:
            pass

        option_elements = driver.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-dropdown:not("
            ".ant-select-dropdown-hidden"
            ") "
            ".ant-select-item-option-content",
        )

        values = []

        for option in option_elements:
            text = (
                option.text or ""
            ).strip()

            if text and text not in values:
                values.append(text)

        return "\n".join(values)

    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    if module == "image":
        return (
            element.get_attribute("alt")
            or element.get_attribute("src")
            or "visible"
        )

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    if module == "table":
        return _table_text_from_element(
            element
        )

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    if module == "ui":
        return (
            "visible"
            if element.is_displayed()
            else "hidden"
        )

    # -----------------------------------------------------
    # LABEL / TEXT
    # -----------------------------------------------------

    return (
        element.text or ""
    ).strip()


# =========================================================
# MAIN RUNNER
# =========================================================

def run_label_text_test(
    worker=None,
    module: str = "label",
    url: str = "",
    page_key: str = "",
    page_name: str = "",
    element_key: str = "",
    element_name: str = "",
    locator_type: str = "css",
    locator_value: str = "",
    expected: str = "",
    case_id: str = "",
    steps: str = "",
    expected_result: str = "",
    action_type: str = "text_equals",
    target_path: str = "",
    trim: bool = True,
    case_sensitive: bool = True,
    headless: bool = False,
    persist: bool = True,
    step_delay: float = 0,
    close_delay: float = 0,
):
    driver = None

    repository = TestResultRepository()

    screenshot_path = ""
    error_message = ""
    actual = ""

    status = "ERROR"
    message = ""

    pairs = []

    try:

        # =================================================
        # LOG - OPEN PAGE
        # =================================================

        if worker:
            worker.log_signal.emit(
                f"[{module.upper()}] "
                f"Mở trang kiểm thử: {page_name}"
            )

            worker.progress_signal.emit(20)

        # =================================================
        # CREATE DRIVER
        # =================================================

        driver = DriverFactory.create_driver(
            headless=headless,
            keep_session=True,
        )

        driver.get(url)

        # =================================================
        # LOGIN
        # =================================================

        _ensure_logged_in(
            driver,
            url,
        )

        if step_delay > 0:
            time.sleep(step_delay)

        # =================================================
        # BOOKING LOG
        # =================================================

        if _is_booking_page(
            module,
            page_key,
        ):
            if worker:
                worker.log_signal.emit(
                    "[BOOKING] "
                    f"Đang kiểm tra: {element_name}"
                )

        # =================================================
        # ELEMENT
        # =================================================

        if worker:
            worker.log_signal.emit(
                f"[{module.upper()}] "
                f"Kiểm tra element: {element_name}"
            )

            worker.progress_signal.emit(60)

        element = driver.find_element(
            _by(locator_type),
            locator_value,
        )

        # =================================================
        # VISUAL HIGHLIGHT
        # =================================================

        if step_delay > 0:

            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView("
                    "{behavior:'smooth', block:'center'});"
                    "arguments[0].style.outline="
                    "'3px solid #ef4444';"
                    "arguments[0].style.outlineOffset="
                    "'4px';",
                    element,
                )

            except Exception:
                # Visual assistance must never
                # change the test result.
                pass

            time.sleep(step_delay)

        # =================================================
        # VEHICLE CATALOG SPECIAL CASE
        # =================================================

        auto_catalog_dropdown = (
            _is_catalog_brand_dropdown(
                module,
                page_key,
                element_key,
            )
        )

        # =================================================
        # BOOKING SPECIAL CASE
        # =================================================

        booking_dropdown = (
            _is_booking_dropdown(
                module,
                page_key,
                element_key,
            )
        )

        if booking_dropdown and worker:
            worker.log_signal.emit(
                "[BOOKING] "
                f"Dropdown: {element_name}"
            )

        # =================================================
        # AUTO EXPECTED - VEHICLE CATALOG
        # =================================================

        if auto_catalog_dropdown:

            active_brands = (
                _active_brand_names_from_catalog(
                    driver
                )
            )

            if not active_brands:
                raise RuntimeError(
                    "Không đọc được danh sách Hãng "
                    "đang hoạt động từ bảng Hãng xe."
                )

            expected = "\n".join(
                active_brands
            )

            expected_result = expected

            if worker:
                worker.log_signal.emit(
                    f"[DROPDOWN] "
                    f"Tự lấy {len(active_brands)} "
                    "Hãng đang hoạt động làm Expected."
                )

        # =================================================
        # READ ACTUAL
        # =================================================

        actual = _read_actual(
            driver,
            element,
            module,
            action_type=action_type,
            target_path=target_path,
            page_key=page_key,
            element_key=element_key,
            element_name=element_name,
        )

        if step_delay > 0:
            time.sleep(step_delay)

        # =================================================
        # COMPARE
        # =================================================

        # -------------------------------------------------
        # VEHICLE CATALOG
        # -------------------------------------------------

        if auto_catalog_dropdown:

            status, pairs = _compare_unordered_lines(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

        # -------------------------------------------------
        # NAVIGATION
        # -------------------------------------------------

        elif action_type in (
            "click_url_contains",
            "deep_link_url_contains",
        ):

            status = _compare_navigation_expected(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

        # -------------------------------------------------
        # CONTAINS
        # -------------------------------------------------

        elif action_type == "contains_all":

            status, pairs = _compare_contains_all(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

        # -------------------------------------------------
        # CONTAINS + NUMBER
        # -------------------------------------------------

        elif action_type == "contains_all_has_number":

            status, pairs = (
                _compare_contains_all_has_number(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        # -------------------------------------------------
        # DROPDOWN / MENU
        # -------------------------------------------------

        elif module in (
            "dropdown",
            "menu",
        ):

            status, pairs = _compare_line_pairs(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        elif module == "table":

            status, pairs = _compare_table_rows(
                expected,
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

        # -------------------------------------------------
        # LABEL / TEXT / OTHER
        # -------------------------------------------------

        else:

            expected_compare = _normalize_text(
                expected,
                trim=trim,
                case_sensitive=case_sensitive,
            )

            actual_compare = _normalize_text(
                actual,
                trim=trim,
                case_sensitive=case_sensitive,
            )

            status = (
                "PASSED"
                if actual_compare == expected_compare
                else "FAILED"
            )

        # =================================================
        # MESSAGE
        # =================================================

        if status == "PASSED":

            if auto_catalog_dropdown:
                message = (
                    "Dropdown đồng bộ với các "
                    "Hãng đang hoạt động"
                )

            elif booking_dropdown:
                message = (
                    "Dropdown Booking khớp "
                    "với Expected"
                )

            else:
                message = (
                    "Expected khớp Actual"
                )

        elif auto_catalog_dropdown:

            message = (
                "Dropdown chưa đồng bộ với "
                "danh sách Hãng đang hoạt động"
            )

        elif booking_dropdown:

            message = (
                "Dropdown Booking chưa khớp "
                "với Expected"
            )

        elif not (expected or "").strip():

            message = (
                "Expected Result đang trống"
            )

        else:

            message = (
                "Expected khác Actual"
            )

        # =================================================
        # SCREENSHOT WHEN FAILED
        # =================================================

        if status != "PASSED" and driver:
            screenshot_path = capture_screenshot(
                driver,
                case_id
                or element_key
                or module,
            )

    except Exception as error:

        actual = f"ERROR: {error}"

        status = "ERROR"

        message = (
            "Không lấy được dữ liệu từ Selenium"
        )

        error_message = str(error)

        if driver:
            screenshot_path = capture_screenshot(
                driver,
                case_id
                or element_key
                or module,
            )

    finally:

        if driver:

            if close_delay > 0:
                time.sleep(close_delay)

            driver.quit()

    # =====================================================
    # RESULT PAYLOAD
    # =====================================================

    effective_case_id = (
        case_id
        or f"{module}:{page_key}:{element_key}"
    )

    effective_expected_result = (
        expected_result
        or expected
    )

    effective_steps = (
        steps
        or (
            f"1. Mở {page_name}. "
            f"2. Tìm {element_name}. "
            f"3. So sánh Expected và Actual."
        )
    )

    payload = {
        "module": module,
        "page_key": page_key,
        "page_name": page_name,
        "element_key": element_key,
        "element_name": element_name,
        "locator_type": locator_type,
        "locator_value": locator_value,
        "expected": expected,
        "case_id": effective_case_id,
        "steps": effective_steps,
        "expected_result": effective_expected_result,
        "actual": actual,
        "actual_result": actual,
        "status": status,
        "message": message,
        "error_message": error_message,
        "screenshot_path": screenshot_path,
        "pairs": pairs,
        "database": repository.db_path,
        "auto_expected": _is_catalog_brand_dropdown(
            module,
            page_key,
            element_key,
        ),
    }

    # =====================================================
    # SAVE RESULT
    # =====================================================

    if persist:
        payload["test_case_id"] = (
            repository.save_case_and_result(
                payload
            )
        )

    # =====================================================
    # LOGGER
    # =====================================================

    logger.info(
        "[%s] page=%s element=%s expected=%s "
        "actual=%s status=%s",
        module.upper(),
        page_name,
        element_name,
        expected,
        actual,
        status,
    )

    # =====================================================
    # WORKER RESULT
    # =====================================================

    if worker:

        worker.progress_signal.emit(100)

        worker.log_signal.emit(
            f"[{module.upper()}] "
            f"{status}: {message}"
        )

    return payload


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def run_text_dropdown_test(
    worker=None,
    **kwargs,
):
    return run_label_text_test(
        worker=worker,
        **kwargs,
    )


# Prevent pytest from treating runner functions
# as test functions.

run_label_text_test.__test__ = False
run_text_dropdown_test.__test__ = False