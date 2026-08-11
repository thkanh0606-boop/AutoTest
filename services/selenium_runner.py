from dataclasses import dataclass
from typing import Dict, List

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


class SeleniumWorker(QObject):
    progress = Signal(str)
    finished = Signal(str, object, str)  # status: PASS / FAIL / ERROR

    def __init__(self, request: RunnerRequest, mode="run"):
        super().__init__()
        self.request = request
        self.mode = mode

    def _by_value(self, By):
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
        return mapping.get(self.request.locator_type, By.CSS_SELECTOR)

    def _extract_actual(self, element):
        test_type = self.request.test_type

        if test_type == "Element tồn tại":
            return ["Tồn tại"]

        if test_type == "Dropdown List":
            from selenium.webdriver.support.ui import Select
            return [option.text for option in Select(element).options]

        if test_type == "Table":
            rows = element.find_elements("css selector", "tr")
            output = []
            for row in rows:
                cells = row.find_elements("css selector", "th,td")
                if cells:
                    output.append(" | ".join(cell.text for cell in cells))
            return output

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

            options = webdriver.ChromeOptions()
            if not self.request.show_browser:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=1440,1000")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(max(15, self.request.timeout + 5))

            self.progress.emit(f"Đang mở {self.request.url}")
            driver.get(self.request.url)

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
