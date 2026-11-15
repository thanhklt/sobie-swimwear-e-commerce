# Use case theo bounded context

**Nguồn:** [BR-TUAN1.md](../business-requirements/BR-TUAN1.md) và ERD `sobin_erd_english_formatted.drawio` (source_of_true). Không dựa vào bộ UC cũ (đã loại bỏ).

**Format:** *Template UC-XXX-Name.md* (Phụ lục A, SDD Ebook), bỏ Owner và Last updated. Mỗi UC ghi rõ BR liên quan, tác nhân (Actor) và Acceptance Criteria (Given/When/Then).

**Quy ước**
- Mã `UC-XX`, đánh số liên tục cho toàn dự án. Tên file: `UC-XX-<slug>.md`.
- Mỗi UC có trong *Notes*: "Quyết định đã chốt" (kèm "đã chốt 15/11/2026" hoặc "theo ERD") và "Giả định [GD]" (chờ developer quyết định). Bảng tổng hợp ở cuối file này.
- Test map theo AC: `test_ucXX_acN_<slug>` (pytest).

## Tác nhân

| Tác nhân | Mô tả |
|---|---|
| Khách vãng lai | Người dùng chưa đăng nhập |
| Khách hàng | Người tự đăng ký trên website để mua hàng |
| Nhân viên | Tài khoản nội bộ, thực hiện mọi thao tác vận hành cửa hàng |
| Admin | Tài khoản nội bộ, chỉ quản lý tài khoản và gán vai trò (Nhân viên ↔ Admin) |
| Hệ thống | Tác vụ tự động (tự hủy đơn, tự xuất hóa đơn, tính mức giảm, tự cộng lại tồn kho) |
| Trang giả lập vận chuyển | 1 trang, không cần đăng nhập; liệt kê đơn "Đang giao" với nút "Đã giao" / "Giao không thành công" |
| Trang giả lập chuyển khoản | 1 trang, không cần đăng nhập; liệt kê đơn QR chưa thanh toán với nút "Xác nhận đã chuyển khoản" |

## Bounded context `[GD]`

| Thư mục | BR | Phạm vi |
|---|---|---|
| [identity-context](identity-context/) | BR-001 | Tài khoản, đăng nhập, hồ sơ, quản lý tài khoản và vai trò |
| [catalog-context](catalog-context/) | BR-002 | Trang bán hàng, sản phẩm, biến thể, giá, phân loại, danh sách yêu thích |
| [checkout-context](checkout-context/) | BR-003, BR-006 (UC-25) | Giỏ hàng, đặt hàng, thanh toán COD/QR, vòng đời đơn, hóa đơn, xác nhận chuyển khoản |
| [promotion-context](promotion-context/) | BR-004 | 3 loại khuyến mãi, tính mức giảm |
| [inventory-context](inventory-context/) | BR-005 | Nhà cung cấp, phiếu nhập, tồn kho, giá vốn |
| [shipping-context](shipping-context/) | BR-006 | Bàn giao vận chuyển, trang giả lập vận chuyển |
| [reporting-context](reporting-context/) | BR-007 | Dashboard |

## Danh mục use case

