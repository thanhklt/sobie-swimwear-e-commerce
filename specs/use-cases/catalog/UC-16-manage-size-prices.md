# UC-16: Quản lý giá bán theo size

## Metadata
- **ID:** UC-16
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Giá bán của một sản phẩm trong portal quản trị.

## Preconditions
- Nhân viên đã đăng nhập vào portal quản trị (UC-02).
- Sản phẩm đã tồn tại (UC-14).
- Sản phẩm đã có ít nhất một biến thể (UC-15).

## Main Flow
1. Hệ thống hiển thị danh sách tất cả các size hiện có của sản phẩm và giá bán hiện tại tương ứng của từng size (dưới dạng số nguyên VND).
2. Nhân viên nhập hoặc chỉnh sửa giá bán cho các size trên form, sau đó bấm "Lưu bảng giá".
3. Hệ thống kiểm tra dữ liệu giá của tất cả các size được sửa: mỗi giá bán phải là số nguyên VND lớn hơn 0 và không vượt giới hạn lưu trữ kiểu `numeric(12,0)` (< 10^12 VND); không cho phép để trống nếu size đó đã có giá trước đó.
4. Trong cùng một Database Transaction, hệ thống thực hiện khóa bi quan dòng sản phẩm cha: `SELECT product_key FROM catalog.product WHERE product_key = :product_key FOR UPDATE;` trước khi đọc trạng thái hoặc cập nhật giá để chống tương tranh với UC-14 và UC-15. Sau đó, hệ thống cập nhật `variant_sell_price` cho tất cả các biến thể có cùng `variant_product_key` và `variant_size_key` tương ứng với giá mới đã nhập, và giữ khóa này cho đến khi commit/rollback transaction. Nếu xảy ra lỗi ghi dữ liệu giữa chừng thì rollback toàn bộ transaction (E4).
5. Sau khi commit Database Transaction thành công, hệ thống tăng số phiên bản catalog để hủy cache (invalidation) tại Redis (theo quy tắc cache BR-002 / Constraints chung). Nếu làm mới Redis thành công, giá mới hiển thị ngay lập tức trên storefront và giỏ hàng; nếu Redis gặp lỗi kết nối hoặc timeout thì chuyển sang nhánh E5. Hệ thống thông báo cập nhật giá thành công.

## Alternative Flows
- **1a. Size chưa có giá:** Tại bước 1, nếu một size chưa được đặt giá (`variant_sell_price` là `NULL`), hệ thống hiển thị trạng thái "Chưa có giá"; Nhân viên có thể nhập giá mới cho size này ở bước 2 hoặc để trống (khi để trống thì bỏ qua không cập nhật size đó, size đó tiếp tục giữ `NULL`). Sản phẩm chưa thể chuyển trạng thái "Đang bán" nếu còn ít nhất một size chưa có giá (UC-14, E3).
- **2a. Đổi giá sản phẩm đang bán (ACTIVE):** Nhân viên thực hiện sửa giá khi sản phẩm đang ở trạng thái "Đang bán". Sau khi lưu database thành công ở bước 4, sản phẩm vẫn giữ nguyên trạng thái "Đang bán". Nếu Redis làm mới thành công ở bước 5, giá mới hiển thị ngay trên storefront; nếu Redis gặp lỗi (E5), storefront có thể hiển thị giá cũ trong tối đa 5 phút (TTL dự phòng). Giỏ hàng và đặt hàng luôn đọc giá mới từ Database.
- **2b. Nhân viên hủy thao tác:** Tại bước 2, Nhân viên không bấm lưu mà chuyển sang trang khác hoặc tải lại trang; hệ thống không bắt đầu ghi dữ liệu và giữ nguyên giá cũ.

