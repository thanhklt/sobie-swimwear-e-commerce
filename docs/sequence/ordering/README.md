# Sequence diagrams — module ordering

## UI thử (`/dev/ordering`)

| Endpoint | Sequence |
|---|---|
| GET `/dev/ordering/checkout` | [dev-checkout.md](./dev-checkout.md) |
| POST `/dev/ordering/checkout/cod` | [dev-place-cod.md](./dev-place-cod.md) |
| POST `/dev/ordering/checkout/qr` | [dev-place-qr.md](./dev-place-qr.md) |
| GET `/dev/ordering/orders` | [dev-orders-list.md](./dev-orders-list.md) |
| GET `/dev/ordering/orders/{code}` | [dev-order-detail.md](./dev-order-detail.md) |
| POST `/dev/ordering/orders/{code}/cancel` | [dev-cancel-customer.md](./dev-cancel-customer.md) |
| GET `/dev/ordering/orders/{code}/invoice` | [dev-invoice.md](./dev-invoice.md) |
| POST `/dev/ordering/staff/confirm` | [dev-staff-confirm.md](./dev-staff-confirm.md) |
| POST `/dev/ordering/staff/lookup-order` | redirect → staff order detail |
| GET `/dev/ordering/staff/orders/{code}` | [dev-staff-order-detail.md](./dev-staff-order-detail.md) |
| POST `/dev/ordering/staff/mark-paid` | service `mark_order_paid_by_code` |
| POST `/dev/ordering/staff/cancel` | service `cancel_order_by_employee` |
| POST `/dev/ordering/staff/transition` | service `transition_status_for_shipping` |
| POST `/dev/ordering/staff/auto-cancel` | [dev-auto-cancel.md](./dev-auto-cancel.md) |
| GET `/dev/ordering/staff/invoice/{id}` | service `get_invoice_for_staff` |

Route production (storefront) chưa gắn — khi làm sẽ bổ sung sequence riêng.
