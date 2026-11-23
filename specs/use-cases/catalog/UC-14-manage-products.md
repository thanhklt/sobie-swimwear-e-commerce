# UC-14: Quản lý sản phẩm

## Metadata
- **ID:** UC-14
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Nhân viên (Khách hàng và Admin không có quyền truy cập chức năng này).

## Trigger
Nhân viên mở mục Sản phẩm trong portal quản trị.

## Preconditions
- Nhân viên đã đăng nhập thành công vào portal quản trị (UC-02).
- Hệ thống đã có ít nhất một danh mục và ít nhất một giới tính tồn tại/khả dụng để chọn (UC-17).

## Main Flow
1. Hệ thống hiển thị danh sách sản phẩm có phân trang cố định 20 sản phẩm/trang, sắp xếp theo sản phẩm mới tạo nhất lên đầu (`product_created_at` giảm dần). Màn hình hỗ trợ:
   - Tìm kiếm theo Tên sản phẩm hoặc Mã sản phẩm (`SP-xxxx`).
   - Lọc theo Trạng thái (Tất cả / Đang bán / Ngừng bán), Danh mục, Giới tính.
   - Mỗi dòng hiển thị: Mã sản phẩm, Ảnh đại diện (ảnh vị trí số 1), Tên sản phẩm, Danh mục, Giới tính, Trạng thái (Đang bán / Ngừng bán), Ngày tạo.
2. Nhân viên chọn "Thêm sản phẩm".
3. Nhân viên nhập thông tin sản phẩm:
   - Tên sản phẩm (bắt buộc, tối đa 255 ký tự, không trùng với tên sản phẩm đã có).
   - Mô tả (tùy chọn).
   - Danh mục (bắt buộc, chọn đúng 1 danh mục từ danh sách khả dụng của UC-17).
   - Giới tính (bắt buộc, chọn đúng 1 giới tính từ danh sách khả dụng của UC-17).
   - Bộ sưu tập (tùy chọn, có thể chọn 0, 1 hoặc nhiều bộ sưu tập).
   - Bộ ảnh (gallery): có thể tải lên một hoặc nhiều ảnh hoặc để trống thêm sau.
   - Không nhập bảng size: cửa hàng dùng một bảng size chung cố định (BR-002).
4. Nhân viên bấm "Lưu sản phẩm".
5. Trong CÙNG MỘT Database Transaction duy nhất (bảo đảm tính nguyên tử từ bước kiểm tra đến ghi):
   - Hệ thống chuẩn hóa cắt bỏ khoảng trắng thừa ở đầu và cuối tên sản phẩm (`trim()`).
   - Kiểm tra các trường bắt buộc (Tên sản phẩm, Danh mục, Giới tính) -> nếu thiếu hoặc để trống sau khi trim thì rollback và chuyển sang Exception E1.
   - Kiểm tra độ dài tên sản phẩm không vượt quá 255 ký tự -> nếu vượt quá rollback và chuyển sang Exception E1.
   - Kiểm tra tính duy nhất của tên sản phẩm nguyên tử (yêu cầu cơ chế bảo đảm duy nhất toàn cục như unique index ở database hoặc advisory lock, phân biệt với khóa dòng sản phẩm đơn lẻ): so sánh chuỗi sau khi trim, không phân biệt hoa/thường, không cho phép trùng với bất kỳ sản phẩm nào khác trong hệ thống (kể cả khi có 2 request gửi đồng thời) -> nếu trùng rollback và chuyển sang Exception E1.
   - Tự động cấp mã sản phẩm duy nhất `product_id` theo định dạng `SP-<4 số tăng dần>` (ví dụ SP-0001, không cho sửa).
   - Tạo bản ghi sản phẩm trong bảng `catalog.product` với tên sản phẩm đã trim (giữ nguyên định dạng chữ hoa/thường nhân viên nhập), trạng thái mặc định `INACTIVE` (Ngừng bán), `product_total_score_review = 0`.
   - Lưu các liên kết bộ sưu tập vào bảng `catalog.product_collection` (nếu có).
   - Lưu các ảnh vào bảng `catalog.gallery` với `gallery_order_no` đánh số liên tục bắt đầu từ 1 (nếu có).
6. Hệ thống commit Database Transaction thành công, hiển thị thông báo "Thêm sản phẩm thành công" và chuyển đến màn hình chi tiết sản phẩm vừa tạo.
7. Nhân viên tiếp tục cấu hình sản phẩm:
   - Bổ sung ảnh gallery nếu chưa có (Alternative Flow 2d).
   - Tạo biến thể màu × size qua UC-15.
   - Thiết lập giá bán theo size qua UC-16.
8. Sau khi sản phẩm đã thỏa mãn đủ điều kiện mở bán, Nhân viên bấm "Chuyển sang Đang bán".
9. Trong MỘT Database Transaction XUYÊN SUỐT từ trước kiểm tra đến commit:
   - Khóa dòng sản phẩm cha (`SELECT * FROM catalog.product WHERE product_key = ... FOR UPDATE`) để giữ độc quyền kiểm tra và ghi, chống race condition.
   - Kiểm tra điều kiện mở bán (xem Exception E3):
     + Sản phẩm phải có ít nhất một biến thể tồn tại trong sản phẩm (UC-15).
     + Mọi size của sản phẩm đều đã được đặt giá bán > 0 (UC-16).
     + Sản phẩm phải có ít nhất một ảnh trong bộ ảnh gallery.
     + Lưu ý: Tồn kho bằng 0 vẫn cho phép mở bán (storefront sẽ hiển thị nhãn "Hết hàng").
   - Nếu không thỏa mãn điều kiện: rollback transaction, giữ nguyên sản phẩm ở trạng thái Ngừng bán và báo lý do theo Exception E3.
   - Nếu thỏa mãn: cập nhật trạng thái sản phẩm sang `ACTIVE` (Đang bán) trong bảng `catalog.product`, cập nhật `product_updated_at = now()`.
   - Commit Database Transaction.
10. Sau khi Database Transaction commit thành công:
    - **Nhánh thông thường:** Hệ thống gọi Redis tăng số phiên bản catalog (`catalog_version`) để làm mới cache công khai. Ở request tiếp theo, sản phẩm chỉ đủ điều kiện xuất hiện trong danh sách storefront nếu có ít nhất một biến thể `ACTIVE` giá > 0; nếu mọi biến thể đều `INACTIVE`, sản phẩm vẫn mở bán thành công nhưng bị ẩn khỏi danh sách và URL chi tiết xử lý theo UC-12 Alternative Flow 2c. Khách hàng đã mở sẵn trang cần tải lại để thấy dữ liệu mới.
    - **Nhánh lỗi Redis sau commit:** Nếu Redis bị lỗi kết nối hoặc timeout khi tăng `catalog_version`, hệ thống ghi log cảnh báo (warning log), KHÔNG rollback Database Transaction đã commit, và vẫn hiển thị thông báo thành công cho Nhân viên (Exception E9). Lưu ý về độ trễ: độ trễ tối đa theo TTL dự phòng (5 phút) hoặc lần tăng version thành công tiếp theo chỉ áp dụng cho các dữ liệu thực sự đọc từ cache công khai (Hàng mới và Bộ sưu tập UC-09, danh sách danh mục UC-10, chi tiết sản phẩm UC-12); các truy vấn trực tiếp Database không qua cache (tìm kiếm UC-11, wishlist UC-38, giỏ hàng UC-18, đặt hàng UC-19/20) luôn đọc trạng thái mới nhất từ Database ngay sau khi commit.
    - Lưu ý: Nếu Database Transaction bị rollback (ở bước 9), hệ thống tuyệt đối không gọi Redis tăng `catalog_version`.
