# UC-18: Quản lý giỏ hàng

## Metadata
- **ID:** UC-18
- **Module:** shopping
- **Liên quan tới BR:** BR-003
- **Status:** draft

## Actor
Khách vãng lai, Khách hàng

## Trigger
Khách bấm "Thêm vào giỏ" trên trang chi tiết sản phẩm, hoặc mở trang giỏ hàng.

## Preconditions
- Biến thể (màu × size) đang được bán và còn hàng.

## Main Flow
1. Khách chọn màu, size, số lượng trên trang chi tiết sản phẩm và bấm "Thêm vào giỏ".
2. Hệ thống gọi Service công khai của `catalog` để kiểm tra từ Database đồng thời sản phẩm cha có `product_status = ACTIVE` và biến thể có `variant_status = ACTIVE`, rồi gọi Service công khai của `inventory` để lấy tồn kho khả dụng hiện hành; không dùng trạng thái/tồn kho từ cache storefront làm căn cứ. Nếu sản phẩm hoặc biến thể không còn được bán thì áp dụng E4; nếu số lượng mới (kể cả cộng dồn với dòng đã có) vượt tồn kho thì áp dụng E1. Chỉ khi hợp lệ mới thêm hoặc cập nhật dòng vào giỏ.
3. Khách mở trang giỏ hàng.
4. Hệ thống hiển thị từng dòng: ảnh, tên sản phẩm, màu, size, đơn giá hiện tại (đã áp khuyến mãi theo sản phẩm), số lượng, thành tiền và tạm tính của giỏ.
5. Khách đổi số lượng hoặc xóa dòng; hệ thống cập nhật lại thành tiền và tạm tính.

## Alternative Flows
- **2a. Khách vãng lai:** giỏ hàng lưu ở `localStorage` của trình duyệt; khách vẫn thêm, sửa, xóa được như Khách hàng. Khi thêm giỏ, trình duyệt phải nhận kết quả kiểm tra từ server theo bước 2 trước khi ghi thay đổi vào `localStorage`; dữ liệu cũ trong trình duyệt không thay thế kiểm tra trạng thái/tồn kho hiện hành.
- **2b. Khách vãng lai đăng nhập:** giỏ trong `localStorage` được gộp vào giỏ của tài khoản; dòng trùng biến thể thì cộng dồn nhưng không vượt tồn kho `[GD]`.
- **4a. Giá hoặc khuyến mãi đã thay đổi:** giỏ luôn hiển thị giá hiện tại, không giữ giá lúc thêm vào giỏ `[GD]`.

## Exceptions
- **E1. Vượt tồn kho:** số lượng thêm hoặc sửa lớn hơn tồn kho của biến thể → hệ thống không cập nhật, báo "Chỉ còn N sản phẩm".
- **E2. Biến thể hết hàng hoặc ngừng bán:** dòng trong giỏ được đánh dấu "Hết hàng/Ngừng bán", không tính vào tạm tính và không đặt hàng được cho tới khi khách xóa `[GD]`.
- **E3. Số lượng không hợp lệ:** số lượng ≤ 0 hoặc không phải số nguyên → hệ thống từ chối.
- **E4. Sản phẩm hoặc biến thể không còn được bán khi thêm giỏ:** tại bước 2, Database cho biết sản phẩm cha đã `INACTIVE`, biến thể đã `INACTIVE`, hoặc sản phẩm/biến thể không còn tồn tại dù giao diện cũ vẫn cho bấm thêm → hệ thống từ chối thêm, báo rõ dòng không còn được bán và giữ nguyên giỏ hiện tại (cả DB lẫn `localStorage`); không giữ chỗ hay trừ tồn kho.

## Postconditions
- Giỏ hàng chứa đúng các biến thể và số lượng khách đã chọn, không dòng nào vượt tồn kho.
- Với Khách hàng đã đăng nhập, giỏ được lưu trong DB; mỗi biến thể chỉ có 1 dòng trong giỏ.

## Acceptance Criteria

### AC-1: Thêm biến thể còn hàng vào giỏ
Given: biến thể "Đỏ / M" còn 5 sản phẩm, giỏ đang trống
When: khách thêm 2 sản phẩm "Đỏ / M" vào giỏ
Then: giỏ có 1 dòng "Đỏ / M" số lượng 2
And: tạm tính = 2 × đơn giá hiện tại

