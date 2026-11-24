# UC-12: Xem chi tiết sản phẩm

## Metadata
- **ID:** UC-12
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng bấm vào một thẻ sản phẩm (từ trang chủ, danh mục, tìm kiếm, yêu thích) hoặc truy cập trực tiếp đường dẫn (URL) sản phẩm.

## Preconditions
- Sản phẩm tồn tại và ở trạng thái Đang bán (`product_status = ACTIVE`).

## Main Flow
1. Người dùng mở trang chi tiết sản phẩm.
2. Hệ thống tải thông tin sản phẩm và hiển thị:
   - Tên sản phẩm, mô tả chi tiết.
   - Bộ ảnh (gallery) theo thứ tự hiển thị (`gallery_order_no`), ảnh đầu tiên làm ảnh chính.
   - Bảng size chung cố định của cửa hàng.
   - Nút thả tim (yêu thích): hiển thị trạng thái đã chọn nếu Khách hàng đã đăng nhập và đã lưu sản phẩm này vào danh sách yêu thích; ngược lại hiển thị trạng thái chưa chọn.
   - Các danh sách lựa chọn màu sắc và kích cỡ (size) có sẵn của sản phẩm; ban đầu chưa có màu hay size nào được chọn sẵn.
   - Khoảng giá ban đầu: từ giá size thấp nhất đến giá size cao nhất trong tập các biến thể ở trạng thái Đang hoạt động có giá bán hợp lệ (`variant_status = ACTIVE` và `variant_sell_price > 0`), độc lập với tình trạng tồn kho (biến thể hết hàng vẫn tham gia tính giá; biến thể INACTIVE hoặc chưa có giá không tham gia tính giá). Nếu mọi size hợp lệ cùng mức giá, hiển thị một mức giá duy nhất. Nếu sản phẩm có chương trình khuyến mãi theo sản phẩm còn hiệu lực (UC-28), hệ thống hiển thị đồng thời khoảng giá gốc và khoảng giá sau giảm.
   - Bộ chọn số lượng (mặc định là 1) và nút "Thêm vào giỏ hàng".
3. Người dùng chọn một thuộc tính (màu hoặc size):
   - Nếu người dùng chọn size có biến thể ACTIVE có giá hợp lệ: hệ thống cập nhật hiển thị đơn giá chính xác của size đó (giá gốc và giá sau giảm nếu có khuyến mãi; mọi màu cùng size có cùng giá theo UC-16).
   - Hệ thống tự động vô hiệu hóa (disable/làm mờ, không cho chọn) các tùy chọn của thuộc tính còn lại nếu tổ hợp màu × size tương ứng không tồn tại hoặc ở trạng thái ngừng bán (`variant_status = INACTIVE`). Bộ ảnh sản phẩm giữ nguyên, không thay đổi theo màu.
4. Người dùng chọn tiếp thuộc tính còn lại để hoàn tất lựa chọn đủ cả màu và size.
5. Hệ thống xác định biến thể cụ thể (`color × size`), đọc dữ liệu tồn kho từ module inventory và hiển thị tình trạng "Còn hàng" (khi tồn kho > 0). Bộ chọn số lượng giới hạn giá trị tối đa không vượt quá số lượng tồn kho khả dụng của biến thể.
6. Người dùng chọn số lượng mong muốn (mặc định là 1) và bấm nút "Thêm vào giỏ hàng".
7. Hệ thống gửi yêu cầu thêm biến thể và số lượng vào giỏ hàng sang module shopping (UC-18). Khi UC-18 phản hồi thành công, hệ thống hiển thị thông báo "Đã thêm vào giỏ hàng" và cập nhật số lượng trên biểu tượng giỏ hàng ở thanh điều hướng.

