# UC-35: Tự cộng lại tồn kho khi giao không thành công

## Metadata
- **ID:** UC-35
- **Module:** inventory
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Hệ thống

## Trigger
Trang giả lập vận chuyển gửi yêu cầu cập nhật đơn sang "Giao không thành công" (nhánh 3c của UC-36).

## Preconditions
- Đơn tồn tại, đang ở trạng thái "Đang giao" (`SHIPPING`); tồn kho đã được trừ khi đặt hàng.
- Các dòng hàng của đơn xác định biến thể và số lượng cần cộng lại từ `ordering.order_detail`.

## Main Flow
1. Service shipping nhận yêu cầu từ UC-36 và gọi service công khai của ordering để chuyển đơn sang "Giao không thành công".
2. Service ordering mở transaction, khóa đơn và kiểm tra lại trạng thái hiện tại là `SHIPPING`. Nếu có yêu cầu đồng thời, chỉ yêu cầu còn thỏa điều kiện này được tiếp tục.
3. Service ordering đọc các dòng hàng đã lưu của đơn và gọi service công khai của inventory, truyền cùng database session và danh sách biến thể, số lượng; không lấy số lượng cộng tồn từ request của Trang giả lập.
4. Service inventory cộng `order_detail_quantity` vào `inventory.stock.stock_quantity` của từng biến thể bằng phép cập nhật tăng tại Database, tránh ghi đè thay đổi tồn kho đồng thời. Giữ nguyên `stock_cost_price` hiện tại; không lấy giá vốn lúc bán để ghi lại giá vốn tồn kho.
5. Trong cùng transaction, service ordering chuyển đơn từ `SHIPPING` sang `DELIVERY_FAILED` và thêm đúng một dòng vào `ordering.order_status_history`: trạng thái cũ `SHIPPING`, trạng thái mới `DELIVERY_FAILED`, nguồn `SHIPPING_SIMULATOR`, người thay đổi `NULL`, thời điểm UTC.
6. Hệ thống commit transaction sau khi tất cả dòng hàng, trạng thái đơn và lịch sử được cập nhật thành công. Chỉ coi commit thành công khi đã nhận xác nhận từ Database; nếu mất kết nối và chưa xác định được kết quả, áp dụng E6.
7. Sau khi xác nhận commit thành công, hệ thống tăng số phiên bản catalog để vô hiệu hóa cache dữ liệu công khai bị ảnh hưởng theo Constraints chung của BR-GIAIDOAN1. Nếu thao tác cache lỗi, áp dụng E5; lỗi này không đổi kết quả nghiệp vụ đã commit.
8. Hệ thống trả kết quả thành công cho UC-36; Trang giả lập làm mới danh sách và không còn hiển thị đơn này. Không cần thao tác nhận hàng hoàn của Nhân viên.

## Alternative Flows
- **4a. Sản phẩm hoặc biến thể đã ngừng bán:** vẫn cộng lại đúng số lượng vào dòng tồn kho hiện có; giữ nguyên giá vốn và trạng thái ngừng bán. Tiếp tục bước 5, không tự bật bán lại.
- **1a. Gửi lại sau lỗi đã rollback:** Trang giả lập gửi lại yêu cầu; hệ thống thực hiện lại từ bước 2. Nếu đơn vẫn là `SHIPPING`, yêu cầu được xử lý bình thường; nếu trạng thái đã đổi bởi yêu cầu khác, áp dụng E1.
- **8a. Mất phản hồi sau khi đã commit:** Trang giả lập chưa nhận được kết quả nên tải lại danh sách / trạng thái đơn. Nếu đơn đã ở `DELIVERY_FAILED`, hiển thị kết quả đã cập nhật và loại đơn khỏi danh sách. Nếu gửi lại yêu cầu đổi trạng thái, áp dụng E1: từ chối thao tác lặp, không cộng tồn hay thêm lịch sử lần nữa; Trang giả lập làm mới theo trạng thái đã lưu.

