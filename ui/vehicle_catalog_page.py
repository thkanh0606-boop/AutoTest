"""PySide6 UI cho phần việc Linh - Danh mục xe.

Chỉ chứa module Hãng xe / Mẫu xe, không mang theo Element Management hay
Test Builder cá nhân từ các ngày trước.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
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
from pages.category_page import CategoryPage
from runners.vehicle_catalog_runner import (
    run_catalog_crud_test,
    run_catalog_locator_test,
)
from services.catalog_import import CatalogImportError, import_catalog_file


PAGE_STYLE = """
QWidget#VehicleCatalogPage { background-color: #f4f7fb; }
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


class VehicleCatalogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VehicleCatalogPage")
        self.setStyleSheet(PAGE_STYLE)
        self.worker = None
        self.import_rows: list[dict] = []
        self._build_ui()
        self._load_locator_tables()

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

        eyebrow = QLabel("LINH · MODULE OWNER")
        eyebrow.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        title = QLabel("DANH MỤC XE")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #071a33;")
        desc = QLabel(
            "Phần việc của Linh: Hãng xe / Mẫu xe · locator · modal · dropdown · CRUD · import CSV/JSON/XLSX."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        root.addWidget(eyebrow)
        root.addWidget(title)
        root.addWidget(desc)

        url_card, url_layout = self._card("Phạm vi kiểm thử", "Fleet Console - trang Danh mục xe sau đăng nhập.")
        url = QLineEdit(CategoryPage.URL)
        url.setReadOnly(True)
        url_layout.addWidget(url)
        root.addWidget(url_card)

        locator_grid = QGridLayout()
        locator_grid.setHorizontalSpacing(14)
        locator_grid.addWidget(self._build_locator_card("brand"), 0, 0)
        locator_grid.addWidget(self._build_locator_card("model"), 0, 1)
        root.addLayout(locator_grid)

        import_card, import_layout = self._card(
            "Bộ dữ liệu kiểm thử (Import CSV / JSON / XLSX)",
            "File được dùng làm test data cho Hãng/Mẫu xe; double-click một dòng để nạp xuống form CRUD.",
        )
        import_actions = QHBoxLayout()
        self.import_path = QLineEdit()
        self.import_path.setReadOnly(True)
        self.import_path.setPlaceholderText("Chưa chọn file")
        import_btn = QPushButton("Import file")
        import_btn.setObjectName("Secondary")
        import_btn.clicked.connect(self._import_file)
        sample_btn = QPushButton("Mở file mẫu")
        sample_btn.setObjectName("Secondary")
        sample_btn.clicked.connect(self._load_sample)
        import_actions.addWidget(self.import_path, 1)
        import_actions.addWidget(import_btn)
        import_actions.addWidget(sample_btn)
        import_layout.addLayout(import_actions)

        self.import_status = QLabel("Sẵn sàng.")
        self.import_status.setStyleSheet("color: #64748b; font-size: 12px;")
        import_layout.addWidget(self.import_status)

        self.import_table = QTableWidget(0, 4)
        self.import_table.setHorizontalHeaderLabels(["Loại", "Tên", "Hãng liên kết", "Trạng thái"])
        self.import_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.import_table.verticalHeader().setVisible(False)
        self.import_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.import_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.import_table.cellDoubleClicked.connect(self._use_import_row)
        self.import_table.setMinimumHeight(150)
        import_layout.addWidget(self.import_table)
        root.addWidget(import_card)

        crud_card, crud_layout = self._card(
            "Kiểm tra CRUD & Dropdown phụ thuộc",
            "AutoTest dùng Chrome session, tự đăng nhập nếu cần, mở Danh mục xe rồi chạy luồng Hãng/Mẫu.",
        )
        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.addWidget(QLabel("Nhóm kiểm tra"), 0, 0)
        form.addWidget(QLabel("Tên test data"), 0, 1)
        form.addWidget(QLabel("Hãng liên kết (chỉ Mẫu xe)"), 0, 2)

        self.kind_combo = QComboBox()
        self.kind_combo.addItem("Hãng xe", "brand")
        self.kind_combo.addItem("Mẫu xe", "model")
        self.kind_combo.currentIndexChanged.connect(self._kind_changed)
        self.name_input = QLineEdit("LINH_AUTO_BRAND")
        self.brand_input = QLineEdit("VinFast")
        self.brand_input.setEnabled(False)
        form.addWidget(self.kind_combo, 1, 0)
        form.addWidget(self.name_input, 1, 1)
        form.addWidget(self.brand_input, 1, 2)
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

        self.crud_status = QLabel("Sẵn sàng chạy kiểm thử Danh mục xe.")
        self.crud_status.setWordWrap(True)
        self.crud_status.setStyleSheet("color: #64748b; font-size: 12px;")
        crud_layout.addWidget(self.crud_status)

        self.result_table = QTableWidget(0, 4)
        self.result_table.setHorizontalHeaderLabels(["STT", "Expected", "Actual", "Kết quả"])
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.setMinimumHeight(190)
        crud_layout.addWidget(self.result_table)
        root.addWidget(crud_card)
        root.addStretch()

    def _build_locator_card(self, group: str):
        is_brand = group == "brand"
        title = "Hãng xe — Element / Locator" if is_brand else "Mẫu xe — Element / Locator"
        card, layout = self._card(title, "Chọn một locator rồi bấm Kiểm tra; modal sẽ được mở tự động khi cần.")

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Element", "Type", "Locator", "Status"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setMinimumHeight(190)
        layout.addWidget(table)

        status = QLabel("Chưa kiểm tra.")
        status.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(status)

        button = QPushButton("Kiểm tra locator đã chọn")
        button.setObjectName("Secondary")
        button.clicked.connect(lambda _=False, g=group: self._check_locator(g))
        layout.addWidget(button)

        if is_brand:
            self.brand_locator_table = table
            self.brand_locator_status = status
            self.brand_locator_btn = button
        else:
            self.model_locator_table = table
            self.model_locator_status = status
            self.model_locator_btn = button
        return card

    def _load_locator_tables(self):
        self._fill_locator_table(self.brand_locator_table, CategoryPage.BRAND_LOCATORS)
        self._fill_locator_table(self.model_locator_table, CategoryPage.MODEL_LOCATORS)

    @staticmethod
    def _scope_for(label: str) -> str:
        if "modal" not in label.lower():
            return "page"
        return "model_modal" if "mẫu" in label.lower() or "hãng (modal)" in label.lower() else "brand_modal"

    def _fill_locator_table(self, table: QTableWidget, data: dict):
        table.setRowCount(0)
        for label, (locator_type, value) in data.items():
            row = table.rowCount()
            table.insertRow(row)
            for col, item_value in enumerate([label, locator_type, value, "Chưa kiểm tra"]):
                item = QTableWidgetItem(item_value)
                if col == 0:
                    item.setData(Qt.UserRole, self._scope_for(label))
                if col != 2:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col, item)

    def _check_locator(self, group: str):
        if self.worker and self.worker.isRunning():
            return
        table = self.brand_locator_table if group == "brand" else self.model_locator_table
        status_label = self.brand_locator_status if group == "brand" else self.model_locator_status
        row = table.currentRow()
        if row < 0:
            row = 0
            table.selectRow(row)
        locator_type = table.item(row, 1).text()
        locator_value = table.item(row, 2).text()
        scope = table.item(row, 0).data(Qt.UserRole) or "page"

        status_label.setText("Đang chạy Selenium...")
        self._set_busy(True)
        self.worker = SeleniumWorker(
            run_catalog_locator_test,
            locator_type=locator_type,
            locator_value=locator_value,
            scope=scope,
            show_browser=self.show_browser_check.isChecked(),
        )
        self.worker.result_signal.connect(
            lambda result, t=table, r=row, s=status_label: self._locator_done(t, r, s, result)
        )
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _locator_done(self, table, row, status_label, result):
        passed = result.get("status") == "PASSED"
        table.item(row, 3).setText("PASS" if passed else "ERROR")
        status_label.setText(result.get("message", "Đã hoàn tất."))

    def _import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn dữ liệu Danh mục xe",
            "",
            "Danh mục xe (*.csv *.json *.xlsx)",
        )
        if path:
            self._load_import(path)

    def _load_sample(self):
        sample = Path(__file__).resolve().parents[1] / "data" / "sample_import" / "danh_muc_xe_mau.csv"
        self._load_import(str(sample))

    def _load_import(self, path: str):
        try:
            rows, warnings = import_catalog_file(path)
        except CatalogImportError as exc:
            self.import_status.setText(str(exc))
            return
        self.import_rows = rows
        self.import_path.setText(path)
        self.import_table.setRowCount(0)
        for data in rows:
            row = self.import_table.rowCount()
            self.import_table.insertRow(row)
            values = [
                "Hãng xe" if data["loai"] == "hang" else "Mẫu xe",
                data["ten"],
                data["hang"],
                data["trang_thai"],
            ]
            for col, value in enumerate(values):
                self.import_table.setItem(row, col, QTableWidgetItem(str(value)))
        suffix = f" · {len(warnings)} cảnh báo" if warnings else ""
        self.import_status.setText(f"Đã import {len(rows)} dòng{suffix}. Double-click để dùng làm test data.")

    def _use_import_row(self, row: int, _column: int):
        if row >= len(self.import_rows):
            return
        data = self.import_rows[row]
        self.kind_combo.setCurrentIndex(0 if data["loai"] == "hang" else 1)
        self.name_input.setText(data["ten"])
        if data["hang"]:
            self.brand_input.setText(data["hang"])

    def _kind_changed(self):
        is_model = self.kind_combo.currentData() == "model"
        self.brand_input.setEnabled(is_model)
        if is_model and self.name_input.text().startswith("LINH_AUTO_BRAND"):
            self.name_input.setText("LINH_AUTO_MODEL")
        elif not is_model and self.name_input.text().startswith("LINH_AUTO_MODEL"):
            self.name_input.setText("LINH_AUTO_BRAND")

    def _run_crud(self):
        if self.worker and self.worker.isRunning():
            return
        name = self.name_input.text().strip()
        brand = self.brand_input.text().strip()
        if not name:
            self.crud_status.setText("Hãy nhập tên test data.")
            return
        if self.kind_combo.currentData() == "model" and not brand:
            self.crud_status.setText("Mẫu xe cần có Hãng liên kết.")
            return

        self.result_table.setRowCount(0)
        self.progress.setValue(5)
        self.crud_status.setText("Đang chạy kiểm thử...")
        self._set_busy(True)
        self.worker = SeleniumWorker(
            run_catalog_crud_test,
            kind=self.kind_combo.currentData(),
            name=name,
            brand=brand,
            cleanup=self.cleanup_check.isChecked(),
            show_browser=self.show_browser_check.isChecked(),
        )
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.log_signal.connect(self.crud_status.setText)
        self.worker.result_signal.connect(self._crud_done)
        self.worker.finished_signal.connect(lambda _: self._set_busy(False))
        self.worker.start()

    def _crud_done(self, result: dict):
        self.result_table.setRowCount(0)
        for index, step in enumerate(result.get("steps", []), start=1):
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            values = [str(index), step.get("expected", ""), step.get("actual", ""), step.get("result", "")]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 3 and value == "PASS":
                    item.setForeground(Qt.darkGreen)
                elif col == 3 and value == "FAIL":
                    item.setForeground(Qt.red)
                self.result_table.setItem(row, col, item)
        self.progress.setValue(100)
        self.crud_status.setText(result.get("message") or result.get("error") or "Đã hoàn tất.")

    def _set_busy(self, busy: bool):
        self.run_btn.setDisabled(busy)
        self.brand_locator_btn.setDisabled(busy)
        self.model_locator_btn.setDisabled(busy)
