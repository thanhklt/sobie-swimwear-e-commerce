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
2. Hệ thống kết thúc phiên đăng nhập hiện tại.
3. Hệ thống chuyển người dùng về trang chủ.

## Alternative Flows
- —

## Exceptions
- **E1. Phiên đã hết hiệu lực:** hệ thống vẫn coi như đăng xuất thành công và chuyển về trang chủ.

## Postconditions
- Phiên đăng nhập hiện tại không còn hiệu lực; người dùng trở thành Khách vãng lai.

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

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** —
- **External Systems:** —

## Notes

### Giả định [GD]
- Toàn bộ UC này là giả định: BR-001 chỉ nêu đăng ký và đăng nhập, không nêu đăng xuất.
- Đăng xuất chỉ kết thúc phiên trên thiết bị hiện tại.
- Sau đăng xuất chuyển về trang chủ.

## History
- v1 (2026-11-15): initial
