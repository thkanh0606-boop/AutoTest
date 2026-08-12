"""Linh - Thứ Tư & Thứ Năm: Module Owner - Danh mục xe (Hãng xe / Mẫu xe).

Thứ Tư (19): UI hai bảng Hãng/Mẫu xe, modal, locator, Selenium kiểm tra
             dropdown/CRUD cơ bản.
Thứ Năm (26): CRUD Hãng/Mẫu, mapping dữ liệu Excel/CSV/JSON và xác nhận
             dropdown cập nhật sau CRUD.

Trang tự đảm bảo Page "Danh mục xe" tồn tại trong DataStore (courses_plt).
Khi mở module, Header được đồng bộ về đúng Page Danh mục xe; Selenium sẽ yêu cầu
tự đăng nhập bằng tài khoản test cục bộ nếu chưa có Firebase Auth rồi mới bắt đầu kiểm thử.
"""

import re
import unicodedata
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.catalog_import import CatalogImportError, import_catalog_file
from services.data_store import DataStore
from services.selenium_runner import CrudRequest, CrudWorker, RunnerRequest, SeleniumWorker
from ui.components import Card, ResultTable, Toast
from ui.linh_styles import LINH_PAGE_STYLE

WEBSITE_ID = "courses_plt"

PAGE_STUB = {
    "id": "vehicle_catalog",
    "name": "Danh mục xe",
    "path": "/cars/catalog",
    "description": "Trang Danh mục xe PCM: quản lý Hãng xe và Mẫu xe.",
    "elements": [],
}