| ID | Tên | Context | BR | Tác nhân |
|---|---|---|---|---|
| [UC-01](identity-context/UC-01-register-account.md) | Đăng ký tài khoản | identity | BR-001 | Khách vãng lai |
| [UC-02](identity-context/UC-02-login.md) | Đăng nhập | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-03](identity-context/UC-03-logout.md) | Đăng xuất `[GD]` | identity | BR-001 | Khách hàng, Nhân viên, Admin |
| [UC-04](identity-context/UC-04-update-customer-profile.md) | Cập nhật hồ sơ khách hàng | identity | BR-001 | Khách hàng |
| [UC-05](identity-context/UC-05-change-password.md) | Đổi mật khẩu | identity | BR-001 | Khách hàng; Nhân viên, Admin `[GD]` |
| [UC-06](identity-context/UC-06-create-internal-account.md) | Tạo tài khoản nội bộ | identity | BR-001 | Admin |
| [UC-07](identity-context/UC-07-edit-account.md) | Sửa tài khoản | identity | BR-001 | Admin |
| [UC-08](identity-context/UC-08-lock-unlock-account.md) | Khóa và mở khóa tài khoản | identity | BR-001 | Admin |
| [UC-09](catalog-context/UC-09-view-home-page.md) | Xem trang chủ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-10](catalog-context/UC-10-browse-category.md) | Xem sản phẩm theo danh mục | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-11](catalog-context/UC-11-search-products.md) | Tìm kiếm sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-12](catalog-context/UC-12-view-product-detail.md) | Xem chi tiết sản phẩm | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-13](catalog-context/UC-13-view-info-pages.md) | Xem trang giới thiệu, chính sách, FAQ | catalog | BR-002 | Khách vãng lai, Khách hàng |
| [UC-14](catalog-context/UC-14-manage-products.md) | Quản lý sản phẩm | catalog | BR-002 | Nhân viên |
| [UC-15](catalog-context/UC-15-manage-variants.md) | Quản lý biến thể màu × size | catalog | BR-002 | Nhân viên |
| [UC-16](catalog-context/UC-16-manage-size-prices.md) | Quản lý giá bán theo size | catalog | BR-002 | Nhân viên |
| [UC-17](catalog-context/UC-17-manage-taxonomy.md) | Quản lý danh mục, bộ sưu tập và thuộc tính | catalog | BR-002 | Nhân viên |
| [UC-18](checkout-context/UC-18-manage-cart.md) | Quản lý giỏ hàng | checkout | BR-003 | Khách vãng lai, Khách hàng |
| [UC-19](checkout-context/UC-19-place-order-cod.md) | Đặt hàng thanh toán COD | checkout | BR-003 | Khách hàng |
| [UC-20](checkout-context/UC-20-place-order-qr.md) | Đặt hàng thanh toán chuyển khoản QR | checkout | BR-003 | Khách hàng |
| [UC-21](checkout-context/UC-21-track-order.md) | Theo dõi đơn hàng | checkout | BR-003 | Khách hàng |
| [UC-22](checkout-context/UC-22-cancel-order.md) | Hủy đơn hàng | checkout | BR-003 | Khách hàng |
| [UC-23](checkout-context/UC-23-confirm-or-reject-order.md) | Xác nhận hoặc từ chối đơn | checkout | BR-003 | Nhân viên |
| [UC-24](checkout-context/UC-24-auto-cancel-overdue-qr-order.md) | Tự hủy đơn chuyển khoản quá hạn | checkout | BR-003 | Hệ thống |
| [UC-25](checkout-context/UC-25-confirm-bank-transfer.md) | Xác nhận chuyển khoản (trang giả lập) | checkout | BR-006 | Trang giả lập chuyển khoản |
| [UC-26](checkout-context/UC-26-issue-invoice.md) | Tự xuất hóa đơn | checkout | BR-003 | Hệ thống |
| [UC-27](checkout-context/UC-27-view-invoice.md) | Xem hóa đơn | checkout | BR-003 | Khách hàng, Nhân viên |
| [UC-28](promotion-context/UC-28-manage-product-promotion.md) | Quản lý khuyến mãi theo sản phẩm | promotion | BR-004 | Nhân viên |
| [UC-29](promotion-context/UC-29-manage-order-promotion.md) | Quản lý khuyến mãi theo giá trị hóa đơn | promotion | BR-004 | Nhân viên |
| [UC-30](promotion-context/UC-30-manage-vouchers.md) | Quản lý voucher | promotion | BR-004 | Nhân viên |
| [UC-31](promotion-context/UC-31-calculate-order-discount.md) | Tính mức giảm cho đơn hàng | promotion | BR-004 | Hệ thống, Khách hàng (nhập voucher) |
| [UC-32](inventory-context/UC-32-manage-suppliers.md) | Quản lý nhà cung cấp | inventory | BR-005 | Nhân viên |
| [UC-33](inventory-context/UC-33-create-goods-receipt.md) | Lập phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-34](inventory-context/UC-34-confirm-goods-receipt.md) | Xác nhận phiếu nhập | inventory | BR-005 | Nhân viên |
| [UC-35](inventory-context/UC-35-restock-failed-delivery.md) | Tự cộng lại tồn kho khi giao không thành công | inventory | BR-005 | Hệ thống |
| [UC-36](shipping-context/UC-36-update-shipment-status.md) | Cập nhật trạng thái giao hàng (trang giả lập) | shipping | BR-006 | Trang giả lập vận chuyển |
| [UC-37](reporting-context/UC-37-view-dashboard.md) | Xem dashboard | reporting | BR-007 | Nhân viên |
| [UC-38](catalog-context/UC-38-manage-wishlist.md) | Quản lý danh sách yêu thích | catalog | BR-002 | Khách hàng |
| [UC-39](inventory-context/UC-39-view-stock.md) | Xem tồn kho | inventory | BR-005 | Nhân viên |
| [UC-40](shipping-context/UC-40-hand-over-to-shipping.md) | Bàn giao đơn cho vận chuyển | shipping | BR-006 | Nhân viên |

