# UC-34: Xác nhận phiếu nhập

## Metadata
- **ID:** UC-34
- **Module:** inventory
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
2. Hệ thống mở MỘT Database Transaction dùng chung cho các Service tham gia:
   - Khóa dòng phiếu nhập `FOR UPDATE`, đọc lại trạng thái; nếu không còn DRAFT thì xử lý E1 trước mọi cập nhật tồn kho.
   - Từ các dòng phiếu hiện hành, gọi Service công khai Catalog xác định toàn bộ sản phẩm cha và khóa `catalog.product FOR UPDATE` theo `product_key ASC`, sau đó khóa các biến thể theo `variant_key ASC` qua cùng Service. Không truy cập Repository/bảng Catalog trực tiếp từ inventory; truyền cùng session/transaction và giữ mọi khóa đến commit/rollback.
   - Không lấy khóa biến thể trước khóa sản phẩm; không lấy thêm khóa taxonomy sau khóa sản phẩm. Xác nhận nhập không tạo/thay đổi tham chiếu taxonomy. Nếu phải chờ thì đọc lại dữ liệu hiện hành sau khi được cấp khóa; kiểm tra lại trạng thái phiếu và các dòng trước bước 3.
3. Với mỗi dòng (biến thể, số lượng nhập, đơn giá nhập thực tế), hệ thống:
   1. Lấy tồn hiện tại và giá vốn hiện tại của biến thể; giá trị tồn hiện tại = tồn hiện tại × giá vốn hiện tại.
   2. Tính tồn sau khi nhập = tồn hiện tại + số lượng nhập.
   3. Tính `Giá vốn mới = (Giá trị tồn hiện tại + Tiền nhập lô này) / Tồn sau khi nhập`, với tiền nhập lô này = số lượng nhập × giá nhập; làm tròn `ROUND_HALF_UP` về số nguyên VND.
   4. Cập nhật tồn kho và giá vốn của biến thể (bảng `inventory.stock`).
4. Hệ thống chuyển phiếu sang "Đã xác nhận" trong cùng transaction. Sau khi commit, mọi sản phẩm có biến thể thuộc phiếu này chỉ được sửa Mô tả theo UC-14-Q11; không tự đổi giá, trạng thái hay cấu hình sản phẩm để đáp ứng điều kiện mở bán.
5. Hệ thống commit transaction.

## Alternative Flows
- **3a. Tồn hiện tại bằng 0:** giá vốn mới = giá nhập của lô này.

## Exceptions
- **E1. Phiếu không còn ở trạng thái "Nháp":** (đã xác nhận hoặc đã hủy, kể cả do hai lần bấm xác nhận đồng thời) → hệ thống từ chối, không thay đổi tồn kho hay giá vốn.
- **E2. Lỗi khi cập nhật một dòng:** hệ thống hủy toàn bộ transaction; không dòng nào được cộng tồn, phiếu vẫn ở "Nháp".

## Postconditions
- Phiếu ở trạng thái "Đã xác nhận", không sửa được.
- Việc chuyển CONFIRMED và cập nhật tồn kho/giá vốn là một commit. Các request sửa Catalog chờ cùng khóa sản phẩm rồi kiểm tra lại phiếu; không được lưu thay đổi ngoài Mô tả dựa trên trạng thái DRAFT cũ. Nếu xác nhận rollback, không phát sinh khóa nghiệp vụ sau nhập mới từ phiếu thất bại này.
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

### AC-7: Xác nhận nhập và sửa Catalog tuân thủ cùng khóa sản phẩm
Given: A chưa có phiếu CONFIRMED, phiếu P đang DRAFT nhập một biến thể của A; Nhân viên đã mở form sửa tên A
When: chạy độc lập hai thứ tự khóa giữa xác nhận P và lưu tên A, dùng chung giao thức khóa sản phẩm qua Service Catalog
Then: nếu xác nhận P giữ khóa trước và commit, request sửa chờ rồi đọc lại CONFIRMED, bị chặn theo UC-14 E10, tên A giữ nguyên
And: nếu sửa tên giữ khóa trước và commit, xác nhận P chờ rồi tiếp tục trên dữ liệu mới; sau commit CONFIRMED, mọi request sửa ngoài Mô tả tiếp theo bị chặn
And: nếu xác nhận P rollback thì tồn kho/giá vốn và trạng thái P giữ nguyên, A không bị khóa sửa bởi lần xác nhận thất bại này

