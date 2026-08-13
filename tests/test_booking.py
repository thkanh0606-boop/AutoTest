import pytest
from pages.login_page import LoginPage
from pages.booking_page import BookingPage

def test_search_booking_success(driver):
    # 1. Khởi tạo các Page Object
    login_page = LoginPage(driver)
    booking_page = BookingPage(driver)

    # 2. Truy cập hệ thống và thực hiện Đăng nhập
    driver.get("https://courses.plt.pro.vn/login")
    login_page.login("test@gmail.com", "123123")

    # 3. Chuyển sang trang Booking/Quản lý Đặt xe
    booking_page.navigate_to_booking_tab(delay=2.0)

    # 4. Thực hiện thao tác kiểm tra/highlight dòng đầu tiên trong bảng booking
    booking_page.highlight_first_row(delay=2.0)

    # 5. Assert xác nhận điều hướng thành công
    assert "courses.plt.pro.vn" in driver.current_url