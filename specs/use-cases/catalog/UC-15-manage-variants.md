# UC-15: Quản lý biến thể màu × size

## Metadata
- **ID:** UC-15
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Quản lý Biến thể của một sản phẩm trong portal quản trị.

## Preconditions
- Nhân viên đã đăng nhập hệ thống với vai trò Nhân viên (UC-02).
- Sản phẩm đã tồn tại trong hệ thống (UC-14).
- Đã có ít nhất một giá trị Màu và ít nhất một giá trị Size trong danh mục thuộc tính sản phẩm (UC-17).

## Main Flow
Các thao tác ghi thành công và fixture AC tương ứng trong UC này chỉ áp dụng khi sản phẩm chưa có bất kỳ biến thể nào thuộc phiếu nhập `CONFIRMED`. Nếu đã có, màn hình chỉ xem, vô hiệu hóa Tạo/Xóa/Đổi trạng thái và server bắt buộc kiểm tra lại theo E7; điều kiện tồn kho bằng 0 không gỡ khóa.

1. Hệ thống hiển thị danh sách biến thể hiện có của sản phẩm, gồm:
   - Mã biến thể tự nhiên SKU (`variant_id`, định dạng `<mã SP>-<MÀU>-<SIZE>`).
   - Tên màu (`color_name`).
   - Tên size (`size_name`).
   - Giá bán (`variant_sell_price`): hiển thị số tiền VND hoặc "Chưa có giá".
   - Tồn kho (`stock_quantity`): lấy từ module `inventory` qua Service công khai. Tồn kho chỉ hiển thị để xem, không cho chỉnh sửa trực tiếp trên màn hình này.
   - Trạng thái (`variant_status`): Đang bán (`ACTIVE`) hoặc Ngừng bán (`INACTIVE`).
   - Các nút thao tác trên từng dòng biến thể: Đổi trạng thái (chuyển sang Alternative Flow 1a), Xóa biến thể (chuyển sang Alternative Flow 1b).
2. Hệ thống hiển thị khu vực tạo biến thể: danh sách các màu và danh sách các size có sẵn trong hệ thống (từ UC-17) dưới dạng các ô tích chọn (checkbox).
3. Nhân viên tích chọn một hoặc nhiều màu và tích chọn một hoặc nhiều size cần tạo, sau đó bấm nút "Tạo biến thể".
4. Hệ thống kiểm tra: Nếu không chọn màu hoặc không chọn size, chuyển sang Exception E1.
5. Hệ thống sinh tập hợp các tổ hợp màu × size từ các giá trị đã chọn và thực hiện đánh giá sơ bộ danh sách tổ hợp đối chiếu với dữ liệu hiện có trên màn hình (lưu ý: việc phân loại tổ hợp chính thức bắt buộc được quyết định cuối cùng bên trong Database Transaction sau khi khóa dòng sản phẩm ở bước 6, hệ thống không kết thúc sớm dựa trên dữ liệu đọc trước khi có khóa).
6. Hệ thống mở MỘT Database Transaction duy nhất bao trùm toàn bộ quá trình kiểm tra, tạo lô các biến thể mới và khởi tạo tồn kho tương ứng:
   - Trước khóa sản phẩm, lấy `FOR KEY SHARE` trên toàn bộ Màu/Size được chọn, theo thứ tự tên bảng rồi khóa UUID tăng dần; giữ đến commit/rollback. Nếu đang chờ taxonomy thì chưa giữ khóa sản phẩm. Sau khi được cấp khóa phải đọc tên Màu/Size hiện hành để sinh SKU; mục không còn tồn tại thì rollback và yêu cầu tải lại lựa chọn. Không lấy thêm khóa taxonomy sau khóa sản phẩm.
   - Hệ thống thực hiện khóa dòng sản phẩm cha trong cơ sở dữ liệu (`SELECT * FROM catalog.product WHERE product_key = :product_key FOR UPDATE`) và giữ khóa này cho tới khi transaction kết thúc (commit hoặc rollback) nhằm ngăn chặn xung đột cạnh tranh đồng thời (race condition) với các thao tác cập nhật giá (UC-16), quản lý sản phẩm (UC-14) hoặc tạo biến thể khác.
   - Sau khi có được khóa, gọi Service công khai `inventory` trong cùng transaction kiểm tra phiếu `CONFIRMED` của mọi biến thể thuộc sản phẩm; nếu có thì chuyển E7 trước khi phân loại hoặc ghi bất kỳ tổ hợp nào. Nếu chưa có, hệ thống đọc lại trạng thái hiện tại của sản phẩm (`product_status`), kiểm tra lại danh sách các tổ hợp biến thể hiện có trong cơ sở dữ liệu và đưa ra quyết định phân loại tổ hợp cuối cùng:
     + Nếu sau khi kiểm tra lại nhận thấy toàn bộ tổ hợp đã chọn đều đã tồn tại (hoặc các tổ hợp mới dự kiến tạo vừa được tạo thành công bởi một giao dịch cạnh tranh khác trong lúc chờ khóa): hệ thống chuyển sang Alternative Flow 5b (kết thúc transaction mà không tạo biến thể nào, hiển thị thông báo theo Flow 5b).
     + Nếu có một số tổ hợp đã tồn tại và một số tổ hợp chưa tồn tại: hệ thống chuyển sang xử lý theo Alternative Flow 5a (bỏ qua các tổ hợp đã tồn tại, tiếp tục xử lý các tổ hợp mới chưa có).
   - Hệ thống đọc bảng giá hiện hành theo size của sản phẩm và đối chiếu các tổ hợp mới cần tạo:
     + **Kiểm tra bất biến sản phẩm Đang bán (đồng bộ UC-14):** Nếu sản phẩm cha đang ở trạng thái Đang bán (`product_status = ACTIVE`), hệ thống kiểm tra các size của các tổ hợp mới dự kiến tạo. Nếu trong lô có bất kỳ tổ hợp nào thuộc size chưa có giá bán tại sản phẩm (`variant_sell_price = NULL`), hệ thống từ chối tạo cả lô và chuyển sang Exception E5 (không một biến thể hay bản ghi tồn kho nào trong lô được lưu, các biến thể cũ giữ nguyên).
     + Nếu sản phẩm đang ở trạng thái Ngừng bán (`product_status = INACTIVE`), hệ thống cho phép tạo các biến thể thuộc size chưa có giá và gán `variant_sell_price = NULL`.
     + Với các size đã có giá bán tại sản phẩm, biến thể mới được tự động kế thừa giá hiện hành của size đó (`variant_sell_price` lấy từ giá size mới nhất đọc được trong transaction).
   - Với mỗi tổ hợp màu × size mới hợp lệ cần tạo:
     + Tự động sinh mã biến thể tự nhiên SKU (`variant_id`) theo quy tắc: `<mã SP>-<MÀU>-<SIZE>` (chuẩn hóa viết hoa, loại bỏ dấu tiếng Việt, loại bỏ khoảng trắng; ví dụ: sản phẩm `SP-0001`, màu "Xanh dương", size "M" -> SKU `SP-0001-XANHDUONG-M`).
     + Kiểm tra hợp lệ của SKU sinh ra: Nếu có bất kỳ SKU nào bị trùng với biến thể đã tồn tại trong hệ thống hoặc vượt quá độ dài 60 ký tự (`varchar(60)`), hệ thống hủy bỏ quá trình tạo lô và chuyển sang Exception E4 (toàn bộ transaction bị rollback, không một biến thể hay dòng tồn kho mới nào trong lô được lưu).
     + Thiết lập trạng thái mặc định: `variant_status = ACTIVE` (Đang bán).
     + Tạo bản ghi biến thể mới trong bảng `catalog.variant`.
     + Module `catalog` gọi Service công khai của module `inventory` để khởi tạo bản ghi tồn kho tương ứng trong bảng `inventory.stock` với `stock_quantity = 0` và `stock_cost_price = 0`.
   - Nếu xảy ra lỗi kỹ thuật, lỗi mạng liên module hoặc vi phạm ràng buộc dữ liệu tại bất kỳ tổ hợp nào trong lô: chuyển sang Exception E3 (toàn bộ transaction bị rollback, các tổ hợp đã tồn tại từ trước giữ nguyên không đổi).
