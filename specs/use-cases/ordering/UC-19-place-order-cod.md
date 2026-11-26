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

## Hiện trạng triển khai

`GET /api/v1/ordering/checkout` hiện hiển thị giỏ và hỗ trợ gộp giỏ sau đăng nhập. Biểu mẫu thông tin nhận hàng và nút “Sử dụng thông tin hồ sơ” cho đơn COD còn chờ triển khai.

## Main Flow
1. Hệ thống mở trang thanh toán với các trường tên người nhận, địa chỉ nhận hàng (số nhà, đường; phường/xã; tỉnh/thành phố; quốc gia) và số điện thoại nhận hàng. Nút "Sử dụng thông tin hồ sơ" chỉ dùng được khi hồ sơ đã lưu đủ họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng hợp lệ. Hệ thống chỉ sao chép dữ liệu hồ sơ khi khách bấm nút.
2. Khách nhập thông tin nhận hàng hoặc bấm "Sử dụng thông tin hồ sơ" để sao chép họ tên, địa chỉ và số điện thoại từ hồ sơ vào các trường tương ứng. Khách vẫn có thể sửa từng trường sau khi sao chép. Thông tin cuối cùng trên biểu mẫu được dùng cho riêng đơn hàng và không cập nhật hồ sơ khách.
3. Khách chọn phương thức "Thanh toán khi nhận hàng (COD)" và có thể nhập mã voucher.
4. Hệ thống tính và hiển thị: tạm tính (đã áp khuyến mãi theo sản phẩm trên từng dòng), mức giảm do UC-31 chọn (tối đa 1 khuyến mãi: theo hóa đơn hoặc voucher), phí vận chuyển cố định, tổng thanh toán. Mọi mức giảm tính theo phần trăm, tiền làm tròn `ROUND_HALF_UP` về số nguyên VND.
5. Khách bấm "Xác nhận đặt hàng".
6. Trong cùng một transaction, hệ thống gọi Service công khai của `catalog` để khóa các dòng sản phẩm cha theo thứ tự `product_key` tăng dần, dùng chung giao thức `FOR UPDATE` với UC-14/15, rồi kiểm tra từ Database đồng thời sản phẩm cha có `product_status = ACTIVE` và từng biến thể có `variant_status = ACTIVE` (không dùng cache storefront); giữ khóa từ trước kiểm tra đến commit/rollback. Nếu sản phẩm hoặc biến thể không còn được bán thì áp dụng E7. Sau đó, hệ thống kiểm tra lại tồn kho từng dòng qua Service công khai inventory, giá hiện tại, điều kiện và lượt còn lại của khuyến mãi được chọn; trừ tồn kho, tăng lượt đã dùng của khuyến mãi được chọn (voucher hoặc khuyến mãi theo hóa đơn) `[GD]`, tạo đơn ở trạng thái "Chưa xử lý" với phương thức COD, lưu lịch sử trạng thái đơn và xóa các dòng đã đặt khỏi giỏ `[GD]`.
7. Sau khi transaction thành công, hệ thống hiển thị trang đặt hàng thành công kèm mã đơn.

## Alternative Flows
- **0a. Khách chưa đăng nhập:** bấm "Đặt hàng" thì chuyển sang UC-02 Đăng nhập; đăng nhập xong quay lại trang thanh toán với giỏ đã gộp.
- **3a. Không nhập voucher:** UC-31 chỉ xét khuyến mãi theo giá trị hóa đơn.
- **4a. Không có khuyến mãi theo hóa đơn hay voucher nào áp được:** mức giảm bằng 0; đơn không gắn khuyến mãi nào.

