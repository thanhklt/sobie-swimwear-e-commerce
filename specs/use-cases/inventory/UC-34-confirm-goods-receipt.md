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
2. Hệ thống mở một transaction:
   1. Khóa dòng phiếu trong `inventory.goods_receipt` bằng `SELECT ... FOR UPDATE`, rồi kiểm tra lại trạng thái `DRAFT` sau khi lấy được khóa. Nếu không còn `DRAFT`, xử lý E1.
   2. Đọc lại các dòng chi tiết đã lưu của phiếu sau khi khóa phiếu. Mọi thao tác sửa chi tiết hoặc hủy phiếu ở UC-33 phải khóa cùng dòng phiếu và kiểm tra lại `DRAFT` trước khi ghi.
   3. Khóa các dòng `inventory.stock` tương ứng bằng `SELECT ... FOR UPDATE`, theo thứ tự tăng dần `stock_variant_key` để các phiếu có biến thể chung lấy khóa theo cùng thứ tự. Giữ các khóa đến khi transaction kết thúc. Các phiếu khác nhau cùng nhập một biến thể phải chờ khóa dòng tồn kho đó; sau khi lấy khóa, bước 3 dùng tồn và giá vốn đã được transaction trước commit.
3. Với mỗi dòng (biến thể, số lượng nhập, đơn giá nhập thực tế), hệ thống:
   1. Đọc tồn hiện tại và giá vốn hiện tại từ dòng `inventory.stock` đã khóa; giá trị tồn hiện tại = tồn hiện tại × giá vốn hiện tại.
   2. Tính tồn sau khi nhập = tồn hiện tại + số lượng nhập.
   3. Tính `Giá vốn mới = (Giá trị tồn hiện tại + Tiền nhập lô này) / Tồn sau khi nhập`, với tiền nhập lô này = số lượng nhập × giá nhập; dùng số nguyên VND / `Decimal`, không dùng `float`, làm tròn `ROUND_HALF_UP` về số nguyên VND ở kết quả cuối.
   4. Cập nhật tồn kho và giá vốn của biến thể (bảng `inventory.stock`).
4. Hệ thống chuyển phiếu sang "Đã xác nhận".
5. Hệ thống commit transaction.
6. Sau khi commit thành công, hệ thống gọi service công khai của catalog để tăng số phiên bản cache catalog theo Constraints chung của BR-GIAIDOAN1. Nếu cập nhật cache thành công, các lượt đọc mới dùng key có phiên bản mới để lấy dữ liệu tồn kho đã cập nhật; nếu lỗi, xử lý E3.
7. Hệ thống thông báo xác nhận phiếu thành công, kể cả khi gặp lỗi cache sau commit theo E3.

## Alternative Flows
- **3a. Tồn hiện tại bằng 0:** giá vốn mới = giá nhập của lô này.
- **1a. Nhà cung cấp đã ngừng hợp tác sau khi lập phiếu:** vẫn cho xác nhận phiếu nháp đã lưu; tiếp tục từ bước 2. Việc chọn/lưu phiếu với nhà cung cấp ngừng hợp tác vẫn bị chặn theo UC-33.

## Exceptions
- **E1. Phiếu không còn ở trạng thái "Nháp":** (đã xác nhận hoặc đã hủy, kể cả do hai lần bấm xác nhận đồng thời) → hệ thống thông báo từ chối, không thông báo thành công; không thay đổi tồn kho hay giá vốn.
- **E2. Lỗi khi cập nhật một dòng, đổi trạng thái phiếu hoặc commit:** hệ thống hủy toàn bộ transaction; tồn kho và giá vốn không đổi, phiếu vẫn ở "Nháp"; không tăng phiên bản cache catalog. Hệ thống báo lỗi, không thông báo xác nhận thành công.
- **E3. Lỗi tăng phiên bản cache catalog sau commit:** phiếu vẫn ở "Đã xác nhận", tồn kho và giá vốn giữ nguyên kết quả đã commit; hệ thống vẫn thông báo xác nhận thành công, ghi log lỗi cache kèm mã phiếu. Không rollback dữ liệu đã commit, không yêu cầu xác nhận lại và không thêm cơ chế retry cache. Dữ liệu cache cũ có thể còn được hiển thị tối đa 5 phút theo TTL dự phòng; khi key hết hạn, lượt đọc tiếp theo lấy dữ liệu mới từ Database.

