from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QFrame
)

from PySide6.QtCore import Qt

from ui.sidebar import Sidebar
from ui.header import Header


class MainWindow(QMainWindow):

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

            page = self.create_placeholder_page(
                title
            )

            index = self.content.addWidget(
                page
            )

            self.page_indexes[
                page_name
            ] = index

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