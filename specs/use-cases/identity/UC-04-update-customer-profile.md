# UC-04: Cập nhật hồ sơ khách hàng

## Metadata
- **ID:** UC-04
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
- Khách hàng cập nhật hồ sơ của chính mình.
- Admin cập nhật hồ sơ của tài khoản Khách hàng qua UC-07.

## Trigger
Khách hàng mở trang hồ sơ hoặc bấm "Sử dụng thông tin hồ sơ" ở checkout khi hồ sơ chưa đầy đủ. Admin có thể lưu thay đổi cho tài khoản Khách hàng đã chọn trong portal quản trị.

## Preconditions
- Khách hàng đang đăng nhập ở storefront, hoặc Admin đang đăng nhập ở portal quản trị và đã chọn một tài khoản Khách hàng theo UC-07.

## Main Flow
1. Khách hàng mở trang hồ sơ.
2. Hệ thống hiển thị thông tin hiện tại của tài khoản gồm mã tài khoản và email (chỉ xem), họ tên, ngày sinh, địa chỉ nhận hàng (số nhà, phường/xã, tỉnh/thành phố, quốc gia) và số điện thoại.
3. Khách hàng sửa họ tên, ngày sinh, địa chỉ hoặc số điện thoại rồi bấm "Lưu".
4. Hệ thống kiểm tra dữ liệu hợp lệ và số điện thoại không trùng với tài khoản khác.
5. Hệ thống lưu họ tên, ngày sinh, địa chỉ và số điện thoại vào tài khoản rồi báo cập nhật thành công. Mã tài khoản `KH-` không đổi.

## Alternative Flows
- **1a. Admin cập nhật hồ sơ Khách hàng:** Admin chọn tài khoản Khách hàng trong portal quản trị theo UC-07. Admin có thể sửa thông tin hồ sơ, bao gồm email. Hệ thống kiểm tra và lưu thay đổi theo UC-07.
- **1b. Bổ sung hồ sơ trong checkout:** Checkout (UC-19 hoặc UC-20) mở biểu mẫu hồ sơ với dữ liệu đã lưu. Khách bổ sung hoặc sửa họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng. Hệ thống kiểm tra và lưu theo bước 4–5. Sau khi lưu thành công, hệ thống về checkout và tự điền tên người nhận, số điện thoại nhận hàng và địa chỉ. Nếu dữ liệu không hợp lệ, hệ thống báo lỗi tại biểu mẫu hồ sơ. Khách có thể đóng biểu mẫu và tiếp tục nhập thông tin nhận hàng ngay tại checkout.
- **3a. Không thay đổi gì:** khách bấm "Lưu" khi không sửa trường nào — hệ thống báo thành công, dữ liệu giữ nguyên.
- **3b. Quản lý sổ địa chỉ:** khách mở «Sổ địa chỉ» / «Thay đổi địa chỉ» → UC-41.

## Exceptions
- **E1. Số điện thoại trùng tài khoản khác:** hệ thống báo số điện thoại đã được sử dụng, không lưu hồ sơ.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc hoặc sai định dạng — hệ thống báo lỗi tại trường tương ứng, không lưu.

## Postconditions
- Tài khoản Khách hàng được cập nhật thông tin hồ sơ. Khi đăng nhập bằng mật khẩu Sobie, khách dùng email của tài khoản hoặc số điện thoại đã lưu sau cập nhật.

## Acceptance Criteria

### AC-1: Cập nhật thành công
Given: Khách hàng đang đăng nhập
When: khách đổi họ tên, ngày sinh rồi bấm "Lưu"
Then: hệ thống lưu thông tin mới vào account
And: trang hồ sơ hiển thị thông tin mới

### AC-2: Khách hàng không đổi được email
Given: Khách hàng đang đăng nhập ở trang hồ sơ
When: khách gửi biểu mẫu hồ sơ kèm email khác email hiện tại
Then: hệ thống lưu các trường khác hợp lệ và giữ nguyên email
And: trang hồ sơ hiển thị email ở dạng chỉ xem

### AC-3: Số điện thoại trùng tài khoản khác
Given: đã có tài khoản khác dùng số "0981234567"
When: khách đổi số điện thoại thành số đó và bấm "Lưu"
Then: hệ thống báo "Số điện thoại đã được sử dụng"
And: hồ sơ giữ nguyên

### AC-4: Dữ liệu không hợp lệ
Given: Khách hàng đang ở trang hồ sơ
When: khách để trống họ tên hoặc nhập số điện thoại sai định dạng và bấm "Lưu"
Then: hệ thống báo lỗi tại trường tương ứng
And: hồ sơ không thay đổi

