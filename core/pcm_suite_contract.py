"""Built-in automation contract for the 31 PCM acceptance test cases."""

from __future__ import annotations

from core.suite_loader import PAGE_URLS


def _case(
    number: int,
    page_key: str,
    module: str,
    title: str,
    expected: str,
    scenario_key: str,
    destructive: bool = False,
) -> dict:
    return {
        "tc_id": f"TC{number:02d}",
        "title": title,
        "area": module,
        "module": module,
        "expected": expected,
        "page_key": page_key,
        "source_sheet": "Built-in TestCase_PCM",
        "url": PAGE_URLS[page_key],
        "action_type": "pcm_scenario",
        "scenario_key": scenario_key,
        "destructive": destructive,
        "executable": True,
    }


def pcm_suite_cases() -> list[dict]:
    """Return TC01–TC31 in their agreed acceptance-test order."""
    return [
        _case(1, "plt_login", "Đăng nhập", "Đăng nhập thành công với tài khoản Quản trị viên hợp lệ", "Rời trang login và hiển thị giao diện ứng dụng", "login_admin_success"),
        _case(2, "plt_login", "Đăng nhập", "Đăng nhập thành công với tài khoản Nhân viên hợp lệ", "Tài khoản nhân viên đăng nhập thành công", "login_staff_success"),
        _case(3, "plt_login", "Đăng nhập", "Đăng nhập thất bại khi sai mật khẩu", "Vẫn ở trang login và hiển thị lỗi", "login_wrong_password"),
        _case(4, "plt_login", "Đăng nhập", "Bỏ trống Email và bấm Đăng nhập", "Email bị đánh dấu bắt buộc", "login_blank_email"),
        _case(5, "plt_login", "Đăng nhập", "Bỏ trống Mật khẩu và bấm Đăng nhập", "Mật khẩu bị đánh dấu bắt buộc", "login_blank_password"),
        _case(6, "plt_login", "Đăng nhập", "Bấm icon hiện/ẩn mật khẩu", "Kiểu input đổi giữa password và text", "login_toggle_password"),
        _case(7, "plt_dashboard", "Dashboard", "Kiểm tra tiêu đề trang và breadcrumb Tổng quan / Dashboard", "Tiêu đề hoặc breadcrumb Dashboard hiển thị", "dashboard_title"),
        _case(8, "plt_dashboard", "Dashboard", "Kiểm tra hiển thị đủ 8 thẻ số liệu vận hành", "Có tối thiểu 8 thẻ số liệu hiển thị", "dashboard_cards"),
        _case(9, "plt_dashboard", "Dashboard", "Kiểm tra menu sidebar điều hướng đúng trang", "Menu có đủ 6 module và href hợp lệ", "dashboard_sidebar"),
        _case(10, "plt_dashboard", "Dashboard", "Bấm nút Tạo booking ở khối Thao tác nhanh", "Điều hướng đến trang tạo booking", "dashboard_create_booking"),
        _case(11, "plt_booking", "Đặt xe", "Kiểm tra bảng danh sách booking hiển thị đủ cột", "Bảng có các cột Booking, Xe, Lịch trình, Trạng thái, Thanh toán, Tệp, Tổng tiền, Thao tác", "booking_table_headers"),
        _case(12, "plt_booking", "Đặt xe", "Tìm kiếm booking theo mã booking", "Kết quả tìm kiếm chứa đúng mã booking", "booking_search"),
        _case(13, "plt_booking", "Đặt xe", "Chuyển đổi giữa Dạng danh sách và Dạng lịch", "Hai chế độ hiển thị đều mở được", "booking_view_toggle"),
        _case(14, "plt_booking", "Đặt xe", "Tạo booking mới đầy đủ thông tin", "Form tạo booking mở và có các trường nghiệp vụ bắt buộc", "booking_create_form"),
        _case(15, "plt_booking", "Đặt xe", "Sửa thông tin booking đang ở trạng thái Nháp", "Mở được form chỉnh sửa của booking Nháp", "booking_edit_draft"),
        _case(16, "plt_booking", "Đặt xe", "Xoá booking chưa xác nhận", "Luồng xác nhận xoá hiển thị cho booking chưa xác nhận", "booking_delete_draft"),
        _case(17, "plt_booking", "Đặt xe", "Không cho xoá booking đã xác nhận hoặc đã thanh toán", "Nút xoá không tồn tại hoặc bị vô hiệu ở booking đã xác nhận", "booking_delete_protected"),
        _case(18, "plt_fleet", "Xe", "Kiểm tra bảng danh sách xe hiển thị đủ cột", "Bảng có Ảnh, Xe, Thông số, Trạng thái, Đơn đang thuê, Thao tác", "fleet_table_headers"),
        _case(19, "plt_fleet", "Xe", "Thêm xe mới: chọn Hãng xe thì danh sách Mẫu xe cập nhật", "Dropdown Mẫu xe thay đổi theo Hãng xe", "fleet_dependent_model"),
        _case(20, "plt_fleet", "Xe", "Tìm kiếm hoặc lọc xe theo trạng thái", "Bộ lọc có Sẵn sàng, Đang vệ sinh, Đang bảo dưỡng", "fleet_status_filter"),
        _case(21, "plt_fleet", "Xe", "Sửa thông tin xe", "Form sửa có trường năm, màu và nhiên liệu", "fleet_edit_form"),
        _case(22, "plt_fleet", "Xe", "Xoá xe khỏi đội xe", "Luồng xác nhận xoá xe hiển thị", "fleet_delete_flow"),
        _case(23, "plt_fleet", "Xe", "Đối chiếu Tổng số xe, Sẵn sàng và Đang bảo dưỡng", "Các KPI là số hợp lệ và tổng không nhỏ hơn số dòng đang hiển thị", "fleet_stats"),
        _case(24, "plt_fleet", "Xe", "Kiểm tra mã booking khi xe đang được thuê", "Xe đang thuê có mã booking khác dấu gạch ngang", "fleet_booking_code"),
        _case(25, "plt_vehicle_catalog", "Danh mục xe", "Thêm hãng xe mới qua modal", "Tạo hãng test, thấy trong bảng và cleanup", "catalog_create_brand", True),
        _case(26, "plt_vehicle_catalog", "Danh mục xe", "Thêm mẫu xe mới và chọn Hãng xe", "Tạo mẫu test đúng hãng, thấy trong bảng và cleanup", "catalog_create_model", True),
        _case(27, "plt_vehicle_catalog", "Danh mục xe", "Chỉnh sửa trạng thái hãng xe", "Đổi trạng thái và khôi phục trạng thái ban đầu", "catalog_toggle_brand", True),
        _case(28, "plt_vehicle_catalog", "Danh mục xe", "Kiểm tra ký tự đặc biệt hoặc chuỗi nghi vấn SQL", "Input được escape hoặc hệ thống từ chối an toàn; không làm hỏng bảng", "catalog_input_security", True),
        _case(29, "plt_user", "Người dùng", "Tạo người dùng với email đã tồn tại", "Hiển thị lỗi email trùng và không tạo bản ghi", "user_duplicate_email"),
        _case(30, "plt_user", "Người dùng", "Tạo người dùng mới và gán vai trò", "Role Dropdown có Quản Trị Viên và Nhân Viên; form chấp nhận lựa chọn", "user_role_form"),
        _case(31, "plt_user", "Người dùng", "Đổi trạng thái tài khoản", "Mở được điều khiển trạng thái và có thể khôi phục trạng thái ban đầu", "user_toggle_status", True),
    ]

