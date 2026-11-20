# UC-20: Đặt hàng thanh toán chuyển khoản QR

## Metadata
- **ID:** UC-20
- **Module:** ordering
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách chọn phương thức "Chuyển khoản qua mã QR" trên trang thanh toán và bấm "Xác nhận đặt hàng".

## Preconditions
- Khách đã đăng nhập.
- Giỏ hàng có ít nhất 1 dòng còn hàng.

## Main Flow
1. Khách thực hiện bước 1–4 như UC-19, chọn phương thức "Chuyển khoản qua mã QR".
2. Khách bấm "Xác nhận đặt hàng".
3. Trong cùng một transaction, hệ thống: kiểm tra lại tồn kho, trừ tồn kho, tăng lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) `[GD]`, sinh mã đơn 8 ký tự Crockford Base32 không trùng, tạo đơn trạng thái "Chưa xử lý", thanh toán "Chưa thanh toán", hạn thanh toán = thời điểm đặt + 24 giờ, và lưu lịch sử trạng thái đơn.
4. Hệ thống xóa các dòng đã đặt khỏi giỏ `[GD]`.
5. Hệ thống hiển thị mã VietQR gồm: tài khoản nhận chuyển khoản (hard-code), số tiền = tổng thanh toán, nội dung chuyển khoản = `SOBIE` + mã đơn; kèm số tài khoản, nội dung chuyển khoản dạng chữ để khách chuyển tay, và hạn thanh toán.
6. Khách chuyển khoản; SePay báo giao dịch qua webhook và hệ thống tự đối soát (UC-25), không cần ai bấm xác nhận.

## Alternative Flows
- **0a. Khách chưa đăng nhập:** như UC-19 (chuyển sang UC-02).
- **5a. Khách xem lại mã QR sau:** khách mở chi tiết đơn (UC-21) để xem lại mã QR khi đơn còn "Chưa thanh toán" và chưa quá hạn `[GD]`.

## Exceptions
- **E1. Hết hàng khi xác nhận:** như UC-19 E1 — không tạo đơn, rollback toàn bộ.
- **E2. Voucher không hợp lệ:** như UC-19 E2.
- **E3. Quá 24 giờ chưa thanh toán:** Hệ thống tự hủy đơn (UC-24); mã QR không còn hiển thị `[GD]`.

## Postconditions
- Đơn QR ở trạng thái "Chưa xử lý", "Chưa thanh toán", có hạn thanh toán; tồn kho đã bị trừ.
- Đơn lưu khuyến mãi theo sản phẩm của từng dòng (nếu có), khuyến mãi được áp cho đơn (tối đa 1), tiền giảm, phí vận chuyển và tổng thanh toán tại thời điểm đặt.
- Lịch sử trạng thái đơn có dòng đầu tiên: trạng thái mới "Chưa xử lý", nguồn là Khách hàng, thời điểm tạo đơn.

## Acceptance Criteria

### AC-1: Đặt hàng QR thành công
Given: khách đã đăng nhập, giỏ có "Đỏ / M" số lượng 1, tồn kho 5
When: khách chọn chuyển khoản QR và xác nhận đặt hàng lúc 10:00 ngày 20/11/2026
Then: hệ thống tạo đơn "Chưa xử lý", "Chưa thanh toán"
And: hạn thanh toán là 10:00 ngày 21/11/2026
And: tồn kho "Đỏ / M" còn 4
And: lịch sử trạng thái đơn có 1 dòng "→ Chưa xử lý"

### AC-2: Nội dung mã QR
Given: đơn QR mã 7K3M9Q2X, tổng thanh toán 480.000đ
When: hệ thống hiển thị mã QR
Then: mã QR chứa tài khoản nhận chuyển khoản của cửa hàng, số tiền 480.000đ và nội dung "SOBIE7K3M9Q2X"
And: trang hiển thị hạn thanh toán

### AC-2b: Mã đơn đúng định dạng và không trùng
Given: hệ thống đã có đơn mã 7K3M9Q2X
When: khách đặt đơn mới và bộ sinh ngẫu nhiên lần đầu trả về 7K3M9Q2X
Then: hệ thống sinh lại mã khác
And: mã đơn mới gồm đúng 8 ký tự trong `0123456789ABCDEFGHJKMNPQRSTVWXYZ`

### AC-3: Xem lại mã QR
Given: đơn QR "Chưa thanh toán", còn trong hạn
When: khách mở chi tiết đơn
Then: khách thấy lại mã QR và hạn thanh toán

### AC-4: Không hiện QR khi đơn đã thanh toán
Given: đơn QR đã ở trạng thái "Đã thanh toán"
When: khách mở chi tiết đơn
Then: mã QR không hiển thị

### AC-5: Hết hàng lúc xác nhận
Given: tồn kho không đủ cho một dòng trong giỏ
When: khách xác nhận đặt hàng QR
Then: không có đơn nào được tạo, tồn kho và lượt đã dùng của khuyến mãi không đổi

### AC-6: Đơn QR chỉ gắn 1 khuyến mãi, tiền giảm theo phần trăm
Given: tạm tính 400.000đ, khách nhập voucher V giảm 10%, V có lợi hơn khuyến mãi theo hóa đơn
When: khách xác nhận đặt hàng QR
Then: đơn chỉ gắn voucher V, tiền giảm 40.000đ
And: số tiền trong mã QR = 400.000đ − 40.000đ + phí vận chuyển (mặc định 12.000đ) = 372.000đ

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận đơn hàng, UC-24 Tự hủy đơn chuyển khoản quá hạn, UC-25 Tự đối soát chuyển khoản qua webhook SePay
- **External Systems:** SePay (nhận giao dịch qua UC-25)

## Notes
- BR-GIAIDOAN1: đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy.
- Tài khoản nhận chuyển khoản lấy từ cấu hình cửa hàng hard-code; phí vận chuyển lấy từ biến môi trường, mặc định 12.000đ cho mọi đơn.
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn trong cùng một transaction (AGENTS.md).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026).
- Mã đơn: 8 ký tự ngẫu nhiên Crockford Base32, sinh bằng `secrets`, UNIQUE, trùng thì sinh lại; nội dung chuyển khoản = `SOBIE` + mã đơn (đã chốt 20/11/2026).
- Mọi mức giảm tính theo phần trăm; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026).
- Mỗi đơn áp tối đa 1 khuyến mãi (theo hóa đơn hoặc voucher); khuyến mãi theo sản phẩm được ghi theo từng dòng đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái (kể cả lúc tạo), hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn; các dòng đã đặt được xóa khỏi giỏ.
- Khách xem lại được mã QR trong chi tiết đơn khi còn chưa thanh toán và chưa quá hạn; ẩn QR khi đơn đã thanh toán, đã hủy hoặc quá hạn.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn; mức giảm theo %, làm tròn ROUND_HALF_UP; mỗi đơn tối đa 1 khuyến mãi (theo ERD); lưu lịch sử trạng thái đơn (theo ERD); thêm AC-6
- v3 (2026-11-20): theo BR-GIAIDOAN1 — mã đơn Crockford Base32, nội dung `SOBIE` + mã đơn, đối soát qua SePay (UC-25), phí vận chuyển từ biến môi trường; thêm AC-2b
