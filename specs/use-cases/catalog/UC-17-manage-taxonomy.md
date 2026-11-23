# UC-17: Quản lý danh mục, bộ sưu tập và thuộc tính

## Metadata
- **ID:** UC-17
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Danh mục, Bộ sưu tập, Giới tính, Màu hoặc Size trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập vào portal quản trị với vai trò Nhân viên (UC-02).

## Main Flow
1. Nhân viên chọn loại cần quản lý: Danh mục, Bộ sưu tập, Giới tính, Màu hoặc Size.
2. Hệ thống hiển thị danh sách hiện có của loại đó (tên mục và số lượng sản phẩm hoặc biến thể đang liên kết).
3. Nhân viên chọn thêm mới và nhập tên mục (ví dụ Giới tính: Nữ, Nam; Màu: Đỏ, Xanh; Size: S, M, L).
4. Hệ thống chuẩn hóa tên (cắt khoảng trắng đầu/cuối - trim, gom nhiều khoảng trắng liên tiếp bên trong thành một khoảng trắng đơn) và kiểm tra dữ liệu:
   - Tên không được để trống (xem E1).
   - Độ dài tên không vượt quá quy định: tối đa 255 ký tự với Danh mục và Bộ sưu tập; tối đa 50 ký tự với Giới tính, Màu và Size (xem E1).
   - Tên không trùng lặp (so sánh không phân biệt hoa/thường - case-insensitive) với các mục đã có trong cùng loại (xem E1).
5. Hệ thống lưu bản ghi mới vào cơ sở dữ liệu PostgreSQL trong một transaction:
   - Việc kiểm tra trùng tên trên chuỗi đã chuẩn hóa (không phân biệt hoa/thường) phải được đảm bảo nguyên tử khi ghi (kể cả khi có thao tác đồng thời tạo mục cùng tên). Nếu trùng tên hoặc lỗi kết nối, transaction rollback, hệ thống dừng xử lý, không tăng phiên bản cache, chuyển sang E1 hoặc báo lỗi hệ thống.
   - Sau khi cơ sở dữ liệu commit thành công: hệ thống gửi lệnh tăng số phiên bản catalog (`catalog_version`) tới Redis để làm mới cache storefront. Nếu Redis gặp sự cố, hệ thống xử lý theo E4.
6. Hệ thống hiển thị thông báo thêm thành công và cập nhật danh sách hiển thị.

## Alternative Flows
- **3a. Sửa tên mục:**
  1. Tại danh sách của loại đang chọn, Nhân viên chọn sửa một mục và nhập tên mới.
  2. Hệ thống chuẩn hóa (cắt khoảng trắng thừa đầu/cuối và gom khoảng trắng nội bộ) và kiểm tra tên mới như bước 4 của Main Flow (không trống, đúng giới hạn độ dài, không trùng với các mục khác trong cùng loại).
  3. Hệ thống cập nhật tên mới vào cơ sở dữ liệu PostgreSQL:
     - Đối với Màu và Size, hệ thống chỉ đổi tên hiển thị, giữ nguyên mã SKU (`variant_id`) bất biến của các biến thể đã tạo trước đó; các màn hình hiển thị tự động cập nhật tên mới qua liên kết khóa ngoại.
     - Việc kiểm tra trùng tên không phân biệt hoa/thường trên chuỗi đã chuẩn hóa được đảm bảo nguyên tử khi ghi. Nếu cập nhật cơ sở dữ liệu thất bại (kể cả do thao tác đồng thời dẫn đến trùng tên): transaction rollback, dừng xử lý, chuyển sang E1 hoặc báo lỗi hệ thống.
  4. Sau khi cơ sở dữ liệu commit thành công, hệ thống gửi lệnh tăng số phiên bản catalog (`catalog_version`) tới Redis để làm mới cache storefront (nếu Redis lỗi, xem E4).
  5. Hệ thống hiển thị thông báo sửa thành công và cập nhật lại danh sách.