## Postconditions
- **Xác nhận thành công:** phiếu ở trạng thái "Đã xác nhận", không sửa được; tồn kho từng biến thể tăng đúng số lượng nhập, giá vốn được tính lại theo bình quân gia quyền; hệ thống thông báo xác nhận thành công.
- **Cache cập nhật thành công sau commit:** phiên bản cache catalog được tăng và lượt đọc mới không dùng dữ liệu tồn kho cache của phiên bản cũ.
- **Cache lỗi sau commit (E3):** phiếu, tồn kho và giá vốn giữ kết quả đã commit; vẫn thông báo xác nhận thành công, ghi log và chờ TTL dự phòng 5 phút làm hết hạn dữ liệu cũ, không retry.
- **Bị từ chối (E1):** yêu cầu không thay đổi phiếu, chi tiết, tồn kho, giá vốn hoặc phiên bản cache; hệ thống thông báo từ chối. Nếu phải chờ transaction khác hoàn tất, yêu cầu bị từ chối giữ nguyên kết quả transaction đó đã commit.
- **Lỗi database và rollback (E2):** mọi thay đổi của yêu cầu bị rollback; phiếu vẫn "Nháp", chi tiết không đổi, tồn kho và giá vốn giữ giá trị trước transaction; không tăng phiên bản cache và không thông báo xác nhận thành công.

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
Given: biến thể tồn 1, giá vốn 100.000đ; phiếu nháp nhập 1 cái giá 100.001đ
When: Nhân viên xác nhận phiếu
Then: tồn kho = 2
And: giá vốn = 100.001đ (200.001 / 2 = 100.000,5 làm tròn ROUND_HALF_UP)

### AC-4: Phiếu nhiều dòng
Given: phiếu nháp có dòng A nhập 20 cái giá 130.000đ cho biến thể A đang tồn 10, giá vốn 100.000đ; dòng B nhập 5 cái giá 100.000đ cho biến thể B đang tồn 5, giá vốn 80.000đ
When: Nhân viên xác nhận phiếu
Then: biến thể A tồn 30, giá vốn 120.000đ
And: biến thể B tồn 10, giá vốn 90.000đ
And: phiếu ở trạng thái "Đã xác nhận"; cả hai dòng được cập nhật trong cùng transaction

### AC-5: Không xác nhận lại phiếu đã xác nhận
Given: phiếu P đã ở trạng thái "Đã xác nhận"
When: Nhân viên xác nhận P lần nữa
Then: hệ thống từ chối vì P không còn ở trạng thái "Nháp"
And: tồn kho, giá vốn, trạng thái phiếu và phiên bản cache catalog không đổi

### AC-6: Lỗi database rollback toàn bộ việc xác nhận
Given: phiếu nháp P có 2 dòng cho 2 biến thể khác nhau; tồn kho, giá vốn và chi tiết trước transaction đã được ghi nhận
When: Nhân viên xác nhận P và gặp từng lỗi độc lập sau đây:

| Điểm lỗi | Các thay đổi đã thực hiện trong transaction trước lỗi |
|---|---|
| Cập nhật tồn kho/giá vốn dòng thứ hai | Dòng thứ nhất đã được cập nhật. |
| Chuyển phiếu sang "Đã xác nhận" | Tồn kho và giá vốn của cả hai biến thể đã được cập nhật. |
| Commit transaction | Cả hai biến thể đã được cập nhật và phiếu đã được chuyển sang "Đã xác nhận" trong transaction chưa commit. |

Then: hệ thống rollback toàn bộ transaction; tồn kho và giá vốn của cả hai biến thể giữ giá trị trước transaction
And: phiếu P vẫn ở trạng thái "Nháp", mọi dòng chi tiết không đổi
And: phiên bản cache catalog không đổi; hệ thống báo lỗi và không thông báo xác nhận thành công

### AC-7: Xác nhận phiếu cũ khi nhà cung cấp đã ngừng hợp tác
Given: phiếu nháp P đã lưu khi nhà cung cấp X còn "Đang hợp tác", có dòng nhập 20 cái giá 130.000đ; biến thể hiện tồn 10, giá vốn 100.000đ; X sau đó chuyển sang "Ngừng hợp tác"
When: Nhân viên xác nhận P
Then: phiếu P ở trạng thái "Đã xác nhận"
And: tồn kho của biến thể = 30, giá vốn = 120.000đ
And: phiếu P vẫn tham chiếu nhà cung cấp X

### AC-8: Hai yêu cầu cùng xác nhận một phiếu nháp
Given: phiếu P ở trạng thái "Nháp", nhập 20 cái giá 130.000đ cho biến thể đang tồn 10, giá vốn 100.000đ; service cache catalog hoạt động bình thường
When: hai yêu cầu xác nhận P đến đồng thời
Then: chỉ một yêu cầu xác nhận thành công; yêu cầu còn lại bị từ chối vì P đã ở trạng thái "Đã xác nhận"
And: tồn kho = 30, giá vốn = 120.000đ, phiếu P ở trạng thái "Đã xác nhận"
And: phiên bản cache catalog chỉ được tăng bởi lần xác nhận thành công

