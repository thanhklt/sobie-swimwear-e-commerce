# UC-33: Lập phiếu nhập

## Metadata
- **ID:** UC-33
- **Module:** inventory
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên chọn "Lập phiếu nhập" khi cửa hàng nhập hàng từ nhà cung cấp, hoặc mở danh sách phiếu nhập để tra cứu, sửa hay hủy phiếu nháp.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Khi lập phiếu hoặc lưu sửa: nhà cung cấp được lưu trên phiếu phải "Đang hợp tác" (UC-32), các biến thể cần nhập đã tồn tại (UC-15).
- Tra cứu hoặc hủy phiếu cũ không yêu cầu còn nhà cung cấp "Đang hợp tác". Khi sửa/hủy, trạng thái `DRAFT` được kiểm tra lại sau khi lấy khóa dòng phiếu theo luồng 4a/4b.

## Main Flow
1. Nhân viên chọn nhà cung cấp.
2. Nhân viên thêm các dòng: chọn biến thể (sản phẩm × màu × size), nhập số lượng và đơn giá nhập thực tế.
3. Hệ thống tính thành tiền từng dòng = số lượng × đơn giá nhập thực tế, và tổng tiền phiếu = tổng thành tiền các dòng.
4. Nhân viên lưu phiếu.
5. Hệ thống lưu phiếu ở trạng thái "Nháp" `[GD]`, kèm nhà cung cấp, Nhân viên lập phiếu, ngày tạo và tổng tiền. Tồn kho và giá vốn chưa thay đổi.

## Alternative Flows
- **4a. Sửa phiếu nháp:** Nhân viên thêm, sửa, xóa dòng hoặc đổi nhà cung cấp khi phiếu còn "Nháp" `[GD]`.
  1. Khi Nhân viên lưu sửa, hệ thống mở database transaction, khóa dòng phiếu trong `inventory.goods_receipt` bằng `SELECT ... FOR UPDATE`.
  2. Sau khi lấy được khóa, hệ thống kiểm tra lại trạng thái `DRAFT`; nếu không còn `DRAFT`, xử lý E5. Không dùng trạng thái đã đọc trước khi lấy khóa để cho phép sửa.
  3. Hệ thống kiểm tra dữ liệu và trạng thái nhà cung cấp tại thời điểm lưu sửa theo E1–E4. Nhà cung cấp của phiếu phải đang hợp tác; nếu đã ngừng hợp tác thì từ chối lưu sửa với nhà cung cấp đó, kể cả khi giữ nguyên nhà cung cấp của phiếu nháp cũ.
  4. Chỉ sau các kiểm tra trên, hệ thống mới sửa phiếu và các dòng chi tiết, tính lại thành tiền từng dòng và tổng tiền, rồi commit cùng một transaction. Giữ khóa dòng phiếu đến khi commit/rollback; lỗi lưu sửa xử lý E6. Tồn kho và giá vốn không thay đổi.
- **4b. Hủy phiếu nháp:** phiếu chuyển sang "Đã hủy", không ảnh hưởng tồn kho `[GD]`.
  1. Hệ thống mở database transaction, khóa cùng dòng phiếu trong `inventory.goods_receipt` bằng `SELECT ... FOR UPDATE`.
  2. Sau khi lấy được khóa, hệ thống kiểm tra lại trạng thái `DRAFT`; nếu không còn `DRAFT`, xử lý E5.
  3. Chỉ sau khi kiểm tra hợp lệ, hệ thống mới chuyển phiếu sang `CANCELLED` và commit. Giữ khóa dòng phiếu đến khi commit/rollback; lỗi ghi hoặc commit xử lý E6. Tồn kho và giá vốn không thay đổi. Trạng thái nhà cung cấp không ngăn hủy phiếu nháp.
- **4c. Xem danh sách phiếu nhập:** Nhân viên xem danh sách phiếu nhập, lọc theo trạng thái và nhà cung cấp `[GD]`.

