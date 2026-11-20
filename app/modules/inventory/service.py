"""Tầng Service của module inventory: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Đọc tồn kho theo biến thể (cho catalog, shopping, reporting).
- Trừ / cộng tồn trong transaction của bên gọi (cho ordering).
- Đọc giá vốn hiện tại (cho ordering, reporting).
- Tạo dòng tồn kho khi tạo biến thể (cho catalog).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""
