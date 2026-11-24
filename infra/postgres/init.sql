-- =====================================================================
-- Soobin Swimwear — schema PostgreSQL (data model v2)
-- Nguồn: specs/business-requirements/BR-GIAIDOAN1.md và specs/use-cases/.
-- Yêu cầu: PostgreSQL 13+ và extension pgcrypto (bcrypt và mật khẩu ngẫu nhiên).
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

BEGIN;


CREATE EXTENSION IF NOT EXISTS pgcrypto;

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

INSERT INTO identity.role (role_code, role_name) VALUES
  ('customer', 'Khách hàng'),
  ('employee', 'Nhân viên'),
  ('admin', 'Admin');

CREATE TABLE identity.account_id_counter (
  account_prefix varchar(2) PRIMARY KEY CHECK (account_prefix IN ('KH', 'NV', 'AD')),
  last_number    integer    NOT NULL DEFAULT 0 CHECK (last_number BETWEEN 0 AND 9999)
);

INSERT INTO identity.account_id_counter (account_prefix) VALUES ('KH'), ('NV'), ('AD');

-- Gọi trong cùng transaction với thao tác tạo tài khoản hoặc đổi vai trò.
CREATE FUNCTION identity.next_account_suffix(p_prefix text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  next_number integer;
BEGIN
  UPDATE identity.account_id_counter
  SET last_number = last_number + 1
  WHERE account_prefix = p_prefix AND last_number < 9999
  RETURNING last_number INTO next_number;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Không thể cấp mã tài khoản cho tiền tố %', p_prefix;
  END IF;

  RETURN lpad(next_number::text, 4, '0');
END;
$$;

CREATE TABLE identity.account (
  account_key           uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id            varchar(100) NOT NULL UNIQUE
                        CHECK (account_id ~ '^(KH-[0-9]{8}|(NV|AD)-[A-Z0-9]+-[0-9]{8})-[0-9]{4}$'),
  account_role_key      uuid         NOT NULL REFERENCES identity.role (role_key) ON DELETE RESTRICT,
  account_email         varchar(255) NOT NULL UNIQUE,
  account_phone_number  varchar(20)  UNIQUE,
  account_hash_password varchar(255),
  account_google_sub    varchar(255) UNIQUE,
  account_status        varchar(20)  NOT NULL DEFAULT 'ACTIVE' CHECK (account_status IN ('ACTIVE', 'LOCKED')),
  account_name          varchar(255),
  account_date_of_birth date,
  account_house_number  varchar(255),
  account_ward          varchar(100),
  account_city          varchar(255),
  account_country       varchar(100),
  account_created_at    timestamptz  NOT NULL DEFAULT now(),
  CONSTRAINT account_password_hash_ck CHECK (
    account_hash_password IS NULL OR
    account_hash_password ~ '^[$]2[aby][$](0[4-9]|[12][0-9]|3[01])[$][./A-Za-z0-9]{53}$'
  ),
  CONSTRAINT account_login_method_ck CHECK (
    account_hash_password IS NOT NULL OR account_google_sub IS NOT NULL
  ),
  CONSTRAINT account_google_customer_ck CHECK (
    account_google_sub IS NULL OR (account_id LIKE 'KH-%' AND btrim(account_google_sub) <> '')
  ),
  -- Service kiểm tra vai trò khớp với tiền tố mã.
  CONSTRAINT account_staff_fields_required CHECK (
    account_id LIKE 'KH-%' OR
    (account_name IS NOT NULL AND account_phone_number IS NOT NULL
      AND account_date_of_birth IS NOT NULL AND account_hash_password IS NOT NULL)
  )
);
CREATE INDEX account_role_key_idx ON identity.account (account_role_key);

-- UC-06: Admin tồn tại khi khởi tạo sạch, kể cả khi không chạy seed demo.
-- Cấp bcrypt hash qua PGOPTIONS (-c sobie.bootstrap_admin_password_hash=...) cho phiên chạy init.
-- Nếu không cấu hình, mật khẩu tạo ngẫu nhiên và không xuất ra log. Cần cấp hash trước khi đăng nhập.
INSERT INTO identity.account (
  account_id, account_role_key, account_email, account_phone_number,
  account_hash_password, account_name, account_date_of_birth, account_country
)
SELECT
  'AD-QUANTRIVIEN-19950101-' || identity.next_account_suffix('AD'),
  role_key,
  COALESCE(NULLIF(current_setting('sobie.bootstrap_admin_email', true), ''), 'admin@example.com'),
  COALESCE(NULLIF(current_setting('sobie.bootstrap_admin_phone', true), ''), '0900000001'),
  COALESCE(
    NULLIF(current_setting('sobie.bootstrap_admin_password_hash', true), ''),
    crypt(encode(gen_random_bytes(32), 'hex'), gen_salt('bf', 10))
  ),
  'Quản Trị Viên', DATE '1995-01-01', 'Việt Nam'
FROM identity.role
WHERE role_code = 'admin';

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
  wishlist_item_added_order  bigint GENERATED ALWAYS AS IDENTITY,
  CONSTRAINT wishlist_item_wishlist_product_uq UNIQUE (wishlist_item_wishlist_key, wishlist_item_product_key)
);
CREATE INDEX wishlist_item_added_order_idx
  ON shopping.wishlist_item (wishlist_item_wishlist_key, wishlist_item_added_order DESC);

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
  supplier_name         varchar(255) NOT NULL UNIQUE,  -- Tên không trùng theo UC-32 [GD]
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
  CONSTRAINT promotion_key_status_uq UNIQUE (promotion_key, promotion_status),
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
  promotion_key                         uuid         PRIMARY KEY,
  product_promotion_product_key         uuid         NOT NULL REFERENCES catalog.product (product_key) ON DELETE RESTRICT,
  product_promotion_discount_percentage numeric(5,2) NOT NULL
    CHECK (product_promotion_discount_percentage > 0 AND product_promotion_discount_percentage < 100),
  -- Đồng bộ với bảng cha để ràng buộc tối đa một chương trình đang bật cho mỗi sản phẩm.
  product_promotion_status              varchar(20)  NOT NULL DEFAULT 'ENABLED',
  CONSTRAINT product_promotion_parent_status_fk
    FOREIGN KEY (promotion_key, product_promotion_status)
    REFERENCES promotion.promotion (promotion_key, promotion_status) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE INDEX product_promotion_product_idx ON promotion.product_promotion (product_promotion_product_key);
CREATE UNIQUE INDEX product_promotion_enabled_product_uq
  ON promotion.product_promotion (product_promotion_product_key)
  WHERE product_promotion_status = 'ENABLED';

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

INSERT INTO ordering.payment (payment_name) VALUES ('COD'), ('QR');

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

COMMIT;
