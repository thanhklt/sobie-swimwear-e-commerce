# Plan: Giao diện trang chủ `/` theo mẫu thiết kế (UI + dữ liệu mẫu)

> Dev đã duyệt 28/11/2026 (chat): phạm vi "Giao diện + dữ liệu mẫu"; xử lý lệch spec "Theo mẫu + bù phần spec"; hotline/Zalo hard-code.

## Goal

Trang `GET /` (Accept: text/html) hiển thị giống mẫu `docs/design/home-mockup.webp`. Dữ liệu sản phẩm là dữ liệu mẫu tạm thời do service catalog trả về; UC-09 đầy đủ (25 AC, đọc DB, reporting/promotion/inventory, Redis) làm sau và chỉ thay nguồn dữ liệu, giữ template.

## Context đã đọc

- `specs/use-cases/catalog/UC-09-view-home-page.md` (Main Flow 2, 4, 5; Notes; Out of Scope).
- `specs/business-requirements/BR-GIAIDOAN1.md` dòng 35, 93: hotline, Zalo hard-code; phí vận chuyển mặc định 12.000đ.
- `app/main.py` (`root` đang gọi `storefront_identity_home` của identity), `app/shared/web/{rendering.py,templates/base.html}`, `app/modules/catalog/*` (gần như trống), `app/modules/identity/router/{_web.py,account.py}`, `docs/sequence/identity/get-home.md`.
- Mẫu: `docs/design/home-mockup.webp`.

## Mô tả mẫu (từ trên xuống)

1. **Header trắng**, cao ~54px: logo chữ "SOBIE" (đậm, condensed, đen) · menu `Trang chủ` (đang chọn, gạch chân lime) · `Sản phẩm` · `Bộ sưu tập` · `Bảng size` · `Giới thiệu` · ô tìm kiếm bo tròn viền xám "Tìm sản phẩm" có icon kính lúp · icon tim · icon user · icon túi.
2. **Hero** full-width, cao ~340px, ảnh nền hồ bơi xanh + người phụ nữ đội kính bơi bên phải; bên trái chữ trắng rất lớn, condensed, đậm, nghiêng: "Bơi theo / cách của bạn."; dòng phụ "Đồ bơi cho hiệu suất, phong cách / và sự tự tin trong mọi chuyển động."; nút lime chữ đen "Khám phá sản phẩm →".
3. **Dải lợi ích** nền lime, 3 cột ngăn bởi vạch dọc: icon xe tải "Giao hàng 12.000₫" · icon thẻ "Thanh toán COD / QR" · icon bong bóng chat "Tư vấn Zalo".
4. **4 ô danh mục** (ảnh dọc, tỉ lệ ~3:4, bo góc nhỏ) với nhãn trắng condensed góc dưới trái + mũi tên → góc dưới phải: Bikini · Đồ bơi một mảnh · Quần bơi nam · Đồ bơi trẻ em.
5. **"BÁN CHẠY TRONG TUẦN"** (tiêu đề condensed đậm, chữ hoa) + link phải "Xem tất cả sản phẩm →"; lưới 3 thẻ lớn. Thẻ: nền kem, ảnh flat-lay trên nền kem, icon tim góc phải trên, nhãn đỏ "-15%" góc trái trên khi có KM; tên đậm; "Từ **246.500₫**" (đỏ khi có KM) + giá gốc gạch ngang xám; hàng chấm màu tròn + link "Xem chi tiết →".
6. **"MỚI CẬP BẾN"** + "Xem tất cả sản phẩm →"; lưới 4 thẻ nhỏ cùng kiểu.
7. **Banner bộ sưu tập**: nửa trái ảnh người mẫu kính râm bên hồ bơi, nửa phải nền navy cắt chéo; eyebrow "BỘ SƯU TẬP" chữ trắng giãn chữ; tiêu đề lime nghiêng "RESORT / ESSENTIALS"; mô tả trắng; nút lime "Khám phá bộ sưu tập →".
8. **Dải mã giảm giá** nền kem bo góc: icon vé · vạch dọc · "**HE2026** · Giảm 15% cho đơn từ 300.000₫".
9. **Footer navy**: logo "SOBIE" + mô tả ngắn · cột Danh mục (Bikini, Đồ bơi một mảnh, Quần bơi nam, Đồ bơi trẻ em) · Chính sách (Thanh toán, Giao hàng, Đổi trả) · FAQ (Câu hỏi thường gặp) · Bảng size (Hướng dẫn chọn size) · 2 ô viền trắng bo góc: "COD – Thanh toán khi nhận hàng", "QR – Thanh toán qua mã QR".

