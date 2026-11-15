# UC-11: Tìm kiếm sản phẩm

## Metadata
- **ID:** UC-11
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng nhập tên hoặc từ khóa vào ô tìm kiếm và gửi.

## Preconditions
- Không có.

## Main Flow
1. Người dùng nhập tên hoặc từ khóa và gửi.
2. Hệ thống tìm các sản phẩm Đang bán có tên hoặc từ khóa khớp, không phân biệt hoa thường và dấu tiếng Việt `[GD]`.
3. Hệ thống hiển thị kết quả có phân trang (cùng số sản phẩm mỗi trang và cùng tiêu chí sắp xếp như UC-10), kèm từ khóa đã tìm và tổng số kết quả.
4. Người dùng bấm một thẻ để xem chi tiết (UC-12).

## Alternative Flows
- **3a. Đổi tiêu chí sắp xếp hoặc chuyển trang:** xử lý như UC-10 (3a, 3b), giữ nguyên từ khóa.
- **2a. Không có kết quả:** hệ thống hiển thị "Không tìm thấy sản phẩm phù hợp với '<từ khóa>'".

## Exceptions
- **E1. Từ khóa rỗng hoặc chỉ có khoảng trắng:** hệ thống không thực hiện tìm kiếm và nhắc "Vui lòng nhập từ khóa".

## Postconditions
- Kết quả tìm kiếm được hiển thị; dữ liệu không thay đổi.

## Acceptance Criteria

### AC-1: Tìm theo tên
Given: có sản phẩm Đang bán tên "Bikini hoa nhí"
When: người dùng tìm "bikini"
Then: sản phẩm "Bikini hoa nhí" có trong kết quả

### AC-2: Không phân biệt hoa thường và dấu
Given: có sản phẩm Đang bán tên "Đồ bơi liền thân"
When: người dùng tìm "do boi lien than"
Then: sản phẩm "Đồ bơi liền thân" có trong kết quả

### AC-3: Không trả về sản phẩm Ngừng bán
Given: sản phẩm "Bikini đỏ" ở trạng thái Ngừng bán
When: người dùng tìm "bikini đỏ"
Then: sản phẩm đó không có trong kết quả

### AC-4: Phân trang kết quả
Given: có 20 sản phẩm khớp từ khóa, mỗi trang 12 sản phẩm
When: người dùng tìm từ khóa đó
Then: trang 1 hiển thị 12 sản phẩm, tổng số kết quả là 20
And: khi chuyển sang trang 2, từ khóa vẫn được giữ và hiển thị 8 sản phẩm

### AC-5: Không có kết quả
Given: không có sản phẩm nào khớp "xyz123"
When: người dùng tìm "xyz123"
Then: hệ thống hiển thị "Không tìm thấy sản phẩm phù hợp với 'xyz123'"

### AC-6: Từ khóa rỗng
Given: người dùng để trống ô tìm kiếm
When: người dùng gửi tìm kiếm
Then: hệ thống không tìm kiếm và hiển thị "Vui lòng nhập từ khóa"

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).
- Out of Scope (BR-TUAN1): bộ lọc nâng cao.

### Giả định [GD]
- Tìm kiếm không phân biệt hoa thường và dấu tiếng Việt.
- "Từ khóa" khớp trên tên và mô tả sản phẩm.

## History
- v1 (2026-11-15): initial
