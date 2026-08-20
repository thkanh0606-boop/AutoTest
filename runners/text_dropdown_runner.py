# runners/text_dropdown_runner.py

import csv
import os
import re
import sys
import time
from io import StringIO

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    SessionNotCreatedException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from core.config import Config
from core.driver_factory import DriverFactory
from core.helpers.utils import (
    capture_screenshot,
    get_logger,
)
from core.test_result_repository import (
    TestResultRepository,
)


logger = get_logger()


# =========================================================
# CUSTOM EXCEPTION
# =========================================================

class SeleniumTestError(RuntimeError):
    """
    Exception nội bộ, message đã được làm sạch (không chứa
    stacktrace nội bộ của chromedriver), kèm context đầy đủ
    (page/element/locator/url) để log/hiển thị cho người dùng.
    """

    __test__ = False


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
# EXCEPTION HELPERS
# =========================================================

def _clean_exception_message(error: Exception) -> str:
    """
    Loại bỏ phần "Stacktrace: chromedriver!..." khỏi message,
    chỉ giữ lại phần mô tả lỗi thực tế do Selenium/W3C trả về.
    """

    raw = str(error) or ""

    if "Stacktrace:" in raw:
        raw = raw.split("Stacktrace:")[0]

    raw = raw.strip()

    if not raw:
        return type(error).__name__

    # Selenium thường trả "Message: <mô tả>\n" -> bỏ tiền tố "Message:"
    if raw.startswith("Message:"):
        raw = raw[len("Message:"):].strip()

    return raw or type(error).__name__


def _classify_exception(error: Exception) -> str:

    if isinstance(error, TimeoutException):
        return "TimeoutException"

    if isinstance(error, NoSuchElementException):
        return "NoSuchElementException"

    if isinstance(error, StaleElementReferenceException):
        return "StaleElementReferenceException"

    if isinstance(error, ElementClickInterceptedException):
        return "ElementClickInterceptedException"

    if isinstance(error, SessionNotCreatedException):
        return "SessionNotCreatedException"

    if isinstance(error, WebDriverException):
        return "WebDriverException"

    return type(error).__name__


def _safe_current_url(driver) -> str:

    try:
        return driver.current_url
    except Exception:
        return "(không lấy được URL - session có thể đã chết)"


def _safe_title(driver) -> str:

    try:
        return driver.title
    except Exception:
        return "(không lấy được title)"


