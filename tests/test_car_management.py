"""8 kịch bản Selenium cho module Quản lý xe (Trân) - courses.plt.pro.vn/cars.

Bám sát bằng chứng thực tế thu được từ ảnh chụp lỗi (reports/screenshots/) của
các lần chạy trước:
  - Form "Thêm xe" là một TRANG riêng, có các field bắt buộc: Biển số, Hãng xe,
    Mẫu xe, Nhiên liệu, Năm, Trạng thái (Màu là tuỳ chọn). KHÔNG có field Giá.
  - Hãng xe / Mẫu xe / Nhiên liệu / Trạng thái là combobox Ant Design tuỳ biến,
    không phải <select> gốc -> không dùng selenium Select().
  - Mẫu xe bị khoá (placeholder "Chọn hãng xe trước") cho tới khi đã chọn
    Hãng xe -> đúng là dropdown phụ thuộc cần kiểm chứng ở TC1.
  - Không có ô tìm kiếm độc lập trên trang danh sách xe; chỉ có sort ở cột XE
    và filter ở cột TRẠNG THÁI -> TC5 thích nghi theo thực tế thay vì giả định
    một ô tìm kiếm không tồn tại.
  - Nút thoát form là link "Quay lại danh sách xe", không phải nút "Hủy".

Nguyên tắc dữ liệu test:
  - Biển số dùng cho các test tạo/sửa/xoá được SINH DUY NHẤT mỗi lần chạy
    (core.helpers.antd_ui.generate_unique_plate) để không bao giờ đụng dữ liệu
    thật hoặc dữ liệu sót lại từ lần chạy trước.
  - Fixture cấp lớp (class-scoped, autouse) đảm bảo xoá xe test đã tạo dù test
    nào đó ở giữa fail/lỗi -> dữ liệu và kết quả chạy luôn khôi phục được.
"""

from __future__ import annotations

import re
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.driver_factory import DriverFactory
from core.helpers import antd_ui
from core.helpers.asserts import CustomAsserts
from locators.car_management_locators import CarManagementLocators as L
from selenium.webdriver.common.keys import Keys
import time

PLATE_PATTERN = re.compile(r"\d{2}[A-Z]-\d{3}\.\d{2}")


# ---------------------------------------------------------------------------
# Helper dùng chung trong file test (không thuộc antd_ui vì gắn với luồng
# nghiệp vụ cụ thể của form Quản lý xe, không tổng quát cho module khác).
# ---------------------------------------------------------------------------

def _open_add_car_form(driver, wait):
    antd_ui.wait_for_loading_to_clear(driver)
    btn = wait.until(EC.element_to_be_clickable(L.ADD_CAR_BTN))
    antd_ui.safe_click(driver, btn)
    wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//label[contains(normalize-space(.), '{L.LABEL_LICENSE_PLATE}')]")
    ))