11. **Quy tắc bất biến khi sản phẩm ở trạng thái Đang bán (`ACTIVE`):**
    - Các điều kiện mở bán (ít nhất 1 ảnh trong gallery, ít nhất 1 biến thể tồn tại, mọi size có giá bán > 0) là bất biến trong suốt thời gian sản phẩm ở trạng thái `ACTIVE`.
    - Hệ thống chặn mọi thao tác làm mất điều kiện này (xóa ảnh cuối cùng, xóa biến thể cuối cùng, hoặc thêm size mới chưa có giá) và yêu cầu chuyển sản phẩm sang Ngừng bán (`INACTIVE`) trước; hệ thống tuyệt đối không tự động chuyển trạng thái ngầm.
    - Làm rõ: Điều kiện là có ít nhất 1 biến thể tồn tại trong sản phẩm (không bắt buộc biến thể đó phải ở trạng thái ACTIVE hay INACTIVE).
    - Mọi thao tác ghi liên quan (chuyển ACTIVE ở bước 9, sửa gallery ở UC-14, thêm/xóa biến thể ở UC-15, sửa giá size ở UC-16) đều phải giữ khóa dòng sản phẩm cha `catalog.product FOR UPDATE` trong Database Transaction của thao tác đó để chống race condition.

## Alternative Flows

- **1a. Tìm kiếm, lọc và phân trang danh sách:**
  - Điều kiện vào: Nhân viên nhập từ khóa tìm kiếm (theo tên hoặc mã `SP-xxxx`), chọn bộ lọc (trạng thái, danh mục, giới tính) hoặc chuyển trang tại danh sách sản phẩm.
  - Xử lý: Hệ thống truy vấn trực tiếp Database (không cache theo quy định portal quản trị), trả về danh sách sản phẩm thỏa mãn điều kiện tìm kiếm/lọc và phân trang tương ứng (20 sản phẩm/trang).

- **2a. Sửa sản phẩm:**
  - Điều kiện vào: Nhân viên chọn sửa một sản phẩm từ danh sách hoặc màn hình chi tiết.
  - Xử lý:
    1. Hệ thống hiển thị form chỉnh sửa gồm: Tên sản phẩm, Mô tả, Danh mục, Giới tính, Bộ sưu tập. Mã sản phẩm `product_id` hiển thị ở chế độ chỉ đọc, không cho sửa.
    2. Nhân viên sửa thông tin và bấm "Lưu thay đổi".
    3. Trong CÙNG MỘT Database Transaction duy nhất (bảo đảm tính nguyên tử từ kiểm tra đến ghi):
       - Hệ thống chuẩn hóa cắt khoảng trắng thừa đầu/cuối của tên sản phẩm (`trim()`), kiểm tra độ dài tối đa 255 ký tự, kiểm tra đủ trường bắt buộc.
       - Kiểm tra tính duy nhất tên sản phẩm nguyên tử: cho phép giữ nguyên tên hiện tại của chính sản phẩm đang sửa, nhưng chặn nếu trùng với bất kỳ sản phẩm nào khác trong hệ thống (so sánh chuỗi sau khi trim, không phân biệt hoa/thường). Nếu không hợp lệ -> rollback và chuyển sang Exception E1.
       - Cập nhật thông tin trong bảng `catalog.product` với tên đã trim (giữ nguyên định dạng hoa/thường nhập) và ghi nhận `product_updated_at = now()`.
       - Đồng bộ lại các liên kết bộ sưu tập trong bảng `catalog.product_collection`.
    4. Sau khi Database Transaction commit thành công:
       - Hệ thống gọi Redis tăng số phiên bản catalog (`catalog_version`) để làm mới cache storefront ở request tiếp theo.
       - Nếu Redis gặp sự cố hoặc timeout: ghi log cảnh báo, không rollback DB, cache storefront làm mới sau tối đa TTL 5 phút hoặc lần tăng version thành công tiếp theo (Exception E9).
       - Hệ thống hiển thị thông báo "Cập nhật sản phẩm thành công".

- **2b. Ngừng bán sản phẩm:**
  - Điều kiện vào: Sản phẩm đang ở trạng thái `ACTIVE` (Đang bán). Nhân viên bấm "Ngừng bán" và xác nhận.
  - Xử lý:
    1. Trong Database Transaction: khóa dòng sản phẩm (`SELECT ... FOR UPDATE`), cập nhật trạng thái sản phẩm sang `INACTIVE` (Ngừng bán) trong bảng `catalog.product`, cập nhật `product_updated_at = now()`.
    2. Sau khi Database Transaction commit thành công:
       - Hệ thống gọi Redis tăng số phiên bản catalog (`catalog_version`) để làm mới cache công khai ở request tiếp theo.
       - Nếu Redis gặp sự cố hoặc timeout: ghi log cảnh báo, không rollback DB, vẫn thông báo thành công cho Nhân viên (Exception E9); độ trễ tối đa TTL 5 phút chỉ áp dụng cho các dữ liệu đọc từ cache công khai.
    3. Tác động trạng thái Ngừng bán trên hệ thống và storefront:
       - **Đối với dữ liệu đọc trực tiếp từ Database (không qua cache Redis công khai):** Request mới ngay lập tức nhận diện trạng thái `INACTIVE` từ Database bất kể Redis tăng version thành công hay lỗi:
         + Kết quả tìm kiếm (UC-11, không cache) không còn trả về sản phẩm.
         + Danh sách yêu thích của khách hàng đã đăng nhập (UC-38, không cache) lập tức hiển thị nhãn "Ngừng bán" và vô hiệu hóa nút xem chi tiết.
         + Khối Top 5 bán chạy trên trang chủ khi render (UC-09, BR-002) luôn lọc theo trạng thái sản phẩm hiện hành từ Database nên sản phẩm tự động biến mất ngay mà không cần chờ tác vụ định kỳ 10 phút của reporting.
         + Mọi thao tác mua hàng (thêm vào giỏ UC-18, đặt hàng COD UC-19, đặt hàng QR UC-20) luôn đọc trạng thái trực tiếp từ Database và lập tức từ chối khi sản phẩm cha ở trạng thái `INACTIVE`.
       - **Đối với dữ liệu đọc từ cache công khai (UC-09 Hàng mới và Bộ sưu tập, UC-10 danh mục, UC-12 chi tiết sản phẩm):**
         + Khi Redis tăng version thành công: cache được làm mới ở request tiếp theo (sản phẩm không còn trong danh mục; truy cập chi tiết báo "Không tìm thấy sản phẩm" UC-12 E1).
         + Khi Redis lỗi sau commit: chỉ các dữ liệu cache công khai này mới có thể trễ tối đa theo TTL dự phòng còn lại (tối đa 5 phút) hoặc cho đến lần tăng version thành công tiếp theo.
       - **Lưu ý về client đang mở sẵn:** Khách hàng đang mở sẵn màn hình trên trình duyệt cần tải lại trang (reload) để thấy trạng thái mới; cơ chế hết hạn cache TTL không tự động làm thay đổi giao diện trình duyệt đã nạp sẵn DOM.
    4. Hệ thống hiển thị thông báo "Đã chuyển sản phẩm sang trạng thái Ngừng bán".

