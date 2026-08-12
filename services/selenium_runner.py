from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal, Slot


@dataclass
class RunnerRequest:
    url: str
    locator_type: str
    locator_value: str
    test_type: str
    expected_lines: List[str]
    trim_whitespace: bool = True
    case_sensitive: bool = False
    check_order: bool = True
    timeout: int = 10
    show_browser: bool = True
    require_login: bool = False
    login_wait_seconds: int = 180
    profile_dir: str = ""


def locator_by(By, locator_type):
    """Map tên loại locator lưu trong data_store sang hằng số Selenium `By`."""
    mapping = {
        "ID": By.ID,
        "NAME": By.NAME,
        "CSS": By.CSS_SELECTOR,
        "XPATH": By.XPATH,
        "CLASS_NAME": By.CLASS_NAME,
        "TAG_NAME": By.TAG_NAME,
        "LINK_TEXT": By.LINK_TEXT,
        "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
    }
    return mapping.get(locator_type, By.CSS_SELECTOR)


def extract_table_rows(element):
    """Đọc từng dòng <tr> của một bảng thành chuỗi 'cell | cell | ...'."""
    rows = element.find_elements("css selector", "tr")
    output = []
    for row in rows:
        cells = row.find_elements("css selector", "th,td")
        if cells:
            output.append(" | ".join(cell.text for cell in cells))
    return output