## Exceptions
- **E1. Đơn không còn ở "Đang giao":** sau khi khóa và kiểm tra lại, trạng thái khác `SHIPPING` (kể cả yêu cầu gửi lại hoặc yêu cầu đồng thời vừa được xử lý) → từ chối; yêu cầu bị từ chối không cộng tồn, không đổi trạng thái và không thêm lịch sử.
- **E2. Lỗi đã xác định transaction không commit:** lỗi khi cộng bất kỳ dòng tồn kho nào, cập nhật trạng thái hoặc ghi lịch sử → rollback toàn bộ transaction. Trường hợp commit bị Database từ chối và đã xác nhận transaction không commit cũng xử lý như vậy. Yêu cầu không để lại thay đổi dở dang; Trang giả lập nhận thông báo cập nhật thất bại và có thể gửi lại. Không áp dụng kết luận rollback cho lỗi mất kết nối có kết quả commit chưa xác định (E6).
- **E3. Đơn không tồn tại:** báo không tìm thấy đơn; không thay đổi dữ liệu.
- **E4. Thiếu dòng tồn kho của biến thể trong đơn:** không bỏ qua dòng hàng và không tự tạo tồn kho với giá vốn mặc định; xử lý như E2 để tránh cập nhật đơn thành công nhưng cộng thiếu hàng.
- **E5. Lỗi tăng phiên bản catalog sau commit:** giữ nguyên kết quả thành công của đơn, tồn kho và lịch sử; tiếp tục bước 8. Hệ thống ghi nhận lỗi và thử lại riêng thao tác tăng phiên bản catalog, không chạy lại luồng cộng tồn. Nếu cache chưa được làm mới, dữ liệu công khai có thể còn cũ cho tới khi thử lại thành công hoặc key cũ hết TTL dự phòng 5 phút theo BR. Màn hình tồn kho và dashboard vẫn đọc Database. Tăng phiên bản nhiều lần do thử lại không được làm thay đổi dữ liệu nghiệp vụ.
- **E6. Chưa xác định kết quả commit:** không thông báo chắc chắn đã rollback và không tự chạy lại cộng tồn. Bỏ session bị lỗi; khi kết nối lại được, service ordering dùng session / transaction mới để khóa và đọc lại đơn từ Database chính, chờ transaction cũ kết thúc trước khi kết luận:
  - Đơn ở `DELIVERY_FAILED`: xác nhận kết quả nghiệp vụ đã được lưu; không cộng tồn hoặc thêm lịch sử. Kết thúc transaction kiểm tra rồi tiếp tục bước 7 để bảo đảm làm mới cache, sau đó trả kết quả đã cập nhật cho UC-36.
  - Đơn vẫn ở `SHIPPING` sau khi transaction cũ đã kết thúc: xác nhận lần cập nhật chưa được lưu; thông báo chưa cập nhật và cho phép gửi lại từ bước 2 với kiểm tra / khóa trạng thái như bình thường.
  - Đơn ở trạng thái khác: áp dụng E1; đơn không tồn tại thì áp dụng E3.
  - Chưa kết nối lại được hoặc chưa xác định được transaction cũ đã kết thúc: Trang giả lập hiển thị "Chưa xác định kết quả cập nhật; vui lòng tải lại trạng thái đơn". Không khẳng định đơn còn `SHIPPING`; lần tải lại / gửi lại sau đó phải đọc và kiểm tra trạng thái đã lưu, không cộng tồn vô điều kiện.