- **2c. Xóa sản phẩm:**
  - Điều kiện vào: Nhân viên bấm "Xóa sản phẩm" tại màn hình quản lý. Hệ thống hiển thị hộp thoại cảnh báo và xác nhận xóa.
  - Xử lý:
    1. Nhân viên bấm xác nhận xóa.
    2. Hệ thống mở một Database Transaction duy nhất để kiểm tra và thực hiện xóa toàn vẹn (chống race condition):
       - Khóa bản ghi sản phẩm cần xóa (`SELECT ... FOR UPDATE`).
       - Kiểm tra phát sinh đơn hàng: gọi Service công khai của module `ordering` kiểm tra sản phẩm có bất kỳ biến thể nào đã xuất hiện trong `ordering.order_detail` hay chưa -> Nếu có: rollback transaction và chuyển sang Exception E2.
       - Kiểm tra phát sinh phiếu nhập: gọi Service công khai của module `inventory` kiểm tra sản phẩm có bất kỳ biến thể nào đã xuất hiện trong `inventory.goods_receipt_detail` (kể cả phiếu nhập nháp UC-33) hay chưa -> Nếu có: rollback transaction và chuyển sang Exception E2.
       - Kiểm tra ràng buộc khuyến mãi: gọi Service công khai của module `promotion` kiểm tra sản phẩm đã từng gắn vào chương trình khuyến mãi theo sản phẩm (`promotion.product_promotion`) hay chưa (do ràng buộc DBML `[delete: restrict]`, kể cả khuyến mãi đã kết thúc) -> Nếu có: rollback transaction và chuyển sang Exception E4.
       - Kiểm tra tồn kho: gọi Service công khai của module `inventory` kiểm tra tồn kho mọi biến thể của sản phẩm (`inventory.stock`) -> Nếu có bất kỳ biến thể nào có số lượng tồn kho > 0: rollback transaction và chuyển sang Exception E5.
       - Nếu thỏa mãn toàn bộ điều kiện trên, hệ thống thực hiện xóa dữ liệu liên kết:
         + Gọi Service công khai của module `inventory` để xóa các bản ghi `stock` liên kết với biến thể của sản phẩm.
         + Gọi Service công khai của module `shopping` để xóa các bản ghi `wishlist_item` liên kết với sản phẩm.
         + Xóa các bản ghi biến thể `catalog.variant` của sản phẩm (các dòng `cart_item` nếu có sẽ tự động bị xóa theo FK cascade).
         + Xóa các liên kết bộ sưu tập trong `catalog.product_collection`.
         + Xóa các bản ghi ảnh trong `catalog.gallery`.
         + Xóa bản ghi sản phẩm trong bảng `catalog.product`.
       - Nếu xảy ra bất kỳ lỗi hệ thống nào trong quá trình gọi Service hoặc xóa dữ liệu: toàn bộ Database Transaction bị rollback, dữ liệu sản phẩm và các module liên quan được bảo toàn nguyên vẹn (chuyển sang Exception E6).
    3. Sau khi Database Transaction commit thành công:
       - Tăng số phiên bản catalog (`catalog_version`) ở Redis để làm mới cache ở request tiếp theo.
       - Nếu Redis gặp sự cố hoặc timeout: ghi log cảnh báo, không rollback DB (Exception E9), cache storefront làm mới sau tối đa TTL 5 phút.
       - Hệ thống cập nhật lại danh sách và thông báo "Xóa sản phẩm thành công".

- **2d. Quản lý bộ ảnh (gallery):**
  - Điều kiện vào: Nhân viên mở mục Quản lý ảnh của sản phẩm.
  - Xử lý:
    1. Nhân viên có thể thực hiện:
       - Thêm ảnh mới: tải lên một hoặc nhiều ảnh hợp lệ.
       - Đổi thứ tự hiển thị: kéo thả hoặc thay đổi vị trí các ảnh.
       - Xóa ảnh: chọn xóa một hoặc nhiều ảnh khỏi gallery.
    2. Trong Database Transaction: khóa dòng sản phẩm cha (`SELECT ... FOR UPDATE` trên bảng `catalog.product`).
    3. Kiểm tra điều kiện ràng buộc: Nếu sản phẩm đang ở trạng thái `ACTIVE` (Đang bán) mà thao tác xóa ảnh làm bộ ảnh rỗng (0 ảnh) -> hệ thống từ chối xóa và chuyển sang Exception E7.
    4. Hệ thống tự động chuẩn hóa và đánh lại số thứ tự `gallery_order_no` thành dãy số nguyên liên tục 1, 2, 3... đến N.
       - Ảnh có `gallery_order_no = 1` mặc định là ảnh đại diện (thumbnail) của sản phẩm trên storefront và quản trị.
       - Cập nhật các bản ghi trong bảng `catalog.gallery`.
    5. Sau khi Database Transaction commit thành công:
       - Tăng số phiên bản catalog (`catalog_version`) ở Redis để làm mới cache ở request tiếp theo.
       - Nếu Redis gặp sự cố hoặc timeout: ghi log cảnh báo, không rollback DB (Exception E9), cache storefront làm mới sau tối đa TTL 5 phút.
       - Hệ thống thông báo "Cập nhật bộ ảnh thành công".

- **8a. Chuyển Đang bán khi chưa đủ điều kiện:** xem Exception E3.

## Exceptions

- **E1. Thiếu trường bắt buộc, sai định dạng hoặc tên sản phẩm bị trùng:**
  - Thiếu tên sản phẩm hoặc tên chỉ chứa khoảng trắng: hệ thống từ chối lưu và báo "Tên sản phẩm là bắt buộc".
  - Tên sản phẩm vượt quá 255 ký tự: hệ thống từ chối lưu và báo "Tên sản phẩm không được vượt quá 255 ký tự".
  - Chưa chọn danh mục: hệ thống từ chối lưu và báo "Vui lòng chọn danh mục cho sản phẩm".
  - Chưa chọn giới tính: hệ thống từ chối lưu và báo "Vui lòng chọn giới tính cho sản phẩm".
  - Trùng tên sản phẩm đã có trong hệ thống (so sánh chuỗi sau khi trim, không phân biệt hoa/thường, bao gồm cả trường hợp 2 request cạnh tranh gửi cùng tên đồng thời thì đúng một request thành công và một request bị chặn bởi lỗi này): hệ thống từ chối lưu và báo "Tên sản phẩm đã tồn tại".

- **E2. Chặn xóa sản phẩm đã phát sinh giao dịch:**
  - Điều kiện: Sản phẩm đã có ít nhất một biến thể xuất hiện trong đơn hàng (`ordering.order_detail`) hoặc trong phiếu nhập (`inventory.goods_receipt_detail`, kể cả phiếu nhập nháp).
  - Xử lý: Hệ thống từ chối xóa, rollback transaction nếu đang mở, giữ nguyên dữ liệu và hiển thị thông báo: "Sản phẩm đã phát sinh giao dịch (đơn hàng hoặc phiếu nhập), không thể xóa. Gợi ý chuyển sang Ngừng bán".

- **E3. Chặn chuyển Đang bán khi chưa đủ điều kiện mở bán:**
  - Điều kiện: Sản phẩm đang ở trạng thái Ngừng bán (`INACTIVE`), Nhân viên bấm chuyển sang Đang bán (`ACTIVE`) nhưng vi phạm một trong các điều kiện mở bán:
    - Sản phẩm chưa có biến thể nào: hệ thống từ chối và báo "Sản phẩm cần có ít nhất một biến thể để mở bán".
    - Sản phẩm có size chưa được đặt giá bán: hệ thống từ chối và báo "Size [Tên size] chưa có giá bán" (UC-16).
    - Sản phẩm chưa có ảnh gallery nào: hệ thống từ chối và báo "Sản phẩm cần có ít nhất một ảnh để mở bán".
  - Xử lý: Hệ thống từ chối kích hoạt, giữ nguyên sản phẩm ở trạng thái Ngừng bán.

- **E4. Chặn xóa sản phẩm đã từng gắn khuyến mãi theo sản phẩm:**
  - Điều kiện: Sản phẩm đã từng gắn vào chương trình khuyến mãi theo sản phẩm (`promotion.product_promotion`), do ràng buộc khóa ngoại `[delete: restrict]` tại database (kể cả khuyến mãi đã kết thúc).
  - Xử lý: Hệ thống từ chối xóa, rollback transaction, giữ nguyên dữ liệu và thông báo: "Sản phẩm đã gắn vào chương trình khuyến mãi, không thể xóa. Vui lòng chuyển sang Ngừng bán".

