# Phần Linh tích hợp trên source nhóm

## Chạy trên VS Code

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Hoặc Windows nhấp đúp `RUN_WINDOWS.bat`.

## Demo nhanh

1. Header chọn `PLT Courses / Đăng nhập`.
2. Vào `Element Management` để xem 4 element mẫu.
3. Vào `Test Builder`.
4. Chọn `Nút Đăng nhập` -> `Text / Value`.
5. Expected `Đăng nhập` -> Run -> PASS nếu text thực tế khớp.
6. Đổi Expected thành `Đăng ký` -> Run -> FAIL.
7. Với `Ô Email` + `Element tồn tại`, Expected được khóa thành `Tồn tại`.

## Demo Danh mục xe (Thứ Tư & Thứ Năm)

1. Vào menu `Danh mục xe` (độc lập, không cần chọn Website/Page ở Header).
2. Hai bảng `Hãng xe` / `Mẫu xe` đã có sẵn locator mẫu — bấm `Kiểm tra locator`
   trên một dòng để gọi Selenium xác nhận trên PCM thật (chỉnh Locator value nếu
   PCM đổi DOM, không cần sửa code).
3. Bấm `Chọn file để Import`, chọn `data/sample_import/danh_muc_xe_mau.csv` (hoặc
   `.json`) để nạp dữ liệu test Hãng/Mẫu vào bảng preview.
4. Xuống mục `Kiểm tra CRUD & Dropdown phụ thuộc`: chọn nhóm `Hãng xe` hoặc
   `Mẫu xe`, chọn Tên từ dữ liệu vừa import (Mẫu xe tự gợi ý Hãng liên kết) rồi
   bấm `Chạy kiểm tra CRUD`.
5. Kết quả Expected–Actual hiển thị ở bảng bên dưới: mở form, nhập tên, (Mẫu xe)
   chọn hãng, xuất hiện trong bảng, và dropdown phụ thuộc đã có giá trị mới; dữ
   liệu test được tự dọn (best-effort) sau khi chạy.

## Push branch riêng

```bash
git checkout -b linh-thu2-thu3
git add .
git commit -m "feat: Linh test UI and element management"
git push -u origin linh-thu2-thu3
```