7. Sau khi tất cả các tổ hợp mới và các bản ghi tồn kho tương ứng trong lô đều được tạo thành công, hệ thống commit Database Transaction duy nhất này. Ngay sau khi commit thành công, hệ thống thực hiện tăng số phiên bản `catalog_version` trong cache Redis để làm mới dữ liệu storefront (nếu giao dịch DB thất bại/rollback thì tuyệt đối không tăng version; nếu Redis gặp sự cố khi tăng version, hệ thống ghi log cảnh báo warning và vẫn trả kết quả thành công cho Nhân viên, dữ liệu storefront sẽ tự làm mới sau TTL dự phòng 5 phút). Hệ thống làm mới danh sách biến thể trên giao diện và hiển thị thông báo thành công: "Đã tạo thành công {N} biến thể mới".

## Alternative Flows

- **1a. Đổi trạng thái biến thể (Ngừng bán / Bán lại):**
  - Điểm rẽ: Bắt đầu từ nút thao tác tại bước 1 của Main Flow.
  - Điều kiện vào: Nhân viên muốn dừng kinh doanh một biến thể cụ thể (ví dụ hết nguyên liệu màu/size đó) hoặc mở bán lại biến thể đã ngừng bán.
  - Xử lý:
    1. Nhân viên bấm nút "Ngừng bán" (khi biến thể đang `ACTIVE`) hoặc "Bán lại" (khi biến thể đang `INACTIVE`) tại dòng biến thể tương ứng.
    2. Hệ thống mở một Database Transaction, thực hiện khóa dòng sản phẩm cha trong cơ sở dữ liệu (`SELECT * FROM catalog.product WHERE product_key = :product_key FOR UPDATE`) và giữ khóa đến khi commit/rollback (không giữ khóa chờ thao tác bấm của người dùng).
    3. Sau khi giữ khóa, gọi Service công khai `inventory` kiểm tra mọi biến thể của sản phẩm có phiếu `CONFIRMED` hay không; nếu có thì từ chối theo E7. Nếu chưa có, đọc lại trạng thái hiện tại của biến thể và sản phẩm cha, rồi cập nhật trường `variant_status` thành `INACTIVE` hoặc `ACTIVE`.
    4. Hệ thống commit transaction. Ngay sau khi commit thành công, hệ thống tăng số phiên bản `catalog_version` trong Redis để làm mới cache storefront (nếu Redis gặp lỗi thì ghi log warning và tiếp tục; storefront tự làm mới sau TTL 5 phút). Hệ thống làm mới trạng thái trên giao diện và hiển thị thông báo: "Cập nhật trạng thái biến thể thành công".
  - Tác động storefront: Biến thể ở trạng thái `INACTIVE` (Ngừng bán) không bị ẩn khỏi các lựa chọn trên storefront; tùy chọn của tổ hợp màu × size không bán này vẫn được hiển thị nhưng bị vô hiệu hóa (`disabled`), không cho khách hàng chọn mua (nhất quán với UC-12). Hệ thống không vô hiệu hóa toàn bộ màu hoặc size nếu vẫn còn tổ hợp `ACTIVE` hợp lệ khác.

- **1b. Xóa biến thể:**
  - Điểm rẽ: Bắt đầu từ nút thao tác tại bước 1 của Main Flow.
  - Điều kiện vào: Nhân viên bấm nút "Xóa" tại dòng biến thể cần xóa. Hệ thống hiển thị hộp thoại xác nhận xóa.
  - Xử lý:
    1. Nhân viên xác nhận xóa trên hộp thoại.
    2. Trong cùng một Database Transaction:
       - Hệ thống thực hiện khóa dòng sản phẩm cha trong cơ sở dữ liệu (`SELECT * FROM catalog.product WHERE product_key = :product_key FOR UPDATE`) và giữ khóa đến khi commit/rollback.
       - Sau khi giữ khóa, hệ thống kiểm tra các điều kiện ràng buộc:
         + Nếu bất kỳ biến thể nào của sản phẩm cha thuộc phiếu nhập `CONFIRMED`, từ chối theo E7, kể cả biến thể đang yêu cầu xóa chưa từng nhập kho.
         + **Kiểm tra bất biến sản phẩm Đang bán (đồng bộ UC-14):** Nếu sản phẩm cha đang ở trạng thái Đang bán (`product_status = ACTIVE`), hệ thống đếm tổng số biến thể hiện có của sản phẩm. Nếu biến thể yêu cầu xóa là biến thể duy nhất còn lại của sản phẩm (xóa xong sản phẩm sẽ có 0 biến thể, vi phạm điều kiện duy trì ACTIVE của UC-14), hệ thống từ chối xóa và chuyển sang Exception E6.
         + Biến thể còn tồn kho (`stock_quantity > 0` từ module `inventory` qua Service công khai)? -> Chuyển sang Exception E2.
         + Biến thể đã từng có trong ít nhất một phiếu nhập (`inventory.goods_receipt_detail` qua Service công khai)? -> Chuyển sang Exception E2.
         + Biến thể đã từng có trong ít nhất một đơn hàng (`ordering.order_detail` qua Service công khai)? -> Chuyển sang Exception E2.
       - Khi thỏa mãn tất cả các điều kiện trên:
         + Module `catalog` gọi Service công khai của module `inventory` để xóa bản ghi `stock` liên kết của biến thể.
         + Module `catalog` xóa bản ghi biến thể trong bảng `catalog.variant` (các dòng trong `shopping.cart_item` nếu có sẽ tự động xóa theo ràng buộc cascade).
    3. Nếu quá trình xóa gặp lỗi kỹ thuật hoặc lỗi liên module: chuyển sang Exception E3 (toàn bộ transaction bị rollback, dữ liệu `stock` và `variant` được bảo toàn nguyên trạng).
    4. Hệ thống commit hoàn tất transaction. Ngay sau khi commit thành công, hệ thống tăng số phiên bản `catalog_version` trong Redis để làm mới cache storefront (nếu Redis gặp lỗi thì ghi log warning và tiếp tục; storefront tự làm mới sau TTL 5 phút). Hệ thống cập nhật lại danh sách biến thể trên giao diện và hiển thị thông báo: "Xóa biến thể thành công".

- **5a. Một số tổ hợp đã tồn tại:**
  - Điểm rẽ: Bắt đầu từ bước 5 (đánh giá sơ bộ) và được quyết định chính thức tại bước 6 của Main Flow sau khi có khóa sản phẩm cha.
  - Điều kiện vào: Tập hợp tổ hợp màu × size chọn ở bước 3 có cả tổ hợp mới và tổ hợp đã tồn tại trong sản phẩm.
  - Xử lý:
    1. Trong Database Transaction tại bước 6, hệ thống bỏ qua các tổ hợp đã tồn tại (giữ nguyên không thay đổi), chỉ thực hiện tạo các tổ hợp mới theo quy trình kiểm tra bất biến, sinh SKU và tạo bản ghi tồn kho.
    2. Chuyển sang bước 7 của Main Flow nhưng hiển thị thông báo kết hợp: "Đã tạo {X} biến thể mới, bỏ qua {Y} tổ hợp đã tồn tại".

