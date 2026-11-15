# UC-08: Khóa và mở khóa tài khoản

## Metadata
- **ID:** UC-08
- **Bounded Context:** identity-context
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Admin

## Trigger
Admin bấm "Khóa" hoặc "Mở khóa" trên một tài khoản trong danh sách tài khoản (UC-07).

## Preconditions
- Admin đang đăng nhập.
- Tài khoản cần thao tác tồn tại.

## Main Flow
1. Admin chọn một tài khoản đang Hoạt động và bấm "Khóa".
2. Hệ thống yêu cầu xác nhận.
3. Admin xác nhận.
4. Hệ thống chuyển tài khoản sang trạng thái Bị khóa và kết thúc mọi phiên đăng nhập đang mở của tài khoản đó `[GD]`.
5. Hệ thống báo khóa thành công.

## Alternative Flows
- **1a. Mở khóa:** Admin chọn tài khoản đang Bị khóa và bấm "Mở khóa" — sau khi xác nhận, hệ thống chuyển tài khoản về Hoạt động; tài khoản đăng nhập lại được.
- **3a. Hủy xác nhận:** Admin bấm "Hủy" — trạng thái tài khoản giữ nguyên.

## Exceptions
- **E1. Tự khóa chính mình:** Admin khóa tài khoản đang dùng — hệ thống từ chối `[GD]`.

## Postconditions
- Tài khoản Bị khóa không đăng nhập được (UC-02, E2); tài khoản được mở khóa đăng nhập lại được.
- Dữ liệu của tài khoản (hồ sơ, đơn hàng) giữ nguyên `[GD]`.

## Acceptance Criteria

### AC-1: Khóa tài khoản
Given: tài khoản Khách hàng "a@example.com" trạng thái Hoạt động
When: Admin bấm "Khóa" và xác nhận
Then: tài khoản chuyển sang Bị khóa
And: đăng nhập bằng "a@example.com" bị từ chối với thông báo "Tài khoản đã bị khóa"

### AC-2: Khóa kết thúc phiên đang mở
Given: Nhân viên "nv1@example.com" đang đăng nhập
When: Admin khóa tài khoản "nv1@example.com"
Then: thao tác tiếp theo của Nhân viên này bị yêu cầu đăng nhập lại

### AC-3: Mở khóa tài khoản
Given: tài khoản "a@example.com" trạng thái Bị khóa
When: Admin bấm "Mở khóa" và xác nhận
Then: tài khoản chuyển về Hoạt động
And: "a@example.com" đăng nhập được

### AC-4: Hủy xác nhận
Given: tài khoản "a@example.com" trạng thái Hoạt động
When: Admin bấm "Khóa" rồi bấm "Hủy" ở bước xác nhận
Then: tài khoản vẫn Hoạt động

### AC-5: Không tự khóa chính mình
Given: Admin "admin@example.com" đang đăng nhập
When: Admin khóa tài khoản "admin@example.com"
Then: hệ thống từ chối
And: tài khoản vẫn Hoạt động

### AC-6: Vai trò khác không khóa được
Given: Nhân viên đang đăng nhập
When: Nhân viên gửi yêu cầu khóa một tài khoản
Then: hệ thống từ chối truy cập

## Dependencies
- **Upstream UC:** UC-07 Sửa tài khoản (danh sách tài khoản)
- **Downstream UC:** UC-02 Đăng nhập
- **External Systems:** —

## Notes

### Giả định [GD]
- Khóa tài khoản kết thúc ngay mọi phiên đăng nhập đang mở của tài khoản đó.
- Admin không tự khóa chính mình.
- Khóa và mở khóa áp dụng cho mọi vai trò (Khách hàng, Nhân viên, Admin).
- Khóa không xóa dữ liệu của tài khoản.

## History
- v1 (2026-11-15): initial
