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
6. Hệ thống tạo phiên đăng nhập (một dòng `identity.session`; hạn 30 phút với Khách hàng, 1 giờ với Nhân viên / Admin, tính từ lần thao tác cuối) và gửi mã phiên trong cookie `HttpOnly`, `Secure`, `SameSite=Lax` của cổng đang đăng nhập. Hai cổng dùng cookie phiên khác tên để một trình duyệt có thể đăng nhập đồng thời vào cả hai cổng.
7. Nếu khách bắt đầu đăng nhập từ bước đặt hàng, hệ thống chuyển khách về trang thanh toán theo 1a. Khi người dùng mở trang đăng nhập trực tiếp, Khách hàng được chuyển đến trang chủ storefront, Nhân viên được chuyển đến tab Tổng quan Nhân viên và Admin được chuyển đến tab Tổng quan Admin.

## Alternative Flows
- **1a. Đăng nhập khi đang đặt hàng:** khách bị yêu cầu đăng nhập từ bước đặt hàng. Sau khi đăng nhập thành công bằng mật khẩu Sobie hoặc Google, khách quay lại trang thanh toán với giỏ đã gộp theo UC-19 và UC-20.
- **1b. Bấm "Quên mật khẩu":** trong giai đoạn 1, storefront hiển thị nút "Quên mật khẩu" và giữ khách ở trang đăng nhập khi bấm nút. Chức năng khôi phục mật khẩu làm ở giai đoạn 2. Portal quản trị không hiển thị nút này trong giai đoạn 1.
- **1c. Đăng nhập với Google (storefront):** Khách chọn “Đăng nhập với Google” và xác thực với Google qua OpenID Connect (OAuth 2.0), hoặc tiếp tục từ E1 của UC-01 với kết quả xác thực Google vừa nhận. Sobie kiểm tra phản hồi và tìm tài khoản hiện có theo định danh Google (`sub`). Nếu đã có liên kết, chuyển thẳng đến bước 4. Nếu chưa có liên kết nhưng email đã xác minh trùng với tài khoản Sobie hiện có, chuyển đến 1d. Các trường hợp khác xử lý theo E6. Khách không phải nhập hoặc tạo mật khẩu Sobie.
- **1d. Dùng Google lần đầu với tài khoản Sobie hiện có:** Sobie gửi OTP đến email đang lưu trên tài khoản Sobie có email trùng. Khách nhập mã và Sobie kiểm tra mã hợp lệ cho lượt liên kết này. Sau khi xác minh OTP thành công và kiểm tra vai trò, trạng thái theo bước 4 và 5, Sobie lưu liên kết Google vào tài khoản hiện có rồi tiếp tục bước 6 để cấp phiên. Nếu xác minh OTP thất bại, xử lý theo E6.
- **6a. Gia hạn phiên:** mỗi request có phiên còn hạn thì hệ thống lùi thời điểm hết hạn thêm 30 phút (Khách hàng) hoặc 1 giờ (Nhân viên / Admin) tính từ lúc đó.
- **6b. Phiên hết hạn:** người dùng không thao tác quá hạn phiên; request tiếp theo coi như chưa đăng nhập, trang cần đăng nhập chuyển người dùng tới trang đăng nhập của cổng tương ứng.

## Exceptions
- **E1. Sai thông tin đăng nhập:** nếu không tìm thấy tài khoản, mật khẩu sai hoặc tài khoản chỉ dùng Google được nhập vào biểu mẫu mật khẩu, hệ thống báo chung "Thông tin đăng nhập không đúng" và không tạo phiên.
- **E2. Tài khoản bị khóa:** hệ thống báo "Tài khoản đã bị khóa", không tạo phiên.
- **E3. Thiếu dữ liệu trong luồng dùng mật khẩu:** bỏ trống email/số điện thoại hoặc mật khẩu — hệ thống báo lỗi tại trường tương ứng.
- **E4. Sai cổng đăng nhập:** nếu tài khoản Nhân viên / Admin đăng nhập ở storefront hoặc tài khoản Khách hàng đăng nhập ở portal, hệ thống chỉ báo "Thông tin đăng nhập không đúng" và không tạo phiên.
- **E5. Vượt giới hạn tần suất đăng nhập bằng mật khẩu:** khi cùng một IP gửi quá 5 yêu cầu đăng nhập bằng mật khẩu trong 1 phút, hệ thống từ chối yêu cầu vượt ngưỡng với HTTP 429 trước khi kiểm tra mật khẩu. Đăng nhập Google không tính vào và không chịu giới hạn của bộ đếm này.
- **E6. Đăng nhập Google không thành công:** nếu khách hủy, phản hồi xác thực không hợp lệ, Sobie không tìm thấy tài khoản hiện có hoặc OTP liên kết không hợp lệ, hệ thống không tạo phiên hoặc liên kết mới. Việc đăng ký tài khoản mới thực hiện theo UC-01.

## Postconditions
- Người dùng có phiên đăng nhập hợp lệ ở cổng đã đăng nhập; chỉ truy cập được chức năng của vai trò hiện tại của tài khoản.