### AC-9: Không xác nhận phiếu đã hủy
Given: phiếu P ở trạng thái "Đã hủy"
When: Nhân viên xác nhận P
Then: hệ thống từ chối vì P không còn ở trạng thái "Nháp"
And: tồn kho, giá vốn, trạng thái phiếu và phiên bản cache catalog không đổi

### AC-10: Giá nhập bằng 0 khi còn tồn kho
Given: biến thể tồn 10, giá vốn 100.000đ; phiếu nháp nhập 10 cái giá 0đ
When: Nhân viên xác nhận phiếu
Then: tồn kho = 20, giá vốn = 50.000đ
And: phiếu ở trạng thái "Đã xác nhận"

### AC-11: Giá nhập bằng 0 khi tồn kho bằng 0
Given: biến thể tồn 0, giá vốn 100.000đ; phiếu nháp nhập 10 cái giá 0đ
When: Nhân viên xác nhận phiếu
Then: tồn kho = 10, giá vốn = 0đ
And: phiếu ở trạng thái "Đã xác nhận"

### AC-12: Cập nhật phiên bản cache sau khi xác nhận thành công
Given: biến thể tồn 0; dữ liệu cache catalog của phiên bản hiện tại thể hiện hết hàng; phiếu nháp nhập 10 cái cho biến thể này; service cache catalog hoạt động bình thường
When: Nhân viên xác nhận phiếu thành công
Then: phiên bản cache catalog tăng sau khi transaction đã commit
And: lượt đọc mới của trang bán hàng dùng key của phiên bản mới và hiển thị biến thể còn hàng

### AC-13: Xác nhận đồng thời với sửa hoặc hủy phiếu
Given: phiếu P ở trạng thái "Nháp"
When: yêu cầu xác nhận và yêu cầu sửa hoặc hủy P chạy đồng thời
Then: các yêu cầu được tuần tự hóa bằng khóa cùng dòng phiếu; kết quả theo thao tác lấy khóa và commit thành công trước:

| Thao tác trước | Yêu cầu chờ khóa | Kết quả |
|---|---|---|
| Sửa phiếu | Xác nhận | Xác nhận đọc các dòng đã sửa và cộng tồn, tính giá vốn theo dữ liệu mới đã lưu. |
| Xác nhận | Sửa phiếu | Từ chối sửa vì phiếu đã xác nhận; chi tiết phiếu, tồn kho và giá vốn không bị thay đổi bởi yêu cầu sửa. |
| Hủy phiếu | Xác nhận | Từ chối xác nhận vì phiếu đã hủy; tồn kho, giá vốn và phiên bản cache catalog không đổi. |
| Xác nhận | Hủy phiếu | Từ chối hủy vì phiếu đã xác nhận; tồn kho chỉ được cộng một lần, giá vốn giữ kết quả của lần xác nhận. |

### AC-14: Lỗi cache sau commit vẫn xác nhận thành công
Given: biến thể tồn 0, giá vốn 0đ; cache catalog hiện thể hiện hết hàng với TTL dự phòng 5 phút; phiếu nháp P nhập 10 cái giá 100.000đ
When: xác nhận P đã commit thành công nhưng lời gọi tăng phiên bản cache catalog gặp lỗi
Then: hệ thống vẫn thông báo xác nhận thành công; P ở trạng thái "Đã xác nhận", tồn kho = 10, giá vốn = 100.000đ
And: hệ thống ghi log lỗi cache kèm mã phiếu P; không yêu cầu xác nhận lại, không rollback dữ liệu đã commit và không retry cache
And: dữ liệu cache cũ chỉ có thể còn được hiển thị tối đa 5 phút; sau khi key hết hạn, lượt đọc tiếp theo lấy dữ liệu mới từ Database và hiển thị biến thể còn hàng

### AC-15: Hai phiếu khác nhau cùng nhập một biến thể đồng thời
Given: biến thể A tồn 10, giá vốn 100.000đ; phiếu nháp P1 nhập 10 cái A giá 120.000đ, phiếu nháp P2 nhập 20 cái A giá 130.000đ; service cache catalog hoạt động bình thường
When: Nhân viên xác nhận P1 và P2 đồng thời, cả hai transaction đều thành công
Then: các yêu cầu được tuần tự hóa tại khóa cùng dòng `inventory.stock` của A; yêu cầu chờ khóa dùng tồn kho và giá vốn đã được yêu cầu trước commit
And: sau khi cả hai transaction hoàn tất, A tồn 40, giá vốn 120.000đ, bất kể P1 hay P2 lấy khóa tồn kho trước
And: P1 và P2 đều ở trạng thái "Đã xác nhận", mỗi phiếu chỉ cộng tồn một lần; hệ thống thông báo xác nhận thành công cho cả hai
And: mỗi lần xác nhận chỉ cập nhật phiên bản cache catalog sau khi transaction của phiếu đó commit

