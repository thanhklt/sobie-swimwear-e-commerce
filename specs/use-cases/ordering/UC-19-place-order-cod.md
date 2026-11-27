# UC-19: Đặt hàng thanh toán COD

## Metadata
- **ID:** UC-19
- **Module:** ordering
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách bấm "Đặt hàng" trên trang giỏ hàng.

## Preconditions
- Khách đã đăng nhập.
- Giỏ hàng có ít nhất 1 dòng còn hàng.

## Main Flow
1. Hệ thống mở trang thanh toán, điền sẵn thông tin nhận hàng từ **địa chỉ mặc định** trong sổ địa chỉ của khách (UC-41). Nếu chưa có địa chỉ trong sổ, khách phải thêm địa chỉ trước khi đặt.
2. Khách kiểm tra địa chỉ đang chọn; có thể **Thay đổi** để chọn địa chỉ khác trong sổ, hoặc **Thêm địa chỉ** (lưu vào sổ theo UC-41, dùng cho đơn này và các lần sau).
3. Khách chọn phương thức "Thanh toán khi nhận hàng (COD)" và có thể nhập mã voucher.
4. Hệ thống tính và hiển thị: tạm tính (đã áp khuyến mãi theo sản phẩm trên từng dòng), mức giảm do UC-31 chọn (tối đa 1 khuyến mãi: theo hóa đơn hoặc voucher), phí vận chuyển cố định, tổng thanh toán. Mọi mức giảm tính theo phần trăm, tiền làm tròn `ROUND_HALF_UP` về số nguyên VND.
5. Khách bấm "Xác nhận đặt hàng".
6. Trong cùng một transaction, hệ thống kiểm tra lại tồn kho từng dòng, giá hiện tại, điều kiện và lượt còn lại của khuyến mãi được chọn; trừ tồn kho, tăng lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) `[GD]`, tạo đơn ở trạng thái "Chưa xử lý" với phương thức COD, lưu lịch sử trạng thái đơn và xóa các dòng đã đặt khỏi giỏ `[GD]`.
7. Sau khi transaction thành công, hệ thống hiển thị trang đặt hàng thành công kèm mã đơn.

## Alternative Flows
- **0a. Khách chưa đăng nhập:** bấm "Đặt hàng" thì chuyển sang UC-02 Đăng nhập; đăng nhập xong quay lại trang thanh toán với giỏ đã gộp.
- **3a. Không nhập voucher:** UC-31 chỉ xét khuyến mãi theo giá trị hóa đơn.
- **4a. Không có khuyến mãi theo hóa đơn hay voucher nào áp được:** mức giảm bằng 0; đơn không gắn khuyến mãi nào.

## Exceptions
- **E1. Hết hàng khi xác nhận:** một dòng không còn đủ tồn kho → không tạo đơn, rollback toàn bộ transaction, báo dòng nào thiếu hàng.
- **E2. Voucher không hợp lệ:** UC-31 báo lỗi; khách sửa hoặc bỏ voucher rồi đặt lại.
- **E3. Thiếu thông tin nhận hàng:** họ tên, số điện thoại hoặc địa chỉ trống → không cho xác nhận, báo trường thiếu.
- **E4. Giá hoặc mức giảm thay đổi trước khi xác nhận:** hệ thống tính lại theo giá hiện tại, báo khách và yêu cầu xác nhận lại `[GD]`.
- **E5. Khuyến mãi hết lượt hoặc không còn đủ điều kiện khi xác nhận:** hệ thống không tạo đơn, không trừ tồn kho hoặc tăng lượt khuyến mãi; cập nhật tổng thanh toán và yêu cầu khách xác nhận lại `[GD]`.
- **E6. Lỗi tạo đơn hoặc cập nhật giỏ:** rollback toàn bộ transaction; đơn, tồn kho, lượt khuyến mãi và giỏ giữ nguyên.