Giá trị thiết kế đề xuất `[GD]`: navy `#0c1f2d`; lime `#d4ef3c`; kem `#f5f2ea`; đỏ KM `#c62828`; chữ `#111`; muted `#6b6b6b`. Font: tiêu đề "Barlow Condensed" 700/800 (italic cho hero và banner), nội dung "Be Vietnam Pro" 400/500/600 qua Google Fonts `[GD]`. Container tối đa ~1200px, gutter 20px.

## Quyết định đã chốt với dev

- D1. Phạm vi: chỉ UI + dữ liệu mẫu. Không đọc DB, không Redis, không gọi module khác. Không viết test AC của UC-09 (AC thuộc UC-09 đầy đủ). Test kiểm code (nếu cần) đặt ở `.artifact/`.
- D2. Lệch spec: giữ bố cục mẫu (hero, banner BST, dải HE2026, chấm màu), **bù phần spec bắt buộc**:
  - Header có hotline (link `tel:`) và link Zalo — đặt ở một thanh mảnh phía trên header hoặc gần icon, không phá bố cục `[GD]`.
  - Khu vực tài khoản: Khách vãng lai thấy "Đăng nhập", "Đăng ký" (dropdown/popover khi bấm icon user hoặc chữ nhỏ cạnh icon); Khách hàng đã đăng nhập thấy link "Tài khoản" tới hồ sơ. Phiên hiện không có tên tài khoản (`AuthenticatedSession` chỉ có key/role) nên **chưa hiện tên** `[GD]`.
  - Footer có hotline và link Zalo, liên kết Giới thiệu, Chính sách, FAQ.
  - Lưới Bán chạy chứa tối đa 5 thẻ, Hàng mới tối đa 8 thẻ (dữ liệu mẫu đúng 3 và 4 thẻ như hình).
- D3. Hotline/Zalo hard-code: `app/config/store.py` (`STORE_HOTLINE = "0901234567"`, `STORE_ZALO_URL = "https://zalo.me/0901234567"`) — giá trị là placeholder `[GD]`.

## Thiết kế kỹ thuật