def _format_selenium_error(
    page_name: str,
    element_name: str,
    locator_type: str,
    locator_value: str,
    url: str,
    exception_type: str,
    message: str,
) -> str:

    return (
        "[SELENIUM ERROR]\n"
        f"page={page_name}\n"
        f"element={element_name}\n"
        f"locator={locator_type}:{locator_value}\n"
        f"url={url}\n"
        f"exception_type={exception_type}\n"
        f"message={message}"
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
        value = " ".join(
            value.split()
        )

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

    expected_lines = _split_compare_lines(
        expected
    )

    actual_lines = _split_compare_lines(
        actual
    )

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
        if pairs
        and all(
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

    expected_lines = _split_compare_lines(
        expected
    )

    actual_lines = _split_compare_lines(
        actual
    )

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
                and expected_compare
                == actual_compare
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

            used_actual_indexes.add(
                matched_index
            )

            pairs.append(
                {
                    "index": len(pairs) + 1,
                    "expected": expected_line,
                    "actual": actual_lines[
                        matched_index
                    ],
                    "status": "PASS",
                }
            )

    for index, actual_line in enumerate(
        actual_lines
    ):

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
        if pairs
        and all(
            pair["status"] == "PASS"
            for pair in pairs
        )
        else "FAILED"
    )

    return status, pairs


# =========================================================
# TABLE
# =========================================================

def _split_table_line(line: str):

    if "\t" in line:
        return [
            cell.strip()
            for cell in line.split("\t")
        ]

    try:
        cells = next(
            csv.reader(
                StringIO(line)
            )
        )

    except Exception:
        cells = [line]

    return [
        cell.strip()
        for cell in cells
    ]


def _table_matrix(text: str):

    rows = []

    for line in (
        text or ""
    ).splitlines():

        if not line.strip():
            continue

        cells = _split_table_line(
            line
        )

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
        return "\n".join(
            table_rows
        )

    lines = [
        line.strip()
        for line in (
            element.text or ""
        ).splitlines()
        if line.strip()
    ]

    return "\t".join(lines)


def _compare_table_rows(
    expected: str,
    actual: str,
    trim: bool = True,
    case_sensitive: bool = True,
):

    expected_rows = _table_matrix(
        expected
    )

    actual_rows = _table_matrix(
        actual
    )

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

        for cell_index in range(
            max_cells
        ):

            expected_cell = (
                expected_cells[cell_index]
                if cell_index < len(
                    expected_cells
                )
                else ""
            )

            actual_cell = (
                actual_cells[cell_index]
                if cell_index < len(
                    actual_cells
                )
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
                    expected_compare
                    == actual_compare
                    and expected_cell
                    and actual_cell
                )
                else "FAIL"
            )

            pairs.append(
                {
                    "index": (
                        f"R{row_index + 1}"
                        f"C{cell_index + 1}"
                    ),
                    "expected": expected_cell,
                    "actual": actual_cell,
                    "status": pair_status,
                }
            )

    status = (
        "PASSED"
        if pairs
        and all(
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

    expected_lines = _split_compare_lines(
        expected
    )

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
            and expected_compare
            in actual_compare
        )

        pairs.append(
            {
                "index": index,
                "expected": expected_line,
                "actual": (
                    expected_line
                    if matched
                    else actual
                ),
                "status": (
                    "PASS"
                    if matched
                    else "FAIL"
                ),
            }
        )

    status = (
        "PASSED"
        if pairs
        and all(
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
        re.search(
            r"\d+",
            actual or "",
        )
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
        (
            "http://",
            "https://",
        )
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

def _login_form_visible(driver, timeout: float = 3):

    try:

        WebDriverWait(
            driver,
            timeout,
        ).until(
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


def _on_login_url(driver) -> bool:
    """
    Kiểm tra URL hiện tại có phải trang login hay không. Đáng tin cậy
    hơn nhiều so với việc kiểm tra form login còn hiển thị hay không,
    vì trong SPA form login có thể vẫn còn trong DOM một lúc sau khi
    đăng nhập thành công.
    """

    try:
        return "/login" in (driver.current_url or "").lower()
    except Exception:
        return False


def _read_login_error_text(driver) -> str:
    """
    Cố gắng đọc thông báo lỗi đăng nhập (sai email/mật khẩu) nếu có,
    để báo lỗi rõ ràng ngay thay vì để timeout mơ hồ ở bước sau.
    """

    selectors = [
        ".ant-form-item-explain-error",
        ".ant-message-error",
        "[role='alert']",
        ".error-message",
    ]

    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector,
            )

            for element in elements:

                if element.is_displayed():

                    text = (
                        element.text or ""
                    ).strip()

                    if text:
                        return text

        except Exception:
            continue

    return ""


def _ensure_logged_in(
    driver,
    target_url: str,
):

    if not _login_form_visible(
        driver
    ):
        return

    logger.info(
        "[LOGIN] Website yêu cầu đăng nhập."
    )

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

    password = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='password'], "
                "input[name='password']",
            )
        )
    )

    email.clear()

    email.send_keys(
        Config.TEST_EMAIL
    )

    password.clear()

    password.send_keys(
        Config.TEST_PASSWORD
    )

    submit = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit'], "
                "input[type='submit']",
            )
        )
    )

    submit.click()

    # =======================================================
    # QUAN TRỌNG: chờ ĐÚNG tín hiệu login thành công là URL rời
    # khỏi "/login". KHÔNG được driver.get(target_url) trước khi
    # xác nhận điều này, vì request login (thường là async/AJAX)
    # có thể chưa hoàn tất -> điều hướng sớm sẽ hủy ngang phiên
    # đăng nhập, khiến mọi trang sau đó bị bounce về lại /login.
    # =======================================================

    try:

        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            lambda browser: not _on_login_url(browser)
        )

    except TimeoutException as error:

        login_error_text = _read_login_error_text(driver)

        if login_error_text:

            raise SeleniumTestError(
                "LoginFailedException: Đăng nhập thất bại.\n"
                f"Thông báo từ trang: {login_error_text}\n"
                f"URL={_safe_current_url(driver)}"
            ) from error

        raise SeleniumTestError(
            "TimeoutException: Đăng nhập không hoàn tất sau "
            f"{Config.EXPLICIT_WAIT} giây (URL vẫn ở trang /login).\n"
            f"URL={_safe_current_url(driver)}\n"
            "Kiểm tra lại email/password trong Config, hoặc trang "
            "login có yêu cầu captcha/2FA không."
        ) from error

    # Chờ document + app render sau khi rời trang login
    _wait_app_rendered(driver)

    # Nếu sau login không tự về đúng target_url thì điều hướng tới
    if target_url and target_url.rstrip("/") not in (driver.current_url or ""):

        driver.get(
            target_url
        )

    # Chờ document + app render tại trang đích
    _wait_app_rendered(driver)


