# UC-11: Tìm kiếm sản phẩm

## Metadata
- **ID:** UC-11
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng nhập từ khóa vào ô tìm kiếm trên thanh điều hướng/header và gửi yêu cầu (bấm Enter hoặc bấm biểu tượng tìm kiếm).

## Preconditions
- Không có.

## Main Flow
1. Người dùng nhập từ khóa vào ô tìm kiếm và gửi yêu cầu (ô tìm kiếm phía client có thuộc tính bắt buộc nhập không để rỗng).
2. Hệ thống nhận từ khóa, thực hiện cắt tỉa khoảng trắng ở hai đầu (trim); nếu độ dài sau trim vượt quá 100 ký tự thì hệ thống tự động cắt lấy 100 ký tự đầu tiên để tìm kiếm (Q4 đã chốt 22/11/2026).
3. Hệ thống tìm kiếm các sản phẩm cha Đang bán (`product_status = 'ACTIVE'`) có tên sản phẩm (`product_name`) hoặc mô tả sản phẩm (`product_description`) khớp chuỗi con với từ khóa, không phân biệt chữ hoa, chữ thường và không phân biệt dấu tiếng Việt (PostgreSQL `unaccent` + `ILIKE`) (Q1 đã chốt 22/11/2026).
   - **Quy tắc lọc tập sản phẩm hợp lệ:** Hệ thống loại trừ các sản phẩm cha ACTIVE không còn bất kỳ biến thể nào ở trạng thái ACTIVE có `variant_sell_price > 0` khỏi tập kết quả tìm kiếm TRƯỚC KHI tính tổng số sản phẩm, tổng số trang và thực hiện phân trang LIMIT/OFFSET (đồng bộ ngày 23/11/2026). Hệ thống không ẩn sản phẩm chỉ vì hết tồn kho. Nếu sau khi loại trừ, tập kết quả rỗng thì chuyển sang Alternative Flow 3a.
4. Hệ thống sắp xếp kết quả mặc định theo sản phẩm mới nhất, sử dụng `product_id ASC` làm khóa phụ cuối cùng duy nhất để đảm bảo thứ tự tất định (`product_created_at DESC, product_id ASC`) (Q3 đã chốt 22/11/2026, bổ sung tie-breaker ngày 23/11/2026).
5. Hệ thống hiển thị trang kết quả tìm kiếm gồm:
   - Từ khóa đã tìm và tổng số kết quả tìm thấy.
   - Bộ lọc kết hợp gồm 4 tiêu chí: giới tính, size, danh mục, bộ sưu tập (Q2 đã chốt 22/11/2026). Mỗi tiêu chí lọc chọn duy nhất một giá trị (Q7 đã chốt 22/11/2026).
   - Danh sách sản phẩm phân trang ở trang 1 với số sản phẩm cố định là 12 sản phẩm/trang kèm điều khiển phân trang (Q6 đã chốt 22/11/2026).
   - Mỗi thẻ sản phẩm hiển thị:
     + Ảnh đại diện (`gallery_order_no = 1`).
     + Tên sản phẩm.
     + Giá bán thấp nhất theo size (`variant_sell_price`): chỉ lấy từ các biến thể ở trạng thái `ACTIVE` có `variant_sell_price > 0` (bỏ qua biến thể `INACTIVE` kể cả khi có giá thấp hơn và còn tồn kho; không xét tồn kho để tính giá) (đồng bộ ngày 23/11/2026).
     + Giá sau khuyến mãi theo sản phẩm (nếu có): tính trên mức giá bán thấp nhất hợp lệ này, làm tròn số nguyên VND theo quy tắc `ROUND_HALF_UP` (Q10 đã chốt 23/11/2026).
     + Nhãn "Hết hàng": hiển thị khi không có bất kỳ biến thể `ACTIVE` có `variant_sell_price > 0` nào còn tồn khả dụng > 0 (lấy từ module `inventory`) (đồng bộ ngày 23/11/2026).
