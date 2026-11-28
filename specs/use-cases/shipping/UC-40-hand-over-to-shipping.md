# UC-40: Bàn giao đơn cho vận chuyển

## Metadata
- **ID:** UC-40
- **Module:** shipping
- **Liên quan tới BR:** BR-006
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên chọn một đơn "Đã xác nhận" trong trang quản lý đơn hàng và bấm "Bàn giao vận chuyển".

## Preconditions
- Nhân viên đã đăng nhập.
- Đơn ở trạng thái "Đã xác nhận" (UC-23).

## Main Flow
1. Nhân viên mở trang quản lý đơn hàng và lọc các đơn "Đã xác nhận".
2. Nhân viên chọn một đơn và bấm "Bàn giao vận chuyển".
3. Hệ thống kiểm tra đơn vẫn ở "Đã xác nhận".
4. Hệ thống chuyển đơn sang "Chờ lấy hàng" và lưu lịch sử trạng thái đơn.
5. Đơn xuất hiện trên Trang giả lập vận chuyển (UC-36) với nút "Đã nhận hàng"; khách thấy trạng thái "Chờ lấy hàng" khi theo dõi đơn (UC-21).
6. Khi đơn vị vận chuyển bấm "Đã nhận hàng" trên trang giả lập, đơn chuyển sang "Đang giao" (UC-36).

## Exceptions
- **E1. Đơn không ở "Đã xác nhận":** đơn đang "Chưa xử lý", đã "Chờ lấy hàng", "Đang giao" hoặc đã ở trạng thái kết thúc — hệ thống từ chối, báo trạng thái hiện tại, đơn không đổi.
- **E2. Đơn không tồn tại:** hệ thống báo không tìm thấy đơn.

## Postconditions
- Đơn ở trạng thái "Chờ lấy hàng" và có trong danh sách của Trang giả lập vận chuyển.
- Lịch sử trạng thái đơn có thêm 1 dòng: "Đã xác nhận → Chờ lấy hàng", nguồn thay đổi, Nhân viên thực hiện, thời điểm.

## Acceptance Criteria

### AC-1: Bàn giao đơn thành công
Given: đơn 7K3M9Q2X ở trạng thái "Đã xác nhận"
When: Nhân viên bấm "Bàn giao vận chuyển" cho 7K3M9Q2X
Then: đơn 7K3M9Q2X chuyển sang "Chờ lấy hàng"
And: 7K3M9Q2X xuất hiện trên Trang giả lập vận chuyển
And: lịch sử trạng thái đơn ghi "Đã xác nhận → Chờ lấy hàng" kèm Nhân viên thực hiện

### AC-2: Đơn chưa xác nhận
Given: đơn 4HZP8W1N ở trạng thái "Chưa xử lý"
When: Nhân viên bấm "Bàn giao vận chuyển" cho 4HZP8W1N
Then: hệ thống từ chối và báo đơn đang "Chưa xử lý"
And: 4HZP8W1N không xuất hiện trên Trang giả lập vận chuyển

### AC-3: Đơn đã bàn giao
Given: đơn 7K3M9Q2X đã ở trạng thái "Chờ lấy hàng"
When: Nhân viên bấm "Bàn giao vận chuyển" cho 7K3M9Q2X lần nữa (ví dụ từ tab cũ)
Then: hệ thống từ chối và báo đơn đang "Chờ lấy hàng"
And: đơn giữ trạng thái "Chờ lấy hàng"

### AC-4: Khách thấy trạng thái mới
Given: đơn 7K3M9Q2X của khách A ở "Đã xác nhận"
When: Nhân viên bàn giao 7K3M9Q2X
Then: khách A mở chi tiết đơn thấy trạng thái "Chờ lấy hàng"

## Dependencies
- **Upstream UC:** UC-23 Xác nhận đơn hàng
- **Downstream UC:** UC-36 Cập nhật trạng thái giao hàng, UC-21 Theo dõi đơn hàng, UC-22 Hủy đơn hàng (Nhân viên còn hủy được đơn "Chờ lấy hàng")
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Trang giả lập vận chuyển (UC-36) chỉ hiển thị mã đơn và trạng thái; không hiển thị thông tin người gửi, người nhận, địa chỉ hay tiền COD.

### Quyết định đã chốt
- Nhân viên bấm "Bàn giao vận chuyển" cho đơn "Đã xác nhận" thì đơn sang "Chờ lấy hàng" và xuất hiện trên Trang giả lập vận chuyển (đã chốt 15/11/2026; đổi đích từ "Đang giao" sang "Chờ lấy hàng" ngày 20/11/2026).
- Mỗi lần bàn giao đúng một đơn; không bàn giao nhiều đơn trong một thao tác (đã chốt 23/11/2026).
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; Đã hủy (đã chốt 15/11/2026, cập nhật 20/11/2026).
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- E1 báo đúng trạng thái thực tế của đơn; E2 báo không tìm thấy đơn — hai thông báo phải khác nhau (đã chốt 24/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-20): bàn giao chuyển đơn sang "Chờ lấy hàng" (không còn sang thẳng "Đang giao"); đơn vị vận chuyển bấm "Đã nhận hàng" mới sang "Đang giao" (UC-36)
- v3 (2026-11-23): mỗi lần chỉ bàn giao một đơn; bỏ luồng và AC bàn giao nhiều đơn chưa được xác nhận
- v4 (2026-11-24): đồng bộ Notes với UC-36 — trang giả lập chỉ mã đơn và trạng thái; ghi rõ mỗi lần bàn giao một đơn; chốt E1/E2 trả lỗi khác nhau
