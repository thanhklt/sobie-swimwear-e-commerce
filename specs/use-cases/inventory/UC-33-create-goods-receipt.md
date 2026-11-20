# UC-33: Lập phiếu nhập

## Metadata
- **ID:** UC-33
- **Bounded Context:** inventory-context
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên chọn "Lập phiếu nhập" khi cửa hàng nhập hàng từ nhà cung cấp.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Có ít nhất một nhà cung cấp "Đang hợp tác" (UC-32) và các biến thể cần nhập đã tồn tại (UC-15).

## Main Flow
1. Nhân viên chọn nhà cung cấp.
2. Nhân viên thêm các dòng: chọn biến thể (sản phẩm × màu × size), nhập số lượng và đơn giá nhập thực tế.
3. Hệ thống tính thành tiền từng dòng = số lượng × đơn giá nhập thực tế, và tổng tiền phiếu = tổng thành tiền các dòng.
4. Nhân viên lưu phiếu.
5. Hệ thống lưu phiếu ở trạng thái "Nháp" `[GD]`, kèm nhà cung cấp, Nhân viên lập phiếu, ngày tạo và tổng tiền. Tồn kho và giá vốn chưa thay đổi.

## Alternative Flows
- **4a. Sửa phiếu nháp:** Nhân viên thêm, sửa, xóa dòng hoặc đổi nhà cung cấp khi phiếu còn "Nháp" `[GD]`.
- **4b. Hủy phiếu nháp:** phiếu chuyển sang "Đã hủy", không ảnh hưởng tồn kho `[GD]`.
- **4c. Xem danh sách phiếu nhập:** Nhân viên xem danh sách phiếu nhập, lọc theo trạng thái và nhà cung cấp `[GD]`.

## Exceptions
- **E1. Phiếu không có dòng nào:** hệ thống báo lỗi, không lưu.
- **E2. Số lượng hoặc giá nhập không hợp lệ:** số lượng không phải số nguyên dương, hoặc giá nhập không phải số nguyên VND dương → hệ thống báo lỗi tại dòng tương ứng, không lưu.
- **E3. Trùng biến thể trong phiếu:** một biến thể xuất hiện ở hai dòng → hệ thống báo lỗi, yêu cầu gộp thành một dòng `[GD]`.
- **E4. Nhà cung cấp đã ngừng hợp tác:** không chọn được (chỉ nhà cung cấp "Đang hợp tác" được chọn); nếu nhà cung cấp chuyển sang ngừng hợp tác khi phiếu đang nháp thì báo lỗi khi lưu `[GD]`.
- **E5. Sửa phiếu không còn ở trạng thái "Nháp":** hệ thống từ chối.

## Postconditions
- Phiếu nhập ở trạng thái "Nháp" với nhà cung cấp, Nhân viên lập phiếu, ngày tạo, tổng tiền và các dòng chi tiết (biến thể, số lượng, đơn giá nhập thực tế, thành tiền); chờ xác nhận (UC-34).

## Acceptance Criteria

### AC-1: Lập phiếu nhập hợp lệ
Given: nhà cung cấp X đang hợp tác, biến thể "Áo bơi A – Đỏ – M" tồn tại với tồn kho 10
When: Nhân viên lập phiếu cho X với dòng "Áo bơi A – Đỏ – M", số lượng 20, giá nhập 130.000đ
Then: phiếu được lưu ở trạng thái "Nháp" với tổng tiền 2.600.000đ
And: phiếu ghi nhà cung cấp X, Nhân viên lập phiếu và ngày tạo
And: tồn kho của biến thể vẫn là 10

### AC-2: Phiếu không có dòng
Given: Nhân viên đã chọn nhà cung cấp
When: Nhân viên lưu phiếu khi chưa thêm dòng nào
Then: hệ thống báo lỗi, không lưu

### AC-3: Số lượng hoặc giá nhập không hợp lệ
Given: Nhân viên đang lập phiếu
When: Nhân viên nhập số lượng 0 hoặc giá nhập âm
Then: hệ thống báo lỗi tại dòng tương ứng, không lưu

### AC-4: Trùng biến thể
Given: phiếu đã có dòng "Áo bơi A – Đỏ – M"
When: Nhân viên thêm dòng thứ hai cùng biến thể
Then: hệ thống báo lỗi trùng biến thể

### AC-5: Không sửa phiếu đã xác nhận
Given: phiếu P ở trạng thái "Đã xác nhận"
When: Nhân viên sửa số lượng một dòng của P
Then: hệ thống từ chối, phiếu P không đổi

### AC-6: Chỉ chọn nhà cung cấp đang hợp tác
Given: nhà cung cấp X "Đang hợp tác", nhà cung cấp Y "Ngừng hợp tác"
When: Nhân viên mở danh sách chọn nhà cung cấp khi lập phiếu nhập
Then: danh sách có X và không có Y

## Dependencies
- **Upstream UC:** UC-02, UC-15, UC-32
- **Downstream UC:** UC-34, UC-37
- **External Systems:** không có

## Notes
- Phiếu nháp chưa làm thay đổi tồn kho hay giá vốn; chỉ UC-34 mới thay đổi.
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách phiếu nhập.

**Quyết định đã chốt**
- Phiếu nhập lưu nhà cung cấp, Nhân viên lập phiếu, ngày tạo, trạng thái, tổng tiền; mỗi dòng chi tiết gồm biến thể, số lượng, đơn giá nhập thực tế, thành tiền (theo ERD).
- Chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (đã chốt 15/11/2026, UC-32).

**Giả định [GD]**
- Phiếu nhập có trạng thái: Nháp → Đã xác nhận | Đã hủy; chỉ sửa và hủy được khi còn "Nháp".
- Mỗi biến thể chỉ xuất hiện một dòng trong một phiếu.
- Danh sách phiếu nhập lọc được theo trạng thái và nhà cung cấp.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): khớp thông tin phiếu nhập và chi tiết phiếu theo ERD
- v3 (2026-11-15): chốt chỉ chọn nhà cung cấp "Đang hợp tác"; thêm AC-6
