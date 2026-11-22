# UC-22: Hủy đơn hàng

## Metadata
- **ID:** UC-22
- **Module:** ordering
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
- Khách hàng (hủy đơn của mình)
- Nhân viên (hủy đơn trong khu vực quản trị)

## Trigger
- Khách bấm "Hủy đơn" trong chi tiết đơn của mình; hoặc
- Nhân viên bấm "Hủy đơn" trong chi tiết đơn ở trang quản lý đơn hàng.

## Preconditions
- Người thao tác đã đăng nhập.
- Khách hàng: đơn thuộc khách và đang "Chưa xử lý".
- Nhân viên: đơn đang "Chưa xử lý", "Đã xác nhận" hoặc "Chờ lấy hàng" (đơn vị vận chuyển chưa nhận hàng).

## Main Flow
1. Hệ thống chỉ hiển thị nút "Hủy đơn" cho Khách hàng trên đơn của mình ở trạng thái "Chưa xử lý"; cho Nhân viên trên đơn "Chưa xử lý", "Đã xác nhận" hoặc "Chờ lấy hàng". Người thao tác bấm nút này; yêu cầu gửi trực tiếp vẫn phải được kiểm tra quyền và trạng thái ở bước 4.
2. Hệ thống hiển thị popup xác nhận hủy:
   - Khách hàng: chỉ hỏi xác nhận.
   - Nhân viên: bắt buộc nhập lý do hủy, tối đa 500 ký tự `[GD]`.
3. Người thao tác bấm xác nhận.
4. Trong cùng một transaction, hệ thống: khóa và kiểm tra lại trạng thái đơn còn được phép hủy theo vai trò, chuyển đơn sang "Đã hủy", cộng lại tồn kho các dòng hàng, hoàn lượt của voucher hoặc khuyến mãi theo hóa đơn đã áp cho đơn, và lưu lịch sử trạng thái đơn (kèm lý do nếu Nhân viên hủy).
5. Hệ thống báo hủy thành công. Nếu đơn đang "Chờ lấy hàng", đơn biến mất khỏi Trang giả lập vận chuyển.

## Alternative Flows
- **2a. Đơn QR đã thanh toán:** popup hiển thị thêm lưu ý "Đơn đã được thanh toán. Việc hoàn tiền xử lý ngoài hệ thống" (với khách: "vui lòng liên hệ cửa hàng để được hỗ trợ hoàn tiền"); vẫn hủy được. Hệ thống không xử lý hoàn tiền.
- **3a. Người thao tác đóng popup hoặc không xác nhận:** đơn giữ nguyên.

## Exceptions
- **E1. Khách hủy đơn không còn "Chưa xử lý":** Nhân viên vừa xác nhận hoặc hủy, hay hệ thống vừa tự hủy → hệ thống từ chối, báo trạng thái hiện tại của đơn.
- **E2. Nhân viên hủy đơn đã được đơn vị vận chuyển nhận hàng hoặc đã kết thúc:** đơn ở "Đang giao", "Giao thành công", "Giao không thành công" hoặc "Đã hủy" → hệ thống từ chối, không hiển thị nút "Hủy đơn" cho các trạng thái này.
- **E3. Lý do hủy không hợp lệ:** Nhân viên để trống hoặc nhập quá 500 ký tự `[GD]` → hệ thống báo lỗi ở ô lý do, không hủy.
- **E4. Đơn không thuộc khách:** hệ thống từ chối.
- **E5. Lỗi hoàn tồn kho, hoàn lượt hoặc lưu lịch sử:** rollback toàn bộ transaction; trạng thái đơn và dữ liệu liên quan giữ nguyên, thông báo hủy không thành công.
- **E6. Yêu cầu hủy lặp:** đơn đã "Đã hủy" không được xử lý lại; không hoàn tồn kho hoặc lượt khuyến mãi lần thứ hai.

## Postconditions
- Đơn ở trạng thái "Đã hủy"; tồn kho và lượt của khuyến mãi đã áp (voucher hoặc khuyến mãi theo hóa đơn) đã được hoàn.
- Lịch sử trạng thái đơn có thêm 1 dòng: trạng thái cũ → "Đã hủy", nguồn (Khách hàng hoặc Nhân viên), người hủy, thời điểm; với Nhân viên có thêm lý do hủy.
- Lý do hủy chỉ Nhân viên xem được; khách chỉ thấy đơn "Đã hủy".

## Acceptance Criteria

### AC-1: Khách hủy đơn chưa xử lý
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

### AC-4: Lưu lịch sử khi khách hủy
Given: đơn "Chưa xử lý"
When: khách hủy đơn
Then: lịch sử trạng thái đơn ghi "Chưa xử lý → Đã hủy", nguồn là Khách hàng

### AC-5: Khách không hủy được đơn đã xác nhận
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
Then: yêu cầu hủy của khách bị từ chối, đơn ở "Đã xác nhận"

