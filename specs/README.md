# Use case theo module

**Nguồn:** [BR-GIAIDOAN1.md](../business-requirements/BR-GIAIDOAN1.md) và ERD `sobin_erd_english_formatted.drawio` (source_of_true). Không dựa vào bộ UC cũ (đã loại bỏ).

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
| Trang giả lập vận chuyển | 1 trang, không cần đăng nhập; đơn "Chờ lấy hàng" có nút "Đã nhận hàng", đơn "Đang giao" có nút "Đã giao" / "Giao không thành công" |
| SePay | Dịch vụ bên thứ 3 theo dõi biến động số dư tài khoản cửa hàng, gửi webhook về website khi nhận tiền (thay trang giả lập chuyển khoản, chốt 20/11/2026) |

## Module (đã chốt 20/11/2026)

Dự án là modular monolith gồm 10 module, trong đó `notification` được thêm ngày 26/11/2026. Mỗi module dùng cùng một tên cho package code `app/modules/<module>/` và cho thư mục UC, schema PostgreSQL, `TableGroup` trong [data_model_v2.dbml](../entity-model/data_model_v2.dbml) khi có. `shipping`, `reporting` và `notification` không có bảng riêng.

| Module | BR | Phạm vi | Bảng (schema cùng tên) |
|---|---|---|---|
| [identity](identity/) | BR-001 | Vai trò, tài khoản (gồm thông tin cá nhân), đăng nhập, phiên đăng nhập, quản lý tài khoản | role, account, session |
| [catalog](catalog/) | BR-002 | Trang bán hàng, sản phẩm, biến thể, giá bán theo size, phân loại, ảnh | category, collection, gender, size, color, product, product_collection, variant, gallery |
| [shopping](shopping/) | BR-002, BR-003 | Giỏ hàng, danh sách yêu thích | cart, cart_item, wishlist, wishlist_item |
| [ordering](ordering/) | BR-003 | Đặt hàng COD/QR, vòng đời đơn, hủy đơn, tự hủy đơn QR quá hạn, hóa đơn | payment (phương thức), order, order_detail, order_status_history, invoice |
| [payment](payment/) | BR-006 | Webhook SePay, tự đối soát chuyển khoản | bank_transaction |
| [promotion](promotion/) | BR-004 | 3 loại khuyến mãi, tính mức giảm | promotion, product_promotion, order_promotion, code_promotion |
| [inventory](inventory/) | BR-005 | Nhà cung cấp, phiếu nhập, tồn kho, giá vốn | supplier, goods_receipt, goods_receipt_detail, stock |
| [shipping](shipping/) | BR-006 | Bàn giao vận chuyển, trang giả lập vận chuyển | (không có — đổi trạng thái đơn qua service của ordering) |
| [reporting](reporting/) | BR-007, BR-002 | Dashboard; khối bán chạy trên trang chủ `[GD]` | (không có — đọc qua service của module khác) |
| `notification` | — | Gửi email theo mẫu (OTP đăng ký UC-01); giai đoạn 2 nhắc giỏ hàng, báo giảm giá wishlist | (không có — module khác gọi `notification/facade.py`) |

Module giao tiếp qua service công khai; không đọc / ghi bảng hoặc gọi repository của module khác (AGENTS.md).

## Danh mục use case

