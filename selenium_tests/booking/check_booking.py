import os
import sys
import time

from selenium.webdriver.common.by import By

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

from core.driver_factory import DriverFactory
from core.test_contract import TestContract


page = next(
    p for p in TestContract.pages
    if p.key == "plt_booking"
)

print("=" * 60)
print("PAGE :", page.name)
print("URL  :", page.url)
print("=" * 60)

driver = DriverFactory.create_driver(
    headless=False,
    keep_session=True
)

try:
    driver.get(page.url)

    print("Chrome đã mở.")

    time.sleep(5)

    print("CURRENT URL:")
    print(driver.current_url)

    print()
    print("TITLE:")
    print(driver.title)

    body = driver.find_element(
        By.TAG_NAME,
        "body"
    )

    print()
    print("BODY VISIBLE:")
    print(body.is_displayed())

    input("\nNhấn Enter để đóng Chrome...")

finally:
    driver.quit()