# UC-41: Quản lý sổ địa chỉ giao hàng

## Metadata
- **ID:** UC-41
- **Module:** identity
- **Liên quan tới BR:** BR-001, BR-003
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách mở sổ địa chỉ từ hồ sơ, hoặc từ trang thanh toán (Thay đổi / Thêm địa chỉ).

## Preconditions
- Khách hàng đang đăng nhập.

## Main Flow
1. Khách mở danh sách địa chỉ giao hàng của mình.
2. Hệ thống hiển thị các địa chỉ trong `identity.shipping_address` (họ tên người nhận, SĐT, số nhà, phường/xã, tỉnh/thành, quốc gia), đánh dấu địa chỉ mặc định.
3. Khách có thể:
   - **Thêm địa chỉ:** nhập họ tên, SĐT, số nhà/đường, phường/xã, tỉnh/thành phố, quốc gia (không có quận/huyện) rồi lưu.
   - **Đặt làm mặc định** (khi có từ 2 địa chỉ trở lên): chọn một địa chỉ chưa mặc định.
4. Khi thêm địa chỉ đầu tiên của tài khoản, hệ thống gán `is_default = true` và đồng bộ mirror địa chỉ lên `account` (house/ward/city/country).
5. Khi đặt địa chỉ B làm mặc định, trong cùng một transaction hệ thống gỡ mặc định của A (nếu có), gán mặc định cho B, đồng bộ mirror lên `account`.
6. Hệ thống báo thành công và cập nhật danh sách.

## Alternative Flows
- **3a. Chỉ có 1 địa chỉ:** địa chỉ đó luôn là mặc định; không bắt buộc hiện nút «Đặt làm mặc định».
- **3b. Thêm địa chỉ từ checkout (UC-19/UC-20):** sau khi lưu sổ, địa chỉ mới được chọn cho đơn đang đặt; lần đặt sau địa chỉ vẫn còn trong danh sách.

## Exceptions
- **E1. Thiếu trường bắt buộc hoặc sai định dạng:** không lưu, báo lỗi tại trường.
- **E2. Đặt mặc định địa chỉ không thuộc tài khoản:** từ chối.

## Postconditions
- Sổ địa chỉ phản ánh thay đổi; tối đa một địa chỉ `is_default = true` / account.
- Mirror địa chỉ trên `account` khớp địa chỉ mặc định (khi đã có ít nhất một địa chỉ).

## Acceptance Criteria

### AC-1: Thêm địa chỉ đầu tiên thành mặc định
Given: khách chưa có dòng nào trong sổ địa chỉ
When: khách thêm một địa chỉ hợp lệ
Then: địa chỉ được lưu với `is_default = true`
And: các cột địa chỉ trên account được đồng bộ theo địa chỉ đó

### AC-2: Thêm địa chỉ thứ hai không đổi mặc định
Given: khách đã có địa chỉ A mặc định
When: khách thêm địa chỉ B
Then: B được lưu với `is_default = false`
And: A vẫn là mặc định

### AC-3: Đặt mặc định chuyển từ A sang B
Given: khách có A (mặc định) và B
When: khách đặt B làm mặc định
Then: B có `is_default = true`, A có `is_default = false`
And: mirror trên account khớp B

### AC-4: Địa chỉ thêm từ checkout còn trong sổ lần sau
Given: khách thêm địa chỉ C khi đang đặt hàng và dùng C cho đơn
When: khách mở lại sổ địa chỉ hoặc checkout lần sau
Then: C vẫn nằm trong danh sách

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-04 Cập nhật hồ sơ (thông tin cá nhân)
- **Downstream UC:** UC-19, UC-20 (chọn / thêm địa chỉ khi đặt hàng)
- **External Systems:** —

## Notes
- Module identity sở hữu bảng; ordering chỉ gọi service công khai / snapshot vào order.
- Sửa / xóa địa chỉ: chưa bắt buộc GĐ1 `[GD]` — có thể bổ sung sau; tối thiểu GĐ1: list, thêm, đặt mặc định.

### Quyết định đã chốt
- Sổ nhiều địa chỉ vào Giai đoạn 1 (27/11/2026); bỏ khỏi Out of Scope BR.
- Form: tỉnh + phường + số nhà (+ tên, SĐT, quốc gia).
- Đúng một mặc định / khách; địa chỉ đầu = mặc định.

## History
- v1 (2026-11-27): initial — sổ địa chỉ + mặc định theo BR-001/BR-003
