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
1. Nhân viên mở dashboard; kỳ báo cáo mặc định là tháng hiện tại.
2. Nhân viên có thể chọn khoảng thời gian (từ ngày – đến ngày).
3. Hệ thống tính và hiển thị các chỉ số trong kỳ:
   1. **Doanh thu:** tổng tiền hàng sau giảm của các đơn có ngày chuyển sang "Giao thành công" nằm trong kỳ, không gồm phí vận chuyển.
   2. **Lợi nhuận gộp:** doanh thu − giá vốn hàng bán (tổng số lượng bán × giá vốn) của cùng các đơn đó.
   3. **Số đơn theo trạng thái:** số đơn tạo trong kỳ theo từng trạng thái (Chưa xử lý, Đã xác nhận, Chờ lấy hàng, Đang giao, Giao thành công, Giao không thành công, Đã hủy).
   4. **Sản phẩm bán chạy:** top 10 sản phẩm theo số lượng bán của cùng nhóm đơn dùng để tính doanh thu. Tính cả biến thể đã ngừng bán.
   5. **Tồn kho thấp:** các biến thể có tồn kho ≤ ngưỡng tồn kho thấp (hard-code) tại thời điểm xem.
   6. **Tiền nhập hàng theo nhà cung cấp:** tổng tiền các phiếu nhập có ngày tạo (`goods_receipt_created_date`) thuộc kỳ báo cáo theo múi giờ `Asia/Ho_Chi_Minh` và ở trạng thái "Đã xác nhận" tại thời điểm xem, nhóm theo nhà cung cấp. Xác nhận muộn có thể làm tăng số liệu kỳ cũ.
4. Ngày giao thành công dùng để xác định kỳ báo cáo và thời gian hiển thị đều theo múi giờ `Asia/Ho_Chi_Minh`.

## Alternative Flows
- **3a. Kỳ không có dữ liệu:** Nếu kỳ được chọn không có đơn nào được tạo, không có đơn nào giao thành công và không có phiếu nhập đủ điều kiện, doanh thu, lợi nhuận gộp và số đơn theo từng trạng thái đều bằng 0. Danh sách sản phẩm bán chạy và tiền nhập theo nhà cung cấp để trống. Danh sách tồn kho thấp vẫn hiển thị theo tồn kho tại thời điểm xem.

## Exceptions
- **E1. Khoảng thời gian không hợp lệ:** ngày bắt đầu sau ngày kết thúc hoặc hai ngày bằng nhau → hệ thống báo lỗi, giữ kết quả kỳ trước.
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

**Có dưới 10 sản phẩm bán chạy**

Given: các đơn "Giao thành công" trong kỳ bán 6 đơn vị A, 8 đơn vị B và 2 đơn vị C. Biến thể đã bán của B hiện ở trạng thái "Ngừng bán".
When: Nhân viên xem dashboard của kỳ đó
Then: danh sách hiển thị lần lượt B (8), A (6), C (2)

**Có hơn 10 sản phẩm bán chạy**

Given: các đơn "Giao thành công" trong kỳ bán 11 sản phẩm khác nhau từ A đến K, với số lượng lần lượt từ 1 đến 11 đơn vị
When: Nhân viên xem dashboard của kỳ đó
Then: danh sách hiển thị đúng 10 sản phẩm theo thứ tự K (11), J (10), I (9), H (8), G (7), F (6), E (5), D (4), C (3), B (2)

### AC-4: Tồn kho thấp
Given: ngưỡng tồn kho thấp là 5; biến thể X tồn 3, biến thể Y tồn 5, biến thể Z tồn 6
When: Nhân viên xem dashboard
Then: danh sách tồn kho thấp gồm X và Y, không có Z

### AC-5: Tiền nhập hàng theo nhà cung cấp
Given: nhà cung cấp X có 3 phiếu được tạo trong kỳ; tại thời điểm xem có 2 phiếu "Đã xác nhận" tổng 5.000.000đ và 1 phiếu "Nháp" 1.000.000đ
When: Nhân viên xem dashboard
Then: tiền nhập của X = 5.000.000đ

### AC-6: Kỳ không có dữ liệu
Given: Kỳ được chọn không có đơn nào được tạo, không có đơn nào giao thành công và không có phiếu nhập đủ điều kiện. Tại thời điểm xem, ngưỡng tồn kho thấp là 5, biến thể X còn 3 và biến thể Y còn 6.
When: Nhân viên xem dashboard của kỳ đó.
Then: Doanh thu, lợi nhuận gộp và số đơn theo từng trạng thái đều bằng 0. Danh sách sản phẩm bán chạy và tiền nhập theo nhà cung cấp để trống. Danh sách tồn kho thấp chỉ hiển thị biến thể X.