def _xpath_literal(value: str) -> str:
    """Escape chuỗi để dùng an toàn trong XPath."""
    value = str(value)
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def try_choose_option(element, text, timeout=12):
    """Chọn option theo text, hỗ trợ <select> và Ant Design Select.

    Fleet Console dùng Ant Design Select. Option được render ra portal bên ngoài
    modal nên không thể tìm bằng ``element.find_elements``. Hàm này mở combobox,
    lọc theo text, đợi dropdown *đang hiển thị* rồi click đúng option.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select, WebDriverWait

    # 1) Native <select>
    try:
        if (element.tag_name or "").lower() == "select":
            Select(element).select_by_visible_text(text)
            return True
    except Exception:
        pass

    driver = element.parent
    wait = WebDriverWait(driver, timeout)
    target = str(text or "").strip()
    if not target:
        return False

    # 2) Ant Design / custom combobox
    try:
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center', inline:'nearest'});",
                element,
            )
        except Exception:
            pass

        # Click để mở dropdown. Dùng JS fallback nếu animation/overlay chặn click.
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)

        # Nếu là input searchable của AntD, gõ tên hãng để lọc option.
        try:
            if (element.tag_name or "").lower() == "input":
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(target)
        except Exception:
            pass

        literal = _xpath_literal(target)
        option_xpath = (
            "//div[contains(@class,'ant-select-dropdown') "
            "and not(contains(@class,'ant-select-dropdown-hidden'))]"
            "//div[contains(@class,'ant-select-item-option') "
            "and not(contains(@class,'ant-select-item-option-disabled'))]"
            f"[.//*[normalize-space()={literal}] or normalize-space()={literal}]"
        )

        # Một số build AntD dùng role=option rõ ràng hơn.
        role_xpath = (
            "//*[@role='option' and not(@aria-disabled='true')]"
            f"[.//*[normalize-space()={literal}] or normalize-space()={literal}]"
        )

        option = None
        for xpath in (option_xpath, role_xpath):
            try:
                option = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
                if option:
                    break
            except Exception:
                continue

        if option is None:
            # Fallback: lấy các option AntD đang hiển thị và so text chính xác.
            visible_options = driver.find_elements(
                By.CSS_SELECTOR,
                ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                ".ant-select-item-option",
            )
            needle = target.casefold()
            for candidate in visible_options:
                if candidate.is_displayed() and (candidate.text or "").strip().casefold() == needle:
                    option = candidate
                    break

        if option is None:
            # Đóng dropdown để không chặn nút submit.
            try:
                element.send_keys(Keys.ESCAPE)
            except Exception:
                pass
            return False

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", option)
        except Exception:
            pass
        try:
            option.click()
        except Exception:
            driver.execute_script("arguments[0].click();", option)

        # Đợi popup đóng. Nếu AntD giữ popup do animation, ESC là fallback an toàn.
        try:
            wait.until(
                lambda d: not any(
                    x.is_displayed()
                    for x in d.find_elements(
                        By.CSS_SELECTOR,
                        ".ant-select-dropdown:not(.ant-select-dropdown-hidden)",
                    )
                )
            )
        except Exception:
            try:
                element.send_keys(Keys.ESCAPE)
            except Exception:
                pass

        return True
    except Exception:
        try:
            element.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return False


def click_safely(driver, element):
    """Click element và xử lý trường hợp AntD popup/animation chặn click."""
    from selenium.webdriver.common.keys import Keys

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'nearest'});",
            element,
        )
    except Exception:
        pass

    # Đóng popup select còn sót trước khi submit.
    try:
        active = driver.switch_to.active_element
        active.send_keys(Keys.ESCAPE)
    except Exception:
        pass

    try:
        element.click()
        return
    except Exception:
        # JS click là fallback cho ElementClickInterceptedException do overlay animation.
        driver.execute_script("arguments[0].click();", element)


def cleanup_row(driver, table_element, value_name):
    """Best-effort: tìm dòng vừa tạo trong bảng và bấm nút Xóa để dọn dữ liệu test."""
    try:
        rows = table_element.find_elements("css selector", "tr")
        target = None
        needle = value_name.strip().lower()
        for row in rows:
            if needle and needle in (row.text or "").strip().lower():
                target = row
                break
        if target is None:
            return False

        delete_btn = None
        for candidate in target.find_elements(
            "xpath", ".//button[contains(.,'Xóa') or contains(.,'Delete')]"
        ):
            delete_btn = candidate
            break
        if delete_btn is None:
            return False

        delete_btn.click()
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except Exception:
            pass
        return True
    except Exception:
        return False


def normalize_text(value: str, trim_whitespace=True, case_sensitive=False):
    value = "" if value is None else str(value)
    if trim_whitespace:
        value = " ".join(value.split()).strip()
    if not case_sensitive:
        value = value.lower()
    return value


def friendly_selenium_error(exc):
    """Không đẩy nguyên stacktrace ChromeDriver lên UI."""
    name = exc.__class__.__name__
    raw = str(exc or "").strip()
    first_line = raw.splitlines()[0].strip() if raw else ""

    if "LOGIN_FAILED:" in raw:
        return raw.split("LOGIN_FAILED:", 1)[1].strip()
    if "LOGIN_TIMEOUT:" in raw:
        return raw.split("LOGIN_TIMEOUT:", 1)[1].strip()
    if "LOGIN_REQUIRED:" in raw:
        return raw.split("LOGIN_REQUIRED:", 1)[1].strip()
    if name == "TimeoutException":
        return "Hết thời gian chờ: không tìm thấy element với locator đã lưu."
    if name in {"NoSuchDriverException", "WebDriverException"} and "driver" in raw.lower():
        return "Không khởi động được ChromeDriver. Kiểm tra Chrome và Selenium rồi chạy lại."
    if name == "SessionNotCreatedException":
        return "Không tạo được phiên Chrome. Hãy cập nhật Chrome/Selenium hoặc đóng ChromeDriver cũ."
    if "net::ERR_" in raw:
        return "Chrome không mở được URL kiểm thử. Kiểm tra Internet hoặc địa chỉ trang."
    if first_line:
        return f"Selenium gặp lỗi: {first_line[:220]}"
    return f"Selenium gặp lỗi ({name})."




PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CREDENTIAL_FILE = PROJECT_ROOT / ".autotest.env"


def _read_simple_env(path: Path) -> Dict[str, str]:
    """Đọc file KEY=VALUE đơn giản, không cần thêm dependency python-dotenv."""
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    except Exception:
        return {}
    return values


def load_autotest_credentials() -> Tuple[str, str]:
    """Lấy tài khoản test từ biến môi trường hoặc .autotest.env cục bộ.

    Ưu tiên biến môi trường để CI/CD có thể truyền secret mà không tạo file.
    File .autotest.env đã được .gitignore nên `git add .` không đẩy mật khẩu.
    """
    local = _read_simple_env(LOCAL_CREDENTIAL_FILE)
    email = (
        os.getenv("AUTOTEST_EMAIL")
        or os.getenv("TEST_EMAIL")
        or local.get("AUTOTEST_EMAIL")
        or local.get("TEST_EMAIL")
        or ""
    ).strip()
    password = (
        os.getenv("AUTOTEST_PASSWORD")
        or os.getenv("TEST_PASSWORD")
        or local.get("AUTOTEST_PASSWORD")
        or local.get("TEST_PASSWORD")
        or ""
    )
    return email, password


def _first_visible(driver, candidates):
    """Trả về element visible đầu tiên trong danh sách locator."""
    for by, value in candidates:
        try:
            for element in driver.find_elements(by, value):
                if element.is_displayed():
                    return element
        except Exception:
            continue
    return None


def submit_login_form(driver, email: str, password: str, timeout: int = 12, progress=None):
    """Tự điền form đăng nhập Fleet Console bằng locator có fallback.

    Không log email/mật khẩu ra UI. Hàm chỉ submit form; việc xác nhận login thành
    công do `open_target_with_login` thực hiện bằng URL/trạng thái trang.
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    if not email or not password:
        return False

    email_candidates = [
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[name='email']"),
        (By.CSS_SELECTOR, "input[autocomplete='email']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Email')]/following::input[1]"),
    ]
    password_candidates = [
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        (By.XPATH, "//label[contains(normalize-space(.),'Mật khẩu')]/following::input[1]"),
    ]
    button_candidates = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(normalize-space(.),'Đăng nhập')]"),
        (By.XPATH, "//button[contains(normalize-space(.),'Login')]"),
    ]

    def form_ready(d):
        return (
            _first_visible(d, email_candidates),
            _first_visible(d, password_candidates),
            _first_visible(d, button_candidates),
        )

    end = time.monotonic() + max(5, timeout)
    email_el = password_el = button_el = None
    while time.monotonic() < end:
        email_el, password_el, button_el = form_ready(driver)
        if email_el and password_el and button_el:
            break
        time.sleep(0.2)

    if not (email_el and password_el and button_el):
        return False

    if progress:
        progress("Đang tự động đăng nhập bằng tài khoản test cục bộ...")

    email_el.click()
    email_el.clear()
    email_el.send_keys(email)
    password_el.click()
    password_el.clear()
    password_el.send_keys(password)
    button_el.click()
    return True

