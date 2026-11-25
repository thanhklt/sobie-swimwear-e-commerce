-- =====================================================================
-- Soobin Swimwear — schema PostgreSQL (data model v2)
-- Nguồn: specs/entity-model/data_model_v2.dbml (bản vẽ: data_model_v2.md)
-- Yêu cầu: PostgreSQL 13+ (gen_random_uuid() có sẵn), extension pgcrypto
--          (seed.sql dùng crypt() để băm mật khẩu mẫu).
-- Chạy 1 lần trên database trống (docker-entrypoint-initdb.d), trước seed.sql.
--
-- Quy ước:
--   - 1 module = 1 schema: identity, catalog, shopping, ordering, payment,
--     promotion, inventory (shipping, reporting không có bảng).
--   - Khóa chính uuid hậu tố _key; mã tự nhiên hậu tố _id (do service cấp).
--   - Tiền numeric(12,0) (số nguyên VND); thời gian timestamptz (UTC).
--   - Trạng thái là varchar + CHECK, không dùng PostgreSQL enum.
--   - Khóa ngoại giữa các schema giữ toàn vẹn dữ liệu; code của module chỉ
--     đọc / ghi bảng của chính module đó.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE SCHEMA identity;
CREATE SCHEMA catalog;
CREATE SCHEMA shopping;
CREATE SCHEMA ordering;
CREATE SCHEMA payment;
CREATE SCHEMA promotion;
CREATE SCHEMA inventory;

-- ---------------------------------------------------------------------
-- identity
-- ---------------------------------------------------------------------

CREATE TABLE identity.role (
  role_key  uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  role_code varchar(50)  NOT NULL UNIQUE CHECK (role_code IN ('customer', 'employee', 'admin')),
  role_name varchar(100) NOT NULL UNIQUE
);

CREATE TABLE identity.account (
  account_key           uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id            varchar(100) NOT NULL UNIQUE
                        CHECK (account_id ~ '^(KH-[0-9]{8}|(NV|AD)-[A-Z0-9]+-[0-9]{8})-[0-9]{4}$'),
  account_role_key      uuid         NOT NULL REFERENCES identity.role (role_key) ON DELETE RESTRICT,
  account_email         varchar(255) NOT NULL UNIQUE,
  account_phone_number  varchar(20)  NOT NULL UNIQUE,
  account_hash_password varchar(255) NOT NULL,
  account_status        varchar(20)  NOT NULL DEFAULT 'ACTIVE' CHECK (account_status IN ('ACTIVE', 'LOCKED')),
  account_name          varchar(255) NOT NULL,
  account_date_of_birth date,
  account_house_number  varchar(255),
  account_ward          varchar(100),
  account_city          varchar(255),
  account_country       varchar(100),
  account_created_at    timestamptz  NOT NULL DEFAULT now(),
  -- Nhân viên / Admin bắt buộc ngày sinh (mã dùng ngày sinh); vai trò nằm ở bảng
  -- role nên service kiểm tra theo vai trò, ở đây chỉ kiểm tra theo tiền tố mã.
  CONSTRAINT account_staff_dob_required
    CHECK (account_id LIKE 'KH-%' OR account_date_of_birth IS NOT NULL)
);
CREATE INDEX account_role_key_idx ON identity.account (account_role_key);

-- Phiên đăng nhập phía server (data model v2.15, Q35). Cookie chỉ chứa mã phiên gốc;
-- bảng lưu bản băm SHA-256 (hex). Hạn: Khách hàng 30 phút, Nhân viên / Admin 1 giờ,
-- service gia hạn expires_at khi còn thao tác. Đổi mật khẩu / đổi vai trò / khóa
-- tài khoản xóa mọi dòng của tài khoản.
CREATE TABLE identity.session (
  session_key          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  session_account_key  uuid        NOT NULL REFERENCES identity.account (account_key) ON DELETE CASCADE,
  session_token_hash   varchar(64) NOT NULL UNIQUE,
  session_created_at   timestamptz NOT NULL DEFAULT now(),
  session_last_seen_at timestamptz NOT NULL DEFAULT now(),
  session_expires_at   timestamptz NOT NULL,
  CONSTRAINT session_expires_after_created CHECK (session_expires_at > session_created_at)
);
CREATE INDEX session_account_key_idx ON identity.session (session_account_key);
CREATE INDEX session_expires_at_idx ON identity.session (session_expires_at);

