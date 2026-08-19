from PySide6.QtCore import QObject, QThread, Signal, Qt
from pathlib import Path
import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QScrollArea,
    QFileDialog,
    QMessageBox,
)

import pandas as pd

from runners.vehicle_catalog_runner import run_catalog_crud_test


class CrudWorker(QObject):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    result_signal = Signal(dict)
    finished = Signal()

    def __init__(self, kind, name, brand, cleanup, show_browser):
        super().__init__()
        self.kind = kind
        self.name = name
        self.brand = brand
        self.cleanup = cleanup
        self.show_browser = show_browser

    def run(self):
        try:
            result = run_catalog_crud_test(
                worker=self,
                kind=self.kind,
                name=self.name,
                brand=self.brand,
                cleanup=self.cleanup,
                show_browser=self.show_browser,
            )
            self.result_signal.emit(result or {})
        except Exception as exc:
            self.result_signal.emit({
                "status": "FAILED",
                "message": f"CRUD gặp lỗi: {exc.__class__.__name__}",
                "error": str(exc),
                "steps": [],
            })
        finally:
            self.finished.emit()


class CrudPage(QWidget):
    def __init__(self):
        super().__init__()
        self._thread = None
        self._worker = None

        # Dữ liệu test import từ CSV / JSON / XLSX.
        self.imported_rows = []
        self.current_import_row = None

        self.setObjectName("CrudPage")
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget#CrudPage {
                background: #f8fafc;
            }

            QLabel {
                background: transparent;
            }

            QFrame#Card {
                background: #ffffff;
                border: 1px solid #dbe4ef;
                border-radius: 12px;
            }

            QComboBox, QLineEdit {
                min-height: 38px;
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 0 12px;
                color: #0f172a;
                font-size: 13px;
            }

            QPushButton#Primary {
                min-height: 40px;
                background: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 700;
            }

            QPushButton#Primary:hover {
                background: #1d4ed8;
            }

            QPushButton#Primary:disabled {
                background: #64748b;
                color: #ffffff;
            }

            QTableWidget {
                background: #ffffff;
                border: 1px solid #dbe4ef;
                border-radius: 8px;
                gridline-color: #e5e7eb;
                color: #0f172a;
                font-size: 12px;
            }

            QHeaderView::section {
                background: #eef4fa;
                color: #0f172a;
                border: none;
                border-bottom: 1px solid #dbe4ef;
                padding: 9px 8px;
                font-weight: 700;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("CrudScrollContent")

        root = QVBoxLayout(content)
        root.setContentsMargins(32, 24, 32, 28)
        root.setSpacing(16)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        breadcrumb = QLabel("AutoTest   /   CRUD")
        breadcrumb.setStyleSheet("color:#8091a5; font-size:12px;")
        root.addWidget(breadcrumb)

        title = QLabel("CRUD")
        title.setStyleSheet("color:#0f172a; font-size:30px; font-weight:800;")
        root.addWidget(title)

        desc = QLabel("Kiểm thử CRUD riêng cho Danh mục xe.")
        desc.setStyleSheet("color:#64748b; font-size:13px;")
        root.addWidget(desc)

        # =====================================================
        # IMPORT TEST DATA
        # =====================================================
        import_card = QFrame()
        import_card.setObjectName("Card")
        import_layout = QVBoxLayout(import_card)
        import_layout.setContentsMargins(20, 18, 20, 18)
        import_layout.setSpacing(12)

        import_title = QLabel("Bộ dữ liệu kiểm thử (Import CSV / JSON / XLSX)")
        import_title.setStyleSheet(
            "color:#0f172a; font-size:18px; font-weight:800;"
        )
        import_layout.addWidget(import_title)

        import_desc = QLabel(
            "Đọc Expected từ file, sau đó lấy Actual từ Selenium để so sánh. "
            "Double-click một dòng để nạp test case xuống form CRUD."
        )
        import_desc.setWordWrap(True)
        import_desc.setStyleSheet("color:#64748b; font-size:12px;")
        import_layout.addWidget(import_desc)

        import_file_row = QHBoxLayout()
        import_file_row.setSpacing(10)

        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("Chưa chọn file")
        import_file_row.addWidget(self.file_path_input, 1)

        self.import_button = QPushButton("Import file")
        self.import_button.setObjectName("Primary")
        self.import_button.setCursor(Qt.PointingHandCursor)
        self.import_button.clicked.connect(self.import_test_file)
        import_file_row.addWidget(self.import_button)

        import_layout.addLayout(import_file_row)

        self.import_table = QTableWidget(0, 6)
        self.import_table.setMinimumHeight(150)
        self.import_table.setMaximumHeight(220)
        self.import_table.setHorizontalHeaderLabels(
            ["Loại", "Tên", "Hãng liên kết", "Expected tên", "Expected hãng", "Trạng thái"]
        )
        self.import_table.verticalHeader().setVisible(False)
        self.import_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.import_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.import_table.setSelectionMode(QTableWidget.SingleSelection)
        self.import_table.doubleClicked.connect(self.load_selected_import_row)

        import_header = self.import_table.horizontalHeader()
        import_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        import_header.setSectionResizeMode(1, QHeaderView.Stretch)
        import_header.setSectionResizeMode(2, QHeaderView.Stretch)
        import_header.setSectionResizeMode(3, QHeaderView.Stretch)
        import_header.setSectionResizeMode(4, QHeaderView.Stretch)
        import_header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        import_layout.addWidget(self.import_table)
        root.addWidget(import_card)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        form_title = QLabel("Thiết lập kiểm thử")
        form_title.setStyleSheet("color:#0f172a; font-size:18px; font-weight:800;")
        card_layout.addWidget(form_title)

        fields = QHBoxLayout()

        self.kind_combo = QComboBox()
        self.kind_combo.addItem("Hãng xe", "brand")
        self.kind_combo.addItem("Mẫu xe", "model")

        self.name_input = QLineEdit("LINH_AUTO_TEST")
        self.brand_input = QLineEdit("VinFast")

        fields.addWidget(self.kind_combo, 1)
        fields.addWidget(self.name_input, 2)
        fields.addWidget(self.brand_input, 2)

        card_layout.addLayout(fields)

        self.expected_file_label = QLabel("Expected từ file: chưa nạp test case")
        self.expected_file_label.setWordWrap(True)
        self.expected_file_label.setStyleSheet(
            "color:#475569; font-size:12px; font-weight:600;"
        )
        card_layout.addWidget(self.expected_file_label)

        options = QHBoxLayout()

        self.cleanup_checkbox = QCheckBox("Dọn dữ liệu test sau khi chạy")
        self.cleanup_checkbox.setChecked(True)

        self.browser_checkbox = QCheckBox("Hiện Chrome khi chạy")
        self.browser_checkbox.setChecked(True)

        self.run_button = QPushButton("Chạy kiểm tra CRUD")
        self.run_button.setObjectName("Primary")
        self.run_button.clicked.connect(self.run_crud)

        options.addWidget(self.cleanup_checkbox)
        options.addWidget(self.browser_checkbox)
        options.addStretch()
        options.addWidget(self.run_button)

        card_layout.addLayout(options)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        card_layout.addWidget(self.progress)

        self.status_label = QLabel("Sẵn sàng.")
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumHeight(54)
        self.status_label.setStyleSheet("color:#64748b; font-size:12px;")
        card_layout.addWidget(self.status_label)

        root.addWidget(card)

        result_card = QFrame()
        result_card.setObjectName("Card")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 18, 20, 18)

        result_title = QLabel("Kết quả CRUD")
        result_title.setStyleSheet("color:#0f172a; font-size:18px; font-weight:800;")
        result_layout.addWidget(result_title)

        self.table = QTableWidget(0, 4)
        self.table.setMinimumHeight(280)
        self.table.setHorizontalHeaderLabels(["STT", "Expected", "Actual", "Kết quả"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        result_layout.addWidget(self.table)
        root.addWidget(result_card, 1)

        self.kind_combo.currentIndexChanged.connect(self._sync_kind_state)
        self._sync_kind_state()

    # =========================================================
    # IMPORT CSV / JSON / XLSX
    # =========================================================

    @staticmethod
    def _normalize_column_name(name):
        return (
            str(name)
            .strip()
            .casefold()
            .replace(" ", "_")
            .replace("-", "_")
        )

    @staticmethod
    def _pick_value(row, aliases, default=""):
        normalized = {
            CrudPage._normalize_column_name(key): value
            for key, value in row.items()
        }

        for alias in aliases:
            key = CrudPage._normalize_column_name(alias)
            if key not in normalized:
                continue

            value = normalized[key]
            if pd.isna(value):
                return default

            return str(value).strip()

        return default

    @staticmethod
    def _normalize_kind(value):
        value = str(value or "").strip().casefold()

        if value in {"brand", "hãng xe", "hang xe", "hãng", "hang"}:
            return "brand"

        if value in {"model", "mẫu xe", "mau xe", "mẫu", "mau"}:
            return "model"

        return "brand"

    def import_test_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file test data",
            "",
            "Test data (*.csv *.json *.xlsx);;CSV (*.csv);;JSON (*.json);;Excel (*.xlsx)",
        )

        if not file_path:
            return

        try:
            rows = self._read_test_file(file_path)

            if not rows:
                raise ValueError("File không có dòng dữ liệu hợp lệ.")

            self.imported_rows = rows
            self.current_import_row = None
            self.file_path_input.setText(file_path)

            self._render_import_rows()

            # Tự chọn và nạp dòng đầu tiên.
            self.import_table.selectRow(0)
            self._load_import_row(0)

            self.status_label.setText(
                f"Đã import {len(rows)} test case từ {Path(file_path).name}."
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Import file thất bại",
                f"Không đọc được file:\n{exc}",
            )

    def _read_test_file(self, file_path):
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path)

        elif suffix == ".xlsx":
            df = pd.read_excel(path)

        elif suffix == ".json":
            try:
                raw = json.loads(path.read_text(encoding="utf-8-sig"))

                if isinstance(raw, list):
                    df = pd.DataFrame(raw)

                elif isinstance(raw, dict) and isinstance(raw.get("data"), list):
                    df = pd.DataFrame(raw["data"])

                elif isinstance(raw, dict):
                    df = pd.DataFrame([raw])

                else:
                    raise ValueError("JSON phải là object hoặc danh sách object.")

            except json.JSONDecodeError:
                # Hỗ trợ JSON Lines.
                df = pd.read_json(path, lines=True)

        else:
            raise ValueError("Chỉ hỗ trợ file CSV, JSON hoặc XLSX.")

        records = df.to_dict(orient="records")
        result = []

        for source_row, row in enumerate(records, start=1):
            kind = self._normalize_kind(
                self._pick_value(
                    row,
                    ["kind", "loai", "loại", "type", "nhom", "nhóm"],
                    "brand",
                )
            )

            name = self._pick_value(
                row,
                ["name", "ten", "tên", "test_data", "testdata"],
                "",
            )

            brand = self._pick_value(
                row,
                [
                    "brand",
                    "hang",
                    "hãng",
                    "hang_lien_ket",
                    "hãng_liên_kết",
                    "hãng liên kết",
                ],
                "",
            )

            expected_name = self._pick_value(
                row,
                [
                    "expected_name",
                    "expected_ten",
                    "expected_tên",
                    "expected",
                    "ket_qua_mong_doi",
                    "kết_quả_mong_đợi",
                ],
                name,
            )

            expected_brand = self._pick_value(
                row,
                [
                    "expected_brand",
                    "expected_hang",
                    "expected_hãng",
                    "expected_hang_lien_ket",
                    "expected_hãng_liên_kết",
                ],
                brand,
            )

            # Bỏ dòng rỗng.
            if not name:
                continue

            result.append(
                {
                    "source_row": source_row,
                    "kind": kind,
                    "name": name,
                    "brand": brand,
                    "expected_name": expected_name or name,
                    "expected_brand": expected_brand or brand,
                    "status": "Chưa chạy",
                }
            )

        return result

    def _render_import_rows(self):
        self.import_table.setRowCount(len(self.imported_rows))

        for row_index, data in enumerate(self.imported_rows):
            display_kind = "Mẫu xe" if data["kind"] == "model" else "Hãng xe"

            values = [
                display_kind,
                data["name"],
                data["brand"],
                data["expected_name"],
                data["expected_brand"],
                data.get("status", "Chưa chạy"),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if col in (0, 5):
                    item.setTextAlignment(Qt.AlignCenter)

                self.import_table.setItem(row_index, col, item)

    def load_selected_import_row(self, _index=None):
        row = self.import_table.currentRow()

        if row >= 0:
            self._load_import_row(row)

    def _load_import_row(self, row_index):
        if row_index < 0 or row_index >= len(self.imported_rows):
            return

        data = self.imported_rows[row_index]
        self.current_import_row = row_index

        combo_index = self.kind_combo.findData(data["kind"])

        if combo_index >= 0:
            self.kind_combo.setCurrentIndex(combo_index)

        self.name_input.setText(data["name"])
        self.brand_input.setText(data["brand"])

        expected_text = f"Expected tên: {data['expected_name']}"

        if data["kind"] == "model":
            expected_text += f" | Expected hãng: {data['expected_brand']}"

        self.expected_file_label.setText(expected_text)

    @staticmethod
    def _extract_actual_from_steps(result, input_name):
        """
        Lấy Actual tương ứng với dữ liệu file:
        - Actual tên: step mà Expected đúng bằng tên test data.
        - Actual hãng: step có note 'Ant Design dropdown'.
        """
        steps = result.get("steps") or []
        actual_name = ""
        actual_brand = ""

        for step in steps:
            expected = str(step.get("expected", "")).strip()
            actual = str(step.get("actual", "")).strip()
            note = str(step.get("note", "")).casefold()

            if expected.casefold() == str(input_name).strip().casefold() and actual:
                actual_name = actual

            if "ant design dropdown" in note and actual:
                actual_brand = actual

        return actual_name, actual_brand

    def _append_file_comparison_rows(self, result):
        """
        Thêm các dòng Expected(file) <-> Actual(Selenium)
        vào bảng Kết quả CRUD.
        """
        if self.current_import_row is None:
            return True

        if not (0 <= self.current_import_row < len(self.imported_rows)):
            return True

        data = self.imported_rows[self.current_import_row]

        actual_name, actual_brand = self._extract_actual_from_steps(
            result,
            data["name"],
        )

        checks = []

        expected_name = str(data["expected_name"]).strip()
        name_pass = actual_name.strip().casefold() == expected_name.casefold()

        checks.append(
            (
                f"FILE - Expected tên: {expected_name}",
                actual_name or "Không lấy được Actual tên",
                name_pass,
            )
        )

        if data["kind"] == "model":
            expected_brand = str(data["expected_brand"]).strip()
            brand_pass = actual_brand.strip().casefold() == expected_brand.casefold()

            checks.append(
                (
                    f"FILE - Expected hãng: {expected_brand}",
                    actual_brand or "Không lấy được Actual hãng",
                    brand_pass,
                )
            )

        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(checks))

        for offset, (expected, actual, passed) in enumerate(checks):
            row = start_row + offset

            values = [
                str(row + 1),
                expected,
                actual,
                "PASS" if passed else "FAIL",
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)

                if col in (0, 3):
                    item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row, col, item)

        file_passed = all(check[2] for check in checks)

        data["status"] = "PASS" if file_passed else "FAIL"

        status_item = self.import_table.item(self.current_import_row, 5)

        if status_item is not None:
            status_item.setText(data["status"])

        return file_passed

    def _sync_kind_state(self):
        self.brand_input.setEnabled(self.kind_combo.currentData() == "model")

    def run_crud(self):
        if self._thread is not None and self._thread.isRunning():
            return

        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Vui lòng nhập tên test data.")
            return

        kind = self.kind_combo.currentData()
        brand = self.brand_input.text().strip()

        if kind == "model" and not brand:
            self.status_label.setText("Mẫu xe cần nhập hãng liên kết.")
            return

        self.table.setRowCount(0)
        self.progress.setValue(0)
        self.run_button.setEnabled(False)
        self.status_label.setText("Đang chạy CRUD...")

        self._thread = QThread(self)
        self._worker = CrudWorker(
            kind,
            name,
            brand,
            self.cleanup_checkbox.isChecked(),
            self.browser_checkbox.isChecked(),
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log_signal.connect(self.status_label.setText)
        self._worker.progress_signal.connect(self.progress.setValue)
        self._worker.result_signal.connect(self._show_result)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._finish_run)

        self._thread.start()

    def _show_result(self, result):
        steps = result.get("steps") or []
        self.table.setRowCount(len(steps))

        for row, step in enumerate(steps):
            values = [
                str(row + 1),
                str(step.get("expected", "")),
                str(step.get("actual", "")),
                str(step.get("result", "")),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col in (0, 3):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        status = result.get("status", "FAILED")
        message = result.get("message", "")
        error = result.get("error", "")

        # Nếu đang dùng test case import từ file:
        # lấy Actual Selenium và so sánh với Expected trong file.
        file_compare_passed = self._append_file_comparison_rows(result)

        overall_passed = status == "PASSED" and file_compare_passed

        if overall_passed:
            self.progress.setValue(100)

            if self.current_import_row is not None:
                self.status_label.setText(
                    f"PASS - Selenium + Expected trong file đều đúng. {message}"
                )
            else:
                self.status_label.setText(f"PASS - {message}")

        else:
            # Không đổ nguyên Chrome stacktrace lên giao diện vì sẽ đẩy bảng kết quả xuống dưới.
            short_error = ""

            if error:
                first_line = str(error).strip().splitlines()[0]
                short_error = f" | {first_line[:180]}"

            if status == "PASSED" and not file_compare_passed:
                self.status_label.setText(
                    "FAIL - Selenium chạy được nhưng Actual không khớp Expected trong file."
                )
            else:
                self.status_label.setText(f"FAIL - {message}{short_error}")

    def _finish_run(self):
        self.run_button.setEnabled(True)
        self._worker = None
        self._thread = None