# =========================================================
# APP RENDER WAIT (React / Ant Design hydration)
# =========================================================

def _wait_app_rendered(driver, timeout: float = None):
    """
    Chờ document ready VÀ có ít nhất vài phần tử con trong <body>.

    Ant Design / React render động sau khi document.readyState đã là
    "complete", nên chỉ chờ readyState là chưa đủ - cần chờ DOM có
    nội dung thật sự trước khi tìm element cụ thể.
    """

    timeout = timeout or Config.EXPLICIT_WAIT

    try:

        WebDriverWait(driver, timeout).until(
            lambda browser:
                browser.execute_script(
                    "return document.readyState"
                )
                == "complete"
        )

    except Exception:
        pass

    try:

        WebDriverWait(driver, timeout).until(
            lambda browser: len(
                browser.find_elements(
                    By.CSS_SELECTOR,
                    "body *",
                )
            )
            > 5
        )

    except Exception:
        pass


# =========================================================
# BOOKING FORM AUTO-OPEN (self-healing, generic theo page_key)
# =========================================================

_BOOKING_FORM_TRIGGER_TEXTS = (
    "tạo đơn thuê",
    "thêm đặt xe",
    "tạo đặt xe",
    "tạo mới",
    "thêm mới",
)


def _try_open_booking_form(driver) -> bool:
    """
    Trang Quản lý đặt xe (plt_booking) chỉ hiển thị các field
    carId/customerId/status/paymentMethod... trên route con
    (VD: /bookings/new) sau khi bấm nút mở form, KHÔNG có sẵn trên
    trang danh sách. Hàm này tìm và click nút mở form đó dựa trên
    text của button (generic, không hard-code theo element_key).

    Trả về True nếu tìm và click được nút, False nếu không tìm thấy.
    """

    try:

        clickable = driver.find_elements(
            By.CSS_SELECTOR,
            "button, a, [role='button']",
        )

    except Exception:
        return False

    target = None

    for candidate in clickable:

        try:

            if not candidate.is_displayed():
                continue

            text = (
                candidate.text or ""
            ).strip().lower()

            if any(
                trigger in text
                for trigger in _BOOKING_FORM_TRIGGER_TEXTS
            ):
                target = candidate
                break

        except Exception:
            continue

    if target is None:
        return False

    logger.info(
        "[BOOKING FORM] Không thấy field trên trang danh sách, "
        "thử mở form bằng nút: %r",
        (target.text or "").strip(),
    )

    try:

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            target,
        )

    except Exception:
        pass

    clicked = False

    try:
        target.click()
        clicked = True
    except Exception:

        try:
            driver.execute_script(
                "arguments[0].click();",
                target,
            )
            clicked = True
        except Exception:
            clicked = False

    if not clicked:
        return False

    _wait_app_rendered(driver)

    return True


# =========================================================
# SAFE ELEMENT FINDER (core fix)
# =========================================================