6. Người dùng bấm một thẻ sản phẩm để chuyển hướng đến trang chi tiết sản phẩm tương ứng (UC-12).

## Alternative Flows
- **5a. Lọc kết quả tìm kiếm (kết hợp bộ lọc):** người dùng chọn giá trị cho một hoặc nhiều tiêu chí lọc (giới tính, size, danh mục, bộ sưu tập); hệ thống chỉ hiển thị các sản phẩm khớp từ khóa VÀ thỏa mãn đồng thời mọi tiêu chí lọc đã chọn (logic AND) (Q2 đã chốt 22/11/2026), giữ nguyên từ khóa tìm kiếm và quay về trang 1. Mỗi tiêu chí lọc chọn duy nhất một giá trị (Q7 đã chốt 22/11/2026).
- **5b. Lọc theo size:** sản phẩm được hiển thị khi có ít nhất một biến thể thuộc size đã chọn, không xét còn hàng hay hết hàng và không tự thêm điều kiện ACTIVE cho bộ lọc size (Q8 đã chốt 22/11/2026, xác nhận lại ngày 23/11/2026).
- **5c. Bỏ lọc:** người dùng xóa một hoặc toàn bộ tiêu chí lọc; hệ thống hiển thị lại kết quả tìm kiếm theo từ khóa và các tiêu chí lọc còn lại (nếu có), quay về trang 1.
- **5d. Đổi tiêu chí sắp xếp:** người dùng chọn tiêu chí sắp xếp khác ("Giá tăng dần", "Giá giảm dần" hoặc "Mới nhất"):
  - "Giá tăng dần": sắp xếp theo `effective_min_price ASC, product_id ASC`.
  - "Giá giảm dần": sắp xếp theo `effective_min_price DESC, product_id ASC`.
  - "Mới nhất": sắp xếp theo `product_created_at DESC, product_id ASC`.
  Trong đó `effective_min_price` là mức giá bán thực tế thấp nhất hiển thị (giá sau khuyến mãi theo sản phẩm nếu có, làm tròn `ROUND_HALF_UP`) tính từ các biến thể `ACTIVE` có `variant_sell_price > 0`. Cả 3 tiêu chí sắp xếp đều có `product_id ASC` làm khóa phụ cuối cùng duy nhất để đảm bảo dữ liệu không bị lặp hoặc bỏ sót khi chuyển trang hoặc tải lại trang. Hệ thống giữ nguyên từ khóa cùng các tiêu chí lọc đang chọn và quay về trang 1 (Q10 đã chốt 23/11/2026, bổ sung tie-breaker ngày 23/11/2026).
- **5e. Chuyển trang:** người dùng chọn trang khác; hệ thống hiển thị sản phẩm của trang đó, giữ nguyên từ khóa tìm kiếm, tiêu chí sắp xếp và các tiêu chí lọc đang chọn trên URL query parameters (Q2, Q6 đã chốt 22/11/2026).
- **3a. Không có kết quả tìm kiếm:** không có sản phẩm Đang bán nào khớp từ khóa, hoặc tất cả sản phẩm khớp từ khóa đều bị loại do không có biến thể ACTIVE có giá > 0, hoặc không khớp bộ lọc; hệ thống hiển thị thông báo "Không tìm thấy sản phẩm phù hợp với '<từ khóa>'" (hoặc "Không có sản phẩm phù hợp" khi kết hợp lọc), kèm tổng số kết quả bằng 0. Ẩn thanh phân trang và không sinh trang 0 (kể cả khi URL có tham số `page`) (Q6 đã chốt 22/11/2026, đồng bộ ngày 23/11/2026).