## Postconditions
- Đơn COD ở trạng thái "Chưa xử lý", tồn kho các biến thể đã bị trừ, tồn kho không âm.
- Đơn lưu lại thông tin nhận hàng, đơn giá từng dòng, khuyến mãi theo sản phẩm của từng dòng (nếu có), khuyến mãi được áp cho đơn (tối đa 1), tiền giảm, phí vận chuyển và tổng thanh toán tại thời điểm đặt.
- Lịch sử trạng thái đơn có dòng đầu tiên: trạng thái mới "Chưa xử lý", nguồn là Khách hàng, thời điểm tạo đơn.
- Nếu đặt hàng thất bại, không tạo đơn, không trừ tồn kho, không tăng lượt khuyến mãi và không xóa dòng giỏ.

## Acceptance Criteria

### AC-1: Đặt hàng COD thành công
Given: khách đã đăng nhập, giỏ có "Đỏ / M" số lượng 2, tồn kho 5
When: khách chọn COD và xác nhận đặt hàng
Then: hệ thống tạo đơn trạng thái "Chưa xử lý", phương thức COD
And: tồn kho "Đỏ / M" còn 3
And: giỏ hàng không còn dòng "Đỏ / M"
And: lịch sử trạng thái đơn có 1 dòng "→ Chưa xử lý"

### AC-2: Tổng thanh toán đúng công thức
Given: tạm tính sau khuyến mãi theo sản phẩm = 500.000đ, UC-31 chọn khuyến mãi theo hóa đơn giảm 10%, phí vận chuyển mặc định = 12.000đ
When: khách mở trang thanh toán
Then: tiền giảm hiển thị 50.000đ
And: tổng thanh toán hiển thị 462.000đ
And: đơn tạo ra lưu tổng thanh toán 462.000đ

### AC-3: Làm tròn tiền giảm
Given: tạm tính = 255.010đ, UC-31 chọn voucher giảm 5%
When: hệ thống tính tiền giảm
Then: tiền giảm = 12.751đ (12.750,5 làm tròn ROUND_HALF_UP)

### AC-4: Đơn chỉ gắn 1 khuyến mãi
Given: khách nhập voucher V giảm 10%, có khuyến mãi theo hóa đơn H giảm 5% đủ điều kiện
When: khách xác nhận đặt hàng
Then: đơn chỉ gắn voucher V
And: lượt đã dùng của V tăng 1, lượt đã dùng của H không đổi

### AC-5: Hết hàng lúc xác nhận
Given: giỏ có "Đỏ / M" số lượng 2, nhưng tồn kho vừa giảm còn 1
When: khách xác nhận đặt hàng
Then: không có đơn nào được tạo
And: tồn kho "Đỏ / M" vẫn là 1
And: lượt đã dùng của khuyến mãi không đổi

### AC-6: Chưa đăng nhập
Given: khách vãng lai có giỏ hàng
When: khách bấm "Đặt hàng"
Then: hệ thống chuyển sang trang đăng nhập
And: đăng nhập xong khách quay lại trang thanh toán

### AC-7: Thiếu thông tin nhận hàng
Given: khách chưa chọn đủ thông tin nhận hàng (thiếu địa chỉ hoặc để trống trường bắt buộc khi thêm địa chỉ)
When: khách xác nhận đặt hàng
Then: hệ thống không tạo đơn
And: báo trường thiếu / yêu cầu chọn hoặc thêm địa chỉ

### AC-12: Prefill địa chỉ mặc định
Given: khách có địa chỉ A mặc định và địa chỉ B trong sổ
When: khách mở trang thanh toán
Then: hệ thống điền sẵn thông tin nhận hàng theo A

### AC-13: Thêm địa chỉ tại checkout lưu sổ
Given: khách đang ở trang thanh toán
When: khách thêm địa chỉ C và xác nhận dùng C cho đơn
Then: C được lưu trong sổ địa chỉ (UC-41)
And: lần đặt sau C vẫn xuất hiện trong danh sách địa chỉ

### AC-8: Hai khách tranh nhau sản phẩm cuối
Given: "Đỏ / M" còn 1, hai khách cùng có 1 "Đỏ / M" trong giỏ
When: cả hai xác nhận đặt hàng gần như cùng lúc
Then: chỉ một đơn được tạo
And: tồn kho "Đỏ / M" là 0, không âm

