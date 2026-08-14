from database.engine import engine, Base, SessionLocal
from database.models import Website, Page, Element, TestCase, TestStep
from core.config import Config

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Đã tạo cấu trúc cơ sở dữ liệu thành công.")

def seed_pcm_data():
    db = SessionLocal()
    
    if db.query(Website).first():
        print("Dữ liệu đã tồn tại. Để cập nhật, vui lòng xóa file autotest.db và chạy lại.")
        db.close()
        return

    # 1. Khởi tạo Website
    pcm_web = Website(name="PCM System", base_url=Config.BASE_URL)
    db.add(pcm_web)
    db.commit()

    # 2. Khởi tạo Pages (Đã bổ sung Quản lý người dùng)
    pages_data = [
        {"name": "Đăng nhập", "url_path": "/login"},
        {"name": "Bảng điều khiển", "url_path": "/dashboard"},
        {"name": "Quản lý đặt xe", "url_path": "/bookings"},
        {"name": "Quản lý xe", "url_path": "/cars"},
        {"name": "Danh mục xe", "url_path": "/catalog"},
        {"name": "Quản lý tài chính", "url_path": "/finance"},
        {"name": "Quản lý người dùng", "url_path": "/users"}
    ]
    for p in pages_data:
        db.add(Page(website_id=pcm_web.id, name=p["name"], url_path=p["url_path"]))
    db.commit()

    # 3. Elements (Đảm bảo >= 35 elements cho T3)
    elements_data = [
        # --- Các element cơ bản (ID 1-10) ---
        {"page_id": 1, "name": "Email Input", "locator_type": "XPATH", "locator_value": "//input[@type='email']"},
        {"page_id": 1, "name": "Password Input", "locator_type": "XPATH", "locator_value": "//input[@type='password']"},
        {"page_id": 1, "name": "Submit Button", "locator_type": "XPATH", "locator_value": "//button[@type='submit']"},
        {"page_id": 2, "name": "Menu Quản lý xe", "locator_type": "XPATH", "locator_value": "//a[@href='/cars']"},
        {"page_id": 3, "name": "Tên khách hàng Text", "locator_type": "XPATH", "locator_value": "//input[@name='customer_name']"},
        {"page_id": 3, "name": "Số điện thoại Text", "locator_type": "XPATH", "locator_value": "//input[@name='customer_phone']"},
        {"page_id": 3, "name": "Trạng thái booking Dropdown", "locator_type": "XPATH", "locator_value": "//select[@name='status']"},
        
        # --- TRANG QUẢN LÝ XE (Page ID = 4) (ID 11-35+) ---
        # Nút chức năng & Tìm kiếm
        {"page_id": 4, "name": "Nút Thêm xe mới", "locator_type": "XPATH", "locator_value": "//button[contains(text(), 'Thêm xe')]"},
        {"page_id": 4, "name": "Ô tìm kiếm xe", "locator_type": "XPATH", "locator_value": "//input[@placeholder='Tìm kiếm biển số...']"},
        {"page_id": 4, "name": "Nút Tìm kiếm", "locator_type": "XPATH", "locator_value": "//button[@id='btn-search']"},
        
        # Form Thêm/Sửa Xe (CRUD)
        {"page_id": 4, "name": "Hãng xe Dropdown", "locator_type": "XPATH", "locator_value": "//select[@name='brand_id']"},
        {"page_id": 4, "name": "Mẫu xe Dropdown (Phụ thuộc)", "locator_type": "XPATH", "locator_value": "//select[@name='model_id']"},
        {"page_id": 4, "name": "Biển số Text", "locator_type": "XPATH", "locator_value": "//input[@name='license_plate']"},
        {"page_id": 4, "name": "Màu sắc Text", "locator_type": "XPATH", "locator_value": "//input[@name='color']"},
        {"page_id": 4, "name": "Giá thuê/ngày Number", "locator_type": "XPATH", "locator_value": "//input[@name='price_per_day']"},
        {"page_id": 4, "name": "Trạng thái xe Dropdown", "locator_type": "XPATH", "locator_value": "//select[@name='car_status']"},
        {"page_id": 4, "name": "Nút Lưu (Save)", "locator_type": "XPATH", "locator_value": "//button[@type='submit' and contains(text(), 'Lưu')]"},
        {"page_id": 4, "name": "Nút Hủy (Cancel)", "locator_type": "XPATH", "locator_value": "//button[contains(text(), 'Hủy')]"},
        
        # Bảng dữ liệu (Table)
        {"page_id": 4, "name": "Bảng danh sách xe", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']"},
        {"page_id": 4, "name": "Cột Biển số", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']//th[contains(text(), 'Biển số')]"},
        {"page_id": 4, "name": "Cột Hãng xe", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']//th[contains(text(), 'Hãng')]"},
        {"page_id": 4, "name": "Cột Trạng thái", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']//th[contains(text(), 'Trạng thái')]"},
        {"page_id": 4, "name": "Hàng đầu tiên trong bảng", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']/tbody/tr[1]"},
        
        # Cột Hành động (Actions) trên bảng
        {"page_id": 4, "name": "Nút Sửa xe (Hàng 1)", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']/tbody/tr[1]//button[contains(@class, 'btn-edit')]"},
        {"page_id": 4, "name": "Nút Xóa xe (Hàng 1)", "locator_type": "XPATH", "locator_value": "//table[@id='car-table']/tbody/tr[1]//button[contains(@class, 'btn-delete')]"},
        {"page_id": 4, "name": "Nút Xác nhận Xóa", "locator_type": "XPATH", "locator_value": "//div[@class='modal']//button[contains(text(), 'Đồng ý')]"},
        
        # Các thông báo lỗi/thành công (Validation/Mismatch)
        {"page_id": 4, "name": "Thông báo Thành công", "locator_type": "XPATH", "locator_value": "//div[contains(@class, 'toast-success')]"},
        {"page_id": 4, "name": "Lỗi: Biển số trùng", "locator_type": "XPATH", "locator_value": "//span[contains(text(), 'Biển số đã tồn tại')]"},
        {"page_id": 4, "name": "Lỗi: Xe đang thuê không được xóa", "locator_type": "XPATH", "locator_value": "//span[contains(text(), 'Không thể xóa xe đang trong trạng thái thuê')]"},
        {"page_id": 4, "name": "Lỗi: Chưa chọn Hãng xe", "locator_type": "XPATH", "locator_value": "//span[contains(text(), 'Vui lòng chọn hãng xe')]"},
        {"page_id": 4, "name": "Lỗi: Bỏ trống Biển số", "locator_type": "XPATH", "locator_value": "//span[contains(text(), 'Biển số không được để trống')]"},
        {"page_id": 4, "name": "Dữ liệu trống (Empty Table)", "locator_type": "XPATH", "locator_value": "//td[contains(text(), 'Không có dữ liệu')]"},
        
        # Phân trang (Pagination)
        {"page_id": 4, "name": "Trang tiếp theo (Next)", "locator_type": "XPATH", "locator_value": "//ul[@class='pagination']//a[contains(text(), 'Next')]"},
        {"page_id": 4, "name": "Trang trước (Prev)", "locator_type": "XPATH", "locator_value": "//ul[@class='pagination']//a[contains(text(), 'Prev')]"},
        {"page_id": 4, "name": "Tổng số xe", "locator_type": "XPATH", "locator_value": "//span[@id='total-cars']"}
    ]
    for e in elements_data:
        db.add(Element(**e))
    db.commit()

    # 4. Test Cases
    tc1 = TestCase(page_id=1, name="TC01 - Đăng nhập hệ thống", description="Kiểm tra luồng đăng nhập thành công")
    tc2 = TestCase(page_id=3, name="TC02 - Nhập form Tạo Booking", description="Kiểm tra tương tác với các trường Text và Dropdown trong Tạo Booking")
    db.add_all([tc1, tc2])
    db.commit()

   # 5. Test Steps (Luồng Quản lý xe)
    steps_data = [
        {"testcase_id": 1, "step_order": 1, "action": "Access the website. Điều hướng tới trang Quản lý xe và nhấn nút Thêm xe mới.", "expected_result": "Form Thêm xe mới hiển thị đầy đủ các trường nhập liệu."},
        {"testcase_id": 1, "step_order": 2, "action": "Access the website. Chọn Hãng xe từ Dropdown.", "expected_result": "Dropdown Mẫu xe tự động tải dữ liệu tương ứng với Hãng xe vừa chọn."},
        {"testcase_id": 1, "step_order": 3, "action": "Access the website. Nhập một Biển số đã tồn tại vào hệ thống và nhấn Lưu.", "expected_result": "Hệ thống chặn việc lưu và hiển thị cảnh báo 'Biển số đã tồn tại'."}
    ]
    for s in steps_data:
        db.add(TestStep(**s))
    db.commit()
    db.close()
    print("Đã hoàn thành công việc T4: Thiết kế TestStep & Seed Dropdown/Text PCM thành công!")

if __name__ == "__main__":
    init_db()
    seed_pcm_data()