- **5b. Toàn bộ tổ hợp đã chọn đều đã tồn tại:**
  - Điểm rẽ: Bắt đầu từ bước 5 (đánh giá sơ bộ) và được quyết định chính thức tại bước 6 của Main Flow sau khi có khóa sản phẩm cha (bao gồm trường hợp sau khi chờ khóa, đối chiếu lại thì không còn tổ hợp mới nào do giao dịch khác vừa tạo).
  - Điều kiện vào: Tất cả tổ hợp màu × size do Nhân viên chọn đều đã có biến thể tương ứng trong sản phẩm.
  - Xử lý:
    1. Hệ thống kết thúc transaction (commit hoặc giải phóng khóa mà không ghi dữ liệu mới), không tạo mới biến thể nào, giữ nguyên danh sách hiện tại.
    2. Hiển thị thông báo: "Tất cả các tổ hợp màu × size đã chọn đều đã tồn tại". Luồng tạo biến thể kết thúc.

## Exceptions

- **E7. Sản phẩm đã nhập kho chỉ được sửa Mô tả:** Sau khóa sản phẩm, Service inventory xác nhận có phiếu `CONFIRMED` thì chặn tạo cả lô, xóa hoặc đổi trạng thái bất kỳ biến thể nào của sản phẩm; báo "Sản phẩm đã nhập kho, chỉ được phép sửa mô tả". Rollback toàn bộ request, giữ nguyên variant/stock và không tăng `catalog_version`, kể cả request trực tiếp hoặc form đã mở trước lúc xác nhận nhập kho (UC-14-Q11).

- **E1. Không chọn màu hoặc không chọn size:**
  - Điểm rẽ: Bắt đầu từ bước 4 của Main Flow.
  - Điều kiện: Nhân viên bấm "Tạo biến thể" nhưng chưa chọn màu nào, hoặc chưa chọn size nào, hoặc không chọn cả hai.
  - Xử lý: Hệ thống không thực hiện tạo biến thể và hiển thị thông báo lỗi:
    - Nếu chưa chọn màu: "Vui lòng chọn ít nhất một màu".
    - Nếu chưa chọn size: "Vui lòng chọn ít nhất một size".
    - Nếu chưa chọn cả hai: "Vui lòng chọn ít nhất một màu và một size".

- **E2. Xóa biến thể không thành công (còn tồn kho hoặc đã phát sinh giao dịch):**
  - Điểm rẽ: Bắt đầu từ bước 2 của Alternative Flow 1b.
  - Điều kiện: Nhân viên yêu cầu xóa biến thể nhưng biến thể không thỏa mãn điều kiện xóa.
  - Xử lý: Hệ thống từ chối xóa, rollback transaction nếu đang mở, giữ nguyên dữ liệu và hiển thị thông báo lỗi cụ thể:
    - Nếu biến thể còn tồn kho (`stock_quantity > 0`): "Không thể xóa biến thể còn tồn kho (số lượng tồn: {stock_quantity})".
    - Nếu biến thể đã phát sinh đơn hàng hoặc phiếu nhập: "Không thể xóa biến thể đã phát sinh đơn hàng hoặc phiếu nhập". Nếu đã có phiếu CONFIRMED thì ưu tiên E7, không gợi ý đổi trạng thái.

- **E3. Lỗi giao dịch hệ thống hoặc lỗi liên module:**
  - Điểm rẽ: Xảy ra tại bước 6 của Main Flow (khi tạo lô biến thể và gọi `inventory` tạo `stock`), hoặc bước 2/3 của Alternative Flow 1b (khi gọi `inventory` xóa `stock` và xóa `variant`).
  - Điều kiện: Xảy ra sự cố kết nối giữa các module, timeout, lỗi cơ sở dữ liệu hoặc một trong các thao tác (`stock` hoặc `variant`) trong transaction thất bại.
  - Xử lý:
    1. Toàn bộ Database Transaction bị rollback ngay lập tức.
    2. Đảm bảo dữ liệu không bị sai lệch hoặc mồ côi một phía (không có `variant` mà thiếu `stock`, và ngược lại; không lưu một phần lô khi tạo hàng loạt).
    3. Hệ thống hiển thị thông báo lỗi: "Thao tác không thành công do lỗi hệ thống. Dữ liệu đã được khôi phục, vui lòng thử lại sau".

- **E4. Trùng mã SKU hoặc mã SKU vượt độ dài quy định:**
  - Điểm rẽ: Bắt đầu từ bước 6 của Main Flow.
  - Điều kiện: Trong lô các tổ hợp cần tạo, có ít nhất một mã SKU sinh ra `<mã SP>-<MÀU>-<SIZE>` bị trùng với mã SKU đã tồn tại trong hệ thống (do tên màu/size khác nhau nhưng sau khi chuẩn hóa bỏ dấu/khoảng trắng thì trùng nhau), hoặc tổng độ dài chuỗi SKU vượt quá 60 ký tự (`varchar(60)`).
  - Xử lý: Hệ thống rollback toàn bộ Database Transaction của cả lô tạo biến thể (không lưu bất kỳ biến thể hay bản ghi stock mới nào trong lô; các tổ hợp đã tồn tại từ trước giữ nguyên), không tự ý cắt ngắn hoặc thêm hậu tố ngẫu nhiên, và hiển thị thông báo lỗi: "Mã SKU sinh ra ({variant_id}) đã tồn tại hoặc vượt quá độ dài tối đa 60 ký tự. Vui lòng kiểm tra lại tên thuộc tính tại Quản lý thuộc tính (UC-17)".

- **E5. Chặn tạo biến thể thuộc size chưa có giá khi sản phẩm Đang bán (đồng bộ UC-14):**
  - Điểm rẽ: Bắt đầu từ bước 6 của Main Flow.
  - Điều kiện: Sản phẩm cha đang ở trạng thái Đang bán (`product_status = ACTIVE`), nhưng trong lô biến thể mới cần tạo có ít nhất một tổ hợp thuộc size chưa có giá bán tại sản phẩm (`variant_sell_price = NULL`).
  - Xử lý: Hệ thống từ chối tạo biến thể, rollback toàn bộ transaction của cả lô (không lưu bất kỳ biến thể hay bản ghi tồn kho nào trong lô; các biến thể đã tồn tại giữ nguyên), và hiển thị thông báo lỗi: "Sản phẩm đang Đang bán, không thể thêm biến thể thuộc size chưa có giá bán. Vui lòng chuyển sản phẩm sang Ngừng bán tại Quản lý sản phẩm (UC-14) trước khi bổ sung size mới, hoặc chỉ chọn tạo biến thể cho các size đã có giá".

- **E6. Chặn xóa biến thể cuối cùng khi sản phẩm Đang bán (đồng bộ UC-14):**
  - Điểm rẽ: Bắt đầu từ bước 2 của Alternative Flow 1b.
  - Điều kiện: Sản phẩm cha đang ở trạng thái Đang bán (`product_status = ACTIVE`) và biến thể yêu cầu xóa là biến thể duy nhất còn lại của sản phẩm.
  - Xử lý: Hệ thống từ chối xóa, rollback transaction, và hiển thị thông báo lỗi: "Không thể xóa biến thể duy nhất còn lại khi sản phẩm đang Đang bán. Vui lòng chuyển sản phẩm sang Ngừng bán tại Quản lý sản phẩm (UC-14) trước khi xóa".

## Postconditions
- Danh sách biến thể của sản phẩm được cập nhật theo thao tác tương ứng (thêm mới cả lô, đổi trạng thái, hoặc xóa).
- Biến thể mới được lưu vào `catalog.variant` với mã SKU tự nhiên chuẩn hóa, trạng thái `ACTIVE`, giá theo size (nếu có), và bản ghi tồn kho tương ứng trong `inventory.stock` với `stock_quantity = 0`, `stock_cost_price = 0`.
- Mỗi tổ hợp màu × size là duy nhất trong phạm vi sản phẩm (`UNIQUE (variant_product_key, variant_size_key, variant_color_key)`).