## Exceptions
- **E1. Phiếu không có dòng nào:** hệ thống báo lỗi, không lưu.
- **E2. Số lượng hoặc giá nhập không hợp lệ:** số lượng không phải số nguyên dương, hoặc giá nhập không phải số nguyên VND không âm (giá nhập bằng 0 hợp lệ) → hệ thống báo lỗi tại dòng tương ứng, không lưu.
- **E3. Trùng biến thể trong phiếu:** một biến thể xuất hiện ở hai dòng → hệ thống báo lỗi, yêu cầu gộp thành một dòng `[GD]`.
- **E4. Nhà cung cấp đã ngừng hợp tác:** không được chọn hoặc lưu trên phiếu; chỉ nhà cung cấp "Đang hợp tác" được chọn/lưu khi lập phiếu hoặc lưu sửa. Nếu nhà cung cấp ngừng hợp tác sau khi lập phiếu nháp, hệ thống chặn lưu sửa với nhà cung cấp đó; phiếu nháp cũ đã lưu vẫn được xác nhận qua UC-34 (đã chốt 22/11/2026).
- **E5. Sửa hoặc hủy phiếu không còn ở trạng thái "Nháp":** sau khi lấy được khóa dòng phiếu, nếu trạng thái không còn `DRAFT` (đã `CONFIRMED` hoặc `CANCELLED`) thì hệ thống từ chối cả sửa và hủy, kết thúc transaction mà không ghi thay đổi. Quy tắc áp dụng cả khi yêu cầu phải chờ UC-34 xác nhận xong mới lấy được khóa. Khi từ chối, phiếu và toàn bộ chi tiết không đổi bởi yêu cầu bị từ chối; tồn kho và giá vốn không bị thay đổi bởi yêu cầu đó.
- **E6. Lỗi khi lưu sửa hoặc hủy:** lỗi ghi phiếu, ghi một dòng chi tiết khi sửa, ghi trạng thái khi hủy hoặc commit → rollback toàn bộ transaction, phiếu và mọi dòng chi tiết giữ nguyên như trước thao tác, không lưu dở thay đổi; giải phóng khóa khi transaction kết thúc, báo lỗi và không thông báo thành công. Tồn kho và giá vốn không thay đổi.

## Postconditions
- **Lập phiếu thành công:** phiếu nhập ở trạng thái "Nháp" với nhà cung cấp, Nhân viên lập phiếu, ngày tạo, tổng tiền và các dòng chi tiết (biến thể, số lượng, đơn giá nhập thực tế, thành tiền); chờ xác nhận (UC-34).
- **Sửa phiếu thành công:** phiếu vẫn ở trạng thái "Nháp"; nhà cung cấp và các dòng chi tiết được lưu theo dữ liệu hợp lệ đã sửa, thành tiền từng dòng và tổng tiền được tính lại; mọi thay đổi được commit cùng nhau.
- **Hủy phiếu thành công:** phiếu chuyển sang "Đã hủy" (`CANCELLED`); các thông tin khác của phiếu và các dòng chi tiết không đổi.
- **Tra cứu:** không làm thay đổi dữ liệu phiếu hoặc chi tiết, kể cả khi mọi nhà cung cấp đã ngừng hợp tác.
- **Bị từ chối hoặc lỗi sửa/hủy:** yêu cầu không ghi thay đổi lên phiếu hay chi tiết; lỗi ghi hoặc commit rollback toàn bộ thay đổi của yêu cầu. Nếu phải chờ UC-34 xác nhận xong thì giữ nguyên kết quả đã commit của UC-34.
- Mọi thao tác thuộc UC-33 không thay đổi tồn kho hoặc giá vốn.

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

### AC-7: Nhà cung cấp ngừng hợp tác trước khi lưu sửa
Given: phiếu nháp P đã lưu với nhà cung cấp X khi X còn "Đang hợp tác"
When: X chuyển sang "Ngừng hợp tác" trước khi Nhân viên lưu sửa P với nhà cung cấp X, kể cả khi không đổi nhà cung cấp
Then: hệ thống báo lỗi và từ chối lưu sửa; phiếu P và toàn bộ dòng chi tiết đã lưu không đổi
And: tồn kho và giá vốn không thay đổi
And: P vẫn được xác nhận qua UC-34 theo dữ liệu cũ đã lưu, như AC-7 của UC-34

### AC-8: Sửa hoặc hủy đồng thời với xác nhận
Given: phiếu P ở trạng thái "Nháp"
When: yêu cầu sửa hoặc hủy P chạy đồng thời với yêu cầu xác nhận qua UC-34
Then: mọi yêu cầu mở transaction, khóa cùng dòng `inventory.goods_receipt` bằng `SELECT ... FOR UPDATE`, kiểm tra lại `DRAFT` sau khi lấy được khóa và giữ khóa đến commit/rollback; kết quả khớp AC-13 của UC-34:

