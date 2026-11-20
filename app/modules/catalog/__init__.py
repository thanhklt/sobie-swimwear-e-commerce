"""Module catalog — sản phẩm, biến thể, giá, phân loại (BR-002).

Use case: specs/use-cases/catalog/ (UC-09 → UC-17).
Bảng sở hữu: catalog.category, catalog.collection, catalog.gender, catalog.size, catalog.color, catalog.product, catalog.product_collection, catalog.variant, catalog.gallery.

Phạm vi:
- Trang chủ, trang danh mục (lọc, sắp xếp, phân trang), tìm kiếm, chi tiết sản phẩm, trang thông tin cố định.
- Quản lý sản phẩm, biến thể màu × size, giá bán theo size, danh mục / bộ sưu tập / thuộc tính.
- Cấp mã SP-<4 số> và SKU <mã SP>-<MÀU>-<SIZE>.

Phụ thuộc module khác (chỉ qua service công khai):
- inventory: đọc tồn kho để hiện còn / hết hàng; tạo dòng tồn kho khi tạo biến thể.
- promotion: đọc giá sau khuyến mãi theo sản phẩm để hiển thị.
"""
