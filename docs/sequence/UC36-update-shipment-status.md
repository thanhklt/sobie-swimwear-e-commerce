# UC-36 — Cập nhật trạng thái giao hàng

```mermaid
sequenceDiagram
    actor Demo as Người demo
    participant R as Route Shipping
    participant S as Shipping Service
    participant O as Ordering Service
    participant I as Inventory Service
    participant C as Catalog Service
    participant P as Ordering Repository
    participant DB as PostgreSQL
    Demo->>R: POST /shipping/orders/{code}/status
    R->>R: Kiểm tra Origin và thao tác
    R->>S: update_simulator_status(code, action)
    S->>O: update_shipping_status(code, action)
    O->>P: Khóa đơn và kiểm tra trạng thái nguồn
    P->>DB: SELECT ... FOR UPDATE
    alt Giao không thành công
        O->>I: Cộng lại tồn trong transaction
    else Giao thành công
        O->>C: Lấy thông tin biến thể chụp hóa đơn
        O->>P: Tạo snapshot hóa đơn; chỉ COD chuyển sang đã thanh toán
    end
    O->>P: Cập nhật trạng thái và ghi lịch sử
    P->>DB: COMMIT
    R-->>Demo: Tải lại danh sách trạng thái
```
