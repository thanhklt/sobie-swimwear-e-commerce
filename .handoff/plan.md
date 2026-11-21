# Sửa docker-compose và chốt 6 câu hỏi mở của init.sql / seed.sql

> Created: 2026-11-21
> Author: plan skill
> Executor: Codex (`gpt-6.2-sol`, reasoning effort `high`)

## Background

Lượt rà soát `infra/postgres/init.sql` và `seed.sql` (21/11/2026) xác nhận hai file khớp DBML và đã chạy thử được trên PostgreSQL 16, nhưng còn lỗi cú pháp ở `infra/docker-compose.yml` (compose không khởi động được nên seed không được nạp) và 6 câu hỏi mở. Developer đã trả lời cả 6 (21/11/2026). Plan này áp dụng các câu trả lời đó vào compose, seed, UC và data model, và sinh ảnh sản phẩm mẫu cho seed.

Quyết định của developer (21/11/2026):

| # | Câu hỏi | Quyết định |
|---|---|---|
| Q1 | Giá nhập: UC-33 đòi "dương", DBML / init cho `>= 0` | Giữ CHECK `>= 0` (giá nhập bằng 0 hợp lệ). `init.sql` và DBML đã đúng; sửa UC-33 cho khớp. `[GD]` cách hiểu "thêm check >= 0" = giữ ràng buộc hiện có, chỉ sửa UC |
| Q2 | UC-34 còn ghi "ERD chưa có cột giá vốn ở biến thể" | Cập nhật UC-34: giá vốn nằm ở `inventory.stock` |
| Q3 | Seed chưa có giỏ hàng, wishlist | Seed phải có giỏ hàng + wishlist của khách demo; bổ sung vào UC thời điểm tạo giỏ / wishlist (nếu chưa có) |
| Q4 | Email seed đuôi `.test` | Đổi sang `@example.com` |
| Q5 | Ảnh gallery chưa tồn tại | Codex sinh ảnh sản phẩm mẫu |
| Q6 | bcrypt `$2a$`; ngày trong mã `KH-` theo giờ VN | Đồng ý cả hai — bỏ `[GD]`, ghi thành quyết định đã chốt |

## Quy tắc thực thi (bắt buộc)

- Tuân thủ [AGENTS.md](../AGENTS.md): **không `git commit` / `git push`**; chỉ sửa đúng phạm vi trong Change list; giữ nguyên comment, cấu trúc không liên quan; giả định mới phải gắn `[GD]` và liệt kê ở báo cáo cuối.
- Viết toàn bộ nội dung tài liệu bằng tiếng Việt có dấu, đúng giọng văn hiện có của file (câu ngắn, ghi ngày chốt dạng `(đã chốt 21/11/2026)`).
- Mỗi UC sửa nội dung thì thêm 1 dòng vào `## History` với version kế tiếp, ngày `2026-11-21`.
- Không đổi tên file, không xóa file. Working tree đang có nhiều thay đổi chưa commit của developer — không revert, không format lại file khác.
- Không cài thêm thư viện (không `pip install`, không `npm install`).

## Change list

### 1. `infra/docker-compose.yml` — Modify

`docker compose -f infra/docker-compose.yml config -q` đang báo: `services.postgres additional properties 'host_name', 'network' not allowed`. Sửa 3 khóa, giữ nguyên mọi thứ khác:

- `host_name: postgres` → `hostname: postgres`
- trong service: `network:` → `networks:` (giữ danh sách `- sobie_network`)
- cấp ngoài cùng: `network:` → `networks:` (giữ `sobie_network:`)

- **Risk**: medium — file `infra/`, quyết định cách nạp init/seed khi chạy lần đầu
- **Side effects**: none (chỉ cấu hình; không chạy `docker compose up`)
- **Rollback**: hoàn tác 3 dòng

### 2. `infra/postgres/seed.sql` — Modify (Q3, Q4, Q5, Q6)

