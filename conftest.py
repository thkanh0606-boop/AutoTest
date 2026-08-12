import pytest
from core.driver_factory import DriverFactory

@pytest.fixture(scope="function")
def driver():
    """Fixture tạo và đóng WebDriver tự động cho từng test case của PyTest"""
    _driver = DriverFactory.create_driver(headless=False)
    yield _driver
    _driver.quit()
    