# UC-23: Xác nhận hoặc từ chối đơn

## Metadata
- **ID:** UC-23
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở trang quản lý đơn hàng trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập.

## Main Flow
1. Hệ thống hiển thị danh sách đơn, có phân trang và lọc theo trạng thái đơn `[GD]`: mã đơn, khách, ngày đặt, tổng thanh toán, phương thức, trạng thái đơn, trạng thái thanh toán.
2. Nhân viên mở một đơn "Chưa xử lý" và xem chi tiết.
3. Nhân viên bấm "Xác nhận".
4. Hệ thống kiểm tra lại đơn vẫn "Chưa xử lý", chuyển sang "Đã xác nhận" và lưu lịch sử trạng thái đơn.
5. Đơn chờ Nhân viên bàn giao cho vận chuyển (UC-40); đơn chưa xuất hiện trên Trang giả lập vận chuyển.

## Alternative Flows
- **3a. Từ chối đơn:** Nhân viên bấm "Từ chối", không nhập lý do → trong cùng một transaction, hệ thống chuyển đơn sang "Bị từ chối", cộng lại tồn kho, hoàn lượt của voucher hoặc khuyến mãi theo hóa đơn `[GD]` đã áp cho đơn, và lưu lịch sử trạng thái đơn. Hệ thống không lưu lý do; khách chỉ thấy trạng thái "Bị từ chối" trong UC-21.
- **3b. Đơn QR đã thanh toán bị từ chối:** hệ thống lưu ý Nhân viên rằng khách đã thanh toán; việc hoàn tiền làm ngoài hệ thống.

## Exceptions
- **E1. Đơn không còn "Chưa xử lý":** khách vừa hủy, hệ thống vừa tự hủy hoặc Nhân viên khác vừa xử lý → từ chối thao tác, báo trạng thái hiện tại.
- **E2. Xác nhận đơn QR chưa thanh toán:** hệ thống không cho xác nhận, báo "Đơn chưa được thanh toán" `[GD]`.

## Postconditions
- Đơn ở trạng thái "Đã xác nhận", chờ bàn giao vận chuyển (UC-40); hoặc ở "Bị từ chối" với tồn kho và lượt khuyến mãi đã hoàn.
- Lịch sử trạng thái đơn có thêm 1 dòng: trạng thái cũ, trạng thái mới, nguồn thay đổi, Nhân viên thực hiện, thời điểm.

## Acceptance Criteria

### AC-1: Xác nhận đơn COD
Given: đơn COD "Chưa xử lý"
When: Nhân viên bấm "Xác nhận"
Then: đơn chuyển sang "Đã xác nhận"
And: đơn chưa xuất hiện trên Trang giả lập vận chuyển
And: lịch sử trạng thái đơn ghi "Chưa xử lý → Đã xác nhận" kèm Nhân viên thực hiện

### AC-2: Từ chối đơn
Given: đơn "Chưa xử lý" có "Đỏ / M" số lượng 2, tồn kho "Đỏ / M" là 3, đơn dùng voucher còn 9 lượt
When: Nhân viên bấm "Từ chối"
Then: đơn chuyển sang "Bị từ chối"
And: hệ thống không yêu cầu nhập lý do và không lưu lý do
And: tồn kho "Đỏ / M" là 5
And: voucher còn 10 lượt

### AC-3: Từ chối đơn dùng khuyến mãi theo hóa đơn
Given: đơn "Chưa xử lý" áp khuyến mãi theo hóa đơn X, X đã dùng 5 lượt
When: Nhân viên từ chối đơn
Then: đơn chuyển sang "Bị từ chối"
And: khuyến mãi X còn 4 lượt đã dùng

### AC-4: Không xác nhận đơn QR chưa thanh toán
Given: đơn QR "Chưa xử lý", "Chưa thanh toán"
When: Nhân viên bấm "Xác nhận"
Then: hệ thống từ chối và báo "Đơn chưa được thanh toán"

### AC-5: Xác nhận đơn QR đã thanh toán
Given: đơn QR "Chưa xử lý", "Đã thanh toán"
When: Nhân viên bấm "Xác nhận"
Then: đơn chuyển sang "Đã xác nhận"

### AC-6: Đơn đã bị khách hủy
Given: Nhân viên đang mở đơn "Chưa xử lý", khách hủy đơn đó
When: Nhân viên bấm "Xác nhận"
Then: hệ thống từ chối, báo đơn đã ở trạng thái "Đã hủy"

### AC-7: Lọc danh sách theo trạng thái
Given: có 3 đơn "Chưa xử lý" và 2 đơn "Đã xác nhận"
When: Nhân viên lọc "Chưa xử lý"
Then: danh sách chỉ hiển thị 3 đơn "Chưa xử lý"

## Dependencies
- **Upstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR, UC-25 Xác nhận chuyển khoản
- **Downstream UC:** UC-40 Bàn giao đơn cho vận chuyển, UC-21 Theo dõi đơn hàng
- **External Systems:** —

## Notes
- BR-TUAN1 dùng tên "Nhân viên" cho vai trò xác nhận hoặc từ chối đơn.
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).
- Đơn bị hủy (khách hủy hoặc hệ thống tự hủy) hoặc bị từ chối thì cộng lại tồn kho và hoàn lượt voucher (đã chốt 15/11/2026).
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Xác nhận đơn chỉ chuyển đơn sang "Đã xác nhận"; đơn chỉ lên Trang giả lập vận chuyển khi Nhân viên bấm "Bàn giao vận chuyển" (UC-40) (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- Từ chối đơn không cần nhập lý do; hệ thống không lưu lý do (ERD không có cột này); khách chỉ thấy trạng thái "Bị từ chối" (đã chốt 15/11/2026).

### Giả định [GD]
- UC này gồm cả xem danh sách đơn, có phân trang và lọc theo trạng thái.
- Không cho xác nhận đơn QR khi chưa thanh toán.
- Từ chối đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn, cộng lại tồn kho và hoàn lượt voucher khi từ chối, phạm vi quyền của Admin
- v3 (2026-11-15): xác nhận đơn không còn tự đưa lên trang giả lập (bàn giao qua UC-40); thêm lưu lịch sử trạng thái đơn (theo ERD); hoàn lượt khuyến mãi theo hóa đơn khi từ chối
- v4 (2026-11-15): bỏ lý do từ chối đơn (không nhập, không lưu) theo data model v1
