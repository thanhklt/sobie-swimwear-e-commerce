# UC-13: Xem trang giới thiệu, chính sách, FAQ

## Metadata
- **ID:** UC-13
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng bấm vào liên kết Giới thiệu, Chính sách hoặc FAQ (ví dụ ở chân trang).

## Preconditions
- Không có.

## Main Flow
1. Người dùng chọn một trang thông tin.
2. Hệ thống hiển thị nội dung trang tương ứng.

## Alternative Flows
- Không có.

## Exceptions
- **E1. Trang không tồn tại:** hệ thống hiển thị trang "Không tìm thấy trang".

## Postconditions
- Nội dung trang thông tin được hiển thị; dữ liệu không thay đổi.

## Acceptance Criteria

### AC-1: Xem trang giới thiệu
Given: người dùng ở bất kỳ trang nào của storefront
When: người dùng bấm liên kết "Giới thiệu"
Then: trang giới thiệu cửa hàng được hiển thị

### AC-2: Xem trang chính sách
Given: người dùng ở bất kỳ trang nào của storefront
When: người dùng bấm liên kết "Chính sách"
Then: trang chính sách được hiển thị

### AC-3: Xem trang FAQ
Given: người dùng ở bất kỳ trang nào của storefront
When: người dùng bấm liên kết "FAQ"
Then: trang câu hỏi thường gặp được hiển thị

### AC-4: Trang không tồn tại
Given: đường dẫn trang thông tin không tồn tại
When: người dùng truy cập đường dẫn đó
Then: hệ thống hiển thị trang "Không tìm thấy trang"

## Dependencies
- **Upstream UC:** không có
- **Downstream UC:** không có
- **External Systems:** không có

## Notes
- Out of Scope (BR-GIAIDOAN1): blog, trang cộng đồng, góp ý.

### Quyết định đã chốt
- Nội dung trang giới thiệu, chính sách, FAQ cố định, không chỉnh sửa trên hệ thống; chỉ thông tin sản phẩm là sửa được (đã chốt 15/11/2026).

### Giả định [GD]
- Chỉ có một trang chính sách chung.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt nội dung trang giới thiệu, chính sách, FAQ cố định, không chỉnh sửa