## Acceptance Criteria

### AC-1: Tạo biến thể theo tổ hợp màu × size và khởi tạo tồn kho
Given: sản phẩm "SP-0001" đang ở trạng thái Ngừng bán (`INACTIVE`) và chưa có biến thể nào
When: Nhân viên chọn màu "Đỏ", "Xanh" và size "S", "M" rồi bấm "Tạo biến thể"
Then: hệ thống mở một transaction, khóa sản phẩm cha, và tạo 4 biến thể mới: Đỏ×S, Đỏ×M, Xanh×S, Xanh×M
And: trạng thái mỗi biến thể là "ACTIVE" (Đang bán)
And: trong module inventory, hệ thống khởi tạo bản ghi tồn kho cho mỗi biến thể với số lượng tồn = 0 và giá vốn = 0
And: transaction được commit và hệ thống thông báo "Đã tạo thành công 4 biến thể mới"

### AC-2: Sinh mã SKU tự nhiên chuẩn hóa
Given: sản phẩm có mã "SP-0001"
When: hệ thống tạo biến thể cho màu "Xanh dương" và size "L"
Then: mã biến thể SKU `variant_id` được sinh tự động là "SP-0001-XANHDUONG-L" (viết hoa, không dấu, không khoảng trắng)

### AC-3: Thừa hưởng giá bán của size đã có giá
Given: sản phẩm "SP-0001" đã có biến thể Đỏ×M với giá bán 320.000đ (size M đã có giá)
When: Nhân viên chọn tạo thêm biến thể màu "Đen" và size "M"
Then: hệ thống tạo biến thể Đen×M với `variant_sell_price` tự động bằng 320.000đ

### AC-4: Biến thể mới khi size chưa có giá bán (sản phẩm Ngừng bán)
Given: sản phẩm "SP-0001" đang ở trạng thái Ngừng bán (`product_status = INACTIVE`), chưa từng có biến thể nào thuộc size "XL" (size XL chưa có giá)
When: Nhân viên chọn tạo biến thể màu "Đen" và size "XL"
Then: biến thể Đen×XL được tạo với `variant_sell_price = NULL`
And: trên giao diện quản trị, cột giá hiển thị "Chưa có giá"

### AC-5: Bỏ qua tổ hợp trùng và tạo tổ hợp mới (Flow 5a)
Given: sản phẩm "SP-0001" đã có biến thể Đỏ×S với giá 300.000đ
When: Nhân viên chọn màu "Đỏ" và size "S", "L" rồi bấm "Tạo biến thể" (giả định size L đã có giá hoặc sản phẩm đang INACTIVE)
Then: hệ thống chỉ tạo thêm 1 biến thể mới là Đỏ×L trong transaction
And: biến thể Đỏ×S đã có từ trước giữ nguyên dữ liệu hiện tại
And: hệ thống thông báo "Đã tạo 1 biến thể mới, bỏ qua 1 tổ hợp đã tồn tại"

### AC-6: Toàn bộ tổ hợp chọn đã tồn tại (Flow 5b)
Given: sản phẩm "SP-0001" đã có đầy đủ biến thể Đỏ×S và Đỏ×M
When: Nhân viên chọn màu "Đỏ" và size "S", "M" rồi bấm "Tạo biến thể"
Then: hệ thống không tạo thêm biến thể nào
And: hệ thống thông báo "Tất cả các tổ hợp màu × size đã chọn đều đã tồn tại"

### AC-7: Thiếu màu hoặc thiếu size khi tạo (Exception E1)
Given: Nhân viên đang ở màn hình tạo biến thể của sản phẩm "SP-0001"
When: Nhân viên chọn màu "Đỏ" nhưng không chọn size nào rồi bấm "Tạo biến thể"
Then: hệ thống không tạo biến thể và hiển thị thông báo lỗi "Vui lòng chọn ít nhất một size"

### AC-8: Tồn kho hiển thị chỉ xem, không cho sửa tay
Given: Nhân viên xem danh sách biến thể của sản phẩm "SP-0001"
When: Nhân viên xem cột tồn kho của biến thể Đỏ×M
Then: hệ thống hiển thị số lượng tồn kho hiện tại (đọc từ module inventory) dưới dạng văn bản chỉ xem (read-only)
And: không có ô nhập liệu hoặc điều khiển nào cho phép sửa trực tiếp tồn kho tại màn hình này

### AC-9: Chuyển trạng thái biến thể sang Ngừng bán (INACTIVE - Flow 1a)
Given: biến thể Đỏ×M đang ở trạng thái "ACTIVE" (Đang bán)
When: Nhân viên bấm nút "Ngừng bán" tại biến thể Đỏ×M
Then: trạng thái của biến thể Đỏ×M chuyển thành "INACTIVE"
And: hệ thống thông báo "Cập nhật trạng thái biến thể thành công"
And: trên trang chi tiết sản phẩm của storefront (UC-12), tùy chọn tương ứng với tổ hợp Đỏ×M vẫn hiển thị nhưng bị vô hiệu hóa (disabled), không cho khách hàng chọn mua

### AC-10: Mở bán lại biến thể đã ngừng bán (ACTIVE - Flow 1a)
Given: biến thể Đỏ×M đang ở trạng thái "INACTIVE" (Ngừng bán)
When: Nhân viên bấm nút "Bán lại" tại biến thể Đỏ×M
Then: trạng thái của biến thể Đỏ×M chuyển thành "ACTIVE"
And: hệ thống thông báo "Cập nhật trạng thái biến thể thành công"
And: trên trang chi tiết sản phẩm của storefront (UC-12), tổ hợp Đỏ×M được kích hoạt lại cho phép người dùng lựa chọn theo điều kiện giá và tồn kho hiện hành (trạng thái ACTIVE không tự bảo đảm còn hàng)

### AC-11: Chặn xóa biến thể đã nhập còn tồn kho (Exception E7)
Given: biến thể Đỏ×M thuộc phiếu CONFIRMED và có tồn kho = 5 (lấy từ module inventory)
When: Nhân viên bấm xóa biến thể Đỏ×M và xác nhận
Then: hệ thống từ chối xóa và hiển thị thông báo "Sản phẩm đã nhập kho, chỉ được phép sửa mô tả"
And: biến thể Đỏ×M vẫn tồn tại trong danh sách

### AC-12: Chặn xóa biến thể đã nhập và có đơn hàng (Exception E7)
Given: biến thể Đỏ×M thuộc phiếu CONFIRMED, có tồn kho = 0 nhưng đã từng có trong ít nhất một đơn hàng
When: Nhân viên bấm xóa biến thể Đỏ×M và xác nhận
Then: hệ thống từ chối xóa và hiển thị thông báo "Sản phẩm đã nhập kho, chỉ được phép sửa mô tả"
And: biến thể Đỏ×M vẫn tồn tại trong danh sách

### AC-13: Chặn xóa biến thể đã có trong phiếu nhập (Exception E2)
Given: biến thể Xanh×L có tồn kho = 0, chưa có trong đơn hàng nào, nhưng đã liên kết phiếu nhập DRAFT; toàn bộ sản phẩm chưa có phiếu CONFIRMED
When: Nhân viên bấm xóa biến thể Xanh×L và xác nhận
Then: hệ thống từ chối xóa và hiển thị thông báo lỗi "Không thể xóa biến thể đã phát sinh đơn hàng hoặc phiếu nhập"
And: biến thể Xanh×L vẫn tồn tại trong danh sách