## Exceptions
- **E1. Hết hàng khi xác nhận:** một dòng không còn đủ tồn kho → không tạo đơn, rollback toàn bộ transaction, báo dòng nào thiếu hàng.
- **E2. Voucher không hợp lệ:** UC-31 báo lỗi; khách sửa hoặc bỏ voucher rồi đặt lại.
- **E3. Thiếu thông tin nhận hàng:** nếu thiếu tên người nhận, số điện thoại nhận hàng hoặc một phần bắt buộc của địa chỉ nhận hàng, hệ thống báo trường thiếu và không tạo đơn.
- **E4. Giá hoặc mức giảm thay đổi trước khi xác nhận:** hệ thống tính lại theo giá hiện tại, báo khách và yêu cầu xác nhận lại `[GD]`.
- **E5. Khuyến mãi hết lượt hoặc không còn đủ điều kiện khi xác nhận:** hệ thống không tạo đơn, không trừ tồn kho hoặc tăng lượt khuyến mãi; cập nhật tổng thanh toán và yêu cầu khách xác nhận lại `[GD]`.
- **E6. Lỗi tạo đơn hoặc cập nhật giỏ:** rollback toàn bộ transaction; đơn, tồn kho, lượt khuyến mãi và giỏ giữ nguyên.
- **E7. Sản phẩm hoặc biến thể đã ngừng bán khi xác nhận:** tại bước 6, một sản phẩm cha hoặc biến thể không còn tồn tại hoặc đã INACTIVE trong Database → rollback toàn bộ transaction, báo rõ dòng không còn được bán; không tạo đơn, không trừ tồn kho, không thay đổi lượt dùng khuyến mãi hay xóa dòng giỏ.

## Postconditions
- Đơn COD ở trạng thái "Chưa xử lý", tồn kho các biến thể đã bị trừ, tồn kho không âm.
- Đơn lưu tên người nhận, số điện thoại nhận hàng và địa chỉ nhận hàng theo giá trị trên biểu mẫu lúc xác nhận. Hồ sơ tài khoản giữ nguyên khi đặt hàng.
- Đơn lưu đơn giá từng dòng, khuyến mãi theo sản phẩm của từng dòng (nếu có), khuyến mãi được áp cho đơn (tối đa 1), tiền giảm, phí vận chuyển và tổng thanh toán tại thời điểm đặt.
- Lịch sử trạng thái đơn có dòng đầu tiên: trạng thái mới "Chưa xử lý", nguồn là Khách hàng, thời điểm tạo đơn.
- Nếu đặt hàng thất bại, không tạo đơn, không trừ tồn kho, không tăng lượt khuyến mãi và không xóa dòng giỏ.

## Acceptance Criteria

### AC-1: Đặt hàng COD thành công
Given: khách đã đăng nhập, giỏ có "Đỏ / M" số lượng 2, tồn kho 5
When: khách điền đủ thông tin nhận hàng, chọn COD và xác nhận đặt hàng
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
Given: khách xóa trống số điện thoại nhận hàng
When: khách xác nhận đặt hàng
Then: hệ thống không tạo đơn và báo thiếu số điện thoại

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
### AC-12: Chặn đặt COD cho biến thể đã ngừng bán dù cache còn hàng
Given: dữ liệu kiểm thử có sản phẩm cha ACTIVE, "Đỏ / M" đã INACTIVE từ trước khi phiếu nhập chuyển CONFIRMED và hiện tồn 5; khách gửi yêu cầu đặt số lượng 1 từ dữ liệu thanh toán cũ thể hiện biến thể đang bán
When: khách xác nhận đặt hàng COD
Then: trong transaction tạo đơn, hệ thống kiểm tra trạng thái hiện hành qua Service công khai của catalog và từ chối theo E7, báo dòng "Đỏ / M" không còn được bán
And: không tạo đơn hoặc lịch sử đơn, tồn kho vẫn là 5, lượt dùng khuyến mãi và giỏ hàng giữ nguyên