| Thao tác lấy khóa và commit thành công trước | Yêu cầu chờ khóa | Kết quả |
|---|---|---|
| Sửa phiếu | Xác nhận | Xác nhận đọc các dòng mới đã lưu sau khi sửa và cộng tồn, tính giá vốn theo dữ liệu đó. Bản thân yêu cầu sửa không thay đổi tồn kho hoặc giá vốn. |
| Hủy phiếu | Xác nhận | Từ chối xác nhận vì phiếu đã `CANCELLED`; tồn kho và giá vốn không đổi. |
| Xác nhận | Sửa phiếu | Từ chối sửa vì phiếu đã `CONFIRMED`; phiếu, chi tiết, tồn kho và giá vốn không bị thay đổi bởi yêu cầu sửa. |
| Xác nhận | Hủy phiếu | Từ chối hủy vì phiếu đã `CONFIRMED`; phiếu và chi tiết không bị thay đổi bởi yêu cầu hủy; tồn kho chỉ được cộng một lần, giá vốn giữ kết quả của lần xác nhận. |

### AC-9: Lỗi lưu sửa rollback toàn bộ phiếu và chi tiết
Given: phiếu P ở trạng thái "Nháp", nhà cung cấp đang hợp tác và có hai dòng chi tiết đã lưu
When: Nhân viên lưu sửa dữ liệu hợp lệ của phiếu và các dòng, nhưng gặp lỗi khi ghi phiếu, ghi dòng thứ hai hoặc commit
Then: hệ thống báo lỗi, rollback toàn bộ transaction và không thông báo thành công
And: phiếu P, nhà cung cấp, tổng tiền, trạng thái và mọi dòng chi tiết giữ nguyên như trước khi sửa, không có thay đổi được lưu dở
And: khóa dòng phiếu được giữ đến khi rollback kết thúc; tồn kho và giá vốn không thay đổi

### AC-10: Sửa phiếu nháp thành công và tính lại tổng tiền
Given: phiếu nháp P của nhà cung cấp X đang hợp tác có dòng A số lượng 20, giá nhập 130.000đ; biến thể B tồn tại và nhà cung cấp Y đang hợp tác
When: Nhân viên thực hiện từng trường hợp độc lập dưới đây rồi lưu sửa
Then: hệ thống khóa phiếu, kiểm tra lại `DRAFT` và dữ liệu hợp lệ, lưu toàn bộ thay đổi cùng một transaction; P vẫn ở trạng thái "Nháp"
And: tồn kho và giá vốn không thay đổi

| Thay đổi | Kết quả sau commit |
|---|---|
| Đổi số lượng A thành 10 | Thành tiền A và tổng phiếu bằng 1.300.000đ. |
| Đổi giá nhập A thành 100.000đ | Thành tiền A và tổng phiếu bằng 2.000.000đ. |
| Thêm dòng B số lượng 2, giá nhập 50.000đ | Thành tiền B bằng 100.000đ, tổng phiếu bằng 2.700.000đ. |
| Thêm và lưu dòng B như trên, sau đó xóa A rồi lưu | Phiếu chỉ còn dòng B, tổng phiếu bằng 100.000đ. |
| Đổi nhà cung cấp từ X sang Y | Phiếu tham chiếu Y, dòng A giữ nguyên, tổng phiếu bằng 2.600.000đ. |

### AC-11: Hủy phiếu nháp thành công khi không còn nhà cung cấp đang hợp tác
Given: phiếu P ở trạng thái "Nháp", nhà cung cấp của P đã ngừng hợp tác và không còn nhà cung cấp nào "Đang hợp tác"
When: Nhân viên hủy P
Then: hệ thống mở transaction, khóa dòng P, kiểm tra lại `DRAFT`, chuyển P sang `CANCELLED` rồi commit
And: các thông tin khác của phiếu và các dòng chi tiết không đổi; tồn kho và giá vốn không thay đổi

### AC-12: Không sửa hoặc hủy phiếu không còn nháp
Given: phiếu P ở trạng thái `CANCELLED` hoặc `CONFIRMED`
When: Nhân viên yêu cầu sửa hoặc hủy P, xét độc lập từng thao tác ở mỗi trạng thái
Then: hệ thống kiểm tra lại trạng thái sau khi lấy khóa dòng phiếu và từ chối theo E5
And: phiếu, toàn bộ chi tiết, tồn kho và giá vốn không bị thay đổi bởi yêu cầu bị từ chối

### AC-13: Lỗi hủy phiếu rollback trạng thái
Given: phiếu P ở trạng thái "Nháp" với các dòng chi tiết đã lưu
When: Nhân viên hủy P nhưng gặp lỗi khi ghi trạng thái `CANCELLED` hoặc commit
Then: hệ thống báo lỗi, rollback toàn bộ transaction, không thông báo thành công; P vẫn ở trạng thái `DRAFT`
And: các thông tin khác của phiếu và toàn bộ dòng chi tiết giữ nguyên như trước thao tác; tồn kho và giá vốn không thay đổi
And: khóa dòng phiếu được giữ đến khi rollback kết thúc