a) **Email → `@example.com` (Q4).** Đổi mọi `@sobie.test`:
   - `admin@sobie.test` → `admin@example.com`
   - `nhanvien@sobie.test` → `nhanvien@example.com`
   - `khachhang@sobie.test` → `khachhang@example.com`
   - `ncc@sobie.test` → `ncc@example.com`
   Gồm cả khối comment đầu file và câu `SELECT account_key ... WHERE account_email = 'nhanvien@...'` ở phần phiếu nhập. Sau khi sửa, `grep -n "sobie.test" infra/postgres/seed.sql` phải không còn kết quả.

b) **Bỏ `[GD]` đã chốt (Q6).**
   - Comment đầu file: dòng "Tài khoản mẫu (mật khẩu chỉ dùng cho dev / demo, băm bcrypt bằng pgcrypto) [GD]:" → bỏ `[GD]`.
   - "Thuật toán băm mật khẩu của ứng dụng chưa chốt; seed dùng bcrypt ($2a$) để thư viện bcrypt của Python kiểm tra được [GD]." → viết lại: "Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026); seed dùng `crypt(..., gen_salt('bf', 10))` của pgcrypto, ra dạng `$2a$` mà thư viện bcrypt của Python kiểm tra được."
   - "-- Mã KH- lấy ngày đăng ký theo giờ Việt Nam [GD]" → "-- Mã KH- lấy ngày đăng ký theo giờ Việt Nam (Asia/Ho_Chi_Minh, đã chốt 21/11/2026)".
   - Giữ `[GD]` ở comment "catalog: thuộc tính phân loại [GD]" (giá trị phân loại mẫu vẫn là giả định).

c) **Gallery dùng ảnh thật (Q5).** Thay câu `INSERT INTO catalog.gallery ... SELECT ... FROM catalog.product;` bằng danh sách tường minh (đúng 3 ảnh sinh ở mục 10):

   ```sql
   INSERT INTO catalog.gallery (gallery_product_key, gallery_order_no, gallery_url)
   SELECT p.product_key, g.order_no, g.url
   FROM (VALUES
     ('SP-0001', 1, '/static/images/products/sp-0001-1.jpg'),
     ('SP-0002', 1, '/static/images/products/sp-0002-1.jpg'),
     ('SP-0002', 2, '/static/images/products/sp-0002-2.jpg')
   ) AS g (product_id, order_no, url)
   JOIN catalog.product p ON p.product_id = g.product_id;
   ```
   Thêm 1 dòng comment phía trên: ảnh nằm ở `app/static/images/products/`, ảnh do AI sinh, chỉ dùng cho dev / demo.

d) **Giỏ hàng + wishlist của khách demo (Q3).** Thêm section mới **sau** section `inventory` (cần biến thể đã có tồn kho), **trước** `COMMIT;`:

   ```sql
   -- ---------------------------------------------------------------------
   -- shopping: giỏ hàng và danh sách yêu thích của khách demo
   -- Mỗi tài khoản Khách hàng có đúng 1 giỏ và 1 danh sách yêu thích, tạo cùng
   -- lúc tạo tài khoản (UC-01, UC-06) [GD]. Số lượng trong giỏ không vượt tồn kho.
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
   ```
   Cập nhật khối comment đầu file thêm 1 dòng: khách demo có sẵn giỏ hàng (2 dòng) và danh sách yêu thích (2 sản phẩm).

### 3. `specs/use-cases/inventory/UC-33-create-goods-receipt.md` — Modify (Q1)

- E2 (dòng ~33): "giá nhập không phải số nguyên VND dương" → "giá nhập không phải số nguyên VND không âm (giá nhập bằng 0 hợp lệ)".
- AC-3 giữ nguyên ("số lượng 0 hoặc giá nhập âm" vẫn đúng).
- Notes → `## Quyết định đã chốt` (hoặc mục tương đương đang có): thêm "Giá nhập là số nguyên VND ≥ 0, khớp CHECK `goods_receipt_detail_unit_price >= 0` của data model (đã chốt 21/11/2026)."
- History: thêm `v4 (2026-11-21)`.

### 4. `specs/use-cases/inventory/UC-34-confirm-goods-receipt.md` — Modify (Q2)

