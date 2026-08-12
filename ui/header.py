from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSizePolicy
)

from PySide6.QtCore import Qt


class Header(QWidget):

    def __init__(self):
        super().__init__()

        # =====================================================
        # HEADER
        # =====================================================

        self.setFixedHeight(72)
        self.setObjectName("Header")

        self.setStyleSheet("""
            QWidget#Header {
                background-color: #ffffff;
                border-bottom: 1px solid #e5e7eb;
            }

            QLabel {
                background-color: transparent;
            }
        """)

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            36,
            10,
            36,
            10
        )

        main_layout.setSpacing(18)

        # =====================================================
        # WEBSITE
        # =====================================================

        website_layout = QVBoxLayout()

        website_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        website_layout.setSpacing(3)

        website_label = QLabel("WEBSITE")

        website_label.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        self.website_combo = QComboBox()

        self.website_combo.addItems([
            "PLT Fleet Console",
            "Courses PLT"
        ])

        self.website_combo.setFixedWidth(135)
        self.website_combo.setFixedHeight(34)

        self.website_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: none;
                color: #162238;
                font-size: 13px;
                font-weight: 600;
                padding-left: 2px;
                padding-right: 22px;
            }

            QComboBox::drop-down {
                border: none;
                width: 22px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #162238;
                margin-right: 4px;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e1e5eb;
                selection-background-color: #eef4ff;
                selection-color: #162238;
            }
        """)

        website_layout.addWidget(website_label)
        website_layout.addWidget(self.website_combo)

        main_layout.addLayout(website_layout)

        # =====================================================
        # SEPARATOR
        # =====================================================

        separator = QLabel("/")

        separator.setAlignment(Qt.AlignCenter)

        separator.setStyleSheet("""
            QLabel {
                color: #b6c0cc;
                font-size: 14px;
                background: transparent;
            }
        """)

        main_layout.addWidget(separator)

        # =====================================================
        # PAGE SELECTOR
        # =====================================================

        page_layout = QVBoxLayout()

        page_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        page_layout.setSpacing(3)

        page_label = QLabel("TRANG ĐANG KIỂM THỬ")

        page_label.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        self.page_combo = QComboBox()

        self.page_combo.addItems([
            "Trang tổng quan",
            "Trang đăng nhập"
        ])

        self.page_combo.setFixedWidth(210)
        self.page_combo.setFixedHeight(34)

        self.page_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: none;
                color: #162238;
                font-size: 13px;
                font-weight: 600;
                padding-left: 2px;
                padding-right: 22px;
            }

            QComboBox::drop-down {
                border: none;
                width: 22px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #162238;
                margin-right: 4px;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e1e5eb;
                selection-background-color: #eef4ff;
                selection-color: #162238;
            }
        """)

        page_layout.addWidget(page_label)
        page_layout.addWidget(self.page_combo)

        main_layout.addLayout(page_layout)

        # =====================================================
        # URL
        # =====================================================

        url_layout = QVBoxLayout()

        url_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        url_layout.setSpacing(3)

        url_label = QLabel("URL")

        url_label.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        self.url_input = QLineEdit()

        self.url_input.setText(
            "https://courses.plt.pro.vn/dashboard"
        )

        self.url_input.setReadOnly(True)

        self.url_input.setFixedHeight(34)

        self.url_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc;
                border: 1px solid #dfe5ec;
                border-radius: 8px;
                color: #64748b;
                padding-left: 13px;
                padding-right: 13px;
                font-size: 12px;
            }
        """)

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # URL chiếm phần không gian còn lại
        main_layout.addLayout(
            url_layout,
            1
        )

        # =====================================================
        # CONNECTION STATUS
        # =====================================================

        status_layout = QVBoxLayout()

        status_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        status_layout.setSpacing(3)

        status_label = QLabel("TRẠNG THÁI")

        status_label.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        self.status_button = QPushButton(
            "●  Đã kết nối"
        )

        self.status_button.setEnabled(False)

        self.status_button.setFixedHeight(34)
        self.status_button.setFixedWidth(94)

        self.status_button.setStyleSheet("""
            QPushButton {
                background-color: #ecfdf5;
                border: 1px solid #b7ead4;
                border-radius: 8px;
                color: #16845b;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_button)

        main_layout.addLayout(status_layout)