## Alternative Flows
- **2a. Khách hàng thả tim hoặc bỏ thả tim sản phẩm:** Khách hàng đã đăng nhập bấm nút thả tim trên trang chi tiết; hệ thống lưu hoặc xóa sản phẩm khỏi danh sách yêu thích qua module shopping (UC-38) và chuyển đổi trạng thái hiển thị của nút tim tương ứng.
- **2b. Khách vãng lai bấm nút thả tim:** Người dùng chưa đăng nhập bấm nút thả tim; hệ thống chuyển hướng tới trang Đăng nhập (UC-02) kèm tham số đường dẫn nội bộ an toàn `return_url` trỏ về trang chi tiết sản phẩm hiện tại. Sau khi đăng nhập thành công, hệ thống chuyển hướng người dùng quay lại đúng trang chi tiết sản phẩm đang xem, KHÔNG tự động thực hiện thích/bỏ thích và không tự tạo `wishlist_item`. Trạng thái hiển thị của nút tim được tải theo dữ liệu thực tế của tài khoản (hiển thị chưa chọn nếu tài khoản chưa từng lưu sản phẩm này, hoặc hiển thị đã chọn nếu tài khoản đã lưu sản phẩm này từ trước theo Main Flow bước 2 / Q4 / AC-17); người dùng có thể chủ động bấm thả tim lại nếu chưa chọn.
- **2c. Sản phẩm không có biến thể Đang hoạt động nào:** Sản phẩm ở trạng thái Đang bán (`product_status = ACTIVE`) nhưng tất cả các biến thể đều ở trạng thái Ngừng bán (`variant_status = INACTIVE`) hoặc không có biến thể nào có giá bán hợp lệ (> 0); hệ thống trả về mã trạng thái HTTP 200 (khác với Exception E1), vẫn hiển thị tên, mô tả và bộ ảnh của sản phẩm, nhưng không hiển thị khoảng giá bán (tuyệt đối không lấy giá từ các biến thể INACTIVE để lấp khoảng giá), vô hiệu hóa tất cả các nút chọn màu và size, vô hiệu hóa bộ chọn số lượng và nút "Thêm vào giỏ hàng", đồng thời hiển thị thông báo "Sản phẩm tạm ngừng kinh doanh".
- **3a. Người dùng thay đổi màu hoặc size đã chọn / Bỏ chọn (Toggle unselect):**
  - Người dùng có thể bấm lại vào nút thuộc tính đang được chọn (đang active) để bỏ chọn thuộc tính đó (toggle unselect). Khi một thuộc tính bị bỏ chọn, hệ thống cập nhật lại danh sách tùy chọn khả dụng của thuộc tính còn lại theo thuộc tính vẫn đang chọn (hoặc mở lại toàn bộ các tùy chọn nếu đã bỏ chọn cả hai thuộc tính), đưa tình trạng tồn kho về trạng thái chưa xác định (do chưa đủ màu và size). Khi bỏ chọn size, hiển thị đơn giá quay trở lại khoảng giá ban đầu từ tập các biến thể ACTIVE có giá hợp lệ.
  - Khi chỉ đang chọn một thuộc tính (ví dụ chỉ chọn màu Đỏ), người dùng có thể bấm trực tiếp vào nút màu khác đang khả dụng (ví dụ Xanh); hệ thống chuyển lựa chọn sang màu mới và cập nhật lại danh sách size khả dụng theo màu mới đó. Các nút đang bị vô hiệu hóa (disabled) không thể bấm trực tiếp.
- **5a. Biến thể đã chọn hết hàng:** Biến thể (màu × size) được chọn có tồn kho = 0; hệ thống hiển thị nhãn "Hết hàng", vô hiệu hóa bộ chọn số lượng, vô hiệu hóa nút "Thêm vào giỏ hàng" và đổi nhãn nút thành "Hết hàng".
- **6a. Bấm thêm vào giỏ khi chưa chọn đủ màu và size:** Người dùng bấm nút "Thêm vào giỏ hàng" khi mới chỉ chọn màu hoặc mới chỉ chọn size (hoặc chưa chọn cả hai); hệ thống không thêm vào giỏ, giữ nguyên trang và hiển thị thông báo nhắc nhở "Vui lòng chọn màu và size".
- **6b. Nhập số lượng mua không hợp lệ hoặc đổi biến thể:**
  - Nếu người dùng nhập số lượng bằng tay ≤ 0, chuỗi rỗng, chữ cái, hoặc số thập phân thì hệ thống tự động đưa về 1.
  - Nếu người dùng nhập số lượng lớn hơn tồn kho khả dụng của biến thể, hệ thống tự động điều chỉnh số lượng về bằng số lượng tồn kho tối đa của biến thể đó và hiển thị thông báo cảnh báo.
  - Khi người dùng đổi sang biến thể khác có tồn kho thấp hơn số lượng đang chọn: nếu biến thể mới có tồn kho > 0, hệ thống tự động giảm số lượng về bằng tồn kho của biến thể mới; nếu biến thể mới có tồn kho = 0, hệ thống áp dụng Alternative Flow 5a (vô hiệu hóa ô số lượng và nút thêm giỏ).
- **7a. Module shopping từ chối thêm vào giỏ hàng:** Module shopping (UC-18) từ chối yêu cầu (do số lượng trong giỏ hàng cộng dồn vượt quá tồn kho hiện tại hoặc biến thể vừa hết hàng); hệ thống giữ nguyên trang chi tiết, hiển thị thông báo lỗi từ UC-18 (ví dụ: "Chỉ còn N sản phẩm") và không cập nhật số lượng giỏ hàng trên thanh điều hướng.

