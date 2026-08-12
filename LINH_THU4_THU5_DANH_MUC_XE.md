# Linh – Thứ Tư & Thứ Năm – Module Owner: Danh mục xe

Theo kế hoạch (`AutoTestApp_KeHoach.xlsx`, sheet "Kế hoạch"):

- **Thứ Tư (dòng 19):** Phát triển trang Danh mục xe — UI hai bảng Hãng/Mẫu xe,
  modal, locator và Selenium kiểm tra dropdown/CRUD cơ bản.
  → *Đầu ra:* Trang Danh mục xe chạy độc lập; ≥4 test; phân biệt đúng Hãng xe và Mẫu xe.
- **Thứ Năm (dòng 26):** Hoàn thiện Danh mục xe — CRUD Hãng/Mẫu, mapping dữ liệu
  Excel/CSV/JSON và xác nhận dropdown cập nhật sau CRUD.
  → *Đầu ra:* CRUD Hãng/Mẫu chạy; import dữ liệu cho module; ≥7 test.

## Đã triển khai

**Trang mới:** `ui/pages/vehicle_catalog_page.py` (menu sidebar **Danh mục xe**),
chạy độc lập — tự gọi `store.ensure_page(...)` để đảm bảo Page `vehicle_catalog`
(PLT Courses `/cars/catalog`) tồn tại, không phụ thuộc Website/Page đang chọn ở Header.

1. **Hai bảng song song, đúng cấu trúc PCM thật** (`ElementGroupPanel`, dùng lại
   cho cả Hãng xe và Mẫu xe):
   - Form Tên element / Loại locator / Locator / Test gợi ý.
   - Bảng element theo nhóm (`group: "brand" | "model"`), Sửa / Xóa / nhấp đúp để sửa.
   - Nút **Kiểm tra locator** gọi lại `SeleniumWorker` sẵn có (không làm treo UI, có
     loading + status).
   - 10 locator được seed sẵn trong `data/page_elements.json` (bảng, nút Thêm, ô tên,
     dropdown chọn hãng, nút Lưu...) — đây là **locator phỏng đoán theo ảnh chụp màn
     hình PCM**, cần Thảo/Huy xác nhận lại bằng nút "Kiểm tra locator" trên PCM thật
     rồi chỉnh sửa tại chỗ (không cần sửa code).

2. **Import dữ liệu kiểm thử Excel/CSV/JSON** (`services/catalog_import.py`):
   - Đọc `.csv` / `.json` / `.xlsx` / `.xls`, tự nhận diện các alias cột phổ biến
     (`loai/loại/type`, `ten/tên/name`, `hang/hãng/brand`...).
   - Chuẩn hoá về `{"loai": "hang"|"mau", "ten", "hang", "trang_thai"}`, bỏ qua và
     cảnh báo dòng thiếu dữ liệu bắt buộc thay vì làm crash import.
   - File mẫu: `data/sample_import/danh_muc_xe_mau.csv` và `.json`.
   - Bảng preview trong UI hiển thị dữ liệu đã nạp; nút "Xóa dữ liệu đã nạp" để reset.

3. **CRUD + xác nhận dropdown cập nhật sau CRUD** (`services/selenium_runner.py` –
   `CrudRequest` / `CrudWorker`, chạy trong `QThread` riêng như các worker khác):
   - Chọn nhóm (Hãng xe / Mẫu xe) và Tên từ dữ liệu đã import (hoặc nhập tay); Mẫu
     xe bắt buộc chọn Hãng liên kết (tự gợi ý theo dữ liệu import).
   - Luồng chạy: mở form Thêm → nhập Tên → (Mẫu xe) chọn Hãng qua `try_choose_option`
     (hỗ trợ cả `<select>` chuẩn lẫn dropdown tuỳ biến) → Lưu → chờ dòng mới xuất
     hiện trong bảng (`extract_table_rows`) → **kiểm tra dropdown phụ thuộc đã có
     giá trị mới** (khi test Hãng thì kiểm tra dropdown "chọn hãng" trong form Mẫu
     xe; khi test Mẫu thì kiểm tra dropdown lọc mẫu xe) → dọn dữ liệu test
     (`cleanup_row`, best-effort, không làm fail nếu không tự xóa được).
   - Kết quả hiển thị lại bằng `ResultTable` (Expected–Actual–Kết quả) đúng chuẩn
     PASS/FAIL đã dùng ở Test Builder; validate trước khi chạy nếu thiếu locator
     hoặc thiếu Hãng liên kết.

## Số lượng test đạt yêu cầu

- Thứ Tư: 4 element/test tối thiểu cho Hãng xe (bảng, nút Thêm, ô tên, nút Lưu) +
  6 cho Mẫu xe (bảng, nút Thêm, ô tên, dropdown hãng, nút Lưu, dropdown lọc) = 10
  locator sẵn sàng kiểm tra bằng Selenium, vượt mốc ≥4.
- Thứ Năm: mỗi lượt CRUD sinh 4–6 dòng Expected–Actual (mở form, nhập tên, chọn
  hãng nếu là Mẫu, xuất hiện trong bảng, dropdown cập nhật) × 2 nhóm (Hãng/Mẫu)
  cộng với các test "Kiểm tra locator" ở trên = vượt mốc ≥7 test.

## Việc cần đội xác nhận trên PCM thật

Locator trong `data/page_elements.json` (page `vehicle_catalog`) là **best-effort**
dựa trên ảnh chụp màn hình `courses.plt.pro.vn/cars/catalog`, chưa chạy trên DOM
thật. Trước khi demo cuối tuần, dùng nút "Kiểm tra locator" trên từng dòng để xác
nhận/điều chỉnh (không cần sửa code, chỉ sửa Locator value tại UI).