def build_chrome_options(webdriver, show_browser=True, profile_dir=""):
    """Tạo ChromeOptions dùng chung.

    Với module Danh mục xe, ``profile_dir`` giúp Firebase Auth/cookie được giữ lại
    giữa các lần chạy Selenium. Thư mục profile chỉ nằm local và được .gitignore.
    """
    options = webdriver.ChromeOptions()
    if not show_browser:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    if profile_dir:
        profile_path = Path(profile_dir).expanduser().resolve()
        profile_path.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
    return options


def is_login_page(driver):
    """Nhận biết browser đang bị chuyển về trang đăng nhập."""
    try:
        current = (driver.current_url or "").lower()
        if "/login" in current:
            return True
        password_inputs = driver.find_elements("css selector", "input[type='password']")
        login_buttons = driver.find_elements(
            "xpath",
            "//button[contains(normalize-space(.),'Đăng nhập') or contains(normalize-space(.),'Login')]",
        )
        return bool(password_inputs and login_buttons)
    except Exception:
        return False


def open_target_with_login(driver, url, timeout, require_login, login_wait_seconds, progress=None):
    """Mở URL đích, tự đăng nhập Fleet Console rồi mới bắt đầu kiểm thử.

    Luồng:
    1. Mở `/cars/catalog`.
    2. Nếu bị redirect về `/login`, đọc tài khoản từ biến môi trường hoặc
       `.autotest.env` (file cục bộ, đã .gitignore), tự điền Email/Mật khẩu và submit.
    3. Chờ Firebase Auth ổn định rồi mở lại `/cars/catalog`.
    4. Chỉ trả về khi thực sự ở trang đích.

    Nếu chưa cấu hình credential thì vẫn fallback sang đăng nhập thủ công để app
    không bị khóa cứng khi đổi tài khoản test.
    """
    import time
    from urllib.parse import urlparse
    from selenium.webdriver.support.ui import WebDriverWait

    target_path = (urlparse(url).path or "/").rstrip("/") or "/"

    def on_target_page(d):
        try:
            current_path = (urlparse(d.current_url or "").path or "/").rstrip("/") or "/"
            return (not is_login_page(d)) and current_path == target_path
        except Exception:
            return False

    if progress:
        progress(f"Đang mở {url}")
    driver.get(url)

    if not require_login:
        try:
            WebDriverWait(driver, max(5, timeout)).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        return

    email, password = load_autotest_credentials()
    has_auto_credentials = bool(email and password)
    deadline = time.monotonic() + max(30, login_wait_seconds)
    saw_authenticated_page = False
    last_retry = 0.0
    auto_attempts = 0
    last_auto_attempt = 0.0
    manual_message_sent = False

    while time.monotonic() < deadline:
        if on_target_page(driver):
            if progress:
                progress("Đã đăng nhập và vào Danh mục xe. Bắt đầu kiểm thử...")
            try:
                WebDriverWait(driver, max(5, timeout)).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception:
                pass
            return

        if is_login_page(driver):
            # Ưu tiên auto login; tránh submit liên tục khi Firebase đang xử lý.
            if has_auto_credentials and auto_attempts < 2 and time.monotonic() - last_auto_attempt >= 4.0:
                submitted = submit_login_form(
                    driver,
                    email,
                    password,
                    timeout=max(8, timeout),
                    progress=progress,
                )
                auto_attempts += 1
                last_auto_attempt = time.monotonic()
                if not submitted:
                    raise RuntimeError(
                        "LOGIN_FAILED: Không tìm thấy form đăng nhập để tự điền. "
                        "Kiểm tra giao diện Login hoặc cập nhật locator Email/Mật khẩu/Nút Đăng nhập."
                    )

                # Cho Firebase xử lý request login. Không điều hướng ngay.
                try:
                    WebDriverWait(driver, min(15, max(8, timeout + 3))).until(
                        lambda d: not is_login_page(d)
                    )
                except Exception:
                    # Có thể credential sai hoặc server phản hồi chậm. Thử tối đa 2 lần.
                    if auto_attempts >= 2:
                        raise RuntimeError(
                            "LOGIN_FAILED: Tự động đăng nhập không thành công. "
                            "Hãy kiểm tra tài khoản test trong .autotest.env rồi chạy lại."
                        )
                    time.sleep(1.0)
                continue

            if has_auto_credentials and auto_attempts >= 2:
                raise RuntimeError(
                    "LOGIN_FAILED: Tự động đăng nhập không thành công sau 2 lần thử. "
                    "Hãy kiểm tra tài khoản test hoặc quyền truy cập Fleet Console."
                )

            # Fallback nếu người dùng xóa .autotest.env.
            if not has_auto_credentials:
                if not manual_message_sent and progress:
                    progress(
                        "Chưa cấu hình tài khoản tự động. Hãy đăng nhập trên Chrome Selenium, "
                        "hoặc tạo .autotest.env theo file .autotest.env.example."
                    )
                    manual_message_sent = True
                time.sleep(0.4)
                continue

            time.sleep(0.4)
            continue

        # Đã rời /login (thường là Dashboard sau khi Firebase login thành công).
        if not saw_authenticated_page:
            saw_authenticated_page = True
            if progress:
                progress("Đăng nhập thành công. Đang chờ Firebase lưu phiên...")
            time.sleep(2.5)

        if time.monotonic() - last_retry >= 2.0:
            if progress:
                progress("Đang chuyển tới Danh mục xe...")
            driver.get(url)
            last_retry = time.monotonic()
        else:
            time.sleep(0.3)

    if is_login_page(driver):
        if has_auto_credentials:
            raise RuntimeError(
                "LOGIN_TIMEOUT: Đã thử tự động đăng nhập nhưng vẫn ở trang Login. "
                "Kiểm tra tài khoản test hoặc quyền truy cập /cars/catalog."
            )
        raise RuntimeError(
            "LOGIN_TIMEOUT: Chưa có phiên đăng nhập hợp lệ trong thời gian chờ. "
            "Hãy cấu hình .autotest.env hoặc đăng nhập thủ công trên Chrome Selenium."
        )

    raise RuntimeError(
        "LOGIN_REQUIRED: Đã đăng nhập nhưng chưa mở được trang Danh mục xe. "
        "Hãy kiểm tra tài khoản có quyền truy cập /cars/catalog rồi thử lại."
    )


