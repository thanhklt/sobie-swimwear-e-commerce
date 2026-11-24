# UC-29 / UC-30 — Tạo khuyến mãi hóa đơn hoặc voucher

```mermaid
sequenceDiagram
    actor NV as Nhân viên
    participant R as Route Promotion
    participant S as Promotion Service
    participant P as Promotion Repository
    participant DB as PostgreSQL
    NV->>R: POST /admin/promotions/validate
    R->>R: Kiểm tra phiên, Origin và trường bắt buộc
    R->>S: validate_promotion(ORDER hoặc CODE)
    S->>P: Kiểm tra mã voucher trùng (nếu là CODE)
    P->>DB: Đọc tham chiếu và kiểm tra duy nhất
    DB-->>R: Hợp lệ hoặc lỗi theo trường
    alt Dữ liệu chưa hợp lệ
        R-->>NV: Trả lỗi tại trường, không hiện xác nhận
    else Dữ liệu hợp lệ
        R-->>NV: Hiện popup tóm tắt để xác nhận
        alt Nhân viên hủy
            NV->>NV: Giữ dữ liệu form, không ghi database
        else Nhân viên xác nhận
            NV->>R: POST /admin/promotions/create
            R->>S: create_promotion(ORDER hoặc CODE)
            S->>DB: Transaction + khóa cấp mã
            S->>S: Kiểm tra lại dữ liệu và tham chiếu
            S->>P: Tạo promotion + bảng con
            P->>DB: INSERT; unique index bảo vệ mã voucher
            DB-->>R: KM-xxxx
            R-->>NV: Chuyển về danh sách
        end
    end
```
