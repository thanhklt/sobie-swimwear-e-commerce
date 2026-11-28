# UC-09: Xem trang chủ

## Metadata
- **ID:** UC-09
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng truy cập địa chỉ gốc của website (`/`).

## Preconditions
- Website đang hoạt động.

## Main Flow
1. Người dùng mở trang chủ website.
2. Hệ thống hiển thị thanh điều hướng (header) gồm logo thương hiệu, menu danh mục sản phẩm (UC-10), ô tìm kiếm (UC-11), liên kết hotline, link Zalo (lấy từ cấu hình cửa hàng), biểu tượng giỏ hàng (UC-18), danh sách yêu thích (UC-38) và khu vực tài khoản người dùng (Khách hàng hiển thị tên tài khoản / Khách vãng lai hiển thị nút Đăng nhập, Đăng ký).
3. Hệ thống tải và hiển thị các khối sản phẩm ở trạng thái Đang bán (`product_status = ACTIVE`) và có ít nhất một biến thể Đang bán (`variant_status = ACTIVE`) với giá bán hợp lệ (`variant_sell_price > 0`). Các sản phẩm cha ACTIVE nhưng không còn biến thể ACTIVE nào có giá > 0 sẽ bị tạm ẩn khỏi các khối hiển thị (lọc bỏ trước khi áp dụng giới hạn số lượng sản phẩm của từng khối để bù suất bằng sản phẩm hợp lệ tiếp theo, không đổi trạng thái sản phẩm trong cơ sở dữ liệu) (đã chốt 23/11/2026):
   - **Khối Bán chạy:** Tối đa 5 sản phẩm hợp lệ có tổng số lượng bán lớn nhất trong 168 giờ gần nhất từ danh sách top 15 của module `reporting` (đã chốt 21/11/2026, cập nhật 23/11/2026).
   - **Khối Hàng mới:** Tối đa 8 sản phẩm hợp lệ mới nhất, sắp xếp theo thời điểm tạo `product_created_at` giảm dần (đã chốt 22/11/2026, cập nhật 23/11/2026).
   - **Khối Sản phẩm theo bộ sưu tập:** Các bộ sưu tập đang có sản phẩm hợp lệ; mỗi bộ sưu tập hiển thị tên bộ sưu tập và tối đa 4 sản phẩm hợp lệ mới nhất thuộc bộ sưu tập đó (đã chốt 22/11/2026, cập nhật 23/11/2026).
4. Mỗi sản phẩm trong các khối hiển thị dưới dạng thẻ sản phẩm gồm:
   - Ảnh đại diện của sản phẩm (ảnh có thứ tự `gallery_order_no = 1` trong gallery; nếu sản phẩm chưa có ảnh thì hiển thị ảnh mặc định placeholder).
   - Tên sản phẩm.
   - Giá bán: Mức giá bán thấp nhất tính từ các biến thể Đang bán (`variant_status = ACTIVE`) có giá hợp lệ (`variant_sell_price > 0`) của sản phẩm (`min(variant_sell_price)`). Tồn kho không tham gia vào điều kiện tính giá bán. Biến thể Ngừng bán (`INACTIVE`) dù có giá rẻ hơn cũng không được tính vào giá thẻ sản phẩm (đã chốt 23/11/2026).
   - Giá sau khuyến mãi theo sản phẩm: Nếu sản phẩm đang có khuyến mãi theo sản phẩm còn hiệu lực (UC-28), hiển thị cả giá gốc và giá sau giảm (tính theo % giảm trên giá thấp nhất nói trên, làm tròn số nguyên VND theo `ROUND_HALF_UP`).
   - Nhãn "Hết hàng": Hiển thị khi không có biến thể Đang bán (`ACTIVE`) có giá > 0 nào còn tồn kho khả dụng > 0 (`stock_quantity > 0` trong `inventory.stock`). Biến thể Ngừng bán (`INACTIVE`) dù còn tồn kho trong kho cũng không được tính vào tồn kho khả dụng để gỡ nhãn Hết hàng. Sản phẩm không tự ẩn khỏi danh sách chỉ vì hết tồn kho (vẫn hiển thị bình thường kèm nhãn "Hết hàng") (đã chốt 23/11/2026).
5. Hệ thống hiển thị chân trang (footer) gồm thông tin hotline, link Zalo và các liên kết thông tin: Giới thiệu, Chính sách, FAQ (UC-13).
6. Người dùng có thể thực hiện một trong các thao tác:
   - Bấm vào một thẻ sản phẩm để xem chi tiết sản phẩm (UC-12).
   - Bấm vào một danh mục trên menu để xem sản phẩm theo danh mục (UC-10).
   - Bấm vào ô tìm kiếm hoặc nhập từ khóa để tìm kiếm sản phẩm (UC-11).
   - Bấm vào hotline để gọi điện hoặc link Zalo để mở liên kết ngoài.

