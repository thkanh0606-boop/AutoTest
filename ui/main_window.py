from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from services.data_store import DataStore
from ui.header import Header
from ui.pages.element_management_page import ElementManagementPage
from ui.pages.test_builder_page import TestBuilderPage
from ui.pages.vehicle_catalog_page import VehicleCatalogPage
from ui.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoTest - Web Validator")
        self.resize(1280, 750)
        self.setMinimumSize(1080, 700)

        self.store = DataStore()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.header = Header(self.store)
        right_layout.addWidget(self.header)

        self.content = QStackedWidget()
        right_layout.addWidget(self.content, 1)
        main_layout.addWidget(right_widget, 1)

        self.create_pages()

        # Linh integration: CRUD element -> Test Builder refresh ngay.
        self.element_page.elements_changed.connect(self.test_builder_page.refresh_elements)
        self.test_builder_page.manage_btn.clicked.connect(lambda: self.open_page("elements"))

        # Header Website/Page là context dùng chung cho hai màn hình của Linh.
        self.header.context_changed.connect(self.sync_test_context)
        self.sync_test_context(*self.header.current_context())

        self.sidebar.page_changed.connect(self.change_page)

        self.sidebar.set_active_page("dashboard")
        self.content.setCurrentIndex(self.page_indexes["dashboard"])

        self.setStyleSheet("""
            QMainWindow { background-color: #f8fafc; }
            QWidget { font-family: "Segoe UI"; }
        """)

    def create_pages(self):
        pages = {
            "dashboard": "Tổng quan",
            "pages": "Quản lý trang",
            "elements": "Element Management",
            "vehicle_catalog": "Danh mục xe",
            "test_builder": "Test Builder",
            "dropdown": "Kiểm tra Dropdown List",
            "label": "Kiểm tra Label / Text",
            "table": "Kiểm tra Table",
            "radio": "Kiểm tra Radio / Checkbox",
            "image": "Kiểm tra Hình ảnh",
            "title": "Kiểm tra Tiêu đề",
            "ui": "Kiểm tra Giao diện",
            "menu": "Kiểm tra Menu website",
        }

        self.page_indexes = {}
        self.element_page = ElementManagementPage(self.store)
        self.test_builder_page = TestBuilderPage(self.store)
        self.vehicle_catalog_page = VehicleCatalogPage(self.store)

        for page_name, title in pages.items():
            if page_name == "elements":
                page = self.element_page
            elif page_name == "test_builder":
                page = self.test_builder_page
            elif page_name == "vehicle_catalog":
                page = self.vehicle_catalog_page
            else:
                page = self.create_placeholder_page(title)

            index = self.content.addWidget(page)
            self.page_indexes[page_name] = index

    def create_placeholder_page(self, title):
        page = QWidget()
        page.setStyleSheet("QWidget { background-color: #f8fafc; }")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(0)

        breadcrumb = QLabel(f"AutoTest   /   {title}")
        breadcrumb.setStyleSheet("color: #8091a5; font-size: 12px; background: transparent;")
        layout.addWidget(breadcrumb)
        layout.addSpacing(22)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #101828; font-size: 28px; font-weight: 700; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(5)

        description = QLabel("Đây là màn hình giao diện của AutoTest.")
        description.setStyleSheet("color: #64748b; font-size: 14px; background: transparent;")
        layout.addWidget(description)
        layout.addSpacing(28)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(6)

        card_title = QLabel("Nội dung màn hình")
        card_title.setStyleSheet(
            "color: #111827; font-size: 18px; font-weight: 700; background: transparent; border: none;"
        )
        card_layout.addWidget(card_title)

        card_text = QLabel("Chức năng của module này sẽ được phát triển ở bước tiếp theo.")
        card_text.setStyleSheet("color: #64748b; font-size: 14px; background: transparent; border: none;")
        card_layout.addWidget(card_text)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def sync_test_context(self, website_id, page_id, website_name, page_name, url):
        self.element_page.set_context(website_id, page_id, website_name, page_name, url)
        self.test_builder_page.set_context(website_id, page_id, website_name, page_name, url)

    def open_page(self, page_name):
        if page_name not in self.page_indexes:
            return
        self.sidebar.set_active_page(page_name)
        self.content.setCurrentIndex(self.page_indexes[page_name])
        if page_name == "test_builder":
            self.test_builder_page.refresh_elements()
        elif page_name == "vehicle_catalog":
            # Danh mục xe là trang sau đăng nhập; Header phải hiển thị đúng context.
            self.header.select_context("courses_plt", "vehicle_catalog")
            self.vehicle_catalog_page.refresh_all()

    def change_page(self, page_name):
        self.open_page(page_name)