## Postconditions
- Khi thành công: đơn ở `DELIVERY_FAILED`, mỗi biến thể tăng đúng số lượng đã đặt và chỉ có một dòng lịch sử cho lần chuyển trạng thái này.
- Giá vốn hiện tại của từng biến thể, giá vốn chụp trong chi tiết đơn và trạng thái bán của sản phẩm / biến thể không bị thay đổi bởi UC-35; không tính giá trị hàng hoàn.
- Cache dữ liệu công khai bị ảnh hưởng được làm mới theo số phiên bản catalog; nếu lỗi cache sau commit, áp dụng E5 với TTL dự phòng 5 phút. Màn hình tồn kho và dashboard đọc Database theo Constraints chung.
- Khi yêu cầu bị từ chối hoặc transaction rollback: yêu cầu không làm thay đổi tồn kho, trạng thái đơn, lịch sử hay số phiên bản catalog.
- Khi kết quả commit chưa xác định: chưa kết luận thành công / rollback cho tới khi kiểm tra được kết quả đã lưu theo E6; mọi lần kiểm tra hoặc gửi lại đều không được cộng tồn hai lần.

## Acceptance Criteria

### AC-1: Cộng lại tồn kho khi giao không thành công
Given: đơn D có dòng "Áo bơi A – Đỏ – M" số lượng 2, đang ở "Đang giao"; biến thể đang tồn 5, giá vốn 120.000đ
When: Trang giả lập vận chuyển cập nhật đơn D sang "Giao không thành công"
Then: tồn kho của biến thể = 7
And: giá vốn của biến thể vẫn = 120.000đ
And: đơn D ở `DELIVERY_FAILED`
And: lịch sử có thêm đúng một dòng `SHIPPING → DELIVERY_FAILED`, nguồn `SHIPPING_SIMULATOR`, người thay đổi `NULL`, thời điểm UTC
And: không có thao tác nào của Nhân viên

### AC-2: Không cộng hai lần
Given: đơn D đã chuyển sang "Giao không thành công" và đã được cộng lại tồn kho
When: yêu cầu chuyển đơn D sang "Giao không thành công" đến lần nữa
Then: hệ thống từ chối vì đơn D không còn ở "Đang giao"
And: tồn kho không đổi
And: không thêm lịch sử trạng thái

### AC-3: Đơn nhiều dòng
Given: đơn D ở "Đang giao", có biến thể A số lượng 2 đang tồn 5 và biến thể B số lượng 3 đang tồn 0
When: đơn D chuyển sang "Giao không thành công"
Then: tồn kho A = 7 và tồn kho B = 3
And: giá vốn hiện tại của cả hai biến thể không đổi

### AC-4: Lỗi giữa chừng rollback toàn bộ
Given: đơn D ở "Đang giao", có 2 dòng hàng; cập nhật tồn kho dòng đầu thành công trong transaction nhưng dòng thứ hai gặp lỗi
When: Trang giả lập vận chuyển cập nhật đơn D sang "Giao không thành công"
Then: đơn D vẫn ở "Đang giao", tồn kho và giá vốn của cả hai biến thể bằng trước yêu cầu
And: không thêm lịch sử trạng thái, không tăng số phiên bản catalog
And: Trang giả lập nhận thông báo cập nhật thất bại và có thể gửi lại

### AC-5: Hai yêu cầu đồng thời chỉ cộng tồn một lần
Given: đơn D ở "Đang giao", có biến thể A số lượng 2 đang tồn 5
When: hai yêu cầu chuyển D sang "Giao không thành công" đến đồng thời và không có lỗi xử lý
Then: chỉ một yêu cầu thành công; yêu cầu còn lại bị từ chối vì trạng thái không còn là `SHIPPING`
And: đơn D ở `DELIVERY_FAILED`, tồn kho A = 7 và chỉ thêm một dòng lịch sử chuyển trạng thái

### AC-6: Hàng ngừng bán vẫn được cộng tồn
Given: đơn D ở "Đang giao", có biến thể A số lượng 2 đang tồn 5, giá vốn 120.000đ; sản phẩm của A hoặc riêng biến thể A đã ở `INACTIVE`
When: Trang giả lập cập nhật D sang "Giao không thành công"
Then: đơn D ở `DELIVERY_FAILED`, tồn kho A = 7, giá vốn vẫn = 120.000đ
And: trạng thái `INACTIVE` được giữ nguyên; kiểm tra cả trường hợp sản phẩm ngừng bán và trường hợp riêng biến thể ngừng bán

