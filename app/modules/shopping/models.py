"""Model lưu trữ của module shopping (schema PostgreSQL `shopping`).

Bảng sở hữu (theo data_model_v2 + bổ sung trên feature/shopping):
- shopping.cart
- shopping.cart_item
- shopping.wishlist
- shopping.wishlist_item (+ wishlist_item_added_at [GD] cho UC-38 AC-3)
- shopping.cart_merge_request [GD] cho UC-18 AC-10/AC-11
"""