## Alternative Flows
- **3a. Một khối không có sản phẩm nào:** Hệ thống ẩn khối đó (áp dụng cho khối Bán chạy khi không có sản phẩm bán được hợp lệ, khối Hàng mới khi không có sản phẩm hợp lệ nào, hoặc bộ sưu tập không có sản phẩm hợp lệ nào) (đã chốt 22/11/2026, cập nhật 23/11/2026).
- **3b. Khối bán chạy còn dưới 5 sản phẩm sau khi lọc:** Nếu sau khi loại bỏ các sản phẩm Ngừng bán (`product_status = INACTIVE`) và các sản phẩm không còn biến thể ACTIVE có giá > 0 từ top 15 của `reporting`, danh sách còn từ 1 đến 4 sản phẩm, hệ thống hiển thị số lượng sản phẩm thực tế còn lại. Không lấy thêm sản phẩm ngoài top 15. Nếu còn 0 sản phẩm thì ẩn khối (đã chốt 22/11/2026, cập nhật 23/11/2026).
- **3c. Sản phẩm cha ACTIVE không có biến thể ACTIVE có giá > 0:** Sản phẩm bị tạm ẩn khỏi các khối hiển thị (Hàng mới, Bộ sưu tập, Bán chạy); trạng thái trong DB không thay đổi; hệ thống tự động bù suất bằng sản phẩm hợp lệ tiếp theo để đảm bảo đủ số lượng tối đa của khối (nếu còn sản phẩm hợp lệ) (đã chốt 23/11/2026).
- **4a. Sản phẩm hiển thị nhãn Hết hàng:** Thẻ sản phẩm vẫn hiển thị ảnh, tên, giá bán và nhãn "Hết hàng"; người dùng vẫn có thể bấm vào thẻ để xem chi tiết sản phẩm (UC-12) nhưng không thể đặt hàng (đã chốt 22/11/2026).
- **6a. Người dùng bấm vào danh mục:** Hệ thống chuyển hướng sang trang duyệt danh mục tương ứng (UC-10).
- **6b. Người dùng tìm kiếm:** Hệ thống chuyển hướng sang trang kết quả tìm kiếm (UC-11).
- **6c. Người dùng bấm vào thẻ sản phẩm:** Hệ thống chuyển hướng sang trang chi tiết sản phẩm tương ứng (UC-12).

## Exceptions
- **E1. Lỗi khi tải dữ liệu sản phẩm:** Hệ thống vẫn hiển thị khung trang chủ (header, footer, menu) và hiển thị thông báo lỗi "Không tải được sản phẩm, vui lòng thử lại" ở vùng nội dung chính.
- **E2. Redis không khả dụng hoặc lỗi kết nối cache:** Hệ thống tự động fallback gọi các service công khai liên quan để truy vấn dữ liệu trực tiếp từ cơ sở dữ liệu, render trang chủ bình thường mà không làm gián đoạn trải nghiệm người dùng (đã chốt 22/11/2026).

## Postconditions
- Trang chủ hiển thị thành công; dữ liệu trên hệ thống không thay đổi.

## Acceptance Criteria

### AC-1: Hiển thị sản phẩm đang bán
Given: có sản phẩm ở trạng thái Đang bán (ACTIVE) có biến thể ACTIVE có giá > 0 và sản phẩm ở trạng thái Ngừng bán (INACTIVE)
When: Khách vãng lai hoặc Khách hàng mở trang chủ
Then: chỉ sản phẩm Đang bán hợp lệ được hiển thị trong các khối
And: mỗi thẻ hiển thị đúng ảnh đại diện (`gallery_order_no = 1`), tên sản phẩm và giá bán

### AC-2: Hiển thị giá khuyến mãi theo sản phẩm
Given: sản phẩm A đang có khuyến mãi theo sản phẩm giảm 10% còn hiệu lực, giá biến thể ACTIVE thấp nhất là 300.000đ
When: người dùng mở trang chủ
Then: thẻ sản phẩm A hiển thị giá gốc 300.000đ và giá sau giảm 270.000đ

### AC-3: Nhãn hết hàng khi mọi biến thể ACTIVE hết tồn kho
Given: sản phẩm B có biến thể size S (`variant_status = ACTIVE`, giá 200.000đ) có tồn kho = 0 trong `inventory.stock`, và không còn biến thể ACTIVE nào khác
When: người dùng mở trang chủ
Then: thẻ sản phẩm B hiển thị nhãn "Hết hàng"
And: người dùng vẫn có thể bấm vào thẻ sản phẩm B để chuyển sang UC-12