### AC-7: Gửi lại sau rollback có thể thành công
Given: yêu cầu trước của đơn D đã rollback theo E2; D vẫn ở "Đang giao", biến thể A số lượng 2 vẫn tồn 5; lỗi đã được khắc phục
When: Trang giả lập gửi lại yêu cầu "Giao không thành công"
Then: đơn D ở `DELIVERY_FAILED`, tồn kho A = 7 và chỉ thêm một dòng lịch sử chuyển trạng thái

### AC-8: Từ chối trạng thái không hợp lệ
Given: đơn D ở một trong các trạng thái `PENDING`, `CONFIRMED`, `AWAITING_PICKUP`, `DELIVERED`, `DELIVERY_FAILED`, `CANCELLED`
When: Trang giả lập yêu cầu chuyển D sang "Giao không thành công"
Then: hệ thống từ chối với từng trạng thái nêu trên
And: yêu cầu không thay đổi tồn kho, giá vốn, trạng thái đơn hoặc lịch sử

### AC-9: Không tìm thấy đơn
Given: mã đơn D không tồn tại
When: Trang giả lập yêu cầu cập nhật D sang "Giao không thành công"
Then: hệ thống báo không tìm thấy đơn và không thay đổi dữ liệu

### AC-10: Thiếu dòng tồn kho không được cộng thiếu hàng
Given: đơn D ở "Đang giao", có 2 dòng hàng nhưng một biến thể không có dòng `inventory.stock`
When: Trang giả lập cập nhật D sang "Giao không thành công"
Then: hệ thống báo cập nhật thất bại, D vẫn ở "Đang giao"
And: không dòng nào được cộng tồn, không tự tạo dòng tồn kho và không thêm lịch sử

### AC-11: Làm mới cache sau khi cộng tồn thành công
Given: biến thể A của sản phẩm đang bán có tồn kho 0; danh sách sản phẩm công khai đã được cache theo phiên bản catalog hiện tại; đơn D ở "Đang giao" có A số lượng 2
When: yêu cầu "Giao không thành công" của D commit thành công và thao tác tăng phiên bản catalog thành công
Then: hệ thống tăng số phiên bản catalog theo Constraints chung
And: lần đọc danh sách sau khi tăng phiên bản dùng phiên bản mới và phản ánh A còn hàng, không chờ TTL 5 phút của key cũ

### AC-12: Không ghi đè tồn kho khi hai đơn cùng hoàn một biến thể
Given: hai đơn D1 và D2 đều ở "Đang giao", cùng có biến thể A lần lượt số lượng 2 và 3; A đang tồn 5
When: hai đơn được cập nhật "Giao không thành công" đồng thời và cả hai transaction commit thành công
Then: tồn kho A = 10, giá vốn không đổi
And: cả hai đơn ở `DELIVERY_FAILED`, mỗi đơn có đúng một dòng lịch sử chuyển trạng thái

### AC-13: Lỗi ghi lịch sử không để lại tồn kho đã cộng
Given: đơn D ở "Đang giao"; cộng tồn và cập nhật trạng thái trong transaction đã thực hiện nhưng ghi lịch sử gặp lỗi
When: hệ thống xử lý lỗi
Then: toàn bộ transaction rollback; D vẫn ở "Đang giao", tồn kho và giá vốn bằng trước yêu cầu
And: không thêm lịch sử, không tăng số phiên bản catalog và Trang giả lập nhận thông báo cập nhật thất bại