def _fill_required_fields(driver, wait, plate: str, color: str = "Trắng") -> dict:
    """Điền toàn bộ field bắt buộc của form Thêm/Sửa xe. Trả về các lựa chọn đã
    chọn (để đối chiếu ở các bước sau nếu cần)."""
    chosen = {}

    plate_item = antd_ui.form_item_by_label(driver, L.LABEL_LICENSE_PLATE)
    plate_input = antd_ui.text_input_in_item(plate_item)
    assert plate_input is not None, "Không tìm thấy ô nhập Biển số trong form."
    plate_input.click()
    plate_input.clear()
    plate_input.send_keys(plate)

    brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
    brand_combo = antd_ui.select_trigger_in_item(brand_item)
    assert brand_combo is not None, "Không tìm thấy combobox Hãng xe."
    brand_name = antd_ui.choose_ant_option_first(driver, brand_combo)
    assert brand_name, "Dropdown Hãng xe không có option nào để chọn."
    chosen["brand"] = brand_name

    # Mẫu xe chỉ mở khoá SAU khi đã chọn Hãng xe -> chờ 1 nhịp để UI cập nhật.
    model_item = antd_ui.form_item_by_label(driver, L.LABEL_MODEL)
    model_combo = antd_ui.select_trigger_in_item(model_item)
    assert model_combo is not None, "Không tìm thấy combobox Mẫu xe."
    WebDriverWait(driver, 10).until(
        lambda d: "disabled" not in (model_combo.get_attribute("class") or "")
        and model_combo.get_attribute("aria-disabled") != "true"
    )
    model_name = antd_ui.choose_ant_option_first(driver, model_combo)
    assert model_name, "Dropdown Mẫu xe không có option nào sau khi đã chọn Hãng xe."
    chosen["model"] = model_name

    fuel_item = antd_ui.form_item_by_label(driver, L.LABEL_FUEL)
    fuel_combo = antd_ui.select_trigger_in_item(fuel_item)
    assert fuel_combo is not None, "Không tìm thấy combobox Nhiên liệu."
    fuel_name = antd_ui.choose_ant_option_first(driver, fuel_combo)
    assert fuel_name, "Dropdown Nhiên liệu không có option nào để chọn."
    chosen["fuel"] = fuel_name

    color_item = antd_ui.form_item_by_label(driver, L.LABEL_COLOR)
    color_input = antd_ui.text_input_in_item(color_item)
    if color_input is not None:
        color_input.click()
        color_input.clear()
        color_input.send_keys(color)
    chosen["color"] = color

    year_item = antd_ui.form_item_by_label(driver, L.LABEL_YEAR)
    year_input = antd_ui.text_input_in_item(year_item)
    if year_input is not None:
        year_input.click()
        year_input.clear()
        year_input.send_keys(str(datetime.now().year))
    else:
        year_combo = antd_ui.select_trigger_in_item(year_item)
        assert year_combo is not None, "Không tìm thấy ô nhập/dropdown Năm."
        chosen["year"] = antd_ui.choose_ant_option_first(driver, year_combo)

    status_item = antd_ui.form_item_by_label(driver, L.LABEL_STATUS)
    status_combo = antd_ui.select_trigger_in_item(status_item)
    assert status_combo is not None, "Không tìm thấy combobox Trạng thái."
    status_name = antd_ui.choose_ant_option_first(driver, status_combo)
    assert status_name, "Dropdown Trạng thái không có option nào để chọn."
    chosen["status"] = status_name

    return chosen


def _save_and_expect_success(driver, wait, plate: str):
    save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
    antd_ui.safe_click(driver, save_btn)

    def _saved(d):
        if plate and antd_ui.find_row_by_plate(d, L.CAR_TABLE, plate, timeout=1):
            return True
        msg = antd_ui.wait_for_any_message(d, timeout=1)
        return msg or False

    try:
        WebDriverWait(driver, 15).until(_saved)
    except Exception:
        pass

    row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=8)
    assert row is not None, (
        f"Không thấy xe biển số {plate} trong bảng sau khi Lưu — "
        "kiểm tra lại field bắt buộc (đặc biệt là Ảnh nếu form yêu cầu upload)."
    )
    return row


def _collect_all_plates(driver, wait, max_pages: int = 10) -> list[str]:
    """Duyệt toàn bộ bảng (kể cả phân trang nếu có) và trả về danh sách biển
    số tìm thấy trên từng dòng."""
    plates: list[str] = []
    for _ in range(max_pages):
        rows = antd_ui.extract_table_rows(driver, L.CAR_TABLE, timeout=8)
        for row_text in rows:
            match = PLATE_PATTERN.search(row_text)
            plates.append(match.group(0) if match else row_text)
        next_btn = driver.find_elements(
            By.CSS_SELECTOR, "li.ant-pagination-next:not(.ant-pagination-disabled) button"
        )
        if not next_btn or not next_btn[0].is_enabled():
            break
        antd_ui.safe_click(driver, next_btn[0])
        WebDriverWait(driver, 5).until(lambda d: True)  # nhịp chờ nhẹ cho bảng render lại
    return plates


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="class", autouse=True)
def cleanup_test_car(request):
    """Đảm bảo xe test (biển số PLATE) luôn được xoá khi hết bộ test, kể cả khi
    có test ở giữa fail/lỗi -> dữ liệu và kết quả chạy có thể khôi phục."""
    yield
    driver = None
    try:
        driver = DriverFactory.create_driver(headless=False)
        wait = WebDriverWait(driver, 15)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, TestCarManagement.PLATE, timeout=5)
        if row is not None:
            delete_btn = row.find_element(By.CSS_SELECTOR, L.ROW_DELETE_BTN_CSS)
            antd_ui.safe_click(driver, delete_btn)
            confirm = wait.until(EC.element_to_be_clickable(L.CONFIRM_DELETE_BTN))
            antd_ui.safe_click(driver, confirm)
            WebDriverWait(driver, 10).until(
                lambda d: antd_ui.find_row_by_plate(d, L.CAR_TABLE, TestCarManagement.PLATE, timeout=1) is None
            )
    except Exception:
        # Dọn dẹp là nỗ lực tối đa (best-effort); không để lỗi dọn dẹp che lấp
        # kết quả thật của bộ test.
        pass
    finally:
        if driver is not None:
            driver.quit()


