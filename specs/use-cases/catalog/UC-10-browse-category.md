# UC-10: Xem sản phẩm theo danh mục

## Metadata
- **ID:** UC-10
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng chọn một danh mục từ menu, trang chủ hoặc truy cập trực tiếp qua đường dẫn (URL) danh mục.

## Preconditions
- Danh mục tồn tại trong hệ thống.
- Website đang hoạt động.

## Main Flow
1. Người dùng chọn một danh mục (hoặc truy cập URL danh mục).
2. Hệ thống kiểm tra danh mục có tồn tại hay không. Nếu không tồn tại, chuyển sang Exception E1.
3. Hệ thống truy vấn danh sách sản phẩm ở trạng thái Đang bán (`product_status = ACTIVE`) thuộc danh mục đã chọn. Trong danh sách này, nếu có từng sản phẩm không có bất kỳ biến thể `variant_status = ACTIVE` có giá bán hợp lệ (> 0) nào thì hệ thống tự động loại trừ (tạm ẩn) sản phẩm đó theo Exception E4. Việc loại trừ này được thực hiện TRƯỚC KHI tính tổng số sản phẩm, tổng số trang và lấy dữ liệu phân trang. Nếu sau khi loại trừ danh mục không còn sản phẩm Đang bán hợp lệ nào, chuyển sang Alternative Flow 3a.
4. Hệ thống áp dụng sắp xếp mặc định theo sản phẩm mới nhất (thời gian tạo `product_created_at` giảm dần; trường hợp trùng thời điểm tạo thì sử dụng `product_id` tăng dần làm tiêu chí sắp xếp phụ duy nhất để đảm bảo phân trang tất định).
5. Hệ thống hiển thị trang 1 với số sản phẩm mỗi trang cố định là 12, kèm điều khiển phân trang (danh sách trang, nút Trước/Sau) và tổng số sản phẩm tìm thấy.
6. Hệ thống hiển thị bộ lọc gồm 4 tiêu chí: Giới tính, Size, Danh mục, Bộ sưu tập. Mỗi tiêu chí hiển thị danh sách các giá trị tương ứng để người dùng lựa chọn.
7. Mỗi sản phẩm trong danh sách được hiển thị dưới dạng thẻ gồm:
   - Ảnh đại diện của sản phẩm (lấy ảnh có thứ tự `gallery_order_no = 1` trong gallery).
   - Tên sản phẩm.
   - Giá bán: hiển thị mức giá thấp nhất trong các biến thể Đang bán (`variant_status = ACTIVE`) và có giá hợp lệ (> 0) của sản phẩm. Nếu các size có mức giá khác nhau, hiển thị theo định dạng `Từ <giá thấp nhất>đ`. Nếu tất cả các size cùng mức giá, hiển thị `<giá>đ`.
   - Giá sau khuyến mãi theo sản phẩm (nếu sản phẩm đang có khuyến mãi theo sản phẩm còn hiệu lực từ module `promotion`): hiển thị giá gốc gạch ngang và giá sau giảm `Từ <giá thấp nhất sau giảm>đ` (hoặc `<giá sau giảm>đ`), làm tròn số nguyên VND theo quy tắc `ROUND_HALF_UP`.
   - Nhãn "Hết hàng": hiển thị khi tất cả các biến thể Đang bán (`variant_status = ACTIVE`) có giá hợp lệ (> 0) của sản phẩm đều có tồn kho bằng 0 (nghĩa là không còn biến thể ACTIVE nào có giá hợp lệ và có tồn kho khả dụng > 0 để mua được) (lấy từ module `inventory`).
8. Người dùng bấm vào một thẻ sản phẩm để chuyển sang màn hình Xem chi tiết sản phẩm (UC-12).

## Alternative Flows
- **3a. Danh mục không có sản phẩm Đang bán:**
  - Điểm xuất phát: Bước 3 trong Main Flow.
  - Điều kiện vào: Danh mục tồn tại nhưng không có sản phẩm nào ở trạng thái Đang bán hợp lệ (`total_products = 0`, `total_pages = 0`).
  - Xử lý: Hệ thống hiển thị thông báo "Chưa có sản phẩm trong danh mục này". Không hiển thị danh sách sản phẩm và ẩn thanh phân trang (kể cả khi URL có tham số `page`, không sinh trang 0). Kết thúc luồng tại đây.
- **4a. Đổi tiêu chí sắp xếp:**
  - Điểm xuất phát: Bước 4 trong Main Flow.
  - Điều kiện vào: Người dùng chọn một tiêu chí sắp xếp khác từ danh sách lựa chọn: "Giá tăng dần" hoặc "Giá giảm dần".
  - Xử lý: Hệ thống sắp xếp lại danh sách sản phẩm theo giá bán thực tế thấp nhất hiển thị (tính từ các biến thể `variant_status = ACTIVE`, giá sau khuyến mãi nếu có) tăng dần hoặc giảm dần; trường hợp nhiều sản phẩm bằng giá thì luôn sử dụng `product_id` tăng dần làm tiêu chí sắp xếp phụ duy nhất (không đảo chiều `product_id` theo chiều giá) để đảm bảo phân trang tất định, đưa danh sách về trang 1, giữ nguyên các tiêu chí lọc đang chọn. Quay lại bước 5.
