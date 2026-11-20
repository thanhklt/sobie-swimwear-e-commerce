# UC-27: Xem hóa đơn

## Metadata
- **ID:** UC-27
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách hàng, Nhân viên

## Trigger
- Khách hàng bấm "Xem hóa đơn" trong chi tiết đơn đã giao thành công.
- Nhân viên mở trang danh sách hóa đơn hoặc bấm "Xem hóa đơn" trong chi tiết đơn.

## Preconditions
- Người xem đã đăng nhập.
- Đơn đã có hóa đơn (UC-26).

## Main Flow
1. Người xem mở hóa đơn.
2. Hệ thống kiểm tra quyền xem: Khách hàng chỉ xem hóa đơn của đơn mình; Nhân viên xem mọi hóa đơn.
3. Hệ thống hiển thị hóa đơn: mã hóa đơn, mã đơn, thời điểm xuất (giờ Asia/Ho_Chi_Minh), thông tin khách và nhận hàng, các dòng hàng, tạm tính, mức giảm, phí vận chuyển, tổng thanh toán, phương thức thanh toán.
4. Hóa đơn chỉ đọc; không có thao tác sửa hoặc xóa.

## Alternative Flows
- **1a. Nhân viên xem danh sách hóa đơn:** hệ thống hiển thị danh sách hóa đơn, mới nhất trước, có phân trang, tìm theo mã đơn hoặc mã hóa đơn `[GD]`; Nhân viên chọn một hóa đơn để xem.

## Exceptions
- **E1. Khách xem hóa đơn của người khác:** hệ thống từ chối, báo không tìm thấy hóa đơn.
- **E2. Đơn chưa có hóa đơn:** hệ thống báo "Đơn chưa có hóa đơn"; nút "Xem hóa đơn" không hiển thị cho đơn chưa giao thành công.

## Postconditions
- Không thay đổi dữ liệu.

## Acceptance Criteria

### AC-1: Khách xem hóa đơn của mình
Given: đơn 7K3M9Q2X của khách A đã giao thành công và có hóa đơn
When: khách A bấm "Xem hóa đơn"
Then: hệ thống hiển thị hóa đơn với đủ thông tin như bước 3

### AC-2: Khách không xem được hóa đơn của người khác
Given: hóa đơn của đơn 4HZP8W1N thuộc khách B
When: khách A mở hóa đơn đó
Then: hệ thống báo không tìm thấy hóa đơn

### AC-3: Nhân viên xem mọi hóa đơn
Given: có hóa đơn của khách A và khách B
When: Nhân viên mở danh sách hóa đơn
Then: thấy hóa đơn của cả hai khách

### AC-4: Không có thao tác sửa
Given: người xem đang mở hóa đơn
When: người xem gửi yêu cầu sửa hoặc xóa hóa đơn
Then: hệ thống từ chối; hóa đơn không đổi

### AC-5: Đơn chưa giao thành công
Given: đơn B6TQ2R5D đang "Đang giao"
When: khách mở chi tiết B6TQ2R5D
Then: không có nút "Xem hóa đơn"

## Dependencies
- **Upstream UC:** UC-26 Tự xuất hóa đơn, UC-21 Theo dõi đơn hàng
- **Downstream UC:** Không có
- **External Systems:** Không có

## Notes
- BR-GIAIDOAN1: khách và nhân viên chỉ xem hóa đơn (đã chốt 20/11/2026).
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách hóa đơn của Nhân viên.

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026). Admin không xem hóa đơn.

### Giả định [GD]
- Nhân viên có trang danh sách hóa đơn, mới nhất trước, phân trang, tìm theo mã đơn hoặc mã hóa đơn.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt Admin không xem hóa đơn
- v3 (2026-11-20): đồng bộ BR-GIAIDOAN1 — chốt khách và Nhân viên chỉ xem hóa đơn; mã đơn ví dụ theo định dạng Crockford Base32
