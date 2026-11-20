"""Tầng Service của module identity: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Lấy tài khoản và vai trò theo account_key (kiểm tra quyền mỗi request).
- Lấy thông tin nhận hàng mặc định của Khách hàng (cho ordering).
- Lấy customer_key theo account_key (cho shopping).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""
