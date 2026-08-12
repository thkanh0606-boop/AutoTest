# Linh - Tự động đăng nhập trước khi kiểm thử Danh mục xe

Trang `https://courses.plt.pro.vn/cars/catalog` yêu cầu Firebase Auth.

Luồng mới:

1. Người dùng bấm **Kiểm tra locator** hoặc **Chạy kiểm tra CRUD**.
2. Selenium mở `/cars/catalog`.
3. Nếu bị chuyển về `/login`, AutoTest tự đọc tài khoản từ `.autotest.env`.
4. AutoTest tự điền Email + Mật khẩu và bấm **Đăng nhập**.
5. Sau khi Firebase Auth ổn định, AutoTest tự mở lại `/cars/catalog`.
6. Chỉ khi vào đúng **Danh mục xe** thì Selenium mới bắt đầu locator/CRUD.
7. Chrome profile vẫn được giữ trong `data/selenium_profile_linh/` để tái sử dụng session.

## Bảo mật

- `.autotest.env` chứa tài khoản thật và đã nằm trong `.gitignore`.
- `.autotest.env.example` chỉ chứa placeholder và có thể push GitHub.
- Có thể dùng biến môi trường `AUTOTEST_EMAIL` và `AUTOTEST_PASSWORD` thay cho file local.
- Không in mật khẩu ra UI/log.

Nếu đổi tài khoản test, chỉ sửa `.autotest.env`, không cần sửa Python.