# ---------------------------------------------------------------------------
# 8 kịch bản
# ---------------------------------------------------------------------------

class TestCarManagement:
    # Biển số duy nhất cho toàn bộ lớp test, sinh 1 lần khi collect test để
    # test_02/03/06/07 dùng chung, không đụng dữ liệu thật hoặc lần chạy khác.
    PLATE = antd_ui.generate_unique_plate()

    def setup_method(self, method):
        pass  # driver do fixture `driver` (conftest.py) cấp theo từng test.

    # -- TC1 -----------------------------------------------------------
    def test_01_dropdown_phu_thuoc_hang_mau(self, driver):
        """Mẫu xe phải bị khoá cho tới khi chọn Hãng xe, và có option sau đó."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        _open_add_car_form(driver, wait)

        model_item = antd_ui.form_item_by_label(driver, L.LABEL_MODEL)
        model_combo = antd_ui.select_trigger_in_item(model_item)
        assert model_combo is not None, "Không tìm thấy combobox Mẫu xe."
        assert L.MODEL_DISABLED_PLACEHOLDER_HINT in model_item.text or (
            model_combo.get_attribute("aria-disabled") == "true"
        ), "Mẫu xe phải ở trạng thái khoá trước khi chọn Hãng xe."

        brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
        brand_combo = antd_ui.select_trigger_in_item(brand_item)
        brand_name = antd_ui.choose_ant_option_first(driver, brand_combo)
        assert brand_name, "Dropdown Hãng xe rỗng, không thể kiểm tra phụ thuộc."

        WebDriverWait(driver, 10).until(
            lambda d: model_combo.get_attribute("aria-disabled") != "true"
        )
        model_name = antd_ui.choose_ant_option_first(driver, model_combo)
        assert model_name, (
            f"Sau khi chọn Hãng xe '{brand_name}', Mẫu xe vẫn không có option nào."
        )

        back = wait.until(EC.element_to_be_clickable(L.BACK_TO_LIST_LINK))
        antd_ui.safe_click(driver, back)

    # -- TC2 -----------------------------------------------------------
    def test_02_them_xe_moi_thanh_cong(self, driver):
        """Tạo mới 1 xe với đầy đủ field bắt buộc -> xe xuất hiện trong bảng."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        _open_add_car_form(driver, wait)
        _fill_required_fields(driver, wait, self.PLATE)
        _save_and_expect_success(driver, wait, self.PLATE)

    # -- TC3 -----------------------------------------------------------
    def test_03_loi_trung_bien_so(self, driver):
        """Tạo xe khác với CÙNG biển số vừa tạo ở TC2 -> hệ thống phải báo lỗi
        trùng, không được tạo thêm bản ghi thứ 2."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        _open_add_car_form(driver, wait)
        _fill_required_fields(driver, wait, self.PLATE, color="Đen")

        save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
        antd_ui.safe_click(driver, save_btn)

        plate_item = antd_ui.form_item_by_label(driver, L.LABEL_LICENSE_PLATE)
        message = antd_ui.wait_for_any_message(driver, timeout=8)
        field_error = antd_ui.field_error_text(plate_item)
        combined = f"{message} {field_error}".casefold()

        assert any(word in combined for word in L.ERR_DUPLICATE_PLATE_HINT_WORDS), (
            "Không thấy thông báo lỗi trùng biển số. Nội dung nhận được: "
            f"message={message!r}, field_error={field_error!r}"
        )

        # Đảm bảo không có bản ghi trùng thứ 2 bị tạo ra ngoài ý muốn.
        back_candidates = driver.find_elements(*L.BACK_TO_LIST_LINK)
        if back_candidates:
            antd_ui.safe_click(driver, back_candidates[0])
        else:
            driver.get(L.LIST_URL)
        rows = [
            r for r in antd_ui.extract_table_rows(driver, L.CAR_TABLE, timeout=8)
            if self.PLATE in r
        ]
        assert len(rows) <= 1, (
            f"Phát hiện {len(rows)} dòng trùng biển số {self.PLATE} — "
            "ràng buộc unique có thể đã bị vi phạm."
        )

    # -- TC4 -----------------------------------------------------------
    def test_04_chan_xoa_xe_dang_thue(self, driver):
        """Không cho xoá xe đang ở trạng thái 'Đang thuê'.

        Test tự dò trong dữ liệu thật xem có xe nào đang thuê hay không, thay
        vì giả định cứng dòng đầu tiên (giả định này đã được xác nhận SAI qua
        ảnh chụp thực tế — dòng đầu tiên hiển thị 'Sẵn sàng', không phải
        'Đang thuê'). Nếu hiện không có xe nào đang thuê, test được skip rõ
        ràng thay vì báo PASS giả.
        """
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        antd_ui.wait_for_loading_to_clear(driver)

        table = wait.until(EC.presence_of_element_located(L.CAR_TABLE))
        rented_row = None
        for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            if L.STATUS_CELL_RENTED_HINT in (row.text or ""):
                rented_row = row
                break

        if rented_row is None:
            pytest.skip(
                "Không có xe nào ở trạng thái 'Đang thuê' trong dữ liệu hiện tại "
                "nên không thể kiểm chứng ràng buộc chặn xoá. Cần tạo/điều phối "
                "một đơn thuê đang hoạt động trước khi chạy lại test này."
            )

        delete_btn = rented_row.find_element(By.CSS_SELECTOR, L.ROW_DELETE_BTN_CSS)
        antd_ui.safe_click(driver, delete_btn)
        confirm_candidates = driver.find_elements(*L.CONFIRM_DELETE_BTN)
        if confirm_candidates:
            antd_ui.safe_click(driver, confirm_candidates[0])

        message = antd_ui.wait_for_any_message(driver, timeout=8).casefold()
        assert any(word in message for word in L.ERR_DELETE_BLOCKED_HINT_WORDS), (
            f"Kỳ vọng thông báo chặn xoá xe đang thuê, nhận được: {message!r}"
        )

    # -- TC5 -----------------------------------------------------------
    def test_05_tim_kiem_va_bat_loi_mismatch_missing(self, driver):
        """Kiểm tra Table hiển thị đúng dữ liệu, dùng CustomAsserts để bắt
        chính xác các lỗi mismatch / missing / unexpected.

        Trang danh sách hiện KHÔNG có ô tìm kiếm độc lập (đã xác nhận qua ảnh
        chụp thực tế) nên test dùng ô tìm kiếm NẾU có, và tự chuyển sang duyệt
        toàn bộ bảng (kể cả phân trang) khi không có — tránh test giả định sai
        về UI rồi báo PASS/FAIL sai lệch.
        """
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        antd_ui.wait_for_loading_to_clear(driver)

        search_input = antd_ui.first_visible(driver, L.SEARCH_INPUT_CANDIDATES)

        if search_input is not None:
            search_input.click()
            search_input.clear()
            search_input.send_keys(self.PLATE)
            search_input.send_keys(u"\ue007")  # Enter
            WebDriverWait(driver, 8).until(lambda d: True)
            actual_rows = antd_ui.extract_table_rows(driver, L.CAR_TABLE, timeout=8)
            actual = [PLATE_PATTERN.search(r).group(0) if PLATE_PATTERN.search(r) else r for r in actual_rows]
        else:
            actual = _collect_all_plates(driver, wait)

        expected = [self.PLATE]
        result = CustomAsserts.compare_table_data(expected, actual)

        assert result["passed"], (
            f"Bảng dữ liệu không khớp kỳ vọng cho biển số {self.PLATE}.\n"
            f"  mismatch  : {result['mismatch']}\n"
            f"  missing   : {result['missing']}\n"
            f"  unexpected: {result['unexpected']}"
        )

    # -- TC6 -----------------------------------------------------------
    def test_06_crud_sua_thong_tin_xe(self, driver):
        """Sửa xe vừa tạo (đổi Màu) -> xác nhận thay đổi PERSIST thật trong
        bảng, không chỉ tin vào thông báo thành công trên UI."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        antd_ui.wait_for_loading_to_clear(driver)

        row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, self.PLATE, timeout=10)
        assert row is not None, f"Không tìm thấy xe {self.PLATE} để sửa (TC2 có thể đã fail)."
        edit_btn = row.find_element(By.CSS_SELECTOR, L.ROW_EDIT_BTN_CSS)
        antd_ui.safe_click(driver, edit_btn)

        color_item = antd_ui.form_item_by_label(driver, L.LABEL_COLOR)
        color_input = antd_ui.text_input_in_item(color_item)
        assert color_input is not None, "Không tìm thấy ô Màu trong form sửa xe."
        new_color = "Xám khói"
        color_input.click()
        color_input.clear()
        color_input.send_keys(new_color)

        save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
        antd_ui.safe_click(driver, save_btn)

        def _updated(d):
            r = antd_ui.find_row_by_plate(d, L.CAR_TABLE, self.PLATE, timeout=1)
            return r is not None and new_color.casefold() in (r.text or "").casefold()

        try:
            WebDriverWait(driver, 15).until(_updated)
        except Exception:
            pass

        row_after = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, self.PLATE, timeout=8)
        assert row_after is not None, f"Không còn thấy xe {self.PLATE} sau khi sửa."
        assert new_color.casefold() in (row_after.text or "").casefold(), (
            f"Màu chưa được cập nhật đúng. Nội dung dòng hiện tại: {row_after.text!r}"
        )

    # -- TC7 -----------------------------------------------------------
    def test_07_crud_xoa_xe_thanh_cong(self, driver):
        """Xoá xe test -> xác nhận biến mất khỏi bảng thật, không chỉ tin
        thông báo thành công."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        antd_ui.wait_for_loading_to_clear(driver)

        row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, self.PLATE, timeout=10)
        assert row is not None, f"Không tìm thấy xe {self.PLATE} để xoá (TC2 có thể đã fail)."
        delete_btn = row.find_element(By.CSS_SELECTOR, L.ROW_DELETE_BTN_CSS)
        antd_ui.safe_click(driver, delete_btn)

        confirm = wait.until(EC.element_to_be_clickable(L.CONFIRM_DELETE_BTN))
        antd_ui.safe_click(driver, confirm)

        try:
            WebDriverWait(driver, 15).until(
                lambda d: antd_ui.find_row_by_plate(d, L.CAR_TABLE, self.PLATE, timeout=1) is None
            )
        except Exception:
            pass

        remaining = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, self.PLATE, timeout=8)
        assert remaining is None, f"Xe {self.PLATE} vẫn còn trong bảng sau khi xoá."

    # -- TC8 -----------------------------------------------------------
    def test_08_bat_loi_thieu_du_lieu_bat_buoc(self, driver):
        """Bấm Lưu khi form trống -> mọi field bắt buộc phải báo lỗi (bắt lỗi
        missing một cách toàn diện, không chỉ kiểm tra 1 field)."""
        wait = WebDriverWait(driver, 20)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        _open_add_car_form(driver, wait)

        save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
        antd_ui.safe_click(driver, save_btn)

        required_labels = [
            L.LABEL_LICENSE_PLATE,
            L.LABEL_BRAND,
            L.LABEL_MODEL,
            L.LABEL_FUEL,
            L.LABEL_YEAR,
            L.LABEL_STATUS,
        ]
        missing_errors = []
        for label in required_labels:
            item = antd_ui.form_item_by_label(driver, label)
            error_text = antd_ui.field_error_text(item)
            if not error_text:
                missing_errors.append(label)

        assert not missing_errors, (
            "Các field bắt buộc sau KHÔNG hiển thị lỗi khi bỏ trống (bắt lỗi "
            f"'missing' thất bại): {missing_errors}"
        )

        back_candidates = driver.find_elements(*L.BACK_TO_LIST_LINK)
        if back_candidates:
            antd_ui.safe_click(driver, back_candidates[0])

    # -- TC9 -----------------------------------------------------------
    def test_09_basic_dropdown_scenarios(self, driver):
        """
        Procedure step:
        1. Access the website và điều hướng đến danh sách xe.
        2. Mở form Thêm xe mới.
        3. Kiểm tra các thao tác cơ bản trên Dropdown Hãng xe (Placeholder, Search, Click Outside).
        """
        wait = WebDriverWait(driver, 15)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        
        # Mở form thêm xe
        _open_add_car_form(driver, wait)

        brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
        brand_combo = antd_ui.select_trigger_in_item(brand_item)
        assert brand_combo is not None, "Không tìm thấy combobox Hãng xe."

        # Kịch bản 1: Default State
        placeholder = brand_combo.find_elements(By.CSS_SELECTOR, ".ant-select-selection-placeholder")
        assert len(placeholder) > 0 and placeholder[0].is_displayed(), "Dropdown không hiển thị Placeholder"

        # Kịch bản 2: Tìm kiếm hợp lệ
        antd_ui.safe_click(driver, brand_combo)
        search_input = brand_combo.find_element(By.CSS_SELECTOR, "input")
        search_input.send_keys("vin")
        time.sleep(1)
        
        options = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option")
        assert len(options) > 0, "Tìm kiếm không trả về kết quả"
        
        # Kịch bản 3: Đóng danh sách khi click ra ngoài
        driver.execute_script("document.body.click();")
        time.sleep(0.5)
        hidden_panel = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
        assert len(hidden_panel) == 0, "Danh sách không tự đóng lại khi click ra ngoài"

        back_btn = wait.until(EC.element_to_be_clickable(L.BACK_TO_LIST_LINK))
        antd_ui.safe_click(driver, back_btn)

    # -- TC10 ----------------------------------------------------------
    def test_10_dropdown_search_injection(self, driver):
        """
        Procedure step:
        1. Access the website và điều hướng đến danh sách xe.
        2. Mở form Thêm xe mới.
        3. Bơm mã độc XSS/SQL Injection vào ô tìm kiếm của Dropdown Hãng xe.
        4. Xác minh hệ thống từ chối an toàn và hiển thị 'Không có dữ liệu'.
        """
        wait = WebDriverWait(driver, 15)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER)
        
        _open_add_car_form(driver, wait)
        
        brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
        brand_combo = antd_ui.select_trigger_in_item(brand_item)
        antd_ui.safe_click(driver, brand_combo)
        
        search_input = brand_combo.find_element(By.CSS_SELECTOR, "input")
        malicious_payload = "<script>alert('Hack')</script>' OR 1=1--"
        search_input.send_keys(malicious_payload)
        time.sleep(1)
        
        # Kiểm tra phản ứng giao diện (kỳ vọng hiển thị Empty State)
        empty_state = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".ant-select-item-empty, .ant-empty-description")
        ))
        assert empty_state.is_displayed(), "Không chặn được mã độc hoặc giao diện phản hồi sai"
        
        search_input.send_keys(Keys.ESCAPE)
        back_btn = wait.until(EC.element_to_be_clickable(L.BACK_TO_LIST_LINK))
        antd_ui.safe_click(driver, back_btn)
