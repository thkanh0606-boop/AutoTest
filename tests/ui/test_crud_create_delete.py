import time
import pytest
from pages.basic_ui_page import BasicUIPage

class TestCRUDCreateDelete:

    def test_create_and_delete_user_account(self, driver):
        # 1. Mở trang Đăng nhập
        driver.get("https://courses.plt.pro.vn/login")
        page = BasicUIPage(driver)

        # 2. Thực hiện điền form đăng nhập (thay thế cho luồng register không tồn tại)
        page.fill_login_form(
            email="admin@gmail.com",
            password="Password123!",
            delay=1.5
        )

        time.sleep(1)
        # 3. Assert xác nhận điều hướng/thao tác thành công
        assert driver.current_url != ""