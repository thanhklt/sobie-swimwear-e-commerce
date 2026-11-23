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
- Biến thể (màu × size) tồn tại trong hệ thống.

## Main Flow
1. Khách chọn màu, size, số lượng trên trang chi tiết sản phẩm và bấm "Thêm vào giỏ".
2. Hệ thống gọi Service công khai của `catalog` để kiểm tra từ Database đồng thời sản phẩm cha có `product_status = ACTIVE` và biến thể có `variant_status = ACTIVE`, rồi gọi Service công khai của `inventory` để lấy tồn kho khả dụng hiện hành; không dùng trạng thái/tồn kho từ cache storefront làm căn cứ. Nếu sản phẩm hoặc biến thể không còn được bán thì áp dụng E7; nếu số lượng mới (kể cả cộng dồn với dòng đã có) vượt tồn kho thì áp dụng E1. Chỉ khi hợp lệ mới thêm hoặc cập nhật dòng vào giỏ.
3. Khách mở trang giỏ hàng.
4. Hệ thống hiển thị từng dòng: ảnh, tên sản phẩm, màu, size, đơn giá hiện tại (đã áp khuyến mãi theo sản phẩm), số lượng, thành tiền và tạm tính của giỏ.
5. Khách đổi số lượng hoặc xóa dòng; hệ thống cập nhật lại thành tiền và tạm tính.

## Alternative Flows
- **2a. Khách vãng lai:** giỏ hàng lưu ở `localStorage` của trình duyệt; khách vẫn thêm, sửa, xóa được như Khách hàng. Khi thêm giỏ, trình duyệt phải nhận kết quả kiểm tra từ server theo bước 2 trước khi ghi thay đổi vào `localStorage`; dữ liệu cũ trong trình duyệt không thay thế kiểm tra trạng thái/tồn kho hiện hành.
- **2b. Khách vãng lai đăng nhập:** giỏ trong `localStorage` được gộp vào giỏ của tài khoản; dòng trùng biến thể thì cộng dồn nhưng không vượt tồn kho `[GD]`.
- **2c. Tồn kho thay đổi khi gộp giỏ:** hệ thống kiểm tra lại tồn kho và trạng thái bán của từng biến thể. Với biến thể còn bán và còn hàng, số lượng gộp không vượt tồn kho. Với biến thể hết hàng hoặc ngừng bán, giữ số lượng khách đã chọn (cộng dồn nếu trùng), gắn nhãn tương ứng, không tính vào tạm tính và không cho đặt; không đổi số lượng thành 0 `[GD]`.
- **2d. Hoàn tất gộp giỏ:** trước khi gửi, trình duyệt lưu một mã yêu cầu gộp duy nhất cùng tài khoản đích và dữ liệu giỏ cần gộp. Mọi lần gửi lại của cùng lần gộp phải dùng nguyên mã và dữ liệu đó, kể cả sau khi tải lại trang. Máy chủ nhận diện yêu cầu theo tài khoản đã xác thực và mã yêu cầu; lưu cập nhật giỏ và dấu đã xử lý trong cùng transaction, bảo đảm cùng yêu cầu chỉ được áp dụng một lần kể cả khi gửi đồng thời. Nếu đã xử lý, trả xác nhận thành công mà không cộng số lượng lại. Chỉ xóa dữ liệu giỏ đã gộp trong `localStorage` sau khi nhận xác nhận thành công; không xóa thay đổi mới ngoài dữ liệu của lần gộp đó.
- **4a. Giá hoặc khuyến mãi đã thay đổi:** giỏ luôn hiển thị giá hiện tại, không giữ giá lúc thêm vào giỏ `[GD]`.