### AC-4: Không hiển thị nhãn hết hàng khi còn ít nhất một biến thể ACTIVE còn hàng
Given: sản phẩm C có biến thể Đỏ-M (`ACTIVE`, giá 200.000đ) tồn kho = 0 nhưng biến thể Đỏ-L (`ACTIVE`, giá 220.000đ) tồn kho = 2
When: người dùng mở trang chủ
Then: thẻ sản phẩm C không hiển thị nhãn "Hết hàng"

### AC-5: Hotline và link Zalo
Given: cấu hình cửa hàng có hotline "0901234567" và link Zalo "https://zalo.me/..."
When: người dùng mở trang chủ
Then: hotline và link Zalo hiển thị đúng giá trị cấu hình ở header và footer

### AC-6: Ẩn khối rỗng
Given: không có sản phẩm nào thuộc một bộ sưu tập X hoặc không có sản phẩm bán chạy hợp lệ trong 168 giờ gần nhất
When: người dùng mở trang chủ
Then: khối bộ sưu tập X hoặc khối bán chạy không được hiển thị trên giao diện

### AC-7: Lỗi tải dữ liệu sản phẩm
Given: hệ thống gặp lỗi kết nối cơ sở dữ liệu khi lấy danh sách sản phẩm
When: người dùng mở trang chủ
Then: trang vẫn hiển thị khung header, footer và thông báo "Không tải được sản phẩm, vui lòng thử lại", không trả về trang trắng

### AC-8: Khối bán chạy xếp theo tổng số lượng bán trong 168 giờ
Given: trong 168 giờ gần nhất tính từ thời điểm tác vụ tính, có đơn 1 mua 5 cái sản phẩm SP-0001 (A), đơn 2 và đơn 3 mỗi đơn mua 1 cái sản phẩm SP-0002 (B); các đơn đều ở trạng thái hợp lệ và cả A, B đều Đang bán hợp lệ
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: khối bán chạy hiển thị A trước B (tổng A = 5, tổng B = 2)

### AC-9: Chỉ tính đơn trong 168 giờ gần nhất (UTC)
Given: sản phẩm SP-0003 (C) chỉ có đơn đặt cách thời điểm tác vụ tính 170 giờ (ngoài khung 168 giờ UTC)
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: C không nằm trong khối bán chạy

### AC-10: Tối đa 5 sản phẩm cho khối bán chạy
Given: trong 168 giờ gần nhất tính từ thời điểm tác vụ tính, có 7 sản phẩm Đang bán hợp lệ đều có đơn hàng ở trạng thái hợp lệ
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: khối bán chạy hiển thị đúng 5 sản phẩm có tổng số lượng bán lớn nhất

### AC-11: Sản phẩm ngừng bán biến mất ngay khỏi khối bán chạy mà không chờ tác vụ 10 phút
Given: sản phẩm SP-0001 (A) đang nằm trong top 5 bán chạy hiển thị trên trang chủ
When: Nhân viên chuyển sản phẩm A sang trạng thái Ngừng bán (UC-14), rồi người dùng tải lại trang chủ ngay sau đó
Then: sản phẩm A không còn xuất hiện trong khối bán chạy
And: hệ thống hiển thị sản phẩm hợp lệ tiếp theo trong top 15 đã cache mà không cần chờ lần chạy tiếp theo của tác vụ định kỳ 10 phút

### AC-12: Trạng thái đơn được tính vào khối bán chạy
Given: trong 168 giờ gần nhất tính từ thời điểm tác vụ tính:
  - Sản phẩm SP-0004 (D) có đơn ở trạng thái "Chưa xử lý"
  - Sản phẩm SP-0005 (E) có đơn ở trạng thái "Đã hủy"
  - Sản phẩm SP-0006 (F) có đơn ở trạng thái "Giao không thành công"
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: số lượng mua của sản phẩm D được tính vào khối bán chạy
And: số lượng mua của sản phẩm E và sản phẩm F không được tính vào khối bán chạy

### AC-13: Tiêu chí phụ khi hòa số lượng bán trong khối bán chạy (Tie-breaker)
**Kịch bản 1: Hòa số lượng bán, khác thời điểm đơn hàng gần nhất**
Given: trong 168 giờ gần nhất, sản phẩm SP-0001 (A) và sản phẩm SP-0002 (B) đều có tổng số lượng bán là 4; đơn hàng gần nhất của A đặt lúc 10:00 UTC, đơn hàng gần nhất của B đặt lúc 09:00 UTC cùng ngày
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: sản phẩm A được xếp trước sản phẩm B trong khối bán chạy

