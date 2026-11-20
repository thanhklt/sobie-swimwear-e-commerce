# UC-06: Admin tạo tài khoản

## Metadata
- **ID:** UC-06
- **Bounded Context:** identity-context
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Admin

## Trigger
Admin bấm "Tạo tài khoản" trong khu vực quản lý tài khoản.

## Preconditions
- Admin đang đăng nhập.

## Main Flow
1. Admin mở form tạo tài khoản.
2. Admin nhập họ tên, ngày sinh, địa chỉ, email, số điện thoại, mật khẩu ban đầu `[GD]` và chọn một trong 3 vai trò: Khách hàng, Nhân viên hoặc Admin.
3. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại chưa được dùng.
4. Trong cùng một transaction `[GD]`, hệ thống tạo account (email, số điện thoại, mật khẩu đã hash, vai trò đã chọn, trạng thái Hoạt động) và hồ sơ tương ứng với vai trò: Customer nếu là Khách hàng, Employee nếu là Nhân viên, Admin nếu là Admin (họ tên, ngày sinh, địa chỉ).
5. Hệ thống báo tạo thành công; tài khoản mới hiện trong danh sách tài khoản (UC-07).

## Alternative Flows
- —

## Exceptions
- **E1. Email hoặc số điện thoại đã được dùng:** hệ thống báo trường bị trùng, không tạo tài khoản.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc, sai định dạng, mật khẩu dưới 6 ký tự `[GD]` — hệ thống báo lỗi tại trường tương ứng, không tạo.
- **E3. Vai trò không hợp lệ:** vai trò không thuộc 3 vai trò cố định — hệ thống từ chối.

## Postconditions
- Có account mới, đăng nhập được ngay bằng mật khẩu ban đầu (UC-02), không bắt buộc đổi mật khẩu ở lần đăng nhập đầu.
- Có hồ sơ Customer, Employee hoặc Admin (theo vai trò) gắn với account đó.

## Acceptance Criteria

### AC-1: Tạo tài khoản Nhân viên
Given: Admin đang đăng nhập, email "nv1@example.com" chưa được dùng
When: Admin nhập đủ thông tin, chọn vai trò Nhân viên và bấm "Tạo"
Then: hệ thống tạo account vai trò Nhân viên, trạng thái Hoạt động
And: hệ thống tạo hồ sơ Employee gắn với account đó
And: tài khoản đăng nhập được bằng mật khẩu ban đầu

### AC-2: Tạo tài khoản Admin
Given: Admin đang đăng nhập
When: Admin tạo tài khoản với vai trò Admin
Then: hệ thống tạo account vai trò Admin
And: hệ thống tạo hồ sơ Admin gắn với account đó

### AC-3: Email hoặc số điện thoại trùng
Given: đã có tài khoản dùng email "nv1@example.com"
When: Admin tạo tài khoản với email "nv1@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: không có tài khoản mới nào được tạo

### AC-4: Tạo tài khoản Khách hàng
Given: Admin đang đăng nhập, email "kh1@example.com" và số điện thoại "0901234567" chưa được dùng
When: Admin nhập đủ thông tin, chọn vai trò Khách hàng và bấm "Tạo"
Then: hệ thống tạo account vai trò Khách hàng, trạng thái Hoạt động
And: hệ thống tạo hồ sơ Customer gắn với account đó
And: tài khoản đăng nhập được ngay và đặt hàng được như tài khoản khách tự đăng ký, không bị yêu cầu đổi mật khẩu

### AC-5: Vai trò khác không tạo được tài khoản
Given: Nhân viên hoặc Khách hàng đang đăng nhập
When: người dùng truy cập chức năng tạo tài khoản
Then: hệ thống từ chối truy cập

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** UC-07 Sửa tài khoản, UC-08 Khóa và mở khóa tài khoản
- **External Systems:** —

## Notes
- 3 vai trò cố định; không tạo vai trò mới hoặc cấu hình quyền (Out of Scope).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Account chỉ giữ thông tin đăng nhập: email (unique), số điện thoại (unique), mật khẩu đã hash, vai trò, trạng thái; không có username riêng (theo ERD, đã chốt 15/11/2026).
- Thông tin cá nhân (họ tên, ngày sinh, địa chỉ) nằm ở hồ sơ riêng theo vai trò: Customer cho Khách hàng, Employee cho Nhân viên, Admin cho Admin; mỗi hồ sơ có khóa ngoại tới account (theo ERD, đã chốt 15/11/2026).
- Admin toàn quyền tạo tài khoản với mọi vai trò: Khách hàng, Nhân viên, Admin (đã chốt 20/11/2026).
- Tài khoản do Admin tạo dùng được ngay, không bắt buộc đổi mật khẩu ở lần đăng nhập đầu (đã chốt 20/11/2026).
- Tài khoản do Admin tạo cũng bắt buộc đủ email và số điện thoại, không trùng tài khoản khác (như đăng ký, UC-01).

### Giả định [GD]
- Tạo account và hồ sơ theo vai trò trong cùng một transaction.
- Admin đặt mật khẩu ban đầu cho tài khoản; mật khẩu tối thiểu 6 ký tự.
- Hệ thống có sẵn 1 tài khoản Admin khi khởi tạo.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): theo ERD — tạo account và hồ sơ Employee/Admin riêng theo vai trò
- v4 (2026-11-20): Admin tạo được tài khoản mọi vai trò (thêm Khách hàng, tạo hồ sơ Customer); đổi tên UC và file thành `UC-06-create-account.md`; tài khoản dùng được ngay, không bắt buộc đổi mật khẩu
