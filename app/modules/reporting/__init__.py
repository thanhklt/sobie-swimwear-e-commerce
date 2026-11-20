"""Module reporting — dashboard, chỉ đọc (BR-007).

Use case: specs/use-cases/reporting/ (UC-37).
Bảng sở hữu: không có bảng riêng.

Phạm vi:
- Doanh thu, lợi nhuận gộp, số đơn theo trạng thái, sản phẩm bán chạy,
- tồn kho thấp, tiền nhập hàng theo nhà cung cấp. Chỉ Nhân viên xem.

Phụ thuộc module khác (chỉ qua service công khai):
- ordering, inventory, catalog: đọc qua service chỉ đọc; không ghi dữ liệu nghiệp vụ.
"""