## Acceptance Criteria

### AC-1: Đăng nhập bằng email
Given: Khách hàng có tài khoản Hoạt động với email "a@example.com" và mở trực tiếp trang đăng nhập storefront
When: người dùng nhập "a@example.com" và đúng mật khẩu ở storefront
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng
And: người dùng được chuyển về trang chủ storefront

### AC-2: Đăng nhập bằng số điện thoại
Given: tài khoản Khách hàng trạng thái Hoạt động với số điện thoại "0901234567"
When: người dùng nhập "0901234567" và đúng mật khẩu ở storefront
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng

### AC-3: Tài khoản nội bộ đăng nhập ở portal quản trị
Given: Nhân viên hoặc Admin có tài khoản Hoạt động và mở trực tiếp trang đăng nhập portal quản trị
When: người dùng đăng nhập đúng thông tin ở portal quản trị
Then: hệ thống tạo phiên đăng nhập với đúng vai trò
And: người dùng được chuyển đến tab Tổng quan tương ứng với vai trò trong portal quản trị

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
When: khách đăng nhập thành công bằng mật khẩu Sobie hoặc Google
Then: khách quay lại trang thanh toán với giỏ đã gộp theo UC-19 và UC-20

### AC-8: Tài khoản nội bộ đăng nhập ở storefront
Given: tài khoản Nhân viên "nv1@example.com" trạng thái Hoạt động
When: người dùng nhập "nv1@example.com" và đúng mật khẩu ở trang đăng nhập storefront
Then: hệ thống báo "Thông tin đăng nhập không đúng"
And: không có phiên đăng nhập nào được tạo

### AC-9: Tài khoản Khách hàng đăng nhập ở portal
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

### AC-13: Vượt giới hạn đăng nhập bằng mật khẩu
Given: cùng một IP đã gửi 5 yêu cầu đăng nhập bằng mật khẩu trong 1 phút
When: IP đó gửi yêu cầu đăng nhập bằng mật khẩu thứ 6 trong phút đó
Then: hệ thống trả HTTP 429 và không kiểm tra mật khẩu

### AC-14: Khách hàng đăng nhập bằng Google mà không cần mật khẩu Sobie
Given: tài khoản Khách hàng đang Hoạt động, đã liên kết với Google và không có mật khẩu Sobie
When: khách chọn “Đăng nhập với Google” ở storefront và Sobie xác thực được phản hồi có định danh Google đúng với liên kết
Then: hệ thống tạo phiên storefront cho tài khoản Khách hàng
And: khách không phải nhập hoặc tạo mật khẩu Sobie
And: Sobie không gửi OTP liên kết cho tài khoản đã liên kết Google

### AC-15: Tài khoản đã liên kết Google bị khóa
Given: tài khoản Khách hàng đã liên kết với Google và đang Bị khóa
When: Sobie xác thực thành công phản hồi Google của khách ở storefront
Then: hệ thống báo "Tài khoản đã bị khóa" và không tạo phiên

### AC-16: Đăng nhập Google không thành công
Given: khách đã chọn “Đăng nhập với Google” ở storefront
When: khách hủy, Sobie không xác thực được phản hồi Google, không tìm thấy tài khoản hiện có hoặc không xác minh được quyền truy cập khi liên kết lần đầu
Then: hệ thống không tạo phiên đăng nhập hoặc liên kết Google mới

### AC-17: Đăng nhập Google lần đầu vào tài khoản Sobie hiện có
Given: tài khoản Khách hàng đang Hoạt động có email trùng với email đã xác minh từ Google và chưa có liên kết với định danh Google này
When: Sobie xác thực phản hồi Google, gửi OTP đến email đang lưu trên tài khoản Sobie và khách nhập đúng mã còn hiệu lực cho lượt liên kết đó
Then: hệ thống liên kết định danh Google với tài khoản hiện có và cấp phiên storefront cho tài khoản đó
And: khách không phải tạo hoặc nhập mật khẩu Sobie, và hệ thống không tạo tài khoản mới

### AC-18: Tài khoản chỉ dùng Google gửi biểu mẫu mật khẩu
Given: tài khoản Khách hàng chỉ liên kết Google và chưa có mật khẩu Sobie
When: khách gửi email của tài khoản đó cùng một mật khẩu qua biểu mẫu đăng nhập
Then: hệ thống báo "Thông tin đăng nhập không đúng" và không tạo phiên

### AC-19: Đăng nhập Google khi bộ đếm mật khẩu đã đạt giới hạn
Given: một IP đã đạt giới hạn đăng nhập bằng mật khẩu và khách có tài khoản Hoạt động đã liên kết Google
When: khách từ IP đó xác thực thành công qua Google trên storefront
Then: hệ thống tạo phiên storefront cho khách và không tăng bộ đếm đăng nhập bằng mật khẩu

### AC-20: Đăng nhập hai cổng trên cùng trình duyệt
Given: một trình duyệt đã có phiên Khách hàng hợp lệ tại storefront
When: Nhân viên hoặc Admin đăng nhập thành công vào portal trên cùng trình duyệt
Then: portal có phiên riêng và storefront vẫn truy cập được bằng phiên Khách hàng hiện tại

