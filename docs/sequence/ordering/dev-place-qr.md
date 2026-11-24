# Sequence — POST /dev/ordering/checkout/qr

UI thử (feature/ordering). Actor: developer / tester. UC-20.

```mermaid
sequenceDiagram
  actor U as Tester
  participant R as ordering.router
  participant A as adapters (GD)
  participant S as ordering.service
  participant Shop as shopping.service
  participant Repo as ordering.repository
  participant DB as PostgreSQL

  U->>R: POST shipping + expected_total (QR)
  R->>A: account_key + DbInventory + DbCatalog
  R->>S: place_qr_order(...)
  S->>S: build_quote + validate shipping
  S->>A: deduct_stock (trong transaction)
  S->>Repo: tạo order PENDING + UNPAID + history; payment=QR
  S->>Shop: remove_ordered_variants
  Repo->>DB: ordering.*
  S-->>R: Order
  R-->>U: 303 → /dev/ordering/orders/{code}
  Note over U,R: Chi tiết đơn hiện VietQR (ảnh + SOBIE+code); hạn +24h
```

Sau CK thật: SePay webhook (UC-25, module payment — chưa gắn `/dev`). Tạm dùng staff «Đánh dấu PAID».