## Exceptions
- **E1. Giá không hợp lệ:** Tại bước 3, nếu có bất kỳ size nào nhập giá ≤ 0, không phải số nguyên (số thập phân, chuỗi ký tự), vượt ngưỡng lưu trữ `numeric(12,0)` (≥ 1.000.000.000.000đ), hoặc xóa trắng ô giá của một size đã có giá trước đó: hệ thống từ chối lưu, không bắt đầu ghi dữ liệu vào database, và báo lỗi cụ thể tại size tương ứng ("Giá bán phải là số nguyên lớn hơn 0", "Giá vượt giới hạn cho phép", hoặc "Giá bán không được để trống").
- **E2. Sản phẩm chưa có biến thể:** Tại bước 1, nếu sản phẩm chưa có bất kỳ biến thể nào (chưa tạo ở UC-15): hệ thống hiển thị thông báo "Sản phẩm chưa có biến thể, vui lòng tạo biến thể trước khi đặt giá" và không hiển thị bảng nhập giá.
- **E3. Sai phân quyền (RBAC):** Người dùng không có vai trò Nhân viên (Khách hàng hoặc Admin) cố gắng truy cập màn hình hoặc API đặt giá: hệ thống từ chối truy cập và trả về mã lỗi 403 Forbidden.
- **E4. Lỗi hệ thống khi ghi database:** Tại bước 4, nếu xảy ra lỗi ghi database giữa chừng đối với bất kỳ biến thể nào: hệ thống rollback toàn bộ Database Transaction, không có giá nào được cập nhật dở dang (all-or-nothing), và hiển thị thông báo lỗi hệ thống.
- **E5. Lỗi làm mới cache Redis sau commit DB:** Tại bước 5, nếu Redis bị lỗi kết nối hoặc timeout khi tăng số phiên bản catalog: hệ thống ghi log cảnh báo, không rollback Database Transaction đã commit, và vẫn thông báo cập nhật giá thành công cho Nhân viên. Storefront có thể hiển thị giá cũ trong tối đa 5 phút (hết TTL dự phòng của cache) hoặc cho đến lần cập nhật catalog tiếp theo tăng version thành công. Các thao tác giỏ hàng (UC-18) và đặt hàng (UC-19) luôn đọc giá hiện hành trực tiếp từ Database (source of truth), bảo đảm không phát sinh đơn hàng theo giá cache cũ.

## Postconditions
- Các size được nhập hoặc sửa giá hợp lệ được cập nhật đồng bộ `variant_sell_price` (số nguyên VND > 0) cho mọi biến thể cùng size.
- Các size chưa có giá mà được để trống tiếp tục giữ giá trị `NULL` ("Chưa có giá"); sản phẩm chưa đủ điều kiện chuyển trạng thái "Đang bán" (UC-14).
- Mọi biến thể cùng sản phẩm và cùng size (mọi màu của size đó) luôn có cùng `variant_sell_price`; bất biến được bảo đảm trong môi trường tương tranh thông qua khóa `catalog.product FOR UPDATE`.
- Cache catalog tại Redis: được làm mới ngay khi Redis hoạt động bình thường; nếu Redis lỗi sau commit DB, DB vẫn giữ giá mới, ghi log cảnh báo và cache cũ tự hết hạn sau tối đa 5 phút (TTL).
- Đơn hàng đã tạo trước đó không bị thay đổi đơn giá (đơn giá lịch sử được bảo toàn trong `ordering.order_detail`).

## Acceptance Criteria

### AC-1: Đặt giá theo size cho sản phẩm mới
Given: sản phẩm A đang ở trạng thái Ngừng bán (mới tạo từ UC-14), có size S và M chưa có giá bán (hiển thị "Chưa có giá")
When: Nhân viên nhập giá S = 300.000đ, M = 320.000đ và bấm "Lưu bảng giá"
Then: hệ thống lưu thành công trong database
And: màn hình quản lý giá hiển thị size S giá 300.000đ và size M giá 320.000đ
And: sản phẩm A vẫn ở trạng thái Ngừng bán (chưa hiển thị công khai trên storefront cho đến khi chuyển Đang bán ở UC-14)

### AC-2: Mọi màu cùng size dùng chung giá bán
Given: sản phẩm A có biến thể Đỏ×M và Xanh×M, giá size M = 320.000đ
When: người dùng chọn Đỏ×M rồi Xanh×M trên trang chi tiết
Then: cả hai đều hiển thị 320.000đ

### AC-3: Đặt giá ghi đồng bộ cho mọi biến thể cùng size trong transaction
Given: sản phẩm A có biến thể Đỏ×M, Xanh×M và Đỏ×L
When: Nhân viên đặt giá size M = 320.000đ và bấm "Lưu bảng giá"
Then: biến thể Đỏ×M và Xanh×M đều có `variant_sell_price` là 320.000đ trong cùng một transaction
And: giá của biến thể Đỏ×L không đổi

