# UC-17: Quản lý danh mục, bộ sưu tập và thuộc tính

## Metadata
- **ID:** UC-17
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Danh mục, Bộ sưu tập, Giới tính, Màu hoặc Size trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên chọn loại cần quản lý: Danh mục, Bộ sưu tập, Giới tính, Màu hoặc Size.
2. Hệ thống hiển thị danh sách hiện có của loại đó.
3. Nhân viên thêm mới: nhập tên (ví dụ Giới tính: Nữ, Nam; Màu: Đỏ, Xanh; Size: S, M, L).
4. Hệ thống kiểm tra tên không trùng trong cùng loại và lưu.

## Alternative Flows
- **3a. Sửa:** Nhân viên đổi tên và lưu; các sản phẩm, biến thể đang gắn được cập nhật theo.
- **3b. Xóa mục chưa được dùng:** hệ thống xóa.
- **3c. Xóa mục đang được sản phẩm hoặc biến thể sử dụng:** xem E2.

## Exceptions
- **E1. Tên trống hoặc trùng trong cùng loại:** hệ thống không lưu và báo lỗi.
- **E2. Xóa danh mục, bộ sưu tập, giới tính, màu hoặc size đang được sản phẩm/biến thể sử dụng:** hệ thống từ chối và báo số sản phẩm đang dùng `[GD]`.

## Postconditions
- Danh mục, bộ sưu tập, giới tính, màu, size được cập nhật và dùng được khi tạo/sửa sản phẩm (UC-14), biến thể (UC-15) và lọc sản phẩm (UC-10).

## Acceptance Criteria

### AC-1: Thêm danh mục
Given: chưa có danh mục "Đồ bơi liền thân"
When: Nhân viên thêm danh mục "Đồ bơi liền thân"
Then: danh mục xuất hiện trong danh sách và trong menu danh mục của storefront

### AC-2: Tên trùng
Given: đã có danh mục "Bikini"
When: Nhân viên thêm danh mục "Bikini"
Then: hệ thống không lưu và báo "Tên đã tồn tại"

### AC-3: Thêm bộ sưu tập
Given: Nhân viên đang ở mục Bộ sưu tập
When: Nhân viên thêm bộ sưu tập "Hè 2026"
Then: bộ sưu tập "Hè 2026" chọn được khi tạo hoặc sửa sản phẩm

### AC-4: Thêm màu
Given: Nhân viên đang ở mục Màu
When: Nhân viên thêm màu "Vàng"
Then: màu "Vàng" chọn được khi tạo biến thể (UC-15)

### AC-5: Thêm giới tính
Given: Nhân viên đang ở mục Giới tính
When: Nhân viên thêm giới tính "Trẻ em"
Then: giới tính "Trẻ em" chọn được khi tạo sản phẩm (UC-14) và xuất hiện trong bộ lọc (UC-10)

### AC-6: Thêm size
Given: Nhân viên đang ở mục Size
When: Nhân viên thêm size "XL"
Then: size "XL" chọn được khi tạo biến thể (UC-15) và xuất hiện trong bộ lọc (UC-10)

### AC-7: Chặn xóa mục đang dùng
Given: danh mục "Bikini" đang có 3 sản phẩm
When: Nhân viên xóa danh mục "Bikini"
Then: hệ thống từ chối và báo "Đang có 3 sản phẩm thuộc danh mục này"

### AC-8: Xóa mục chưa dùng
Given: bộ sưu tập "Thu 2026" chưa gắn với sản phẩm nào
When: Nhân viên xóa "Thu 2026"
Then: bộ sưu tập bị xóa khỏi danh sách

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** UC-09, UC-10 Xem sản phẩm theo danh mục, UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).
- Out of Scope (BR-TUAN1): mega menu.

### Quyết định đã chốt
- Phân loại gồm 5 loại: danh mục, bộ sưu tập, giới tính, màu, size; mỗi loại là một danh sách tên (theo ERD, đã chốt 15/11/2026).
- Thuộc tính sản phẩm gồm giới tính, màu, size (theo ERD, đã chốt 15/11/2026).
- Mỗi sản phẩm thuộc 1 danh mục, 1 giới tính và nhiều bộ sưu tập; biến thể = màu × size (theo ERD, đã chốt 15/11/2026).

### Giả định [GD]
- Danh mục một cấp (không có danh mục con).
- Không xóa danh mục, bộ sưu tập, giới tính, màu hoặc size đang được sử dụng.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo ERD — phân loại gồm danh mục, bộ sưu tập, giới tính, màu, size; chốt thuộc tính sản phẩm; thêm AC-5, AC-6
