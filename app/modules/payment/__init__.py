"""Module payment — tự đối soát chuyển khoản qua webhook SePay (BR-006).

Use case: specs/use-cases/payment/ (UC-25 (hiển thị VietQR dùng ở UC-20)).
Bảng sở hữu: payment.bank_transaction.

Phạm vi:
- Nhận webhook SePay, xác thực API key nạp từ biến môi trường.
- Chống xử lý trùng theo mã giao dịch SePay; lưu mọi giao dịch (khớp hoặc không).
- Khớp nội dung SOBIE + order_code, số tiền >= tổng thanh toán, đơn còn hạn 24 giờ.
- Sinh dữ liệu VietQR (tài khoản cửa hàng, số tiền, nội dung chuyển khoản).

Phụ thuộc module khác (chỉ qua service công khai):
- ordering: tìm đơn theo order_code, chuyển Đã thanh toán trong cùng transaction ghi giao dịch.
"""
