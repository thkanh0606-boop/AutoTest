import copy
import re
from html import escape
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
    """Hàm chuẩn hóa chuỗi tên Module về key màn hình Builder chuẩn"""
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
        ],
        'Đặt xe': [],
        'Xe': [],
        'Danh mục xe': [],
        'Người dùng': [],
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
        """Reset danh sách về ban đầu hoàn toàn"""
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
            'Title',
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
    navigate_to_module_signal = Signal(str, str, str)

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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 20, 28, 20)
        main_layout.setSpacing(16)

        # 1. TOP BAR
        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        title_label = QLabel('Quản lý trang')
        title_label.setStyleSheet(
            'font-size: 22px; font-weight: 800; color: #0f172a;'
        )
        subtitle_label = QLabel(
            'Mỗi trang có URL, quyền truy cập, element và bộ test riêng.'
        )
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
        # Sửa CSS giữ chữ rõ ràng không đổi màu trắng khi chọn
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
        self.page_table.setFixedHeight(180)
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

        elem_header_layout.addWidget(self.elem_title)
        elem_header_layout.addStretch()
        elem_header_layout.addWidget(filter_label)
        elem_header_layout.addWidget(self.module_filter_combo)
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
        # Sửa CSS bảng Element giữ chữ đen/rõ nét không biến thành chữ trắng
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
        self.elem_table.setFixedHeight(210)
        self.elem_table.itemChanged.connect(self._on_table_item_changed)
        self.elem_table.cellClicked.connect(self._on_elem_row_clicked)
        main_layout.addWidget(self.elem_table)

        # 5. CHI TIẾT KẾT QUẢ KIỂM THỬ
        self.result_detail_panel = QFrame()
        self.result_detail_panel.setStyleSheet(
            'QFrame { background-color: #ffffff; border: 1px solid #cbd5e1;'
            ' border-radius: 10px; padding: 12px; }'
        )
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
        self.result_detail_text.setStyleSheet(
            'QTextEdit { background: #f8fafc; border: 1px solid #e2e8f0;'
            ' border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont,'
            ' "Segoe UI", sans-serif; font-size: 13px; padding: 10px; color: #0f172a; }'
        )

        result_panel_layout.addWidget(self.progress_bar)
        result_panel_layout.addWidget(self.result_detail_title)
        result_panel_layout.addWidget(self.result_detail_text)

        main_layout.addWidget(self.result_detail_panel)

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
        """Khôi phục toàn bộ danh sách dữ liệu về ban đầu"""
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
            self.selected_page_filter = page_name_item.text()
            self._refresh_element_table()

    def _on_elem_row_clicked(self, row, col):
        """Khi bấm vào một hàng element, chỉ hiển thị kết quả nếu là PASSED hoặc FAILED"""
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

        # CHỈ hiển thị chi tiết khi có trạng thái PASSED hoặc FAILED
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
            # Nếu ở trạng thái "Sẵn sàng" -> xóa trắng kết quả chi tiết
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
            status_item.setForeground(Qt.black)  # Đã đổi thành màu đen
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
            # Fix CSS dropdown item không bị đổi chữ thành màu trắng
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
                res_item.setForeground(Qt.black)  # Đã đổi chữ "Sẵn sàng" thành màu đen

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

        self.navigate_to_module_signal.emit(
            module_key, page_name, elem_data.get('key', elem_data.get('name'))
        )

    def _format_plt_value(self, val_str):
        """Format chuỗi hiển thị trong bảng chi tiết"""
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
        """Hiển thị bảng chi tiết kết quả kiểm thử (chỉ áp dụng cho PASSED / FAILED)"""
        raw_status = str(payload.get('status', '')).upper()

        # Nếu không có kết quả PASS hoặc FAIL -> xóa trắng chi tiết
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

        comparison_rows = payload.get('pairs') or []
        if not comparison_rows:
            comparison_rows = [
                {
                    'expected': payload.get('expected', ''),
                    'actual': payload.get('actual', ''),
                    'status': 'PASS' if is_passed else 'FAIL',
                }
            ]

        comparison_html = ''
        for item in comparison_rows:
            result_value = str(item.get('status', '')).upper()
            result_color = '#16a34a' if result_value == 'PASS' else '#dc2626'
            comparison_html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; vertical-align: top; color:#0284c7;">
                        {self._format_plt_value(escape(str(item.get('expected', ''))))}
                    </td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; vertical-align: top; color:#0f172a;">
                        {self._format_plt_value(escape(str(item.get('actual', ''))))}
                    </td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; vertical-align: top; font-weight: 800; color:{result_color};">
                        {escape(result_value)}
                    </td>
                </tr>
            """

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
            </table>
            <table border="0" style="width: 100%; border-collapse: collapse; margin-top: 10px; background: #ffffff;">
                <thead>
                    <tr>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; background:#f1f5f9; text-align:left;">Expected Result</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; background:#f1f5f9; text-align:left;">Actual Result</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; background:#f1f5f9; text-align:left;">Result</th>
                    </tr>
                </thead>
                <tbody>{comparison_html}</tbody>
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
