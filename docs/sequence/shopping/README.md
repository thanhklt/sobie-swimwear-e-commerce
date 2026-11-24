# Sequence diagrams — module shopping

## UI thử (`/dev/shopping`)

| Endpoint | Sequence |
|---|---|
| GET `/dev/shopping/cart` | [dev-cart-page.md](./dev-cart-page.md) |
| POST `/dev/shopping/cart/add` | [dev-cart-add.md](./dev-cart-add.md) |
| POST `/dev/shopping/cart/set-qty` | cùng luồng add (gọi `set_cart_item_quantity`) |
| POST `/dev/shopping/cart/remove` | cùng luồng add (gọi `remove_cart_item`) |
| POST `/dev/shopping/cart/merge` | service `merge_guest_cart` |
| Wishlist GET/POST | [dev-wishlist.md](./dev-wishlist.md) |

Route production (storefront) chưa gắn — khi làm sẽ bổ sung sequence riêng.