**Kịch bản 2: Hòa số lượng bán và cùng thời điểm đơn hàng gần nhất**
Given: trong 168 giờ gần nhất, sản phẩm SP-0001 và sản phẩm SP-0002 đều có tổng số lượng bán là 3; đơn hàng gần nhất của cả hai sản phẩm được đặt cùng thời điểm 10:00 UTC (nằm trong cùng một đơn hàng)
When: tác vụ tính bán chạy đã chạy ghi cache và người dùng mở trang chủ
Then: sản phẩm SP-0001 được xếp trước sản phẩm SP-0002 do có mã `product_id` nhỏ hơn

### AC-14: Khối bán chạy hiển thị số lượng thực tế khi còn dưới 5 sản phẩm
Given: trong 168 giờ gần nhất, sau khi tác vụ chạy và hệ thống lọc bỏ sản phẩm không hợp lệ từ top 15, chỉ còn 3 sản phẩm hợp lệ
When: người dùng mở trang chủ
Then: khối bán chạy hiển thị đúng 3 sản phẩm đó, không báo lỗi và không hiển thị ô trống

### AC-15: Khối hàng mới hiển thị tối đa 8 sản phẩm mới nhất
Given: hệ thống có 10 sản phẩm Đang bán hợp lệ với thời điểm tạo `product_created_at` khác nhau
When: người dùng mở trang chủ
Then: khối "Hàng mới" hiển thị đúng 8 sản phẩm có thời điểm tạo mới nhất, theo thứ tự giảm dần thời gian tạo

### AC-16: Khối sản phẩm theo bộ sưu tập
Given: bộ sưu tập "Hè 2026" có 6 sản phẩm Đang bán hợp lệ
When: người dùng mở trang chủ
Then: khối bộ sưu tập "Hè 2026" hiển thị tiêu đề bộ sưu tập và đúng 4 sản phẩm mới nhất thuộc bộ sưu tập đó

### AC-17: Thẻ sản phẩm hiển thị giá bán thấp nhất từ các biến thể ACTIVE có giá > 0
Given: sản phẩm A có các biến thể `variant_status = ACTIVE`: size S giá 250.000đ, size M giá 280.000đ, size L giá 300.000đ
When: người dùng xem thẻ sản phẩm A trên trang chủ
Then: thẻ sản phẩm A hiển thị giá bán là 250.000đ

### AC-18: Hiển thị ảnh mặc định khi sản phẩm chưa có ảnh
Given: sản phẩm SP-0007 ở trạng thái Đang bán hợp lệ nhưng chưa có bản ghi ảnh nào trong `catalog.gallery`
When: người dùng mở trang chủ
Then: thẻ sản phẩm SP-0007 hiển thị ảnh mặc định (placeholder), không bị lỗi vỡ giao diện

### AC-19: Fallback khi Redis mất dữ liệu hoặc lỗi kết nối cache
Given: Redis cache của khối bán chạy hoặc khối trang chủ bị trống hoặc mất kết nối
When: người dùng mở trang chủ
Then: hệ thống tự động gọi các service công khai liên quan để truy vấn dữ liệu từ cơ sở dữ liệu và hiển thị trang chủ bình thường mà không phát sinh lỗi 500

### AC-20: Điều hướng xem sản phẩm theo danh mục
Given: người dùng đang ở trang chủ, thanh điều hướng menu có danh mục "Bikini"
When: người dùng bấm vào danh mục "Bikini"
Then: hệ thống chuyển hướng người dùng sang trang danh mục "Bikini" (UC-10)

### AC-21: Điều hướng tìm kiếm sản phẩm
Given: người dùng đang ở trang chủ, nhập từ khóa "áo bơi tay dài" vào ô tìm kiếm và xác nhận tìm kiếm
When: hệ thống xử lý tìm kiếm
Then: hệ thống chuyển hướng người dùng sang trang kết quả tìm kiếm với từ khóa "áo bơi tay dài" (UC-11)

### AC-22: Điều hướng xem chi tiết sản phẩm
Given: thẻ sản phẩm SP-0001 hiển thị trong một khối trên trang chủ
When: người dùng bấm vào thẻ sản phẩm SP-0001
Then: hệ thống chuyển hướng người dùng sang trang chi tiết sản phẩm của SP-0001 (UC-12)

### AC-23: Phân biệt biến thể INACTIVE còn tồn kho và biến thể ACTIVE hết tồn kho
Given: sản phẩm SP-0010 có:
  - Biến thể size S ở trạng thái Ngừng bán (`variant_status = INACTIVE`), giá 100.000đ, tồn kho khả dụng = 5 trong `inventory.stock`
  - Biến thể size M ở trạng thái Đang bán (`variant_status = ACTIVE`), giá 200.000đ, tồn kho khả dụng = 0 trong `inventory.stock`
  - Không còn biến thể nào khác