## Exceptions
- **E1. Sản phẩm không tồn tại hoặc Ngừng bán:** Người dùng truy cập mã sản phẩm không tồn tại trong hệ thống hoặc sản phẩm có `product_status = INACTIVE`; hệ thống hiển thị trang thông báo lỗi "Không tìm thấy sản phẩm" (HTTP 404).

## Postconditions
- Trang chi tiết sản phẩm được hiển thị; dữ liệu của sản phẩm và biến thể trong cơ sở dữ liệu không thay đổi.
- Trường hợp người dùng thêm vào giỏ hàng thành công: giỏ hàng được cập nhật thêm dòng sản phẩm theo UC-18 (lưu ở `localStorage` đối với Khách vãng lai, hoặc lưu vào database đối với Khách hàng).
- Trường hợp Khách hàng thả tim: danh sách yêu thích của Khách hàng được cập nhật tương ứng theo UC-38.

## Acceptance Criteria

### AC-1: Hiển thị thông tin ban đầu của sản phẩm
Given: sản phẩm A ở trạng thái Đang bán, có tên, mô tả, bộ ảnh gồm 3 ảnh, có các màu Đỏ, Xanh và các size S, M; giá size S = 300.000đ, size M = 320.000đ, không có khuyến mãi
When: người dùng mở trang chi tiết sản phẩm A
Then: hệ thống hiển thị tên, mô tả, 3 ảnh theo thứ tự, bảng size chung cố định của cửa hàng, các nút chọn màu (Đỏ, Xanh) và size (S, M) ở trạng thái chưa được chọn
And: khoảng giá hiển thị là "300.000đ - 320.000đ"
And: nút "Thêm vào giỏ hàng" hiển thị bình thường, số lượng mặc định là 1

### AC-2: Bảng size chung cố định
Given: sản phẩm A và sản phẩm B đều ở trạng thái Đang bán
When: người dùng lần lượt mở trang chi tiết sản phẩm A và sản phẩm B
Then: cả hai trang hiển thị cùng một bảng size chung cố định của cửa hàng

### AC-3: Bộ ảnh hiển thị theo thứ tự
Given: sản phẩm A có 3 ảnh với thứ tự hiển thị `gallery_order_no` lần lượt là 1, 2, 3
When: người dùng mở trang chi tiết sản phẩm A
Then: các ảnh được hiển thị đúng thứ tự 1, 2, 3 và ảnh có thứ tự 1 được hiển thị làm ảnh chính

### AC-4: Đổi màu không thay đổi bộ ảnh
Given: người dùng đang xem trang chi tiết sản phẩm A có các màu Đỏ và Xanh
When: người dùng chuyển từ việc chọn màu Đỏ sang màu Xanh
Then: bộ ảnh gallery của sản phẩm giữ nguyên, không thay đổi

### AC-5: Cập nhật giá theo size
Given: sản phẩm A có giá size S = 300.000đ, size M = 320.000đ
When: người dùng bấm chọn size M (chưa chọn màu hoặc đã chọn màu bất kỳ)
Then: đơn giá hiển thị trên trang được cập nhật thành 320.000đ

### AC-6: Cùng size khác màu cùng giá bán
Given: sản phẩm A có giá size M = 320.000đ, có các màu Đỏ và Xanh
When: người dùng chọn size M lần lượt với màu Đỏ và màu Xanh
Then: đơn giá hiển thị ở cả hai trường hợp đều là 320.000đ

### AC-7: Hiển thị khoảng giá ban đầu khi có khuyến mãi theo sản phẩm
Given: sản phẩm A có khuyến mãi giảm 10% còn hiệu lực, size S giá gốc 300.000đ (sau giảm 270.000đ), size M giá gốc 320.000đ (sau giảm 288.000đ)
When: người dùng mở trang chi tiết sản phẩm A (chưa chọn size)
Then: khoảng giá gốc hiển thị là "300.000đ - 320.000đ" (gạch ngang)
And: khoảng giá sau giảm hiển thị là "270.000đ - 288.000đ" kèm nhãn "-10%"

### AC-8: Hiển thị đơn giá sau khuyến mãi khi chọn size cụ thể
Given: sản phẩm A có khuyến mãi theo sản phẩm giảm 10% còn hiệu lực, size M có giá gốc 320.000đ (giá sau giảm là 288.000đ)
When: người dùng chọn size M trên trang chi tiết sản phẩm A
Then: hệ thống hiển thị giá gốc gạch ngang 320.000đ và giá sau giảm 288.000đ kèm nhãn giảm "-10%"

