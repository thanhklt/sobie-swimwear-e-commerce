"""Module inventory — nhà cung cấp, phiếu nhập, tồn kho, giá vốn (BR-005).

Use case: specs/use-cases/inventory/ (UC-32 → UC-35, UC-39).
Bảng sở hữu: inventory.supplier, inventory.goods_receipt, inventory.goods_receipt_detail, inventory.stock.

Phạm vi:
- Quản lý nhà cung cấp (NCC-<4 số>), lập và xác nhận phiếu nhập (PN-<4 số>).
- Xác nhận phiếu: cộng tồn, tính lại giá vốn bình quân gia quyền theo biến thể.
- Tồn kho không bao giờ âm; chỉ module này ghi inventory.stock.
- Cộng lại tồn khi hủy đơn / giao không thành công (giá vốn không đổi).
- Xem tồn kho; ngưỡng tồn kho thấp hard-code.

Phụ thuộc module khác (chỉ qua service công khai):
- catalog: kiểm tra biến thể tồn tại.
"""