When: người dùng mở trang chủ
Then: thẻ sản phẩm SP-0010 hiển thị giá bán là 200.000đ (không lấy giá 100.000đ của biến thể INACTIVE)
And: thẻ sản phẩm SP-0010 hiển thị nhãn "Hết hàng" (không tính 5 tồn kho của biến thể INACTIVE để gỡ nhãn Hết hàng)

### AC-24: Tạm ẩn sản phẩm cha ACTIVE không còn biến thể ACTIVE có giá > 0 và bù suất hiển thị
**Kịch bản 1: Bù suất trong khối Hàng mới (giới hạn 8 sản phẩm)**
Given: hệ thống có đúng 9 sản phẩm ở trạng thái Đang bán (`product_status = ACTIVE`) với thời điểm tạo mới nhất giảm dần từ SP-0001 đến SP-0009; trong đó sản phẩm mới nhất SP-0001 không có biến thể hợp lệ nào (toàn bộ biến thể ở trạng thái `INACTIVE` hoặc không có giá bán > 0), còn 8 sản phẩm SP-0002 đến SP-0009 đều có ít nhất một biến thể `ACTIVE` có giá > 0
When: người dùng mở trang chủ
Then: sản phẩm SP-0001 bị tạm ẩn khỏi khối "Hàng mới" mà không bị thay đổi trạng thái trong cơ sở dữ liệu (`product_status` của SP-0001 trong DB vẫn là `ACTIVE`)
And: khối "Hàng mới" hiển thị đủ đúng 8 thẻ sản phẩm hợp lệ gồm SP-0002 đến SP-0009 (SP-0001 bị ẩn không chiếm suất của các sản phẩm hợp lệ)

**Kịch bản 2: Bù suất trong khối Bộ sưu tập (giới hạn 4 sản phẩm mỗi BST)**
Given: bộ sưu tập "Hè 2026" có đúng 5 sản phẩm Đang bán (`product_status = ACTIVE`) với thời điểm tạo mới nhất giảm dần từ SP-0010 đến SP-0014; trong đó sản phẩm mới nhất SP-0010 không có biến thể hợp lệ nào (toàn bộ biến thể `INACTIVE` hoặc chưa có giá > 0), còn 4 sản phẩm SP-0011 đến SP-0014 đều là sản phẩm hợp lệ
When: người dùng mở trang chủ
Then: sản phẩm SP-0010 bị tạm ẩn khỏi khối bộ sưu tập "Hè 2026", không chiếm suất hiển thị
And: khối bộ sưu tập "Hè 2026" hiển thị tiêu đề bộ sưu tập và đủ đúng 4 thẻ sản phẩm hợp lệ gồm SP-0011 đến SP-0014

### AC-25: Kiểm tra trạng thái hiện hành từ Database khi render khối Bán chạy và giới hạn Top 15
**Kịch bản 1: Loại bỏ sản phẩm không hợp lệ trong top 15, bù bằng ranks tiếp theo**
Given: tác vụ reporting đã ghi nhận danh sách top 15 bán chạy vào Redis theo thứ tự xếp hạng từ rank 1 đến rank 15 (sản phẩm R1 đến R15); sau đó sản phẩm ở rank 1 (R1) bị Nhân viên chuyển sang Ngừng bán (`product_status = INACTIVE`) hoặc toàn bộ biến thể bị chuyển sang `INACTIVE`, còn 14 sản phẩm từ rank 2 đến rank 15 (R2 đến R15) đều là sản phẩm Đang bán hợp lệ
When: người dùng mở trang chủ (kể cả khi việc tăng số phiên bản cache catalog ở Redis gặp sự cố hoặc chưa hoàn tất)
Then: khi render trang chủ, module `catalog` kiểm tra trực tiếp trạng thái hiện hành từ cơ sở dữ liệu, loại bỏ ngay sản phẩm R1 khỏi danh sách hiển thị
And: khối Bán chạy hiển thị đúng 5 sản phẩm hợp lệ tiếp theo tương ứng với ranks 2, 3, 4, 5, 6 (R2 đến R6)

**Kịch bản 2: Toàn bộ top 15 bị loại bỏ và có sản phẩm hợp lệ ở rank 16 trong Database**
Given: tác vụ reporting đã ghi nhận top 15 sản phẩm bán chạy vào Redis (R1 đến R15); trong cơ sở dữ liệu có sản phẩm R16 xếp hạng 16 về số lượng bán và đang ở trạng thái Đang bán hợp lệ; tại thời điểm render trang chủ, toàn bộ 15 sản phẩm trong top 15 đã cache (R1 đến R15) đều bị Ngừng bán hoặc không còn biến thể hợp lệ
When: người dùng mở trang chủ
Then: hệ thống lọc bỏ toàn bộ 15 sản phẩm không hợp lệ trong top 15 và ẩn hoàn toàn khối Bán chạy khỏi trang chủ
And: hệ thống tuyệt đối không truy vấn lấy thêm sản phẩm ngoài top 15 (sản phẩm rank 16 không được đưa vào khối Bán chạy)

