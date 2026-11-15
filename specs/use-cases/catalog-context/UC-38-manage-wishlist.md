# UC-38: Quản lý danh sách yêu thích

## Metadata
- **ID:** UC-38
- **Bounded Context:** catalog-context `[GD]`
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách hàng

## Trigger
Khách hàng bấm nút thả tim trên thẻ sản phẩm hoặc trang chi tiết sản phẩm, hoặc mở trang "Danh sách yêu thích".

## Preconditions
- Khách hàng đang đăng nhập (UC-02).

## Main Flow
1. Khách hàng bấm nút thả tim trên một sản phẩm chưa có trong danh sách yêu thích (trên thẻ sản phẩm `[GD]` hoặc trang chi tiết UC-12).
2. Hệ thống lưu sản phẩm vào danh sách yêu thích của tài khoản và hiển thị nút tim ở trạng thái đã chọn.
3. Khách hàng mở trang "Danh sách yêu thích".
4. Hệ thống hiển thị các sản phẩm trong danh sách, mới thêm nhất trước `[GD]`, có phân trang `[GD]`: ảnh, tên, giá bán thấp nhất theo size, giá sau khuyến mãi theo sản phẩm (nếu có).
5. Khách hàng bấm một sản phẩm để xem chi tiết (UC-12).

## Alternative Flows
- **1a. Bỏ tim:** Khách hàng bấm nút tim của sản phẩm đã có trong danh sách (trên thẻ, trang chi tiết hoặc trang danh sách yêu thích); hệ thống xóa sản phẩm khỏi danh sách và đưa nút tim về trạng thái chưa chọn.
- **1b. Khách vãng lai bấm tim:** hệ thống yêu cầu đăng nhập (UC-02); sau khi đăng nhập, khách quay lại trang đang xem `[GD]` và có thể bấm tim lại.
- **4a. Danh sách rỗng:** hệ thống hiển thị "Bạn chưa có sản phẩm yêu thích".
- **4b. Sản phẩm đã ngừng bán:** sản phẩm vẫn nằm trong danh sách nhưng hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết `[GD]`; khách vẫn bỏ tim được.

## Exceptions
- **E1. Sản phẩm đã có trong danh sách:** yêu cầu thêm trùng (ví dụ bấm tim hai lần liên tiếp từ hai thẻ) — hệ thống không tạo thêm bản ghi, danh sách vẫn chỉ có sản phẩm đó một lần.
- **E2. Sản phẩm không tồn tại:** hệ thống báo "Không tìm thấy sản phẩm", không lưu.

## Postconditions
- Danh sách yêu thích của tài khoản có hoặc không có sản phẩm đúng theo thao tác; mỗi sản phẩm xuất hiện tối đa một lần.

## Acceptance Criteria

### AC-1: Thả tim sản phẩm
Given: Khách hàng đang đăng nhập, sản phẩm A chưa có trong danh sách yêu thích
When: Khách hàng bấm nút tim của sản phẩm A
Then: sản phẩm A được thêm vào danh sách yêu thích
And: nút tim của sản phẩm A hiển thị trạng thái đã chọn

### AC-2: Bỏ tim sản phẩm
Given: sản phẩm A đang có trong danh sách yêu thích của Khách hàng
When: Khách hàng bấm lại nút tim của sản phẩm A
Then: sản phẩm A bị xóa khỏi danh sách yêu thích
And: nút tim trở về trạng thái chưa chọn

### AC-3: Xem danh sách yêu thích
Given: Khách hàng đã thả tim sản phẩm A rồi sản phẩm B
When: Khách hàng mở trang "Danh sách yêu thích"
Then: hệ thống hiển thị sản phẩm B rồi đến sản phẩm A, kèm ảnh, tên và giá

### AC-4: Không trùng sản phẩm
Given: sản phẩm A đã có trong danh sách yêu thích
When: hệ thống nhận thêm một yêu cầu thêm sản phẩm A cho cùng tài khoản
Then: danh sách vẫn chỉ có sản phẩm A một lần

### AC-5: Khách vãng lai bấm tim
Given: người dùng chưa đăng nhập
When: người dùng bấm nút tim của sản phẩm A
Then: hệ thống chuyển tới trang đăng nhập
And: sản phẩm A không được lưu vào danh sách nào

### AC-6: Danh sách rỗng
Given: Khách hàng chưa thả tim sản phẩm nào
When: Khách hàng mở trang "Danh sách yêu thích"
Then: hệ thống hiển thị "Bạn chưa có sản phẩm yêu thích"

### AC-7: Sản phẩm ngừng bán trong danh sách
Given: sản phẩm A trong danh sách yêu thích chuyển sang Ngừng bán
When: Khách hàng mở trang "Danh sách yêu thích"
Then: sản phẩm A vẫn hiển thị kèm nhãn "Ngừng bán"
And: Khách hàng bỏ tim được sản phẩm A

### AC-8: Danh sách riêng theo tài khoản
Given: Khách hàng X đã thả tim sản phẩm A, Khách hàng Y chưa thả tim sản phẩm nào
When: Khách hàng Y mở trang "Danh sách yêu thích"
Then: sản phẩm A không xuất hiện trong danh sách của Y

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-10 Xem sản phẩm theo danh mục, UC-12 Xem chi tiết sản phẩm, UC-14 Quản lý sản phẩm
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).

### Quyết định đã chốt
- Wishlist là chức năng trong phạm vi MVP: khách thả tim để lưu sản phẩm vào một danh sách (đã chốt 15/11/2026).
- Mỗi sản phẩm chỉ xuất hiện 1 lần trong danh sách của một tài khoản (theo ERD: unique account + product).

### Giả định [GD]
- UC thuộc catalog-context.
- Nút tim có trên cả thẻ sản phẩm và trang chi tiết.
- Khách vãng lai bấm tim thì được yêu cầu đăng nhập; sau đăng nhập quay lại trang đang xem, không tự lưu sản phẩm.
- Danh sách yêu thích sắp xếp mới thêm nhất trước (theo thứ tự thêm; ERD không có cột thời gian riêng), có phân trang.
- Sản phẩm ngừng bán vẫn ở danh sách, hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo data model v1 — sắp xếp theo thứ tự thêm, không dùng cột thời gian
