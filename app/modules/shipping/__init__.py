"""Module shipping — bàn giao vận chuyển và trang giả lập vận chuyển (BR-006).

Use case: specs/use-cases/shipping/ (UC-36, UC-40).
Bảng sở hữu: không có bảng riêng.

Phạm vi:
- Nhân viên bàn giao từng đơn Đã xác nhận -> Chờ lấy hàng.
- Website giả lập riêng, không cần đăng nhập, chỉ hiển thị mã và trạng thái đơn.
- Nút cập nhật trạng thái giao hàng; giao thành công xuất hóa đơn, giao lỗi hoàn tồn.

Phụ thuộc module khác (chỉ qua service công khai):
- ordering: đổi trạng thái đơn (kéo theo xuất hóa đơn hoặc cộng lại tồn).
"""