- **3b. Xóa mục chưa được sử dụng:**
  1. Nhân viên chọn xóa một mục hiển thị chưa có sản phẩm hoặc biến thể nào liên kết.
  2. Hệ thống hiển thị hộp thoại yêu cầu xác nhận xóa.
  3. Nhân viên xác nhận xóa.
  4. Hệ thống thực hiện xóa bản ghi trong cơ sở dữ liệu PostgreSQL:
     - Tại thời điểm xóa, cơ sở dữ liệu kiểm tra ràng buộc toàn vẹn khóa ngoại (`ON DELETE RESTRICT`). Nếu có sản phẩm hoặc biến thể liên kết phát sinh đồng thời từ request khác, cơ sở dữ liệu từ chối xóa, transaction rollback và chuyển sang E2.
  5. Sau khi cơ sở dữ liệu commit xóa thành công, hệ thống gửi lệnh tăng số phiên bản catalog (`catalog_version`) tới Redis để làm mới cache storefront (nếu Redis lỗi, xem E4).
  6. Hệ thống hiển thị thông báo xóa thành công và loại bỏ mục khỏi danh sách hiển thị.
- **3c. Xóa mục đang được sản phẩm hoặc biến thể sử dụng:** xem E2.
- **1a. Người dùng không có quyền truy cập:** xem E3.

## Exceptions
- **E1. Tên không hợp lệ (trống, vượt quá độ dài hoặc trùng tên):**
  - Tên để trống sau khi chuẩn hóa: hệ thống báo lỗi "Tên không được để trống".
  - Tên vượt quá độ dài tối đa (256 ký tự trở lên với Danh mục/Bộ sưu tập; 51 ký tự trở lên với Giới tính/Màu/Size): hệ thống báo lỗi "Tên vượt quá độ dài cho phép".
  - Tên trùng (so sánh không phân biệt hoa/thường trên chuỗi đã chuẩn hóa, được đảm bảo nguyên tử khi ghi kể cả khi có thao tác đồng thời): hệ thống không lưu và báo lỗi "Tên đã tồn tại".
  - Cơ sở dữ liệu không lưu thay đổi; hệ thống giữ nguyên dữ liệu đang nhập để Nhân viên chỉnh sửa.
- **E2. Xóa mục đang được sử dụng (phát hiện trước hoặc tại thời điểm xóa trong DB):**
  - Đối với Danh mục, Bộ sưu tập, Giới tính: Nếu đang có ít nhất 1 sản phẩm liên kết (kể cả liên kết mới tạo đồng thời), hệ thống từ chối xóa, rollback dữ liệu và báo lỗi: "Đang có {N} sản phẩm thuộc danh mục này, không thể xóa" (hoặc "Đang có {N} sản phẩm gắn bộ sưu tập này, không thể xóa", "Đang có {N} sản phẩm thuộc giới tính này, không thể xóa").
  - Đối với Size, Màu: Nếu đang có ít nhất 1 biến thể liên kết, hệ thống từ chối xóa, rollback dữ liệu và báo lỗi: "Đang có {N} biến thể đang sử dụng mục này, không thể xóa".
  - Dữ liệu trong cơ sở dữ liệu được bảo toàn nguyên vẹn.
- **E3. Sai vai trò hoặc chưa đăng nhập:**
  - Người dùng có vai trò Admin truy cập chức năng: hệ thống từ chối truy cập và báo "Chức năng chỉ dành cho Nhân viên" (HTTP 403).
  - Người dùng chưa đăng nhập hoặc có vai trò Khách hàng: hệ thống chuyển hướng về trang đăng nhập của portal quản trị (UC-02).
- **E4. Lỗi kết nối Redis khi làm mới cache:**
  - Cơ sở dữ liệu đã commit thành công nhưng việc gửi lệnh tăng `catalog_version` tới Redis thất bại (mất kết nối hoặc timeout): hệ thống ghi log cảnh báo (warning log), không rollback cơ sở dữ liệu, vẫn trả về thông báo thành công cho Nhân viên. Dữ liệu cache cũ trên storefront sẽ tự động làm mới khi hết hạn TTL dự phòng 5 phút hoặc ở lần cập nhật catalog thành công tiếp theo.