- **E5. Chặn xóa sản phẩm còn tồn kho:**
  - Điều kiện: Sản phẩm có biến thể có số lượng tồn kho `stock_quantity > 0` trong kho.
  - Xử lý: Hệ thống từ chối xóa, rollback transaction, thông báo: "Sản phẩm vẫn còn hàng trong kho, không thể xóa".

- **E6. Lỗi hệ thống khi xóa sản phẩm giữa chừng:**
  - Điều kiện: Quá trình gọi Service công khai của `inventory`, `shopping` hoặc xóa dữ liệu cục bộ gặp sự cố kết nối hoặc lỗi runtime.
  - Xử lý: Toàn bộ Database Transaction bị rollback; bản ghi sản phẩm cùng mọi dữ liệu liên kết (`stock`, `wishlist_item`, `variant`, `gallery`, `product_collection`) được bảo toàn nguyên vẹn; hệ thống thông báo: "Có lỗi xảy ra trong quá trình xóa sản phẩm, toàn bộ dữ liệu đã được hoàn tác. Vui lòng thử lại sau".

- **E7. Chặn xóa ảnh cuối cùng của sản phẩm đang Đang bán:**
  - Điều kiện: Sản phẩm đang ở trạng thái `ACTIVE` (Đang bán), nhân viên thực hiện xóa ảnh khiến số lượng ảnh trong gallery trở về 0.
  - Xử lý: Hệ thống từ chối xóa ảnh và thông báo: "Sản phẩm đang Đang bán, bắt buộc phải có ít nhất một ảnh trong bộ ảnh. Vui lòng chuyển sản phẩm sang Ngừng bán trước hoặc tải ảnh thay thế".

- **E8. Chặn thao tác làm mất bất biến mở bán của sản phẩm đang Đang bán:**
  - Điều kiện: Sản phẩm đang ở trạng thái `ACTIVE` (Đang bán), nhân viên thao tác xóa biến thể cuối cùng của sản phẩm (UC-15) hoặc thêm size mới chưa có giá bán (UC-15, UC-16).
  - Xử lý: Hệ thống từ chối thực hiện thao tác, giữ nguyên trạng thái và dữ liệu trong Database, hiển thị thông báo: "Sản phẩm đang Đang bán, không thể thực hiện thao tác làm mất điều kiện mở bán. Vui lòng chuyển sản phẩm sang Ngừng bán trước".

- **E9. Lỗi cập nhật Redis cache version sau khi Database Transaction đã commit:**
  - Điều kiện: Thao tác cập nhật sản phẩm (đổi thông tin, đổi trạng thái Đang bán/Ngừng bán, xóa sản phẩm, sửa gallery) đã commit Database Transaction thành công nhưng lệnh tăng `catalog_version` ở Redis bị lỗi kết nối hoặc timeout.
  - Xử lý:
    + Hệ thống ghi log cảnh báo mức warning kèm chi tiết lỗi Redis để đội ngũ kỹ thuật theo dõi.
    + Tuyệt đối KHÔNG rollback Database Transaction đã commit (Database là nguồn sự thật duy nhất).
    + Vẫn trả về thông báo thành công cho Nhân viên bình thường.
    + Giới hạn độ trễ: Chỉ các dữ liệu thực sự đọc từ cache công khai (Hàng mới và Bộ sưu tập UC-09, danh mục UC-10, chi tiết sản phẩm UC-12) mới có thể phản ánh trễ tối đa trong thời gian TTL dự phòng còn lại (tối đa 5 phút) hoặc cho đến lần tăng version thành công tiếp theo. Các nghiệp vụ và truy vấn đọc trực tiếp Database (tìm kiếm UC-11, wishlist UC-38, giỏ hàng UC-18, đặt hàng UC-19/20, khối bán chạy UC-09) luôn thấy dữ liệu và trạng thái mới nhất ngay sau khi SQL commit.

## Postconditions
- Sản phẩm được tạo, cập nhật, đổi trạng thái hoặc xóa đúng theo thao tác.
- Mã sản phẩm tự nhiên `SP-xxxx` được cấp duy nhất, không thể sửa đổi trong suốt vòng đời sản phẩm.
- Khi sản phẩm thay đổi thông tin, đổi trạng thái hoặc bị xóa, số phiên bản catalog (`catalog_version`) ở Redis được tăng lên CHỈ SAU KHI Database Transaction đã commit thành công.
- Nếu Redis bị lỗi khi tăng `catalog_version` sau khi DB đã commit: hệ thống ghi log cảnh báo mức warning, không rollback DB; độ trễ tối đa TTL 5 phút chỉ áp dụng cho dữ liệu đọc từ cache công khai, các truy vấn trực tiếp Database luôn thấy trạng thái mới nhất ngay sau khi commit.
- Nếu Database Transaction bị rollback: hệ thống tuyệt đối không gọi Redis tăng `catalog_version`.
- Màn hình quản trị sản phẩm luôn truy vấn trực tiếp Database với `Cache-Control: no-store`.

## Acceptance Criteria

### AC-1: Thêm sản phẩm hợp lệ
Given: Nhân viên đã đăng nhập và hệ thống đã có danh mục "Bikini", giới tính "Nữ" khả dụng
When: Nhân viên nhập tên "  Bikini Liền Thân Classic  ", chọn danh mục "Bikini", giới tính "Nữ" và lưu
Then: hệ thống tự động cắt khoảng trắng thừa thành "Bikini Liền Thân Classic" và lưu vào DB với đúng định dạng chữ hoa/thường nhập trong cùng một transaction
And: sản phẩm được tạo thành công ở trạng thái Ngừng bán (`INACTIVE`)
And: hệ thống tự cấp mã sản phẩm duy nhất theo định dạng `SP-<4 số>` (ví dụ `SP-0001`)
And: sản phẩm xuất hiện trong danh sách quản trị sản phẩm

### AC-2: Thiếu trường bắt buộc
Given: Nhân viên đang thêm sản phẩm
When: Nhân viên để trống tên sản phẩm hoặc không chọn danh mục hoặc không chọn giới tính và bấm lưu
Then: hệ thống từ chối lưu và chỉ rõ trường bắt buộc còn thiếu

### AC-3: Trùng tên sản phẩm
Given: hệ thống đã tồn tại sản phẩm có tên "Bikini Liền Thân Classic"
When: Nhân viên tạo một sản phẩm mới với tên "   bikini liền thân classic   "
Then: hệ thống từ chối lưu và báo lỗi "Tên sản phẩm đã tồn tại"

### AC-3b: Đảm bảo tính duy nhất nguyên tử khi cạnh tranh tạo tên sản phẩm trùng lặp
Given: hai nhân viên đồng thời gửi yêu cầu tạo sản phẩm với tên "Bikini Hè" và "  bikini hè  " (sau khi trim và chuyển chữ thường là trùng nhau)
When: hệ thống xử lý hai yêu cầu trong hai Database Transaction song song
Then: đúng một sản phẩm được tạo thành công
And: yêu cầu còn lại bị từ chối với thông báo lỗi E1 "Tên sản phẩm đã tồn tại"

### AC-4: Tên sản phẩm vượt quá 255 ký tự
Given: Nhân viên đang thêm hoặc sửa sản phẩm
When: Nhân viên nhập tên sản phẩm dài hơn 255 ký tự và bấm lưu
Then: hệ thống từ chối lưu và báo lỗi "Tên sản phẩm không được vượt quá 255 ký tự"

### AC-5: Sửa thông tin sản phẩm
Given: sản phẩm A có mã `SP-0001` đã tồn tại
When: Nhân viên đổi tên thành "Bikini Liền Thân Cao Cấp", sửa mô tả, đổi danh mục sang "Đồ Bơi Liền Thân" và bấm lưu
Then: thông tin mới được cập nhật thành công sau khi Database Transaction commit
And: mã sản phẩm `SP-0001` được giữ nguyên không đổi
And: cache version ở Redis được tăng lên sau khi commit DB thành công