### AC-9: Chọn size trước rồi khóa màu không tương ứng
Given: sản phẩm A có các biến thể Đỏ × S (ACTIVE), Đỏ × M (ACTIVE), Xanh × M (ACTIVE); không có biến thể Xanh × S
When: người dùng bấm chọn size S trước khi chọn màu
Then: đơn giá cập nhật theo size S, nút chọn màu Đỏ khả dụng, còn nút chọn màu Xanh bị vô hiệu hóa (disabled)

### AC-10: Vô hiệu hóa lựa chọn khi tổ hợp màu × size không tồn tại hoặc ngừng bán
Given: sản phẩm A có các biến thể Đỏ × S (ACTIVE), Xanh × S (ACTIVE), Xanh × M (ACTIVE); tổ hợp Đỏ × M không tồn tại trong hệ thống (hoặc có `variant_status = INACTIVE`)
When: người dùng bấm chọn màu Đỏ
Then: nút chọn size S vẫn khả dụng, còn nút chọn size M bị vô hiệu hóa (disabled/làm mờ, không bấm được)

### AC-11: Biến thể còn hàng
Given: biến thể Đỏ × M của sản phẩm A có tồn kho khả dụng = 5
When: người dùng chọn màu Đỏ và size M
Then: hệ thống hiển thị tình trạng "Còn hàng"
And: bộ chọn số lượng cho phép chọn tối đa 5 sản phẩm
And: nút "Thêm vào giỏ hàng" sẵn sàng hoạt động

### AC-12: Biến thể hết hàng
Given: biến thể Đỏ × L của sản phẩm A có tồn kho = 0
When: người dùng chọn màu Đỏ và size L
Then: hệ thống hiển thị tình trạng "Hết hàng"
And: bộ chọn số lượng và nút "Thêm vào giỏ hàng" bị vô hiệu hóa, nhãn nút chuyển thành "Hết hàng"

### AC-13: Nhắc nhở khi chưa chọn đủ màu và size
Given: người dùng đang xem sản phẩm A và mới chỉ chọn màu Đỏ, chưa chọn size
When: người dùng bấm nút "Thêm vào giỏ hàng"
Then: hệ thống không thêm sản phẩm vào giỏ hàng
And: hiển thị thông báo nhắc nhở "Vui lòng chọn màu và size"

### AC-14: Giới hạn và tự động điều chỉnh số lượng mua theo tồn kho
Given: biến thể Xanh × S có tồn kho khả dụng = 3
When: người dùng chọn biến thể Xanh × S và nhập số lượng mua là 5 vào ô số lượng
Then: hệ thống tự động điều chỉnh số lượng về 3 và thông báo "Số lượng mua tối đa là 3"
When: người dùng nhập số lượng là 0, chuỗi rỗng, chữ cái "abc" hoặc số thập phân "2.5"
Then: hệ thống tự động điều chỉnh số lượng về 1
Given: người dùng đang chọn biến thể Đỏ × M có tồn kho khả dụng = 10, số lượng mua đang chọn là 5
When: người dùng chuyển sang chọn biến thể Đỏ × S có tồn kho khả dụng = 2
Then: hệ thống tự động điều chỉnh số lượng mua từ 5 giảm về 2 và thông báo "Số lượng đã được điều chỉnh về mức tồn kho tối đa (2)"
Given: người dùng đang chọn biến thể Đỏ × M có tồn kho khả dụng = 10, số lượng mua đang chọn là 3
When: người dùng chuyển sang chọn biến thể Đỏ × L có tồn kho = 0
Then: hệ thống hiển thị tình trạng "Hết hàng", vô hiệu hóa bộ chọn số lượng và vô hiệu hóa nút "Thêm vào giỏ hàng" (áp dụng Alternative Flow 5a)

### AC-15: Thêm vào giỏ hàng thành công
Given: biến thể Đỏ × S có tồn kho khả dụng = 5, người dùng đã chọn số lượng là 2
When: người dùng bấm "Thêm vào giỏ hàng" và module shopping (UC-18) phản hồi thêm thành công
Then: hệ thống hiển thị thông báo "Đã thêm vào giỏ hàng"
And: số lượng hiển thị trên biểu tượng giỏ hàng ở thanh điều hướng được cập nhật tăng thêm 2

