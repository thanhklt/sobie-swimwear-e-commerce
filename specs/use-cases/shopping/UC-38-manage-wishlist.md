# UC-38: Quản lý danh sách yêu thích

## Metadata
- **ID:** UC-38
- **Module:** shopping
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
- **1b. Khách vãng lai bấm tim trên trang chi tiết UC-12:** hệ thống chuyển sang đăng nhập storefront (UC-02) kèm `return_url` nội bộ an toàn của trang chi tiết đang xem. Sau khi đăng nhập thành công và đích được UC-02 kiểm tra, khách quay lại trang đó; hệ thống không tự thêm hoặc xóa wishlist_item. Nếu tài khoản chưa lưu sản phẩm thì tim chưa chọn và khách có thể bấm lại để thích; nếu đã lưu từ trước thì tim đã chọn, bảo toàn wishlist cũ. Thao tác bấm tim sau khi quay lại mới áp dụng Main Flow hoặc 1a.
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
Given: người dùng chưa đăng nhập đang xem chi tiết sản phẩm A tại UC-12; tài khoản Khách hàng sẽ đăng nhập chưa lưu A vào wishlist
When: người dùng bấm nút tim của sản phẩm A
Then: hệ thống chuyển tới đăng nhập storefront kèm return_url nội bộ an toàn của trang chi tiết A và không lưu A chỉ vì lần bấm khi chưa đăng nhập
When: người dùng đăng nhập thành công
Then: hệ thống quay lại trang chi tiết A, nút tim chưa chọn, wishlist vẫn chưa có A; đăng nhập không tự thực hiện thích/bỏ thích
When: Khách hàng chủ động bấm tim tại trang chi tiết sau khi quay lại
Then: hệ thống thêm A theo Main Flow và hiển thị tim đã chọn

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

### AC-9: Bảo toàn sản phẩm đã thích trước khi đăng nhập trở lại
Given: tài khoản Khách hàng X đã có sản phẩm A trong wishlist; X hiện chưa đăng nhập, mở trang chi tiết A và bấm tim để tới đăng nhập
When: X đăng nhập thành công qua UC-02 và quay lại trang chi tiết A theo return_url hợp lệ
Then: wishlist_item của A vẫn giữ nguyên, không bị tạo trùng hoặc xóa bởi việc đăng nhập
And: nút tim hiển thị đã chọn theo dữ liệu hiện có; chỉ thay đổi khi X chủ động thao tác tiếp

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-02 Đăng nhập, UC-06 Tạo tài khoản, UC-10 Xem sản phẩm theo danh mục, UC-12 Xem chi tiết sản phẩm, UC-14 Quản lý sản phẩm
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung).
- UC-02 kiểm tra đích return_url ở server; UC-38 không dùng đích quay lại để tự thực hiện hành động thích/bỏ thích. Đồng bộ lần này chỉ chốt nguồn từ trang chi tiết UC-12; vị trí nút tim trên thẻ và các hành vi khác còn giữ giả định riêng bên dưới.

### Quyết định đã chốt
- Khách vãng lai bấm tim trên trang chi tiết UC-12 đăng nhập xong quay lại bằng return_url nội bộ an toàn; không tự thêm/xóa wishlist_item, tim phản ánh dữ liệu đã lưu của tài khoản. Khách chủ động bấm tim sau khi quay lại để thay đổi (UC-12-Q8, developer yêu cầu đồng bộ tại Codex 23/11/2026).
- Wishlist là chức năng trong phạm vi MVP: khách thả tim để lưu sản phẩm vào một danh sách (đã chốt 15/11/2026).
- Mỗi sản phẩm chỉ xuất hiện 1 lần trong danh sách của một tài khoản (theo ERD: unique account + product).
- Mỗi Khách hàng có đúng 1 danh sách yêu thích trong DB, tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06). Trang danh sách yêu thích luôn có danh sách để đọc / ghi, không tạo danh sách khi thả tim lần đầu (đã chốt 21/11/2026, Q39).

### Giả định [GD]
- UC thuộc module shopping (cùng giỏ hàng), đã chốt 20/11/2026.
- Nút tim có trên cả thẻ sản phẩm và trang chi tiết.
- Danh sách yêu thích sắp xếp mới thêm nhất trước (theo thứ tự thêm; ERD không có cột thời gian riêng), có phân trang.
- Sản phẩm ngừng bán vẫn ở danh sách, hiển thị nhãn "Ngừng bán" và không mở được trang chi tiết.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo data model v1 — sắp xếp theo thứ tự thêm, không dùng cột thời gian
- v3 (2026-11-21): bổ sung giả định tạo danh sách yêu thích cùng lúc tạo tài khoản Khách hàng
- v4 (2026-11-21): chốt tạo danh sách yêu thích cùng lúc tạo tài khoản Khách hàng (Q39)
- v5 (2026-11-23): theo yêu cầu đồng bộ tại Codex, chốt Flow 1b từ trang chi tiết bằng return_url an toàn, không auto-like/unlike, bảo toàn dữ liệu wishlist; mở rộng AC-5 và thêm AC-9 cho sản phẩm đã thích từ trước. Giữ draft và các giả định khác.