## Exceptions
- **E1. Từ khóa rỗng hoặc chỉ có khoảng trắng:** người dùng gửi tìm kiếm với từ khóa rỗng hoặc chỉ toàn khoảng trắng (hoặc truy cập trực tiếp URL tìm kiếm không có tham số từ khóa `q`); hệ thống không thực hiện truy vấn cơ sở dữ liệu, hiển thị trang tìm kiếm kèm thông báo "Vui lòng nhập từ khóa" và không hiển thị danh sách sản phẩm (Q4 đã chốt 22/11/2026).
- **E2. Số trang yêu cầu vượt quá tổng số trang:** khi kết quả tìm kiếm có sản phẩm (tổng số trang ≥ 1), nếu người dùng yêu cầu số trang lớn hơn tổng số trang kết quả thì hệ thống hiển thị trang kết quả cuối cùng (Q6 đã chốt 22/11/2026). Trường hợp kết quả tìm kiếm là 0 sản phẩm (0 trang) thì áp dụng theo 3a.
- **E3. Giá trị lọc không tồn tại:** giá trị giới tính, size, danh mục hoặc bộ sưu tập trên URL không tồn tại trong hệ thống; hệ thống bỏ qua tiêu chí không hợp lệ đó và hiển thị danh sách theo từ khóa cùng các tiêu chí hợp lệ còn lại (Q9 đã chốt 22/11/2026).

## Postconditions
- Kết quả tìm kiếm sản phẩm theo từ khóa (và bộ lọc/sắp xếp nếu có) được hiển thị cho người dùng; dữ liệu sản phẩm trong cơ sở dữ liệu không thay đổi.

## Acceptance Criteria

### AC-1: Tìm theo tên sản phẩm
Given: có sản phẩm Đang bán tên "Bikini hoa nhí"
When: người dùng tìm từ khóa "bikini"
Then: sản phẩm "Bikini hoa nhí" có trong kết quả tìm kiếm

### AC-2: Tìm theo mô tả sản phẩm
Given: sản phẩm "Áo bơi liền thân cao cấp" Đang bán có mô tả "Chất liệu thun co giãn chống tia UV"
When: người dùng tìm từ khóa "chống tia UV"
Then: sản phẩm "Áo bơi liền thân cao cấp" có trong kết quả tìm kiếm

### AC-3: Không phân biệt chữ hoa, chữ thường và dấu tiếng Việt
Given: có sản phẩm Đang bán tên "Đồ bơi liền thân"
When: người dùng tìm từ khóa "do boi lien than" hoặc "ĐỒ BƠI"
Then: sản phẩm "Đồ bơi liền thân" có trong kết quả tìm kiếm

### AC-4: Không trả về sản phẩm Ngừng bán và sản phẩm không có biến thể ACTIVE có giá hợp lệ
Given: có 3 sản phẩm khớp từ khóa "bikini":
  - Sản phẩm A ở trạng thái Ngừng bán (`product_status = 'INACTIVE'`)
  - Sản phẩm B ở trạng thái Đang bán (`product_status = 'ACTIVE'`) nhưng chỉ có các biến thể ở trạng thái `INACTIVE` hoặc chưa có giá (`variant_sell_price` IS NULL hoặc ≤ 0)
  - Sản phẩm C ở trạng thái Đang bán (`product_status = 'ACTIVE'`) và có ít nhất 1 biến thể `ACTIVE` với `variant_sell_price > 0`
When: người dùng tìm từ khóa "bikini"
Then: chỉ sản phẩm C xuất hiện trong kết quả tìm kiếm
And: sản phẩm A và sản phẩm B đều bị loại bỏ khỏi kết quả tìm kiếm

### AC-5: Sắp xếp mặc định mới nhất với khóa phụ product_id ASC
Given: có 3 sản phẩm khớp từ khóa "Bikini":
  - Sản phẩm SP-0002 tạo lúc 10:00:00 UTC ngày 15/11/2026
  - Sản phẩm SP-0001 tạo lúc 10:00:00 UTC ngày 15/11/2026 (trùng thời gian tạo với SP-0002)
  - Sản phẩm SP-0003 tạo lúc 08:00:00 UTC ngày 01/11/2026
