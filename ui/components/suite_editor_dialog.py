import uuid
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QMessageBox,
    QHeaderView,
    QAbstractItemView
)

from core.test_result_repository import TestResultRepository

# ==========================================
# CÁC DANH MỤC LỰA CHỌN MẶC ĐỊNH (DROPDOWNS)
# ==========================================
COMMON_TC_IDS = ["", "TC_01", "TC_02", "TC_03", "TC_04", "TC_LOGIN_01", "TC_NAV_01", "TC_BOOKING_01", "TC_FLEET_01"]
COMMON_MODULES = ["", "Login", "Dashboard", "Booking", "Fleet", "Vehicle Catalog", "User", "Finance", "Navigation"]
COMMON_TITLES = ["", "Kiểm tra đăng nhập thành công", "Kiểm tra hiển thị bảng điều khiển", "Kiểm tra chức năng tìm kiếm", "Kiểm tra thêm mới thành công", "Kiểm tra xóa thành công", "Kiểm tra điều hướng", "Kiểm thử luồng nghiệp vụ"]
ACTION_TYPES = ["", "click", "input", "assert_text", "route_smoke", "pcm_scenario"]
LOCATOR_TYPES = ["", "pom", "xpath", "css selector", "id", "name"]
COMMON_DATA = ["", "admin@gmail.com", "123456", "Bảng điều khiển", "Sẵn sàng", "Đang thuê"]
COMMON_URLS = ["", "/dashboard", "/login", "/bookings", "/cars", "/users"]

def _get_all_locators() -> list[str]:
    """Tự động quét các biến POM có sẵn để người dùng chọn dễ dàng."""
    locs = [""]
    try:
        from locators.dashboard_locators import DashboardLocators
        locs.extend([f"DashboardLocators.{a}" for a in dir(DashboardLocators) if not a.startswith('_')])
    except: pass
    try:
        from locators.car_management_locators import CarManagementLocators
        locs.extend([f"CarManagementLocators.{a}" for a in dir(CarManagementLocators) if not a.startswith('_')])
    except: pass
    try:
        from locators.pcm_locators import PCMLocators
        locs.extend([f"PCMLocators.{a}" for a in dir(PCMLocators) if not a.startswith('_')])
    except: pass
    # Một vài xpath / css thông dụng
    locs.extend(["//button[@type='submit']", "//input[@name='email']", "//input[@name='password']", ".btn-primary"])
    return locs