class SeleniumWorker(QObject):
    progress = Signal(str)
    finished = Signal(str, object, str)  # status: PASS / FAIL / ERROR

    def __init__(self, request: RunnerRequest, mode="run"):
        super().__init__()
        self.request = request
        self.mode = mode

    def _by_value(self, By):
        return locator_by(By, self.request.locator_type)

    def _extract_actual(self, element):
        test_type = self.request.test_type

        if test_type == "Element tồn tại":
            return ["Tồn tại"]

        if test_type == "Dropdown List":
            from selenium.webdriver.support.ui import Select
            return [option.text for option in Select(element).options]

        if test_type == "Table":
            return extract_table_rows(element)

        if test_type == "Attribute placeholder":
            return [element.get_attribute("placeholder") or ""]

        # Text / Value
        text = (element.text or "").strip()
        if text:
            return [text]
        value = element.get_attribute("value")
        if value not in (None, ""):
            return [value]
        return [element.get_attribute("placeholder") or ""]

    def _compare(self, expected, actual):
        req = self.request
        expected_norm = [
            normalize_text(x, req.trim_whitespace, req.case_sensitive)
            for x in expected
        ]
        actual_norm = [
            normalize_text(x, req.trim_whitespace, req.case_sensitive)
            for x in actual
        ]

        rows: List[Dict[str, str]] = []

        if req.check_order:
            size = max(len(expected), len(actual))
            for i in range(size):
                e = expected[i] if i < len(expected) else ""
                a = actual[i] if i < len(actual) else ""
                e_norm = expected_norm[i] if i < len(expected_norm) else None
                a_norm = actual_norm[i] if i < len(actual_norm) else None

                if e_norm is None:
                    result = "Unexpected"
                elif a_norm is None:
                    result = "Missing"
                elif e_norm == a_norm:
                    result = "PASS"
                else:
                    result = "FAIL"
                rows.append({"expected": e, "actual": a, "result": result})
        else:
            used = set()
            for e, e_norm in zip(expected, expected_norm):
                match = next(
                    (i for i, a_norm in enumerate(actual_norm) if i not in used and a_norm == e_norm),
                    None,
                )
                if match is None:
                    rows.append({"expected": e, "actual": "", "result": "Missing"})
                else:
                    used.add(match)
                    rows.append({"expected": e, "actual": actual[match], "result": "PASS"})
            for i, a in enumerate(actual):
                if i not in used:
                    rows.append({"expected": "", "actual": a, "result": "Unexpected"})

        passed = bool(rows) and all(row["result"] == "PASS" for row in rows)
        return passed, rows

    @Slot()
    def run(self):
        driver = None
        try:
            self.progress.emit("Đang khởi tạo Chrome...")

            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            options = build_chrome_options(
                webdriver,
                show_browser=self.request.show_browser,
                profile_dir=self.request.profile_dir,
            )

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(max(15, self.request.timeout + 5))

            open_target_with_login(
                driver,
                self.request.url,
                self.request.timeout,
                self.request.require_login,
                self.request.login_wait_seconds,
                self.progress.emit,
            )

            locator = (self._by_value(By), self.request.locator_value)
            self.progress.emit("Đang tìm element đã lưu...")
            element = WebDriverWait(driver, self.request.timeout).until(
                EC.presence_of_element_located(locator)
            )

            if self.mode == "check":
                detail = f"Tìm thấy <{element.tag_name}>"
                text = (element.text or "").strip()
                if text:
                    detail += f" – {text[:80]}"
                self.finished.emit(
                    "PASS",
                    [{"expected": "Element tồn tại", "actual": detail, "result": "PASS"}],
                    detail,
                )
                return

            self.progress.emit("Đang lấy Actual Result...")
            actual = self._extract_actual(element)
            expected = list(self.request.expected_lines)
            if self.request.test_type == "Element tồn tại" and not expected:
                expected = ["Tồn tại"]

            passed, rows = self._compare(expected, actual)
            if passed:
                self.finished.emit("PASS", rows, "PASS – Actual khớp Expected.")
            else:
                self.finished.emit("FAIL", rows, "FAIL – Actual không khớp Expected.")

        except ModuleNotFoundError:
            self.finished.emit(
                "ERROR",
                [],
                "Chưa cài Selenium. Chạy: pip install -r requirements.txt",
            )
        except Exception as exc:
            self.finished.emit("ERROR", [], friendly_selenium_error(exc))
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass


