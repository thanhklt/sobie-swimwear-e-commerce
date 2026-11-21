# UC-09: Xem trang chủ

## Metadata
- **ID:** UC-09
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng truy cập địa chỉ gốc của website.

## Preconditions
- Website đang hoạt động.

## Main Flow
1. Người dùng mở trang chủ.
2. Hệ thống hiển thị các khối sản phẩm đang bán: hàng mới `[GD]`, sản phẩm theo bộ sưu tập `[GD]`, và khối bán chạy — 5 sản phẩm có tổng số lượng bán lớn nhất trong 7 ngày gần nhất (đã chốt 21/11/2026, xem BR-002).
3. Mỗi sản phẩm hiển thị dạng thẻ: ảnh, tên, giá bán, giá sau khuyến mãi theo sản phẩm (nếu có), nhãn "Hết hàng" khi mọi biến thể hết hàng.
4. Hệ thống hiển thị menu danh mục, ô tìm kiếm, hotline và link Zalo (lấy từ cấu hình cửa hàng hard-code).
5. Người dùng bấm vào một thẻ sản phẩm để xem chi tiết (UC-12), hoặc vào một danh mục (UC-10).

## Alternative Flows
- **2a. Một khối không có sản phẩm nào:** hệ thống ẩn khối đó `[GD]`.

## Exceptions
- **E1. Lỗi khi tải dữ liệu sản phẩm:** hệ thống vẫn hiển thị khung trang chủ và thông báo "Không tải được sản phẩm, vui lòng thử lại".

## Postconditions
- Trang chủ hiển thị; dữ liệu không thay đổi.

## Acceptance Criteria

### AC-1: Hiển thị sản phẩm đang bán
Given: có sản phẩm ở trạng thái Đang bán và sản phẩm ở trạng thái Ngừng bán
When: Khách vãng lai mở trang chủ
Then: chỉ sản phẩm Đang bán được hiển thị
And: mỗi thẻ có ảnh, tên và giá bán

### AC-2: Hiển thị giá khuyến mãi theo sản phẩm
Given: sản phẩm A đang có khuyến mãi theo sản phẩm còn hiệu lực
When: người dùng mở trang chủ
Then: thẻ sản phẩm A hiển thị cả giá gốc và giá sau giảm

### AC-3: Nhãn hết hàng
Given: mọi biến thể của sản phẩm B có tồn kho = 0
When: người dùng mở trang chủ
Then: thẻ sản phẩm B hiển thị nhãn "Hết hàng"

### AC-4: Hotline và link Zalo
Given: cấu hình cửa hàng hard-code có hotline và link Zalo
When: người dùng mở trang chủ
Then: hotline và link Zalo hiển thị đúng giá trị cấu hình

### AC-5: Ẩn khối rỗng
Given: không có sản phẩm nào thuộc một khối
When: người dùng mở trang chủ
Then: khối đó không được hiển thị

### AC-6: Lỗi tải dữ liệu
Given: hệ thống không lấy được danh sách sản phẩm
When: người dùng mở trang chủ
Then: trang vẫn hiển thị khung trang và thông báo lỗi, không hiển thị trang trắng

### AC-7: Khối bán chạy xếp theo tổng số lượng bán
Given: trong 7 ngày gần nhất có đơn 1 mua 5 cái sản phẩm A (2 cái màu đỏ, 3 cái màu xanh); đơn 2 và đơn 3 mỗi đơn mua 1 cái sản phẩm B; cả A và B đang bán
When: người dùng mở trang chủ sau khi tác vụ tính bán chạy đã chạy
Then: khối bán chạy hiển thị A trước B (A = 5, B = 2)

### AC-8: Chỉ tính đơn trong 7 ngày gần nhất
Given: sản phẩm C chỉ có đơn đặt cách đây 8 ngày
When: người dùng mở trang chủ
Then: C không nằm trong khối bán chạy

