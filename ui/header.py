from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


COMBO_STYLE = """
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
    color: #162238;
    border: 1px solid #e1e5eb;
    selection-background-color: #eef4ff;
    selection-color: #162238;
    outline: 0;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
}
"""


class Header(QWidget):
    context_changed = Signal(str, str, str, str, str)
    # website_id, page_id, website_name, page_name, url

    def __init__(self, store=None):
        super().__init__()
        self.store = store

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

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(36, 10, 36, 10)
        main_layout.setSpacing(18)

        # WEBSITE
        website_layout = self._field_layout("WEBSITE")

        self.website_combo = QComboBox()
        self.website_combo.setFixedWidth(160)
        self.website_combo.setFixedHeight(34)
        self.website_combo.setStyleSheet(COMBO_STYLE)

        website_layout.addWidget(self.website_combo)
        main_layout.addLayout(website_layout)

        # Separator
        separator = QLabel("/")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet(
            "color: #b6c0cc; font-size: 14px;"
        )
        main_layout.addWidget(separator)

        # PAGE
        page_layout = self._field_layout(
            "TRANG ĐANG KIỂM THỬ"
        )

        self.page_combo = QComboBox()
        self.page_combo.setFixedWidth(220)
        self.page_combo.setFixedHeight(34)
        self.page_combo.setStyleSheet(COMBO_STYLE)

        page_layout.addWidget(self.page_combo)
        main_layout.addLayout(page_layout)

        # URL
        url_layout = self._field_layout("URL")

        self.url_input = QLineEdit()
        self.url_input.setReadOnly(True)
        self.url_input.setFixedHeight(34)
        self.url_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
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

        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout, 1)

        # STATUS
        status_layout = self._field_layout(
            "TRẠNG THÁI"
        )

        self.status_button = QPushButton(
            "●  Đã cấu hình"
        )
        self.status_button.setEnabled(False)
        self.status_button.setFixedHeight(34)
        self.status_button.setFixedWidth(105)

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

        status_layout.addWidget(
            self.status_button
        )
        main_layout.addLayout(
            status_layout
        )

        # Events
        self.website_combo.currentIndexChanged.connect(
            self._load_pages
        )

        self.page_combo.currentIndexChanged.connect(
            self._emit_context
        )

        self.reload_from_store()

    @staticmethod
    def _field_layout(label_text):
        layout = QVBoxLayout()
        layout.setContentsMargins(
            0, 0, 0, 0
        )
        layout.setSpacing(3)

        label = QLabel(label_text)

        label.setStyleSheet("""
            QLabel {
                color: #8091a5;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        layout.addWidget(label)

        return layout

    def reload_from_store(self):
        self.website_combo.blockSignals(
            True
        )

        self.website_combo.clear()

        if self.store:
            self.store.reload()

            for website in (
                self.store.websites()
            ):
                self.website_combo.addItem(
                    website.get("name", ""),
                    website.get("id"),
                )

        else:
            self.website_combo.addItems([
                "PLT Fleet Console",
                "Courses PLT",
            ])

        self.website_combo.blockSignals(
            False
        )

        self._load_pages()

    def _load_pages(self):
        self.page_combo.blockSignals(True)
        self.page_combo.clear()

        if self.store:
            website = (
                self.store.find_website(
                    self.website_combo.currentData()
                )
            )

            if website:
                for page in website.get(
                    "pages", []
                ):
                    self.page_combo.addItem(
                        page.get("name", ""),
                        page.get("id"),
                    )

        else:
            self.page_combo.addItems([
                "Trang tổng quan",
                "Trang đăng nhập",
                "Danh mục xe",
            ])

        self.page_combo.blockSignals(False)

        self._emit_context()

    def _emit_context(self):
        if self.store:
            website_id = (
                self.website_combo.currentData()
            )

            page_id = (
                self.page_combo.currentData()
            )

            website_name = (
                self.website_combo.currentText()
            )

            page_name = (
                self.page_combo.currentText()
            )

            url = self.store.page_url(
                website_id,
                page_id,
            )

        else:
            website_id = (
                self.website_combo.currentText()
            )

            page_id = (
                self.page_combo.currentText()
            )

            website_name = website_id
            page_name = page_id

            url = self.url_input.text()

        self.url_input.setText(
            url or ""
        )

        self.context_changed.emit(
            website_id or "",
            page_id or "",
            website_name,
            page_name,
            url or "",
        )

    def select_context(
        self,
        website_id,
        page_id,
    ):
        """
        Chọn Website/Page bằng ID.

        Dùng khi mở module chuyên biệt như
        Danh mục xe để Header hiển thị đúng
        trang đang kiểm thử.
        """

        if self.store:
            self.store.reload()

        website_index = (
            self.website_combo.findData(
                website_id
            )
        )

        if website_index < 0:
            self.reload_from_store()

            website_index = (
                self.website_combo.findData(
                    website_id
                )
            )

        if website_index >= 0:
            self.website_combo.setCurrentIndex(
                website_index
            )

        page_index = (
            self.page_combo.findData(
                page_id
            )
        )

        if page_index >= 0:
            self.page_combo.setCurrentIndex(
                page_index
            )
        else:
            self._emit_context()

    def current_context(self):
        return (
            self.website_combo.currentData()
            or "",
            self.page_combo.currentData()
            or "",
            self.website_combo.currentText(),
            self.page_combo.currentText(),
            self.url_input.text(),
        )