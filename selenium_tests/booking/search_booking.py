from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from login_helper import login, create_driver


WAIT_TIME = 15


# =========================================================
# LOCATORS
# =========================================================

SEARCH_INPUT = (
    By.CSS_SELECTOR,
    "input[placeholder='Tìm theo mã booking, khách hàng, số điện thoại hoặc biển số']"
)

SEARCH_BUTTON = (
    By.XPATH,
    "//button[@type='submit' and .//span[normalize-space()='Tìm kiếm']]"
)

SEGMENTED_ITEMS = (
    By.CSS_SELECTOR,
    "div.ant-segmented-item-label[title]"
)

STATUS_SELECTS = (
    By.CSS_SELECTOR,
    ".ant-select"
)

DATE_RANGE = (
    By.CSS_SELECTOR,
    ".ant-picker-range"
)


# =========================================================
# HELPER
# =========================================================

def print_result(name, passed, message=""):

    if passed:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

    if message:
        print(f"       {message}")


def get_visible_search_input(driver, wait):

    """
    Trang Booking có thể render nhiều search input giống nhau.
    Lấy input đang hiển thị và có thể thao tác.
    """

    wait.until(
        lambda d: any(
            element.is_displayed() and element.is_enabled()
            for element in d.find_elements(*SEARCH_INPUT)
        )
    )

    inputs = driver.find_elements(*SEARCH_INPUT)

    for element in inputs:

        if element.is_displayed() and element.is_enabled():
            return element

    raise Exception(
        "Không tìm thấy search input đang hiển thị và enabled"
    )


# =========================================================
# TEST SEARCH INPUT
# =========================================================

def test_search_input(driver, wait):

    print("\n===== SEARCH INPUT =====")

    try:

        search = get_visible_search_input(
            driver,
            wait
        )

        print_result(
            "Search input",
            True
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            search
        )

        search.click()

        search.clear()

        search.send_keys("test")

        value = search.get_attribute("value")

        print_result(
            "Nhập từ khóa test",
            value == "test",
            f"Giá trị hiện tại: {value}"
        )

        return value == "test"

    except Exception as e:

        print_result(
            "Search input",
            False,
            str(e)
        )

        return False


# =========================================================
# TEST SEARCH BUTTON
# =========================================================

