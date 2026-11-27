# Use case theo module

[Sơ đồ activity đặt hàng và thanh toán](diagrams/activity-dat-hang-khach-hang.md#1-đặt-hàng-và-thanh-toán)

**Nguồn:** [BR-GIAIDOAN1.md](business-requirements/BR-GIAIDOAN1.md) và ERD `sobin_erd_english_formatted.drawio` (source_of_true). Không dựa vào bộ UC cũ (đã loại bỏ).

**Format:** *Template UC-XXX-Name.md* (Phụ lục A, SDD Ebook), bỏ Owner và Last updated. Mỗi UC ghi rõ BR liên quan, tác nhân (Actor) và Acceptance Criteria (Given/When/Then).

**Quy ước**
- Mã `UC-XX`, đánh số liên tục cho toàn dự án. Tên file: `UC-XX-<slug>.md`.
- Mỗi UC có trong *Notes*: "Quyết định đã chốt" (kèm "đã chốt 15/11/2026" hoặc "theo ERD") và "Giả định [GD]" (chờ developer quyết định). Bảng tổng hợp ở cuối file này.
- Test map theo AC: `test_ucXX_acN_<slug>` (pytest).

## Tác nhân

| Tác nhân | Mô tả |
|---|---|
| Khách vãng lai | Người dùng chưa đăng nhập |
| Khách hàng | Người tự đăng ký trên website, hoặc được Admin tạo tài khoản, để mua hàng |
| Nhân viên | Tài khoản nội bộ, vận hành cửa hàng và được xem thông tin, khóa tài khoản Khách hàng |
| Admin | Tài khoản nội bộ, chỉ quản lý tài khoản: tạo tài khoản mọi vai trò và đổi vai trò qua lại giữa Nhân viên và Admin |
| Hệ thống | Tác vụ tự động (tự hủy đơn, tự xuất hóa đơn, tính mức giảm, tự cộng lại tồn kho) |
| Trang giả lập vận chuyển | 1 trang, không cần đăng nhập, chỉ hiển thị mã đơn và trạng thái; đơn "Chờ lấy hàng" có nút "Đã nhận hàng", đơn "Đang giao" có nút "Đã giao" / "Giao không thành công" |
| SePay | Dịch vụ bên thứ 3 theo dõi biến động số dư tài khoản cửa hàng, gửi webhook về website khi nhận tiền (thay trang giả lập chuyển khoản, chốt 20/11/2026) |

## Module (đã chốt 20/11/2026)

Dự án là modular monolith gồm 10 module, trong đó `notification` được thêm ngày 26/11/2026. Mỗi module dùng cùng một tên cho package code `app/modules/<module>/` và cho thư mục UC, schema PostgreSQL, `TableGroup` trong [data_model_v2.dbml](entity-model/data_model_v2.dbml) khi có. `shipping`, `reporting` và `notification` không có bảng riêng.

| Module | BR | Phạm vi | Bảng (schema cùng tên) |
|---|---|---|---|
| [identity](use-cases/identity/) | BR-001 | Vai trò, tài khoản (gồm thông tin cá nhân), đăng nhập, phiên đăng nhập, quản lý tài khoản | role, account, session |
| [catalog](use-cases/catalog/) | BR-002 | Trang bán hàng, sản phẩm, biến thể, giá bán theo size, phân loại, ảnh | category, collection, gender, size, color, product, product_collection, variant, gallery |
| [shopping](use-cases/shopping/) | BR-002, BR-003 | Giỏ hàng, danh sách yêu thích | cart, cart_item, wishlist, wishlist_item |
| [ordering](use-cases/ordering/) | BR-003 | Đặt hàng COD/QR, vòng đời đơn, hủy đơn, tự hủy đơn QR quá hạn, hóa đơn | payment (phương thức), order, order_detail, order_status_history, invoice |
| [payment](use-cases/payment/) | BR-006 | Webhook SePay, tự đối soát chuyển khoản | bank_transaction |
| [promotion](use-cases/promotion/) | BR-004 | 3 loại khuyến mãi, tính mức giảm | promotion, product_promotion, order_promotion, code_promotion |
| [inventory](use-cases/inventory/) | BR-005 | Nhà cung cấp, phiếu nhập, tồn kho, giá vốn | supplier, goods_receipt, goods_receipt_detail, stock |
| [shipping](use-cases/shipping/) | BR-006 | Bàn giao vận chuyển, trang giả lập vận chuyển | (không có — đổi trạng thái đơn qua service của ordering) |
| [reporting](use-cases/reporting/) | BR-007, BR-002 | Dashboard; tác vụ tổng hợp bán chạy cho trang chủ (đã chốt 22/11/2026, UC-09; catalog phụ trách hiển thị) | (không có — đọc qua service của module khác) |
| `notification` | — | Gửi email theo mẫu (OTP đăng ký UC-01); giai đoạn 2 nhắc giỏ hàng, báo giảm giá wishlist | (không có — module khác gọi `notification/facade.py`) |

Module giao tiếp qua service công khai; không đọc / ghi bảng hoặc gọi repository của module khác (AGENTS.md).

## Danh mục use case

| ID | Tên | Module | BR | Tác nhân |
|---|---|---|---|---|
| [UC-01](use-cases/identity/UC-01-register-account.md) | Đăng ký tài khoản | identity | BR-001 | Khách vãng lai |
| [UC-02](use-cases/identity/UC-02-login.md) | Đăng nhập | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-03](use-cases/identity/UC-03-logout.md) | Đăng xuất `[GD]` | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-04](use-cases/identity/UC-04-update-customer-profile.md) | Cập nhật hồ sơ khách hàng | identity | BR-001 | Khách hàng; Admin qua UC-07 |
| [UC-05](use-cases/identity/UC-05-change-password.md) | Đổi mật khẩu | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-06](use-cases/identity/UC-06-create-account.md) | Admin tạo tài khoản (mọi vai trò) | identity | BR-001 | Admin |
| [UC-07](use-cases/identity/UC-07-edit-account.md) | Sửa tài khoản | identity | BR-001 | Admin; Nhân viên chỉ xem thông tin Khách hàng |
| [UC-08](use-cases/identity/UC-08-lock-unlock-account.md) | Khóa và mở khóa tài khoản | identity | BR-001 | Admin; Nhân viên chỉ khóa Khách hàng |
| [UC-09](use-cases/catalog/UC-09-view-home-page.md) | Xem trang chủ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-10](use-cases/catalog/UC-10-browse-category.md) | Xem sản phẩm theo danh mục | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-11](use-cases/catalog/UC-11-search-products.md) | Tìm kiếm sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-12](use-cases/catalog/UC-12-view-product-detail.md) | Xem chi tiết sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-13](use-cases/catalog/UC-13-view-info-pages.md) | Xem trang giới thiệu, chính sách, FAQ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-14](use-cases/catalog/UC-14-manage-products.md) | Quản lý sản phẩm | catalog | BR-002 | Nhân viên |
| [UC-15](use-cases/catalog/UC-15-manage-variants.md) | Quản lý biến thể màu × size | catalog | BR-002 | Nhân viên |
| [UC-16](use-cases/catalog/UC-16-manage-size-prices.md) | Quản lý giá bán theo size | catalog | BR-002 | Nhân viên |
| [UC-17](use-cases/catalog/UC-17-manage-taxonomy.md) | Quản lý danh mục, bộ sưu tập và thuộc tính | catalog | BR-002 | Nhân viên |
| [UC-18](use-cases/shopping/UC-18-manage-cart.md) | Quản lý giỏ hàng | shopping | BR-003 | Khách vãng lai, Khách hàng |
| [UC-19](use-cases/ordering/UC-19-place-order-cod.md) | Đặt hàng thanh toán COD | ordering | BR-003 | Khách hàng |
| [UC-20](use-cases/ordering/UC-20-place-order-qr.md) | Đặt hàng thanh toán chuyển khoản QR | ordering | BR-003 | Khách hàng |
| [UC-21](use-cases/ordering/UC-21-track-order.md) | Theo dõi đơn hàng | ordering | BR-003 | Khách hàng |
| [UC-22](use-cases/ordering/UC-22-cancel-order.md) | Hủy đơn hàng | ordering | BR-003 | Khách hàng, Nhân viên |
| [UC-23](use-cases/ordering/UC-23-confirm-order.md) | Xác nhận đơn hàng | ordering | BR-003 | Nhân viên |
| [UC-24](use-cases/ordering/UC-24-auto-cancel-overdue-qr-order.md) | Tự hủy đơn chuyển khoản quá hạn | ordering | BR-003 | Hệ thống |
| [UC-25](use-cases/payment/UC-25-confirm-bank-transfer.md) | Tự đối soát chuyển khoản qua webhook SePay | payment | BR-006 | SePay |
| [UC-26](use-cases/ordering/UC-26-issue-invoice.md) | Tự xuất hóa đơn | ordering | BR-003 | Hệ thống |
| [UC-27](use-cases/ordering/UC-27-view-invoice.md) | Xem hóa đơn | ordering | BR-003 | Khách hàng, Nhân viên |
| [UC-28](use-cases/promotion/UC-28-manage-product-promotion.md) | Quản lý khuyến mãi theo sản phẩm | promotion | BR-004 | Nhân viên |
| [UC-29](use-cases/promotion/UC-29-manage-order-promotion.md) | Quản lý khuyến mãi theo giá trị hóa đơn | promotion | BR-004 | Nhân viên |
| [UC-30](use-cases/promotion/UC-30-manage-vouchers.md) | Quản lý voucher | promotion | BR-004 | Nhân viên |
| [UC-31](use-cases/promotion/UC-31-calculate-order-discount.md) | Tính mức giảm cho đơn hàng | promotion | BR-004 | Hệ thống, Khách hàng (nhập voucher) |
| [UC-32](use-cases/inventory/UC-32-manage-suppliers.md) | Quản lý nhà cung cấp | inventory | BR-005 | Nhân viên |
| [UC-33](use-cases/inventory/UC-33-create-goods-receipt.md) | Lập phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-34](use-cases/inventory/UC-34-confirm-goods-receipt.md) | Xác nhận phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-35](use-cases/inventory/UC-35-restock-failed-delivery.md) | Tự cộng lại tồn kho khi giao không thành công | inventory | BR-005 | Hệ thống |
| [UC-36](use-cases/shipping/UC-36-update-shipment-status.md) | Cập nhật trạng thái giao hàng (trang giả lập) | shipping | BR-006 | Trang giả lập vận chuyển |
| [UC-37](use-cases/reporting/UC-37-view-dashboard.md) | Xem dashboard | reporting | BR-007 | Nhân viên |
| [UC-38](use-cases/shopping/UC-38-manage-wishlist.md) | Quản lý danh sách yêu thích | shopping | BR-002 | Khách hàng |
| [UC-39](use-cases/inventory/UC-39-view-stock.md) | Xem tồn kho | inventory | BR-005 | Nhân viên |
| [UC-40](use-cases/shipping/UC-40-hand-over-to-shipping.md) | Bàn giao đơn cho vận chuyển | shipping | BR-006 | Nhân viên |

