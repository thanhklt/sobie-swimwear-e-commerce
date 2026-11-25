-- Run after init.sql and seed.sql, or once against an existing deployment.
-- Sequence watermarks survive hard-deleted suppliers and transaction rollbacks.
BEGIN;
CREATE SEQUENCE IF NOT EXISTS inventory.supplier_number_seq MINVALUE 1 MAXVALUE 9999;
CREATE SEQUENCE IF NOT EXISTS inventory.goods_receipt_number_seq MINVALUE 1 MAXVALUE 9999;

SELECT setval('inventory.supplier_number_seq',
    GREATEST(COALESCE((SELECT MAX(substring(supplier_id FROM 5)::integer)
                      FROM inventory.supplier), 0), last_value),
    is_called OR EXISTS (SELECT 1 FROM inventory.supplier))
FROM inventory.supplier_number_seq;

SELECT setval('inventory.goods_receipt_number_seq',
    GREATEST(COALESCE((SELECT MAX(substring(goods_receipt_id FROM 4)::integer)
                      FROM inventory.goods_receipt), 0), last_value),
    is_called OR EXISTS (SELECT 1 FROM inventory.goods_receipt))
FROM inventory.goods_receipt_number_seq;

CREATE UNIQUE INDEX IF NOT EXISTS supplier_name_normalized_uq
    ON inventory.supplier (lower(btrim(supplier_name)));
COMMIT;