## Postconditions
- Mục Danh mục, Bộ sưu tập, Giới tính, Màu hoặc Size được tạo mới, cập nhật tên hoặc xóa thành công khỏi cơ sở dữ liệu PostgreSQL.
- Khi cập nhật Redis thành công: số phiên bản catalog (`catalog_version`) trong Redis được tăng lên, làm mới cache dữ liệu công khai trên storefront (dữ liệu mới hiển thị ngay trên menu, bộ lọc và trang sản phẩm storefront).
- Khi Redis gặp sự cố: xử lý theo ngoại lệ E4 (cơ sở dữ liệu đã commit thành công, giao diện báo thành công cho Nhân viên; dữ liệu cache cũ trên storefront sẽ tự động làm mới khi hết hạn TTL dự phòng 5 phút khi Redis còn truy xuất được).
- Khi đổi tên Màu hoặc Size: các biến thể cũ giữ nguyên mã SKU (`variant_id`).
- Dữ liệu mới/cập nhật được dùng ngay khi tạo/sửa sản phẩm (UC-14), biến thể (UC-15) trong portal quản trị.

## Acceptance Criteria

### AC-1: Thêm danh mục thành công
Given: chưa có danh mục "Đồ bơi liền thân"
When: Nhân viên nhập "Đồ bơi liền thân" và bấm lưu
Then: danh mục được lưu thành công vào cơ sở dữ liệu, hiển thị trong danh sách quản trị và xuất hiện trong menu danh mục của storefront

### AC-2: Chặn thêm trùng tên (không phân biệt hoa/thường)
Given: đã có danh mục "Bikini"
When: Nhân viên thêm danh mục "bikini" (chữ thường)
Then: hệ thống không lưu vào cơ sở dữ liệu và báo lỗi "Tên đã tồn tại"

### AC-3: Chuẩn hóa khoảng trắng đầu/cuối và gom khoảng trắng nội bộ
Given: chưa có bộ sưu tập "Hè 2026"
When: Nhân viên nhập tên "  Hè     2026   " (có khoảng trắng thừa ở đầu, cuối và giữa) và bấm lưu
Then: bộ sưu tập được lưu vào cơ sở dữ liệu với tên chuẩn hóa chính xác là "Hè 2026"

### AC-4: Chặn tên để trống
Given: Nhân viên đang thêm mới mục Màu
When: Nhân viên để trống ô tên (hoặc chỉ nhập khoảng trắng) và bấm lưu
Then: hệ thống không lưu vào cơ sở dữ liệu và báo lỗi "Tên không được để trống"

### AC-5: Thêm bộ sưu tập thành công
Given: Nhân viên đang ở mục Bộ sưu tập
When: Nhân viên thêm bộ sưu tập "Hè 2026"
Then: bộ sưu tập "Hè 2026" xuất hiện trong danh sách và chọn được khi tạo hoặc sửa sản phẩm (UC-14)

### AC-6: Thêm màu thành công
Given: Nhân viên đang ở mục Màu
When: Nhân viên thêm màu "Vàng"
Then: màu "Vàng" xuất hiện trong danh sách và chọn được khi tạo biến thể (UC-15)

### AC-7: Thêm giới tính thành công
Given: Nhân viên đang ở mục Giới tính
When: Nhân viên thêm giới tính "Trẻ em"
Then: giới tính "Trẻ em" xuất hiện trong danh sách, chọn được khi tạo sản phẩm (UC-14) và xuất hiện trong bộ lọc (UC-10)

### AC-8: Thêm size thành công
Given: Nhân viên đang ở mục Size
When: Nhân viên thêm size "XL"
Then: size "XL" xuất hiện trong danh sách, chọn được khi tạo biến thể (UC-15) và xuất hiện trong bộ lọc (UC-10)