### AC-16: Module shopping từ chối do vượt tồn kho giỏ hàng
Given: biến thể Đỏ × S có tồn kho khả dụng = 2, trong giỏ hàng hiện tại của người dùng đã có sẵn 2 sản phẩm Đỏ × S
When: người dùng chọn số lượng 1 trên trang chi tiết và bấm "Thêm vào giỏ hàng"
Then: module shopping (UC-18) từ chối yêu cầu với lỗi vượt tồn kho
And: hệ thống hiển thị thông báo lỗi "Chỉ còn 2 sản phẩm"
And: số lượng trên biểu tượng giỏ hàng không thay đổi

### AC-17: Khách hàng đã thích sản phẩm khi mở trang chi tiết
Given: Khách hàng đang đăng nhập và sản phẩm A đã có trong danh sách yêu thích của Khách hàng
When: Khách hàng mở trang chi tiết sản phẩm A
Then: nút thả tim hiển thị ở trạng thái đã chọn (active/đỏ)

### AC-18: Khách hàng thả tim và bỏ thả tim từ trang chi tiết
Given: Khách hàng đang đăng nhập, sản phẩm A chưa có trong danh sách yêu thích
When: Khách hàng bấm nút thả tim trên trang chi tiết sản phẩm A
Then: sản phẩm A được thêm vào danh sách yêu thích của Khách hàng (UC-38)
And: nút thả tim chuyển sang trạng thái đã chọn (active/đỏ)
When: Khách hàng bấm lại nút thả tim lần nữa
Then: sản phẩm A được xóa khỏi danh sách yêu thích
And: nút thả tim trở về trạng thái chưa chọn

### AC-19: Khách vãng lai bấm nút thả tim và quay lại trang sau khi đăng nhập
Given: người dùng chưa đăng nhập (Khách vãng lai) đang ở trang chi tiết sản phẩm A
When: người dùng bấm nút thả tim
Then: hệ thống chuyển hướng người dùng tới trang Đăng nhập (UC-02) kèm tham số đường dẫn nội bộ an toàn `return_url` trỏ về trang chi tiết sản phẩm A

Scenario: Tài khoản sau khi đăng nhập chưa từng lưu sản phẩm A trong danh sách yêu thích
Given: người dùng thực hiện đăng nhập thành công vào tài khoản mà sản phẩm A chưa nằm trong danh sách yêu thích của tài khoản này
When: hệ thống chuyển hướng người dùng quay lại trang chi tiết sản phẩm A theo `return_url`
Then: hệ thống KHÔNG tự động thực hiện thao tác thích hay tạo bản ghi `wishlist_item` mới chỉ vì đăng nhập
And: nút thả tim hiển thị ở trạng thái chưa chọn
And: người dùng có thể chủ động bấm nút thả tim lại để thêm sản phẩm A vào danh sách yêu thích

Scenario: Tài khoản sau khi đăng nhập đã lưu sản phẩm A trong danh sách yêu thích từ trước
Given: người dùng thực hiện đăng nhập thành công vào tài khoản mà sản phẩm A đã được lưu trong danh sách yêu thích từ trước đó
When: hệ thống chuyển hướng người dùng quay lại trang chi tiết sản phẩm A theo `return_url`
Then: hệ thống bảo toàn danh sách yêu thích cũ, không tự ý xóa hay reset trạng thái yêu thích
And: nút thả tim hiển thị ở trạng thái đã chọn (active/đỏ theo Main Flow bước 2, Q4 và AC-17)

### AC-20: Sản phẩm không tồn tại hoặc Ngừng bán
Given: sản phẩm B ở trạng thái Ngừng bán (`product_status = INACTIVE`) hoặc mã sản phẩm không tồn tại
When: người dùng truy cập vào trang chi tiết của sản phẩm B
Then: hệ thống hiển thị trang thông báo lỗi "Không tìm thấy sản phẩm" (404)

### AC-21: Bỏ chọn thuộc tính (Toggle unselect) và đổi tổ hợp biến thể
Given: sản phẩm A chỉ có 2 biến thể Đỏ × S (ACTIVE) và Xanh × M (ACTIVE); người dùng đang chọn biến thể Đỏ × S
And: nút chọn màu Đỏ và size S đang ở trạng thái active; nút chọn màu Xanh và size M đang bị vô hiệu hóa (disabled)
When: người dùng bấm lại vào nút màu Đỏ đang active
Then: màu Đỏ trở về trạng thái chưa chọn; nút chọn size S vẫn active; hệ thống cập nhật lại danh sách màu: nút Đỏ khả dụng, nút Xanh vẫn bị vô hiệu hóa (do không có Xanh × S); tình trạng tồn kho trở về chưa xác định
When: người dùng bấm tiếp vào nút size S đang active
Then: size S trở về trạng thái chưa chọn; toàn bộ các nút màu (Đỏ, Xanh) và size (S, M) đều khả dụng trở lại; giá hiển thị quay về khoảng giá ban đầu
When: người dùng bấm chọn màu Xanh
Then: màu Xanh chuyển sang trạng thái active; nút chọn size M khả dụng, nút chọn size S bị vô hiệu hóa