### AC-14: Lỗi cache sau commit không làm thất bại nghiệp vụ
Given: đơn D có biến thể A số lượng 2 đang tồn 5; transaction đã commit D sang `DELIVERY_FAILED`, tồn kho A = 7 và đã ghi một dòng lịch sử; thao tác tăng phiên bản catalog gặp lỗi
When: hệ thống xử lý lỗi cache
Then: Trang giả lập vẫn nhận kết quả cập nhật thành công và D không còn trong danh sách đang giao
And: hệ thống giữ nguyên tồn kho A = 7, giá vốn và dòng lịch sử đã lưu; ghi nhận lỗi để thử lại riêng thao tác tăng phiên bản
And: khi thử lại cache thành công, danh sách công khai dùng phiên bản mới; nếu chưa thành công, key cũ hết hạn theo TTL dự phòng 5 phút
And: thử lại cache, kể cả nhiều lần, không cộng thêm tồn hoặc thêm lịch sử trạng thái

### AC-15: Mất kết nối lúc commit nhưng Database đã lưu thành công
Given: đơn D ở `SHIPPING`, có A số lượng 2 đang tồn 5; Database đã commit D sang `DELIVERY_FAILED`, tồn kho A = 7 và một dòng lịch sử nhưng ứng dụng mất kết nối trước khi nhận xác nhận commit
When: hệ thống kết nối lại bằng session mới và kiểm tra trạng thái theo E6 sau khi transaction cũ kết thúc
Then: hệ thống xác nhận đơn đã cập nhật, thực hiện bước làm mới cache và trả kết quả đã cập nhật cho UC-36
And: không thực hiện lại cộng tồn hoặc ghi lịch sử; tồn kho A vẫn = 7 và chỉ có một dòng lịch sử chuyển trạng thái

### AC-16: Mất kết nối lúc commit và transaction không được lưu
Given: lần cập nhật D mất kết nối lúc commit; sau khi transaction cũ kết thúc, Database xác nhận D vẫn ở `SHIPPING`, tồn kho A vẫn = 5 và chưa có lịch sử chuyển sang `DELIVERY_FAILED`; D có A số lượng 2
When: hệ thống kiểm tra bằng session mới theo E6
Then: hệ thống thông báo chưa cập nhật và cho phép gửi lại với kiểm tra / khóa trạng thái từ bước 2
And: nếu lần gửi lại commit thành công, D ở `DELIVERY_FAILED`, tồn kho A = 7 và chỉ thêm một dòng lịch sử chuyển trạng thái

### AC-17: Chưa thể kiểm tra kết quả commit
Given: ứng dụng mất kết nối lúc commit và chưa thể đọc lại trạng thái đã lưu của D hoặc transaction cũ chưa kết thúc
When: hệ thống phản hồi cho Trang giả lập
Then: hiển thị "Chưa xác định kết quả cập nhật; vui lòng tải lại trạng thái đơn"
And: không khẳng định đã rollback hoặc đã thành công, không tự thực hiện thêm lần cộng tồn nào
And: khi có thể kiểm tra lại, hệ thống phân nhánh theo trạng thái thực tế ở E6

### AC-18: Mất phản hồi rồi gửi lại không cộng tồn hai lần
Given: D đã được commit sang `DELIVERY_FAILED`, tồn kho A đã tăng từ 5 lên 7 và đã ghi một dòng lịch sử nhưng Trang giả lập không nhận được phản hồi
When: Trang giả lập gửi lại yêu cầu "Giao không thành công"
Then: hệ thống từ chối thao tác lặp theo E1 và Trang giả lập tải lại trạng thái đã lưu của D
And: D vẫn ở `DELIVERY_FAILED` và không còn trong danh sách đang giao; tồn kho A vẫn = 7, không thêm lịch sử

## Dependencies
- **Upstream UC:** UC-36
- **Downstream UC:** UC-09, UC-10 (dữ liệu công khai được làm mới cache), UC-12, UC-18, UC-37, UC-39
- **External Systems:** Trang giả lập vận chuyển

