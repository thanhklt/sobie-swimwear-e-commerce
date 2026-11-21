"""Module ordering — đặt hàng, vòng đời đơn, hóa đơn (BR-003).

Use case: specs/use-cases/ordering/ (UC-19 → UC-24, UC-26, UC-27).
Bảng sở hữu: ordering.payment, ordering.order, ordering.order_detail, ordering.order_status_history, ordering.invoice.

Phạm vi:
- Đặt hàng COD / QR: sinh order_code (8 ký tự Crockford Base32), chụp thông tin nhận hàng.
- Sinh dữ liệu VietQR cho đơn QR (tài khoản cửa hàng, số tiền, nội dung SOBIE + order_code),
  hiển thị khi đặt hàng (UC-20) và ở chi tiết đơn chưa thanh toán (UC-21).
- Trừ tồn, áp khuyến mãi / tăng lượt và tạo đơn trong cùng 1 transaction.
- Theo dõi, hủy (khách / Nhân viên có lý do), xác nhận đơn; tự hủy đơn QR quá 24 giờ.
- Ghi lịch sử mỗi lần đổi trạng thái đơn.
- Tự xuất hóa đơn khi đơn sang Giao thành công (mã HD-<order_code>, snapshot); chỉ xem.

Phụ thuộc module khác (chỉ qua service công khai):
- shopping: các dòng giỏ cần đặt.
- catalog: giá bán theo size lúc đặt.
- inventory: trừ / cộng lại tồn, đọc giá vốn để chụp vào order_detail_cost_price.
- promotion: tính mức giảm, tăng / hoàn lượt khuyến mãi.
- identity: thông tin người đặt.
"""
