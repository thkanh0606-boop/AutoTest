from dataclasses import dataclass
from typing import List

@dataclass
class PageUnderTest:
    key: str
    name: str
    path: str
    url: str

@dataclass
class ElementUnderTest:
    key: str
    page_key: str
    test_type: str
    name: str
    locator_type: str
    locator_value: str
    sample_expected: str
    case_id: str

class TestContract:
    pages: List[PageUnderTest] = [
        PageUnderTest(
            key="plt_users",
            name="Quản lý Nhân sự",
            path="/users",
            url="https://courses.plt.pro.vn/users",
        ),
        PageUnderTest(
            key="plt_users_create",
            name="Thêm mới Nhân sự",
            path="/users/create",
            url="https://courses.plt.pro.vn/users/create",
        ),
    ]

    elements: List[ElementUnderTest] = [
        # --- MÀN HÌNH DANH SÁCH NHÂN SỰ (/users) ---
        ElementUnderTest(
            key="header_title",
            page_key="plt_users",
            test_type="label",
            name="Tiêu đề Header",
            locator_type="xpath",
            locator_value="//*[@id='root']//header//h4",
            sample_expected="Nhân sự",
            case_id="STAFF-LIST-001",
        ),
        ElementUnderTest(
            key="header_role_span",
            page_key="plt_users",
            test_type="label",
            name="Nhãn vai trò tài khoản",
            locator_type="xpath",
            locator_value="//*[@id='root']//header/div[2]/span",
            sample_expected="Quản trị viên",
            case_id="STAFF-LIST-002",
        ),
        ElementUnderTest(
            key="btn_open_create_page",
            page_key="plt_users",
            test_type="button",
            name="Nút chuyển sang trang Thêm nhân sự",
            locator_type="xpath",
            locator_value="//*[@id='root']//main/div/div/section/div[1]/div[2]/a/button",
            sample_expected="Thêm nhân sự",
            case_id="STAFF-LIST-003",
        ),
        ElementUnderTest(
            key="table_delete_btn",
            page_key="plt_users",
            test_type="button",
            name="Nút Xóa dòng dữ liệu",
            locator_type="xpath",
            locator_value="//button[@aria-label='Xóa']",
            sample_expected="",
            case_id="STAFF-LIST-004",
        ),
        ElementUnderTest(
            key="pagination_list",
            page_key="plt_users",
            test_type="pagination",
            name="Thanh phân trang Ant Design",
            locator_type="xpath",
            locator_value="//ul[contains(@class,'ant-pagination')]",
            sample_expected="",
            case_id="STAFF-LIST-005",
        ),

        # --- MÀN HÌNH FORM THÊM MỚI NHÂN SỰ (/users/create) ---
        ElementUnderTest(
            key="btn_back_to_list",
            page_key="plt_users_create",
            test_type="button",
            name="Nút Quay lại danh sách",
            locator_type="xpath",
            locator_value="//button[@aria-label='Quay lại']",
            sample_expected="",
            case_id="STAFF-CREATE-001",
        ),
        ElementUnderTest(
            key="input_email",
            page_key="plt_users_create",
            test_type="input",
            name="Ô nhập Email",
            locator_type="xpath",
            locator_value="//input[@id='email']",
            sample_expected="",
            case_id="STAFF-CREATE-002",
        ),
        ElementUnderTest(
            key="input_password",
            page_key="plt_users_create",
            test_type="input",
            name="Ô nhập Mật khẩu",
            locator_type="xpath",
            locator_value="//input[@id='password']",
            sample_expected="",
            case_id="STAFF-CREATE-003",
        ),
        ElementUnderTest(
            key="input_password_confirm",
            page_key="plt_users_create",
            test_type="input",
            name="Ô Nhập lại mật khẩu",
            locator_type="xpath",
            locator_value="//input[@id='passwordConfirm']",
            sample_expected="",
            case_id="STAFF-CREATE-004",
        ),
        ElementUnderTest(
            key="select_role",
            page_key="plt_users_create",
            test_type="select",
            name="Dropdown Chọn Vai trò",
            locator_type="xpath",
            locator_value="//input[@id='role']/ancestor::div[contains(@class,'ant-select')]",
            sample_expected="Nhân viên",
            case_id="STAFF-CREATE-005",
        ),
        ElementUnderTest(
            key="switch_is_active",
            page_key="plt_users_create",
            test_type="switch",
            name="Công tắc Được đăng nhập",
            locator_type="xpath",
            locator_value="//button[@id='isActive']",
            sample_expected="Hoạt động",
            case_id="STAFF-CREATE-006",
        ),
        ElementUnderTest(
            key="btn_cancel_form",
            page_key="plt_users_create",
            test_type="button",
            name="Nút Hủy bỏ",
            locator_type="xpath",
            locator_value="//button[span[text()='Hủy']]",
            sample_expected="Hủy",
            case_id="STAFF-CREATE-007",
        ),
        ElementUnderTest(
            key="btn_submit_form",
            page_key="plt_users_create",
            test_type="button",
            name="Nút Submit Thêm nhân sự",
            locator_type="xpath",
            locator_value="//button[@type='submit' and span[text()='Thêm nhân sự']]",
            sample_expected="Thêm nhân sự",
            case_id="STAFF-CREATE-008",
        ),
    ]