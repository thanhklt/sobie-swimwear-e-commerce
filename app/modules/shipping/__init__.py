"""Module shipping — bàn giao vận chuyển và trang giả lập vận chuyển (BR-006).

Use case: specs/use-cases/shipping/ (UC-36, UC-40).
Bảng sở hữu: không có bảng riêng.

Phạm vi:
- Nhân viên bàn giao đơn Đã xác nhận -> Chờ lấy hàng.
- Trang giả lập vận chuyển (1 trang, không cần đăng nhập): Đã nhận hàng, Đã giao, Giao không thành công.

Phụ thuộc module khác (chỉ qua service công khai):
- ordering: đổi trạng thái đơn (kéo theo xuất hóa đơn hoặc cộng lại tồn).
"""