### AC-7: Khoảng thời gian không hợp lệ
Given: Nhân viên đang xem kết quả dashboard của một kỳ hợp lệ.
When: Nhân viên chọn ngày bắt đầu sau ngày kết thúc hoặc chọn hai ngày bằng nhau.
Then: Hệ thống báo lỗi ngày bắt đầu phải nhỏ hơn ngày kết thúc.
And: Dashboard vẫn hiển thị kết quả của kỳ hợp lệ trước đó.

### AC-8: Vai trò không được phép
Given: người dùng đăng nhập với vai trò Khách hàng hoặc Admin
When: người dùng truy cập dashboard
Then: hệ thống từ chối truy cập

### AC-9: Ghi nhận theo ngày giao thành công
Given: đơn duy nhất đặt ngày 30/11 và chuyển sang "Giao thành công" ngày 01/12. Đơn có 2 đơn vị sản phẩm A, tiền hàng sau giảm là 400.000đ và giá vốn đã lưu là 120.000đ/đơn vị.
When: Nhân viên xem lần lượt báo cáo tháng 11 và tháng 12.
Then: tháng 11 có doanh thu và lợi nhuận gộp bằng 0, danh sách sản phẩm bán chạy trống.
And: tháng 12 có doanh thu 400.000đ, lợi nhuận gộp 160.000đ và danh sách sản phẩm bán chạy hiển thị A (2).

### AC-10: Xác nhận muộn làm tăng tiền nhập của kỳ tạo phiếu
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
- Cách lấy giá vốn tại thời điểm bán: Giá vốn dùng để tính lợi nhuận gộp là giá vốn bình quân gia quyền của từng biến thể, được ghi vào `order_detail_cost_price` khi khách đặt đơn. Giá vốn hàng bán trong kỳ bằng tổng `(số lượng × order_detail_cost_price)` của các dòng hàng thuộc các đơn giao thành công được tính trong kỳ.
- Tiền tính bằng số nguyên VND; thời gian lưu UTC, hiển thị `Asia/Ho_Chi_Minh` (AGENTS.md).
- Theo constraint cache (BR-GIAIDOAN1, Constraints chung — Cache): dashboard không cache — truy vấn trực tiếp Database và trả `Cache-Control: no-store` như mọi trang của portal quản trị (đã chốt 21/11/2026).
- [Sơ đồ sequence của `GET /admin/dashboard`](../../../docs/sequence/uc-37-get-dashboard.md).
- "Sản phẩm bán chạy" ở đây khác khối bán chạy trên trang chủ (UC-09): dashboard tính theo kỳ báo cáo, chỉ đơn "Giao thành công", top 10.

**Quyết định đã chốt**
- Chỉ Nhân viên xem dashboard; Khách hàng và Admin không xem được (đã chốt 15/11/2026).
- Không làm chỉ số "Hiệu quả khuyến mãi"; chuyển sang Out of Scope (đã chốt 15/11/2026).
- Kỳ báo cáo mặc định là tháng hiện tại, chọn được khoảng thời gian. Từ ngày bắt đầu: dd/mm/yyyy đến ngày kết thúc: dd/mm/yyyy, ngày bắt đầu phải nhỏ hơn ngày kết thúc. Nếu vi phạm như ngày bắt đầu lớn hơn hoặc bằng ngày kết thúc, thông báo lỗi cho người dùng để nhập lại.
- Doanh thu, lợi nhuận gộp và Top 10 sản phẩm bán chạy được ghi nhận vào kỳ chứa ngày đơn chuyển sang "Giao thành công" (đã chốt 22/11/2026).
- Doanh thu là tiền hàng sau giảm, không gồm phí vận chuyển. Top 10 xếp theo số lượng bán.
- Tồn kho thấp: tồn kho ≤ ngưỡng.

- Tiền nhập hàng theo nhà cung cấp lọc theo ngày tạo phiếu, chỉ tính phiếu đã xác nhận tại thời điểm xem; số liệu kỳ cũ có thể tăng khi xác nhận muộn. Không bổ sung thời điểm xác nhận phiếu nhập (đã chốt 22/11/2026, UC-34).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt chỉ Nhân viên xem dashboard
- v3 (2026-11-15): bỏ chỉ số "Hiệu quả khuyến mãi" (chuyển Out of Scope)
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — số đơn theo trạng thái: thêm "Chờ lấy hàng", bỏ "Bị từ chối"
- v5 (2026-11-21): chốt dashboard không cache phía server; phân biệt với khối bán chạy trang chủ
- v6 (2026-11-21): theo BR-GIAIDOAN1 v22 — trang dashboard trả `no-store` thay cho `private, no-cache` + `ETag`
- v7 (2026-11-22): chốt ngày giao thành công làm mốc ghi nhận doanh thu, lợi nhuận gộp và Top 10
- v8 (2026-11-22): đồng bộ kỳ tiền nhập hàng theo ngày tạo phiếu với UC-34, giữ các quy tắc dashboard đã có trên main; cập nhật AC-5 và thêm AC-10 cho xác nhận khác kỳ tạo
