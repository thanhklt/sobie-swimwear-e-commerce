"""Module payment — tự đối soát chuyển khoản qua webhook SePay (BR-006).

Use case: specs/use-cases/payment/ (UC-25).
Bảng sở hữu: payment.bank_transaction.

Phạm vi:
- Nhận webhook SePay, xác thực API key nạp từ biến môi trường.
- Chống xử lý trùng theo mã giao dịch SePay; lưu mọi giao dịch (khớp hoặc không).
- Khớp nội dung SOBIE + order_code, số tiền >= tổng thanh toán, đơn còn hạn 24 giờ.
- Không sinh VietQR: phần này thuộc ordering (UC-20), để payment chỉ phụ thuộc một chiều vào ordering.

Phụ thuộc module khác (chỉ qua service công khai):
- ordering: tìm đơn theo order_code, chuyển Đã thanh toán trong cùng transaction ghi giao dịch.
"""
