# UC-36 — Danh sách đơn trên trang vận chuyển

```mermaid
sequenceDiagram
    actor Demo as Người demo
    participant R as Route Shipping
    participant SS as Shipping Service
    participant O as Ordering Service
    participant P as Ordering Repository
    participant DB as PostgreSQL
    Demo->>R: GET /shipping/
    R->>SS: list_simulator_orders(db)
    SS->>O: list_shipping_orders(db)
    O->>P: Đọc đơn AWAITING_PICKUP / SHIPPING
    P->>DB: SELECT mã đơn và trạng thái
    DB-->>R: Danh sách không chứa thông tin cá nhân
    R-->>Demo: Website giả lập vận chuyển
```