### AC-14: Xóa biến thể hợp lệ và dọn bản ghi tồn kho liên kết (Flow 1b)
Given: sản phẩm "SP-0001" có nhiều biến thể; biến thể Vàng×S có tồn kho = 0, chưa từng có trong đơn hàng và chưa từng có trong phiếu nhập nào
When: Nhân viên bấm xóa biến thể Vàng×S và xác nhận
Then: trong cùng một Database Transaction có khóa sản phẩm cha, hệ thống xóa bản ghi tồn kho liên kết trong bảng `inventory.stock` qua Service của inventory, sau đó xóa bản ghi biến thể Vàng×S khỏi bảng `catalog.variant`
And: nếu có dòng chứa biến thể Vàng×S trong giỏ hàng (`shopping.cart_item`), dòng đó tự động bị xóa theo cascade
And: hệ thống hiển thị thông báo "Xóa biến thể thành công"

### AC-15: Toàn vẹn Transaction khi khởi tạo biến thể thất bại ở module inventory (Exception E3)
Given: Nhân viên thực hiện tạo biến thể mới Đỏ×XL
When: quá trình ghi bản ghi biến thể `catalog.variant` hoàn tất nhưng cuộc gọi khởi tạo tồn kho sang module `inventory` gặp lỗi
Then: toàn bộ transaction bị rollback ngay lập tức
And: biến thể Đỏ×XL không được lưu trong bảng `catalog.variant`
And: số phiên bản `catalog_version` trong Redis không bị tăng (giữ nguyên giá trị hiện hành)
And: hệ thống hiển thị thông báo lỗi "Thao tác không thành công do lỗi hệ thống. Dữ liệu đã được khôi phục, vui lòng thử lại sau"

### AC-16: Toàn vẹn Transaction khi xóa biến thể gặp lỗi dọn tồn kho (Exception E3)
Given: biến thể Vàng×S đủ điều kiện xóa (tồn kho = 0, không có đơn hàng hay phiếu nhập, không phải biến thể cuối cùng khi sản phẩm ACTIVE)
When: Nhân viên xác nhận xóa nhưng cuộc gọi xóa bản ghi `stock` tại module inventory gặp sự cố
Then: toàn bộ transaction bị rollback ngay lập tức
And: bản ghi biến thể Vàng×S trong `catalog.variant` và bản ghi tồn kho trong `inventory.stock` đều được giữ nguyên
And: số phiên bản `catalog_version` trong Redis không bị tăng (giữ nguyên giá trị hiện hành)
And: hệ thống hiển thị thông báo lỗi "Thao tác không thành công do lỗi hệ thống. Dữ liệu đã được khôi phục, vui lòng thử lại sau"

### AC-17: Xử lý lỗi trùng mã SKU hoặc vượt quá độ dài trong lô (Exception E4)
Given: sản phẩm "SP-0001" đã có biến thể ứng với màu "Xanh dương" và size "M" (SKU "SP-0001-XANHDUONG-M")
When: Nhân viên chọn 2 màu "Đen", "Xanhduong" và 1 size "M" rồi bấm "Tạo biến thể" (tạo lô gồm 2 tổ hợp: Đen×M hợp lệ và "Xanhduong"×M bị trùng SKU với Xanh dương×M sau khi chuẩn hóa, hoặc tên thuộc tính khiến SKU vượt 60 ký tự)
Then: hệ thống từ chối tạo biến thể và rollback toàn bộ Database Transaction của cả lô
And: không có bất kỳ biến thể hay bản ghi stock mới nào được lưu vào hệ thống (biến thể hợp lệ Đen×M cũng không được tạo)
And: biến thể đã tồn tại từ trước (Xanh dương×M) giữ nguyên dữ liệu
And: số phiên bản `catalog_version` trong Redis không bị tăng (giữ nguyên giá trị hiện hành)
And: hệ thống hiển thị thông báo lỗi "Mã SKU sinh ra (SP-0001-XANHDUONG-M) đã tồn tại hoặc vượt quá độ dài tối đa 60 ký tự. Vui lòng kiểm tra lại tên thuộc tính tại Quản lý thuộc tính (UC-17)"

### AC-18: Phân quyền truy cập quản lý biến thể
Given: người dùng đăng nhập với vai trò Khách hàng (hoặc Khách vãng lai chưa đăng nhập)
When: người dùng cố gắng truy cập màn hình hoặc gửi yêu cầu API quản lý biến thể sản phẩm
Then: hệ thống từ chối truy cập và chuyển hướng về trang phù hợp

### AC-19: Chặn tạo lô biến thể có size chưa có giá khi sản phẩm Đang bán (Exception E5, đồng bộ UC-14)
Given: sản phẩm "SP-0001" đang ở trạng thái Đang bán (`product_status = ACTIVE`), đã có size M (giá 320.000đ), chưa có size XL (chưa có giá)
When: Nhân viên chọn màu "Đỏ", "Đen" và size "M", "XL" rồi bấm "Tạo biến thể" (lô gồm: Đen×M hợp lệ có giá kế thừa 320.000đ, và Đỏ×XL, Đen×XL thuộc size XL chưa có giá)
Then: hệ thống từ chối tạo biến thể và rollback toàn bộ Database Transaction của cả lô
And: không có bất kỳ biến thể hay bản ghi tồn kho mới nào được lưu vào hệ thống (kể cả Đen×M cũng không được tạo)
And: các biến thể đã có từ trước (Đỏ×M) giữ nguyên dữ liệu
And: số phiên bản `catalog_version` trong Redis không bị tăng (giữ nguyên giá trị hiện hành)
And: hệ thống hiển thị thông báo lỗi "Sản phẩm đang Đang bán, không thể thêm biến thể thuộc size chưa có giá bán. Vui lòng chuyển sản phẩm sang Ngừng bán tại Quản lý sản phẩm (UC-14) trước khi bổ sung size mới, hoặc chỉ chọn tạo biến thể cho các size đã có giá"

### AC-20: Cho phép thêm màu mới cho size đã có giá khi sản phẩm Đang bán
Given: sản phẩm "SP-0001" đang ở trạng thái Đang bán (`product_status = ACTIVE`), đã có biến thể Đỏ×M với giá 320.000đ
When: Nhân viên chọn màu "Đen" và size "M" rồi bấm "Tạo biến thể"
Then: hệ thống tạo thành công biến thể Đen×M với `variant_sell_price` tự động bằng 320.000đ và `variant_status = ACTIVE`
And: sản phẩm "SP-0001" vẫn giữ nguyên trạng thái Đang bán (`ACTIVE`)
And: hệ thống thông báo "Đã tạo thành công 1 biến thể mới"

### AC-21: Chặn xóa biến thể cuối cùng khi sản phẩm Đang bán (Exception E6, đồng bộ UC-14)
Given: sản phẩm "SP-0001" đang ở trạng thái Đang bán (`product_status = ACTIVE`), chỉ còn đúng 1 biến thể duy nhất là Đỏ×M (tồn kho = 0, chưa có đơn hàng hay phiếu nhập)
When: Nhân viên bấm xóa biến thể Đỏ×M và xác nhận
Then: hệ thống từ chối xóa và rollback transaction
And: biến thể Đỏ×M vẫn tồn tại trong danh sách
And: số phiên bản `catalog_version` trong Redis không bị tăng (giữ nguyên giá trị hiện hành)
And: hệ thống hiển thị thông báo lỗi "Không thể xóa biến thể duy nhất còn lại khi sản phẩm đang Đang bán. Vui lòng chuyển sản phẩm sang Ngừng bán tại Quản lý sản phẩm (UC-14) trước khi xóa"