def _wait_find_element(
    driver,
    locator_type: str,
    locator_value: str,
    page_name: str = "",
    element_name: str = "",
    element_key: str = "",
    page_key: str = "",
    timeout: float = None,
    require_visible: bool = True,
    _retried_after_form_open: bool = False,
):
    """
    Tìm element an toàn, có wait rõ ràng (không dùng sleep) và khi
    fail luôn ném SeleniumTestError với message sạch, kèm URL/title/
    login-state để debug - thay vì để lộ stacktrace chromedriver.

    Với page_key="plt_booking": nếu lần tìm đầu tiên timeout, tự
    động thử mở form "Tạo đơn thuê" (các field booking chỉ tồn tại
    trên route con /bookings/new) rồi thử lại một lần trước khi báo
    lỗi thật.
    """

    timeout = timeout or Config.EXPLICIT_WAIT

    by = _by(locator_type)

    logger.info(
        "[FIND] page=%s element=%s locator=%s:%s timeout=%s",
        page_name,
        element_name or element_key,
        locator_type,
        locator_value,
        timeout,
    )

    wait = WebDriverWait(driver, timeout)

    try:

        element = wait.until(
            EC.presence_of_element_located(
                (by, locator_value)
            )
        )

    except TimeoutException as error:

        # ---------------------------------------------------
        # Self-healing: thử mở form booking rồi tìm lại 1 lần
        # ---------------------------------------------------

        if (
            page_key == "plt_booking"
            and not _retried_after_form_open
        ):

            opened = _try_open_booking_form(driver)

            if opened:

                return _wait_find_element(
                    driver=driver,
                    locator_type=locator_type,
                    locator_value=locator_value,
                    page_name=page_name,
                    element_name=element_name,
                    element_key=element_key,
                    page_key=page_key,
                    timeout=timeout,
                    require_visible=require_visible,
                    _retried_after_form_open=True,
                )

        current_url = _safe_current_url(driver)
        title = _safe_title(driver)
        login_visible = _login_form_visible(driver, timeout=1)

        detail_message = (
            f"Không tìm thấy element sau {timeout} giây."
        )

        logger.error(
            _format_selenium_error(
                page_name,
                element_name or element_key,
                locator_type,
                locator_value,
                current_url,
                "TimeoutException",
                detail_message,
            )
        )

        raise SeleniumTestError(
            "TimeoutException: "
            f"Không tìm thấy element \"{element_name or element_key}\"\n"
            f"locator={locator_type}:{locator_value}\n"
            f"URL={current_url}\n"
            f"page_title={title}\n"
            f"login_page_visible={login_visible}"
        ) from error

    except NoSuchElementException as error:

        current_url = _safe_current_url(driver)
        title = _safe_title(driver)

        logger.error(
            _format_selenium_error(
                page_name,
                element_name or element_key,
                locator_type,
                locator_value,
                current_url,
                "NoSuchElementException",
                _clean_exception_message(error),
            )
        )

        raise SeleniumTestError(
            "NoSuchElementException: "
            f"Không tồn tại element \"{element_name or element_key}\"\n"
            f"locator={locator_type}:{locator_value}\n"
            f"URL={current_url}\n"
            f"page_title={title}"
        ) from error

    except SessionNotCreatedException as error:

        raise SeleniumTestError(
            "SessionNotCreatedException: "
            "Chrome session không được tạo hoặc đã chết trước khi "
            "tìm được element. Kiểm tra lại phiên bản Chrome/ChromeDriver.\n"
            f"chi_tiet={_clean_exception_message(error)}"
        ) from error

    except WebDriverException as error:

        current_url = _safe_current_url(driver)
        title = _safe_title(driver)
        clean_message = _clean_exception_message(error)

        logger.error(
            _format_selenium_error(
                page_name,
                element_name or element_key,
                locator_type,
                locator_value,
                current_url,
                "WebDriverException",
                clean_message,
            )
        )

        raise SeleniumTestError(
            "WebDriverException: "
            f"Lỗi khi tìm element \"{element_name or element_key}\"\n"
            f"locator={locator_type}:{locator_value}\n"
            f"URL={current_url}\n"
            f"page_title={title}\n"
            f"chi_tiet={clean_message}"
        ) from error

    if require_visible:

        try:

            wait.until(
                EC.visibility_of(element)
            )

        except Exception:

            logger.warning(
                "[FIND] Element tồn tại nhưng chưa visible: "
                "page=%s element=%s locator=%s:%s",
                page_name,
                element_name or element_key,
                locator_type,
                locator_value,
            )

    return element


# =========================================================
# VEHICLE CATALOG
# =========================================================

