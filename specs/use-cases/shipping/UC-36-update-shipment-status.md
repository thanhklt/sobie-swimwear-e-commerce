# UC-36: Cập nhật trạng thái giao hàng (trang giả lập)

## Metadata
- **ID:** UC-36
- **Module:** shipping
- **Liên quan tới BR:** BR-006
- **Status:** draft

## Actor
Người demo thao tác trên website giả lập vận chuyển riêng, không cần đăng nhập

## Trigger
Người demo mở website giả lập vận chuyển riêng để xem các đơn đang giao và cập nhật trạng thái giao hàng.

## Preconditions
- Đơn đã được Nhân viên bàn giao cho vận chuyển (UC-40), ở trạng thái "Chờ lấy hàng" hoặc "Đang giao".

## Main Flow
1. Người demo mở trang giả lập vận chuyển; trang không yêu cầu đăng nhập.
2. Trang hiển thị danh sách đơn "Chờ lấy hàng" và "Đang giao": mã đơn và trạng thái hiện tại. Không hiển thị thông tin cá nhân hoặc số tiền của khách trên website giả lập công khai. Nút theo trạng thái:
   - Đơn "Chờ lấy hàng": nút "Đã nhận hàng" (đơn vị vận chuyển đã lấy được hàng từ cửa hàng).
   - Đơn "Đang giao": nút "Đã giao" và "Giao không thành công".
3. Người demo bấm một nút cho một đơn.
4. Hệ thống kiểm tra đơn vẫn ở trạng thái tương ứng với nút, cập nhật đơn trên website sang trạng thái mới và lưu lịch sử trạng thái đơn.
5. Trang cập nhật lại danh sách; khách thấy trạng thái mới khi theo dõi đơn (UC-21).

## Alternative Flows
- **3a. Đã nhận hàng:** đơn "Chờ lấy hàng" chuyển "Đang giao"; đơn vẫn trên trang, giờ có nút "Đã giao" / "Giao không thành công". Từ lúc này Nhân viên không hủy được đơn (UC-22).
- **3b. Đã giao:** đơn "Đang giao" chuyển "Giao thành công"; hệ thống tự xuất hóa đơn (UC-26); đơn biến mất khỏi trang.
- **3c. Giao không thành công:** đơn "Đang giao" chuyển "Giao không thành công"; hệ thống tự cộng lại hàng vào tồn kho (UC-35); đơn biến mất khỏi trang.

## Exceptions
- **E1. Đơn không còn ở trạng thái tương ứng với nút:** đơn đã được cập nhật trước đó (ví dụ bấm hai lần hoặc hai tab), hoặc Nhân viên vừa hủy đơn "Chờ lấy hàng" — hệ thống từ chối, đơn giữ trạng thái hiện tại.
- **E2. Đơn không tồn tại:** hệ thống báo không tìm thấy đơn.

## Postconditions
- Đơn ở trạng thái "Đang giao", "Giao thành công" hoặc "Giao không thành công", khớp với thao tác trên trang giả lập.
- Lịch sử trạng thái đơn có thêm 1 dòng: trạng thái cũ, trạng thái mới, nguồn thay đổi là Trang giả lập vận chuyển, thời điểm.

## Acceptance Criteria

### AC-1: Trang không cần đăng nhập
Given: người demo chưa đăng nhập
When: người demo mở trang giả lập vận chuyển
Then: trang hiển thị danh sách đơn, không chuyển tới trang đăng nhập

### AC-2: Chỉ hiển thị đơn đã bàn giao, nút theo trạng thái
Given: đơn 7K3M9Q2X ở "Chờ lấy hàng", đơn 4HZP8W1N ở "Đang giao", đơn B6TQ2R5D ở "Đã xác nhận"
When: người demo mở trang giả lập vận chuyển
Then: danh sách có 7K3M9Q2X với trạng thái "Chờ lấy hàng" và nút "Đã nhận hàng", 4HZP8W1N với trạng thái "Đang giao" và nút "Đã giao" / "Giao không thành công"
And: B6TQ2R5D không có trong danh sách
And: trang không hiển thị tên, số điện thoại, địa chỉ hoặc số tiền của khách