## Dependencies
- **Upstream Services & UC:**
  - Module `catalog` (UC-14, UC-15, UC-16, UC-17): Cung cấp thông tin sản phẩm (Đang bán/Ngừng bán), danh sách biến thể (`variant_status = ACTIVE`), giá bán theo size (`variant_sell_price > 0`), danh mục, bộ sưu tập và bộ ảnh gallery.
  - Module `reporting` (Service tổng hợp bán chạy): Cung cấp tác vụ định kỳ 10 phút tính top 15 sản phẩm bán chạy trong 168 giờ gần nhất và ghi vào Redis (phân biệt với UC-37 Xem dashboard vốn tính theo kỳ báo cáo và chỉ tính đơn giao thành công).
  - Module `inventory` (Service tồn kho): Cung cấp tồn kho biến thể (`inventory.stock`) để xác định nhãn "Hết hàng".
  - Module `promotion` (Service khuyến mãi, UC-28): Cung cấp thông tin khuyến mãi đang hiệu lực theo sản phẩm.
  - Module `ordering` (UC-19, UC-20, UC-22): Nguồn dữ liệu đơn hàng và trạng thái đơn phục vụ tác vụ tính bán chạy của module `reporting`.
  - Module `shipping` (UC-36): Cung cấp trạng thái giao hàng phục vụ loại trừ đơn giao không thành công cho tác vụ của module `reporting`.
- **Downstream UC:**
  - UC-10 Xem sản phẩm theo danh mục
  - UC-11 Tìm kiếm sản phẩm
  - UC-12 Xem chi tiết sản phẩm
  - UC-13 Xem trang giới thiệu, chính sách, FAQ
  - UC-18 Quản lý giỏ hàng
  - UC-38 Quản lý danh sách yêu thích
- **External Systems:**
  - Redis: Cache dữ liệu các khối trang chủ (theo phiên bản catalog, TTL dự phòng 5 phút) và lưu danh sách top 15 sản phẩm bán chạy (TTL 30 phút).

## Notes
- Áp dụng constraint cache (BR-GIAIDOAN1, Constraints chung — Cache): Dữ liệu các khối trang chủ cache ở Redis theo số phiên bản catalog, TTL dự phòng 5 phút; HTML render lại mỗi request (do header có phần định danh riêng của từng người dùng) và trả `Cache-Control: private, no-cache`, không dùng `ETag` (đã chốt 21/11/2026).
- Khối bán chạy theo BR-002 Constraints (đã chốt 21/11/2026, cập nhật 22/11/2026 và 23/11/2026):
  - Tác vụ nền chạy mỗi 10 phút thuộc module `reporting` tính top 15 sản phẩm theo tổng số lượng bán (cộng dồn mọi biến thể) của các đơn đặt trong 168 giờ gần nhất (UTC), ghi vào Redis (TTL 30 phút, chỉ lưu `product_id` và số lượng bán).
  - Trạng thái đơn được tính: `Chưa xử lý`, `Đã xác nhận`, `Chờ lấy hàng`, `Đang giao`, `Giao thành công`. Loại bỏ đơn `Đã hủy` và đơn `Giao không thành công`.
  - Tie-breaker khi hòa số lượng bán: Ưu tiên sản phẩm có đơn hàng phát sinh gần nhất; nếu thời điểm đơn gần nhất vẫn trùng nhau thì sắp xếp theo `product_id` tăng dần.
  - Khi render trang chủ, module `catalog` đọc top 15 từ Redis. Module `catalog` kiểm tra trạng thái sản phẩm cha (`product_status = ACTIVE`) và tập biến thể hợp lệ (`variant_status = ACTIVE`, `variant_sell_price > 0`) hiện hành trực tiếp từ cơ sở dữ liệu. Nhờ đó, việc loại bỏ sản phẩm không hợp lệ diễn ra ngay lập tức tại thời điểm render mà không phụ thuộc vào việc tăng số phiên bản cache catalog ở Redis có thành công hay không (đã chốt 23/11/2026).
  - `catalog` gọi service công khai của module `promotion` để lấy giá khuyến mãi theo sản phẩm, gọi service công khai của module `inventory` để lấy tồn kho biến thể, và kết hợp thông tin sản phẩm trong module `catalog` (tên, ảnh, giá theo size). Hệ thống lọc bỏ các sản phẩm Ngừng bán (INACTIVE) hoặc không còn biến thể ACTIVE có giá > 0 rồi lấy tối đa 5 sản phẩm đầu tiên; nếu thiếu thì hiển thị phần còn lại (1-4 sản phẩm); nếu không còn sản phẩm nào thì ẩn khối; tuyệt đối không lấy thêm sản phẩm ngoài top 15.
  - Xử lý fallback: Nếu Redis trống hoặc gặp sự cố kết nối, `catalog` gọi service công khai của module `reporting` để tính toán danh sách bán chạy trực tiếp từ Database, gọi service công khai của `promotion` và `inventory` tương ứng. Tuyệt đối không đọc trực tiếp bảng cơ sở dữ liệu của module khác.
  - Dữ liệu thực sự đọc từ cache công khai khác áp dụng ngoại lệ chung TTL. Không tuyên bố TTL tự cập nhật trên DOM đang mở của người dùng.