### AC-13: Ngừng bán sau CONFIRMED bị chặn, đặt COD đọc lại trạng thái sau chờ
Given: sản phẩm cha và "Đỏ / M" đều ACTIVE, đã có phiếu CONFIRMED, tồn 5 và giá hợp lệ; khách đặt 1 sản phẩm với các điều kiện COD khác hợp lệ, không áp dụng khuyến mãi; transaction UC-15 đang giữ khóa cha để xử lý yêu cầu ngừng bán và chưa kết thúc
When: khách xác nhận đặt COD cho "Đỏ / M" và transaction tạo đơn yêu cầu cùng khóa qua Service catalog
Then: UC-15 kiểm tra CONFIRMED, từ chối ngừng bán theo E7 của UC-15 và rollback, giữ nguyên trạng thái ACTIVE; transaction tạo đơn chờ đến khi khóa được giải phóng
And: sau chờ, UC-19 đọc lại cả sản phẩm và biến thể vẫn ACTIVE, tiếp tục đặt COD thành công theo Main Flow; không từ chối với E7 của UC-19
And: chỉ một đơn và lịch sử tương ứng được tạo, tồn còn 4 và các dòng đã đặt được xóa khỏi giỏ trong transaction tạo đơn; yêu cầu ngừng bán không thay đổi dữ liệu

### AC-14: Chặn đặt COD khi sản phẩm cha ngừng bán nhưng biến thể vẫn ACTIVE
Given: dữ liệu kiểm thử có sản phẩm cha đã INACTIVE từ trước khi phiếu nhập chuyển CONFIRMED, biến thể "Đỏ / M" vẫn ACTIVE và hiện tồn 5; khách gửi yêu cầu đặt số lượng 1 từ dữ liệu thanh toán cũ thể hiện sản phẩm đang bán
When: khách xác nhận đặt COD
Then: sau khi có khóa, Service catalog đọc trạng thái hiện hành của cả sản phẩm và biến thể; hệ thống từ chối theo E7 vì sản phẩm cha INACTIVE
And: transaction tạo đơn rollback toàn bộ; không tạo đơn/lịch sử đơn, tồn kho vẫn là 5, lượt dùng khuyến mãi và giỏ hàng giữ nguyên

### AC-15: Sao chép thông tin nhận hàng từ hồ sơ khi khách yêu cầu
Given: khách đã lưu hồ sơ có đủ họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng hợp lệ
When: khách mở trang thanh toán
Then: nút "Sử dụng thông tin hồ sơ" dùng được và hệ thống chờ khách bấm trước khi sao chép thông tin
And: khi khách bấm, ba trường tên người nhận, số điện thoại và địa chỉ nhận hàng được điền từ hồ sơ

### AC-16: Dùng thông tin nhận hàng khác với hồ sơ
Given: khách đã bấm "Sử dụng thông tin hồ sơ"
When: khách sửa thông tin nhận hàng rồi xác nhận với dữ liệu hợp lệ
Then: đơn lưu tên người nhận, số điện thoại và địa chỉ theo biểu mẫu lúc xác nhận
And: hồ sơ tài khoản giữ nguyên

### AC-17: Hồ sơ chưa đầy đủ vẫn đặt hàng bằng cách nhập tay
Given: hồ sơ đã có họ tên, số điện thoại và địa chỉ nhận hàng nhưng thiếu ngày sinh
When: khách mở trang thanh toán
Then: nút "Sử dụng thông tin hồ sơ" không dùng được
And: khách vẫn đặt được hàng khi nhập tay đầy đủ thông tin nhận hàng hợp lệ và đáp ứng các điều kiện đặt hàng khác

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-04 Cập nhật hồ sơ khách hàng, UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size, UC-18 Quản lý giỏ hàng, UC-31 Tính mức giảm cho đơn hàng
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng, UC-23 Xác nhận đơn hàng
- **Internal Services:** `catalog` kiểm tra trạng thái sản phẩm cha và biến thể sau khi giữ khóa sản phẩm cha trong cùng transaction; `inventory` kiểm tra/trừ tồn kho. Module ordering không truy cập trực tiếp Repository hoặc bảng của catalog/inventory.
- **External Systems:** Không có

