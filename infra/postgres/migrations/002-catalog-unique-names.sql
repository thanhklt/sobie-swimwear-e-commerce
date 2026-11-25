-- Từ chối nếu dữ liệu cũ trùng; không tự sửa dữ liệu.
BEGIN;
CREATE UNIQUE INDEX IF NOT EXISTS category_normalized_name_uq ON catalog.category (lower(regexp_replace(trim(category_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS collection_normalized_name_uq ON catalog.collection (lower(regexp_replace(trim(collection_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS gender_normalized_name_uq ON catalog.gender (lower(regexp_replace(trim(gender_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS color_normalized_name_uq ON catalog.color (lower(regexp_replace(trim(color_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS size_normalized_name_uq ON catalog.size (lower(regexp_replace(trim(size_name), '[[:space:]]+', ' ', 'g')));
CREATE UNIQUE INDEX IF NOT EXISTS product_normalized_name_uq ON catalog.product (lower(trim(product_name)));
COMMIT;
