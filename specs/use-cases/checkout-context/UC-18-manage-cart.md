# UC-18: Quản lý giỏ hàng

## Metadata
- **ID:** UC-18
- **Bounded Context:** checkout-context
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
2. Hệ thống kiểm tra tồn kho của biến thể và thêm dòng vào giỏ (nếu biến thể đã có trong giỏ thì cộng dồn số lượng).
3. Khách mở trang giỏ hàng.
4. Hệ thống hiển thị từng dòng: ảnh, tên sản phẩm, màu, size, đơn giá hiện tại (đã áp khuyến mãi theo sản phẩm), số lượng, thành tiền và tạm tính của giỏ.
5. Khách đổi số lượng hoặc xóa dòng; hệ thống cập nhật lại thành tiền và tạm tính.

## Alternative Flows
- **2a. Khách vãng lai:** giỏ hàng lưu trên trình duyệt `[GD]`; khách vẫn thêm, sửa, xóa được như Khách hàng.
- **2b. Khách vãng lai đăng nhập:** giỏ trên trình duyệt được gộp vào giỏ của tài khoản; dòng trùng biến thể thì cộng dồn nhưng không vượt tồn kho `[GD]`.
- **4a. Giá hoặc khuyến mãi đã thay đổi:** giỏ luôn hiển thị giá hiện tại, không giữ giá lúc thêm vào giỏ `[GD]`.

## Exceptions
- **E1. Vượt tồn kho:** số lượng thêm hoặc sửa lớn hơn tồn kho của biến thể → hệ thống không cập nhật, báo "Chỉ còn N sản phẩm".
- **E2. Biến thể hết hàng hoặc ngừng bán:** dòng trong giỏ được đánh dấu "Hết hàng/Ngừng bán", không tính vào tạm tính và không đặt hàng được cho tới khi khách xóa `[GD]`.
- **E3. Số lượng không hợp lệ:** số lượng ≤ 0 hoặc không phải số nguyên → hệ thống từ chối.

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

## Dependencies
- **Upstream UC:** UC-12 Xem chi tiết sản phẩm, UC-15 Quản lý biến thể màu × size, UC-16 Quản lý giá bán theo size, UC-28 Quản lý khuyến mãi theo sản phẩm
- **Downstream UC:** UC-19 Đặt hàng thanh toán COD, UC-20 Đặt hàng thanh toán chuyển khoản QR
- **External Systems:** Không có

## Notes
- BR-TUAN1: khách chưa đăng nhập vẫn dùng được giỏ hàng, nhưng phải đăng nhập mới đặt hàng được.
- Thêm vào giỏ không giữ chỗ tồn kho; tồn kho chỉ bị trừ khi tạo đơn.
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).

### Quyết định đã chốt
- Giỏ của Khách hàng đã đăng nhập lưu trong DB; mỗi Khách hàng có 1 giỏ, mỗi biến thể chỉ có 1 dòng trong giỏ (theo ERD).

### Giả định [GD]
- Giỏ của khách vãng lai lưu trên trình duyệt.
- Khi đăng nhập, giỏ trình duyệt gộp vào giỏ tài khoản; dòng trùng cộng dồn nhưng không vượt tồn kho.
- Giỏ hiển thị giá hiện tại, không giữ giá lúc thêm.
- Dòng hết hàng/ngừng bán vẫn nằm trong giỏ nhưng không tính tiền và không đặt được.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giỏ của Khách hàng đăng nhập lưu trong DB, 1 dòng mỗi biến thể (theo ERD); thêm AC-8