### AC-6: Chuyển Đang bán thành công
Given: sản phẩm A có ít nhất 1 ảnh gallery, ít nhất 1 biến thể `ACTIVE` có giá bán > 0 và mọi size của A đều đã có giá bán > 0 (kể cả khi tồn kho = 0); Redis hoạt động bình thường
When: Nhân viên bấm chuyển A sang Đang bán
Then: hệ thống thực hiện trong một Database Transaction xuyên suốt: khóa dòng sản phẩm A FOR UPDATE, kiểm tra đủ điều kiện và cập nhật A sang trạng thái `ACTIVE`
And: cache version ở Redis được tăng lên sau khi commit DB thành công
And: sản phẩm A đủ điều kiện xuất hiện trong danh sách storefront ở request tiếp theo (theo bộ lọc và giới hạn của từng khối/danh sách); khi hết tồn kho vẫn hiển thị nhãn "Hết hàng"

### AC-6b: Mở bán thành công khi mọi biến thể đều Ngừng bán
Given: sản phẩm B có ảnh gallery, ít nhất 1 biến thể tồn tại, mọi size có giá bán > 0 nhưng mọi biến thể đều `INACTIVE`; Redis hoạt động bình thường
When: Nhân viên chuyển sản phẩm B sang Đang bán
Then: hệ thống kiểm tra điều kiện dưới khóa dòng sản phẩm trong cùng transaction và commit `product_status = ACTIVE` thành công, sau đó tăng `catalog_version`
And: B bị loại khỏi danh sách trang chủ, danh mục và tìm kiếm trước khi tính tổng số hoặc giới hạn hiển thị vì không có biến thể `ACTIVE` có giá hợp lệ
And: truy cập URL chi tiết B trả HTTP 200 với tên, mô tả và gallery, không hiển thị giá bán, vô hiệu hóa màu/size/số lượng/thêm giỏ và báo "Sản phẩm tạm ngừng kinh doanh" theo UC-12

### AC-7: Chặn chuyển Đang bán khi chưa có biến thể
Given: sản phẩm A mới tạo, đã có ảnh gallery nhưng chưa có biến thể nào
When: Nhân viên bấm chuyển A sang Đang bán
Then: hệ thống từ chối và báo "Sản phẩm cần có ít nhất một biến thể để mở bán"
And: sản phẩm A vẫn ở trạng thái Ngừng bán

### AC-8: Chặn chuyển Đang bán khi có size chưa có giá bán
Given: sản phẩm A có biến thể size S và size L, trong đó size L chưa được thiết lập giá bán
When: Nhân viên bấm chuyển A sang Đang bán
Then: hệ thống từ chối và báo "Size L chưa có giá bán"
And: sản phẩm A vẫn ở trạng thái Ngừng bán

### AC-9: Chặn chuyển Đang bán khi chưa có ảnh gallery
Given: sản phẩm A đã có biến thể và mọi size đã có giá bán nhưng gallery chưa có ảnh nào
When: Nhân viên bấm chuyển A sang Đang bán
Then: hệ thống từ chối và báo "Sản phẩm cần có ít nhất một ảnh để mở bán"
And: sản phẩm A vẫn ở trạng thái Ngừng bán

### AC-10: Ngừng bán sản phẩm
Given: sản phẩm A đang ở trạng thái Đang bán (`ACTIVE`)
When: Nhân viên chuyển A sang Ngừng bán (`INACTIVE`)
Then: trong cùng một transaction: dòng sản phẩm A được khóa FOR UPDATE, cập nhật sang trạng thái `INACTIVE` và commit thành công
And: sau khi commit DB, hệ thống gọi Redis tăng `catalog_version` thành công
And: ở request tiếp theo trên storefront, sản phẩm A không còn xuất hiện ở trang chủ, trang danh mục, kết quả tìm kiếm và không mở được trang chi tiết (khách hàng đã mở sẵn trang cần tải lại trang)
And: sản phẩm A bị loại khỏi khối Top 5 bán chạy trên trang chủ ở request tiếp theo mà không cần chờ tác vụ định kỳ 10 phút

### AC-11: Chặn xóa sản phẩm đã có trong đơn hàng
Given: sản phẩm A đã có ít nhất một biến thể xuất hiện trong đơn hàng
When: Nhân viên bấm xóa sản phẩm A
Then: hệ thống từ chối xóa và hiển thị thông báo "Sản phẩm đã phát sinh giao dịch (đơn hàng hoặc phiếu nhập), không thể xóa. Gợi ý chuyển sang Ngừng bán"
And: hệ thống tuyệt đối không gọi Redis tăng `catalog_version` khi transaction bị rollback

### AC-12: Chặn xóa sản phẩm đã có trong phiếu nhập
Given: sản phẩm A chưa có đơn hàng nào nhưng đã có biến thể nằm trong phiếu nhập (kể cả phiếu nhập nháp)
When: Nhân viên bấm xóa sản phẩm A
Then: hệ thống từ chối xóa và hiển thị thông báo "Sản phẩm đã phát sinh giao dịch (đơn hàng hoặc phiếu nhập), không thể xóa. Gợi ý chuyển sang Ngừng bán"
And: hệ thống tuyệt đối không gọi Redis tăng `catalog_version` khi transaction bị rollback

### AC-13: Chặn xóa sản phẩm đã từng gắn khuyến mãi theo sản phẩm
Given: sản phẩm A đã từng gắn vào một chương trình khuyến mãi theo sản phẩm (kể cả đã kết thúc)
When: Nhân viên bấm xóa sản phẩm A
Then: hệ thống từ chối xóa và báo lỗi "Sản phẩm đã gắn vào chương trình khuyến mãi, không thể xóa. Vui lòng chuyển sang Ngừng bán"
And: hệ thống tuyệt đối không gọi Redis tăng `catalog_version` khi transaction bị rollback

### AC-14: Chặn xóa sản phẩm còn tồn kho > 0
Given: sản phẩm A chưa có đơn hàng hay phiếu nhập nhưng có biến thể có tồn kho > 0
When: Nhân viên bấm xóa sản phẩm A
Then: hệ thống từ chối xóa và báo lỗi "Sản phẩm vẫn còn hàng trong kho, không thể xóa"
And: hệ thống tuyệt đối không gọi Redis tăng `catalog_version` khi transaction bị rollback

### AC-15: Toàn vẹn Transaction khi xóa sản phẩm thất bại giữa chừng
Given: sản phẩm B đủ điều kiện xóa nhưng xảy ra lỗi hệ thống khi gọi Service xóa `stock` ở module inventory
When: Nhân viên thực hiện xóa sản phẩm B
Then: toàn bộ Database Transaction bị rollback
And: bản ghi sản phẩm B, biến thể và các dữ liệu liên kết được bảo toàn nguyên vẹn
And: hệ thống tuyệt đối không gọi Redis tăng `catalog_version` khi transaction bị rollback
And: hệ thống hiển thị thông báo lỗi và yêu cầu thử lại sau

### AC-16: Xóa sản phẩm hợp lệ
Given: sản phẩm B chưa từng có trong đơn hàng hoặc phiếu nhập nào, chưa từng gắn khuyến mãi và tồn kho mọi biến thể = 0
When: Nhân viên xác nhận xóa sản phẩm B
Then: trong cùng một transaction, hệ thống xóa bản ghi sản phẩm B cùng các dữ liệu con liên kết (biến thể, gallery, liên kết bộ sưu tập, wishlist_item, stock)
And: sau khi commit DB thành công, cache version ở Redis được tăng lên
And: sản phẩm B biến mất hoàn toàn khỏi danh sách quản trị

