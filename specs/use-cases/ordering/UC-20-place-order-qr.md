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
3. Trong cùng một transaction, hệ thống kiểm tra lại tồn kho, giá hiện tại, điều kiện và lượt còn lại của khuyến mãi được chọn; trừ tồn kho, tăng lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) `[GD]`, sinh mã đơn 8 ký tự Crockford Base32 không trùng, tạo đơn trạng thái "Chưa xử lý", thanh toán "Chưa thanh toán", hạn thanh toán = thời điểm đặt + 24 giờ, lưu lịch sử trạng thái đơn và xóa các dòng đã đặt khỏi giỏ `[GD]`.
4. Sau khi transaction thành công, hệ thống hiển thị mã VietQR gồm: tài khoản nhận chuyển khoản (hard-code), số tiền = tổng thanh toán, nội dung chuyển khoản = `SOBIE` + mã đơn; kèm số tài khoản, nội dung chuyển khoản dạng chữ để khách chuyển tay, và hạn thanh toán.
5. Khách chuyển khoản; SePay báo giao dịch qua webhook và hệ thống tự đối soát (UC-25), không cần ai bấm xác nhận.

## Alternative Flows
- **0a. Khách chưa đăng nhập:** như UC-19 (chuyển sang UC-02).
- **4a. Khách xem lại mã QR sau:** khách mở chi tiết đơn (UC-21) để xem lại mã QR khi đơn ở "Chưa xử lý", "Chưa thanh toán" và chưa quá hạn; ẩn QR khi đơn đã hủy `[GD]`.

## Exceptions
- **E1. Hết hàng khi xác nhận:** như UC-19 E1 — không tạo đơn, rollback toàn bộ.
- **E2. Voucher không hợp lệ:** như UC-19 E2.
- **E3. Quá 24 giờ chưa thanh toán:** Hệ thống tự hủy đơn (UC-24); mã QR không còn hiển thị `[GD]`.
- **E4. Giá hoặc mức giảm thay đổi khi xác nhận:** hệ thống tính lại theo giá và khuyến mãi hiện tại, chưa tạo đơn và yêu cầu khách xác nhận lại `[GD]`.
- **E5. Lỗi tạo đơn hoặc cập nhật giỏ:** rollback toàn bộ transaction; không tạo đơn, không trừ tồn kho, không tăng lượt khuyến mãi và các dòng giỏ vẫn giữ nguyên.

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
Given: đơn QR mã 7K3M9Q2X, tạm tính 500.000đ, giảm 50.000đ, phí vận chuyển 12.000đ; tổng thanh toán 462.000đ
When: hệ thống hiển thị mã QR
Then: mã QR chứa tài khoản nhận chuyển khoản của cửa hàng, số tiền 462.000đ và nội dung "SOBIE7K3M9Q2X"
And: trang hiển thị hạn thanh toán

### AC-3: Mã đơn đúng định dạng và không trùng
Given: hệ thống đã có đơn mã 7K3M9Q2X
When: khách đặt đơn mới và bộ sinh ngẫu nhiên lần đầu trả về 7K3M9Q2X
Then: hệ thống sinh lại mã khác
And: mã đơn mới gồm đúng 8 ký tự trong `0123456789ABCDEFGHJKMNPQRSTVWXYZ`

### AC-4: Xem lại mã QR
Given: đơn QR ở trạng thái "Chưa xử lý", "Chưa thanh toán" và còn trong hạn thanh toán
When: khách mở chi tiết đơn
Then: khách thấy lại mã QR và hạn thanh toán

### AC-5: Không hiện QR khi đơn đã thanh toán
Given: đơn QR đã ở trạng thái "Đã thanh toán"
When: khách mở chi tiết đơn
Then: mã QR không hiển thị

### AC-6: Hết hàng lúc xác nhận
Given: tồn kho không đủ cho một dòng trong giỏ
When: khách xác nhận đặt hàng QR
Then: không có đơn nào được tạo, tồn kho và lượt đã dùng của khuyến mãi không đổi

### AC-7: Đơn QR chỉ gắn 1 khuyến mãi, tiền giảm theo phần trăm
Given: tạm tính 400.000đ, khách nhập voucher V giảm 10%, V có lợi hơn khuyến mãi theo hóa đơn
When: khách xác nhận đặt hàng QR
Then: đơn chỉ gắn voucher V, tiền giảm 40.000đ
And: số tiền trong mã QR = 400.000đ − 40.000đ + phí vận chuyển (mặc định 12.000đ) = 372.000đ

