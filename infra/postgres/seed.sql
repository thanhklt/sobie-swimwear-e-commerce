-- =====================================================================
-- Soobin Swimwear — dữ liệu mẫu cho môi trường dev / demo
-- Chạy sau init.sql, trên database trống. KHÔNG dùng cho production.
--
-- Tài khoản mẫu (mật khẩu chỉ dùng cho dev / demo, băm bcrypt bằng pgcrypto):
--   Admin      admin@example.com       / 0900000001 / mật khẩu: Admin@Sobie2026
--   Nhân viên  nhanvien@example.com    / 0900000002 / mật khẩu: Staff@Sobie2026
--   Khách hàng khachhang@example.com   / 0900000003 / mật khẩu: Customer@Sobie2026
-- Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026); seed dùng `crypt(..., gen_salt('bf', 10))`
-- của pgcrypto, ra dạng `$2a$` mà thư viện bcrypt của Python kiểm tra được.
--
-- Sản phẩm SP-0001 là sản phẩm demo thanh toán QR giá 2.000đ cho mọi size
-- (BR-006: đơn demo = 2.000đ + phí vận chuyển 12.000đ = 14.000đ).
-- Tồn kho đi qua phiếu nhập PN-0001 đã xác nhận để tồn kho và giá vốn khớp nhau.
-- Khách demo có sẵn giỏ hàng (2 dòng) và danh sách yêu thích (2 sản phẩm).
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- identity
-- ---------------------------------------------------------------------

INSERT INTO identity.role (role_code, role_name) VALUES
  ('customer', 'Khách hàng'),
  ('employee', 'Nhân viên'),
  ('admin',    'Admin');

INSERT INTO identity.account
  (account_id, account_role_key, account_email, account_phone_number, account_hash_password,
   account_name, account_date_of_birth, account_house_number, account_ward, account_city, account_country)
VALUES
  ('AD-QUANTRIVIEN-19950101-0001',
   (SELECT role_key FROM identity.role WHERE role_code = 'admin'),
   'admin@example.com', '0900000001', crypt('Admin@Sobie2026', gen_salt('bf', 10)),
   'Quản Trị Viên', DATE '1995-01-01', NULL, NULL, NULL, 'Việt Nam'),
  ('NV-NHANVIENDEMO-19990101-0001',
   (SELECT role_key FROM identity.role WHERE role_code = 'employee'),
   'nhanvien@example.com', '0900000002', crypt('Staff@Sobie2026', gen_salt('bf', 10)),
   'Nhân Viên Demo', DATE '1999-01-01', NULL, NULL, NULL, 'Việt Nam');

-- Mã KH- lấy ngày đăng ký theo giờ Việt Nam (Asia/Ho_Chi_Minh, đã chốt 21/11/2026)
INSERT INTO identity.account
  (account_id, account_role_key, account_email, account_phone_number, account_hash_password,
   account_name, account_date_of_birth, account_house_number, account_ward, account_city, account_country)
VALUES
  ('KH-' || to_char(now() AT TIME ZONE 'Asia/Ho_Chi_Minh', 'YYYYMMDD') || '-0001',
   (SELECT role_key FROM identity.role WHERE role_code = 'customer'),
   'khachhang@example.com', '0900000003', crypt('Customer@Sobie2026', gen_salt('bf', 10)),
   'Khách Hàng Demo', NULL, '273 An Dương Vương', 'Phường Chợ Quán', 'TP. Hồ Chí Minh', 'Việt Nam');

-- ---------------------------------------------------------------------
-- ordering: phương thức thanh toán
-- ---------------------------------------------------------------------

INSERT INTO ordering.payment (payment_name) VALUES ('COD'), ('QR');

-- ---------------------------------------------------------------------
-- catalog: thuộc tính phân loại [GD]
-- ---------------------------------------------------------------------

INSERT INTO catalog.gender (gender_name) VALUES ('Nữ'), ('Nam'), ('Trẻ em');
INSERT INTO catalog.size (size_name) VALUES ('S'), ('M'), ('L'), ('XL');
INSERT INTO catalog.color (color_name) VALUES ('Đen'), ('Trắng'), ('Đỏ'), ('Xanh dương');
INSERT INTO catalog.category (category_name) VALUES ('Bikini'), ('Đồ bơi một mảnh'), ('Quần bơi nam');
INSERT INTO catalog.collection (collection_name) VALUES ('Hè 2026'), ('Demo');