### AC-17: Quản lý gallery và ảnh đại diện
Given: sản phẩm A có 3 ảnh với thứ tự hiển thị 1, 2, 3
When: Nhân viên đổi ảnh vị trí số 2 lên vị trí số 1 và lưu
Then: ảnh mới ở vị trí số 1 trở thành ảnh đại diện của sản phẩm A
And: các ảnh còn lại được tự động chuẩn hóa thứ tự liên tục 2, 3
And: cache version ở Redis được cập nhật sau khi commit DB

### AC-18: Chặn xóa ảnh cuối cùng khi sản phẩm đang Đang bán
Given: sản phẩm A đang ở trạng thái `ACTIVE` (Đang bán) và chỉ còn đúng 1 ảnh trong gallery
When: Nhân viên thực hiện xóa ảnh đó
Then: hệ thống từ chối xóa ảnh và hiển thị thông báo "Sản phẩm đang Đang bán, bắt buộc phải có ít nhất một ảnh trong bộ ảnh. Vui lòng chuyển sản phẩm sang Ngừng bán trước hoặc tải ảnh thay thế"
And: ảnh đó vẫn được giữ nguyên trong gallery của sản phẩm A

### AC-19: Tìm kiếm, lọc và phân trang danh sách sản phẩm quản trị
Given: hệ thống có 25 sản phẩm khớp đồng thời danh mục "Bikini", trạng thái "Đang bán" và tên chứa từ khóa "Classic", cùng một số sản phẩm khác không khớp (khác danh mục, trạng thái Ngừng bán hoặc không chứa từ khóa "Classic")
When: Nhân viên lọc theo danh mục "Bikini", trạng thái "Đang bán", tìm theo từ khóa "Classic"
Then: hệ thống hiển thị chính xác 25 sản phẩm thỏa mãn đồng thời cả 3 điều kiện tìm kiếm/lọc trên và loại trừ các sản phẩm không khớp
And: danh sách được sắp xếp sản phẩm mới tạo nhất lên đầu (`product_created_at` DESC)
And: phân trang danh sách hiển thị đúng 20 sản phẩm trên trang đầu tiên và 5 sản phẩm ở trang thứ hai

### AC-20: Phân quyền quản lý sản phẩm
Given: người dùng đăng nhập với vai trò Khách hàng, hoặc Admin, hoặc người dùng chưa đăng nhập
When: truy cập vào màn hình hoặc gửi yêu cầu API quản lý sản phẩm
Then: hệ thống từ chối truy cập và chuyển hướng hoặc báo lỗi quyền truy cập

### AC-21: Sản phẩm hỗ trợ 1 danh mục, 1 giới tính và nhiều bộ sưu tập
Given: có danh mục "Bikini", giới tính "Nữ", bộ sưu tập "Hè 2026" và "Biển Xanh"
When: Nhân viên tạo sản phẩm gắn với danh mục "Bikini", giới tính "Nữ" và chọn cả 2 bộ sưu tập trên
Then: sản phẩm được lưu thành công với đúng 1 danh mục, 1 giới tính và 2 liên kết bộ sưu tập

### AC-22: Chặn xóa biến thể cuối cùng của sản phẩm đang Đang bán
Given: sản phẩm A đang ở trạng thái `ACTIVE` (Đang bán) và chỉ còn đúng 1 biến thể duy nhất
When: Nhân viên thực hiện xóa biến thể đó (tại UC-15)
Then: hệ thống từ chối xóa và hiển thị thông báo "Sản phẩm đang Đang bán, không thể xóa biến thể cuối cùng. Vui lòng chuyển sản phẩm sang Ngừng bán trước"
And: biến thể đó vẫn được giữ nguyên trong sản phẩm A

### AC-23: Đồng bộ chống cạnh tranh giữa chuyển Đang bán và sửa dữ liệu con
Given: sản phẩm A đang được xử lý chuyển sang Đang bán trong Transaction T1 (đang giữ khóa FOR UPDATE trên dòng A)
When: một thao tác sửa ảnh hoặc biến thể của A được gửi tới trong Transaction T2
Then: T2 phải chờ Transaction T1 hoàn tất để kiểm tra tính toàn vẹn trên trạng thái mới nhất của A, đảm bảo không có tình trạng mở bán với dữ liệu không hợp lệ

### AC-24: Chặn thêm size mới chưa có giá bán khi sản phẩm cha đang Đang bán
Given: sản phẩm A đang ở trạng thái `ACTIVE` (Đang bán) với các biến thể size S và M đã có giá bán
When: Nhân viên thực hiện thêm biến thể mới có size XL chưa được thiết lập giá bán (tại UC-15)
Then: hệ thống từ chối thêm biến thể và hiển thị thông báo "Sản phẩm đang Đang bán, không thể thêm size mới chưa có giá bán. Vui lòng thiết lập giá cho size XL trước hoặc chuyển sản phẩm sang Ngừng bán"
And: sản phẩm A và danh sách biến thể giữ nguyên không đổi

### AC-25: Sửa sản phẩm giữ nguyên tên chính nó và cạnh tranh đổi tên sang cùng tên
Given: sản phẩm A có tên "Bikini Classic" và sản phẩm B có tên "Bikini Summer"
When: Nhân viên sửa sản phẩm A (đổi mô tả hoặc danh mục) nhưng giữ nguyên tên "Bikini Classic"
Then: hệ thống lưu cập nhật thành công, không báo lỗi trùng tên
And: Khi hai nhân viên đồng thời sửa sản phẩm A thành "Bikini Sport" và sản phẩm B thành "  bikini sport  " trong hai transaction song song
Then: đúng một sản phẩm được cập nhật tên thành công, sản phẩm còn lại bị từ chối với thông báo lỗi E1 "Tên sản phẩm đã tồn tại"

### AC-26: Xử lý lỗi Redis cache version sau khi commit DB thành công
Given: sản phẩm A đang `ACTIVE`, có biến thể `ACTIVE` giá hợp lệ, đang xuất hiện trong cache Hàng mới và Bộ sưu tập UC-09, danh mục UC-10, chi tiết UC-12 và trong top 15 Bán chạy của reporting; các cache công khai còn TTL không quá 5 phút và Redis vẫn đọc được
When: Nhân viên Ngừng bán A, Database Transaction đã commit `product_status = INACTIVE` vào PostgreSQL, nhưng lệnh tăng `catalog_version` ở Redis bị timeout hoặc lỗi kết nối
Then: hệ thống ghi nhận log cảnh báo (warning log) kèm chi tiết lỗi Redis
And: toàn bộ thay đổi dữ liệu trong PostgreSQL được giữ nguyên, tuyệt đối KHÔNG rollback Database Transaction đã commit
And: hệ thống vẫn trả về thông báo thao tác thành công cho Nhân viên
And: các truy vấn đọc trực tiếp Database (tìm kiếm UC-11, wishlist UC-38, giỏ hàng UC-18, đặt hàng UC-19/20, lọc khối bán chạy UC-09) lập tức thấy trạng thái mới nhất từ Database
And: chỉ các dữ liệu đọc từ cache công khai (Hàng mới và Bộ sưu tập UC-09, danh mục UC-10, chi tiết sản phẩm UC-12) chấp nhận có thể cũ (stale cache) tối đa trong thời gian TTL dự phòng còn lại (tối đa 5 phút) hoặc cho đến lần tăng `catalog_version` thành công tiếp theo
And: với thao tác Ngừng bán A, request trang chủ ngay sau commit có thể còn thấy A trong Hàng mới và Bộ sưu tập từ cache cũ, nhưng khối Bán chạy phải loại A ngay qua kiểm tra trạng thái DB hiện hành, dù cache top 15 của reporting vẫn chứa A
And: khi cache cũ hết TTL hoặc phiên bản được tăng thành công, request mới cho Hàng mới và Bộ sưu tập không còn trả A; TTL không tự thay DOM đã mở trên trình duyệt