-- ---------------------------------------------------------------------
-- catalog
-- ---------------------------------------------------------------------

CREATE TABLE catalog.category (
  category_key  uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  category_name varchar(255) NOT NULL UNIQUE
);

CREATE TABLE catalog.collection (
  collection_key  uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_name varchar(255) NOT NULL UNIQUE
);

CREATE TABLE catalog.gender (
  gender_key  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  gender_name varchar(50) NOT NULL UNIQUE
);

CREATE TABLE catalog.size (
  size_key  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  size_name varchar(50) NOT NULL UNIQUE
);

CREATE TABLE catalog.color (
  color_key  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  color_name varchar(50) NOT NULL UNIQUE
);

CREATE TABLE catalog.product (
  product_key                uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id                 varchar(10)  NOT NULL UNIQUE CHECK (product_id ~ '^SP-[0-9]{4}$'),
  product_name               varchar(255) NOT NULL,
  product_description        text,
  product_total_score_review numeric(3,2) NOT NULL DEFAULT 0,
  product_status             varchar(20)  NOT NULL DEFAULT 'INACTIVE' CHECK (product_status IN ('ACTIVE', 'INACTIVE')),
  product_created_at         timestamptz  NOT NULL DEFAULT now(),
  product_updated_at         timestamptz  NOT NULL DEFAULT now(),
  product_category_key       uuid         NOT NULL REFERENCES catalog.category (category_key) ON DELETE RESTRICT,
  product_gender_key         uuid         NOT NULL REFERENCES catalog.gender (gender_key) ON DELETE RESTRICT
);
CREATE INDEX product_created_at_idx ON catalog.product (product_created_at DESC);

CREATE TABLE catalog.product_collection (
  product_collection_product_key    uuid NOT NULL REFERENCES catalog.product (product_key) ON DELETE CASCADE,
  product_collection_collection_key uuid NOT NULL REFERENCES catalog.collection (collection_key) ON DELETE RESTRICT,
  PRIMARY KEY (product_collection_product_key, product_collection_collection_key)
);

CREATE TABLE catalog.variant (
  variant_key         uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_id          varchar(60)   NOT NULL UNIQUE CHECK (variant_id ~ '^SP-[0-9]{4}-[A-Z0-9]+-[A-Z0-9]+$'),
  variant_product_key uuid          NOT NULL REFERENCES catalog.product (product_key) ON DELETE RESTRICT,
  variant_size_key    uuid          NOT NULL REFERENCES catalog.size (size_key) ON DELETE RESTRICT,
  variant_color_key   uuid          NOT NULL REFERENCES catalog.color (color_key) ON DELETE RESTRICT,
  variant_sell_price  numeric(12,0) CHECK (variant_sell_price > 0),  -- NULL = size chưa có giá
  variant_status      varchar(20)   NOT NULL DEFAULT 'ACTIVE' CHECK (variant_status IN ('ACTIVE', 'INACTIVE')),
  CONSTRAINT variant_product_size_color_uq UNIQUE (variant_product_key, variant_size_key, variant_color_key)
);
CREATE INDEX variant_product_size_idx ON catalog.variant (variant_product_key, variant_size_key);

CREATE TABLE catalog.gallery (
  gallery_key         uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  gallery_product_key uuid         NOT NULL REFERENCES catalog.product (product_key) ON DELETE CASCADE,
  gallery_order_no    int          NOT NULL,
  gallery_url         varchar(500) NOT NULL,
  CONSTRAINT gallery_product_order_uq UNIQUE (gallery_product_key, gallery_order_no)
);

