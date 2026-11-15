# UC-36: Cập nhật trạng thái giao hàng (trang giả lập)

## Metadata
- **ID:** UC-36
- **Bounded Context:** shipping-context
- **Liên quan tới BR:** BR-006
- **Status:** draft

## Actor
Trang giả lập vận chuyển (người demo thao tác trên trang này, không cần đăng nhập)

## Trigger
Người demo mở trang giả lập vận chuyển và bấm "Đã giao" hoặc "Giao không thành công" cho một đơn.

## Preconditions
- Đơn đã được Nhân viên bàn giao cho vận chuyển (UC-40), ở trạng thái "Đang giao".

## Main Flow
1. Người demo mở trang giả lập vận chuyển; trang không yêu cầu đăng nhập.
2. Trang hiển thị danh sách các đơn đang vận chuyển (trạng thái "Đang giao") `[GD]`: mã đơn, người nhận, số điện thoại, địa chỉ nhận hàng, thông tin người gửi (từ cấu hình hard-code), số tiền cần thu khi giao với đơn COD `[GD]`. Mỗi đơn có 2 nút "Đã giao" và "Giao không thành công".
3. Người demo bấm "Đã giao" hoặc "Giao không thành công" cho một đơn.
4. Hệ thống kiểm tra đơn vẫn ở "Đang giao", cập nhật đơn trên website sang trạng thái tương ứng và lưu lịch sử trạng thái đơn.
5. Đơn biến mất khỏi danh sách trên trang giả lập; khách thấy trạng thái mới khi theo dõi đơn (UC-21).

## Alternative Flows
- **3a. Đã giao:** đơn chuyển "Giao thành công"; hệ thống tự xuất hóa đơn (UC-26).
- **3b. Giao không thành công:** đơn chuyển "Giao không thành công"; hệ thống tự cộng lại hàng vào tồn kho (UC-35).

## Exceptions
- **E1. Đơn không còn "Đang giao":** đơn đã được cập nhật trước đó (ví dụ bấm hai lần hoặc hai tab) — hệ thống từ chối, đơn giữ trạng thái hiện tại.
- **E2. Đơn không tồn tại:** hệ thống báo không tìm thấy đơn.

## Postconditions
- Đơn ở trạng thái "Giao thành công" hoặc "Giao không thành công", khớp với thao tác trên trang giả lập.
- Lịch sử trạng thái đơn có thêm 1 dòng: trạng thái cũ, trạng thái mới, nguồn thay đổi là Trang giả lập vận chuyển, thời điểm.

## Acceptance Criteria

### AC-1: Trang không cần đăng nhập
Given: người demo chưa đăng nhập
When: người demo mở trang giả lập vận chuyển
Then: trang hiển thị danh sách đơn đang vận chuyển, không chuyển tới trang đăng nhập

### AC-2: Chỉ hiển thị đơn đang giao
Given: đơn DH001 ở "Đang giao", đơn DH002 ở "Đã xác nhận", đơn DH003 ở "Chưa xử lý"
When: người demo mở trang giả lập vận chuyển
Then: danh sách chỉ có DH001
And: thông tin người gửi lấy từ cấu hình hard-code của cửa hàng

### AC-3: Đã giao
Given: đơn DH001 ở trạng thái "Đang giao"
When: người demo bấm "Đã giao" cho DH001
Then: đơn DH001 chuyển sang "Giao thành công"
And: hệ thống tự xuất hóa đơn cho DH001 (UC-26)
And: DH001 không còn trong danh sách của trang giả lập

### AC-4: Giao không thành công
Given: đơn DH001 ở trạng thái "Đang giao", gồm 2 sản phẩm biến thể "Đỏ-M"
When: người demo bấm "Giao không thành công"
Then: đơn DH001 chuyển sang "Giao không thành công"
And: tồn kho biến thể "Đỏ-M" được cộng lại 2 (UC-35)

### AC-5: Bấm lại cho đơn đã cập nhật
Given: đơn DH001 đã chuyển sang "Giao thành công"
When: trang giả lập gửi cập nhật "Giao không thành công" cho DH001
Then: hệ thống từ chối
And: đơn giữ trạng thái "Giao thành công"

### AC-6: Lưu lịch sử trạng thái
Given: đơn DH001 ở trạng thái "Đang giao"
When: người demo bấm "Đã giao"
Then: lịch sử trạng thái đơn ghi "Đang giao → Giao thành công", nguồn là Trang giả lập vận chuyển

## Dependencies
- **Upstream UC:** UC-40 Bàn giao đơn cho vận chuyển
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-26 Tự xuất hóa đơn, UC-35 Tự cộng lại tồn kho khi giao không thành công
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung) cho danh sách đơn trên trang giả lập.
- Không kết nối đơn vị vận chuyển thật (Out of Scope).
- Thông tin người gửi lấy từ cấu hình hard-code.

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; Đã hủy; Bị từ chối (đã chốt 15/11/2026).
- Trang giả lập vận chuyển không cần đăng nhập; là 1 trang duy nhất hiển thị danh sách đơn đang vận chuyển ("Đang giao"); mỗi đơn có 2 nút "Đã giao" (→ Giao thành công) và "Giao không thành công" (đã chốt 15/11/2026).
- Trang giả lập không chuyển đơn sang "Đang giao"; việc đó do Nhân viên bàn giao ở UC-40 (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Giả định [GD]
- Danh sách trên trang giả lập gồm: mã đơn, người nhận, số điện thoại, địa chỉ, người gửi, số tiền thu khi giao với đơn COD.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): chốt trang giả lập không cần đăng nhập, chỉ hiển thị đơn "Đang giao" với 2 nút Đã giao / Giao không thành công; nhận đơn từ UC-40; thêm lưu lịch sử trạng thái đơn (theo ERD)
