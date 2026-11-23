# UC-02: Đăng nhập

## Metadata
- **ID:** UC-02
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách hàng, Nhân viên, Admin

## Trigger
Người dùng bấm "Đăng nhập", hoặc bị yêu cầu đăng nhập khi thực hiện thao tác cần tài khoản (ví dụ đặt hàng).

## Preconditions
- Người dùng chưa đăng nhập.
- Tài khoản đã tồn tại (UC-01 hoặc UC-06).

## Main Flow
1. Người dùng mở trang đăng nhập: Khách hàng ở storefront, Nhân viên và Admin ở portal quản trị riêng.
2. Người dùng nhập email hoặc số điện thoại, và mật khẩu.
3. Hệ thống tìm account theo email hoặc số điện thoại (lưu trên account) và kiểm tra mật khẩu.
4. Hệ thống kiểm tra vai trò của tài khoản thuộc cổng đang đăng nhập: storefront chỉ nhận Khách hàng; portal chỉ nhận Nhân viên và Admin.
5. Hệ thống kiểm tra tài khoản đang ở trạng thái Hoạt động.
6. Hệ thống tạo phiên đăng nhập (một dòng `identity.session`; hạn 30 phút với Khách hàng, 1 giờ với Nhân viên / Admin, tính từ lần thao tác cuối) và gửi mã phiên trong cookie `HttpOnly`, `Secure`, `SameSite=Lax` của cổng đang đăng nhập.
7. Sau khi xác thực đúng vai trò/cổng và tạo phiên thành công, Khách hàng đăng nhập storefront từ checkout hoặc nút tim trên trang chi tiết được quay lại theo `return_url` nội bộ hợp lệ (1a, 1c). Nếu thiếu hoặc không hợp lệ, bỏ qua `return_url` và áp dụng chuyển hướng mặc định theo vai trò `[GD]`: Khách hàng về trang bán hàng; Nhân viên và Admin về trang đầu của portal quản trị. `return_url` không thay thế kiểm tra vai trò/cổng ở bước 4.

## Alternative Flows
- **1a. Đăng nhập khi đang đặt hàng:** khách bị yêu cầu đăng nhập từ checkout; hệ thống giữ đích quay lại qua `return_url` trong quá trình đăng nhập, kiểm tra lại đích ở server trước khi chuyển hướng. Sau khi Khách hàng đăng nhập storefront thành công, hệ thống đưa khách quay lại checkout theo đích nội bộ hợp lệ.
- **1b. Bấm "Quên mật khẩu":** trang đăng nhập storefront có nút "Quên mật khẩu" nhưng ở giai đoạn 1 bấm vào không có hành động nào; chức năng làm ở giai đoạn 2. Portal quản trị không có nút này `[GD]`.
- **1c. Đăng nhập từ nút tim trên trang chi tiết (UC-12):** khách vãng lai bấm tim được chuyển tới đăng nhập storefront kèm `return_url` trỏ về trang chi tiết đang xem. Sau khi đăng nhập đúng cổng thành công, hệ thống kiểm tra lại đích nội bộ hợp lệ rồi quay lại đúng trang đó; không tự thích hoặc bỏ thích. Nút tim phản ánh wishlist hiện có của tài khoản theo UC-12/UC-38; khách chủ động bấm tim sau khi quay lại nếu muốn thay đổi.
- **1d. Đích quay lại không hợp lệ hoặc không đúng phạm vi:** bỏ qua `return_url` và dùng chuyển hướng mặc định ở bước 7, không chuyển tới đích bị từ chối. Chỉ chấp nhận đường dẫn nội bộ đã chuẩn hóa thuộc checkout hoặc trang chi tiết storefront, không có scheme/host và bắt đầu bằng đúng một dấu `/`. Từ chối URL tuyệt đối, dạng `//`, dấu gạch chéo ngược, ký tự điều khiển, đường dẫn khác phạm vi và các biến thể mã hóa dẫn tới đích bị cấm. Chỉ kiểm tra tiền tố `/` là không đủ. Đăng nhập portal quản trị không sử dụng `return_url` của storefront.
- **6a. Gia hạn phiên:** mỗi request có phiên còn hạn thì hệ thống lùi thời điểm hết hạn thêm 30 phút (Khách hàng) hoặc 1 giờ (Nhân viên / Admin) tính từ lúc đó.
- **6b. Phiên hết hạn:** người dùng không thao tác quá hạn phiên; request tiếp theo coi như chưa đăng nhập, trang cần đăng nhập chuyển người dùng tới trang đăng nhập của cổng tương ứng.