-- ---------------------------------------------------------------------
-- shopping
-- ---------------------------------------------------------------------

CREATE TABLE shopping.wishlist (
  wishlist_key         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wishlist_account_key uuid NOT NULL UNIQUE REFERENCES identity.account (account_key) ON DELETE CASCADE
);

CREATE TABLE shopping.wishlist_item (
  wishlist_item_key          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wishlist_item_wishlist_key uuid NOT NULL REFERENCES shopping.wishlist (wishlist_key) ON DELETE CASCADE,
  wishlist_item_product_key  uuid NOT NULL REFERENCES catalog.product (product_key) ON DELETE CASCADE,
  CONSTRAINT wishlist_item_wishlist_product_uq UNIQUE (wishlist_item_wishlist_key, wishlist_item_product_key)
);

CREATE TABLE shopping.cart (
  cart_key         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_account_key uuid NOT NULL UNIQUE REFERENCES identity.account (account_key) ON DELETE CASCADE
);

CREATE TABLE shopping.cart_item (
  cart_item_key         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_item_cart_key    uuid NOT NULL REFERENCES shopping.cart (cart_key) ON DELETE CASCADE,
  cart_item_variant_key uuid NOT NULL REFERENCES catalog.variant (variant_key) ON DELETE CASCADE,
  cart_item_quantity    int  NOT NULL DEFAULT 1 CHECK (cart_item_quantity > 0),
  CONSTRAINT cart_item_cart_variant_uq UNIQUE (cart_item_cart_key, cart_item_variant_key)
);

-- ---------------------------------------------------------------------
-- inventory
-- ---------------------------------------------------------------------

CREATE TABLE inventory.supplier (
  supplier_key          uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  supplier_id           varchar(10)  NOT NULL UNIQUE CHECK (supplier_id ~ '^NCC-[0-9]{4}$'),
  supplier_name         varchar(255) NOT NULL,
  supplier_phone_number varchar(20)  NOT NULL,
  supplier_email        varchar(255),
  supplier_address      varchar(255),
  supplier_status       varchar(20)  NOT NULL DEFAULT 'ACTIVE' CHECK (supplier_status IN ('ACTIVE', 'INACTIVE'))
);

CREATE TABLE inventory.goods_receipt (
  goods_receipt_key          uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  goods_receipt_id           varchar(10)   NOT NULL UNIQUE CHECK (goods_receipt_id ~ '^PN-[0-9]{4}$'),
  goods_receipt_final_price  numeric(12,0) NOT NULL DEFAULT 0 CHECK (goods_receipt_final_price >= 0),
  goods_receipt_status       varchar(20)   NOT NULL DEFAULT 'DRAFT' CHECK (goods_receipt_status IN ('DRAFT', 'CONFIRMED', 'CANCELLED')),
  goods_receipt_created_date timestamptz   NOT NULL DEFAULT now(),
  goods_receipt_supplier_key uuid          NOT NULL REFERENCES inventory.supplier (supplier_key) ON DELETE RESTRICT,
  goods_receipt_account_key  uuid          NOT NULL REFERENCES identity.account (account_key) ON DELETE RESTRICT
);

CREATE TABLE inventory.goods_receipt_detail (
  goods_receipt_detail_key               uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  goods_receipt_detail_goods_receipt_key uuid          NOT NULL REFERENCES inventory.goods_receipt (goods_receipt_key) ON DELETE CASCADE,
  goods_receipt_detail_variant_key       uuid          NOT NULL REFERENCES catalog.variant (variant_key) ON DELETE RESTRICT,
  goods_receipt_detail_quantity          int           NOT NULL CHECK (goods_receipt_detail_quantity > 0),
  goods_receipt_detail_unit_price        numeric(12,0) NOT NULL CHECK (goods_receipt_detail_unit_price >= 0),
  goods_receipt_detail_total_price       numeric(12,0) NOT NULL,
  CONSTRAINT goods_receipt_detail_total_ck
    CHECK (goods_receipt_detail_total_price = goods_receipt_detail_quantity * goods_receipt_detail_unit_price),
  CONSTRAINT goods_receipt_detail_receipt_variant_uq
    UNIQUE (goods_receipt_detail_goods_receipt_key, goods_receipt_detail_variant_key)
);