### AC-14: Tra cứu phiếu cũ khi không còn nhà cung cấp đang hợp tác
Given: có các phiếu đã lưu và mọi nhà cung cấp đã chuyển sang "Ngừng hợp tác"
When: Nhân viên xem danh sách phiếu nhập hoặc lọc theo trạng thái và nhà cung cấp
Then: hệ thống vẫn hiển thị các phiếu đáp ứng điều kiện lọc, không chặn tra cứu do trạng thái nhà cung cấp
And: dữ liệu phiếu, các dòng chi tiết, tồn kho và giá vốn không thay đổi

## Dependencies
- **Upstream UC:** UC-02, UC-15, UC-32
- **Downstream UC:** UC-34, UC-37
- **External Systems:** không có

## Notes
- Phiếu nháp chưa làm thay đổi tồn kho hay giá vốn; chỉ UC-34 mới thay đổi.
- Sửa/hủy ở UC-33 và xác nhận ở UC-34 phải mở transaction, khóa cùng dòng `inventory.goods_receipt` bằng `SELECT ... FOR UPDATE`, rồi mới kiểm tra lại `DRAFT` trước khi sửa phiếu/chi tiết hoặc chuyển trạng thái. Giữ khóa đến khi commit/rollback; yêu cầu chờ khóa phải dùng trạng thái sau khi lấy được khóa.
- Sửa phiếu, các dòng chi tiết, thành tiền và tổng tiền phải nguyên tử trong cùng transaction; lỗi lưu sửa hoặc hủy rollback toàn bộ, không ảnh hưởng tồn kho hay giá vốn. Kết quả sửa/hủy đồng thời với xác nhận tuân theo AC-13 của UC-34.
- Điều kiện nhà cung cấp "Đang hợp tác" áp dụng khi lập/lưu sửa phiếu; không chặn tra cứu hoặc hủy phiếu nháp cũ. Hậu điều kiện được xét theo từng thao tác và kết quả, không mặc định mọi luồng đều kết thúc ở trạng thái "Nháp".
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách phiếu nhập.

**Quyết định đã chốt**
- Phiếu nhập lưu nhà cung cấp, Nhân viên lập phiếu, ngày tạo, trạng thái, tổng tiền; mỗi dòng chi tiết gồm biến thể, số lượng, đơn giá nhập thực tế, thành tiền (theo ERD).
- Chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (đã chốt 15/11/2026, UC-32).
- Nhà cung cấp ngừng hợp tác không được chọn/lưu trên phiếu; nếu ngừng hợp tác sau khi lập phiếu nháp thì chặn lưu sửa với nhà cung cấp đó. Phiếu nháp cũ đã lưu vẫn được xác nhận qua UC-34 (đã chốt 22/11/2026).
- Giá nhập là số nguyên VND ≥ 0, khớp CHECK `goods_receipt_detail_unit_price >= 0` của data model (đã chốt 21/11/2026).

**Giả định [GD]**
- Phiếu nhập có trạng thái: Nháp → Đã xác nhận | Đã hủy; chỉ sửa và hủy được khi còn "Nháp".
- Mỗi biến thể chỉ xuất hiện một dòng trong một phiếu.
- Danh sách phiếu nhập lọc được theo trạng thái và nhà cung cấp.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): khớp thông tin phiếu nhập và chi tiết phiếu theo ERD
- v3 (2026-11-15): chốt chỉ chọn nhà cung cấp "Đang hợp tác"; thêm AC-6
- v4 (2026-11-21): chốt giá nhập là số nguyên VND không âm, chấp nhận giá nhập bằng 0
- v5 (2026-11-22): đồng bộ khóa dòng phiếu, kiểm tra lại DRAFT và tính nguyên tử khi sửa/hủy với UC-34; mở rộng E5, thêm E6 và AC-7–AC-9; chốt E4 về chặn lưu sửa với nhà cung cấp ngừng hợp tác nhưng vẫn cho xác nhận phiếu nháp cũ
- v6 (2026-11-22): giới hạn điều kiện nhà cung cấp theo thao tác; hoàn thiện hậu điều kiện, xử lý lỗi hủy và AC-10–AC-14 cho sửa/hủy thành công, từ chối phiếu không còn nháp, rollback khi hủy lỗi và tra cứu khi không còn nhà cung cấp đang hợp tác