## Exceptions
- **E1. Vượt tồn kho:** số lượng thêm hoặc sửa lớn hơn tồn kho của biến thể → hệ thống không cập nhật, báo "Chỉ còn N sản phẩm".
- **E2. Biến thể hết hàng hoặc ngừng bán:** dòng trong giỏ được đánh dấu "Hết hàng/Ngừng bán", không tính vào tạm tính và không đặt hàng được cho tới khi khách xóa `[GD]`.
- **E3. Số lượng không hợp lệ:** số lượng ≤ 0 hoặc không phải số nguyên → hệ thống từ chối.
- **E4. Lỗi lưu giỏ:** rollback cập nhật giỏ và dấu đã xử lý yêu cầu gộp; giữ giỏ trình duyệt và mã yêu cầu để thử lại.
- **E5. Mất phản hồi khi gộp giỏ:** trình duyệt chưa xác định được kết quả nên giữ dữ liệu và mã yêu cầu; gửi lại cùng yêu cầu để lấy xác nhận. Nếu máy chủ đã lưu, không cộng lại số lượng.
- **E6. Dùng lại mã yêu cầu với dữ liệu khác:** hệ thống từ chối, không thay đổi giỏ; một mã chỉ đại diện cho một bộ dữ liệu gộp cố định.
- **E7. Sản phẩm hoặc biến thể không còn được bán khi thêm giỏ:** tại bước 2, Database cho biết sản phẩm cha đã `INACTIVE`, biến thể đã `INACTIVE`, hoặc sản phẩm/biến thể không còn tồn tại dù giao diện cũ vẫn cho bấm thêm → hệ thống từ chối thêm, báo rõ dòng không còn được bán và giữ nguyên giỏ hiện tại (cả DB lẫn `localStorage`); không giữ chỗ hay trừ tồn kho.

## Postconditions
- Giỏ lưu số lượng đã được chấp nhận ở lần cập nhật; kiểm tra tồn kho tại thời điểm thêm, sửa hoặc gộp giỏ. Giỏ không giữ chỗ tồn kho; dòng hết hàng/ngừng bán vẫn được giữ và đánh dấu không thể đặt.
- Với Khách hàng đã đăng nhập, giỏ được lưu trong DB; mỗi biến thể chỉ có 1 dòng trong giỏ.
- Một yêu cầu gộp được áp dụng tối đa một lần; gửi lại không làm tăng số lượng thêm lần nữa.

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

### AC-9: Gộp giỏ khi tồn kho thay đổi
Given: giỏ trình duyệt có biến thể "Đỏ / M" số lượng 2 nhưng tồn kho hiện tại chỉ còn 1
When: khách đăng nhập và hệ thống gộp hai giỏ
Then: số lượng trong giỏ tài khoản là 1
And: số lượng không vượt tồn kho hiện tại

### AC-10: Mất phản hồi sau khi lưu giỏ
Given: giỏ tài khoản có "Đỏ / M" số lượng 1, giỏ trình duyệt có số lượng 2, tồn kho 10
When: máy chủ xử lý yêu cầu gộp M thành công nhưng phản hồi bị mất
Then: giỏ tài khoản có số lượng 3; trình duyệt vẫn giữ dữ liệu gộp và mã M
When: trình duyệt gửi lại cùng mã M và dữ liệu gộp
Then: máy chủ xác nhận đã xử lý, số lượng cuối cùng vẫn là 3, không tăng thành 5
And: trình duyệt xóa dữ liệu đã gộp sau khi nhận xác nhận thành công

### AC-11: Gửi đồng thời cùng yêu cầu gộp
Given: giỏ tài khoản có số lượng 1, dữ liệu gộp có số lượng 2, tồn kho 10
When: hai yêu cầu cùng mã gộp và cùng dữ liệu được xử lý đồng thời cho tài khoản đó
Then: dữ liệu gộp chỉ được áp dụng một lần và số lượng cuối cùng là 3
### AC-12: Chặn thêm biến thể ngừng bán từ giao diện cũ
Given: dữ liệu kiểm thử có sản phẩm cha ACTIVE, biến thể "Đỏ / M" đã INACTIVE từ trước khi phiếu nhập chuyển CONFIRMED và hiện tồn 5; dữ liệu cũ trong trình duyệt vẫn thể hiện biến thể đang bán
When: Khách hàng đã đăng nhập hoặc Khách vãng lai bấm thêm biến thể "Đỏ / M" từ trang cũ
Then: server đọc trạng thái hiện hành qua Service công khai của catalog và từ chối thêm theo E7
And: giỏ trong DB hoặc localStorage giữ nguyên, tồn kho không bị trừ, khách nhận thông báo biến thể không còn được bán

