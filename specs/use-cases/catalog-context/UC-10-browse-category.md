# UC-10: Xem sản phẩm theo danh mục

## Metadata
- **ID:** UC-10
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng chọn một danh mục từ menu hoặc trang chủ.

## Preconditions
- Danh mục tồn tại.

## Main Flow
1. Người dùng chọn một danh mục.
2. Hệ thống lấy các sản phẩm Đang bán thuộc danh mục, sắp xếp mặc định theo mới nhất.
3. Hệ thống hiển thị trang 1 với số sản phẩm mỗi trang cố định `[GD]` (12), kèm điều khiển phân trang và tổng số sản phẩm.
4. Hệ thống hiển thị bộ lọc: giới tính, size, danh mục, bộ sưu tập.
5. Mỗi thẻ hiển thị ảnh, tên, giá bán thấp nhất theo size `[GD]`, giá sau khuyến mãi theo sản phẩm (nếu có), nhãn "Hết hàng" khi mọi biến thể hết hàng.
6. Người dùng bấm một thẻ để xem chi tiết (UC-12).

## Alternative Flows
- **4a. Lọc sản phẩm:** người dùng chọn giá trị cho một hoặc nhiều tiêu chí lọc (giới tính, size, danh mục, bộ sưu tập); hệ thống chỉ hiển thị sản phẩm thỏa đồng thời mọi tiêu chí đã chọn `[GD]` và quay về trang 1. Mỗi tiêu chí chọn một giá trị `[GD]`.
- **4b. Lọc theo size:** sản phẩm được hiển thị khi có ít nhất một biến thể thuộc size đã chọn, không xét còn hàng hay hết hàng `[GD]`.
- **4c. Lọc theo danh mục khác:** người dùng chọn danh mục khác trong bộ lọc; hệ thống hiển thị sản phẩm của danh mục đó, giữ các tiêu chí lọc còn lại.
- **4d. Bỏ lọc:** người dùng xóa một hoặc mọi tiêu chí lọc; hệ thống hiển thị lại danh sách theo các tiêu chí còn lại và quay về trang 1.
- **4e. Không có sản phẩm khớp bộ lọc:** hệ thống hiển thị "Không có sản phẩm phù hợp".
- **3a. Đổi tiêu chí sắp xếp:** người dùng chọn tiêu chí khác (giá tăng dần, giá giảm dần `[GD]`); hệ thống sắp xếp lại và quay về trang 1.
- **3b. Chuyển trang:** người dùng chọn trang khác; hệ thống hiển thị sản phẩm của trang đó, giữ nguyên tiêu chí lọc và sắp xếp.
- **2a. Danh mục không có sản phẩm Đang bán:** hệ thống hiển thị "Chưa có sản phẩm trong danh mục này".

## Exceptions
- **E1. Danh mục không tồn tại:** hệ thống hiển thị trang "Không tìm thấy danh mục".
- **E2. Số trang vượt quá tổng số trang:** hệ thống hiển thị trang cuối cùng `[GD]`.
- **E3. Giá trị lọc không tồn tại:** giá trị giới tính, size, danh mục hoặc bộ sưu tập không tồn tại — hệ thống bỏ qua tiêu chí đó và hiển thị danh sách theo các tiêu chí còn lại `[GD]`.

## Postconditions
- Danh sách sản phẩm theo danh mục và bộ lọc được hiển thị; dữ liệu không thay đổi.

## Acceptance Criteria

### AC-1: Chỉ hiển thị sản phẩm Đang bán của danh mục
Given: danh mục "Bikini" có 3 sản phẩm Đang bán và 1 sản phẩm Ngừng bán
When: người dùng mở danh mục "Bikini"
Then: chỉ 3 sản phẩm Đang bán được hiển thị

### AC-2: Phân trang
Given: danh mục có 30 sản phẩm Đang bán, mỗi trang 12 sản phẩm
When: người dùng mở danh mục
Then: trang 1 hiển thị 12 sản phẩm
And: có 3 trang, tổng số sản phẩm hiển thị là 30

### AC-3: Sắp xếp mặc định mới nhất
Given: danh mục có sản phẩm A tạo ngày 01/11 và sản phẩm B tạo ngày 10/11
When: người dùng mở danh mục mà không chọn sắp xếp
Then: sản phẩm B đứng trước sản phẩm A