### AC-5: Admin cập nhật hồ sơ Khách hàng
Given: Admin đang đăng nhập ở portal quản trị và đã chọn một tài khoản Khách hàng theo UC-07
When: Admin lưu họ tên hoặc địa chỉ nhận hàng hợp lệ cho tài khoản đã chọn
Then: hệ thống cập nhật hồ sơ của tài khoản Khách hàng đó và giữ nguyên mã `KH-`
And: trang hồ sơ của Khách hàng hiển thị thông tin đã cập nhật

### AC-6: Bổ sung hồ sơ để tự điền trong checkout
Given: Khách hàng đang checkout và hồ sơ còn thiếu hoặc có thông tin không hợp lệ
When: khách bấm "Sử dụng thông tin hồ sơ" và lưu biểu mẫu hồ sơ với đủ dữ liệu hợp lệ
Then: hệ thống lưu hồ sơ và tự điền tên người nhận, số điện thoại nhận hàng và địa chỉ trên biểu mẫu đặt hàng
And: ngày sinh chỉ lưu trong hồ sơ

## Hiện trạng triển khai

- Khách hàng xem và lưu hồ sơ của mình tại `/api/v1/identity/account/profile`. Admin lưu hồ sơ tài khoản Khách hàng đã chọn tại `POST /api/v1/identity/portal/accounts/{account_key}/edit` theo UC-07.
- Hai POST sửa hồ sơ hiện kiểm tra `csrf_token`. Kiểm tra `Origin` theo API Contract v1 còn chờ triển khai.
- Checkout hiện hiển thị và gộp giỏ. Nút “Sử dụng thông tin hồ sơ” còn chờ triển khai tại UC-19 và UC-20.

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-02 Đăng nhập
- **Downstream UC:** UC-19, UC-20 (nút "Sử dụng thông tin hồ sơ" khi đặt hàng)
- **Related UC:** UC-07 Sửa tài khoản (Admin cập nhật hồ sơ Khách hàng trong portal)
- **External Systems:** —

## Notes
- Địa chỉ giao hàng không còn «chỉ 1 địa chỉ sửa trên hồ sơ»; dùng sổ `shipping_address` (UC-41).

### Quyết định đã chốt
- Thông tin cá nhân (họ tên, ngày sinh) nằm trong account cùng email, số điện thoại (đã chốt 21/11/2026).
- Sổ nhiều địa chỉ giao hàng + 1 mặc định (đã chốt 27/11/2026); `account_*` địa chỉ = mirror mặc định.
- Email và số điện thoại unique, dùng để đăng nhập; không có username riêng (đã chốt 15/11/2026).
- Mã tài khoản không sửa được (đã chốt 21/11/2026).
- Khách hàng tự cập nhật hồ sơ ở storefront. Admin cũng được cập nhật hồ sơ Khách hàng qua UC-07 ở portal quản trị (đã chốt 23/11/2026).
- Khách có thể nhập tay tên người nhận, số điện thoại nhận hàng và địa chỉ nhận hàng. Khi khách bấm "Sử dụng thông tin hồ sơ", hệ thống tự điền ba thông tin nhận hàng nếu hồ sơ đã có đủ họ tên, ngày sinh, số điện thoại và địa chỉ hợp lệ. Nếu hồ sơ còn thiếu hoặc có dữ liệu không hợp lệ, hệ thống mở biểu mẫu cập nhật hồ sơ ngay trong checkout theo UC-04. Sau khi lưu hồ sơ hợp lệ, hệ thống tự điền thông tin nhận hàng và đưa khách về biểu mẫu đặt hàng. Khách có thể sửa các giá trị trước khi xác nhận. Đơn lưu thông tin nhận hàng cuối cùng tại thời điểm đặt. Ngày sinh là điều kiện hồ sơ đầy đủ (đã chốt 27/11/2026).

- Đổi số điện thoại không cần xác minh lại (đã chốt 24/11/2026).
- Khách hàng không tự đổi email. Email chỉ đổi qua Admin (UC-07) vì Sobie liên kết Google theo email đã xác minh (UC-01, UC-02) (đã chốt 26/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo ERD — hồ sơ Customer (họ tên, ngày sinh, địa chỉ) tách khỏi account (email, số điện thoại)
- v3 (2026-11-21): theo data model v2 — bỏ hồ sơ Customer, mọi thông tin lưu ở account; hiển thị mã tài khoản (bước 2, 5); bỏ giả định lưu 2 bảng trong 1 transaction
- v4 (2026-11-23): dùng nút "Sử dụng thông tin hồ sơ" khi đặt hàng và chốt điều kiện hồ sơ đầy đủ, gồm ngày sinh.
- v5 (2026-11-23): chốt quyền cập nhật hồ sơ Khách hàng cho chủ tài khoản và Admin qua UC-07.
- v6 (2026-11-26): email chỉ xem trên hồ sơ storefront, AC-3 kiểm tra số điện thoại trùng.
- v7 (2026-11-27): thêm luồng cập nhật hồ sơ tại checkout và tự điền sau khi lưu hợp lệ.
