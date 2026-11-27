# Sequence — GET /dev/ordering/orders/{code}

UI thử chi tiết đơn (UC-20 xem lại VietQR khi còn hạn + UNPAID).

```mermaid
sequenceDiagram
  actor U as Tester / KH
  participant R as ordering.router
  participant A as adapters (GD)
  participant S as ordering.service
  participant Repo as ordering.repository
  participant DB as PostgreSQL

  U->>R: GET /dev/ordering/orders/{code}
  R->>A: get_account_key_by_email
  R->>S: get_customer_order
  S->>Repo: load order + list_status_history
  Repo->>DB: ordering.*
  S->>S: to_order_view (VietQR + status_history, note=None)
  S-->>R: OrderView
  R-->>U: HTML — Tạo + timeline trạng thái (không lý do hủy) + QR nếu còn
```

Ghi chú:

- Timeline dưới thời gian tạo; mỗi lần NV/hệ thống đổi status → thêm mốc `changed_at`.
- KH không thấy `order_status_history_note`; NV xem qua `get_staff_order`.
- Quét VietQR không gọi app. PAID qua SePay (UC-25) /dev giả webhook.
