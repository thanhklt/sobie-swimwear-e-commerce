"""Module shopping — giỏ hàng và danh sách yêu thích (BR-002, BR-003).

Use case: specs/use-cases/shopping/ (UC-18, UC-38).
Bảng sở hữu: shopping.cart, shopping.cart_item, shopping.wishlist, shopping.wishlist_item.

Phạm vi:
- Giỏ hàng của Khách hàng đăng nhập (DB); giỏ khách vãng lai ở localStorage, gộp khi đăng nhập.
- Giỏ không lưu giá, luôn hiển thị giá hiện tại.
- Danh sách yêu thích: mỗi sản phẩm 1 lần.

Phụ thuộc module khác (chỉ qua service công khai):
- identity: customer_key của tài khoản đang đăng nhập.
- catalog: thông tin và giá biến thể.
- inventory: tồn kho để giới hạn số lượng.
"""