## Trạng thái đơn dùng chung (đã chốt 15/11/2026)

```
Chưa xử lý ──(UC-23 xác nhận)──► Đã xác nhận ──(UC-40 bàn giao)──► Đang giao ──(UC-36 "Đã giao")──► Giao thành công      (UC-26 tự xuất hóa đơn)
    │                                                                    └──(UC-36)──────────────► Giao không thành công (UC-35 tự cộng lại tồn kho)
    ├──► Đã hủy      (UC-22 khách hủy, UC-24 hệ thống tự hủy)
    └──► Bị từ chối  (UC-23 Nhân viên từ chối)
```
- Đơn QR có thêm trạng thái thanh toán: Chưa thanh toán → Đã thanh toán (UC-25).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử thay đổi (theo ERD).

## Quyết định đã chốt (15/11/2026)

| Chủ đề | Quyết định | UC |
|---|---|---|
| Trạng thái đơn | Bộ trạng thái như sơ đồ trên; Nhân viên bàn giao vận chuyển thì đơn sang "Đang giao" | UC-19 → UC-24, UC-36, UC-40 |
| Hủy / từ chối đơn | Cộng lại tồn kho và hoàn lượt voucher | UC-22, UC-23, UC-24, UC-31 |
| Phân quyền | Admin chỉ quản lý tài khoản và gán vai trò (Nhân viên ↔ Admin); Nhân viên vận hành cửa hàng; Admin không xem hóa đơn, dashboard | UC-02, UC-06, UC-07, UC-14, UC-23, UC-27, UC-37 |
| Đổi vai trò | Có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất | UC-07 |
| Tài khoản (ERD) | Account gồm email, SĐT (unique), mật khẩu, vai trò, trạng thái; không có username. Hồ sơ Customer / Employee / Admin gồm họ tên, ngày sinh, địa chỉ | UC-01, UC-02, UC-04, UC-06, UC-07 |
| Đăng ký / đăng nhập | Đăng ký nhập đủ email và SĐT; đăng nhập bằng một trong hai | UC-01, UC-02 |
| Trang danh mục | Lọc theo giới tính, size, danh mục, bộ sưu tập; sắp xếp mặc định mới nhất | UC-10 |
| Sản phẩm (ERD) | 1 danh mục, 1 giới tính, nhiều bộ sưu tập; ảnh (gallery) theo sản phẩm, có thứ tự; review để giai đoạn 2 | UC-12, UC-14, UC-17 |
| Giá bán | Chỉ đổi theo size; cùng size khác màu cùng giá | UC-12, UC-16 |
| Trang thông tin | Giới thiệu, chính sách, FAQ có nội dung cố định | UC-13 |
| Wishlist | Khách hàng thả tim lưu sản phẩm; mỗi sản phẩm 1 lần trong danh sách | UC-38 |
| Khuyến mãi | Giảm theo %, không có mức tối đa; mỗi đơn tối đa 1 khuyến mãi theo hóa đơn hoặc voucher; bằng nhau ưu tiên voucher | UC-28 → UC-31 |
| Số lượng khuyến mãi | Có số lượng được áp dụng và số đã dùng; khuyến mãi theo sản phẩm không giới hạn, hiệu lực đến khi Nhân viên kết thúc | UC-28, UC-29, UC-30 |
| Voucher (ERD) | Có giá trị đơn tối thiểu; chỉ giới hạn tổng lượt dùng | UC-30, UC-31 |
| Nhà cung cấp | Gồm tên, SĐT, email, địa chỉ | UC-32 |
| Tồn kho | Nhân viên xem được tồn kho theo biến thể | UC-39 |
| Trang giả lập | Không cần đăng nhập, mỗi loại 1 trang | UC-25, UC-36 |
| Hóa đơn (ERD) | Lưu snapshot thông tin đơn lúc xuất | UC-26 |
| Dashboard | Bỏ chỉ số hiệu quả khuyến mãi | UC-37 |
| Bảng size | Một bảng size chung, nội dung cố định | UC-12, UC-14 |
| Giá theo size | Giữ `variant_sell_price`; đặt giá cho size thì ghi cùng giá cho mọi màu của size đó | UC-16 |
| Từ chối đơn | Không nhập, không lưu lý do | UC-23 |
| Lịch sử thanh toán | Đổi trạng thái thanh toán không ghi vào lịch sử trạng thái đơn | UC-25, UC-26 |
| Sửa khuyến mãi | Khuyến mãi đã tạo không được sửa, chỉ ngừng; tạo có popup xác nhận | UC-28 → UC-31 |
| Tra cứu khuyến mãi | Không có tên; danh sách lọc theo khoảng thời gian — hiện khuyến mãi có thời gian hiệu lực giao với khoảng chọn (kể cả một phần); chưa kết thúc thì tính đến hiện tại | UC-28, UC-29, UC-30 |
| Nhà cung cấp | Có trạng thái Đang hợp tác / Ngừng hợp tác; chỉ chọn nhà cung cấp Đang hợp tác khi lập phiếu | UC-32, UC-33 |
| Phiếu nhập | Không lưu người / thời điểm xác nhận | UC-34 |
| Hàng hoàn | Chống cộng tồn hai lần bằng trạng thái đơn, không có cột đánh dấu | UC-35 |