### AC-9: Kiểm tra lại giá và khuyến mãi
Given: giá, mức giảm hoặc điều kiện áp dụng khuyến mãi cho đơn thay đổi sau khi khách xem trang thanh toán
When: khách xác nhận đặt hàng COD
Then: hệ thống tính lại tổng thanh toán và yêu cầu khách xác nhận lại
And: chưa tạo đơn, chưa trừ tồn kho hoặc tăng lượt khuyến mãi

### AC-10: Lỗi cập nhật giỏ khi tạo đơn
Given: dữ liệu đặt hàng hợp lệ nhưng xóa dòng giỏ thất bại
When: khách xác nhận đặt hàng COD
Then: transaction rollback; không tạo đơn, không trừ tồn kho, không tăng lượt khuyến mãi
And: các dòng giỏ vẫn còn

### AC-11: Lượt giảm nhưng khuyến mãi vẫn hợp lệ
Given: voucher còn 10 lượt lúc khách xem trang thanh toán, sau đó còn 9 lượt; giá, mức giảm và điều kiện áp dụng cho đơn vẫn giữ nguyên
When: khách xác nhận đặt hàng và hệ thống kiểm tra lại lượt trong transaction
Then: đơn được tạo với cùng mức giảm và tổng thanh toán, không yêu cầu xác nhận lại
And: lượt còn lại giảm từ 9 xuống 8 do đơn này, không ghi đè theo số lượt cũ

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng, UC-41 Quản lý sổ địa chỉ
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận đơn hàng
- **External Systems:** Không có

## Notes
- Luôn kiểm tra lượt còn lại trong transaction tạo đơn. Chỉ thay đổi số lượt còn lại, trong khi khuyến mãi vẫn hợp lệ và giá, mức giảm, điều kiện áp dụng cho đơn không đổi, không yêu cầu khách xác nhận lại.
- Phí vận chuyển là 1 mức cho mọi đơn, lấy từ biến môi trường, mặc định 12.000đ (BR-GIAIDOAN1, Constraints chung).
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn chạy trong cùng một transaction (AGENTS.md).
- Thông tin nhận hàng trên đơn là snapshot lúc đặt; không FK tới `shipping_address`.

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026: thêm "Chờ lấy hàng", bỏ "Bị từ chối").
- Mọi mức giảm tính theo phần trăm; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026).
- Mỗi đơn áp tối đa 1 khuyến mãi (theo hóa đơn hoặc voucher); khuyến mãi theo sản phẩm được ghi theo từng dòng đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái (kể cả lúc tạo), hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- Prefill / chọn / thêm địa chỉ từ sổ (UC-41); thêm địa chỉ lưu sổ (đã chốt 27/11/2026). Bỏ quy tắc «sửa chỉ cho đơn / không cập nhật hồ sơ».

### Giả định [GD]
- Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn.
- Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công.
- Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): mức giảm theo %, làm tròn ROUND_HALF_UP; mỗi đơn tối đa 1 khuyến mãi, khuyến mãi theo sản phẩm ghi theo dòng (theo ERD); lưu lịch sử trạng thái đơn (theo ERD); thêm AC-3, AC-4
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — thêm trạng thái "Chờ lấy hàng", bỏ "Bị từ chối"; phí vận chuyển lấy từ biến môi trường (mặc định 12.000đ)
- v5 (2026-11-22): thống nhất phí vận chuyển mặc định 12.000đ và cập nhật AC-2.
- v6 (2026-11-22): đưa xóa giỏ và kiểm tra lại giá, khuyến mãi vào transaction; bổ sung rollback và AC-9, AC-10.
- v7 (2026-11-22): làm rõ sửa thông tin nhận hàng chỉ áp dụng cho đơn đang đặt.
- v8 (2026-11-23): sửa điều kiện xác nhận lại trong AC-9; thêm AC-11 cho trường hợp lượt giảm nhưng voucher vẫn hợp lệ, giữ kiểm tra lượt trong transaction.
- v9 (2026-11-27): checkout dùng sổ địa chỉ (UC-41); prefill mặc định; thêm địa chỉ lưu sổ; AC-12, AC-13; bỏ «sửa chỉ cho đơn».