-- ---------------------------------------------------------------------
-- catalog: sản phẩm
-- ---------------------------------------------------------------------

INSERT INTO catalog.product
  (product_id, product_name, product_description, product_status, product_category_key, product_gender_key)
VALUES
  ('SP-0001', 'Sản phẩm demo thanh toán QR',
   'Sản phẩm dùng để demo luồng chuyển khoản QR với số tiền nhỏ (BR-006).', 'ACTIVE',
   (SELECT category_key FROM catalog.category WHERE category_name = 'Đồ bơi một mảnh'),
   (SELECT gender_key FROM catalog.gender WHERE gender_name = 'Nữ')),
  ('SP-0002', 'Bikini Hoa Nhí',
   'Bikini hai mảnh họa tiết hoa nhí.', 'ACTIVE',
   (SELECT category_key FROM catalog.category WHERE category_name = 'Bikini'),
   (SELECT gender_key FROM catalog.gender WHERE gender_name = 'Nữ'));

INSERT INTO catalog.product_collection (product_collection_product_key, product_collection_collection_key)
SELECT p.product_key, c.collection_key
FROM catalog.product p
JOIN catalog.collection c
  ON (p.product_id = 'SP-0001' AND c.collection_name = 'Demo')
  OR (p.product_id = 'SP-0002' AND c.collection_name = 'Hè 2026');

-- Ảnh nằm ở app/static/images/products/, do AI sinh, chỉ dùng cho dev / demo.
INSERT INTO catalog.gallery (gallery_product_key, gallery_order_no, gallery_url)
SELECT p.product_key, g.order_no, g.url
FROM (VALUES
  ('SP-0001', 1, '/static/images/products/sp-0001-1.jpg'),
  ('SP-0002', 1, '/static/images/products/sp-0002-1.jpg'),
  ('SP-0002', 2, '/static/images/products/sp-0002-2.jpg')
) AS g (product_id, order_no, url)
JOIN catalog.product p ON p.product_id = g.product_id;

-- Biến thể: SKU = <mã SP>-<MÀU>-<SIZE>; giá chỉ đổi theo size
INSERT INTO catalog.variant (variant_id, variant_product_key, variant_size_key, variant_color_key, variant_sell_price)
SELECT v.variant_id, p.product_key, s.size_key, c.color_key, v.price
FROM (VALUES
  ('SP-0001-DEN-S',        'SP-0001', 'S',  'Đen',        2000),
  ('SP-0001-DEN-M',        'SP-0001', 'M',  'Đen',        2000),
  ('SP-0001-DEN-L',        'SP-0001', 'L',  'Đen',        2000),
  ('SP-0001-DEN-XL',       'SP-0001', 'XL', 'Đen',        2000),
  ('SP-0002-DO-S',         'SP-0002', 'S',  'Đỏ',         290000),
  ('SP-0002-DO-M',         'SP-0002', 'M',  'Đỏ',         300000),
  ('SP-0002-DO-L',         'SP-0002', 'L',  'Đỏ',         310000),
  ('SP-0002-XANHDUONG-S',  'SP-0002', 'S',  'Xanh dương', 290000),
  ('SP-0002-XANHDUONG-M',  'SP-0002', 'M',  'Xanh dương', 300000),
  ('SP-0002-XANHDUONG-L',  'SP-0002', 'L',  'Xanh dương', 310000)
) AS v (variant_id, product_id, size_name, color_name, price)
JOIN catalog.product p ON p.product_id = v.product_id
JOIN catalog.size s    ON s.size_name = v.size_name
JOIN catalog.color c   ON c.color_name = v.color_name;

-- ---------------------------------------------------------------------
-- inventory: nhà cung cấp, phiếu nhập đã xác nhận, tồn kho
-- ---------------------------------------------------------------------

