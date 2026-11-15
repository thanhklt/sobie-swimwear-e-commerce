# UC-40: Bàn giao đơn cho vận chuyển

## Metadata
- **ID:** UC-40
- **Bounded Context:** shipping-context
- **Liên quan tới BR:** BR-006
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên chọn một đơn "Đã xác nhận" trong trang quản lý đơn hàng và bấm "Bàn giao vận chuyển".

## Preconditions
- Nhân viên đã đăng nhập.
- Đơn ở trạng thái "Đã xác nhận" (UC-23).

## Main Flow
1. Nhân viên mở trang quản lý đơn hàng và lọc các đơn "Đã xác nhận".
2. Nhân viên chọn một đơn và bấm "Bàn giao vận chuyển".
3. Hệ thống kiểm tra đơn vẫn ở "Đã xác nhận".
4. Hệ thống chuyển đơn sang "Đang giao" và lưu lịch sử trạng thái đơn.
5. Đơn xuất hiện trên Trang giả lập vận chuyển (UC-36); khách thấy trạng thái "Đang giao" khi theo dõi đơn (UC-21).

## Alternative Flows
- **2a. Bàn giao nhiều đơn một lúc `[GD]`:** Nhân viên chọn nhiều đơn "Đã xác nhận" và bấm "Bàn giao vận chuyển"; hệ thống xử lý từng đơn như bước 3–5, đơn nào không hợp lệ thì bỏ qua và báo lại cho Nhân viên.

## Exceptions
- **E1. Đơn không ở "Đã xác nhận":** đơn đang "Chưa xử lý", đã "Đang giao" hoặc đã ở trạng thái kết thúc — hệ thống từ chối, báo trạng thái hiện tại, đơn không đổi.
- **E2. Đơn không tồn tại:** hệ thống báo không tìm thấy đơn.

## Postconditions
- Đơn ở trạng thái "Đang giao" và có trong danh sách của Trang giả lập vận chuyển.
- Lịch sử trạng thái đơn có thêm 1 dòng: "Đã xác nhận → Đang giao", nguồn thay đổi, Nhân viên thực hiện, thời điểm.

## Acceptance Criteria

### AC-1: Bàn giao đơn thành công
Given: đơn DH001 ở trạng thái "Đã xác nhận"
When: Nhân viên bấm "Bàn giao vận chuyển" cho DH001
Then: đơn DH001 chuyển sang "Đang giao"
And: DH001 xuất hiện trên Trang giả lập vận chuyển
And: lịch sử trạng thái đơn ghi "Đã xác nhận → Đang giao" kèm Nhân viên thực hiện

### AC-2: Đơn chưa xác nhận
Given: đơn DH002 ở trạng thái "Chưa xử lý"
When: Nhân viên bấm "Bàn giao vận chuyển" cho DH002
Then: hệ thống từ chối và báo đơn đang "Chưa xử lý"
And: DH002 không xuất hiện trên Trang giả lập vận chuyển

### AC-3: Đơn đã bàn giao
Given: đơn DH001 đã ở trạng thái "Đang giao"
When: Nhân viên bấm "Bàn giao vận chuyển" cho DH001 lần nữa
Then: hệ thống từ chối, đơn giữ trạng thái "Đang giao"

### AC-4: Bàn giao nhiều đơn
Given: đơn DH001 và DH003 ở "Đã xác nhận", đơn DH002 ở "Chưa xử lý"
When: Nhân viên chọn cả 3 đơn và bấm "Bàn giao vận chuyển"
Then: DH001 và DH003 chuyển sang "Đang giao"
And: DH002 không đổi và hệ thống báo DH002 không được bàn giao

### AC-5: Khách thấy trạng thái mới
Given: đơn DH001 của khách A ở "Đã xác nhận"
When: Nhân viên bàn giao DH001
Then: khách A mở chi tiết đơn thấy trạng thái "Đang giao"

## Dependencies
- **Upstream UC:** UC-23 Xác nhận hoặc từ chối đơn
- **Downstream UC:** UC-36 Cập nhật trạng thái giao hàng, UC-21 Theo dõi đơn hàng
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Thông tin người gửi hiển thị trên trang giả lập lấy từ cấu hình hard-code.

### Quyết định đã chốt
- Nhân viên bấm "Bàn giao vận chuyển" cho đơn "Đã xác nhận" thì đơn sang "Đang giao" và xuất hiện trên Trang giả lập vận chuyển (đã chốt 15/11/2026).
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Có thể bàn giao nhiều đơn một lúc; đơn không hợp lệ thì bỏ qua và báo lại.

## History
- v1 (2026-11-15): initial
