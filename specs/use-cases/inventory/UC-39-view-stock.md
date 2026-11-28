# UC-39: Xem tồn kho

## Metadata
- **ID:** UC-39
- **Module:** inventory
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình tồn kho trong khu vực quản trị.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên mở màn hình tồn kho.
2. Hệ thống kiểm tra phiên đăng nhập còn hiệu lực và vai trò Nhân viên ở mỗi request xem danh sách, kể cả tìm kiếm, lọc và chuyển trang.
3. Hệ thống đọc tồn kho hiện tại theo biến thể từ Database (`inventory.stock`), lấy tên sản phẩm, màu, size và danh mục qua service công khai của catalog. Danh sách bao gồm cả sản phẩm/biến thể ngừng bán và biến thể tồn 0.
4. Hệ thống sắp xếp theo tên sản phẩm, khi trùng tên thì theo SKU (`catalog.variant.variant_id`); cả hai tăng dần. Danh sách được phân trang 20 biến thể/trang.
5. Hệ thống hiển thị trang đầu với tên sản phẩm, màu, size, số lượng tồn; đánh dấu các biến thể tồn ≤ 5 (bao gồm tồn 0), không hiển thị giá vốn và không có thao tác sửa tay tồn kho. Response trả `Cache-Control: no-store`.

## Alternative Flows
- **3a. Tìm theo tên sản phẩm:** Nhân viên nhập từ khóa → hệ thống tìm tên sản phẩm chứa từ khóa, không phân biệt hoa/thường nhưng có phân biệt dấu; tiếp tục bước 4–5 với kết quả tìm kiếm.
- **3b. Lọc theo danh mục:** Nhân viên chọn danh mục → hệ thống chỉ lấy biến thể của sản phẩm thuộc danh mục đó; tiếp tục bước 4–5 với kết quả lọc.
- **3c. Kết hợp tìm kiếm và lọc:** Nhân viên nhập từ khóa đồng thời chọn danh mục → hệ thống chỉ lấy biến thể thỏa cả hai điều kiện; tiếp tục bước 4–5 với kết quả kết hợp.
- **3d. Không có kết quả:** chưa có biến thể nào hoặc từ khóa/bộ lọc không khớp biến thể nào → hệ thống hiển thị danh sách trống kèm thông báo "Không tìm thấy biến thể".
- **5a. Chuyển trang:** Nhân viên chọn trang khác → hệ thống thực hiện lại bước 2–4 với từ khóa và danh mục đang áp dụng, hiển thị trang được chọn theo bước 5.
- **5b. Mở lại hoặc tải lại màn hình:** hệ thống thực hiện lại bước 2–5, đọc số lượng tồn mới nhất đã được lưu sau đặt hàng (UC-19, UC-20), hủy đơn (UC-22, UC-24), xác nhận phiếu nhập (UC-34) hoặc giao không thành công (UC-35).

## Exceptions
- **E1. Vai trò không được phép:** Khách hàng hoặc Admin truy cập màn hình tồn kho → hệ thống từ chối.
- **E2. Cố sửa tồn kho:** màn hình chỉ để xem, không có thao tác sửa số lượng tồn; mọi yêu cầu sửa tay tồn kho bị từ chối.
- **E3. Chưa đăng nhập hoặc phiên hết hạn:** hệ thống không hiển thị dữ liệu tồn kho, yêu cầu đăng nhập lại ở portal quản trị (UC-02).

## Postconditions
- Không thay đổi dữ liệu nghiệp vụ; chỉ hiển thị tồn kho đọc từ Database tại thời điểm xử lý request.

## Acceptance Criteria

### AC-1: Xem danh sách tồn kho
Given: biến thể "Áo bơi A – Đỏ – M" tồn 30, "Áo bơi A – Xanh – L" tồn 0
When: Nhân viên mở màn hình tồn kho
Then: danh sách hiển thị cả hai biến thể với tên sản phẩm, màu, size và số lượng tồn 30 và 0

### AC-2: Tìm theo tên sản phẩm
Given: có biến thể của "Áo bơi A" và "Quần bơi B"
When: Nhân viên tìm "bƠi a"
Then: chỉ hiển thị các biến thể của "Áo bơi A"

### AC-3: Lọc theo danh mục
Given: "Áo bơi A" thuộc danh mục "Bikini", "Quần bơi B" thuộc danh mục "Quần bơi"
When: Nhân viên lọc danh mục "Bikini"
Then: chỉ hiển thị các biến thể của sản phẩm thuộc "Bikini"

### AC-4: Đánh dấu tồn kho thấp
Given: ngưỡng tồn kho thấp hard-code là 5; biến thể W tồn 0, X tồn 3, Y tồn 5, Z tồn 6
When: Nhân viên mở màn hình tồn kho
Then: biến thể W, X và Y được đánh dấu tồn kho thấp, biến thể Z không

