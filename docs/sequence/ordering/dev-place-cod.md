# Sequence — POST /dev/ordering/checkout/cod

UI thử (feature/ordering). Actor: developer / tester.

Snapshot địa chỉ từ sổ (shipping_address_key → identity → ShippingInfo).

```mermaid
sequenceDiagram
  actor U as Tester
  participant R as ordering.router
  participant A as adapters (GD)
  participant Id as identity.service
  participant S as ordering.service
  participant Shop as shopping.service
  participant Repo as ordering.repository
  participant DB as PostgreSQL

  U->>R: POST shipping_address_key + expected_total
  R->>A: account_key + DbInventory + DbCatalog
  R->>Id: get_shipping_address(key)
  Id-->>R: ShippingAddressView
  R->>S: place_cod_order(shipping snapshot)
  S->>S: build_quote + validate shipping
  S->>A: deduct_stock (trong transaction)
  S->>Repo: tạo order + details + history
  S->>Shop: remove_ordered_variants
  Repo->>DB: ordering.*
  S-->>R: Order
  R-->>U: 303 → /dev/ordering/orders/{code}
```