- Notes dòng 87 "ERD hiện chưa có cột giá vốn ở biến thể; cần bổ sung..." → thay bằng: "Tồn kho và giá vốn bình quân gia quyền của biến thể lưu ở `inventory.stock` (`stock_quantity`, `stock_cost_price`), chỉ module inventory ghi (data model v2, đã chốt 20/11/2026)."
- Quyết định đã chốt dòng 90 "Bổ sung cột giá vốn ở biến thể trong ERD..." → "Giá vốn bình quân gia quyền lưu theo biến thể ở `inventory.stock.stock_cost_price` (đã chốt 15/11/2026; chuyển từ `catalog.variant` sang `inventory.stock` ngày 20/11/2026, data model v2)."
- Main Flow bước 3.1 / 3.4 nói "tồn hiện tại và giá vốn hiện tại của biến thể" — giữ nguyên ý, có thể thêm "(bảng `inventory.stock`)" ở bước 3.4.
- History: thêm `v4 (2026-11-21)`.

### 5. `specs/use-cases/identity/UC-01-register-account.md` — Modify (Q3, Q6)

- Main Flow bước 4: sau "tạo account gồm ...", thêm "đồng thời tạo giỏ hàng và danh sách yêu thích trống cho tài khoản `[GD]`".
- Postconditions: thêm "Tài khoản có 1 giỏ hàng trống và 1 danh sách yêu thích trống (UC-18, UC-38) `[GD]`."
- Notes / quyết định: "Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` của `account_created_at` (đã chốt 21/11/2026)." và "Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026)."
- Mục Giả định `[GD]` của UC: thêm "Giỏ hàng và danh sách yêu thích được tạo cùng transaction tạo account; identity gọi service công khai của shopping."
- History: thêm version mới.

### 6. `specs/use-cases/identity/UC-06-create-account.md` — Modify (Q3, Q6)

- Main Flow bước 4: thêm "nếu vai trò là Khách hàng, đồng thời tạo giỏ hàng và danh sách yêu thích trống `[GD]`".
- Postconditions: tương tự UC-01 (chỉ với vai trò Khách hàng).
- Notes: cùng 2 quyết định đã chốt như UC-01 (bcrypt; ngày `KH-` theo giờ VN); thêm giả định cùng nội dung UC-01.
- History: thêm `v6 (2026-11-21)`.

### 7. `specs/use-cases/shopping/UC-18-manage-cart.md` và `UC-38-manage-wishlist.md` — Modify (Q3)

- UC-18 Notes → Quyết định đã chốt: thêm "Mỗi Khách hàng có đúng 1 giỏ trong DB, tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06); trang giỏ luôn có giỏ để đọc / ghi, không tạo giỏ khi thêm sản phẩm lần đầu `[GD]`." (đặt ở mục Giả định `[GD]` nếu phù hợp hơn; nội dung giữ tag `[GD]`).
- UC-38 Notes: thêm câu tương đương cho danh sách yêu thích.
- Dependencies → Upstream UC của cả hai: thêm "UC-01 Đăng ký tài khoản, UC-06 Tạo tài khoản" nếu chưa có.
- History mỗi file: thêm version mới.

### 8. `specs/use-cases/README.md` — Modify

- Bảng "Tổng hợp giả định `[GD]`": thêm dòng cho UC-01, UC-06, UC-18, UC-38 về việc tạo giỏ / danh sách yêu thích cùng lúc tạo tài khoản Khách hàng.
- Bảng quyết định (phần "Quyết định đã chốt" có các dòng `| Chủ đề | Quyết định | UC |`): thêm dòng "Mật khẩu" — băm bcrypt (21/11/2026) — UC-01, UC-05, UC-06; dòng "Mã khách hàng" — ngày đăng ký theo giờ Asia/Ho_Chi_Minh (21/11/2026) — UC-01, UC-06; dòng "Giá nhập" — số nguyên VND ≥ 0 (21/11/2026) — UC-33. Không trùng dòng đã có; nếu đã có dòng cùng chủ đề thì bổ sung vào dòng đó.

### 9. Data model — `specs/entity-model/data_model_v2.dbml`, `data_model_v2.md`, `entity_diagram_v2.md` — Modify

Quy tắc của dự án: sửa DBML trước, rồi cập nhật `data_model_v2.md` cho khớp (cùng câu chữ trong note / bảng cột). Không đổi cột, kiểu, ràng buộc nào.

