# UC-09: Xem trang chủ

## Metadata
- **ID:** UC-09
- **Bounded Context:** catalog-context
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
2. Hệ thống hiển thị các khối sản phẩm đang bán `[GD]`: hàng mới, sản phẩm theo bộ sưu tập.
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

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-10 Xem sản phẩm theo danh mục, UC-11 Tìm kiếm sản phẩm, UC-12 Xem chi tiết sản phẩm
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung).
- Out of Scope (BR-GIAIDOAN1): mega menu, thanh thông báo chạy, banner tùy chỉnh, thêm nhanh vào giỏ từ thẻ sản phẩm.

### Giả định [GD]
- Trang chủ gồm khối hàng mới và khối sản phẩm theo bộ sưu tập.
- Khối không có sản phẩm thì ẩn.

## History
- v1 (2026-11-15): initial
