"""Load Test Suite data from Excel or CSV files.

The project receives workbooks from several contributors, so column names and
sheet layouts are not completely uniform.  This module keeps the UI-facing
contract small (a list of dictionaries) while normalising those variations.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


_TC_ID_COLUMNS = {"tc id", "test case id", "testcase id", "ma tc"}
_TITLE_COLUMNS = {"title", "test case", "test case name", "ten test case", "ten case"}
_AREA_COLUMNS = {"area", "module", "page", "trang", "trang pcm", "feature"}
_EXPECTED_COLUMNS = {
    "expected",
    "expected result",
    "expected results",
    "ket qua mong doi",
    "ghi chu dieu kien",
}
_PCM_COLUMNS = {"ma pcm", "pcm", "pcm id"}

_PCM_PAGE_KEYS = {
    "PCM-01": "plt_login",
    "PCM-02": "plt_dashboard",
    "PCM-03": "plt_booking",
    "PCM-04": "plt_fleet",
    "PCM-05": "plt_vehicle_catalog",
    "PCM-06": "plt_user",
    "PCM-07": "plt_finance",
}

PAGE_MODULE_NAMES = {
    "plt_login": "Đăng nhập",
    "plt_dashboard": "Dashboard",
    "plt_booking": "Đặt xe",
    "plt_fleet": "Xe",
    "plt_vehicle_catalog": "Danh mục xe",
    "plt_finance": "Tài chính",
    "plt_user": "Người dùng",
}

PAGE_URLS = {
    "plt_login": "https://courses.plt.pro.vn/login",
    "plt_dashboard": "https://courses.plt.pro.vn/dashboard",
    "plt_booking": "https://courses.plt.pro.vn/bookings",
    "plt_fleet": "https://courses.plt.pro.vn/cars",
    "plt_vehicle_catalog": "https://courses.plt.pro.vn/cars/catalog",
    "plt_finance": "https://courses.plt.pro.vn/finance",
    "plt_user": "https://courses.plt.pro.vn/users",
}


def _normalise(value: object) -> str:
    text = str(value or "").replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().lower()
    return re.sub(r"\s+", " ", text)


def _clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _find_column(columns: dict[str, object], aliases: set[str]):
    for normalised_name, original_name in columns.items():
        if normalised_name in aliases:
            return original_name
    return None


def _promote_header_if_needed(frame: pd.DataFrame) -> pd.DataFrame:
    """Use the first data row as header for sheets with a title row."""
    current = {_normalise(column) for column in frame.columns}
    if current & _TC_ID_COLUMNS or frame.empty:
        return frame

    first_row = {_normalise(value) for value in frame.iloc[0].tolist()}
    if first_row & _TC_ID_COLUMNS:
        promoted = frame.iloc[1:].copy()
        promoted.columns = [
            _clean_cell(value) or f"Unnamed {index}"
            for index, value in enumerate(frame.iloc[0].tolist())
        ]
        return promoted.reset_index(drop=True)
    return frame


def _infer_page_key(*values: str) -> str:
    combined = " ".join(value for value in values if value)
    upper = combined.upper()
    for pcm_code, page_key in _PCM_PAGE_KEYS.items():
        if pcm_code in upper:
            return page_key

    text = _normalise(combined)
    # Check the more specific catalogue/user phrases before the generic car
    # phrase so "Danh mục xe" is not classified as the fleet page.
    mappings = (
        (("danh muc xe", "danhmucxe", "car catalog"), "plt_vehicle_catalog"),
        (("nguoi dung", "nguoidung", "user"), "plt_user"),
        (("dat xe", "datxe", "booking"), "plt_booking"),
        (("dashboard", "tong quan"), "plt_dashboard"),
        (("dang nhap", "login"), "plt_login"),
        (("tai chinh", "finance"), "plt_finance"),
        (("quan ly xe", "tc xe", "fleet"), "plt_fleet"),
    )
    for phrases, page_key in mappings:
        if any(phrase in text for phrase in phrases):
            return page_key
    return ""


def _cases_from_frame(frame: pd.DataFrame, sheet_name: str) -> list[dict]:
    frame = _promote_header_if_needed(frame)
    if frame.empty:
        return []

    columns = {_normalise(column): column for column in frame.columns}
    tc_column = _find_column(columns, _TC_ID_COLUMNS)
    if tc_column is None:
        # A scope/summary sheet is not an executable test-case sheet.
        return []

    title_column = _find_column(columns, _TITLE_COLUMNS)
    area_column = _find_column(columns, _AREA_COLUMNS)
    expected_column = _find_column(columns, _EXPECTED_COLUMNS)
    pcm_column = _find_column(columns, _PCM_COLUMNS)

    cases = []
    for _, row in frame.iterrows():
        tc_id = _clean_cell(row.get(tc_column))
        title = _clean_cell(row.get(title_column)) if title_column is not None else ""
        area = _clean_cell(row.get(area_column)) if area_column is not None else ""
        expected = _clean_cell(row.get(expected_column)) if expected_column is not None else ""
        pcm_code = _clean_cell(row.get(pcm_column)) if pcm_column is not None else ""

        if not tc_id or _normalise(tc_id) in _TC_ID_COLUMNS:
            continue
        # Some source files contain a descriptive sentence immediately below
        # the header.  It has no usable case data and must not appear in the UI.
        if not any((title, area, expected, pcm_code)):
            continue

        cases.append(
            {
                "tc_id": tc_id,
                "title": title,
                "area": area,
                "expected": expected,
                "page_key": _infer_page_key(pcm_code, tc_id, area, title, sheet_name),
                "source_sheet": sheet_name,
            }
        )
    return cases


def _read_csv(path: Path) -> dict[str, pd.DataFrame]:
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin1"):
        try:
            frame = pd.read_csv(path, sep=None, engine="python", encoding=encoding)
            return {path.stem: frame}
        except UnicodeDecodeError as error:
            last_error = error
    if last_error:
        raise last_error
    return {}


def load_test_suite_from_excel(filepath: str) -> list[dict]:
    """Return all valid test cases found in an ``.xlsx``, ``.xls`` or CSV file.

    The historical function name is retained because the UI imports it.  Read
    errors and unsupported layouts are raised with a useful message instead of
    being silently converted to an empty list.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    extension = path.suffix.lower()
    try:
        if extension == ".csv":
            sheets = _read_csv(path)
        elif extension in {".xlsx", ".xls"}:
            sheets = pd.read_excel(path, sheet_name=None)
        else:
            raise ValueError("Chỉ hỗ trợ file .xlsx, .xls hoặc .csv")
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"Không thể đọc file {path.name}: {error}") from error

    test_cases = []
    for sheet_name, frame in sheets.items():
        test_cases.extend(_cases_from_frame(frame, str(sheet_name)))

    if not test_cases:
        raise ValueError(
            "Không tìm thấy dữ liệu Test Case. File cần có cột 'TC ID' hoặc 'Mã TC'."
        )
    return test_cases


