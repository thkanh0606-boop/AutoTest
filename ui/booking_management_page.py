"""PySide6 UI cho module Quản lý đặt xe (Booking Management)"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.helpers.worker import SeleniumWorker
from runners.booking_runner import (
    run_booking_crud_test,
    run_booking_locator_test,
)

PAGE_STYLE = """
QWidget#BookingManagementPage { background-color: #f4f7fb; }
QLabel { background: transparent; color: #102033; }
QFrame#Card { background: #ffffff; border: 1px solid #dfe5ec; border-radius: 12px; }
QLineEdit, QComboBox {
    background: #ffffff; border: 1px solid #cfd8e3; border-radius: 8px;
    padding: 7px 10px; color: #102033; font-size: 13px;
}
QPushButton { border-radius: 8px; padding: 8px 14px; font-weight: 700; }
QPushButton#Primary { background: #2563eb; color: #ffffff; border: none; }
QPushButton#Secondary { background: #f8fbff; color: #12365f; border: 1px solid #b9cbe0; }
QTableWidget { background: #ffffff; border: 1px solid #dfe5ec; gridline-color: #e8edf3; }
QHeaderView::section { background: #eef3f8; color: #23364d; font-weight: 700; padding: 7px; border: none; }
"""


class BookingManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BookingManagementPage")
        self.setStyleSheet(PAGE_STYLE)
        self.worker = None
        self._build_ui()

    def _card(self, title: str, subtitle: str = ""):
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title_label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setStyleSheet("color: #64748b; font-size: 12px;")
            layout.addWidget(sub)
        return frame, layout

    def _build_ui(self):
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        shell.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: #f4f7fb;")
        scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(32, 26, 32, 32)
        root.setSpacing(16)

        # Breadcrumb + Title
        eyebrow = QLabel("AUTOTEST · MODULE BOOKING")
        eyebrow.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        title = QLabel("QUẢN LÝ ĐẶT XE")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #071a33;")
        desc = QLabel(
            "Phần kiểm thử module Quản lý đặt xe của PLT Fleet Console. "
            "Booking / CRUD / Form / Table / Dropdown / Validation."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        root.addWidget(eyebrow)
        root.addWidget(title)
        root.addWidget(desc)

        # Card: Phạm vi kiểm thử
        scope_card, scope_layout = self._card(
            "Phạm vi kiểm thử",
            "Fleet Console - trang Quản lý đặt xe sau đăng nhập."
        )
        url_input = QLineEdit("https://courses.plt.pro.vn/bookings")
        url_input.setReadOnly(True)
        scope_layout.addWidget(url_input)
        root.addWidget(scope_card)

        # Card: Booking Form — Element / Locator
        form_card, form_layout = self._card(
            "Booking Form — Element / Locator",
            "Chọn một locator rồi bấm Kiểm tra; AutoTest sẽ mở trang và kiểm tra element tương ứng."
        )
        self.form_table = QTableWidget(0, 4)
        self.form_table.setHorizontalHeaderLabels(["Element", "Type", "Locator", "Status"])
        header = self.form_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.form_table.verticalHeader().setVisible(False)
        self.form_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.form_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.form_table.setMinimumHeight(200)
        form_layout.addWidget(self.form_table)

        self.form_status = QLabel("Chưa kiểm tra.")
        self.form_status.setStyleSheet("color: #64748b; font-size: 12px;")
        form_layout.addWidget(self.form_status)

        form_btn = QPushButton("Kiểm tra locator đã chọn")
        form_btn.setObjectName("Secondary")
        form_btn.clicked.connect(lambda: self._check_locator("form"))
        form_layout.addWidget(form_btn)
        self.form_check_btn = form_btn

        root.addWidget(form_card)

        # Card: Booking Table — Element / Locator
        table_card, table_layout = self._card(
            "Booking Table — Element / Locator",
            "Các element trên bảng danh sách booking."
        )
        self.table_locator_table = QTableWidget(0, 4)
        self.table_locator_table.setHorizontalHeaderLabels(["Element", "Type", "Locator", "Status"])
        header = self.table_locator_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_locator_table.verticalHeader().setVisible(False)
        self.table_locator_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_locator_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table_locator_table.setMinimumHeight(180)
        table_layout.addWidget(self.table_locator_table)

        self.table_locator_status = QLabel("Chưa kiểm tra.")
        self.table_locator_status.setStyleSheet("color: #64748b; font-size: 12px;")
        table_layout.addWidget(self.table_locator_status)

        table_btn = QPushButton("Kiểm tra locator đã chọn")
        table_btn.setObjectName("Secondary")
        table_btn.clicked.connect(lambda: self._check_locator("table"))
        table_layout.addWidget(table_btn)
        self.table_check_btn = table_btn

        root.addWidget(table_card)

        # Card: Dropdown / Filter — Element / Locator
        dropdown_card, dropdown_layout = self._card(
            "Dropdown / Filter — Element / Locator",
            "Các dropdown và filter trên trang booking."
        )
        self.dropdown_table = QTableWidget(0, 4)
        self.dropdown_table.setHorizontalHeaderLabels(["Element", "Type", "Locator", "Status"])
        header = self.dropdown_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.dropdown_table.verticalHeader().setVisible(False)
        self.dropdown_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dropdown_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.dropdown_table.setMinimumHeight(150)
        dropdown_layout.addWidget(self.dropdown_table)

        self.dropdown_status = QLabel("Chưa kiểm tra.")
        self.dropdown_status.setStyleSheet("color: #64748b; font-size: 12px;")
        dropdown_layout.addWidget(self.dropdown_status)

        dropdown_btn = QPushButton("Kiểm tra locator đã chọn")
        dropdown_btn.setObjectName("Secondary")
        dropdown_btn.clicked.connect(lambda: self._check_locator("dropdown"))
        dropdown_layout.addWidget(dropdown_btn)
        self.dropdown_check_btn = dropdown_btn

        root.addWidget(dropdown_card)

        # Card: Kiểm tra CRUD
        crud_card, crud_layout = self._card(
            "Kiểm tra CRUD",
            "AutoTest sử dụng Chrome/Selenium để thực hiện kiểm thử trực tiếp trên trang Quản lý đặt xe."
        )
        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.addWidget(QLabel("Nhóm kiểm tra"), 0, 0)
        form.addWidget(QLabel("Tên test data"), 0, 1)
        form.addWidget(QLabel("Loại test"), 0, 2)

        self.test_group_combo = QComboBox()
        self.test_group_combo.addItem("Booking CRUD", "crud")
        self.test_group_combo.addItem("Booking Form", "form")
        self.test_group_combo.addItem("Booking Table", "table")
        self.test_group_combo.addItem("Booking Dropdown", "dropdown")

        self.test_name_input = QLineEdit("SELENIUM_TEST_BOOKING")

        self.test_type_combo = QComboBox()
        self.test_type_combo.addItem("Toàn bộ", "all")
        self.test_type_combo.addItem("CREATE", "create")
        self.test_type_combo.addItem("UPDATE", "update")
        self.test_type_combo.addItem("DELETE", "delete")

        form.addWidget(self.test_group_combo, 1, 0)
        form.addWidget(self.test_name_input, 1, 1)
        form.addWidget(self.test_type_combo, 1, 2)
        crud_layout.addLayout(form)

        options = QHBoxLayout()
        self.cleanup_check = QCheckBox("Dọn dữ liệu test sau khi chạy (best-effort)")
        self.cleanup_check.setChecked(True)
        self.show_browser_check = QCheckBox("Hiện Chrome khi chạy")
        self.show_browser_check.setChecked(True)
        self.run_btn = QPushButton("Chạy kiểm tra CRUD")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._run_crud)
        options.addWidget(self.cleanup_check)
        options.addWidget(self.show_browser_check)
        options.addStretch()
        options.addWidget(self.run_btn)
        crud_layout.addLayout(options)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        crud_layout.addWidget(self.progress)

        self.crud_status = QLabel("Sẵn sàng chạy kiểm thử Booking.")
        self.crud_status.setWordWrap(True)
        self.crud_status.setStyleSheet("color: #64748b; font-size: 12px;")
        crud_layout.addWidget(self.crud_status)
        root.addWidget(crud_card)

        # Card: Kết quả kiểm thử
        result_card, result_layout = self._card(
            "Kết quả kiểm thử",
            "Chi tiết kết quả từng bước."
        )
        stats = QHBoxLayout()
        self.total_label = QLabel("TOTAL: 0")
        self.pass_label = QLabel("PASS: 0")
        self.fail_label = QLabel("FAIL: 0")
        for lbl in (self.total_label, self.pass_label, self.fail_label):
            lbl.setStyleSheet("font-weight: 700; font-size: 14px; margin-right: 16px;")
        stats.addWidget(self.total_label)
        stats.addWidget(self.pass_label)
        stats.addWidget(self.fail_label)
        stats.addStretch()
        result_layout.addLayout(stats)

        self.result_table = QTableWidget(0, 5)
        self.result_table.setHorizontalHeaderLabels(["STT", "Test Case", "Expected", "Actual", "Kết quả"])
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.setMinimumHeight(200)
        result_layout.addWidget(self.result_table)

        self.result_status = QLabel("Chưa có kết quả kiểm thử.")
        self.result_status.setStyleSheet("color: #64748b; font-size: 12px;")
        result_layout.addWidget(self.result_status)
        root.addWidget(result_card)

        root.addStretch()

        # Load locator tables
        self._load_locator_tables()

    def _load_locator_tables(self):
        # Form locators - cập nhật nút "Tạo đơn thuê"
        form_data = [
            ("Nút Tạo đơn thuê", "XPATH", "//button[@aria-label='Tạo đơn thuê']"),
            ("Dropdown xe", "ID", "carId"),
            ("Dropdown khách hàng", "ID", "customerId"),
            ("Tên người thuê", "ID", "customerName"),
            ("Số điện thoại", "ID", "customerPhoneNumber"),
            ("Email", "ID", "customerEmail"),
            ("Ngày bắt đầu", "ID", "startDate"),
            ("Ngày kết thúc", "CSS", "input[id='endDate']"),
            ("Điểm nhận xe", "ID", "pickupLocation"),
            ("Điểm trả xe", "ID", "returnLocation"),
            ("Trạng thái", "ID", "status"),
            ("Tiền thuê", "ID", "rentalAmount"),
            ("Ghi chú", "ID", "note"),
            ("Nút Lưu", "XPATH", "//button[@type='submit' and (.//span[contains(normalize-space(.),'Lưu')] or .//span[contains(normalize-space(.),'Tạo đơn thuê')] or .//span[contains(normalize-space(.),'Cập nhật')])]"),
        ]
        self._fill_locator_table(self.form_table, form_data)

        # Table locators
        table_data = [
            ("Bảng danh sách booking", "CSS", "table"),
            ("Nút Sửa (hàng)", "XPATH", "//button[@aria-label='Sửa']"),
            ("Nút Xóa (hàng)", "XPATH", "//button[@aria-label='Xóa']"),
            ("Nút Xem chi tiết (hàng)", "XPATH", "//button[@aria-label='Xem chi tiết']"),
            ("Ô tìm kiếm", "ID", "search"),
            ("Filter trạng thái", "ID", "statusFilter"),
        ]
        self._fill_locator_table(self.table_locator_table, table_data)

        # Dropdown / Filter locators
        dropdown_data = [
            ("Bộ lọc xe", "ID", "carFilter"),
            ("Bộ lọc khách hàng", "ID", "customerFilter"),
            ("Bộ lọc trạng thái", "ID", "statusFilter"),
            ("Bộ lọc thanh toán", "ID", "paymentStatusFilter"),
        ]
        self._fill_locator_table(self.dropdown_table, dropdown_data)

    def _fill_locator_table(self, table: QTableWidget, data: list):
        table.setRowCount(0)
        for label, locator_type, value in data:
            row = table.rowCount()
            table.insertRow(row)
            for col, item_value in enumerate([label, locator_type, value, "Chưa kiểm tra"]):
                item = QTableWidgetItem(item_value)
                if col != 2:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col, item)

    def _check_locator(self, scope: str):
        if self.worker and self.worker.isRunning():
            return

        if scope == "form":
            table = self.form_table
            status_label = self.form_status
        elif scope == "table":
            table = self.table_locator_table
            status_label = self.table_locator_status
        else:
            table = self.dropdown_table
            status_label = self.dropdown_status

        row = table.currentRow()
        if row < 0:
            row = 0
            table.selectRow(row)

        locator_type = table.item(row, 1).text()
        locator_value = table.item(row, 2).text()

        status_label.setText("Đang chạy Selenium...")
        self._set_busy(True)
        self.worker = SeleniumWorker(
            run_booking_locator_test,
            locator_type=locator_type,
            locator_value=locator_value,
            show_browser=self.show_browser_check.isChecked(),
        )
        self.worker.result_signal.connect(
            lambda result, t=table, r=row, s=status_label: self._locator_done(t, r, s, result)
        )
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _locator_done(self, table, row, status_label, result):
        passed = result.get("status") == "PASSED"
        table.item(row, 3).setText("PASS" if passed else "FAIL")
        status_label.setText(result.get("message", "Đã hoàn tất."))

    def _run_crud(self):
        if self.worker and self.worker.isRunning():
            return

        test_name = self.test_name_input.text().strip()
        if not test_name:
            self.crud_status.setText("Vui lòng nhập tên test data.")
            return

        self.result_table.setRowCount(0)
        self.result_status.setText("Đang chạy kiểm thử...")
        self.progress.setValue(5)
        self._set_busy(True)

        self.worker = SeleniumWorker(
            run_booking_crud_test,
            test_name=test_name,
            cleanup=self.cleanup_check.isChecked(),
            show_browser=self.show_browser_check.isChecked(),
            test_group=self.test_group_combo.currentData(),
            test_type=self.test_type_combo.currentData(),
        )
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.log_signal.connect(self.crud_status.setText)
        self.worker.result_signal.connect(self._crud_done)
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _crud_done(self, result: dict):
        self.result_table.setRowCount(0)
        steps = result.get("steps", [])
        total = len(steps)
        passed = 0
        failed = 0
        for idx, step in enumerate(steps, start=1):
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            status = step.get("result", "FAIL")
            if status == "PASS":
                passed += 1
            else:
                failed += 1
            values = [str(idx), step.get("test_case", ""), step.get("expected", ""), step.get("actual", ""), status]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                if col == 4:
                    if val == "PASS":
                        item.setForeground(Qt.darkGreen)
                    else:
                        item.setForeground(Qt.red)
                self.result_table.setItem(row, col, item)

        self.total_label.setText(f"TOTAL: {total}")
        self.pass_label.setText(f"PASS: {passed}")
        self.fail_label.setText(f"FAIL: {failed}")
        self.progress.setValue(100)
        self.result_status.setText(result.get("message", "Đã hoàn tất."))

    def _set_busy(self, busy: bool):
        self.run_btn.setDisabled(busy)
        self.form_check_btn.setDisabled(busy)
        self.table_check_btn.setDisabled(busy)
        self.dropdown_check_btn.setDisabled(busy)