import re
import unicodedata

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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

from services.data_store import DataStore
from services.selenium_runner import RunnerRequest, SeleniumWorker
from ui.components import Card, Toast
from ui.linh_styles import LINH_PAGE_STYLE


def slugify(value):
    value = unicodedata.normalize("NFD", value.strip().lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("đ", "d")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "element"


class ElementManagementPage(QWidget):
    elements_changed = Signal()

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self.setObjectName("LinhPage")
        self.setStyleSheet(LINH_PAGE_STYLE)

        self.store = store
        self.website_id = None
        self.page_id = None
        self.current_url = ""
        self.editing_id = None
        self.check_status = {}
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

        title = QLabel("ELEMENT MANAGEMENT")
        title.setObjectName("LinhTitle")
        root.addWidget(title)

        subtitle = QLabel(
            "Quản lý element theo Page: thêm/sửa/xóa locator và kiểm tra locator bằng Selenium."
        )
        subtitle.setObjectName("LinhSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        context_card = Card("Phạm vi đang quản lý")
        context_row = QHBoxLayout()
        self.context_label = QLabel("Chưa chọn Website / Page")
        self.context_label.setStyleSheet("font-weight: 700; color: #0f172a;")
        self.url_label = QLabel("")
        self.url_label.setObjectName("Muted")
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        context_row.addWidget(self.context_label)
        context_row.addStretch()
        context_card.layout.addLayout(context_row)
        context_card.layout.addWidget(self.url_label)
        root.addWidget(context_card)

        form = Card(
            "Element / Locator Form",
            "Tester chỉ cần chọn element ở Test Builder; locator được cấu hình và lưu tại đây.",
        )

        row1 = QHBoxLayout()
        name_box = QVBoxLayout()
        name_label = QLabel("Tên element")
        name_label.setObjectName("SmallLabel")
        self.element_name = QLineEdit()
        self.element_name.setPlaceholderText("Ví dụ: Nút Đăng nhập")
        name_box.addWidget(name_label)
        name_box.addWidget(self.element_name)

        type_box = QVBoxLayout()
        type_label = QLabel("Loại locator")
        type_label.setObjectName("SmallLabel")
        self.locator_type = QComboBox()
        self.locator_type.addItems([
            "ID", "NAME", "CSS", "XPATH", "CLASS_NAME", "TAG_NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT"
        ])
        self.locator_type.setCurrentText("CSS")
        type_box.addWidget(type_label)
        type_box.addWidget(self.locator_type)

        test_box = QVBoxLayout()
        test_label = QLabel("Loại test gợi ý")
        test_label.setObjectName("SmallLabel")
        self.recommended_test = QComboBox()
        self.recommended_test.addItems([
            "Element tồn tại", "Text / Value", "Attribute placeholder", "Dropdown List", "Table"
        ])
        test_box.addWidget(test_label)
        test_box.addWidget(self.recommended_test)

        row1.addLayout(name_box, 2)
        row1.addLayout(type_box, 1)
        row1.addLayout(test_box, 1)
        form.layout.addLayout(row1)

        locator_label = QLabel("Locator value")
        locator_label.setObjectName("SmallLabel")
        self.locator_value = QLineEdit()
        self.locator_value.setPlaceholderText("Ví dụ: button[type='submit']")
        form.layout.addWidget(locator_label)
        form.layout.addWidget(self.locator_value)

        actions = QHBoxLayout()
        self.save_btn = QPushButton("Lưu Element")
        self.save_btn.setObjectName("PrimaryButton")
        self.check_btn = QPushButton("Kiểm tra locator")
        self.check_btn.setObjectName("SecondaryButton")
        self.clear_btn = QPushButton("Đặt lại form")
        self.clear_btn.setObjectName("SecondaryButton")
        actions.addWidget(self.save_btn)
        actions.addWidget(self.check_btn)
        actions.addWidget(self.clear_btn)
        actions.addStretch()
        form.layout.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        form.layout.addWidget(self.progress)

        self.status = QLabel("Sẵn sàng.")
        self.status.setObjectName("Muted")
        self.status.setWordWrap(True)
        form.layout.addWidget(self.status)
        root.addWidget(form)

        table_card = Card(
            "Element trên trang",
            "Nhấp đúp một dòng để sửa. Dữ liệu sau khi lưu được Test Builder tải lại ngay.",
        )
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Element", "Type", "Locator", "Test gợi ý", "Status", "Thao tác"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(190)
        table_card.layout.addWidget(self.table)
        root.addWidget(table_card)
        root.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.toast = Toast(self)

        self.save_btn.clicked.connect(self.save_element)
        self.check_btn.clicked.connect(self.check_locator)
        self.clear_btn.clicked.connect(self.clear_form)
        self.table.cellDoubleClicked.connect(self.edit_table_row)

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
        if changed:
            self.clear_form()
        self.load_table()

    def page(self):
        return self.store.find_page(self.website_id, self.page_id)

    def unique_element_id(self, base_id):
        page = self.page() or {}
        used = {e.get("id") for e in page.get("elements", [])}
        if base_id not in used:
            return base_id
        index = 2
        while f"{base_id}_{index}" in used:
            index += 1
        return f"{base_id}_{index}"

    def load_table(self):
        self.store.reload()
        page = self.page()
        self.table.setRowCount(0)
        if not page:
            return
        for element in page.get("elements", []):
            self.add_table_row(element)

    def add_table_row(self, element):
        row = self.table.rowCount()
        self.table.insertRow(row)
        status = self.check_status.get(element.get("id"), "Chưa kiểm tra")
        values = [
            element.get("name", ""),
            element.get("locator_type", ""),
            element.get("locator_value", ""),
            element.get("recommended_test", ""),
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
        self.table.setCellWidget(row, 5, action)

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
        self.recommended_test.setCurrentText(element.get("recommended_test", "Element tồn tại"))
        self.save_btn.setText("Cập nhật Element")
        self.toast.show_message("Đang chỉnh sửa element.", "INFO")

    def clear_form(self):
        self.editing_id = None
        self.element_name.clear()
        self.locator_value.clear()
        self.locator_type.setCurrentText("CSS")
        self.recommended_test.setCurrentText("Element tồn tại")
        self.save_btn.setText("Lưu Element")

    def save_element(self):
        if not self.website_id or not self.page_id:
            self.toast.show_message("Chưa chọn Website / Page.", "ERROR")
            return

        name = self.element_name.text().strip()
        locator_value = self.locator_value.text().strip()
        if not name or not locator_value:
            self.toast.show_message("Cần nhập Tên element và Locator.", "ERROR")
            return

        element_id = self.editing_id or self.unique_element_id(slugify(name))
        data = {
            "id": element_id,
            "name": name,
            "locator_type": self.locator_type.currentText(),
            "locator_value": locator_value,
            "recommended_test": self.recommended_test.currentText(),
        }
        self.store.add_or_update_element(
            self.website_id,
            self.page_id,
            data,
            original_element_id=self.editing_id,
        )
        self.load_table()
        self.clear_form()
        self.elements_changed.emit()
        self.toast.show_message("Đã lưu element. Test Builder sẽ cập nhật ngay.", "PASS")

    def delete_element(self, element_id):
        answer = QMessageBox.question(
            self,
            "Xóa element",
            "Bạn có chắc muốn xóa element này?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if self.store.delete_element(self.website_id, self.page_id, element_id):
            self.load_table()
            self.elements_changed.emit()
            self.toast.show_message("Đã xóa element.", "PASS")

    def set_loading(self, loading, message):
        self.progress.setVisible(loading)
        self.check_btn.setEnabled(not loading)
        self.save_btn.setEnabled(not loading)
        self.clear_btn.setEnabled(not loading)
        self.status.setText(message)

    def check_locator(self):
        locator = self.locator_value.text().strip()
        if not locator:
            self.toast.show_message("Nhập locator trước khi kiểm tra.", "ERROR")
            return
        if not self.current_url:
            self.toast.show_message("Page chưa có URL.", "ERROR")
            return

        request = RunnerRequest(
            url=self.current_url,
            locator_type=self.locator_type.currentText(),
            locator_value=locator,
            test_type="Element tồn tại",
            expected_lines=["Tồn tại"],
            timeout=10,
            show_browser=False,
        )
        self.set_loading(True, "Đang gọi Selenium để kiểm tra locator...")
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

        object_name = {
            "PASS": "StatusPass",
            "FAIL": "StatusFail",
            "ERROR": "StatusError",
        }.get(status, "Muted")
        self.status.setObjectName(object_name)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

        if status == "PASS":
            self.toast.show_message("PASS – Locator tìm thấy.", "PASS")
        elif status == "FAIL":
            self.toast.show_message("FAIL – Locator không tìm thấy.", "FAIL")
        else:
            self.toast.show_message(message, "ERROR")