def _active_brand_names_from_catalog(
    driver
):

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
            + "/following::*"
            "[@role='row'][position()>1]",
        )

    active_names = []

    for row in rows:

        row_text = (
            row.text or ""
        ).strip()

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
            and brand_name
            not in active_names
        ):
            active_names.append(
                brand_name
            )

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
# BOOKING
# =========================================================

def _is_booking_page(
    module: str,
    page_key: str,
) -> bool:

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

    return (
        module == "dropdown"
        and page_key == "plt_booking"
    )


def _booking_dropdown_log_name(
    element_key: str,
    element_name: str,
) -> str:

    if element_name:
        return element_name

    if element_key:
        return element_key

    return "Booking Dropdown"


# =========================================================
# WAIT ANT DESIGN OPTIONS
# =========================================================

def _get_visible_booking_options(
    driver
):
    """
    Ant Design render dropdown ở portal (thường append vào cuối
    <body>), KHÔNG nằm trong DOM con của input. Vì vậy luôn tìm bằng
    driver.find_elements(...) (toàn document), không dùng
    element.find_elements(...).
    """

    selectors = [

        # Ant Design
        (
            ".ant-select-dropdown:not("
            ".ant-select-dropdown-hidden"
            ") "
            ".ant-select-item-option-content"
        ),

        # Ant Design role option
        (
            ".ant-select-dropdown:not("
            ".ant-select-dropdown-hidden"
            ") "
            "[role='option']"
        ),

        # Generic listbox
        (
            "[role='listbox']:not("
            "[aria-hidden='true'"
            "]) "
            "[role='option']"
        ),

        # Generic option
        (
            "[role='option']"
        ),
    ]

    for selector in selectors:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            selector,
        )

        visible = []

        for element in elements:

            try:

                if element.is_displayed():

                    text = (
                        element.text or ""
                    ).strip()

                    if text:
                        visible.append(
                            element
                        )

            except Exception:
                continue

        if visible:
            return visible

    return []


# =========================================================
# READ BOOKING DROPDOWN
# =========================================================

