import time
import pytest
import logging
from pages.staff_page import StaffPage

@pytest.mark.usefixtures("setup_driver")
class TestStaffManagement:

    @pytest.fixture(autouse=True)
    def setup_page(self):
        self.staff_page = StaffPage(self.driver)

    def test_01_verify_staff_list_page_loaded(self):
        """[READ] Testcase 1: Kiểm tra tải trang Nhân sự thành công"""
        logging.info("Chạy Test 1: Verify Staff List Page Loaded")
        assert self.staff_page.is_page_loaded(), "Trang Nhân sự không tải thành công."

    def test_02_verify_table_data_not_empty(self):
        """[READ] Testcase 2: Kiểm tra dữ liệu bảng hiển thị danh sách nhân sự"""
        logging.info("Chạy Test 2: Verify Table Data Not Empty")
        row_count = self.staff_page.get_table_row_count()
        assert row_count > 0, "Danh sách nhân sự đang bị trống dữ liệu."

    def test_03_verify_pagination_exists(self):
        """[READ] Testcase 3: Kiểm tra sự tồn tại của thanh Phân Trang Ant Design"""
        logging.info("Chạy Test 3: Verify Pagination Exists")
        page_count = self.staff_page.get_pagination_count()
        assert page_count > 0, "Thanh phân trang không tồn tại trên giao diện."

    def test_04_verify_create_button_visible(self):
        """[NAVIGATION] Testcase 4: Kiểm tra nút 'Thêm nhân sự' hiển thị"""
        logging.info("Chạy Test 4: Verify Create Button Visible")
        btn_create = self.driver.find_element(*StaffPage.BTN_GO_TO_CREATE)
        assert btn_create.is_displayed(), "Không tìm thấy nút Thêm nhân sự."

    def test_05_navigate_to_create_staff_form(self):
        """[CREATE] Testcase 5: Chuyển hướng tới trang Form tạo mới thành công (/users/new)"""
        logging.info("Chạy Test 5: Navigate to Create Staff Form")
        self.staff_page.click_add_staff_button()
        assert "/users/new" in self.driver.current_url or "/users/create" in self.driver.current_url, "Không thể chuyển tới trang tạo nhân sự."

    def test_06_validation_error_on_empty_submit(self):
        """[CREATE VALIDATE] Testcase 6: Bật lỗi Validate khi để trống form và bấm Submit"""
        logging.info("Chạy Test 6: Validation Error on Empty Submit")
        if "/users/new" not in self.driver.current_url and "/users/create" not in self.driver.current_url:
            self.staff_page.click_add_staff_button()
        
        self.staff_page.submit_create_form()
        time.sleep(0.5)
        assert self.staff_page.has_form_error_messages(), "Không hiển thị cảnh báo khi để trống trường bắt buộc."

    def test_07_fill_create_staff_form_successfully(self):
        """[CREATE] Testcase 7: Nhập thành công dữ liệu vào Form Thêm mới"""
        logging.info("Chạy Test 7: Fill Create Staff Form Successfully")
        if "/users/new" not in self.driver.current_url and "/users/create" not in self.driver.current_url:
            self.staff_page.click_add_staff_button()
            
        self.staff_page.fill_create_form(
            email=f"test_user_{int(time.time())}@gmail.com",
            password="Password123!",
            confirm_password="Password123!"
        )
        self.staff_page.toggle_is_active_switch()
        
        submit_btn = self.driver.find_element(*StaffPage.BTN_SUBMIT)
        assert submit_btn.is_enabled(), "Nút submit bị vô hiệu hóa."

    def test_08_cancel_create_and_return_to_list(self):
        """[NAVIGATION/CANCEL] Testcase 8: Bấm nút Quay lại để trở về trang Danh sách"""
        logging.info("Chạy Test 8: Cancel Create and Return to List")
        if "/users/new" in self.driver.current_url or "/users/create" in self.driver.current_url:
            self.staff_page.click_back_button()
        
        assert self.staff_page.is_page_loaded(), "Không thể quay lại trang danh sách nhân sự thành công."