| ID | Tên | Module | BR | Tác nhân |
|---|---|---|---|---|
| [UC-01](identity/UC-01-register-account.md) | Đăng ký tài khoản | identity | BR-001 | Khách vãng lai |
| [UC-02](identity/UC-02-login.md) | Đăng nhập | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-03](identity/UC-03-logout.md) | Đăng xuất `[GD]` | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-04](identity/UC-04-update-customer-profile.md) | Cập nhật hồ sơ khách hàng | identity | BR-001 | Khách hàng; Admin qua UC-07 |
| [UC-05](identity/UC-05-change-password.md) | Đổi mật khẩu | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-06](identity/UC-06-create-account.md) | Admin tạo tài khoản (mọi vai trò) | identity | BR-001 | Admin |
| [UC-07](identity/UC-07-edit-account.md) | Sửa tài khoản | identity | BR-001 | Admin; Nhân viên chỉ xem thông tin Khách hàng |
| [UC-08](identity/UC-08-lock-unlock-account.md) | Khóa và mở khóa tài khoản | identity | BR-001 | Admin; Nhân viên chỉ khóa Khách hàng |
| [UC-09](catalog/UC-09-view-home-page.md) | Xem trang chủ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-10](catalog/UC-10-browse-category.md) | Xem sản phẩm theo danh mục | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-11](catalog/UC-11-search-products.md) | Tìm kiếm sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-12](catalog/UC-12-view-product-detail.md) | Xem chi tiết sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-13](catalog/UC-13-view-info-pages.md) | Xem trang giới thiệu, chính sách, FAQ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-14](catalog/UC-14-manage-products.md) | Quản lý sản phẩm | catalog | BR-002 | Nhân viên |
| [UC-15](catalog/UC-15-manage-variants.md) | Quản lý biến thể màu × size | catalog | BR-002 | Nhân viên |
| [UC-16](catalog/UC-16-manage-size-prices.md) | Quản lý giá bán theo size | catalog | BR-002 | Nhân viên |
| [UC-17](catalog/UC-17-manage-taxonomy.md) | Quản lý danh mục, bộ sưu tập và thuộc tính | catalog | BR-002 | Nhân viên |
| [UC-18](shopping/UC-18-manage-cart.md) | Quản lý giỏ hàng | shopping | BR-003 | Khách vãng lai, Khách hàng |
| [UC-19](ordering/UC-19-place-order-cod.md) | Đặt hàng thanh toán COD | ordering | BR-003 | Khách hàng |
| [UC-20](ordering/UC-20-place-order-qr.md) | Đặt hàng thanh toán chuyển khoản QR | ordering | BR-003 | Khách hàng |
| [UC-21](ordering/UC-21-track-order.md) | Theo dõi đơn hàng | ordering | BR-003 | Khách hàng |
| [UC-22](ordering/UC-22-cancel-order.md) | Hủy đơn hàng | ordering | BR-003 | Khách hàng, Nhân viên |
| [UC-23](ordering/UC-23-confirm-order.md) | Xác nhận đơn hàng | ordering | BR-003 | Nhân viên |
| [UC-24](ordering/UC-24-auto-cancel-overdue-qr-order.md) | Tự hủy đơn chuyển khoản quá hạn | ordering | BR-003 | Hệ thống |
| [UC-25](payment/UC-25-confirm-bank-transfer.md) | Tự đối soát chuyển khoản qua webhook SePay | payment | BR-006 | SePay |
| [UC-26](ordering/UC-26-issue-invoice.md) | Tự xuất hóa đơn | ordering | BR-003 | Hệ thống |
| [UC-27](ordering/UC-27-view-invoice.md) | Xem hóa đơn | ordering | BR-003 | Khách hàng, Nhân viên |
| [UC-28](promotion/UC-28-manage-product-promotion.md) | Quản lý khuyến mãi theo sản phẩm | promotion | BR-004 | Nhân viên |
| [UC-29](promotion/UC-29-manage-order-promotion.md) | Quản lý khuyến mãi theo giá trị hóa đơn | promotion | BR-004 | Nhân viên |
| [UC-30](promotion/UC-30-manage-vouchers.md) | Quản lý voucher | promotion | BR-004 | Nhân viên |
| [UC-31](promotion/UC-31-calculate-order-discount.md) | Tính mức giảm cho đơn hàng | promotion | BR-004 | Hệ thống, Khách hàng (nhập voucher) |
| [UC-32](inventory/UC-32-manage-suppliers.md) | Quản lý nhà cung cấp | inventory | BR-005 | Nhân viên |
| [UC-33](inventory/UC-33-create-goods-receipt.md) | Lập phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-34](inventory/UC-34-confirm-goods-receipt.md) | Xác nhận phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-35](inventory/UC-35-restock-failed-delivery.md) | Tự cộng lại tồn kho khi giao không thành công | inventory | BR-005 | Hệ thống |
| [UC-36](shipping/UC-36-update-shipment-status.md) | Cập nhật trạng thái giao hàng (trang giả lập) | shipping | BR-006 | Trang giả lập vận chuyển |
| [UC-37](reporting/UC-37-view-dashboard.md) | Xem dashboard | reporting | BR-007 | Nhân viên |
| [UC-38](shopping/UC-38-manage-wishlist.md) | Quản lý danh sách yêu thích | shopping | BR-002 | Khách hàng |
| [UC-39](inventory/UC-39-view-stock.md) | Xem tồn kho | inventory | BR-005 | Nhân viên |
| [UC-40](shipping/UC-40-hand-over-to-shipping.md) | Bàn giao đơn cho vận chuyển | shipping | BR-006 | Nhân viên |

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
| Hủy đơn | Cộng lại tồn kho và hoàn lượt voucher. Khách hủy khi "Chưa xử lý"; Nhân viên hủy đến trước khi vận chuyển nhận hàng, bắt buộc nhập lý do, khách không thấy lý do; không còn "Từ chối" (cập nhật 20/11/2026) | UC-22, UC-23, UC-24, UC-31 |
| Phân quyền | Admin quản trị tài khoản, tạo tài khoản cho mọi vai trò dùng được ngay và đổi vai trò giữa Nhân viên và Admin. Nhân viên vận hành cửa hàng, được xem thông tin và khóa tài khoản Khách hàng (23/11/2026). Admin không xem hóa đơn, dashboard. | UC-02, UC-06, UC-07, UC-08, UC-14, UC-23, UC-27, UC-37 |
| Đổi vai trò | Chỉ đổi qua lại giữa Nhân viên và Admin; không đổi Khách hàng ↔ Nhân viên/Admin (chốt lại 20/11/2026); có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất; tài khoản được cấp mã mới (`NV-` ↔ `AD-`) | UC-07 |
| Tài khoản | Account gồm email, SĐT (unique), mật khẩu, vai trò, trạng thái và họ tên, ngày sinh, địa chỉ; không có username; không còn hồ sơ riêng theo vai trò (21/11/2026). Mã `KH-` / `NV-` / `AD-` do hệ thống cấp, bộ đếm riêng từng loại; ngày sinh bắt buộc với Nhân viên, Admin | UC-01, UC-02, UC-04, UC-06, UC-07 |
| Mật khẩu | Băm bằng bcrypt (21/11/2026) | UC-01, UC-05, UC-06 |
| Tự đổi mật khẩu | Khách hàng, Nhân viên và Admin được tự đổi mật khẩu Sobie đã có. Mật khẩu mới tối thiểu 6 ký tự và phải khác mật khẩu hiện tại (23/11/2026). | UC-05 |
| Admin tạo tài khoản | Admin chọn vai trò từ danh sách thả xuống và đặt mật khẩu ban đầu có ít nhất 6 ký tự. Cấp mã và tạo tài khoản trong cùng một transaction. Hệ thống có sẵn một Admin Hoạt động khi khởi tạo lần đầu (23/11/2026). | UC-06 |
| Mã khách hàng | Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` (21/11/2026) | UC-01, UC-06 |
| Giỏ hàng, danh sách yêu thích | Mỗi Khách hàng có 1 giỏ và 1 danh sách yêu thích, tạo cùng transaction tạo tài khoản Khách hàng; identity gọi service công khai của shopping (21/11/2026, Q39) | UC-01, UC-06, UC-18, UC-38 |
| Thông tin nhận hàng | Khách nhập tên người nhận, số điện thoại và địa chỉ, hoặc bấm "Sử dụng thông tin hồ sơ" nếu hồ sơ có đủ họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng hợp lệ. Khách sửa được thông tin cho riêng đơn (23/11/2026). | UC-04, UC-19, UC-20 |
| Đăng ký / đăng nhập | Đăng ký bằng email OTP rồi tạo mật khẩu Sobie. Đăng nhập bằng email hoặc số điện thoại đã lưu kèm mật khẩu. Luồng Google dùng chung cho hai trang, cấp phiên ngay sau khi tìm, liên kết hoặc tạo tài khoản. | UC-01, UC-02, UC-04 |
| Cổng đăng nhập | Storefront chỉ cho Khách hàng; Nhân viên / Admin đăng nhập ở storefront bị báo "Thông tin đăng nhập không đúng"; Nhân viên và Admin dùng portal quản trị riêng (21/11/2026) | UC-02 |
| Quên mật khẩu | Làm ở giai đoạn 2; giai đoạn 1 storefront có nút "Quên mật khẩu" nhưng không có hành động (21/11/2026) | UC-02 |
| Xác thực | Website SSR nên dùng phiên phía server lưu ở `identity.session`, không dùng JWT; cookie `HttpOnly`, `Secure`, `SameSite=Lax`, kiểm tra header `Origin` ở mọi request ghi; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ, tính từ lần thao tác cuối; rate limit theo IP: đăng nhập 5 lần/phút (21/11/2026) | UC-02, UC-03 |
| Kết thúc phiên | Đổi vai trò, khóa, đổi mật khẩu xóa mọi `identity.session` của tài khoản → mọi phiên kết thúc ngay (đổi mật khẩu kết thúc cả phiên hiện tại); đăng xuất xóa phiên hiện tại, có hiệu lực ngay (21/11/2026) | UC-03, UC-05, UC-07, UC-08 |
| Cache | Không phải danh sách nào cũng cache. Chỉ dữ liệu công khai cache ở Redis (cache dữ liệu, không cache HTML): danh mục, thuộc tính, danh sách sản phẩm theo danh mục, trang chủ (theo số phiên bản catalog, TTL 5 phút), khuyến mãi đang hiệu lực, khối bán chạy. Không cache: kết quả tìm kiếm, mọi trang / danh sách cần đăng nhập (kể cả portal quản trị), dashboard. Header: không trang HTML nào `public`; trang công khai `private, no-cache`, không dùng `ETag`; trang cần đăng nhập `no-store`; `Vary: HX-Request`; file tĩnh cache 1 năm (21/11/2026, cập nhật cho SSR) | Mọi UC có danh sách |
| Khối bán chạy trang chủ | Top 5 sản phẩm theo tổng số lượng bán, 7 ngày gần nhất, tính đơn từ lúc đặt; tác vụ 10 phút; Ngừng bán biến mất ngay (21/11/2026) | UC-09 |
| Trang danh mục | Lọc theo giới tính, size, danh mục, bộ sưu tập; sắp xếp mặc định mới nhất | UC-10 |
| Sản phẩm (ERD) | 1 danh mục, 1 giới tính, nhiều bộ sưu tập; ảnh (gallery) theo sản phẩm, có thứ tự; review để giai đoạn 2 | UC-12, UC-14, UC-17 |
| Giá bán | Chỉ đổi theo size; cùng size khác màu cùng giá | UC-12, UC-16 |
| Trang thông tin | Giới thiệu, chính sách, FAQ có nội dung cố định | UC-13 |
| Wishlist | Khách hàng thả tim lưu sản phẩm; mỗi sản phẩm 1 lần trong danh sách | UC-38 |
| Khuyến mãi | Giảm theo %, không có mức tối đa; mỗi đơn tối đa 1 khuyến mãi theo hóa đơn hoặc voucher; bằng nhau ưu tiên voucher | UC-28 → UC-31 |
| Số lượng khuyến mãi | Có số lượng được áp dụng và số đã dùng; khuyến mãi theo sản phẩm không giới hạn, hiệu lực đến khi Nhân viên kết thúc | UC-28, UC-29, UC-30 |
| Thời gian khuyến mãi | Theo sản phẩm: chỉ có tạo rồi kết thúc, không có ngày bắt đầu / kết thúc, gắn đúng 1 sản phẩm. Theo hóa đơn và voucher: có ngày bắt đầu / kết thúc; hết hiệu lực khi tới ngày kết thúc hoặc Nhân viên ngừng trước hạn (giữ nguyên ngày kết thúc) (20/11/2026) | UC-28, UC-29, UC-30 |
| Admin | Hệ thống luôn có ít nhất một Admin ở trạng thái Hoạt động. Khóa và đổi vai trò phải giữ ràng buộc này, kể cả khi thao tác đồng thời (23/11/2026). | UC-06, UC-07, UC-08 |
| Khóa và mở khóa tài khoản | Admin có thể khóa và mở khóa tài khoản của cả ba vai trò, tuân theo ràng buộc Admin Hoạt động. Hồ sơ, đơn hàng và dữ liệu nghiệp vụ giữ nguyên (23/11/2026). | UC-08 |
| Giỏ khách vãng lai | Lưu ở `localStorage`; giỏ không lưu giá, luôn hiển thị giá hiện tại (20/11/2026) | UC-18 |
| Lý do hủy | Lưu ở `order_status_history_note` (20/11/2026) | UC-22 |
| Trạng thái khuyến mãi | Lưu cờ bật / tắt; trạng thái hiển thị Sắp diễn ra (chỉ hóa đơn và voucher) / Đang hiệu lực / Đã kết thúc được tính ra; đã kết thúc thì không bật lại (20/11/2026) | UC-28, UC-29, UC-30 |
| Voucher (ERD) | Có giá trị đơn tối thiểu; chỉ giới hạn tổng lượt dùng | UC-30, UC-31 |
| Nhà cung cấp | Gồm tên, SĐT, email, địa chỉ | UC-32 |
| Tồn kho | Chỉ Nhân viên xem; mỗi dòng gồm tên sản phẩm, màu, size, số lượng tồn; 20 biến thể/trang, sắp theo tên sản phẩm tăng dần, trùng tên thì theo SKU tăng dần. Tìm tên chứa từ khóa, không phân biệt hoa/thường, có phân biệt dấu; kết hợp được với lọc danh mục, giữ điều kiện khi chuyển trang. Đánh dấu tồn ≤ 5, gồm cả tồn 0; không hiển thị giá vốn; vẫn hiển thị sản phẩm/biến thể ngừng bán. Không sửa tay tồn kho, không cache, đọc DB mỗi request; tồn mới hiển thị ở lần yêu cầu xem tiếp theo (22/11/2026) | UC-39 |
| Trang giả lập | Chỉ còn trang giả lập vận chuyển, không cần đăng nhập, 1 trang (cập nhật 20/11/2026) | UC-36 |
| Thanh toán chuyển khoản | Dùng chung 1 tài khoản; SePay gửi webhook, hệ thống tự đối soát; nội dung `SOBIE` + mã đơn; thừa tiền vẫn khớp, thiếu là không khớp, không cộng dồn; không khớp thì khách liên hệ cửa hàng (20/11/2026) | UC-20, UC-25 |
| Mã đơn hàng | 8 ký tự ngẫu nhiên Crockford Base32, UNIQUE, trùng thì sinh lại (20/11/2026) | UC-20, UC-25 |
| Phí vận chuyển | 1 biến môi trường cho mọi đơn, mặc định 12.000đ; demo bằng sản phẩm 2.000đ (20/11/2026) | UC-19, UC-20, UC-31 |
| Hóa đơn | Tự xuất khi giao thành công; khách và Nhân viên chỉ xem (20/11/2026) | UC-26, UC-27 |
| Hóa đơn (ERD) | Lưu snapshot thông tin đơn lúc xuất | UC-26 |
| Dashboard | Bỏ chỉ số hiệu quả khuyến mãi | UC-37 |
| Kỳ ghi nhận trên dashboard | Doanh thu, lợi nhuận gộp và Top 10 sản phẩm bán chạy tính theo ngày đơn chuyển sang "Giao thành công" (22/11/2026). Doanh thu là tiền hàng sau giảm, không gồm phí vận chuyển. Top 10 xếp theo số lượng bán. | UC-37 |
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
| Phiếu nhập — xử lý đồng thời | Sửa/hủy/xác nhận cùng khóa dòng phiếu rồi kiểm tra lại DRAFT trong transaction; xác nhận khóa inventory.stock và tăng phiên bản cache catalog sau commit thành công (22/11/2026) | UC-33, UC-34 |
| Phiếu nhập — lỗi cache sau commit | Vẫn báo xác nhận thành công, giữ dữ liệu đã commit, ghi log lỗi cache kèm mã phiếu; chờ TTL dự phòng 5 phút, không retry (22/11/2026) | UC-34 |
| Phiếu nhập — NCC ngừng hợp tác | Chặn chọn/lưu với NCC ngừng hợp tác; vẫn cho xác nhận phiếu nháp đã lưu trước khi NCC ngừng hợp tác (22/11/2026) | UC-33, UC-34 |
| Tiền nhập hàng theo NCC | Theo ngày tạo phiếu, chỉ tính phiếu đã xác nhận tại thời điểm xem; xác nhận muộn có thể làm tăng số liệu kỳ cũ (22/11/2026) | UC-34, UC-37 |
| Hàng hoàn | Khóa và kiểm tra trạng thái đơn để chống cộng tồn hai lần; cộng tồn, đổi trạng thái và ghi lịch sử cùng transaction. Hàng ngừng bán vẫn được cộng tồn; lỗi đã xác định không commit thì rollback và cho gửi lại. Kết quả commit chưa xác định phải kiểm tra lại Database; lỗi cache sau commit chỉ thử lại cache, giữ kết quả nghiệp vụ thành công (22/11/2026) | UC-35 |

## Data model

Bản hiện hành: [data_model_v2.dbml](../entity-model/data_model_v2.dbml) — review ERD vẽ tay theo BR, changelog và câu hỏi mở ở cuối file.
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
| UC-02 | Đăng nhập khi đang đặt hàng thì quay lại trang đang thao tác. |
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
| UC-09 | Trang chủ gồm khối hàng mới và khối sản phẩm theo bộ sưu tập. |
| UC-09 | Khối không có sản phẩm thì ẩn. |
| UC-09 | Khối bán chạy: "7 ngày gần nhất" là 7 × 24 giờ tính lùi; loại đơn "Đã hủy"; còn dưới 5 sản phẩm sau khi lọc thì hiển thị số còn lại. |
| UC-09 | Khối bán chạy thuộc module `reporting`, đọc số lượng bán qua `ordering`, lọc trạng thái sản phẩm qua `catalog`. |
| Chung | Khuyến mãi đang hiệu lực trong Redis: TTL hết hạn ở mốc bắt đầu / kết thúc gần nhất, xóa key khi tạo hoặc kết thúc khuyến mãi. |
| UC-10 | Các tiêu chí sắp xếp khác ngoài mặc định: giá tăng dần, giá giảm dần. |
| UC-10 | Các tiêu chí lọc kết hợp theo kiểu "và" (thỏa đồng thời); mỗi tiêu chí chọn một giá trị. |
| UC-10 | Lọc theo size: sản phẩm có ít nhất một biến thể size đó, không xét còn hàng. |
| UC-10 | Giá trị lọc không tồn tại thì bỏ qua tiêu chí đó. |
| UC-10 | Mỗi trang 12 sản phẩm. |
| UC-10 | Thẻ sản phẩm hiển thị giá thấp nhất trong các size. |
| UC-10 | Yêu cầu trang vượt quá tổng số trang thì hiển thị trang cuối. |
| UC-11 | Tìm kiếm không phân biệt hoa thường và dấu tiếng Việt. |
| UC-11 | "Từ khóa" khớp trên tên và mô tả sản phẩm. |
| UC-13 | Chỉ có một trang chính sách chung. |
| UC-14 | Sản phẩm có 2 trạng thái: Đang bán, Ngừng bán; sản phẩm mới tạo ở trạng thái Ngừng bán. |
| UC-14 | Tên, danh mục, giới tính là trường bắt buộc. |
| UC-14 | Chỉ chuyển Đang bán khi đã có biến thể và mọi size đã có giá. |
| UC-14 | Không xóa sản phẩm đã có trong đơn hàng hoặc phiếu nhập. |
| UC-15 | Biến thể mới tạo có tồn kho = 0; tồn kho không sửa tay. |
| UC-15 | Chỉ xóa được biến thể có tồn kho = 0 và chưa có trong đơn hàng hoặc phiếu nhập. |
| UC-16 | Đổi giá không ảnh hưởng đơn hàng đã tạo. |
| UC-16 | Không lưu lịch sử giá. |
| UC-17 | Danh mục một cấp (không có danh mục con). |
| UC-17 | Không xóa danh mục, bộ sưu tập, giới tính, màu hoặc size đang được sử dụng. |
| UC-18 | Khi đăng nhập, giỏ trong `localStorage` gộp vào giỏ tài khoản; dòng trùng cộng dồn nhưng không vượt tồn kho. |
| UC-18 | Dòng hết hàng/ngừng bán vẫn nằm trong giỏ nhưng không tính tiền và không đặt được. |
| UC-19 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn. |
| UC-19 | Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công. |
| UC-19 | Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại. |
| UC-20 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn; các dòng đã đặt được xóa khỏi giỏ. |
| UC-20 | Khách xem lại được mã QR trong chi tiết đơn khi còn chưa thanh toán và chưa quá hạn; ẩn QR khi đơn đã thanh toán, đã hủy hoặc quá hạn. |
| UC-21 | Danh sách đơn sắp xếp mới nhất trước, có phân trang. |
| UC-22 | Hủy đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt). |
| UC-22 | Lý do hủy tối đa 500 ký tự. |
| UC-23 | UC này gồm cả xem danh sách đơn, có phân trang và lọc theo trạng thái. |
| UC-23 | Không cho xác nhận đơn QR khi chưa thanh toán. |
| UC-24 | Tác vụ chạy mỗi 5 phút. |
| UC-24 | Tự hủy cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt). |
| UC-25 | Mã đơn được tìm trong nội dung chuyển khoản không phân biệt vị trí, hoa thường. |
| UC-25 | Mọi giao dịch đều lưu ở `bank_transaction`; không có màn hình cho Nhân viên xem giao dịch không khớp. |
| UC-25 | Webhook không khớp vẫn trả thành công cho SePay. |
| UC-25 | Công cụ gửi webhook mẫu dự phòng khi demo, chỉ bật ở dev/demo. |
| UC-26 | Đơn COD được ghi nhận "Đã thanh toán" khi giao thành công. |
| UC-26 | Lỗi tạo hóa đơn không làm thay đổi trạng thái giao của đơn; hệ thống thử lại. |
| UC-27 | Nhân viên có trang danh sách hóa đơn, mới nhất trước, phân trang, tìm theo mã đơn hoặc mã hóa đơn. |
| UC-28 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-29 | Được phép có nhiều khuyến mãi theo hóa đơn cùng hiệu lực; UC-31 chọn cái giảm nhiều nhất trong số đủ điều kiện. |
| UC-29 | Đơn bị hủy thì hoàn lượt khuyến mãi theo hóa đơn (giảm số lượng đã dùng 1). |
| UC-29 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100; số lượng được áp dụng ≥ 1. |
| UC-29 | Danh sách khuyến mãi hiển thị số lượng được áp dụng và số lượng đã dùng. |
| UC-30 | Mã voucher không phân biệt hoa thường. |
| UC-30 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-30 | Danh sách voucher hiển thị tổng lượt dùng và số lượt đã dùng. |
| UC-31 | Có nhiều khuyến mãi theo hóa đơn đủ điều kiện thì lấy mức giảm lớn nhất. |
| UC-31 | Mức giảm theo hóa đơn hoặc voucher tính trên tạm tính (đã gồm khuyến mãi theo sản phẩm), không áp vào phí vận chuyển, và không vượt quá tạm tính. |
| UC-31 | Số tiền thay đổi giữa lúc xem và lúc xác nhận thì không tạo đơn, yêu cầu khách xác nhận lại. |
| UC-31 | Đơn bị hủy thì hoàn cả lượt khuyến mãi theo hóa đơn. |
| UC-33 | Phiếu nhập có trạng thái: Nháp → Đã xác nhận \| Đã hủy; chỉ sửa và hủy được khi còn "Nháp". |
| UC-33 | Mỗi biến thể chỉ xuất hiện một dòng trong một phiếu. |
| UC-33 | Danh sách phiếu nhập lọc được theo trạng thái và nhà cung cấp. |
| UC-36 | Danh sách trên trang giả lập gồm: mã đơn, trạng thái, người nhận, số điện thoại, địa chỉ, người gửi, số tiền thu khi giao với đơn COD. |
| UC-38 | Nút tim có trên cả thẻ sản phẩm và trang chi tiết. |
| UC-38 | Khách vãng lai bấm tim thì được yêu cầu đăng nhập; sau đăng nhập quay lại trang đang xem, không tự lưu sản phẩm. |
| UC-38 | Danh sách yêu thích sắp xếp mới thêm nhất trước (theo thứ tự thêm; ERD không có cột thời gian riêng), có phân trang. |
| UC-38 | Sản phẩm ngừng bán vẫn ở danh sách, hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết. |
| UC-40 | Có thể bàn giao nhiều đơn một lúc; đơn không hợp lệ thì bỏ qua và báo lại. |

## Câu hỏi mở (từ BR-GIAIDOAN1)

- Chung: phạm vi constraint cache — đã chốt 21/11/2026, cập nhật cho SSR (xem bảng quyết định, dòng "Cache"): danh sách quản trị không cache; không dùng `ETag`.
- Chung `[GD]`: cách gom In Scope thành 7 BR; Success Metric của từng BR suy ra từ metric tổng.
