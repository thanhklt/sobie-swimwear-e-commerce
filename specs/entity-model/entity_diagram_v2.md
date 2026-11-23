# Entity Diagram v2 — Soobin Swimwear

## Metadata
- **Phiên bản:** v2.1 (21/11/2026)
- **Nguồn:** [data_model_v2.dbml](data_model_v2.dbml) (bản vẽ: [data_model_v2.md](data_model_v2.md)), [BR-GIAIDOAN1.md](../business-requirements/BR-GIAIDOAN1.md), [use case](../use-cases/README.md)

## Quy ước

Theo SDD Ebook — Tầng 3: Entity Model trả lời câu hỏi *hệ thống đang nói về những "danh từ" nào*. Tài liệu này tập trung vào **tên gọi, ý nghĩa, trạng thái, quan hệ và quy tắc nghiệp vụ**; không nói về datatype, index, khóa ngoại — phần đó nằm ở data model.

- Mỗi module là một bounded context: trong module đó một từ có đúng một nghĩa. Entity của module khác chỉ được tham chiếu bằng khóa và truy cập qua service công khai (AGENTS.md).
- Mỗi entity ghi: **Đại diện**, **Bảng**, **Mã** (mã tự nhiên người dùng thấy), **Trường**, **Trạng thái**, quan hệ (**Có nhiều / Có một / Thuộc / Tham chiếu**) và **Quy tắc**.
- Mọi entity có khóa kỹ thuật `<x>_key` (uuid), không ghi lại ở từng entity.
- Tiền: số nguyên VND, làm tròn `ROUND_HALF_UP`. Thời gian: lưu UTC, hiển thị `Asia/Ho_Chi_Minh`.
- `[GD]`: giả định chưa được developer chốt.

## Tổng quan

| Module | Entity | Không phải entity |
|---|---|---|
| identity | Role, Account, Session | — |
| catalog | Category, Collection, Gender, Size, Color, Product, Variant, Gallery | — |
| shopping | Cart, CartItem, Wishlist, WishlistItem | Giỏ khách vãng lai (localStorage) |
| ordering | PaymentMethod, Order, OrderDetail, OrderStatusHistory, Invoice | Tạm tính, hạn thanh toán QR (tính ra), mã VietQR (sinh khi hiển thị) |
| payment | BankTransaction | — |
| promotion | Promotion, ProductPromotion, OrderPromotion, Voucher | Trạng thái hiển thị (tính ra) |
| inventory | Supplier, GoodsReceipt, GoodsReceiptDetail, Stock | — |
| shipping | (không có) | Trang giả lập vận chuyển |
| reporting | (không có) | Dashboard (view tổng hợp) |

---

# Entity Model — identity (BR-001)

## Role
- **Đại diện:** một vai trò cố định của tài khoản.
- **Bảng:** `identity.role`
- **Trường:** role_code (`customer` | `employee` | `admin`), role_name (Khách hàng | Nhân viên | Admin)
- **Có nhiều:** Account
- **Quy tắc:**
  - Đúng 3 vai trò, tạo sẵn khi khởi tạo hệ thống; không tạo, sửa, xóa vai trò (Out of Scope).
  - Chưa có Permission: quyền kiểm tra theo role_code. Admin chỉ quản lý tài khoản; Nhân viên vận hành cửa hàng; Khách hàng mua hàng.