### AC-8: Hai phiếu nhập nhiều sản phẩm không đảo thứ tự khóa
Given: P và Q là hai phiếu DRAFT khác nhau cùng chứa sản phẩm A và B nhưng thứ tự các dòng trên form ngược nhau; tồn ban đầu bằng 0, giá nhập hợp lệ
When: xác nhận đồng thời P và Q
Then: cả hai lấy khóa sản phẩm theo product_key ASC trước bất kỳ khóa biến thể nào, không theo thứ tự dòng trên form
And: cả hai phiếu được xác nhận lần lượt, không chờ vòng do đảo thứ tự sản phẩm; tồn kho cuối bằng tổng nhập của cả hai phiếu và giá vốn tính từ các lần nhập đã commit

## Dependencies
- **Upstream UC:** UC-02, UC-33
- **Internal Services:** Catalog khóa sản phẩm/biến thể và lấy quan hệ biến thể–sản phẩm qua Service công khai dùng cùng DB session; đồng bộ hợp đồng với UC-14/15/16/17.
- **Downstream UC:** UC-12 (tình trạng còn/hết hàng), UC-18, UC-19, UC-20, UC-37, UC-39
- **External Systems:** không có

## Notes
- Công thức giá vốn, cách làm tròn và giá vốn theo biến thể đã chốt trong BR-GIAIDOAN1 (Constraints của BR-007).
- Cộng tồn và cập nhật giá vốn trong cùng một transaction.
- Khóa dòng phiếu → toàn bộ sản phẩm cha theo product_key ASC qua Service Catalog → biến thể theo variant_key ASC → cập nhật stock trong cùng transaction. Catalog kiểm tra CONFIRMED bằng Service inventory sau cùng khóa sản phẩm. Hợp đồng này ngăn xác nhận nhập chen giữa kiểm tra và ghi thay đổi Catalog; không khóa taxonomy trong khi đã giữ khóa sản phẩm. Giữ Status draft vì lượt này chỉ đồng bộ hợp đồng liên UC đã được yêu cầu tại Codex, không chốt toàn bộ nghiệp vụ inventory.
- Khi được gọi từ Catalog để kiểm tra CONFIRMED, Service inventory chỉ đọc dữ liệu đã commit trong cùng session, không lấy khóa dòng phiếu vì bên gọi đã giữ khóa sản phẩm; tránh vòng chờ ngược với luồng xác nhận phiếu.
- Hợp đồng này dùng isolation READ COMMITTED; sau chờ khóa, Catalog phải thực hiện truy vấn kiểm tra CONFIRMED mới trong cùng transaction, không dùng snapshot/kết quả kiểm tra trước khi chờ.
- Tồn kho không bao giờ âm (BR-005).
- Tồn kho và giá vốn bình quân gia quyền của biến thể lưu ở `inventory.stock` (`stock_quantity`, `stock_cost_price`), chỉ module inventory ghi (data model v2, đã chốt 20/11/2026).

**Quyết định đã chốt**
- Giá vốn bình quân gia quyền lưu theo biến thể ở `inventory.stock.stock_cost_price` (đã chốt 15/11/2026; chuyển từ `catalog.variant` sang `inventory.stock` ngày 20/11/2026, data model v2).
- Nhân viên xem được tồn kho theo biến thể ngoài dashboard (đã chốt 15/11/2026) — xem UC-39.
- Không lưu người và thời điểm xác nhận phiếu nhập (đã chốt 15/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bổ sung cột giá vốn ở biến thể trong ERD; câu hỏi xem tồn kho chuyển sang UC-39
- v3 (2026-11-15): chốt không lưu người và thời điểm xác nhận phiếu nhập
- v4 (2026-11-21): cập nhật nơi lưu tồn kho và giá vốn bình quân gia quyền theo data model v2
- v5 (2026-11-23): đồng bộ phạm vi khóa với Catalog theo yêu cầu developer tại Codex: khóa phiếu, gọi Service Catalog cùng session khóa sản phẩm ASC rồi biến thể ASC, kiểm tra lại sau chờ; thêm AC-7/8, bảo toàn khóa sửa sau CONFIRMED và rollback, giữ draft ngoài phạm vi hoàn thiện Catalog.
