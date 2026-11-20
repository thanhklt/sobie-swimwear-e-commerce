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
1. Người dùng mở trang đăng nhập.
2. Người dùng nhập email hoặc số điện thoại, và mật khẩu.
3. Hệ thống tìm account theo email hoặc số điện thoại (lưu trên account) và kiểm tra mật khẩu.
4. Hệ thống kiểm tra tài khoản đang ở trạng thái Hoạt động.
5. Hệ thống tạo phiên đăng nhập gắn với vai trò của tài khoản.
6. Hệ thống chuyển người dùng theo vai trò `[GD]`: Khách hàng về trang bán hàng; Nhân viên và Admin về khu vực quản trị.

## Alternative Flows
- **1a. Đăng nhập khi đang đặt hàng:** khách bị yêu cầu đăng nhập từ bước đặt hàng; sau khi đăng nhập thành công hệ thống đưa khách quay lại trang đang thao tác `[GD]`.

## Exceptions
- **E1. Sai thông tin đăng nhập:** không tìm thấy tài khoản hoặc sai mật khẩu — hệ thống báo chung "Thông tin đăng nhập không đúng", không cho biết sai trường nào `[GD]`.
- **E2. Tài khoản bị khóa:** hệ thống báo "Tài khoản đã bị khóa", không tạo phiên.
- **E3. Thiếu dữ liệu:** bỏ trống email/số điện thoại hoặc mật khẩu — hệ thống báo lỗi tại trường tương ứng.

## Postconditions
- Người dùng có phiên đăng nhập hợp lệ với đúng vai trò; chỉ truy cập được chức năng của vai trò đó.

## Acceptance Criteria

### AC-1: Đăng nhập bằng email
Given: tài khoản Khách hàng trạng thái Hoạt động với email "a@example.com"
When: người dùng nhập "a@example.com" và đúng mật khẩu
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng
And: người dùng được chuyển về trang bán hàng

### AC-2: Đăng nhập bằng số điện thoại
Given: tài khoản Khách hàng trạng thái Hoạt động với số điện thoại "0901234567"
When: người dùng nhập "0901234567" và đúng mật khẩu
Then: hệ thống tạo phiên đăng nhập vai trò Khách hàng

### AC-3: Tài khoản nội bộ vào khu vực quản trị
Given: tài khoản Nhân viên (hoặc Admin) trạng thái Hoạt động
When: người dùng đăng nhập đúng thông tin
Then: hệ thống tạo phiên với đúng vai trò
And: người dùng được chuyển vào khu vực quản trị

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

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản, UC-08 Khóa và mở khóa tài khoản
- **Downstream UC:** UC-03 Đăng xuất, UC-04, UC-05, UC-18 Quản lý giỏ hàng, UC-19, UC-20 (đặt hàng cần đăng nhập)
- **External Systems:** —

## Notes
- Không có quên mật khẩu qua email (Out of Scope).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Email và số điện thoại dùng để đăng nhập nằm trên account (unique); không có username riêng. Vai trò và trạng thái cũng nằm trên account (theo ERD, đã chốt 15/11/2026).

### Giả định [GD]
- Sau đăng nhập: Khách hàng về trang bán hàng; Nhân viên và Admin về khu vực quản trị.
- Đăng nhập khi đang đặt hàng thì quay lại trang đang thao tác.
- Sai thông tin đăng nhập báo chung, không chỉ rõ sai tài khoản hay mật khẩu.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): theo ERD — đăng nhập bằng email hoặc số điện thoại trên account, không có username
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — UC-06 đổi tên thành "Admin tạo tài khoản"
