# Fix Dropdown Ant Design – Mẫu xe

- Chọn Hãng trong modal Mẫu xe bằng Ant Design Select (không dùng Selenium `Select`).
- Chỉ click option trong dropdown đang hiển thị.
- Tự đóng popup sau khi chọn để tránh `ElementClickInterceptedException` khi bấm Tạo mẫu xe.
- Có JS click fallback cho nút submit nếu animation của AntD chặn click.
- Sau khi tạo Mẫu, kiểm tra cùng dòng bảng có cả tên Mẫu và Hãng liên kết.
- Sau khi tạo Hãng, kiểm tra dropdown lọc Hãng ngoài trang đã có Hãng mới.