### AC-22: Đồng bộ cạnh tranh giữa tạo biến thể kế thừa giá (UC-15) và cập nhật giá size (UC-16)
Given: sản phẩm "SP-0001" đang có biến thể Đỏ×M với giá 320.000đ
When: Transaction T1 (UC-15 tạo biến thể Đen×M) và Transaction T2 (UC-16 cập nhật giá size M thành 350.000đ) gửi yêu cầu đồng thời
Then: nhờ cơ chế khóa `SELECT ... FROM catalog.product WHERE product_key = :product_key FOR UPDATE`:
  - Trường hợp 1 (T1 giữ khóa trước): T1 đọc giá size M là 320.000đ, tạo Đen×M với giá 320.000đ rồi commit (tại thời điểm trung gian này cả Đỏ×M và Đen×M đều đồng nhất giá 320.000đ); sau đó T2 có khóa, đọc và cập nhật giá size M thành 350.000đ cho cả Đỏ×M và Đen×M rồi commit -> kết quả cả hai biến thể đều có giá 350.000đ
  - Trường hợp 2 (T2 giữ khóa trước): T2 cập nhật giá size M cho Đỏ×M thành 350.000đ rồi commit; sau đó T1 có khóa, đọc lại giá size M thấy 350.000đ và tạo Đen×M với giá 350.000đ rồi commit -> kết quả cả hai biến thể đều có giá 350.000đ
And: sau khi CẢ HAI transaction đều hoàn tất commit, mọi biến thể cùng size M đều có mức giá mới 350.000đ; đồng thời trong toàn bộ các thời điểm trung gian, các biến thể cùng size M luôn đảm bảo đồng nhất mức giá bán với nhau (tuân thủ tuyệt đối BR-002)

### AC-23: Làm mới cache storefront sau khi thay đổi biến thể thành công
Given: hệ thống storefront đang cache danh mục và chi tiết sản phẩm "SP-0001" theo số phiên bản `catalog_version` = 10 trong Redis
When: Nhân viên thực hiện một thao tác ghi biến thể (tạo biến thể mới, xóa biến thể, hoặc đổi trạng thái ACTIVE ↔ INACTIVE) và Database Transaction commit thành công
Then: hệ thống thực hiện tăng số phiên bản `catalog_version` lên 11 trong Redis
And: các lượt truy cập storefront tiếp theo nhận diện phiên bản mới và tải lại dữ liệu biến thể mới nhất từ cơ sở dữ liệu

### AC-24: Xử lý ngoại lệ kỹ thuật Redis khi làm mới cache
Given: Nhân viên thực hiện thao tác thay đổi biến thể (tạo mới, xóa, hoặc đổi trạng thái) và Database Transaction đã commit thành công vào PostgreSQL
When: hệ thống gọi cập nhật tăng `catalog_version` sang Redis nhưng Redis bị mất kết nối hoặc phản hồi lỗi
Then: hệ thống ghi nhận log cảnh báo (warning log) về sự cố Redis
And: cơ sở dữ liệu PostgreSQL giữ đúng thay đổi đã commit, tuyệt đối không bị rollback khi gặp lỗi Redis
And: hệ thống vẫn trả về kết quả thành công cho Nhân viên trên portal quản trị kèm thông báo tương ứng với thao tác
And: dữ liệu cache cũ trên storefront chỉ được làm mới ở lần truy cập sau khi hết khoảng thời gian TTL dự phòng còn lại tối đa 5 phút hoặc khi có lần tăng `catalog_version` thành công tiếp theo

### AC-25: Có phiếu CONFIRMED khóa toàn bộ biến thể của sản phẩm
Given: A có Đỏ×M thuộc phiếu CONFIRMED và Xanh×L chưa từng nhập; tồn kho cả hai đã về 0, các điều kiện tạo/xóa/đổi trạng thái khác đều hợp lệ
When: Nhân viên lần lượt gửi request tạo cả lô gồm tổ hợp mới, xóa Xanh×L, ngừng bán hoặc bán lại một biến thể
Then: mọi request đều bị từ chối theo E7 sau kiểm tra lại dưới khóa sản phẩm, không có lô được tạo một phần
And: toàn bộ variant, giá, trạng thái và stock giữ nguyên, không tăng catalog_version; nút ghi trên màn hình bị vô hiệu hóa
And: phiếu chỉ DRAFT/CANCELLED chưa kích hoạt E7, nhưng điều kiện chặn xóa do từng liên kết phiếu nhập vẫn áp dụng

## Dependencies
- **Upstream UC:**
  - UC-02 Đăng nhập (xác thực quyền Nhân viên vận hành).
  - UC-14 Quản lý sản phẩm (sản phẩm cha chứa các biến thể; đồng bộ điều kiện duy trì trạng thái ACTIVE).
  - UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính (cung cấp danh mục các giá trị Màu và Size).
- **Downstream UC:**
  - UC-10 Xem sản phẩm theo danh mục (lọc sản phẩm theo size biến thể).
  - UC-12 Xem chi tiết sản phẩm (hiển thị màu, size, tình trạng còn/hết hàng; hiển thị vô hiệu hóa các tổ hợp `INACTIVE`).
  - UC-14 Quản lý sản phẩm (điều kiện chuyển Đang bán: sản phẩm phải có ít nhất một biến thể và mọi size đều có giá).
  - UC-16 Quản lý giá bán theo size (thiết lập hoặc cập nhật giá `variant_sell_price` cho các biến thể theo size; chia sẻ cơ chế khóa chống race condition).
  - UC-18 Quản lý giỏ hàng (khách hàng chọn biến thể thêm vào giỏ; kiểm tra trực tiếp trạng thái và tồn kho từ Database chống stale cache, đã đồng bộ đặc tả ngày 23/11/2026 theo phê duyệt Codex).
  - UC-19 / UC-20 Đặt hàng và thanh toán (kiểm tra trực tiếp trạng thái biến thể ACTIVE và tồn kho từ Database chống stale cache, đã đồng bộ đặc tả ngày 23/11/2026 theo phê duyệt Codex).
  - UC-33 Lập phiếu nhập (chọn biến thể để tạo dòng phiếu nhập).
  - UC-34 Xác nhận phiếu nhập (cộng tồn kho theo biến thể trong `inventory.stock`).
  - UC-39 Xem tồn kho (xem số lượng tồn kho theo từng biến thể).
- **Internal Services:**
  - Module `inventory`: Service khởi tạo bản ghi tồn kho `stock` khi tạo biến thể; Service xóa bản ghi `stock` khi xóa biến thể; Service đọc số lượng tồn kho `stock_quantity`.
  - Module `ordering`: Service kiểm tra biến thể đã phát sinh trong chi tiết đơn hàng (`order_detail`) hay chưa khi thực hiện xóa biến thể.
- **External Systems:** Redis (lưu trữ và quản lý số phiên bản cache `catalog_version` của danh mục sản phẩm).

