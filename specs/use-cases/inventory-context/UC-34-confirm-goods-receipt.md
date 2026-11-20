# UC-34: Xác nhận phiếu nhập

## Metadata
- **ID:** UC-34
- **Bounded Context:** inventory-context
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Hàng đã về kho; Nhân viên chọn "Xác nhận" trên một phiếu nhập ở trạng thái "Nháp".

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Phiếu nhập ở trạng thái "Nháp" và có ít nhất một dòng hợp lệ (UC-33).

## Main Flow
1. Nhân viên mở phiếu nhập và chọn "Xác nhận".
2. Hệ thống mở một transaction và khóa các biến thể trong phiếu.
3. Với mỗi dòng (biến thể, số lượng nhập, đơn giá nhập thực tế), hệ thống:
   1. Lấy tồn hiện tại và giá vốn hiện tại của biến thể; giá trị tồn hiện tại = tồn hiện tại × giá vốn hiện tại.
   2. Tính tồn sau khi nhập = tồn hiện tại + số lượng nhập.
   3. Tính `Giá vốn mới = (Giá trị tồn hiện tại + Tiền nhập lô này) / Tồn sau khi nhập`, với tiền nhập lô này = số lượng nhập × giá nhập; làm tròn `ROUND_HALF_UP` về số nguyên VND.
   4. Cập nhật tồn kho và giá vốn của biến thể.
4. Hệ thống chuyển phiếu sang "Đã xác nhận".
5. Hệ thống commit transaction.

## Alternative Flows
- **3a. Tồn hiện tại bằng 0:** giá vốn mới = giá nhập của lô này.

## Exceptions
- **E1. Phiếu không còn ở trạng thái "Nháp":** (đã xác nhận hoặc đã hủy, kể cả do hai lần bấm xác nhận đồng thời) → hệ thống từ chối, không thay đổi tồn kho hay giá vốn.
- **E2. Lỗi khi cập nhật một dòng:** hệ thống hủy toàn bộ transaction; không dòng nào được cộng tồn, phiếu vẫn ở "Nháp".

## Postconditions
- Phiếu ở trạng thái "Đã xác nhận", không sửa được.
- Tồn kho của từng biến thể tăng đúng số lượng nhập; giá vốn được tính lại theo bình quân gia quyền.

## Acceptance Criteria

### AC-1: Tính giá vốn bình quân gia quyền
Given: biến thể "Áo bơi A – Đỏ – M" tồn 10, giá vốn 100.000đ; phiếu nháp có dòng biến thể này, số lượng 20, giá nhập 130.000đ
When: Nhân viên xác nhận phiếu
Then: tồn kho của biến thể = 30
And: giá vốn của biến thể = 120.000đ
And: phiếu ở trạng thái "Đã xác nhận"

### AC-2: Tồn hiện tại bằng 0
Given: biến thể tồn 0, giá vốn bất kỳ; phiếu nháp nhập 15 cái giá 90.000đ
When: Nhân viên xác nhận phiếu
Then: tồn kho = 15
And: giá vốn = 90.000đ

### AC-3: Làm tròn ROUND_HALF_UP
Given: biến thể tồn 1, giá vốn 100.000đ; phiếu nháp nhập 2 cái giá 100.001đ
When: Nhân viên xác nhận phiếu
Then: giá vốn = 100.001đ (300.002 / 3 = 100.000,67 làm tròn lên)

### AC-4: Phiếu nhiều dòng
Given: phiếu nháp có 2 dòng cho 2 biến thể khác nhau
When: Nhân viên xác nhận phiếu
Then: mỗi biến thể được cộng tồn và tính giá vốn độc lập theo dòng của nó

### AC-5: Không xác nhận lại phiếu đã xác nhận
Given: phiếu P đã ở trạng thái "Đã xác nhận"
When: Nhân viên xác nhận P lần nữa (hoặc hai yêu cầu xác nhận đến đồng thời)
Then: chỉ một lần xác nhận có hiệu lực
And: tồn kho chỉ được cộng một lần

### AC-6: Lỗi giữa chừng không cộng tồn dở dang
Given: phiếu nháp có 2 dòng, cập nhật dòng thứ hai gặp lỗi
When: Nhân viên xác nhận phiếu
Then: tồn kho và giá vốn của cả hai biến thể không đổi
And: phiếu vẫn ở trạng thái "Nháp"

## Dependencies
- **Upstream UC:** UC-02, UC-33
- **Downstream UC:** UC-12 (tình trạng còn/hết hàng), UC-18, UC-19, UC-20, UC-37, UC-39
- **External Systems:** không có

## Notes
- Công thức giá vốn, cách làm tròn và giá vốn theo biến thể đã chốt trong BR-GIAIDOAN1 (Constraints của BR-007).
- Cộng tồn và cập nhật giá vốn trong cùng một transaction.
- Tồn kho không bao giờ âm (BR-005).
- ERD hiện chưa có cột giá vốn ở biến thể; cần bổ sung để lưu giá vốn bình quân gia quyền.

**Quyết định đã chốt**
- Bổ sung cột giá vốn ở biến thể trong ERD để lưu giá vốn bình quân gia quyền (đã chốt 15/11/2026).
- Nhân viên xem được tồn kho theo biến thể ngoài dashboard (đã chốt 15/11/2026) — xem UC-39.
- Không lưu người và thời điểm xác nhận phiếu nhập (đã chốt 15/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bổ sung cột giá vốn ở biến thể trong ERD; câu hỏi xem tồn kho chuyển sang UC-39
- v3 (2026-11-15): chốt không lưu người và thời điểm xác nhận phiếu nhập
