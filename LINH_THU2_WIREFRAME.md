# Linh – Thứ Hai – PySide6 Test UI

Theo bảng `AutoTestApp_KeHoach.xlsx`:

- Vai trò: **PySide6 Test UI**.
- Công việc: thiết kế wireframe và component dùng chung cho **Dropdown, Text, Table, Search, CRUD và Result**.
- Quy tắc bắt buộc: **Actual Result phải ẩn trước Run**.

## Luồng chung

`Website -> Page -> Element -> Test Type -> Expected -> Run -> Actual -> PASS/FAIL`

## Component dùng chung

1. **Test context**: Website / Page / URL lấy từ Header của source nhóm.
2. **Element selector**: chỉ chọn element đã được cấu hình trong Element Management.
3. **Locator preview**: read-only; tester không phải nhập locator.
4. **Expected editor**: một giá trị trên một dòng, có tùy chọn trim / case / order.
5. **Run panel**: loading + Run + Reset.
6. **Result table**: STT / Expected / Actual / Kết quả.
7. **Toast**: PASS / FAIL / ERROR.

## Wireframe theo loại test

### Dropdown
- Element: select/dropdown.
- Expected: danh sách option, mỗi dòng một giá trị.
- Result: Missing / Unexpected / Wrong order / PASS.

### Text
- Element: label, button, input.
- Expected: nội dung text/value/placeholder.
- Result: Expected – Actual – PASS/FAIL.

### Table
- Element: table hoặc tbody.
- Expected: mỗi row dạng `cột 1 | cột 2 | ...`.
- Result: so khớp từng row.

### Search
- Input search + keyword + table/result container.
- Expected: row mong đợi xuất hiện hoặc số lượng kết quả.
- Phần runner Search thuộc ngày tích hợp tiếp theo.

### CRUD
- Step Create -> Read -> Update -> Delete.
- Mỗi step có action, input và expected riêng.
- Actual hiển thị sau từng step khi runner hoàn thành.
- Phần runner CRUD thuộc ngày tích hợp tiếp theo.

### Result
- Trước Run: chỉ hiện `Chưa có Actual Result`.
- Sau Run: hiển thị bảng Expected – Actual.
- `PASS`: Selenium chạy được và Actual khớp Expected.
- `FAIL`: Selenium chạy được nhưng dữ liệu không khớp.
- `ERROR`: Selenium / Chrome / locator không thể thực thi test.