CREATE TABLE inventory.stock (
  stock_key         uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  stock_variant_key uuid          NOT NULL UNIQUE REFERENCES catalog.variant (variant_key) ON DELETE RESTRICT,
  stock_quantity    int           NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),  -- tồn kho không bao giờ âm
  stock_cost_price  numeric(12,0) NOT NULL DEFAULT 0 CHECK (stock_cost_price >= 0)
);

-- ---------------------------------------------------------------------
-- promotion
-- ---------------------------------------------------------------------

CREATE TABLE promotion.promotion (
  promotion_key         uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  promotion_id          varchar(10) NOT NULL UNIQUE CHECK (promotion_id ~ '^KM-[0-9]{4}$'),
  promotion_type        varchar(20) NOT NULL CHECK (promotion_type IN ('PRODUCT', 'ORDER', 'CODE')),
  promotion_quantity    int,
  promotion_used_amount int         NOT NULL DEFAULT 0 CHECK (promotion_used_amount >= 0),
  promotion_start_date  timestamptz,
  promotion_end_date    timestamptz,
  promotion_status      varchar(20) NOT NULL DEFAULT 'ENABLED' CHECK (promotion_status IN ('ENABLED', 'DISABLED')),
  -- PRODUCT: không có ngày bắt đầu / kết thúc, không giới hạn lượt.
  -- ORDER / CODE: có ngày bắt đầu / kết thúc và số lượt.
  CONSTRAINT promotion_type_fields_ck CHECK (
    (promotion_type = 'PRODUCT'
       AND promotion_start_date IS NULL AND promotion_end_date IS NULL AND promotion_quantity IS NULL)
    OR
    (promotion_type IN ('ORDER', 'CODE')
       AND promotion_start_date IS NOT NULL AND promotion_end_date IS NOT NULL
       AND promotion_end_date > promotion_start_date
       AND promotion_quantity IS NOT NULL AND promotion_quantity > 0
       AND promotion_used_amount <= promotion_quantity)
  )
);
CREATE INDEX promotion_type_dates_idx ON promotion.promotion (promotion_type, promotion_start_date, promotion_end_date);

CREATE TABLE promotion.product_promotion (
  promotion_key                         uuid         PRIMARY KEY REFERENCES promotion.promotion (promotion_key) ON DELETE CASCADE,
  product_promotion_product_key         uuid         NOT NULL REFERENCES catalog.product (product_key) ON DELETE RESTRICT,
  product_promotion_discount_percentage numeric(5,2) NOT NULL
    CHECK (product_promotion_discount_percentage > 0 AND product_promotion_discount_percentage < 100)
);
CREATE INDEX product_promotion_product_idx ON promotion.product_promotion (product_promotion_product_key);

CREATE TABLE promotion.order_promotion (
  promotion_key                       uuid          PRIMARY KEY REFERENCES promotion.promotion (promotion_key) ON DELETE CASCADE,
  order_promotion_discount_percentage numeric(5,2)  NOT NULL
    CHECK (order_promotion_discount_percentage > 0 AND order_promotion_discount_percentage < 100),
  order_promotion_thresh_price        numeric(12,0) NOT NULL CHECK (order_promotion_thresh_price >= 0)
);

