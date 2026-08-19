from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QFileDialog,
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


class TestBuilderPage(QWidget):
    # Phát ra mỗi khi trang PCM đang test bên trong màn này đổi (name, url) -
    # để MainWindow đồng bộ lại thanh header "TRANG ĐANG KIỂM THỬ" cho khớp.
    page_selected = Signal(str, str)

    def __init__(self, module_key: str, title: str):
        super().__init__()
        self.module_key = module_key
        self.title = title
        self.worker = None
        self.page_by_index = []
        self.element_by_index = []
        self.table_file_path = ""

        self.setObjectName("TestBuilderPage")
        self.setStyleSheet("""
            QWidget#TestBuilderPage {
                background-color: #f4f7fb;
            }

            QLabel {
                background: transparent;
                color: #102033;
            }

            QFrame {
                background-color: #ffffff;
                border: 1px solid #dfe5ec;
                border-radius: 10px;
            }

            QLineEdit, QComboBox, QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #cfd8e3;
                border-radius: 8px;
                color: #102033;
                font-size: 13px;
                padding: 8px 10px;
            }

            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            QPushButton {
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 16px;
            }

            QPushButton#runButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
            }

            QPushButton#runButton:disabled {
                background-color: #94a3b8;
            }

            QPushButton#locatorButton {
                background-color: #f8fbff;
                color: #12365f;
                border: 1px solid #1f5caa;
            }
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
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #f4f7fb;
                border: none;
            }
            QScrollBar:vertical {
                background: #eef2f6;
                width: 10px;
                margin: 4px 2px 4px 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #b8c4d2;
                border-radius: 5px;
                min-height: 36px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content = QWidget()
        content.setObjectName("TestBuilderScrollContent")
        content.setStyleSheet("QWidget#TestBuilderScrollContent { background-color: #f4f7fb; }")
        scroll.setWidget(content)
        shell.addWidget(scroll)

        root = QVBoxLayout(content)
        root.setContentsMargins(58, 36, 58, 36)
        root.setSpacing(22)

        context = QFrame()
        context.setStyleSheet("QFrame { background-color: #eef4ff; border: 1px solid #d6e4ff; }")
        context_layout = QHBoxLayout(context)
        context_layout.setContentsMargins(18, 12, 18, 12)
        self.context_label = QLabel("PCM")
        self.context_label.setTextFormat(Qt.RichText)
        self.case_count_label = QLabel("Trang kiểm thử")
        self.case_count_label.setStyleSheet("color: #12365f; font-size: 12px;")
        context_layout.addWidget(self.context_label)
        context_layout.addStretch()
        context_layout.addWidget(self.case_count_label)
        root.addWidget(context)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        eyebrow = QLabel(f"TEST BUILDER · {self.module_key.upper()}")
        eyebrow.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        title = QLabel(self.title)
        title.setStyleSheet("font-size: 30px; font-weight: 700; color: #071a33;")
        subtitle = QLabel("Chọn trang PCM, chọn element cần kiểm tra, nhập Expected Result rồi Run.")
        subtitle.setStyleSheet("color: #52657a; font-size: 13px;")
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
        result_title = QLabel("Actual Result")
        result_title.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.status_label = QLabel("Sẵn sàng chạy kiểm thử")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.actual_value = QLabel("Chưa có Actual Result")
        self.actual_value.setWordWrap(True)
        self.actual_value.setStyleSheet("color: #102033; font-size: 14px; padding: 12px; background: #f8fafc; border: 1px solid #dfe5ec; border-radius: 8px;")
        self.compare_value = QLabel("Expected - Actual sẽ hiển thị sau khi Run.")
        self.compare_value.setWordWrap(True)
        self.compare_value.setStyleSheet("color: #64748b; font-size: 12px;")

        action_row = QHBoxLayout()
        action_row.addStretch()
        reset_button = QPushButton("Đặt lại")
        reset_button.setFixedHeight(38)
        reset_button.clicked.connect(self._reset_result)
        self.run_button = QPushButton("▶ Run Test")
        self.run_button.setObjectName("runButton")
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

        title = QLabel("01  Element trên trang")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        page_row = QHBoxLayout()
        page_col = QVBoxLayout()
        page_col.addWidget(QLabel("Trang PCM"))
        self.page_combo = QComboBox(panel)
        self.page_combo.currentIndexChanged.connect(self._on_page_changed)
        page_col.addWidget(self.page_combo)
        page_row.addLayout(page_col)
        layout.addLayout(page_row)

        self.url_input = QLineEdit(panel)
        self.url_input.setReadOnly(True)
        self.url_input.hide()

        row = QHBoxLayout()
        element_col = QVBoxLayout()
        element_col.addWidget(QLabel("Element"))
        self.element_combo = QComboBox()
        self.element_combo.currentIndexChanged.connect(self._on_element_changed)
        element_col.addWidget(self.element_combo)

        locator_type_col = QVBoxLayout()
        locator_type_col.addWidget(QLabel("Locator"))
        self.locator_type_combo = QComboBox()
        self.locator_type_combo.addItems(["css", "xpath", "id", "name", "class", "tag"])
        locator_type_col.addWidget(self.locator_type_combo)
        row.addLayout(element_col)
        row.addLayout(locator_type_col)
        layout.addLayout(row)

        layout.addWidget(QLabel("Locator value"))
        self.locator_input = QLineEdit()
        layout.addWidget(self.locator_input)

        hint = QLabel("✓ Có thể sửa locator nếu selector thực tế của PCM khác dữ liệu mẫu")
        hint.setStyleSheet("color: #16845b; background: #ecfdf5; padding: 9px; border-radius: 8px;")
        layout.addWidget(hint)
        return panel

    def _create_expected_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        title = QLabel("02  Expected Result")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        subtitle = QLabel("Nhập text/số liệu mong đợi của element đã chọn")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(QLabel("Expected"))
        self.expected_input = QTextEdit()
        self.expected_input.setMinimumHeight(130)
        layout.addWidget(self.expected_input)

        if self.module_key == "table":
            upload_row = QHBoxLayout()
            upload_button = QPushButton("Upload Excel/CSV")
            upload_button.setObjectName("uploadTableFileButton")
            upload_button.setFixedHeight(36)
            upload_button.clicked.connect(self._select_table_file)
            self.table_file_label = QLabel("Chưa chọn file")
            self.table_file_label.setStyleSheet("color: #64748b; font-size: 12px;")
            upload_row.addWidget(upload_button)
            upload_row.addWidget(self.table_file_label, 1)
            layout.addLayout(upload_row)

        option_row = QHBoxLayout()
        self.trim_checkbox = QCheckBox("Bỏ qua khoảng trắng")
        self.trim_checkbox.setChecked(True)
        self.case_checkbox = QCheckBox("Phân biệt hoa thường")
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

    def set_active_page_by_name(self, name: str) -> bool:
        """Chuyển combo 'Trang PCM' sang đúng trang có tên khớp `name` (nếu có).
        Dùng để đồng bộ theo thanh header 'TRANG ĐANG KIỂM THỬ' khi điều hướng
        vào màn Test Builder này. Trả về True nếu tìm thấy và đã chuyển."""
        idx = self.page_combo.findText(name)
        if idx < 0:
            return False
        if self.page_combo.currentIndex() != idx:
            self.page_combo.setCurrentIndex(idx)
        else:
            # Cùng index rồi thì vẫn phát tín hiệu để header luôn khớp,
            # phòng trường hợp header đang hiển thị tên khác do nơi khác ghi đè.
            self._on_page_changed(idx)
        return True

    def _on_page_changed(self, index):
        if index < 0 or index >= len(self.page_by_index):
            return

        page = self.page_by_index[index]
        self.context_label.setText(f"<b style='color:#2563eb'>PCM</b> &nbsp; {page.name} &nbsp; <span style='color:#64748b'>{page.path}</span>")
        self.url_input.setText(page.url)
        self.page_selected.emit(page.name, page.url)

        elements = TestContract.elements_for(page.key, self.module_key)
        if not elements and self.module_key in ("title", "ui", "menu", "image", "radio"):
            elements = TestContract.elements_for(page.key, "label")

        self.element_by_index = elements
        self.element_combo.blockSignals(True)
        self.element_combo.clear()
        for element in self.element_by_index:
            self.element_combo.addItem(element.name)
        self.element_combo.blockSignals(False)
        self.case_count_label.setText(f"{len(elements)} elements")
        self._on_element_changed(0)

    def _on_element_changed(self, index):
        if index < 0 or index >= len(self.element_by_index):
            self.locator_input.clear()
            self.expected_input.clear()
            return

        element = self.element_by_index[index]
        self.locator_type_combo.setCurrentText(element.locator_type)
        self.locator_input.setText(element.locator_value)
        self.expected_input.clear()
        self.table_file_path = ""
        if hasattr(self, "table_file_label"):
            self.table_file_label.setText("Chưa chọn file")

    def _select_table_file(self):
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Chọn file expected cho Table",
            "",
            "Table files (*.xlsx *.csv);;Excel files (*.xlsx);;CSV files (*.csv)",
        )
        if not file_path:
            return

        try:
            expected_text = load_table_file(file_path)
        except Exception as error:
            self.status_label.setText(f"Không đọc được file: {error}")
            return

        self.table_file_path = file_path
        self.expected_input.setPlainText(expected_text)
        if hasattr(self, "table_file_label"):
            self.table_file_label.setText(file_path)
        self.status_label.setText("Đã tải dữ liệu expected từ file.")

    def _run_test(self):
        if self.worker and self.worker.isRunning():
            return
        if not self.element_by_index:
            self.status_label.setText("Chưa có element cho trang kiểm thử này.")
            return

        page = self.page_by_index[self.page_combo.currentIndex()]
        element = self.element_by_index[self.element_combo.currentIndex()]
        expected_text = self.expected_input.toPlainText()

        self.run_button.setEnabled(False)
        self.progress.setValue(0)
        self.actual_value.setText("Đang chạy Selenium...")
        self.compare_value.setText("Đang lấy Actual Result từ PCM.")

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

    def _handle_result(self, payload):
        self.actual_value.setText((payload.get("actual", "") or "").replace("\t", "\n"))
        status = payload.get("status", "FAILED")
        pairs = payload.get("pairs") or []
        if pairs:
            pair_lines = [
                f"{pair['index']}. {pair['expected']} - {pair['actual']} -> {pair['status']}"
                for pair in pairs
            ]
            compare_text = "\n".join(pair_lines)
            compare_text += f"\nResult: {status} - {payload.get('message', '')}"
        else:
            compare_text = (
                f"Expected: {payload.get('expected', '')}\n"
                f"Actual: {payload.get('actual', '')}\n"
                f"Result: {status} - {payload.get('message', '')}"
            )
        self.compare_value.setText(compare_text)
        color = "#16845b" if status == "PASSED" else "#b42318"
        self.compare_value.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 700;")

    def _handle_finished(self, _finished):
        self.run_button.setEnabled(True)

    def _reset_result(self):
        self.progress.setValue(0)
        self.status_label.setText("Sẵn sàng chạy kiểm thử")
        self.actual_value.setText("Chưa có Actual Result")
        self.compare_value.setText("Expected - Actual sẽ hiển thị sau khi Run.")
        self.compare_value.setStyleSheet("color: #64748b; font-size: 12px;")