## Account
- **Đại diện:** một người dùng của hệ thống — Khách hàng, Nhân viên hoặc Admin — gồm thông tin đăng nhập và thông tin cá nhân.
- **Bảng:** `identity.account`
- **Mã:** `KH-<YYYYMMDD ngày đăng ký>-<4 số>` | `NV-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>` | `AD-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>`
- **Trường:** email, phone_number, hash_password, status, name, date_of_birth, house_number, ward, city, country, created_at (ngày đăng ký)
- **Trạng thái:** Hoạt động (`ACTIVE`) | Bị khóa (`LOCKED`)
- **Thuộc:** Role (đúng 1)
- **Có một:** Cart, Wishlist (chỉ Khách hàng)
- **Có nhiều:** Session, Order (Khách hàng đặt), GoodsReceipt (Nhân viên lập), OrderStatusHistory (người đổi trạng thái)
- **Quy tắc:**
  - Đăng ký bắt buộc đủ email và số điện thoại, cả hai duy nhất; đăng nhập bằng một trong hai; không có username.
  - Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026).
  - Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` (đã chốt 21/11/2026).
  - Ngày sinh bắt buộc với Nhân viên, Admin (mã dùng ngày sinh); không bắt buộc với Khách hàng.
  - Địa chỉ của Khách hàng là địa chỉ nhận hàng mặc định; mỗi khách 1 địa chỉ.
  - Mã do hệ thống cấp, không sửa. Bộ đếm 4 số riêng cho từng tiền tố KH, NV, AD; `<HỌ TÊN>` bỏ dấu, viết hoa, bỏ khoảng trắng. Cách cấp số không trùng khi nhiều tài khoản tạo cùng lúc: khóa theo tiền tố trong transaction rồi lấy số lớn nhất + 1 `[GD]`.
  - Đổi vai trò chỉ giữa Nhân viên ↔ Admin; đổi thì cấp mã mới (mã cũ không dùng lại), đăng xuất phiên đang mở. Khách hàng không đổi sang vai trò nội bộ và ngược lại.
  - Hệ thống luôn có ít nhất 1 Admin đang hoạt động: chặn đổi vai trò hoặc khóa Admin hoạt động cuối cùng. Admin được tự đổi vai trò, tự khóa mình khi còn Admin khác.
  - Khóa tài khoản kết thúc mọi phiên đăng nhập; dữ liệu giữ nguyên.
  - Phiên đăng nhập lưu ở Session (đã chốt 21/11/2026). Đổi vai trò, khóa tài khoản, đổi mật khẩu xóa mọi Session của tài khoản để mọi phiên kết thúc ngay (đổi mật khẩu kết thúc cả phiên hiện tại).

## Session
- **Đại diện:** một lần đăng nhập đang còn hiệu lực của một tài khoản trên một trình duyệt.
- **Bảng:** `identity.session`
- **Trường:** token_hash (băm của mã phiên trong cookie), created_at (lúc đăng nhập), last_seen_at (lần thao tác cuối), expires_at (hết hạn)
- **Thuộc:** Account (đúng 1)
- **Quy tắc:**
  - Đăng nhập tạo 1 Session; một tài khoản có thể có nhiều Session (nhiều thiết bị). Mã phiên gốc chỉ nằm trong cookie `HttpOnly`, `Secure`, `SameSite=Lax`; hệ thống chỉ lưu bản băm.
  - Hạn: Khách hàng 30 phút, Nhân viên / Admin 1 giờ, tính từ lần thao tác cuối (đã chốt 21/11/2026). Hết hạn thì coi như chưa đăng nhập.
  - Đăng xuất xóa Session hiện tại, có hiệu lực ngay. Đổi mật khẩu, đổi vai trò, khóa tài khoản xóa mọi Session của tài khoản.
  - Session không lưu vai trò: mỗi request đọc vai trò và trạng thái từ Account.

---

# Entity Model — catalog (BR-002)

## Category / Collection / Gender / Size / Color
- **Đại diện:** danh mục, bộ sưu tập, giới tính, size, màu — thuộc tính phân loại sản phẩm.
- **Bảng:** `catalog.category`, `catalog.collection`, `catalog.gender`, `catalog.size`, `catalog.color`
- **Trường:** name (duy nhất trong từng loại)
- **Quy tắc:**
  - Danh mục một cấp `[GD]`. Không xóa giá trị đang được dùng `[GD]`.
  - Trang danh mục lọc theo giới tính, size, danh mục, bộ sưu tập.
  - Bảng size dùng chung cả cửa hàng, nội dung cố định (không phải entity).

## Product
- **Đại diện:** một mẫu đồ bơi.
- **Bảng:** `catalog.product`
- **Mã:** `SP-<4 số>`
- **Trường:** name, description, total_score_review (giai đoạn 2, chưa dùng), status, created_at, updated_at
- **Trạng thái:** Đang bán (`ACTIVE`) | Ngừng bán (`INACTIVE`, mặc định khi tạo)
- **Thuộc:** Category (đúng 1), Gender (đúng 1)
- **Có nhiều:** Variant, Gallery, Collection (nhiều – nhiều), ProductPromotion (theo thời gian)
- **Quy tắc:**
  - Chỉ chuyển Đang bán khi đã có biến thể và mọi size đã có giá.
  - Sắp xếp mặc định "mới nhất" theo created_at.
  - Không gắn với nhà cung cấp; một sản phẩm nhập được từ nhiều nhà cung cấp.

## Variant
- **Đại diện:** một tổ hợp màu × size của sản phẩm — đơn vị được bán, nhập kho và tính tồn.
- **Bảng:** `catalog.variant`
- **Mã (SKU):** `<mã SP>-<MÀU>-<SIZE>`, ví dụ `SP-0001-XANHDUONG-M`
- **Trường:** sell_price, status
- **Trạng thái:** Đang bán (`ACTIVE`) | Ngừng bán riêng biến thể (`INACTIVE`)
- **Thuộc:** Product, Size, Color
- **Có một:** Stock (module inventory)
- **Quy tắc:**
  - Mỗi tổ hợp màu × size chỉ 1 biến thể trong một sản phẩm.
  - Giá bán chỉ đổi theo size: đặt giá cho 1 size thì ghi cùng giá cho mọi màu của size đó. Giá trống = size chưa có giá.
  - Tồn kho và giá vốn không nằm ở đây mà ở Stock.

## Gallery
- **Đại diện:** một ảnh của sản phẩm.
- **Bảng:** `catalog.gallery`
- **Trường:** order_no (thứ tự hiển thị), url
- **Thuộc:** Product
- **Quy tắc:** ảnh gắn theo sản phẩm, không theo màu.

---

# Entity Model — shopping (BR-002, BR-003)

## Cart / CartItem
- **Đại diện:** giỏ hàng của Khách hàng đã đăng nhập / một dòng trong giỏ.
- **Bảng:** `shopping.cart`, `shopping.cart_item`
- **Trường (CartItem):** quantity
- **Thuộc:** Cart thuộc Account (vai trò Khách hàng, mỗi khách 1 giỏ); CartItem thuộc Cart
- **Tham chiếu:** Variant
- **Quy tắc:**
  - Giỏ được tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06) (đã chốt 21/11/2026).
  - Mỗi biến thể 1 dòng trong giỏ; số lượng > 0, không vượt tồn kho.
  - Giỏ không lưu giá, luôn hiển thị giá hiện tại.
  - Giỏ khách vãng lai lưu ở localStorage, gộp vào giỏ tài khoản khi đăng nhập (cộng dồn, không vượt tồn) `[GD]`.
  - Thêm vào giỏ không giữ chỗ tồn kho.

## Wishlist / WishlistItem
- **Đại diện:** danh sách yêu thích của Khách hàng / một sản phẩm được thả tim.
- **Bảng:** `shopping.wishlist`, `shopping.wishlist_item`
- **Thuộc:** Wishlist thuộc Account (mỗi khách 1 danh sách); WishlistItem thuộc Wishlist
- **Tham chiếu:** Product
- **Quy tắc:**
  - Mỗi sản phẩm chỉ 1 lần trong danh sách.
  - Danh sách yêu thích được tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06) (đã chốt 21/11/2026).

---

# Entity Model — ordering (BR-003)

## PaymentMethod
- **Đại diện:** phương thức thanh toán của đơn.
- **Bảng:** `ordering.payment`
- **Trường:** name — `COD` | `QR`
- **Có nhiều:** Order

## Order
- **Đại diện:** một lần Khách hàng đặt hàng.
- **Bảng:** `ordering.order`
- **Mã:** `order_code` — 8 ký tự ngẫu nhiên Crockford Base32 (`0-9`, `A-Z` bỏ I, L, O, U), sinh bằng `secrets`, trùng thì sinh lại; tách khỏi khóa
- **Trường:** thông tin nhận hàng chụp lúc đặt (customer_name, phone_number, house_number, ward, city, country), discount_amount, shipping_fee, total_price, payment_status, status, created_date, updated_date
- **Trạng thái đơn:**
  ```
  Chưa xử lý ──► Đã xác nhận ──► Chờ lấy hàng ──► Đang giao ──► Giao thành công
     │               │               │                  └──────► Giao không thành công
     └───────────────┴───────────────┴──► Đã hủy
  ```
  `PENDING` → `CONFIRMED` → `AWAITING_PICKUP` → `SHIPPING` → `DELIVERED` | `DELIVERY_FAILED`; nhánh kết thúc `CANCELLED`
- **Trạng thái thanh toán:** Chưa thanh toán (`UNPAID`) | Đã thanh toán (`PAID`)
- **Thuộc:** Account (Khách hàng đặt), PaymentMethod
- **Có nhiều:** OrderDetail, OrderStatusHistory, BankTransaction (module payment)
- **Có một:** Invoice (khi giao thành công)
- **Tham chiếu:** OrderPromotion **hoặc** Voucher (tối đa 1)
- **Giá trị tính ra (không lưu):** tạm tính = tổng (giá sau khuyến mãi sản phẩm × số lượng); hạn thanh toán QR = created_date + 24 giờ
- **Quy tắc:**
  - Phải đăng nhập mới đặt hàng. total_price = tạm tính − discount_amount + shipping_fee; phí vận chuyển lấy từ biến môi trường (mặc định 12.000đ) lúc đặt.
  - Trừ tồn, kiểm tra / tăng lượt khuyến mãi và tạo đơn trong cùng 1 transaction.
  - Khách hủy được khi `PENDING`; Nhân viên hủy được khi `PENDING`, `CONFIRMED`, `AWAITING_PICKUP`, bắt buộc nhập lý do; hệ thống tự hủy đơn QR `PENDING` + `UNPAID` quá 24 giờ.
  - Hủy: cộng lại tồn, hoàn lượt khuyến mãi theo hóa đơn / voucher. Giao không thành công: cộng lại tồn.
  - Đơn QR chuyển `PAID` khi nhận giao dịch khớp qua webhook SePay. Đơn COD ghi nhận đã thanh toán khi giao thành công `[GD]`.

## OrderDetail
- **Đại diện:** một dòng hàng trong đơn.
- **Bảng:** `ordering.order_detail`
- **Trường:** quantity, unit_price (giá gốc theo size lúc đặt), cost_price (giá vốn lúc bán)
- **Thuộc:** Order
- **Tham chiếu:** Variant, ProductPromotion (nếu sản phẩm đang có khuyến mãi)
- **Quy tắc:**
  - Mỗi biến thể 1 dòng trong đơn.
  - Giá sau giảm = unit_price × (1 − % khuyến mãi sản phẩm), làm tròn `ROUND_HALF_UP`; ổn định vì khuyến mãi không được sửa.
  - cost_price chụp từ Stock lúc đặt, để lợi nhuận gộp quá khứ không đổi khi nhập lô mới.

## OrderStatusHistory
- **Đại diện:** một lần đơn đổi trạng thái.
- **Bảng:** `ordering.order_status_history`
- **Trường:** from_value, to_value, source, note (lý do hủy), changed_time
- **Nguồn:** `CUSTOMER` | `EMPLOYEE` | `SYSTEM` | `SHIPPING_SIMULATOR`
- **Thuộc:** Order
- **Tham chiếu:** Account (người đổi; trống khi nguồn là hệ thống hoặc trang giả lập)
- **Quy tắc:** ghi mọi lần đổi trạng thái đơn; đổi trạng thái thanh toán không ghi ở đây. Lý do hủy chỉ Nhân viên xem.

## Invoice
- **Đại diện:** hóa đơn của một đơn đã giao thành công.
- **Bảng:** `ordering.invoice`
- **Mã:** `HD-<order_code>`
- **Trường:** created_date (thời điểm xuất), snapshot (tên sản phẩm, màu, size, đơn giá gốc / sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng, người nhận, email, phương thức thanh toán)
- **Thuộc:** Order (mỗi đơn tối đa 1 hóa đơn)
- **Quy tắc:** tự xuất khi đơn sang Giao thành công, trong cùng transaction đổi trạng thái; chỉ xem, không sửa, không xuất lại. Admin không xem hóa đơn.

---

# Entity Model — payment (BR-006)

## BankTransaction
- **Đại diện:** một giao dịch tiền vào tài khoản cửa hàng, do SePay báo qua webhook.
- **Bảng:** `payment.bank_transaction`
- **Trường:** provider_id (mã giao dịch SePay), gateway, account_number, amount, content, reference_code, time (tại ngân hàng), received_time (website nhận), match_status, raw_payload `[GD]`
- **Trạng thái khớp:** Khớp (`MATCHED`) | Không khớp (`UNMATCHED`)
- **Tham chiếu:** Order (chỉ khi khớp)
- **Quy tắc:**
  - Webhook xác thực bằng API key từ biến môi trường; sai khóa thì không ghi.
  - Mỗi provider_id chỉ xử lý 1 lần (SePay có thể gửi lại).
  - Khớp khi nội dung chứa `SOBIE` + order_code của đơn QR `PENDING`, `UNPAID`, còn hạn 24 giờ, và số tiền ≥ total_price; thừa vẫn khớp, thiếu không khớp, mỗi giao dịch xét riêng.
  - Lưu mọi giao dịch (khớp hoặc không) để đối chiếu khi khách liên hệ; ghi giao dịch và chuyển đơn `PAID` trong cùng transaction.

---

# Entity Model — promotion (BR-004)

## Promotion
- **Đại diện:** một chương trình khuyến mãi (gốc chung của 3 loại).
- **Bảng:** `promotion.promotion`
- **Mã:** `KM-<4 số>` (3 loại dùng chung bộ đếm); khuyến mãi không có tên
- **Trường:** type, quantity (số lượt được áp dụng), used_amount (số lượt đã dùng), start_date, end_date, status
- **Loại:** theo sản phẩm (`PRODUCT`) | theo hóa đơn (`ORDER`) | voucher (`CODE`)
- **Trạng thái lưu:** Bật (`ENABLED`) | Tắt (`DISABLED`)
- **Trạng thái hiển thị (tính ra):** Sắp diễn ra | Đang hiệu lực | Đã kết thúc
- **Có một:** ProductPromotion **hoặc** OrderPromotion **hoặc** Voucher (theo loại)
- **Quy tắc:**
  - Giảm theo %, 0 < % < 100, không có mức giảm tối đa.
  - Tạo có popup xác nhận; không sửa; chỉ kết thúc (Bật → Tắt), không bật lại — muốn áp lại thì tạo mới.
  - Danh sách khuyến mãi theo hóa đơn và voucher lọc được theo khoảng thời gian (giao với [start_date, end_date]).

## ProductPromotion
- **Đại diện:** khuyến mãi giảm trực tiếp trên giá một sản phẩm.
- **Bảng:** `promotion.product_promotion`
- **Trường:** discount_percentage
- **Thuộc:** Promotion (loại PRODUCT)
- **Tham chiếu:** Product (đúng 1)
- **Quy tắc:**
  - Chỉ có tạo rồi kết thúc: không có ngày bắt đầu / kết thúc, không giới hạn lượt; hiệu lực ngay khi tạo đến khi Nhân viên kết thúc.
  - Trạng thái hiển thị: Đang hiệu lực | Đã kết thúc. Không lọc theo khoảng thời gian.
  - Mỗi sản phẩm tối đa 1 khuyến mãi chưa kết thúc; áp cho mọi biến thể; được tính cùng mức giảm theo hóa đơn / voucher.

## OrderPromotion
- **Đại diện:** khuyến mãi giảm theo giá trị hóa đơn.
- **Bảng:** `promotion.order_promotion`
- **Trường:** discount_percentage, thresh_price (giá trị đơn tối thiểu)
- **Thuộc:** Promotion (loại ORDER)
- **Quy tắc:**
  - Có thời điểm bắt đầu / kết thúc; hết hiệu lực khi hết hạn hoặc Nhân viên kết thúc sớm (giữ nguyên end_date).
  - Áp khi đang bật, trong thời gian hiệu lực, còn lượt và tạm tính ≥ thresh_price; mỗi đơn dùng 1 lượt, hủy đơn thì hoàn lượt.

## Voucher
- **Đại diện:** mã giảm giá khách nhập khi đặt hàng.
- **Bảng:** `promotion.code_promotion`
- **Trường:** code (duy nhất, không phân biệt hoa thường `[GD]`), discount_percentage, thresh_price
- **Thuộc:** Promotion (loại CODE)
- **Quy tắc:** như OrderPromotion; chỉ giới hạn tổng lượt, không giới hạn số lần mỗi khách.

## Quy tắc chọn mức giảm (UC-31)
- Mỗi đơn tối đa 1 khuyến mãi theo hóa đơn **hoặc** 1 voucher — chọn mức có lợi hơn cho khách; bằng nhau ưu tiên voucher.
- Mức giảm tính trên tạm tính (đã gồm khuyến mãi sản phẩm), không áp vào phí vận chuyển.

---

# Entity Model — inventory (BR-005)

## Supplier
- **Đại diện:** một nhà cung cấp hàng.
- **Bảng:** `inventory.supplier`
- **Mã:** `NCC-<4 số>`
- **Trường:** name, phone_number, email, address, status
- **Tên:** bắt buộc, không trùng với nhà cung cấp khác kể cả nhà cung cấp "Ngừng hợp tác"; so sánh bỏ khoảng trắng đầu/cuối, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt; khi sửa loại trừ chính nhà cung cấp đang sửa (UC-32, đã chốt 22/11/2026).
- **Trạng thái:** Đang hợp tác (`ACTIVE`) | Ngừng hợp tác (`INACTIVE`)
- **Có nhiều:** GoodsReceipt
- **Quy tắc:** chỉ nhà cung cấp Đang hợp tác được chọn khi lập phiếu; cho phép xóa hẳn khi chưa có phiếu nhập; nếu có phiếu tham chiếu ở bất kỳ trạng thái nào thì từ chối xóa và gợi ý ngừng hợp tác (UC-32, đã chốt 22/11/2026).

## GoodsReceipt / GoodsReceiptDetail
- **Đại diện:** một phiếu nhập hàng / một dòng biến thể trong phiếu.
- **Bảng:** `inventory.goods_receipt`, `inventory.goods_receipt_detail`
- **Mã:** `PN-<4 số>`
- **Trường:** final_price (tổng tiền phiếu), status, created_date; dòng: quantity, unit_price (giá nhập thực tế), total_price
- **Trạng thái:** Nháp (`DRAFT`) → Đã xác nhận (`CONFIRMED`) | Đã hủy (`CANCELLED`)
- **Thuộc:** Supplier; Account (Nhân viên lập phiếu)
- **Có nhiều:** GoodsReceiptDetail (mỗi biến thể 1 dòng), tham chiếu Variant
- **Quy tắc:**
  - Xác nhận phiếu cộng tồn và tính lại giá vốn trong cùng 1 transaction; không lưu người / thời điểm xác nhận.
  - Giá nhập là số nguyên VND ≥ 0 (đã chốt 21/11/2026).

## Stock
- **Đại diện:** tồn kho và giá vốn hiện tại của một biến thể (1 kho duy nhất).
- **Bảng:** `inventory.stock`
- **Trường:** quantity, cost_price
- **Thuộc:** Variant (1 – 1, tạo cùng lúc tạo biến thể)
- **Quy tắc:**
  - Tồn kho không bao giờ âm; chỉ module inventory ghi, module khác gọi service.
  - Thay đổi khi: xác nhận phiếu nhập (+), tạo đơn (−), hủy / tự hủy đơn (+), giao không thành công (+, tự động, không thao tác nhận hàng hoàn).
  - Giá vốn bình quân gia quyền theo biến thể: `(giá trị tồn hiện tại + tiền nhập lô) / tồn sau nhập`; tồn = 0 thì bằng giá nhập lô mới; hàng hoàn không làm đổi giá vốn.
  - Ngưỡng tồn kho thấp hard-code.

---

# Entity Model — shipping, reporting

## shipping (BR-006)
- Không có entity riêng. Bàn giao (`CONFIRMED` → `AWAITING_PICKUP`) và trang giả lập vận chuyển (Đã nhận hàng → `SHIPPING`; Đã giao → `DELIVERED`; Giao không thành công → `DELIVERY_FAILED`) chỉ đổi trạng thái Order qua service của ordering.
- Trang giả lập: 1 trang, không cần đăng nhập.

## Dashboard (reporting, BR-007 — view, không phải bảng)
- **Tổng hợp:** doanh thu, lợi nhuận gộp (= doanh thu − Σ số lượng × cost_price của OrderDetail), số đơn theo trạng thái, sản phẩm bán chạy, tồn kho thấp, tiền nhập hàng theo nhà cung cấp (GoodsReceipt đã xác nhận).
- Doanh thu tính trên đơn Giao thành công `[GD]`. Chỉ Nhân viên xem.

---

## Giá trị cố định (hard-code / biến môi trường, không phải entity)

| Giá trị | Nơi lưu |
|---|---|
| Phí vận chuyển cố định cho mọi đơn (mặc định 12.000đ) | Biến môi trường `SHIPPING_FEE` |
| API key webhook SePay | Biến môi trường `SEPAY_API_KEY` |
| Hotline, link Zalo, thông tin người gửi, tài khoản nhận chuyển khoản, ngưỡng tồn kho thấp | Hard-code |
| Nội dung trang giới thiệu, chính sách, FAQ; bảng size chung | Hard-code |

## History
- v2 (2026-11-21): viết lại theo data model v2 — 9 module, gộp hồ sơ vào Account, tách Stock khỏi Variant, mã tự nhiên, khuyến mãi theo sản phẩm chỉ tạo rồi kết thúc, BankTransaction cho webhook SePay
- v2.1 (2026-11-21): chốt bcrypt, múi giờ của mã `KH-` và giá nhập không âm, ghi giả định về thời điểm tạo giỏ hàng và danh sách yêu thích
- v2.2 (2026-11-21): chốt tạo giỏ hàng và danh sách yêu thích cùng lúc tạo tài khoản Khách hàng (Q39)
