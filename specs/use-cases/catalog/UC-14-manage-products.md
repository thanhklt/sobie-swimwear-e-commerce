# UC-14: Quản lý sản phẩm

## Metadata
- **ID:** UC-14
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Sản phẩm trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Đã có ít nhất một danh mục (UC-17).

## Main Flow
1. Hệ thống hiển thị danh sách sản phẩm có phân trang, tìm theo tên, kèm trạng thái Đang bán / Ngừng bán `[GD]`.
2. Nhân viên chọn "Thêm sản phẩm".
3. Nhân viên nhập thông tin: tên, mô tả, 1 danh mục, 1 giới tính, bộ sưu tập (có thể nhiều), bộ ảnh (gallery) có thứ tự hiển thị. Tên, danh mục và giới tính là bắt buộc `[GD]`. Không nhập bảng size: cửa hàng dùng một bảng size chung cố định.
4. Hệ thống kiểm tra dữ liệu hợp lệ và lưu sản phẩm ở trạng thái Ngừng bán `[GD]`.
5. Nhân viên thêm biến thể (UC-15) và giá theo size (UC-16), rồi chuyển sản phẩm sang Đang bán.

## Alternative Flows
- **2a. Sửa sản phẩm:** Nhân viên chọn một sản phẩm, sửa thông tin và lưu; hệ thống kiểm tra như bước 4.
- **2b. Ngừng bán sản phẩm:** Nhân viên chuyển sản phẩm sang Ngừng bán; sản phẩm không còn hiển thị trên storefront.
- **2c. Xóa sản phẩm:** chỉ xóa được sản phẩm chưa phát sinh đơn hàng hoặc phiếu nhập `[GD]`.
- **2d. Sắp xếp bộ ảnh:** Nhân viên thêm, xóa ảnh hoặc đổi thứ tự hiển thị ảnh trong gallery của sản phẩm; hệ thống lưu thứ tự mới.
- **5a. Chuyển Đang bán khi chưa đủ giá:** xem E3.

## Exceptions
- **E1. Thiếu trường bắt buộc:** hệ thống không lưu và chỉ ra trường còn thiếu.
- **E2. Xóa sản phẩm đã phát sinh giao dịch:** hệ thống từ chối và gợi ý chuyển sang Ngừng bán.
- **E3. Chuyển Đang bán khi sản phẩm chưa có biến thể hoặc có size chưa có giá:** hệ thống từ chối và báo lý do `[GD]`.

## Postconditions
- Sản phẩm được tạo, cập nhật, đổi trạng thái hoặc xóa đúng theo thao tác.

## Acceptance Criteria

### AC-1: Thêm sản phẩm
Given: Nhân viên đã đăng nhập và có danh mục "Bikini"
When: Nhân viên nhập đủ thông tin bắt buộc và lưu
Then: sản phẩm được tạo ở trạng thái Ngừng bán
And: sản phẩm xuất hiện trong danh sách quản trị

### AC-2: Thiếu trường bắt buộc
Given: Nhân viên đang thêm sản phẩm
When: Nhân viên để trống tên và lưu
Then: hệ thống không lưu và báo "Tên sản phẩm là bắt buộc"

### AC-3: Sửa sản phẩm
Given: sản phẩm A đã tồn tại
When: Nhân viên đổi mô tả và lưu
Then: mô tả mới hiển thị trên trang chi tiết sản phẩm A

### AC-4: Chuyển Đang bán
Given: sản phẩm A có ít nhất một biến thể và mọi size đều có giá
When: Nhân viên chuyển A sang Đang bán
Then: sản phẩm A hiển thị trên storefront

### AC-5: Chặn chuyển Đang bán khi thiếu giá
Given: sản phẩm A có size L chưa có giá
When: Nhân viên chuyển A sang Đang bán
Then: hệ thống từ chối và báo "Size L chưa có giá bán"

### AC-6: Ngừng bán
Given: sản phẩm A đang bán
When: Nhân viên chuyển A sang Ngừng bán
Then: A không còn xuất hiện ở trang chủ, danh mục, tìm kiếm và trang chi tiết

### AC-7: Chặn xóa sản phẩm đã có giao dịch
Given: sản phẩm A đã có trong ít nhất một đơn hàng
When: Nhân viên xóa A
Then: hệ thống từ chối và gợi ý chuyển sang Ngừng bán

### AC-8: Xóa sản phẩm chưa có giao dịch
Given: sản phẩm B chưa có trong đơn hàng hoặc phiếu nhập nào
When: Nhân viên xóa B
Then: B bị xóa khỏi danh sách

### AC-9: Phân quyền
Given: người dùng đăng nhập với vai trò Khách hàng
When: người dùng truy cập chức năng quản lý sản phẩm
Then: hệ thống từ chối truy cập

### AC-10: Sản phẩm có 1 danh mục, 1 giới tính, nhiều bộ sưu tập
Given: có danh mục "Bikini", giới tính "Nữ", bộ sưu tập "Hè 2026" và "Biển xanh"
When: Nhân viên tạo sản phẩm với danh mục "Bikini", giới tính "Nữ", bộ sưu tập "Hè 2026" và "Biển xanh"
Then: sản phẩm được lưu với đúng 1 danh mục, 1 giới tính và 2 bộ sưu tập

### AC-11: Thiếu giới tính
Given: Nhân viên đang thêm sản phẩm
When: Nhân viên không chọn giới tính và lưu
Then: hệ thống không lưu và báo "Giới tính là bắt buộc"

### AC-12: Đổi thứ tự ảnh
Given: sản phẩm A có ảnh X ở vị trí 1 và ảnh Y ở vị trí 2
When: Nhân viên đổi ảnh Y lên vị trí 1 và lưu
Then: trang chi tiết sản phẩm A hiển thị ảnh Y trước ảnh X

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính
- **Downstream UC:** UC-09, UC-10, UC-11, UC-12, UC-15 Quản lý biến thể màu × size, UC-16 Quản lý giá bán theo size, UC-28 Quản lý khuyến mãi theo sản phẩm, UC-33 Lập phiếu nhập
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung). Khi sản phẩm thay đổi, danh sách hiển thị trên storefront phải được làm mới theo chiến lược cache đã chốt.

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Sản phẩm gồm tên, mô tả, trạng thái, 1 danh mục, 1 giới tính, nhiều bộ sưu tập, bộ ảnh (gallery) gắn theo sản phẩm có thứ tự hiển thị (theo ERD, đã chốt 15/11/2026).
- Đánh giá sản phẩm (review) để giai đoạn 2, không làm trong MVP (đã chốt 15/11/2026).
- Bảng size không phải trường của sản phẩm; cả cửa hàng dùng một bảng size chung, nội dung cố định (hard-code như trang thông tin) (đã chốt 15/11/2026).

### Giả định [GD]
- Sản phẩm có 2 trạng thái: Đang bán, Ngừng bán; sản phẩm mới tạo ở trạng thái Ngừng bán.
- Tên, danh mục, giới tính là trường bắt buộc.
- Chỉ chuyển Đang bán khi đã có biến thể và mọi size đã có giá.
- Không xóa sản phẩm đã có trong đơn hàng hoặc phiếu nhập.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt chỉ Nhân viên quản lý sản phẩm
- v3 (2026-11-15): theo ERD — thông tin sản phẩm gồm 1 danh mục, 1 giới tính, nhiều bộ sưu tập, gallery có thứ tự; review để giai đoạn 2; thêm AC-10 → AC-12
- v4 (2026-11-15): chốt bảng size chung cố định, bỏ bảng size khỏi thông tin sản phẩm