class SuiteEditorDialog(QDialog):
    """
    Cửa sổ Giao diện (Dialog) cho phép người dùng Tạo/Chỉnh sửa Test Suite
    giống như thao tác trên một bảng tính Excel.
    Khi lưu, dữ liệu sẽ được ghi thẳng vào Database SQLite (TestResultRepository).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo Test Suite Mới")
        self.resize(900, 600)
        self.repository = TestResultRepository()
        self._build_ui()

    def _build_ui(self):
        """Khởi tạo toàn bộ giao diện: Tên Suite, Bảng tính, Các nút bấm."""
        layout = QVBoxLayout(self)

        # --- 1. Dòng trên cùng: Tên Suite ---
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Tên Suite:"))
        
        self.suite_name_input = QLineEdit()
        self.suite_name_input.setPlaceholderText("Ví dụ: Kịch bản Đăng nhập thành công...")
        header_layout.addWidget(self.suite_name_input, 1)
        
        layout.addLayout(header_layout)

        # --- 2. Ở giữa: Bảng Grid (TableWidget) hiển thị Test Case ---
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "TC ID", "Module", "Tên Test Case", "Action", 
            "Locator Type", "Locator Value", "Data", "URL"
        ])
        
        # Chọn cả dòng khi click
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Chỉnh độ rộng các cột cho đẹp
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Tên Test Case (cần rộng)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Locator Value (cần rộng)
        
        layout.addWidget(self.table, 1)

        # --- 3. Dòng dưới cùng: Các nút thao tác ---
        actions_layout = QHBoxLayout()
        
        # Nút Thêm dòng / Xóa dòng
        add_btn = QPushButton("Thêm dòng")
        add_btn.clicked.connect(self._add_row)
        
        remove_btn = QPushButton("Xóa dòng")
        remove_btn.clicked.connect(self._remove_row)
        
        # Nút Lưu / Hủy
        save_btn = QPushButton("Lưu Suite")
        save_btn.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold;")
        save_btn.clicked.connect(self._save_suite)
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        # Xếp các nút vào layout
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(remove_btn)
        actions_layout.addStretch()  # Đẩy các nút Lưu/Hủy về bên phải
        actions_layout.addWidget(cancel_btn)
        actions_layout.addWidget(save_btn)
        
        layout.addLayout(actions_layout)

        # Khởi tạo sẵn 1 dòng trống đầu tiên khi mới mở cửa sổ
        self._add_row()

    def _add_row(self):
        """Thêm một dòng trống mới vào cuối bảng."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột TC ID (Cột 0) --
        tc_combo = QComboBox()
        tc_combo.setEditable(True)
        tc_combo.addItems(COMMON_TC_IDS)
        self.table.setCellWidget(row, 0, tc_combo)

        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột Module (Cột 1) --
        mod_combo = QComboBox()
        mod_combo.setEditable(True)
        mod_combo.addItems(COMMON_MODULES)
        self.table.setCellWidget(row, 1, mod_combo)

        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột Tên Test Case (Cột 2) --
        title_combo = QComboBox()
        title_combo.setEditable(True)
        title_combo.addItems(COMMON_TITLES)
        self.table.setCellWidget(row, 2, title_combo)

        # -- Gắn Dropdown cho cột Action (Cột 3) --
        action_combo = QComboBox()
        action_combo.addItems(ACTION_TYPES)
        self.table.setCellWidget(row, 3, action_combo)

        # -- Gắn Dropdown cho cột Locator Type (Cột 4) --
        loc_type_combo = QComboBox()
        loc_type_combo.addItems(LOCATOR_TYPES)
        self.table.setCellWidget(row, 4, loc_type_combo)
        
        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột Locator Value (Cột 5) --
        loc_val_combo = QComboBox()
        loc_val_combo.setEditable(True)
        loc_val_combo.addItems(_get_all_locators())
        self.table.setCellWidget(row, 5, loc_val_combo)

        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột Data (Cột 6) --
        data_combo = QComboBox()
        data_combo.setEditable(True)
        data_combo.addItems(COMMON_DATA)
        self.table.setCellWidget(row, 6, data_combo)

        # -- Gắn Dropdown CÓ THỂ CHỈNH SỬA cho cột URL (Cột 7) --
        url_combo = QComboBox()
        url_combo.setEditable(True)
        url_combo.addItems(COMMON_URLS)
        self.table.setCellWidget(row, 7, url_combo)

    def _remove_row(self):
        """Xóa các dòng đang được chọn trong bảng."""
        # Lấy danh sách index các dòng đang được chọn
        selected_rows = set(item.row() for item in self.table.selectedItems())
        # Phải xóa từ dưới lên trên để không bị sai lệch index
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

    def _get_cell_value(self, row: int, col: int) -> str:
        """Hàm phụ trợ để lấy giá trị text của một ô tại dòng/cột bất kỳ."""
        # Kiểm tra xem ô đó là QComboBox (Dropdown) hay ô Text thường
        widget = self.table.cellWidget(row, col)
        if isinstance(widget, QComboBox):
            return widget.currentText().strip()
            
        item = self.table.item(row, col)
        return item.text().strip() if item else ""

    def _save_suite(self):
        """Đọc toàn bộ dữ liệu trên bảng, chuyển thành List[dict] và lưu vào DB."""
        name = self.suite_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Tên Suite!")
            return

        cases = []
        # Duyệt qua từng dòng của bảng
        for row in range(self.table.rowCount()):
            # Lấy mã TC ID (nếu bỏ trống thì bỏ qua dòng đó)
            tc_id = self._get_cell_value(row, 0)
            if not tc_id:
                continue

            # Lấy các cột quan trọng
            action = self._get_cell_value(row, 3)
            loc_type = self._get_cell_value(row, 4)
            loc_value = self._get_cell_value(row, 5)
            
            # (Đặc biệt) Xử lý tự động map các biến POM (như LoginLocators.EMAIL) sang By.XXX
            resolved_loc_type, resolved_loc_value = loc_type, loc_value
            if loc_type.lower() == "pom":
                # Import hàm từ core.suite_loader để dịch chuỗi POM
                from core.suite_loader import _resolve_pom_locator
                resolved_loc_type, resolved_loc_value = _resolve_pom_locator(loc_value)

            # Đóng gói dữ liệu của 1 Test Case vào một cuốn từ điển (Dict)
            case_dict = {
                "tc_id": tc_id,
                "module": self._get_cell_value(row, 1),
                "title": self._get_cell_value(row, 2),
                "area": self._get_cell_value(row, 1),  # Dùng module làm area luôn
                "expected": self._get_cell_value(row, 6),
                "source_sheet": "GUI Builder",
                "page_key": ""
            }

            # Chỉ đưa vào Dict những trường có nhập giá trị
            if action:
                case_dict["action_type"] = action
            if resolved_loc_type:
                case_dict["locator_type"] = resolved_loc_type
            if resolved_loc_value:
                case_dict["locator_value"] = resolved_loc_value
            if self._get_cell_value(row, 6):
                case_dict["expected_result"] = self._get_cell_value(row, 6)
            if self._get_cell_value(row, 7):
                case_dict["url"] = self._get_cell_value(row, 7)

            cases.append(case_dict)

        # Kiểm tra xem có Test Case nào hợp lệ không
        if not cases:
            QMessageBox.warning(self, "Lỗi", "Suite chưa có Test Case nào (cần điền TC ID)!")
            return

        # Lưu thẳng vào cơ sở dữ liệu SQLite
        try:
            suite_key = f"gui:{uuid.uuid4().hex[:8]}"
            self.repository.save_suite_definition(
                name=name,
                cases=cases,
                source_path="GUI Builder",
                suite_key=suite_key
            )
            QMessageBox.information(self, "Thành công", f"Đã lưu Suite '{name}'!")
            self.accept()  # Đóng cửa sổ dialog
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu Suite: {e}")
