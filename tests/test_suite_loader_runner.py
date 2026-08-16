from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from core.suite_loader import load_test_suite_from_excel
from runners.suite_runner import _page_url, _run_page_open_check


def test_loader_aggregates_test_case_sheets_and_skips_summary_rows():
    booking = pd.DataFrame(
        [
            {
                "TC ID": "Submit button is enabled with labels",
                "Title": None,
                "Area": None,
                "Expected Results": None,
            },
            {
                "TC ID": "TC_DatXe_001",
                "Title": "Kiểm tra danh sách đặt xe",
                "Area": "Đặt xe",
                "Expected Results": "Hiển thị danh sách",
            },
        ]
    )
    users = pd.DataFrame(
        [
            {
                "TC ID": "TC_ThemNguoiDung_001",
                "Title": "Tạo người dùng",
                "Area": "Người dùng",
                "Expected Results": "Tạo thành công",
            }
        ]
    )
    summary = pd.DataFrame([{"Mã": "PCM-01", "Trang PCM": "Đăng nhập"}])

    with (
        patch("core.suite_loader.Path.is_file", return_value=True),
        patch(
            "core.suite_loader.pd.read_excel",
            return_value={"ScopeTable": summary, "DatXe_TCs": booking, "NguoiDung_TCs": users},
        ),
    ):
        cases = load_test_suite_from_excel("suite.xlsx")

    assert [case["tc_id"] for case in cases] == ["TC_DatXe_001", "TC_ThemNguoiDung_001"]
    assert [case["page_key"] for case in cases] == ["plt_booking", "plt_user"]


def test_loader_supports_pcm_detail_columns_and_csv():
    frame = pd.DataFrame(
        [
            {
                "Mã TC": "TC07",
                "Mã PCM": "PCM-02",
                "Trang": "Dashboard",
                "Tên Test Case": "Kiểm tra tiêu đề",
                "Ghi chú / Điều kiện": "Có session admin",
            }
        ]
    )
    with (
        patch("core.suite_loader.Path.is_file", return_value=True),
        patch("core.suite_loader._read_csv", return_value={"suite": frame}),
    ):
        cases = load_test_suite_from_excel("suite.csv")

    assert cases == [
        {
            "tc_id": "TC07",
            "title": "Kiểm tra tiêu đề",
            "area": "Dashboard",
            "expected": "Có session admin",
            "page_key": "plt_dashboard",
            "source_sheet": "suite",
        }
    ]


def test_loader_reports_an_unsupported_layout_instead_of_silent_empty_result():
    frame = pd.DataFrame([{"Tên": "Không có mã test case"}])
    with (
        patch("core.suite_loader.Path.is_file", return_value=True),
        patch("core.suite_loader.pd.read_excel", return_value={"Sheet1": frame}),
    ):
        with pytest.raises(ValueError, match="TC ID.*Mã TC"):
            load_test_suite_from_excel("suite.xlsx")


def test_page_open_check_uses_visible_chrome_and_closes_it():
    driver = MagicMock()
    driver.current_url = "https://courses.plt.pro.vn/bookings"
    with (
        patch("core.driver_factory.DriverFactory.create_driver", return_value=driver) as create,
        patch("runners.suite_runner.time.sleep"),
    ):
        success, message = _run_page_open_check("plt_booking")

    assert success is True
    assert "bookings" in message
    create.assert_called_once_with(headless=False, keep_session=True)
    driver.get.assert_called_once_with(_page_url("plt_booking"))
    driver.quit.assert_called_once_with()


def test_page_open_check_returns_failure_when_driver_cannot_start():
    with patch(
        "core.driver_factory.DriverFactory.create_driver",
        side_effect=RuntimeError("driver unavailable"),
    ):
        success, message = _run_page_open_check("plt_login")

    assert success is False
    assert "driver unavailable" in message
