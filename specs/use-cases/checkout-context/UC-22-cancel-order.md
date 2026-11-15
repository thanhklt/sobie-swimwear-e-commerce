# UC-22: Hủy đơn hàng

## Metadata
- **ID:** UC-22
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách bấm "Hủy đơn" trong chi tiết đơn.

## Preconditions
- Khách đã đăng nhập.
- Đơn thuộc khách và đang ở trạng thái "Chưa xử lý".

## Main Flow
1. Khách bấm "Hủy đơn".
2. Hệ thống hỏi xác nhận.
3. Khách xác nhận.
4. Trong cùng một transaction, hệ thống: kiểm tra lại đơn vẫn "Chưa xử lý", chuyển đơn sang "Đã hủy", cộng lại tồn kho các dòng hàng, hoàn lượt của voucher hoặc khuyến mãi theo hóa đơn `[GD]` đã áp cho đơn, và lưu lịch sử trạng thái đơn.
5. Hệ thống báo hủy thành công.

## Alternative Flows
- **2a. Đơn QR đã thanh toán:** hệ thống hiển thị lưu ý "Đơn đã được thanh toán. Sau khi hủy, vui lòng liên hệ cửa hàng để được hỗ trợ hoàn tiền"; khách vẫn hủy được. Hệ thống không xử lý hoàn tiền.
- **3a. Khách không xác nhận:** đơn giữ nguyên.

## Exceptions
- **E1. Đơn không còn "Chưa xử lý":** Nhân viên vừa xác nhận/từ chối hoặc hệ thống vừa tự hủy → hệ thống từ chối hủy, báo trạng thái hiện tại của đơn.
- **E2. Đơn không thuộc khách:** hệ thống từ chối.

## Postconditions
- Đơn ở trạng thái "Đã hủy"; tồn kho và lượt của khuyến mãi đã áp (voucher hoặc khuyến mãi theo hóa đơn) đã được hoàn.
- Lịch sử trạng thái đơn có thêm 1 dòng: "Chưa xử lý → Đã hủy", nguồn là Khách hàng, thời điểm.

## Acceptance Criteria

### AC-1: Hủy đơn chưa xử lý
Given: đơn "Chưa xử lý" có "Đỏ / M" số lượng 2, tồn kho "Đỏ / M" đang là 3
When: khách hủy đơn
Then: đơn chuyển sang "Đã hủy"
And: tồn kho "Đỏ / M" là 5

### AC-2: Hoàn lượt voucher
Given: đơn "Chưa xử lý" dùng voucher còn 9 lượt
When: khách hủy đơn
Then: voucher còn 10 lượt

### AC-3: Hoàn lượt khuyến mãi theo hóa đơn
Given: đơn "Chưa xử lý" áp khuyến mãi theo hóa đơn H, H đã dùng 5 lượt
When: khách hủy đơn
Then: H còn 4 lượt đã dùng

### AC-4: Lưu lịch sử trạng thái
Given: đơn "Chưa xử lý"
When: khách hủy đơn
Then: lịch sử trạng thái đơn ghi "Chưa xử lý → Đã hủy", nguồn là Khách hàng

### AC-5: Không hủy được đơn đã xác nhận
Given: đơn ở trạng thái "Đã xác nhận"
When: khách gửi yêu cầu hủy
Then: hệ thống từ chối, đơn vẫn "Đã xác nhận", tồn kho không đổi

### AC-6: Đơn QR đã thanh toán
Given: đơn QR "Chưa xử lý", "Đã thanh toán"
When: khách bấm "Hủy đơn"
Then: hệ thống hiển thị lưu ý liên hệ cửa hàng để hoàn tiền
And: sau khi khách xác nhận, đơn chuyển sang "Đã hủy" và không có giao dịch hoàn tiền nào được tạo

### AC-7: Tranh chấp với Nhân viên
Given: đơn "Chưa xử lý"
When: Nhân viên xác nhận đơn ngay trước khi khách bấm xác nhận hủy
Then: yêu cầu hủy bị từ chối, đơn ở "Đã xác nhận"

## Dependencies
- **Upstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR, UC-21 Theo dõi đơn hàng
- **Downstream UC:** UC-37 Xem dashboard (số đơn theo trạng thái)
- **External Systems:** Không có

## Notes
- BR-TUAN1: khách hủy đơn khi đơn chưa xử lý; khách đã chuyển khoản rồi mới hủy thì tự liên hệ cửa hàng, hệ thống không xử lý hoàn tiền (Out of Scope).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).
- Đơn bị hủy (khách hủy hoặc hệ thống tự hủy) hoặc bị từ chối thì cộng lại tồn kho và hoàn lượt voucher (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Hủy đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn, cộng lại tồn kho và hoàn lượt voucher khi hủy
- v3 (2026-11-15): hoàn lượt khuyến mãi theo hóa đơn khi hủy; lưu lịch sử trạng thái đơn (theo ERD); thêm AC-3, AC-4