## Dependencies
- **Upstream UC:** UC-02, UC-33
- **Downstream UC:** UC-12 (tình trạng còn/hết hàng), UC-18, UC-19, UC-20, UC-37, UC-39
- **External Systems:** không có

## Notes
- Công thức giá vốn, cách làm tròn và giá vốn theo biến thể đã chốt trong BR-GIAIDOAN1 (Constraints của BR-007).
- Cộng tồn và cập nhật giá vốn trong cùng một transaction.
- Tồn kho không bao giờ âm (BR-005).
- Tồn kho và giá vốn bình quân gia quyền của biến thể lưu ở `inventory.stock` (`stock_quantity`, `stock_cost_price`), chỉ module inventory ghi (data model v2, đã chốt 20/11/2026).
- Service của inventory điều phối transaction; repository của inventory khóa phiếu và tồn kho thuộc module này. Không khóa hoặc cập nhật `catalog.variant` để thay cho khóa `inventory.stock`.
- UC-33 và UC-34 dùng chung quy tắc: khóa phiếu trước khi kiểm tra `DRAFT` và đọc/ghi chi tiết hoặc trạng thái; sau đó UC-34 mới khóa các dòng tồn kho. Không dùng trạng thái hay chi tiết từ trước khi lấy khóa để quyết định xác nhận.
- Cache catalog chỉ đổi phiên bản sau commit thành công, qua service công khai của catalog; không tăng phiên bản khi từ chối hoặc rollback. Portal quản trị không cache theo Constraints chung của BR-GIAIDOAN1.
- Lỗi cache sau commit không làm thất bại việc xác nhận phiếu: ghi log và dựa vào TTL dự phòng 5 phút để hết hạn dữ liệu cũ, không thêm cơ chế retry. E2 chỉ xử lý lỗi transaction Database; lỗi cache sau commit xử lý theo E3.

**Quyết định đã chốt**
- Giá vốn bình quân gia quyền lưu theo biến thể ở `inventory.stock.stock_cost_price` (đã chốt 15/11/2026; chuyển từ `catalog.variant` sang `inventory.stock` ngày 20/11/2026, data model v2).
- Nhân viên xem được tồn kho theo biến thể ngoài dashboard (đã chốt 15/11/2026) — xem UC-39.
- Không lưu người và thời điểm xác nhận phiếu nhập (đã chốt 15/11/2026).
- Cho xác nhận phiếu nháp đã lưu trước khi nhà cung cấp ngừng hợp tác; vẫn chặn chọn/lưu phiếu với nhà cung cấp ngừng hợp tác theo UC-33 (đã chốt 22/11/2026).
- Tiền nhập hàng trên dashboard tính theo ngày tạo phiếu, chỉ tính phiếu đã xác nhận tại thời điểm xem; xác nhận muộn có thể làm tăng số liệu kỳ cũ (đã chốt 22/11/2026, xem UC-37).
- Khóa phiếu, kiểm tra lại `DRAFT`, khóa đúng dòng `inventory.stock` và đồng bộ sửa/hủy với UC-33; bổ sung AC cho đồng thời, phiếu đã hủy, giá nhập 0 và cập nhật phiên bản cache sau commit (đã chốt 22/11/2026).
- Nếu tăng phiên bản cache catalog lỗi sau khi phiếu đã commit: vẫn báo xác nhận thành công, ghi log lỗi cache kèm mã phiếu, chờ TTL dự phòng 5 phút làm mới dữ liệu; không thêm cơ chế retry (đã chốt 22/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt bổ sung cột giá vốn ở biến thể trong ERD; câu hỏi xem tồn kho chuyển sang UC-39
- v3 (2026-11-15): chốt không lưu người và thời điểm xác nhận phiếu nhập
- v4 (2026-11-21): cập nhật nơi lưu tồn kho và giá vốn bình quân gia quyền theo data model v2
- v5 (2026-11-22): chốt xác nhận phiếu nháp cũ khi nhà cung cấp ngừng hợp tác và cách tính kỳ tiền nhập hàng trên dashboard; thêm AC-7
- v6 (2026-11-22): hoàn thiện khóa phiếu/tồn kho và đồng bộ sửa/hủy UC-33; sửa AC-3 và AC-5; thêm AC-8 đến AC-13; cập nhật phiên bản cache catalog sau commit thành công
- v7 (2026-11-22): chốt lỗi cache sau commit vẫn báo xác nhận thành công, ghi log và chờ TTL 5 phút, không retry; thêm E3 và AC-14, làm rõ hậu điều kiện cùng AC-8/AC-12 khi cache hoạt động bình thường
- v8 (2026-11-22): tách hậu điều kiện thành công/từ chối/rollback; cụ thể hóa AC-4, mở rộng AC-6 cho lỗi đổi trạng thái và commit; thêm AC-15 cho hai phiếu khác nhau cùng nhập một biến thể đồng thời
