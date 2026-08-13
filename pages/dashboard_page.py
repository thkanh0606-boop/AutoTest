from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from core.config import Config
from locators.dashboard_locators import DashboardLocators
from pages.login_page import LoginPage


class DashboardPage:
    URL = "https://courses.plt.pro.vn/dashboard"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)

    def open(self):
        self.driver.get(self.URL)
        if self._is_login_form_visible():
            self._login_and_reopen_dashboard()
        self.wait_for_loaded()

    def _is_login_form_visible(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            return True
        except Exception:
            return False

    def _login_and_reopen_dashboard(self):
        login_page = LoginPage(self.driver)
        login_page.load(Config.BASE_URL)
        login_page.execute_login(Config.TEST_EMAIL, Config.TEST_PASSWORD)
        self.wait.until(lambda browser: "login" not in browser.current_url.lower())
        self.driver.get(self.URL)

    def wait_for_loaded(self):
        self.wait.until(EC.presence_of_element_located(DashboardLocators.MAIN))
        self.wait.until(EC.visibility_of_element_located(DashboardLocators.HERO_TITLE))
        return True

    def current_url(self):
        return self.driver.current_url

    def title_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.HERO_TITLE)).text.strip()

    def header_title_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.HEADER_TITLE)).text.strip()

    def hero_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.HERO_SECTION)).text.strip()

    def card_text(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text.strip()

    def stat_cards(self):
        return {
            "rented": self.card_text(DashboardLocators.KPI_RENTED_CARD),
            "ready": self.card_text(DashboardLocators.KPI_READY_CARD),
            "pickup": self.card_text(DashboardLocators.KPI_PICKUP_CARD),
            "return": self.card_text(DashboardLocators.KPI_RETURN_CARD),
            "overdue": self.card_text(DashboardLocators.KPI_OVERDUE_CARD),
            "maintenance": self.card_text(DashboardLocators.KPI_MAINTENANCE_CARD),
        }

    def quick_actions_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.QUICK_ACTIONS_SECTION)).text.strip()

    def booking_list_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.BOOKING_LIST_SECTION)).text.strip()

    def sidebar_menu_text(self):
        return self.wait.until(EC.visibility_of_element_located(DashboardLocators.SIDEBAR_MENU)).text.strip()

    def click_and_wait_url(self, locator, expected_path: str):
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        self.wait.until(EC.url_contains(expected_path))
        return self.driver.current_url

    def open_quick_booking_list(self):
        return self.click_and_wait_url(DashboardLocators.QUICK_BOOKING_LIST, "/bookings")

    def open_quick_fleet(self):
        return self.click_and_wait_url(DashboardLocators.QUICK_FLEET, "/cars")

    def open_quick_finance(self):
        return self.click_and_wait_url(DashboardLocators.QUICK_FINANCE, "/finance")

    def open_deep_link(self, path: str):
        self.driver.get(f"https://courses.plt.pro.vn{path}")
        self.wait.until(EC.url_contains(path))
        return self.driver.current_url

    def go_dashboard_from_menu(self):
        return self.click_and_wait_url(DashboardLocators.NAV_DASHBOARD, "/dashboard")
