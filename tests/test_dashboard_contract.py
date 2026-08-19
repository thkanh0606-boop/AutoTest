import sqlite3

from core.test_contract import TestContract
from core.test_result_repository import TestResultRepository
from runners.text_dropdown_runner import _compare_line_pairs, _compare_navigation_expected, _compare_table_rows


def _dashboard_cases():
    return [element for element in TestContract.elements if element.page_key == "plt_dashboard" and element.case_id]


def test_dashboard_contract_has_required_cases():
    cases = _dashboard_cases()
    case_ids = {case.case_id for case in cases}

    assert len(cases) >= 6
    assert len(case_ids) == len(cases)
    assert {"DASH-001", "DASH-003", "DASH-006", "DASH-011", "DASH-012", "DASH-013", "DASH-014"} <= case_ids
    assert all(case.steps for case in cases)
    assert all(case.expected_result for case in cases)


def test_dashboard_contract_covers_card_menu_and_deep_link():
    cases = _dashboard_cases()

    assert any(case.action_type == "contains_all_has_number" for case in cases)
    assert any(case.action_type == "click_url_contains" and case.target_path == "/bookings" for case in cases)
    assert any(case.action_type == "click_url_contains" and case.target_path == "/cars" for case in cases)
    assert any(case.action_type == "click_url_contains" and case.target_path == "/finance" for case in cases)
    assert any(case.action_type == "deep_link_url_contains" and case.target_path == "/dashboard" for case in cases)


def test_dashboard_contract_covers_current_date_and_all_sidebar_routes():
    cases = _dashboard_cases()
    route_targets = {
        case.target_path
        for case in cases
        if case.action_type == "click_url_contains"
    }

    assert any(case.action_type == "today_vi_date" for case in cases)
    assert {
        "/dashboard",
        "/bookings",
        "/bookings/new",
        "/customers",
        "/cars",
        "/cars/catalog",
        "/finance",
        "/users",
    } <= route_targets
    assert any(
        case.key == "dashboard_sidebar_menu"
        and case.action_type == "contains_all"
        for case in cases
    )


def test_dropdown_and_menu_compare_by_position():
    status, pairs = _compare_line_pairs("English\nTiếng Việt", "English\nTiếng Anh")

    assert status == "FAILED"
    assert pairs[0]["status"] == "PASS"
    assert pairs[1]["expected"] == "Tiếng Việt"
    assert pairs[1]["actual"] == "Tiếng Anh"
    assert pairs[1]["status"] == "FAIL"


def test_navigation_uses_user_expected_not_contract_target_path():
    actual = "https://courses.plt.pro.vn/bookings"

    assert _compare_navigation_expected("/bookings", actual) == "PASSED"
    assert _compare_navigation_expected("https://courses.plt.pro.vn/bookings", actual) == "PASSED"
    assert _compare_navigation_expected("https://docs.google.com/spreadsheets/d/example/edit", actual) == "FAILED"
    assert _compare_navigation_expected("", actual) == "FAILED"


def test_table_compare_each_cell_by_position():
    expected = "Mã BK\tTrạng thái\tKhách\nBK-01\tĐang thực hiện\tPhúc Trần Minh"
    actual = "Mã BK\tTrạng thái\tKhách\nBK-01\tĐang chờ\tPhúc Trần Minh"

    status, pairs = _compare_table_rows(expected, actual)

    assert status == "FAILED"
    assert pairs[0] == {"index": "R1C1", "expected": "Mã BK", "actual": "Mã BK", "status": "PASS"}
    assert pairs[4] == {"index": "R2C2", "expected": "Đang thực hiện", "actual": "Đang chờ", "status": "FAIL"}
    assert pairs[5] == {"index": "R2C3", "expected": "Phúc Trần Minh", "actual": "Phúc Trần Minh", "status": "PASS"}


def test_table_compare_manual_line_cells_by_position():
    expected = "BK-20260405-9228\nĐang thực hiện\n19:00 05 thg 4"
    actual = "BK-20260405-9228\nĐang thực hiện\n19:00 06 thg 4"

    status, pairs = _compare_table_rows(expected, actual)

    assert status == "FAILED"
    assert pairs[0]["index"] == "R1C1"
    assert pairs[0]["status"] == "PASS"
    assert pairs[2] == {"index": "R3C1", "expected": "19:00 05 thg 4", "actual": "19:00 06 thg 4", "status": "FAIL"}


def test_table_compare_single_card_row_cells_by_position():
    expected = "BK-20260405-9228\tĐang thực hiện\tPhúc Trần Minh"
    actual = "BK-20260405-9228\tĐang chờ\tPhúc Trần Minh"

    status, pairs = _compare_table_rows(expected, actual)

    assert status == "FAILED"
    assert pairs[0] == {"index": "R1C1", "expected": "BK-20260405-9228", "actual": "BK-20260405-9228", "status": "PASS"}
    assert pairs[1] == {"index": "R1C2", "expected": "Đang thực hiện", "actual": "Đang chờ", "status": "FAIL"}
    assert pairs[2] == {"index": "R1C3", "expected": "Phúc Trần Minh", "actual": "Phúc Trần Minh", "status": "PASS"}


def test_repository_single_run_persists_without_duplicate_test_case(tmp_path):
    db_path = tmp_path / "autotest.sqlite3"
    repository = TestResultRepository(str(db_path))
    case = next(element for element in _dashboard_cases() if element.case_id == "DASH-001")
    payload = {
        "module": case.test_type,
        "page_key": case.page_key,
        "page_name": "Trang tổng quan",
        "element_key": case.key,
        "element_name": case.name,
        "locator_type": case.locator_type,
        "locator_value": case.locator_value,
        "expected": case.sample_expected,
        "case_id": case.case_id,
        "steps": case.steps,
        "expected_result": case.expected_result,
        "actual": "Dashboard",
        "actual_result": "Dashboard",
        "status": "PASSED",
        "message": "Expected khớp Actual",
        "error_message": "",
        "screenshot_path": "",
    }

    repository.save_case_and_result(payload)
    repository.save_case_and_result(payload)

    with sqlite3.connect(db_path) as connection:
        case_count = connection.execute(
            "SELECT COUNT(*) FROM test_cases WHERE case_id = ?",
            (case.case_id,),
        ).fetchone()[0]
        run_count = connection.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0]
        result_count = connection.execute("SELECT COUNT(*) FROM test_results").fetchone()[0]

    assert case_count == 1
    assert run_count == 2
    assert result_count == 2