GROUPS = [
    ("brand", "Hãng xe"),
    ("model", "Mẫu xe"),
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SELENIUM_PROFILE_DIR = str(PROJECT_ROOT / "data" / "selenium_profile_linh")
LOGIN_WAIT_SECONDS = 180


def slugify(value):
    value = unicodedata.normalize("NFD", value.strip().lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("đ", "d")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "element"


# =============================================================================
# PANEL: quản lý locator cho một nhóm (Hãng xe hoặc Mẫu xe)
# =============================================================================
class ElementGroupPanel(QWidget):
    """Form + bảng locator, giới hạn trong một nhóm element (brand / model).

    Tái sử dụng đúng vòng đời Lưu / Sửa / Xóa / Kiểm tra locator như
    Element Management, nhưng thu gọn để đặt song song hai bảng Hãng/Mẫu
    giống giao diện PCM thật.
    """

    elements_changed = Signal()

    def __init__(self, store: DataStore, group: str, group_label: str, parent=None):
        super().__init__(parent)
        self.store = store
        self.group = group
        self.group_label = group_label
        self.website_id = WEBSITE_ID
        self.page_id = PAGE_STUB["id"]
        self.current_url = ""
        self.editing_id = None
        self.check_status = {}
        self.thread = None
        self.worker = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        card = Card(
            f"{group_label} — Element / Locator",
            "Cấu hình locator để Selenium kiểm tra bảng và chạy CRUD bên dưới.",
        )

        row1 = QHBoxLayout()
        name_box = QVBoxLayout()
        name_label = QLabel("Tên element")
        name_label.setObjectName("SmallLabel")
        self.element_name = QLineEdit()
        self.element_name.setPlaceholderText(f"Ví dụ: Nút Thêm {group_label.lower()}")
        name_box.addWidget(name_label)
        name_box.addWidget(self.element_name)

        type_box = QVBoxLayout()
        type_label = QLabel("Loại locator")
        type_label.setObjectName("SmallLabel")
        self.locator_type = QComboBox()
        self.locator_type.addItems(
            ["ID", "NAME", "CSS", "XPATH", "CLASS_NAME", "TAG_NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT"]
        )
        self.locator_type.setCurrentText("CSS")
        type_box.addWidget(type_label)
        type_box.addWidget(self.locator_type)

        test_box = QVBoxLayout()
        test_label = QLabel("Test gợi ý")
        test_label.setObjectName("SmallLabel")
        self.recommended_test = QComboBox()
        self.recommended_test.addItems(
            ["Element tồn tại", "Text / Value", "Attribute placeholder", "Dropdown List", "Table"]
        )
        test_box.addWidget(test_label)
        test_box.addWidget(self.recommended_test)

        row1.addLayout(name_box, 2)
        row1.addLayout(type_box, 1)
        row1.addLayout(test_box, 1)
        card.layout.addLayout(row1)

        locator_label = QLabel("Locator value")
        locator_label.setObjectName("SmallLabel")
        self.locator_value = QLineEdit()
        self.locator_value.setPlaceholderText("Ví dụ: button[type='submit']")
        card.layout.addWidget(locator_label)
        card.layout.addWidget(self.locator_value)

        actions = QHBoxLayout()
        self.save_btn = QPushButton("Lưu Element")
        self.save_btn.setObjectName("PrimaryButton")
        self.check_btn = QPushButton("Kiểm tra locator")
        self.check_btn.setObjectName("SecondaryButton")
        self.clear_btn = QPushButton("Đặt lại")
        self.clear_btn.setObjectName("SecondaryButton")
        actions.addWidget(self.save_btn)
        actions.addWidget(self.check_btn)
        actions.addWidget(self.clear_btn)
        actions.addStretch()
        card.layout.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        card.layout.addWidget(self.progress)

        self.status = QLabel("Sẵn sàng.")
        self.status.setObjectName("Muted")
        self.status.setWordWrap(True)
        card.layout.addWidget(self.status)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Element", "Type", "Locator", "Status", "Thao tác"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(160)
        card.layout.addWidget(self.table)

        outer.addWidget(card)

        self.save_btn.clicked.connect(self.save_element)
        self.check_btn.clicked.connect(self.check_locator)
        self.clear_btn.clicked.connect(self.clear_form)
        self.table.cellDoubleClicked.connect(self.edit_table_row)

    def set_url(self, url):
        self.current_url = url
        self.load_table()

    def elements(self):
        return self.store.elements_by_group(self.website_id, self.page_id, self.group)

    def unique_element_id(self, base_id):
        used = {e.get("id") for e in self.store.find_page(self.website_id, self.page_id).get("elements", [])}
        if base_id not in used:
            return base_id
        index = 2
        while f"{base_id}_{index}" in used:
            index += 1
        return f"{base_id}_{index}"

    def load_table(self):
        self.store.reload()
        self.table.setRowCount(0)
        for element in self.elements():
            self.add_table_row(element)

    def add_table_row(self, element):
        row = self.table.rowCount()
        self.table.insertRow(row)
        status = self.check_status.get(element.get("id"), "Chưa kiểm tra")
        values = [
            element.get("name", ""),
            element.get("locator_type", ""),
            element.get("locator_value", ""),
            status,
        ]
        for col, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            if col == 0:
                item.setData(Qt.UserRole, element.get("id"))
            self.table.setItem(row, col, item)

        action = QWidget()
        layout = QHBoxLayout(action)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        edit_btn = QPushButton("Sửa")
        edit_btn.setObjectName("SecondaryButton")
        delete_btn = QPushButton("Xóa")
        delete_btn.setObjectName("DangerButton")
        edit_btn.clicked.connect(lambda _, eid=element.get("id"): self.edit_element(eid))
        delete_btn.clicked.connect(lambda _, eid=element.get("id"): self.delete_element(eid))
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        self.table.setCellWidget(row, 4, action)

    def edit_table_row(self, row, _column):
        item = self.table.item(row, 0)
        if item:
            element_id = item.data(Qt.UserRole)
            if element_id:
                self.edit_element(element_id)

    def edit_element(self, element_id):
        element = self.store.find_element(self.website_id, self.page_id, element_id)
        if not element:
            return
        self.editing_id = element_id
        self.element_name.setText(element.get("name", ""))
        self.locator_type.setCurrentText(element.get("locator_type", "CSS"))
        self.locator_value.setText(element.get("locator_value", ""))
        recommended = element.get("recommended_test", "Element tồn tại")
        idx = self.recommended_test.findText(recommended)
        if idx >= 0:
            self.recommended_test.setCurrentIndex(idx)
        self.save_btn.setText("Cập nhật Element")

    def clear_form(self):
        self.editing_id = None
        self.element_name.clear()
        self.locator_value.clear()
        self.locator_type.setCurrentText("CSS")
        self.recommended_test.setCurrentText("Element tồn tại")
        self.save_btn.setText("Lưu Element")

    def save_element(self):
        name = self.element_name.text().strip()
        locator_value = self.locator_value.text().strip()
        if not name or not locator_value:
            self.status.setText("Cần nhập Tên element và Locator.")
            return

        element_id = self.editing_id or self.unique_element_id(slugify(f"{self.group}_{name}"))
        data = {
            "id": element_id,
            "name": name,
            "locator_type": self.locator_type.currentText(),
            "locator_value": locator_value,
            "recommended_test": self.recommended_test.currentText(),
            "group": self.group,
        }
        self.store.add_or_update_element(
            self.website_id, self.page_id, data, original_element_id=self.editing_id
        )
        self.load_table()
        self.clear_form()
        self.elements_changed.emit()
        self.status.setText("Đã lưu element.")

    def delete_element(self, element_id):
        answer = QMessageBox.question(
            self, "Xóa element", "Bạn có chắc muốn xóa element này?", QMessageBox.Yes | QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        if self.store.delete_element(self.website_id, self.page_id, element_id):
            self.load_table()
            self.elements_changed.emit()
            self.status.setText("Đã xóa element.")

    def set_loading(self, loading, message):
        self.progress.setVisible(loading)
        self.check_btn.setEnabled(not loading)
        self.save_btn.setEnabled(not loading)
        self.clear_btn.setEnabled(not loading)
        self.status.setText(message)

    def check_locator(self):
        locator = self.locator_value.text().strip()
        if not locator:
            self.status.setText("Nhập locator trước khi kiểm tra.")
            return
        if not self.current_url:
            self.status.setText("Page chưa có URL.")
            return

        request = RunnerRequest(
            url=self.current_url,
            locator_type=self.locator_type.currentText(),
            locator_value=locator,
            test_type="Element tồn tại",
            expected_lines=["Tồn tại"],
            timeout=12,
            show_browser=True,
            require_login=True,
            login_wait_seconds=LOGIN_WAIT_SECONDS,
            profile_dir=SELENIUM_PROFILE_DIR,
        )
        self.set_loading(
            True,
            "Đang mở Chrome và tự đăng nhập nếu cần. AutoTest sẽ vào Danh mục xe rồi kiểm tra locator.",
        )
        self.thread = QThread(self)
        self.worker = SeleniumWorker(request, mode="check")
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.status.setText)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_check_finished(self, status, _rows, message):
        self.set_loading(False, message)
        if self.editing_id:
            self.check_status[self.editing_id] = status
            self.load_table()


# =============================================================================
# TRANG CHÍNH: DANH MỤC XE
# =============================================================================
class VehicleCatalogPage(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self.setObjectName("LinhPage")
        self.setStyleSheet(LINH_PAGE_STYLE)

        self.store = store
        self.website_id = WEBSITE_ID
        self.page_id = self.store.ensure_page(WEBSITE_ID, PAGE_STUB)
        self.current_url = self.store.page_url(self.website_id, self.page_id)

        self.dataset_rows = []
        self.dataset_warnings = []
        self.thread = None
        self.worker = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("LinhScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("LinhPage")
        root = QVBoxLayout(content)
        root.setContentsMargins(30, 24, 30, 26)
        root.setSpacing(12)

        title = QLabel("DANH MỤC XE")
        title.setObjectName("LinhTitle")
        root.addWidget(title)

        subtitle = QLabel(
            "Module Owner: Linh — Hãng xe & Mẫu xe của PCM. Luồng kiểm thử đúng: "
            "Tự đăng nhập → Danh mục xe → chạy Locator/CRUD."
        )
        subtitle.setObjectName("LinhSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        context_card = Card("Phạm vi đang quản lý")
        context_row = QHBoxLayout()
        context_label = QLabel("PLT Courses  /  Danh mục xe")
        context_label.setStyleSheet("font-weight: 700; color: #0f172a;")
        context_row.addWidget(context_label)
        context_row.addStretch()
        context_card.layout.addLayout(context_row)
        url_label = QLabel(self.current_url)
        url_label.setObjectName("Muted")
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        context_card.layout.addWidget(url_label)
        root.addWidget(context_card)

        login_card = Card(
            "Tự động đăng nhập trước khi kiểm thử",
            "Fleet Console yêu cầu xác thực. Khi bấm Kiểm tra locator hoặc Chạy kiểm tra CRUD, "
            "AutoTest tự đọc tài khoản test từ file .autotest.env cục bộ, tự đăng nhập Fleet Console, "
            "sau đó mở /cars/catalog và tiếp tục kiểm thử. File credential đã được .gitignore nên không bị push lên GitHub.",
        )
        login_hint = QLabel(
            "Bước 1: AutoTest tự đăng nhập  →  Bước 2: tự mở Danh mục xe  →  Bước 3: kiểm thử tự chạy."
        )
        login_hint.setObjectName("Muted")
        login_hint.setWordWrap(True)
        login_card.layout.addWidget(login_hint)
        root.addWidget(login_card)

        # ---- Hai bảng Hãng xe / Mẫu xe song song ----
        self.brand_panel = ElementGroupPanel(self.store, "brand", "Hãng xe")
        self.model_panel = ElementGroupPanel(self.store, "model", "Mẫu xe")
        self.brand_panel.set_url(self.current_url)
        self.model_panel.set_url(self.current_url)
        self.brand_panel.elements_changed.connect(self.refresh_all)
        self.model_panel.elements_changed.connect(self.refresh_all)

        panels_row = QHBoxLayout()
        panels_row.setSpacing(12)
        panels_row.addWidget(self.brand_panel, 1)
        panels_row.addWidget(self.model_panel, 1)
        root.addLayout(panels_row)

        # ---- Bộ dữ liệu kiểm thử (Import Excel/CSV/JSON) ----
        dataset_card = Card(
            "Bộ dữ liệu kiểm thử (Import Excel / CSV / JSON)",
            "Cột cần có: loai (hang/mau), ten, hang (chỉ Mẫu xe cần), trang_thai. "
            "File mẫu: data/sample_import/danh_muc_xe_mau.csv|.json",
        )
        dataset_actions = QHBoxLayout()
        self.import_btn = QPushButton("Chọn file để Import")
        self.import_btn.setObjectName("PrimaryButton")
        self.clear_dataset_btn = QPushButton("Xóa dữ liệu đã nạp")
        self.clear_dataset_btn.setObjectName("SecondaryButton")
        dataset_actions.addWidget(self.import_btn)
        dataset_actions.addWidget(self.clear_dataset_btn)
        dataset_actions.addStretch()
        dataset_card.layout.addLayout(dataset_actions)

        self.dataset_status = QLabel("Chưa import dữ liệu.")
        self.dataset_status.setObjectName("Muted")
        self.dataset_status.setWordWrap(True)
        dataset_card.layout.addWidget(self.dataset_status)

        self.dataset_table = QTableWidget(0, 4)
        self.dataset_table.setHorizontalHeaderLabels(["Loại", "Tên", "Hãng liên kết", "Trạng thái"])
        d_header = self.dataset_table.horizontalHeader()
        d_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        d_header.setSectionResizeMode(1, QHeaderView.Stretch)
        d_header.setSectionResizeMode(2, QHeaderView.Stretch)
        d_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.dataset_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataset_table.setAlternatingRowColors(True)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.setMinimumHeight(150)
        dataset_card.layout.addWidget(self.dataset_table)
        root.addWidget(dataset_card)

        # ---- Kiểm tra CRUD & dropdown phụ thuộc ----
        crud_card = Card(
            "Kiểm tra CRUD & Dropdown phụ thuộc",
            "Selenium tự đăng nhập nếu cần, sau đó mở Danh mục xe, thêm một Hãng/Mẫu, "
            "kiểm tra bảng cập nhật và dropdown liên kết đã có giá trị mới; cuối cùng tự dọn dữ liệu test (best-effort).",
        )

        crud_row1 = QHBoxLayout()
        group_box = QVBoxLayout()
        group_label = QLabel("Nhóm kiểm tra")
        group_label.setObjectName("SmallLabel")
        self.group_combo = QComboBox()
        for group_id, group_label_text in GROUPS:
            self.group_combo.addItem(group_label_text, group_id)
        group_box.addWidget(group_label)
        group_box.addWidget(self.group_combo)

        value_box = QVBoxLayout()
        value_label = QLabel("Giá trị Tên (từ dữ liệu import hoặc nhập tay)")
        value_label.setObjectName("SmallLabel")
        self.value_combo = QComboBox()
        self.value_combo.setEditable(True)
        value_box.addWidget(value_label)
        value_box.addWidget(self.value_combo)

        brand_box = QVBoxLayout()
        brand_label = QLabel("Hãng liên kết (chỉ Mẫu xe)")
        brand_label.setObjectName("SmallLabel")
        self.brand_value_combo = QComboBox()
        self.brand_value_combo.setEditable(True)
        brand_box.addWidget(brand_label)
        brand_box.addWidget(self.brand_value_combo)

        crud_row1.addLayout(group_box, 1)
        crud_row1.addLayout(value_box, 1)
        crud_row1.addLayout(brand_box, 1)
        crud_card.layout.addLayout(crud_row1)

        options_row = QHBoxLayout()
        self.cleanup_cb = QCheckBox("Dọn dữ liệu test sau khi chạy")
        self.cleanup_cb.setChecked(True)
        self.browser_cb = QCheckBox("Hiện Chrome khi chạy (khuyên bật để quan sát)")
        self.browser_cb.setChecked(True)
        self.browser_cb.setEnabled(False)
        options_row.addWidget(self.cleanup_cb)
        options_row.addWidget(self.browser_cb)
        options_row.addStretch()
        self.run_crud_btn = QPushButton("Chạy kiểm tra CRUD")
        self.run_crud_btn.setObjectName("PrimaryButton")
        options_row.addWidget(self.run_crud_btn)
        crud_card.layout.addLayout(options_row)

        self.crud_progress = QProgressBar()
        self.crud_progress.setRange(0, 0)
        self.crud_progress.hide()
        crud_card.layout.addWidget(self.crud_progress)

        self.crud_status = QLabel("Chưa chạy kiểm tra CRUD.")
        self.crud_status.setObjectName("Muted")
        self.crud_status.setWordWrap(True)
        crud_card.layout.addWidget(self.crud_status)

        self.result_table = ResultTable()
        self.result_table.setMinimumHeight(150)
        crud_card.layout.addWidget(self.result_table)

        root.addWidget(crud_card)
        root.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.toast = Toast(self)

        self.import_btn.clicked.connect(self.import_dataset)
        self.clear_dataset_btn.clicked.connect(self.clear_dataset)
        self.group_combo.currentIndexChanged.connect(self.on_group_changed)
        self.value_combo.currentIndexChanged.connect(self.on_value_selected)
        self.run_crud_btn.clicked.connect(self.run_crud_test)

        self.on_group_changed()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.toast.isVisible():
            self.toast.adjustSize()
            self.toast.move(
                max(12, self.width() - self.toast.width() - 24),
                max(12, self.height() - self.toast.height() - 24),
            )

    def refresh_all(self):
        self.current_url = self.store.page_url(self.website_id, self.page_id)
        self.brand_panel.set_url(self.current_url)
        self.model_panel.set_url(self.current_url)

    # ------------------------------------------------------------------
    # IMPORT DỮ LIỆU (Thứ Năm)
    # ------------------------------------------------------------------
    def import_dataset(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import dữ liệu Hãng/Mẫu xe",
            "",
            "Dữ liệu (*.csv *.json *.xlsx *.xls)",
        )
        if not path:
            return
        try:
            rows, warnings = import_catalog_file(path)
        except CatalogImportError as exc:
            self.toast.show_message(str(exc), "ERROR", 4500)
            self.dataset_status.setText(str(exc))
            return

        self.dataset_rows = rows
        self.dataset_warnings = warnings
        self.load_dataset_table()
        self.refresh_value_combos()

        summary = f"Đã import {len(rows)} dòng từ {path.split('/')[-1]}."
        if warnings:
            summary += f" ({len(warnings)} cảnh báo, xem trong bảng.)"
        self.dataset_status.setText(summary)
        self.toast.show_message(summary, "PASS" if not warnings else "INFO")

    def clear_dataset(self):
        self.dataset_rows = []
        self.dataset_warnings = []
        self.load_dataset_table()
        self.refresh_value_combos()
        self.dataset_status.setText("Đã xóa dữ liệu đã nạp.")

    def load_dataset_table(self):
        self.dataset_table.setRowCount(0)
        for row in self.dataset_rows:
            r = self.dataset_table.rowCount()
            self.dataset_table.insertRow(r)
            loai_label = "Hãng xe" if row["loai"] == "hang" else "Mẫu xe"
            values = [loai_label, row["ten"], row.get("hang", ""), row.get("trang_thai", "")]
            for col, value in enumerate(values):
                self.dataset_table.setItem(r, col, QTableWidgetItem(str(value)))

    def refresh_value_combos(self):
        group_id = self.group_combo.currentData()
        loai = "hang" if group_id == "brand" else "mau"

        self.value_combo.blockSignals(True)
        self.value_combo.clear()
        for row in self.dataset_rows:
            if row["loai"] == loai:
                self.value_combo.addItem(row["ten"], row)
        self.value_combo.blockSignals(False)

        self.brand_value_combo.blockSignals(True)
        self.brand_value_combo.clear()
        for row in self.dataset_rows:
            if row["loai"] == "hang":
                self.brand_value_combo.addItem(row["ten"], row)
        self.brand_value_combo.blockSignals(False)

        self.on_value_selected()

    def on_group_changed(self):
        group_id = self.group_combo.currentData()
        is_model = group_id == "model"
        self.brand_value_combo.setEnabled(is_model)
        self.refresh_value_combos()

    def on_value_selected(self):
        row = self.value_combo.currentData()
        if isinstance(row, dict) and row.get("hang"):
            idx = self.brand_value_combo.findText(row["hang"])
            if idx >= 0:
                self.brand_value_combo.setCurrentIndex(idx)
            else:
                self.brand_value_combo.setEditText(row["hang"])

    # ------------------------------------------------------------------
    # CHẠY KIỂM TRA CRUD (Thứ Năm)
    # ------------------------------------------------------------------
    def _locator_tuple(self, panel: ElementGroupPanel, element_id):
        element = self.store.find_element(self.website_id, self.page_id, element_id)
        if not element:
            return None
        return (element.get("locator_type", "CSS"), element.get("locator_value", ""))

    def set_crud_loading(self, loading, message):
        self.crud_progress.setVisible(loading)
        self.run_crud_btn.setEnabled(not loading)
        self.crud_status.setText(message)

    def run_crud_test(self):
        group_id = self.group_combo.currentData()
        group_label = "Hãng xe" if group_id == "brand" else "Mẫu xe"
        value_name = self.value_combo.currentText().strip()

        if not value_name:
            self.toast.show_message("Nhập hoặc chọn Tên để chạy CRUD.", "ERROR")
            return

        if group_id == "brand":
            add_button = self._locator_tuple(self.brand_panel, "brand_add_button")
            name_field = self._locator_tuple(self.brand_panel, "brand_name_input")
            save_button = self._locator_tuple(self.brand_panel, "brand_save_button")
            table = self._locator_tuple(self.brand_panel, "brand_table")
            # Sau khi thêm Hãng, dropdown lọc Hãng ở khu Mẫu xe phải có Hãng mới.
            dependent_dropdown = self._locator_tuple(self.model_panel, "model_filter_dropdown")
            brand_field = None
            value_brand = ""
        else:
            add_button = self._locator_tuple(self.model_panel, "model_add_button")
            name_field = self._locator_tuple(self.model_panel, "model_name_input")
            save_button = self._locator_tuple(self.model_panel, "model_save_button")
            table = self._locator_tuple(self.model_panel, "model_table")
            # Với Mẫu xe, mapping được kiểm tra ngay trên dòng bảng sau khi tạo.
            # Dropdown lọc ngoài trang chứa Hãng, không chứa tên Mẫu nên không kiểm tra model ở đây.
            dependent_dropdown = None
            brand_field = self._locator_tuple(self.model_panel, "model_brand_select")
            value_brand = self.brand_value_combo.currentText().strip()
            if not value_brand:
                self.toast.show_message("Mẫu xe cần chọn Hãng liên kết trước khi chạy.", "ERROR")
                return

        missing = [
            name
            for name, loc in [
                ("Nút Thêm", add_button),
                ("Ô tên", name_field),
                ("Nút Lưu", save_button),
                ("Bảng", table),
            ]
            if not loc or not loc[1]
        ]
        if missing:
            self.toast.show_message(
                "Thiếu locator cho: " + ", ".join(missing) + ". Cấu hình ở bảng phía trên trước.",
                "ERROR",
                4500,
            )
            return

        request = CrudRequest(
            url=self.current_url,
            add_button=add_button,
            name_field=name_field,
            save_button=save_button,
            table=table,
            value_name=value_name,
            group_label=group_label,
            brand_field=brand_field,
            value_brand=value_brand,
            dependent_dropdown=dependent_dropdown if dependent_dropdown and dependent_dropdown[1] else None,
            cleanup=self.cleanup_cb.isChecked(),
            timeout=15,
            show_browser=True,
            require_login=True,
            login_wait_seconds=LOGIN_WAIT_SECONDS,
            profile_dir=SELENIUM_PROFILE_DIR,
        )

        self.result_table.setRowCount(0)
        self.set_crud_loading(True, f"Đang chạy CRUD {group_label}...")
        self.thread = QThread(self)
        self.worker = CrudWorker(request)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.crud_status.setText)
        self.worker.finished.connect(self.on_crud_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_crud_finished(self, status, rows, message):
        self.set_crud_loading(False, message)
        rows = rows or []
        self.result_table.set_results(rows)
        self.toast.show_message(message, status if status in {"PASS", "FAIL", "ERROR"} else "INFO", 4200)