### AC-3: Đã nhận hàng
Given: đơn 7K3M9Q2X ở "Chờ lấy hàng"
When: người demo bấm "Đã nhận hàng" cho 7K3M9Q2X
Then: đơn 7K3M9Q2X chuyển sang "Đang giao"
And: 7K3M9Q2X vẫn trên trang với nút "Đã giao" và "Giao không thành công"
And: lịch sử trạng thái đơn ghi "Chờ lấy hàng → Đang giao", nguồn là Trang giả lập vận chuyển

### AC-4: Đã giao
Given: đơn 7K3M9Q2X ở trạng thái "Đang giao"
When: người demo bấm "Đã giao" cho 7K3M9Q2X
Then: đơn 7K3M9Q2X chuyển sang "Giao thành công"
And: hệ thống tự xuất hóa đơn cho 7K3M9Q2X (UC-26)
And: 7K3M9Q2X không còn trong danh sách của trang giả lập

### AC-5: Giao không thành công
Given: đơn 7K3M9Q2X ở trạng thái "Đang giao", gồm 2 sản phẩm biến thể "Đỏ-M"
When: người demo bấm "Giao không thành công"
Then: đơn 7K3M9Q2X chuyển sang "Giao không thành công"
And: tồn kho biến thể "Đỏ-M" được cộng lại 2 (UC-35)

### AC-6: Bấm lại cho đơn đã cập nhật
Given: đơn 7K3M9Q2X đã chuyển sang "Giao thành công"
When: trang giả lập gửi cập nhật "Giao không thành công" cho 7K3M9Q2X
Then: hệ thống từ chối
And: đơn giữ trạng thái "Giao thành công"

### AC-7: Không giao khi chưa nhận hàng
Given: đơn 7K3M9Q2X ở "Chờ lấy hàng"
When: trang giả lập gửi cập nhật "Đã giao" cho 7K3M9Q2X
Then: hệ thống từ chối, đơn vẫn "Chờ lấy hàng"

### AC-8: Đơn đã bị Nhân viên hủy
Given: đơn 7K3M9Q2X ở "Chờ lấy hàng" đang hiện trên trang giả lập
When: Nhân viên hủy 7K3M9Q2X (UC-22), sau đó người demo bấm "Đã nhận hàng"
Then: hệ thống từ chối, đơn vẫn "Đã hủy"

## Dependencies
- **Upstream UC:** UC-40 Bàn giao đơn cho vận chuyển
- **Downstream UC:** UC-21 Theo dõi đơn hàng, UC-26 Tự xuất hóa đơn, UC-35 Tự cộng lại tồn kho khi giao không thành công, UC-22 Hủy đơn hàng
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách đơn trên trang giả lập.
- Không kết nối đơn vị vận chuyển thật (Out of Scope).
- Website giả lập vận chuyển là trang riêng, chỉ hiển thị mã đơn và trạng thái để tránh đưa thông tin cá nhân lên trang công khai.

### Quyết định đã chốt
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026).
- Trang giả lập vận chuyển không cần đăng nhập, là 1 trang duy nhất (đã chốt 15/11/2026).
- Trang có 3 nút theo trạng thái: "Đã nhận hàng" cho đơn "Chờ lấy hàng" (→ Đang giao); "Đã giao" (→ Giao thành công) và "Giao không thành công" cho đơn "Đang giao" (đã chốt 20/11/2026).
- Trang giả lập không đưa đơn lên trang; việc đó do Nhân viên bàn giao ở UC-40 (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).

### Quy tắc hiển thị đã chốt
- Danh sách trên website giả lập gồm mã đơn và trạng thái; không hiển thị thông tin cá nhân hay số tiền của khách.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bộ trạng thái đơn
- v3 (2026-11-15): chốt trang giả lập không cần đăng nhập, chỉ hiển thị đơn "Đang giao" với 2 nút Đã giao / Giao không thành công; nhận đơn từ UC-40; thêm lưu lịch sử trạng thái đơn (theo ERD)
- v4 (2026-11-20): thêm trạng thái "Chờ lấy hàng" và nút "Đã nhận hàng"; thêm AC-3, AC-7, AC-8
- v5 (2026-11-23): xác định đây là website riêng; chỉ hiển thị mã đơn và trạng thái, không công khai thông tin cá nhân hoặc tiền COD