INSERT INTO inventory.supplier (supplier_id, supplier_name, supplier_phone_number, supplier_email, supplier_address)
VALUES ('NCC-0001', 'Xưởng may đồ bơi Demo', '0280000001', 'ncc@example.com', 'TP. Hồ Chí Minh');

INSERT INTO inventory.goods_receipt
  (goods_receipt_id, goods_receipt_status, goods_receipt_supplier_key, goods_receipt_account_key)
VALUES
  ('PN-0001', 'CONFIRMED',
   (SELECT supplier_key FROM inventory.supplier WHERE supplier_id = 'NCC-0001'),
   (SELECT account_key FROM identity.account WHERE account_email = 'nhanvien@example.com'));

-- Mỗi biến thể nhập 50 cái; giá nhập: SP-0001 1.000đ, SP-0002 150.000đ
INSERT INTO inventory.goods_receipt_detail
  (goods_receipt_detail_goods_receipt_key, goods_receipt_detail_variant_key,
   goods_receipt_detail_quantity, goods_receipt_detail_unit_price, goods_receipt_detail_total_price)
SELECT gr.goods_receipt_key, v.variant_key, 50, x.unit_price, 50 * x.unit_price
FROM catalog.variant v
JOIN (VALUES ('SP-0001-%', 1000), ('SP-0002-%', 150000)) AS x (pattern, unit_price)
  ON v.variant_id LIKE x.pattern
CROSS JOIN inventory.goods_receipt gr
WHERE gr.goods_receipt_id = 'PN-0001';

UPDATE inventory.goods_receipt gr
SET goods_receipt_final_price = (
  SELECT sum(d.goods_receipt_detail_total_price)
  FROM inventory.goods_receipt_detail d
  WHERE d.goods_receipt_detail_goods_receipt_key = gr.goods_receipt_key)
WHERE gr.goods_receipt_id = 'PN-0001';

-- Tồn kho = số lượng phiếu nhập; giá vốn = giá nhập (tồn trước đó = 0)
INSERT INTO inventory.stock (stock_variant_key, stock_quantity, stock_cost_price)
SELECT d.goods_receipt_detail_variant_key, d.goods_receipt_detail_quantity, d.goods_receipt_detail_unit_price
FROM inventory.goods_receipt_detail d;

-- ---------------------------------------------------------------------
-- shopping: giỏ hàng và danh sách yêu thích của khách demo
-- Mỗi tài khoản Khách hàng có đúng 1 giỏ và 1 danh sách yêu thích, tạo cùng
-- lúc tạo tài khoản (UC-01, UC-06) (đã chốt 21/11/2026, Q39). Số lượng trong giỏ không vượt tồn kho.
-- ---------------------------------------------------------------------

INSERT INTO shopping.cart (cart_account_key)
SELECT account_key FROM identity.account WHERE account_email = 'khachhang@example.com';

INSERT INTO shopping.wishlist (wishlist_account_key)
SELECT account_key FROM identity.account WHERE account_email = 'khachhang@example.com';

-- Giỏ: 1 cái SP-0001 đen size M (đơn demo QR), 2 cái SP-0002 đỏ size M
INSERT INTO shopping.cart_item (cart_item_cart_key, cart_item_variant_key, cart_item_quantity)
SELECT c.cart_key, v.variant_key, x.quantity
FROM (VALUES ('SP-0001-DEN-M', 1), ('SP-0002-DO-M', 2)) AS x (variant_id, quantity)
JOIN catalog.variant v ON v.variant_id = x.variant_id
CROSS JOIN shopping.cart c
JOIN identity.account a ON a.account_key = c.cart_account_key
WHERE a.account_email = 'khachhang@example.com';

-- Danh sách yêu thích: thả tim SP-0001 rồi SP-0002 (thứ tự thêm)
INSERT INTO shopping.wishlist_item (wishlist_item_wishlist_key, wishlist_item_product_key)
SELECT w.wishlist_key, p.product_key
FROM shopping.wishlist w
JOIN identity.account a ON a.account_key = w.wishlist_account_key
JOIN catalog.product p ON p.product_id IN ('SP-0001', 'SP-0002')
WHERE a.account_email = 'khachhang@example.com'
ORDER BY p.product_id;

COMMIT;
