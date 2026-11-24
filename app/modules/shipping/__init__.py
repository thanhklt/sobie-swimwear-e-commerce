"""Module shipping — bàn giao vận chuyển và trang giả lập vận chuyển (BR-006).

Use case: specs/use-cases/shipping/ (UC-36, UC-40).
Bảng sở hữu: không có bảng riêng.

Phạm vi:
- Nhân viên bàn giao từng đơn Đã xác nhận -> Chờ lấy hàng.
- Website giả lập riêng, không cần đăng nhập, chỉ hiển thị mã và trạng thái đơn.
- Nút cập nhật trạng thái giao hàng; giao thành công xuất hóa đơn, giao lỗi hoàn tồn.

Phụ thuộc module khác (chỉ qua service công khai):
- ordering: đổi trạng thái đơn (kéo theo xuất hóa đơn hoặc cộng lại tồn).

Service công khai:
- list_simulator_orders (lọc q / status), update_simulator_status
- list_orders_ready_for_handoff (lọc q), handoff_order
  (E1 ValueError kèm trạng thái thực tế; E2 LookupError không tìm thấy đơn)
"""