### AC-4: Đổi tiêu chí sắp xếp
Given: danh mục có nhiều sản phẩm với giá khác nhau
When: người dùng chọn sắp xếp "Giá tăng dần"
Then: sản phẩm được sắp theo giá tăng dần
And: danh sách quay về trang 1

### AC-5: Lọc theo giới tính
Given: danh mục có 2 sản phẩm giới tính "Nữ" và 1 sản phẩm giới tính "Nam"
When: người dùng lọc giới tính "Nữ"
Then: chỉ 2 sản phẩm giới tính "Nữ" được hiển thị
And: danh sách quay về trang 1

### AC-6: Lọc theo size
Given: sản phẩm A có biến thể size M, sản phẩm B chỉ có size S
When: người dùng lọc size "M"
Then: chỉ sản phẩm A được hiển thị

### AC-7: Lọc theo bộ sưu tập
Given: sản phẩm A thuộc bộ sưu tập "Hè 2026", sản phẩm B không thuộc
When: người dùng lọc bộ sưu tập "Hè 2026"
Then: chỉ sản phẩm A được hiển thị

### AC-8: Kết hợp nhiều tiêu chí lọc
Given: sản phẩm A giới tính "Nữ" có size M; sản phẩm B giới tính "Nữ" chỉ có size S; sản phẩm C giới tính "Nam" có size M
When: người dùng lọc giới tính "Nữ" và size "M"
Then: chỉ sản phẩm A được hiển thị

### AC-9: Đổi danh mục trong bộ lọc
Given: người dùng đang xem danh mục "Bikini" với lọc giới tính "Nữ"
When: người dùng chọn danh mục "Áo bơi liền thân" trong bộ lọc
Then: hệ thống hiển thị sản phẩm "Nữ" của danh mục "Áo bơi liền thân"

### AC-10: Không có sản phẩm khớp bộ lọc
Given: không có sản phẩm nào giới tính "Nam" có size "XS"
When: người dùng lọc giới tính "Nam" và size "XS"
Then: hệ thống hiển thị "Không có sản phẩm phù hợp"

### AC-11: Giữ lọc và sắp xếp khi chuyển trang
Given: người dùng đang xem danh mục lọc giới tính "Nữ", sắp xếp "Giá tăng dần"
When: người dùng chuyển sang trang 2
Then: trang 2 vẫn lọc giới tính "Nữ" và sắp xếp theo "Giá tăng dần"

### AC-12: Danh mục rỗng
Given: danh mục không có sản phẩm Đang bán
When: người dùng mở danh mục
Then: hệ thống hiển thị "Chưa có sản phẩm trong danh mục này"

### AC-13: Danh mục không tồn tại
Given: mã danh mục không tồn tại
When: người dùng truy cập danh mục đó
Then: hệ thống hiển thị trang "Không tìm thấy danh mục"

### AC-14: Trang vượt quá tổng số trang
Given: danh mục chỉ có 2 trang
When: người dùng yêu cầu trang 5
Then: hệ thống hiển thị trang 2

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm, UC-16 Quản lý giá bán theo size, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).
- Out of Scope (BR-TUAN1): mega menu, bộ lọc nâng cao (ngoài 4 tiêu chí giới tính, size, danh mục, bộ sưu tập), thêm nhanh vào giỏ từ thẻ sản phẩm.

### Quyết định đã chốt
- Lọc sản phẩm theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- Sắp xếp mặc định theo sản phẩm mới nhất (đã chốt 15/11/2026).

### Giả định [GD]
- Các tiêu chí sắp xếp khác ngoài mặc định: giá tăng dần, giá giảm dần.
- Các tiêu chí lọc kết hợp theo kiểu "và" (thỏa đồng thời); mỗi tiêu chí chọn một giá trị.
- Lọc theo size: sản phẩm có ít nhất một biến thể size đó, không xét còn hàng.
- Giá trị lọc không tồn tại thì bỏ qua tiêu chí đó.
- Mỗi trang 12 sản phẩm.
- Thẻ sản phẩm hiển thị giá thấp nhất trong các size.
- Yêu cầu trang vượt quá tổng số trang thì hiển thị trang cuối.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): thêm lọc theo giới tính, size, danh mục, bộ sưu tập; chốt sắp xếp mặc định mới nhất; thêm AC lọc