### AC-4: Giá không hợp lệ (nhỏ hơn hoặc bằng 0, số thập phân, chuỗi ký tự, vượt giới hạn lưu trữ)
Given: Nhân viên đang sửa giá sản phẩm A
When: Nhân viên nhập giá size S là giá trị không hợp lệ (lần lượt: 0, số âm -50.000đ, số thập phân 300000.5, chuỗi "abc", hoặc số ≥ 1.000.000.000.000đ) và bấm "Lưu bảng giá"
Then: hệ thống từ chối lưu, không tự ý làm tròn hay cắt bớt số thập phân
And: báo lỗi "Giá bán phải là số nguyên lớn hơn 0" (hoặc "Giá vượt giới hạn cho phép") tại ô size S
And: dữ liệu trong database không thay đổi

### AC-5: Chặn xóa trắng giá của size đã có giá
Given: sản phẩm A có size S đang có giá 300.000đ
When: Nhân viên xóa trắng ô giá size S và bấm "Lưu bảng giá"
Then: hệ thống từ chối lưu và báo "Giá bán không được để trống"
And: giá size S trong database vẫn giữ nguyên 300.000đ

### AC-6: Đổi giá sản phẩm đang bán (ACTIVE) khi Redis hoạt động bình thường
Given: sản phẩm A đang ở trạng thái "Đang bán" (ACTIVE) có size S giá 300.000đ
When: Nhân viên đổi giá size S thành 330.000đ và lưu thành công
Then: sản phẩm A vẫn giữ nguyên trạng thái "Đang bán"
And: cache catalog tại Redis được làm mới ngay (tăng phiên bản catalog)
And: khách hàng xem trang chi tiết sản phẩm thấy giá size S hiển thị ngay là 330.000đ

### AC-7: Đổi giá không ảnh hưởng đơn đã tạo
Given: đơn hàng X đã đặt sản phẩm A size M với giá 320.000đ
When: Nhân viên đổi giá size M thành 350.000đ
Then: đơn hàng X vẫn giữ giá 320.000đ
And: đơn mới đặt sau đó dùng giá 350.000đ

### AC-8: Đổi giá cập nhật giá hiển thị trong giỏ hàng
Given: khách hàng có biến thể Đỏ×M của sản phẩm A trong giỏ hàng lúc giá đang là 320.000đ
When: Nhân viên đổi giá size M thành 350.000đ
Then: khi khách hàng mở trang giỏ hàng (UC-18), đơn giá của dòng Đỏ×M hiển thị là 350.000đ và tạm tính giỏ hàng được tính lại theo đơn giá mới

### AC-9: Phân quyền truy cập (RBAC)
Given: người dùng đăng nhập với vai trò Khách hàng hoặc Admin
When: người dùng cố gắng truy cập màn hình hoặc API đặt giá của sản phẩm
Then: hệ thống từ chối truy cập và trả về mã lỗi 403 Forbidden

### AC-10: Sản phẩm chưa có biến thể không thể đặt giá
Given: sản phẩm B vừa tạo (UC-14) và chưa có bất kỳ biến thể nào ở UC-15
When: Nhân viên mở mục Giá bán của sản phẩm B
Then: hệ thống hiển thị thông báo "Sản phẩm chưa có biến thể, vui lòng tạo biến thể trước khi đặt giá" và không cho phép nhập giá

### AC-11: Lưu một size có giá và giữ nguyên size chưa định giá
Given: sản phẩm A mới tạo có size S và size M, cả 2 size đều chưa có giá ("Chưa có giá")
When: Nhân viên chỉ nhập giá cho size S = 300.000đ và để trống ô giá size M, rồi bấm "Lưu bảng giá"
Then: hệ thống lưu thành công
And: mọi biến thể size S của sản phẩm A có `variant_sell_price` = 300.000đ
And: mọi biến thể size M của sản phẩm A tiếp tục có `variant_sell_price` là NULL (hiển thị "Chưa có giá")
And: sản phẩm A vẫn ở trạng thái Ngừng bán và chưa thể chuyển Đang bán

### AC-12: Lưu theo lô all-or-nothing khi có một size bị lỗi validation
Given: sản phẩm A có size S đang có giá 300.000đ và size M đang có giá 320.000đ
When: Nhân viên sửa giá size S = 350.000đ (hợp lệ) và size M = -50.000đ (không hợp lệ) rồi bấm "Lưu bảng giá"
Then: hệ thống từ chối lưu toàn bộ, không bắt đầu ghi database
And: báo lỗi tại ô size M
And: giá size S trong database vẫn giữ nguyên 300.000đ và size M vẫn giữ nguyên 320.000đ