### AC-9: Sửa tên danh mục thành công
Given: danh mục "Bikini" đang có 3 sản phẩm
When: Nhân viên đổi tên thành "Đồ bơi hai mảnh" và lưu
Then: danh mục được cập nhật tên mới trong cơ sở dữ liệu và danh sách quản trị
And: 3 sản phẩm đang gắn danh mục này tự động hiển thị tên danh mục mới trên storefront

### AC-10: Chặn sửa tên trùng với mục khác cùng loại
Given: đã có màu "Đỏ" và màu "Xanh"
When: Nhân viên sửa màu "Xanh" thành "đỏ"
Then: hệ thống không lưu vào cơ sở dữ liệu và báo lỗi "Tên đã tồn tại"

### AC-11: Sửa tên màu hoặc size giữ nguyên mã SKU biến thể cũ
Given: sản phẩm SP-0001 có biến thể với mã SKU là "SP-0001-DO-M" (gắn với màu "Đỏ" và size "M")
When: Nhân viên sửa tên màu "Đỏ" thành "Đỏ đô" và sửa tên size "M" thành "Medium"
Then: tên hiển thị của màu đổi thành "Đỏ đô", tên hiển thị của size đổi thành "Medium"
And: mã SKU của biến thể vẫn giữ nguyên không đổi là "SP-0001-DO-M"

### AC-12: Chặn xóa danh mục đang có sản phẩm
Given: danh mục "Bikini" đang có 3 sản phẩm liên kết
When: Nhân viên xóa danh mục "Bikini"
Then: hệ thống từ chối xóa và báo lỗi "Đang có 3 sản phẩm thuộc danh mục này, không thể xóa"
And: danh mục "Bikini" và 3 sản phẩm liên quan được giữ nguyên trong cơ sở dữ liệu

### AC-13: Chặn xóa bộ sưu tập đang có sản phẩm
Given: bộ sưu tập "Hè 2026" đang gắn với 2 sản phẩm
When: Nhân viên xóa bộ sưu tập "Hè 2026"
Then: hệ thống từ chối xóa và báo lỗi "Đang có 2 sản phẩm gắn bộ sưu tập này, không thể xóa"

### AC-14: Chặn xóa giới tính đang có sản phẩm
Given: giới tính "Nữ" đang gắn với 5 sản phẩm
When: Nhân viên xóa giới tính "Nữ"
Then: hệ thống từ chối xóa và báo lỗi "Đang có 5 sản phẩm thuộc giới tính này, không thể xóa"

### AC-15: Chặn xóa màu đang có biến thể
Given: màu "Đỏ" đang được 4 biến thể sử dụng
When: Nhân viên xóa màu "Đỏ"
Then: hệ thống từ chối xóa và báo lỗi "Đang có 4 biến thể đang sử dụng mục này, không thể xóa"

### AC-16: Chặn xóa size đang có biến thể
Given: size "M" đang được 6 biến thể sử dụng
When: Nhân viên xóa size "M"
Then: hệ thống từ chối xóa và báo lỗi "Đang có 6 biến thể đang sử dụng mục này, không thể xóa"

### AC-17: Xóa mục chưa được sử dụng
Given: bộ sưu tập "Thu 2026" chưa gắn với sản phẩm nào
When: Nhân viên xác nhận xóa "Thu 2026"
Then: bộ sưu tập bị xóa khỏi cơ sở dữ liệu và biến mất khỏi danh sách quản trị

### AC-18: Phân quyền - Chặn Admin truy cập
Given: người dùng đang đăng nhập với vai trò Admin
When: người dùng truy cập trang quản lý danh mục/thuộc tính
Then: hệ thống từ chối truy cập và hiển thị thông báo "Chức năng chỉ dành cho Nhân viên"

### AC-19: Phân quyền - Chặn người dùng chưa đăng nhập hoặc Khách hàng
Given: người dùng chưa đăng nhập hoặc đăng nhập với vai trò Khách hàng
When: người dùng truy cập đường dẫn quản lý danh mục/thuộc tính
Then: hệ thống chuyển hướng người dùng về trang đăng nhập của portal quản trị