When: người dùng tìm từ khóa "Bikini" mà không chọn tiêu chí sắp xếp
Then: thứ tự hiển thị chính xác là SP-0001 (do cùng thời gian tạo mới nhất nhưng `product_id` nhỏ hơn), tiếp theo là SP-0002, và cuối cùng là SP-0003

### AC-6: Đổi tiêu chí sắp xếp theo giá tăng dần và giảm dần có phân trang 12 sp/trang và khóa phụ product_id ASC
Given: kết quả tìm kiếm từ khóa "Đồ bơi" chỉ có đúng 15 sản phẩm đủ điều kiện thỏa mãn:
  - Sản phẩm A (SP-0002) có giá gốc thấp nhất 300.000đ và có khuyến mãi giảm 50% nên giá sau giảm là 150.000đ
  - Sản phẩm B (SP-0001) có giá gốc thấp nhất 200.000đ không có khuyến mãi nên giá là 200.000đ
  - 13 sản phẩm khác (từ SP-0003 đến SP-0015) đều có cùng giá bán thực tế thấp nhất hiển thị là 250.000đ
When: người dùng chọn tiêu chí sắp xếp "Giá tăng dần"
Then: hệ thống đưa danh sách về trang 1 và hiển thị đúng 12 sản phẩm đầu tiên gồm: SP-0002 (150.000đ), SP-0001 (200.000đ), và 10 sản phẩm bằng giá xếp theo thứ tự `product_id ASC` (SP-0003, SP-0004, ..., SP-0012)
And: từ khóa "Đồ bơi" cùng các bộ lọc đang chọn vẫn được giữ nguyên
When: người dùng bấm chuyển sang trang 2
Then: trang 2 hiển thị đúng 3 sản phẩm còn lại gồm: SP-0013, SP-0014, SP-0015 (đều có giá 250.000đ và duy trì thứ tự `product_id ASC`)
And: không có sản phẩm nào bị lặp lại hoặc bị bỏ sót giữa trang 1 và trang 2; khi người dùng tải lại trang (reload), kết quả hiển thị trên trang 2 vẫn giữ nguyên
When: người dùng đổi sang tiêu chí sắp xếp "Giá giảm dần"
Then: hệ thống đưa danh sách về trang 1 và hiển thị đúng 12 sản phẩm đầu tiên gồm: 12 sản phẩm bằng giá 250.000đ xếp theo thứ tự `product_id ASC` (SP-0003, SP-0004, ..., SP-0014)
And: từ khóa "Đồ bơi" cùng các bộ lọc đang chọn vẫn được giữ nguyên
When: người dùng bấm chuyển sang trang 2
Then: trang 2 hiển thị đúng 3 sản phẩm còn lại theo thứ tự: SP-0015 (giá 250.000đ), tiếp theo là SP-0001 (giá 200.000đ), và cuối cùng là SP-0002 (giá sau khuyến mãi 150.000đ)
And: không có sản phẩm nào bị lặp lại hoặc bị bỏ sót giữa trang 1 và trang 2; các tham số tìm kiếm và bộ lọc trên URL query parameters vẫn được duy trì

### AC-7: Kết hợp đồng thời nhiều tiêu chí lọc (AND)
Given: từ khóa "Bikini" khớp với 3 sản phẩm:
  - Sản phẩm A: danh mục "Bikini", giới tính "Nữ"
  - Sản phẩm B: danh mục "Bikini", giới tính "Nam"
  - Sản phẩm C: danh mục "Áo bơi", giới tính "Nữ"
When: người dùng tìm từ khóa "Bikini" và chọn đồng thời bộ lọc danh mục "Bikini" và giới tính "Nữ"
Then: chỉ sản phẩm A được hiển thị trong kết quả tìm kiếm
And: từ khóa "Bikini" cùng hai tiêu chí lọc đều được duy trì trên URL query parameters, danh sách quay về trang 1

