# Linh - Module Danh mục xe

Phạm vi chỉ gồm **Danh mục xe** theo kế hoạch của Linh, không mang theo Element Management/Test Builder cá nhân cũ.

## Thứ Tư
- UI riêng cho Hãng xe / Mẫu xe.
- Locator ổn định theo section/text của Fleet Console.
- Check locator bằng Selenium; element trong modal sẽ tự mở modal trước khi check.
- CRUD cơ bản Hãng/Mẫu và kiểm tra mapping Hãng - Mẫu.

## Thứ Năm
- Import test data CSV / JSON / XLSX.
- Kiểm tra dropdown Hãng cập nhật sau khi tạo Hãng.
- Kiểm tra Mẫu xe xuất hiện đúng Hãng liên kết.
- Cleanup dữ liệu test theo best-effort.

## Chạy
```bash
python main.py
```
Sau đó chọn **Danh mục xe** ở sidebar.

## Unit test riêng của Linh
```bash
python -m unittest tests.test_vehicle_catalog_linh_unittest -v
```

## File chính
- `ui/vehicle_catalog_page.py`
- `runners/vehicle_catalog_runner.py`
- `pages/category_page.py`
- `services/catalog_import.py`
- `data/sample_import/*`
- `tests/test_vehicle_catalog_linh_unittest.py`


## Tự động đăng nhập
Copy `.autotest.env.example` thành `.autotest.env`, điền `TEST_EMAIL` và `TEST_PASSWORD`. File `.autotest.env` đã được `.gitignore`.
