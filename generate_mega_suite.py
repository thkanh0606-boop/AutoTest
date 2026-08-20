import pandas as pd
import os

data = []

# --- 1. LOGIN ---
data.extend([
    {"TC ID": "TC_LOGIN_01", "Module": "Login", "Tên Test Case": "Đăng nhập thành công với Admin", "Action": "input", "Locator Type": "pom", "Locator Value": "LoginLocators.EMAIL_INPUT", "Data": "admin@gmail.com", "URL": "/login"},
    {"TC ID": "TC_LOGIN_01", "Module": "Login", "Tên Test Case": "Đăng nhập thành công với Admin", "Action": "input", "Locator Type": "pom", "Locator Value": "LoginLocators.PASSWORD_INPUT", "Data": "123456", "URL": ""},
    {"TC ID": "TC_LOGIN_01", "Module": "Login", "Tên Test Case": "Đăng nhập thành công với Admin", "Action": "click", "Locator Type": "pom", "Locator Value": "LoginLocators.LOGIN_BUTTON", "Data": "", "URL": ""},
    {"TC ID": "TC_LOGIN_01", "Module": "Login", "Tên Test Case": "Đăng nhập thành công với Admin", "Action": "assert_text", "Locator Type": "pom", "Locator Value": "DashboardLocators.HEADER_TITLE", "Data": "Bảng điều khiển", "URL": ""}
])

# --- 2. ROUTING (NAVIGATION 50 cases) ---
for i in range(1, 26):
    data.append({"TC ID": f"TC_NAV_{i:02d}", "Module": "Navigation", "Tên Test Case": f"Kiểm tra điều hướng tới trang Booking {i}", "Action": "route_smoke", "Locator Type": "", "Locator Value": "", "Data": "", "URL": "/bookings"})
for i in range(26, 51):
    data.append({"TC ID": f"TC_NAV_{i:02d}", "Module": "Navigation", "Tên Test Case": f"Kiểm tra điều hướng tới trang Fleet {i}", "Action": "route_smoke", "Locator Type": "", "Locator Value": "", "Data": "", "URL": "/cars"})

# --- 3. FILTERING BOOKINGS (30 cases) ---
for i in range(1, 31):
    data.append({"TC ID": f"TC_BOOKING_FILTER_{i:02d}", "Module": "Booking", "Tên Test Case": f"Kiểm tra lọc danh sách chuyến đi - Bộ lọc {i}", "Action": "input", "Locator Type": "xpath", "Locator Value": f"//input[@id='filter-{i}']", "Data": f"Gia tri {i}", "URL": "/bookings"})
    data.append({"TC ID": f"TC_BOOKING_FILTER_{i:02d}", "Module": "Booking", "Tên Test Case": f"Kiểm tra lọc danh sách chuyến đi - Bộ lọc {i}", "Action": "click", "Locator Type": "xpath", "Locator Value": f"//button[@id='btn-search']", "Data": "", "URL": ""})

# --- 4. FLEET STATUS CHECK (40 cases) ---
for i in range(1, 41):
    data.append({"TC ID": f"TC_FLEET_STATUS_{i:02d}", "Module": "Fleet", "Tên Test Case": f"Kiểm tra trạng thái xe ID-{i}", "Action": "assert_text", "Locator Type": "css selector", "Locator Value": f".car-status-{i}", "Data": "Sẵn sàng", "URL": "/cars"})

# --- 5. PCM SCENARIOS (5 cases) ---
for i in range(1, 6):
    data.append({"TC ID": f"TC_PCM_{i:02d}", "Module": "Business Logic", "Tên Test Case": f"Kiểm thử nghiệp vụ PCM luồng {i}", "Action": "pcm_scenario", "Locator Type": "", "Locator Value": "", "Data": "", "URL": ""})

df = pd.DataFrame(data)
output_path = r'C:\AutoTest-AI\AutoTest\Demo_Mega_Suite_V2.xlsx'
df.to_excel(output_path, index=False)
print(f"Created: {output_path} with {len(df)} rows.")