## Exceptions
- **E1. Sai thông tin đăng nhập:** không tìm thấy tài khoản hoặc sai mật khẩu — hệ thống báo chung "Thông tin đăng nhập không đúng", không cho biết sai trường nào `[GD]`.
- **E2. Tài khoản bị khóa:** hệ thống báo "Tài khoản đã bị khóa", không tạo phiên.
- **E3. Thiếu dữ liệu:** bỏ trống email/số điện thoại hoặc mật khẩu — hệ thống báo lỗi tại trường tương ứng.
- **E4. Sai cổng đăng nhập:** tài khoản Nhân viên / Admin đăng nhập ở storefront, hoặc tài khoản Khách hàng đăng nhập ở portal `[GD]` — hệ thống báo "Thông tin đăng nhập không đúng" như E1, không tạo phiên.
- **E5. Vượt giới hạn tần suất:** quá 5 lần đăng nhập trong 1 phút từ cùng một IP — hệ thống từ chối (HTTP 429 `[GD]`), không kiểm tra mật khẩu.

## Postconditions
- Người dùng có phiên đăng nhập hợp lệ ở cổng đã đăng nhập; chỉ truy cập được chức năng của vai trò hiện tại của tài khoản.

## Acceptance Criteria

### AC-1: Đăng nhập bằng email
Given: tài khoản Khách hàng trạng thái Hoạt động với email "a@example.com"
When: người dùng nhập "a@example.com" và đúng mật khẩu ở storefront
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng
And: người dùng được chuyển về trang bán hàng

### AC-2: Đăng nhập bằng số điện thoại
Given: tài khoản Khách hàng trạng thái Hoạt động với số điện thoại "0901234567"
When: người dùng nhập "0901234567" và đúng mật khẩu ở storefront
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng

### AC-3: Tài khoản nội bộ đăng nhập ở portal quản trị
Given: tài khoản Nhân viên (hoặc Admin) trạng thái Hoạt động
When: người dùng đăng nhập đúng thông tin ở portal quản trị
Then: hệ thống tạo phiên đăng nhập với đúng vai trò
And: người dùng được chuyển vào portal quản trị

### AC-4: Sai mật khẩu
Given: tài khoản với email "a@example.com" tồn tại
When: người dùng nhập "a@example.com" và sai mật khẩu
Then: hệ thống báo "Thông tin đăng nhập không đúng"
And: không có phiên đăng nhập nào được tạo

### AC-5: Tài khoản không tồn tại
Given: không có tài khoản nào dùng email "x@example.com"
When: người dùng đăng nhập bằng "x@example.com"
Then: hệ thống báo "Thông tin đăng nhập không đúng"

### AC-6: Tài khoản bị khóa
Given: tài khoản ở trạng thái Bị khóa
When: người dùng đăng nhập đúng email và mật khẩu
Then: hệ thống báo "Tài khoản đã bị khóa"
And: không có phiên đăng nhập nào được tạo

### AC-7: Quay lại trang đặt hàng sau đăng nhập
Given: khách vãng lai bấm đặt hàng và bị chuyển tới trang đăng nhập storefront với return_url nội bộ hợp lệ trỏ về checkout
When: khách đăng nhập thành công
Then: khách được đưa quay lại bước đặt hàng

### AC-8: Tài khoản nội bộ đăng nhập ở storefront
Given: tài khoản Nhân viên "nv1@example.com" trạng thái Hoạt động
When: người dùng nhập "nv1@example.com" và đúng mật khẩu ở trang đăng nhập storefront
Then: hệ thống báo "Thông tin đăng nhập không đúng"
And: không có phiên đăng nhập nào được tạo

