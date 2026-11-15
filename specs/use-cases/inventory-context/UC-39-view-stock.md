# UC-39: Xem tồn kho

## Metadata
- **ID:** UC-39
- **Bounded Context:** inventory-context
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình tồn kho trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên mở màn hình tồn kho.
2. Hệ thống hiển thị danh sách tồn kho theo biến thể, có phân trang `[GD]`: tên sản phẩm, màu, size, số lượng tồn.
3. Nhân viên có thể tìm theo tên sản phẩm và lọc theo danh mục `[GD]`.
4. Hệ thống đánh dấu các biến thể có tồn ≤ ngưỡng tồn kho thấp (hard-code) `[GD]`.

## Alternative Flows
- **3a. Không có kết quả:** từ khóa hoặc bộ lọc không khớp biến thể nào → hệ thống hiển thị danh sách trống kèm thông báo "Không tìm thấy biến thể".

## Exceptions
- **E1. Vai trò không được phép:** Khách hàng hoặc Admin truy cập màn hình tồn kho → hệ thống từ chối.
- **E2. Cố sửa tồn kho:** màn hình chỉ để xem, không có thao tác sửa số lượng tồn; mọi yêu cầu sửa tay tồn kho bị từ chối.

## Postconditions
- Không thay đổi dữ liệu; chỉ hiển thị tồn kho.

## Acceptance Criteria

### AC-1: Xem danh sách tồn kho
Given: biến thể "Áo bơi A – Đỏ – M" tồn 30, "Áo bơi A – Xanh – L" tồn 0
When: Nhân viên mở màn hình tồn kho
Then: danh sách hiển thị cả hai biến thể với tên sản phẩm, màu, size và số lượng tồn 30 và 0

### AC-2: Tìm theo tên sản phẩm
Given: có biến thể của "Áo bơi A" và "Quần bơi B"
When: Nhân viên tìm "Áo bơi A"
Then: chỉ hiển thị các biến thể của "Áo bơi A"

### AC-3: Lọc theo danh mục
Given: "Áo bơi A" thuộc danh mục "Bikini", "Quần bơi B" thuộc danh mục "Quần bơi"
When: Nhân viên lọc danh mục "Bikini"
Then: chỉ hiển thị các biến thể của sản phẩm thuộc "Bikini"

### AC-4: Đánh dấu tồn kho thấp
Given: ngưỡng tồn kho thấp là 5; biến thể X tồn 3, biến thể Y tồn 6
When: Nhân viên mở màn hình tồn kho
Then: biến thể X được đánh dấu tồn kho thấp, biến thể Y không

### AC-5: Không tìm thấy
Given: không có sản phẩm nào khớp "zzz"
When: Nhân viên tìm "zzz"
Then: hệ thống hiển thị "Không tìm thấy biến thể"

### AC-6: Vai trò không được phép
Given: người dùng đăng nhập với vai trò Khách hàng hoặc Admin
When: người dùng truy cập màn hình tồn kho
Then: hệ thống từ chối truy cập

### AC-7: Tồn kho cập nhật sau khi xác nhận phiếu nhập
Given: biến thể X tồn 10
When: một phiếu nhập 20 cái biến thể X được xác nhận (UC-34), sau đó Nhân viên mở màn hình tồn kho
Then: biến thể X hiển thị tồn 30

## Dependencies
- **Upstream UC:** UC-02, UC-15, UC-19, UC-20, UC-22, UC-23, UC-24, UC-34, UC-35
- **Downstream UC:** không có
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung); tồn kho hiển thị phải được làm mới khi tồn kho thay đổi (đặt hàng, hủy/từ chối đơn, xác nhận phiếu nhập, giao không thành công).
- Tồn kho không bao giờ âm và không sửa tay; chỉ thay đổi qua các UC nghiệp vụ (BR-005).
- Ngưỡng tồn kho thấp lấy từ cấu hình hard-code (BR-TUAN1, Constraints chung).

**Quyết định đã chốt**
- Nhân viên quản lý hàng hóa nên xem được tồn kho theo biến thể ngoài dashboard (đã chốt 15/11/2026).

**Giả định [GD]**
- Danh sách tồn kho có phân trang; mỗi dòng gồm tên sản phẩm, màu, size, số lượng tồn.
- Tìm theo tên sản phẩm và lọc theo danh mục.
- Biến thể có tồn ≤ ngưỡng tồn kho thấp được đánh dấu.
- Giá vốn có hiển thị trên màn hình tồn kho hay không: chưa chốt, hiện chưa hiển thị.
- Khách hàng và Admin không truy cập được màn hình tồn kho.

## History
- v1 (2026-11-15): initial