### AC-8: Phân trang kết quả, loại sản phẩm không hợp lệ trước phân trang và giữ tham số
Given: từ khóa "Áo tắm" khớp với:
  - 13 sản phẩm ở trạng thái Đang bán, có ít nhất một biến thể ACTIVE có giá > 0 và đều thuộc giới tính "Nữ"
  - 1 sản phẩm ở trạng thái Đang bán, cũng thuộc giới tính "Nữ" nhưng bị loại do chỉ có các biến thể ở trạng thái INACTIVE
And: người dùng đang tìm kiếm với bộ lọc giới tính "Nữ" và tiêu chí sắp xếp "Giá tăng dần"
When: người dùng gửi yêu cầu tìm kiếm từ khóa "Áo tắm"
Then: hệ thống tính toán trên tập sản phẩm hợp lệ sau khi loại trừ, tổng số kết quả hiển thị là 13 sản phẩm
And: trang 1 hiển thị đúng 12 sản phẩm đầu tiên
When: người dùng bấm chuyển sang trang 2
Then: trang 2 hiển thị đúng 1 sản phẩm còn lại
And: không xảy ra lặp lại sản phẩm giữa trang 1 và trang 2 hoặc bỏ sót sản phẩm
And: từ khóa "Áo tắm", bộ lọc giới tính "Nữ" và tiêu chí sắp xếp "Giá tăng dần" vẫn được giữ nguyên trên URL query parameters

### AC-9: Không có kết quả tìm kiếm và trường hợp toàn bộ sản phẩm bị ẩn
Given: không có sản phẩm Đang bán nào khớp với từ khóa "xyz123", hoặc có sản phẩm khớp từ khóa "Áo lặn" nhưng tất cả sản phẩm đó đều không có biến thể ACTIVE có giá > 0
When: người dùng tìm từ khóa "xyz123" hoặc "Áo lặn"
Then: hệ thống hiển thị thông báo "Không tìm thấy sản phẩm phù hợp với '<từ khóa>'"
And: tổng số kết quả hiển thị là 0, không hiển thị thanh phân trang và không sinh trang 0

### AC-10: Từ khóa rỗng hoặc chỉ có khoảng trắng
Given: người dùng để trống ô tìm kiếm hoặc chỉ nhập khoảng trắng "   "
When: người dùng gửi yêu cầu tìm kiếm lên hệ thống
Then: hệ thống không thực hiện truy vấn cơ sở dữ liệu
And: hệ thống hiển thị thông báo "Vui lòng nhập từ khóa" và không hiển thị danh sách sản phẩm

### AC-11: Cắt tỉa khoảng trắng và giới hạn độ dài từ khóa tối đa 100 ký tự
Given: có sản phẩm Đang bán tên "Bikini chấm bi"
When: người dùng gửi tìm kiếm với chuỗi có khoảng trắng ở hai đầu "   Bikini chấm bi   "
Then: hệ thống tự động cắt tỉa khoảng trắng thành "Bikini chấm bi" và trả về sản phẩm "Bikini chấm bi" trong kết quả
And: nếu người dùng nhập chuỗi dài 120 ký tự bắt đầu bằng 100 ký tự hợp lệ và 20 ký tự thừa ở cuối, hệ thống tự động cắt lấy đúng 100 ký tự đầu tiên sau khi trim để thực hiện tìm kiếm

### AC-12: Số trang yêu cầu vượt quá tổng số trang
Given: kết quả tìm kiếm có sản phẩm và chỉ có 2 trang (tổng số trang = 2)
When: người dùng truy cập trang 5 trên URL query (`?q=bikini&page=5`)
Then: hệ thống hiển thị dữ liệu của trang 2 (trang cuối cùng)