@dataclass
class CrudRequest:
    """Linh - Thứ Năm: CRUD Hãng/Mẫu xe + xác nhận dropdown cập nhật sau CRUD."""

    url: str
    add_button: Tuple[str, str]
    name_field: Tuple[str, str]
    save_button: Tuple[str, str]
    table: Tuple[str, str]
    value_name: str
    group_label: str = "Hãng xe"
    brand_field: Optional[Tuple[str, str]] = None
    value_brand: str = ""
    dependent_dropdown: Optional[Tuple[str, str]] = None
    cleanup: bool = True
    timeout: int = 12
    show_browser: bool = True
    require_login: bool = False
    login_wait_seconds: int = 180
    profile_dir: str = ""


class CrudWorker(QObject):
    """Chạy một lượt CRUD (Thêm) trên Danh mục xe và đối chiếu Expected–Actual.

    Các bước: mở form Thêm -> nhập tên -> (Mẫu xe) chọn Hãng liên kết -> Lưu ->
    kiểm tra dòng mới xuất hiện trong bảng -> kiểm tra dropdown phụ thuộc đã cập
    nhật -> dọn dữ liệu test (best-effort).
    """

    progress = Signal(str)
    finished = Signal(str, object, str)  # status: PASS / FAIL / ERROR

    def __init__(self, request: CrudRequest):
        super().__init__()
        self.request = request

    @Slot()
    def run(self):
        driver = None
        req = self.request
        rows: List[Dict[str, str]] = []
        try:
            self.progress.emit("Đang khởi tạo Chrome...")

            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            options = build_chrome_options(
                webdriver,
                show_browser=req.show_browser,
                profile_dir=req.profile_dir,
            )

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(max(15, req.timeout + 5))
            wait = WebDriverWait(driver, req.timeout)

            open_target_with_login(
                driver,
                req.url,
                req.timeout,
                req.require_login,
                req.login_wait_seconds,
                self.progress.emit,
            )

            # 1) Mở form Thêm
            self.progress.emit(f"Đang mở form Thêm {req.group_label}...")
            add_type, add_value = req.add_button
            add_btn = wait.until(
                EC.element_to_be_clickable((locator_by(By, add_type), add_value))
            )
            add_btn.click()
            rows.append({
                "expected": "Mở được form Thêm",
                "actual": "Đã click nút Thêm",
                "result": "PASS",
            })

            # 2) Nhập tên
            name_type, name_value = req.name_field
            name_field = wait.until(
                EC.visibility_of_element_located((locator_by(By, name_type), name_value))
            )
            name_field.clear()
            name_field.send_keys(req.value_name)
            actual_name = name_field.get_attribute("value") or ""
            rows.append({
                "expected": req.value_name,
                "actual": actual_name,
                "result": "PASS" if actual_name.strip() == req.value_name.strip() else "FAIL",
            })

            # 3) Chọn Hãng liên kết (chỉ áp dụng cho Mẫu xe)
            if req.brand_field and req.value_brand:
                self.progress.emit("Đang chọn Hãng liên kết...")
                brand_type, brand_value = req.brand_field
                brand_el = wait.until(
                    EC.visibility_of_element_located((locator_by(By, brand_type), brand_value))
                )
                chosen = try_choose_option(brand_el, req.value_brand, req.timeout)
                rows.append({
                    "expected": req.value_brand,
                    "actual": req.value_brand if chosen else "Không chọn được option",
                    "result": "PASS" if chosen else "FAIL",
                })

            # 4) Lưu
            self.progress.emit("Đang lưu...")
            save_type, save_value = req.save_button
            save_btn = wait.until(
                EC.element_to_be_clickable((locator_by(By, save_type), save_value))
            )
            click_safely(driver, save_btn)

            # 5) Kiểm tra dòng mới trong bảng
            self.progress.emit("Đang kiểm tra bảng sau khi Lưu...")
            table_type, table_value = req.table
            table_el = wait.until(
                EC.presence_of_element_located((locator_by(By, table_type), table_value))
            )

            def table_has_value(_driver):
                return any(
                    req.value_name.strip().lower() in line.lower()
                    for line in extract_table_rows(table_el)
                )

            try:
                WebDriverWait(driver, req.timeout).until(table_has_value)
                found_in_table = True
            except Exception:
                found_in_table = False

            rows.append({
                "expected": f"'{req.value_name}' xuất hiện trong bảng",
                "actual": "Có" if found_in_table else "Không thấy",
                "result": "PASS" if found_in_table else "FAIL",
            })

            # Với Mẫu xe: kiểm tra mapping Hãng ngay trên cùng dòng của bảng.
            if req.value_brand:
                mapped = False
                mapped_text = "Không thấy dòng Mẫu xe"
                try:
                    for tr in table_el.find_elements(By.CSS_SELECTOR, "tbody tr"):
                        line = " ".join((tr.text or "").split())
                        if req.value_name.strip().casefold() in line.casefold():
                            mapped_text = line
                            mapped = req.value_brand.strip().casefold() in line.casefold()
                            break
                except Exception:
                    pass
                rows.append({
                    "expected": f"{req.value_name} thuộc Hãng {req.value_brand}",
                    "actual": mapped_text[:180],
                    "result": "PASS" if mapped else "FAIL",
                })

            # 6) Kiểm tra dropdown phụ thuộc đã cập nhật
            if req.dependent_dropdown:
                self.progress.emit("Đang kiểm tra dropdown phụ thuộc...")
                dd_type, dd_value = req.dependent_dropdown
                try:
                    dd_el = wait.until(
                        EC.presence_of_element_located((locator_by(By, dd_type), dd_value))
                    )
                    expected_option = req.value_name.strip()
                    options_text = []

                    if (dd_el.tag_name or "").lower() == "select":
                        from selenium.webdriver.support.ui import Select
                        options_text = [option.text for option in Select(dd_el).options]
                    else:
                        # Ant Design Select: mở dropdown và đọc option đang render.
                        try:
                            dd_el.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", dd_el)
                        try:
                            WebDriverWait(driver, req.timeout).until(
                                lambda d: any(
                                    x.is_displayed()
                                    for x in d.find_elements(
                                        By.CSS_SELECTOR,
                                        ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option",
                                    )
                                )
                            )
                        except Exception:
                            pass
                        for option in driver.find_elements(
                            By.CSS_SELECTOR,
                            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option",
                        ):
                            if option.is_displayed():
                                label = " ".join((option.text or "").split())
                                if label:
                                    options_text.append(label)
                        try:
                            from selenium.webdriver.common.keys import Keys
                            dd_el.send_keys(Keys.ESCAPE)
                        except Exception:
                            pass

                    has_option = any(
                        expected_option.casefold() == option.strip().casefold()
                        for option in options_text
                    )
                    rows.append({
                        "expected": f"Dropdown có '{expected_option}'",
                        "actual": ", ".join(options_text)[:160] or "(rỗng)",
                        "result": "PASS" if has_option else "FAIL",
                    })
                except Exception as exc:
                    rows.append({
                        "expected": "Dropdown cập nhật sau CRUD",
                        "actual": friendly_selenium_error(exc),
                        "result": "FAIL",
                    })

            # 7) Dọn dữ liệu test (best-effort)
            cleanup_note = ""
            if req.cleanup:
                self.progress.emit("Đang dọn dữ liệu test...")
                cleaned = cleanup_row(driver, table_el, req.value_name)
                cleanup_note = (
                    " Đã dọn dữ liệu test." if cleaned else " Không tự dọn được, hãy xóa thủ công."
                )

            passed = bool(rows) and all(row["result"] == "PASS" for row in rows)
            status = "PASS" if passed else "FAIL"
            summary = f"CRUD {req.group_label}: " + ("PASS." if passed else "có bước FAIL.")
            self.finished.emit(status, rows, summary + cleanup_note)

        except ModuleNotFoundError:
            self.finished.emit(
                "ERROR",
                rows,
                "Chưa cài Selenium. Chạy: pip install -r requirements.txt",
            )
        except Exception as exc:
            self.finished.emit("ERROR", rows, friendly_selenium_error(exc))
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