## Trạng thái đơn dùng chung (đã chốt 15/11/2026, cập nhật 20/11/2026)

```
Chưa xử lý ──(UC-23 xác nhận)──► Đã xác nhận ──(UC-40 bàn giao)──► Chờ lấy hàng ──(UC-36 "Đã nhận hàng")──► Đang giao ──(UC-36 "Đã giao")──► Giao thành công      (UC-26 tự xuất hóa đơn)
    │                                │                                  │                                          └──(UC-36)──────────────► Giao không thành công (UC-35 tự cộng lại tồn kho)
    └────────────────────────────────┴──────────────────────────────────┴──► Đã hủy
        UC-22: khách hủy khi "Chưa xử lý"; Nhân viên hủy (nhập lý do) khi "Chưa xử lý" / "Đã xác nhận" / "Chờ lấy hàng"
        UC-24: hệ thống tự hủy đơn QR quá 24 giờ chưa thanh toán
```
- Không còn thao tác "Từ chối" và trạng thái "Bị từ chối" (đã chốt 20/11/2026).
- Đơn QR có thêm trạng thái thanh toán: Chưa thanh toán → Đã thanh toán, do hệ thống tự đối soát qua webhook SePay (UC-25).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử thay đổi (theo ERD).

## Quyết định đã chốt (15/11/2026)