## Notes
- Luôn kiểm tra lượt còn lại trong transaction tạo đơn. Chỉ thay đổi số lượt còn lại, trong khi khuyến mãi vẫn hợp lệ và giá, mức giảm, điều kiện áp dụng cho đơn không đổi, không yêu cầu khách xác nhận lại.
- Phí vận chuyển là 1 mức cho mọi đơn, lấy từ biến môi trường, mặc định 12.000đ (BR-GIAIDOAN1, Constraints chung).
- Kiểm tra/trừ tồn kho, áp khuyến mãi/voucher và tạo đơn chạy trong cùng một transaction (AGENTS.md).
- Service catalog phải dùng cùng transaction với tạo đơn khi kiểm tra trạng thái sản phẩm cha và biến thể, giữ khóa sản phẩm cha để đồng bộ với UC-14/15; không kiểm tra ACTIVE ngoài transaction rồi tạo đơn sau khi đã nhả khóa. Việc kiểm tra khi thêm giỏ hay TTL cache không thay thế bước này.

### Quyết định đã chốt
- Xác nhận COD phải kiểm tra đồng thời sản phẩm cha ACTIVE, biến thể ACTIVE và tồn kho hiện hành qua Service công khai trong transaction tạo đơn; sản phẩm hoặc biến thể đã ngừng bán thì từ chối, rollback toàn bộ và báo dòng lỗi (UC-15-Q7; bổ sung điều kiện sản phẩm cha theo yêu cầu xử lý rà soát vòng 3 tại Codex 23/11/2026).
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
- v5 (2026-11-22): thống nhất phí vận chuyển mặc định 12.000đ và cập nhật AC-2.
- v6 (2026-11-22): đưa xóa giỏ và kiểm tra lại giá, khuyến mãi vào transaction; bổ sung rollback và AC-9, AC-10.
- v7 (2026-11-22): làm rõ sửa thông tin nhận hàng chỉ áp dụng cho đơn đang đặt.
- v8 (2026-11-23): sửa điều kiện xác nhận lại trong AC-9; thêm AC-11 cho trường hợp lượt giảm nhưng voucher vẫn hợp lệ, giữ kiểm tra lượt trong transaction.
- v9 (2026-11-23): theo phê duyệt đồng bộ UC-15-Q7 tại Codex, kiểm tra trạng thái ACTIVE/tồn kho từ DB qua Service trong transaction tạo đơn, khóa sản phẩm đồng bộ UC-15; bổ sung E7 và AC-12/13 cho cache cũ và ngừng bán đồng thời. Giữ draft và các giả định khác.
- v10 (2026-11-23): theo yêu cầu xử lý rà soát vòng 3 tại Codex, kiểm tra product_status cùng variant_status sau khi giữ khóa đồng bộ UC-14/15 trong transaction; bổ sung AC-14 chặn đặt COD khi sản phẩm cha INACTIVE dù biến thể còn ACTIVE/còn hàng. Giữ nguyên các giả định khác.

- v11 (2026-11-23): merge main, giữ kiểm tra trạng thái Catalog dưới khóa cha (E7, AC-12..14) cùng kiểm tra lại giá/khuyến mãi và xóa giỏ trong transaction; không thay các giả định chưa chốt.
- v12 (2026-11-23): sửa AC liên UC theo quy tắc chỉ sửa Mô tả sau CONFIRMED: trạng thái INACTIVE trong fixture được đặt trước xác nhận nhập; thao tác ngừng bán sau CONFIRMED bị từ chối, đặt hàng chờ khóa rồi đọc lại ACTIVE và tiếp tục khi đủ điều kiện. Không đổi luồng nghiệp vụ hoặc các giả định khác.
- v13 (2026-11-23): chốt nút "Sử dụng thông tin hồ sơ", điều kiện hồ sơ đầy đủ và lưu thông tin nhận hàng theo từng đơn.