### AC-13: Thông tin hiển thị trên thẻ sản phẩm và phân biệt biến thể
Given: sản phẩm A Đang bán có:
  - Biến thể 1: trạng thái `INACTIVE`, size S, giá 100.000đ, tồn kho = 10
  - Biến thể 2: trạng thái `ACTIVE`, size M, giá 200.000đ, tồn kho = 0
  - Biến thể 3: trạng thái `ACTIVE`, size L, giá 250.000đ, tồn kho = 0
  - Sản phẩm A đang có khuyến mãi theo sản phẩm giảm 10%
And: sản phẩm B Đang bán có biến thể `ACTIVE`, size M, giá 300.000đ, tồn kho = 5
When: người dùng tìm kiếm từ khóa khớp với cả sản phẩm A và B
Then: thẻ sản phẩm A hiển thị giá bán thấp nhất lấy từ biến thể ACTIVE có giá > 0 là 200.000đ (bỏ qua biến thể INACTIVE giá 100.000đ dù còn tồn kho)
And: giá sau khuyến mãi của sản phẩm A hiển thị là 180.000đ (200.000đ × 90%, làm tròn `ROUND_HALF_UP`)
And: thẻ sản phẩm A hiển thị nhãn "Hết hàng" (vì tất cả biến thể ACTIVE có giá > 0 đều có tồn kho bằng 0)
And: thẻ sản phẩm B hiển thị giá 300.000đ và không có nhãn "Hết hàng"

### AC-14: HTTP header không cache kết quả tìm kiếm
Given: người dùng gửi yêu cầu tìm kiếm sản phẩm với từ khóa "Bikini"
When: hệ thống trả về kết quả trang tìm kiếm đầy đủ hoặc mảnh HTMX
Then: HTTP response header chứa `Cache-Control: private, no-cache` và `Vary: HX-Request`
And: hệ thống không trả về header `ETag` và không lưu kết quả tìm kiếm vào cache Redis (khi Redis tăng version catalog bị lỗi cũng không khiến tìm kiếm phải đợi TTL, mọi request tìm kiếm mới luôn đọc trực tiếp từ Database)

### AC-15: Điều hướng xem chi tiết sản phẩm
Given: người dùng đang ở trang kết quả tìm kiếm có sản phẩm "Bikini hoa nhí"
When: người dùng bấm vào thẻ sản phẩm "Bikini hoa nhí"
Then: hệ thống điều hướng người dùng tới trang chi tiết của sản phẩm đó (UC-12)

### AC-16: Giá trị lọc trên URL không tồn tại
Given: trong hệ thống không tồn tại danh mục có mã "danh-muc-la"
When: người dùng tìm từ khóa "Bikini" và truy cập URL có bộ lọc danh mục không tồn tại (`?q=bikini&category=danh-muc-la`)
Then: hệ thống bỏ qua tiêu chí lọc danh mục đó và hiển thị danh sách kết quả tìm kiếm theo từ khóa "Bikini" cùng các tiêu chí hợp lệ còn lại

## Dependencies
- **Upstream UC:** UC-14 Quản lý sản phẩm, UC-16 Quản lý giá bán theo size, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm
- **Internal Services:**
  - Module `promotion`: Service công khai để lấy thông tin khuyến mãi theo sản phẩm đang hiệu lực.
  - Module `inventory`: Service công khai để lấy số lượng tồn kho theo biến thể (`inventory.stock`) xác định nhãn "Hết hàng".
- **External Systems:** không có

