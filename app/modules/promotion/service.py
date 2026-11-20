"""Tầng Service của module promotion: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Giá sau giảm theo sản phẩm (cho catalog, ordering).
- Tính mức giảm cho đơn; tăng / hoàn lượt trong transaction của bên gọi (cho ordering).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""
