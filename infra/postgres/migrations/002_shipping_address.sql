-- Migration: sổ địa chỉ giao hàng (identity.shipping_address)
-- Spec: data model v2.17 / UC-41 — đã chốt 27/11/2026
-- Dùng cho DB đã init trước đó (volume Docker còn data). Máy mới: init.sql đã có bảng.
--
-- Chạy một lần:
--   Get-Content infra/postgres/migrations/002_shipping_address.sql -Raw |
--     docker exec -i postgres psql -U sobie -d sobieDB -v ON_ERROR_STOP=1

BEGIN;

CREATE TABLE IF NOT EXISTS identity.shipping_address (
  shipping_address_key          uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
  shipping_address_account_key  uuid         NOT NULL
    REFERENCES identity.account (account_key) ON DELETE CASCADE,
  shipping_address_name         varchar(255) NOT NULL,
  shipping_address_phone        varchar(20)  NOT NULL,
  shipping_address_house_number varchar(255) NOT NULL,
  shipping_address_ward         varchar(100) NOT NULL,
  shipping_address_city         varchar(255) NOT NULL,
  shipping_address_country      varchar(100) NOT NULL,
  shipping_address_is_default   boolean      NOT NULL DEFAULT false,
  shipping_address_created_at   timestamptz  NOT NULL DEFAULT now(),
  shipping_address_updated_at   timestamptz  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS shipping_address_account_key_idx
  ON identity.shipping_address (shipping_address_account_key);

CREATE UNIQUE INDEX IF NOT EXISTS shipping_address_one_default_per_account_uq
  ON identity.shipping_address (shipping_address_account_key)
  WHERE shipping_address_is_default;

-- Backfill: mỗi Khách hàng đã có địa chỉ trên account → 1 dòng sổ mặc định (nếu chưa có)
INSERT INTO identity.shipping_address
  (shipping_address_account_key, shipping_address_name, shipping_address_phone,
   shipping_address_house_number, shipping_address_ward, shipping_address_city,
   shipping_address_country, shipping_address_is_default)
SELECT
  a.account_key,
  a.account_name,
  a.account_phone_number,
  a.account_house_number,
  a.account_ward,
  a.account_city,
  COALESCE(a.account_country, 'Việt Nam'),
  true
FROM identity.account a
JOIN identity.role r ON r.role_key = a.account_role_key
WHERE r.role_code = 'customer'
  AND a.account_house_number IS NOT NULL
  AND btrim(a.account_house_number) <> ''
  AND a.account_ward IS NOT NULL
  AND btrim(a.account_ward) <> ''
  AND a.account_city IS NOT NULL
  AND btrim(a.account_city) <> ''
  AND NOT EXISTS (
    SELECT 1
    FROM identity.shipping_address s
    WHERE s.shipping_address_account_key = a.account_key
  );

COMMIT;