### AC-20: Tăng phiên bản catalog làm mới cache storefront khi cập nhật
Given: người dùng đang xem menu danh mục trên storefront từ cache Redis
When: Nhân viên thêm thành công danh mục "Phụ kiện bơi"
Then: cơ sở dữ liệu lưu thành công và hệ thống tăng số phiên bản `catalog_version` trong Redis
And: người dùng tải lại trang storefront sẽ thấy ngay danh mục "Phụ kiện bơi"

### AC-21: Chặn tên Danh mục/Bộ sưu tập vượt quá 255 ký tự
Given: Nhân viên đang thêm mới Danh mục
When: Nhân viên nhập tên danh mục dài 256 ký tự và bấm lưu
Then: hệ thống từ chối lưu vào cơ sở dữ liệu và báo lỗi "Tên vượt quá độ dài cho phép"

### AC-22: Chặn tên Giới tính/Màu/Size vượt quá 50 ký tự
Given: Nhân viên đang thêm mới Size
When: Nhân viên nhập tên size dài 51 ký tự và bấm lưu
Then: hệ thống từ chối lưu vào cơ sở dữ liệu và báo lỗi "Tên vượt quá độ dài cho phép"

### AC-23: Chặn xóa khi có liên kết phát sinh đồng thời
Given: danh mục "Phụ kiện" ban đầu chưa có sản phẩm nào
When: Nhân viên bấm xác nhận xóa "Phụ kiện", nhưng ngay trước thời điểm xóa có một sản phẩm mới được tạo gắn vào danh mục này
Then: cơ sở dữ liệu từ chối xóa do vi phạm ràng buộc khóa ngoại
And: hệ thống rollback transaction và hiển thị thông báo lỗi "Đang có 1 sản phẩm thuộc danh mục này, không thể xóa"

### AC-24: Xử lý lỗi Redis sau khi cơ sở dữ liệu đã commit thành công
Given: kết nối Redis gặp sự cố (mất kết nối hoặc timeout)
When: Nhân viên thêm danh mục "Kính bơi" và cơ sở dữ liệu đã commit thành công
Then: hệ thống ghi log cảnh báo lỗi Redis và vẫn trả về thông báo thêm thành công cho Nhân viên
And: dữ liệu "Kính bơi" đã được lưu vĩnh viễn trong cơ sở dữ liệu; storefront sẽ nhận dữ liệu mới khi hết hạn TTL 5 phút của Redis

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** UC-09 Xem trang chủ, UC-10 Xem sản phẩm theo danh mục, UC-11 Tìm kiếm sản phẩm, UC-12 Xem chi tiết sản phẩm, UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size
- **External Systems:** Redis (cache `catalog_version`)

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung): Danh mục và thuộc tính sản phẩm công khai được cache ở Redis theo `catalog_version`. Mọi thao tác thêm, sửa, xóa thành công đều commit DB trước rồi mới gửi lệnh tăng `catalog_version` để làm mới cache trên storefront.
- Trình tự xử lý lỗi hạ tầng: SQL commit thành công là nguồn sự thật duy nhất (source of truth). Nếu Redis lỗi sau khi DB đã commit, không rollback DB mà dựa vào TTL 5 phút của Redis để tự khôi phục dữ liệu cache.
- Out of Scope (BR-GIAIDOAN1): Mega menu, danh mục phân cấp nhiều tầng (chỉ dùng danh mục 1 cấp).