- Phân biệt với dashboard (UC-37): Khối bán chạy trang chủ do tác vụ nền của module `reporting` tổng hợp cho 168 giờ gần nhất tính từ thời điểm đặt hàng (mọi đơn hợp lệ chưa hủy / chưa giao thất bại); dashboard (UC-37) tính theo kỳ báo cáo (tháng hoặc khoảng ngày chọn) và chỉ tính các đơn có ngày chuyển sang "Giao thành công".
- Tập biến thể và hiển thị thẻ sản phẩm (đã chốt 23/11/2026):
  - Sản phẩm cha ở trạng thái `ACTIVE` nhưng không còn biến thể `ACTIVE` nào có giá > 0 sẽ bị tạm ẩn khỏi các khối danh sách trên trang chủ; trạng thái sản phẩm trong DB không đổi; lọc trước khi giới hạn số lượng (8 cho Hàng mới, 4 cho mỗi BST, 5 cho Bán chạy) để bù suất bằng sản phẩm hợp lệ tiếp theo.
  - Sản phẩm không tự ẩn chỉ vì mọi biến thể hết tồn kho (vẫn hiển thị bình thường kèm nhãn "Hết hàng").
  - Giá bán hiển thị trên thẻ là mức giá thấp nhất tính từ các biến thể `ACTIVE` có giá hợp lệ (`variant_sell_price > 0`). Tồn kho không tham gia điều kiện tính giá. Biến thể `INACTIVE` dù có giá rẻ hơn cũng không được tính vào giá thẻ.
  - Khuyến mãi theo sản phẩm tính trên giá thấp nhất này: `min_price * (100 - promotion_discount_percent) / 100`, làm tròn theo `ROUND_HALF_UP` thành số nguyên VND.
  - Ảnh đại diện lấy ảnh có `gallery_order_no = 1` trong `catalog.gallery`; nếu sản phẩm chưa có ảnh thì hiển thị ảnh mặc định (placeholder). Giữ nguyên cách hiển thị giá / ảnh đã chốt tại UC-09, không tự thêm định dạng thẻ mới.
  - Nhãn "Hết hàng" hiển thị khi không có biến thể `ACTIVE` có giá > 0 nào còn tồn kho khả dụng > 0 (`stock_quantity > 0`). Biến thể `INACTIVE` dù còn tồn kho trong kho cũng không được tính vào tồn kho khả dụng để gỡ nhãn Hết hàng.
- Out of Scope (BR-GIAIDOAN1): Mega menu, thanh thông báo chạy, banner tùy chỉnh, thêm nhanh vào giỏ hàng từ thẻ sản phẩm.