| File | Thay đổi |
|---|---|
| `app/config/store.py` (mới) | Hằng hotline, Zalo, phí ship hiển thị `"12.000₫"` lấy từ `Config.SHIPPING_FEE` nếu có, mặc định 12000 `[GD]`. |
| `app/shared/web/rendering.py` | Thêm filter Jinja `vnd` (int → `"246.500₫"`, dấu chấm phân cách nghìn, không float) và global `store` (hotline, zalo). Giữ nguyên phần còn lại. |
| `app/shared/web/templates/storefront.html` (mới) | Layout storefront extends `base.html`: nạp font + `/static/css/storefront.css`, include header và footer. |
| `app/shared/web/templates/_storefront/header.html`, `footer.html`, `icons.html` (mới) | Header/footer theo mẫu; icon SVG inline (tim, user, túi, kính lúp, mũi tên, xe tải, thẻ, chat, vé, hộp, QR). Link chưa có trang thì dùng `#` hoặc đường dẫn dự kiến `[GD]`; link đăng nhập/đăng ký/hồ sơ dùng `request.url_for('storefront_login')`, `registration_form`, `customer_profile`. Search là `<form method="get" action="/search">` với `name="q"` `[GD]`. |
| `app/static/css/storefront.css` (mới) | Token màu trên `:root`, header, footer, nút, thẻ sản phẩm, toàn bộ khối trang chủ. Responsive: ≥1024px như mẫu; 640–1023px danh mục 2 cột, Bán chạy 2 cột, Hàng mới 2 cột, banner xếp dọc; <640px 1–2 cột, menu chính cuộn ngang hoặc ẩn sau nút menu, không tràn ngang. |
| `app/modules/catalog/schemas.py` | Dataclass `HomeProductCard` (product_id, name, image_url, price: int, sale_price: int \| None, discount_percent: int \| None, colors: tuple[str, ...] (mã hex), out_of_stock: bool, detail_url), `HomeCategoryTile`, `HomeCollectionBanner`, `HomePage` (best_sellers, new_arrivals, categories, collection, coupon). |
| `app/modules/catalog/home_sample.py` (mới) | Dữ liệu mẫu tạm thời `[GD]` (docstring ghi rõ: thay bằng truy vấn thật ở UC-09). 7 sản phẩm: Bikini Hoa Nhí 290.000 → 246.500 (-15%, màu đỏ/navy) · Olive Ribbed 520.000 (olive/đen) · Cát Vàng Bandeau 460.000 (be/trắng) · Terracotta 550.000 (terracotta/be) · Tailored Olive 395.000 (olive/navy) · Bikini Xanh Biển 440.000 (xanh dương/xanh nhạt) · Seafoam 340.000 (seafoam/trắng). Giá sau KM tính bằng `Decimal` + `ROUND_HALF_UP`. |
| `app/modules/catalog/service.py` | Thêm `get_home_page() -> HomePage` trả dữ liệu mẫu; giữ nguyên `get_cart_variants`. |
| `app/modules/catalog/router.py` | Thêm `storefront_home(request)` render `catalog/home.html` với `Cache-Control: private, no-cache`, `Vary: Accept` (UC-09 Notes). Router chỉ gọi service. |
| `app/modules/catalog/templates/home.html` (mới) | Extends `storefront.html`; các khối 2–8 của mẫu. Khối rỗng thì ẩn (`{% if %}`). Thẻ sản phẩm là partial `catalog/_partials/product_card.html` với biến thể kích thước lớn/nhỏ; nhãn "Hết hàng" khi `out_of_stock`. Ảnh có `alt`, `loading="lazy"` (trừ hero), `width/height` hoặc `aspect-ratio` để không nhảy layout. |
| `app/main.py` | `register_templates("catalog", ...)`; mount `/static/images` → `app/static/images`; `root` gọi `storefront_home` của catalog thay cho `storefront_identity_home` (giữ nhánh JSON cho Accept khác). Bỏ import identity home khỏi main. Không xóa code identity `[GD]`. |
| `app/static/images/home/*` (mới) | Ảnh do Codex **sinh bằng image generation**: `hero.jpg` (≥1920×800, người phụ nữ châu Á đội kính bơi, áo bơi đen, hồ bơi xanh, khoảng trống bên trái cho chữ), `cat-bikini.jpg`, `cat-one-piece.jpg`, `cat-men.jpg`, `cat-kids.jpg` (dọc 3:4, ≥720×960), `collection-resort.jpg` (người mẫu kính râm, đồ bơi một mảnh olive, bên hồ bơi, ≥1200×800). |
| `app/static/images/products/sample-*.jpg` (mới) | 7 ảnh flat-lay sản phẩm trên nền kem nhạt (vuông hoặc 4:5, ≥800px), đúng mô tả từng sản phẩm. Nén JPEG hợp lý (mỗi ảnh ≲ 400KB). |
| `docs/sequence/catalog/get-home.md` (mới) | Sơ đồ sequence `GET /`: Browser → main.root → catalog router → catalog service (dữ liệu mẫu) → render; ghi chú dữ liệu mẫu tạm thời. |
| `docs/sequence/identity/get-home.md` | Thêm 1 dòng: endpoint đã chuyển sang `docs/sequence/catalog/get-home.md` `[GD]`. |

Kiến trúc: Route → Service (→ dữ liệu mẫu thay cho Repository, tạm thời) — không gọi repository/DB từ router. Tiền là `int` VND; không `float`.

## Ràng buộc cho Codex

- Không dùng skill superpowers và gitnexus.
- Không commit/push; không động DB, Docker, `infra/`, seed; không đổi `pyproject.toml`/`poetry.lock`.
- Chỉ sửa/tạo file trong bảng trên; buộc phải sửa file khác thì báo lý do.
- Không sửa test identity; không đổi hành vi các trang identity.
- Không thêm JS framework; JS thuần tối thiểu chỉ khi cần (dropdown tài khoản, menu mobile).

## Kiểm chứng

