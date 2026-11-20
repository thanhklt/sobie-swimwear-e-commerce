# UC-12: Xem chi tiết sản phẩm

## Metadata
- **ID:** UC-12
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng bấm vào một thẻ sản phẩm.

## Preconditions
- Sản phẩm tồn tại và ở trạng thái Đang bán.

## Main Flow
1. Người dùng mở trang chi tiết sản phẩm.
2. Hệ thống hiển thị tên, mô tả, bộ ảnh (gallery) của sản phẩm theo thứ tự hiển thị, các màu và size có sẵn, bảng size chung của cửa hàng, nút thả tim (yêu thích).
3. Người dùng chọn màu; bộ ảnh không thay đổi theo màu.
4. Người dùng chọn size; hệ thống hiển thị giá bán của size đó (mọi màu cùng size có cùng giá) và tình trạng còn/hết hàng của biến thể (màu × size) đã chọn.
5. Nếu sản phẩm có khuyến mãi theo sản phẩm còn hiệu lực, hệ thống hiển thị giá gốc và giá sau giảm.
6. Người dùng chọn số lượng và thêm vào giỏ hàng (UC-18).

## Alternative Flows
- **2a. Thả tim sản phẩm:** người dùng bấm nút thả tim; hệ thống lưu hoặc bỏ sản phẩm khỏi danh sách yêu thích (UC-38).
- **4a. Biến thể đã chọn hết hàng:** hệ thống hiển thị "Hết hàng" và vô hiệu hóa nút thêm vào giỏ.
- **4b. Chưa chọn đủ màu và size:** nút thêm vào giỏ bị vô hiệu hóa, hệ thống nhắc "Vui lòng chọn màu và size".

## Exceptions
- **E1. Sản phẩm không tồn tại hoặc Ngừng bán:** hệ thống hiển thị trang "Không tìm thấy sản phẩm".

## Postconditions
- Trang chi tiết sản phẩm được hiển thị; dữ liệu không thay đổi (trừ khi người dùng thả tim, xem UC-38).

## Acceptance Criteria

### AC-1: Hiển thị thông tin sản phẩm
Given: sản phẩm A Đang bán, có bộ ảnh và mô tả
When: người dùng mở trang chi tiết sản phẩm A
Then: tên, mô tả, bộ ảnh, các màu, các size, bảng size chung và nút thả tim được hiển thị

### AC-2: Bảng size chung
Given: sản phẩm A và sản phẩm B đều Đang bán
When: người dùng lần lượt mở trang chi tiết sản phẩm A và sản phẩm B
Then: cả hai trang hiển thị cùng một bảng size chung của cửa hàng

### AC-3: Bộ ảnh theo thứ tự hiển thị
Given: sản phẩm A có 3 ảnh với thứ tự hiển thị 1, 2, 3
When: người dùng mở trang chi tiết sản phẩm A
Then: ảnh được hiển thị đúng thứ tự 1, 2, 3

### AC-4: Đổi màu không đổi ảnh
Given: người dùng đang xem sản phẩm A có màu Đỏ và Xanh
When: người dùng chuyển từ màu Đỏ sang màu Xanh
Then: bộ ảnh của sản phẩm giữ nguyên

### AC-5: Giá theo size
Given: sản phẩm A có giá size S = 300.000đ, size M = 320.000đ
When: người dùng chọn size M
Then: giá hiển thị là 320.000đ

### AC-6: Cùng size khác màu cùng giá
Given: sản phẩm A có giá size M = 320.000đ, có màu Đỏ và Xanh
When: người dùng chọn size M, lần lượt với màu Đỏ và màu Xanh
Then: giá hiển thị đều là 320.000đ

### AC-7: Giá sau khuyến mãi theo sản phẩm
Given: sản phẩm A có khuyến mãi theo sản phẩm còn hiệu lực làm giá size M còn 288.000đ
When: người dùng chọn size M
Then: hệ thống hiển thị giá gốc 320.000đ và giá sau giảm 288.000đ

### AC-8: Còn hàng
Given: biến thể Đỏ × M có tồn kho > 0
When: người dùng chọn màu Đỏ và size M
Then: hệ thống hiển thị "Còn hàng" và cho phép thêm vào giỏ

### AC-9: Hết hàng
Given: biến thể Đỏ × L có tồn kho = 0
When: người dùng chọn màu Đỏ và size L
Then: hệ thống hiển thị "Hết hàng"
And: nút thêm vào giỏ bị vô hiệu hóa

### AC-10: Chưa chọn đủ màu và size
Given: người dùng mới chọn màu, chưa chọn size
When: người dùng bấm thêm vào giỏ
Then: hệ thống không thêm vào giỏ và nhắc "Vui lòng chọn màu và size"

### AC-11: Sản phẩm Ngừng bán
Given: sản phẩm B ở trạng thái Ngừng bán
When: người dùng truy cập trang chi tiết sản phẩm B
Then: hệ thống hiển thị trang "Không tìm thấy sản phẩm"

### AC-12: Thả tim từ trang chi tiết
Given: Khách hàng đang đăng nhập, sản phẩm A chưa có trong danh sách yêu thích
When: Khách hàng bấm nút thả tim trên trang chi tiết sản phẩm A
Then: sản phẩm A được thêm vào danh sách yêu thích (UC-38)

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size, UC-16 Quản lý giá bán theo size, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-18 Quản lý giỏ hàng, UC-38 Quản lý danh sách yêu thích
- **External Systems:** không có

## Notes
- Giá sau khuyến mãi theo sản phẩm lấy từ promotion-context (UC-28).
- Tồn kho của biến thể lấy từ inventory-context.
- Out of Scope (BR-GIAIDOAN1): đánh giá sản phẩm (để giai đoạn 2).

### Quyết định đã chốt
- Bộ ảnh (gallery) gắn theo sản phẩm, có thứ tự hiển thị; chọn màu không đổi ảnh (theo ERD, đã chốt 15/11/2026).
- Giá bán đổi theo size; cùng size khác màu cùng giá (đã chốt 15/11/2026).
- Có chức năng thả tim lưu sản phẩm vào danh sách yêu thích (đã chốt 15/11/2026, UC-38).
- Dùng một bảng size chung cho cả cửa hàng, nội dung cố định (hard-code như trang thông tin), không phải trường của sản phẩm (đã chốt 15/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): ảnh theo sản phẩm (theo ERD), chốt giá theo size chung cho mọi màu, thêm nút thả tim dẫn tới UC-38
- v3 (2026-11-15): chốt bảng size chung cố định cho cả cửa hàng; thêm AC-2, đánh số lại AC
