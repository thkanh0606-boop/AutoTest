from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config import Config
from core.helpers.utils import get_logger
from core.pcm_suite_contract import pcm_suite_cases
from core.suite_loader import (
    dashboard_regression_cases,
    demo_7_module_cases,
    load_test_suite_from_excel,
)
from core.test_result_repository import TestResultRepository
from runners.suite_runner import SuiteWorker
from services.suite_report_export import export_report


logger = get_logger()

_EXCLUDED_AUTO_SUITES = {
    "TestCase_PCM.xlsx",
}


class TestSuitePage(QWidget):
    """Test Suite, grouped history and report workspace."""

    def __init__(self):
        super().__init__()
        self.setObjectName("TestSuitePage")
        self.repository = TestResultRepository()
        self.worker = None
        self.current_suite_id = 0
        self.current_suite_name = ""
        self.current_run_id = ""
        self.test_cases: list[dict] = []
        self.visible_case_indices: list[int] = []
        self.running_case_keys: list[str] = []
        self.selected_case_keys: set[str] = set()
        self.case_results: dict[str, dict] = {}
        self.report_results: list[dict] = []
        self.report_run: dict = {}
        self.current_screenshot_path = ""

        self._set_styles()
        self._build_ui()
        self._configure_combo_popups()
        self._register_default_suites()
        self._refresh_suite_choices()
        self._refresh_history()

    def _set_styles(self):
        self.setStyleSheet(
            """
            QWidget#TestSuitePage { background: #f4f7fb; color: #102033; }
            QLabel { color: #102033; }
            QFrame#Card { background: #ffffff; border: 1px solid #dfe5ec; border-radius: 10px; }
            QComboBox, QLineEdit, QTextEdit, QTextBrowser {
                background: #ffffff; border: 1px solid #cfd8e3; border-radius: 7px;
                color: #102033; padding: 7px; min-height: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff; color: #102033;
                border: 1px solid #94a3b8; border-radius: 5px;
                selection-background-color: #dbeafe; selection-color: #102033;
                outline: 0; padding: 4px;
            }
            QComboBox QAbstractItemView::item { min-height: 28px; padding: 4px 8px; }
            QPushButton { border-radius: 7px; font-weight: 700; padding: 8px 13px; }
            QPushButton#Primary { background: #2563eb; color: white; border: none; }
            QPushButton#Danger { background: #ef4444; color: white; border: none; }
            QPushButton#Secondary { background: #e2e8f0; color: #334155; border: none; }
            QPushButton:disabled { background: #cbd5e1; color: #64748b; }
            QTabWidget::pane { border: 1px solid #dfe5ec; background: white; }
            QTabBar::tab { padding: 10px 18px; background: #e8edf4; color: #475569; }
            QTabBar::tab:selected { background: white; color: #1d4ed8; font-weight: 700; }
            QTableWidget { background: white; color: #102033; border: 1px solid #e2e8f0; gridline-color: #e2e8f0; }
            QHeaderView::section { background: #f1f5f9; color: #334155; padding: 7px; border: 1px solid #e2e8f0; font-weight: 700; }
            """
        )

    def _configure_combo_popups(self):
        """Style popup windows directly so the global dark theme cannot leak in."""
        popup_style = """
            QAbstractItemView {
                background-color: #ffffff;
                color: #102033;
                border: 1px solid #94a3b8;
                border-radius: 5px;
                selection-background-color: #dbeafe;
                selection-color: #102033;
                outline: 0;
                padding: 4px;
            }
            QAbstractItemView::item {
                color: #102033;
                min-height: 28px;
                padding: 4px 8px;
            }
            QAbstractItemView::item:selected {
                background-color: #dbeafe;
                color: #102033;
            }
        """
        for combo in self.findChildren(QComboBox):
            combo.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )
            combo.setMinimumContentsLength(12)
            combo.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            combo.view().setStyleSheet(popup_style)
            combo.view().setTextElideMode(Qt.TextElideMode.ElideRight)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 14, 24, 18)
        root.setSpacing(8)

        eyebrow = QLabel("TEST SUITE & REPORT CENTER")
        eyebrow.setStyleSheet("color:#2563eb;font-size:11px;font-weight:800;letter-spacing:2px")
        title = QLabel("Kiểm thử theo suite, lịch sử và báo cáo")
        title.setStyleSheet("font-size:23px;font-weight:750;color:#071a33")
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        subtitle = QLabel(
            "Chạy Selected / Current Module / Full Website · lưu lịch sử · gom kết quả theo module · export Excel/HTML/PDF"
        )
        subtitle.setStyleSheet("color:#52657a;font-size:12px")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        root.addWidget(eyebrow)
        root.addWidget(title)
        root.addWidget(subtitle)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_suite_tab(), "Test Suite")
        self.tabs.addTab(self._build_history_tab(), "Lịch sử chạy")
        self.tabs.addTab(self._build_report_tab(), "Báo cáo")
        self.tabs.addTab(self._build_guide_tab(), "User Guide")
        root.addWidget(self.tabs, 1)

    def _card(self) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        return frame, layout

    def _update_credential_status(self):
        admin_state = "Admin ✓" if self.admin_email_value and self.admin_password_value else "Admin thiếu"
        staff_state = "Nhân viên ✓" if self.staff_email_value and self.staff_password_value else "TC02 thiếu tài khoản"
        self.credential_status.setText(f"{admin_state} · {staff_state}")

    def _open_credentials_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tài khoản chạy TestCase_PCM")
        dialog.setModal(True)
        dialog.setMinimumWidth(480)
        root = QVBoxLayout(dialog)
        form = QFormLayout()

        admin_email = QLineEdit(self.admin_email_value)
        admin_password = QLineEdit(self.admin_password_value)
        admin_password.setEchoMode(QLineEdit.EchoMode.Password)
        staff_email = QLineEdit(self.staff_email_value)
        staff_email.setPlaceholderText("Bắt buộc cho TC02")
        staff_password = QLineEdit(self.staff_password_value)
        staff_password.setEchoMode(QLineEdit.EchoMode.Password)
        staff_password.setPlaceholderText("Bắt buộc cho TC02")
        form.addRow("Email Admin:", admin_email)
        form.addRow("Mật khẩu Admin:", admin_password)
        form.addRow("Email Nhân viên:", staff_email)
        form.addRow("Mật khẩu Nhân viên:", staff_password)
        root.addLayout(form)

        note = QLabel(
            "Thông tin chỉ dùng trong tiến trình hiện tại, không ghi mật khẩu vào báo cáo hoặc database."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#64748b;font-size:11px")
        root.addWidget(note)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        root.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.admin_email_value = admin_email.text().strip()
            self.admin_password_value = admin_password.text()
            self.staff_email_value = staff_email.text().strip()
            self.staff_password_value = staff_password.text()
            self._update_credential_status()

    def _build_suite_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        source_card, source_layout = self._card()
        source_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        source_layout.setContentsMargins(12, 8, 12, 8)
        source_layout.setSpacing(6)
        suite_row = QHBoxLayout()
        suite_row.addWidget(QLabel("Suite:"))
        self.suite_combo = QComboBox()
        self.suite_combo.setMinimumWidth(180)
        self.suite_combo.currentIndexChanged.connect(self._on_suite_changed)
        suite_row.addWidget(self.suite_combo, 1)
        import_button = QPushButton("Import suite...")
        import_button.setObjectName("Secondary")
        import_button.clicked.connect(self._import_suite)
        suite_row.addWidget(import_button)
        source_layout.addLayout(suite_row)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Chế độ chạy:"))
        self.run_mode_combo = QComboBox()
        self.run_mode_combo.addItem("Selected", "selected")
        self.run_mode_combo.addItem("Current Page (module đang lọc)", "current_module")
        self.run_mode_combo.addItem("Full Website", "full_website")
        mode_row.addWidget(self.run_mode_combo, 1)
        source_layout.addLayout(mode_row)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Module:"))
        self.module_filter = QComboBox()
        self.module_filter.addItem("Tất cả module", "")
        self.module_filter.currentIndexChanged.connect(self._refresh_case_table)
        filter_row.addWidget(self.module_filter)
        self.case_search = QLineEdit()
        self.case_search.setPlaceholderText("Tìm TC ID hoặc tên case...")
        self.case_search.textChanged.connect(self._refresh_case_table)
        filter_row.addWidget(self.case_search, 1)
        source_layout.addLayout(filter_row)
        select_module = QPushButton("Chọn module")
        select_module.setObjectName("Secondary")
        select_module.clicked.connect(self._select_visible)
        clear_select = QPushButton("Bỏ chọn")
        clear_select.setObjectName("Secondary")
        clear_select.clicked.connect(self._clear_selection)
        selection_actions = QHBoxLayout()
        selection_actions.addStretch()
        selection_actions.addWidget(select_module)
        selection_actions.addWidget(clear_select)
        source_layout.addLayout(selection_actions)
        layout.addWidget(source_card)

        self.credential_card, credential_layout = self._card()
        self.credential_card.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        credential_layout.setContentsMargins(12, 7, 12, 7)
        credential_layout.setSpacing(6)
        self.admin_email_value = Config.TEST_EMAIL
        self.admin_password_value = Config.TEST_PASSWORD
        self.staff_email_value = os.getenv("TEST_STAFF_EMAIL", "")
        self.staff_password_value = os.getenv("TEST_STAFF_PASSWORD", "")
        credential_row = QHBoxLayout()
        credential_title = QLabel("Tài khoản TestCase_PCM")
        credential_title.setStyleSheet("font-weight:700;color:#1e3a5f")
        self.credential_status = QLabel()
        self.credential_status.setStyleSheet("color:#64748b;font-size:11px")
        self.credential_status.setWordWrap(True)
        self.credential_status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        credential_button = QPushButton("Cấu hình tài khoản...")
        credential_button.setObjectName("Secondary")
        credential_button.clicked.connect(self._open_credentials_dialog)
        credential_row.addWidget(credential_title)
        credential_row.addStretch()
        credential_row.addWidget(credential_button)
        credential_layout.addLayout(credential_row)
        credential_layout.addWidget(self.credential_status)
        self._update_credential_status()
        layout.addWidget(self.credential_card)

        self.case_table = QTableWidget(0, 7)
        self.case_table.setHorizontalHeaderLabels(
            ["Chọn", "Module", "TC ID", "Tên Test Case", "Expected", "Khả năng chạy", "Status"]
        )
        self.case_table.verticalHeader().setVisible(False)
        self.case_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.case_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.case_table.setMinimumHeight(140)
        self.case_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        header = self.case_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.case_table.setColumnWidth(0, 48)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.case_table, 1)

        action_card, action_layout = self._card()
        action_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        action_layout.setContentsMargins(12, 8, 12, 8)
        action_layout.setSpacing(5)
        stats = QHBoxLayout()
        self.total_label = QLabel("TOTAL 0")
        self.pass_label = QLabel("PASS 0")
        self.fail_label = QLabel("FAIL 0")
        self.error_label = QLabel("ERROR 0")
        self.skip_label = QLabel("SKIP 0")
        self.pass_label.setStyleSheet("color:#087f5b;font-weight:800")
        self.fail_label.setStyleSheet("color:#c92a2a;font-weight:800")
        self.error_label.setStyleSheet("color:#9c1c1c;font-weight:800")
        self.skip_label.setStyleSheet("color:#b26a00;font-weight:800")
        for widget in (self.total_label, self.pass_label, self.fail_label, self.error_label, self.skip_label):
            stats.addWidget(widget)
        stats.addStretch()
        self.run_button = QPushButton("▶ Chạy")
        self.run_button.setObjectName("Primary")
        self.run_button.clicked.connect(self._run_tests)
        self.stop_button = QPushButton("■ Dừng")
        self.stop_button.setObjectName("Danger")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_tests)
        stats.addWidget(self.run_button)
        stats.addWidget(self.stop_button)
        action_layout.addLayout(stats)
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setStyleSheet("color:#52657a")
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%v / %m test")
        action_layout.addWidget(self.status_label)
        action_layout.addWidget(self.progress)
        layout.addWidget(action_card)
        return page

    def _build_history_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        self.history_suite_filter = QComboBox()
        self.history_suite_filter.addItem("Tất cả suite", "")
        self.history_status_filter = QComboBox()
        self.history_status_filter.addItem("Tất cả trạng thái", "")
        for status in ("PASSED", "PASSED_WITH_SKIPS", "FAILED", "ERROR", "STOPPED"):
            self.history_status_filter.addItem(status, status)
        self.history_module_filter = QComboBox()
        self.history_module_filter.addItem("Tất cả module", "")
        self.history_suite_filter.currentIndexChanged.connect(self._refresh_history)
        self.history_status_filter.currentIndexChanged.connect(self._refresh_history)
        self.history_module_filter.currentIndexChanged.connect(self._refresh_history)

        suite_filters = QHBoxLayout()
        suite_filters.addWidget(QLabel("Suite:"))
        suite_filters.addWidget(self.history_suite_filter, 1)
        suite_filters.addWidget(QLabel("Status:"))
        suite_filters.addWidget(self.history_status_filter, 1)
        layout.addLayout(suite_filters)

        module_filters = QHBoxLayout()
        module_filters.addWidget(QLabel("Module:"))
        module_filters.addWidget(self.history_module_filter, 1)
        layout.addLayout(module_filters)

        refresh = QPushButton("Làm mới")
        refresh.setObjectName("Secondary")
        refresh.clicked.connect(self._refresh_history)
        open_report = QPushButton("Xem báo cáo run")
        open_report.setObjectName("Primary")
        open_report.clicked.connect(self._open_selected_history_run)
        history_actions = QHBoxLayout()
        history_actions.addStretch()
        history_actions.addWidget(refresh)
        history_actions.addWidget(open_report)
        layout.addLayout(history_actions)

        self.history_table = QTableWidget(0, 10)
        self.history_table.setHorizontalHeaderLabels(
            ["Run ID", "Suite", "Mode", "Status", "Total", "Pass", "Fail", "Error", "Skip", "Bắt đầu"]
        )
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.doubleClicked.connect(self._open_selected_history_run)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table, 1)
        return page

    def _build_report_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        run_row = QHBoxLayout()
        run_row.addWidget(QLabel("Run:"))
        self.report_run_combo = QComboBox()
        self.report_run_combo.setMinimumWidth(180)
        self.report_run_combo.currentIndexChanged.connect(self._on_report_run_changed)
        run_row.addWidget(self.report_run_combo, 1)
        layout.addLayout(run_row)

        export_row = QHBoxLayout()
        export_row.addStretch()
        for label, extension in (("Export Excel", ".xlsx"), ("Export HTML", ".html"), ("Export PDF", ".pdf")):
            button = QPushButton(label)
            button.setObjectName("Secondary")
            button.clicked.connect(lambda _checked=False, ext=extension: self._export_current_report(ext))
            export_row.addWidget(button)
        layout.addLayout(export_row)

        self.report_summary_label = QLabel("Chưa chọn run")
        self.report_summary_label.setStyleSheet("font-size:14px;font-weight:700;color:#1e3a5f")
        self.report_summary_label.setWordWrap(True)
        self.report_summary_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self.report_summary_label)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.module_summary_table = QTableWidget(0, 7)
        self.module_summary_table.setHorizontalHeaderLabels(
            ["Module", "Total", "Pass", "Fail", "Error", "Skip", "Thời gian (ms)"]
        )
        self.module_summary_table.verticalHeader().setVisible(False)
        self.module_summary_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.module_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        splitter.addWidget(self.module_summary_table)

        result_panel = QWidget()
        result_layout = QVBoxLayout(result_panel)
        result_layout.setContentsMargins(0, 0, 0, 0)
        report_filters = QHBoxLayout()
        self.report_status_filter = QComboBox()
        self.report_status_filter.addItem("Tất cả status", "")
        for status in ("PASSED", "FAILED", "ERROR", "SKIPPED"):
            self.report_status_filter.addItem(status, status)
        self.report_status_filter.currentIndexChanged.connect(self._refresh_report_results)
        self.report_module_filter = QComboBox()
        self.report_module_filter.addItem("Tất cả module", "")
        self.report_module_filter.currentIndexChanged.connect(self._refresh_report_results)
        self.report_search = QLineEdit()
        self.report_search.setPlaceholderText("Lọc TC ID hoặc tên case...")
        self.report_search.textChanged.connect(self._refresh_report_results)
        report_filters.addWidget(self.report_status_filter)
        report_filters.addWidget(self.report_module_filter)
        report_filters.addWidget(self.report_search, 1)
        result_layout.addLayout(report_filters)

        self.report_result_table = QTableWidget(0, 7)
        self.report_result_table.setHorizontalHeaderLabels(
            ["TC ID", "Module", "Tên case", "Status", "Expected", "Actual", "Thời gian"]
        )
        self.report_result_table.verticalHeader().setVisible(False)
        self.report_result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.report_result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.report_result_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.report_result_table.itemSelectionChanged.connect(self._show_result_detail)
        result_header = self.report_result_table.horizontalHeader()
        result_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        result_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        result_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        result_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        result_layout.addWidget(self.report_result_table, 1)

        detail_row = QHBoxLayout()
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setPlaceholderText("Chọn một kết quả để xem log, expected, actual và lỗi.")
        self.screenshot_button = QPushButton("Mở screenshot lỗi")
        self.screenshot_button.setObjectName("Secondary")
        self.screenshot_button.setEnabled(False)
        self.screenshot_button.clicked.connect(self._open_screenshot)
        detail_row.addWidget(self.result_detail, 1)
        detail_row.addWidget(self.screenshot_button)
        result_layout.addLayout(detail_row)
        splitter.addWidget(result_panel)
        splitter.setSizes([180, 520])
        layout.addWidget(splitter, 1)
        return page

    def _build_guide_tab(self):
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(
            """
            <h2>Hướng dẫn Test Suite</h2>
            <ol>
              <li>Chọn suite có sẵn hoặc bấm <b>Import suite</b> để nạp Excel/CSV.</li>
              <li>Lọc theo module, chọn các case cần chạy.</li>
              <li><b>Selected</b>: chỉ chạy case đã chọn; <b>Current Module</b>: chạy module đang lọc; <b>Full Website</b>: chạy toàn suite.</li>
              <li>Case có locator/action hoặc route-smoke mới được thực thi. Case chỉ có mô tả nghiệp vụ sẽ <b>SKIPPED</b>, không PASS giả.</li>
              <li>Mở tab <b>Lịch sử chạy</b> để lọc run; mở <b>Báo cáo</b> để xem nhóm module, log và screenshot.</li>
              <li>Xuất báo cáo bằng Excel, HTML hoặc PDF.</li>
            </ol>
            <h3>Hai suite chuẩn</h3>
            <ul><li><b>Demo 7 Modules</b>: kiểm tra route và DOM của 7 module PCM.</li>
            <li><b>Dashboard Regression</b>: chạy từng locator/assertion Dashboard độc lập.</li></ul>
            <p>Tài liệu đầy đủ: <code>docs/TEST_SUITE_USER_GUIDE.md</code>, <code>docs/TEST_SUMMARY.md</code>, <code>docs/DEMO_7_MODULES.md</code>.</p>
            """
        )
        return browser

    # ------------------------------------------------------------------
    # Suite definitions and case selection
    # ------------------------------------------------------------------
    def _register_default_suites(self):
        self.repository.save_suite_definition(
            "Demo 7 Modules", demo_7_module_cases(), suite_key="builtin:demo-7-modules"
        )
        self.repository.save_suite_definition(
            "Dashboard Regression",
            dashboard_regression_cases(),
            suite_key="builtin:dashboard-regression",
        )
        excel_dir = Path(__file__).resolve().parents[1] / "excel"
        pcm_excel_path = excel_dir / "TestCase_PCM.xlsx"
        self.repository.remove_suite_definition_by_source(str(pcm_excel_path))
        self.repository.save_suite_definition(
            "TestCase_PCM",
            pcm_suite_cases(),
            suite_key="builtin:testcase-pcm-31",
        )
        if excel_dir.exists():
            for path in sorted(excel_dir.iterdir()):
                if path.suffix.lower() not in {".xlsx", ".xls", ".csv"}:
                    continue
                if path.name in _EXCLUDED_AUTO_SUITES:
                    self.repository.remove_suite_definition_by_source(str(path))
                    continue
                try:
                    cases = load_test_suite_from_excel(str(path))
                    self.repository.save_suite_definition(path.stem, cases, str(path))
                except Exception as error:
                    logger.error("Không đăng ký được suite %s: %s", path.name, error)

    def _refresh_suite_choices(self, select_suite_id: int = 0):
        suites = self.repository.list_suite_definitions()
        self.suite_combo.blockSignals(True)
        self.suite_combo.clear()
        for suite in suites:
            self.suite_combo.addItem(f"{suite['name']} ({suite['case_count']} cases)", suite["id"])
        self.suite_combo.blockSignals(False)

        for combo in (self.history_suite_filter,):
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Tất cả suite", "")
            for suite in suites:
                combo.addItem(suite["name"], suite["name"])
            index = combo.findData(current)
            combo.setCurrentIndex(max(0, index))
            combo.blockSignals(False)

        if select_suite_id:
            target_index = self.suite_combo.findData(select_suite_id)
        else:
            default_suite = next((suite for suite in suites if suite["name"] == "TestCase_PCM"), None)
            target_index = self.suite_combo.findData(default_suite["id"]) if default_suite else 0
        self.suite_combo.setCurrentIndex(max(0, target_index))
        self._on_suite_changed(self.suite_combo.currentIndex())

    def _on_suite_changed(self, _index: int):
        suite_id = self.suite_combo.currentData()
        if not suite_id:
            return
        definition = self.repository.suite_definition(int(suite_id)) or {}
        self.current_suite_id = int(suite_id)
        self.current_suite_name = definition.get("name", "")
        self.credential_card.setVisible(self.current_suite_name == "TestCase_PCM")
        self.test_cases = self.repository.suite_cases(self.current_suite_id)
        for index, case in enumerate(self.test_cases):
            case["_ui_key"] = f"{index}:{case.get('source_sheet', '')}:{case.get('tc_id', '')}"
        self.selected_case_keys = {case["_ui_key"] for case in self.test_cases}
        self.case_results.clear()
        self._refresh_module_choices()
        self._refresh_case_table()
        self._reset_run_stats()
        self.status_label.setText(f"Đã tải {len(self.test_cases)} case từ {self.current_suite_name}")

    def _refresh_module_choices(self):
        modules = sorted({self._case_module(case) for case in self.test_cases})
        self.module_filter.blockSignals(True)
        self.module_filter.clear()
        self.module_filter.addItem("Tất cả module", "")
        for module in modules:
            self.module_filter.addItem(module, module)
        self.module_filter.blockSignals(False)

        for combo in (self.history_module_filter,):
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Tất cả module", "")
            for module in modules:
                combo.addItem(module, module)
            combo.setCurrentIndex(max(0, combo.findData(current)))
            combo.blockSignals(False)

    def _case_module(self, case: dict) -> str:
        return str(case.get("module") or case.get("area") or case.get("page_key") or "General")

    def _is_executable(self, case: dict) -> bool:
        return bool(
            case.get("action_type") in {"route_smoke", "pcm_scenario"}
            or (case.get("locator_type") and case.get("locator_value"))
        )

    def _refresh_case_table(self):
        module = self.module_filter.currentData() or ""
        query = self.case_search.text().strip().lower()
        self.visible_case_indices = []
        for index, case in enumerate(self.test_cases):
            haystack = f"{case.get('tc_id', '')} {case.get('title', '')}".lower()
            if module and self._case_module(case) != module:
                continue
            if query and query not in haystack:
                continue
            self.visible_case_indices.append(index)

        self.case_table.setRowCount(0)
        for row, case_index in enumerate(self.visible_case_indices):
            case = self.test_cases[case_index]
            self.case_table.insertRow(row)
            checkbox = QCheckBox()
            checkbox.setChecked(case["_ui_key"] in self.selected_case_keys)
            checkbox.stateChanged.connect(
                lambda state, key=case["_ui_key"]: self._selection_changed(key, state)
            )
            holder = QWidget()
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(0, 0, 0, 0)
            holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            holder_layout.addWidget(checkbox)
            self.case_table.setCellWidget(row, 0, holder)
            values = (
                self._case_module(case),
                case.get("tc_id", ""),
                case.get("title", ""),
                case.get("expected", ""),
                "AUTOMATED" if self._is_executable(case) else "SKIP (thiếu locator)",
                self.case_results.get(case["_ui_key"], {}).get("status", "Pending"),
            )
            for column, value in enumerate(values, start=1):
                item = QTableWidgetItem(str(value))
                if column == 5:
                    item.setForeground(QColor("#087f5b" if self._is_executable(case) else "#b26a00"))
                if column == 6:
                    self._style_status_item(item, str(value))
                self.case_table.setItem(row, column, item)

    def _selection_changed(self, key: str, state: int):
        if state == Qt.CheckState.Checked.value:
            self.selected_case_keys.add(key)
        else:
            self.selected_case_keys.discard(key)

    def _select_visible(self):
        self.selected_case_keys.update(
            self.test_cases[index]["_ui_key"] for index in self.visible_case_indices
        )
        self._refresh_case_table()

    def _clear_selection(self):
        self.selected_case_keys.clear()
        self._refresh_case_table()

    def _import_suite(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Test Suite",
            "",
            "Test Suite (*.xlsx *.xls *.csv);;Excel (*.xlsx *.xls);;CSV (*.csv)",
        )
        if not path:
            return
        try:
            cases = load_test_suite_from_excel(path)
            suite_id = self.repository.save_suite_definition(Path(path).stem, cases, path)
            self._refresh_suite_choices(suite_id)
            self.status_label.setText(f"Import thành công {len(cases)} case")
        except Exception as error:
            QMessageBox.critical(self, "Import thất bại", str(error))

    # ------------------------------------------------------------------
    # Running
    # ------------------------------------------------------------------
    def _cases_for_run(self) -> tuple[list[dict], str]:
        mode = self.run_mode_combo.currentData()
        if mode == "selected":
            cases = [case for case in self.test_cases if case["_ui_key"] in self.selected_case_keys]
            label = "Selected"
        elif mode == "current_module":
            module = self.module_filter.currentData() or ""
            if not module:
                raise ValueError("Hãy chọn một module trước khi chạy Current Module.")
            cases = [case for case in self.test_cases if self._case_module(case) == module]
            label = f"Current Page: {module}"
        else:
            cases = list(self.test_cases)
            label = "Full Website"
        if not cases:
            raise ValueError("Không có Test Case phù hợp để chạy.")
        return cases, label

    def _run_tests(self):
        if self.worker and self.worker.isRunning():
            return
        try:
            cases, mode_label = self._cases_for_run()
        except ValueError as error:
            self.status_label.setText(str(error))
            return

        Config.TEST_EMAIL = self.admin_email_value.strip()
        Config.TEST_PASSWORD = self.admin_password_value
        if self.current_suite_name == "TestCase_PCM" and (
            not Config.TEST_EMAIL or not Config.TEST_PASSWORD
        ):
            self.status_label.setText("Thiếu tài khoản Admin. Hãy bấm Cấu hình tài khoản.")
            self._open_credentials_dialog()
            return
        staff_email = self.staff_email_value.strip()
        staff_password = self.staff_password_value
        if staff_email:
            os.environ["TEST_STAFF_EMAIL"] = staff_email
        else:
            os.environ.pop("TEST_STAFF_EMAIL", None)
        if staff_password:
            os.environ["TEST_STAFF_PASSWORD"] = staff_password
        else:
            os.environ.pop("TEST_STAFF_PASSWORD", None)

        destructive_cases = [case["tc_id"] for case in cases if case.get("destructive")]
        if destructive_cases:
            answer = QMessageBox.warning(
                self,
                "Xác nhận chạy test dữ liệu",
                "Các case sau sẽ tạo dữ liệu test hoặc đổi trạng thái rồi cleanup/khôi phục:\n"
                + ", ".join(destructive_cases)
                + "\n\nBạn có muốn tiếp tục?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.status_label.setText("Đã hủy trước nhóm test thay đổi dữ liệu.")
                return

        self.running_case_keys = [case["_ui_key"] for case in cases]
        for key in self.running_case_keys:
            self.case_results[key] = {"status": "Pending"}
        self._refresh_case_table()
        self._reset_run_stats(total=len(cases))
        self.progress.setRange(0, len(cases))
        self.progress.setValue(0)
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Đang khởi động Selenium...")

        clean_cases = [{key: value for key, value in case.items() if key != "_ui_key"} for case in cases]
        self.worker = SuiteWorker(
            clean_cases,
            suite_id=self.current_suite_id,
            suite_name=self.current_suite_name,
            run_mode=mode_label,
            db_path=self.repository.db_path,
        )
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.result_signal.connect(self._on_result)
        self.worker.detail_signal.connect(self._on_detail)
        self.worker.run_started_signal.connect(self._on_run_started)
        self.worker.summary_signal.connect(self._on_run_summary)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _reset_run_stats(self, total: int | None = None):
        self.run_counts = {"PASSED": 0, "FAILED": 0, "ERROR": 0, "SKIPPED": 0}
        self.total_label.setText(f"TOTAL {len(self.test_cases) if total is None else total}")
        self.pass_label.setText("PASS 0")
        self.fail_label.setText("FAIL 0")
        self.error_label.setText("ERROR 0")
        self.skip_label.setText("SKIP 0")

    def _on_run_started(self, run_id: str):
        self.current_run_id = run_id

    def _on_progress(self, current: int, total: int, message: str):
        self.progress.setRange(0, max(1, total))
        self.progress.setValue(current)
        self.status_label.setText(message)

    def _on_result(self, index: int, status: str, message: str):
        if 0 <= index < len(self.running_case_keys):
            key = self.running_case_keys[index]
            self.case_results.setdefault(key, {})
            self.case_results[key].update({"status": status, "message": message})
        self.run_counts[status] = self.run_counts.get(status, 0) + 1
        self.pass_label.setText(f"PASS {self.run_counts.get('PASSED', 0)}")
        self.fail_label.setText(f"FAIL {self.run_counts.get('FAILED', 0)}")
        self.error_label.setText(f"ERROR {self.run_counts.get('ERROR', 0)}")
        self.skip_label.setText(f"SKIP {self.run_counts.get('SKIPPED', 0)}")
        self._refresh_case_table()

    def _on_detail(self, index: int, payload: dict):
        if 0 <= index < len(self.running_case_keys):
            self.case_results[self.running_case_keys[index]] = payload

    def _on_run_summary(self, summary: dict):
        self.current_run_id = summary.get("run_id", self.current_run_id)

    def _on_finished(self):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Đã hoàn tất. Run ID: {self.current_run_id}")
        self._refresh_history()
        self._refresh_report_run_choices(self.current_run_id)

    def _stop_tests(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.stop_button.setEnabled(False)
            self.status_label.setText("Đang dừng sau thao tác Selenium hiện tại...")

    def _style_status_item(self, item: QTableWidgetItem, status: str):
        colors = {
            "PASSED": "#087f5b",
            "FAILED": "#c92a2a",
            "ERROR": "#9c1c1c",
            "SKIPPED": "#b26a00",
            "Pending": "#64748b",
        }
        item.setForeground(QColor(colors.get(status, "#334155")))

    # ------------------------------------------------------------------
    # History and report
    # ------------------------------------------------------------------
    def _refresh_history(self, *_args):
        runs = self.repository.list_suite_runs(
            suite_name=self.history_suite_filter.currentData() or "",
            status=self.history_status_filter.currentData() or "",
            module=self.history_module_filter.currentData() or "",
        )
        self.history_rows = runs
        self.history_table.setRowCount(0)
        for row, run in enumerate(runs):
            self.history_table.insertRow(row)
            values = (
                run["run_id"], run["suite_name"], run["run_mode"], run["status"],
                run["total"], run["passed"], run["failed"], run["error"], run["skipped"], run["started_at"],
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 3:
                    self._style_status_item(item, str(value).replace("PASSED_WITH_SKIPS", "SKIPPED"))
                self.history_table.setItem(row, column, item)
        self._refresh_report_run_choices(self.current_run_id)

    def _open_selected_history_run(self, *_args):
        row = self.history_table.currentRow()
        if row < 0 or row >= len(getattr(self, "history_rows", [])):
            return
        run_id = self.history_rows[row]["run_id"]
        self._refresh_report_run_choices(run_id)
        self.tabs.setCurrentIndex(2)

    def _refresh_report_run_choices(self, select_run_id: str = ""):
        runs = self.repository.list_suite_runs(limit=200)
        self.report_run_combo.blockSignals(True)
        self.report_run_combo.clear()
        for run in runs:
            label = f"{run['started_at']} · {run['suite_name']} · {run['status']} · {run['run_id']}"
            self.report_run_combo.addItem(label, run["run_id"])
        index = self.report_run_combo.findData(select_run_id) if select_run_id else 0
        self.report_run_combo.setCurrentIndex(max(0, index))
        self.report_run_combo.blockSignals(False)
        if self.report_run_combo.count():
            self._load_report(self.report_run_combo.currentData())

    def _on_report_run_changed(self, _index: int):
        run_id = self.report_run_combo.currentData()
        if run_id:
            self._load_report(run_id)

    def _load_report(self, run_id: str):
        run = self.repository.suite_run(run_id)
        if not run:
            return
        self.report_run = run
        self.report_results = self.repository.suite_run_results(run_id)
        module_summary = self.repository.suite_run_module_summary(run_id)
        self.report_summary_label.setText(
            f"{run['suite_name']} · {run['run_mode']} · {run['status']}  |  "
            f"Total {run['total']} · Pass {run['passed']} · Fail {run['failed']} · "
            f"Error {run['error']} · Skip {run['skipped']}"
        )
        self.module_summary_table.setRowCount(0)
        for row, summary in enumerate(module_summary):
            self.module_summary_table.insertRow(row)
            for column, key in enumerate(("module", "total", "passed", "failed", "error", "skipped", "duration_ms")):
                self.module_summary_table.setItem(row, column, QTableWidgetItem(str(summary.get(key, 0))))

        modules = sorted({result["module"] for result in self.report_results})
        self.report_module_filter.blockSignals(True)
        self.report_module_filter.clear()
        self.report_module_filter.addItem("Tất cả module", "")
        for module in modules:
            self.report_module_filter.addItem(module, module)
        self.report_module_filter.blockSignals(False)
        self._refresh_report_results()

    def _refresh_report_results(self):
        status = self.report_status_filter.currentData() or ""
        module = self.report_module_filter.currentData() or ""
        query = self.report_search.text().strip().lower()
        self.visible_report_results = []
        for result in self.report_results:
            if status and result["status"] != status:
                continue
            if module and result["module"] != module:
                continue
            if query and query not in f"{result['case_id']} {result['title']}".lower():
                continue
            self.visible_report_results.append(result)

        self.report_result_table.setRowCount(0)
        for row, result in enumerate(self.visible_report_results):
            self.report_result_table.insertRow(row)
            values = (
                result["case_id"], result["module"], result["title"], result["status"],
                result["expected"], result["actual"], f"{result['duration_ms'] / 1000:.1f}s",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 3:
                    self._style_status_item(item, str(value))
                self.report_result_table.setItem(row, column, item)
        self.result_detail.clear()
        self.screenshot_button.setEnabled(False)

    def _show_result_detail(self):
        row = self.report_result_table.currentRow()
        if row < 0 or row >= len(getattr(self, "visible_report_results", [])):
            return
        result = self.visible_report_results[row]
        detail = (
            f"TC ID: {result['case_id']}\nModule: {result['module']}\nStatus: {result['status']}\n"
            f"Started: {result['started_at']}\nFinished: {result['finished_at']}\n\n"
            f"EXPECTED\n{result['expected']}\n\nACTUAL\n{result['actual']}\n\n"
            f"MESSAGE\n{result['message']}\n\nERROR\n{result['error_message']}\n\n"
            f"LOG\n{result['log_text']}\n\nSCREENSHOT\n{result['screenshot_path']}"
        )
        self.result_detail.setPlainText(detail)
        self.current_screenshot_path = result.get("screenshot_path", "")
        self.screenshot_button.setEnabled(bool(self.current_screenshot_path and Path(self.current_screenshot_path).exists()))

    def _open_screenshot(self):
        if self.current_screenshot_path and Path(self.current_screenshot_path).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_screenshot_path))

    def _export_current_report(self, extension: str):
        if not self.report_run:
            QMessageBox.information(self, "Báo cáo", "Chưa có run để export.")
            return
        filters = {
            ".xlsx": "Excel (*.xlsx)",
            ".html": "HTML (*.html)",
            ".pdf": "PDF (*.pdf)",
        }
        default_name = f"Test_Suite_Report_{self.report_run['run_id']}{extension}"
        path, _ = QFileDialog.getSaveFileName(self, "Export báo cáo", default_name, filters[extension])
        if not path:
            return
        if not path.lower().endswith(extension):
            path += extension
        try:
            module_summary = self.repository.suite_run_module_summary(self.report_run["run_id"])
            export_report(path, self.report_run, self.report_results, module_summary)
            QMessageBox.information(self, "Export thành công", f"Đã lưu báo cáo:\n{path}")
        except Exception as error:
            logger.exception("Export suite report failed")
            QMessageBox.critical(self, "Export thất bại", str(error))