## Notes
- **Ranh giới Modular Monolith (AGENTS.md):** Module `catalog` không truy cập trực tiếp bảng `promotion.product_promotion` hay `inventory.stock`. Mọi dữ liệu khuyến mãi và tồn kho đều thông qua Service công khai của module tương ứng.
- **Tiền tệ & Số học tài chính (AGENTS.md):** Tiền tệ luôn biểu diễn bằng số nguyên VND. Mức giá sau khuyến mãi được tính toán và làm tròn theo phương thức `ROUND_HALF_UP`.
- **Constraint Cache (BR-GIAIDOAN1, chốt 21/11/2026):**
  - Kết quả tìm kiếm **KHÔNG cache ở Redis** (đọc trực tiếp từ Database do từ khóa đa dạng). Lỗi tăng version catalog ở Redis không ảnh hưởng tìm kiếm, truy vấn mới luôn đọc trực tiếp từ DB.
  - HTTP header của trang tìm kiếm và mảnh HTMX: `Cache-Control: private, no-cache`, `Vary: HX-Request`, không dùng `ETag`.
- **Out of Scope (BR-GIAIDOAN1):** bộ lọc nâng cao, tự động gợi ý từ khóa (autocomplete), tìm kiếm mờ (fuzzy search) ở Giai đoạn 1.

### Quyết định đã chốt
- Lọc sản phẩm theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- Kết quả tìm kiếm KHÔNG cache ở Redis; HTTP header `Cache-Control: private, no-cache`, `Vary: HX-Request`, không dùng ETag (đã chốt 21/11/2026, BR-GIAIDOAN1).
- Tìm kiếm không phân biệt chữ hoa, chữ thường và dấu tiếng Việt (PostgreSQL `unaccent` + `ILIKE`) trên `product_name` và `product_description` của các sản phẩm có `product_status = 'ACTIVE'` (Q1 đã chốt 22/11/2026).
- Hỗ trợ bộ lọc kết hợp (giới tính, size, danh mục, bộ sưu tập) trên kết quả tìm kiếm theo logic AND; khi lọc, đổi sắp xếp hoặc chuyển trang luôn duy trì từ khóa tìm kiếm `q` trên URL query parameters (Q2 đã chốt 22/11/2026).
- Sắp xếp mặc định theo sản phẩm mới nhất (`product_created_at` giảm dần) (Q3 đã chốt 22/11/2026).
- Từ khóa rỗng hoặc chỉ có khoảng trắng: client chặn submit bằng `required`, server hiển thị thông báo "Vui lòng nhập từ khóa" và không query DB; từ khóa được cắt tỉa khoảng trắng hai đầu (trim), nếu sau trim dài hơn 100 ký tự thì tự động cắt lấy đúng 100 ký tự đầu tiên để tìm kiếm (Q4 đã chốt 22/11/2026).
- Thẻ sản phẩm hiển thị: ảnh đại diện (`gallery_order_no = 1`), tên sản phẩm. Giá bán thấp nhất theo size và dùng để sắp xếp chỉ lấy từ các biến thể `ACTIVE` có `variant_sell_price > 0`, không xét tồn kho để tính giá. Giá sau khuyến mãi theo sản phẩm (nếu có) tính trên mức giá này và làm tròn theo quy tắc `ROUND_HALF_UP`. Nhãn "Hết hàng" hiển thị khi không có biến thể `ACTIVE` có giá > 0 nào còn tồn khả dụng > 0 (Q6 đã chốt 22/11/2026, đồng bộ ngày 23/11/2026 theo UC-10).
- Loại trừ sản phẩm cha `ACTIVE` không còn bất kỳ biến thể `ACTIVE` có `variant_sell_price > 0` nào khỏi tập kết quả tìm kiếm TRƯỚC KHI tính tổng số, tổng trang và phân trang LIMIT/OFFSET. Không ẩn sản phẩm chỉ vì hết tồn kho. Nếu tập còn lại rỗng thì dùng luồng không có kết quả (3a), không sinh trang 0 (đồng bộ ngày 23/11/2026 theo UC-10/UC-14).
- Phân trang cố định 12 sản phẩm/trang; số trang vượt quá tổng số trang (khi có sản phẩm) thì hiển thị trang cuối; không có kết quả hiển thị thông báo "Không tìm thấy sản phẩm phù hợp với '<từ khóa>'" (Q6 đã chốt 22/11/2026).
- Cả 3 tiêu chí sắp xếp đều có `product_id ASC` làm khóa phụ cuối cùng duy nhất: `product_created_at DESC, product_id ASC`; `effective_min_price ASC, product_id ASC`; `effective_min_price DESC, product_id ASC` nhằm đảm bảo dữ liệu cố định không bị lặp hay bỏ sót sản phẩm khi chuyển trang hoặc reload (Q10 đã chốt 23/11/2026, bổ sung tie-breaker ngày 23/11/2026).
- Mỗi tiêu chí lọc chọn duy nhất một giá trị (single-select filter) (Q7 đã chốt 22/11/2026).
- Lọc theo size: sản phẩm có ít nhất một biến thể size đó, không xét còn hàng hay hết hàng và không tự thêm điều kiện ACTIVE cho bộ lọc size (Q8 đã chốt 22/11/2026, xác nhận ngày 23/11/2026).
- Giá trị lọc trên URL không tồn tại trong hệ thống thì bỏ qua tiêu chí đó và hiển thị theo các tiêu chí hợp lệ còn lại (Q9 đã chốt 22/11/2026).