def _map_to_page_key(tc_id: str) -> str:
    """Backward-compatible wrapper used by older callers/tests."""
    return _infer_page_key(tc_id)


def demo_7_module_cases() -> list[dict]:
    """Built-in, executable route smoke suite covering the seven PCM modules."""
    cases = []
    paths = {
        "plt_login": "/login",
        "plt_dashboard": "/dashboard",
        "plt_booking": "/bookings",
        "plt_fleet": "/cars",
        "plt_vehicle_catalog": "/cars/catalog",
        "plt_finance": "/finance",
        "plt_user": "/users",
    }
    for index, (page_key, module_name) in enumerate(PAGE_MODULE_NAMES.items(), start=1):
        target_path = paths[page_key]
        cases.append(
            {
                "tc_id": f"DEMO-{index:02d}",
                "title": f"Mở và xác nhận trang {module_name}",
                "area": module_name,
                "module": module_name,
                "expected": f"URL chứa {target_path} và nội dung trang hiển thị",
                "page_key": page_key,
                "source_sheet": "Demo 7 modules",
                "action_type": "route_smoke",
                "target_path": target_path,
                "url": PAGE_URLS[page_key],
                "executable": True,
            }
        )
    return cases


def dashboard_regression_cases() -> list[dict]:
    """Expose each Dashboard contract as one independently executable case."""
    from core.test_contract import TestContract

    cases = []
    for element in TestContract.elements:
        if element.page_key != "plt_dashboard":
            continue
        cases.append(
            {
                "tc_id": element.case_id or element.key,
                "title": element.name,
                "area": "Dashboard",
                "module": "Dashboard",
                "expected": element.sample_expected,
                "page_key": element.page_key,
                "source_sheet": "Dashboard Regression",
                "element_key": element.key,
                "locator_type": element.locator_type,
                "locator_value": element.locator_value,
                "test_type": element.test_type,
                "action_type": element.action_type,
                "target_path": element.target_path,
                "steps": element.steps,
                "expected_result": element.expected_result,
                "url": PAGE_URLS["plt_dashboard"],
                "executable": True,
            }
        )
    return cases