CREATE TABLE promotion.code_promotion (
  promotion_key                      uuid          PRIMARY KEY REFERENCES promotion.promotion (promotion_key) ON DELETE CASCADE,
  code_promotion_code                varchar(50)   NOT NULL UNIQUE,
  code_promotion_discount_percentage numeric(5,2)  NOT NULL
    CHECK (code_promotion_discount_percentage > 0 AND code_promotion_discount_percentage < 100),
  code_promotion_thresh_price        numeric(12,0) NOT NULL CHECK (code_promotion_thresh_price >= 0)
);
-- Mã voucher không phân biệt hoa thường [GD]
CREATE UNIQUE INDEX code_promotion_code_lower_uq ON promotion.code_promotion (lower(code_promotion_code));

-- ---------------------------------------------------------------------
-- ordering
-- ---------------------------------------------------------------------

CREATE TABLE ordering.payment (
  payment_key  uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_name varchar(100) NOT NULL UNIQUE CHECK (payment_name IN ('COD', 'QR'))
);

CREATE TABLE ordering."order" (
  order_key                   uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  order_code                  varchar(8)    NOT NULL UNIQUE CHECK (order_code ~ '^[0-9A-HJKMNP-TV-Z]{8}$'),
  order_account_key           uuid          NOT NULL REFERENCES identity.account (account_key) ON DELETE RESTRICT,
  order_payment_key           uuid          NOT NULL REFERENCES ordering.payment (payment_key) ON DELETE RESTRICT,
  order_order_promotion_key   uuid          REFERENCES promotion.order_promotion (promotion_key) ON DELETE RESTRICT,
  order_code_promotion_key    uuid          REFERENCES promotion.code_promotion (promotion_key) ON DELETE RESTRICT,
  order_customer_name         varchar(255)  NOT NULL,
  order_customer_phone_number varchar(20)   NOT NULL,
  order_customer_house_number varchar(255)  NOT NULL,
  order_customer_ward         varchar(100)  NOT NULL,
  order_customer_city         varchar(255)  NOT NULL,
  order_customer_country      varchar(100)  NOT NULL,
  order_discount_amount       numeric(12,0) NOT NULL DEFAULT 0 CHECK (order_discount_amount >= 0),
  order_shipping_fee          numeric(12,0) NOT NULL CHECK (order_shipping_fee >= 0),
  order_total_price           numeric(12,0) NOT NULL CHECK (order_total_price >= 0),
  order_payment_status        varchar(20)   NOT NULL DEFAULT 'UNPAID' CHECK (order_payment_status IN ('UNPAID', 'PAID')),
  order_status                varchar(20)   NOT NULL DEFAULT 'PENDING'
    CHECK (order_status IN ('PENDING', 'CONFIRMED', 'AWAITING_PICKUP', 'SHIPPING', 'DELIVERED', 'DELIVERY_FAILED', 'CANCELLED')),
  order_created_date          timestamptz   NOT NULL DEFAULT now(),
  order_updated_date          timestamptz   NOT NULL DEFAULT now(),
  -- Mỗi đơn tối đa 1 khuyến mãi theo hóa đơn HOẶC 1 voucher (BR-004)
  CONSTRAINT order_one_promotion_ck
    CHECK (order_order_promotion_key IS NULL OR order_code_promotion_key IS NULL)
);
CREATE INDEX order_account_created_idx ON ordering."order" (order_account_key, order_created_date);
CREATE INDEX order_status_created_idx ON ordering."order" (order_status, order_created_date);

CREATE TABLE ordering.order_detail (
  order_detail_key                   uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  order_detail_order_key             uuid          NOT NULL REFERENCES ordering."order" (order_key) ON DELETE CASCADE,
  order_detail_variant_key           uuid          NOT NULL REFERENCES catalog.variant (variant_key) ON DELETE RESTRICT,
  order_detail_quantity              int           NOT NULL CHECK (order_detail_quantity > 0),
  order_detail_unit_price            numeric(12,0) NOT NULL CHECK (order_detail_unit_price >= 0),
  order_detail_product_promotion_key uuid          REFERENCES promotion.product_promotion (promotion_key) ON DELETE RESTRICT,
  order_detail_cost_price            numeric(12,0) NOT NULL CHECK (order_detail_cost_price >= 0),
  CONSTRAINT order_detail_order_variant_uq UNIQUE (order_detail_order_key, order_detail_variant_key)
);

