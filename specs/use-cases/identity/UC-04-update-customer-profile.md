# UC-04: Cập nhật hồ sơ khách hàng

## Metadata
- **ID:** UC-04
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách hàng mở trang hồ sơ và bấm "Lưu" sau khi sửa thông tin.

## Preconditions
- Khách hàng đang đăng nhập.

## Main Flow
1. Khách hàng mở trang hồ sơ.
2. Hệ thống hiển thị thông tin hiện tại của account: mã tài khoản (chỉ xem), họ tên, ngày sinh, địa chỉ nhận hàng (số nhà, phường/xã, tỉnh/thành phố, quốc gia), email, số điện thoại.
3. Khách hàng sửa thông tin và bấm "Lưu".
4. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại mới không trùng account khác.
5. Hệ thống lưu họ tên, ngày sinh, địa chỉ, email, số điện thoại vào account; báo cập nhật thành công. Mã tài khoản `KH-` không đổi.

## Alternative Flows
- **3a. Không thay đổi gì:** khách bấm "Lưu" khi không sửa trường nào — hệ thống báo thành công, dữ liệu giữ nguyên.

## Exceptions
- **E1. Email hoặc số điện thoại trùng tài khoản khác:** hệ thống báo trường bị trùng, không lưu.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc hoặc sai định dạng — hệ thống báo lỗi tại trường tương ứng, không lưu.

## Postconditions
- Account được cập nhật thông tin cá nhân, email, số điện thoại mới và lần đăng nhập sau dùng email hoặc số điện thoại mới.

## Acceptance Criteria

### AC-1: Cập nhật thành công
Given: Khách hàng đang đăng nhập
When: khách đổi họ tên, ngày sinh và địa chỉ nhận hàng (số nhà, phường/xã, tỉnh/thành phố, quốc gia) rồi bấm "Lưu"
Then: hệ thống lưu thông tin mới vào account
And: trang hồ sơ hiển thị thông tin mới

### AC-2: Đổi email rồi đăng nhập bằng email mới
Given: khách đổi email từ "a@example.com" sang "b@example.com" thành công
When: khách đăng xuất rồi đăng nhập bằng "b@example.com"
Then: đăng nhập thành công
And: đăng nhập bằng "a@example.com" bị từ chối

### AC-3: Email trùng tài khoản khác
Given: đã có tài khoản khác dùng email "c@example.com"
When: khách đổi email thành "c@example.com" và bấm "Lưu"
Then: hệ thống báo "Email đã được sử dụng"
And: hồ sơ giữ nguyên email cũ

### AC-4: Dữ liệu không hợp lệ
Given: Khách hàng đang ở trang hồ sơ
When: khách để trống họ tên hoặc nhập số điện thoại sai định dạng và bấm "Lưu"
Then: hệ thống báo lỗi tại trường tương ứng
And: hồ sơ không thay đổi

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-02 Đăng nhập
- **Downstream UC:** UC-19, UC-20 (địa chỉ nhận hàng dùng khi đặt hàng `[GD]`)
- **External Systems:** —

## Notes
- Mỗi khách chỉ có 1 địa chỉ nhận hàng (sổ nhiều địa chỉ là Out of Scope).

### Quyết định đã chốt
- Thông tin cá nhân (họ tên, ngày sinh, 1 địa chỉ nhận hàng: số nhà, phường/xã, tỉnh/thành phố, quốc gia) nằm trong account cùng email, số điện thoại (đã chốt 21/11/2026, data model v2, thay quyết định tách hồ sơ Customer ngày 15/11/2026).
- Email và số điện thoại unique, dùng để đăng nhập; không có username riêng (đã chốt 15/11/2026).
- Mã tài khoản không sửa được (đã chốt 21/11/2026).

### Giả định [GD]
- Địa chỉ trong hồ sơ được điền sẵn khi đặt hàng.
- Đổi email hoặc số điện thoại không cần xác minh lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo ERD — hồ sơ Customer (họ tên, ngày sinh, địa chỉ) tách khỏi account (email, số điện thoại)
- v3 (2026-11-21): theo data model v2 — bỏ hồ sơ Customer, mọi thông tin lưu ở account; hiển thị mã tài khoản (bước 2, 5); bỏ giả định lưu 2 bảng trong 1 transaction
