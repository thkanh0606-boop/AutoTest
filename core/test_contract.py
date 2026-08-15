from dataclasses import dataclass
from typing import Dict, List


# =========================================================
# PAGE CONTRACT
# =========================================================

@dataclass(frozen=True)
class PageUnderTest:
    key: str
    name: str
    path: str
    url: str


# =========================================================
# ELEMENT CONTRACT
# =========================================================

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


# =========================================================
# TEST CONTRACT
# =========================================================

class TestContract:

    # =====================================================
    # PAGES
    # =====================================================

    pages: List[PageUnderTest] = [

        # =================================================
        # DASHBOARD
        # =================================================

        PageUnderTest(
            key="plt_dashboard",
            name="Trang tổng quan",
            path="/dashboard",
            url="https://courses.plt.pro.vn/dashboard",
        ),

        # =================================================
        # LOGIN
        # =================================================

        PageUnderTest(
            key="plt_login",
            name="Trang đăng nhập",
            path="/login",
            url="https://courses.plt.pro.vn/login",
        ),

        # =================================================
        # VEHICLE CATALOG
        # =================================================

        PageUnderTest(
            key="plt_vehicle_catalog",
            name="Danh mục xe",
            path="/cars/catalog",
            url="https://courses.plt.pro.vn/cars/catalog",
        ),

        # =================================================
        # BOOKING MANAGEMENT
        # =================================================

        PageUnderTest(
            key="plt_booking",
            name="Quản lý đặt xe",
            path="/bookings",
            url="https://courses.plt.pro.vn/bookings",
        ),
    ]

    # =====================================================
    # ELEMENTS
    # =====================================================

    elements: List[ElementUnderTest] = [

        # =================================================
        # =================================================
        # DASHBOARD
        # =================================================
        # =================================================

        # -------------------------------------------------
        # DASHBOARD - LABEL
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_main_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Tiêu đề hero Dashboard",
            locator_type="xpath",
            locator_value="//h1[normalize-space()='Dashboard']",
            sample_expected="Dashboard",
            case_id="DASH-001",
            steps=(
                "1. Mở trang /dashboard bằng tài khoản test. "
                "2. Đợi Dashboard tải xong. "
                "3. Lấy text tiêu đề hero."
            ),
            expected_result=(
                "Tiêu đề hero hiển thị đúng text Dashboard."
            ),
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
            steps=(
                "1. Mở trang /dashboard. "
                "2. Đợi header hiển thị. "
                "3. Lấy text tiêu đề header."
            ),
            expected_result=(
                "Header hiển thị đúng nội dung "
                "Bảng điều khiển vận hành."
            ),
        ),

        ElementUnderTest(
            key="dashboard_rented_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe đang cho thuê",
            locator_type="xpath",
            locator_value=(
                "(//main//div[contains(@class,'grid')])[1]/*[1]"
            ),
            sample_expected=(
                "XE ĐANG CHO THUÊ\n"
                "Các xe hiện đang ở ngoài với khách."
            ),
            case_id="DASH-003",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI xe đang cho thuê. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card XE ĐANG CHO THUÊ hiển thị đúng "
                "nhãn, mô tả và có số liệu."
            ),
            action_type="contains_all_has_number",
        ),

        ElementUnderTest(
            key="dashboard_ready_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe sẵn sàng hôm nay",
            locator_type="xpath",
            locator_value=(
                "(//main//div[contains(@class,'grid')])[1]/*[2]"
            ),
            sample_expected=(
                "XE SẴN SÀNG HÔM NAY\n"
                "Có thể bàn giao ngay cho booking tiếp theo."
            ),
            case_id="DASH-004",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI xe sẵn sàng hôm nay. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card XE SẴN SÀNG HÔM NAY hiển thị đúng "
                "nhãn, mô tả và có số liệu."
            ),
            action_type="contains_all_has_number",
        ),

        ElementUnderTest(
            key="dashboard_overdue_booking_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI booking trễ hạn",
            locator_type="xpath",
            locator_value=(
                "(//main//div[contains(@class,'grid')])[2]/*[1]"
            ),
            sample_expected=(
                "BOOKING TRỄ HẠN\n"
                "Các booking đã quá thời gian trả xe dự kiến."
            ),
            case_id="DASH-005",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI booking trễ hạn. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card BOOKING TRỄ HẠN hiển thị đúng "
                "nhãn, mô tả và có số liệu."
            ),
            action_type="contains_all_has_number",
        ),

        # -------------------------------------------------
        # DASHBOARD - DROPDOWN
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_language_dropdown",
            page_key="plt_dashboard",
            test_type="dropdown",
            name="Dropdown ngôn ngữ",
            locator_type="css",
            locator_value=".ant-select",
            sample_expected="English\nTiếng Việt",
            case_id="DASH-006",
            steps=(
                "1. Mở Dashboard. "
                "2. Mở dropdown ngôn ngữ. "
                "3. So sánh từng option theo đúng vị trí "
                "Expected - Actual."
            ),
            expected_result=(
                "Dropdown ngôn ngữ có English ở vị trí 1 "
                "và Tiếng Việt ở vị trí 2."
            ),
        ),

        # -------------------------------------------------
        # DASHBOARD - TABLE
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_booking_list",
            page_key="plt_dashboard",
            test_type="table",
            name="Danh sách bàn giao sắp tới",
            locator_type="xpath",
            locator_value=(
                "(//main//div[contains(@class,'grid')])[6]/*[1]"
            ),
            sample_expected="Các lượt bàn giao sắp tới",
        ),

        ElementUnderTest(
            key="dashboard_first_booking_row",
            page_key="plt_dashboard",
            test_type="table",
            name="Dòng booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "((//main//div[contains(@class,'grid')])[6]"
                "/*[1]//button[contains(., 'BK-')])[1]"
            ),
            sample_expected=(
                "BK-20260405-9228\t"
                "Đang thực hiện\t"
                "Phúc Trần Minh\t"
                "Xem\t"
                "NHẬN XE\t"
                "19:00 05 thg 4\t"
                "TRẢ XE\t"
                "19:00 06 thg 4\t"
                "60C2-77188\t"
                "Vinfast VF3"
            ),
        ),

        # -------------------------------------------------
        # DASHBOARD - RADIO
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_selected_menu_state",
            page_key="plt_dashboard",
            test_type="radio",
            name="Trạng thái menu Dashboard đang chọn",
            locator_type="xpath",
            locator_value=(
                "//li[@role='menuitem' and "
                "contains(@class, 'ant-menu-item-selected')]"
            ),
            sample_expected="Dashboard",
        ),

        # -------------------------------------------------
        # DASHBOARD - IMAGE
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_logo",
            page_key="plt_dashboard",
            test_type="image",
            name="Logo PLT Solutions",
            locator_type="css",
            locator_value="aside img[alt='PLT Solutions']",
            sample_expected="PLT Solutions",
        ),

        # -------------------------------------------------
        # DASHBOARD - TITLE
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_browser_header_title",
            page_key="plt_dashboard",
            test_type="title",
            name="Tiêu đề trang trên header",
            locator_type="xpath",
            locator_value=(
                "//h3[normalize-space()='Bảng điều khiển vận hành']"
            ),
            sample_expected="Bảng điều khiển vận hành",
        ),

        # -------------------------------------------------
        # DASHBOARD - UI
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_hero_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Hero tổng quan hiển thị",
            locator_type="xpath",
            locator_value="(//main//section)[1]",
            sample_expected="visible",
            case_id="DASH-007",
            steps=(
                "1. Mở Dashboard. "
                "2. Đợi hero section xuất hiện. "
                "3. Kiểm tra element đang hiển thị."
            ),
            expected_result=(
                "Hero tổng quan hiển thị trên Dashboard."
            ),
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
            steps=(
                "1. Mở Dashboard. "
                "2. Đợi khối thao tác nhanh xuất hiện. "
                "3. Kiểm tra element đang hiển thị."
            ),
            expected_result=(
                "Khối thao tác nhanh hiển thị trên Dashboard."
            ),
            action_type="visible",
        ),

        # -------------------------------------------------
        # DASHBOARD - MENU
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_sidebar_menu",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu sidebar",
            locator_type="css",
            locator_value="ul[role='menu']",
            sample_expected=(
                "Dashboard Đặt xe Xe Danh mục xe "
                "Tài chính Người dùng"
            ),
            case_id="DASH-009",
            steps=(
                "1. Mở Dashboard. "
                "2. Lấy danh sách menu sidebar. "
                "3. So sánh nội dung menu theo từng vị trí."
            ),
            expected_result=(
                "Menu sidebar hiển thị đủ các module chính "
                "theo đúng thứ tự."
            ),
        ),

        ElementUnderTest(
            key="dashboard_menu_item",
            page_key="plt_dashboard",
            test_type="menu",
            name="Item menu Dashboard",
            locator_type="xpath",
            locator_value=(
                "//li[@role='menuitem']"
                "[.//span[normalize-space()='Dashboard']]"
            ),
            sample_expected="Dashboard",
            case_id="DASH-010",
            steps=(
                "1. Mở Dashboard. "
                "2. Kiểm tra item Dashboard trên sidebar. "
                "3. Xác nhận item đang tồn tại và đúng text."
            ),
            expected_result=(
                "Item Dashboard trên sidebar hiển thị đúng."
            ),
        ),

        ElementUnderTest(
            key="dashboard_quick_booking_list",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở danh sách booking",
            locator_type="xpath",
            locator_value=(
                "//main//h4[normalize-space()='Thao tác nhanh']"
                "/ancestor::section//button"
                "[.//p[normalize-space()='Xem danh sách booking']]"
            ),
            sample_expected="/bookings",
            case_id="DASH-011",
            steps=(
                "1. Mở Dashboard. "
                "2. Click menu nhanh Xem danh sách booking. "
                "3. Kiểm tra URL sau điều hướng."
            ),
            expected_result=(
                "Menu nhanh mở đúng module Booking "
                "với URL chứa /bookings."
            ),
            action_type="click_url_contains",
            target_path="/bookings",
        ),

        ElementUnderTest(
            key="dashboard_quick_fleet",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở đội xe",
            locator_type="xpath",
            locator_value=(
                "//main//h4[normalize-space()='Thao tác nhanh']"
                "/ancestor::section//button"
                "[.//p[normalize-space()='Kiểm tra đội xe']]"
            ),
            sample_expected="/cars",
            case_id="DASH-012",
            steps=(
                "1. Mở Dashboard. "
                "2. Click menu nhanh Kiểm tra đội xe. "
                "3. Kiểm tra URL sau điều hướng."
            ),
            expected_result=(
                "Menu nhanh mở đúng module Xe "
                "với URL chứa /cars."
            ),
            action_type="click_url_contains",
            target_path="/cars",
        ),

        ElementUnderTest(
            key="dashboard_quick_finance",
            page_key="plt_dashboard",
            test_type="menu",
            name="Menu nhanh mở tài chính",
            locator_type="xpath",
            locator_value=(
                "//main//h4[normalize-space()='Thao tác nhanh']"
                "/ancestor::section//button"
                "[.//p[normalize-space()='Mở tài chính']]"
            ),
            sample_expected="/finance",
            case_id="DASH-013",
            steps=(
                "1. Mở Dashboard. "
                "2. Click menu nhanh Mở tài chính. "
                "3. Kiểm tra URL sau điều hướng."
            ),
            expected_result=(
                "Menu nhanh mở đúng module Tài chính "
                "với URL chứa /finance."
            ),
            action_type="click_url_contains",
            target_path="/finance",
        ),

        # -------------------------------------------------
        # DASHBOARD - DEEP LINK
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_deep_link",
            page_key="plt_dashboard",
            test_type="ui",
            name="Deep link mở Dashboard",
            locator_type="css",
            locator_value="main",
            sample_expected="/dashboard",
            case_id="DASH-014",
            steps=(
                "1. Mở trực tiếp URL /dashboard. "
                "2. Đợi trang tải xong. "
                "3. Kiểm tra URL và nội dung chính."
            ),
            expected_result=(
                "Deep link /dashboard mở đúng trang tổng quan."
            ),
            action_type="deep_link_url_contains",
            target_path="/dashboard",
        ),

        # =================================================
        # =================================================
        # VEHICLE CATALOG
        # =================================================
        # =================================================

        ElementUnderTest(
            key="catalog_page_title",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Tiêu đề Danh mục xe",
            locator_type="xpath",
            locator_value=(
                "(//*[normalize-space()='Danh mục xe' "
                "and not(ancestor::aside)])[1]"
            ),
            sample_expected="Danh mục xe",
            case_id="CAT-001",
            steps=(
                "1. Mở /cars/catalog. "
                "2. Đợi trang tải xong. "
                "3. Lấy text tiêu đề."
            ),
            expected_result=(
                "Tiêu đề hiển thị đúng Danh mục xe."
            ),
        ),

        ElementUnderTest(
            key="catalog_total_brand_label",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Nhãn Tổng số hãng",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Tổng số hãng' "
                "or normalize-space()='TỔNG SỐ HÃNG']"
            ),
            sample_expected="Tổng số hãng",
            case_id="CAT-002",
        ),

        ElementUnderTest(
            key="catalog_active_brand_label",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Nhãn Hãng đang hoạt động",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Hãng đang hoạt động' "
                "or normalize-space()='HÃNG ĐANG HOẠT ĐỘNG']"
            ),
            sample_expected="Hãng đang hoạt động",
            case_id="CAT-003",
        ),

        ElementUnderTest(
            key="catalog_total_model_label",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Nhãn Tổng số mẫu xe",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Tổng số mẫu xe' "
                "or normalize-space()='TỔNG SỐ MẪU XE']"
            ),
            sample_expected="Tổng số mẫu xe",
            case_id="CAT-004",
        ),

        ElementUnderTest(
            key="catalog_brand_section_title",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Tiêu đề Danh sách hãng xe",
            locator_type="xpath",
            locator_value="//h4[normalize-space()='Danh sách hãng xe']",
            sample_expected="Danh sách hãng xe",
            case_id="CAT-005",
        ),

        ElementUnderTest(
            key="catalog_model_section_title",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Tiêu đề Danh sách mẫu xe",
            locator_type="xpath",
            locator_value="//h4[normalize-space()='Danh sách mẫu xe']",
            sample_expected="Danh sách mẫu xe",
            case_id="CAT-006",
        ),

        ElementUnderTest(
            key="catalog_add_brand_button",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Nút Thêm hãng xe",
            locator_type="xpath",
            locator_value=(
                "//button[.//span[normalize-space()='Thêm hãng xe'] "
                "or normalize-space()='Thêm hãng xe']"
            ),
            sample_expected="Thêm hãng xe",
            case_id="CAT-007",
        ),

        ElementUnderTest(
            key="catalog_add_model_button",
            page_key="plt_vehicle_catalog",
            test_type="label",
            name="Nút Thêm mẫu xe",
            locator_type="xpath",
            locator_value=(
                "//button[.//span[normalize-space()='Thêm mẫu xe'] "
                "or normalize-space()='Thêm mẫu xe']"
            ),
            sample_expected="Thêm mẫu xe",
            case_id="CAT-008",
        ),

        ElementUnderTest(
            key="catalog_brand_filter",
            page_key="plt_vehicle_catalog",
            test_type="dropdown",
            name="Dropdown lọc Hãng ở bảng Mẫu",
            locator_type="xpath",
            locator_value=(
                "//h4[normalize-space()='Danh sách mẫu xe']"
                "/ancestor::section[1]//*[@role='combobox'][1]"
            ),
            sample_expected="",
            case_id="CAT-009",
        ),

        ElementUnderTest(
            key="catalog_brand_table",
            page_key="plt_vehicle_catalog",
            test_type="table",
            name="Bảng danh sách hãng xe",
            locator_type="xpath",
            locator_value=(
                "//h4[normalize-space()='Danh sách hãng xe']"
                "/ancestor::section[1]//table"
            ),
            sample_expected="",
            case_id="CAT-010",
        ),

        ElementUnderTest(
            key="catalog_model_table",
            page_key="plt_vehicle_catalog",
            test_type="table",
            name="Bảng danh sách mẫu xe",
            locator_type="xpath",
            locator_value=(
                "//h4[normalize-space()='Danh sách mẫu xe']"
                "/ancestor::section[1]//table"
            ),
            sample_expected="",
            case_id="CAT-011",
        ),

        ElementUnderTest(
            key="catalog_active_status",
            page_key="plt_vehicle_catalog",
            test_type="radio",
            name="Trạng thái Đang hoạt động",
            locator_type="xpath",
            locator_value=(
                "(//span[contains(@class,'ant-tag') "
                "and normalize-space()='Đang hoạt động'])[1]"
            ),
            sample_expected="Đang hoạt động",
            case_id="CAT-012",
        ),

        ElementUnderTest(
            key="catalog_logo",
            page_key="plt_vehicle_catalog",
            test_type="image",
            name="Logo PLT Solutions",
            locator_type="css",
            locator_value="aside img[alt='PLT Solutions']",
            sample_expected="PLT Solutions",
            case_id="CAT-013",
        ),

        ElementUnderTest(
            key="catalog_header_title",
            page_key="plt_vehicle_catalog",
            test_type="title",
            name="Tiêu đề trang Danh mục xe",
            locator_type="xpath",
            locator_value=(
                "(//*[normalize-space()='Danh mục xe' "
                "and not(ancestor::aside)])[1]"
            ),
            sample_expected="Danh mục xe",
            case_id="CAT-014",
        ),

        ElementUnderTest(
            key="catalog_brand_section_visible",
            page_key="plt_vehicle_catalog",
            test_type="ui",
            name="Khu Danh sách hãng xe hiển thị",
            locator_type="xpath",
            locator_value=(
                "//h4[normalize-space()='Danh sách hãng xe']"
                "/ancestor::section[1]"
            ),
            sample_expected="visible",
            case_id="CAT-015",
            action_type="visible",
        ),

        ElementUnderTest(
            key="catalog_model_section_visible",
            page_key="plt_vehicle_catalog",
            test_type="ui",
            name="Khu Danh sách mẫu xe hiển thị",
            locator_type="xpath",
            locator_value=(
                "//h4[normalize-space()='Danh sách mẫu xe']"
                "/ancestor::section[1]"
            ),
            sample_expected="visible",
            case_id="CAT-016",
            action_type="visible",
        ),

        ElementUnderTest(
            key="catalog_sidebar_menu_item",
            page_key="plt_vehicle_catalog",
            test_type="menu",
            name="Item menu Danh mục xe",
            locator_type="xpath",
            locator_value=(
                "//li[@role='menuitem']"
                "[.//span[normalize-space()='Danh mục xe']]"
            ),
            sample_expected="Danh mục xe",
            case_id="CAT-017",
        ),

        # =================================================
        # =================================================
        # BOOKING MANAGEMENT
        # =================================================
        # =================================================

        # -------------------------------------------------
        # BOOKING - LABEL
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_page_title",
            page_key="plt_booking",
            test_type="label",
            name="Tiêu đề Quản lý đặt xe",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Quản lý đặt xe' "
                "and not(ancestor::aside)]"
            ),
            sample_expected="Quản lý đặt xe",
            case_id="BOOK-001",
            steps=(
                "1. Mở trang /bookings. "
                "2. Đợi trang tải xong. "
                "3. Kiểm tra tiêu đề Quản lý đặt xe."
            ),
            expected_result=(
                "Tiêu đề Quản lý đặt xe hiển thị đúng."
            ),
        ),

        ElementUnderTest(
            key="booking_list_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn khu vực danh sách booking",
            locator_type="xpath",
            locator_value=(
                "//main//*["
                "contains(normalize-space(), 'booking') "
                "or contains(normalize-space(), 'Booking') "
                "or contains(normalize-space(), 'Đặt xe')"
                "]"
            ),
            sample_expected="",
            case_id="BOOK-002",
            steps=(
                "1. Mở trang /bookings. "
                "2. Tìm khu vực danh sách booking. "
                "3. Kiểm tra nhãn hiển thị."
            ),
            expected_result=(
                "Khu vực danh sách booking hiển thị đúng."
            ),
        ),

        # -------------------------------------------------
        # BOOKING - DROPDOWN
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_dropdown",
            page_key="plt_booking",
            test_type="dropdown",
            name="Dropdown ngôn ngữ trên trang Booking",
            locator_type="css",
            locator_value=".ant-select",
            sample_expected="Tiếng Việt\nEnglish",
            case_id="BOOK-003",
            steps=(
                "1. Mở trang /bookings. "
                "2. Tìm dropdown ngôn ngữ. "
                "3. Click dropdown. "
                "4. Kiểm tra các option."
            ),
            expected_result=(
                "Dropdown ngôn ngữ hiển thị đúng "
                "và có thể mở được."
            ),
        ),

        # -------------------------------------------------
        # BOOKING - TABLE
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_table",
            page_key="plt_booking",
            test_type="table",
            name="Bảng danh sách booking",
            locator_type="xpath",
            locator_value="//main//table",
            sample_expected=(
                "Đơn thuê\n"
                "Xe\n"
                "Ngày thuê\n"
                "Trạng thái\n"
                "Thanh toán\n"
                "Tệp\n"
                "Tổng tiền\n"
                "Thao tác"
            ),
            case_id="BOOK-004",
            steps=(
                "1. Mở trang /bookings. "
                "2. Đợi danh sách booking tải xong. "
                "3. Kiểm tra bảng dữ liệu. "
                "4. Kiểm tra các header."
            ),
            expected_result=(
                "Bảng booking hiển thị đầy đủ "
                "và có các cột dữ liệu chính."
            ),
            action_type="table_headers",
        ),

        ElementUnderTest(
            key="booking_first_row",
            page_key="plt_booking",
            test_type="table",
            name="Dòng booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]"
            ),
            sample_expected=(
                "BK-\t"
                "Xe\t"
                "Ngày thuê\t"
                "Trạng thái\t"
                "Thanh toán\t"
                "Tổng tiền"
            ),
            case_id="BOOK-005",
            steps=(
                "1. Mở trang /bookings. "
                "2. Bỏ qua dòng đo kích thước ẩn của Ant Design. "
                "3. Lấy dòng booking đầu tiên. "
                "4. Kiểm tra dữ liệu trên dòng."
            ),
            expected_result=(
                "Dòng booking đầu tiên hiển thị dữ liệu "
                "và mã booking bắt đầu bằng BK-."
            ),
            action_type="contains_booking_code",
        ),

        ElementUnderTest(
            key="booking_first_row_booking_code",
            page_key="plt_booking",
            test_type="table",
            name="Mã booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[1]"
            ),
            sample_expected="BK-20260815-6651",
            case_id="BOOK-006",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Đơn thuê."
            ),
            expected_result=(
                "Mã booking đầu tiên hiển thị và "
                "có định dạng bắt đầu bằng BK-."
            ),
            action_type="starts_with",
        ),

        ElementUnderTest(
            key="booking_first_row_vehicle",
            page_key="plt_booking",
            test_type="table",
            name="Thông tin xe của booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[2]"
            ),
            sample_expected="Tên xe",
            case_id="BOOK-007",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Xe."
            ),
            expected_result=(
                "Thông tin xe của booking đầu tiên "
                "được hiển thị."
            ),
            action_type="not_empty",
        ),

        ElementUnderTest(
            key="booking_first_row_rental_date",
            page_key="plt_booking",
            test_type="table",
            name="Ngày thuê booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[3]"
            ),
            sample_expected="Ngày thuê",
            case_id="BOOK-008",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Ngày thuê."
            ),
            expected_result=(
                "Ngày thuê booking đầu tiên được hiển thị."
            ),
            action_type="not_empty",
        ),

        ElementUnderTest(
            key="booking_first_row_status",
            page_key="plt_booking",
            test_type="table",
            name="Trạng thái booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[4]"
            ),
            sample_expected=(
                "Nháp / Đang thực hiện / Quá hạn / Hoàn tất"
            ),
            case_id="BOOK-009",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Trạng thái."
            ),
            expected_result=(
                "Cột Trạng thái hiển thị trạng thái "
                "của booking."
            ),
            action_type="not_empty",
        ),

        ElementUnderTest(
            key="booking_first_row_payment",
            page_key="plt_booking",
            test_type="table",
            name="Trạng thái thanh toán booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[5]"
            ),
            sample_expected=(
                "Chưa thanh toán / "
                "Thanh toán một phần / "
                "Đã thanh toán"
            ),
            case_id="BOOK-010",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Thanh toán."
            ),
            expected_result=(
                "Cột Thanh toán hiển thị đúng "
                "trạng thái thanh toán."
            ),
            action_type="not_empty",
        ),

        ElementUnderTest(
            key="booking_first_row_file",
            page_key="plt_booking",
            test_type="table",
            name="Tệp booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[6]"
            ),
            sample_expected="Tệp",
            case_id="BOOK-011",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Tệp."
            ),
            expected_result=(
                "Cột Tệp hiển thị đúng trạng thái "
                "hoặc nút thao tác tương ứng."
            ),
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_first_row_total",
            page_key="plt_booking",
            test_type="table",
            name="Tổng tiền booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//table//tbody//tr["
                "not(@aria-hidden='true') "
                "and normalize-space(.)!=''"
                "])[1]//td[7]"
            ),
            sample_expected="500.000 ₫",
            case_id="BOOK-012",
            steps=(
                "1. Mở trang /bookings. "
                "2. Lấy dòng booking đầu tiên. "
                "3. Kiểm tra cột Tổng tiền."
            ),
            expected_result=(
                "Tổng tiền booking đầu tiên được hiển thị."
            ),
            action_type="not_empty",
        ),

        # -------------------------------------------------
        # BOOKING - CHECKBOX
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_checkbox",
            page_key="plt_booking",
            test_type="radio",
            name="Checkbox trong bảng Booking",
            locator_type="xpath",
            locator_value=(
                "(//main//table//input[@type='checkbox'])[1]"
            ),
            sample_expected="checkbox",
            case_id="BOOK-013",
            steps=(
                "1. Mở trang /bookings. "
                "2. Tìm checkbox trong bảng booking. "
                "3. Kiểm tra checkbox hiển thị."
            ),
            expected_result=(
                "Checkbox trong bảng booking tồn tại."
            ),
            action_type="exists",
        ),

        # -------------------------------------------------
        # BOOKING - IMAGE
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_logo",
            page_key="plt_booking",
            test_type="image",
            name="Logo PLT Solutions",
            locator_type="css",
            locator_value="aside img[alt='PLT Solutions']",
            sample_expected="PLT Solutions",
            case_id="BOOK-014",
            steps=(
                "1. Mở trang /bookings. "
                "2. Kiểm tra logo trên sidebar."
            ),
            expected_result=(
                "Logo PLT Solutions hiển thị đúng."
            ),
        ),

        # -------------------------------------------------
        # BOOKING - TITLE
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_title",
            page_key="plt_booking",
            test_type="title",
            name="Tiêu đề trang Booking",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Quản lý đặt xe' "
                "and not(ancestor::aside)]"
            ),
            sample_expected="Quản lý đặt xe",
            case_id="BOOK-015",
            steps=(
                "1. Mở trang /bookings. "
                "2. Kiểm tra tiêu đề trang."
            ),
            expected_result=(
                "Tiêu đề trang Booking hiển thị đúng."
            ),
        ),

        # -------------------------------------------------
        # BOOKING - UI
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_main_section",
            page_key="plt_booking",
            test_type="ui",
            name="Khu vực quản lý booking hiển thị",
            locator_type="xpath",
            locator_value="//main",
            sample_expected="visible",
            case_id="BOOK-016",
            steps=(
                "1. Mở trang /bookings. "
                "2. Đợi nội dung chính tải xong. "
                "3. Kiểm tra khu vực quản lý booking."
            ),
            expected_result=(
                "Khu vực quản lý booking hiển thị."
            ),
            action_type="visible",
        ),

        ElementUnderTest(
            key="booking_table_section_visible",
            page_key="plt_booking",
            test_type="ui",
            name="Khu vực bảng booking hiển thị",
            locator_type="xpath",
            locator_value=(
                "(//main//table/"
                "ancestor::*[self::section or self::div][1])[1]"
            ),
            sample_expected="visible",
            case_id="BOOK-017",
            steps=(
                "1. Mở trang /bookings. "
                "2. Đợi bảng booking tải xong. "
                "3. Kiểm tra khu vực bảng."
            ),
            expected_result=(
                "Khu vực bảng booking hiển thị."
            ),
            action_type="visible",
        ),

        # -------------------------------------------------
        # BOOKING - MENU
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_sidebar_menu",
            page_key="plt_booking",
            test_type="menu",
            name="Menu sidebar Booking",
            locator_type="css",
            locator_value="ul[role='menu']",
            sample_expected=(
                "Dashboard Đặt xe Xe Danh mục xe "
                "Tài chính Người dùng"
            ),
            case_id="BOOK-018",
            steps=(
                "1. Mở trang /bookings. "
                "2. Kiểm tra menu sidebar."
            ),
            expected_result=(
                "Menu sidebar hiển thị đúng."
            ),
        ),

        ElementUnderTest(
            key="booking_sidebar_menu_item",
            page_key="plt_booking",
            test_type="menu",
            name="Item menu Đặt xe",
            locator_type="xpath",
            locator_value=(
                "//li[@role='menuitem']"
                "[.//span[contains(normalize-space(), 'Đặt xe')]]"
            ),
            sample_expected="Đặt xe",
            case_id="BOOK-019",
            steps=(
                "1. Mở trang /bookings. "
                "2. Kiểm tra item menu Đặt xe."
            ),
            expected_result=(
                "Item menu Đặt xe hiển thị đúng."
            ),
        ),

        # -------------------------------------------------
        # BOOKING - PAGINATION
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_pagination",
            page_key="plt_booking",
            test_type="ui",
            name="Phân trang danh sách booking",
            locator_type="css",
            locator_value=".ant-pagination",
            sample_expected="pagination",
            case_id="BOOK-020",
            steps=(
                "1. Mở trang /bookings. "
                "2. Cuộn xuống cuối danh sách. "
                "3. Kiểm tra khu vực phân trang."
            ),
            expected_result=(
                "Khu vực phân trang của danh sách booking "
                "hiển thị đúng nếu danh sách có nhiều dữ liệu."
            ),
            action_type="exists",
        ),
    ]

    # =====================================================
    # PAGE MAP
    # =====================================================

    @classmethod
    def page_map(cls) -> Dict[str, PageUnderTest]:
        return {
            page.key: page
            for page in cls.pages
        }

    # =====================================================
    # GET ELEMENTS BY PAGE + TEST TYPE
    # =====================================================

    @classmethod
    def elements_for(
        cls,
        page_key: str,
        test_type: str,
    ) -> List[ElementUnderTest]:

        return [
            element
            for element in cls.elements
            if (
                element.page_key == page_key
                and element.test_type == test_type
            )
        ]