1. `poetry run python -c "from app.main import app"` import được.
2. Chạy server `poetry run uvicorn app.main:app --port 8000`, `curl -H "Accept: text/html" localhost:8000/` → 200, có các khối; mọi ảnh `/static/images/...` trả 200.
3. Claude chụp màn hình 1440px và 375px, so từng khối với mẫu.
4. `poetry run python -m pytest -q -p no:cacheprovider tests`: không lỗi mới so với baseline.

Baseline 28/11/2026: `6 passed, 1 skipped, 102 errors` — 102 lỗi do thiếu biến môi trường `UC01_TEST_DATABASE_URL` (test identity cần PostgreSQL test), không liên quan.

## Ngoài phạm vi

UC-09 đầy đủ (đọc DB, bán chạy từ reporting, KM từ promotion, tồn kho từ inventory, Redis, test AC); trang danh mục/tìm kiếm/chi tiết/bảng size/giới thiệu; wishlist và giỏ hàng thật.

## Câu hỏi mở [GD]

1. Giá trị hotline/Zalo thật (đang placeholder `0901234567`).
2. Không hiện tên tài khoản ở header vì phiên chưa có tên; cần thêm hàm facade identity ở UC-09?
3. Hero, banner "Resort Essentials", dải mã HE2026 là nội dung tĩnh — spec UC-09 xếp "banner tùy chỉnh" vào Out of Scope; cần cập nhật spec cho khớp mẫu.
4. Chấm màu trên thẻ sản phẩm chưa có trong spec ("không tự thêm định dạng thẻ mới") — cần cập nhật spec.
5. Seed chỉ có 3 danh mục (thiếu "Đồ bơi trẻ em"); ô danh mục thứ 4 trong mẫu cần danh mục tương ứng khi làm UC-10.
6. Font qua Google Fonts (phụ thuộc mạng ngoài) hay tự host.
7. Đường dẫn các link chưa có trang (`/search`, danh mục, bảng size, giới thiệu, chính sách).
8. `storefront_identity_home` và `identity/account/home.html` còn giữ nhưng không dùng — xóa ở bước sau?

9. API contract trên Drive ghi `/api/v1/catalog/home` cho UC-09 đầy đủ; bản UI này đặt ở `GET /` (HTML). Hai địa chỉ có thể cùng tồn tại — cần dev xác nhận khi làm UC-09.

## Kết quả

Thực thi 28/11/2026 — Codex 1 lượt, Claude kiểm chứng, không cần vòng sửa.

- File: `app/config/store.py`, `app/main.py`, `app/shared/web/rendering.py`, `app/shared/web/templates/{storefront.html,_storefront/header.html,_storefront/footer.html,_storefront/icons.html}`, `app/static/css/storefront.css`, `app/modules/catalog/{schemas.py,home_sample.py,service.py,router.py,templates/home.html,templates/_partials/product_card.html}`, `docs/sequence/catalog/get-home.md`, `docs/sequence/identity/get-home.md`; 13 ảnh sinh bằng image generation (`app/static/images/home/*` 6 ảnh, `app/static/images/products/sample-*.jpg` 7 ảnh, mỗi ảnh < 400KB). Không đụng file ngoài plan.
- `from app.main import app`: OK. `GET /` (Accept: text/html) → 200, `Cache-Control: private, no-cache`, `Vary: Accept`; mọi ảnh và CSS → 200; nhánh JSON giữ nguyên.
- So với mẫu (Claude chụp ở 1200px và 375px, font Barlow Condensed/Be Vietnam Pro tải đúng): đủ 9 khối theo đúng thứ tự, bố cục, màu và kiểu thẻ khớp mẫu. Khác có chủ đích: thanh Hotline/Zalo trên header, footer có thêm Giới thiệu/Hotline/Zalo (bù spec, D2); ảnh sinh mới nên tư thế và góc chụp khác ảnh mẫu.
- 375px: không tràn ngang (scrollWidth = 375), menu cuộn ngang, danh mục 2 cột. Console không lỗi.
- pytest toàn bộ: `6 passed, 1 skipped, 102 errors` — khớp baseline (102 lỗi do thiếu `UC01_TEST_DATABASE_URL`).
- Codex không dùng skill superpowers/gitnexus (kiểm trong log).
