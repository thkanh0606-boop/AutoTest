import threading

from runners.login_runner import run_login_test
from core.config import Config
from services.data_store import DataStore

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QFormLayout,
)
from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

from ui.sidebar import Sidebar
from ui.header import Header

# Trang của Linh
from ui.pages.element_management_page import ElementManagementPage
from ui.pages.test_builder_page import TestBuilderPage as LinhTestBuilderPage
from ui.pages.vehicle_catalog_page import VehicleCatalogPage

# Test Builder chung của nhánh main
from ui.test_builder_page import TestBuilderPage as GenericTestBuilderPage


SVG_EYE_OPEN = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
</svg>"""

SVG_EYE_OFF = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
</svg>"""


def create_svg_icon(svg_code: str, width: int = 20, height: int = 20) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg_code.encode("utf-8")))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


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

        # Linh: CRUD Element -> Test Builder refresh ngay.
        self.element_page.elements_changed.connect(
            self.test_builder_page.refresh_elements
        )
        self.test_builder_page.manage_btn.clicked.connect(
            lambda: self.open_page("elements")
        )

        # Header Website/Page là context dùng chung cho phần của Linh.
        self.header.context_changed.connect(self.sync_test_context)
        self.sync_test_context(*self.header.current_context())

        self.sidebar.page_changed.connect(self.change_page)

        self.sidebar.set_active_page("dashboard")
        self.content.setCurrentIndex(self.page_indexes["dashboard"])

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }

            QWidget {
                font-family: "Segoe UI";
            }
        """)

    def create_pages(self):
        pages = {
            "dashboard": "Tổng quan",
            "pages": "Quản lý trang",
            "elements": "Element Management",
            "vehicle_catalog": "Danh mục xe",
            "config": "Cấu hình hệ thống",
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

        # Các module của Linh
        self.element_page = ElementManagementPage(self.store)
        self.test_builder_page = LinhTestBuilderPage(self.store)
        self.vehicle_catalog_page = VehicleCatalogPage(self.store)

        generic_test_pages = {
            "dropdown",
            "label",
            "table",
            "radio",
            "image",
            "title",
            "ui",
            "menu",
        }

        for page_name, title in pages.items():
            if page_name == "elements":
                page = self.element_page

            elif page_name == "test_builder":
                page = self.test_builder_page

            elif page_name == "vehicle_catalog":
                page = self.vehicle_catalog_page

            elif page_name == "config":
                page = self.create_config_page(title)

            elif page_name in generic_test_pages:
                page = GenericTestBuilderPage(page_name, title)

            else:
                page = self.create_placeholder_page(title)

            index = self.content.addWidget(page)
            self.page_indexes[page_name] = index

    def create_placeholder_page(self, title):
        page = QWidget()
        page.setStyleSheet(
            "QWidget { background-color: #f8fafc; }"
        )

        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(0)

        breadcrumb = QLabel(
            f"AutoTest   /   {title}"
        )
        breadcrumb.setStyleSheet(
            "color: #8091a5; font-size: 12px; background: transparent;"
        )
        layout.addWidget(breadcrumb)
        layout.addSpacing(22)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #101828; font-size: 28px; "
            "font-weight: 700; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(5)

        description = QLabel(
            "Đây là màn hình giao diện của AutoTest."
        )
        description.setStyleSheet(
            "color: #64748b; font-size: 14px; background: transparent;"
        )
        layout.addWidget(description)
        layout.addSpacing(28)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { "
            "background-color: #ffffff; "
            "border: 1px solid #e5e7eb; "
            "border-radius: 10px; "
            "}"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            16, 12, 16, 12
        )
        card_layout.setSpacing(6)

        card_title = QLabel(
            "Nội dung màn hình"
        )
        card_title.setStyleSheet(
            "color: #111827; font-size: 18px; "
            "font-weight: 700; background: transparent; border: none;"
        )
        card_layout.addWidget(card_title)

        card_text = QLabel(
            "Chức năng của module này sẽ được phát triển ở bước tiếp theo."
        )
        card_text.setStyleSheet(
            "color: #64748b; font-size: 14px; "
            "background: transparent; border: none;"
        )
        card_layout.addWidget(card_text)

        layout.addWidget(card)
        layout.addStretch()

        return page

    def sync_test_context(
        self,
        website_id,
        page_id,
        website_name,
        page_name,
        url,
    ):
        self.element_page.set_context(
            website_id,
            page_id,
            website_name,
            page_name,
            url,
        )

        self.test_builder_page.set_context(
            website_id,
            page_id,
            website_name,
            page_name,
            url,
        )

    def open_page(self, page_name):
        if page_name not in self.page_indexes:
            return

        self.sidebar.set_active_page(page_name)
        self.content.setCurrentIndex(
            self.page_indexes[page_name]
        )

        if page_name == "test_builder":
            self.test_builder_page.refresh_elements()

        elif page_name == "vehicle_catalog":
            # Danh mục xe là trang sau đăng nhập.
            self.header.select_context(
                "courses_plt",
                "vehicle_catalog",
            )
            self.vehicle_catalog_page.refresh_all()

    def change_page(self, page_name):
        self.open_page(page_name)

    def open_module_from_quick_menu(
        self,
        page_name,
    ):
        self.open_page(page_name)

    def create_config_page(self, title):
        page = QWidget()
        page.setStyleSheet(
            "QWidget { background-color: #f8fafc; }"
        )

        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            38, 30, 38, 30
        )

        breadcrumb = QLabel(
            f"AutoTest   /   {title}"
        )
        breadcrumb.setStyleSheet(
            "color: #8091a5; font-size: 12px; background: transparent;"
        )
        layout.addWidget(breadcrumb)
        layout.addSpacing(22)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #101828; font-size: 28px; "
            "font-weight: 700; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(5)

        description = QLabel(
            "Tùy chỉnh các thông số kết nối và tài khoản kiểm thử mặc định."
        )
        description.setStyleSheet(
            "color: #64748b; font-size: 14px; background: transparent;"
        )
        layout.addWidget(description)
        layout.addSpacing(28)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }

            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }

            QLineEdit {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #111827;
            }

            QLineEdit:focus {
                border: 1px solid #2563eb;
                background-color: #ffffff;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            28, 28, 28, 28
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(
            Qt.AlignLeft
        )
        form_layout.setFormAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )

        self.input_base_url = QLineEdit(
            getattr(
                Config,
                "BASE_URL",
                "https://courses.plt.pro.vn/login",
            )
        )
        self.input_base_url.setFixedWidth(450)

        self.input_email = QLineEdit(
            getattr(
                Config,
                "TEST_EMAIL",
                "",
            )
        )
        self.input_email.setFixedWidth(450)

        pass_container = QWidget()
        pass_container.setFixedWidth(450)

        pass_layout = QHBoxLayout(
            pass_container
        )
        pass_layout.setContentsMargins(
            0, 0, 0, 0
        )
        pass_layout.setSpacing(8)

        self.input_password = QLineEdit(
            getattr(
                Config,
                "TEST_PASSWORD",
                "",
            )
        )
        self.input_password.setEchoMode(
            QLineEdit.Password
        )

        self.icon_eye_open = create_svg_icon(
            SVG_EYE_OPEN,
            18,
            18,
        )
        self.icon_eye_off = create_svg_icon(
            SVG_EYE_OFF,
            18,
            18,
        )

        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setFixedSize(
            36, 34
        )
        self.btn_toggle_pass.setCursor(
            Qt.PointingHandCursor
        )
        self.btn_toggle_pass.setIcon(
            self.icon_eye_open
        )
        self.btn_toggle_pass.setIconSize(
            QSize(18, 18)
        )
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.btn_toggle_pass.clicked.connect(
            self.toggle_password_visibility
        )

        pass_layout.addWidget(
            self.input_password
        )
        pass_layout.addWidget(
            self.btn_toggle_pass
        )

        form_layout.addRow(
            "BASE_URL:",
            self.input_base_url,
        )
        form_layout.addRow(
            "TEST_EMAIL:",
            self.input_email,
        )
        form_layout.addRow(
            "TEST_PASSWORD:",
            pass_container,
        )

        card_layout.addLayout(
            form_layout
        )
        card_layout.addSpacing(24)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_save = QPushButton(
            "Lưu cấu hình"
        )
        btn_save.setFixedHeight(38)
        btn_save.setFixedWidth(130)
        btn_save.setCursor(
            Qt.PointingHandCursor
        )
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_save.clicked.connect(
            self.save_config
        )

        btn_test_login = QPushButton(
            "Chạy thử"
        )
        btn_test_login.setFixedHeight(38)
        btn_test_login.setFixedWidth(180)
        btn_test_login.setCursor(
            Qt.PointingHandCursor
        )
        btn_test_login.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover {
                background-color: #15803d;
            }
        """)
        btn_test_login.clicked.connect(
            self.run_test_login
        )

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(
            btn_test_login
        )
        btn_layout.addStretch()

        card_layout.addLayout(
            btn_layout
        )

        layout.addWidget(card)
        layout.addStretch()

        return page

    def toggle_password_visibility(self):
        if (
            self.input_password.echoMode()
            == QLineEdit.Password
        ):
            self.input_password.setEchoMode(
                QLineEdit.Normal
            )
            self.btn_toggle_pass.setIcon(
                self.icon_eye_off
            )
        else:
            self.input_password.setEchoMode(
                QLineEdit.Password
            )
            self.btn_toggle_pass.setIcon(
                self.icon_eye_open
            )

    def save_config(self):
        Config.BASE_URL = (
            self.input_base_url.text().strip()
        )
        Config.TEST_EMAIL = (
            self.input_email.text().strip()
        )
        Config.TEST_PASSWORD = (
            self.input_password.text().strip()
        )

        # Không in mật khẩu ra Terminal.
        print(
            "[CONFIG SAVED] "
            f"BASE_URL: {Config.BASE_URL} | "
            f"EMAIL: {Config.TEST_EMAIL}"
        )

    def run_test_login(self):
        url = (
            self.input_base_url.text().strip()
        )
        email = (
            self.input_email.text().strip()
        )
        password = (
            self.input_password.text().strip()
        )

        Config.BASE_URL = url
        Config.TEST_EMAIL = email
        Config.TEST_PASSWORD = password

        print(
            "[TEST RUNNER] "
            f"Khởi chạy Selenium với URL: {url} | "
            f"EMAIL: {email}..."
        )

        threading.Thread(
            target=run_login_test,
            kwargs={
                "url": url,
                "email": email,
                "password": password,
            },
            daemon=True,
        ).start()
