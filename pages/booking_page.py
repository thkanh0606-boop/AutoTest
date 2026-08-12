import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage

class BookingPage(BasePage):
    # Locators
    BOOKING_TAB_LINK = (By.XPATH, "//a[contains(@href, '/booking') or contains(@href, '/bookings') or contains(text(), 'Booking') or contains(text(), 'Đặt lịch')]")
    VEHICLE_TAB_LINK = (By.XPATH, "//a[contains(@href, '/vehicle') or contains(@href, '/vehicles') or contains(text(), 'Xe') or contains(text(), 'Vehicle')]")
    
    SEARCH_INPUT = (By.XPATH, "//input[@type='search' or @placeholder='Search' or contains(@placeholder, 'Tìm kiếm') or contains(@name, 'search')]")
    SEARCH_BTN = (By.XPATH, "//button[contains(text(), 'Tìm') or contains(text(), 'Search') or @type='submit']")
    
    # Hỗ trợ cả Table HTML lẫn Card/List UI
    FIRST_ROW = (By.XPATH, "//table//tbody/tr[1] | //div[contains(@class,'card') or contains(@class,'item') or contains(@class,'row')][1]")
    ALL_ROWS = (By.XPATH, "//table//tbody/tr | //div[contains(@class,'card') or contains(@class,'item')]")

    def navigate_to_booking_tab(self, delay=1.5):
        if "booking" not in self.driver.current_url.lower():
            try:
                self.click(self.BOOKING_TAB_LINK)
            except Exception:
                self.driver.get("https://courses.plt.pro.vn/bookings")
        time.sleep(delay)

    def navigate_to_vehicle_tab(self, delay=1.5):
        try:
            self.click(self.VEHICLE_TAB_LINK)
        except Exception:
            self.driver.get("https://courses.plt.pro.vn/vehicles")
        time.sleep(delay)
        return True

    def highlight_first_row(self, delay=1.5):
        """Cuộn tới dòng đầu tiên và highlight viền đỏ nền vàng rõ ràng."""
        try:
            row = self.find_visible(self.FIRST_ROW)
            # Cuộn màn hình tới phần tử để người dùng nhìn thấy thao tác
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", row)
            self.highlight_element(row, color="yellow", border="3px solid red")
            time.sleep(delay)
            return True
        except Exception:
            # Fallback nếu trang không có dữ liệu bảng: cuộn nhẹ trang web để nhận biết thao tác
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(delay)
            return True

    def search_booking(self, keyword, delay=1.0):
        """Thực hiện tìm kiếm với phản hồi trực quan."""
        inputs = self.driver.find_elements(*self.SEARCH_INPUT)
        if len(inputs) > 0:
            elem = inputs[0]
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
            self.highlight_element(elem, color="cyan", border="2px solid blue")
            elem.clear()
            elem.send_keys(keyword)
            time.sleep(delay)
            
            btns = self.driver.find_elements(*self.SEARCH_BTN)
            if len(btns) > 0:
                btns[0].click()
            else:
                elem.send_keys(Keys.ENTER)
            time.sleep(delay)