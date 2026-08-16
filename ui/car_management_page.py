from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QProgressBar,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt

from core.helpers.worker import SeleniumWorker
from runners.car_management_runner import run_car_management_test


class CarManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        # Layout chính của trang (sắp xếp từ trên xuống dưới)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Tiêu đề trang
        title = QLabel("Quản lý xe - Cấu hình & Kiểm thử")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Tự kiểm thử Dropdown phụ thuộc Hãng-Mẫu, Search/Table, và CRUD xe "
            "trực tiếp trên courses.plt.pro.vn/cars. Dữ liệu test dùng biển số "
            "sinh ngẫu nhiên và được dọn dẹp sau khi chạy (nếu bật 'Dọn dẹp')."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6c757d; margin-bottom: 6px;")
        layout.addWidget(subtitle)

        # 2. Khu vực nút bấm chạy kịch bản + tuỳ chọn
        btn_layout = QHBoxLayout()
        self.run_test_btn = QPushButton("▶ Chạy kịch bản Kiểm thử Quản lý xe")
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
        btn_layout.addWidget(self.run_test_btn)

        self.cleanup_check = QCheckBox("Dọn dẹp dữ liệu test sau khi chạy")
        self.cleanup_check.setChecked(True)
        btn_layout.addWidget(self.cleanup_check)

        self.show_browser_check = QCheckBox("Hiện trình duyệt")
        self.show_browser_check.setChecked(True)
        btn_layout.addWidget(self.show_browser_check)

        btn_layout.addStretch()  # Đẩy các control về bên trái
        layout.addLayout(btn_layout)

        # 3. Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # 4. Bảng kết quả từng bước (Expected / Actual / Result)
        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(["Kỳ vọng (Expected)", "Thực tế (Actual)", "Kết quả"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setMaximumHeight(220)
        layout.addWidget(self.result_table)

        # 5. Khung hiển thị log/kết quả chạy test
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText(
            "Sẵn sàng...\n"
            "- Nhấn nút bên trên để chạy self-test: Dropdown phụ thuộc, Search/Table, "
            "CRUD (Tạo/Sửa/Xoá), chặn trùng biển số, bắt lỗi thiếu dữ liệu bắt buộc.\n"
            "- Log chi tiết từng bước sẽ hiển thị tại đây; kết quả PASS/FAIL ở bảng trên."
        )
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

    # ------------------------------------------------------------------
    def _run_test(self):
        if self.worker and self.worker.isRunning():
            return

        self.result_table.setRowCount(0)
        self.log_console.clear()
        self.progress.setValue(0)
        self._append_log("Bắt đầu self-test module Quản lý xe...")
        self._set_busy(True)

        self.worker = SeleniumWorker(
            run_car_management_test,
            cleanup=self.cleanup_check.isChecked(),
            show_browser=self.show_browser_check.isChecked(),
        )
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.log_signal.connect(self._append_log)
        self.worker.result_signal.connect(self._on_result)
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _append_log(self, text: str):
        self.log_console.append(text)

    def _on_result(self, result: dict):
        for step in result.get("steps", []):
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            values = [step.get("expected", ""), step.get("actual", ""), step.get("result", "")]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 2 and value == "PASS":
                    item.setForeground(Qt.darkGreen)
                elif col == 2 and value == "FAIL":
                    item.setForeground(Qt.red)
                self.result_table.setItem(row, col, item)

        status = result.get("status", "UNKNOWN")
        message = result.get("message") or result.get("error") or ""
        prefix = "✅" if status == "PASSED" else "❌"
        self._append_log(f"\n{prefix} [{status}] {message}")

    def _set_busy(self, busy: bool):
        self.run_test_btn.setDisabled(busy)
        self.run_test_btn.setText("⏳ Đang chạy..." if busy else "▶ Chạy kịch bản Kiểm thử Quản lý xe")
