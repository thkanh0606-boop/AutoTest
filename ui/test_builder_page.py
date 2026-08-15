import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.helpers.worker import SeleniumWorker
from core.table_file_loader import load_table_file
from core.test_contract import TestContract
from runners.text_dropdown_runner import run_label_text_test

try:
    from ui.page_management_page import element_registry
except ImportError:
    try:
        from page_management_page import element_registry
    except ImportError:
        element_registry = None


class TestBuilderPage(QWidget):

    def __init__(self, module_key: str, title: str):
        super().__init__()
        self.module_key = module_key
        self.title = title
        self.worker = None
        self.page_by_index = []
        self.element_by_index = []
        self.table_file_path = ''

        self.setObjectName('TestBuilderPage')
        self.setStyleSheet("""
            QWidget#TestBuilderPage { background-color: #f4f7fb; }
            QLabel { background: transparent; color: #102033; }
            QFrame { background-color: #ffffff; border: 1px solid #dfe5ec; border-radius: 10px; }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #f8fafc; border: 1px solid #cfd8e3;
                border-radius: 8px; color: #102033; font-size: 13px; padding: 8px 10px;
            }
            QComboBox::drop-down { border: none; width: 24px; }
            QPushButton { border-radius: 8px; font-size: 13px; font-weight: 700; padding: 0 16px; }
            QPushButton#runButton { background-color: #2563eb; color: #ffffff; border: none; }
            QPushButton#runButton:disabled { background-color: #94a3b8; }
        """)

        self._build_ui()
        self._load_pages()

    def _build_ui(self):
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName('TestBuilderScrollContent')
        scroll.setWidget(content)
        shell.addWidget(scroll)

        root = QVBoxLayout(content)
        root.setContentsMargins(58, 36, 58, 36)
        root.setSpacing(22)

        context = QFrame()
        context.setStyleSheet(
            'QFrame { background-color: #eef4ff; border: 1px solid #d6e4ff; }'
        )
        context_layout = QHBoxLayout(context)
        context_layout.setContentsMargins(18, 12, 18, 12)
        self.context_label = QLabel('PCM')
        self.context_label.setTextFormat(Qt.RichText)
        self.case_count_label = QLabel('Trang kiểm thử')
        self.case_count_label.setStyleSheet('color: #12365f; font-size: 12px;')
        context_layout.addWidget(self.context_label)
        context_layout.addStretch()
        context_layout.addWidget(self.case_count_label)
        root.addWidget(context)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        eyebrow = QLabel(f'TEST BUILDER · {self.module_key.upper()}')
        eyebrow.setStyleSheet(
            'color: #2563eb; font-size: 11px; font-weight: 800; letter-spacing:'
            ' 2px;'
        )
        title = QLabel(self.title)
        title.setStyleSheet('font-size: 30px; font-weight: 700; color: #071a33;')
        subtitle = QLabel(
            'Chọn trang PCM, chọn element cần kiểm tra, nhập Expected Result rồi'
            ' Run.'
        )
        subtitle.setStyleSheet('color: #52657a; font-size: 13px;')
        title_box.addWidget(eyebrow)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        root.addLayout(header)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(18)
        form_grid.setVerticalSpacing(18)
        form_grid.addWidget(self._create_page_panel(), 0, 0)
        form_grid.addWidget(self._create_expected_panel(), 0, 1)
        root.addLayout(form_grid)

        result_panel = QFrame()
        result_layout = QVBoxLayout(result_panel)
        result_layout.setContentsMargins(22, 18, 22, 18)
        result_layout.setSpacing(10)
        result_title = QLabel('Actual Result')
        result_title.setStyleSheet('font-size: 18px; font-weight: 700;')
        self.status_label = QLabel('Sẵn sàng chạy kiểm thử')
        self.status_label.setStyleSheet('color: #64748b; font-size: 12px;')
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.actual_value = QLabel('Chưa có Actual Result')
        self.actual_value.setWordWrap(True)
        self.actual_value.setStyleSheet(
            'color: #102033; font-size: 14px; padding: 12px; background: #f8fafc;'
            ' border: 1px solid #dfe5ec; border-radius: 8px;'
        )
        self.compare_value = QLabel('Expected - Actual sẽ hiển thị sau khi Run.')
        self.compare_value.setWordWrap(True)
        self.compare_value.setStyleSheet('color: #64748b; font-size: 12px;')

        action_row = QHBoxLayout()
        action_row.addStretch()
        reset_button = QPushButton('Đặt lại')
        reset_button.setFixedHeight(38)
        reset_button.clicked.connect(self._reset_result)
        self.run_button = QPushButton('▶ Run Test')
        self.run_button.setObjectName('runButton')
        self.run_button.setFixedHeight(38)
        self.run_button.clicked.connect(self._run_test)
        action_row.addWidget(reset_button)
        action_row.addWidget(self.run_button)

        result_layout.addWidget(result_title)
        result_layout.addWidget(self.status_label)
        result_layout.addWidget(self.progress)
        result_layout.addWidget(self.actual_value)
        result_layout.addWidget(self.compare_value)
        result_layout.addLayout(action_row)
        root.addWidget(result_panel)
        root.addStretch()

    def _create_page_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        title = QLabel('01  Element trên trang')
        title.setStyleSheet('font-size: 18px; font-weight: 700;')
        layout.addWidget(title)

        self.page_combo = QComboBox(panel)
        self.page_combo.currentIndexChanged.connect(self._on_page_changed)
        self.page_combo.hide()

        self.url_input = QLineEdit(panel)
        self.url_input.hide()

        row = QHBoxLayout()
        element_col = QVBoxLayout()
        element_col.addWidget(QLabel('Element'))
        self.element_combo = QComboBox()
        self.element_combo.currentIndexChanged.connect(self._on_element_changed)
        element_col.addWidget(self.element_combo)

        locator_type_col = QVBoxLayout()
        locator_type_col.addWidget(QLabel('Locator'))
        self.locator_type_combo = QComboBox()
        self.locator_type_combo.addItems(
            ['css', 'xpath', 'id', 'name', 'class', 'tag']
        )
        self.locator_type_combo.currentTextChanged.connect(
            lambda: self._sync_to_management(status='Sẵn sàng')
        )
        locator_type_col.addWidget(self.locator_type_combo)
        row.addLayout(element_col)
        row.addLayout(locator_type_col)
        layout.addLayout(row)

        layout.addWidget(QLabel('Locator value'))
        self.locator_input = QLineEdit()
        self.locator_input.textChanged.connect(
            lambda: self._sync_to_management(status='Sẵn sàng')
        )
        layout.addWidget(self.locator_input)

        hint = QLabel(
            '✓ Có thể sửa locator nếu selector thực tế của PCM khác dữ liệu mẫu'
        )
        hint.setStyleSheet(
            'color: #16845b; background: #ecfdf5; padding: 9px; border-radius:'
            ' 8px;'
        )
        layout.addWidget(hint)
        return panel

    def _create_expected_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        title = QLabel('02  Expected Result')
        title.setStyleSheet('font-size: 18px; font-weight: 700;')
        subtitle = QLabel('Nhập text/số liệu mong đợi của element đã chọn')
        subtitle.setStyleSheet('color: #64748b; font-size: 12px;')
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(QLabel('Expected'))
        self.expected_input = QTextEdit()
        self.expected_input.setMinimumHeight(130)
        self.expected_input.textChanged.connect(
            lambda: self._sync_to_management(status='Sẵn sàng')
        )
        layout.addWidget(self.expected_input)

        if self.module_key == 'table':
            upload_row = QHBoxLayout()
            upload_button = QPushButton('Upload Excel/CSV')
            upload_button.setFixedHeight(36)
            upload_button.clicked.connect(self._select_table_file)
            self.table_file_label = QLabel('Chưa chọn file')
            self.table_file_label.setStyleSheet('color: #64748b; font-size: 12px;')
            upload_row.addWidget(upload_button)
            upload_row.addWidget(self.table_file_label, 1)
            layout.addLayout(upload_row)

        option_row = QHBoxLayout()
        self.trim_checkbox = QCheckBox('Bỏ qua khoảng trắng')
        self.trim_checkbox.setChecked(True)
        self.case_checkbox = QCheckBox('Phân biệt hoa thường')
        self.case_checkbox.setChecked(True)
        option_row.addWidget(self.trim_checkbox)
        option_row.addWidget(self.case_checkbox)
        option_row.addStretch()
        layout.addLayout(option_row)
        return panel

    def _load_pages(self):
        self.page_by_index = list(TestContract.pages)
        self.page_combo.clear()
        for page in self.page_by_index:
            self.page_combo.addItem(page.name)
        self._on_page_changed(0)

    def set_page_by_key(self, page_key: str):
        """Chọn đúng trang kiểm thử từ Header và nạp lại element theo module hiện tại."""
        for index, page in enumerate(self.page_by_index):
            if page.key == page_key:
                if self.page_combo.currentIndex() == index:
                    self._on_page_changed(index)
                else:
                    self.page_combo.setCurrentIndex(index)
                return True
        return False

    def _on_page_changed(self, index):
        if index < 0 or index >= len(self.page_by_index):
            return

        page = self.page_by_index[index]
        self.context_label.setText(
            f"<b style='color:#2563eb'>PCM</b> &nbsp; {page.name} &nbsp; <span"
            f" style='color:#64748b'>{page.path}</span>"
        )
        self.url_input.setText(page.url)

        elements = TestContract.elements_for(page.key, self.module_key)
        
        if not elements and self.module_key in (
            'title',
            'ui',
            'menu',
            'image',
            'radio',
            'table',
        ):
            elements = TestContract.elements_for(page.key, 'label')

        self.element_by_index = list(elements) if elements else []
        self.element_combo.blockSignals(True)
        self.element_combo.clear()
        for element in self.element_by_index:
            self.element_combo.addItem(element.name)
        self.element_combo.blockSignals(False)
        self.case_count_label.setText(f'{len(self.element_by_index)} elements')
        
        if self.element_by_index:
            self._on_element_changed(0)
        else:
            self.locator_input.clear()
            self.expected_input.clear()

    def _on_element_changed(self, index):
        if index < 0 or index >= len(self.element_by_index):
            self.locator_input.clear()
            self.expected_input.clear()
            return

        element = self.element_by_index[index]
        current_page_name = (
            self.page_by_index[self.page_combo.currentIndex()].name
            if self.page_by_index
            else ''
        )

        reg_elem = None
        if element_registry and current_page_name:
            reg_list = element_registry.get_elements(current_page_name)
            for r in reg_list:
                if r.get('name') == element.name or (
                    r.get('key') and r.get('key') == element.key
                ):
                    reg_elem = r
                    break

        self.locator_type_combo.blockSignals(True)
        self.locator_input.blockSignals(True)
        self.expected_input.blockSignals(True)

        if reg_elem:
            self.locator_type_combo.setCurrentText(
                reg_elem.get('locator_type', element.locator_type)
            )
            self.locator_input.setText(
                reg_elem.get('locator_value', element.locator_value)
            )
            self.expected_input.setPlainText(reg_elem.get('expected_result', ''))
        else:
            self.locator_type_combo.setCurrentText(element.locator_type)
            self.locator_input.setText(element.locator_value)
            self.expected_input.clear()

        self.locator_type_combo.blockSignals(False)
        self.locator_input.blockSignals(False)
        self.expected_input.blockSignals(False)

        self._sync_to_management(status='Sẵn sàng')

    def _select_table_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Chọn file expected cho Table',
            '',
            'Table files (*.xlsx *.csv);;Excel files (*.xlsx);;CSV files'
            ' (*.csv)',
        )
        if not file_path:
            return

        try:
            expected_text = load_table_file(file_path)
        except Exception as error:
            self.status_label.setText(f'Không đọc được file: {error}')
            return

        self.table_file_path = file_path
        self.expected_input.setPlainText(expected_text)
        if hasattr(self, 'table_file_label'):
            self.table_file_label.setText(file_path)
        self.status_label.setText('Đã tải dữ liệu expected từ file.')

    def _sync_to_management(
        self, status='Sẵn sàng', actual_result='-', reason=''
    ):
        if not element_registry or not self.page_by_index or not self.element_by_index:
            return

        page_idx = self.page_combo.currentIndex()
        elem_idx = self.element_combo.currentIndex()

        if page_idx < 0 or page_idx >= len(self.page_by_index):
            return
        if elem_idx < 0 or elem_idx >= len(self.element_by_index):
            return

        page = self.page_by_index[page_idx]
        element = self.element_by_index[elem_idx]

        module_display = self.module_key.replace('_', ' ').title()
        if self.module_key == 'dropdown':
            module_display = 'Dropdown List'
        elif self.module_key in ('label', 'text'):
            module_display = 'Label / Text'
        elif self.module_key == 'table':
            module_display = 'Table'
        elif self.module_key == 'radio':
            module_display = 'Radio / Checkbox'

        locator_type = self.locator_type_combo.currentText()
        locator_val = self.locator_input.text().strip()

        element_registry.add_or_update_element(
            page.name,
            {
                'key': element.key,
                'name': element.name,
                'module': module_display,
                'locator_type': locator_type,
                'locator_value': locator_val,
                'expected_result': self.expected_input.toPlainText(),
                'actual_result': actual_result,
                'status': status,
                'reason': reason,
            },
        )

    def _run_test(self):
        if self.worker and self.worker.isRunning():
            return
        if not self.element_by_index:
            self.status_label.setText('Chưa có element cho trang kiểm thử này.')
            return

        page = self.page_by_index[self.page_combo.currentIndex()]
        element = self.element_by_index[self.element_combo.currentIndex()]
        expected_text = self.expected_input.toPlainText()

        self.run_button.setEnabled(False)
        self.progress.setValue(0)
        self.actual_value.setText('Đang chạy Selenium...')
        self.compare_value.setText('Đang lấy Actual Result từ PCM.')

        self.worker = SeleniumWorker(
            run_label_text_test,
            module=self.module_key,
            url=self.url_input.text().strip(),
            page_key=page.key,
            page_name=page.name,
            element_key=element.key,
            element_name=element.name,
            locator_type=self.locator_type_combo.currentText(),
            locator_value=self.locator_input.text().strip(),
            expected=expected_text,
            case_id=element.case_id,
            steps=element.steps,
            expected_result=expected_text,
            action_type=element.action_type,
            target_path=element.target_path,
            trim=self.trim_checkbox.isChecked(),
            case_sensitive=self.case_checkbox.isChecked(),
            headless=False,
            persist=True,
        )
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.log_signal.connect(self.status_label.setText)
        self.worker.result_signal.connect(self._handle_result)
        self.worker.finished_signal.connect(self._handle_finished)
        self.worker.start()

    def _format_plt_value(self, val_str):
        """Hàm chuẩn hóa định dạng danh sách thành '1-Tiếng Việt', '2-English'"""
        if not val_str or val_str == '-':
            return '-'

        raw_lines = [
            l.strip()
            for l in str(val_str).replace('\r', '').split('\n')
            if l.strip()
        ]
        if not raw_lines:
            return '-'

        # Xóa tiền tố tiền định dạng cũ nếu có (vd: "1-", "2. ")
        cleaned_lines = [re.sub(r'^\d+[\.-]\s*', '', line) for line in raw_lines]

        if len(cleaned_lines) > 1:
            return '\n'.join([f'{i + 1}-{line}' for i, line in enumerate(cleaned_lines)])
        return cleaned_lines[0]

    def _handle_result(self, payload):
        raw_actual = (payload.get('actual', '') or '').replace('\t', '\n')
        raw_expected = payload.get('expected', '') or ''

        # Định dạng dạng 1-..., 2-... cho cả Expected và Actual
        formatted_actual = self._format_plt_value(raw_actual)
        formatted_expected = self._format_plt_value(raw_expected)

        self.actual_value.setText(formatted_actual)
        status = payload.get('status', 'FAILED')
        message = payload.get('message', '')

        compare_text = (
            f"Expected:\n{formatted_expected}\n\n"
            f"Actual:\n{formatted_actual}\n\n"
            f"Result: {status} - {message}"
        )
        self.compare_value.setText(compare_text)
        color = '#16845b' if 'PASSED' in status else '#b42318'
        self.compare_value.setStyleSheet(
            f'color: {color}; font-size: 12px; font-weight: 700;'
        )

        # ĐỒNG BỘ KẾT QUẢ VỀ MANAGEMENT DÀNH CHO BẢNG & PANEL CHI TIẾT
        self._sync_to_management(
            status=status, actual_result=formatted_actual, reason=message
        )

        if element_registry:
            page = self.page_by_index[self.page_combo.currentIndex()]
            element = self.element_by_index[self.element_combo.currentIndex()]
            result_detail = {
                'page_name': page.name,
                'element_key': element.key,
                'element_name': element.name,
                'locator_type': self.locator_type_combo.currentText(),
                'locator_value': self.locator_input.text().strip(),
                'expected': formatted_expected,
                'actual': formatted_actual,
                'status': status,
                'message': message,
            }
            element_registry.notify_test_result(result_detail)

    def _handle_finished(self, _finished):
        self.run_button.setEnabled(True)

    def _reset_result(self):
        self.progress.setValue(0)
        self.status_label.setText('Sẵn sàng chạy kiểm thử')
        self.actual_value.setText('Chưa có Actual Result')
        self.compare_value.setText('Expected - Actual sẽ hiển thị sau khi Run.')
        self.compare_value.setStyleSheet('color: #64748b; font-size: 12px;')
        self._sync_to_management(status='Sẵn sàng', actual_result='-', reason='')

    def select_page_and_element(self, page_name: str, element_key_or_name: str):
        """Hàm chọn đúng Trang, Element và đồng bộ lại tham số từ Quản lý trang sang"""
        target_page_idx = -1
        for idx, page in enumerate(self.page_by_index):
            if page.name == page_name or page.key == page_name:
                target_page_idx = idx
                break

        if target_page_idx != -1:
            if self.page_combo.currentIndex() == target_page_idx:
                self._on_page_changed(target_page_idx)
            else:
                self.page_combo.setCurrentIndex(target_page_idx)

        target_elem_idx = -1
        for idx, elem in enumerate(self.element_by_index):
            if elem.name == element_key_or_name or elem.key == element_key_or_name:
                target_elem_idx = idx
                break

        if target_elem_idx != -1:
            if self.element_combo.currentIndex() == target_elem_idx:
                self._on_element_changed(target_elem_idx)
            else:
                self.element_combo.setCurrentIndex(target_elem_idx)
        else:
            if self.element_combo.count() > 0:
                self._on_element_changed(0)