## Dependencies
- **Upstream UC:**
  - UC-02 Đăng nhập (xác thực quyền Nhân viên quản trị).
  - UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính (cung cấp danh mục và giới tính bắt buộc).
- **Downstream UC:**
  - UC-09 Xem trang chủ (hiển thị sản phẩm mới, khối bán chạy).
  - UC-10 Xem sản phẩm theo danh mục (lọc và duyệt sản phẩm công khai).
  - UC-11 Tìm kiếm sản phẩm (tìm kiếm sản phẩm công khai).
  - UC-12 Xem chi tiết sản phẩm (hiển thị thông tin chi tiết, gallery, giá và chọn biến thể).
  - UC-15 Quản lý biến thể màu × size (tạo các biến thể màu × size cho sản phẩm; tuân thủ bất biến mở bán của sản phẩm cha).
  - UC-16 Quản lý giá bán theo size (định giá cho từng size của sản phẩm để đủ điều kiện mở bán).
  - UC-28 Quản lý khuyến mãi theo sản phẩm (áp dụng mức giảm giá cho sản phẩm).
  - UC-33 Lập phiếu nhập (nhập hàng theo biến thể của sản phẩm).
  - UC-38 Quản lý danh sách yêu thích (khách hàng thả tim sản phẩm).
- **Internal Services:**
  - Module `inventory`: Service kiểm tra giao dịch phiếu nhập (`goods_receipt_detail`), kiểm tra số lượng tồn kho (`stock_quantity`) và dọn bản ghi tồn kho `stock` khi xóa sản phẩm.
  - Module `ordering`: Service kiểm tra giao dịch đơn hàng (`order_detail`).
  - Module `promotion`: Service kiểm tra sản phẩm đã từng gắn khuyến mãi (`product_promotion`).
  - Module `shopping`: Service dọn bản ghi `wishlist_item` khi xóa sản phẩm.
- **External Systems:** không có

## Notes
- **Quy tắc Cache (BR-GIAIDOAN1):** 
  - Khi sản phẩm thay đổi thông tin, đổi trạng thái hoặc bị xóa, hệ thống tăng số phiên bản catalog (`catalog_version`) ở Redis để toàn bộ cache Redis công khai (trang chủ, danh mục, chi tiết) tự động được làm mới ở request tiếp theo. Việc tăng cache version chỉ được thực hiện sau khi Database Transaction đã commit thành công (không gọi Redis trong SQL transaction).
  - Nếu Database Transaction bị rollback: tuyệt đối không gọi Redis tăng `catalog_version`.
  - Nếu Database Transaction commit thành công nhưng Redis bị lỗi/timeout: hệ thống ghi log warning, không rollback DB, vẫn thông báo thành công cho Nhân viên; độ trễ tối đa TTL 5 phút chỉ áp dụng cho dữ liệu thực sự đọc từ cache công khai (Hàng mới, Bộ sưu tập, danh mục, chi tiết). Các truy vấn trực tiếp Database không cache (tìm kiếm, wishlist, giỏ hàng, đặt hàng, lọc khối bán chạy) luôn nhận trạng thái mới nhất từ DB. Cache TTL không tự động làm mới giao diện trình duyệt của khách hàng nếu khách hàng không tải lại trang.
  - Màn hình quản trị sản phẩm tuyệt đối không cache, luôn đọc Database trực tiếp với `Cache-Control: no-store`.
- **Ranh giới Modular Monolith (AGENTS.md):** Module `catalog` không truy cập trực tiếp các bảng của `ordering`, `inventory`, `promotion` hay `shopping`. Việc kiểm tra ràng buộc giao dịch hoặc dọn dữ liệu liên quan được thực hiện qua Service công khai của các module đó.
- **Toàn vẹn Transaction & Đồng bộ chống cạnh tranh (AGENTS.md):** 
  - Mọi thao tác kiểm tra giao dịch/tồn kho và xóa dữ liệu liên quan khi xóa sản phẩm, cũng như thao tác chuyển Đang bán và các thao tác sửa dữ liệu con (ảnh, biến thể, giá), phải chạy trong Database Transaction có khóa dòng sản phẩm cha `catalog.product FOR UPDATE` để chống race condition và bảo toàn tính toàn vẹn trạng thái/giá.
  - Lưu ý quan trọng: Khóa dòng sản phẩm đơn lẻ này (`FOR UPDATE`) chỉ bảo vệ tính nhất quán dữ liệu của chính sản phẩm đó; nó không thể thay thế cho cơ chế bảo đảm tính duy nhất toàn cục của tên sản phẩm (uniqueness giữa các sản phẩm khác nhau). Cơ chế bảo đảm tính duy nhất nguyên tử tên sản phẩm cần giải pháp toàn cục riêng (unique constraint ở database hoặc cơ chế khóa toàn cục tương đương).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Sản phẩm gồm: mã tự nhiên `product_id`, tên, mô tả, trạng thái, 1 danh mục, 1 giới tính, nhiều bộ sưu tập, bộ ảnh (gallery) gắn theo sản phẩm có thứ tự hiển thị (đã chốt 15/11/2026, theo ERD).
- Đánh giá sản phẩm (review) để giai đoạn 2, không làm trong MVP; `product_total_score_review` mặc định 0 (đã chốt 15/11/2026).
- Bảng size không phải trường của sản phẩm; cả cửa hàng dùng một bảng size chung, nội dung cố định (hard-code như trang thông tin) (đã chốt 15/11/2026).
- Sản phẩm có 2 trạng thái: Đang bán (`ACTIVE`) và Ngừng bán (`INACTIVE`). Sản phẩm mới tạo ở trạng thái Ngừng bán. Mã sản phẩm dạng `SP-<4 số tăng dần>` do hệ thống cấp, không cho sửa (đã chốt 22/11/2026, UC-14-Q1).
- Điều kiện mở bán (chuyển sang Đang bán): phải có ít nhất 1 ảnh trong gallery, ít nhất 1 biến thể và mọi size đã được đặt giá bán > 0; tồn kho = 0 vẫn cho phép mở bán (storefront hiển thị "Hết hàng") (đã chốt 22/11/2026, UC-14-Q1).
- Tên sản phẩm là duy nhất trong toàn hệ thống (so sánh không phân biệt hoa/thường dựa trên chuỗi đã trim). Tên lưu trong DB là tên đã được trim, giữ nguyên định dạng chữ hoa/thường người dùng nhập (đã chốt 22/11/2026, UC-14-Q3).
- Bộ ảnh (gallery) có thứ tự liên tục từ 1..N. Ảnh có thứ tự = 1 mặc định là ảnh đại diện trên storefront và quản trị. Đổi vị trí hoặc xóa ảnh sẽ tự động chuẩn hóa lại thứ tự trong Database Transaction (đã chốt 22/11/2026, UC-14-Q4).
- Danh sách quản trị phân trang cố định 20 sản phẩm/trang, sắp xếp mới nhất lên đầu (`product_created_at` DESC), hỗ trợ tìm theo tên hoặc mã SP, lọc kết hợp theo trạng thái, danh mục, giới tính (đã chốt 22/11/2026, UC-14-Q5, UC-14-Q5a).
- Chặn xóa mọi sản phẩm đã từng gắn vào chương trình khuyến mãi theo sản phẩm (`promotion.product_promotion`), kể cả đã kết thúc, do ràng buộc khóa ngoại `[delete: restrict]` tại DBML để bảo toàn lịch sử khuyến mãi; nếu không kinh doanh thì chuyển sang Ngừng bán (đã chốt 22/11/2026, UC-14-Q6).
- Chặn xóa ảnh cuối cùng trong bộ ảnh (gallery) nếu sản phẩm đang ở trạng thái `ACTIVE` (Đang bán) để bảo đảm điều kiện mở bán; không tự động chuyển trạng thái ngầm (đã chốt 22/11/2026, UC-14-Q7).
- Điều kiện mở bán (ít nhất 1 ảnh, ít nhất 1 biến thể tồn tại, mọi size có giá bán > 0) là bất biến trong suốt thời gian sản phẩm ở trạng thái ACTIVE. Hệ thống chặn mọi thao tác làm mất điều kiện mở bán (chặn xóa ảnh cuối cùng, chặn xóa biến thể cuối cùng, chặn thêm biến thể có size mới chưa có giá bán khi sản phẩm đang ACTIVE), yêu cầu nhân viên chuyển sang Ngừng bán trước; hệ thống tuyệt đối không tự động chuyển trạng thái ngầm. Dùng chung cơ chế khóa dòng sản phẩm cha `catalog.product FOR UPDATE` giữa UC-14, UC-15, UC-16 khi ghi để chống race condition (đã chốt 23/11/2026, UC-14-Q8).
- Bảo đảm tính duy nhất nguyên tử của tên sản phẩm lúc ghi trong cùng một Database Transaction (phân biệt tạo mới và sửa giữ nguyên tên chính nó; 2 request gửi đồng thời thì đúng một request thành công và một request báo lỗi E1) (đã chốt 23/11/2026, UC-14-Q9).
- Xử lý lỗi Redis sau khi Database Transaction đã commit: Database commit thành công trước rồi mới gọi Redis tăng `catalog_version`. Nếu Redis bị timeout hoặc lỗi kết nối: ghi log warning, không rollback Database Transaction, vẫn trả thông báo thành công cho Nhân viên; độ trễ tối đa theo TTL dự phòng (5 phút) hoặc lần tăng version thành công tiếp theo chỉ áp dụng cho dữ liệu đọc từ cache công khai (Hàng mới và Bộ sưu tập UC-09, UC-10, UC-12). Các luồng đọc trực tiếp Database không cache (tìm kiếm UC-11, wishlist UC-38, giỏ hàng UC-18, đặt hàng UC-19/20, lọc khối bán chạy UC-09) luôn thấy trạng thái mới nhất ngay sau khi DB commit. Nếu Database Transaction bị rollback thì tuyệt đối không gọi Redis tăng `catalog_version`. Cache TTL không tự động làm mới giao diện trình duyệt của khách hàng nếu khách hàng không tải lại trang (đã chốt 23/11/2026, UC-14-Q10).