### AC-21: OTP liên kết Google không hợp lệ
Given: Sobie đã gửi OTP đến email của tài khoản hiện có để xác minh lần liên kết Google đầu tiên
When: khách nhập mã sai, mã hết hạn hoặc mã của lượt khác
Then: hệ thống báo lỗi xác minh và không lưu liên kết Google hoặc cấp phiên

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản, UC-08 Khóa và mở khóa tài khoản
- **Downstream UC:** UC-03 Đăng xuất, UC-04, UC-05, UC-18 Quản lý giỏ hàng, UC-19, UC-20 (đặt hàng cần đăng nhập)
- **External Systems:** Redis (bộ đếm rate limit), Google (OpenID Connect), dịch vụ gửi email OTP.

## Notes
- Quên mật khẩu làm ở giai đoạn 2; giai đoạn 1 chỉ có nút trên storefront, chưa có hành động (BR-GIAIDOAN1, đã chốt 21/11/2026).
- Cơ chế phiên, thời hạn và rate limit theo BR-GIAIDOAN1, Constraints chung — Xác thực; bảng `identity.session` theo data model v2.15 (Q35).

### Quyết định đã chốt
- Khi đã có phiên portal hợp lệ, mở lại trang đăng nhập đưa người dùng về tab Tổng quan của vai trò hiện tại. Tab Tổng quan Admin phục vụ quản trị tài khoản. Dashboard báo cáo UC-37 thuộc quyền Nhân viên.
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Email và số điện thoại dùng để đăng nhập nằm trên account (unique); không có username riêng. Vai trò và trạng thái cũng nằm trên account (theo ERD, đã chốt 15/11/2026).
- Khách hàng có liên kết Google đăng nhập ở storefront bằng định danh Google đã liên kết, không cần nhập hoặc tạo mật khẩu Sobie (đã chốt 23/11/2026).
- Khi khách dùng Google lần đầu để đăng nhập vào tài khoản Sobie có email trùng, Sobie xác minh OTP qua email đã lưu rồi liên kết. Các lần đăng nhập sau sử dụng liên kết Google hiện có (đã chốt 23/11/2026).
- Phiên đăng nhập phía server lưu ở `identity.session`, cookie `HttpOnly`, `Secure`, `SameSite=Lax`; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ; không dùng JWT (đã chốt 21/11/2026, thay quyết định access / refresh token cùng ngày).
- Storefront chỉ cho Khách hàng đăng nhập; tài khoản Nhân viên / Admin đăng nhập ở storefront bị báo "Thông tin đăng nhập không đúng". Nhân viên và Admin dùng portal quản trị riêng (đã chốt 21/11/2026).
- Rate limit theo IP là 5 lần/phút cho đăng nhập bằng mật khẩu. Yêu cầu vượt ngưỡng nhận HTTP 429. Google không tính vào bộ đếm này (đã chốt phạm vi và mã phản hồi 23/11/2026).
- Hạn phiên tính từ lần thao tác cuối (mỗi request hợp lệ gia hạn phiên), không tính từ lúc đăng nhập (đã chốt 21/11/2026).
- Đích chuyển trang sau đăng nhập, thông báo chung khi sai thông tin hoặc sai cổng, việc ẩn nút "Quên mật khẩu" tại portal trong giai đoạn 1, và cookie phiên riêng cho từng cổng được áp dụng theo các luồng trên (đã chốt 23/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): theo ERD — đăng nhập bằng email hoặc số điện thoại trên account, không có username
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — UC-06 đổi tên thành "Admin tạo tài khoản"
- v5 (2026-11-21): theo BR-GIAIDOAN1 v20 — cấp access token / refresh token thay cho "phiên đăng nhập"; storefront và portal quản trị đăng nhập riêng (bước 1, 4, E4, AC-8, AC-9); nút "Quên mật khẩu" chưa có hành động (1b, AC-10); làm mới token (6a, AC-11, AC-12); rate limit đăng nhập (E5, AC-13)
- v6 (2026-11-21): theo BR-GIAIDOAN1 v21 — website SSR nên dùng phiên phía server (`identity.session`) thay access / refresh token; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ (bước 6, 6a, 6b, AC-11, AC-12); bỏ rate limit làm mới token
- v7 (2026-11-23): bổ sung đăng nhập với Google cho Khách hàng ở storefront mà không cần mật khẩu Sobie.
- v8 (2026-11-23): bổ sung đăng nhập Google lần đầu vào tài khoản Sobie hiện có và đồng bộ E1 của UC-01.
- v9 (2026-11-23): chốt chuyển trang, thông báo lỗi, nút quên mật khẩu ở portal, phiên riêng từng cổng và HTTP 429 cho đăng nhập bằng mật khẩu. Google không tính vào bộ đếm mật khẩu.
- v10 (2026-11-23): chốt gửi OTP đến email đã lưu trên tài khoản Sobie trong lần liên kết Google đầu tiên.