- `identity.account.account_id` note: thêm "Ngày đăng ký lấy theo giờ Asia/Ho_Chi_Minh (đã chốt 21/11/2026)."
- `identity.account.account_hash_password`: thêm note "Băm bcrypt (đã chốt 21/11/2026)".
- `shopping.cart` Note và `shopping.wishlist` Note: thêm "Tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06), identity gọi service của shopping `[GD]`."
- `inventory.goods_receipt_detail.goods_receipt_detail_unit_price` note: "Giá nhập thực tế. CHECK >= 0 (giá nhập bằng 0 hợp lệ, đã chốt 21/11/2026)".
- CHANGELOG: thêm khối `// v2.16 — Chốt câu hỏi mở của init.sql / seed.sql (21/11/2026)` với các mục đánh số tiếp từ 96 (account_id note, hash_password note, cart/wishlist note, goods_receipt_detail_unit_price note).
- OPEN QUESTIONS: thêm `Q36. [ĐÃ CHỐT 21/11/2026] Băm mật khẩu bằng bcrypt.`, `Q37. [ĐÃ CHỐT 21/11/2026] Ngày trong mã KH- theo giờ Asia/Ho_Chi_Minh.`, `Q38. [ĐÃ CHỐT 21/11/2026] Giá nhập >= 0.`, `Q39. [GD] Giỏ hàng và danh sách yêu thích tạo cùng lúc tạo tài khoản Khách hàng.`
- `data_model_v2.md`: phản ánh đúng các note trên trong bảng cột / ghi chú bảng tương ứng; cập nhật ngày ở dòng đầu nếu cần.
- `entity_diagram_v2.md`: mục Account → Quy tắc thêm bcrypt và ngày `KH-` theo giờ VN; mục Cart / CartItem và Wishlist / WishlistItem → Quy tắc thêm "tạo cùng lúc tạo tài khoản Khách hàng `[GD]`"; mục GoodsReceipt → giá nhập ≥ 0; History thêm dòng `v2.1 (2026-11-21)`.

### 10. Ảnh sản phẩm mẫu — Create `app/static/images/products/sp-0001-1.jpg`, `sp-0002-1.jpg`, `sp-0002-2.jpg` (Q5)

Dùng công cụ sinh ảnh có sẵn của Codex (image generation). Yêu cầu chung cho cả 3 ảnh:

- Ảnh chụp sản phẩm kiểu e-commerce, khung dọc 3:4, nền trơn sáng (trắng ngà / xám rất nhạt), ánh sáng studio mềm.
- Sản phẩm đặt dạng flat-lay hoặc trên ma-nơ-canh vô hình (ghost mannequin). **Không có người, không có khuôn mặt, không chữ, không logo, không watermark.**
- Nhất quán phong cách giữa 3 ảnh.

Nội dung từng ảnh:

| File | Sản phẩm (khớp seed) | Mô tả |
|---|---|---|
| `sp-0001-1.jpg` | SP-0001 "Sản phẩm demo thanh toán QR", danh mục Đồ bơi một mảnh, màu Đen | Đồ bơi nữ một mảnh màu đen trơn, kiểu cơ bản |
| `sp-0002-1.jpg` | SP-0002 "Bikini Hoa Nhí", màu Đỏ | Bikini nữ hai mảnh nền đỏ, họa tiết hoa nhí nhỏ màu trắng |
| `sp-0002-2.jpg` | SP-0002 "Bikini Hoa Nhí", màu Xanh dương | Cùng mẫu bikini, nền xanh dương, họa tiết hoa nhí trắng |

Hậu xử lý (công cụ sinh ảnh ra PNG ~2 MB; máy không có Pillow và **không được cài**): dùng Windows PowerShell + `System.Drawing` để resize về **900 × 1200 px** (cắt giữa nếu tỉ lệ khác 3:4) và lưu **JPEG chất lượng 85**, mục tiêu ≤ 400 KB mỗi ảnh. Tạo thư mục `app/static/images/products/` nếu chưa có. Không để lại file PNG trong repo.

Nếu công cụ sinh ảnh không dùng được: **dừng mục này, không tạo ảnh giả / placeholder**, ghi rõ lý do trong báo cáo cuối (các mục khác vẫn làm).

### 11. `README.md` — Modify

