# UC-03: Đăng xuất

## Metadata
- **ID:** UC-03
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách hàng, Nhân viên, Admin

## Trigger
Người dùng bấm "Đăng xuất".

## Preconditions
- Người dùng đang đăng nhập.

## Main Flow
1. Người dùng bấm "Đăng xuất".
2. Hệ thống xóa phiên hiện tại khỏi `identity.session` và xóa cookie phiên của cổng đang dùng.
3. Hệ thống chuyển người dùng về trang chủ.

## Alternative Flows
- —

## Exceptions
- **E1. Phiên đã hết hiệu lực:** hệ thống vẫn coi như đăng xuất thành công và chuyển về trang chủ.

## Postconditions
- Phiên hiện tại không còn hiệu lực ngay lập tức; người dùng trở thành Khách vãng lai.
- Phiên trên các thiết bị khác không bị ảnh hưởng.

## Acceptance Criteria

### AC-1: Đăng xuất thành công
Given: Khách hàng đang đăng nhập
When: khách bấm "Đăng xuất"
Then: phiên đăng nhập hiện tại bị kết thúc
And: khách được chuyển về trang chủ

### AC-2: Không dùng lại được phiên cũ
Given: người dùng vừa đăng xuất
When: người dùng truy cập trang cần đăng nhập (ví dụ hồ sơ khách hàng)
Then: hệ thống yêu cầu đăng nhập

### AC-3: Phiên đã hết hiệu lực
Given: phiên của người dùng đã hết hiệu lực
When: người dùng bấm "Đăng xuất"
Then: hệ thống chuyển về trang chủ, không báo lỗi

### AC-4: Mã phiên cũ không dùng lại được
Given: người dùng vừa đăng xuất
When: có request gửi kèm mã phiên cũ (ví dụ cookie được sao chép trước khi đăng xuất)
Then: hệ thống coi như chưa đăng nhập

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** —
- **External Systems:** không có

## Notes

### Quyết định đã chốt
- Đăng xuất xóa dòng `identity.session` của phiên hiện tại, có hiệu lực ngay (đã chốt 21/11/2026, thay quyết định "chỉ hủy refresh token" cùng ngày).
- Đăng xuất chỉ kết thúc phiên trên thiết bị hiện tại.
- Sau đăng xuất chuyển về trang chủ `/`.

### Giả định [GD]
- Toàn bộ UC này là giả định: BR-001 chỉ nêu đăng ký và đăng nhập, không nêu đăng xuất.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-21): theo BR-GIAIDOAN1 v20 — đăng xuất hủy refresh token của thiết bị hiện tại; access token còn hạn không bị thu hồi; thêm AC-4
- v3 (2026-11-21): theo BR-GIAIDOAN1 v21 — đăng xuất xóa phiên hiện tại trong `identity.session`, có hiệu lực ngay (bước 2, Postconditions, AC-4); bỏ access / refresh token