### Giả định [GD]
- Hiện tại không còn giả định nội bộ hoặc câu hỏi mở nào bị chặn cho UC-11 (toàn bộ các quyết định và dependency đồng bộ đã được developer phê duyệt chốt).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-22): chốt Q1 đến Q6: đồng bộ cache theo BR-GIAIDOAN1 (không cache kết quả tìm kiếm ở Redis), chốt phạm vi tìm kiếm unaccent trên tên và mô tả sản phẩm, bổ sung bộ lọc kết hợp (giới tính, size, danh mục, bộ sưu tập), chốt sắp xếp mặc định mới nhất, chuẩn hóa phân trang 12 sp/trang và xử lý từ khóa rỗng/trim/cắt lấy 100 ký tự đầu; bổ sung AC-2, AC-5 đến AC-15. Tách bạch các giả định Q7, Q8, Q9 chờ developer quyết định.
- v3 (2026-11-22): chốt toàn bộ Q7 (mỗi tiêu chí 1 giá trị), Q8 (lọc size không xét tồn kho), Q9 (bỏ qua giá trị lọc không hợp lệ trên URL); gỡ bỏ toàn bộ nhãn [GD]; bổ sung AC-16; chuyển Status sang ready.
- v4 (2026-11-23): mở đợt rà soát vòng 2; xử lý phát hiện #6 và phối hợp #2: developer chốt "accept" cho UC-11-Q10 (sắp xếp giá tăng/giảm theo giá thực tế thấp nhất sau khuyến mãi theo sản phẩm, làm tròn ROUND_HALF_UP); cập nhật 5d, AC-6 (bổ sung cả hai nhánh sắp xếp Giá tăng dần và Giá giảm dần cùng fixture A 150k và B 200k), Quyết định đã chốt; ghi nhận Dependency #2 chờ đồng bộ từ UC-10; giữ Status draft.
- v5 (2026-11-23): developer phê duyệt đồng bộ toàn diện catalog theo UC-10 và UC-14: gỡ bỏ Dependency #2; chốt giá min và sắp xếp chỉ từ biến thể ACTIVE có giá > 0 (không xét tồn); nhãn Hết hàng khi không có biến thể ACTIVE có giá > 0 nào còn tồn > 0; loại sản phẩm cha không có biến thể ACTIVE có giá > 0 trước khi tính tổng số/phân trang; bổ sung khóa phụ `product_id ASC` cho cả 3 tiêu chí sắp xếp; chuẩn hóa fixture qua các trang trong AC-6 (15 sản phẩm phân bổ trang 1: 12 SP, trang 2: 3 SP cho cả 2 chiều tăng/giảm) và AC-8 (13 SP hợp lệ + 1 SP bị loại đều khớp giới tính Nữ); chuyển Status sang ready.
