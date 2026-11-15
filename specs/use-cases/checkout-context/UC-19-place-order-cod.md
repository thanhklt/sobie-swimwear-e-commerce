# UC-19: Đặt hàng thanh toán COD

## Metadata
- **ID:** UC-19
- **Bounded Context:** checkout-context
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
1. Hệ thống mở trang thanh toán, điền sẵn họ tên, số điện thoại, địa chỉ nhận hàng từ hồ sơ khách `[GD]`.
2. Khách kiểm tra hoặc sửa thông tin nhận hàng.
3. Khách chọn phương thức "Thanh toán khi nhận hàng (COD)" và có thể nhập mã voucher.
4. Hệ thống tính và hiển thị: tạm tính (đã áp khuyến mãi theo sản phẩm trên từng dòng), mức giảm do UC-31 chọn (tối đa 1 khuyến mãi: theo hóa đơn hoặc voucher), phí vận chuyển cố định, tổng thanh toán. Mọi mức giảm tính theo phần trăm, tiền làm tròn `ROUND_HALF_UP` về số nguyên VND.
5. Khách bấm "Xác nhận đặt hàng".
6. Trong cùng một transaction, hệ thống: kiểm tra lại tồn kho từng dòng, trừ tồn kho, tăng lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) `[GD]`, tạo đơn ở trạng thái "Chưa xử lý" với phương thức COD, và lưu lịch sử trạng thái đơn.
7. Hệ thống xóa các dòng đã đặt khỏi giỏ `[GD]` và hiển thị trang đặt hàng thành công kèm mã đơn.

## Alternative Flows
- **0a. Khách chưa đăng nhập:** bấm "Đặt hàng" thì chuyển sang UC-02 Đăng nhập; đăng nhập xong quay lại trang thanh toán với giỏ đã gộp.
- **3a. Không nhập voucher:** UC-31 chỉ xét khuyến mãi theo giá trị hóa đơn.
- **4a. Không có khuyến mãi theo hóa đơn hay voucher nào áp được:** mức giảm bằng 0; đơn không gắn khuyến mãi nào.

## Exceptions
- **E1. Hết hàng khi xác nhận:** một dòng không còn đủ tồn kho → không tạo đơn, rollback toàn bộ transaction, báo dòng nào thiếu hàng.
- **E2. Voucher không hợp lệ:** UC-31 báo lỗi; khách sửa hoặc bỏ voucher rồi đặt lại.
- **E3. Thiếu thông tin nhận hàng:** họ tên, số điện thoại hoặc địa chỉ trống → không cho xác nhận, báo trường thiếu.
- **E4. Giá hoặc mức giảm thay đổi trước khi xác nhận:** hệ thống tính lại theo giá hiện tại, báo khách và yêu cầu xác nhận lại `[GD]`.

## Postconditions
- Đơn COD ở trạng thái "Chưa xử lý", tồn kho các biến thể đã bị trừ, tồn kho không âm.
- Đơn lưu lại thông tin nhận hàng, đơn giá từng dòng, khuyến mãi theo sản phẩm của từng dòng (nếu có), khuyến mãi được áp cho đơn (tối đa 1), tiền giảm, phí vận chuyển và tổng thanh toán tại thời điểm đặt.
- Lịch sử trạng thái đơn có dòng đầu tiên: trạng thái mới "Chưa xử lý", nguồn là Khách hàng, thời điểm tạo đơn.

## Acceptance Criteria

### AC-1: Đặt hàng COD thành công
Given: khách đã đăng nhập, giỏ có "Đỏ / M" số lượng 2, tồn kho 5
When: khách chọn COD và xác nhận đặt hàng
Then: hệ thống tạo đơn trạng thái "Chưa xử lý", phương thức COD
And: tồn kho "Đỏ / M" còn 3
And: giỏ hàng không còn dòng "Đỏ / M"
And: lịch sử trạng thái đơn có 1 dòng "→ Chưa xử lý"

### AC-2: Tổng thanh toán đúng công thức
Given: tạm tính sau khuyến mãi theo sản phẩm = 500.000đ, UC-31 chọn khuyến mãi theo hóa đơn giảm 10%, phí vận chuyển cố định = 30.000đ
When: khách mở trang thanh toán
Then: tiền giảm hiển thị 50.000đ
And: tổng thanh toán hiển thị 480.000đ
And: đơn tạo ra lưu tổng thanh toán 480.000đ

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
Given: khách xóa trống số điện thoại nhận hàng
When: khách xác nhận đặt hàng
Then: hệ thống không tạo đơn và báo thiếu số điện thoại

### AC-8: Hai khách tranh nhau sản phẩm cuối
Given: "Đỏ / M" còn 1, hai khách cùng có 1 "Đỏ / M" trong giỏ
When: cả hai xác nhận đặt hàng gần như cùng lúc
Then: chỉ một đơn được tạo
And: tồn kho "Đỏ / M" là 0, không âm

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận hoặc từ chối đơn
- **External Systems:** Không có

## Notes
- Phí vận chuyển cố định lấy từ cấu hình cửa hàng hard-code (BR-TUAN1, Constraints chung).
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn chạy trong cùng một transaction (AGENTS.md).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).
- Mọi mức giảm tính theo phần trăm; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026).
- Mỗi đơn áp tối đa 1 khuyến mãi (theo hóa đơn hoặc voucher); khuyến mãi theo sản phẩm được ghi theo từng dòng đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái (kể cả lúc tạo), hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Thông tin nhận hàng được điền sẵn từ hồ sơ khách, khách sửa được cho riêng đơn này.
- Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn.
- Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công.
- Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): mức giảm theo %, làm tròn ROUND_HALF_UP; mỗi đơn tối đa 1 khuyến mãi, khuyến mãi theo sản phẩm ghi theo dòng (theo ERD); lưu lịch sử trạng thái đơn (theo ERD); thêm AC-3, AC-4
