# UC-37: Xem dashboard

## Metadata
- **ID:** UC-37
- **Bounded Context:** reporting-context
- **Liên quan tới BR:** BR-007
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở trang dashboard trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên mở dashboard; kỳ báo cáo mặc định là tháng hiện tại `[GD]`.
2. Nhân viên có thể chọn khoảng thời gian (từ ngày – đến ngày) `[GD]`.
3. Hệ thống tính và hiển thị các chỉ số trong kỳ:
   1. **Doanh thu:** tổng tiền hàng sau giảm của các đơn "Giao thành công" trong kỳ, không gồm phí vận chuyển `[GD]`.
   2. **Lợi nhuận gộp:** doanh thu − giá vốn hàng bán (tổng số lượng bán × giá vốn) của cùng các đơn đó.
   3. **Số đơn theo trạng thái:** số đơn tạo trong kỳ theo từng trạng thái (Chưa xử lý, Đã xác nhận, Chờ lấy hàng, Đang giao, Giao thành công, Giao không thành công, Đã hủy).
   4. **Sản phẩm bán chạy:** top 10 sản phẩm theo số lượng bán của các đơn "Giao thành công" trong kỳ `[GD]`.
   5. **Tồn kho thấp:** các biến thể có tồn kho ≤ ngưỡng tồn kho thấp (hard-code) tại thời điểm xem `[GD]`.
   6. **Tiền nhập hàng theo nhà cung cấp:** tổng tiền các phiếu nhập "Đã xác nhận" trong kỳ, nhóm theo nhà cung cấp.
4. Thời gian hiển thị theo múi giờ `Asia/Ho_Chi_Minh`.

## Alternative Flows
- **3a. Kỳ không có dữ liệu:** các chỉ số tiền và số lượng hiển thị 0, danh sách hiển thị trống.

## Exceptions
- **E1. Khoảng thời gian không hợp lệ:** ngày bắt đầu sau ngày kết thúc → hệ thống báo lỗi, giữ kết quả kỳ trước.
- **E2. Vai trò không được phép:** Khách hàng hoặc Admin truy cập dashboard → hệ thống từ chối.

## Postconditions
- Không thay đổi dữ liệu; chỉ hiển thị chỉ số.

## Acceptance Criteria

### AC-1: Doanh thu và lợi nhuận gộp
Given: trong kỳ có 1 đơn "Giao thành công" gồm 2 cái "Áo bơi A – Đỏ – M", tiền hàng sau giảm 400.000đ, giá vốn 120.000đ/cái; và 1 đơn "Đã hủy" 300.000đ
When: Nhân viên xem dashboard của kỳ đó
Then: doanh thu = 400.000đ
And: lợi nhuận gộp = 400.000 − 2 × 120.000 = 160.000đ

### AC-2: Số đơn theo trạng thái
Given: trong kỳ có 3 đơn "Chưa xử lý", 2 đơn "Giao thành công", 1 đơn "Đã hủy"
When: Nhân viên xem dashboard
Then: số đơn hiển thị đúng 3, 2, 1 cho từng trạng thái, các trạng thái khác là 0

### AC-3: Sản phẩm bán chạy
Given: các đơn "Giao thành công" trong kỳ bán 5 sản phẩm A, 8 sản phẩm B, 2 sản phẩm C
When: Nhân viên xem dashboard
Then: danh sách bán chạy theo thứ tự B, A, C kèm số lượng

### AC-4: Tồn kho thấp
Given: ngưỡng tồn kho thấp là 5; biến thể X tồn 3, biến thể Y tồn 5, biến thể Z tồn 6
When: Nhân viên xem dashboard
Then: danh sách tồn kho thấp gồm X và Y, không có Z

### AC-5: Tiền nhập hàng theo nhà cung cấp
Given: trong kỳ nhà cung cấp X có 2 phiếu "Đã xác nhận" tổng 5.000.000đ và 1 phiếu "Nháp" 1.000.000đ
When: Nhân viên xem dashboard
Then: tiền nhập của X = 5.000.000đ

### AC-6: Kỳ không có dữ liệu
Given: kỳ được chọn không có đơn và phiếu nhập nào
When: Nhân viên xem dashboard
Then: doanh thu, lợi nhuận gộp và tiền nhập hiển thị 0đ, các danh sách trống

### AC-7: Khoảng thời gian không hợp lệ
Given: Nhân viên ở dashboard
When: Nhân viên chọn ngày bắt đầu sau ngày kết thúc
Then: hệ thống báo lỗi khoảng thời gian

### AC-8: Vai trò không được phép
Given: người dùng đăng nhập với vai trò Khách hàng hoặc Admin
When: người dùng truy cập dashboard
Then: hệ thống từ chối truy cập

## Dependencies
- **Upstream UC:** UC-19, UC-20, UC-23, UC-26, UC-31, UC-32, UC-34, UC-35, UC-36
- **Downstream UC:** không có
- **External Systems:** không có

## Notes
- Lợi nhuận gộp = Doanh thu − Giá vốn hàng bán (SL bán × giá vốn); giá vốn theo bình quân gia quyền, tính riêng từng biến thể (BR-GIAIDOAN1, Constraints của BR-007).
- Cách lấy giá vốn tại thời điểm bán: BR ghi "chưa cần quan tâm", UC không đặc tả thêm.
- Tiền tính bằng số nguyên VND; thời gian lưu UTC, hiển thị `Asia/Ho_Chi_Minh` (AGENTS.md).
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho các danh sách trên dashboard.

**Quyết định đã chốt**
- Chỉ Nhân viên xem dashboard; Khách hàng và Admin không xem được (đã chốt 15/11/2026).
- Không làm chỉ số "Hiệu quả khuyến mãi"; chuyển sang Out of Scope (đã chốt 15/11/2026).

**Giả định [GD]**
- Kỳ báo cáo mặc định là tháng hiện tại, chọn được khoảng thời gian.
- Doanh thu tính trên đơn "Giao thành công", tiền hàng sau giảm, không gồm phí vận chuyển.
- Sản phẩm bán chạy: top 10 theo số lượng bán từ đơn "Giao thành công".
- Tồn kho thấp: tồn kho ≤ ngưỡng.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt chỉ Nhân viên xem dashboard
- v3 (2026-11-15): bỏ chỉ số "Hiệu quả khuyến mãi" (chuyển Out of Scope)
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — số đơn theo trạng thái: thêm "Chờ lấy hàng", bỏ "Bị từ chối"