### AC-9: Tối đa 5 sản phẩm
Given: có 7 sản phẩm đang bán có đơn trong 7 ngày gần nhất
When: người dùng mở trang chủ
Then: khối bán chạy hiển thị đúng 5 sản phẩm có tổng số lượng bán lớn nhất

### AC-10: Sản phẩm ngừng bán biến mất ngay khỏi khối bán chạy
Given: sản phẩm A đang nằm trong khối bán chạy
When: Nhân viên chuyển A sang Ngừng bán (UC-14), rồi người dùng tải lại trang chủ ngay sau đó
Then: A không còn trong khối bán chạy, không phải chờ lần chạy tiếp theo của tác vụ

### AC-11: Tính cả đơn chưa giao
Given: sản phẩm D chỉ có đơn ở trạng thái "Chưa xử lý" trong 7 ngày gần nhất
When: người dùng mở trang chủ sau khi tác vụ đã chạy
Then: D được tính vào khối bán chạy

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính, UC-19, UC-20 (đơn đặt hàng cho khối bán chạy), UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-10 Xem sản phẩm theo danh mục, UC-11 Tìm kiếm sản phẩm, UC-12 Xem chi tiết sản phẩm
- **External Systems:** Redis (cache khối trang chủ và khối bán chạy)

## Notes
- Áp dụng constraint cache (BR-GIAIDOAN1, Constraints chung — Cache): dữ liệu các khối trang chủ cache ở Redis theo số phiên bản catalog, TTL dự phòng 5 phút; HTML render lại mỗi request (header có phần riêng của người dùng) và trả `Cache-Control: private, no-cache`, không dùng `ETag` (đã chốt 21/11/2026).
- Khối bán chạy theo BR-002 Constraints (đã chốt 21/11/2026): tác vụ chạy mỗi 10 phút tính top 15 sản phẩm theo tổng số lượng bán (cộng mọi biến thể) của các đơn đặt trong 7 ngày gần nhất, ghi vào Redis (TTL 30 phút); khi hiển thị bỏ sản phẩm Ngừng bán rồi lấy 5 sản phẩm đầu; tên, ảnh, giá lấy tại lúc hiển thị.
- Khối bán chạy ở trang chủ khác "Sản phẩm bán chạy" trên dashboard (UC-37): trang chủ tính 7 ngày gần nhất, mọi đơn từ lúc đặt; dashboard tính theo kỳ báo cáo, chỉ đơn "Giao thành công".
- Out of Scope (BR-GIAIDOAN1): mega menu, thanh thông báo chạy, banner tùy chỉnh, thêm nhanh vào giỏ từ thẻ sản phẩm.

### Quyết định đã chốt
- Có khối bán chạy: top 5 sản phẩm (không theo biến thể), 7 ngày gần nhất, tính đơn từ lúc đặt, xếp theo tổng số lượng bán; Ngừng bán thì biến mất ngay khỏi khối (đã chốt 21/11/2026).

### Giả định [GD]
- Trang chủ gồm khối hàng mới và khối sản phẩm theo bộ sưu tập.
- Khối không có sản phẩm thì ẩn.
- Khối bán chạy: "7 ngày gần nhất" là 7 × 24 giờ tính lùi từ lúc tính; loại đơn "Đã hủy"; còn dưới 5 sản phẩm sau khi lọc thì hiển thị số còn lại.
- Khối bán chạy thuộc module `reporting`, lấy số lượng bán qua service của `ordering` và lọc trạng thái sản phẩm qua service của `catalog`.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-21): theo BR-GIAIDOAN1 v20 — thêm khối bán chạy (bước 2, AC-7 → AC-11); ghi chiến lược cache
- v3 (2026-11-21): theo BR-GIAIDOAN1 v22 — HTML trang chủ không còn `public, max-age=60`; trả `private, no-cache` + `ETag`, chỉ cache dữ liệu ở Redis (Notes)
- v4 (2026-11-21): theo BR-GIAIDOAN1 v23 — bỏ `ETag` (Notes)