### AC-13: Rollback toàn bộ khi lỗi ghi database giữa chừng
Given: Nhân viên nhập bảng giá hợp lệ cho các size S và M của sản phẩm A
When: hệ thống đang ghi dữ liệu ở bước 4 thì xảy ra lỗi database giữa chừng
Then: hệ thống rollback toàn bộ Database Transaction
And: không có biến thể nào của size S hoặc size M bị cập nhật giá dở dang

### AC-14: Hủy thao tác giữ nguyên giá cũ
Given: sản phẩm A có size S đang có giá 300.000đ
When: Nhân viên nhập đổi giá size S thành 400.000đ nhưng không bấm lưu mà chuyển sang trang khác hoặc tải lại trang
Then: hệ thống không lưu giá mới
And: khi mở lại màn hình giá bán, giá size S vẫn giữ nguyên 300.000đ

### AC-15: Đổi giá thành công nhưng lỗi làm mới cache Redis (E5)
Given: sản phẩm A đang "Đang bán" có size S giá 300.000đ
When: Nhân viên sửa giá size S thành 350.000đ, DB commit thành công nhưng Redis gặp sự cố (timeout hoặc mất kết nối)
Then: hệ thống ghi log cảnh báo và vẫn thông báo cập nhật thành công cho Nhân viên
And: dữ liệu trong database giữ đúng giá mới 350.000đ, không bị rollback
And: trên storefront, trang chi tiết có thể tiếp tục hiển thị giá cũ 300.000đ cho đến khi hết TTL 5 phút hoặc lần tăng version catalog kế tiếp
And: khi khách hàng thêm vào giỏ hoặc đặt hàng, hệ thống đọc giá từ database là 350.000đ, không cho phép đặt hàng theo giá cũ 300.000đ

### AC-16: Kiểm soát tương tranh khi đổi giá và tạo biến thể mới diễn ra đồng thời (Shared Parent Product Lock)
Given: sản phẩm A đang có size M giá 320.000đ (đang có biến thể Đỏ×M); Nhân viên 1 thực hiện đổi giá size M thành 350.000đ (UC-16), đồng thời Nhân viên 2 thực hiện tạo biến thể Xanh×M (UC-15). Cả hai thao tác đều chạy trong Database Transaction riêng và dùng chung giao thức khóa dòng sản phẩm cha `SELECT product_key FROM catalog.product WHERE product_key = :product_key FOR UPDATE;` ngay đầu transaction trước khi đọc/ghi
When: cả hai thao tác được gửi lên hệ thống và thực thi đồng thời theo thứ tự cấp khóa của từng kịch bản:
- **Kịch bản A (UC-16 được cấp khóa trước):**
  1. Transaction UC-16 lấy khóa `FOR UPDATE` trên sản phẩm A trước.
  2. Transaction UC-15 yêu cầu khóa `FOR UPDATE` trên sản phẩm A và bị chặn chờ (waiting).
  3. UC-16 cập nhật `variant_sell_price` của size M thành 350.000đ (Đỏ×M thành 350.000đ) và commit transaction (giải phóng khóa).
  4. UC-15 được cấp khóa, đọc giá hiện hành của size M từ database thấy 350.000đ.
  5. UC-15 chèn biến thể Xanh×M với giá 350.000đ và commit transaction.
- **Kịch bản B (UC-15 được cấp khóa trước):**
  1. Transaction UC-15 lấy khóa `FOR UPDATE` trên sản phẩm A trước.
  2. Transaction UC-16 yêu cầu khóa `FOR UPDATE` trên sản phẩm A và bị chặn chờ (waiting).
  3. UC-15 đọc giá hiện tại của size M (320.000đ), chèn biến thể Xanh×M với giá 320.000đ và commit transaction (giải phóng khóa). Lúc này sản phẩm A có 2 biến thể Đỏ×M và Xanh×M đều giá 320.000đ.
  4. UC-16 nhận được khóa, thực hiện cập nhật toàn bộ biến thể cùng size M của sản phẩm A (bao gồm cả Đỏ×M và Xanh×M vừa tạo) lên giá mới 350.000đ và commit transaction.
