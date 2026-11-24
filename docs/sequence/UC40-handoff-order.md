# UC-40 — Bàn giao đơn vận chuyển

```mermaid
sequenceDiagram
    actor NV as Nhân viên
    participant R as Route Shipping
    participant S as Shipping Service
    participant O as Ordering Service
    participant P as Ordering Repository
    participant DB as PostgreSQL
    NV->>R: POST /admin/shipping/{code}/handoff
    R->>R: Kiểm tra phiên Nhân viên và Origin
    R->>S: handoff_order(code, account_key)
    S->>O: handoff_order(code, account_key)
    O->>P: Chuyển CONFIRMED thành AWAITING_PICKUP
    P->>DB: UPDATE có điều kiện + INSERT lịch sử trạng thái
    alt Đơn đã xác nhận
        DB-->>R: Commit
        R-->>NV: Danh sách chờ bàn giao cập nhật
    else Đơn chưa xác nhận hoặc không tồn tại
        O->>P: Đọc trạng thái hiện tại theo mã đơn
        P->>DB: SELECT order_status
        DB-->>R: Trạng thái hiện tại hoặc không tìm thấy
        R-->>NV: Hiện lỗi cụ thể; không đổi đơn
    end
```