### AC-9: Tài khoản Khách hàng đăng nhập ở portal `[GD]`
Given: tài khoản Khách hàng "a@example.com" trạng thái Hoạt động
When: người dùng nhập "a@example.com" và đúng mật khẩu ở portal quản trị
Then: hệ thống báo "Thông tin đăng nhập không đúng"
And: không có phiên đăng nhập nào được tạo

### AC-10: Nút quên mật khẩu chưa có hành động
Given: Khách vãng lai ở trang đăng nhập storefront
When: khách bấm "Quên mật khẩu"
Then: không có hành động nào xảy ra, khách vẫn ở trang đăng nhập

### AC-11: Phiên Khách hàng hết hạn sau 30 phút không thao tác
Given: Khách hàng đã đăng nhập và không gửi request nào trong hơn 30 phút
When: khách mở trang hồ sơ khách hàng
Then: hệ thống coi như chưa đăng nhập và chuyển khách tới trang đăng nhập storefront

### AC-12: Phiên được gia hạn khi còn thao tác
Given: Nhân viên đăng nhập portal lúc 08:00 và thao tác lần cuối lúc 08:50
When: Nhân viên mở một trang quản trị lúc 09:30
Then: phiên vẫn hợp lệ (hết hạn lúc 09:50, tính từ lần thao tác 08:50)
And: hạn mới của phiên là 10:30

### AC-13: Vượt giới hạn đăng nhập
Given: cùng một IP đã gửi 5 yêu cầu đăng nhập trong 1 phút
When: IP đó gửi yêu cầu đăng nhập thứ 6 trong phút đó
Then: hệ thống từ chối yêu cầu, không kiểm tra mật khẩu

### AC-14: Quay lại trang chi tiết từ nút tim, không tự thay đổi wishlist
Given: khách vãng lai đang xem sản phẩm A tại UC-12, bấm tim và được chuyển tới đăng nhập storefront với return_url nội bộ hợp lệ của trang chi tiết A
When: khách đăng nhập thành công bằng tài khoản Khách hàng đang Hoạt động
Then: hệ thống tạo phiên đúng cổng và chuyển khách về đúng trang chi tiết A
And: riêng việc đăng nhập không tạo hoặc xóa wishlist_item; trạng thái tim được tải theo wishlist hiện có, khách chủ động bấm tim nếu muốn thay đổi

### AC-15: Bỏ qua đích quay lại không an toàn hoặc ngoài phạm vi
Given: Khách hàng gửi đăng nhập storefront kèm return_url là URL ngoài như https://example.org, //example.org, dạng mã hóa /%2fexample.org hoặc /%5cexample.org, hoặc đường dẫn nội bộ không thuộc checkout/trang chi tiết
When: khách đăng nhập đúng thông tin và server kiểm tra đích sau chuẩn hóa nhất quán với định tuyến
Then: đăng nhập vẫn thành công nhưng return_url bị bỏ qua, không chuyển tới đích bị cấm
And: hệ thống dùng chuyển hướng mặc định ở bước 7; không thực hiện hành động wishlist từ tham số quay lại

### AC-16: Tham số quay lại không vượt ranh giới cổng đăng nhập
Given: tài khoản Nhân viên đang Hoạt động gửi đăng nhập kèm return_url trỏ tới trang chi tiết storefront
When: người dùng đăng nhập đúng thông tin tại portal quản trị
Then: hệ thống tạo phiên portal, bỏ qua return_url storefront và dùng đích mặc định của portal theo bước 7
When: tài khoản Nhân viên dùng cùng thông tin và return_url tại trang đăng nhập storefront
Then: hệ thống từ chối theo E4, không tạo phiên; return_url hợp lệ không cho phép vượt kiểm tra vai trò/cổng

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản, UC-08 Khóa và mở khóa tài khoản
- **Downstream UC:** UC-03 Đăng xuất, UC-04, UC-05, UC-12 Xem chi tiết sản phẩm, UC-18 Quản lý giỏ hàng, UC-19, UC-20 (đặt hàng cần đăng nhập), UC-38 Quản lý danh sách yêu thích
- **External Systems:** Redis (bộ đếm rate limit)