### Quyết định đã chốt
- Phân loại gồm 5 loại: danh mục, bộ sưu tập, giới tính, màu, size; mỗi loại là một danh sách tên (theo ERD, đã chốt 15/11/2026).
- Thuộc tính sản phẩm gồm giới tính, màu, size (theo ERD, đã chốt 15/11/2026).
- Mỗi sản phẩm thuộc 1 danh mục, 1 giới tính và nhiều bộ sưu tập; biến thể = màu × size (theo ERD, đã chốt 15/11/2026).
- Danh mục một cấp, không có danh mục con (đã chốt 22/11/2026).
- Quy tắc chặn xóa mục đang dùng: Danh mục, Bộ sưu tập, Giới tính bị chặn khi có sản phẩm đang liên kết; Màu, Size bị chặn khi có biến thể đang liên kết; thông báo cụ thể số lượng đang sử dụng (đã chốt 22/11/2026, UC-17-Q1).
- Chuẩn hóa tên: tự động trim khoảng trắng thừa đầu/cuối và gom khoảng trắng liên tiếp bên trong; so sánh trùng tên không phân biệt hoa/thường (case-insensitive); độ dài tối đa 255 ký tự với Danh mục/Bộ sưu tập, 50 ký tự với Giới tính/Màu/Size (đã chốt 22/11/2026, UC-17-Q2).
- Đổi tên Màu hoặc Size chỉ cập nhật tên hiển thị, giữ nguyên mã SKU (`variant_id`) bất biến của các biến thể đã tạo trước đó (đã chốt 22/11/2026, UC-17-Q3).
- Thêm/sửa/xóa taxonomy thành công sẽ tăng `catalog_version` trong Redis để làm mới cache storefront (đã chốt 22/11/2026, UC-17-Q4).
- Phân quyền: Chỉ tài khoản vai trò Nhân viên được truy cập và thao tác; Admin và Khách hàng bị chặn (đã chốt 22/11/2026, UC-17-Q5).
- Kiểm tra toàn vẹn xóa và trùng tên tại thời điểm thực thi trong DB: xử lý race condition khi xóa bằng ràng buộc khóa ngoại RESTRICT; việc kiểm tra trùng tên không phân biệt hoa/thường trên chuỗi đã chuẩn hóa phải được đảm bảo tính nguyên tử khi ghi (không dựa đơn thuần vào ràng buộc varchar UNIQUE case-sensitive của DB để chống trùng đồng thời Bikini/bikini), bảo toàn hành vi E1 nếu có thao tác đồng thời (chốt 22/11/2026).
- Xử lý lỗi Redis sau khi commit DB: ghi log cảnh báo, không rollback DB, vẫn thông báo thành công cho Nhân viên; cache storefront tự làm mới qua cơ chế TTL dự phòng 5 phút (đã chốt 22/11/2026, UC-17-Q6).

### Giả định [GD]
*(Không còn giả định mở chưa giải quyết)*

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): theo ERD — phân loại gồm danh mục, bộ sưu tập, giới tính, màu, size; chốt thuộc tính sản phẩm; thêm AC-5, AC-6
- v3 (2026-11-22): chốt toàn bộ các câu hỏi mở UC-17-Q1 → UC-17-Q5 với developer: quy tắc chặn xóa chi tiết theo sản phẩm/biến thể, chuẩn hóa trim và kiểm tra trùng case-insensitive, giữ nguyên SKU biến thể khi đổi tên màu/size, tăng catalog_version làm mới cache Redis, bổ sung luồng và AC phân quyền.
- v4 (2026-11-22): hoàn thiện xử lý lỗi DB/Redis (tách biệt commit DB trước khi tăng Redis version), kiểm tra ràng buộc concurrency tại thời điểm xóa/sửa trong DB; bổ sung AC-21 (256 ký tự), AC-22 (51 ký tự), AC-23 (concurrency delete) và AC-24 (lỗi Redis); mở câu hỏi UC-17-Q6.
- v5 (2026-11-22): chốt câu hỏi UC-17-Q6 với developer — xử lý lỗi Redis sau khi commit DB bằng cảnh báo log và tận dụng TTL 5 phút, gỡ toàn bộ nhãn [GD] trong UC-17.
- v6 (2026-11-22): làm rõ postconditions theo nhánh thành công/lỗi Redis (E4); chuẩn hóa diễn đạt kiểm tra trùng tên case-insensitive nguyên tử khi ghi; cập nhật Status: ready.