### AC-22: Tính khoảng giá ban đầu trên tập biến thể ACTIVE có giá hợp lệ
Given: sản phẩm A đang bán có khuyến mãi giảm 10% còn hiệu lực
And: size S có giá 100.000đ nhưng chỉ có biến thể ở trạng thái INACTIVE (tồn kho 5)
And: size M có giá 200.000đ (sau giảm 180.000đ) ở trạng thái ACTIVE nhưng tồn kho = 0
And: size L có giá 250.000đ (sau giảm 225.000đ) ở trạng thái ACTIVE có tồn kho 10
When: người dùng mở trang chi tiết sản phẩm A (chưa chọn size)
Then: khoảng giá gốc ban đầu hiển thị là "200.000đ - 250.000đ" (biến thể INACTIVE size S không tham gia tính giá; biến thể ACTIVE size M hết hàng vẫn tham gia tính giá)
And: khoảng giá sau giảm hiển thị là "180.000đ - 225.000đ" kèm nhãn "-10%"
When: người dùng chọn size M
Then: đơn giá gốc hiển thị là 200.000đ và giá sau giảm là 180.000đ
When: người dùng bấm bỏ chọn size M (toggle unselect)
Then: hiển thị quay trở lại khoảng giá gốc "200.000đ - 250.000đ" và giá sau giảm "180.000đ - 225.000đ"

### AC-23: Truy cập URL trực tiếp của sản phẩm cha ACTIVE nhưng không có biến thể hợp lệ
Given: sản phẩm B ở trạng thái Đang bán (`product_status = ACTIVE`) nhưng tất cả các biến thể đều ở trạng thái Ngừng bán (`variant_status = INACTIVE`) hoặc không có biến thể nào có giá bán hợp lệ (> 0)
When: người dùng truy cập trực tiếp vào URL trang chi tiết sản phẩm B
Then: hệ thống trả về mã trạng thái HTTP 200 (không trả về lỗi 404 như Exception E1)
And: hệ thống vẫn hiển thị tên, mô tả và bộ ảnh của sản phẩm B
And: không hiển thị khoảng giá bán (tuyệt đối không lấy giá từ các biến thể INACTIVE để lấp khoảng giá)
And: tất cả các nút chọn màu, size, bộ chọn số lượng và nút "Thêm vào giỏ hàng" đều bị vô hiệu hóa (disabled)
And: hiển thị thông báo "Sản phẩm tạm ngừng kinh doanh"

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size, UC-16 Quản lý giá bán theo size, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-18 Quản lý giỏ hàng, UC-38 Quản lý danh sách yêu thích
- **External Systems:** Không có

## Notes
- Giá sau khuyến mãi theo sản phẩm lấy từ module promotion (UC-28): `giá sau giảm = giá gốc × (100% − % giảm)`, làm tròn `ROUND_HALF_UP` về số nguyên VND theo BR-004 và AGENTS.md.
- Tồn kho của biến thể lấy từ module inventory (bảng `inventory.stock`) qua service công khai.
- Giỏ hàng và danh sách yêu thích giao tiếp qua service công khai của module shopping (UC-18, UC-38).
- Out of Scope (BR-GIAIDOAN1): đánh giá sản phẩm (để giai đoạn 2).

