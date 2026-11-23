# UC-26: Tự xuất hóa đơn

## Metadata
- **ID:** UC-26
- **Module:** ordering
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Hệ thống

## Trigger
Đơn chuyển sang trạng thái "Giao thành công" (do Trang giả lập vận chuyển cập nhật ở UC-36).

## Preconditions
- Đơn ở trạng thái "Giao thành công" và chưa có hóa đơn.

## Main Flow
1. Sau khi UC-36 ghi nhận đơn "Giao thành công", hệ thống nhận sự kiện; với đơn COD, ghi nhận "Đã thanh toán" theo giả định hiện có, không ghi lịch sử cho thay đổi thanh toán. Việc ghi nhận này độc lập với kết quả xuất hóa đơn.
2. Hệ thống tạo hóa đơn cho đơn gồm mã hóa đơn, mã đơn, thời điểm xuất và snapshot tại thời điểm xuất: tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán.
3. Trước khi tạo hoặc thử xuất lại, hệ thống kiểm tra hóa đơn hiện có và bảo đảm mỗi đơn chỉ có một hóa đơn.
4. Hóa đơn ở chế độ chỉ đọc, không sửa và không xóa; mỗi đơn có tối đa một hóa đơn kể cả khi sự kiện được gửi lại.

## Alternative Flows
- **1a. Đơn giao không thành công:** không xuất hóa đơn; tồn kho được cộng lại theo UC-35.

## Exceptions
- **E1. Đơn đã có hóa đơn:** sự kiện bị gửi lặp → hệ thống không tạo thêm hóa đơn (mỗi đơn đúng 1 hóa đơn).
- **E2. Lỗi khi tạo hóa đơn:** rollback phần tạo hóa đơn, ghi log và thử lại; đơn vẫn "Giao thành công", COD vẫn "Đã thanh toán" `[GD]`.
- **E3. Tác vụ thử lại:** hệ thống kiểm tra hóa đơn hiện có trước khi tạo; nếu đã có hóa đơn thì trả về hóa đơn đó và không tạo bản thứ hai.

## Postconditions
- Đơn "Giao thành công" có đúng 1 hóa đơn chỉ đọc, lưu snapshot thông tin tại thời điểm xuất.
- Với đơn COD: trạng thái thanh toán "Đã thanh toán" `[GD]`.
- UC này không ghi thêm lịch sử trạng thái đơn; dòng "Đang giao → Giao thành công" do UC-36 ghi.

## Acceptance Criteria

### AC-1: Xuất hóa đơn khi giao thành công
Given: đơn 7K3M9Q2X "Đang giao", tổng thanh toán 480.000đ
When: Trang giả lập vận chuyển cập nhật 7K3M9Q2X sang "Giao thành công"
Then: hệ thống tạo 1 hóa đơn cho 7K3M9Q2X với tổng 480.000đ
And: hóa đơn có đủ tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán

### AC-2: Không xuất hóa đơn khi giao không thành công
Given: đơn 4HZP8W1N "Đang giao"
When: trang giả lập cập nhật 4HZP8W1N sang "Giao không thành công"
Then: không có hóa đơn nào được tạo cho 4HZP8W1N

### AC-3: Không tạo trùng
Given: đơn 7K3M9Q2X đã có hóa đơn
When: sự kiện "Giao thành công" của 7K3M9Q2X được gửi lại
Then: 7K3M9Q2X vẫn chỉ có 1 hóa đơn

### AC-4: Hóa đơn không đổi khi dữ liệu gốc thay đổi
Given: hóa đơn của 7K3M9Q2X ghi đơn giá "Đỏ / M" là 250.000đ và tên sản phẩm "Áo bơi A"
When: Nhân viên đổi giá size M thành 300.000đ và đổi tên sản phẩm thành "Áo bơi A mới"
Then: hóa đơn của 7K3M9Q2X vẫn ghi 250.000đ và "Áo bơi A"

### AC-5: Đơn COD được ghi nhận đã thanh toán
Given: đơn COD B6TQ2R5D "Đang giao"
When: trang giả lập cập nhật B6TQ2R5D sang "Giao thành công"
Then: B6TQ2R5D được ghi nhận "Đã thanh toán" và có hóa đơn

### AC-6: Hai tác vụ xuất hóa đơn đồng thời
Given: đơn "Giao thành công" chưa có hóa đơn
When: hai tác vụ cùng xử lý xuất hóa đơn cho đơn đó
Then: chỉ một hóa đơn được tạo; tác vụ còn lại sử dụng hóa đơn đã có

### AC-7: Thử lại sau lỗi tạo hóa đơn
Given: đơn đã "Giao thành công" nhưng chưa có hóa đơn do lần tạo trước thất bại
When: hệ thống thử lại và xử lý thành công
Then: đơn vẫn "Giao thành công" và có đúng một hóa đơn
And: các lần thử lại tiếp theo không tạo thêm hóa đơn

## Dependencies
- **Upstream UC:** UC-36 Cập nhật trạng thái giao hàng
- **Downstream UC:** UC-27 Xem hóa đơn, UC-37 Xem dashboard
- **External Systems:** Không có

## Notes
- Việc tạo hóa đơn phải bảo đảm duy nhất theo đơn ở cơ sở dữ liệu, kể cả khi hai tác vụ cùng kiểm tra chưa có hóa đơn rồi cùng tạo.
- BR-GIAIDOAN1: hóa đơn tự xuất khi giao thành công; khách và nhân viên chỉ xem (đã chốt 20/11/2026).
- Không phải hóa đơn điện tử VAT (Out of Scope).
- Tiền tính bằng số nguyên VND.

### Quyết định đã chốt
- Hóa đơn lưu snapshot tại thời điểm xuất gồm: tên sản phẩm, đơn giá gốc, đơn giá sau giảm, số lượng, tiền giảm, phí vận chuyển, tổng thanh toán, địa chỉ, người đặt, số điện thoại, email, phương thức thanh toán (theo ERD).
- Mỗi đơn có tối đa 1 hóa đơn (theo ERD).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử: trạng thái cũ, trạng thái mới, nguồn thay đổi, người đổi (nếu có), thời điểm (theo ERD).
- Thay đổi trạng thái thanh toán không được ghi lịch sử; `order_status_history` chỉ lưu trạng thái đơn (đã chốt 15/11/2026).
- Mã hóa đơn hiển thị sinh từ `invoice_id`, không có cột riêng (data model v1).

### Giả định [GD]
- Đơn COD được ghi nhận "Đã thanh toán" khi giao thành công.
- Lỗi tạo hóa đơn không làm thay đổi trạng thái giao của đơn; hệ thống thử lại.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt snapshot hóa đơn và mỗi đơn tối đa 1 hóa đơn (theo ERD); lưu lịch sử khi COD chuyển "Đã thanh toán"
- v3 (2026-11-15): không ghi thay đổi trạng thái thanh toán vào lịch sử (theo data model v1); mã hóa đơn sinh từ `invoice_id`
- v4 (2026-11-20): đồng bộ BR-GIAIDOAN1 — chốt khách và Nhân viên chỉ xem hóa đơn; mã đơn ví dụ theo định dạng Crockford Base32
- v5 (2026-11-22): làm rõ thứ tự với UC-36, kiểm tra hóa đơn trước khi tạo và xử lý retry; thêm AC-6, AC-7.
- v6 (2026-11-22): bỏ ngoại lệ E3 trùng; làm rõ chống tạo hóa đơn đồng thời và cập nhật AC-6.
- v7 (2026-11-22): làm rõ COD đã thanh toán khi giao thành công, độc lập với lỗi xuất hóa đơn.
