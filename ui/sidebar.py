from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSizePolicy
)

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        # =====================================================
        # SIDEBAR
        # =====================================================

        self.setObjectName("Sidebar")
        self.setFixedWidth(248)

        # Quan trọng: khóa nền sidebar
        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.setStyleSheet("""
            QWidget#Sidebar {
                background-color: #0d1b2a;
            }

            QWidget#Sidebar QLabel {
                background-color: transparent;
            }

            QWidget#Sidebar QPushButton {
                background-color: transparent;
            }
        """)

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            24,
            16,
            20
        )

        layout.setSpacing(0)

        # =====================================================
        # LOGO AREA
        # =====================================================

        logo_layout = QHBoxLayout()

        logo_layout.setContentsMargins(
            8,
            0,
            0,
            0
        )

        logo_layout.setSpacing(10)

        logo_layout.setAlignment(
            Qt.AlignVCenter
        )

        # =====================================================
        # LOGO IMAGE
        # =====================================================

        logo_icon = QLabel()

        logo_icon.setFixedSize(
            44,
            44
        )

        logo_icon.setAlignment(
            Qt.AlignCenter
        )

        logo_icon.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)

        pixmap = QPixmap(
            "assets/logo2.png"
        )

        if not pixmap.isNull():

            pixmap = pixmap.scaled(
                44,
                44,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            logo_icon.setPixmap(
                pixmap
            )

        else:

            logo_icon.setText("A")

            logo_icon.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    color: #17324d;
                    border-radius: 10px;
                    font-size: 21px;
                    font-weight: bold;
                }
            """)

        logo_layout.addWidget(
            logo_icon
        )

        # =====================================================
        # LOGO TEXT
        # =====================================================

        logo_text_layout = QVBoxLayout()

        logo_text_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        logo_text_layout.setSpacing(
            1
        )

        logo_text_layout.setAlignment(
            Qt.AlignVCenter
        )

        # AutoTest
        logo = QLabel(
            "AutoTest"
        )

        logo.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: 700;
                background-color: transparent;
            }
        """)

        # WEB VALIDATOR
        subtitle = QLabel(
            "WEB VALIDATOR"
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #8ea3b8;
                font-size: 9px;
                font-weight: 400;
                background-color: transparent;
            }
        """)

        logo_text_layout.addWidget(
            logo
        )

        logo_text_layout.addWidget(
            subtitle
        )

        logo_layout.addLayout(
            logo_text_layout
        )

        layout.addLayout(
            logo_layout
        )

        # Khoảng cách logo → menu
        layout.addSpacing(
            32
        )

    # =====================================================
        # QUẢN LÝ
        # =====================================================

        self.add_section_title(
            layout,
            "QUẢN LÝ"
        )

        self.add_menu_item(
            layout,
            "⌂",
            "Tổng quan",
            "dashboard"
        )

        self.add_menu_item(
            layout,
            "▤",
            "Quản lý trang",
            "pages",
            "5"
        )

        self.add_menu_item(
            layout,
            "▣",
            "Danh mục xe",
            "vehicle_catalog"
        )

        # CRUD riêng - đặt ngay dưới Danh mục xe.
        # Không thay đổi trang Danh mục xe hiện tại.
        self.add_menu_item(
            layout,
            "C",
            "CRUD",
            "crud"
        )

        self.add_menu_item(
            layout,
            "▥",
            "Quản lý xe",
            "car_management"
        )

        self.add_menu_item(
            layout,
            "▨",
            "Quản lý đặt xe",
            "booking_management"
        )

        self.add_menu_item(
            layout,
            "▧",
            "Nhân sự",
            "staff_management"
        )

        # --- THÊM MỤC CẤU HÌNH TẠI ĐÂY ---
        self.add_menu_item(
            layout,
            "⚙",
            "Cấu hình",
            "config"
        )

        # ---------------------------------

        layout.addSpacing(
            22
        )

        # =====================================================
        # KIỂM THỬ
        # =====================================================

        self.add_section_title(
            layout,
            "KIỂM THỬ"
        )

        self.add_menu_item(
            layout,
            "▶",
            "Test Suite",
            "test_suite"
        )

        self.add_menu_item(
            layout,
            "⌄",
            "Dropdown List",
            "dropdown"
        )

        self.add_menu_item(
            layout,
            "T",
            "Label / Text",
            "label"
        )

        self.add_menu_item(
            layout,
            "▦",
            "Table",
            "table"
        )

        self.add_menu_item(
            layout,
            "◉",
            "Radio / Checkbox",
            "radio"
        )

        self.add_menu_item(
            layout,
            "▧",
            "Hình ảnh",
            "image"
        )

        self.add_menu_item(
            layout,
            "H",
            "Tiêu đề",
            "title"
        )

        self.add_menu_item(
            layout,
            "◇",
            "Giao diện",
            "ui"
        )

        self.add_menu_item(
            layout,
            "☷",
            "Menu website",
            "menu"
        )

        layout.addStretch()

        # =====================================================
        # MẶC ĐỊNH CHỌN TỔNG QUAN
        # =====================================================

        self.set_active_page(
            "dashboard"
        )

    # =========================================================
    # SECTION TITLE
    # =========================================================
    def add_section_title(
        self,
        layout,
        text
    ):

        label = QLabel(
            text
        )

        label.setFixedHeight(
            30
        )

        label.setAlignment(
            Qt.AlignLeft |
            Qt.AlignVCenter
        )

        label.setStyleSheet("""
            QLabel {
                color: #71869b;
                font-size: 10px;
                font-weight: 700;
                padding-left: 12px;
                background-color: transparent;
            }
        """)

        layout.addWidget(
            label
        )

    # =========================================================
    # MENU ITEM
    # =========================================================

    def add_menu_item(
        self,
        layout,
        icon,
        text,
        page_name,
        badge=None
        ):

        button = QPushButton()

        button.setFixedHeight(
            42
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        button_layout = QHBoxLayout(
            button
        )

        button_layout.setContentsMargins(
            12,
            0,
            10,
            0
        )

        button_layout.setSpacing(
            11
        )

        # =====================================================
        # ICON
        # =====================================================

        icon_label = QLabel(
            icon
        )

        icon_label.setFixedWidth(
            18
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setStyleSheet("""
            QLabel {
                color: #9db0c2;
                font-size: 15px;
                background-color: transparent;
            }
        """)

        button_layout.addWidget(
            icon_label
        )

        # =====================================================
        # TEXT
        # =====================================================

        text_label = QLabel(
            text
        )

        text_label.setStyleSheet("""
            QLabel {
                color: #d9e2ec;
                font-size: 13px;
                background-color: transparent;
            }
        """)

        button_layout.addWidget(
            text_label
        )

        # =====================================================
        # BADGE
        # =====================================================

        if badge is not None:

            badge_label = QLabel(
                str(badge)
            )

            badge_label.setFixedSize(
                20,
                20
            )

            badge_label.setAlignment(
                Qt.AlignCenter
            )

            badge_label.setStyleSheet("""
                QLabel {
                    background-color: #294664;
                    color: #dbe8f5;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """)

            button_layout.addStretch()

            button_layout.addWidget(
                badge_label
            )

        else:

            button_layout.addStretch()

        # =====================================================
        # BUTTON STYLE
        # =====================================================

        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #172d45;
            }

            QPushButton:pressed {
                background-color: #1d3957;
            }
        """)

        button.setProperty(
            "page_name",
            page_name
        )

        button.clicked.connect(
            lambda checked=False,
            name=page_name:
            self.handle_page_change(name)
        )

        layout.addWidget(
            button
        )

    # =========================================================
    # PAGE CHANGE
    # =========================================================

    def handle_page_change(
        self,
        page_name
    ):

        self.set_active_page(
            page_name
        )

        self.page_changed.emit(
            page_name
        )

    # =========================================================
    # ACTIVE PAGE
    # =========================================================

    def set_active_page(
        self,
        page_name
    ):

        buttons = self.findChildren(
            QPushButton
        )

        for button in buttons:

            current_page = button.property(
                "page_name"
            )

            if current_page == page_name:

                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2563d9;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                    }

                    QPushButton:hover {
                        background-color: #2d6fe8;
                    }

                    QPushButton:pressed {
                        background-color: #1f56bd;
                    }
                """)
  
            else:

                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                    }

                    QPushButton:hover {
                        background-color: #172d45;
                    }

                    QPushButton:pressed {
                        background-color: #1d3957;
                    }
                """)