### AC-2: Thêm biến thể đã có trong giỏ
Given: giỏ có "Đỏ / M" số lượng 2, tồn kho 5
When: khách thêm tiếp 1 sản phẩm "Đỏ / M"
Then: giỏ vẫn có 1 dòng "Đỏ / M" với số lượng 3

### AC-3: Vượt tồn kho
Given: biến thể "Đỏ / M" còn 3 sản phẩm, giỏ có "Đỏ / M" số lượng 2
When: khách đổi số lượng thành 4
Then: hệ thống từ chối và báo "Chỉ còn 3 sản phẩm"
And: số lượng trong giỏ vẫn là 2

### AC-4: Xóa dòng
Given: giỏ có 2 dòng
When: khách xóa 1 dòng
Then: giỏ còn 1 dòng và tạm tính được tính lại

### AC-5: Khách vãng lai dùng giỏ
Given: khách chưa đăng nhập
When: khách thêm 1 sản phẩm vào giỏ rồi tải lại trang
Then: giỏ vẫn còn sản phẩm đó

### AC-6: Gộp giỏ khi đăng nhập
Given: khách vãng lai có "Đỏ / M" số lượng 2 trong giỏ trình duyệt; giỏ tài khoản có "Đỏ / M" số lượng 2; tồn kho 3
When: khách đăng nhập
Then: giỏ tài khoản có "Đỏ / M" số lượng 3 (không vượt tồn kho)
And: giỏ trên trình duyệt được làm trống

### AC-7: Biến thể hết hàng trong giỏ
Given: giỏ có "Xanh / S", tồn kho của biến thể này về 0
When: khách mở giỏ hàng
Then: dòng "Xanh / S" hiển thị "Hết hàng" và không tính vào tạm tính

### AC-8: Giỏ của Khách hàng lưu trên tài khoản
Given: Khách hàng đã đăng nhập thêm "Đỏ / M" số lượng 1 vào giỏ trên máy A
When: Khách hàng đăng nhập trên máy B và mở giỏ hàng
Then: giỏ có dòng "Đỏ / M" số lượng 1

### AC-9: Chặn thêm biến thể ngừng bán từ giao diện cũ
Given: trang chi tiết đang hiển thị dữ liệu cũ cho biến thể "Đỏ / M" còn hàng; Nhân viên đã chuyển biến thể này sang INACTIVE và DB đã commit, nhưng tăng catalog_version thất bại nên cache cũ chưa hết TTL
When: Khách hàng đã đăng nhập hoặc Khách vãng lai bấm thêm biến thể "Đỏ / M" từ trang cũ
Then: server đọc trạng thái hiện hành qua Service công khai của catalog và từ chối thêm theo E4
And: giỏ trong DB hoặc localStorage giữ nguyên, tồn kho không bị trừ, khách nhận thông báo biến thể không còn được bán

### AC-10: Kiểm tra tồn kho hiện hành khi thêm từ giao diện cũ
Given: biến thể "Đỏ / M" vẫn ACTIVE, cache storefront hiển thị tồn kho 5 nhưng Database hiện chỉ còn 1; giỏ đang trống
When: Khách hàng đã đăng nhập hoặc Khách vãng lai yêu cầu thêm 2 sản phẩm "Đỏ / M"
Then: hệ thống lấy tồn kho hiện hành qua Service công khai của inventory và từ chối theo E1 với thông báo "Chỉ còn 1 sản phẩm"
And: giỏ trong DB hoặc localStorage giữ nguyên và tồn kho không bị trừ

### AC-11: Chặn thêm giỏ khi sản phẩm cha ngừng bán nhưng biến thể vẫn ACTIVE
Given: trang chi tiết cũ vẫn hiển thị "Đỏ / M" còn hàng; sản phẩm cha đã được chuyển sang INACTIVE tại UC-14 và DB đã commit, trong khi biến thể vẫn ACTIVE với tồn kho 5
When: Khách hàng đã đăng nhập hoặc Khách vãng lai yêu cầu thêm 1 sản phẩm "Đỏ / M"
Then: Service catalog đọc trạng thái hiện hành của cả sản phẩm và biến thể; hệ thống từ chối thêm theo E4 do sản phẩm cha INACTIVE
And: giỏ trong DB hoặc localStorage giữ nguyên, tồn kho vẫn là 5 và khách nhận thông báo dòng không còn được bán