### AC-5: Không tìm thấy
Given: chưa có biến thể nào, hoặc từ khóa/danh mục đang chọn không khớp biến thể nào
When: Nhân viên mở danh sách tồn kho tương ứng
Then: hệ thống hiển thị "Không tìm thấy biến thể"
And: danh sách không có dòng dữ liệu

### AC-6: Vai trò không được phép
Given: người dùng đăng nhập với vai trò Khách hàng hoặc Admin
When: người dùng truy cập màn hình tồn kho
Then: hệ thống từ chối truy cập

### AC-7: Tồn kho cập nhật sau khi xác nhận phiếu nhập
Given: biến thể X tồn 10
When: một phiếu nhập 20 cái biến thể X được xác nhận (UC-34), sau đó Nhân viên mở màn hình tồn kho
Then: biến thể X hiển thị tồn 30

### AC-8: Phân trang và sắp xếp
Given: có 21 biến thể thuộc các sản phẩm có tên khác nhau; dữ liệu không thay đổi giữa các lần xem
When: Nhân viên mở danh sách tồn kho và chuyển từ trang 1 sang trang 2
Then: trang 1 hiển thị 20 biến thể đầu theo tên sản phẩm tăng dần, trang 2 hiển thị biến thể còn lại
And: không có biến thể bị lặp hoặc bỏ sót giữa hai trang

### AC-9: Kết hợp tìm kiếm và lọc danh mục
Given: có "Áo bơi A" thuộc danh mục "Bikini", "Áo bơi B" thuộc danh mục "Quần bơi" và "Bộ C" thuộc danh mục "Bikini"
When: Nhân viên tìm "áo bơi" đồng thời lọc danh mục "Bikini"
Then: chỉ hiển thị các biến thể của "Áo bơi A"

### AC-10: Không hiển thị giá vốn
Given: biến thể X có tồn 10 và giá vốn 120.000đ
When: Nhân viên mở màn hình tồn kho
Then: danh sách hiển thị số lượng tồn 10 nhưng không hiển thị giá vốn

### AC-11: Hiển thị hàng ngừng bán
Given: sản phẩm A đã ngừng bán có biến thể X tồn 10; sản phẩm B có biến thể Y đã ngừng bán tồn 0
When: Nhân viên mở màn hình tồn kho
Then: danh sách vẫn hiển thị biến thể X tồn 10 và biến thể Y tồn 0

### AC-12: Tìm kiếm có phân biệt dấu
Given: có biến thể của "Áo bơi A", không có sản phẩm nào có tên chứa "boi a"
When: Nhân viên tìm "boi a"
Then: hệ thống hiển thị "Không tìm thấy biến thể", không trả về các biến thể của "Áo bơi A"

### AC-13: Phân trang khi tên sản phẩm trùng nhau
Given: có 21 biến thể cùng tên sản phẩm, mỗi biến thể có SKU duy nhất; dữ liệu không thay đổi giữa các lần xem
When: Nhân viên xem trang 1, trang 2 rồi mở lại trang 1
Then: trang 1 luôn chứa 20 biến thể đầu theo SKU tăng dần, trang 2 chứa biến thể còn lại
And: không có biến thể bị lặp hoặc bỏ sót giữa hai trang

### AC-14: Giữ điều kiện tìm kiếm và lọc khi chuyển trang
Given: có 21 biến thể thỏa đồng thời từ khóa và danh mục đang chọn, cùng các biến thể khác không thỏa điều kiện
When: Nhân viên chuyển từ trang 1 sang trang 2 của kết quả
Then: trang 2 chỉ hiển thị biến thể còn lại thỏa cả hai điều kiện
And: từ khóa và danh mục đang áp dụng được giữ nguyên

### AC-15: Không cho sửa tay tồn kho
Given: Nhân viên đang xem biến thể X tồn 10
When: Nhân viên gửi trực tiếp yêu cầu sửa tay số lượng tồn
Then: màn hình không có thao tác sửa tồn kho; yêu cầu sửa tay bị từ chối
And: số lượng tồn của X vẫn là 10

### AC-16: Hiển thị tồn mới sau đặt hàng
Given: Nhân viên đã xem biến thể X tồn 10
When: một đơn COD (UC-19) hoặc QR (UC-20) được tạo thành công với 2 cái X, sau đó Nhân viên mở lại hoặc tải lại màn hình tồn kho
Then: biến thể X hiển thị tồn 8
And: việc xem tồn kho không trừ thêm tồn