| Chủ đề | Quyết định | UC |
|---|---|---|
| Trạng thái đơn | Bộ trạng thái như sơ đồ trên; Nhân viên bàn giao vận chuyển thì đơn sang "Chờ lấy hàng", đơn vị vận chuyển bấm "Đã nhận hàng" thì sang "Đang giao" (cập nhật 20/11/2026) | UC-19 → UC-24, UC-36, UC-40 |
| Hủy đơn | Cộng lại tồn kho và hoàn lượt của voucher hoặc khuyến mãi theo hóa đơn đã áp. Khách hủy khi "Chưa xử lý"; Nhân viên hủy đến trước khi vận chuyển nhận hàng, bắt buộc nhập lý do, khách không thấy lý do; không còn "Từ chối" (cập nhật 20/11/2026) | UC-22, UC-23, UC-24, UC-31 |
| Phân quyền | Admin quản trị tài khoản, tạo tài khoản cho mọi vai trò dùng được ngay và đổi vai trò giữa Nhân viên và Admin. Nhân viên vận hành cửa hàng, được xem thông tin và khóa tài khoản Khách hàng (23/11/2026). Admin không xem hóa đơn, dashboard. | UC-02, UC-06, UC-07, UC-08, UC-14, UC-23, UC-27, UC-37 |
| Đổi vai trò | Chỉ đổi qua lại giữa Nhân viên và Admin; không đổi Khách hàng ↔ Nhân viên/Admin (chốt lại 20/11/2026); có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất; tài khoản được cấp mã mới (`NV-` ↔ `AD-`) | UC-07 |
| Tài khoản | Account gồm email, SĐT (unique), mật khẩu, vai trò, trạng thái và họ tên, ngày sinh, địa chỉ; không có username; không còn hồ sơ riêng theo vai trò (21/11/2026). Mã `KH-` / `NV-` / `AD-` do hệ thống cấp, bộ đếm riêng từng loại; ngày sinh bắt buộc với Nhân viên, Admin | UC-01, UC-02, UC-04, UC-06, UC-07 |
| Mật khẩu | Băm bằng bcrypt (21/11/2026) | UC-01, UC-05, UC-06 |
| Tự đổi mật khẩu | Khách hàng, Nhân viên và Admin được tự đổi mật khẩu Sobie đã có. Mật khẩu mới tối thiểu 6 ký tự và phải khác mật khẩu hiện tại (23/11/2026). | UC-05 |
| Admin tạo tài khoản | Admin chọn vai trò từ danh sách thả xuống và đặt mật khẩu ban đầu có ít nhất 6 ký tự. Cấp mã và tạo tài khoản trong cùng một transaction. Hệ thống có sẵn một Admin Hoạt động khi khởi tạo lần đầu (23/11/2026). | UC-06 |
| Mã khách hàng | Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` (21/11/2026) | UC-01, UC-06 |
| Giỏ hàng, danh sách yêu thích | Mỗi Khách hàng có 1 giỏ và 1 danh sách yêu thích, tạo cùng transaction tạo tài khoản Khách hàng; identity gọi service công khai của shopping (21/11/2026, Q39) | UC-01, UC-06, UC-18, UC-38 |
| Thông tin nhận hàng | Khách nhập tay hoặc bấm "Sử dụng thông tin hồ sơ". Hồ sơ đầy đủ thì hệ thống tự điền. Hồ sơ còn thiếu thì mở biểu mẫu hồ sơ tại checkout và tự điền sau khi lưu hợp lệ. Giá trị cuối cùng được lưu theo từng đơn (27/11/2026). | UC-04, UC-19, UC-20 |
| Đăng ký / đăng nhập | Đăng ký bằng email OTP rồi tạo mật khẩu Sobie. Đăng nhập bằng email hoặc số điện thoại đã lưu kèm mật khẩu. Luồng Google dùng chung cho hai trang, cấp phiên ngay sau khi tìm, liên kết hoặc tạo tài khoản. | UC-01, UC-02, UC-04 |
| Cổng đăng nhập | Storefront chỉ cho Khách hàng; Nhân viên / Admin đăng nhập ở storefront bị báo "Thông tin đăng nhập không đúng"; Nhân viên và Admin dùng portal quản trị riêng (21/11/2026) | UC-02 |
| Quay lại sau đăng nhập | Khách hàng đăng nhập storefront từ checkout hoặc tim trên chi tiết được quay lại theo return_url nội bộ hợp lệ của đúng hai luồng này. Server kiểm tra đích sau chuẩn hóa, chặn URL ngoài/dạng //, gạch chéo ngược/ký tự điều khiển/biến thể mã hóa tới đích bị cấm; đích không hợp lệ dùng nhánh mặc định. Giữ kiểm tra vai trò/cổng, không dùng đích storefront ở portal quản trị và không tự thay đổi wishlist (UC-12-Q8; yêu cầu đồng bộ tại Codex 23/11/2026) | UC-02, UC-12, UC-19, UC-20, UC-38 |
| Quên mật khẩu | Làm ở giai đoạn 2; giai đoạn 1 storefront có nút "Quên mật khẩu" nhưng không có hành động (21/11/2026) | UC-02 |
| Xác thực | Website SSR nên dùng phiên phía server lưu ở `identity.session`, không dùng JWT; cookie `HttpOnly`, `Secure`, `SameSite=Lax`, kiểm tra header `Origin` ở mọi request ghi; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ, tính từ lần thao tác cuối; rate limit theo IP: đăng nhập 5 lần/phút (21/11/2026) | UC-02, UC-03 |
| Kết thúc phiên | Đổi vai trò, khóa, đổi mật khẩu xóa mọi `identity.session` của tài khoản → mọi phiên kết thúc ngay (đổi mật khẩu kết thúc cả phiên hiện tại); đăng xuất xóa phiên hiện tại, có hiệu lực ngay (21/11/2026) | UC-03, UC-05, UC-07, UC-08 |
| Cache | Không phải danh sách nào cũng cache. Chỉ dữ liệu công khai cache ở Redis (cache dữ liệu, không cache HTML): danh mục, thuộc tính, danh sách sản phẩm theo danh mục, trang chủ (theo số phiên bản catalog, TTL 5 phút), khuyến mãi đang hiệu lực, khối bán chạy. Không cache: kết quả tìm kiếm, mọi trang / danh sách cần đăng nhập (kể cả portal quản trị), dashboard. Header: không trang HTML nào `public`; trang công khai `private, no-cache`, không dùng `ETag`; trang cần đăng nhập `no-store`; `Vary: HX-Request`; file tĩnh cache 1 năm (21/11/2026, cập nhật cho SSR) | Mọi UC có danh sách |
| Lỗi Redis sau khi DB commit | Trong UC-14/15/16/17, commit PostgreSQL trước rồi mới tăng phiên bản catalog; DB rollback thì không tăng phiên bản. Nếu Redis lỗi/timeout sau commit: ghi log cảnh báo, vẫn báo thành công, không rollback DB. Chỉ dữ liệu thực sự đọc từ cache công khai có thể cũ đến hết TTL còn lại (tối đa 5 phút) hoặc lần tăng phiên bản thành công tiếp theo; request mới làm mới cache sẽ nhận dữ liệu mới. Luồng không cache và lọc trạng thái hiện hành từ DB ở khối Bán chạy không chờ TTL. TTL không tự cập nhật DOM đã mở (22/11/2026, UC-17-Q6 và áp dụng UC-16; mở rộng UC-14-Q10/UC-15-Q7 theo duyệt tại Codex 23/11/2026) | UC-14, UC-15, UC-16, UC-17 |
| Chặn mua từ dữ liệu storefront cũ | UC-18 kiểm tra cả sản phẩm cha và biến thể đều ACTIVE, cùng tồn kho hiện hành từ DB qua Service công khai trước khi thêm giỏ, kể cả localStorage. UC-19/20 kiểm tra lại sau khi giữ khóa sản phẩm trong transaction tạo đơn, đồng bộ với UC-14/15 qua Service catalog; sản phẩm hoặc biến thể không còn ACTIVE thì rollback, báo dòng lỗi, không tạo đơn hoặc trừ kho. TTL cache không thay thế kiểm tra này (23/11/2026, UC-15-Q7 và yêu cầu xử lý rà soát vòng 3 tại Codex) | UC-18, UC-19, UC-20 |
| Các khối sản phẩm trang chủ | Hàng mới: tối đa 8 sản phẩm hợp lệ mới nhất theo product_created_at giảm dần. Mỗi bộ sưu tập: tên bộ sưu tập và tối đa 4 sản phẩm hợp lệ mới nhất. Lọc sản phẩm cha ACTIVE có biến thể ACTIVE giá > 0 trước giới hạn 8/4; bù suất bằng sản phẩm hợp lệ tiếp theo, khối rỗng thì ẩn (22/11/2026, UC-09-Q1; cập nhật 23/11/2026 theo UC-10-Q10, duyệt tại Codex) | UC-09 |
| Khối bán chạy trang chủ | Top 5 theo tổng số lượng bán trong 168 giờ UTC; tính từ lúc đặt, loại Đã hủy/Giao không thành công. Bằng số lượng ưu tiên đơn gần nhất rồi product_id tăng dần. Tác vụ 10 phút tính top 15, TTL 30 phút; khi render đọc trạng thái và biến thể hợp lệ hiện hành từ DB, loại sản phẩm Ngừng bán/không có biến thể ACTIVE giá > 0 rồi lấy tối đa 5 trong top 15. Không lấy ngoài top 15; còn 1–4 hiển thị số còn lại, còn 0 ẩn khối. Lọc hiển thị không đổi thống kê reporting (UC-09-Q2/Q4; cập nhật theo UC-10-Q10, duyệt tại Codex 23/11/2026) | UC-09 |
| Ranh giới khối bán chạy trang chủ | reporting tổng hợp qua service ordering và ghi Redis; catalog đọc top 15, lọc dữ liệu sản phẩm/biến thể hiện hành trong module catalog trước giới hạn 5, độc lập việc tăng catalog_version thành công hay lỗi; lấy khuyến mãi/tồn kho qua service promotion/inventory. Redis trống/lỗi thì gọi service reporting tính lại qua service ordering (22/11/2026, UC-09-Q2; cập nhật 23/11/2026) | UC-09 |
| Trang danh mục | Lọc theo giới tính, size, danh mục, bộ sưu tập; sắp xếp mặc định mới nhất | UC-10 |
| Sản phẩm (ERD) | 1 danh mục, 1 giới tính, nhiều bộ sưu tập; ảnh (gallery) theo sản phẩm, có thứ tự; review để giai đoạn 2 | UC-12, UC-14, UC-17 |
| Giá bán | Chỉ đặt/đổi trước nhập kho CONFIRMED, theo size; cùng size khác màu cùng giá | UC-12, UC-16 |
| Tập biến thể tính giá và nhãn tồn kho | Chỉ biến thể ACTIVE có variant_sell_price > 0 tham gia min giá thẻ và min-max chi tiết khi có tập hợp lệ; không xét tồn khi tính giá. Nhãn Hết hàng trên thẻ khi không có biến thể trong tập này còn tồn khả dụng > 0 (23/11/2026, UC-10-Q9; duyệt đồng bộ tại Codex) | UC-09, UC-10, UC-11, UC-12 |
| Sản phẩm đủ điều kiện xuất hiện trong danh sách | Sản phẩm cha ACTIVE có ít nhất một biến thể ACTIVE giá > 0; loại từng sản phẩm không đủ điều kiện trước tổng số/tổng trang/giới hạn hiển thị. Không đổi trạng thái DB, không ẩn vì hết tồn. Danh sách rỗng không sinh trang 0 (23/11/2026, UC-10-Q10; duyệt tại Codex) | UC-09, UC-10, UC-11 |
| URL chi tiết không còn biến thể hợp lệ | Sản phẩm cha ACTIVE nhưng không còn biến thể ACTIVE có giá hợp lệ vẫn trả HTTP 200, hiện tên/mô tả/ảnh và "Sản phẩm tạm ngừng kinh doanh", không hiện khoảng giá, vô hiệu hóa màu/size/số lượng/thêm giỏ. Cha INACTIVE hoặc không tồn tại vẫn 404 (UC-12-Q9b, chốt và đồng bộ tại Codex 23/11/2026) | UC-12 |
| Trang thông tin | Giới thiệu, chính sách, FAQ có nội dung cố định | UC-13 |
| Lỗi 404 HTMX trang thông tin | Giữ HTTP 404, dùng htmx:beforeSwap cho riêng response 404 với target #main-content để hiện lỗi trong DOM; không bật swap mọi 4xx/5xx, không thay lỗi session 401/403 (UC-13-Q5, chốt 23/11/2026; đồng bộ tại Codex) | UC-13 |
| Lịch sử HTMX và phiên | `no-store` chỉ kiểm soát HTTP cache. Layout có nội dung gắn với phiên phải có `hx-history="false"` trước khi rời trang; `historyRestoreAsHxRequest = false` để Back/Forward yêu cầu trang đầy đủ và server kiểm tra lại phiên, không khôi phục DOM riêng của phiên đã đăng xuất (review PR #7, 23/11/2026; UC-13 AC-9) | UC-13, layout chung |
| Wishlist | Khách hàng thả tim lưu sản phẩm; mỗi sản phẩm 1 lần trong danh sách | UC-38 |
| Tim sau đăng nhập từ trang chi tiết | Chỉ quay lại trang, không tự thích/bỏ thích. Tim phản ánh wishlist đã lưu: chưa có thì chưa chọn, đã có thì đã chọn; khách chủ động thao tác tiếp để thay đổi (UC-12-Q4/Q8, đồng bộ UC-38 tại Codex 23/11/2026) | UC-12, UC-38 |
| Khuyến mãi | Giảm theo %, không có mức tối đa; mỗi đơn tối đa 1 khuyến mãi theo hóa đơn hoặc voucher; bằng nhau ưu tiên voucher. Khi mức giảm hoặc nguồn giảm thay đổi, khách xác nhận kết quả mới trước khi tạo đơn. | UC-28 → UC-31 |
| Số lượng khuyến mãi | Có số lượng được áp dụng và số đã dùng; khuyến mãi theo sản phẩm không giới hạn, hiệu lực đến khi Nhân viên kết thúc | UC-28, UC-29, UC-30 |
| Thời gian khuyến mãi | Theo sản phẩm: chỉ có tạo rồi kết thúc, không có ngày bắt đầu / kết thúc, gắn đúng 1 sản phẩm; không lưu thời điểm tạo / kết thúc. Theo hóa đơn và voucher: chọn ngày theo lịch `Asia/Ho_Chi_Minh`; bắt đầu từ 00:00:00 ngày bắt đầu; áp đến hết ngày kết thúc (hết hiệu lực 00:00:00 ngày kế tiếp); hoặc Nhân viên ngừng trước hạn (giữ nguyên ngày kết thúc) (20/11/2026; làm rõ mốc hết ngày 24/11/2026) | UC-28, UC-29, UC-30 |
| Admin | Hệ thống luôn có ít nhất một Admin ở trạng thái Hoạt động. Khóa và đổi vai trò phải giữ ràng buộc này, kể cả khi thao tác đồng thời (23/11/2026). | UC-06, UC-07, UC-08 |
| Khóa và mở khóa tài khoản | Admin có thể khóa và mở khóa tài khoản của cả ba vai trò, tuân theo ràng buộc Admin Hoạt động. Hồ sơ, đơn hàng và dữ liệu nghiệp vụ giữ nguyên (23/11/2026). | UC-08 |
| Giỏ khách vãng lai | Lưu ở `localStorage`; giỏ không lưu giá, luôn hiển thị giá hiện tại (20/11/2026) | UC-18 |
| Lý do hủy | Lưu ở `order_status_history_note` (20/11/2026) | UC-22 |
| Trạng thái khuyến mãi | Lưu cờ bật / tắt; trạng thái hiển thị Sắp diễn ra (chỉ hóa đơn và voucher) / Đang hiệu lực / Đã kết thúc được tính ra; đã kết thúc thì không bật lại (20/11/2026) | UC-28, UC-29, UC-30 |
| Voucher (ERD) | Có giá trị đơn tối thiểu; chỉ giới hạn tổng lượt dùng | UC-30, UC-31 |
| Nhà cung cấp | Gồm tên, SĐT, email, địa chỉ | UC-32 |
| Tồn kho | Chỉ Nhân viên xem; mỗi dòng gồm tên sản phẩm, màu, size, số lượng tồn; 20 biến thể/trang, sắp theo tên sản phẩm tăng dần, trùng tên thì theo SKU tăng dần. Tìm tên chứa từ khóa, không phân biệt hoa/thường, có phân biệt dấu; kết hợp được với lọc danh mục, giữ điều kiện khi chuyển trang. Đánh dấu tồn ≤ 5, gồm cả tồn 0; không hiển thị giá vốn; vẫn hiển thị sản phẩm/biến thể ngừng bán. Không sửa tay tồn kho, không cache, đọc DB mỗi request; tồn mới hiển thị ở lần yêu cầu xem tiếp theo (22/11/2026) | UC-39 |
| Trang giả lập | Chỉ còn trang giả lập vận chuyển, không cần đăng nhập, 1 trang; chỉ hiển thị mã đơn và trạng thái, không công khai PII / COD; mỗi lần bàn giao một đơn (cập nhật 20/11/2026, đồng bộ demo 24/11/2026) | UC-36, UC-40 |
| Thanh toán chuyển khoản | Dùng chung 1 tài khoản; SePay gửi webhook, hệ thống tự đối soát; nội dung `SOBIE` + mã đơn; thừa tiền vẫn khớp, thiếu là không khớp, không cộng dồn; không khớp thì khách liên hệ cửa hàng (20/11/2026) | UC-20, UC-25 |
| Mã đơn hàng | 8 ký tự ngẫu nhiên Crockford Base32, UNIQUE, trùng thì sinh lại (20/11/2026) | UC-20, UC-25 |
| Phí vận chuyển | 1 biến môi trường cho mọi đơn, mặc định 12.000đ; demo bằng sản phẩm 2.000đ (20/11/2026) | UC-19, UC-20, UC-31 |
| Hóa đơn | Tự xuất khi giao thành công; khách và Nhân viên chỉ xem (20/11/2026) | UC-26, UC-27 |
| Hóa đơn (ERD) | Lưu snapshot thông tin đơn lúc xuất | UC-26 |
| Dashboard | Bỏ chỉ số hiệu quả khuyến mãi | UC-37 |
| Kỳ ghi nhận trên dashboard | Doanh thu, lợi nhuận gộp và Top 10 sản phẩm bán chạy tính theo ngày đơn chuyển sang "Giao thành công" (22/11/2026). Doanh thu là tiền hàng sau giảm, không gồm phí vận chuyển. Top 10 xếp theo số lượng bán. | UC-37 |
| Kỳ ghi nhận tiền nhập hàng | Cộng tiền các phiếu nhập đã xác nhận theo ngày lập phiếu và nhóm theo nhà cung cấp (22/11/2026) | UC-37 |
| Bảng size | Một bảng size chung, nội dung cố định | UC-12, UC-14 |
| Giá theo size | Giữ `variant_sell_price`; đặt giá cho size thì ghi cùng giá cho mọi màu của size đó | UC-16 |
| Từ chối đơn | Bỏ hẳn thao tác từ chối; Nhân viên dùng "Hủy đơn" có lý do (cập nhật 20/11/2026) | UC-22, UC-23 |
| Lịch sử thanh toán | Đổi trạng thái thanh toán không ghi vào lịch sử trạng thái đơn | UC-25, UC-26 |
| Sửa khuyến mãi | Khuyến mãi đã tạo không được sửa, chỉ ngừng; tạo có popup xác nhận | UC-28 → UC-31 |
| Tra cứu khuyến mãi | Không có tên, nhận diện bằng mã `KM-<4 số>`; danh sách khuyến mãi theo hóa đơn và voucher lọc theo khoảng thời gian — hiện khuyến mãi có thời gian hiệu lực giao với khoảng chọn (kể cả một phần); khuyến mãi theo sản phẩm không lọc theo thời gian (20/11/2026) | UC-28, UC-29, UC-30 |
| Nhà cung cấp | Có trạng thái Đang hợp tác / Ngừng hợp tác; chỉ chọn nhà cung cấp Đang hợp tác khi lập phiếu | UC-32, UC-33 |
| Xóa nhà cung cấp | Cho phép xóa hẳn khi chưa có phiếu nhập; nếu có phiếu tham chiếu ở bất kỳ trạng thái nào thì từ chối xóa và gợi ý ngừng hợp tác (22/11/2026) | UC-32 |
| Tên nhà cung cấp | Bắt buộc, không trùng với NCC khác kể cả NCC ngừng hợp tác; so sánh bỏ khoảng trắng đầu/cuối, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt; khi sửa loại trừ chính NCC đang sửa (22/11/2026) | UC-32 |
| Danh sách nhà cung cấp | Có phân trang, tìm theo tên chứa từ khóa; tìm kiếm bỏ khoảng trắng đầu/cuối của tên và từ khóa, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt (22/11/2026) | UC-32 |
| Giá nhập | Số nguyên VND ≥ 0 (21/11/2026) | UC-33 |
| Phiếu nhập | Không lưu người / thời điểm xác nhận | UC-34 |
| Phiếu nhập — xử lý đồng thời | Sửa/hủy/xác nhận cùng khóa dòng phiếu rồi kiểm tra lại DRAFT trong transaction; xác nhận khóa sản phẩm/biến thể qua Service Catalog trước inventory.stock và tăng phiên bản cache catalog sau commit thành công (22/11/2026) | UC-33, UC-34 |
| Phiếu nhập — lỗi cache sau commit | Vẫn báo xác nhận thành công, giữ dữ liệu đã commit, ghi log lỗi cache kèm mã phiếu; chờ TTL dự phòng 5 phút, không retry (22/11/2026) | UC-34 |
| Phiếu nhập — NCC ngừng hợp tác | Chặn chọn/lưu với NCC ngừng hợp tác; vẫn cho xác nhận phiếu nháp đã lưu trước khi NCC ngừng hợp tác (22/11/2026) | UC-33, UC-34 |
| Tiền nhập hàng theo NCC | Theo ngày tạo phiếu, chỉ tính phiếu đã xác nhận tại thời điểm xem; xác nhận muộn có thể làm tăng số liệu kỳ cũ (22/11/2026) | UC-34, UC-37 |
| Hàng hoàn | Khóa và kiểm tra trạng thái đơn để chống cộng tồn hai lần; cộng tồn, đổi trạng thái và ghi lịch sử cùng transaction. Hàng ngừng bán vẫn được cộng tồn; lỗi đã xác định không commit thì rollback và cho gửi lại. Kết quả commit chưa xác định phải kiểm tra lại Database; lỗi cache sau commit chỉ thử lại cache, giữ kết quả nghiệp vụ thành công (22/11/2026) | UC-35 |
| Sắp xếp trang danh mục và tìm kiếm | Mới nhất: product_created_at DESC, product_id ASC; Giá tăng/giảm: effective_min_price ASC/DESC sau khuyến mãi, luôn product_id ASC làm khóa phụ cuối. Dữ liệu cố định thì phân trang/reload nhất quán (UC-10-Q2/Q11, UC-11-Q10; duyệt đồng bộ tại Codex 23/11/2026) | UC-10, UC-11 |
| Bộ lọc trang danh mục | Các tiêu chí kết hợp theo VÀ (AND); mỗi tiêu chí chọn tối đa một giá trị (22/11/2026, Q4) | UC-10 |
| Lọc size trên trang danh mục | Hiển thị sản phẩm có ít nhất một biến thể thuộc size đã chọn, không xét còn hàng hay hết hàng (22/11/2026, Q3) | UC-10 |
| Giá trị lọc không tồn tại | Bỏ qua tiêu chí lọc không hợp lệ, tiếp tục áp dụng các tiêu chí hợp lệ còn lại (22/11/2026, Q8) | UC-10 |
| Phân trang danh mục | Cố định 12 sản phẩm/trang (22/11/2026, Q7) | UC-10 |
| Giá trên thẻ sản phẩm danh mục | Giá thấp nhất từ biến thể ACTIVE có giá > 0; nhiều mức giá dùng `Từ <giá thấp nhất>đ`, cùng giá hiển thị một mức giá; có khuyến mãi hiển thị giá gốc/giá sau giảm, làm tròn VND nguyên ROUND_HALF_UP (22/11/2026, Q1; cập nhật 23/11/2026 theo Q9) | UC-10 |
| Tham số trang danh mục | Khi có kết quả, trang vượt giới hạn trả trang cuối; trang nhỏ hơn 1 hoặc không hợp lệ trả trang 1. Kết quả rỗng thì hiển thị thông báo rỗng, không sinh trang 0 (22/11/2026, Q5) | UC-10 |
| Chuẩn hóa tìm kiếm | Tìm kiếm không phân biệt hoa/thường và dấu tiếng Việt (22/11/2026, Q1) | UC-11 |
| Phạm vi từ khóa tìm kiếm | Khớp chuỗi con trên tên và mô tả của sản phẩm Đang bán (22/11/2026, Q1) | UC-11 |
| Trang chính sách | Một trang chính sách chung duy nhất (22/11/2026, Q1) | UC-13 |
| Trạng thái sản phẩm | Đang bán (`ACTIVE`) hoặc Ngừng bán (`INACTIVE`); sản phẩm mới tạo ở trạng thái Ngừng bán (22/11/2026, Q1) | UC-14 |
| Trường bắt buộc của sản phẩm | Tên sản phẩm, một danh mục và một giới tính là bắt buộc (22/11/2026, Main Flow và Quyết định đã chốt) | UC-14 |
| Khóa sản phẩm đã nhập kho | Có phiếu CONFIRMED ở bất kỳ biến thể nào thì chỉ được sửa Mô tả toàn sản phẩm; khóa mọi trường khác, ảnh, giá, trạng thái, thêm/xóa/đổi trạng thái biến thể, đổi tên taxonomy liên quan. Tồn kho về 0 không gỡ khóa; DRAFT/CANCELLED chưa kích hoạt khóa sửa, điều kiện chặn xóa do liên kết phiếu nhập vẫn áp dụng. Ưu tiên hơn các quyền sửa cũ; cấu hình trước khi xác nhận nhập (developer chốt tại Codex 23/11/2026, review PR #7, UC-14-Q11/UC-17-Q7) | UC-14, UC-15, UC-16, UC-17 |
| Thứ tự khóa chống tương tranh | UC-14/15 lấy đủ taxonomy KEY SHARE theo tên bảng/UUID trước sản phẩm; UC-17 lấy taxonomy FOR UPDATE trước sản phẩm. Sản phẩm product_key ASC trước biến thể variant_key ASC. UC-34 khóa dòng phiếu rồi gọi Service Catalog cùng session khóa sản phẩm/biến thể, tiếp đến khóa inventory.stock trước xác nhận; Catalog chỉ đọc CONFIRMED qua Service inventory, không khóa phiếu sau sản phẩm. Đọc lại dữ liệu sau chờ, giữ khóa tới commit/rollback (yêu cầu xử lý rà soát tại Codex 23/11/2026) | UC-14, UC-15, UC-17, UC-34 |
| Điều kiện mở bán sản phẩm | Có ít nhất một ảnh gallery, ít nhất một biến thể và mọi size đã có giá bán > 0; tồn kho = 0 vẫn cho mở bán. Chặn xóa ảnh cuối khi sản phẩm đang ACTIVE (22/11/2026, Q1/Q7) | UC-14 |
| Xóa sản phẩm | Chặn xóa nếu đã có trong đơn hàng hoặc phiếu nhập (kể cả nháp), đã từng gắn khuyến mãi theo sản phẩm (kể cả đã kết thúc), hoặc còn tồn kho > 0. Xóa hợp lệ và dọn dữ liệu liên quan qua service công khai trong cùng transaction; lỗi thì rollback (22/11/2026, Q2/Q6) | UC-14 |
| Tồn kho biến thể mới | Tồn kho và giá vốn ban đầu bằng 0, khởi tạo qua service inventory trong cùng transaction tạo biến thể; không sửa tồn kho trực tiếp trên màn hình biến thể (22/11/2026, Q1) | UC-15 |
| Xóa biến thể | Chỉ xóa khi tồn kho = 0 và chưa có trong đơn hàng/phiếu nhập; kiểm tra, xóa biến thể và dọn stock qua service inventory trong cùng transaction (22/11/2026, Q3) | UC-15 |
| Giá đơn hàng đã tạo | Giữ snapshot đơn giá lúc đặt hàng; sản phẩm có phiếu CONFIRMED không được đổi giá nữa (Q1 ngày 22/11/2026, giới hạn bởi UC-14-Q11 ngày 23/11/2026) | UC-16 |
| Lịch sử giá | Không lưu lịch sử giá; chỉ lưu giá hiện hành tại `catalog.variant.variant_sell_price` (22/11/2026, Q1) | UC-16 |
| Cấp danh mục | Chỉ có danh mục một cấp, không có danh mục con (22/11/2026, Quyết định đã chốt) | UC-17 |
| Xóa danh mục và thuộc tính | Chặn xóa danh mục/bộ sưu tập/giới tính khi có sản phẩm liên kết; chặn xóa màu/size khi có biến thể liên kết, kiểm tra tại thời điểm xóa và báo số lượng đang dùng (22/11/2026, Q1) | UC-17 |

## Data model

Bản hiện hành: [data_model_v2.dbml](entity-model/data_model_v2.dbml) — review ERD vẽ tay theo BR, changelog và câu hỏi mở ở cuối file.
## Tổng hợp giả định `[GD]`

Mỗi dòng là một giả định đang có trong mục *Notes* của UC, chờ developer xác nhận hoặc sửa. Developer chốt 9 module ngày 20/11/2026 và bổ sung `notification` ngày 26/11/2026, nâng tổng số lên 10 module.

| UC | Giả định |
|---|---|
| UC-01 | Ngày sinh và địa chỉ nhận hàng không bắt buộc khi đăng ký; khách bổ sung ở UC-04. |
| UC-01 | Cấp mã và tạo account trong cùng một transaction. |
| UC-01 | Mật khẩu tối thiểu 6 ký tự. |
| UC-01 | Đăng ký bằng email OTP xong thì chuyển tới trang đăng nhập. Đăng ký qua Google cấp phiên ngay và đưa khách tới trang chủ hoặc checkout. |
| UC-01 | Người đã đăng nhập mở trang đăng ký thì bị chuyển về trang chủ. |
| UC-02 | Sau đăng nhập: Khách hàng về trang bán hàng; Nhân viên và Admin về trang đầu của portal quản trị. |
| UC-02 | Sai thông tin đăng nhập báo chung, không chỉ rõ sai tài khoản hay mật khẩu. |
| UC-02 | Portal quản trị từ chối tài khoản Khách hàng với cùng thông báo "Thông tin đăng nhập không đúng". |
| UC-02 | Portal quản trị không có nút "Quên mật khẩu". |
| UC-02 | Vượt rate limit trả HTTP 429. |
| UC-02 | Storefront và portal quản trị dùng 2 cookie phiên khác tên; một trình duyệt có thể đăng nhập cùng lúc vào cả hai cổng. |
| UC-03 | Toàn bộ UC này là giả định: BR-001 chỉ nêu đăng ký và đăng nhập, không nêu đăng xuất. |
| UC-04 | Email trên hồ sơ storefront chỉ xem. Khách có thể đổi số điện thoại mà không cần xác minh lại. Admin có thể đổi email qua UC-07. |
| UC-07 | Việc xem và tìm danh sách tài khoản gộp vào UC này. |
| UC-07 | Danh sách có phân trang; tìm theo họ tên, email hoặc số điện thoại. |
| UC-07 | Admin sửa được thông tin mọi tài khoản. |
| UC-07 | Đổi vai trò giữ nguyên thông tin cá nhân, email, số điện thoại, mật khẩu; lưu trong một transaction, lỗi thì hủy toàn bộ. |
| UC-08 | Khóa và mở khóa áp dụng cho mọi vai trò (Khách hàng, Nhân viên, Admin). |
| UC-08 | Khóa không xóa dữ liệu của tài khoản. |
| Chung | Khuyến mãi đang hiệu lực trong Redis: TTL hết hạn ở mốc bắt đầu / kết thúc gần nhất, xóa key khi tạo hoặc kết thúc khuyến mãi. |
| UC-18 | Khi đăng nhập, giỏ trong `localStorage` gộp vào giỏ tài khoản; dòng trùng cộng dồn nhưng không vượt tồn kho. |
| UC-18 | Dòng hết hàng/ngừng bán vẫn nằm trong giỏ nhưng không tính tiền và không đặt được. |
| UC-19 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn. |
| UC-19 | Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công. |
| UC-19 | Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại. |
| UC-20 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn; các dòng đã đặt được xóa khỏi giỏ. |
| UC-20 | Khách xem lại được mã QR trong chi tiết đơn khi còn chưa thanh toán và chưa quá hạn; ẩn QR khi đơn đã thanh toán, đã hủy hoặc quá hạn. |
| UC-21 | Danh sách đơn sắp xếp mới nhất trước, có phân trang. |
| UC-22 | Lý do hủy tối đa 500 ký tự. |
| UC-23 | UC này gồm cả xem danh sách đơn, có phân trang và lọc theo trạng thái. |
| UC-23 | Không cho xác nhận đơn QR khi chưa thanh toán. |
| UC-24 | Tác vụ chạy mỗi 5 phút. |
| UC-25 | Mã đơn được tìm trong nội dung chuyển khoản không phân biệt vị trí, hoa thường. |
| UC-25 | Mọi giao dịch đều lưu ở `bank_transaction`; không có màn hình cho Nhân viên xem giao dịch không khớp. |
| UC-25 | Webhook không khớp vẫn trả thành công cho SePay. |
| UC-25 | Công cụ gửi webhook mẫu dự phòng khi demo, chỉ bật ở dev/demo. |
| UC-26 | Đơn COD được ghi nhận "Đã thanh toán" khi giao thành công. |
| UC-26 | Lỗi tạo hóa đơn không làm thay đổi trạng thái giao của đơn; hệ thống thử lại. |
| UC-27 | Nhân viên có trang danh sách hóa đơn, mới nhất trước, phân trang, tìm theo mã đơn hoặc mã hóa đơn. |
| UC-28 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-29 | Được phép có nhiều khuyến mãi theo hóa đơn cùng hiệu lực; UC-31 chọn cái giảm nhiều nhất trong số đủ điều kiện. |
| UC-29 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100; số lượng được áp dụng ≥ 1. |
| UC-29 | Danh sách khuyến mãi hiển thị số lượng được áp dụng và số lượng đã dùng. |
| UC-30 | Mã voucher không phân biệt hoa thường. |
| UC-30 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-30 | Danh sách voucher hiển thị tổng lượt dùng và số lượt đã dùng. |
| UC-31 | Có nhiều khuyến mãi theo hóa đơn đủ điều kiện thì lấy mức giảm lớn nhất. |
| UC-31 | Mức giảm theo hóa đơn hoặc voucher tính trên tạm tính (đã gồm khuyến mãi theo sản phẩm), không áp vào phí vận chuyển, và không vượt quá tạm tính. |
| UC-33 | Phiếu nhập có trạng thái: Nháp → Đã xác nhận \| Đã hủy; chỉ sửa và hủy được khi còn "Nháp". |
| UC-33 | Mỗi biến thể chỉ xuất hiện một dòng trong một phiếu. |
| UC-33 | Danh sách phiếu nhập lọc được theo trạng thái và nhà cung cấp. |
| UC-38 | Nút tim có trên cả thẻ sản phẩm và trang chi tiết. |
| UC-38 | Danh sách yêu thích sắp xếp mới thêm nhất trước (theo thứ tự thêm; ERD không có cột thời gian riêng), có phân trang. |
| UC-38 | Sản phẩm ngừng bán vẫn ở danh sách, hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết. |

## Câu hỏi mở (từ BR-GIAIDOAN1)

- Chung: phạm vi constraint cache — đã chốt 21/11/2026, cập nhật cho SSR (xem bảng quyết định, dòng "Cache"): danh sách quản trị không cache; không dùng `ETag`.
- Chung `[GD]`: cách gom In Scope thành 7 BR; Success Metric của từng BR suy ra từ metric tổng.
- Promotion / Ordering: `quote_order_discount` / `confirm_order_discount` / `consume_promotion` / `refund_promotion` đã sẵn trong module promotion; UC-19/20 (đặt) và UC-22/24 (hủy) cần gọi trong cùng transaction khi triển khai ordering. `/admin/promotions` chỉ có công cụ tính thử, không tạo đơn và không thay đổi lượt dùng.