### Quyết định đã chốt
- Bộ ảnh (gallery) gắn theo sản phẩm, có thứ tự hiển thị; chọn màu không đổi ảnh (theo ERD, đã chốt 15/11/2026).
- Giá bán đổi theo size; cùng size khác màu cùng giá (đã chốt 15/11/2026).
- Có chức năng thả tim lưu sản phẩm vào danh sách yêu thích (đã chốt 15/11/2026, UC-38).
- Dùng một bảng size chung cho cả cửa hàng, nội dung cố định (hard-code như trang thông tin), không phải trường của sản phẩm (đã chốt 15/11/2026).
- Tổ hợp biến thể không tồn tại hoặc có `variant_status = INACTIVE`: vô hiệu hóa nút thuộc tính tương ứng khi người dùng đã chọn 1 thuộc tính trước đó (đã chốt 22/11/2026, UC-12-Q1; quyết định liên UC đồng bộ với UC-15: giữ hiển thị nhưng vô hiệu hóa đối với biến thể INACTIVE).
- Thứ tự chọn thuộc tính linh hoạt (có thể chọn size trước hoặc màu trước); khi chưa chọn size hiển thị khoảng giá min - max (kèm giá sau giảm nếu có khuyến mãi); chọn size lập tức hiển thị đơn giá của size đó (đã chốt 22/11/2026, UC-12-Q2).
- Tập biến thể tính khoảng giá min - max ban đầu: chỉ tính trên các biến thể có `variant_status = ACTIVE` và `variant_sell_price > 0`, độc lập với tồn kho (biến thể hết hàng vẫn tham gia tính giá; biến thể INACTIVE hoặc chưa có giá không tham gia tính giá). Khi chọn size có biến thể ACTIVE có giá hợp lệ, hiển thị giá của size đó (mọi màu cùng size cùng giá); bỏ chọn size quay lại khoảng giá từ tập hợp lệ (đã chốt 23/11/2026, phê duyệt liên UC tại Codex theo UC10-Q9/Q10/Q11 và UC14-Q10).
- Tồn kho chỉ hiển thị nhãn chữ "Còn hàng" hoặc "Hết hàng", không hiển thị số lượng cụ thể; bộ chọn số lượng giới hạn tối đa bằng tồn kho khả dụng; khi hết hàng vô hiệu hóa nút thêm giỏ và đổi nhãn thành "Hết hàng" (đã chốt 22/11/2026, UC-12-Q3).
- Nút thả tim: hiển thị trạng thái đã chọn nếu Khách hàng đã đăng nhập và đã thích sản phẩm; Khách vãng lai bấm tim chuyển hướng sang trang đăng nhập và quay lại trang chi tiết sau khi đăng nhập (đã chốt 22/11/2026, UC-12-Q4).
- Nút "Thêm vào giỏ hàng" vẫn bấm được khi chưa chọn đủ màu và size để hiển thị thông báo nhắc nhở "Vui lòng chọn màu và size" (đã chốt 22/11/2026, UC-12-Q5, đồng bộ AC-13).
- Cơ chế chuyển đổi/bỏ chọn tổ hợp thuộc tính: giữ nguyên tắc Q1 là nút không tương thích bị vô hiệu hóa hoàn toàn (disabled) và không thể bấm trực tiếp; người dùng chuyển đổi tổ hợp biến thể hoặc thoát kẹt bằng cơ chế Toggle Unselect (bấm lại nút thuộc tính đang active để bỏ chọn, từ đó hệ thống giải phóng và tính toán lại các lựa chọn khả dụng) (đã chốt 23/11/2026, developer duyệt Phương án 1 tại UC-12-Q6b).
- Xử lý số lượng mua không hợp lệ và đổi biến thể: tự động đưa về 1 nếu nhập ≤ 0, chuỗi rỗng, chữ cái hoặc số thập phân; tự động đưa về tồn kho tối đa nếu vượt tồn; tự giảm về tồn kho mới khi đổi biến thể; khi đổi sang biến thể tồn kho 0 thì vô hiệu hóa ô số lượng và nút thêm giỏ (áp dụng 5a); kết quả thêm vào giỏ phụ thuộc service UC-18 (đã chốt 22/11/2026, UC-12-Q7).
- Khách vãng lai bấm nút thả tim: chuyển sang trang đăng nhập (UC-02) kèm tham số `return_url` nội bộ an toàn; sau đăng nhập thành công quay lại trang chi tiết, hệ thống KHÔNG tự động thực hiện thích/bỏ thích và không tự tạo `wishlist_item` mới. Trạng thái nút tim hiển thị theo đúng dữ liệu thực tế của tài khoản (chưa chọn nếu tài khoản chưa từng lưu A, hoặc đã chọn nếu tài khoản đã lưu A từ trước theo Main 2/Q4/AC-17), bảo toàn trạng thái cũ không bị reset (đã chốt 23/11/2026, developer duyệt Phương án A tại UC-12-Q8 và làm rõ ràng buộc fixture/trạng thái; khớp UC-38 Flow 1b).
- Xử lý URL trực tiếp khi sản phẩm cha ACTIVE nhưng không còn biến thể ACTIVE có giá > 0: trả về mã trạng thái HTTP 200 (khác Exception E1 trả về HTTP 404 khi sản phẩm cha INACTIVE hoặc không tồn tại); vẫn mở trang chi tiết hiển thị tên, mô tả, bộ ảnh nhưng không hiển thị khoảng giá bán (tuyệt đối không lấy giá từ các biến thể INACTIVE để lấp khoảng giá), vô hiệu hóa toàn bộ nút màu/size/mua hàng và hiển thị thông báo "Sản phẩm tạm ngừng kinh doanh" (đã chốt 23/11/2026, developer duyệt Phương án 1 tại UC-12-Q9b và làm rõ HTTP 200/cấm lấp giá).

