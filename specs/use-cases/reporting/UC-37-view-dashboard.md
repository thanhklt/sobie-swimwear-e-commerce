# UC-37: Xem dashboard

## Metadata
- **ID:** UC-37
- **Module:** reporting
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
   6. **Tiền nhập hàng theo nhà cung cấp:** tổng tiền các phiếu nhập có ngày tạo (`goods_receipt_created_date`) thuộc kỳ báo cáo theo múi giờ `Asia/Ho_Chi_Minh` và ở trạng thái "Đã xác nhận" tại thời điểm xem, nhóm theo nhà cung cấp. Xác nhận muộn có thể làm tăng số liệu kỳ cũ.
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
Given: nhà cung cấp X có 3 phiếu được tạo trong kỳ; tại thời điểm xem có 2 phiếu "Đã xác nhận" tổng 5.000.000đ và 1 phiếu "Nháp" 1.000.000đ
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

### AC-9: Xác nhận muộn làm tăng tiền nhập của kỳ tạo phiếu
Given: nhà cung cấp X chỉ có phiếu P tổng 1.000.000đ, tạo ngày 30/11/2026 theo múi giờ `Asia/Ho_Chi_Minh`; P còn "Nháp" nên tiền nhập tháng 11 của X đang là 0đ
When: Nhân viên xác nhận P ngày 01/12/2026 rồi xem lại dashboard tháng 11 và tháng 12
Then: tiền nhập tháng 11 của X = 1.000.000đ
And: tiền nhập tháng 12 của X = 0đ

## Dependencies
- **Upstream UC:** UC-19, UC-20, UC-23, UC-26, UC-31, UC-32, UC-34, UC-35, UC-36
- **Downstream UC:** không có
- **External Systems:** không có

## Notes
- Lợi nhuận gộp = Doanh thu − Giá vốn hàng bán (SL bán × giá vốn); giá vốn theo bình quân gia quyền, tính riêng từng biến thể (BR-GIAIDOAN1, Constraints của BR-007).
- Cách lấy giá vốn tại thời điểm bán: BR ghi "chưa cần quan tâm", UC không đặc tả thêm.
- Tiền tính bằng số nguyên VND; thời gian lưu UTC, hiển thị `Asia/Ho_Chi_Minh` (AGENTS.md).
- Theo constraint cache (BR-GIAIDOAN1, Constraints chung — Cache): dashboard không cache — truy vấn trực tiếp Database và trả `Cache-Control: no-store` như mọi trang của portal quản trị (đã chốt 21/11/2026).
- "Sản phẩm bán chạy" ở đây khác khối bán chạy trên trang chủ (UC-09): dashboard tính theo kỳ báo cáo, chỉ đơn "Giao thành công", top 10.

**Quyết định đã chốt**
- Chỉ Nhân viên xem dashboard; Khách hàng và Admin không xem được (đã chốt 15/11/2026).
- Không làm chỉ số "Hiệu quả khuyến mãi"; chuyển sang Out of Scope (đã chốt 15/11/2026).
- Tiền nhập hàng theo nhà cung cấp lọc theo ngày tạo phiếu, chỉ tính phiếu đã xác nhận tại thời điểm xem; số liệu kỳ cũ có thể tăng khi xác nhận muộn. Không bổ sung thời điểm xác nhận phiếu nhập (đã chốt 22/11/2026, UC-34).

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
- v5 (2026-11-21): chốt dashboard không cache phía server; phân biệt với khối bán chạy trang chủ
- v6 (2026-11-21): theo BR-GIAIDOAN1 v22 — trang dashboard trả `no-store` thay cho `private, no-cache` + `ETag`
- v7 (2026-11-22): chốt kỳ tiền nhập hàng theo ngày tạo phiếu và trạng thái đã xác nhận tại thời điểm xem; thêm AC-9 cho xác nhận khác kỳ tạo
