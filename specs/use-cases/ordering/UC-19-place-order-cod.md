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
1. Hệ thống mở trang thanh toán với các trường tên người nhận, địa chỉ nhận hàng (số nhà, đường; phường/xã; tỉnh/thành phố; quốc gia) và số điện thoại nhận hàng. Nút "Sử dụng thông tin hồ sơ" chỉ dùng được khi hồ sơ đã lưu đủ họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng hợp lệ. Hệ thống chỉ sao chép dữ liệu hồ sơ khi khách bấm nút.
2. Khách nhập thông tin nhận hàng hoặc bấm "Sử dụng thông tin hồ sơ" để sao chép họ tên, địa chỉ và số điện thoại từ hồ sơ vào các trường tương ứng. Khách vẫn có thể sửa từng trường sau khi sao chép. Thông tin cuối cùng trên biểu mẫu được dùng cho riêng đơn hàng.
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
- **E3. Thiếu thông tin nhận hàng:** nếu thiếu tên người nhận, số điện thoại nhận hàng hoặc một phần bắt buộc của địa chỉ nhận hàng, hệ thống báo trường thiếu và không tạo đơn.
- **E4. Giá hoặc mức giảm thay đổi trước khi xác nhận:** hệ thống tính lại theo giá hiện tại, báo khách và yêu cầu xác nhận lại `[GD]`.

## Postconditions
- Đơn COD ở trạng thái "Chưa xử lý", tồn kho các biến thể đã bị trừ, tồn kho không âm.
- Đơn lưu tên người nhận, số điện thoại nhận hàng và địa chỉ nhận hàng theo giá trị trên biểu mẫu lúc xác nhận. Hồ sơ tài khoản giữ nguyên khi đặt hàng.
- Đơn lưu đơn giá từng dòng, khuyến mãi theo sản phẩm của từng dòng (nếu có), khuyến mãi được áp cho đơn (tối đa 1), tiền giảm, phí vận chuyển và tổng thanh toán tại thời điểm đặt.
- Lịch sử trạng thái đơn có dòng đầu tiên: trạng thái mới "Chưa xử lý", nguồn là Khách hàng, thời điểm tạo đơn.

## Acceptance Criteria

### AC-1: Đặt hàng COD thành công
Given: khách đã đăng nhập, giỏ có "Đỏ / M" số lượng 2, tồn kho 5
When: khách điền đủ thông tin nhận hàng, chọn COD và xác nhận đặt hàng
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

### AC-9: Sao chép thông tin nhận hàng từ hồ sơ khi khách yêu cầu
Given: khách đã lưu hồ sơ có đủ họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng hợp lệ
When: khách mở trang thanh toán
Then: nút "Sử dụng thông tin hồ sơ" dùng được và hệ thống chờ khách bấm trước khi sao chép thông tin
And: khi khách bấm, ba trường tên người nhận, số điện thoại và địa chỉ nhận hàng được điền từ hồ sơ

### AC-10: Dùng thông tin nhận hàng khác với hồ sơ
Given: khách đã bấm "Sử dụng thông tin hồ sơ"
When: khách sửa thông tin nhận hàng rồi xác nhận với dữ liệu hợp lệ
Then: đơn lưu tên người nhận, số điện thoại và địa chỉ theo biểu mẫu lúc xác nhận
And: hồ sơ tài khoản giữ nguyên

### AC-11: Hồ sơ chưa đầy đủ vẫn đặt hàng bằng cách nhập tay
Given: hồ sơ đã có họ tên, số điện thoại và địa chỉ nhận hàng nhưng thiếu ngày sinh
When: khách mở trang thanh toán
Then: nút "Sử dụng thông tin hồ sơ" không dùng được
And: khách vẫn đặt được hàng khi nhập tay đầy đủ thông tin nhận hàng hợp lệ và đáp ứng các điều kiện đặt hàng khác

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-04 Cập nhật hồ sơ khách hàng, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận đơn hàng
- **External Systems:** Không có

## Notes
- Phí vận chuyển là 1 mức cho mọi đơn, lấy từ biến môi trường, mặc định 12.000đ (BR-GIAIDOAN1, Constraints chung).
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn chạy trong cùng một transaction (AGENTS.md).

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026: thêm "Chờ lấy hàng", bỏ "Bị từ chối").
- Mọi mức giảm tính theo phần trăm; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026).
- Mỗi đơn áp tối đa 1 khuyến mãi (theo hóa đơn hoặc voucher); khuyến mãi theo sản phẩm được ghi theo từng dòng đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái (kể cả lúc tạo), hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) tăng khi tạo đơn.
- Các dòng đã đặt được xóa khỏi giỏ sau khi đặt thành công.
- Giá hoặc mức giảm thay đổi trước khi xác nhận thì tính lại và yêu cầu khách xác nhận lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): mức giảm theo %, làm tròn ROUND_HALF_UP; mỗi đơn tối đa 1 khuyến mãi, khuyến mãi theo sản phẩm ghi theo dòng (theo ERD); lưu lịch sử trạng thái đơn (theo ERD); thêm AC-3, AC-4
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — thêm trạng thái "Chờ lấy hàng", bỏ "Bị từ chối"; phí vận chuyển lấy từ biến môi trường (mặc định 12.000đ)
- v5 (2026-11-23): chốt nút "Sử dụng thông tin hồ sơ", điều kiện hồ sơ đầy đủ và lưu thông tin nhận hàng theo từng đơn.