- **5a. Chuyển trang:**
  - Điểm xuất phát: Bước 5 trong Main Flow.
  - Điều kiện vào: Danh mục có ít nhất một trang sản phẩm (`total_pages ≥ 1`) và người dùng bấm chọn một số trang cụ thể hoặc nút chuyển trang Trước/Sau hợp lệ (`1 ≤ page ≤ total_pages`).
  - Xử lý: Hệ thống hiển thị danh sách sản phẩm của trang được chọn (tối đa 12 sản phẩm), giữ nguyên các tiêu chí lọc và sắp xếp hiện tại. Tiếp tục bước 6.
- **6a. Lọc sản phẩm:**
  - Điểm xuất phát: Bước 6 trong Main Flow.
  - Điều kiện vào: Người dùng chọn một giá trị lọc cho một hoặc nhiều tiêu chí (Giới tính, Size, Bộ sưu tập).
  - Quy tắc: Mỗi tiêu chí chỉ cho phép chọn tối đa 1 giá trị (single-select).
  - Xử lý: Hệ thống lọc danh sách sản phẩm thỏa mãn đồng thời tất cả các tiêu chí đã chọn (phép VÀ - AND), đưa danh sách về trang 1 và cập nhật lại phân trang cùng tổng số sản phẩm khớp bộ lọc. Quay lại bước 5.
- **6b. Lọc theo size:**
  - Điểm xuất phát: Bước 6 trong Main Flow (trường hợp người dùng chọn tiêu chí Size).
  - Xử lý: Hệ thống hiển thị các sản phẩm có ít nhất một biến thể thuộc size đã chọn, không phân biệt biến thể đó còn hàng hay hết hàng (theo quyết định đã chốt 22/11/2026). Nếu tất cả biến thể `variant_status = ACTIVE` có giá hợp lệ của sản phẩm đều hết hàng, thẻ sản phẩm vẫn hiển thị kèm nhãn "Hết hàng". Quay lại bước 5.
- **6c. Chọn danh mục khác trong bộ lọc:**
  - Điểm xuất phát: Bước 6 trong Main Flow (người dùng chọn một danh mục khác tại tiêu chí Danh mục trong bộ lọc).
  - Xử lý: Hệ thống điều hướng sang trang của danh mục mới được chọn, giữ nguyên các tiêu chí lọc còn lại (Giới tính, Size, Bộ sưu tập nếu có), đưa về trang 1 và áp dụng tiêu chí sắp xếp hiện tại. Quay lại bước 1 cho danh mục mới.
- **6d. Bỏ tiêu chí lọc:**
  - Điểm xuất phát: Bước 6 trong Main Flow.
  - Điều kiện vào: Người dùng bấm bỏ chọn một tiêu chí lọc cụ thể hoặc chọn "Xóa tất cả bộ lọc".
  - Xử lý: Hệ thống cập nhật lại danh sách sản phẩm theo các tiêu chí còn lại (hoặc toàn bộ sản phẩm Đang bán của danh mục nếu bỏ hết), đưa về trang 1 và cập nhật lại phân trang. Quay lại bước 5.
- **6e. Không có sản phẩm khớp bộ lọc:**
  - Điểm xuất phát: Bước 6 trong Main Flow.
  - Điều kiện vào: Sau khi áp dụng bộ lọc, không có sản phẩm nào thỏa mãn đồng thời các tiêu chí đã chọn (`total_products = 0`, `total_pages = 0`).
  - Xử lý: Hệ thống hiển thị thông báo "Không có sản phẩm phù hợp". Thanh phân trang bị ẩn (không sinh trang 0 kể cả khi URL có tham số `page`). Kết thúc luồng tại đây.

## Exceptions
- **E1. Danh mục không tồn tại:**
  - Điểm xuất phát: Bước 2 trong Main Flow.
  - Điều kiện vào: Mã định danh danh mục trên URL không tồn tại trong cơ sở dữ liệu.
  - Xử lý: Hệ thống hiển thị trang thông báo lỗi "Không tìm thấy danh mục" (HTTP 404). Kết thúc luồng tại đây.
- **E2. Số trang yêu cầu không hợp lệ hoặc vượt quá tổng số trang:**
  - Điểm xuất phát: Bước 5 trong Main Flow (hoặc khi người dùng truy cập trực tiếp URL có tham số `page`).
  - Xử lý:
    + Khi danh sách có ít nhất một trang (`total_pages ≥ 1`):
      * Nếu `page > total_pages`: Hệ thống hiển thị dữ liệu của trang cuối cùng (`total_pages`).
      * Nếu `page < 1` hoặc tham số `page` không phải số nguyên dương hợp lệ (ví dụ chuỗi ký tự, số âm): Hệ thống hiển thị dữ liệu của trang 1.
    + Khi danh sách rỗng (`total_pages = 0`, do danh mục chưa có sản phẩm hoặc bộ lọc không khớp sản phẩm nào): Hệ thống không áp dụng phân trang, không sinh trang 0, mà chuyển sang hiển thị thông báo rỗng theo Alternative Flow 3a hoặc 6e.
