"""Tầng Service của module ordering: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Đổi trạng thái đơn khi bàn giao / vận chuyển (cho shipping).
- Tìm đơn QR theo order_code và đánh dấu Đã thanh toán (cho payment).
- Đọc số liệu đơn đã giao để làm báo cáo (cho reporting).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""