## Notes
- Quy tắc ưu tiên UC-14-Q11 (developer chốt 23/11/2026): có phiếu `CONFIRMED` ở bất kỳ biến thể nào thì sản phẩm chỉ sửa Mô tả; không còn được tạo/xóa/đổi trạng thái biến thể, dù tồn kho bằng 0. Quy tắc này thay thế quyền chuyển INACTIVE cho biến thể đã nhập trong Q4 cũ. Kiểm tra qua Service inventory sau khóa cha; hợp đồng tuần tự hóa với xác nhận nhập kho theo Notes UC-14.
- **Ranh giới Modular Monolith (AGENTS.md):** Module `catalog` không truy cập trực tiếp bảng `inventory.stock`, `inventory.goods_receipt_detail` hay `ordering.order_detail`. Mọi thao tác kiểm tra giao dịch, khởi tạo hoặc xóa bản ghi tồn kho đều thông qua Service công khai của module tương ứng.
- **Tồn kho biến thể (BR-005, Data Model v2):** Tồn kho và giá vốn chuyển sang bảng `inventory.stock` (không còn cột tồn kho ở `catalog.variant`). Tồn kho chỉ thay đổi qua module inventory (xác nhận phiếu nhập, đặt/hủy đơn hàng, giao hàng không thành công). Tồn kho không bao giờ âm.
- **Mã tự nhiên SKU (Data Model v2):** Cấp tự động theo định dạng `<mã SP>-<MÀU>-<SIZE>` (bỏ dấu tiếng Việt, viết hoa, bỏ khoảng trắng), NOT NULL, UNIQUE, không cho phép chỉnh sửa.
- **Toàn vẹn Transaction & Cơ chế khóa đồng bộ (AGENTS.md, đã chốt 23/11/2026):**
  - Mọi thao tác ghi dữ liệu biến thể chạy trong MỘT Database Transaction, khóa sản phẩm cha `FOR UPDATE` trước khi đọc trạng thái, đối chiếu tổ hợp, đọc giá hoặc ghi dữ liệu và giữ đến commit/rollback. Riêng tạo lô phải lấy đủ khóa taxonomy `FOR KEY SHARE` trước khóa cha theo Main 6; xóa/đổi trạng thái không tạo tham chiếu taxonomy mới nên không cần khóa taxonomy. Thứ tự này thống nhất UC-14/17, không giữ khóa cha rồi chờ taxonomy.
  - Sau khi có được khóa `FOR UPDATE`, hệ thống bắt buộc phải truy vấn kiểm tra lại danh sách tổ hợp biến thể và giá size hiện hành để triệt tiêu hoàn toàn race condition với các request cạnh tranh đồng thời.
  - Thao tác kiểm tra điều kiện xóa (tồn kho, đơn hàng, phiếu nhập, điều kiện biến thể cuối cùng) và xóa biến thể kèm dọn bản ghi `stock` phải chạy trong cùng transaction có khóa này. Nếu có lỗi ở bất kỳ bước nào, toàn bộ transaction bị rollback.

### Quyết định đã chốt
- UC-14-Q11 (developer chốt tại Codex 23/11/2026): có bất kỳ phiếu CONFIRMED của sản phẩm thì chặn mọi ghi biến thể; quyền tạo/xóa/đổi trạng thái trong các quyết định bên dưới chỉ áp dụng trước mốc này.
- Quản lý biến thể là quyền vận hành cửa hàng của Nhân viên (đã chốt 15/11/2026).
- Tồn kho và giá vốn chuyển sang bảng `inventory.stock`; bảng `catalog.variant` không còn cột tồn kho (đã chốt 20/11/2026).
- Tồn kho ban đầu của biến thể mới tạo = 0, giá vốn = 0; được khởi tạo trong `inventory.stock` qua Service công khai của module inventory trong cùng một transaction khi tạo biến thể; tồn kho không cho sửa tay (đã chốt 22/11/2026, UC-15-Q1).
- Mã biến thể tự nhiên SKU (`variant_id`) cấp tự động theo quy tắc `<mã SP>-<MÀU>-<SIZE>` (bỏ dấu, viết hoa, bỏ khoảng trắng), không cho sửa (đã chốt 22/11/2026, UC-15-Q1).
- Biến thể mới tạo cho một size đã có giá bán tại sản phẩm sẽ tự động kế thừa `variant_sell_price` của size đó; size chưa có giá bán thì để `NULL` chờ định giá ở UC-16 (đã chốt 22/11/2026, UC-15-Q2).
- Biến thể chỉ được xóa khi thỏa mãn đồng thời: chưa từng có trong đơn hàng, chưa từng có trong phiếu nhập, và tồn kho hiện tại = 0; kiểm tra và xóa được thực hiện nguyên tử trong cùng một transaction; khi xóa hợp lệ, hệ thống dọn bản ghi tồn kho liên kết trong `inventory.stock` qua Service của inventory (đã chốt 22/11/2026, UC-15-Q3).
- Hỗ trợ chuyển trạng thái biến thể giữa `ACTIVE` và `INACTIVE` chỉ trước khi sản phẩm có phiếu CONFIRMED (UC-14-Q11, 23/11/2026, thay thế phạm vi Q4 ngày 22/11/2026). Không gợi ý ngừng bán biến thể đã nhập xác nhận. Biến thể `INACTIVE` vẫn hiển thị tùy chọn disabled trên storefront theo UC-12.
- Khi chọn tổ hợp màu × size trùng một phần: hệ thống bỏ qua tổ hợp đã tồn tại, chỉ tạo tổ hợp mới và thông báo rõ ràng số lượng tạo mới cũng như số lượng bỏ qua trên giao diện (đã chốt 22/11/2026, UC-15-Q5).
- Xử lý mã SKU trùng do chuẩn hóa hoặc vượt quá 60 ký tự (`varchar(60)`): hệ thống từ chối tạo biến thể đó (rollback toàn bộ lô tạo biến thể nếu tạo hàng loạt), hiển thị thông báo lỗi rõ ràng để Nhân viên kiểm tra và điều chỉnh lại tên thuộc tính tại UC-17; không tự ý cắt ngắn chuỗi hay sinh hậu tố ngẫu nhiên (đã chốt 22/11/2026, UC-15-Q6).
- **Quy tắc bất biến sản phẩm Đang bán và cơ chế khóa đồng bộ (đã chốt 23/11/2026, đồng bộ UC-14, UC-16):**
  + CHẶN xóa biến thể cuối cùng khi sản phẩm cha đang `ACTIVE` (yêu cầu chuyển Ngừng bán trước ở UC-14, không tự động chuyển `product_status = INACTIVE`).
  + CHẶN tạo lô biến thể có size chưa có giá khi sản phẩm cha đang `ACTIVE` (yêu cầu chuyển Ngừng bán trước ở UC-14). Sản phẩm `INACTIVE` được phép tạo size chưa có giá (`variant_sell_price = NULL`).
  + Cho phép thêm màu mới cho các size đã có giá khi sản phẩm cha đang `ACTIVE` và tự động kế thừa giá hiện hành của size đó.
  + Áp dụng MỘT PostgreSQL transaction giữ khóa `SELECT ... FROM catalog.product WHERE product_key = :product_key FOR UPDATE` trước khi đọc trạng thái, đối chiếu tổ hợp, đọc giá và ghi dữ liệu cho tới khi commit/rollback nhằm triệt tiêu hoàn toàn race condition với UC-16 và các giao dịch tạo/sửa khác.
- **Cơ chế invalidation cache Redis và phòng chống stale cache (đã chốt 23/11/2026, UC-15-Q7):**
  + Tăng số phiên bản `catalog_version` trong Redis ngay sau khi Database Transaction hoàn tất `commit` thành công (áp dụng cho cả Tạo biến thể mới, Xóa biến thể, và Đổi trạng thái biến thể). Khi đó, các key cache storefront (danh mục, trang chủ) tự động hết hiệu lực và tải dữ liệu mới. Nếu DB transaction thất bại/rollback thì tuyệt đối không tăng version.
  + Xử lý lỗi Redis: Nếu DB commit thành công nhưng Redis bị lỗi khi tăng `catalog_version`, hệ thống ghi log cảnh báo (log warning) và vẫn trả kết quả thành công cho Nhân viên; dữ liệu storefront sẽ tự làm mới sau khi hết TTL dự phòng (5 phút).
  + Rủi ro dữ liệu cũ (stale cache) và bảo vệ nghiệp vụ: TTL 5 phút không đảm bảo ngăn chặn mua sai nếu khách hàng đang xem trang cũ chưa tải lại. Do đó, quy tắc nghiệp vụ của UC-15 yêu cầu các thao tác mua hàng (Thêm vào giỏ UC-18, Đặt hàng UC-19/UC-20) phải kiểm tra lại trạng thái biến thể (`variant_status = ACTIVE`) và số lượng tồn kho trực tiếp từ Database qua Service công khai (đã đồng bộ vào đặc tả của BR-002, README và UC-18/19/20 ngày 23/11/2026 theo phê duyệt tại Codex; không bao hàm xác nhận triển khai hay kiểm thử mã nguồn).

