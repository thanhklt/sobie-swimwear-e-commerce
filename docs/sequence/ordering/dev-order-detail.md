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
  S->>Repo: load order (+ payment name)
  Repo->>DB: ordering.*
  S->>S: to_order_view (_show_qr, transfer SOBIE+code, VietQR URL từ VIETQR_*)
  S-->>R: OrderView
  alt show_qr
    R-->>U: HTML + ảnh VietQR + TK + nội dung CK
  else đã PAID / hủy / quá hạn
    R-->>U: HTML không hiện QR
  end
```

Ghi chú:

- Quét VietQR **không** gọi app — chỉ giúp KH CK đúng TK/số tiền/nội dung.
- Production: SePay webhook (UC-25) → `mark_order_paid_by_code` → PAID, ẩn QR; đơn vẫn PENDING tới UC-23.
- `/dev`: POST staff «Đánh dấu PAID» giả webhook; chưa implement endpoint SePay.
