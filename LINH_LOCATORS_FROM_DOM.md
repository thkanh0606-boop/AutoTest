# Locator Danh mục xe – cập nhật từ DOM thật

Nguồn DOM: trang `https://courses.plt.pro.vn/cars/catalog` do Linh cung cấp ngày 12/08/2026.

## Locator đã đối chiếu trực tiếp trên DOM trang

- Bảng Hãng xe: `//h4[normalize-space()='Danh sách hãng xe']/ancestor::section[1]//table`
- Nút Thêm hãng xe: `//button[.//span[normalize-space()='Thêm hãng xe'] or normalize-space()='Thêm hãng xe']`
- Bảng Mẫu xe: `//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//table`
- Nút Thêm mẫu xe: `//button[.//span[normalize-space()='Thêm mẫu xe'] or normalize-space()='Thêm mẫu xe']`
- Dropdown lọc hãng ở khu Mẫu xe: `//h4[normalize-space()='Danh sách mẫu xe']/ancestor::section[1]//*[@role='combobox'][1]`

Các locator trên đều khớp đúng 1 element khi kiểm tra trên HTML được cung cấp.

## Locator trong modal

Modal không nằm trong DOM tĩnh khi đóng, nên locator được scope vào modal đang mở để tránh bắt nhầm element ngoài trang:

- Ô tên Hãng xe: `(//*[@role='dialog'] | //div[contains(@class,'ant-modal')])[last()]//label[contains(normalize-space(.),'Tên hãng xe')]/following::input[1]`
- Nút Tạo hãng xe: `(//*[@role='dialog'] | //div[contains(@class,'ant-modal')])[last()]//button[.//span[normalize-space()='Tạo hãng xe'] or normalize-space()='Tạo hãng xe']`
- Ô tên Mẫu xe: `(//*[@role='dialog'] | //div[contains(@class,'ant-modal')])[last()]//label[contains(normalize-space(.),'Tên mẫu xe')]/following::input[1]`
- Dropdown Hãng trong modal Mẫu xe: `(//*[@role='dialog'] | //div[contains(@class,'ant-modal')])[last()]//*[@role='combobox'][1]`
- Nút Tạo mẫu xe: `(//*[@role='dialog'] | //div[contains(@class,'ant-modal')])[last()]//button[.//span[normalize-space()='Tạo mẫu xe'] or normalize-space()='Tạo mẫu xe']`
