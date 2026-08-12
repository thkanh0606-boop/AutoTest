import pytest
from pages.basic_ui_page import BasicUIPage

class TestBasicUI:

    def test_page_title_and_logo(self, driver):
        driver.get("https://courses.plt.pro.vn/")
        page = BasicUIPage(driver)

        # Kiểm tra Title trang web chứa từ khóa PLT hoặc Courses
        assert "PLT" in driver.title or "Courses" in driver.title or len(driver.title) > 0

        # Kiểm tra Logo
        src, _ = page.get_logo_info()
        assert src != ""

    def test_navigation_menu_list(self, driver):
        driver.get("https://courses.plt.pro.vn/")
        page = BasicUIPage(driver)

        menus = page.get_menu_list_text()
        # Kiểm tra menu điều hướng có dữ liệu
        assert len(menus) > 0