### AC-8: Nhân viên hủy đơn kèm lý do
Given: đơn "Đã xác nhận" có "Đỏ / M" số lượng 1, tồn kho "Đỏ / M" là 4
When: Nhân viên bấm "Hủy đơn", nhập lý do "Khách gọi điện đổi ý" và xác nhận
Then: đơn chuyển sang "Đã hủy"
And: tồn kho "Đỏ / M" là 5
And: lịch sử trạng thái đơn ghi "Đã xác nhận → Đã hủy", nguồn là Nhân viên, kèm lý do "Khách gọi điện đổi ý"

### AC-9: Bắt buộc nhập lý do
Given: đơn "Chưa xử lý"
When: Nhân viên bấm "Hủy đơn" và xác nhận khi ô lý do để trống
Then: hệ thống báo lỗi ở ô lý do, đơn vẫn "Chưa xử lý"

### AC-10: Nhân viên hủy đơn "Chờ lấy hàng"
Given: đơn "Chờ lấy hàng" đang hiện trên Trang giả lập vận chuyển
When: Nhân viên hủy đơn với lý do "Hết bao bì"
Then: đơn chuyển sang "Đã hủy" và không còn trên Trang giả lập vận chuyển

### AC-11: Không hủy được sau khi vận chuyển đã nhận hàng
Given: đơn "Đang giao"
When: Nhân viên mở chi tiết đơn
Then: không có nút "Hủy đơn"
And: request hủy gửi trực tiếp bị từ chối, đơn vẫn "Đang giao"

### AC-12: Khách không thấy lý do hủy
Given: Nhân viên đã hủy đơn của khách A với lý do "Nghi ngờ đơn ảo"
When: khách A mở chi tiết đơn (UC-21)
Then: khách thấy trạng thái "Đã hủy" và không thấy lý do

### AC-13: Hủy thất bại phải rollback
Given: đơn được phép hủy nhưng việc hoàn tồn kho hoặc lượt khuyến mãi thất bại
When: người thao tác xác nhận hủy
Then: transaction rollback; đơn, tồn kho, lượt khuyến mãi và lịch sử giữ nguyên

### AC-14: Hủy lặp không hoàn dữ liệu lần hai
Given: đơn đã "Đã hủy" và đã hoàn tồn kho, lượt khuyến mãi
When: người thao tác gửi lại yêu cầu hủy
Then: hệ thống từ chối và không hoàn tồn kho hoặc lượt khuyến mãi thêm lần nữa

## Dependencies
- **Upstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR, UC-21 Theo dõi đơn hàng, UC-23 Xác nhận đơn hàng, UC-40 Bàn giao đơn cho vận chuyển
- **Downstream UC:** UC-37 Xem dashboard (số đơn theo trạng thái), UC-39 Xem tồn kho
- **External Systems:** Không có

## Notes
- BR-GIAIDOAN1 (BR-003): khách hủy đơn khi đơn chưa xử lý; Nhân viên hủy đơn trước khi đơn vị vận chuyển nhận hàng, qua popup nhập lý do; đơn hủy tự cộng lại tồn kho. Hoàn tiền nằm ngoài hệ thống (Out of Scope).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026).
- Không có thao tác "Từ chối" riêng; Nhân viên chỉ có nút "Hủy đơn" (đã chốt 20/11/2026).
- Khách chỉ hủy được đơn "Chưa xử lý"; Nhân viên hủy được đơn "Chưa xử lý", "Đã xác nhận", "Chờ lấy hàng" (đã chốt 20/11/2026).
- Nhân viên hủy phải nhập lý do qua popup; khách không thấy lý do (đã chốt 20/11/2026).
- Đơn bị hủy thì cộng lại tồn kho và hoàn lượt voucher (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- Lý do hủy lưu ở cột ghi chú của lịch sử trạng thái đơn (`order_status_history_note`) (đã chốt 20/11/2026, data model v2, Q23e).

### Giả định [GD]
- Hủy đơn cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt).
- Lý do hủy tối đa 500 ký tự.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn, cộng lại tồn kho và hoàn lượt voucher khi hủy
- v3 (2026-11-15): hoàn lượt khuyến mãi theo hóa đơn khi hủy; lưu lịch sử trạng thái đơn (theo ERD); thêm AC-3, AC-4
- v4 (2026-11-20): thêm actor Nhân viên — hủy được đến trước khi đơn vị vận chuyển nhận hàng, bắt buộc nhập lý do qua popup, khách không thấy lý do; bỏ "Bị từ chối"; thêm AC-8 → AC-12
- v5 (2026-11-20): theo data model v2 — chốt lý do hủy lưu ở `order_status_history_note`
- v6 (2026-11-22): bổ sung rollback khi hủy thất bại và chống xử lý hủy lặp; thêm AC-13, AC-14.
- v7 (2026-11-22): làm rõ điều kiện hiển thị nút hủy theo vai trò và kiểm tra yêu cầu trực tiếp.
- v8 (2026-11-22): đưa giới hạn lý do hủy 500 ký tự vào luồng và ngoại lệ.
