# Ví dụ logic Check & Highlight Element
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_and_highlight_element(driver, locator_type, locator_value, fallback_value=None):
    by_map = {
        "XPATH": By.XPATH,
        "ID": By.ID,
        "NAME": By.NAME,
        "CSS": By.CSS_SELECTOR,
        "CLASS": By.CLASS_NAME
    }
    
    by_type = by_map.get(locator_type.upper(), By.XPATH)
    element = None
    used_fallback = False

    try:
        # 1. Thử Primary Locator
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((by_type, locator_value))
        )
    except Exception:
        # 2. Thử Fallback Locator nếu có
        if fallback_value:
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, fallback_value))
                )
                used_fallback = True
            except Exception:
                element = None

    if element:
        # 3. Selenium Highlight Element
        driver.execute_script(
            "arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='yellow';", 
            element
        )
        status = "PASS (Fallback)" if used_fallback else "PASS"
        return True, status, f"Tìm thấy element ({'Fallback' if used_fallback else 'Primary'})"
    else:
        # 4. Chụp ảnh khi lỗi
        screenshot_path = f"logs/screenshots/fail_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        return False, "FAIL", screenshot_path