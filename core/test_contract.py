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
    sample_expected: str


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
        ),
        ElementUnderTest(
            key="dashboard_header_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Tiêu đề header vận hành",
            locator_type="xpath",
            locator_value="//h3[normalize-space()='Bảng điều khiển vận hành']",
            sample_expected="Bảng điều khiển vận hành",
        ),
        ElementUnderTest(
            key="dashboard_rented_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe đang cho thuê",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[1]/*[1]",
            sample_expected="XE ĐANG CHO THUÊ\n9\nCác xe hiện đang ở ngoài với khách.",
        ),
        ElementUnderTest(
            key="dashboard_ready_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe sẵn sàng hôm nay",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[1]/*[2]",
            sample_expected="XE SẴN SÀNG HÔM NAY\n43\nCó thể bàn giao ngay cho booking tiếp theo.",
        ),
        ElementUnderTest(
            key="dashboard_overdue_booking_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI booking trễ hạn",
            locator_type="xpath",
            locator_value="(//main//div[contains(@class,'grid')])[2]/*[1]",
            sample_expected="BOOKING TRỄ HẠN\n63\nCác booking đã quá thời gian trả xe dự kiến.",
        ),
        ElementUnderTest(
            key="dashboard_language_dropdown",
            page_key="plt_dashboard",
            test_type="dropdown",
            name="Dropdown ngôn ngữ",
            locator_type="css",
            locator_value=".ant-select",
            sample_expected="English\nTiếng Việt",
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
            sample_expected="BK-20260405-9228 Đang thực hiện Phúc Trần Minh Xem NHẬN XE 19:00 05 thg 4 TRẢ XE 19:00 06 thg 4 60C2-77188 Vinfast VF3",
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
        ),
        ElementUnderTest(
            key="dashboard_quick_actions_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Khối thao tác nhanh hiển thị",
            locator_type="xpath",
            locator_value="(//main//section)[2]",
            sample_expected="visible",
        ),
        ElementUnderTest(
            key="dashboard_sidebar_menu",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu sidebar",
            locator_type="css",
            locator_value="ul[role='menu']",
            sample_expected="Dashboard Đặt xe Xe Danh mục xe Tài chính Người dùng",
        ),
        ElementUnderTest(
            key="dashboard_menu_item",
            page_key="plt_dashboard",
            test_type="menu",
            name="Item menu Dashboard",
            locator_type="xpath",
            locator_value="//li[@role='menuitem'][.//span[normalize-space()='Dashboard']]",
            sample_expected="Dashboard",
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