Then: trong cả hai kịch bản, cả hai biến thể Đỏ×M và Xanh×M đều có giá bán thống nhất là 350.000đ; không bị lệch giá giữa các màu
And: bất biến "mọi màu cùng size dùng chung một giá" luôn được bảo toàn tuyệt đối
And: PostgreSQL commit thành công trước rồi mới tăng catalog_version ở Redis (Redis không nằm trong transaction SQL, nếu Redis gặp lỗi sau commit thì xử lý theo nhánh E5 như đã chốt)

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập (xác thực và phân quyền Nhân viên), UC-14 Quản lý sản phẩm, UC-15 Quản lý biến thể màu × size
- **Downstream UC:**
  - UC-10 Xem sản phẩm theo danh mục (hiển thị giá thấp nhất theo size)
  - UC-12 Xem chi tiết sản phẩm (hiển thị giá theo size đã chọn)
  - UC-14 Quản lý sản phẩm (điều kiện chuyển Đang bán là mọi size phải có giá)
  - UC-18 Quản lý giỏ hàng (hiển thị đơn giá hiện hành của biến thể)
  - UC-19, UC-20 Đặt hàng COD / Chuyển khoản QR (snapshot đơn giá vào `order_detail_unit_price`)
  - UC-28 Quản lý khuyến mãi theo sản phẩm (tính % giảm trực tiếp trên giá bán của size)
- **External Systems:** Redis (lưu cache catalog và số phiên bản catalog)

## Notes
- Tiền tệ luôn biểu diễn bằng số nguyên VND, ánh xạ kiểu `Decimal` trong backend và `numeric(12,0)` trong database, làm tròn `ROUND_HALF_UP` (AGENTS.md, BR-GIAIDOAN1).
- Thời gian lưu trữ UTC (`timestamptz`).
- Thao tác cập nhật giá cho các biến thể cùng size phải thực thi trong cùng một Database Transaction và bắt buộc khóa dòng sản phẩm cha (`SELECT product_key FROM catalog.product WHERE product_key = :product_key FOR UPDATE;`) trước khi đọc trạng thái hoặc ghi dữ liệu để bảo đảm toàn vẹn dữ liệu và kiểm soát tương tranh với UC-14, UC-15 (quyết định UC-14-Q8 và phê duyệt liên UC ngày 23/11/2026 tại Codex).
- Sau khi commit transaction DB thành công, hệ thống thực hiện làm mới cache catalog ở Redis (tăng số phiên bản catalog theo *Constraints chung - Cache*). Nếu Redis gặp sự cố kết nối hoặc timeout sau commit DB: hệ thống ghi log cảnh báo và không rollback DB; storefront có thể hiển thị giá cũ tối đa 5 phút (TTL dự phòng); giỏ hàng và thanh toán đọc trực tiếp từ DB nên luôn áp dụng giá mới (đã chốt theo quyết định UC-17-Q6, developer duyệt 22/11/2026 tại session Codex).

### Quyết định đã chốt
- Giá bán theo size; mọi màu cùng size dùng chung một giá (đã chốt 15/11/2026).
- Giữ `variant_sell_price` ở biến thể theo ERD: khi Nhân viên đặt giá cho một size, hệ thống ghi cùng giá cho mọi biến thể cùng sản phẩm và cùng size (đã chốt 15/11/2026, theo data model v1 — ưu tiên ERD). Không còn lệch ERD.
- Đổi giá không ảnh hưởng đơn hàng đã tạo; đơn hàng lưu snapshot `order_detail_unit_price` tại thời điểm đặt (đã chốt 22/11/2026, Q1).
- Không lưu lịch sử giá; chỉ lưu giá bán hiện hành tại cột `catalog.variant.variant_sell_price` (đã chốt 22/11/2026, Q1).
- Cho phép đổi giá khi sản phẩm đang ở trạng thái Đang bán (ACTIVE); sau khi đổi giá, sản phẩm vẫn giữ trạng thái Đang bán; khi Redis hoạt động bình thường, storefront hiển thị giá mới ngay lập tức; nếu Redis lỗi sau commit DB thì DB giữ giá mới, ghi log cảnh báo và không rollback DB, storefront hiển thị giá mới sau tối đa 5 phút (TTL), giỏ hàng/thanh toán đọc trực tiếp từ DB luôn dùng giá mới (đã chốt 22/11/2026, Q2 và quyết định UC-17-Q6 được developer duyệt 22/11/2026 tại session Codex).
- Khi tạo thêm biến thể mới ở UC-15 cho size đã có giá, biến thể mới tự động nhận giá của size đó; tại UC-16 lệnh lưu giá luôn cập nhật đồng bộ toàn bộ biến thể cùng sản phẩm và size (đã chốt 22/11/2026, Q3).
- Lưu giá theo lô (toàn bộ các size được nhập/sửa trên form) trong một transaction; giá nhập bắt buộc là số nguyên VND > 0; không cho phép xóa trắng giá về NULL đối với size đã có giá (đã chốt 22/11/2026, Q4).
- Phân quyền: Chỉ tài khoản vai trò Nhân viên (`employee`) mới có quyền truy cập và chỉnh sửa giá bán; Admin và Khách hàng bị từ chối truy cập (đã chốt 22/11/2026, Q5).
- Kiểm soát tương tranh liên UC: Áp dụng giao thức dùng chung khóa dòng sản phẩm cha `SELECT product_key FROM catalog.product WHERE product_key = :product_key FOR UPDATE;` trong cùng PostgreSQL transaction giữa UC-14 (quản lý sản phẩm / chuyển trạng thái), UC-15 (tạo / xóa biến thể) và UC-16 (quản lý giá bán theo size) trước khi đọc trạng thái/giá hoặc cập nhật biến thể, giữ khóa đến khi commit/rollback; loại trừ hoàn toàn race condition làm lệch giá giữa các màu cùng size khi tạo biến thể và đổi giá đồng thời (đã chốt theo UC-14-Q8 và phê duyệt liên UC ngày 23/11/2026 tại session Codex).

