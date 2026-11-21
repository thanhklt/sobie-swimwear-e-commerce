# UC-01: Đăng ký tài khoản

## Metadata
- **ID:** UC-01
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách vãng lai

## Trigger
Khách vãng lai bấm "Đăng ký" trên website.

## Preconditions
- Khách vãng lai chưa đăng nhập.

## Main Flow
1. Khách vãng lai mở trang đăng ký.
2. Khách vãng lai nhập họ tên, email, số điện thoại, mật khẩu và nhập lại mật khẩu. Ngày sinh và địa chỉ nhận hàng không bắt buộc khi đăng ký, bổ sung sau ở UC-04 `[GD]`.
3. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại chưa được dùng cho tài khoản nào.
4. Trong cùng một transaction `[GD]`, hệ thống cấp mã tài khoản `KH-<YYYYMMDD ngày đăng ký>-<4 số>` và tạo account gồm email, số điện thoại, mật khẩu đã hash, vai trò Khách hàng, trạng thái Hoạt động, họ tên (ngày sinh, địa chỉ để trống nếu chưa nhập), đồng thời tạo giỏ hàng và danh sách yêu thích trống cho tài khoản (đã chốt 21/11/2026).
5. Hệ thống thông báo đăng ký thành công và chuyển tới trang đăng nhập `[GD]`.

## Alternative Flows
- **1a. Đang đăng nhập:** người dùng đã đăng nhập mở trang đăng ký thì hệ thống chuyển về trang chủ, không cho đăng ký thêm tài khoản `[GD]`.

## Exceptions
- **E1. Email đã được dùng:** hệ thống báo "Email đã được sử dụng", không tạo tài khoản.
- **E2. Số điện thoại đã được dùng:** hệ thống báo "Số điện thoại đã được sử dụng", không tạo tài khoản.
- **E3. Dữ liệu không hợp lệ:** thiếu trường bắt buộc, email hoặc số điện thoại sai định dạng, mật khẩu ngắn hơn 6 ký tự `[GD]`, hoặc nhập lại mật khẩu không khớp — hệ thống báo lỗi tại từng trường, không tạo tài khoản.

## Postconditions
- Có một account mới vai trò Khách hàng, trạng thái Hoạt động, đăng nhập được bằng email hoặc số điện thoại (UC-02).
- Account có mã `KH-...` và họ tên đã nhập.
- Tài khoản có 1 giỏ hàng trống và 1 danh sách yêu thích trống (UC-18, UC-38).

## Acceptance Criteria

### AC-1: Đăng ký thành công
Given: email "a@example.com" và số điện thoại "0901234567" chưa được dùng
When: khách vãng lai nhập đủ họ tên, email, số điện thoại, mật khẩu hợp lệ và bấm "Đăng ký"
Then: hệ thống tạo account vai trò Khách hàng, trạng thái Hoạt động
And: account có họ tên đã nhập và mã dạng `KH-<YYYYMMDD ngày đăng ký>-<4 số>`
And: khách được chuyển tới trang đăng nhập với thông báo đăng ký thành công

### AC-2: Email đã tồn tại
Given: đã có tài khoản dùng email "a@example.com"
When: khách vãng lai đăng ký với email "a@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: không có tài khoản mới nào được tạo

### AC-3: Số điện thoại đã tồn tại
Given: đã có tài khoản dùng số điện thoại "0901234567"
When: khách vãng lai đăng ký với số điện thoại "0901234567"
Then: hệ thống báo "Số điện thoại đã được sử dụng"
And: không có tài khoản mới nào được tạo

### AC-4: Dữ liệu không hợp lệ
Given: khách vãng lai đang ở trang đăng ký
When: khách nhập email sai định dạng, hoặc mật khẩu dưới 6 ký tự, hoặc nhập lại mật khẩu không khớp
Then: hệ thống báo lỗi tại trường tương ứng
And: không có tài khoản mới nào được tạo

### AC-5: Người đã đăng nhập không đăng ký được
Given: người dùng đang đăng nhập
When: người dùng mở trang đăng ký
Then: hệ thống chuyển về trang chủ

### AC-6: Lỗi giữa chừng không để lại dữ liệu dở dang
Given: khách vãng lai nhập thông tin đăng ký hợp lệ
When: việc cấp mã tài khoản hoặc lưu account thất bại giữa chừng
Then: toàn bộ thao tác bị hủy, không có account nào được tạo và bộ đếm mã `KH-` không bị dùng mất số
And: hệ thống báo đăng ký không thành công

## Dependencies
- **Upstream UC:** —
- **Downstream UC:** UC-02 Đăng nhập, UC-04 Cập nhật hồ sơ khách hàng
- **External Systems:** —

## Notes
- Đăng ký không xác minh email hoặc số điện thoại (BR không có yêu cầu xác minh).

### Quyết định đã chốt
- Đăng ký bắt buộc nhập đủ email và số điện thoại; đăng nhập bằng email hoặc số điện thoại đều được (đã chốt 15/11/2026).
- Account gồm thông tin đăng nhập (email unique, số điện thoại unique, mật khẩu đã hash, vai trò, trạng thái) và thông tin cá nhân (họ tên, ngày sinh, địa chỉ: số nhà, phường/xã, tỉnh/thành phố, quốc gia) trong cùng một bản ghi; không có username riêng (đã chốt 21/11/2026, data model v2, thay quyết định tách hồ sơ Customer ngày 15/11/2026).
- Mã tài khoản Khách hàng `KH-<YYYYMMDD ngày đăng ký>-<4 số>`, hệ thống cấp, không sửa; bộ đếm riêng cho tiền tố `KH` (đã chốt 21/11/2026).
- Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` của `account_created_at` (đã chốt 21/11/2026).
- Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026).
- Giỏ hàng và danh sách yêu thích trống được tạo cùng transaction tạo account; module identity gọi service công khai của shopping (đã chốt 21/11/2026, Q39).

### Giả định [GD]
- Ngày sinh và địa chỉ nhận hàng không bắt buộc khi đăng ký; khách bổ sung ở UC-04.
- Cấp mã và tạo account trong cùng một transaction.
- Mật khẩu tối thiểu 6 ký tự.
- Đăng ký xong chuyển tới trang đăng nhập, không tự đăng nhập.
- Người đã đăng nhập mở trang đăng ký thì bị chuyển về trang chủ.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt đăng ký đủ email và số điện thoại
- v3 (2026-11-15): theo ERD — tách account (thông tin đăng nhập) và hồ sơ Customer; thêm AC-6
- v4 (2026-11-21): theo data model v2 — bỏ hồ sơ Customer, thông tin cá nhân nằm trong account; cấp mã `KH-` (bước 4, AC-1, AC-6)
- v5 (2026-11-21): chốt bcrypt và múi giờ của mã `KH-`, bổ sung giả định tạo giỏ hàng và danh sách yêu thích khi đăng ký
- v6 (2026-11-21): chốt tạo giỏ hàng và danh sách yêu thích cùng transaction tạo account (Q39)