### AC-17: Hiển thị tồn mới sau hủy đơn
Given: Nhân viên đã xem biến thể X tồn 8; đơn cần hủy có 2 cái X đã được trừ tồn
When: Khách hàng/Nhân viên hủy đơn thành công theo UC-22 hoặc hệ thống tự hủy theo UC-24, sau đó Nhân viên mở lại hoặc tải lại màn hình tồn kho
Then: biến thể X hiển thị tồn 10
And: việc xem tồn kho không cộng thêm tồn

### AC-18: Hiển thị tồn mới sau giao không thành công
Given: Nhân viên đã xem biến thể X tồn 8; một đơn đang giao có 2 cái X
When: đơn chuyển sang "Giao không thành công" và hoàn tồn thành công theo UC-35, sau đó Nhân viên mở lại hoặc tải lại màn hình tồn kho
Then: biến thể X hiển thị tồn 10
And: việc xem tồn kho không cộng thêm tồn

### AC-19: Chưa đăng nhập hoặc phiên hết hạn
Given: người truy cập không có phiên portal quản trị hoặc phiên đã hết hạn
When: người đó yêu cầu xem danh sách tồn kho, kể cả tìm kiếm, lọc hoặc chuyển trang
Then: hệ thống không hiển thị dữ liệu tồn kho, yêu cầu đăng nhập lại theo UC-02

### AC-20: Không cache danh sách tồn kho
Given: Nhân viên có phiên hợp lệ
When: Nhân viên xem, tìm kiếm, lọc, chuyển trang hoặc tải lại danh sách tồn kho
Then: hệ thống đọc dữ liệu hiện tại từ Database, không sử dụng cache danh sách
And: response trả `Cache-Control: no-store`

## Dependencies
- **Upstream UC:** UC-02, UC-15, UC-19, UC-20, UC-22, UC-24, UC-34, UC-35
- **Downstream UC:** không có
- **External Systems:** không có

## Notes
- Không cache danh sách tồn kho; mỗi request đọc Database và trả `Cache-Control: no-store` (BR-GIAIDOAN1, Constraints chung). Route trả cả trang đầy đủ và mảnh HTMX phải thêm `Vary: HX-Request`.
- Tồn kho thay đổi qua các UC nghiệp vụ được phản ánh ở lần yêu cầu xem tiếp theo; UC-39 không tự đặt hàng, hủy đơn, nhập hàng hoặc hoàn tồn.
- Tên sản phẩm, màu, size, danh mục và SKU lấy qua service công khai của catalog; repository inventory không truy vấn trực tiếp bảng catalog (AGENTS.md).
- Tồn kho không bao giờ âm và không sửa tay; chỉ thay đổi qua các UC nghiệp vụ (BR-005).
- Ngưỡng tồn kho thấp hard-code là 5 (BR-GIAIDOAN1, Constraints chung; giá trị đã chốt 22/11/2026).

**Quyết định đã chốt**
- Nhân viên quản lý hàng hóa nên xem được tồn kho theo biến thể ngoài dashboard (đã chốt 15/11/2026).
- Danh sách có 20 biến thể/trang, mặc định sắp theo tên sản phẩm tăng dần, khi trùng tên thì theo SKU tăng dần; mỗi dòng gồm tên sản phẩm, màu, size, số lượng tồn (đã chốt 22/11/2026). SKU là thứ tự phụ duy nhất, không thêm cột hiển thị.
- Tìm tên sản phẩm chứa từ khóa, không phân biệt hoa/thường, có phân biệt dấu; có lọc theo danh mục và kết hợp được với tìm kiếm (đã chốt 22/11/2026).
- Ngưỡng tồn kho thấp hard-code là 5; đánh dấu khi tồn ≤ 5, bao gồm cả tồn 0 (đã chốt 22/11/2026).
- Không hiển thị giá vốn (đã chốt 22/11/2026).
- Sản phẩm/biến thể ngừng bán vẫn hiển thị trong danh sách tồn kho (đã chốt 22/11/2026).
- Chỉ Nhân viên được xem; Khách hàng và Admin không truy cập được màn hình tồn kho (theo BR-GIAIDOAN1: Nhân viên vận hành cửa hàng, Admin chỉ quản lý tài khoản và vai trò).

**Câu hỏi mở [GD]**
- Không còn giả định chờ chốt trong UC-39.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-22): chốt phân trang, tìm kiếm, lọc danh mục, ngưỡng tồn kho thấp, không hiển thị giá vốn và hiển thị hàng ngừng bán; chuyển phân quyền sang quyết định đã chốt và bổ sung AC tương ứng.
- v3 (2026-11-22): chốt SKU làm thứ tự phụ; hoàn thiện Main Flow, Alternative Flows, Exceptions và AC; đồng bộ quy định không cache, bỏ dependency UC-23 vì xác nhận đơn không thay đổi tồn kho.
