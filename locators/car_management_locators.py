"""Locator cho module Quản lý xe (Trân).

QUAN TRỌNG: Trang thật dùng Ant Design cho toàn bộ UI:
  - Text nút bấm có thể nằm trong <span> lồng bên trong <button> -> PHẢI dùng
    `contains(normalize-space(.), ...)` (so khớp toàn bộ text hậu duệ), KHÔNG
    dùng `contains(text(), ...)` (chỉ so khớp text node trực tiếp của chính
    thẻ đó, sẽ luôn thất bại nếu label nằm trong span con). Đây chính là
    nguyên nhân khiến bộ 8 test trước đó luôn FAIL tại bước bấm "Thêm xe".
  - Hãng xe / Mẫu xe / Nhiên liệu / Trạng thái là combobox Ant Design tuỳ biến
    (div, không phải <select>) -> KHÔNG dùng selenium Select(); xem
    `core/helpers/antd_ui.choose_ant_option` / `choose_ant_option_first`.
  - Form "Thêm xe" là một TRANG riêng (điều hướng, không phải modal) với các
    field bắt buộc: Biển số, Hãng xe, Mẫu xe, Nhiên liệu, Năm, Trạng thái.
    Trường "Màu" là tuỳ chọn. KHÔNG có field Giá/price_per_day (form thật
    không có field này - đã kiểm chứng qua ảnh chụp lỗi thực tế).
  - Nút thoát khỏi form Thêm xe là link "Quay lại danh sách xe", không phải
    nút "Hủy" như locator cũ giả định.

Các field động trong form (theo nhãn) được truy vấn trực tiếp bằng
`core/helpers/antd_ui.form_item_by_label` trong lúc chạy test, thay vì cố định
theo tên thuộc tính (name/id) nội bộ mà ta không thể xác nhận nếu không có
quyền truy cập DOM trực tiếp - cách này bền vững hơn khi FE đổi cấu trúc HTML.
"""

from selenium.webdriver.common.by import By


class CarManagementLocators:
    # ---------------------------------------------------------------
    # 1. Điều hướng / trang danh sách xe
    # ---------------------------------------------------------------
    LIST_URL = "https://courses.plt.pro.vn/cars"

    PAGE_READY_MARKER = (
        By.XPATH,
        "//*[contains(normalize-space(.), 'Danh sách xe')]",
    )

    STAT_TOTAL_CARS = (
        By.XPATH,
        "//*[contains(normalize-space(.), 'Tất cả xe')]/following::div[1]",
    )

    # ---------------------------------------------------------------
    # 2. Nút hành động chính
    # ---------------------------------------------------------------
    ADD_CAR_BTN = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'Thêm xe') "
        "and not(contains(normalize-space(.), 'Thêm xe mới'))]",
    )
    SAVE_BTN = (
        By.XPATH,
        "//button[@type='submit' or contains(normalize-space(.), 'Lưu')"
        " or contains(normalize-space(.), 'Tạo xe')]",
    )
    BACK_TO_LIST_LINK = (
        By.XPATH,
        "//*[self::a or self::button or self::span]"
        "[contains(normalize-space(.), 'Quay lại danh sách xe')]",
    )

    # ---------------------------------------------------------------
    # 3. Nhãn field trong form Thêm/Sửa xe (dùng với antd_ui.form_item_by_label)
    # ---------------------------------------------------------------
    LABEL_LICENSE_PLATE = "Biển số"
    LABEL_BRAND = "Hãng xe"
    LABEL_MODEL = "Mẫu xe"
    LABEL_FUEL = "Nhiên liệu"
    LABEL_COLOR = "Màu"
    LABEL_YEAR = "Năm"
    LABEL_STATUS = "Trạng thái"

    MODEL_DISABLED_PLACEHOLDER_HINT = "Chọn hãng xe trước"

    # ---------------------------------------------------------------
    # 4. Bảng & thao tác theo dòng
    # ---------------------------------------------------------------
    CAR_TABLE = (By.CSS_SELECTOR, "div.ant-table-wrapper table")
    CAR_TABLE_ROWS = (By.CSS_SELECTOR, "div.ant-table-wrapper table tbody tr")

    ROW_EDIT_BTN_CSS = (
        "button[aria-label='Chỉnh sửa'], button[aria-label='Sửa'], button[title='Chỉnh sửa']"
    )
    ROW_DELETE_BTN_CSS = (
        "button[aria-label='Xóa'], button[aria-label='Xoá'], button[title='Xóa']"
    )

    STATUS_CELL_RENTED_HINT = "Đang thuê"

    # Xác nhận xoá: có thể là Popconfirm (popover nhỏ) hoặc Modal đầy đủ.
    CONFIRM_DELETE_BTN = (
        By.XPATH,
        "//*[contains(@class,'ant-popover') or contains(@class,'ant-modal')]"
        "[not(contains(@style,'display: none'))]"
        "//button[contains(normalize-space(.), 'Đồng ý') "
        "or contains(normalize-space(.), 'Xóa') "
        "or contains(normalize-space(.), 'Xoá') "
        "or contains(normalize-space(.), 'Xác nhận')]",
    )

    # ---------------------------------------------------------------
    # 5. Tìm kiếm (trang danh sách hiện KHÔNG có ô tìm kiếm độc lập theo
    #    kiểm chứng ảnh chụp thực tế - chỉ có sort ở cột XE và filter ở cột
    #    TRẠNG THÁI). Vẫn dò thêm các khả năng phổ biến để không bỏ sót nếu
    #    UI đã/sẽ được bổ sung ô tìm kiếm.
    # ---------------------------------------------------------------
    SEARCH_INPUT_CANDIDATES = [
        (By.CSS_SELECTOR, "input[placeholder*='Tìm kiếm']"),
        (By.CSS_SELECTOR, "input[type='search']"),
        (By.XPATH, "//input[contains(@placeholder, 'biển số')]"),
    ]
    STATUS_FILTER_TRIGGER = (
        By.XPATH,
        "//th[contains(., 'Trạng thái') or contains(., 'TRẠNG THÁI')]"
        "//span[contains(@class, 'ant-table-filter-trigger')]",
    )

    # ---------------------------------------------------------------
    # 6. Thông báo lỗi / thành công (nội dung tham chiếu - việc dò phần tử
    #    thực hiện qua antd_ui.wait_for_any_message / field_error_text)
    # ---------------------------------------------------------------
    MSG_SUCCESS_HINT_WORDS = ("thành công", "đã lưu", "đã tạo", "đã xóa", "đã xoá")
    ERR_DUPLICATE_PLATE_HINT_WORDS = ("đã tồn tại", "trùng", "đã được sử dụng")
    ERR_DELETE_BLOCKED_HINT_WORDS = ("không thể xóa", "không thể xoá", "đang thuê", "đang được thuê")
    ERR_REQUIRED_FIELD_HINT_WORDS = ("không được để trống", "vui lòng", "bắt buộc", "chưa nhập", "chọn")
