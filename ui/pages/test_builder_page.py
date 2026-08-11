from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from services.data_store import DataStore
from services.selenium_runner import RunnerRequest, SeleniumWorker
from ui.components import Card, ResultTable, Toast
from ui.linh_styles import LINH_PAGE_STYLE


class TestBuilderPage(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self.setObjectName("LinhPage")
        self.setStyleSheet(LINH_PAGE_STYLE)

        self.store = store
        self.website_id = None
        self.page_id = None
        self.current_url = ""
        self.thread = None
        self.worker = None
        self.last_rows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 26)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("TEST BUILDER")
        title.setObjectName("LinhTitle")
        subtitle = QLabel(
            "Chọn element đã lưu → nhập Expected → Run → Selenium lấy Actual → PASS / FAIL."
        )
        subtitle.setObjectName("LinhSubtitle")
        subtitle.setWordWrap(True)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.manage_btn = QPushButton("Quản lý element")
        self.manage_btn.setObjectName("SecondaryButton")
        header.addWidget(self.manage_btn)
        root.addLayout(header)

        context = Card()
        context_row = QHBoxLayout()
        self.context_label = QLabel("Chưa chọn Website / Page")
        self.context_label.setStyleSheet("font-weight: 700; color: #0f172a;")
        self.url_label = QLabel("")
        self.url_label.setObjectName("Muted")
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        context_row.addWidget(self.context_label)
        context_row.addStretch()
        context.layout.addLayout(context_row)
        context.layout.addWidget(self.url_label)
        root.addWidget(context)

        # Main content: 01 Element và 02 Expected nằm CÙNG MỘT HÀNG.
        # Dùng scroll cho toàn bộ vùng nội dung để không bị chồng control khi cửa sổ thấp.
        content_scroll = QScrollArea()
        content_scroll.setObjectName("LinhScroll")
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_widget.setObjectName("LinhPage")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 6, 0)
        content_layout.setSpacing(12)

        # ==============================
        # HÀNG 1: ELEMENT + EXPECTED
        # ==============================
        config_row = QHBoxLayout()
        config_row.setSpacing(12)

        element_card = Card(
            "01  Element trên trang",
            "Danh sách element được tải theo Page. Tester không cần nhập lại locator.",
        )
        element_card.setMinimumWidth(430)

        name_label = QLabel("Tên kiểm tra")
        name_label.setObjectName("SmallLabel")
        self.test_name = QLineEdit()
        self.test_name.setPlaceholderText("Ví dụ: Kiểm tra nút Đăng nhập")
        element_card.layout.addWidget(name_label)
        element_card.layout.addWidget(self.test_name)

        element_label = QLabel("Element")
        element_label.setObjectName("SmallLabel")
        self.element_combo = QComboBox()
        self.element_combo.setMinimumHeight(36)
        element_card.layout.addWidget(element_label)
        element_card.layout.addWidget(self.element_combo)

        type_label = QLabel("Loại kiểm thử")
        type_label.setObjectName("SmallLabel")
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems([
            "Element tồn tại",
            "Text / Value",
            "Attribute placeholder",
            "Dropdown List",
            "Table",
        ])
        self.test_type_combo.setMinimumHeight(36)
        element_card.layout.addWidget(type_label)
        element_card.layout.addWidget(self.test_type_combo)

        locator_label = QLabel("Locator đã lưu")
        locator_label.setObjectName("SmallLabel")
        locator_row = QHBoxLayout()
        self.locator_type = QLineEdit()
        self.locator_type.setReadOnly(True)
        self.locator_type.setMaximumWidth(125)
        self.locator_value = QLineEdit()
        self.locator_value.setReadOnly(True)
        locator_row.addWidget(self.locator_type)
        locator_row.addWidget(self.locator_value, 1)
        element_card.layout.addWidget(locator_label)
        element_card.layout.addLayout(locator_row)

        action_row = QHBoxLayout()
        self.check_locator_btn = QPushButton("Kiểm tra locator")
        self.check_locator_btn.setObjectName("SecondaryButton")
        action_row.addWidget(self.check_locator_btn)
        action_row.addStretch()
        element_card.layout.addLayout(action_row)

        self.locator_status = QLabel("Locator được tải tự động theo element.")
        self.locator_status.setObjectName("Muted")
        self.locator_status.setWordWrap(True)
        element_card.layout.addWidget(self.locator_status)

        expected_card = Card("02  Expected Result", "Mỗi giá trị trên một dòng.")
        expected_card.setMinimumWidth(430)

        expected_label = QLabel("Danh sách mong đợi")
        expected_label.setObjectName("SmallLabel")
        expected_card.layout.addWidget(expected_label)

        self.expected_text = QPlainTextEdit()
        self.expected_text.setPlaceholderText("Ví dụ:\nĐăng nhập")
        self.expected_text.setMinimumHeight(190)
        expected_card.layout.addWidget(self.expected_text, 1)

        self.trim_cb = QCheckBox("Bỏ qua khoảng trắng")
        self.trim_cb.setChecked(True)
        self.case_cb = QCheckBox("Phân biệt hoa thường")
        self.order_cb = QCheckBox("Kiểm tra đúng thứ tự")
        self.order_cb.setChecked(True)
        self.browser_cb = QCheckBox("Hiện Chrome khi Run")
        self.browser_cb.setChecked(True)

        options_row_1 = QHBoxLayout()
        options_row_1.addWidget(self.trim_cb)
        options_row_1.addWidget(self.case_cb)
        options_row_1.addStretch()
        expected_card.layout.addLayout(options_row_1)

        options_row_2 = QHBoxLayout()
        options_row_2.addWidget(self.order_cb)
        options_row_2.addWidget(self.browser_cb)
        options_row_2.addStretch()
        expected_card.layout.addLayout(options_row_2)

        # Ép hai card có cùng chiều cao khi nằm cùng hàng.
        element_card.setMinimumHeight(430)
        expected_card.setMinimumHeight(430)
        config_row.addWidget(element_card, 1)
        config_row.addWidget(expected_card, 1)
        content_layout.addLayout(config_row)

        # ==============================
        # HÀNG 2: RUN & ĐỐI CHIẾU - RIÊNG MỘT HÀNG
        # ==============================
        run_card = Card("03  Run & đối chiếu")
        self.run_status = QLabel("Chưa có Actual Result. Nhấn Run Test để bắt đầu.")
        self.run_status.setObjectName("Muted")
        self.run_status.setWordWrap(True)
        run_card.layout.addWidget(self.run_status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        run_card.layout.addWidget(self.progress)

        run_actions = QHBoxLayout()
        run_actions.addStretch()
        self.reset_btn = QPushButton("Đặt lại")
        self.reset_btn.setObjectName("SecondaryButton")
        self.run_btn = QPushButton("Run Test")
        self.run_btn.setObjectName("PrimaryButton")
        run_actions.addWidget(self.reset_btn)
        run_actions.addWidget(self.run_btn)
        run_card.layout.addLayout(run_actions)
        content_layout.addWidget(run_card)

        # ==============================
        # HÀNG 3: ACTUAL RESULT - RIÊNG MỘT HÀNG, FULL WIDTH
        # ==============================
        result_host = QWidget()
        result_host.setObjectName("LinhPage")
        result_host_layout = QVBoxLayout(result_host)
        result_host_layout.setContentsMargins(0, 0, 0, 0)
        result_host_layout.setSpacing(0)

        self.empty_result_card = Card(
            "04  Actual Result",
            "Actual Result chỉ xuất hiện sau khi Selenium chạy xong. PASS = khớp, FAIL = không khớp, ERROR = Selenium/locator không chạy được.",
        )
        empty = QLabel("Chưa có Actual Result")
        empty.setObjectName("Muted")
        empty.setAlignment(Qt.AlignCenter)
        empty.setMinimumHeight(120)
        self.empty_result_card.layout.addWidget(empty)
        result_host_layout.addWidget(self.empty_result_card)

        self.result_card = Card("04  Actual Result", "Kết quả Expected – Actual và trạng thái.")
        self.result_table = ResultTable()
        self.result_table.setMinimumHeight(220)
        self.result_card.layout.addWidget(self.result_table)
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_btn = QPushButton("Xuất CSV")
        self.export_btn.setObjectName("SecondaryButton")
        export_row.addWidget(self.export_btn)
        self.result_card.layout.addLayout(export_row)
        self.result_card.hide()
        result_host_layout.addWidget(self.result_card)

        content_layout.addWidget(result_host)
        content_layout.addStretch()

        content_scroll.setWidget(content_widget)
        root.addWidget(content_scroll, 1)

        self.toast = Toast(self)

        self.element_combo.currentIndexChanged.connect(self.load_element_detail)
        self.test_type_combo.currentTextChanged.connect(self.on_test_type_changed)
        self.check_locator_btn.clicked.connect(self.check_locator)
        self.run_btn.clicked.connect(self.run_test)
        self.reset_btn.clicked.connect(self.reset_result)
        self.export_btn.clicked.connect(self.export_csv)
        self.on_test_type_changed(self.test_type_combo.currentText())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.toast.isVisible():
            self.toast.adjustSize()
            self.toast.move(
                max(12, self.width() - self.toast.width() - 24),
                max(12, self.height() - self.toast.height() - 24),
            )

    def set_context(self, website_id, page_id, website_name="", page_name="", url=""):
        changed = website_id != self.website_id or page_id != self.page_id
        self.website_id = website_id
        self.page_id = page_id
        self.current_url = url or self.store.page_url(website_id, page_id)
        self.context_label.setText(f"{website_name or website_id}  /  {page_name or page_id}")
        self.url_label.setText(self.current_url)
        self.refresh_elements()
        if changed:
            self.reset_result()

    def refresh_elements(self):
        selected = self.element_combo.currentData()
        self.store.reload()
        page = self.store.find_page(self.website_id, self.page_id)
        self.element_combo.blockSignals(True)
        self.element_combo.clear()
        if page:
            for element in page.get("elements", []):
                self.element_combo.addItem(element.get("name", ""), element.get("id"))
        if selected:
            idx = self.element_combo.findData(selected)
            if idx >= 0:
                self.element_combo.setCurrentIndex(idx)
        self.element_combo.blockSignals(False)
        self.load_element_detail()

    def current_element(self):
        return self.store.find_element(
            self.website_id,
            self.page_id,
            self.element_combo.currentData(),
        )

    def load_element_detail(self):
        element = self.current_element()
        if not element:
            self.locator_type.clear()
            self.locator_value.clear()
            return
        self.locator_type.setText(element.get("locator_type", ""))
        self.locator_value.setText(element.get("locator_value", ""))
        recommended = element.get("recommended_test", "")
        index = self.test_type_combo.findText(recommended)
        if index >= 0:
            self.test_type_combo.setCurrentIndex(index)
        self.locator_status.setText("Locator được tải tự động theo element.")
        self.locator_status.setObjectName("Muted")
        self._repolish(self.locator_status)
        self.reset_result()

    def on_test_type_changed(self, test_type):
        if test_type == "Element tồn tại":
            self.expected_text.setPlainText("Tồn tại")
            self.expected_text.setEnabled(False)
        else:
            if not self.expected_text.isEnabled():
                self.expected_text.clear()
            self.expected_text.setEnabled(True)

    def expected_lines(self):
        return [line for line in self.expected_text.toPlainText().splitlines() if line.strip()]

    def build_request(self, mode="run"):
        return RunnerRequest(
            url=self.current_url,
            locator_type=self.locator_type.text().strip(),
            locator_value=self.locator_value.text().strip(),
            test_type=self.test_type_combo.currentText(),
            expected_lines=self.expected_lines(),
            trim_whitespace=self.trim_cb.isChecked(),
            case_sensitive=self.case_cb.isChecked(),
            check_order=self.order_cb.isChecked(),
            timeout=10,
            show_browser=self.browser_cb.isChecked() if mode == "run" else False,
        )

    def set_loading(self, loading, message):
        self.run_btn.setEnabled(not loading)
        self.check_locator_btn.setEnabled(not loading)
        self.element_combo.setEnabled(not loading)
        self.test_type_combo.setEnabled(not loading)
        self.progress.setVisible(loading)
        self.run_status.setText(message)

    def start_worker(self, mode):
        request = self.build_request(mode)
        if not request.url or not request.locator_value:
            self.toast.show_message("Page hoặc locator chưa được cấu hình.", "ERROR")
            return
        if mode == "run" and request.test_type != "Element tồn tại" and not request.expected_lines:
            self.toast.show_message("Vui lòng nhập Expected Result trước khi Run.", "ERROR")
            return

        if mode == "run":
            self.result_card.hide()
            self.empty_result_card.show()

        self.set_loading(True, "Đang gọi Selenium...")
        self.thread = QThread(self)
        self.worker = SeleniumWorker(request, mode=mode)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.run_status.setText)
        if mode == "run":
            self.worker.finished.connect(self.on_run_finished)
        else:
            self.worker.finished.connect(self.on_check_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def run_test(self):
        self.start_worker("run")

    def check_locator(self):
        self.start_worker("check")

    def on_run_finished(self, status, rows, message):
        self.set_loading(False, message)
        self.last_rows = rows
        object_name = {
            "PASS": "StatusPass",
            "FAIL": "StatusFail",
            "ERROR": "StatusError",
        }.get(status, "Muted")
        self.run_status.setObjectName(object_name)
        self._repolish(self.run_status)

        if status == "ERROR":
            # ERROR là lỗi runner, không giả thành FAIL test case.
            self.result_table.setRowCount(0)
            self.result_card.hide()
            self.empty_result_card.show()
            self.toast.show_message(message, "ERROR", 4500)
            return

        self.result_table.set_results(rows)
        self.empty_result_card.hide()
        self.result_card.show()
        self.toast.show_message(message, status)

    def on_check_finished(self, status, _rows, message):
        self.set_loading(False, message)
        object_name = {
            "PASS": "StatusPass",
            "FAIL": "StatusFail",
            "ERROR": "StatusError",
        }.get(status, "Muted")
        self.locator_status.setText(("✓ " if status == "PASS" else "✕ ") + message)
        self.locator_status.setObjectName(object_name)
        self._repolish(self.locator_status)
        self.toast.show_message(message, status if status in {"PASS", "FAIL", "ERROR"} else "INFO")

    def reset_result(self):
        self.last_rows = []
        self.result_table.setRowCount(0)
        self.result_card.hide()
        self.empty_result_card.show()
        self.run_status.setText("Chưa có Actual Result. Nhấn Run Test để bắt đầu.")
        self.run_status.setObjectName("Muted")
        self.locator_status.setText("Locator được tải tự động theo element.")
        self.locator_status.setObjectName("Muted")
        self._repolish(self.run_status)
        self._repolish(self.locator_status)

    def export_csv(self):
        if self.result_table.rowCount() == 0:
            self.toast.show_message("Chưa có kết quả để xuất.", "ERROR")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất kết quả CSV",
            "autotest_result.csv",
            "CSV (*.csv)",
        )
        if not path:
            return
        self.result_table.export_csv(path)
        self.toast.show_message("Đã xuất CSV.", "PASS")

    @staticmethod
    def _repolish(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
