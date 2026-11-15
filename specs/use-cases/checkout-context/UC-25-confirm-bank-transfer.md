# UC-25: Xác nhận chuyển khoản (trang giả lập)

## Metadata
- **ID:** UC-25
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-006
- **Status:** draft

## Actor
Trang giả lập chuyển khoản (người demo thao tác trên trang này, không cần đăng nhập)

## Trigger
Người demo mở trang giả lập chuyển khoản và bấm "Xác nhận đã chuyển khoản" cho một đơn QR.

## Preconditions
- Đơn QR tồn tại, ở trạng thái "Chưa xử lý", "Chưa thanh toán" và còn trong hạn 24 giờ.

## Main Flow
1. Người demo mở trang giả lập chuyển khoản; trang không yêu cầu đăng nhập.
2. Trang hiển thị danh sách các đơn QR "Chưa thanh toán"; mỗi đơn có nút "Xác nhận đã chuyển khoản".
3. Người demo bấm "Xác nhận đã chuyển khoản" cho một đơn.
4. Hệ thống kiểm tra đơn vẫn "Chưa xử lý", "Chưa thanh toán" và chưa quá hạn.
5. Hệ thống chuyển trạng thái thanh toán của đơn sang "Đã thanh toán" (số tiền coi như bằng tổng thanh toán của đơn). Trạng thái đơn không đổi nên không ghi lịch sử trạng thái đơn.
6. Đơn biến mất khỏi danh sách trên trang giả lập; khách thấy trạng thái thanh toán mới trong UC-21, mã QR không còn hiển thị.

## Alternative Flows
- **3a. Gửi trùng xác nhận:** đơn đã "Đã thanh toán" → hệ thống không thay đổi gì và trả kết quả thành công (idempotent) `[GD]`.

## Exceptions
- **E1. Đơn đã hủy hoặc đã quá hạn:** hệ thống từ chối ghi nhận, trả lý do; trang giả lập hiển thị lỗi.
- **E2. Mã đơn không tồn tại hoặc không phải đơn QR:** hệ thống từ chối.

## Postconditions
- Đơn QR ở trạng thái thanh toán "Đã thanh toán"; trạng thái đơn vẫn "Chưa xử lý" chờ Nhân viên xác nhận (UC-23).
- Lịch sử trạng thái đơn không có dòng mới (thay đổi trạng thái thanh toán không được ghi lịch sử).

## Acceptance Criteria

### AC-1: Trang không cần đăng nhập
Given: người demo chưa đăng nhập
When: người demo mở trang giả lập chuyển khoản
Then: trang hiển thị danh sách đơn QR chưa thanh toán, không chuyển tới trang đăng nhập

### AC-2: Chỉ hiển thị đơn QR chưa thanh toán
Given: đơn QR DH0001 "Chưa thanh toán", đơn QR DH0002 "Đã thanh toán", đơn COD DH0003
When: người demo mở trang giả lập chuyển khoản
Then: danh sách chỉ có DH0001

### AC-3: Xác nhận chuyển khoản thành công
Given: đơn QR DH0001 "Chưa xử lý", "Chưa thanh toán", tổng 480.000đ, còn hạn
When: người demo bấm "Xác nhận đã chuyển khoản" cho DH0001
Then: đơn DH0001 có trạng thái thanh toán "Đã thanh toán"
And: trạng thái đơn vẫn "Chưa xử lý"
And: DH0001 không còn trong danh sách của trang giả lập
And: lịch sử trạng thái đơn của DH0001 không có dòng mới

### AC-4: Đơn đã hủy
Given: đơn QR DH0001 đã "Đã hủy"
When: trang giả lập gửi xác nhận cho DH0001
Then: hệ thống từ chối, đơn vẫn "Đã hủy" và "Chưa thanh toán"

### AC-5: Gửi trùng
Given: đơn QR DH0001 đã "Đã thanh toán"
When: trang giả lập gửi lại xác nhận cho DH0001
Then: hệ thống không thay đổi dữ liệu và trả kết quả thành công

### AC-6: Website tự cập nhật
Given: khách đang theo dõi đơn QR DH0001 "Chưa thanh toán"
When: trang giả lập xác nhận chuyển khoản thành công
Then: khách mở lại chi tiết đơn thấy "Đã thanh toán" và không còn mã QR

## Dependencies
- **Upstream UC:** UC-20 Đặt hàng thanh toán chuyển khoản QR
- **Downstream UC:** UC-23 Xác nhận hoặc từ chối đơn, UC-24 Tự hủy đơn chuyển khoản quá hạn, UC-21 Theo dõi đơn hàng
- **External Systems:** Trang giả lập chuyển khoản

## Notes
- BR-TUAN1: trang giả lập xác nhận chuyển khoản tự động cập nhật trạng thái đơn về website; không kết nối ngân hàng thật (Out of Scope).
- UC này thuộc BR-006 nhưng đặt trong checkout-context vì nó thay đổi trạng thái thanh toán của đơn.

### Quyết định đã chốt
- Trang giả lập chuyển khoản giống trang giả lập vận chuyển: không cần đăng nhập, 1 trang duy nhất liệt kê đơn QR chưa thanh toán, mỗi đơn có nút "Xác nhận đã chuyển khoản" (đã chốt 15/11/2026).
- Người demo chỉ bấm nút, không nhập số tiền; số tiền ghi nhận bằng tổng thanh toán của đơn (đã chốt 15/11/2026).
- Lịch sử (`order_status_history`) chỉ lưu thay đổi trạng thái đơn; thay đổi trạng thái thanh toán không được ghi lịch sử (đã chốt 15/11/2026). Không lưu thời điểm thanh toán (ERD không có cột này).

### Giả định [GD]
- Gửi trùng xác nhận cho đơn đã thanh toán là idempotent.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt trang giả lập không cần đăng nhập, 1 trang, chỉ bấm nút xác nhận (bỏ nhập và kiểm tra số tiền); thêm lưu lịch sử (theo ERD)
- v3 (2026-11-15): không ghi thay đổi trạng thái thanh toán vào lịch sử, không lưu thời điểm thanh toán (theo data model v1)
