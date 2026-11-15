# UC-26: Tự xuất hóa đơn

## Metadata
- **ID:** UC-26
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Hệ thống

## Trigger
Đơn chuyển sang trạng thái "Giao thành công" (do Trang giả lập vận chuyển cập nhật ở UC-36).

## Preconditions
- Đơn ở trạng thái "Giao thành công" và chưa có hóa đơn.

## Main Flow
1. Hệ thống nhận sự kiện đơn "Giao thành công".
2. Hệ thống tạo hóa đơn cho đơn gồm mã hóa đơn, mã đơn, thời điểm xuất và snapshot tại thời điểm xuất: tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán.
3. Với đơn COD, hệ thống ghi nhận đơn "Đã thanh toán" khi giao thành công `[GD]` và lưu lịch sử thay đổi của đơn.
4. Hóa đơn ở chế độ chỉ đọc, không sửa và không xóa.

## Alternative Flows
- **1a. Đơn giao không thành công:** không xuất hóa đơn; tồn kho được cộng lại theo UC-35.

## Exceptions
- **E1. Đơn đã có hóa đơn:** sự kiện bị gửi lặp → hệ thống không tạo thêm hóa đơn (mỗi đơn đúng 1 hóa đơn).
- **E2. Lỗi khi tạo hóa đơn:** rollback, ghi log và thử lại; trạng thái "Giao thành công" của đơn không bị ảnh hưởng `[GD]`.

## Postconditions
- Đơn "Giao thành công" có đúng 1 hóa đơn chỉ đọc, lưu snapshot thông tin tại thời điểm xuất.
- Với đơn COD: trạng thái thanh toán "Đã thanh toán"; lịch sử thay đổi của đơn có thêm 1 dòng với nguồn là Hệ thống `[GD]`.

## Acceptance Criteria

### AC-1: Xuất hóa đơn khi giao thành công
Given: đơn DH0001 "Đang giao", tổng thanh toán 480.000đ
When: Trang giả lập vận chuyển cập nhật DH0001 sang "Giao thành công"
Then: hệ thống tạo 1 hóa đơn cho DH0001 với tổng 480.000đ
And: hóa đơn có đủ tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán

### AC-2: Không xuất hóa đơn khi giao không thành công
Given: đơn DH0002 "Đang giao"
When: trang giả lập cập nhật DH0002 sang "Giao không thành công"
Then: không có hóa đơn nào được tạo cho DH0002

### AC-3: Không tạo trùng
Given: đơn DH0001 đã có hóa đơn
When: sự kiện "Giao thành công" của DH0001 được gửi lại
Then: DH0001 vẫn chỉ có 1 hóa đơn

### AC-4: Hóa đơn không đổi khi dữ liệu gốc thay đổi
Given: hóa đơn của DH0001 ghi đơn giá "Đỏ / M" là 250.000đ và tên sản phẩm "Áo bơi A"
When: Nhân viên đổi giá size M thành 300.000đ và đổi tên sản phẩm thành "Áo bơi A mới"
Then: hóa đơn của DH0001 vẫn ghi 250.000đ và "Áo bơi A"

### AC-5: Đơn COD được ghi nhận đã thanh toán
Given: đơn COD DH0003 "Đang giao"
When: trang giả lập cập nhật DH0003 sang "Giao thành công"
Then: DH0003 được ghi nhận "Đã thanh toán" và có hóa đơn

## Dependencies
- **Upstream UC:** UC-36 Cập nhật trạng thái giao hàng
- **Downstream UC:** UC-27 Xem hóa đơn, UC-37 Xem dashboard
- **External Systems:** Không có

## Notes
- BR-TUAN1: hóa đơn tự xuất khi giao thành công; khách và nhân viên chỉ xem (cần chốt).
- Không phải hóa đơn điện tử VAT (Out of Scope).
- Tiền tính bằng số nguyên VND.

### Quyết định đã chốt
- Hóa đơn lưu snapshot tại thời điểm xuất gồm: tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán (theo ERD).
- Mỗi đơn có tối đa 1 hóa đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Đơn COD được ghi nhận "Đã thanh toán" khi giao thành công; thay đổi này cũng được ghi vào lịch sử của đơn.
- Lỗi tạo hóa đơn không làm thay đổi trạng thái giao của đơn; hệ thống thử lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt snapshot hóa đơn và mỗi đơn tối đa 1 hóa đơn (theo ERD); lưu lịch sử khi COD chuyển "Đã thanh toán"
