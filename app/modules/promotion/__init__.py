"""Module promotion — khuyến mãi theo sản phẩm, theo hóa đơn, voucher (BR-004).

Use case: specs/use-cases/promotion/ (UC-28 → UC-31).
Bảng sở hữu: promotion.promotion, promotion.product_promotion, promotion.order_promotion, promotion.code_promotion.

Phạm vi:
- Tạo (có popup xác nhận) và kết thúc khuyến mãi; không sửa, không bật lại.
- Theo sản phẩm: 1 khuyến mãi = 1 sản phẩm, hiệu lực ngay khi tạo.
- Theo hóa đơn / voucher: có thời điểm bắt đầu / kết thúc, số lượt.
- Chọn mức giảm có lợi hơn giữa hóa đơn và voucher (bằng nhau ưu tiên voucher).
- Cấp mã KM-<4 số>.

Phụ thuộc module khác (chỉ qua service công khai):
- catalog: kiểm tra sản phẩm tồn tại khi tạo khuyến mãi theo sản phẩm.
"""