def _read_booking_dropdown(
    driver,
    element,
):

    wait = WebDriverWait(
        driver,
        Config.EXPLICIT_WAIT,
    )

    element_id = (
        element.get_attribute("id")
        or ""
    )

    logger.info(
        "[BOOKING DROPDOWN] "
        "Reading id=%s",
        element_id,
    )

    # -----------------------------------------------------
    # Scroll
    # -----------------------------------------------------

    try:

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                behavior: 'instant',
                block: 'center'
            });
            """,
            element,
        )

    except Exception:
        pass

    # -----------------------------------------------------
    # Nếu element là input
    # -----------------------------------------------------

    target = element

    try:

        if (
            element.tag_name or ""
        ).lower() != "input":

            nested = element.find_elements(
                By.CSS_SELECTOR,
                "input[role='combobox']",
            )

            if nested:
                target = nested[0]

    except Exception:
        pass

    # -----------------------------------------------------
    # Click
    # -----------------------------------------------------

    clicked = False

    try:

        wait.until(
            EC.visibility_of(target)
        )

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    ".",
                )
            )
        )

        target.click()

        clicked = True

    except (
        ElementClickInterceptedException,
        StaleElementReferenceException,
        TimeoutException,
        WebDriverException,
    ) as error:

        logger.warning(
            "[BOOKING DROPDOWN] "
            "Normal click failed (%s): %s",
            type(error).__name__,
            _clean_exception_message(error),
        )

    # -----------------------------------------------------
    # JS click fallback
    # -----------------------------------------------------

    if not clicked:

        try:

            driver.execute_script(
                "arguments[0].click();",
                target,
            )

            clicked = True

        except Exception as error:

            logger.warning(
                "[BOOKING DROPDOWN] "
                "JS click failed: %s",
                _clean_exception_message(error),
            )

    if not clicked:

        raise SeleniumTestError(
            "ElementClickInterceptedException: "
            "Không click được dropdown "
            f"id={element_id}\n"
            f"URL={_safe_current_url(driver)}"
        )

    # -----------------------------------------------------
    # Chờ option (KHÔNG dùng sleep)
    # -----------------------------------------------------

    try:

        options = wait.until(
            lambda browser:
                _get_visible_booking_options(
                    browser
                )
                or False
        )

    except TimeoutException as error:

        try:
            capture_screenshot(
                driver,
                f"booking_dropdown_{element_id}",
            )
        except Exception:
            pass

        raise SeleniumTestError(
            "TimeoutException: "
            "Dropdown đã được click nhưng không thấy option xuất hiện "
            f"sau {Config.EXPLICIT_WAIT} giây.\n"
            f"id={element_id}\n"
            f"URL={_safe_current_url(driver)}\n"
            "Gợi ý: option có thể được load bằng API - kiểm tra "
            "Network tab xem API có trả dữ liệu không."
        ) from error

    # -----------------------------------------------------
    # Đọc text
    # -----------------------------------------------------

    values = []

    for option in options:

        try:

            text = (
                option.text or ""
            ).strip()

            if (
                text
                and text not in values
            ):
                values.append(text)

        except StaleElementReferenceException:
            continue
        except Exception:
            continue

    # -----------------------------------------------------
    # Không có value
    # -----------------------------------------------------

    if not values:

        raise SeleniumTestError(
            "NoSuchElementException: "
            "Dropdown mở nhưng không đọc được option nào (option "
            "rỗng hoặc chỉ có khoảng trắng).\n"
            f"id={element_id}"
        )

    logger.info(
        "[BOOKING DROPDOWN] "
        "id=%s -> %s options",
        element_id,
        len(values),
    )

    # -----------------------------------------------------
    # Close dropdown
    # -----------------------------------------------------

    try:

        driver.execute_script(
            """
            document.body.click();
            """
        )

    except Exception:
        pass

    return "\n".join(values)


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
    # Navigation
    # -----------------------------------------------------

    if action_type == "click_url_contains":

        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            EC.element_to_be_clickable(
                (
                    _by("css"),
                    element.get_attribute(
                        "data-testid"
                    )
                    or "#"
                )
            )
        )

        element.click()

        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            EC.url_contains(
                target_path
            )
        )

        return driver.current_url

    if action_type == "deep_link_url_contains":

        WebDriverWait(
            driver,
            Config.EXPLICIT_WAIT,
        ).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "main",
                )
            )
        )

        return driver.current_url

    # -----------------------------------------------------
    # Booking Dropdown
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
    # Generic Dropdown
    # -----------------------------------------------------

    if module == "dropdown":

        # Native select
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

        # Ant Design
        try:

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    behavior: 'instant',
                    block: 'center'
                });
                """,
                element,
            )

        except Exception:
            pass

        try:
            element.click()

        except Exception:

            try:

                nested_input = element.find_element(
                    By.CSS_SELECTOR,
                    "input[role='combobox']",
                )

                nested_input.click()

            except Exception:
                pass

        try:

            WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
            ).until(
                lambda browser:
                    _get_visible_booking_options(
                        browser
                    )
                    or False
            )

        except Exception:
            pass

        option_elements = (
            _get_visible_booking_options(
                driver
            )
        )

        values = []

        for option in option_elements:

            try:

                text = (
                    option.text or ""
                ).strip()

                if (
                    text
                    and text not in values
                ):
                    values.append(text)

            except Exception:
                continue

        return "\n".join(values)

    # -----------------------------------------------------
    # Image
    # -----------------------------------------------------

    if module == "image":

        return (
            element.get_attribute("alt")
            or element.get_attribute("src")
            or "visible"
        )

    # -----------------------------------------------------
    # Table
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
    # Label / Text
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
    driver=None,
):

    own_driver = False
    if driver is None:
        own_driver = True

    repository = TestResultRepository()

    screenshot_path = ""
    error_message = ""

    actual = ""
    status = "ERROR"
    message = ""

    pairs = []

    try:

        # =================================================
        # LOG
        # =================================================

        if worker:

            worker.log_signal.emit(
                f"[{module.upper()}] "
                f"Mở trang kiểm thử: {page_name}"
            )

            worker.progress_signal.emit(
                10
            )

        logger.info(
            "[%s] Opening: %s",
            module.upper(),
            url,
        )

        # =================================================
        # CREATE DRIVER
        # =================================================

        if driver is None:
            driver = DriverFactory.create_driver(
                headless=headless,
                keep_session=True,
            )

        if worker:

            worker.log_signal.emit(
                "[SELENIUM] Chrome đã khởi động."
            )

            worker.progress_signal.emit(
                25
            )

        # =================================================
        # OPEN URL
        # =================================================

        current_url = driver.current_url or ""
        if current_url.rstrip("/") != url.rstrip("/"):
            driver.get(url)

        # Chờ document + app render (React/Ant Design hydration)
        _wait_app_rendered(driver)

        # =================================================
        # LOGIN
        # =================================================

        _ensure_logged_in(
            driver,
            url,
        )

        # =================================================
        # WAIT AFTER LOGIN / PAGE LOAD
        # =================================================

        _wait_app_rendered(driver)

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
                f"Đang tìm element: "
                f"{element_name}"
            )

            worker.progress_signal.emit(
                50
            )

        logger.info(
            "[%s] locator=%s %s",
            module.upper(),
            locator_type,
            locator_value,
        )

        # =================================================
        # WAIT + FIND ELEMENT (an toàn, không sleep,
        # exception rõ ràng nếu fail)
        # =================================================

        element = _wait_find_element(
            driver=driver,
            locator_type=locator_type,
            locator_value=locator_value,
            page_name=page_name,
            element_name=element_name,
            element_key=element_key,
            page_key=page_key,
            timeout=Config.EXPLICIT_WAIT,
        )

        # =================================================
        # VISUAL HIGHLIGHT
        # =================================================

        if step_delay > 0:

            try:

                driver.execute_script(
                    """
                    arguments[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });

                    arguments[0].style.outline =
                        '3px solid #ef4444';

                    arguments[0].style.outlineOffset =
                        '4px';
                    """,
                    element,
                )

            except Exception:
                pass

            time.sleep(
                step_delay
            )

        # =================================================
        # SPECIAL CASE
        # =================================================

        auto_catalog_dropdown = (
            _is_catalog_brand_dropdown(
                module,
                page_key,
                element_key,
            )
        )

        booking_dropdown = (
            _is_booking_dropdown(
                module,
                page_key,
                element_key,
            )
        )

        # =================================================
        # BOOKING LOG
        # =================================================

        if booking_dropdown:

            if worker:

                worker.log_signal.emit(
                    "[BOOKING] "
                    f"Dropdown: {element_name}"
                )

        # =================================================
        # VEHICLE CATALOG EXPECTED
        # =================================================

        if auto_catalog_dropdown:

            active_brands = (
                _active_brand_names_from_catalog(
                    driver
                )
            )

            if not active_brands:

                raise SeleniumTestError(
                    "NoSuchElementException: "
                    "Không đọc được danh sách "
                    "Hãng đang hoạt động từ bảng Hãng xe."
                )

            expected = "\n".join(
                active_brands
            )

            expected_result = expected

            if worker:

                worker.log_signal.emit(
                    "[DROPDOWN] "
                    f"Tự lấy {len(active_brands)} "
                    "Hãng đang hoạt động làm Expected."
                )

        # =================================================
        # READ ACTUAL
        # =================================================

        actual = _read_actual(
            driver=driver,
            element=element,
            module=module,
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

        if auto_catalog_dropdown:

            status, pairs = (
                _compare_unordered_lines(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        elif action_type in (
            "click_url_contains",
            "deep_link_url_contains",
        ):

            status = (
                _compare_navigation_expected(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        elif action_type == "contains_all":

            status, pairs = (
                _compare_contains_all(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        elif action_type == "contains_all_has_number":

            status, pairs = (
                _compare_contains_all_has_number(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        elif module in (
            "dropdown",
            "menu",
        ):

            status, pairs = (
                _compare_line_pairs(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

        elif module == "table":

            status, pairs = (
                _compare_table_rows(
                    expected,
                    actual,
                    trim=trim,
                    case_sensitive=case_sensitive,
                )
            )

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
                if (
                    actual_compare
                    == expected_compare
                )
                else "FAILED"
            )

        # =================================================
        # MESSAGE
        # =================================================

        if status == "PASSED":

            if auto_catalog_dropdown:

                message = (
                    "Dropdown đồng bộ với "
                    "các Hãng đang hoạt động."
                )

            elif booking_dropdown:

                message = (
                    "Dropdown Booking khớp "
                    "với Expected."
                )

            else:

                message = (
                    "Expected khớp Actual."
                )

        elif auto_catalog_dropdown:

            message = (
                "Dropdown chưa đồng bộ với "
                "danh sách Hãng đang hoạt động."
            )

        elif booking_dropdown:

            message = (
                "Dropdown Booking chưa khớp "
                "với Expected."
            )

        elif not (
            expected or ""
        ).strip():

            message = (
                "Expected Result đang trống."
            )

        else:

            message = (
                "Expected khác Actual."
            )

        # =================================================
        # SCREENSHOT FAILED
        # =================================================

        if (
            status != "PASSED"
            and driver
        ):

            try:

                screenshot_path = (
                    capture_screenshot(
                        driver,
                        case_id
                        or element_key
                        or module,
                    )
                )

            except Exception:
                screenshot_path = ""

    # =====================================================
    # ERROR - đã phân loại, message sạch (không có
    # stacktrace chromedriver)
    # =====================================================

    except SeleniumTestError as error:

        actual = f"ERROR: {error}"

        status = "ERROR"

        message = str(error).split("\n", 1)[0]

        error_message = str(error)

        logger.error(
            "[%s] page=%s element=%s\n%s",
            module.upper(),
            page_name,
            element_name,
            error_message,
        )

        if driver:

            try:

                screenshot_path = (
                    capture_screenshot(
                        driver,
                        case_id
                        or element_key
                        or module,
                    )
                )

            except Exception:
                screenshot_path = ""

    except (
        TimeoutException,
        NoSuchElementException,
        StaleElementReferenceException,
        ElementClickInterceptedException,
        SessionNotCreatedException,
        WebDriverException,
    ) as error:

        exception_type = _classify_exception(error)
        clean_message = _clean_exception_message(error)
        current_url = _safe_current_url(driver) if driver else ""
        title = _safe_title(driver) if driver else ""

        formatted = _format_selenium_error(
            page_name,
            element_name,
            locator_type,
            locator_value,
            current_url,
            exception_type,
            clean_message,
        )

        logger.error(formatted)

        actual = (
            f"ERROR: {exception_type}: {clean_message}\n"
            f"URL={current_url}\n"
            f"page_title={title}"
        )

        status = "ERROR"

        message = (
            f"{exception_type} khi thao tác với "
            f"element \"{element_name or element_key}\"."
        )

        error_message = (
            f"{exception_type}: {clean_message}"
        )

        if driver:

            try:

                screenshot_path = (
                    capture_screenshot(
                        driver,
                        case_id
                        or element_key
                        or module,
                    )
                )

            except Exception:
                screenshot_path = ""

    except Exception as error:

        clean_message = _clean_exception_message(error)

        actual = (
            f"ERROR: {type(error).__name__}: {clean_message}"
        )

        status = "ERROR"

        message = (
            "Lỗi không xác định trong quá trình test."
        )

        error_message = clean_message

        logger.exception(
            "[%s] UNEXPECTED ERROR page=%s element=%s",
            module.upper(),
            page_name,
            element_name,
        )

        if driver:

            try:

                screenshot_path = (
                    capture_screenshot(
                        driver,
                        case_id
                        or element_key
                        or module,
                    )
                )

            except Exception:
                screenshot_path = ""

    # =====================================================
    # FINALLY
    # =====================================================

    finally:

        if driver and own_driver:

            if close_delay > 0:

                time.sleep(
                    close_delay
                )

            DriverFactory.quit_driver(
                driver
            )

    # =====================================================
    # RESULT
    # =====================================================

    effective_case_id = (
        case_id
        or (
            f"{module}:"
            f"{page_key}:"
            f"{element_key}"
        )
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
        "auto_expected": (
            _is_catalog_brand_dropdown(
                module,
                page_key,
                element_key,
            )
        ),
    }

    # =====================================================
    # SAVE
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
        "[%s] page=%s element=%s "
        "expected=%s actual=%s status=%s",
        module.upper(),
        page_name,
        element_name,
        expected,
        actual,
        status,
    )

    # =====================================================
    # WORKER
    # =====================================================

    if worker:

        worker.progress_signal.emit(
            100
        )

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


# =========================================================
# PYTEST PROTECTION
# =========================================================

run_label_text_test.__test__ = False
run_text_dropdown_test.__test__ = False