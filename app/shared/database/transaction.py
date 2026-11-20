"""Quản lý transaction dùng chung; chưa triển khai.

Các thao tác đi qua nhiều module (trừ tồn + áp khuyến mãi + tạo đơn; ghi giao dịch SePay +
đánh dấu đơn đã thanh toán) phải chạy trong cùng 1 transaction: service của module gọi
truyền session / unit of work cho service của module được gọi.
"""
