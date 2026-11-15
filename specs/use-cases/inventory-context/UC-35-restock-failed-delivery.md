# UC-35: Tự cộng lại tồn kho khi giao không thành công

## Metadata
- **ID:** UC-35
- **Bounded Context:** inventory-context
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Hệ thống

## Trigger
Đơn hàng chuyển sang trạng thái "Giao không thành công" do Trang giả lập vận chuyển cập nhật (UC-36).

## Preconditions
- Đơn ở trạng thái "Giao không thành công".
- Số lượng của đơn chưa được cộng lại vào tồn kho `[GD]`.

## Main Flow
1. Hệ thống nhận sự kiện đơn chuyển sang "Giao không thành công".
2. Trong cùng transaction với việc cập nhật trạng thái đơn `[GD]`, với mỗi dòng của đơn, hệ thống cộng số lượng vào tồn kho của biến thể tương ứng.
3. Hệ thống giữ nguyên giá vốn của các biến thể.
4. Hệ thống đánh dấu đơn đã được cộng lại tồn kho `[GD]`.

## Alternative Flows
- **2a. Biến thể hoặc sản phẩm đã ngừng bán:** vẫn cộng lại tồn kho bình thường `[GD]`.

## Exceptions
- **E1. Sự kiện đến lần thứ hai cho cùng đơn:** đơn đã được đánh dấu cộng lại tồn kho → hệ thống bỏ qua, không cộng thêm.
- **E2. Lỗi khi cộng tồn:** hệ thống hủy transaction; trạng thái đơn và tồn kho không đổi, Trang giả lập vận chuyển nhận lỗi để gửi lại `[GD]`.

## Postconditions
- Tồn kho của từng biến thể trong đơn tăng đúng số lượng của đơn.
- Giá vốn không đổi; không tính giá trị hàng hoàn.

## Acceptance Criteria

### AC-1: Cộng lại tồn kho khi giao không thành công
Given: đơn D có dòng "Áo bơi A – Đỏ – M" số lượng 2, đang ở "Đang giao"; biến thể đang tồn 5, giá vốn 120.000đ
When: Trang giả lập vận chuyển cập nhật đơn D sang "Giao không thành công"
Then: tồn kho của biến thể = 7
And: giá vốn của biến thể vẫn = 120.000đ
And: không có thao tác nào của Nhân viên

### AC-2: Không cộng hai lần
Given: đơn D đã được cộng lại tồn kho
When: sự kiện "Giao không thành công" của đơn D đến lần nữa
Then: tồn kho không đổi

### AC-3: Đơn nhiều dòng
Given: đơn D có 2 dòng cho 2 biến thể khác nhau
When: đơn D chuyển sang "Giao không thành công"
Then: mỗi biến thể được cộng đúng số lượng của dòng tương ứng

### AC-4: Lỗi không làm lệch trạng thái
Given: việc cộng tồn của đơn D gặp lỗi
When: Trang giả lập vận chuyển cập nhật đơn D sang "Giao không thành công"
Then: đơn D vẫn ở trạng thái trước đó và tồn kho không đổi

## Dependencies
- **Upstream UC:** UC-36
- **Downstream UC:** UC-12, UC-18, UC-37
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Theo BR: đơn giao không thành công thì hệ thống tự cộng lại hàng vào tồn kho, không có thao tác nhận hàng hoàn; giá vốn không đổi; không tính giá trị hàng hoàn.
- Out of Scope: thao tác nhận hàng hoàn thủ công, tính giá trị hàng hoàn.

**Giả định [GD]**
- Cộng tồn chạy trong cùng transaction với cập nhật trạng thái đơn.
- Đơn được đánh dấu đã cộng lại tồn kho để không cộng hai lần.
- Biến thể hoặc sản phẩm đã ngừng bán vẫn được cộng lại tồn kho.
- Khi lỗi, Trang giả lập vận chuyển nhận lỗi và có thể gửi lại.

## History
- v1 (2026-11-15): initial