## Notes
- Quên mật khẩu làm ở giai đoạn 2; giai đoạn 1 chỉ có nút trên storefront, chưa có hành động (BR-GIAIDOAN1, đã chốt 21/11/2026).
- Cơ chế phiên, thời hạn và rate limit theo BR-GIAIDOAN1, Constraints chung — Xác thực; bảng `identity.session` theo data model v2.15 (Q35).
- Hợp đồng quay lại sau đăng nhập chỉ chốt cho checkout và trang chi tiết từ thao tác tim. Server kiểm tra `return_url` trước khi dùng, không tin giá trị giữ trên form/query; áp dụng danh sách loại route được phép sau chuẩn hóa, không mở chuyển hướng tùy ý trong hoặc ngoài website. Tài nguyên đích được render theo UC tương ứng, không được dùng `return_url` để bỏ qua phân quyền hoặc tự thực hiện hành động ghi.

### Quyết định đã chốt
- Khách hàng đăng nhập storefront từ checkout hoặc nút tim trên trang chi tiết được quay lại theo return_url nội bộ hợp lệ; đích không an toàn/khác phạm vi bị bỏ qua, giữ phân quyền theo cổng và nhánh mặc định hiện có. Đăng nhập không tự thích/bỏ thích (UC-12-Q8, developer yêu cầu đồng bộ tại Codex 23/11/2026).
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Email và số điện thoại dùng để đăng nhập nằm trên account (unique); không có username riêng. Vai trò và trạng thái cũng nằm trên account (theo ERD, đã chốt 15/11/2026).
- Phiên đăng nhập phía server lưu ở `identity.session`, cookie `HttpOnly`, `Secure`, `SameSite=Lax`; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ; không dùng JWT (đã chốt 21/11/2026, thay quyết định access / refresh token cùng ngày).
- Storefront chỉ cho Khách hàng đăng nhập; tài khoản Nhân viên / Admin đăng nhập ở storefront bị báo "Thông tin đăng nhập không đúng". Nhân viên và Admin dùng portal quản trị riêng (đã chốt 21/11/2026).
- Rate limit theo IP: đăng nhập 5 lần/phút (đã chốt 21/11/2026).
- Hạn phiên tính từ lần thao tác cuối (mỗi request hợp lệ gia hạn phiên), không tính từ lúc đăng nhập (đã chốt 21/11/2026).

### Giả định [GD]
- Sau đăng nhập: Khách hàng về trang bán hàng; Nhân viên và Admin về trang đầu của portal quản trị.
- Sai thông tin đăng nhập báo chung, không chỉ rõ sai tài khoản hay mật khẩu.
- Portal quản trị từ chối tài khoản Khách hàng với cùng thông báo "Thông tin đăng nhập không đúng".
- Portal quản trị không có nút "Quên mật khẩu".
- Vượt rate limit trả HTTP 429.
- Storefront và portal quản trị dùng 2 cookie phiên khác tên; một trình duyệt có thể đăng nhập cùng lúc vào cả hai cổng.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): theo ERD — đăng nhập bằng email hoặc số điện thoại trên account, không có username
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — UC-06 đổi tên thành "Admin tạo tài khoản"
- v5 (2026-11-21): theo BR-GIAIDOAN1 v20 — cấp access token / refresh token thay cho "phiên đăng nhập"; storefront và portal quản trị đăng nhập riêng (bước 1, 4, E4, AC-8, AC-9); nút "Quên mật khẩu" chưa có hành động (1b, AC-10); làm mới token (6a, AC-11, AC-12); rate limit đăng nhập (E5, AC-13)
- v6 (2026-11-21): theo BR-GIAIDOAN1 v21 — website SSR nên dùng phiên phía server (`identity.session`) thay access / refresh token; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ (bước 6, 6a, 6b, AC-11, AC-12); bỏ rate limit làm mới token
- v7 (2026-11-23): theo yêu cầu đồng bộ tại Codex, chốt return_url nội bộ an toàn cho checkout và trang chi tiết từ wishlist, bảo toàn cổng/vai trò và không tự thay đổi wishlist; cập nhật bước 7, 1a, thêm 1c/1d, AC-14..16, chốt giả định quay lại checkout. Giữ draft và các giả định khác.
