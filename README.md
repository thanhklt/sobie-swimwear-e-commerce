# Sobie — thương mại điện tử đồ bơi

Dự án tổ chức theo **modular monolith**: một ứng dụng gồm 9 module nghiệp vụ.

Hiện repo **chỉ có khung thư mục / file** (mỗi file chỉ có docstring mô tả trách nhiệm). Chưa chọn framework, chưa khai báo thư viện, chưa có API, kết nối database hay logic nghiệp vụ.

## Tài liệu

| Tài liệu | Vị trí |
|---|---|
| Business requirements | [specs/business-requirements/BR-GIAIDOAN1.md](specs/business-requirements/BR-GIAIDOAN1.md) |
| Use case theo module | [specs/use-cases/](specs/use-cases/README.md) |
| Data model hiện hành | [specs/entity-model/data_model_v2.dbml](specs/entity-model/data_model_v2.dbml) (bản vẽ Mermaid: [data_model_v2.md](specs/entity-model/data_model_v2.md)) |
| Entity diagram (SDD Tầng 3) | [specs/entity-model/entity_diagram_v2.md](specs/entity-model/entity_diagram_v2.md) |
| Schema và dữ liệu mẫu PostgreSQL | [infra/postgres/init.sql](infra/postgres/init.sql), [infra/postgres/seed.sql](infra/postgres/seed.sql) |
| Quy tắc cho agent | [AGENTS.md](AGENTS.md) |

## Module

Một module dùng chung **một tên** cho: thư mục use case `specs/use-cases/<module>/`, schema PostgreSQL, `TableGroup` trong data model và package `app/modules/<module>/`.

| Module | BR | Phạm vi | Bảng | Use case |
|---|---|---|---|---|
| `identity` | BR-001 | Vai trò, tài khoản (gồm thông tin cá nhân của cả 3 vai trò), phiên đăng nhập | role, account, session | UC-01 → 08 |
| `catalog` | BR-002 | Sản phẩm, biến thể, giá bán theo size, phân loại, ảnh | category, collection, gender, size, color, product, product_collection, variant, gallery | UC-09 → 17 |
| `shopping` | BR-002, BR-003 | Giỏ hàng, danh sách yêu thích | cart, cart_item, wishlist, wishlist_item | UC-18, 38 |
| `ordering` | BR-003 | Đặt hàng, VietQR, vòng đời đơn, hủy đơn, hóa đơn | payment (phương thức), order, order_detail, order_status_history, invoice | UC-19 → 24, 26, 27 |
| `payment` | BR-006 | Webhook SePay, tự đối soát chuyển khoản | bank_transaction | UC-25 |
| `promotion` | BR-004 | Khuyến mãi theo sản phẩm, theo hóa đơn, voucher | promotion, product_promotion, order_promotion, code_promotion | UC-28 → 31 |
| `inventory` | BR-005 | Nhà cung cấp, phiếu nhập, tồn kho, giá vốn | supplier, goods_receipt, goods_receipt_detail, stock | UC-32 → 35, 39 |
| `shipping` | BR-006 | Bàn giao vận chuyển, trang giả lập vận chuyển | (không có) | UC-36, 40 |
| `reporting` | BR-007 | Dashboard, chỉ đọc | (không có) | UC-37 |

## Cấu trúc thư mục

```text
soobin-swimwear-e-commerce/
├── app/
│   ├── main.py                     # Khởi tạo ứng dụng, đăng ký router của 9 module
│   ├── config/settings.py          # Nạp cấu hình từ biến môi trường
│   ├── database/
│   │   ├── engine.py               # Async engine, session factory
│   │   └── transaction.py          # Transaction đi qua nhiều module
│   ├── security/session.py         # Middleware phiên, kiểm tra vai trò
│   ├── shared/web/                 # Template và cấu hình render HTML dùng chung
│   │   ├── rendering.py
│   │   └── templates/base.html
│   ├── static/css/
│   ├── money.py                    # VND / Decimal, ROUND_HALF_UP
│   └── modules/
│       ├── identity/
│       ├── catalog/
│       ├── shopping/
│       ├── ordering/               # có thêm jobs.py (tự hủy đơn QR quá hạn)
│       ├── payment/
│       ├── promotion/
│       ├── inventory/
│       ├── shipping/               # không có repository.py, models.py
│       └── reporting/              # không có repository.py, models.py
├── tests/<module>/                 # Test theo module: test_ucXX_acN_<slug>
├── specs/                          # BR, use case, data model
├── infra/                          # Hạ tầng PostgreSQL
├── pyproject.toml
├── .env.example
└── AGENTS.md
```

## Cấu trúc mỗi module

```text
app/modules/<module>/
├── __init__.py      # Phạm vi, bảng sở hữu, use case, phụ thuộc
├── router.py        # Nhận request, kiểm tra dữ liệu, gọi service
├── service.py       # Nghiệp vụ, transaction, service công khai cho module khác
├── repository.py    # Truy vấn bảng do module sở hữu
├── schemas.py       # Schema đầu vào / đầu ra API
└── models.py        # Model lưu trữ (schema PostgreSQL cùng tên module)
```

Luồng bắt buộc: `Route → Service → Repository → Database`. Module chỉ gọi **service công khai** của module khác; không import repository / model hoặc truy cập bảng của module khác. Thao tác đi qua nhiều module (trừ tồn + áp khuyến mãi + tạo đơn) chạy trong cùng một transaction: service gọi truyền session cho service được gọi.

## Trạng thái và phần còn chờ

- Chưa chọn framework web, ORM, công cụ migration; `pyproject.toml` chưa khai báo thư viện.
- `init.sql` và `seed.sql` đã chạy thử trên PostgreSQL 16 (21/11/2026).
- Docker Compose chạy PostgreSQL 16 và tự nạp `init.sql` rồi `seed.sql` khi volume còn trống (`docker compose -f infra/docker-compose.yml up -d`).