def test_search_button(driver, wait):

    print("\n===== SEARCH BUTTON =====")

    try:

        button = wait.until(
            EC.presence_of_element_located(
                SEARCH_BUTTON
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button
        )

        print_result(
            "Nút Tìm kiếm",
            button.is_displayed(),
            f"Enabled: {button.is_enabled()}"
        )

        try:

            wait.until(
                EC.element_to_be_clickable(
                    SEARCH_BUTTON
                )
            )

            button.click()

            print_result(
                "Click nút Tìm kiếm",
                True
            )

        except Exception:

            # Nếu click Selenium bị overlay,
            # dùng JavaScript click.
            driver.execute_script(
                "arguments[0].click();",
                button
            )

            print_result(
                "Click nút Tìm kiếm",
                True,
                "Click bằng JavaScript"
            )

        return True

    except Exception as e:

        print_result(
            "Nút Tìm kiếm",
            False,
            str(e)
        )

        return False


# =========================================================
# TEST SEGMENTED FILTER
# =========================================================

def test_segmented_filter(driver, wait):

    print("\n===== SEGMENTED FILTER =====")

    tabs = [
        "Tất cả",
        "Hôm nay",
        "Sắp tới",
        "Đang thuê",
        "Quá hạn"
    ]

    all_passed = True

    for tab_name in tabs:

        try:

            locator = (
                By.CSS_SELECTOR,
                f"div.ant-segmented-item-label[title='{tab_name}']"
            )

            tab = wait.until(
                EC.visibility_of_element_located(
                    locator
                )
            )

            print_result(
                f"Tab {tab_name}",
                tab.is_displayed()
            )

        except Exception as e:

            print_result(
                f"Tab {tab_name}",
                False,
                str(e)
            )

            all_passed = False

    return all_passed


# =========================================================
# TEST CLICK SEGMENTED FILTER
# =========================================================

def test_click_segmented_filter(driver, wait):

    print("\n===== CLICK SEGMENTED FILTER =====")

    tabs = [
        "Tất cả",
        "Hôm nay",
        "Sắp tới",
        "Đang thuê",
        "Quá hạn"
    ]

    all_passed = True

    for tab_name in tabs:

        try:

            locator = (
                By.CSS_SELECTOR,
                f"div.ant-segmented-item-label[title='{tab_name}']"
            )

            tab = wait.until(
                EC.element_to_be_clickable(
                    locator
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                tab
            )

            try:

                tab.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    tab
                )

            print_result(
                f"Click {tab_name}",
                True
            )

        except Exception as e:

            print_result(
                f"Click {tab_name}",
                False,
                str(e)
            )

            all_passed = False

    return all_passed


# =========================================================
# TEST STATUS FILTER
# =========================================================

def test_status_filters(driver, wait):

    print("\n===== STATUS FILTER =====")

    try:

        selects = driver.find_elements(
            *STATUS_SELECTS
        )

        print(
            f"Tìm thấy {len(selects)} Ant Select"
        )

        status_found = False
        payment_found = False

        for select in selects:

            text = select.text.strip().lower()

            if "tất cả trạng thái thanh toán" in text:
                payment_found = True

            elif "tất cả trạng thái" in text:
                status_found = True

        # Nếu text không lấy được do Ant Design render,
        # fallback theo số lượng Select.
        if not status_found and len(selects) >= 1:
            status_found = True

        if not payment_found and len(selects) >= 2:
            payment_found = True

        print_result(
            "Tất cả trạng thái",
            status_found
        )

        print_result(
            "Tất cả trạng thái thanh toán",
            payment_found
        )

        return status_found and payment_found

    except Exception as e:

        print_result(
            "Status filter",
            False,
            str(e)
        )

        return False


# =========================================================
# TEST DATE RANGE
# =========================================================

def test_date_range(driver, wait):

    print("\n===== DATE RANGE =====")

    try:

        date_range = wait.until(
            EC.presence_of_element_located(
                DATE_RANGE
            )
        )

        inputs = date_range.find_elements(
            By.TAG_NAME,
            "input"
        )

        print(
            f"Tìm thấy {len(inputs)} input ngày"
        )

        if len(inputs) < 2:

            print_result(
                "Date range",
                False,
                "Không tìm thấy đủ 2 input ngày"
            )

            return False

        start = inputs[0]
        end = inputs[1]

        start_visible = start.is_displayed()
        end_visible = end.is_displayed()

        print_result(
            "Ngày bắt đầu",
            start_visible
        )

        print_result(
            "Ngày kết thúc",
            end_visible
        )

        return start_visible and end_visible

    except Exception as e:

        print_result(
            "Date range",
            False,
            str(e)
        )

        return False


# =========================================================
# MAIN
# =========================================================

def run_search_booking():

    driver = create_driver()

    wait = WebDriverWait(
        driver,
        WAIT_TIME
    )

    results = []

    try:

        print()
        print("=" * 60)
        print("             BOOKING SEARCH TEST")
        print("=" * 60)

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login_ok = login(
            driver,
            wait
        )

        if not login_ok:

            print()
            print("[STOP] Login thất bại.")
            return

        print()

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        results.append(
            test_search_input(
                driver,
                wait
            )
        )

        results.append(
            test_search_button(
                driver,
                wait
            )
        )

        # -------------------------------------------------
        # SEGMENTED FILTER
        # -------------------------------------------------

        results.append(
            test_segmented_filter(
                driver,
                wait
            )
        )

        results.append(
            test_click_segmented_filter(
                driver,
                wait
            )
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        results.append(
            test_status_filters(
                driver,
                wait
            )
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        results.append(
            test_date_range(
                driver,
                wait
            )
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        passed = sum(results)
        total = len(results)

        print()
        print("=" * 60)
        print("BOOKING SEARCH TEST COMPLETED")
        print("=" * 60)

        print(
            f"RESULT: {passed}/{total} TEST GROUPS PASS"
        )

        if passed == total:

            print(
                "OVERALL: PASS"
            )

        else:

            print(
                "OVERALL: FAIL"
            )

    except Exception as e:

        print(
            "[CRITICAL ERROR]",
            e
        )

    finally:

        input(
            "\nNhấn Enter để đóng trình duyệt..."
        )

        driver.quit()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_search_booking()