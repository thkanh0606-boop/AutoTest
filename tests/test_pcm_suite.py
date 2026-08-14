import time
import pytest
from pages.booking_page import BookingPage

class TestPCMAutomationSuite:

    def test_01_login_positive(self, logged_in_driver):
        assert logged_in_driver is not None

    def test_02_navigation_smoke_test(self, logged_in_driver):
        """Test Case 2: Smoke Test điều hướng menu"""
        driver = logged_in_driver
        booking_page = BookingPage(driver)
        
        # Chuyển tab Xe / Vehicle
        nav_success = booking_page.navigate_to_vehicle_tab(delay=2.0)
        assert nav_success is True

    def test_03_booking_table_and_search(self, logged_in_driver):
        """Test Case 3: Kiểm tra bảng booking và thao tác tìm kiếm"""
        driver = logged_in_driver
        booking_page = BookingPage(driver)
        
        # Quay về trang Booking
        booking_page.navigate_to_booking_tab(delay=1.5)
        
        # Thử tìm kiếm
        booking_page.search_booking("Test", delay=1.5)
        
        # Highlight dòng dữ liệu đầu tiên
        is_highlighted = booking_page.highlight_first_row(delay=2.0)
        assert is_highlighted is True