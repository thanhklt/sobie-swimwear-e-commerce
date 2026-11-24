# UC-28 — Danh sách khuyến mãi sản phẩm

```mermaid
sequenceDiagram
    actor NV as Nhân viên
    participant R as Route Promotion
    participant S as Promotion Service
    participant P as Promotion Repository
    participant C as Catalog Service
    participant DB as PostgreSQL
    NV->>R: GET /admin/promotions
    R->>R: Kiểm tra phiên Nhân viên
    R->>S: list_promotions(db)
    S->>P: list_promotions(db)
    P->>DB: Đọc promotion và bảng con
    DB-->>P: Danh sách chương trình
    P-->>S: Bản ghi khuyến mãi
    S-->>R: Trạng thái hiển thị
    R->>C: active_products_for_promotion(db)
    C->>DB: Đọc sản phẩm đang bán để chọn khi tạo
    DB-->>C: Mã và tên sản phẩm
    R-->>NV: Trang danh sách
```
