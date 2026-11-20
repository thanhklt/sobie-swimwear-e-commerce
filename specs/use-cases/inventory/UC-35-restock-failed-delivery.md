# UC-35: Tự cộng lại tồn kho khi giao không thành công

## Metadata
- **ID:** UC-35
- **Module:** inventory
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Hệ thống

## Trigger
Đơn hàng chuyển sang trạng thái "Giao không thành công" do Trang giả lập vận chuyển cập nhật (UC-36).

## Preconditions
- Đơn đang ở trạng thái "Đang giao" và được chuyển sang "Giao không thành công" (UC-36).

## Main Flow
1. Hệ thống nhận yêu cầu chuyển đơn từ "Đang giao" sang "Giao không thành công".
2. Trong cùng transaction với việc cập nhật trạng thái đơn `[GD]`, với mỗi dòng của đơn, hệ thống cộng số lượng vào tồn kho của biến thể tương ứng.
3. Hệ thống giữ nguyên giá vốn của các biến thể.

## Alternative Flows
- **2a. Biến thể hoặc sản phẩm đã ngừng bán:** vẫn cộng lại tồn kho bình thường `[GD]`.

## Exceptions
- **E1. Yêu cầu đến lần thứ hai cho cùng đơn:** đơn không còn ở "Đang giao" (đã là "Giao không thành công") → hệ thống từ chối chuyển trạng thái, không cộng thêm tồn kho.
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
Given: đơn D đã chuyển sang "Giao không thành công" và đã được cộng lại tồn kho
When: yêu cầu chuyển đơn D sang "Giao không thành công" đến lần nữa
Then: hệ thống từ chối vì đơn D không còn ở "Đang giao"
And: tồn kho không đổi

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

**Quyết định đã chốt**
- Không có cột đánh dấu đơn đã cộng lại tồn kho (theo data model v1, ưu tiên ERD). Chống cộng hai lần bằng trạng thái đơn: chỉ chuyển "Đang giao → Giao không thành công" được một lần; lần gửi thứ hai bị từ chối vì đơn không còn "Đang giao" (đã chốt 15/11/2026).

**Giả định [GD]**
- Cộng tồn chạy trong cùng transaction với cập nhật trạng thái đơn.
- Biến thể hoặc sản phẩm đã ngừng bán vẫn được cộng lại tồn kho.
- Khi lỗi, Trang giả lập vận chuyển nhận lỗi và có thể gửi lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo data model v1 — bỏ đánh dấu đơn đã cộng tồn, chống cộng hai lần bằng trạng thái đơn