## Notes
- Theo BR: đơn giao không thành công thì hệ thống tự cộng lại hàng vào tồn kho, không có thao tác nhận hàng hoàn; giá vốn không đổi; không tính giá trị hàng hoàn.
- Out of Scope: thao tác nhận hàng hoàn thủ công, tính giá trị hàng hoàn.
- UC-35 là xử lý nội bộ trong nhánh giao không thành công của UC-36, không có thao tác hay endpoint cộng tồn riêng.
- Luồng liên module: shipping gọi service ordering; ordering điều phối transaction và gọi service inventory với cùng session. Mỗi module chỉ truy cập repository / bảng do mình sở hữu.
- Theo data model v2, tồn kho và giá vốn hiện tại lưu ở `inventory.stock` (`stock_quantity`, `stock_cost_price`); số lượng cần cộng lấy từ `ordering.order_detail.order_detail_quantity`.
- Giao không thành công chỉ cộng lại tồn kho; không hoàn lượt khuyến mãi như nhánh hủy đơn (theo data model v2), không xuất hóa đơn (UC-26) và không xử lý hoàn tiền trong hệ thống.

**Quyết định đã chốt**
- Không có cột đánh dấu đơn đã cộng lại tồn kho (data model v2 tiếp tục giữ quyết định ngày 15/11/2026). Chống cộng hai lần bằng việc khóa và kiểm tra trạng thái đơn trong transaction; chỉ một lần chuyển `SHIPPING → DELIVERY_FAILED` có hiệu lực, kể cả yêu cầu đồng thời.
- Cộng tồn, đổi trạng thái đơn và ghi lịch sử chạy trong cùng một Database Transaction; service inventory không commit riêng (xử lý giả định ngày 22/11/2026).
- Sản phẩm hoặc biến thể ngừng bán vẫn được cộng lại tồn kho; không tự đổi trạng thái bán (xử lý giả định ngày 22/11/2026).
- Lỗi đã xác định transaction không commit phải rollback toàn bộ và báo thất bại cho Trang giả lập; cho phép gửi lại khi đơn vẫn ở `SHIPPING`. Nếu kết quả commit chưa xác định, kiểm tra lại theo E6 trước khi kết luận (xử lý giả định ngày 22/11/2026, bổ sung cùng ngày).
- Làm mới cache theo phiên bản catalog sau commit; không tăng phiên bản cho yêu cầu bị từ chối hoặc rollback (Constraints chung, bổ sung vào UC ngày 22/11/2026).
- Lỗi cache sau commit không làm thất bại nghiệp vụ đã lưu; ghi nhận lỗi và thử lại riêng thao tác cache, với TTL dự phòng 5 phút theo BR. Không chạy lại cộng tồn để khắc phục lỗi cache (chốt theo yêu cầu xử lý ngày 22/11/2026).
- Mất kết nối lúc commit được xem là kết quả chưa xác định cho tới khi kiểm tra Database bằng session mới sau khi transaction cũ kết thúc; mất phản hồi sau commit không cho phép cộng tồn lần nữa (chốt theo yêu cầu xử lý ngày 22/11/2026).

**Câu hỏi mở / Giả định [GD]**
- Không còn giả định chưa xử lý trong UC-35; ba giả định của bản v2 và hai đề xuất xử lý lỗi cache / kết quả commit chưa xác định đã được đưa vào flow và AC theo yêu cầu ngày 22/11/2026.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo data model v1 — bỏ đánh dấu đơn đã cộng tồn, chống cộng hai lần bằng trạng thái đơn
- v3 (2026-11-22): xử lý ba giả định; hoàn thiện main / alternative flows, exceptions và AC; bổ sung chống yêu cầu đồng thời, rollback lịch sử, làm mới cache và tham chiếu data model v2.
- v4 (2026-11-22): bổ sung E5 / E6 và AC-14 đến AC-18 cho lỗi cache sau commit, kết quả commit chưa xác định và mất phản hồi; điều chỉnh AC-11 và postconditions theo các nhánh lỗi.