### AC-13: Kiểm tra tồn kho hiện hành khi thêm từ giao diện cũ
Given: biến thể "Đỏ / M" vẫn ACTIVE, cache storefront hiển thị tồn kho 5 nhưng Database hiện chỉ còn 1; giỏ đang trống
When: Khách hàng đã đăng nhập hoặc Khách vãng lai yêu cầu thêm 2 sản phẩm "Đỏ / M"
Then: hệ thống lấy tồn kho hiện hành qua Service công khai của inventory và từ chối theo E1 với thông báo "Chỉ còn 1 sản phẩm"
And: giỏ trong DB hoặc localStorage giữ nguyên và tồn kho không bị trừ

### AC-14: Chặn thêm giỏ khi sản phẩm cha ngừng bán nhưng biến thể vẫn ACTIVE
Given: dữ liệu kiểm thử có sản phẩm cha đã INACTIVE từ trước khi phiếu nhập chuyển CONFIRMED, biến thể "Đỏ / M" vẫn ACTIVE và hiện tồn 5; trình duyệt đang giữ dữ liệu cũ thể hiện sản phẩm đang bán
When: Khách hàng đã đăng nhập hoặc Khách vãng lai yêu cầu thêm 1 sản phẩm "Đỏ / M"
Then: Service catalog đọc trạng thái hiện hành của cả sản phẩm và biến thể; hệ thống từ chối thêm theo E7 do sản phẩm cha INACTIVE
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
- v6 (2026-11-22): cho phép mở giỏ có biến thể hết hàng; bổ sung xử lý lỗi lưu và AC-9.
- v7 (2026-11-22): bổ sung kiểm tra tồn kho và trạng thái bán khi gộp giỏ; thêm AC-10.
- v8 (2026-11-22): gộp tiêu chí hết hàng trùng vào AC-7; đánh lại tiêu chí gộp giỏ thành AC-9.
- v9 (2026-11-22): làm rõ số lượng của dòng hết hàng khi gộp và chỉ xóa giỏ trình duyệt sau khi lưu thành công.
- v10 (2026-11-23): nhận diện yêu cầu gộp bằng mã duy nhất theo tài khoản, lưu dấu xử lý cùng transaction; bổ sung AC-10, AC-11 chống cộng lặp khi mất phản hồi hoặc gửi đồng thời.
- v11 (2026-11-23): theo phê duyệt đồng bộ UC-15-Q7 tại Codex, kiểm tra trạng thái/tồn kho từ DB qua Service trước khi thêm giỏ, kể cả localStorage; bổ sung E7, AC-12/13 cho giao diện cũ. Giữ draft và các giả định khác.
- v12 (2026-11-23): theo yêu cầu xử lý rà soát vòng 3 tại Codex, bổ sung kiểm tra product_status cùng variant_status ở bước 2/E7 và AC-14 chặn thêm giỏ khi sản phẩm cha INACTIVE dù biến thể còn ACTIVE/còn hàng; giữ nguyên các giả định khác.

- v13 (2026-11-23): merge main, giữ xử lý gộp giỏ chống cộng lặp cùng kiểm tra DB hiện hành từ Catalog; E7 và AC-12..14 giữ các ca dữ liệu storefront cũ.
- v14 (2026-11-23): sửa AC liên UC theo quy tắc chỉ sửa Mô tả sau CONFIRMED: trạng thái INACTIVE trong fixture được đặt trước xác nhận nhập; thao tác ngừng bán sau CONFIRMED bị từ chối, đặt hàng chờ khóa rồi đọc lại ACTIVE và tiếp tục khi đủ điều kiện. Không đổi luồng nghiệp vụ hoặc các giả định khác.
