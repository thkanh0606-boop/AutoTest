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

## Push branch riêng

```bash
git checkout -b linh-thu2-thu3
git add .
git commit -m "feat: Linh test UI and element management"
git push -u origin linh-thu2-thu3
```