### Câu hỏi mở & Giả định `[GD]` đang chờ chốt
*Không còn câu hỏi mở nào. Toàn bộ các yêu cầu nghiệp vụ và kỹ thuật đã được Developer phê duyệt.*

## History
- v1 (2026-11-15): initial
- v2 (2026-11-22): chốt toàn bộ các giả định theo phê duyệt của developer (UC-15-Q1 đến UC-15-Q5): chuẩn hóa quy tắc cấp SKU tự nhiên, khởi tạo và xóa dòng tồn kho qua Service `inventory` trong cùng transaction, cơ chế tự động kế thừa giá theo size, bổ sung luồng đổi trạng thái biến thể ACTIVE/INACTIVE (Ngừng bán), quy tắc xử lý trùng tổ hợp và chặn xóa khi còn tồn kho hoặc đã phát sinh giao dịch; hoàn thiện Main Flow, Alternative Flows và Acceptance Criteria.
- v3 (2026-11-22): rà soát theo phản hồi của Coordinator: chuẩn hóa nhãn các nhánh rẽ Main Flow (1a, 1b, 5a, 5b); bổ sung Exception E3 và AC-15, AC-16 về kiểm tra nguyên tử / rollback transaction cho cả tạo và xóa biến thể; bỏ gợi ý xuất kho thủ công ở E2/AC-11 (thay bằng chuyển Ngừng bán); nêu câu hỏi mở UC-15-Q6 về xử lý SKU trùng/vượt độ dài [GD]; ghi nhận câu hỏi liên UC chờ thống nhất hiển thị INACTIVE với UC-12; giữ Status: draft do còn câu hỏi chặn.
- v4 (2026-11-22): đồng bộ quyết định từ developer tại session Codex: chốt phương án biến thể INACTIVE vẫn hiển thị tùy chọn nhưng bị vô hiệu hóa (disabled) trên storefront (nhất quán với UC-12); cập nhật Flow 1a, AC-9, AC-10, Dependencies, Notes; gỡ bỏ tag [GD] liên quan đến vấn đề hiển thị INACTIVE; chỉ còn câu hỏi mở UC-15-Q6 đang chờ chốt tại session UC-15.
- v5 (2026-11-22): chốt quyết định UC-15-Q6 theo phê duyệt của developer: từ chối tạo biến thể và rollback lô khi SKU trùng hoặc vượt quá 60 ký tự; gỡ bỏ toàn bộ nhãn [GD] còn lại; chuyển Status sang ready.
- v6 (2026-11-22): làm rõ cơ chế một Database Transaction duy nhất bao trùm toàn bộ lô tạo biến thể (Main Flow bước 6-7, Flow 5a, E3, E4, Notes); bổ sung scenario kiểm thử trong AC-17 cho trường hợp lô có tổ hợp hợp lệ đi kèm tổ hợp lỗi SKU thì rollback toàn bộ lô không lưu bất kỳ variant hay stock mới nào.
- v7 (2026-11-22): chuẩn hóa fixture kịch bản AC-17 khớp tích Descartes từ form checkbox (chọn 2 màu "Đen", "Xanhduong" và 1 size "M" để tạo đúng lô 2 tổ hợp Đen×M và Xanhduong×M).
- v8 (2026-11-23): đợt rà soát logic vòng 2: chuyển Status sang draft; mở câu hỏi mở UC-15-Q7 [GD] về cơ chế invalidation cache Redis và rủi ro stale cache.
- v9 (2026-11-23): cập nhật quyết định đã duyệt liên UC (UC-14-Q8/Q9 và UC-16): bổ sung cơ chế khóa PostgreSQL `catalog.product` FOR UPDATE từ trước kiểm tra/đọc giá tới commit; CHẶN tạo lô biến thể có size chưa có giá khi sản phẩm cha ACTIVE (Exception E5, AC-19); cho phép thêm màu mới cho size đã có giá trên sản phẩm ACTIVE (AC-20); CHẶN xóa biến thể cuối cùng khi sản phẩm cha ACTIVE (Exception E6, AC-21); bổ sung AC-22 kiểm tra cạnh tranh giá với UC-16; gỡ bỏ đề xuất tự chuyển INACTIVE; giữ Status: draft do câu hỏi mở UC-15-Q7 [GD] về cache vẫn đang chờ developer duyệt.
- v10 (2026-11-23): chuẩn hóa thứ tự thao tác và diễn đạt theo phản hồi rà soát của Coordinator: Flow 1a Nhân viên bấm đổi trạng thái trước rồi server mới mở tx/khóa/ghi (không giữ khóa chờ bấm); Main 5, Flow 5a, 5b phân loại tổ hợp có quyết định cuối trong transaction sau khóa ở Main 6 (không thoát sớm theo dữ liệu trước khóa); AC-22 làm rõ kết luận đồng nhất giá ở giai đoạn trung gian (320k) và giá mới (350k) sau khi cả hai transaction commit; giữ Status: draft chờ chốt UC-15-Q7 [GD].
- v11 (2026-11-23): chốt toàn bộ quyết định theo phê duyệt của Developer cho UC-15-Q7: bổ sung cơ chế invalidation cache storefront qua catalog_version trong Redis (Main Flow 7, Flow 1a, Flow 1b), xử lý ngoại lệ Redis ghi log warning và fallback TTL 5 phút, bổ sung ràng buộc kiểm tra DB trực tiếp cho UC-18/19/20 chống stale cache; bổ sung AC-23 và AC-24; gỡ bỏ toàn bộ nhãn [GD] và câu hỏi mở; chuyển Status: ready.
- v12 (2026-11-23): hoàn thiện tính nhất quán và bằng chứng AC theo điều phối của Coordinator: khai báo Redis tại External Systems; AC-24 bổ sung DB giữ nguyên thay đổi đã commit (không rollback khi lỗi Redis) và cache làm mới sau TTL tối đa 5 phút hoặc lần tăng version thành công tiếp theo; bổ sung assertion không tăng catalog_version khi DB rollback tại AC-15, AC-16, AC-17, AC-19, AC-21; làm rõ dependency UC-18/19/20 chờ Codex trình duyệt phạm vi đồng bộ; giữ nguyên Status: ready.
- v13 (2026-11-23): cập nhật ghi chú dependency liên UC: chuyển trạng thái bảo vệ stale cache tại UC-18/19/20 sang 'đã đồng bộ đặc tả ngày 23/11/2026 theo phê duyệt Codex' (sau khi Developer duyệt đồng bộ 5 file BR/README/UC-18/19/20 tại Codex); giữ nguyên Status: ready.
- v14 (2026-11-23): đồng bộ UC-14-Q11 theo quyết định developer tại Codex: chặn tạo/xóa/đổi trạng thái mọi biến thể sau phiếu CONFIRMED, kiểm tra dưới khóa cha, thêm E7/AC-25; sửa AC-11..13 và bỏ gợi ý ngừng bán không còn hợp lệ; giữ ready.
- v15 (2026-11-23): thống nhất thứ tự khóa với UC-14/17: tạo lô lấy đủ Màu/Size KEY SHARE trước khóa cha, đọc tên mới sau chờ để sinh SKU; không giữ sản phẩm rồi chờ taxonomy. Xóa/đổi trạng thái không thêm tham chiếu nên giữ giao thức khóa cha hiện có.
