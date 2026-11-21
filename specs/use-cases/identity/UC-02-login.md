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
7. Hệ thống chuyển người dùng theo vai trò `[GD]`: Khách hàng về trang bán hàng; Nhân viên và Admin về trang đầu của portal quản trị.

## Alternative Flows
- **1a. Đăng nhập khi đang đặt hàng:** khách bị yêu cầu đăng nhập từ bước đặt hàng; sau khi đăng nhập thành công hệ thống đưa khách quay lại trang đang thao tác `[GD]`.
- **1b. Bấm "Quên mật khẩu":** trang đăng nhập storefront có nút "Quên mật khẩu" nhưng ở giai đoạn 1 bấm vào không có hành động nào; chức năng làm ở giai đoạn 2. Portal quản trị không có nút này `[GD]`.
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
Given: khách vãng lai bấm đặt hàng và bị chuyển tới trang đăng nhập
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

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản, UC-08 Khóa và mở khóa tài khoản
- **Downstream UC:** UC-03 Đăng xuất, UC-04, UC-05, UC-18 Quản lý giỏ hàng, UC-19, UC-20 (đặt hàng cần đăng nhập)
- **External Systems:** Redis (bộ đếm rate limit)

## Notes
- Quên mật khẩu làm ở giai đoạn 2; giai đoạn 1 chỉ có nút trên storefront, chưa có hành động (BR-GIAIDOAN1, đã chốt 21/11/2026).
- Cơ chế phiên, thời hạn và rate limit theo BR-GIAIDOAN1, Constraints chung — Xác thực; bảng `identity.session` theo data model v2.15 (Q35).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Email và số điện thoại dùng để đăng nhập nằm trên account (unique); không có username riêng. Vai trò và trạng thái cũng nằm trên account (theo ERD, đã chốt 15/11/2026).
- Phiên đăng nhập phía server lưu ở `identity.session`, cookie `HttpOnly`, `Secure`, `SameSite=Lax`; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ; không dùng JWT (đã chốt 21/11/2026, thay quyết định access / refresh token cùng ngày).
- Storefront chỉ cho Khách hàng đăng nhập; tài khoản Nhân viên / Admin đăng nhập ở storefront bị báo "Thông tin đăng nhập không đúng". Nhân viên và Admin dùng portal quản trị riêng (đã chốt 21/11/2026).
- Rate limit theo IP: đăng nhập 5 lần/phút (đã chốt 21/11/2026).
- Hạn phiên tính từ lần thao tác cuối (mỗi request hợp lệ gia hạn phiên), không tính từ lúc đăng nhập (đã chốt 21/11/2026).

### Giả định [GD]
- Sau đăng nhập: Khách hàng về trang bán hàng; Nhân viên và Admin về trang đầu của portal quản trị.
- Đăng nhập khi đang đặt hàng thì quay lại trang đang thao tác.
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
