from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PageUnderTest:
    key: str
    name: str
    path: str
    url: str


@dataclass(frozen=True)
class ElementUnderTest:
    key: str
    page_key: str
    test_type: str
    name: str
    locator_type: str
    locator_value: str
    sample_expected: str = ""
    case_id: str = ""
    steps: str = ""
    expected_result: str = ""
    action_type: str = "text_equals"
    target_path: str = ""


class TestContract:
    pages: List[PageUnderTest] = [
        PageUnderTest(
            key="plt_dashboard",
            name="Trang tổng quan",
            path="/dashboard",
            url="https://courses.plt.pro.vn/dashboard",
        ),
        PageUnderTest(
            key="plt_login",
            name="Trang đăng nhập",
            path="/login",
            url="https://courses.plt.pro.vn/login",
        ),
    ]

    elements: List[ElementUnderTest] = [
        ElementUnderTest(
            key="dashboard_main_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Tiêu đề hero Dashboard",
            locator_type="xpath",
            locator_value="//h1[normalize-space()='Dashboard']",
            sample_expected="Dashboard",
            case_id="DASH-001",
            steps="1. Mở trang /dashboard bằng tài khoản test. 2. Đợi Dashboard tải xong. 3. Lấy text tiêu đề hero.",
            expected_result="Tiêu đề hero hiển thị đúng text Dashboard.",
        ),
        ElementUnderTest(
            key="dashboard_header_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Tiêu đề header vận hành",
            locator_type="xpath",
            locator_value="//h3[normalize-space()='Bảng điều khiển vận hành']",
            sample_expected="Bảng điều khiển vận hành",
            case_id="DASH-002",
            steps="1. Mở trang /dashboard. 2. Đợi header hiển thị. 3. Lấy text tiêu đề header.",
            expected_result="Header hiển thị đúng nội dung Bảng điều khiển vận hành.",
        ),
        ElementUnderTest(
            key="dashboard_rented_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe đang cho thuê",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[1]/*[1]",
            sample_expected="XE ĐANG CHO THUÊ\nCác xe hiện đang ở ngoài với khách.",
            case_id="DASH-003",
            steps="1. Mở Dashboard. 2. Tìm card KPI xe đang cho thuê. 3. Kiểm tra nhãn, mô tả và số liệu trên card.",
            expected_result="Card XE ĐANG CHO THUÊ hiển thị đúng nhãn, mô tả và có số liệu.",
            action_type="contains_all_has_number",
        ),
        ElementUnderTest(
            key="dashboard_ready_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe sẵn sàng hôm nay",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[1]/*[2]",
            sample_expected="XE SẴN SÀNG HÔM NAY\nCó thể bàn giao ngay cho booking tiếp theo.",
            case_id="DASH-004",
            steps="1. Mở Dashboard. 2. Tìm card KPI xe sẵn sàng hôm nay. 3. Kiểm tra nhãn, mô tả và số liệu trên card.",
            expected_result="Card XE SẴN SÀNG HÔM NAY hiển thị đúng nhãn, mô tả và có số liệu.",
            action_type="contains_all_has_number",
        ),
        ElementUnderTest(
            key="dashboard_overdue_booking_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI booking trễ hạn",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[2]/*[1]",
            sample_expected="BOOKING TRỄ HẠN\nCác booking đã quá thời gian trả xe dự kiến.",
            case_id="DASH-005",
            steps="1. Mở Dashboard. 2. Tìm card KPI booking trễ hạn. 3. Kiểm tra nhãn, mô tả và số liệu trên card.",
            expected_result="Card BOOKING TRỄ HẠN hiển thị đúng nhãn, mô tả và có số liệu.",
            action_type="contains_all_has_number",
        ),
        ElementUnderTest(
            key="dashboard_language_dropdown",
            page_key="plt_dashboard",
            test_type="dropdown",
            name="Dropdown ngôn ngữ",
            locator_type="css",
            locator_value=".ant-select",
            sample_expected="English\nTiếng Việt",
            case_id="DASH-006",
            steps="1. Mở Dashboard. 2. Mở dropdown ngôn ngữ. 3. So sánh từng option theo đúng vị trí Expected - Actual.",
            expected_result="Dropdown ngôn ngữ có English ở vị trí 1 và Tiếng Việt ở vị trí 2.",
        ),
        ElementUnderTest(
            key="dashboard_booking_list",
            page_key="plt_dashboard",
            test_type="table",
            name="Danh sách bàn giao sắp tới",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[6]/*[1]",
            sample_expected="Các lượt bàn giao sắp tới",
        ),
        ElementUnderTest(
            key="dashboard_first_booking_row",
            page_key="plt_dashboard",
            test_type="table",
            name="Dòng booking đầu tiên",
            locator_type="xpath",
            locator_value="((//main//div[contains(@class,'grid')])[6]/*[1]//button[contains(., 'BK-')])[1]",
            sample_expected="BK-20260405-9228\tĐang thực hiện\tPhúc Trần Minh\tXem\tNHẬN XE\t19:00 05 thg 4\tTRẢ XE\t19:00 06 thg 4\t60C2-77188\tVinfast VF3",
        ),
        ElementUnderTest(
            key="dashboard_selected_menu_state",
            page_key="plt_dashboard",
            test_type="radio",
            name="Trạng thái menu Dashboard đang chọn",
            locator_type="xpath",
            locator_value="//li[@role='menuitem' and contains(@class, 'ant-menu-item-selected')]",
            sample_expected="Dashboard",
        ),
        ElementUnderTest(
            key="dashboard_logo",
            page_key="plt_dashboard",
            test_type="image",
            name="Logo PLT Solutions",
            locator_type="css",
            locator_value="aside img[alt='PLT Solutions']",
            sample_expected="PLT Solutions",
        ),
        ElementUnderTest(
            key="dashboard_browser_header_title",
            page_key="plt_dashboard",
            test_type="title",
            name="Tiêu đề trang trên header",
            locator_type="xpath",
            locator_value="//h3[normalize-space()='Bảng điều khiển vận hành']",
            sample_expected="Bảng điều khiển vận hành",
        ),
        ElementUnderTest(
            key="dashboard_hero_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Hero tổng quan hiển thị",
            locator_type="xpath",
            locator_value="(//main//section)[1]",
            sample_expected="visible",
            case_id="DASH-007",
            steps="1. Mở Dashboard. 2. Đợi hero section xuất hiện. 3. Kiểm tra element đang hiển thị.",
            expected_result="Hero tổng quan hiển thị trên Dashboard.",
            action_type="visible",
        ),
        ElementUnderTest(
            key="dashboard_quick_actions_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Khối thao tác nhanh hiển thị",
            locator_type="xpath",
            locator_value="(//main//section)[2]",
            sample_expected="visible",
            case_id="DASH-008",
            steps="1. Mở Dashboard. 2. Đợi khối thao tác nhanh xuất hiện. 3. Kiểm tra element đang hiển thị.",
            expected_result="Khối thao tác nhanh hiển thị trên Dashboard.",
            action_type="visible",
        ),
        ElementUnderTest(
            key="dashboard_sidebar_menu",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu sidebar",
            locator_type="css",
            locator_value="ul[role='menu']",
            sample_expected="Dashboard Đặt xe Xe Danh mục xe Tài chính Người dùng",
            case_id="DASH-009",
            steps="1. Mở Dashboard. 2. Lấy danh sách menu sidebar. 3. So sánh nội dung menu theo từng vị trí.",
            expected_result="Menu sidebar hiển thị đủ các module chính theo đúng thứ tự.",
        ),
        ElementUnderTest(
            key="dashboard_menu_item",
            page_key="plt_dashboard",
            test_type="menu",
            name="Item menu Dashboard",
            locator_type="xpath",
            locator_value="//li[@role='menuitem'][.//span[normalize-space()='Dashboard']]",
            sample_expected="Dashboard",
            case_id="DASH-010",
            steps="1. Mở Dashboard. 2. Kiểm tra item Dashboard trên sidebar. 3. Xác nhận item đang tồn tại và đúng text.",
            expected_result="Item Dashboard trên sidebar hiển thị đúng.",
        ),
        ElementUnderTest(
            key="dashboard_quick_booking_list",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở danh sách booking",
            locator_type="xpath",
            locator_value="//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Xem danh sách booking']]",
            sample_expected="/bookings",
            case_id="DASH-011",
            steps="1. Mở Dashboard. 2. Click menu nhanh Xem danh sách booking. 3. Kiểm tra URL sau điều hướng.",
            expected_result="Menu nhanh mở đúng module Booking với URL chứa /bookings.",
            action_type="click_url_contains",
            target_path="/bookings",
        ),
        ElementUnderTest(
            key="dashboard_quick_fleet",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở đội xe",
            locator_type="xpath",
            locator_value="//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Kiểm tra đội xe']]",
            sample_expected="/cars",
            case_id="DASH-012",
            steps="1. Mở Dashboard. 2. Click menu nhanh Kiểm tra đội xe. 3. Kiểm tra URL sau điều hướng.",
            expected_result="Menu nhanh mở đúng module Xe với URL chứa /cars.",
            action_type="click_url_contains",
            target_path="/cars",
        ),
        ElementUnderTest(
            key="dashboard_quick_finance",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở tài chính",
            locator_type="xpath",
            locator_value="//main//h4[normalize-space()='Thao tác nhanh']/ancestor::section//button[.//p[normalize-space()='Mở tài chính']]",
            sample_expected="/finance",
            case_id="DASH-013",
            steps="1. Mở Dashboard. 2. Click menu nhanh Mở tài chính. 3. Kiểm tra URL sau điều hướng.",
            expected_result="Menu nhanh mở đúng module Tài chính với URL chứa /finance.",
            action_type="click_url_contains",
            target_path="/finance",
        ),
        ElementUnderTest(
            key="dashboard_deep_link",
            page_key="plt_dashboard",
            test_type="ui",
            name="Deep link mở Dashboard",
            locator_type="css",
            locator_value="main",
            sample_expected="/dashboard",
            case_id="DASH-014",
            steps="1. Mở trực tiếp URL /dashboard. 2. Đợi trang tải xong. 3. Kiểm tra URL và nội dung chính.",
            expected_result="Deep link /dashboard mở đúng trang tổng quan.",
            action_type="deep_link_url_contains",
            target_path="/dashboard",
        ),
    ]

    @classmethod
    def page_map(cls) -> Dict[str, PageUnderTest]:
        return {page.key: page for page in cls.pages}

    @classmethod
    def elements_for(cls, page_key: str, test_type: str) -> List[ElementUnderTest]:
        return [
            element
            for element in cls.elements
            if element.page_key == page_key and element.test_type == test_type
        ]