- **E3. Giá trị lọc không tồn tại:**
  - Điểm xuất phát: Bước 6 trong Main Flow (khi tham số lọc trên URL chứa giá trị không hợp lệ).
  - Điều kiện vào: Giá trị lọc gửi lên (giới tính, size, danh mục, bộ sưu tập) không tồn tại trong danh mục thuộc tính hệ thống.
  - Xử lý: Hệ thống tự động bỏ qua tiêu chí không hợp lệ đó và hiển thị danh sách sản phẩm theo các tiêu chí hợp lệ còn lại.
- **E4. Loại trừ từng sản phẩm Đang bán không có biến thể ACTIVE có giá hợp lệ:**
  - Điểm xuất phát: Bước 3 trong Main Flow.
  - Điều kiện vào: Trong danh sách sản phẩm `product_status = ACTIVE` của danh mục, phát hiện sản phẩm mà tất cả các biến thể đều có `variant_status = INACTIVE` hoặc chưa có biến thể ACTIVE nào có giá bán hợp lệ (> 0).
  - Xử lý: Hệ thống tự động loại trừ (tạm ẩn) từng sản phẩm không đủ điều kiện này khỏi kết quả truy vấn TRƯỚC KHI tính tổng số sản phẩm và phân trang, sau đó tiếp tục xử lý và hiển thị danh sách các sản phẩm hợp lệ còn lại. Luồng duyệt danh mục không bị dừng lại khi có sản phẩm bị loại trừ. Nếu sau khi loại trừ danh mục không còn sản phẩm hợp lệ nào (`total_products = 0`, `total_pages = 0`), hệ thống chuyển sang Alternative Flow 3a (hoặc 6e nếu lọc) hiển thị thông báo rỗng, không sinh trang 0.

## Postconditions
- Danh sách sản phẩm theo danh mục và bộ lọc được hiển thị cho người dùng; dữ liệu sản phẩm và danh mục trong hệ thống không bị thay đổi.

## Acceptance Criteria

### AC-1: Chỉ hiển thị sản phẩm Đang bán của danh mục
Given: danh mục "Bikini" có 3 sản phẩm ở trạng thái Đang bán (`product_status = ACTIVE`, đều có ít nhất một biến thể `variant_status = ACTIVE` có giá bán hợp lệ) và 1 sản phẩm ở trạng thái Ngừng bán (`product_status = INACTIVE`)
When: người dùng mở danh mục "Bikini"
Then: chỉ 3 sản phẩm Đang bán được hiển thị trong danh sách
And: sản phẩm Ngừng bán không xuất hiện

### AC-2: Phân trang cố định 12 sản phẩm mỗi trang
Given: danh mục "Đồ bơi một mảnh" có 30 sản phẩm Đang bán (`product_status = ACTIVE` và đều có biến thể `variant_status = ACTIVE` có giá bán hợp lệ)
When: người dùng mở danh mục
Then: trang 1 hiển thị đúng 12 sản phẩm đầu tiên
And: tổng số sản phẩm hiển thị là 30, kèm điều khiển phân trang gồm 3 trang

### AC-3: Sắp xếp mặc định theo sản phẩm mới nhất
Given: danh mục có sản phẩm A (tạo lúc 08:00 UTC ngày 01/11/2026) và sản phẩm B (tạo lúc 10:00 UTC ngày 10/11/2026) đều ở trạng thái Đang bán và có biến thể ACTIVE có giá bán hợp lệ
When: người dùng mở danh mục mà không chọn tiêu chí sắp xếp
Then: sản phẩm B xuất hiện trước sản phẩm A trong danh sách