### Giả định [GD]
- Không còn giả định mở.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt giá theo size, mọi màu cùng size chung giá; ghi chú lệch ERD (`variant_sell_price`)
- v3 (2026-11-15): theo data model v1 — giữ `variant_sell_price`, đặt giá theo size ghi cho mọi biến thể cùng size; thêm AC-3
- v4 (2026-11-22): chốt toàn bộ các giả định [GD] thành quyết định chính thức; hoàn thiện Main Flow (bước 1-5 kèm cập nhật cache Redis), Alternative Flows (1a size chưa có giá, 2a đổi giá sản phẩm đang bán, 2b hủy thao tác), Exceptions (E1 giá không hợp lệ/chặn xóa về NULL, E2 chưa có biến thể, E3 phân quyền RBAC); hoàn thiện AC-1 đến AC-10.
- v5 (2026-11-22): điều chỉnh hậu điều kiện cho phép size chưa định giá giữ NULL; sửa AC-1 kiểm tra ở màn hình quản trị (không gọi storefront cho sản phẩm mới); bổ sung E4, AC-11 (lưu lẻ một size, giữ NULL size còn lại), AC-12 (all-or-nothing validation theo lô), AC-13 (rollback transaction khi lỗi DB), AC-14 (hủy thao tác giữ nguyên giá); cập nhật AC-4 kiểm tra số thập phân, chuỗi và giới hạn numeric(12,0); sửa External Systems thành Redis và ghi chú xử lý lỗi Redis sau commit.
- v6 (2026-11-22): áp dụng quyết định UC-17-Q6 đã được developer phê duyệt tại session Codex (22/11/2026): cập nhật Main Flow bước 5, Alternative 2a, Postconditions; bổ sung Exception E5 và AC-15 xử lý lỗi Redis sau commit DB (không rollback DB, log cảnh báo, storefront tối đa 5 phút TTL, giỏ hàng/thanh toán luôn đọc giá mới từ DB); cập nhật AC-6; chuyển Status sang ready.
- v7 (2026-11-23): mở lại rà soát logic vòng 2 (phát hiện #3 về tương tranh giữa UC-15 và UC-16); chuyển Status về draft; đưa giả định [GD-01] về giao thức khóa bi quan dòng sản phẩm cha vào danh sách câu hỏi mở UC-16-Q6.
- v8 (2026-11-23): áp dụng quyết định UC-14-Q8 và phê duyệt phạm vi liên UC của Developer tại session Codex (23/11/2026): bổ sung khóa bi quan catalog.product FOR UPDATE vào Main Flow bước 4 và Notes; hoàn thiện Postconditions; bổ sung AC-16 kiểm chứng tương tranh cho cả 2 thứ tự xen kẽ với UC-15; giải quyết hoàn toàn GD-01 / UC-16-Q6; chuyển Status sang ready.