Mục "Trạng thái và phần còn chờ":
- Dòng "`infra/postgres/init.sql` (schema theo data model v2) và `seed.sql` (dữ liệu dev / demo) chưa được chạy thử trên PostgreSQL." → "`init.sql` và `seed.sql` đã chạy thử trên PostgreSQL 16 (21/11/2026)."
- Dòng "`docker-compose.yml` trong `infra/` còn rỗng." → mô tả đúng: compose chạy PostgreSQL 16, tự nạp `init.sql` rồi `seed.sql` khi volume còn trống (`docker compose -f infra/docker-compose.yml up -d`).
- Nếu README có liệt kê tài khoản mẫu / email thì đổi sang `@example.com` (hiện tại không có — chỉ kiểm tra).

## Parallelization

- **Group A (independent):** mục 10 (sinh ảnh) — chỉ tạo file trong `app/static/images/products/`.
- **Group B (independent):** mục 3, 4 (UC inventory).
- **Group C (independent):** mục 5, 6, 7, 8, 9 (UC identity / shopping, README UC, data model) — làm tuần tự trong nhóm vì cùng nội dung quyết định.
- Mục 1 (risk medium) và mục 2, 11 làm tuần tự, không song song.

## Test strategy

Chưa có pytest trong dự án (chưa khai báo dependency) và plan không đổi logic Python, nên không thêm test Python. Kiểm bằng chạy SQL thật:

- Chạy `init.sql` + `seed.sql` trên container `postgres:16-alpine` tạm → không lỗi.
- Truy vấn kiểm: 4 email đều `@example.com`; khách demo có 1 cart (2 cart_item, số lượng ≤ tồn kho) và 1 wishlist (2 wishlist_item); gallery có 3 dòng và mỗi `gallery_url` trỏ tới file có thật trong `app/static/`.
- `docker compose -f infra/docker-compose.yml config -q` → không lỗi.

## Compile check

(none — không đổi mã Python; thay đổi gồm SQL seed, YAML, tài liệu Markdown / DBML và file ảnh)

## Verification plan

Chạy từ thư mục gốc repo (Git Bash), cần Docker Desktop đang chạy:

- `docker compose -f infra/docker-compose.yml config -q` — không in lỗi.
- `grep -rn "sobie.test" infra README.md specs` — không còn kết quả.
- `ls -l app/static/images/products/` — có đúng `sp-0001-1.jpg`, `sp-0002-1.jpg`, `sp-0002-2.jpg`, mỗi file ≤ 400 KB, mở được là JPEG 900×1200.
- `docker run -d --rm --name sobie-sqlcheck -e POSTGRES_PASSWORD=check -e POSTGRES_DB=sobiecheck postgres:16-alpine`, chờ `pg_isready`, rồi `docker exec -i sobie-sqlcheck psql -v ON_ERROR_STOP=1 -U postgres -d sobiecheck < infra/postgres/init.sql` và tương tự với `seed.sql` — cả hai exit 0.
- Truy vấn kiểm dữ liệu (cùng container):
  - `SELECT account_email FROM identity.account ORDER BY 1;` → 3 email `@example.com`; `SELECT supplier_email FROM inventory.supplier;` → `ncc@example.com`.
  - `SELECT v.variant_id, ci.cart_item_quantity, st.stock_quantity FROM shopping.cart_item ci JOIN catalog.variant v ON v.variant_key = ci.cart_item_variant_key JOIN inventory.stock st ON st.stock_variant_key = v.variant_key;` → `SP-0001-DEN-M` 1, `SP-0002-DO-M` 2, đều ≤ tồn.
  - `SELECT count(*) FROM shopping.cart; SELECT count(*) FROM shopping.wishlist; SELECT count(*) FROM shopping.wishlist_item;` → 1, 1, 2.
  - `SELECT gallery_url FROM catalog.gallery ORDER BY 1;` → 3 URL khớp 3 file ảnh.
- `docker rm -f sobie-sqlcheck` — dọn container.

## Báo cáo cuối của executor

Kết thúc bằng: danh sách file đã sửa / tạo; mục nào bỏ qua và lý do; mọi giả định mới gắn `[GD]`; nhắc lại rằng chưa commit.
