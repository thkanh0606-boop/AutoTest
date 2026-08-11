# Linh – Thứ Ba – Element Management

Đã triển khai trực tiếp trên source `AutoTest-main`:

- Menu **Element Management** trong sidebar.
- Danh sách Element theo Website / Page đang chọn ở Header.
- Form `Tên element / Loại locator / Locator / Test gợi ý`.
- Thêm / sửa / xóa element.
- Double-click row để sửa.
- `Kiểm tra locator` gọi Selenium bằng `QThread`, không làm treo UI.
- Có loading và toast PASS / FAIL / ERROR.
- Không hiển thị nguyên ChromeDriver stacktrace ra màn hình.
- Khi Element thay đổi, Test Builder refresh danh sách ngay.

Dữ liệu tạm đang lưu ở `data/page_elements.json`. Khi repository SQLite của nhóm hoàn thiện, chỉ cần thay implementation trong `services/data_store.py`, giao diện không cần đổi.
