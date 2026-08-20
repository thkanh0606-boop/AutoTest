import copy
import re
from PySide6.QtCore import QByteArray, QObject, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QScrollArea,  # đã có, nhưng thêm vào để rõ
)


def create_svg_icon(svg_xml: str, color='#ffffff', size=16) -> QIcon:
    formatted_svg = svg_xml.format(color=color)
    renderer = QSvgRenderer(QByteArray(formatted_svg.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


SVG_ICONS = {
    'scan': (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        ' viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2"'
        ' stroke-linecap="round" stroke-linejoin="round"><circle cx="11"'
        ' cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
    ),
    'stop': (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        ' viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2"'
        ' stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4"'
        ' width="16" height="16" rx="3"/></svg>'
    ),
    'reset': (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        ' viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2"'
        ' stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0'
        ' 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>'
    ),
    'add': (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        ' viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2"'
        ' stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5"'
        ' x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>'
    ),
    'play': (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        ' viewBox="0 0 24 24" fill="{color}" stroke="none"><polygon points="6,4'
        ' 20,12 6,20"/></svg>'
    ),
}

MODULE_SCREEN_MAP = {
    'dropdown list': 'dropdown',
    'dropdown': 'dropdown',
    'label / text': 'label',
    'label': 'label',
    'text': 'label',
    'table': 'table',
    'radio / checkbox': 'radio',
    'radio': 'radio',
    'checkbox': 'radio',
    'image': 'image',
    'hình ảnh': 'image',
    'title': 'title',
    'tiêu đề': 'title',
    'ui': 'ui',
    'giao diện': 'ui',
    'menu': 'menu',
    'menu website': 'menu',
}


def get_module_key(module_str: str) -> str:
    if not module_str:
        return 'label'
    clean_key = str(module_str).strip().lower()
    return MODULE_SCREEN_MAP.get(clean_key, 'label')


# ==============================================================================
# CENTRAL ELEMENT REGISTRY
# ==============================================================================
class ElementRegistry(QObject):
    data_changed = Signal()
    test_result_updated = Signal(dict)

    DEFAULT_STORE = {
        'Trang tổng quan': [
            # 1. Dropdown List
            {
                'key': 'lang_dropdown',
                'name': 'Dropdown ngôn ngữ',
                'module': 'Dropdown List',
                'locator_type': 'css',
                'locator_value': '.ant-select',
                'expected_result': 'Tiếng Việt\nEnglish',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 2. Label / Text
            {
                'key': 'hero_title',
                'name': 'Tiêu đề hero Dashboard',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h1[normalize-space()='Dashboard']",
                'expected_result': 'Dashboard',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'header_title',
                'name': 'Tiêu đề header vận hành',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h3[normalize-space()='Bảng điều khiển vận hành']",
                'expected_result': 'Bảng điều khiển vận hành',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'kpi_renting',
                'name': 'KPI xe đang cho thuê',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Xe đang cho thuê')]",
                'expected_result': 'Xe đang cho thuê',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'kpi_ready_today',
                'name': 'KPI xe sẵn sàng hôm nay',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(.), 'Sẵn sàng hôm nay')]/following::div[1]",
                'expected_result': 'Sẵn sàng hôm nay',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'kpi_overdue_booking',
                'name': 'KPI booking trễ hạn',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Booking trễ hạn')]",
                'expected_result': 'Booking trễ hạn',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'hero_section',
                'name': 'Hero tổng quan hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "(//main//section)[1]",
                'expected_result': 'Hero tổng quan',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'quick_actions',
                'name': 'Khối thao tác nhanh hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "(//main//section)[2]",
                'expected_result': 'Thao tác nhanh',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 3. Table
            {
                'key': 'dashboard_stats_table',
                'name': 'Bảng thống kê tổng quan',
                'module': 'Table',
                'locator_type': 'xpath',
                'locator_value': "(/main//div[contains(@class,'grid')])[6]/*[1]",
                'expected_result': 'Danh sách bàn giao sắp tới',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 4. Radio / Checkbox
            {
                'key': 'menu_dashboard_selected',
                'name': 'Trạng thái menu Dashboard đang chọn',
                'module': 'Radio / Checkbox',
                'locator_type': 'xpath',
                'locator_value': "//li[@role='menuitem' and contains(@class, 'ant-menu-item-selected')]",
                'expected_result': 'Dashboard',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 5. Hình ảnh
            {
                'key': 'logo_image',
                'name': 'Logo PLT Solutions',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': "aside img[alt='PLT Solutions']",
                'expected_result': 'logo.png',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 6. Tiêu đề
            {
                'key': 'page_title',
                'name': 'Tiêu đề trang chủ',
                'module': 'Tiêu đề',
                'locator_type': 'xpath',
                'locator_value': "//title",
                'expected_result': 'PLT Fleet Console',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 7. Giao diện
            {
                'key': 'dark_mode_toggle',
                'name': 'Chế độ giao diện (sáng/tối)',
                'module': 'Giao diện',
                'locator_type': 'id',
                'locator_value': 'themeToggle',
                'expected_result': 'light',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 8. Menu website
            {
                'key': 'sidebar_menu',
                'name': 'Menu sidebar',
                'module': 'Menu website',
                'locator_type': 'css',
                'locator_value': "ul[role='menu']",
                'expected_result': 'Dashboard\nXe\nĐặt xe\nNhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'menu_item_dashboard',
                'name': 'Item menu Dashboard',
                'module': 'Menu website',
                'locator_type': 'xpath',
                'locator_value': "//li[@role='menuitem'][./span[normalize-space()='Dashboard']]",
                'expected_result': 'Dashboard',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
        ],
        'Danh mục xe': [
            # 1. Dropdown List
            {
                'key': 'catalog_filter_brand',
                'name': 'Dropdown lọc Hãng ở bảng Mẫu',
                'module': 'Dropdown List',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//*[@role='combobox'][1]",
                'expected_result': 'Hãng xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 2. Label / Text
            {
                'key': 'catalog_title',
                'name': 'Tiêu đề Danh mục xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "(//*[normalize-space()='Danh mục xe' and not(ancestor::aside)])[1]",
                'expected_result': 'Danh mục xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'total_brands_label',
                'name': 'Nhãn Tổng số hãng',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Tổng số hãng')]",
                'expected_result': 'Tổng số hãng',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'active_brands_label',
                'name': 'Nhãn Hãng đang hoạt động',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Hãng đang hoạt động')]",
                'expected_result': 'Hãng đang hoạt động',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'total_models_label',
                'name': 'Nhãn Tổng số mẫu xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Tổng số mẫu xe')]",
                'expected_result': 'Tổng số mẫu xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'brand_list_title',
                'name': 'Tiêu đề Danh sách hãng xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách hãng xe']",
                'expected_result': 'Danh sách hãng xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'model_list_title',
                'name': 'Tiêu đề Danh sách mẫu xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách mẫu xe']",
                'expected_result': 'Danh sách mẫu xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'add_brand_btn',
                'name': 'Nút Thêm hãng xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[contains(text(), 'Thêm hãng')]",
                'expected_result': 'Thêm hãng',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'add_model_btn',
                'name': 'Nút Thêm mẫu xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[contains(text(), 'Thêm mẫu')]",
                'expected_result': 'Thêm mẫu',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'brand_section_visible',
                'name': 'Khu Danh sách hãng xe hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]",
                'expected_result': 'Danh sách hãng xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'model_section_visible',
                'name': 'Khu Danh sách mẫu xe hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]",
                'expected_result': 'Danh sách mẫu xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 3. Table
            {
                'key': 'brand_table',
                'name': 'Bảng danh sách hãng xe',
                'module': 'Table',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]//table",
                'expected_result': 'STT, Tên hãng, Số lượng mẫu',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'model_table',
                'name': 'Bảng danh sách mẫu xe',
                'module': 'Table',
                'locator_type': 'xpath',
                'locator_value': "//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//table",
                'expected_result': 'STT, Tên mẫu, Hãng',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 4. Radio / Checkbox
            {
                'key': 'catalog_active_checkbox',
                'name': 'Hiển thị hoạt động',
                'module': 'Radio / Checkbox',
                'locator_type': 'id',
                'locator_value': 'activeOnly',
                'expected_result': 'True',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'active_status_tag',
                'name': 'Trạng thái Đang hoạt động',
                'module': 'Radio / Checkbox',
                'locator_type': 'xpath',
                'locator_value': "(//span[contains(@class,'ant-tag') and normalize-space()='Đang hoạt động'])[1]",
                'expected_result': 'Đang hoạt động',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 5. Hình ảnh
            {
                'key': 'catalog_logo',
                'name': 'Logo PLT Solutions',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': "aside img[alt='PLT Solutions']",
                'expected_result': 'logo.png',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 6. Tiêu đề
            {
                'key': 'catalog_page_title',
                'name': 'Tiêu đề trang Danh mục xe',
                'module': 'Tiêu đề',
                'locator_type': 'xpath',
                'locator_value': "//title",
                'expected_result': 'Danh mục xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 7. Giao diện
            {
                'key': 'catalog_theme_toggle',
                'name': 'Chế độ giao diện (sáng/tối)',
                'module': 'Giao diện',
                'locator_type': 'id',
                'locator_value': 'themeToggle',
                'expected_result': 'light',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 8. Menu website
            {
                'key': 'catalog_menu_item',
                'name': 'Item menu Danh mục xe',
                'module': 'Menu website',
                'locator_type': 'xpath',
                'locator_value': "//li[@role='menuitem'][./span[normalize-space()='Danh mục xe']]",
                'expected_result': 'Danh mục xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
        ],
        'Quản lý xe': [
            # 1. Dropdown List
            {
                'key': 'car_brand_form_dropdown',
                'name': 'Dropdown Hãng xe (Form Thêm)',
                'module': 'Dropdown List',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(.), 'Hãng xe')]/ancestor::*[contains(@class,'ant-form-item')][1]//*[@role='combobox']",
                'expected_result': 'Toyota, Honda, Ford',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'car_fuel_dropdown',
                'name': 'Dropdown Nhiên liệu (Form Thêm)',
                'module': 'Dropdown List',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(.), 'Nhiên liệu')]/ancestor::*[contains(@class,'ant-form-item')][1]//*[@role='combobox']",
                'expected_result': 'Xăng, Dầu, Điện',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'car_brand_filter',
                'name': 'Filter hãng xe',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'brandFilter',
                'expected_result': 'Toyota, Honda, Ford',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 2. Label / Text
            {
                'key': 'add_car_btn',
                'name': 'Nút Thêm xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[contains(text(),'Thêm xe')]",
                'expected_result': 'Thêm xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'stat_ready_today',
                'name': 'Thống kê Sẵn sàng hôm nay',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(.), 'Sẵn sàng hôm nay')]/following::div[1]",
                'expected_result': 'Sẵn sàng hôm nay',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'stat_maintenance',
                'name': 'Thống kê Đang bảo dưỡng',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(.), 'Đang bảo dưỡng')]/following::div[1]",
                'expected_result': 'Đang bảo dưỡng',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'delete_modal',
                'name': 'Modal xác nhận Xóa xe hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(@class,'ant-popover') or contains(@class,'ant-modal')][not(contains(@style,'display: none'))]",
                'expected_result': 'Xác nhận xóa',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 3. Table
            {
                'key': 'car_table',
                'name': 'Bảng danh sách xe',
                'module': 'Table',
                'locator_type': 'css',
                'locator_value': 'table.ant-table',
                'expected_result': 'ID, Biển số, Hãng, Mẫu, Năm sản xuất',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'first_car_row',
                'name': 'Dòng dữ liệu xe đầu tiên',
                'module': 'Table',
                'locator_type': 'css',
                'locator_value': 'div.ant-table-wrapper table tbody tr:nth-child(1)',
                'expected_result': 'Dòng xe đầu tiên',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 4. Radio / Checkbox
            {
                'key': 'car_status_checkbox',
                'name': 'Hiển thị xe đang hoạt động',
                'module': 'Radio / Checkbox',
                'locator_type': 'id',
                'locator_value': 'showActiveOnly',
                'expected_result': 'True',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 5. Hình ảnh
            {
                'key': 'car_image',
                'name': 'Ảnh xe',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': '.car-image img',
                'expected_result': 'car.jpg',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 6. Tiêu đề
            {
                'key': 'car_page_title',
                'name': 'Tiêu đề trang Quản lý xe',
                'module': 'Tiêu đề',
                'locator_type': 'xpath',
                'locator_value': "//title",
                'expected_result': 'Quản lý xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 7. Giao diện
            {
                'key': 'car_theme_toggle',
                'name': 'Chế độ giao diện (sáng/tối)',
                'module': 'Giao diện',
                'locator_type': 'id',
                'locator_value': 'themeToggle',
                'expected_result': 'light',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 8. Menu website
            {
                'key': 'car_menu',
                'name': 'Menu điều hướng',
                'module': 'Menu website',
                'locator_type': 'css',
                'locator_value': '.ant-menu',
                'expected_result': 'Dashboard\nXe\nĐặt xe\nNhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
        ],
        'Quản lý đặt xe': [
            # 1. Dropdown List
            {
                'key': 'car_dropdown',
                'name': 'Chọn xe',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'carId',
                'expected_result': 'Xe 1, Xe 2',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'customer_dropdown',
                'name': 'Chọn khách',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'customerId',
                'expected_result': 'KH A, KH B',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'booking_status_dropdown',
                'name': 'Trạng thái đơn thuê',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'status',
                'expected_result': 'Chờ duyệt, Đã duyệt, Hủy',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'payment_method_dropdown',
                'name': 'Phương thức thanh toán',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'paymentMethod',
                'expected_result': 'Tiền mặt, Chuyển khoản',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 2. Label / Text
            {
                'key': 'booking_title',
                'name': 'Tiêu đề Quản lý đặt xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[normalize-space()='Quản lý đặt xe' and not(ancestor::aside)]",
                'expected_result': 'Quản lý đặt xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'booking_list_label',
                'name': 'Nhãn khu vực danh sách booking',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[contains(normalize-space(), 'Danh sách booking')]",
                'expected_result': 'Danh sách booking',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'car_label',
                'name': 'Nhãn Xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='carId']",
                'expected_result': 'Xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'customer_label',
                'name': 'Nhãn Khách có sẵn',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='customerId']",
                'expected_result': 'Khách có sẵn',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'customer_name_label',
                'name': 'Nhãn Tên khách',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='customerName']",
                'expected_result': 'Tên khách',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'phone_label',
                'name': 'Nhãn Số điện thoại',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='customerPhoneNumber']",
                'expected_result': 'Số điện thoại',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'email_label',
                'name': 'Nhãn Email',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='customerEmail']",
                'expected_result': 'Email',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'start_date_label',
                'name': 'Nhãn Ngày nhận xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='startDate']",
                'expected_result': 'Ngày nhận xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'end_date_label',
                'name': 'Nhãn Ngày trả xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='endDate']",
                'expected_result': 'Ngày trả xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'pickup_label',
                'name': 'Nhãn Điểm nhận xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='pickupLocation']",
                'expected_result': 'Điểm nhận xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'return_label',
                'name': 'Nhãn Điểm trả xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='returnLocation']",
                'expected_result': 'Điểm trả xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'rental_amount_label',
                'name': 'Nhãn Tiền thuê xe',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//label[@for='rentalAmount']",
                'expected_result': 'Tiền thuê xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'create_booking_btn',
                'name': 'Nút Tạo đơn thuê',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[@aria-label='Tạo đơn thuê']",
                'expected_result': 'Tạo đơn thuê',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'save_btn',
                'name': 'Nút Lưu (Tạo/Cập nhật)',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[@type='submit' and (.//span[contains(normalize-space(.),'Lưu')] or .//span[contains(normalize-space(.),'Tạo đơn thuê')] or .//span[contains(normalize-space(.),'Cập nhật')])]",
                'expected_result': 'Lưu',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'search_input',
                'name': 'Ô tìm kiếm',
                'module': 'Label / Text',
                'locator_type': 'id',
                'locator_value': 'search',
                'expected_result': 'Tìm kiếm booking...',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'booking_section_visible',
                'name': 'Khu vực quản lý booking hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//main",
                'expected_result': 'Quản lý booking',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'booking_table_section_visible',
                'name': 'Khu vực bảng booking hiển thị',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//main//table",
                'expected_result': 'Bảng booking',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 3. Table
            {
                'key': 'booking_table',
                'name': 'Bảng danh sách booking',
                'module': 'Table',
                'locator_type': 'css',
                'locator_value': 'table',
                'expected_result': 'ID, Xe, Khách hàng, Ngày bắt đầu, Ngày kết thúc, Trạng thái, Tiền thuê',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'first_booking_row',
                'name': 'Dòng booking đầu tiên',
                'module': 'Table',
                'locator_type': 'xpath',
                'locator_value': "(//main//table//tbody//tr)[1]",
                'expected_result': 'Dòng booking đầu tiên',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 4. Radio / Checkbox
            {
                'key': 'booking_checkbox',
                'name': 'Checkbox trong bảng Booking',
                'module': 'Radio / Checkbox',
                'locator_type': 'xpath',
                'locator_value': "(//main//table//input[@type='checkbox'])[1]",
                'expected_result': 'True',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 5. Hình ảnh
            {
                'key': 'booking_logo',
                'name': 'Logo PLT Solutions',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': "aside img[alt='PLT Solutions']",
                'expected_result': 'logo.png',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 6. Tiêu đề
            {
                'key': 'booking_page_title',
                'name': 'Tiêu đề trang Booking',
                'module': 'Tiêu đề',
                'locator_type': 'xpath',
                'locator_value': "//title",
                'expected_result': 'Quản lý đặt xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 7. Giao diện
            {
                'key': 'booking_theme_toggle',
                'name': 'Chế độ giao diện (sáng/tối)',
                'module': 'Giao diện',
                'locator_type': 'id',
                'locator_value': 'themeToggle',
                'expected_result': 'light',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 8. Menu website
            {
                'key': 'booking_menu',
                'name': 'Menu sidebar Booking',
                'module': 'Menu website',
                'locator_type': 'css',
                'locator_value': "ul[role='menu']",
                'expected_result': 'Dashboard\nXe\nĐặt xe\nNhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'booking_menu_item',
                'name': 'Item menu Đặt xe',
                'module': 'Menu website',
                'locator_type': 'xpath',
                'locator_value': "//li[@role='menuitem'][./span[normalize-space()='Đặt xe']]",
                'expected_result': 'Đặt xe',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
        ],
        'Nhân sự': [
            # 1. Dropdown List
            {
                'key': 'staff_role_filter',
                'name': 'Filter vai trò',
                'module': 'Dropdown List',
                'locator_type': 'id',
                'locator_value': 'roleFilter',
                'expected_result': 'Tất cả\nAdmin\nNhân viên',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 2. Label / Text
            {
                'key': 'staff_title',
                'name': 'Tiêu đề Nhân sự',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//*[normalize-space()='Nhân sự' and not(ancestor::aside)]",
                'expected_result': 'Nhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'add_staff_btn',
                'name': 'Nút Thêm nhân sự',
                'module': 'Label / Text',
                'locator_type': 'xpath',
                'locator_value': "//button[contains(text(),'Thêm nhân sự')]",
                'expected_result': 'Thêm nhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'staff_pagination',
                'name': 'Phân trang Nhân sự',
                'module': 'Label / Text',
                'locator_type': 'css',
                'locator_value': '.ant-pagination',
                'expected_result': 'Phân trang',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 3. Table
            {
                'key': 'staff_table',
                'name': 'Bảng danh sách Nhân sự',
                'module': 'Table',
                'locator_type': 'css',
                'locator_value': 'table.ant-table',
                'expected_result': 'ID, Tên, Email, Vai trò',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 4. Radio / Checkbox
            {
                'key': 'staff_active_checkbox',
                'name': 'Hiển thị nhân viên đang hoạt động',
                'module': 'Radio / Checkbox',
                'locator_type': 'id',
                'locator_value': 'activeOnly',
                'expected_result': 'True',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 5. Hình ảnh
            {
                'key': 'staff_avatar',
                'name': 'Avatar nhân viên',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': '.staff-avatar img',
                'expected_result': 'avatar.png',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            {
                'key': 'staff_logo',
                'name': 'Logo PLT Solutions',
                'module': 'Hình ảnh',
                'locator_type': 'css',
                'locator_value': "aside img[alt='PLT Solutions']",
                'expected_result': 'logo.png',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 6. Tiêu đề
            {
                'key': 'staff_page_title',
                'name': 'Tiêu đề trang Nhân sự',
                'module': 'Tiêu đề',
                'locator_type': 'xpath',
                'locator_value': "//title",
                'expected_result': 'Nhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 7. Giao diện
            {
                'key': 'staff_theme_toggle',
                'name': 'Chế độ giao diện (sáng/tối)',
                'module': 'Giao diện',
                'locator_type': 'id',
                'locator_value': 'themeToggle',
                'expected_result': 'light',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
            # 8. Menu website
            {
                'key': 'staff_menu_item',
                'name': 'Item menu Nhân sự',
                'module': 'Menu website',
                'locator_type': 'xpath',
                'locator_value': "//button][.//*[contains(normalize-space(), 'Nhân sự') or contains(normalize-space(), 'Người dùng')]]",
                'expected_result': 'Nhân sự',
                'actual_result': '-',
                'status': 'Sẵn sàng',
                'reason': '',
            },
        ],
        'Tài chính': [],
    }

    def __init__(self):
        super().__init__()
        self._store = copy.deepcopy(self.DEFAULT_STORE)

    def get_elements(self, page_name=None):
        if page_name:
            return self._store.get(page_name, [])

        all_elems = []
        for p_name, elems in self._store.items():
            for e in elems:
                item = dict(e)
                item['page_name'] = p_name
                all_elems.append(item)
        return all_elems

    def add_or_update_element(self, page_name, element_data):
        if page_name not in self._store:
            self._store[page_name] = []

        elements = self._store[page_name]
        found = False
        for el in elements:
            if el.get('name') == element_data.get('name') or (
                el.get('key') and el.get('key') == element_data.get('key')
            ):
                el.update(element_data)
                found = True
                break

        if not found:
            elements.append(element_data)

        self.data_changed.emit()

    def notify_test_result(self, result_payload):
        page_name = result_payload.get('page_name')
        elem_key = result_payload.get('element_key')
        elem_name = result_payload.get('element_name')

        if page_name and page_name in self._store:
            for el in self._store[page_name]:
                if el.get('key') == elem_key or el.get('name') == elem_name:
                    el['last_result_payload'] = result_payload
                    el['status'] = result_payload.get('status', 'FAILED')
                    el['actual_result'] = result_payload.get('actual', '-')
                    el['reason'] = result_payload.get('message', '')
                    break

        self.test_result_updated.emit(result_payload)
        self.data_changed.emit()

    def reset_to_default(self):
        self._store = copy.deepcopy(self.DEFAULT_STORE)
        self.data_changed.emit()


element_registry = ElementRegistry()


# ==============================================================================
# DIALOG: THÊM ELEMENT / TRANG MỚI
# ==============================================================================
class AddElementDialog(QDialog):
    def __init__(self, parent=None, existing_pages=None):
        super().__init__(parent)
        self.setWindowTitle('Thêm Element / Trang mới')
        self.setFixedWidth(480)
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { font-weight: bold; color: #334155; }
            QMessageBox { background: white; }
            QMessageBox QLabel { color: #334155; font-weight: normal; }
            QMessageBox QPushButton { background: #e2e8f0; color: #1e293b; border: 1px solid #cbd5e1; min-width: 60px; padding: 5px 12px; }
            QMessageBox QPushButton:hover { background: #cbd5e1; }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px; font-size: 13px;
                color: #0f172a; width: 100%;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #e2e8f0;
                selection-color: #0f172a;
            }
            QPushButton {
                border-radius: 6px; padding: 8px 16px; font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.page_combo = QComboBox()
        self.page_combo.setEditable(True)
        self.page_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pages = existing_pages or list(element_registry._store.keys())
        self.page_combo.addItems(pages)

        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.name_input.setPlaceholderText('Ví dụ: Nút Đăng nhập')

        self.module_combo = QComboBox()
        self.module_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.module_combo.addItems([
            'Label / Text',
            'Dropdown List',
            'Table',
            'Radio / Checkbox',
            'Hình ảnh',
            'Tiêu đề',
            'Giao diện',
            'Menu website',
        ])

        self.locator_type_combo = QComboBox()
        self.locator_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.locator_type_combo.addItems(['xpath', 'css', 'id', 'name', 'class'])

        self.locator_val_input = QLineEdit()
        self.locator_val_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.locator_val_input.setPlaceholderText("//button[@id='btn-login']")

        self.expected_input = QTextEdit()
        self.expected_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.expected_input.setFixedHeight(70)
        self.expected_input.setPlaceholderText('Nhập kết quả mong đợi...')

        form_layout.addRow('Tên Trang:', self.page_combo)
        form_layout.addRow('Tên Element:', self.name_input)
        form_layout.addRow('Module:', self.module_combo)
        form_layout.addRow('Locator Type:', self.locator_type_combo)
        form_layout.addRow('Locator Value:', self.locator_val_input)
        form_layout.addRow('Expected Result:', self.expected_input)

        layout.addLayout(form_layout)

        btn_box = QHBoxLayout()
        btn_save = QPushButton('Lưu Element')
        btn_save.setStyleSheet('background-color: #2563eb; color: white;')
        btn_save.clicked.connect(self.accept)

        btn_cancel = QPushButton('Hủy')
        btn_cancel.setStyleSheet('background-color: #94a3b8; color: white;')
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def get_data(self):
        page_name = self.page_combo.currentText().strip()
        elem_name = self.name_input.text().strip()
        key_val = elem_name.lower().replace(' ', '_')
        return page_name, {
            'key': key_val,
            'name': elem_name,
            'module': self.module_combo.currentText(),
            'locator_type': self.locator_type_combo.currentText(),
            'locator_value': self.locator_val_input.text().strip(),
            'expected_result': self.expected_input.toPlainText().strip(),
            'actual_result': '-',
            'status': 'Sẵn sàng',
            'reason': '',
        }


# ==============================================================================
# MAIN PAGE: QUẢN LÝ TRANG
# ==============================================================================
class PageManagementPage(QWidget):
    open_test_builder_signal = Signal(str, str, dict)
    navigate_to_module_signal = Signal(str, str, dict)

    def __init__(self, header_widget=None):
        super().__init__()
        self.header = header_widget
        self.active_worker = None
        self.selected_page_filter = None
        self._is_refreshing = False

        self._build_ui()
        element_registry.data_changed.connect(self._refresh_tables)
        element_registry.test_result_updated.connect(
            self._display_detailed_test_result
        )

        if self.header and hasattr(self.header, 'page_combo'):
            self.header.page_combo.currentTextChanged.connect(
                self._on_header_page_changed
            )

        self._refresh_tables()

    def _build_ui(self):
        # Tạo ScrollArea để bọc toàn bộ nội dung, cho phép cuộn
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: #f4f7fb; border: none; }")

        # Container chứa toàn bộ giao diện
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 20, 28, 20)
        main_layout.setSpacing(16)

        # 1. TOP BAR
        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        title_label = QLabel('Quản lý trang')
        title_label.setStyleSheet('font-size: 22px; font-weight: 800; color: #0f172a;')
        subtitle_label = QLabel('Mỗi trang có URL, quyền truy cập, element và bộ test riêng.')
        subtitle_label.setStyleSheet('color: #64748b; font-size: 12px;')
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)

        self.btn_scan = QPushButton(' Scan Elements')
        self.btn_scan.setIcon(create_svg_icon(SVG_ICONS['scan']))
        self.btn_scan.setStyleSheet(
            'QPushButton { background-color: #8b5cf6; color: white; font-weight:'
            ' bold; border-radius: 6px; padding: 8px 14px; }'
        )
        self.btn_scan.clicked.connect(self.action_scan)

        self.btn_stop = QPushButton(' Stop')
        self.btn_stop.setIcon(create_svg_icon(SVG_ICONS['stop']))
        self.btn_stop.setStyleSheet(
            'QPushButton { background-color: #ef4444; color: white; font-weight:'
            ' bold; border-radius: 6px; padding: 8px 14px; }'
        )
        self.btn_stop.clicked.connect(self.action_stop)

        self.btn_reset = QPushButton(' Reset dữ liệu')
        self.btn_reset.setIcon(create_svg_icon(SVG_ICONS['reset']))
        self.btn_reset.setStyleSheet(
            'QPushButton { background-color: #64748b; color: white; font-weight:'
            ' bold; border-radius: 6px; padding: 8px 14px; }'
        )
        self.btn_reset.clicked.connect(self.action_reset)

        self.btn_add_page = QPushButton(' Thêm mới')
        self.btn_add_page.setIcon(create_svg_icon(SVG_ICONS['add']))
        self.btn_add_page.setStyleSheet(
            'QPushButton { background-color: #2563eb; color: white; font-weight:'
            ' bold; border-radius: 6px; padding: 8px 14px; }'
        )
        self.btn_add_page.clicked.connect(self.action_add_element)

        btn_box.addWidget(self.btn_scan)
        btn_box.addWidget(self.btn_stop)
        btn_box.addWidget(self.btn_reset)
        btn_box.addWidget(self.btn_add_page)

        top_bar.addLayout(title_box)
        top_bar.addStretch()
        top_bar.addLayout(btn_box)
        main_layout.addLayout(top_bar)

        # 2. CARDS THỐNG KÊ
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.card_total_pages, self.val_total_pages = (
            self._create_compact_stat_card('TỔNG SỐ TRANG')
        )
        self.card_configured, self.val_configured = self._create_compact_stat_card(
            'ĐÃ CẤU HÌNH'
        )
        self.card_test_cases, self.val_test_cases = self._create_compact_stat_card(
            'TỔNG TEST CASE'
        )
        self.card_saved_elements, self.val_saved_elements = (
            self._create_compact_stat_card('ELEMENT ĐÃ LƯU')
        )

        stats_layout.addWidget(self.card_total_pages)
        stats_layout.addWidget(self.card_configured)
        stats_layout.addWidget(self.card_test_cases)
        stats_layout.addWidget(self.card_saved_elements)
        main_layout.addLayout(stats_layout)

        # 3. BẢNG 1: DANH SÁCH TRANG
        page_list_title = QLabel(
            'Danh sách trang (Nhấn vào hàng để lọc Element tương ứng)'
        )
        page_list_title.setStyleSheet(
            'font-size: 14px; font-weight: 700; color: #334155;'
        )
        main_layout.addWidget(page_list_title)

        self.page_table = QTableWidget()
        self.page_table.setColumnCount(5)
        self.page_table.setHorizontalHeaderLabels(
            ['#', 'TRANG', 'URL / ROUTE', 'ELEMENT', 'TRẠNG THÁI']
        )
        self.page_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.page_table.setMinimumHeight(200)
        self.page_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.page_table.setStyleSheet("""
            QTableWidget { 
                background: white; 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                color: #0f172a;
                selection-background-color: #e0f2fe;
                selection-color: #0f172a;
            } 
            QTableWidget::item:selected { 
                background-color: #e0f2fe; 
                color: #0f172a; 
            }
        """)
        self.page_table.cellClicked.connect(self._on_page_row_clicked)
        main_layout.addWidget(self.page_table)

        # 4. BẢNG 2: DANH SÁCH ELEMENTS
        elem_header_layout = QHBoxLayout()
        self.elem_title = QLabel('Danh sách Elements (Hiển thị tất cả)')
        self.elem_title.setStyleSheet(
            'font-size: 14px; font-weight: 700; color: #2563eb;'
        )

        filter_label = QLabel('Lọc Module:')
        self.module_filter_combo = QComboBox()
        self.module_filter_combo.addItems([
            'Tất cả Module',
            'Dropdown List',
            'Label / Text',
            'Table',
            'Radio / Checkbox',
            'Hình ảnh',
            'Tiêu đề',
            'Giao diện',
            'Menu website',
        ])
        self.module_filter_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 4px 8px;
                color: #0f172a;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #e2e8f0;
                selection-color: #0f172a;
            }
        """)
        self.module_filter_combo.currentTextChanged.connect(
            self._refresh_element_table
        )

        # Nút "Hiển thị tất cả"
        btn_show_all = QPushButton("Hiển thị tất cả")
        btn_show_all.setObjectName("Secondary")
        btn_show_all.setFixedHeight(32)
        btn_show_all.clicked.connect(self._show_all_elements)

        elem_header_layout.addWidget(self.elem_title)
        elem_header_layout.addStretch()
        elem_header_layout.addWidget(filter_label)
        elem_header_layout.addWidget(self.module_filter_combo)
        elem_header_layout.addWidget(btn_show_all)
        main_layout.addLayout(elem_header_layout)

        self.elem_table = QTableWidget()
        self.elem_table.setColumnCount(8)
        self.elem_table.setHorizontalHeaderLabels([
            'TRANG',
            'TÊN ELEMENT',
            'MODULE',
            'LOCATOR',
            'LOCATOR VALUE',
            'EXPECTED RESULT',
            'RESULT',
            'HÀNH ĐỘNG',
        ])
        self.elem_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.elem_table.setMinimumHeight(400)
        self.elem_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.elem_table.setStyleSheet("""
            QTableWidget { 
                background: white; 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                color: #0f172a;
                selection-background-color: #f1f5f9;
                selection-color: #0f172a;
            } 
            QTableWidget::item:selected { 
                background-color: #f1f5f9; 
                color: #0f172a; 
            }
        """)
        self.elem_table.itemChanged.connect(self._on_table_item_changed)
        self.elem_table.cellClicked.connect(self._on_elem_row_clicked)
        main_layout.addWidget(self.elem_table)

        # 5. CHI TIẾT KẾT QUẢ KIỂM THỬ - CHIỀU CAO VỪA PHẢI
        self.result_detail_panel = QFrame()
        self.result_detail_panel.setStyleSheet(
            'QFrame { background-color: #ffffff; border: 1px solid #cbd5e1;'
            ' border-radius: 10px; padding: 12px; }'
        )
        self.result_detail_panel.setMinimumHeight(350)
        self.result_detail_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        result_panel_layout = QVBoxLayout(self.result_detail_panel)
        result_panel_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        self.result_detail_title = QLabel(
            'Chi tiết kết quả kiểm thử (Cập nhật tự động):'
        )
        self.result_detail_title.setStyleSheet(
            'font-weight: 800; font-size: 14px; color: #0f172a;'
        )

        self.result_detail_text = QTextEdit()
        self.result_detail_text.setReadOnly(True)
        self.result_detail_text.setMinimumHeight(200)
        self.result_detail_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_detail_text.setStyleSheet(
            'QTextEdit { background: #f8fafc; border: 1px solid #e2e8f0;'
            ' border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont,'
            ' "Segoe UI", sans-serif; font-size: 13px; padding: 10px; color: #0f172a; }'
        )

        result_panel_layout.addWidget(self.progress_bar)
        result_panel_layout.addWidget(self.result_detail_title)
        result_panel_layout.addWidget(self.result_detail_text)

        main_layout.addWidget(self.result_detail_panel)

        # Đặt container vào scroll area
        scroll.setWidget(container)

        # Gán scroll là layout chính của page
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)

    # ===== PHƯƠNG THỨC HIỂN THỊ TẤT CẢ =====
    def _show_all_elements(self):
        """Reset bộ lọc trang và module, hiển thị toàn bộ element của tất cả các trang."""
        self.selected_page_filter = None
        self.module_filter_combo.setCurrentIndex(0)
        self.elem_title.setText("Danh sách Elements (Hiển thị tất cả)")
        self._refresh_element_table()

    # =====================================

    def _create_compact_stat_card(self, title):
        card = QFrame()
        card.setStyleSheet(
            'QFrame { background-color: white; border: 1px solid #e2e8f0;'
            ' border-radius: 8px; padding: 8px 12px; }'
        )
        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 8, 10, 8)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(
            'color: #64748b; font-size: 10px; font-weight: 700; letter-spacing:'
            ' 0.5px;'
        )
        v_lbl = QLabel('0')
        v_lbl.setStyleSheet(
            'color: #0f172a; font-size: 20px; font-weight: 800;'
        )

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        return card, v_lbl

    def action_scan(self):
        self.result_detail_text.setHtml("""
            <div style="font-size: 13px; line-height: 1.6;">
                <div style="margin-bottom: 8px;">
                    <span style="background-color: #16a34a; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">
                        PLT-SCANNING
                    </span>
                    &nbsp; <b style="font-weight: bold;">Mã Kiểm Thử:</b> <code style="color:#2563eb; font-weight: normal;">PLT-SCAN-ALL</code>
                </div>
                <div style="margin-top: 8px; color: #15803d; background: #f0fdf4; padding: 8px; border-radius: 6px; border: 1px solid #bbf7d0;">
                    <b style="font-weight: bold;">[PLT-SUCCESS] Thông báo:</b> Đang thực hiện Scan toàn bộ DOM Elements trên trang hiện tại thành công!
                </div>
            </div>
        """)

    def action_stop(self):
        self.result_detail_text.setHtml("""
            <div style="font-size: 13px; line-height: 1.6;">
                <div style="margin-bottom: 8px;">
                    <span style="background-color: #dc2626; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">
                        PLT-STOPPED
                    </span>
                    &nbsp; <b style="font-weight: bold;">Mã Kiểm Thử:</b> <code style="color:#dc2626; font-weight: normal;">PLT-STOP-PROCESS</code>
                </div>
                <div style="margin-top: 8px; color: #dc2626; background: #fef2f2; padding: 8px; border-radius: 6px; border: 1px solid #fca5a5;">
                    <b style="font-weight: bold;">[PLT-ERROR] Thông báo:</b> Tiến trình kiểm thử đã bị dừng bởi người dùng!
                </div>
            </div>
        """)

    def action_reset(self):
        self.selected_page_filter = None
        element_registry.reset_to_default()
        self.result_detail_text.clear()

    def action_add_element(self):
        dialog = AddElementDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            page_name, elem_data = dialog.get_data()
            if not elem_data.get('name'):
                QMessageBox.warning(
                    self, 'Cảnh báo', 'Vui lòng nhập tên Element!'
                )
                return

            element_registry.add_or_update_element(page_name, elem_data)
            self._refresh_tables()

    def _on_page_row_clicked(self, row, col):
        page_name_item = self.page_table.item(row, 1)
        if page_name_item:
            page_name = page_name_item.text()
            self.selected_page_filter = page_name
            self._refresh_element_table()

            if self.header and hasattr(self.header, 'page_combo'):
                if self.header.page_combo.findText(page_name) < 0:
                    self.header.page_combo.addItem(page_name)
                self.header.page_combo.setCurrentText(page_name)

    def _on_elem_row_clicked(self, row, col):
        page_item = self.elem_table.item(row, 0)
        name_item = self.elem_table.item(row, 1)
        if not page_item or not name_item:
            return

        p_name = page_item.text()
        e_name = name_item.text()

        elements = element_registry.get_elements(p_name)
        selected_elem = None
        for el in elements:
            if el.get('name') == e_name:
                selected_elem = el
                break

        if not selected_elem:
            return

        status_str = str(selected_elem.get('status', 'Sẵn sàng')).upper()

        if 'PASS' in status_str or 'FAIL' in status_str:
            if 'last_result_payload' in selected_elem:
                self._display_detailed_test_result(selected_elem['last_result_payload'])
            else:
                payload = {
                    'page_name': p_name,
                    'element_key': selected_elem.get('key', e_name),
                    'element_name': e_name,
                    'locator_type': selected_elem.get('locator_type', 'css'),
                    'locator_value': selected_elem.get('locator_value', ''),
                    'expected': selected_elem.get('expected_result', ''),
                    'actual': selected_elem.get('actual_result', '-'),
                    'status': selected_elem.get('status', 'FAILED'),
                    'message': selected_elem.get('reason', ''),
                }
                self._display_detailed_test_result(payload)
        else:
            self.result_detail_text.clear()

    def _on_header_page_changed(self, page_name):
        self._refresh_element_table()

    def _refresh_tables(self):
        self._update_stat_cards()
        self._refresh_page_table()
        self._refresh_element_table()

    def _update_stat_cards(self):
        pages = (
            self.header.PAGES_MAP
            if (self.header and hasattr(self.header, 'PAGES_MAP'))
            else {}
        )
        total_pages = max(len(pages), len(element_registry._store))
        all_elements = []
        configured_count = 0
        for p_name, elems in element_registry._store.items():
            if elems:
                configured_count += 1
                all_elements.extend(elems)

        total_elements = len(all_elements)
        self.val_total_pages.setText(f'{total_pages:02d}')
        self.val_configured.setText(f'{configured_count:02d}')
        self.val_test_cases.setText(f'{total_elements:02d}')
        self.val_saved_elements.setText(f'{total_elements:02d}')

    def _refresh_page_table(self):
        pages = (
            self.header.PAGES_MAP
            if (self.header and hasattr(self.header, 'PAGES_MAP'))
            else {}
        )

        all_page_names = []
        for p in element_registry._store.keys():
            if p != 'Tài chính' and p not in all_page_names:
                all_page_names.append(p)
        for p in pages.keys():
            if p != 'Tài chính' and p not in all_page_names:
                all_page_names.append(p)

        self.page_table.setRowCount(len(all_page_names))
        for row, name in enumerate(all_page_names):
            url = pages.get(name, f'/{name.lower().replace(" ", "-")}')
            elements_count = len(element_registry.get_elements(name))

            self.page_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.page_table.setItem(row, 1, QTableWidgetItem(name))
            self.page_table.setItem(row, 2, QTableWidgetItem(url))
            self.page_table.setItem(
                row, 3, QTableWidgetItem(str(elements_count))
            )

            status_item = QTableWidgetItem('Sẵn sàng')
            status_item.setForeground(Qt.black)
            self.page_table.setItem(row, 4, status_item)

    def _refresh_element_table(self):
        self._is_refreshing = True
        self.elem_table.blockSignals(True)

        if self.selected_page_filter:
            self.elem_title.setText(
                f"Danh sách Elements thuộc Trang: '{self.selected_page_filter}'"
            )
            elements = element_registry.get_elements(self.selected_page_filter)
            for e in elements:
                e['page_name'] = self.selected_page_filter
        else:
            self.elem_title.setText('Danh sách Elements (Hiển thị tất cả)')
            elements = element_registry.get_elements()

        filter_mod = self.module_filter_combo.currentText()
        if filter_mod != 'Tất cả Module':
            elements = [e for e in elements if e.get('module') == filter_mod]

        self.elem_table.setRowCount(len(elements))

        for row, el in enumerate(elements):
            p_name = el.get('page_name', 'Trang tổng quan')
            self.elem_table.setItem(row, 0, QTableWidgetItem(p_name))
            self.elem_table.setItem(
                row, 1, QTableWidgetItem(el.get('name', ''))
            )
            self.elem_table.setItem(
                row, 2, QTableWidgetItem(el.get('module', ''))
            )

            locator_combo = QComboBox()
            locator_combo.addItems(
                ['css', 'xpath', 'id', 'name', 'class', 'tag']
            )
            locator_combo.setCurrentText(el.get('locator_type', 'css'))
            locator_combo.setStyleSheet("""
                QComboBox { 
                    background: white; 
                    border: 1px solid #cbd5e1; 
                    border-radius: 4px; 
                    padding: 2px 5px; 
                    color: #0f172a; 
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #0f172a;
                    selection-background-color: #e2e8f0;
                    selection-color: #0f172a;
                }
            """)
            locator_combo.currentTextChanged.connect(
                lambda text, page=p_name, elem=el: self._on_locator_combo_changed(
                    page, elem, text
                )
            )
            self.elem_table.setCellWidget(row, 3, locator_combo)

            self.elem_table.setItem(
                row, 4, QTableWidgetItem(el.get('locator_value', ''))
            )
            self.elem_table.setItem(
                row, 5, QTableWidgetItem(el.get('expected_result', ''))
            )

            status = el.get('status', 'Sẵn sàng')
            res_item = QTableWidgetItem(status)
            if 'PASSED' in status.upper() or 'PASS' in status.upper():
                res_item.setForeground(Qt.green)
            elif 'FAILED' in status.upper() or 'FAIL' in status.upper() or 'ERROR' in status.upper():
                res_item.setForeground(Qt.red)
            else:
                res_item.setForeground(Qt.black)

            self.elem_table.setItem(row, 6, res_item)

            btn_test = QPushButton(' Kiểm thử')
            btn_test.setIcon(
                create_svg_icon(SVG_ICONS['play'], color='#047857')
            )
            btn_test.setStyleSheet(
                'background-color: #ecfdf5; color: #047857; font-weight: bold;'
                ' border-radius: 4px; border: 1px solid #a7f3d0;'
            )
            btn_test.clicked.connect(
                lambda ch, elem=el, page=p_name, r=row: self._go_to_module_test(
                    page, elem, r
                )
            )
            self.elem_table.setCellWidget(row, 7, btn_test)

        self.elem_table.blockSignals(False)
        self._is_refreshing = False

    def _on_locator_combo_changed(self, page_name, elem_data, new_locator_type):
        if self._is_refreshing:
            return
        elem_data['locator_type'] = new_locator_type
        element_registry.add_or_update_element(page_name, elem_data)

    def _on_table_item_changed(self, item):
        if self._is_refreshing:
            return

        row = item.row()
        col = item.column()
        if col in (4, 5):
            page_item = self.elem_table.item(row, 0)
            name_item = self.elem_table.item(row, 1)
            if not page_item or not name_item:
                return

            page_name = page_item.text()
            elem_name = name_item.text()

            elements = element_registry.get_elements(page_name)
            for el in elements:
                if el.get('name') == elem_name:
                    if col == 4:
                        el['locator_value'] = item.text().strip()
                    elif col == 5:
                        el['expected_result'] = item.text().strip()
                    element_registry.add_or_update_element(page_name, el)
                    break

    def _go_to_module_test(self, page_name, elem_data, row_idx):
        locator_widget = self.elem_table.cellWidget(row_idx, 3)
        if isinstance(locator_widget, QComboBox):
            elem_data['locator_type'] = locator_widget.currentText()

        val_item = self.elem_table.item(row_idx, 4)
        if val_item:
            elem_data['locator_value'] = val_item.text().strip()

        exp_item = self.elem_table.item(row_idx, 5)
        if exp_item:
            elem_data['expected_result'] = exp_item.text().strip()

        element_registry.add_or_update_element(page_name, elem_data)

        module_name = elem_data.get('module', 'Label / Text')
        module_key = get_module_key(module_name)

        self.navigate_to_module_signal.emit(module_key, page_name, elem_data)

    # ============ NHẬN KẾT QUẢ TỪ TEST BUILDER ============
    def _on_test_result_received(self, payload: dict):
        result_payload = {
            'page_name': payload.get('page_name'),
            'element_key': payload.get('element_name'),
            'element_name': payload.get('element_name'),
            'locator_type': payload.get('locator_type'),
            'locator_value': payload.get('locator_value'),
            'expected': payload.get('expected'),
            'actual': payload.get('actual'),
            'status': payload.get('status'),
            'message': payload.get('message'),
        }
        element_registry.notify_test_result(result_payload)

    # =========================================================

    def _format_plt_value(self, val_str):
        if not val_str or val_str == '-':
            return '-'

        lines = [
            l.strip()
            for l in str(val_str).replace('\r', '').split('\n')
            if l.strip()
        ]
        if not lines:
            return '-'

        cleaned_lines = [re.sub(r'^(\d+[\.-]\s*)+', '', line) for line in lines]

        if len(cleaned_lines) > 1:
            formatted_lines = [
                f'{i + 1}-{line}' for i, line in enumerate(cleaned_lines)
            ]
            return '<br>'.join(formatted_lines)
        return cleaned_lines[0] if cleaned_lines else '-'

    def _display_detailed_test_result(self, payload):
        raw_status = str(payload.get('status', '')).upper()

        if 'PASS' not in raw_status and 'FAIL' not in raw_status:
            self.result_detail_text.clear()
            return

        is_passed = 'PASS' in raw_status
        plt_status = 'PLT-PASSED' if is_passed else 'PLT-FAILED'

        raw_key = payload.get(
            'element_key', payload.get('element_name', 'TEST')
        )
        plt_case_id = (
            raw_key
            if str(raw_key).startswith('PLT-')
            else f'PLT-{str(raw_key).upper()}'
        )

        badge_color = '#16a34a' if is_passed else '#dc2626'

        exp_formatted = self._format_plt_value(payload.get('expected', ''))
        act_formatted = self._format_plt_value(payload.get('actual', ''))

        html = f"""
        <div style="font-size: 13px; line-height: 1.6; color: #0f172a;">
            <div style="margin-bottom: 8px;">
                <span style="background-color: {badge_color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">
                    {plt_status}
                </span>
                &nbsp; <b style="font-weight: bold;">Mã Kiểm Thử:</b> <code style="color:#2563eb; font-weight: normal;">{plt_case_id}</code> 
                | <b style="font-weight: bold;">Trang:</b> <span style="font-weight: normal;">{payload.get('page_name', '-')}</span> 
                | <b style="font-weight: bold;">Element:</b> <span style="font-weight: normal;">{payload.get('element_name', '-')}</span>
            </div>
            <table border="0" style="width: 100%; border-collapse: collapse; margin-top: 5px;">
                <tr>
                    <td style="width: 140px; color: #475569; font-weight: bold;">Mã Kết Quả:</td>
                    <td style="font-weight: normal; color: {badge_color};"><b>{plt_status}</b></td>
                </tr>
                <tr>
                    <td style="color: #475569; font-weight: bold;">Locator Type:</td>
                    <td style="font-weight: normal;"><code>{payload.get('locator_type', '-')}</code></td>
                </tr>
                <tr>
                    <td style="color: #475569; font-weight: bold;">Locator Value:</td>
                    <td style="font-weight: normal;"><code>{payload.get('locator_value', '-')}</code></td>
                </tr>
                <tr>
                    <td style="color: #475569; font-weight: bold; vertical-align: top;">PLT Expected:</td>
                    <td style="font-weight: normal; color: #0284c7;">{exp_formatted}</td>
                </tr>
                <tr>
                    <td style="color: #475569; font-weight: bold; vertical-align: top;">PLT Actual:</td>
                    <td style="font-weight: normal; color: #0f172a;">{act_formatted}</td>
                </tr>
            </table>
        """

        msg = payload.get('message', '')
        if is_passed:
            html += f"""
            <div style="margin-top: 8px; color: #15803d; background: #f0fdf4; padding: 8px; border-radius: 6px; border: 1px solid #bbf7d0;">
                <b style="font-weight: bold;">[PLT-SUCCESS] Thông báo chi tiết:</b> <span style="font-weight: normal;">{msg or "Kiểm thử thành công! Dữ liệu Actual trùng khớp hoàn toàn với Expected."}</span>
            </div>
            """
        else:
            html += f"""
            <div style="margin-top: 8px; color: #dc2626; background: #fef2f2; padding: 8px; border-radius: 6px; border: 1px solid #fca5a5;">
                <b style="font-weight: bold;">[PLT-ERROR] Thông báo chi tiết:</b> <span style="font-weight: normal;">{msg or "Kiểm thử thất bại! Dữ liệu không trùng khớp."}</span>
            </div>
            """

        html += '</div>'
        self.result_detail_text.setHtml(html)