### AC-4: Đổi tiêu chí sắp xếp sang Giá tăng dần căn cứ theo giá sau khuyến mãi
Given: sản phẩm A có giá gốc 300.000đ và đang có khuyến mãi theo sản phẩm giảm 50% nên giá sau giảm là 150.000đ; sản phẩm B có giá 200.000đ không có khuyến mãi (cả hai đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn tiêu chí sắp xếp "Giá tăng dần"
Then: sản phẩm A (giá thực tế 150.000đ) xuất hiện trước sản phẩm B (giá thực tế 200.000đ)
And: danh sách quay về trang 1

### AC-5: Đổi tiêu chí sắp xếp sang Giá giảm dần
Given: sản phẩm A có giá thấp nhất thực tế 300.000đ và sản phẩm B có giá thấp nhất thực tế 500.000đ (cả hai đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn tiêu chí sắp xếp "Giá giảm dần"
Then: sản phẩm B xuất hiện trước sản phẩm A
And: danh sách quay về trang 1

### AC-6: Hiển thị giá thấp nhất theo size và giá khuyến mãi trên thẻ sản phẩm
Given: sản phẩm A có size S giá 300.000đ, size M giá 350.000đ (đều là biến thể ACTIVE) và đang có khuyến mãi theo sản phẩm giảm 10%
When: người dùng xem thẻ sản phẩm A trong danh sách danh mục
Then: thẻ hiển thị ảnh đại diện có thứ tự gallery đầu tiên (`gallery_order_no = 1`), tên sản phẩm A
And: giá gốc hiển thị gạch ngang `Từ 300.000đ`
And: giá sau giảm hiển thị nổi bật `Từ 270.000đ` (300.000đ × 90%, làm tròn `ROUND_HALF_UP`)

### AC-7: Hiển thị nhãn Hết hàng trên thẻ sản phẩm
Given: sản phẩm B có 2 biến thể (Đỏ×S và Đỏ×M, đều có `variant_status = ACTIVE` và có giá bán hợp lệ), cả 2 biến thể đều có tồn kho bằng 0 trong kho (`inventory.stock`)
When: người dùng xem danh sách sản phẩm của danh mục
Then: thẻ sản phẩm B vẫn hiển thị và có gắn nhãn "Hết hàng" (không bị ẩn)
And: người dùng vẫn có thể bấm vào thẻ để xem chi tiết sản phẩm

### AC-8: Lọc theo giới tính
Given: danh mục có 2 sản phẩm gắn giới tính "Nữ" và 1 sản phẩm gắn giới tính "Nam" (đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn lọc giới tính "Nữ"
Then: chỉ 2 sản phẩm giới tính "Nữ" được hiển thị
And: danh sách đưa về trang 1

### AC-9: Lọc theo size không xét trạng thái tồn kho
Given: sản phẩm A có biến thể size M (tồn kho = 0), sản phẩm B có biến thể size M (tồn kho = 5), sản phẩm C chỉ có size S (tồn kho = 10) (cả ba đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn lọc size "M"
Then: cả sản phẩm A và sản phẩm B đều được hiển thị
And: sản phẩm C không được hiển thị

### AC-10: Lọc theo bộ sưu tập
Given: sản phẩm A thuộc bộ sưu tập "Hè 2026", sản phẩm B không thuộc bộ sưu tập "Hè 2026" (cả hai đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn lọc bộ sưu tập "Hè 2026"
Then: chỉ sản phẩm A được hiển thị

### AC-11: Kết hợp nhiều tiêu chí lọc (phép VÀ - AND)
Given: sản phẩm A có giới tính "Nữ" và có biến thể size M; sản phẩm B có giới tính "Nữ" nhưng chỉ có size S; sản phẩm C có giới tính "Nam" và có biến thể size M (cả ba đều Đang bán và có biến thể ACTIVE có giá hợp lệ)
When: người dùng chọn lọc giới tính "Nữ" và chọn lọc size "M"
Then: chỉ sản phẩm A được hiển thị thỏa mãn đồng thời cả 2 tiêu chí

### AC-12: Chọn danh mục khác trong bộ lọc
Given: người dùng đang xem danh mục "Bikini" và đang áp dụng bộ lọc giới tính "Nữ"
When: người dùng chọn danh mục "Áo bơi liền thân" tại bộ lọc
Then: hệ thống điều hướng sang trang danh mục "Áo bơi liền thân"
And: bộ lọc giới tính "Nữ" vẫn được giữ nguyên
And: danh sách hiển thị các sản phẩm của "Áo bơi liền thân" thỏa mãn giới tính "Nữ" tại trang 1

### AC-13: Bỏ tiêu chí lọc
Given: người dùng đang lọc danh mục với tiêu chí giới tính "Nữ" và size "M"
When: người dùng bấm bỏ tiêu chí lọc size "M"
Then: hệ thống hiển thị lại các sản phẩm thỏa mãn tiêu chí giới tính "Nữ" (mọi size) tại trang 1

### AC-14: Không có sản phẩm khớp bộ lọc
Given: trong danh mục không có sản phẩm nào thuộc giới tính "Nam" có size "XS"
When: người dùng chọn lọc giới tính "Nam" và size "XS"
Then: hệ thống hiển thị thông báo "Không có sản phẩm phù hợp"
And: tổng số sản phẩm hiển thị là 0, không hiển thị thanh phân trang

### AC-15: Giữ lọc và sắp xếp khi chuyển trang hợp lệ
Given: danh mục có 25 sản phẩm giới tính "Nữ" (đều Đang bán và có biến thể ACTIVE có giá hợp lệ), người dùng chọn lọc giới tính "Nữ" và sắp xếp "Giá tăng dần"
When: người dùng chuyển sang trang 2
Then: trang 2 hiển thị các sản phẩm tiếp theo vẫn thỏa mãn giới tính "Nữ" và vẫn được sắp xếp theo "Giá tăng dần"

### AC-16: Danh mục không có sản phẩm Đang bán
Given: danh mục "Phụ kiện bơi" không có sản phẩm nào ở trạng thái Đang bán
When: người dùng mở danh mục "Phụ kiện bơi"
Then: hệ thống hiển thị thông báo "Chưa có sản phẩm trong danh mục này"
And: không hiển thị danh sách sản phẩm và phân trang

### AC-17: Danh mục không tồn tại
Given: đường dẫn danh mục chứa mã danh mục không tồn tại trong hệ thống
When: người dùng truy cập đường dẫn đó
Then: hệ thống trả về mã trạng thái HTTP 404 và hiển thị trang thông báo "Không tìm thấy danh mục"

### AC-18: Số trang yêu cầu vượt quá tổng số trang khi có dữ liệu
Given: danh mục có tổng cộng 2 trang sản phẩm (`total_pages = 2`)
When: người dùng yêu cầu tham số `page=5` trên URL
Then: hệ thống hiển thị dữ liệu của trang 2 (trang cuối cùng)

### AC-19: Số trang yêu cầu nhỏ hơn 1 hoặc không phải số hợp lệ khi có dữ liệu
Given: danh mục có 2 trang sản phẩm và người dùng truy cập tham số `page=0` hoặc `page=-3` hoặc `page=abc`
When: hệ thống xử lý yêu cầu
Then: hệ thống tự động đưa về trang 1 và hiển thị dữ liệu của trang 1

### AC-20: Có tham số trang nhưng kết quả rỗng (không sinh trang 0)
Given: danh mục không có sản phẩm Đang bán nào (hoặc bộ lọc không khớp sản phẩm nào dẫn đến `total_pages = 0`)
When: người dùng truy cập URL danh mục với tham số `page=2`
Then: hệ thống hiển thị thông báo rỗng tương ứng ("Chưa có sản phẩm trong danh mục này" hoặc "Không có sản phẩm phù hợp")
And: hệ thống không hiển thị thanh phân trang và không sinh trang 0

### AC-21: Giá trị lọc không tồn tại bị bỏ qua
Given: người dùng truy cập URL danh mục với tham số lọc size không tồn tại `size=XXXL` và giới tính hợp lệ `gender=Nu`
When: hệ thống xử lý yêu cầu
Then: tiêu chí `size=XXXL` bị bỏ qua
And: hệ thống hiển thị danh sách sản phẩm lọc theo giới tính "Nữ"

### AC-22: Điều hướng xem chi tiết sản phẩm
Given: người dùng đang xem danh sách sản phẩm của danh mục "Bikini" có hiển thị sản phẩm A
When: người dùng bấm vào thẻ sản phẩm A
Then: hệ thống điều hướng người dùng sang trang chi tiết của sản phẩm A (UC-12)

### AC-23: Phản hồi HTTP Header và Cache dữ liệu theo catalog version
Given: danh mục có sản phẩm Đang bán hợp lệ
When: người dùng truy cập trang danh mục
Then: hệ thống trả về mã trạng thái HTTP 200 kèm các header `Cache-Control: private, no-cache`, `Vary: HX-Request`
And: dữ liệu danh sách sản phẩm được lưu cache tại Redis theo số phiên bản catalog (catalog version) với TTL dự phòng 5 phút

### AC-24: Giá hiển thị trên thẻ và nhãn tồn kho chỉ tính trên biến thể ACTIVE có giá hợp lệ
Given: sản phẩm A ở trạng thái Đang bán có biến thể S (`variant_status = INACTIVE`, giá 100.000đ, tồn kho = 5) và biến thể M (`variant_status = ACTIVE`, giá 200.000đ, tồn kho = 0)
When: người dùng xem danh sách sản phẩm trong danh mục
Then: thẻ sản phẩm A hiển thị giá bán `200.000đ` (loại trừ giá của biến thể S do đã ngừng bán)
And: thẻ sản phẩm A hiển thị nhãn "Hết hàng" (do biến thể ACTIVE duy nhất là M có tồn kho = 0; số lượng tồn kho của biến thể INACTIVE không được tính)

### AC-25: Loại trừ từng sản phẩm Đang bán không có biến thể ACTIVE có giá hợp lệ
Given: danh mục có 13 sản phẩm hợp lệ (đều ở trạng thái `product_status = ACTIVE` và có ít nhất một biến thể `variant_status = ACTIVE` có giá bán > 0; trong đó có sản phẩm hết hàng nhưng vẫn hiển thị nhãn "Hết hàng", không bị ẩn) và 1 sản phẩm B (`product_status = ACTIVE` nhưng tất cả biến thể đều có `variant_status = INACTIVE` hoặc chưa có biến thể ACTIVE nào có giá bán hợp lệ > 0)
When: người dùng xem danh sách sản phẩm trong danh mục
Then: sản phẩm B bị loại trừ (tạm ẩn) hoàn toàn và không chiếm vị trí trong danh sách
And: tổng số sản phẩm hợp lệ hiển thị là 13, chia làm 2 trang
And: trang 1 hiển thị đủ 12 sản phẩm hợp lệ đầu tiên, trang 2 hiển thị đúng 1 sản phẩm hợp lệ còn lại
When: trong một danh mục khác mà tất cả sản phẩm Đang bán đều rơi vào trường hợp không có biến thể ACTIVE có giá hợp lệ như sản phẩm B
Then: toàn bộ sản phẩm trong danh mục đó bị loại trừ, tổng số sản phẩm hiển thị là 0
And: hệ thống hiển thị thông báo "Chưa có sản phẩm trong danh mục này", ẩn thanh phân trang và không sinh trang 0

### AC-26: Phân trang tất định không lặp và không bỏ sót khi có nhiều sản phẩm bằng giá
Given: danh mục có 13 sản phẩm mang mã từ SP-0001 đến SP-0013, tất cả đều ở trạng thái Đang bán, có biến thể `variant_status = ACTIVE` và đều có cùng mức giá thấp nhất thực tế là 300.000đ; dữ liệu sản phẩm cố định không thay đổi giữa các lần yêu cầu
When: người dùng chọn sắp xếp "Giá tăng dần" và xem trang 1
Then: trang 1 hiển thị đúng 12 sản phẩm từ SP-0001 đến SP-0012 theo thứ tự `product_id ASC`
When: người dùng chuyển sang trang 2
Then: trang 2 hiển thị đúng 1 sản phẩm SP-0013
And: không xuất hiện lại bất kỳ sản phẩm nào từ SP-0001 đến SP-0012 của trang 1 và không bỏ sót sản phẩm SP-0013
When: người dùng chuyển sang tiêu chí sắp xếp "Giá giảm dần"
Then: do tất cả sản phẩm bằng giá, hệ thống vẫn áp dụng tiêu chí sắp xếp phụ `product_id ASC` (không đảo chiều `product_id` theo chiều giá)
And: trang 1 vẫn hiển thị đúng 12 sản phẩm từ SP-0001 đến SP-0012 và trang 2 hiển thị SP-0013
And: khi người dùng tải lại trang (reload) ở bất kỳ tiêu chí sắp xếp nào, thứ tự hiển thị tại mỗi trang giữ nguyên nhất quán

### AC-27: Phân trang tất định khi nhiều sản phẩm trùng thời điểm tạo
Given: sản phẩm SP-0001 và SP-0002 đều ở trạng thái Đang bán, có biến thể `variant_status = ACTIVE` với giá bán hợp lệ, và có cùng thời điểm tạo `product_created_at` (08:00:00 UTC ngày 01/11/2026)
When: người dùng mở danh mục với sắp xếp mặc định "Mới nhất"
Then: sản phẩm SP-0001 xuất hiện trước sản phẩm SP-0002 trong danh sách nhờ tie-breaker `product_id ASC`

## Dependencies
- **Upstream UC:**
  - UC-14 Quản lý sản phẩm (cung cấp sản phẩm và trạng thái Đang bán/Ngừng bán).
  - UC-15 Quản lý biến thể màu × size (cung cấp liên kết biến thể theo size và trạng thái biến thể `variant_status`).
  - UC-16 Quản lý giá bán theo size (cung cấp giá bán `variant_sell_price`).
  - UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính (cung cấp danh mục, bộ sưu tập, giới tính, size cho bộ lọc).
  - UC-28 Quản lý khuyến mãi theo sản phẩm (cung cấp chương trình giảm giá đang hiệu lực).
- **Downstream UC:**
  - UC-12 Xem chi tiết sản phẩm (khi người dùng bấm vào thẻ sản phẩm).
- **Internal Services:**
  - Module `promotion`: Service công khai để lấy thông tin khuyến mãi theo sản phẩm đang hiệu lực.
  - Module `inventory`: Service công khai để lấy số lượng tồn kho theo biến thể (`inventory.stock`) nhằm xác định nhãn "Hết hàng".
- **External Systems:**
  - Redis: Cache dữ liệu danh sách sản phẩm theo danh mục và thuộc tính phân loại.

## Notes
- **Ranh giới Modular Monolith (AGENTS.md):** Module `catalog` không truy cập trực tiếp bảng `promotion.product_promotion` hay `inventory.stock`. Mọi dữ liệu khuyến mãi và tồn kho đều thông qua Service công khai của module tương ứng.
- **Tiền tệ & Số học tài chính (AGENTS.md):** Tiền tệ luôn biểu diễn bằng số nguyên VND. Mức giá sau khuyến mãi được tính toán và làm tròn theo phương thức `ROUND_HALF_UP`.
- **Thời gian & Múi giờ (AGENTS.md):** Sắp xếp sản phẩm mới nhất dựa trên `product_created_at` lưu theo chuẩn UTC.
- **Chiến lược Cache (BR-GIAIDOAN1 - Constraints chung, đã chốt 21/11/2026):**
  - Cache dữ liệu danh sách sản phẩm theo danh mục tại Redis với khóa cache chứa *số phiên bản catalog (catalog version)*. TTL dự phòng 5 phút. Khi sản phẩm, khuyến mãi hoặc tồn kho thay đổi thì số phiên bản catalog tăng lên, khóa cũ tự động vô hiệu.
  - Không cache HTML. HTML được render phía server (FastAPI + Jinja + HTMX) cho mỗi request.
  - HTTP Header trả về: `Cache-Control: private, no-cache`, `Vary: HX-Request`, không dùng `ETag`.
- **Out of Scope (BR-GIAIDOAN1):**
  - Mega menu, bộ lọc nâng cao (ngoài 4 tiêu chí: giới tính, size, danh mục, bộ sưu tập).
  - Thêm nhanh sản phẩm vào giỏ hàng trực tiếp từ thẻ sản phẩm.

### Quyết định đã chốt
- Lọc sản phẩm theo 4 tiêu chí: giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- Sắp xếp mặc định theo sản phẩm mới nhất (`product_created_at` giảm dần) (đã chốt 15/11/2026).
- Hỗ trợ 3 tiêu chí sắp xếp: Mới nhất (mặc định), Giá tăng dần, Giá giảm dần. Căn cứ sắp xếp theo giá là mức giá bán thực tế thấp nhất hiển thị (giá sau khuyến mãi nếu có) (đã chốt 22/11/2026, UC-10-Q2).
- Mỗi tiêu chí lọc chọn tối đa 1 giá trị (single-select). Các tiêu chí khác nhau kết hợp theo điều kiện VÀ (AND) (đã chốt 22/11/2026, UC-10-Q4).
- Lọc theo size: hiển thị sản phẩm có ít nhất một biến thể thuộc size đã chọn, không xét còn hàng hay hết hàng (đã chốt 22/11/2026, UC-10-Q3; giữ nguyên quy tắc lọc size độc lập với tồn kho, không phụ thuộc vào trạng thái ACTIVE của biến thể cho bộ lọc size). Riêng đối với điều kiện hiển thị nhãn "Hết hàng" trên thẻ sản phẩm, quy tắc Q9 (chốt 23/11/2026) thay thế tập xét cũ: nhãn "Hết hàng" hiển thị khi tất cả biến thể Đang bán (`variant_status = ACTIVE`) có giá hợp lệ (> 0) của sản phẩm đều có tồn kho bằng 0.
- Thẻ sản phẩm hiển thị ảnh đại diện (`gallery_order_no = 1`), tên, giá thấp nhất theo định dạng `Từ <giá thấp nhất>đ` (hoặc `<giá>đ` nếu các size cùng giá). Nếu có khuyến mãi theo sản phẩm thì hiển thị giá gốc gạch ngang và giá sau giảm `Từ <giá thấp nhất sau giảm>đ` làm tròn số nguyên VND theo `ROUND_HALF_UP` (đã chốt 22/11/2026, UC-10-Q1).
- Phân trang: Mỗi trang cố định 12 sản phẩm (đã chốt 22/11/2026, UC-10-Q7).
- Xử lý số trang: Khi có dữ liệu (`total_pages ≥ 1`), yêu cầu `page > total_pages` thì hiển thị trang cuối cùng (`total_pages`); `page < 1` hoặc không phải số nguyên dương hợp lệ thì hiển thị trang 1. Khi `total_pages = 0` thì hiển thị thông báo rỗng tương ứng, không sinh trang 0 (đã chốt 22/11/2026, UC-10-Q5).
- Chọn danh mục khác trong bộ lọc: điều hướng sang URL danh mục mới, giữ nguyên các tiêu chí lọc còn lại (giới tính, size, bộ sưu tập) và đặt lại `page = 1` (đã chốt 22/11/2026, UC-10-Q6).
- Giá trị lọc không tồn tại: tự động bỏ qua tiêu chí không hợp lệ và hiển thị danh sách theo các tiêu chí hợp lệ còn lại (đã chốt 22/11/2026, UC-10-Q8).
- Tập biến thể tính giá và nhãn tồn kho: Mức giá bán thấp nhất hiển thị trên thẻ (và giá dùng để sắp xếp) chỉ tính trên các biến thể Đang bán (`variant_status = ACTIVE`) có giá bán hợp lệ (> 0) của sản phẩm, bất kể biến thể đó còn hàng hay hết hàng; nhãn "Hết hàng" hiển thị khi tất cả biến thể `variant_status = ACTIVE` có giá hợp lệ (> 0) của sản phẩm đều có tồn kho bằng 0 (đã chốt 23/11/2026, UC-10-Q9).
- Xử lý khi sản phẩm Đang bán không có biến thể ACTIVE có giá hợp lệ: Hệ thống tự động loại trừ (tạm ẩn) từng sản phẩm này khỏi danh sách hiển thị trên storefront trước khi tính tổng số sản phẩm và phân trang, sau đó tiếp tục xử lý các sản phẩm hợp lệ còn lại; nếu cả danh mục không còn sản phẩm hợp lệ nào thì chuyển sang hiển thị thông báo danh mục rỗng (đã chốt 23/11/2026, UC-10-Q10).
- Tiêu chí sắp xếp phụ duy nhất (tie-breaker): Sử dụng `product_id ASC` làm tiêu chí sắp xếp phụ duy nhất cho mọi trường hợp sắp xếp (Mới nhất: `product_created_at DESC, product_id ASC`; Giá tăng dần: `effective_min_price ASC, product_id ASC`; Giá giảm dần: `effective_min_price DESC, product_id ASC`) để đảm bảo phân trang tất định (đã chốt 23/11/2026, UC-10-Q11).

### Giả định [GD]
- Hiện tại không còn giả định hoặc câu hỏi mở nào bị chặn cho UC-10.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): thêm lọc theo giới tính, size, danh mục, bộ sưu tập; chốt sắp xếp mặc định mới nhất; thêm AC lọc
- v3 (2026-11-22): chốt UC-10-Q1 đến UC-10-Q6 (sắp xếp giá tăng/giảm theo giá thực tế sau KM, lọc single-select kết hợp AND, lọc size không xét tồn kho, định dạng hiển thị giá/KM/hết hàng trên thẻ, chuyển danh mục trong bộ lọc); bổ sung ranh giới Service và cache Redis theo catalog version.
- v4 (2026-11-22): rà soát theo phản hồi Coordinator: giữ Status draft và gắn tag [GD] cho 2 mục chưa xác nhận (UC-10-Q7: 12 sản phẩm/trang, UC-10-Q8: bỏ qua tiêu chí lọc không tồn tại); chỉnh khớp mã điểm rẽ Alternative Flows (3a, 4a, 5a, 6a-6e) với các bước Main Flow; làm rõ E2 và thêm AC-20 chống sinh trang 0 khi kết quả rỗng; sửa AC-4 minh chứng rõ sắp xếp theo giá sau khuyến mãi; bổ sung AC-22 (điều hướng UC-12) và AC-23 (HTTP header & cache Redis). Tổng cộng 23 ACs.
- v5 (2026-11-22): developer phê duyệt chốt UC-10-Q7 (12 sản phẩm/trang) và UC-10-Q8 (bỏ qua tiêu chí lọc không tồn tại); gỡ bỏ toàn bộ nhãn [GD]; cập nhật Quyết định đã chốt; chuyển Status sang ready.
- v6 (2026-11-23): tiếp nhận rà soát logic vòng 2 (Phát hiện #2); chuyển Status draft; gắn tag [GD] và bổ sung câu hỏi mở UC-10-Q9 (tập biến thể ACTIVE tính giá và nhãn Hết hàng) và UC-10-Q10 (xử lý sản phẩm không có biến thể ACTIVE có giá); làm rõ bước 7, 4a và thêm Exception E4.
- v7 (2026-11-23): tiếp nhận rà soát logic vòng 3 (Phát hiện #3); bổ sung tiêu chí sắp xếp phụ duy nhất (tie-breaker) `product_id ASC` vào Main Flow 4, Alternative Flow 4a và câu hỏi mở UC-10-Q11 để đảm bảo phân trang tất định (chống lặp/bỏ sót sản phẩm khi bằng giá hoặc bằng ngày tạo).
- v8 (2026-11-23): developer phê duyệt chốt toàn bộ UC-10-Q9, Q10, Q11; hoàn thiện Main Flow 3, 4, 7, Alternative Flow 4a, 6b và Exception E4; bổ sung AC-24 (tập biến thể ACTIVE tính giá và nhãn hết hàng), AC-25 (tạm ẩn sản phẩm không có biến thể ACTIVE có giá), AC-26 (phân trang tất định không lặp/bỏ sót với 13 sản phẩm cùng giá), AC-27 (tie-breaker khi trùng ngày tạo); gỡ bỏ toàn bộ nhãn [GD]; cập nhật Quyết định đã chốt; chuyển Status sang ready (tổng cộng 27 ACs).
- v9 (2026-11-23): tinh chỉnh Main 3 & Exception E4 loại trừ từng sản phẩm không đủ điều kiện trước khi tính tổng/phân trang; hoàn thiện AC-25 (fixture hỗn hợp 13 sp hợp lệ + 1 sp bị ẩn, trường hợp tất cả bị ẩn), AC-26 (kiểm chứng cả Giá tăng dần và Giá giảm dần đều giữ tie-breaker product_id ASC, reload nhất quán), cập nhật Given AC-1/2/26/27 đầy đủ điều kiện hợp lệ mới; cập nhật Notes/Quyết định Q3 dẫn chiếu rõ quy tắc Q9 thay thế tập xét nhãn Hết hàng trong khi vẫn bảo lưu quy tắc lọc size không xét tồn.