### AC-8: Kiểm tra lại giá và khuyến mãi
Given: giá, mức giảm hoặc điều kiện áp dụng khuyến mãi cho đơn thay đổi sau khi khách xem trang thanh toán
When: khách xác nhận đặt hàng QR
Then: hệ thống tính lại tổng thanh toán và yêu cầu khách xác nhận lại
And: chưa tạo đơn, chưa trừ tồn kho hoặc tăng lượt khuyến mãi

### AC-9: Không hiện QR khi đơn đã hủy nhưng còn hạn
Given: đơn QR đã "Đã hủy", vẫn "Chưa thanh toán" và còn trong hạn thanh toán
When: khách mở lại chi tiết đơn
Then: mã QR không hiển thị

### AC-10: Lượt giảm nhưng khuyến mãi vẫn hợp lệ
Given: voucher còn 10 lượt lúc khách xem trang thanh toán, sau đó còn 9 lượt; giá, mức giảm và điều kiện áp dụng cho đơn vẫn giữ nguyên
When: khách xác nhận đặt hàng và hệ thống kiểm tra lại lượt trong transaction
Then: đơn được tạo với cùng mức giảm và tổng thanh toán, không yêu cầu xác nhận lại
And: lượt còn lại giảm từ 9 xuống 8 do đơn này, không ghi đè theo số lượt cũ

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng, UC-41 Quản lý sổ địa chỉ (qua bước nhận hàng như UC-19)
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận đơn hàng, UC-24 Tự hủy đơn chuyển khoản quá hạn, UC-25 Tự đối soát chuyển khoản qua webhook SePay
- **External Systems:** SePay (nhận giao dịch qua UC-25)

## Notes
- Luôn kiểm tra lượt còn lại trong transaction tạo đơn. Chỉ thay đổi số lượt còn lại, trong khi khuyến mãi vẫn hợp lệ và giá, mức giảm, điều kiện áp dụng cho đơn không đổi, không yêu cầu khách xác nhận lại.
- BR-GIAIDOAN1: đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy.
- Tài khoản nhận chuyển khoản lấy từ cấu hình cửa hàng hard-code; phí vận chuyển lấy từ biến môi trường, mặc định 12.000đ cho mọi đơn.
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn trong cùng một transaction (AGENTS.md).
- Thông tin nhận hàng: giống UC-19 (sổ địa chỉ UC-41, snapshot vào đơn).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026).
- Mã đơn: 8 ký tự ngẫu nhiên Crockford Base32, sinh bằng `secrets`, UNIQUE, trùng thì sinh lại; nội dung chuyển khoản = `SOBIE` + mã đơn (đã chốt 20/11/2026).
- Mọi mức giảm tính theo phần trăm; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026).
- Mỗi đơn áp tối đa 1 khuyến mãi (theo hóa đơn hoặc voucher); khuyến mãi theo sản phẩm được ghi theo từng dòng đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái (kể cả lúc tạo), hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- Nhận hàng theo sổ địa chỉ (đã chốt 27/11/2026) — xem UC-19 / UC-41.

### Giả định [GD]
- Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn; các dòng đã đặt được xóa khỏi giỏ.
- Khách chỉ xem lại được mã QR trong chi tiết đơn khi đơn "Chưa xử lý", "Chưa thanh toán" và còn trong hạn thanh toán; ẩn QR khi đơn đã thanh toán, đã hủy hoặc quá hạn.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn; mức giảm theo %, làm tròn ROUND_HALF_UP; mỗi đơn tối đa 1 khuyến mãi (theo ERD); lưu lịch sử trạng thái đơn (theo ERD); thêm AC-6
- v3 (2026-11-20): theo BR-GIAIDOAN1 — mã đơn Crockford Base32, nội dung `SOBIE` + mã đơn, đối soát qua SePay (UC-25), phí vận chuyển từ biến môi trường; thêm AC-3.
- v4 (2026-11-22): đưa xóa giỏ và kiểm tra lại giá, khuyến mãi vào transaction; bổ sung rollback và AC-7.
- v5 (2026-11-22): làm rõ công thức ví dụ QR với phí ship 12.000đ; chuẩn hóa số bước và AC-1 đến AC-8.
- v6 (2026-11-22): bổ sung kiểm tra trạng thái đơn khi xem lại QR, không hiển thị QR cho đơn đã hủy.
- v7 (2026-11-23): đồng bộ AC-4 và giả định với luồng 4a; thêm AC-9 kiểm tra ẩn QR cho đơn đã hủy nhưng còn hạn.
- v8 (2026-11-23): sửa điều kiện xác nhận lại trong AC-8; thêm AC-10 cho trường hợp lượt giảm nhưng voucher vẫn hợp lệ, giữ kiểm tra lượt trong transaction.
- v9 (2026-11-27): liên kết UC-41 / sổ địa chỉ (nhận hàng như UC-19).
