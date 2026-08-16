"""Selenium runner self-test cho module Quản lý xe (Trân) - courses.plt.pro.vn/cars.

Chạy TRONG MỘT phiên trình duyệt duy nhất qua toàn bộ Dropdown / Search /
Table / CRUD để phục vụ nút "Chạy kịch bản Kiểm thử Quản lý xe" trên UI
(trước đây nút này chưa được nối với logic nào). Đây là bản rút gọn/hợp nhất
của 8 kịch bản trong `tests/test_car_management.py` — dùng cho việc tự kiểm
thử nhanh ngay trong app; bộ pytest đầy đủ vẫn là nguồn kiểm thử chính thức.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.driver_factory import DriverFactory
from core.helpers import antd_ui
from core.helpers.antd_ui import log, safe_click, step
from locators.car_management_locators import CarManagementLocators as L

PLATE_PATTERN = re.compile(r"\d{2}[A-Z]-\d{3}\.\d{2}")


def _open_add_car_form(driver, wait):
    antd_ui.wait_for_loading_to_clear(driver)
    btn = wait.until(EC.element_to_be_clickable(L.ADD_CAR_BTN))
    safe_click(driver, btn)
    wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//label[contains(normalize-space(.), '{L.LABEL_LICENSE_PLATE}')]")
    ))


def _fill_required_fields(driver, plate: str, color: str = "Trắng") -> dict:
    chosen: dict[str, Any] = {}

    plate_item = antd_ui.form_item_by_label(driver, L.LABEL_LICENSE_PLATE)
    plate_input = antd_ui.text_input_in_item(plate_item)
    if plate_input is None:
        raise RuntimeError("Không tìm thấy ô nhập Biển số.")
    plate_input.click()
    plate_input.clear()
    plate_input.send_keys(plate)

    brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
    brand_combo = antd_ui.select_trigger_in_item(brand_item)
    brand_name = antd_ui.choose_ant_option_first(driver, brand_combo) if brand_combo else None
    chosen["brand"] = brand_name

    model_item = antd_ui.form_item_by_label(driver, L.LABEL_MODEL)
    model_combo = antd_ui.select_trigger_in_item(model_item)
    if model_combo:
        WebDriverWait(driver, 10).until(
            lambda d: model_combo.get_attribute("aria-disabled") != "true"
        )
        chosen["model"] = antd_ui.choose_ant_option_first(driver, model_combo)

    fuel_item = antd_ui.form_item_by_label(driver, L.LABEL_FUEL)
    fuel_combo = antd_ui.select_trigger_in_item(fuel_item)
    chosen["fuel"] = antd_ui.choose_ant_option_first(driver, fuel_combo) if fuel_combo else None

    color_item = antd_ui.form_item_by_label(driver, L.LABEL_COLOR)
    color_input = antd_ui.text_input_in_item(color_item)
    if color_input is not None:
        color_input.click()
        color_input.clear()
        color_input.send_keys(color)

    year_item = antd_ui.form_item_by_label(driver, L.LABEL_YEAR)
    year_input = antd_ui.text_input_in_item(year_item)
    if year_input is not None:
        year_input.click()
        year_input.clear()
        year_input.send_keys(str(datetime.now().year))
    else:
        year_combo = antd_ui.select_trigger_in_item(year_item)
        if year_combo:
            chosen["year"] = antd_ui.choose_ant_option_first(driver, year_combo)

    status_item = antd_ui.form_item_by_label(driver, L.LABEL_STATUS)
    status_combo = antd_ui.select_trigger_in_item(status_item)
    chosen["status"] = antd_ui.choose_ant_option_first(driver, status_combo) if status_combo else None

    return chosen


def _delete_by_plate(driver, wait, plate: str) -> bool:
    row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=8)
    if row is None:
        return False
    delete_btn = row.find_element(By.CSS_SELECTOR, L.ROW_DELETE_BTN_CSS)
    safe_click(driver, delete_btn)
    confirm_candidates = driver.find_elements(*L.CONFIRM_DELETE_BTN)
    if confirm_candidates:
        safe_click(driver, confirm_candidates[0])
    try:
        WebDriverWait(driver, 10).until(
            lambda d: antd_ui.find_row_by_plate(d, L.CAR_TABLE, plate, timeout=1) is None
        )
    except Exception:
        pass
    return antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=3) is None


def run_car_management_test(worker=None, cleanup: bool = True, show_browser: bool = True) -> dict:
    """Tự kiểm thử Dropdown / Search / Table / CRUD cho module Quản lý xe.

    Trả về dict {"status", "message", "steps"} - cùng contract với
    `runners.vehicle_catalog_runner` để UI xử lý thống nhất.
    """
    driver = None
    steps: list[dict[str, str]] = []
    plate = antd_ui.generate_unique_plate()

    try:
        driver = DriverFactory.create_driver(headless=not show_browser, keep_session=True)
        wait = WebDriverWait(driver, 20)

        log(worker, "Đăng nhập / mở trang Quản lý xe...", 5)
        antd_ui.login_if_needed(driver, L.LIST_URL, page_ready_locator=L.PAGE_READY_MARKER, worker=worker)

        # 1) Dropdown phụ thuộc Hãng - Mẫu -------------------------------
        log(worker, "[Dropdown] Kiểm tra Mẫu xe phụ thuộc Hãng xe...", 15)
        _open_add_car_form(driver, wait)
        model_item = antd_ui.form_item_by_label(driver, L.LABEL_MODEL)
        model_combo = antd_ui.select_trigger_in_item(model_item)
        locked_before = bool(model_combo) and (
            L.MODEL_DISABLED_PLACEHOLDER_HINT in model_item.text
            or model_combo.get_attribute("aria-disabled") == "true"
        )
        steps.append(step("Mẫu xe khoá trước khi chọn Hãng", "Khoá" if locked_before else "KHÔNG khoá", locked_before))

        brand_item = antd_ui.form_item_by_label(driver, L.LABEL_BRAND)
        brand_combo = antd_ui.select_trigger_in_item(brand_item)
        brand_name = antd_ui.choose_ant_option_first(driver, brand_combo) if brand_combo else None
        steps.append(step("Chọn được 1 Hãng xe", brand_name or "Không có option", bool(brand_name)))

        if model_combo:
            WebDriverWait(driver, 10).until(lambda d: model_combo.get_attribute("aria-disabled") != "true")
            model_name = antd_ui.choose_ant_option_first(driver, model_combo)
        else:
            model_name = None
        steps.append(step("Mẫu xe có option sau khi chọn Hãng", model_name or "Không có option", bool(model_name)))

        back = driver.find_elements(*L.BACK_TO_LIST_LINK)
        if back:
            safe_click(driver, back[0])
        else:
            driver.get(L.LIST_URL)

        # 2) Tạo mới xe ----------------------------------------------------
        log(worker, "[CRUD] Tạo xe mới...", 35)
        _open_add_car_form(driver, wait)
        _fill_required_fields(driver, plate)
        save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
        safe_click(driver, save_btn)
        try:
            WebDriverWait(driver, 15).until(
                lambda d: antd_ui.find_row_by_plate(d, L.CAR_TABLE, plate, timeout=1) is not None
            )
        except Exception:
            pass
        created = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=8) is not None
        steps.append(step(f"Xe {plate} xuất hiện trong bảng sau khi Lưu", "Có" if created else "Không thấy", created))

        # 3) Trùng biển số ---------------------------------------------------
        if created:
            log(worker, "[Validation] Kiểm tra chặn trùng biển số...", 50)
            _open_add_car_form(driver, wait)
            _fill_required_fields(driver, plate, color="Đen")
            save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
            safe_click(driver, save_btn)
            plate_item = antd_ui.form_item_by_label(driver, L.LABEL_LICENSE_PLATE)
            message = antd_ui.wait_for_any_message(driver, timeout=8)
            field_error = antd_ui.field_error_text(plate_item)
            combined = f"{message} {field_error}".casefold()
            duplicate_blocked = any(w in combined for w in L.ERR_DUPLICATE_PLATE_HINT_WORDS)
            steps.append(step("Báo lỗi khi trùng biển số", combined.strip() or "(không có thông báo)", duplicate_blocked))
            back = driver.find_elements(*L.BACK_TO_LIST_LINK)
            if back:
                safe_click(driver, back[0])
            else:
                driver.get(L.LIST_URL)

        # 4) Table / mismatch-missing-unexpected -----------------------------
        log(worker, "[Table] Đối chiếu dữ liệu bảng (mismatch/missing/unexpected)...", 65)
        from core.helpers.asserts import CustomAsserts

        search_input = antd_ui.first_visible(driver, L.SEARCH_INPUT_CANDIDATES)
        if search_input is not None:
            search_input.click()
            search_input.clear()
            search_input.send_keys(plate)
            search_input.send_keys("\ue007")
            rows = antd_ui.extract_table_rows(driver, L.CAR_TABLE, timeout=8)
        else:
            rows = antd_ui.extract_table_rows(driver, L.CAR_TABLE, timeout=8)
        actual = [PLATE_PATTERN.search(r).group(0) if PLATE_PATTERN.search(r) else r for r in rows]
        result = CustomAsserts.compare_table_data([plate], actual) if created else {"passed": True, "mismatch": [], "missing": [], "unexpected": []}
        note = f"mismatch={len(result['mismatch'])} missing={len(result['missing'])} unexpected={len(result['unexpected'])}"
        steps.append(step("Table khớp dữ liệu kỳ vọng (0 mismatch/missing/unexpected)", note, result["passed"]))

        # 5) Sửa xe -----------------------------------------------------------
        updated = False
        if created:
            log(worker, "[CRUD] Sửa thông tin xe...", 80)
            driver.get(L.LIST_URL)
            row = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=10)
            if row is not None:
                edit_btn = row.find_element(By.CSS_SELECTOR, L.ROW_EDIT_BTN_CSS)
                safe_click(driver, edit_btn)
                color_item = antd_ui.form_item_by_label(driver, L.LABEL_COLOR)
                color_input = antd_ui.text_input_in_item(color_item)
                if color_input is not None:
                    color_input.click()
                    color_input.clear()
                    color_input.send_keys("Xám khói")
                    save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
                    safe_click(driver, save_btn)
                    try:
                        WebDriverWait(driver, 15).until(
                            lambda d: "xám khói" in (
                                antd_ui.find_row_by_plate(d, L.CAR_TABLE, plate, timeout=1).text or ""
                            ).casefold()
                            if antd_ui.find_row_by_plate(d, L.CAR_TABLE, plate, timeout=1)
                            else False
                        )
                    except Exception:
                        pass
                    row_after = antd_ui.find_row_by_plate(driver, L.CAR_TABLE, plate, timeout=8)
                    updated = bool(row_after) and "xám khói" in (row_after.text or "").casefold()
            steps.append(step("Màu xe được cập nhật đúng", "Đã cập nhật" if updated else "Chưa thấy thay đổi", updated))

        # 6) Xoá xe -------------------------------------------------------------
        deleted = False
        if created and cleanup:
            log(worker, "[CRUD] Xoá xe test...", 92)
            deleted = _delete_by_plate(driver, wait, plate)
            steps.append(step(f"Xe {plate} biến mất khỏi bảng sau khi xoá", "Đã xoá" if deleted else "Vẫn còn", deleted))

        # 7) Thiếu dữ liệu bắt buộc ------------------------------------------------
        log(worker, "[Validation] Kiểm tra bắt lỗi thiếu dữ liệu bắt buộc...", 97)
        _open_add_car_form(driver, wait)
        save_btn = wait.until(EC.element_to_be_clickable(L.SAVE_BTN))
        safe_click(driver, save_btn)
        required_labels = [L.LABEL_LICENSE_PLATE, L.LABEL_BRAND, L.LABEL_MODEL, L.LABEL_FUEL, L.LABEL_YEAR, L.LABEL_STATUS]
        missing_ok = []
        for label in required_labels:
            item = antd_ui.form_item_by_label(driver, label)
            missing_ok.append(bool(antd_ui.field_error_text(item)))
        all_flagged = all(missing_ok)
        steps.append(step(
            "Tất cả field bắt buộc báo lỗi khi để trống",
            f"{sum(missing_ok)}/{len(missing_ok)} field có lỗi",
            all_flagged,
        ))
        back = driver.find_elements(*L.BACK_TO_LIST_LINK)
        if back:
            safe_click(driver, back[0])

        # Dọn dẹp nếu vì lý do gì đó xe vẫn còn (ví dụ bước xoá bị bỏ qua)
        if created and cleanup and not deleted:
            _delete_by_plate(driver, wait, plate)

        passed = all(s["result"] == "PASS" for s in steps)
        log(worker, "Hoàn tất self-test.", 100)
        return {
            "status": "PASSED" if passed else "FAILED",
            "message": f"Quản lý xe: {'đạt AC' if passed else 'còn bước FAIL, xem bảng kết quả'} · biển số test: {plate}",
            "steps": steps,
        }
    except Exception as exc:
        return {
            "status": "FAILED",
            "message": f"Selenium gặp lỗi: {exc.__class__.__name__}: {exc}",
            "error": str(exc),
            "steps": steps,
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