## Dependencies
- **Upstream UC:** UC-01 Đăng ký tài khoản, UC-06 Tạo tài khoản, UC-12 Xem chi tiết sản phẩm, UC-15 Quản lý biến thể màu × size, UC-16 Quản lý giá bán theo size, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR
- **Internal Services:** `catalog` kiểm tra trạng thái sản phẩm cha và biến thể từ DB; `inventory` cung cấp tồn kho khả dụng hiện hành. Module shopping không truy cập trực tiếp Repository hoặc bảng của hai module này.
- **External Systems:** Không có

## Notes
- BR-GIAIDOAN1: khách chưa đăng nhập vẫn dùng được giỏ hàng, nhưng phải đăng nhập mới đặt hàng được.
- Thêm vào giỏ không giữ chỗ tồn kho; tồn kho chỉ bị trừ khi tạo đơn.
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung).
- Giao diện cũ, cache Redis và localStorage không xác nhận biến thể còn bán/còn hàng; bước thêm giỏ luôn kiểm tra lại ở server qua Service công khai. Kiểm tra này không giữ chỗ tồn kho và không thay thế kiểm tra trong transaction tạo đơn ở UC-19/20.

### Quyết định đã chốt
- Kiểm tra đồng thời sản phẩm cha ACTIVE, biến thể ACTIVE và tồn kho hiện hành từ DB qua Service công khai trước khi thêm giỏ; dữ liệu storefront cũ không cho phép bỏ qua kiểm tra, kể cả giỏ khách vãng lai (UC-15-Q7; bổ sung điều kiện sản phẩm cha theo yêu cầu xử lý rà soát vòng 3 tại Codex 23/11/2026).
- Giỏ của Khách hàng đã đăng nhập lưu trong DB; mỗi Khách hàng có 1 giỏ, mỗi biến thể chỉ có 1 dòng trong giỏ (theo ERD).
- Giỏ của khách vãng lai lưu ở `localStorage` của trình duyệt (đã chốt 20/11/2026, data model v2, Q23d).
- Giỏ không lưu giá; luôn hiển thị giá hiện tại, không giữ giá lúc thêm (đã chốt 20/11/2026, data model v2, Q26).
- Mỗi Khách hàng có đúng 1 giỏ trong DB, tạo cùng lúc tạo tài khoản Khách hàng (UC-01, UC-06). Trang giỏ luôn có giỏ để đọc / ghi, không tạo giỏ khi thêm sản phẩm lần đầu (đã chốt 21/11/2026, Q39).

### Giả định [GD]
- Khi đăng nhập, giỏ trong `localStorage` gộp vào giỏ tài khoản; dòng trùng cộng dồn nhưng không vượt tồn kho.
- Dòng hết hàng/ngừng bán vẫn nằm trong giỏ nhưng không tính tiền và không đặt được.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giỏ của Khách hàng đăng nhập lưu trong DB, 1 dòng mỗi biến thể (theo ERD); thêm AC-8
- v3 (2026-11-20): theo data model v2 — chốt giỏ khách vãng lai lưu ở `localStorage` (2a, 2b); chốt giỏ không lưu giá
- v4 (2026-11-21): bổ sung giả định tạo giỏ hàng cùng lúc tạo tài khoản Khách hàng
- v5 (2026-11-21): chốt tạo giỏ hàng cùng lúc tạo tài khoản Khách hàng (Q39)
- v6 (2026-11-23): theo phê duyệt đồng bộ UC-15-Q7 tại Codex, kiểm tra trạng thái/tồn kho từ DB qua Service trước khi thêm giỏ, kể cả localStorage; bổ sung E4, AC-9/10 cho giao diện cũ. Giữ draft và các giả định khác.
- v7 (2026-11-23): theo yêu cầu xử lý rà soát vòng 3 tại Codex, bổ sung kiểm tra product_status cùng variant_status ở bước 2/E4 và AC-11 chặn thêm giỏ khi sản phẩm cha INACTIVE dù biến thể còn ACTIVE/còn hàng; giữ nguyên các giả định khác.