### Giả định [GD]
- Hiện tại không còn giả định hoặc câu hỏi mở nào bị chặn cho UC-12.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): ảnh theo sản phẩm (theo ERD), chốt giá theo size chung cho mọi màu, thêm nút thả tim dẫn tới UC-38
- v3 (2026-11-15): chốt bảng size chung cố định cho cả cửa hàng; thêm AC-2, đánh số lại AC
- v4 (2026-11-22): chốt UC-12-Q1 -> Q5: hoàn thiện xử lý tổ hợp không tồn tại/ngừng bán, khoảng giá ban đầu, quy tắc tồn kho & số lượng mua, đồng bộ wishlist và hành vi nút thêm giỏ hàng; hoàn thiện Main Flow, Alternative Flows (2a, 2b, 3a, 5a, 6a, 6b), Exception E1 và bổ sung AC-11 đến AC-15
- v5 (2026-11-22): rà soát theo phản hồi của Coordinator: chuyển Status draft, gắn [GD] và bổ sung câu hỏi mở UC-12-Q6, UC-12-Q7; chuẩn hóa ranh giới gọi UC-18 ở bước 7 và Flow 7a; bổ sung AC cho khoảng giá khuyến mãi, chọn size trước, trạng thái tim ban đầu, phản hồi giỏ hàng thành công / từ chối (tổng cộng 20 ACs)
- v6 (2026-11-22): developer phê duyệt chốt UC-12-Q6 và UC-12-Q7; hoàn thiện Alternative Flow 3a, 6b; mở rộng AC-14 (thập phân, chữ cái, đổi biến thể sang tồn kho thấp hơn và tồn kho 0); bổ sung AC-21 (Toggle unselect và đổi tổ hợp); cập nhật Quyết định đã chốt; gỡ bỏ toàn bộ nhãn [GD]; chuyển Status sang ready
- v7 (2026-11-23): developer chính thức phê duyệt Phương án 1 cho UC-12-Q6b: chốt cơ chế Toggle Unselect thuần túy (giữ nghiêm ngặt Q1 disabled, không cho bấm trực tiếp vào nút đang bị vô hiệu hóa); đồng bộ quyết định liên UC-12/UC-15 (INACTIVE giữ hiển thị nhưng disabled); gỡ bỏ toàn bộ nhãn [GD]; chuyển Status sang ready
- v8 (2026-11-23): mở đợt rà soát logic vòng 2 theo yêu cầu Coordinator: chuyển Status draft, gắn [GD] tại Flow 2b, AC-19 và mở câu hỏi UC-12-Q8 (phát hiện #7: hành vi sau đăng nhập của khách vãng lai) và UC-12-Q9 (phối hợp #2 với UC-10: tập biến thể tính khoảng giá min-max)
- v9 (2026-11-23): đồng bộ tập biến thể tính giá min-max theo phê duyệt liên UC ngày 23/11/2026 tại Codex (chỉ variant ACTIVE có giá > 0, độc lập với tồn kho); bổ sung AC-22 kiểm chứng fixture giá ACTIVE/INACTIVE/tồn kho; giữ Status draft chờ developer trả lời Q8 và Q9b
- v10 (2026-11-23): developer chính thức phê duyệt Phương án A cho UC-12-Q8 (khách vãng lai đăng nhập xong quay lại trang chi tiết, nút tim chưa chọn, tự bấm tim lại) và Phương án 1 cho UC-12-Q9b (URL trực tiếp của sản phẩm cha ACTIVE nhưng toàn bộ variant INACTIVE: mở trang chi tiết nhưng hiển thị "Sản phẩm tạm ngừng kinh doanh", vô hiệu hóa đặt hàng); bổ sung Alternative Flow 2c và AC-23; gỡ bỏ toàn bộ nhãn [GD]; chuyển Status sang ready
- v11 (2026-11-23): tinh chỉnh theo phản hồi của Coordinator Codex: làm rõ 2 kịch bản tại AC-19 (chưa lưu thì hiển thị chưa chọn & không auto-like; đã lưu từ trước thì hiển thị đã chọn theo Q4/AC-17); bổ sung rõ mã HTTP 200 và cấm lấp giá từ INACTIVE tại Alternative Flow 2c và AC-23; phân biệt rõ với Exception E1 (HTTP 404); giữ Status ready
