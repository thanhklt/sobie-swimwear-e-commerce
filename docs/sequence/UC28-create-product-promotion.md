# UC-28 — Tạo khuyến mãi sản phẩm

```mermaid
sequenceDiagram
    actor NV as Nhân viên
    participant R as Route Promotion
    participant S as Promotion Service
    participant C as Catalog Service
    participant P as Promotion Repository
    participant DB as PostgreSQL
    NV->>R: POST /admin/promotions/validate
    R->>S: validate_promotion(PRODUCT)
    S->>C: Kiểm tra sản phẩm đang bán
    C->>DB: Đọc catalog.product
    DB-->>C: product_key hoặc không tìm thấy
    S->>P: Kiểm tra sản phẩm chưa có promotion đang bật
    P->>DB: Đọc promotion.product_promotion
    alt Thiếu, sai hoặc sản phẩm đang khuyến mãi
        R-->>NV: Hiện lỗi tại trường sản phẩm
    else Hợp lệ
        R-->>NV: Hiện popup tóm tắt
        alt Nhân viên hủy
            NV->>NV: Giữ form, không lưu
        else Nhân viên xác nhận
            NV->>R: POST /admin/promotions/create
            R->>S: create_promotion(PRODUCT)
            S->>DB: Mở transaction, khóa cấp mã
            S->>C: Kiểm tra lại sản phẩm và khuyến mãi
            S->>P: Tạo promotion + product_promotion
            P->>DB: INSERT trong cùng transaction
            DB-->>R: KM-xxxx
            R-->>NV: Chuyển về danh sách
        end
    end
```