### Quyết định đã chốt
- Có khối bán chạy: Top 5 sản phẩm (không theo biến thể), 7 ngày gần nhất (168 giờ UTC), tính đơn từ lúc đặt; xếp theo tổng số lượng bán; Ngừng bán thì biến mất ngay khỏi khối (đã chốt 21/11/2026).
- Trạng thái đơn tính vào khối bán chạy: `Chưa xử lý`, `Đã xác nhận`, `Chờ lấy hàng`, `Đang giao`, `Giao thành công`. Loại đơn `Đã hủy` và `Giao không thành công` (đã chốt 22/11/2026).
- Tie-breaker bán chạy: Ưu tiên đơn đặt gần nhất, sau đó theo `product_id` tăng dần (đã chốt 22/11/2026).
- Khối bán chạy còn dưới 5 sản phẩm sau khi lọc thì hiển thị số còn lại; còn 0 sản phẩm thì ẩn khối; không lấy thêm ngoài top 15 (đã chốt 22/11/2026, cập nhật 23/11/2026).
- Ranh giới module Bán chạy: Tác vụ định kỳ 10 phút thuộc `reporting` ghi top 15 vào Redis; `catalog` đọc top 15, kiểm tra trực tiếp trạng thái hiện hành từ cơ sở dữ liệu (không phụ thuộc việc tăng version cache Redis) để lọc bỏ sản phẩm Ngừng bán hoặc không có biến thể hợp lệ rồi lấy 5 sản phẩm đầu; Redis lỗi thì fallback qua Database (đã chốt 22/11/2026, cập nhật 23/11/2026).
- Khối Hàng mới: Tối đa 8 sản phẩm Đang bán hợp lệ mới nhất, sắp xếp theo `product_created_at` giảm dần; không có sản phẩm thì ẩn (đã chốt 22/11/2026, cập nhật 23/11/2026).
- Khối Bộ sưu tập: Mỗi bộ sưu tập có sản phẩm Đang bán hợp lệ hiển thị tối đa 4 sản phẩm mới nhất; không có sản phẩm thì ẩn (đã chốt 22/11/2026, cập nhật 23/11/2026).
- Tập biến thể tính giá thẻ và tồn kho: Giá thẻ chỉ tính min từ các biến thể `ACTIVE` có `variant_sell_price > 0`; tồn kho không tham gia điều kiện tính giá; biến thể `INACTIVE` rẻ hơn không được tính. Nhãn "Hết hàng" hiển thị khi không có biến thể `ACTIVE` có giá > 0 nào còn tồn kho khả dụng > 0; biến thể `INACTIVE` còn tồn kho không được tính (đã chốt 23/11/2026 theo UC-10-Q9/Q10).
- Tạm ẩn sản phẩm cha: Sản phẩm cha `ACTIVE` không còn biến thể `ACTIVE` có giá > 0 thì tạm ẩn khỏi các khối trang chủ, không đổi trạng thái DB; lọc trước khi áp giới hạn số lượng để bù suất bằng sản phẩm hợp lệ tiếp theo; không tự ẩn khi hết tồn kho (đã chốt 23/11/2026 theo UC-10-Q11 & UC-14-Q10).
- Quy chuẩn thẻ sản phẩm: Giá sau khuyến mãi làm tròn VND nguyên (`ROUND_HALF_UP`); ảnh đại diện lấy `gallery_order_no = 1` hoặc placeholder (đã chốt 22/11/2026).

### Giả định [GD]
*(Không còn giả định chưa được giải quyết; toàn bộ giả định đã được developer phê duyệt và chuyển thành Quyết định đã chốt).*

## History
- v1 (2026-11-15): initial
- v2 (2026-11-21): theo BR-GIAIDOAN1 v20 — thêm khối bán chạy (bước 2, AC-7 → AC-11); ghi chiến lược cache
- v3 (2026-11-21): theo BR-GIAIDOAN1 v22 — HTML trang chủ không còn `public, max-age=60`; trả `private, no-cache` + `ETag`, chỉ cache dữ liệu ở Redis (Notes)
- v4 (2026-11-21): theo BR-GIAIDOAN1 v23 — bỏ `ETag` (Notes)
- v5 (2026-11-22): chốt toàn bộ giả định UC-09-Q1 → UC-09-Q4: quy cách khối Hàng mới (8 SP), khối Bộ sưu tập (4 SP/BST), tie-breaker và trạng thái đơn tính bán chạy (loại hủy và giao không thành công), ranh giới reporting/catalog, fallback Redis, quy cách thẻ giá min và ảnh đại diện, bổ sung AC-12 → AC-18.
- v6 (2026-11-22): rà soát theo chỉ đạo coordinator: tinh chỉnh Dependencies tách khỏi UC-37, làm rõ ranh giới gọi service công khai (reporting/promotion/inventory) trong Notes fallback, bổ sung kịch bản tie-breaker theo product_id (AC-13), chuẩn hóa điều kiện 168 giờ UTC & đọc sau khi cache ở các AC bán chạy, bổ sung AC-18 (ảnh placeholder), AC-20 → AC-22 (điều hướng).
- v7 (2026-11-23): đồng bộ theo quyết định developer duyệt tại Codex (UC-10-Q9/Q10/Q11 & UC-14-Q10): chuẩn hóa tập biến thể tính giá thẻ (ACTIVE, giá > 0), điều kiện nhãn Hết hàng (ACTIVE có giá > 0 và tồn kho > 0), quy tắc tạm ẩn sản phẩm cha không còn biến thể hợp lệ và bù suất trước khi giới hạn, kiểm tra trạng thái hiện hành từ DB cho top 15 bán chạy không phụ thuộc version cache, bổ sung AC-23 → AC-25 (tổng cộng 25 AC).
