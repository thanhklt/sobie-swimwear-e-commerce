# UC-24: Tự hủy đơn chuyển khoản quá hạn

## Metadata
- **ID:** UC-24
- **Module:** ordering
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Hệ thống (tác vụ chạy định kỳ)

## Trigger
Tác vụ định kỳ chạy, mỗi 5 phút một lần `[GD]`.

## Preconditions
- Có đơn QR ở trạng thái "Chưa xử lý", "Chưa thanh toán", thời điểm hiện tại ≥ thời điểm đặt + 24 giờ.

## Main Flow
1. Hệ thống tìm các đơn QR "Chưa xử lý", "Chưa thanh toán" đã quá 24 giờ kể từ lúc đặt.
2. Với từng đơn, trong một transaction: kiểm tra lại đơn vẫn "Chưa xử lý" và "Chưa thanh toán", chuyển sang "Đã hủy" với lý do "Quá hạn thanh toán", cộng lại tồn kho, hoàn lượt của voucher hoặc khuyến mãi theo hóa đơn `[GD]` đã áp cho đơn, và lưu lịch sử trạng thái đơn với nguồn là Hệ thống.
3. Khách thấy đơn ở "Đã hủy" trong UC-21; mã QR không còn hiển thị.

## Alternative Flows
- **1a. Không có đơn quá hạn:** tác vụ kết thúc, không thay đổi gì.

## Exceptions
- **E1. Thanh toán được xác nhận đúng lúc tự hủy:** nếu UC-25 đã ghi nhận "Đã thanh toán" trước khi transaction tự hủy chạy, đơn không bị hủy.
- **E2. Lỗi khi hủy một đơn:** rollback riêng đơn đó, ghi log, các đơn khác vẫn được xử lý; lần chạy sau thử lại.

## Postconditions
- Mọi đơn QR quá 24 giờ chưa thanh toán ở trạng thái "Đã hủy"; tồn kho và lượt của khuyến mãi đã áp (voucher hoặc khuyến mãi theo hóa đơn) đã hoàn.
- Lịch sử trạng thái mỗi đơn bị hủy có thêm 1 dòng: "Chưa xử lý → Đã hủy", nguồn là Hệ thống, thời điểm.

## Acceptance Criteria

### AC-1: Hủy đơn quá 24 giờ
Given: đơn QR đặt lúc 10:00 ngày 20/11/2026, "Chưa xử lý", "Chưa thanh toán", có "Đỏ / M" số lượng 1, tồn kho "Đỏ / M" là 4
When: tác vụ chạy lúc 10:05 ngày 21/11/2026
Then: đơn chuyển sang "Đã hủy" với lý do "Quá hạn thanh toán"
And: tồn kho "Đỏ / M" là 5

### AC-2: Chưa đủ 24 giờ thì không hủy
Given: đơn QR đặt lúc 10:00 ngày 20/11/2026, "Chưa thanh toán"
When: tác vụ chạy lúc 09:59 ngày 21/11/2026
Then: đơn vẫn "Chưa xử lý"

### AC-3: Đơn đã thanh toán không bị hủy
Given: đơn QR đặt quá 24 giờ nhưng đã "Đã thanh toán"
When: tác vụ chạy
Then: đơn không bị hủy

### AC-4: Đơn COD không bị ảnh hưởng
Given: đơn COD "Chưa xử lý" đặt quá 24 giờ
When: tác vụ chạy
Then: đơn COD vẫn "Chưa xử lý"

### AC-5: Hoàn lượt voucher
Given: đơn QR quá hạn dùng voucher còn 9 lượt
When: tác vụ hủy đơn
Then: voucher còn 10 lượt

### AC-6: Hoàn lượt khuyến mãi theo hóa đơn
Given: đơn QR quá hạn áp khuyến mãi theo hóa đơn H, H đã dùng 5 lượt
When: tác vụ hủy đơn
Then: H còn 4 lượt đã dùng

### AC-7: Lưu lịch sử trạng thái
Given: đơn QR quá hạn "Chưa xử lý"
When: tác vụ hủy đơn
Then: lịch sử trạng thái đơn ghi "Chưa xử lý → Đã hủy", nguồn là Hệ thống

## Dependencies
- **Upstream UC:** UC-20 Đặt hàng thanh toán chuyển khoản QR, UC-25 Tự đối soát chuyển khoản qua webhook SePay
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-37 Xem dashboard
- **External Systems:** Không có

## Notes
- BR-GIAIDOAN1: đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy.
- Thời gian lưu và so sánh ở UTC; chỉ đổi sang Asia/Ho_Chi_Minh khi hiển thị (AGENTS.md).
- Độ trễ hủy tối đa bằng chu kỳ chạy của tác vụ.

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026: thêm "Chờ lấy hàng", bỏ "Bị từ chối").
- Đơn bị hủy (khách hủy, Nhân viên hủy hoặc hệ thống tự hủy) thì cộng lại tồn kho và hoàn lượt voucher (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Tác vụ chạy mỗi 5 phút.
- Tự hủy cũng hoàn lượt của khuyến mãi theo hóa đơn đã áp (voucher đã chốt).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn, cộng lại tồn kho và hoàn lượt voucher khi tự hủy
- v3 (2026-11-15): hoàn lượt khuyến mãi theo hóa đơn khi tự hủy; lưu lịch sử trạng thái đơn (theo ERD); thêm AC-6, AC-7
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — thêm trạng thái "Chờ lấy hàng", bỏ "Bị từ chối"; UC-25 đổi thành đối soát qua webhook SePay
