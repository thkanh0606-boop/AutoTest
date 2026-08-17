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

        # -------------------------------------------------
        # DASHBOARD
        # -------------------------------------------------

        PageUnderTest(
            key="plt_dashboard",
            name="Trang tổng quan",
            path="/dashboard",
            url="https://courses.plt.pro.vn/dashboard",
        ),

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        PageUnderTest(
            key="plt_login",
            name="Trang đăng nhập",
            path="/login",
            url="https://courses.plt.pro.vn/login",
        ),

        # -------------------------------------------------
        # VEHICLE CATALOG
        # -------------------------------------------------

        PageUnderTest(
            key="plt_vehicle_catalog",
            name="Danh mục xe",
            path="/cars/catalog",
            url="https://courses.plt.pro.vn/cars/catalog",
        ),

        # -------------------------------------------------
        # BOOKING MANAGEMENT
        # -------------------------------------------------

        PageUnderTest(
            key="plt_booking",
            name="Quản lý đặt xe",
            path="/bookings",
            url="https://courses.plt.pro.vn/bookings",
        ),

        # -------------------------------------------------
        # STAFF MANAGEMENT
        # -------------------------------------------------

        PageUnderTest(
            key="plt_user",
            name="Nhân sự",
            path="/users",
            url="https://courses.plt.pro.vn/users",
        ),
    ]

    # =====================================================
    # ELEMENTS
    # =====================================================

    elements: List[ElementUnderTest] = [

        # =================================================
        #
        # DASHBOARD
        #
        # =================================================

        ElementUnderTest(
            key="dashboard_main_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Tiêu đề trang Tổng quan",
            locator_type="xpath",
            locator_value="//header//h3[normalize-space()='Tổng quan']",
            sample_expected="Tổng quan",
            case_id="DASH-001",
            steps=(
                "1. Mở trang /dashboard bằng tài khoản test. "
                "2. Đợi Dashboard tải xong. "
                "3. Lấy text tiêu đề trang."
            ),
            expected_result=(
                "Tiêu đề trang hiển thị đúng text Tổng quan."
            ),
        ),

        ElementUnderTest(
            key="dashboard_header_title",
            page_key="plt_dashboard",
            test_type="label",
            name="Mô tả header tổng quan",
            locator_type="xpath",
            locator_value=(
                "//header//*[normalize-space()="
                "'Nhận xe, trả xe và việc cần xử lý trong ngày.']"
            ),
            sample_expected="Nhận xe, trả xe và việc cần xử lý trong ngày.",
            case_id="DASH-002",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Đợi phần mô tả header hiển thị. "
                "3. Lấy text mô tả header."
            ),
            expected_result=(
                "Header hiển thị đúng mô tả vận hành trong ngày."
            ),
        ),

        ElementUnderTest(
            key="dashboard_rented_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI nhận xe hôm nay",
            locator_type="xpath",
            locator_value=(
                "//main//button[.//span[normalize-space()='Nhận xe hôm nay']]"
            ),
            sample_expected=(
                "NHẬN XE HÔM NAY\n"
                "Đơn thuê bắt đầu trong ngày."
            ),
            case_id="DASH-003",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI nhận xe hôm nay. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card NHẬN XE HÔM NAY hiển thị đúng "
                "nhãn, mô tả và có số liệu."
            ),
            action_type="contains_all_has_number",
        ),

        ElementUnderTest(
            key="dashboard_ready_cars_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI xe sẵn sàng",
            locator_type="xpath",
            locator_value=(
                "//main//button[.//span[normalize-space()='Xe sẵn sàng']]"
            ),
            sample_expected=(
                "XE SẴN SÀNG\n"
                "Có thể giao ngay."
            ),
            case_id="DASH-004",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI xe sẵn sàng. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card XE SẴN SÀNG hiển thị đúng "
                "nhãn, mô tả và có số liệu."
            ),
            action_type="contains_all_has_number",
        ),

        ElementUnderTest(
            key="dashboard_overdue_booking_value",
            page_key="plt_dashboard",
            test_type="label",
            name="KPI quá hạn trả",
            locator_type="xpath",
            locator_value=(
                "//main//button[.//span[normalize-space()='Quá hạn trả']]"
            ),
            sample_expected=(
                "QUÁ HẠN TRẢ\n"
                "Đã quá giờ trả xe dự kiến."
            ),
            case_id="DASH-005",
            steps=(
                "1. Mở Dashboard. "
                "2. Tìm card KPI quá hạn trả. "
                "3. Kiểm tra nhãn, mô tả và số liệu trên card."
            ),
            expected_result=(
                "Card QUÁ HẠN TRẢ hiển thị đúng "
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
            locator_value="header .ant-select",
            sample_expected="English\nTiếng Việt",
            case_id="DASH-006",
            steps=(
                "1. Mở Dashboard. "
                "2. Mở dropdown ngôn ngữ. "
                "3. So sánh từng option theo đúng vị trí."
            ),
            expected_result=(
                "Dropdown ngôn ngữ có English và Tiếng Việt."
            ),
        ),

        # -------------------------------------------------
        # DASHBOARD - TABLE
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_booking_list",
            page_key="plt_dashboard",
            test_type="table",
            name="Danh sách giao nhận sắp tới",
            locator_type="xpath",
            locator_value=(
                "//main//section[.//h4[normalize-space()='Lượt giao nhận sắp tới']]"
            ),
            sample_expected="Lượt giao nhận sắp tới",
        ),

        ElementUnderTest(
            key="dashboard_first_booking_row",
            page_key="plt_dashboard",
            test_type="table",
            name="Dòng booking đầu tiên",
            locator_type="xpath",
            locator_value=(
                "(//main//section[.//h4[normalize-space()='Lượt giao nhận sắp tới']]"
                "//button[contains(., 'BK-')])[1]"
            ),
            sample_expected="BK-",
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
                "//aside//li[@role='menuitem' and "
                "contains(@class, 'ant-menu-item-selected') and "
                "normalize-space()='Tổng quan']"
            ),
            sample_expected="Tổng quan",
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
                "//header//h3[normalize-space()='Tổng quan']"
            ),
            sample_expected="Tổng quan",
        ),

        # -------------------------------------------------
        # DASHBOARD - UI
        # -------------------------------------------------

        ElementUnderTest(
            key="dashboard_hero_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Header tổng quan hiển thị",
            locator_type="xpath",
            locator_value="//header[.//h3[normalize-space()='Tổng quan']]",
            sample_expected="visible",
            case_id="DASH-007",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Đợi header Tổng quan hiển thị. "
                "3. Kiểm tra header đang visible."
            ),
            expected_result=(
                "Header Tổng quan hiển thị trên Dashboard."
            ),
            action_type="visible",
        ),

        ElementUnderTest(
            key="dashboard_quick_actions_visible",
            page_key="plt_dashboard",
            test_type="ui",
            name="Nút tạo đơn thuê hiển thị",
            locator_type="xpath",
            locator_value="//main//button[normalize-space()='Tạo đơn thuê']",
            sample_expected="visible",
            case_id="DASH-008",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Tìm nút Tạo đơn thuê trong nội dung Dashboard. "
                "3. Kiểm tra nút đang visible."
            ),
            expected_result=(
                "Nút Tạo đơn thuê hiển thị và sẵn sàng thao tác."
            ),
            action_type="visible",
        ),

        ElementUnderTest(
            key="dashboard_today_date",
            page_key="plt_dashboard",
            test_type="label",
            name="Ngày hiện tại trên Dashboard",
            locator_type="xpath",
            locator_value="//header//*[contains(normalize-space(), 'Hôm nay')]",
            sample_expected="Hôm nay\nNgày hiện tại theo định dạng Việt Nam",
            case_id="DASH-009",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Tìm nhãn ngày trong header. "
                "3. Kiểm tra có chữ Hôm nay và ngày hiện tại."
            ),
            expected_result=(
                "Header hiển thị đúng ngày hiện tại theo định dạng "
                "d thg m, yyyy."
            ),
            action_type="today_vi_date",
        ),

        ElementUnderTest(
            key="dashboard_create_booking",
            page_key="plt_dashboard",
            test_type="menu",
            name="Nút Tạo đơn thuê mở form tạo mới",
            locator_type="xpath",
            locator_value="//main//button[normalize-space()='Tạo đơn thuê']",
            sample_expected="/bookings/new",
            case_id="DASH-010",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm nút Tạo đơn thuê. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Dashboard điều hướng đến trang tạo đơn thuê /bookings/new."
            ),
            action_type="click_url_contains",
            target_path="/bookings/new",
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
                "Tổng quan\n"
                "Đơn thuê\n"
                "Khách hàng\n"
                "Xe\n"
                "Danh mục xe\n"
                "Tài chính\n"
                "Nhân sự"
            ),
            case_id="DASH-019",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Lấy text toàn bộ sidebar. "
                "3. Kiểm tra đủ các menu điều hướng chính."
            ),
            expected_result=(
                "Sidebar có đủ Tổng quan, Đơn thuê, Khách hàng, Xe, "
                "Danh mục xe, Tài chính và Nhân sự."
            ),
            action_type="contains_all",
        ),

        ElementUnderTest(
            key="dashboard_menu_item",
            page_key="plt_dashboard",
            test_type="menu",
            name="Item menu Tổng quan",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Tổng quan']"
            ),
            sample_expected="Tổng quan",
        ),

        ElementUnderTest(
            key="dashboard_quick_booking_list",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở danh sách đơn thuê",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Đơn thuê']"
            ),
            sample_expected="/bookings",
            case_id="DASH-011",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Đơn thuê trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /bookings."
            ),
            action_type="click_url_contains",
            target_path="/bookings",
        ),

        ElementUnderTest(
            key="dashboard_quick_fleet",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở danh sách xe",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Xe']"
            ),
            sample_expected="/cars",
            case_id="DASH-012",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Xe trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /cars."
            ),
            action_type="click_url_contains",
            target_path="/cars",
        ),

        ElementUnderTest(
            key="dashboard_quick_finance",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở tài chính",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Tài chính']"
            ),
            sample_expected="/finance",
            case_id="DASH-013",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Tài chính trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /finance."
            ),
            action_type="click_url_contains",
            target_path="/finance",
        ),

        ElementUnderTest(
            key="dashboard_deep_link",
            page_key="plt_dashboard",
            test_type="menu",
            name="Deep link mở trực tiếp Dashboard",
            locator_type="css",
            locator_value="main",
            sample_expected="/dashboard",
            case_id="DASH-014",
            steps=(
                "1. Mở trực tiếp URL /dashboard bằng tài khoản test. "
                "2. Đợi nội dung Dashboard hiển thị. "
                "3. Kiểm tra URL hiện tại."
            ),
            expected_result=(
                "Deep link /dashboard mở đúng trang Tổng quan."
            ),
            action_type="deep_link_url_contains",
            target_path="/dashboard",
        ),

        ElementUnderTest(
            key="dashboard_menu_overview",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở Tổng quan",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Tổng quan']"
            ),
            sample_expected="/dashboard",
            case_id="DASH-015",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Tổng quan trên sidebar. "
                "3. Kiểm tra URL vẫn ở Dashboard."
            ),
            expected_result=(
                "Sidebar điều hướng hoặc giữ đúng trang /dashboard."
            ),
            action_type="click_url_contains",
            target_path="/dashboard",
        ),

        ElementUnderTest(
            key="dashboard_menu_customers",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở khách hàng",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Khách hàng']"
            ),
            sample_expected="/customers",
            case_id="DASH-016",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Khách hàng trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /customers."
            ),
            action_type="click_url_contains",
            target_path="/customers",
        ),

        ElementUnderTest(
            key="dashboard_menu_catalog",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở danh mục xe",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Danh mục xe']"
            ),
            sample_expected="/cars/catalog",
            case_id="DASH-017",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Danh mục xe trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /cars/catalog."
            ),
            action_type="click_url_contains",
            target_path="/cars/catalog",
        ),

        ElementUnderTest(
            key="dashboard_menu_users",
            page_key="plt_dashboard",
            test_type="menu",
            name="Sidebar mở nhân sự",
            locator_type="xpath",
            locator_value=(
                "//aside//li[@role='menuitem' and normalize-space()='Nhân sự']"
            ),
            sample_expected="/users",
            case_id="DASH-018",
            steps=(
                "1. Mở trang /dashboard. "
                "2. Bấm item Nhân sự trên sidebar. "
                "3. Kiểm tra URL điều hướng."
            ),
            expected_result=(
                "Sidebar điều hướng đến trang /users."
            ),
            action_type="click_url_contains",
            target_path="/users",
        ),

        # =================================================
        #
        # VEHICLE CATALOG
        #
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
        #
        # BOOKING MANAGEMENT
        #
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
        ),

        # =================================================
        # BOOKING CREATE FORM
        # =================================================

        # -------------------------------------------------
        # CREATE FORM - LABEL
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_create_car_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Xe",
            locator_type="xpath",
            locator_value="//label[@for='carId']",
            sample_expected="Xe",
            case_id="BOOK-FORM-001",
        ),

        ElementUnderTest(
            key="booking_create_customer_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Khách có sẵn",
            locator_type="xpath",
            locator_value="//label[@for='customerId']",
            sample_expected="Khách có sẵn",
            case_id="BOOK-FORM-002",
        ),

        ElementUnderTest(
            key="booking_create_customer_name_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Tên khách",
            locator_type="xpath",
            locator_value="//label[@for='customerName']",
            sample_expected="Tên khách",
            case_id="BOOK-FORM-003",
        ),

        ElementUnderTest(
            key="booking_create_phone_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Số điện thoại",
            locator_type="xpath",
            locator_value="//label[@for='customerPhoneNumber']",
            sample_expected="Số điện thoại",
            case_id="BOOK-FORM-004",
        ),

        ElementUnderTest(
            key="booking_create_email_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Email",
            locator_type="xpath",
            locator_value="//label[@for='customerEmail']",
            sample_expected="Email",
            case_id="BOOK-FORM-005",
        ),

        ElementUnderTest(
            key="booking_create_start_date_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Ngày nhận xe",
            locator_type="xpath",
            locator_value="//label[@for='startDate']",
            sample_expected="Ngày nhận xe",
            case_id="BOOK-FORM-006",
        ),

        ElementUnderTest(
            key="booking_create_end_date_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Ngày trả xe",
            locator_type="xpath",
            locator_value="//label[@for='endDate']",
            sample_expected="Ngày trả xe",
            case_id="BOOK-FORM-007",
        ),

        ElementUnderTest(
            key="booking_create_pickup_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Điểm nhận xe",
            locator_type="xpath",
            locator_value="//label[@for='pickupLocation']",
            sample_expected="Điểm nhận xe",
            case_id="BOOK-FORM-008",
        ),

        ElementUnderTest(
            key="booking_create_return_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Điểm trả xe",
            locator_type="xpath",
            locator_value="//label[@for='returnLocation']",
            sample_expected="Điểm trả xe",
            case_id="BOOK-FORM-009",
        ),

        ElementUnderTest(
            key="booking_create_status_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Trạng thái đơn thuê",
            locator_type="xpath",
            locator_value="//label[@for='status']",
            sample_expected="Trạng thái đơn thuê",
            case_id="BOOK-FORM-010",
        ),

        ElementUnderTest(
            key="booking_create_rental_amount_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Tiền thuê xe",
            locator_type="xpath",
            locator_value="//label[@for='rentalAmount']",
            sample_expected="Tiền thuê xe",
            case_id="BOOK-FORM-011",
        ),

        ElementUnderTest(
            key="booking_create_deposit_amount_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Tiền cọc giữ chỗ",
            locator_type="xpath",
            locator_value="//label[@for='depositAmount']",
            sample_expected="Tiền cọc giữ chỗ",
            case_id="BOOK-FORM-012",
        ),

        ElementUnderTest(
            key="booking_create_security_deposit_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Tiền thế chân",
            locator_type="xpath",
            locator_value="//label[@for='securityDeposit']",
            sample_expected="Tiền thế chân",
            case_id="BOOK-FORM-013",
        ),

        ElementUnderTest(
            key="booking_create_payment_amount_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Thu lần này",
            locator_type="xpath",
            locator_value="//label[@for='paymentAmountThisTime']",
            sample_expected="Thu lần này",
            case_id="BOOK-FORM-014",
        ),

        ElementUnderTest(
            key="booking_create_payment_method_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Cách thanh toán",
            locator_type="xpath",
            locator_value="//label[@for='paymentMethod']",
            sample_expected="Cách thanh toán",
            case_id="BOOK-FORM-015",
        ),

        ElementUnderTest(
            key="booking_create_payment_note_label",
            page_key="plt_booking",
            test_type="label",
            name="Nhãn Ghi chú thanh toán",
            locator_type="xpath",
            locator_value="//label[@for='paymentNote']",
            sample_expected="Ghi chú thanh toán",
            case_id="BOOK-FORM-016",
        ),

        # -------------------------------------------------
        # CREATE FORM - INPUT
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_customer_name_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Tên khách",
            locator_type="id",
            locator_value="customerName",
            sample_expected="",
            case_id="BOOK-INPUT-001",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_customer_phone_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Số điện thoại",
            locator_type="id",
            locator_value="customerPhoneNumber",
            sample_expected="",
            case_id="BOOK-INPUT-002",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_customer_email_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Email",
            locator_type="id",
            locator_value="customerEmail",
            sample_expected="",
            case_id="BOOK-INPUT-003",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_start_date_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Ngày nhận xe",
            locator_type="id",
            locator_value="startDate",
            sample_expected="Chọn thời điểm",
            case_id="BOOK-INPUT-004",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_end_date_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Ngày trả xe",
            locator_type="id",
            locator_value="endDate",
            sample_expected="Chọn thời điểm",
            case_id="BOOK-INPUT-005",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_pickup_location_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Điểm nhận xe",
            locator_type="id",
            locator_value="pickupLocation",
            sample_expected="Văn phòng PLT",
            case_id="BOOK-INPUT-006",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_return_location_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Điểm trả xe",
            locator_type="id",
            locator_value="returnLocation",
            sample_expected="Văn phòng PLT",
            case_id="BOOK-INPUT-007",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_rental_amount_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Tiền thuê xe",
            locator_type="id",
            locator_value="rentalAmount",
            sample_expected="0 ₫",
            case_id="BOOK-INPUT-008",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_deposit_amount_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Tiền cọc giữ chỗ",
            locator_type="id",
            locator_value="depositAmount",
            sample_expected="0 ₫",
            case_id="BOOK-INPUT-009",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_security_deposit_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Tiền thế chân",
            locator_type="id",
            locator_value="securityDeposit",
            sample_expected="0 ₫",
            case_id="BOOK-INPUT-010",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_payment_amount_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Thu lần này",
            locator_type="id",
            locator_value="paymentAmountThisTime",
            sample_expected="0 ₫",
            case_id="BOOK-INPUT-011",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_payment_note_input",
            page_key="plt_booking",
            test_type="input",
            name="Ô Ghi chú thanh toán",
            locator_type="id",
            locator_value="paymentNote",
            sample_expected="",
            case_id="BOOK-INPUT-012",
            action_type="exists",
        ),

        # -------------------------------------------------
        # CREATE FORM - DROPDOWN
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_car_dropdown",
            page_key="plt_booking",
            test_type="dropdown",
            name="Chọn xe",
            locator_type="id",
            locator_value="carId",
            sample_expected=(
                "30L-678.90 • Everest Diesel • Sẵn sàng"
            ),
            case_id="BOOK-DROP-001",
            steps=(
                "1. Đăng nhập bằng email/password. "
                "2. Mở /bookings/new. "
                "3. Mở dropdown Chọn xe. "
                "4. Kiểm tra option."
            ),
            expected_result=(
                "Dropdown Chọn xe tồn tại và có dữ liệu xe."
            ),
            action_type="dropdown_has_options",
        ),

        ElementUnderTest(
            key="booking_customer_dropdown",
            page_key="plt_booking",
            test_type="dropdown",
            name="Chọn khách",
            locator_type="id",
            locator_value="customerId",
            sample_expected="Chọn khách",
            case_id="BOOK-DROP-002",
            steps=(
                "1. Đăng nhập bằng email/password. "
                "2. Mở /bookings/new. "
                "3. Mở dropdown Chọn khách. "
                "4. Kiểm tra option."
            ),
            expected_result=(
                "Dropdown Chọn khách tồn tại và có dữ liệu."
            ),
            action_type="dropdown_has_options",
        ),

        ElementUnderTest(
            key="booking_status_dropdown",
            page_key="plt_booking",
            test_type="dropdown",
            name="Trạng thái",
            locator_type="id",
            locator_value="status",
            sample_expected=(
                "Nháp\n"
                "Đã xác nhận\n"
                "Đang thuê\n"
                "Hoàn tất\n"
                "Đã hủy"
            ),
            case_id="BOOK-DROP-003",
            steps=(
                "1. Đăng nhập bằng email/password. "
                "2. Mở /bookings/new. "
                "3. Mở dropdown Trạng thái. "
                "4. Kiểm tra toàn bộ option."
            ),
            expected_result=(
                "Dropdown Trạng thái có đủ các trạng thái."
            ),
            action_type="dropdown_has_options",
        ),

        ElementUnderTest(
            key="booking_payment_method_dropdown",
            page_key="plt_booking",
            test_type="dropdown",
            name="Phương thức thanh toán",
            locator_type="id",
            locator_value="paymentMethod",
            sample_expected=(
                "Chuyển khoản\n"
                "Thẻ\n"
                "Khác"
            ),
            case_id="BOOK-DROP-004",
            steps=(
                "1. Đăng nhập bằng email/password. "
                "2. Mở /bookings/new. "
                "3. Mở dropdown Phương thức thanh toán. "
                "4. Kiểm tra toàn bộ option."
            ),
            expected_result=(
                "Dropdown Phương thức thanh toán "
                "có đủ các option."
            ),
            action_type="dropdown_has_options",
        ),

        # -------------------------------------------------
        # CREATE FORM - BUTTON
        # -------------------------------------------------

        ElementUnderTest(
            key="booking_create_button",
            page_key="plt_booking",
            test_type="button",
            name="Nút Tạo đơn thuê",
            locator_type="xpath",
            locator_value=(
                "//button[@type='submit' "
                "and normalize-space()='Tạo đơn thuê']"
            ),
            sample_expected="Tạo đơn thuê",
            case_id="BOOK-BTN-001",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_back_button",
            page_key="plt_booking",
            test_type="button",
            name="Nút Quay lại danh sách đơn thuê",
            locator_type="xpath",
            locator_value=(
                "//button[contains(normalize-space(), "
                "'Quay lại danh sách đơn thuê')]"
            ),
            sample_expected="Quay lại danh sách đơn thuê",
            case_id="BOOK-BTN-002",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_add_extra_charge_button",
            page_key="plt_booking",
            test_type="button",
            name="Nút Thêm phụ phí",
            locator_type="xpath",
            locator_value=(
                "//button[normalize-space()='Thêm phụ phí']"
            ),
            sample_expected="Thêm phụ phí",
            case_id="BOOK-BTN-003",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_add_discount_button",
            page_key="plt_booking",
            test_type="button",
            name="Nút Thêm giảm giá hoặc hoàn tiền",
            locator_type="xpath",
            locator_value=(
                "//button[normalize-space()='"
                "Thêm giảm giá hoặc hoàn tiền']"
            ),
            sample_expected="Thêm giảm giá hoặc hoàn tiền",
            case_id="BOOK-BTN-004",
            action_type="exists",
        ),

        ElementUnderTest(
            key="booking_upload_button",
            page_key="plt_booking",
            test_type="button",
            name="Nút Tải tệp lên",
            locator_type="xpath",
            locator_value=(
                "//button[normalize-space()='Tải tệp lên']"
            ),
            sample_expected="Tải tệp lên",
            case_id="BOOK-BTN-005",
            action_type="exists",
        ),

        # -------------------------------------------------
        # BOOKING LIST - TABLE
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
            sample_expected="BK-",
            case_id="BOOK-005",
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
            sample_expected="BK-",
            case_id="BOOK-006",
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
            sample_expected="Trạng thái",
            case_id="BOOK-009",
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
            sample_expected="Thanh toán",
            case_id="BOOK-010",
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
            action_type="exists",
        ),

        # =================================================
        #
        # STAFF MANAGEMENT
        #
        # =================================================

        ElementUnderTest(
            key="staff_page_title",
            page_key="plt_user",
            test_type="label",
            name="Tiêu đề Nhân sự",
            locator_type="xpath",
            locator_value=(
                "//*[normalize-space()='Nhân sự' or normalize-space()='Quản lý Nhân sự' "
                "or normalize-space()='Danh bạ nhân sự']"
            ),
            sample_expected="Nhân sự",
            case_id="USER-001",
            action_type="contains_text",
        ),

        ElementUnderTest(
            key="staff_create_button",
            page_key="plt_user",
            test_type="label",
            name="Nút Thêm nhân sự",
            locator_type="xpath",
            locator_value=(
                "//a[contains(@href, '/users/new') or contains(@href, '/users/create')]//button "
                "| //button[.//span[contains(normalize-space(), 'Thêm')]]"
            ),
            sample_expected="Thêm",
            case_id="USER-002",
            action_type="exists",
        ),

        ElementUnderTest(
            key="staff_table",
            page_key="plt_user",
            test_type="table",
            name="Bảng danh sách Nhân sự",
            locator_type="xpath",
            locator_value="//table | //section[.//*[contains(normalize-space(), 'nhân sự')]]",
            sample_expected="Danh sách nhân sự có dữ liệu",
            case_id="USER-003",
            action_type="exists",
        ),

        ElementUnderTest(
            key="staff_pagination",
            page_key="plt_user",
            test_type="ui",
            name="Phân trang Nhân sự",
            locator_type="css",
            locator_value=".ant-pagination",
            sample_expected="pagination",
            case_id="USER-004",
            action_type="exists",
        ),

        ElementUnderTest(
            key="staff_sidebar_menu_item",
            page_key="plt_user",
            test_type="menu",
            name="Item menu Nhân sự",
            locator_type="xpath",
            locator_value=(
                "//*[self::li or self::a or self::button]"
                "[.//*[contains(normalize-space(), 'Nhân sự') or contains(normalize-space(), 'Người dùng')]]"
            ),
            sample_expected="Nhân sự",
            case_id="USER-005",
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

    # =====================================================
    # GET ALL ELEMENTS OF PAGE
    # =====================================================

    @classmethod
    def elements_for_page(
        cls,
        page_key: str,
    ) -> List[ElementUnderTest]:

        return [
            element
            for element in cls.elements
            if element.page_key == page_key
        ]

    # =====================================================
    # GET ELEMENT BY KEY
    # =====================================================

    @classmethod
    def get_element(
        cls,
        key: str,
    ) -> ElementUnderTest:

        for element in cls.elements:
            if element.key == key:
                return element

        raise KeyError(
            f"Không tìm thấy element contract: {key}"
        )

    # =====================================================
    # GET PAGE BY KEY
    # =====================================================

    @classmethod
    def get_page(
        cls,
        key: str,
    ) -> PageUnderTest:

        for page in cls.pages:
            if page.key == key:
                return page

        raise KeyError(
            f"Không tìm thấy page contract: {key}"
        )
