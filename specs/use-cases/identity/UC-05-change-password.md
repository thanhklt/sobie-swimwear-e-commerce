# UC-05: Đổi mật khẩu

## Metadata
- **ID:** UC-05
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách hàng; Nhân viên và Admin.

## Trigger
Người dùng mở chức năng "Đổi mật khẩu".

## Preconditions
- Người dùng đang đăng nhập.
- Tài khoản đã có mật khẩu Sobie.

## Main Flow
1. Người dùng mở chức năng "Đổi mật khẩu".
2. Người dùng nhập mật khẩu hiện tại, mật khẩu mới và nhập lại mật khẩu mới.
3. Hệ thống kiểm tra mật khẩu hiện tại đúng, mật khẩu mới có ít nhất 6 ký tự và khác mật khẩu hiện tại, đồng thời hai lần nhập mật khẩu mới khớp nhau.
4. Trong cùng một transaction, hệ thống lưu mật khẩu mới và xóa mọi phiên (`identity.session`) của tài khoản.
5. Hệ thống báo đổi mật khẩu thành công. Mọi phiên của tài khoản, gồm cả phiên hiện tại, bị kết thúc và người dùng được chuyển tới trang đăng nhập của cổng tương ứng với vai trò để đăng nhập lại.

## Alternative Flows
- —

## Exceptions
- **E1. Sai mật khẩu hiện tại:** hệ thống báo "Mật khẩu hiện tại không đúng", không đổi.
- **E2. Mật khẩu mới không hợp lệ:** ngắn hơn 6 ký tự hoặc trùng mật khẩu hiện tại — hệ thống báo lỗi, không đổi.
- **E3. Nhập lại không khớp:** hệ thống báo "Mật khẩu nhập lại không khớp", không đổi.

## Postconditions
- Khi đăng nhập bằng mật khẩu Sobie, hệ thống chấp nhận mật khẩu mới và từ chối mật khẩu cũ.
- Mọi phiên đăng nhập của tài khoản (trên mọi thiết bị, kể cả thiết bị đang dùng) hết hiệu lực ngay.

## Acceptance Criteria

### AC-1: Đổi mật khẩu thành công
Given: Khách hàng đang đăng nhập, mật khẩu hiện tại là "matkhau1"
When: khách nhập đúng "matkhau1", mật khẩu mới "matkhau2" hai lần khớp nhau
Then: hệ thống báo đổi mật khẩu thành công
And: lần đăng nhập sau, "matkhau2" đăng nhập được, "matkhau1" bị từ chối

### AC-2: Sai mật khẩu hiện tại
Given: Khách hàng đang đăng nhập
When: khách nhập sai mật khẩu hiện tại
Then: hệ thống báo "Mật khẩu hiện tại không đúng"
And: mật khẩu không thay đổi

### AC-3: Mật khẩu mới không hợp lệ
Given: Khách hàng đang đăng nhập
When: khách nhập mật khẩu mới dưới 6 ký tự hoặc trùng mật khẩu hiện tại
Then: hệ thống báo lỗi tại trường mật khẩu mới
And: mật khẩu không thay đổi

### AC-4: Nhập lại không khớp
Given: Khách hàng đang đăng nhập
When: khách nhập mật khẩu mới và nhập lại khác nhau
Then: hệ thống báo "Mật khẩu nhập lại không khớp"
And: mật khẩu không thay đổi

### AC-5: Tài khoản nội bộ đổi mật khẩu
Given: Nhân viên hoặc Admin đang đăng nhập và tài khoản có mật khẩu Sobie
When: người dùng nhập đúng mật khẩu hiện tại và xác nhận mật khẩu mới hợp lệ
Then: hệ thống lưu mật khẩu mới cho tài khoản của chính người dùng

### AC-6: Đổi mật khẩu đăng xuất mọi thiết bị
Given: Khách hàng đang đăng nhập trên máy tính và điện thoại
When: khách đổi mật khẩu thành công trên máy tính
Then: phiên trên máy tính bị kết thúc, khách được chuyển tới trang đăng nhập
And: thao tác tiếp theo trên điện thoại bị yêu cầu đăng nhập lại

### AC-7: Đổi mật khẩu thất bại không đăng xuất
Given: Khách hàng đang đăng nhập
When: khách đổi mật khẩu nhưng bị từ chối (sai mật khẩu hiện tại, mật khẩu mới không hợp lệ hoặc nhập lại không khớp)
Then: phiên đăng nhập vẫn còn hiệu lực

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** —
- **External Systems:** —

## Notes
- BR-001 quy định Khách hàng, Nhân viên và Admin được tự đổi mật khẩu Sobie của mình.
- Kết thúc phiên bằng cách xóa các dòng `identity.session` của tài khoản (BR-GIAIDOAN1, Constraints chung — Xác thực; data model v2.15, Q35).

### Quyết định đã chốt
- Đổi mật khẩu kết thúc mọi phiên của tài khoản, kể cả phiên hiện tại, và đưa người dùng về trang đăng nhập (đã chốt 21/11/2026).
- Khách hàng, Nhân viên và Admin được tự đổi mật khẩu Sobie của mình (đã chốt 23/11/2026).
- Mật khẩu mới có ít nhất 6 ký tự và phải khác mật khẩu hiện tại (đã chốt 23/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-21): chốt đổi mật khẩu đăng xuất mọi thiết bị, kể cả thiết bị hiện tại (bước 4–5, AC-6, AC-7); bỏ giả định "không đăng xuất phiên hiện tại"
- v3 (2026-11-21): theo BR-GIAIDOAN1 v21 — kết thúc phiên bằng xóa `identity.session` thay cho `account_token_version` (bước 4, Postconditions, AC-6, Notes)
- v4 (2026-11-23): chốt quyền tự đổi mật khẩu cho cả ba vai trò, độ dài tối thiểu và yêu cầu khác mật khẩu hiện tại.
