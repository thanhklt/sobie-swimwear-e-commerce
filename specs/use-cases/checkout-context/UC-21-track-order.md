# UC-21: Theo dõi đơn hàng

## Metadata
- **ID:** UC-21
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách mở trang "Đơn hàng của tôi".

## Preconditions
- Khách đã đăng nhập.

## Main Flow
1. Hệ thống hiển thị danh sách đơn của khách, mới nhất trước `[GD]`, có phân trang: mã đơn, ngày đặt, tổng thanh toán, phương thức thanh toán, trạng thái đơn, trạng thái thanh toán (đơn QR).
2. Khách chọn một đơn.
3. Hệ thống hiển thị chi tiết: các dòng hàng (tên, màu, size, số lượng, đơn giá), tạm tính, mức giảm, phí vận chuyển, tổng thanh toán, thông tin nhận hàng, trạng thái đơn hiện tại.

## Alternative Flows
- **3a. Đơn QR chưa thanh toán, còn hạn:** chi tiết hiển thị thêm mã QR và hạn thanh toán (UC-20).
- **3b. Đơn "Chưa xử lý":** chi tiết hiển thị nút "Hủy đơn" (UC-22).
- **3c. Đơn "Giao thành công":** chi tiết hiển thị liên kết xem hóa đơn (UC-27).
- **1a. Chưa có đơn nào:** hiển thị "Bạn chưa có đơn hàng nào".

## Exceptions
- **E1. Xem đơn của người khác:** khách mở đơn không thuộc tài khoản mình → hệ thống từ chối, báo không tìm thấy đơn.

## Postconditions
- Không thay đổi dữ liệu.

## Acceptance Criteria

### AC-1: Danh sách đơn của khách
Given: khách A có 3 đơn, khách B có 2 đơn
When: khách A mở "Đơn hàng của tôi"
Then: chỉ thấy 3 đơn của mình, đơn mới nhất ở đầu

### AC-2: Chi tiết đơn
Given: đơn của khách có 2 dòng hàng, mức giảm 50.000đ, phí vận chuyển 30.000đ
When: khách mở chi tiết đơn
Then: thấy đủ 2 dòng hàng, tạm tính, mức giảm, phí vận chuyển, tổng thanh toán và trạng thái đơn

### AC-3: Trạng thái cập nhật khi giao hàng
Given: đơn đang "Đã xác nhận"
When: Nhân viên bàn giao đơn cho vận chuyển (UC-40), sau đó Trang giả lập vận chuyển bấm "Đã giao" (UC-36)
Then: khách mở lại chi tiết đơn lần lượt thấy trạng thái "Đang giao" rồi "Giao thành công"

### AC-4: Không xem được đơn của người khác
Given: đơn DH0002 thuộc khách B
When: khách A mở chi tiết DH0002
Then: hệ thống báo không tìm thấy đơn

### AC-5: Nút hủy chỉ hiện khi "Chưa xử lý"
Given: đơn ở trạng thái "Đã xác nhận"
When: khách mở chi tiết đơn
Then: không có nút "Hủy đơn"

## Dependencies
- **Upstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR, UC-23 Xác nhận hoặc từ chối đơn, UC-40 Bàn giao đơn cho vận chuyển, UC-36 Cập nhật trạng thái giao hàng
- **Downstream UC:** UC-22 Hủy đơn hàng, UC-27 Xem hóa đơn
- **External Systems:** Không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung). Trạng thái đơn hiển thị phải phản ánh cập nhật mới nhất từ trang giả lập.

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).

### Giả định [GD]
- Danh sách đơn sắp xếp mới nhất trước, có phân trang.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): "Đang giao" do Nhân viên bàn giao (UC-40), trang giả lập chỉ cập nhật kết quả giao (UC-36); sửa AC-3