### Giả định [GD]
- [GD] UC-14-Q11 (review PR #7, mục 3): Cần developer chốt phạm vi "sản phẩm đã nhập kho chỉ được sửa mô tả": khóa cả giá/trạng thái/thêm biến thể hay chỉ thông tin sản phẩm, gallery và tên taxonomy liên quan? Mốc khóa là có phiếu CONFIRMED hay mọi liên kết phiếu nhập kể cả DRAFT/CANCELLED? Chưa áp dụng quy tắc mới vào Flow/AC trước khi chốt vì có thể thay thế hành vi đã duyệt tại UC-15/16; UC-17-Q7 phụ thuộc cùng quyết định.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt chỉ Nhân viên quản lý sản phẩm
- v3 (2026-11-15): theo ERD — thông tin sản phẩm gồm 1 danh mục, 1 giới tính, nhiều bộ sưu tập, gallery có thứ tự; review để giai đoạn 2; thêm AC-10 → AC-12
- v4 (2026-11-15): chốt bảng size chung cố định, bỏ bảng size khỏi thông tin sản phẩm
- v5 (2026-11-22): chốt các nguyên tắc cơ bản (cấp mã SP-xxxx tự nhiên, điều kiện mở bán, tính duy nhất tên sản phẩm, thứ tự gallery và ảnh đại diện).
- v6 (2026-11-22): rà soát theo phản hồi của Coordinator: chuẩn hóa preconditions; bổ sung trim tên và validation độ dài 255 ký tự; đưa toàn bộ kiểm tra và thao tác xóa vào cùng 1 Database Transaction với nhánh rollback bảo toàn dữ liệu; tách riêng commit DB trước khi tăng Redis cache version; gắn nhãn [GD] cho các câu hỏi mở.
- v7 (2026-11-22): chốt toàn bộ các câu hỏi mở theo phê duyệt của developer (UC-14-Q5a: 20 sản phẩm/trang; UC-14-Q6: chặn xóa sản phẩm đã từng gắn khuyến mãi do ràng buộc DBML [delete: restrict]; UC-14-Q7: chặn xóa ảnh cuối cùng của sản phẩm đang ACTIVE).
- v8 (2026-11-23): rà soát logic vòng 2 (phát hiện #1 và #4): bổ sung nguyên tắc bất biến điều kiện mở bán trong suốt thời gian sản phẩm ACTIVE, cơ chế khóa dòng cha FOR UPDATE chống race condition cạnh tranh giữa mở bán và sửa con; chuẩn hóa kiểm tra duy nhất nguyên tử tên sản phẩm lúc ghi (phân biệt create/update), phân biệt rõ với khóa dòng đơn lẻ; bổ sung AC-3b cạnh tranh tên, AC-22 chặn xóa biến thể cuối cùng, AC-23 đồng bộ chống race condition; mở hai câu hỏi [GD] UC-14-Q8 và UC-14-Q9; chuyển Status sang draft.
- v9 (2026-11-23): developer phê duyệt chốt dứt điểm vòng 2 (UC-14-Q8: điều kiện mở bán là bất biến suốt khi ACTIVE, chặn mọi thao tác làm mất điều kiện và yêu cầu Ngừng bán trước, không tự đổi trạng thái ngầm, đồng bộ qua khóa dòng cha FOR UPDATE; UC-14-Q9: bảo đảm tính duy nhất nguyên tử tên sản phẩm lúc ghi); gỡ bỏ toàn bộ nhãn [GD]; chuyển Status sang ready.
- v10 (2026-11-23): rà soát theo ý kiến Coordinator: làm rõ quy trình nguyên tử trong CÙNG một transaction ở Main 5 và Alt 2a.3, quy trình xuyên suốt giữ khóa từ trước kiểm tra đến commit ở Main 9-10; làm rõ điều kiện là có ít nhất 1 biến thể tồn tại (không bắt buộc biến thể ACTIVE); bổ sung AC-24 (chặn thêm size mới chưa có giá khi parent ACTIVE) và AC-25 (sửa giữ nguyên tên chính nó và cạnh tranh đổi tên), nâng tổng số AC lên 26 AC (AC-1..AC-3, AC-3b, AC-4..AC-25) mà không renumber.
- v11 (2026-11-23): rà soát logic vòng 3 (phát hiện #2): developer phê duyệt chốt dứt điểm UC-14-Q10; bổ sung nhánh xử lý lỗi Redis timeout/mất kết nối sau khi Database Transaction đã commit (ghi log warning, giữ nguyên DB, báo thành công cho nhân viên); làm rõ độ trễ TTL 5 phút chỉ áp dụng dữ liệu cache công khai, các luồng không cache (tìm kiếm, wishlist, mua hàng, khối bán chạy) luôn đọc trạng thái DB mới nhất; làm rõ không tăng version khi DB rollback; thêm Exception E9, AC-26; gỡ bỏ toàn bộ nhãn [GD]; chuyển Status sang ready.
- v12 (2026-11-23): sửa review PR #7 mục 2/4: phân biệt điều kiện mở bán với hiển thị danh sách qua AC-6/AC-6b; bổ sung Hàng mới và Bộ sưu tập vào phạm vi cache và AC-26. Mở UC-14-Q11, giữ draft chờ chốt phạm vi khóa sản phẩm đã nhập kho (mục 3).