## Data model

Xem [data_model_v1.md](../entity-model/data_model_v1.md) — bám sát ERD, chỉ thay đổi 6 điểm đã chốt.

## Tổng hợp giả định `[GD]`

Mỗi dòng là một giả định đang có trong mục *Notes* của UC, chờ developer xác nhận hoặc sửa. Ngoài ra: cách chia 7 bounded context ở trên cũng là `[GD]`.

| UC | Giả định |
|---|---|
| UC-01 | Ngày sinh và địa chỉ nhận hàng không bắt buộc khi đăng ký; khách bổ sung ở UC-04. |
| UC-01 | Tạo account và hồ sơ Customer trong cùng một transaction. |
| UC-01 | Mật khẩu tối thiểu 6 ký tự. |
| UC-01 | Đăng ký xong chuyển tới trang đăng nhập, không tự đăng nhập. |
| UC-01 | Người đã đăng nhập mở trang đăng ký thì bị chuyển về trang chủ. |
| UC-02 | Sau đăng nhập: Khách hàng về trang bán hàng; Nhân viên và Admin về khu vực quản trị. |
| UC-02 | Đăng nhập khi đang đặt hàng thì quay lại trang đang thao tác. |
| UC-02 | Sai thông tin đăng nhập báo chung, không chỉ rõ sai tài khoản hay mật khẩu. |
| UC-03 | Toàn bộ UC này là giả định: BR-001 chỉ nêu đăng ký và đăng nhập, không nêu đăng xuất. |
| UC-03 | Đăng xuất chỉ kết thúc phiên trên thiết bị hiện tại. |
| UC-03 | Sau đăng xuất chuyển về trang chủ. |
| UC-04 | Lưu hồ sơ Customer và account trong cùng một transaction. |
| UC-04 | Địa chỉ trong hồ sơ được điền sẵn khi đặt hàng. |
| UC-04 | Đổi email hoặc số điện thoại không cần xác minh lại. |
| UC-05 | Nhân viên và Admin cũng tự đổi được mật khẩu của mình. |
| UC-05 | Mật khẩu mới tối thiểu 6 ký tự và phải khác mật khẩu hiện tại. |
| UC-05 | Đổi mật khẩu không đăng xuất phiên hiện tại. |
| UC-06 | Tạo account và hồ sơ Employee/Admin trong cùng một transaction. |
| UC-06 | Admin đặt mật khẩu ban đầu cho tài khoản nội bộ; mật khẩu tối thiểu 6 ký tự. |
| UC-06 | Admin chỉ tạo tài khoản Nhân viên hoặc Admin; tài khoản Khách hàng chỉ tạo qua đăng ký (UC-01). |
| UC-06 | Hệ thống có sẵn 1 tài khoản Admin khi khởi tạo. |
| UC-07 | Việc xem và tìm danh sách tài khoản gộp vào UC này. |
| UC-07 | Danh sách có phân trang; tìm theo họ tên, email hoặc số điện thoại. |
| UC-07 | Admin sửa được thông tin mọi tài khoản. |
| UC-07 | Admin không tự đổi vai trò của chính mình. |
| UC-07 | Đổi vai trò Nhân viên ↔ Admin: tạo hồ sơ ở bảng của vai trò mới với cùng thông tin rồi xóa hồ sơ ở bảng cũ, cùng với đổi vai trò trên account, trong một transaction; lỗi thì hủy toàn bộ. |
| UC-08 | Khóa tài khoản kết thúc ngay mọi phiên đăng nhập đang mở của tài khoản đó. |
| UC-08 | Admin không tự khóa chính mình. |
| UC-08 | Khóa và mở khóa áp dụng cho mọi vai trò (Khách hàng, Nhân viên, Admin). |
| UC-08 | Khóa không xóa dữ liệu của tài khoản. |
| UC-09 | Trang chủ gồm khối hàng mới và khối sản phẩm theo bộ sưu tập. |
| UC-09 | Khối không có sản phẩm thì ẩn. |
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
| UC-18 | Giỏ của khách vãng lai lưu trên trình duyệt. |
| UC-18 | Khi đăng nhập, giỏ trình duyệt gộp vào giỏ tài khoản; dòng trùng cộng dồn nhưng không vượt tồn kho. |
| UC-18 | Giỏ hiển thị giá hiện tại, không giữ giá lúc thêm. |
| UC-18 | Dòng hết hàng/ngừng bán vẫn nằm trong giỏ nhưng không tính tiền và không đặt được. |
| UC-19 | Thông tin nhận hàng được điền sẵn từ hồ sơ khách, khách sửa được cho riêng đơn này. |
| UC-19 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn. |
| UC-19 | Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công. |
| UC-19 | Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại. |
| UC-20 | Nội dung chuyển khoản trong mã QR là mã đơn. |
| UC-20 | Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn; các dòng đã đặt được xóa khỏi giỏ. |
| UC-20 | Khách xem lại được mã QR trong chi tiết đơn khi còn chưa thanh toán và chưa quá hạn; ẩn QR khi đơn đã thanh toán, đã hủy hoặc quá hạn. |
| UC-21 | Danh sách đơn sắp xếp mới nhất trước, có phân trang. |
| UC-22 | Hủy đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt). |
| UC-23 | UC này gồm cả xem danh sách đơn, có phân trang và lọc theo trạng thái. |
| UC-23 | Không cho xác nhận đơn QR khi chưa thanh toán. |
| UC-23 | Từ chối đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt). |
| UC-24 | Tác vụ chạy mỗi 5 phút. |
| UC-24 | Tự hủy cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt). |
| UC-25 | Gửi trùng xác nhận cho đơn đã thanh toán là idempotent. |
| UC-26 | Đơn COD được ghi nhận "Đã thanh toán" khi giao thành công. |
| UC-26 | Lỗi tạo hóa đơn không làm thay đổi trạng thái giao của đơn; hệ thống thử lại. |
| UC-27 | Nhân viên có trang danh sách hóa đơn, mới nhất trước, phân trang, tìm theo mã đơn hoặc mã hóa đơn. |
| UC-28 | Một khuyến mãi áp dụng cho một hoặc nhiều sản phẩm. |
| UC-28 | Ngày kết thúc tự động không dùng cho loại này; ngày kết thúc được ghi khi Nhân viên kết thúc chương trình. |
| UC-28 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-28 | Danh sách khuyến mãi hiển thị trạng thái: sắp diễn ra, đang hiệu lực, đã kết thúc. |
| UC-29 | Được phép có nhiều khuyến mãi theo hóa đơn cùng hiệu lực; UC-31 chọn cái giảm nhiều nhất trong số đủ điều kiện. |
| UC-29 | Đơn bị hủy hoặc bị từ chối thì hoàn lượt khuyến mãi theo hóa đơn (giảm số lượng đã dùng 1). |
| UC-29 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100; số lượng được áp dụng ≥ 1. |
| UC-29 | Danh sách khuyến mãi hiển thị số lượng được áp dụng, số lượng đã dùng và trạng thái. |
| UC-30 | Mã voucher không phân biệt hoa thường. |
| UC-30 | Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100. |
| UC-30 | Danh sách voucher hiển thị tổng lượt dùng, số lượt đã dùng và trạng thái. |
| UC-31 | Có nhiều khuyến mãi theo hóa đơn đủ điều kiện thì lấy mức giảm lớn nhất. |
| UC-31 | Mức giảm theo hóa đơn hoặc voucher tính trên tạm tính (đã gồm khuyến mãi theo sản phẩm), không áp vào phí vận chuyển, và không vượt quá tạm tính. |
| UC-31 | Số tiền thay đổi giữa lúc xem và lúc xác nhận thì không tạo đơn, yêu cầu khách xác nhận lại. |
| UC-31 | Đơn bị hủy hoặc bị từ chối thì hoàn cả lượt khuyến mãi theo hóa đơn. |
| UC-32 | Tên nhà cung cấp là bắt buộc và không trùng. |
| UC-32 | Danh sách có phân trang và tìm theo tên. |
| UC-32 | Nhà cung cấp đã có phiếu nhập không xóa được, chỉ ngừng hợp tác; chưa có phiếu nhập thì xóa hẳn được. |
| UC-33 | Phiếu nhập có trạng thái: Nháp → Đã xác nhận | Đã hủy; chỉ sửa và hủy được khi còn "Nháp". |
| UC-33 | Mỗi biến thể chỉ xuất hiện một dòng trong một phiếu. |
| UC-33 | Danh sách phiếu nhập lọc được theo trạng thái và nhà cung cấp. |
| UC-35 | Cộng tồn chạy trong cùng transaction với cập nhật trạng thái đơn. |
| UC-35 | Biến thể hoặc sản phẩm đã ngừng bán vẫn được cộng lại tồn kho. |
| UC-35 | Khi lỗi, Trang giả lập vận chuyển nhận lỗi và có thể gửi lại. |
| UC-36 | Danh sách trên trang giả lập gồm: mã đơn, người nhận, số điện thoại, địa chỉ, người gửi, số tiền thu khi giao với đơn COD. |
| UC-37 | Kỳ báo cáo mặc định là tháng hiện tại, chọn được khoảng thời gian. |
| UC-37 | Doanh thu tính trên đơn "Giao thành công", tiền hàng sau giảm, không gồm phí vận chuyển. |
| UC-37 | Sản phẩm bán chạy: top 10 theo số lượng bán từ đơn "Giao thành công". |
| UC-37 | Tồn kho thấp: tồn kho ≤ ngưỡng. |
| UC-38 | UC thuộc catalog-context. |
| UC-38 | Nút tim có trên cả thẻ sản phẩm và trang chi tiết. |
| UC-38 | Khách vãng lai bấm tim thì được yêu cầu đăng nhập; sau đăng nhập quay lại trang đang xem, không tự lưu sản phẩm. |
| UC-38 | Danh sách yêu thích sắp xếp mới thêm nhất trước (theo thứ tự thêm; ERD không có cột thời gian riêng), có phân trang. |
| UC-38 | Sản phẩm ngừng bán vẫn ở danh sách, hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết. |
| UC-39 | Danh sách tồn kho có phân trang; mỗi dòng gồm tên sản phẩm, màu, size, số lượng tồn. |
| UC-39 | Tìm theo tên sản phẩm và lọc theo danh mục. |
| UC-39 | Biến thể có tồn ≤ ngưỡng tồn kho thấp được đánh dấu. |
| UC-39 | Giá vốn có hiển thị trên màn hình tồn kho hay không: chưa chốt, hiện chưa hiển thị. |
| UC-39 | Khách hàng và Admin không truy cập được màn hình tồn kho. |
| UC-40 | Có thể bàn giao nhiều đơn một lúc; đơn không hợp lệ thì bỏ qua và báo lại. |

## Câu hỏi mở (từ BR-TUAN1)

- Chung: phạm vi constraint cache danh sách (danh sách phía khách hay cả trang quản trị; dữ liệu được phép cũ bao lâu).
- Chung `[GD]`: cách gom In Scope thành 7 BR; Success Metric của từng BR suy ra từ metric tổng.
