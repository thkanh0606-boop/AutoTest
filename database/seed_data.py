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

    # 2. Khởi tạo Pages
    pages_data = [
        {"name": "Đăng nhập", "url_path": "/login"},
        {"name": "Bảng điều khiển", "url_path": "/dashboard"},
        {"name": "Quản lý đặt xe", "url_path": "/bookings"},
        {"name": "Quản lý xe", "url_path": "/cars"},
        {"name": "Danh mục xe", "url_path": "/catalog"},
        {"name": "Quản lý tài chính", "url_path": "/finance"}
    ]
    for p in pages_data:
        db.add(Page(website_id=pcm_web.id, name=p["name"], url_path=p["url_path"]))
    db.commit()

    # 3. Elements (Bao gồm Dropdown/Text PCM theo yêu cầu T4)
    elements_data = [
        {"page_id": 1, "name": "Email Input", "locator_type": "XPATH", "locator_value": "//input[@type='email']"},
        {"page_id": 1, "name": "Password Input", "locator_type": "XPATH", "locator_value": "//input[@type='password']"},
        {"page_id": 1, "name": "Submit Button", "locator_type": "XPATH", "locator_value": "//button[@type='submit']"},
        {"page_id": 3, "name": "Tên khách hàng Text", "locator_type": "XPATH", "locator_value": "//input[@name='customer_name']"},
        {"page_id": 3, "name": "Số điện thoại Text", "locator_type": "XPATH", "locator_value": "//input[@name='customer_phone']"},
        {"page_id": 3, "name": "Trạng thái booking Dropdown", "locator_type": "XPATH", "locator_value": "//div[contains(@class, 'select-status')]"},
        {"page_id": 3, "name": "Phương thức thanh toán Dropdown", "locator_type": "XPATH", "locator_value": "//div[contains(@class, 'select-payment')]"}
    ]
    for e in elements_data:
        db.add(Element(**e))
    db.commit()

    # 4. Test Cases
    tc1 = TestCase(page_id=1, name="TC01 - Đăng nhập hệ thống", description="Kiểm tra luồng đăng nhập thành công")
    tc2 = TestCase(page_id=3, name="TC02 - Nhập form Tạo Booking", description="Kiểm tra tương tác với các trường Text và Dropdown trong Tạo Booking")
    db.add_all([tc1, tc2])
    db.commit()

    # 5. Test Steps (Chi tiết các bước thực hiện & Expected Result)
    steps_data = [
        {"testcase_id": tc1.id, "step_order": 1, "action": "Access the website. Nhập email hợp lệ vào Email Input.", "expected_result": "Dữ liệu email hiển thị chính xác trong ô input."},
        {"testcase_id": tc1.id, "step_order": 2, "action": "Access the website. Nhập mật khẩu hợp lệ vào Password Input.", "expected_result": "Mật khẩu bị ẩn dưới dạng ký tự sao."},
        {"testcase_id": tc1.id, "step_order": 3, "action": "Access the website. Click vào Submit Button.", "expected_result": "Hệ thống xác thực và chuyển hướng thành công."},
        {"testcase_id": tc2.id, "step_order": 1, "action": "Access the website. Click vào nút + Tạo booking.", "expected_result": "Giao diện Tạo booking hiện ra."},
        {"testcase_id": tc2.id, "step_order": 2, "action": "Access the website. Nhập tên vào ô Tên khách hàng Text.", "expected_result": "Text được điền vào ô thành công."},
        {"testcase_id": tc2.id, "step_order": 3, "action": "Access the website. Click vào ô Trạng thái booking Dropdown và chọn giá trị.", "expected_result": "Dropdown hiển thị danh sách và nhận đúng giá trị vừa chọn."}
    ]
    for s in steps_data:
        db.add(TestStep(**s))
    
    db.commit()
    db.close()
    print("Đã hoàn thành công việc T4: Thiết kế TestStep & Seed Dropdown/Text PCM thành công!")

if __name__ == "__main__":
    init_db()
    seed_pcm_data()