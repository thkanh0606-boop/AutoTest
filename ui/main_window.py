import threading
from core.config import Config

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QFormLayout
)
from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

# Import local modules
from ui.sidebar import Sidebar
from ui.header import Header
from ui.test_builder_page import TestBuilderPage
from ui.vehicle_catalog_page import VehicleCatalogPage
from ui.test_suite_page import TestSuitePage


# --- MÃ SVG VECTOR ICON MẮT ---
SVG_EYE_OPEN = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
</svg>"""

SVG_EYE_OFF = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
</svg>"""


def create_svg_icon(svg_code: str, width: int = 20, height: int = 20) -> QIcon:
    """Hàm dựng hình icon SVG sắc nét thành QIcon"""
    renderer = QSvgRenderer(QByteArray(svg_code.encode('utf-8')))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)  # Chuẩn Enum trong PySide6 / Qt6
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    ...
    def __init__(self):
        super().__init__()

        # =====================================================
        # MAIN WINDOW
        # =====================================================

        self.setWindowTitle("AutoTest - Web Validator")
        self.resize(1280, 750)

        # =====================================================
        # CENTRAL WIDGET
        # =====================================================

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        # =====================================================
        # SIDEBAR
        # =====================================================

        self.sidebar = Sidebar()

        main_layout.addWidget(
            self.sidebar
        )

        # =====================================================
        # RIGHT SIDE
        #
        # Header + Content
        # =====================================================

        right_widget = QWidget()

        right_layout = QVBoxLayout(
            right_widget
        )

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(0)

        # =====================================================
        # HEADER
        # =====================================================

        self.header = Header()

        right_layout.addWidget(
            self.header
        )

        # =====================================================
        # CONTENT
        # =====================================================

        self.content = QStackedWidget()

        right_layout.addWidget(
            self.content
        )

        # =====================================================
        # ADD RIGHT SIDE
        # =====================================================

        main_layout.addWidget(
            right_widget,
            1
        )

        # =====================================================
        # CREATE PAGES
        # =====================================================

        self.create_pages()

        # =====================================================
        # SIDEBAR ROUTING
        # =====================================================

        self.sidebar.page_changed.connect(
            self.change_page
        )

        # =====================================================
        # DEFAULT PAGE
        # =====================================================

        self.sidebar.set_active_page(
            "dashboard"
        )

        self.content.setCurrentIndex(
            self.page_indexes["dashboard"]
        )

        # =====================================================
        # GLOBAL STYLE
        # =====================================================

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }

            QWidget {
                font-family: "Segoe UI";
            }
        """)

    # =========================================================
    # CREATE PAGES
    # =========================================================

    def create_pages(self):

        pages = {
            "dashboard": "Tổng quan",
            "pages": "Quản lý trang",
            "config": "Cấu hình hệ thống",
            "vehicle_catalog": "Danh mục xe",
            "test_suite": "Chạy Test Suite",
            "dropdown": "Kiểm tra Dropdown List",
            "label": "Kiểm tra Label / Text",
            "table": "Kiểm tra Table",
            "radio": "Kiểm tra Radio / Checkbox",
            "image": "Kiểm tra Hình ảnh",
            "title": "Kiểm tra Tiêu đề",
            "ui": "Kiểm tra Giao diện",
            "menu": "Kiểm tra Menu website"
        }

        self.page_indexes = {}

        for page_name, title in pages.items():

            # Nếu là trang config thì tạo giao diện Form cấu hình riêng
            if page_name in ("dropdown", "label", "table", "radio", "image", "title", "ui", "menu"):
                page = TestBuilderPage(
                    page_name,
                    title
                )
            elif page_name == "config":
                page = self.create_config_page(title)
            elif page_name == "vehicle_catalog":
                page = VehicleCatalogPage()
            elif page_name == "test_suite":
                page = TestSuitePage()
            else:
                page = self.create_placeholder_page(title)

            index = self.content.addWidget(page)
            self.page_indexes[page_name] = index

    # =========================================================
    # PLACEHOLDER PAGE
    # =========================================================

    def create_placeholder_page(self, title):

        page = QWidget()

        page.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            38,
            30,
            38,
            30
        )

        layout.setSpacing(0)

        # =====================================================
        # BREADCRUMB
        # =====================================================

        breadcrumb = QLabel(
            f"AutoTest   /   {title}"
        )

        breadcrumb.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 12px;
                background: transparent;
            }
        """)

        layout.addWidget(
            breadcrumb
        )

        layout.addSpacing(22)

        # =====================================================
        # TITLE
        # =====================================================

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                color: #101828;
                font-size: 28px;
                font-weight: 700;
                background: transparent;
            }
        """)

        layout.addWidget(
            title_label
        )

        layout.addSpacing(5)

        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = QLabel(
            "Đây là màn hình giao diện của AutoTest."
        )

        description.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                background: transparent;
            }
        """)

        layout.addWidget(
            description
        )

        layout.addSpacing(28)

        # =====================================================
        # PLACEHOLDER CARD
        # =====================================================

        card = QFrame()

        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        card_layout.setSpacing(6)

        # -----------------------------------------------------
        # CARD TITLE
        # -----------------------------------------------------

        card_title = QLabel(
            "Nội dung màn hình"
        )

        card_title.setStyleSheet("""
            QLabel {
                color: #111827;
                font-size: 18px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
        """)

        card_layout.addWidget(
            card_title
        )

        # -----------------------------------------------------
        # CARD TEXT
        # -----------------------------------------------------

        card_text = QLabel(
            "Chức năng của module này sẽ được "
            "phát triển ở bước tiếp theo."
        )

        card_text.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)

        card_layout.addWidget(
            card_text
        )

        layout.addWidget(
            card
        )

        layout.addStretch()

        return page

    # =========================================================
    # ROUTING
    # =========================================================

    def change_page(
        self,
        page_name
    ):

        if page_name not in self.page_indexes:
            return

        index = self.page_indexes[
            page_name
        ]

        self.content.setCurrentIndex(
            index
        )

        # Linh - đồng bộ Header khi mở riêng module Danh mục xe.
        if page_name == "vehicle_catalog":
            self.header.website_combo.setCurrentText("PLT Fleet Console")
            if self.header.page_combo.findText("Danh mục xe") < 0:
                self.header.page_combo.addItem("Danh mục xe")
            self.header.page_combo.setCurrentText("Danh mục xe")
            self.header.url_input.setText("https://courses.plt.pro.vn/cars/catalog")

    def open_module_from_quick_menu(
        self,
        page_name
    ):

        if page_name not in self.page_indexes:
            return

        self.sidebar.set_active_page(
            page_name
        )

        self.change_page(
            page_name
        )

   # =========================================================
    # CONFIG PAGE (FORM CHỈNH SỬA + ICON SVG MẮT)
    # =========================================================

    def create_config_page(self, title):
        page = QWidget()
        page.setStyleSheet("QWidget { background-color: #f8fafc; }")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)

        # 1. Breadcrumb & Title
        breadcrumb = QLabel(f"AutoTest   /   {title}")
        breadcrumb.setStyleSheet("color: #8091a5; font-size: 12px; background: transparent;")
        layout.addWidget(breadcrumb)
        layout.addSpacing(22)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #101828; font-size: 28px; font-weight: 700; background: transparent;")
        layout.addWidget(title_label)
        layout.addSpacing(5)

        description = QLabel("Tùy chỉnh các thông số kết nối và tài khoản kiểm thử mặc định.")
        description.setStyleSheet("color: #64748b; font-size: 14px; background: transparent;")
        layout.addWidget(description)
        layout.addSpacing(28)

        # 2. Card Form
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
        card_layout.setContentsMargins(28, 28, 28, 28)

        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Inputs Căn Trái
        self.input_base_url = QLineEdit("https://courses.plt.pro.vn/login")
        self.input_base_url.setFixedWidth(450)

        self.input_email = QLineEdit("test@gmail.com")
        self.input_email.setFixedWidth(450)

        # Password + Nút SVG Eye
        pass_container = QWidget()
        pass_container.setFixedWidth(450)
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(8)

        self.input_password = QLineEdit("123123")
        self.input_password.setEchoMode(QLineEdit.Password)

        # Tạo Icon SVG
        self.icon_eye_open = create_svg_icon(SVG_EYE_OPEN, 18, 18)
        self.icon_eye_off = create_svg_icon(SVG_EYE_OFF, 18, 18)

        # Nút Mắt hiển thị Icon SVG
        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setFixedSize(36, 34)
        self.btn_toggle_pass.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pass.setIcon(self.icon_eye_open)
        self.btn_toggle_pass.setIconSize(QSize(18, 18))
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
        self.btn_toggle_pass.clicked.connect(self.toggle_password_visibility)

        pass_layout.addWidget(self.input_password)
        pass_layout.addWidget(self.btn_toggle_pass)

        form_layout.addRow("BASE_URL:", self.input_base_url)
        form_layout.addRow("TEST_EMAIL:", self.input_email)
        form_layout.addRow("TEST_PASSWORD:", pass_container)

        card_layout.addLayout(form_layout)
        card_layout.addSpacing(24)

        # --- LAYOUT CHỨA BỘ NÚT BẤM (HÀNH ĐỘNG) ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        # Nút Lưu Cấu Hình
        btn_save = QPushButton("Lưu cấu hình")
        btn_save.setFixedHeight(38)
        btn_save.setFixedWidth(130)
        btn_save.setCursor(Qt.PointingHandCursor)
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
        btn_save.clicked.connect(self.save_config)

        # Nút Chạy Thử Đăng Nhập
        btn_test_login = QPushButton("Chạy thử")
        btn_test_login.setFixedHeight(38)
        btn_test_login.setFixedWidth(180)
        btn_test_login.setCursor(Qt.PointingHandCursor)
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
        btn_test_login.clicked.connect(self.run_test_login)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_test_login)
        btn_layout.addStretch()

        card_layout.addLayout(btn_layout)

        layout.addWidget(card)
        layout.addStretch()

        return page

    # =========================================================
    # HÀM BẬT / ẨN MẮT XEM MẬT KHẨU
    # =========================================================

    def toggle_password_visibility(self):
        if self.input_password.echoMode() == QLineEdit.Password:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setIcon(self.icon_eye_off)
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setIcon(self.icon_eye_open)

 # =========================================================
    # HÀM LƯU CẤU HÌNH
    # =========================================================

    def save_config(self):
        Config.BASE_URL = self.input_base_url.text().strip()
        Config.TEST_EMAIL = self.input_email.text().strip()
        Config.TEST_PASSWORD = self.input_password.text().strip()

        print(f"[CONFIG SAVED] BASE_URL: {Config.BASE_URL} | EMAIL: {Config.TEST_EMAIL} | PASS: {Config.TEST_PASSWORD}")

    # =========================================================
    # HÀM CHẠY THỬ TEST ĐĂNG NHẬP
    # =========================================================

    def run_test_login(self):
        url = self.input_base_url.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        # Đồng bộ vào Config
        Config.BASE_URL = url
        Config.TEST_EMAIL = email
        Config.TEST_PASSWORD = password

        print(f"[TEST RUNNER] Khởi chạy Selenium với URL: {url} | EMAIL: {email}...")

        from runners.login_runner import run_login_test

        threading.Thread(
            target=run_login_test,
            kwargs={"url": url, "email": email, "password": password},
            daemon=True
        ).start()
