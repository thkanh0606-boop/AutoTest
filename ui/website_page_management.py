from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
    QDialog,
)

from services.sqlite_service import SQLiteService
from ui.page_modal import PageModal


class WebsitePageManagement(QWidget):
    """
    Màn hình quản lý Website / Page.

    Chức năng:
    - Hiển thị danh sách Page từ SQLite
    - Tìm kiếm Page
    - Hiển thị thống kê
    - Thêm Page
    - Sửa Page
    - Xóa Page
    - Xác nhận trước khi xóa
    - Mở màn hình kiểm thử của Page
    """

    def __init__(self):
        super().__init__()

        self.service = SQLiteService()

        self.websites = []
        self.pages = []

        # Website hiện tại
        self.current_website_id = None
        self.current_website_name = ""

        self.setup_ui()
        self.load_data()

    # =====================================================
    # SAFE VALUE HELPER
    # =====================================================

    def _get_value(self, row, key, default=""):
        """
        Lấy giá trị từ sqlite3.Row hoặc dict.

        sqlite3.Row không có .get()
        nên không được dùng row.get(...).
        """

        if row is None:
            return default

        try:
            return row[key]
        except (KeyError, IndexError, TypeError):
            return default

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fb;
                font-family: "Segoe UI";
            }

            QLabel {
                background: transparent;
            }
        """)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            38,
            30,
            38,
            30
        )

        main_layout.setSpacing(0)

        # =================================================
        # TOP AREA
        # =================================================

        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        # WORKSPACE

        workspace_label = QLabel(
            "WORKSPACE"
        )

        workspace_label.setStyleSheet("""
            QLabel {
                color: #1769ff;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
            }
        """)

        title_layout.addWidget(
            workspace_label
        )

        # TITLE

        title = QLabel(
            "Quản lý trang"
        )

        title.setStyleSheet("""
            QLabel {
                color: #101828;
                font-size: 29px;
                font-weight: 500;
            }
        """)

        title_layout.addWidget(
            title
        )

        # DESCRIPTION

        self.description_label = QLabel(
            "Mỗi trang có URL, quyền truy cập, element và bộ test riêng."
        )

        self.description_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 13px;
            }
        """)

        title_layout.addWidget(
            self.description_label
        )

        top_layout.addLayout(
            title_layout
        )

        top_layout.addStretch()

        # ADD PAGE

        self.add_page_button = QPushButton(
            "+  Thêm trang mới"
        )

        self.add_page_button.setFixedSize(
            138,
            40
        )

        self.add_page_button.setCursor(
            Qt.PointingHandCursor
        )

        self.add_page_button.setStyleSheet("""
            QPushButton {
                background-color: #2468df;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d5bc7;
            }

            QPushButton:pressed {
                background-color: #164da8;
            }
        """)

        self.add_page_button.clicked.connect(
            self.add_page
        )

        top_layout.addWidget(
            self.add_page_button
        )

        main_layout.addLayout(
            top_layout
        )

        main_layout.addSpacing(28)

        # =================================================
        # STATISTICS
        # =================================================

        stats_layout = QHBoxLayout()

        stats_layout.setSpacing(14)

        self.total_pages_card = self.create_stat_card(
            "TỔNG SỐ TRANG",
            "00"
        )

        self.configured_card = self.create_stat_card(
            "ĐÃ CẤU HÌNH",
            "00"
        )

        self.test_cases_card = self.create_stat_card(
            "TỔNG TEST CASE",
            "00"
        )

        self.elements_card = self.create_stat_card(
            "ELEMENT ĐÃ LƯU",
            "00"
        )

        stats_layout.addWidget(
            self.total_pages_card
        )

        stats_layout.addWidget(
            self.configured_card
        )

        stats_layout.addWidget(
            self.test_cases_card
        )

        stats_layout.addWidget(
            self.elements_card
        )

        main_layout.addLayout(
            stats_layout
        )

        main_layout.addSpacing(20)

        # =================================================
        # TABLE CARD
        # =================================================

        table_card = QFrame()

        table_card.setObjectName(
            "tableCard"
        )

        table_card.setStyleSheet("""
            QFrame#tableCard {
                background-color: #ffffff;
                border: 1px solid #e1e7ef;
                border-radius: 11px;
            }
        """)

        table_layout = QVBoxLayout(
            table_card
        )

        table_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        table_layout.setSpacing(0)

        # =================================================
        # TABLE HEADER
        # =================================================

        table_header = QHBoxLayout()

        table_header.setContentsMargins(
            18,
            14,
            18,
            12
        )

        # TABLE TITLE

        self.table_title = QLabel(
            "Danh sách trang"
        )

        self.table_title.setStyleSheet("""
            QLabel {
                color: #101828;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        table_header.addWidget(
            self.table_title
        )

        table_header.addStretch()

        # SEARCH

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "⌕  Tìm trang..."
        )

        self.search_input.setFixedSize(
            180,
            38
        )

        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d6deea;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 8px;
                color: #162238;
                font-size: 12px;
            }

            QLineEdit:hover {
                border: 1px solid #b8c6d8;
            }

            QLineEdit:focus {
                border: 1px solid #7aa7e8;
            }
        """)

        self.search_input.textChanged.connect(
            self.filter_pages
        )

        table_header.addWidget(
            self.search_input
        )

        table_header.addSpacing(8)

        # FILTER

        self.filter_button = QPushButton(
            "⇅  Lọc"
        )

        self.filter_button.setFixedSize(
            72,
            38
        )

        self.filter_button.setCursor(
            Qt.PointingHandCursor
        )

        self.filter_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d6deea;
                border-radius: 8px;
                color: #64748b;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #c6d1df;
            }

            QPushButton:pressed {
                background-color: #f1f4f8;
            }
        """)

        table_header.addWidget(
            self.filter_button
        )

        table_layout.addLayout(
            table_header
        )

        # =================================================
        # TABLE
        # =================================================

        self.page_table = QTableWidget()

        self.page_table.setColumnCount(
            7
        )

        self.page_table.setHorizontalHeaderLabels([
            "TRANG",
            "URL / ROUTE",
            "PROFILE",
            "ELEMENT",
            "TEST CASE",
            "TRẠNG THÁI",
            "THAO TÁC"
        ])

        self.page_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.page_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.page_table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.page_table.verticalHeader().setVisible(
            False
        )

        self.page_table.setShowGrid(
            False
        )

        self.page_table.setWordWrap(
            False
        )

        self.page_table.setTextElideMode(
            Qt.ElideNone
        )

        self.page_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.page_table.setVerticalScrollMode(
            QTableWidget.ScrollPerPixel
        )

        self.page_table.setFocusPolicy(
            Qt.NoFocus
        )

        self.page_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: none;
                color: #162238;
                font-size: 11px;
                outline: none;
                selection-background-color: #f5f8fc;
            }

            QTableWidget::item {
                border-bottom: 1px solid #edf1f5;
                padding: 6px 8px;
            }

            QTableWidget::item:selected {
                background-color: #f5f8fc;
                color: #162238;
            }

            QHeaderView::section {
                background-color: #ffffff;
                color: #7b8da3;
                border: none;
                border-top: 1px solid #edf1f5;
                border-bottom: 1px solid #dfe6ee;
                padding: 11px 8px;
                font-size: 9px;
                font-weight: 700;
            }
        """)

        # =================================================
        # COLUMN WIDTH
        # =================================================

        header = self.page_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            1,
            145
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            2,
            90
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            3,
            78
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            4,
            90
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            5,
            115
        )

        header.setSectionResizeMode(
            6,
            QHeaderView.Fixed
        )

        self.page_table.setColumnWidth(
            6,
            190
        )

        table_layout.addWidget(
            self.page_table
        )

        main_layout.addWidget(
            table_card,
            1
        )

    # =====================================================
    # STAT CARD
    # =====================================================

    def create_stat_card(
        self,
        title,
        value
    ):

        card = QFrame()

        card.setObjectName(
            "statCard"
        )

        card.setMinimumHeight(
            94
        )

        card.setStyleSheet("""
            QFrame#statCard {
                background-color: #ffffff;
                border: 1px solid #e1e7ef;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            15,
            18,
            14
        )

        layout.setSpacing(7)

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                color: #7b8da3;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet("""
            QLabel {
                color: #101828;
                font-size: 25px;
                font-weight: 500;
            }
        """)

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        card.value_label = value_label

        return card

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):

        try:

            self.websites = (
                self.service.get_websites()
            )

            if not self.websites:

                self.current_website_id = None
                self.current_website_name = ""
                self.pages = []

            else:

                website = self.websites[0]

                self.current_website_id = self._get_value(
                    website,
                    "id",
                    None
                )

                self.current_website_name = str(
                    self._get_value(
                        website,
                        "name",
                        ""
                    )
                )

                self.pages = (
                    self.service.get_pages(
                        self.current_website_id
                    )
                )

        except Exception as e:

            print(
                "Load data error:",
                e
            )

            self.websites = []
            self.pages = []

            self.current_website_id = None
            self.current_website_name = ""

        # UPDATE TITLE

        if self.current_website_name:

            self.table_title.setText(
                f"Danh sách trang - "
                f"{self.current_website_name}"
            )

        else:

            self.table_title.setText(
                "Danh sách trang"
            )

        self.update_statistics()

        self.display_pages(
            self.pages
        )

    # =====================================================
    # UPDATE STATISTICS
    # =====================================================

    def update_statistics(self):

        total_pages = len(
            self.pages
        )

        configured = total_pages

        test_cases = 0

        elements = 0

        self.total_pages_card.value_label.setText(
            f"{total_pages:02d}"
        )

        self.configured_card.value_label.setText(
            f"{configured:02d}"
        )

        self.test_cases_card.value_label.setText(
            f"{test_cases:02d}"
        )

        self.elements_card.value_label.setText(
            f"{elements:02d}"
        )

    # =====================================================
    # DISPLAY PAGES
    # =====================================================

    def display_pages(
        self,
        pages
    ):

        self.page_table.clearContents()

        self.page_table.setRowCount(
            0
        )

        # EMPTY STATE

        if not pages:

            self.page_table.setRowCount(
                1
            )

            empty_item = QTableWidgetItem(
                "Chưa có trang nào được cấu hình."
            )

            empty_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.page_table.setItem(
                0,
                0,
                empty_item
            )

            self.page_table.setSpan(
                0,
                0,
                1,
                7
            )

            self.page_table.setRowHeight(
                0,
                70
            )

            return

        # DISPLAY

        for page in pages:

            row = self.page_table.rowCount()

            self.page_table.insertRow(
                row
            )

            self.page_table.setRowHeight(
                row,
                58
            )

            # =============================================
            # PAGE DATA
            # =============================================

            page_id = self._get_value(
                page,
                "id",
                None
            )

            page_name = str(
                self._get_value(
                    page,
                    "name",
                    ""
                )
            )

            path = str(
                self._get_value(
                    page,
                    "path",
                    ""
                )
            )

            # =============================================
            # PAGE NAME
            # =============================================

            name_widget = (
                self.create_page_name_widget(
                    page_name
                )
            )

            self.page_table.setCellWidget(
                row,
                0,
                name_widget
            )

            # =============================================
            # PATH
            # =============================================

            path_widget = (
                self.create_path_badge(
                    path
                )
            )

            self.page_table.setCellWidget(
                row,
                1,
                path_widget
            )

            # =============================================
            # PROFILE
            # =============================================

            profile = self.get_profile(
                page_name
            )

            profile_widget = (
                self.create_profile_badge(
                    profile
                )
            )

            self.page_table.setCellWidget(
                row,
                2,
                profile_widget
            )

            # =============================================
            # ELEMENT
            # =============================================

            element_item = QTableWidgetItem(
                "0"
            )

            element_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.page_table.setItem(
                row,
                3,
                element_item
            )

            # =============================================
            # TEST CASE
            # =============================================

            test_item = QTableWidgetItem(
                "0"
            )

            test_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.page_table.setItem(
                row,
                4,
                test_item
            )

            # =============================================
            # STATUS
            # =============================================

            status_widget = (
                self.create_status_widget()
            )

            self.page_table.setCellWidget(
                row,
                5,
                status_widget
            )

            # =============================================
            # ACTION
            # =============================================

            action_widget = (
                self.create_action_widget(
                    page_id
                )
            )

            self.page_table.setCellWidget(
                row,
                6,
                action_widget
            )

    # =====================================================
    # PAGE NAME WIDGET
    # =====================================================

    def create_page_name_widget(
        self,
        page_name
    ):

        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            8,
            0,
            4,
            0
        )

        layout.setSpacing(
            10
        )

        icon = QLabel(
            self.get_page_icon(
                page_name
            )
        )

        icon.setFixedSize(
            30,
            30
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        icon.setStyleSheet("""
            QLabel {
                background-color: #edf4ff;
                color: #1769ff;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        layout.addWidget(
            icon
        )

        name_label = QLabel(
            page_name
        )

        name_label.setStyleSheet("""
            QLabel {
                color: #172033;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        layout.addWidget(
            name_label
        )

        layout.addStretch()

        return container

    # =====================================================
    # PAGE ICON
    # =====================================================

    def get_page_icon(
        self,
        page_name
    ):

        name = str(
            page_name
        ).lower()

        if "dashboard" in name:
            return "⌂"

        if "booking" in name:
            return "≡"

        if "xe" in name:
            return "▣"

        if "danh mục" in name:
            return "▦"

        if "tài chính" in name:
            return "$"

        if "người dùng" in name:
            return "♙"

        if (
            "login" in name
            or "đăng nhập" in name
        ):
            return "↪"

        return "□"

    # =====================================================
    # PATH BADGE
    # =====================================================

    def create_path_badge(
        self,
        path
    ):

        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            8,
            0,
            8,
            0
        )

        label = QLabel(
            path
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setMinimumWidth(
            70
        )

        label.setStyleSheet("""
            QLabel {
                background-color: #f1f4f8;
                color: #718096;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 10px;
            }
        """)

        layout.addWidget(
            label,
            0,
            Qt.AlignCenter
        )

        return container

    # =====================================================
    # PROFILE BADGE
    # =====================================================

    def create_profile_badge(
        self,
        profile
    ):

        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        badge = QLabel(
            profile
        )

        badge.setAlignment(
            Qt.AlignCenter
        )

        badge.setFixedHeight(
            23
        )

        badge.setMinimumWidth(
            58
        )

        badge.setStyleSheet("""
            QLabel {
                background-color: #f0e9ff;
                color: #7546d8;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 9px;
                font-weight: 700;
            }
        """)

        layout.addWidget(
            badge,
            0,
            Qt.AlignCenter
        )

        return container

    # =====================================================
    # STATUS WIDGET
    # =====================================================

    def create_status_widget(
        self
    ):

        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        status = QLabel(
            "● Sẵn sàng"
        )

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet("""
            QLabel {
                color: #159447;
                font-size: 10px;
                font-weight: 600;
            }
        """)

        layout.addWidget(
            status,
            0,
            Qt.AlignCenter
        )

        return container

    # =====================================================
    # ACTION WIDGET
    # =====================================================

    def create_action_widget(
        self,
        page_id
    ):

        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            2,
            0,
            2,
            0
        )

        layout.setSpacing(
            4
        )

        # -------------------------------------------------
        # EDIT
        # -------------------------------------------------

        edit_button = QPushButton(
            "Sửa"
        )

        edit_button.setFixedSize(
            42,
            30
        )

        edit_button.setCursor(
            Qt.PointingHandCursor
        )

        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #eef4ff;
                border: 1px solid #d8e5ff;
                border-radius: 6px;
                color: #1769ff;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #e1ecff;
                border-color: #bfd3f8;
            }

            QPushButton:pressed {
                background-color: #d5e5ff;
            }
        """)

        edit_button.clicked.connect(
            lambda checked=False, pid=page_id:
            self.edit_page(pid)
        )

        layout.addWidget(
            edit_button
        )

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        delete_button = QPushButton(
            "Xóa"
        )

        delete_button.setFixedSize(
            42,
            30
        )

        delete_button.setCursor(
            Qt.PointingHandCursor
        )

        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #fff1f2;
                border: 1px solid #ffd5d9;
                border-radius: 6px;
                color: #dc3545;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #ffe4e7;
                border-color: #ffbfc6;
            }

            QPushButton:pressed {
                background-color: #ffd7dc;
            }
        """)

        delete_button.clicked.connect(
            lambda checked=False, pid=page_id:
            self.delete_page(pid)
        )

        layout.addWidget(
            delete_button
        )

        # -------------------------------------------------
        # TEST
        # -------------------------------------------------

        test_button = QPushButton(
            "Mở kiểm thử ›"
        )

        test_button.setFixedSize(
            92,
            30
        )

        test_button.setCursor(
            Qt.PointingHandCursor
        )

        test_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #1769ff;
                font-size: 10px;
                font-weight: 600;
                padding: 0px;
            }

            QPushButton:hover {
                color: #0d4fc4;
                background-color: #f2f6ff;
                border-radius: 5px;
            }

            QPushButton:pressed {
                background-color: #e8f0ff;
            }
        """)

        test_button.clicked.connect(
            lambda checked=False, pid=page_id:
            self.open_test_page(pid)
        )

        layout.addWidget(
            test_button
        )

        return container

    # =====================================================
    # PROFILE
    # =====================================================

    def get_profile(
        self,
        page_name
    ):

        name = str(
            page_name
        ).lower()

        if (
            "đăng nhập" in name
            or "login" in name
        ):
            return "GUEST"

        return "ADMIN"

    # =====================================================
    # SEARCH
    # =====================================================

    def filter_pages(
        self,
        text
    ):

        text = str(
            text
        ).lower().strip()

        if not text:

            filtered = self.pages

        else:

            filtered = []

            for page in self.pages:

                name = str(
                    self._get_value(
                        page,
                        "name",
                        ""
                    )
                ).lower()

                path = str(
                    self._get_value(
                        page,
                        "path",
                        ""
                    )
                ).lower()

                if (
                    text in name
                    or text in path
                ):

                    filtered.append(
                        page
                    )

        self.display_pages(
            filtered
        )

    # =====================================================
    # CHECK DUPLICATE
    # =====================================================

    def is_duplicate_page(
        self,
        name,
        path,
        exclude_page_id=None
    ):

        name_lower = name.strip().lower()
        path_lower = path.strip().lower()

        for page in self.pages:

            page_id = self._get_value(
                page,
                "id",
                None
            )

            # Khi sửa thì bỏ qua Page hiện tại

            if (
                exclude_page_id is not None
                and page_id == exclude_page_id
            ):
                continue

            existing_name = str(
                self._get_value(
                    page,
                    "name",
                    ""
                )
            ).strip().lower()

            existing_path = str(
                self._get_value(
                    page,
                    "path",
                    ""
                )
            ).strip().lower()

            if existing_name == name_lower:
                return "name"

            if existing_path == path_lower:
                return "path"

        return None

    # =====================================================
    # ADD PAGE
    # =====================================================

    def add_page(
        self
    ):

        if self.current_website_id is None:

            QMessageBox.warning(
                self,
                "Chưa có Website",
                "Chưa có Website nào trong database."
            )

            return

        try:

            dialog = PageModal(
                website_id=self.current_website_id,
                parent=self
            )

            result = dialog.exec()

            if result != QDialog.Accepted:
                return

            data = dialog.get_data()

            name = str(
                data["name"]
            ).strip()

            path = str(
                data["path"]
            ).strip()

            # DUPLICATE

            duplicate = self.is_duplicate_page(
                name,
                path
            )

            if duplicate == "name":

                QMessageBox.warning(
                    self,
                    "Page đã tồn tại",
                    (
                        f"Page '{name}' đã tồn tại "
                        "trong Website này."
                    )
                )

                return

            if duplicate == "path":

                QMessageBox.warning(
                    self,
                    "Route đã tồn tại",
                    (
                        f"Route '{path}' đã tồn tại "
                        "trong Website này."
                    )
                )

                return

            # INSERT

            new_page_id = self.service.add_page(
                self.current_website_id,
                name,
                path
            )

            print(
                "Page created:",
                new_page_id
            )

            self.load_data()

            QMessageBox.information(
                self,
                "Thành công",
                (
                    f"Đã thêm trang '{name}'.\n\n"
                    f"Route: {path}\n"
                    f"Page ID: {new_page_id}"
                )
            )

        except Exception as e:

            print(
                "Add page error:",
                e
            )

            QMessageBox.critical(
                self,
                "Lỗi",
                (
                    "Không thể thêm Page.\n\n"
                    f"{e}"
                )
            )

    # =====================================================
    # EDIT PAGE
    # =====================================================

    def edit_page(
        self,
        page_id
    ):

        if page_id is None:
            return

        try:

            page = self.service.get_page(
                page_id
            )

            if not page:

                QMessageBox.warning(
                    self,
                    "Không tìm thấy Page",
                    (
                        f"Page ID {page_id} "
                        "không tồn tại."
                    )
                )

                return

            old_name = str(
                self._get_value(
                    page,
                    "name",
                    ""
                )
            )

            old_path = str(
                self._get_value(
                    page,
                    "path",
                    ""
                )
            )

            # Mở modal sửa

            dialog = PageModal(
                page=page,
                parent=self
            )

            result = dialog.exec()

            if result != QDialog.Accepted:
                return

            data = dialog.get_data()

            name = str(
                data["name"]
            ).strip()

            path = str(
                data["path"]
            ).strip()

            # DUPLICATE

            duplicate = self.is_duplicate_page(
                name,
                path,
                exclude_page_id=page_id
            )

            if duplicate == "name":

                QMessageBox.warning(
                    self,
                    "Page đã tồn tại",
                    (
                        f"Page '{name}' đã tồn tại "
                        "trong Website này."
                    )
                )

                return

            if duplicate == "path":

                QMessageBox.warning(
                    self,
                    "Route đã tồn tại",
                    (
                        f"Route '{path}' đã tồn tại "
                        "trong Website này."
                    )
                )

                return

            # UPDATE

            self.service.update_page(
                page_id,
                name,
                path
            )

            print(
                "Page updated:",
                page_id
            )

            self.load_data()

            QMessageBox.information(
                self,
                "Cập nhật thành công",
                (
                    f"Đã cập nhật Page.\n\n"
                    f"Tên cũ: {old_name}\n"
                    f"Route cũ: {old_path}\n\n"
                    f"Tên mới: {name}\n"
                    f"Route mới: {path}"
                )
            )

        except Exception as e:

            print(
                "Edit page error:",
                e
            )

            QMessageBox.critical(
                self,
                "Lỗi",
                (
                    "Không thể sửa Page.\n\n"
                    f"{e}"
                )
            )

    # =====================================================
    # DELETE PAGE
    # =====================================================

    def delete_page(
        self,
        page_id
    ):

        if page_id is None:
            return

        try:

            # GET PAGE

            page = self.service.get_page(
                page_id
            )

            if not page:

                QMessageBox.warning(
                    self,
                    "Không tìm thấy Page",
                    (
                        f"Page ID {page_id} "
                        "không tồn tại."
                    )
                )

                return

            page_name = str(
                self._get_value(
                    page,
                    "name",
                    ""
                )
            )

            page_path = str(
                self._get_value(
                    page,
                    "path",
                    ""
                )
            )

            # =================================================
            # CONFIRM
            # =================================================

            reply = QMessageBox.question(
                self,
                "Xác nhận xóa Page",
                (
                    "Bạn có chắc muốn xóa Page này không?\n\n"
                    f"Tên trang: {page_name}\n"
                    f"Route: {page_path}\n\n"
                    "Dữ liệu Page sẽ bị xóa khỏi database."
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            # =================================================
            # DELETE
            # =================================================

            self.service.delete_page(
                page_id
            )

            print(
                "Page deleted:",
                page_id
            )

            # RELOAD

            self.load_data()

            QMessageBox.information(
                self,
                "Đã xóa",
                (
                    f"Đã xóa Page '{page_name}'."
                )
            )

        except Exception as e:

            print(
                "Delete page error:",
                e
            )

            QMessageBox.critical(
                self,
                "Lỗi",
                (
                    "Không thể xóa Page.\n\n"
                    f"{e}"
                )
            )

    # =====================================================
    # OPEN TEST
    # =====================================================

    def open_test_page(
        self,
        page_id
    ):

        if page_id is None:
            return

        try:

            page = self.service.get_page(
                page_id
            )

            if not page:

                QMessageBox.warning(
                    self,
                    "Không tìm thấy Page",
                    (
                        f"Page ID {page_id} "
                        "không tồn tại."
                    )
                )

                return

            page_name = str(
                self._get_value(
                    page,
                    "name",
                    ""
                )
            )

            page_path = str(
                self._get_value(
                    page,
                    "path",
                    ""
                )
            )

            QMessageBox.information(
                self,
                "Mở kiểm thử",
                (
                    f"Trang: {page_name}\n"
                    f"Route: {page_path}\n"
                    f"Page ID: {page_id}"
                )
            )

        except Exception as e:

            print(
                "Open test page error:",
                e
            )

            QMessageBox.critical(
                self,
                "Lỗi",
                (
                    "Không thể mở Page.\n\n"
                    f"{e}"
                )
            )