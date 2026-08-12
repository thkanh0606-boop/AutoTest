from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from PySide6.QtCore import Qt


class PageModal(QDialog):

    def __init__(
        self,
        parent=None,
        page=None,
    ):
        super().__init__(parent)

        self.page = page
        self.is_edit = page is not None

        self.result_name = ""
        self.result_path = ""

        self.setWindowTitle(
            "Sửa trang" if self.is_edit else "Thêm trang mới"
        )

        self.setFixedSize(460, 330)

        self.setup_ui()

        if self.is_edit:
            self.load_page_data()

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }

            QLabel {
                background: transparent;
            }

            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d6deea;
                border-radius: 7px;
                padding: 0 12px;
                color: #162238;
                font-size: 12px;
            }

            QLineEdit:focus {
                border: 1px solid #2468df;
            }

            QPushButton {
                border-radius: 7px;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        main_layout.setSpacing(0)

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "Sửa trang" if self.is_edit else "Thêm trang mới"
        )

        title.setStyleSheet("""
            QLabel {
                color: #101828;
                font-size: 21px;
                font-weight: 600;
            }
        """)

        main_layout.addWidget(title)

        main_layout.addSpacing(6)

        # =================================================
        # DESCRIPTION
        # =================================================

        description = QLabel(
            "Cập nhật thông tin trang cần kiểm thử."
            if self.is_edit
            else "Nhập thông tin trang cần kiểm thử."
        )

        description.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
            }
        """)

        main_layout.addWidget(description)

        main_layout.addSpacing(22)

        # =================================================
        # PAGE NAME
        # =================================================

        name_label = QLabel("Tên trang")

        name_label.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        main_layout.addWidget(name_label)

        main_layout.addSpacing(7)

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Ví dụ: Dashboard"
        )

        self.name_input.setFixedHeight(38)

        main_layout.addWidget(
            self.name_input
        )

        main_layout.addSpacing(16)

        # =================================================
        # PATH
        # =================================================

        path_label = QLabel("URL / Route")

        path_label.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        main_layout.addWidget(path_label)

        main_layout.addSpacing(7)

        self.path_input = QLineEdit()

        self.path_input.setPlaceholderText(
            "Ví dụ: /dashboard"
        )

        self.path_input.setFixedHeight(38)

        main_layout.addWidget(
            self.path_input
        )

        main_layout.addStretch()

        # =================================================
        # BUTTONS
        # =================================================

        button_layout = QHBoxLayout()

        button_layout.setSpacing(8)

        button_layout.addStretch()

        # -------------------------------------------------
        # CANCEL
        # -------------------------------------------------

        self.cancel_button = QPushButton("Hủy")

        self.cancel_button.setFixedSize(
            58,
            36,
        )

        self.cancel_button.setCursor(
            Qt.PointingHandCursor
        )

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #d6deea;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)

        self.cancel_button.clicked.connect(
            self.reject
        )

        button_layout.addWidget(
            self.cancel_button
        )

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        self.save_button = QPushButton("Lưu")

        self.save_button.setFixedSize(
            58,
            36,
        )

        self.save_button.setCursor(
            Qt.PointingHandCursor
        )

        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2468df;
                color: white;
                border: none;
            }

            QPushButton:hover {
                background-color: #1d5bc7;
            }

            QPushButton:pressed {
                background-color: #164da8;
            }
        """)

        self.save_button.clicked.connect(
            self.save
        )

        button_layout.addWidget(
            self.save_button
        )

        main_layout.addLayout(
            button_layout
        )

    # =====================================================
    # LOAD PAGE
    # =====================================================

    def load_page_data(self):

        self.name_input.setText(
            str(self.page["name"])
        )

        self.path_input.setText(
            str(self.page["path"])
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        name = self.name_input.text().strip()
        path = self.path_input.text().strip()

        # -------------------------------------------------
        # VALIDATE NAME
        # -------------------------------------------------

        if not name:

            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng nhập tên trang.",
            )

            self.name_input.setFocus()

            return

        # -------------------------------------------------
        # VALIDATE PATH
        # -------------------------------------------------

        if not path:

            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng nhập URL / Route.",
            )

            self.path_input.setFocus()

            return

        # -------------------------------------------------
        # NORMALIZE PATH
        # -------------------------------------------------

        if not path.startswith("/"):
            path = "/" + path

        self.result_name = name
        self.result_path = path

        self.accept()

    # =====================================================
    # GET DATA
    # =====================================================

    def get_data(self):

        return {
            "name": self.result_name,
            "path": self.result_path,
        }