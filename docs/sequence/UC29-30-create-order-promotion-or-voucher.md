# UC-29 / UC-30 — Tạo khuyến mãi hóa đơn hoặc voucher

```mermaid
sequenceDiagram
    actor NV as Nhân viên
    participant R as Route Promotion
    participant S as Promotion Service
    participant P as Promotion Repository
    participant DB as PostgreSQL
    NV->>R: POST /admin/promotions/create (Xác nhận)
    R->>R: Kiểm tra phiên, Origin và dữ liệu
    R->>S: create_promotion(ORDER hoặc CODE)
    S->>DB: Mở transaction, khóa cấp mã
    S->>S: Kiểm tra phần trăm, ngưỡng, lượt và ngày
    S->>P: Tạo promotion + bảng con
    P->>DB: INSERT; unique index bảo vệ mã voucher
    DB-->>R: KM-xxxx
    R-->>NV: Chuyển về danh sách
```
