from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.helpers.worker import SeleniumWorker
from runners.staff_management_runner import run_staff_management_test


class StaffManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Nhân sự - Cấu hình & Kiểm thử")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Chạy bộ test Selenium cho trang /users: tải danh sách, bảng dữ liệu, "
            "phân trang, nút thêm nhân sự, form tạo mới, validate và quay lại."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6c757d;")
        layout.addWidget(subtitle)

        action_row = QHBoxLayout()
        self.run_test_btn = QPushButton("▶ Chạy kịch bản Kiểm thử Nhân sự")
        self.run_test_btn.setCursor(Qt.PointingHandCursor)
        self.run_test_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:disabled { background-color: #93b8f5; }
            """
        )
        self.run_test_btn.clicked.connect(self._run_test)
        action_row.addWidget(self.run_test_btn)

        self.show_browser_check = QCheckBox("Hiện trình duyệt")
        self.show_browser_check.setChecked(True)
        self.show_browser_check.setEnabled(False)
        action_row.addWidget(self.show_browser_check)
        action_row.addStretch()
        layout.addLayout(action_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.result_table = QTableWidget(0, 4)
        self.result_table.setHorizontalHeaderLabels(["#", "Test case", "Kỳ vọng", "Kết quả"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setMaximumHeight(240)
        layout.addWidget(self.result_table)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText("Log chạy test Nhân sự sẽ hiển thị tại đây.")
        self.log_console.setStyleSheet(
            """
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            font-family: Consolas, monospace;
            """
        )
        layout.addWidget(self.log_console)
        self._load_test_cases()

    def _load_test_cases(self):
        cases = [
            "Tải trang danh sách Nhân sự",
            "Bảng Nhân sự có dữ liệu",
            "Có phân trang Ant Design",
            "Nút Thêm nhân sự hiển thị",
            "Mở form tạo mới Nhân sự",
            "Validate khi submit rỗng",
            "Điền form tạo mới hợp lệ",
            "Quay lại danh sách",
        ]
        self.result_table.setRowCount(0)
        for index, case in enumerate(cases, start=1):
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            values = [str(index), case, "PASS khi UI đúng contract", "Chưa chạy"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 3:
                    item.setForeground(Qt.darkGray)
                self.result_table.setItem(row, col, item)

    def _run_test(self):
        if self.worker and self.worker.isRunning():
            return

        self.progress.setValue(5)
        self.log_console.clear()
        self._set_busy(True)
        self.worker = SeleniumWorker(run_staff_management_test)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.log_signal.connect(self._append_log)
        self.worker.result_signal.connect(self._on_result)
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _append_log(self, text: str):
        self.log_console.append(text)

    def _on_result(self, result: dict):
        passed = result.get("status") == "PASSED"
        for row in range(self.result_table.rowCount()):
            item = self.result_table.item(row, 3)
            item.setText("PASS" if passed else "FAIL")
            item.setForeground(Qt.darkGreen if passed else Qt.red)

        message = result.get("message", "Đã hoàn tất.")
        output = result.get("output", "")
        self._append_log(f"\n[{result.get('status', 'UNKNOWN')}] {message}")
        if output:
            self._append_log(output[-4000:])

    def _set_busy(self, busy: bool):
        self.run_test_btn.setDisabled(busy)
        self.run_test_btn.setText(
            "⏳ Đang chạy..." if busy else "▶ Chạy kịch bản Kiểm thử Nhân sự"
        )
