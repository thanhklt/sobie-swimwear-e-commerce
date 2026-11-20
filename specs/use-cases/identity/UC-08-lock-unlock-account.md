# UC-08: Khóa và mở khóa tài khoản

## Metadata
- **ID:** UC-08
- **Module:** identity
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
- **1b. Admin tự khóa chính mình:** được phép khi hệ thống còn ít nhất 1 Admin khác đang hoạt động (E1). Sau khi khóa, phiên của Admin đó bị kết thúc và không đăng nhập lại được cho tới khi một Admin khác mở khóa.
- **3a. Hủy xác nhận:** Admin bấm "Hủy" — trạng thái tài khoản giữ nguyên.

## Exceptions
- **E1. Khóa Admin đang hoạt động cuối cùng:** tài khoản cần khóa là Admin đang hoạt động duy nhất — hệ thống từ chối, vì hệ thống luôn phải có ít nhất 1 Admin đang hoạt động. Người khóa luôn là một Admin đang hoạt động, nên trường hợp này chỉ xảy ra khi Admin đó tự khóa chính mình.
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

### AC-5: Admin tự khóa chính mình
Given: Admin "admin@example.com" đang đăng nhập; hệ thống còn Admin "admin2@example.com" đang hoạt động
When: "admin@example.com" khóa tài khoản của chính mình và xác nhận
Then: "admin@example.com" chuyển sang Bị khóa, phiên đang mở bị kết thúc
And: "admin2@example.com" mở khóa được "admin@example.com"

### AC-7: Không khóa Admin đang hoạt động cuối cùng
Given: "admin@example.com" là Admin đang hoạt động duy nhất
When: "admin@example.com" khóa tài khoản của chính mình
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

### Quyết định đã chốt
- Hệ thống luôn có ít nhất 1 Admin đang hoạt động (vai trò Admin, trạng thái Hoạt động); không cho khóa Admin đang hoạt động cuối cùng (đã chốt 20/11/2026, data model v2, Q24).
- Kiểm tra trong cùng transaction với thao tác khóa, khóa các dòng tài khoản Admin để 2 thao tác đồng thời không cùng vượt qua kiểm tra (data model v2).
- Admin được tự khóa chính mình khi còn ít nhất 1 Admin khác đang hoạt động (đã chốt 20/11/2026).

### Giả định [GD]
- Khóa tài khoản kết thúc ngay mọi phiên đăng nhập đang mở của tài khoản đó.
- Khóa và mở khóa áp dụng cho mọi vai trò (Khách hàng, Nhân viên, Admin).
- Khóa không xóa dữ liệu của tài khoản.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-20): theo data model v2 — không khóa Admin đang hoạt động cuối cùng (E2, AC-7)
- v3 (2026-11-20): cho Admin tự khóa chính mình khi còn Admin khác đang hoạt động (bỏ E1 cũ, thêm 1b, AC-5 viết lại); E2 đổi thành E1, AC-7 viết lại
