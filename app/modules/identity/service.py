"""Tầng Service của module identity: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Lấy tài khoản và vai trò từ mã phiên trong cookie, gia hạn phiên (kiểm tra quyền mỗi request).
- Lấy thông tin nhận hàng mặc định của Khách hàng (cho ordering).
- Kiểm tra tài khoản có vai trò Khách hàng (cho shopping).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""