CREATE TABLE ordering.order_status_history (
  order_status_history_key            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  order_status_history_order_key      uuid        NOT NULL REFERENCES ordering."order" (order_key) ON DELETE CASCADE,
  order_status_history_from_value     varchar(20)
    CHECK (order_status_history_from_value IN ('PENDING', 'CONFIRMED', 'AWAITING_PICKUP', 'SHIPPING', 'DELIVERED', 'DELIVERY_FAILED', 'CANCELLED')),
  order_status_history_to_value       varchar(20) NOT NULL
    CHECK (order_status_history_to_value IN ('PENDING', 'CONFIRMED', 'AWAITING_PICKUP', 'SHIPPING', 'DELIVERED', 'DELIVERY_FAILED', 'CANCELLED')),
  order_status_history_source         varchar(20) NOT NULL
    CHECK (order_status_history_source IN ('CUSTOMER', 'EMPLOYEE', 'SYSTEM', 'SHIPPING_SIMULATOR')),
  order_status_history_note           text,       -- lý do hủy do Nhân viên nhập
  order_status_history_changed_by_key uuid        REFERENCES identity.account (account_key) ON DELETE RESTRICT,
  order_status_history_changed_time   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX order_status_history_order_time_idx
  ON ordering.order_status_history (order_status_history_order_key, order_status_history_changed_time);

CREATE TABLE ordering.invoice (
  invoice_key           uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id            varchar(11) NOT NULL UNIQUE CHECK (invoice_id ~ '^HD-[0-9A-HJKMNP-TV-Z]{8}$'),
  invoice_order_key     uuid        NOT NULL UNIQUE REFERENCES ordering."order" (order_key) ON DELETE RESTRICT,
  invoice_created_date  timestamptz NOT NULL DEFAULT now(),
  invoice_snapshot_json jsonb       NOT NULL
);

-- ---------------------------------------------------------------------
-- payment
-- ---------------------------------------------------------------------

CREATE TABLE payment.bank_transaction (
  bank_transaction_key            uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  bank_transaction_provider_id    varchar(100)  NOT NULL UNIQUE,  -- mã giao dịch SePay, chống xử lý trùng
  bank_transaction_gateway        varchar(100),
  bank_transaction_account_number varchar(50),
  bank_transaction_amount         numeric(12,0) NOT NULL CHECK (bank_transaction_amount >= 0),
  bank_transaction_content        text,
  bank_transaction_reference_code varchar(100),
  bank_transaction_time           timestamptz,
  bank_transaction_received_time  timestamptz   NOT NULL DEFAULT now(),
  bank_transaction_match_status   varchar(20)   NOT NULL CHECK (bank_transaction_match_status IN ('MATCHED', 'UNMATCHED')),
  bank_transaction_order_key      uuid          REFERENCES ordering."order" (order_key) ON DELETE RESTRICT,
  bank_transaction_raw_payload    jsonb,
  CONSTRAINT bank_transaction_matched_order_ck
    CHECK (bank_transaction_match_status = 'UNMATCHED' OR bank_transaction_order_key IS NOT NULL)
);

-- Catalog: tên duy nhất theo UC-14/17, không phân biệt hoa thường.
CREATE UNIQUE INDEX IF NOT EXISTS category_normalized_name_uq ON catalog.category (lower(regexp_replace(trim(category_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS collection_normalized_name_uq ON catalog.collection (lower(regexp_replace(trim(collection_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS gender_normalized_name_uq ON catalog.gender (lower(regexp_replace(trim(gender_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS color_normalized_name_uq ON catalog.color (lower(regexp_replace(trim(color_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS size_normalized_name_uq ON catalog.size (lower(regexp_replace(trim(size_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS product_normalized_name_uq ON catalog.product (lower(trim(product_name)));
