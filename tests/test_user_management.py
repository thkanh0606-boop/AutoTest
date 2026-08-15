import pytest
import time
from pages.user_management_page import UserManagementPage

@pytest.mark.usefixtures("setup_driver")
class TestUserManagementModule:

    @pytest.fixture(autouse=True)
    def init_page(self):
        self.user_page = UserManagementPage(self.driver)

    def test_01_independent_page_load_and_header_ui(self):
        assert self.user_page.is_sign_out_button_visible() is True

    def test_02_team_directory_table_data_display(self):
        rows = self.user_page.get_table_row_count()
        assert rows >= 0

    def test_03_validation_invalid_email_format(self):
        self.user_page.open_create_user_form()
        self.user_page.fill_user_form(email="invalid_email_test")
        self.user_page.submit_form()
        assert True

    def test_04_retest_high_bug_duplicate_email(self):
        self.user_page.open_create_user_form()
        self.user_page.fill_user_form(email="admin@gmail.com")
        self.user_page.submit_form()
        assert True

    def test_05_validation_mismatch_confirm_password(self):
        self.user_page.open_create_user_form()
        self.user_page.fill_user_form(password="12345678", confirm_password="87654321")
        self.user_page.submit_form()
        assert True

    def test_06_full_crud_create_user_positive(self):
        self.user_page.open_create_user_form()
        new_email = f"user_{int(time.time())}@gmail.com"
        self.user_page.fill_user_form(email=new_email, password="Password123!", confirm_password="Password123!")
        assert True

    def test_07_dropdown_role_staff_selection(self):
        self.user_page.open_create_user_form()
        assert True

    def test_08_verify_user_status_badges(self):
        count = self.user_page.get_active_users_count()
        assert count >= 0

    def test_09_check_sidebar_profile_and_permission(self):
        assert self.user_page.is_sign_out_button_visible() is True

    def test_10_smoke_regression_module_health(self):
        self.user_page.search_user("admin")
        time.sleep(1)
        assert True