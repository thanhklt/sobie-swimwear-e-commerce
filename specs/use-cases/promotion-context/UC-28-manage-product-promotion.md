# UC-28: Quản lý khuyến mãi theo sản phẩm

## Metadata
- **ID:** UC-28
- **Bounded Context:** promotion-context
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý khuyến mãi theo sản phẩm để tạo, sửa hoặc kết thúc một chương trình khuyến mãi.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Sản phẩm cần áp khuyến mãi đã tồn tại (UC-14).

## Main Flow
1. Nhân viên chọn "Tạo khuyến mãi theo sản phẩm".
2. Nhân viên nhập tên, phần trăm giảm, ngày bắt đầu, và chọn một hoặc nhiều sản phẩm được áp dụng `[GD]`.
3. Hệ thống kiểm tra dữ liệu hợp lệ và các sản phẩm được chọn chưa thuộc khuyến mãi theo sản phẩm nào khác còn hiệu lực.
4. Hệ thống lưu khuyến mãi với loại PRODUCT.
5. Từ ngày bắt đầu cho đến khi Nhân viên kết thúc chương trình, giá sau giảm = giá bán theo size × (100% − phần trăm giảm), làm tròn `ROUND_HALF_UP` về số nguyên VND; giá này được hiển thị trên trang chi tiết sản phẩm (UC-12) và dùng khi tính tiền đơn (UC-31).

## Alternative Flows
- **1a. Sửa khuyến mãi:** Nhân viên chọn một khuyến mãi chưa kết thúc, sửa thông tin, hệ thống kiểm tra như bước 3 rồi lưu. Đơn đã tạo không bị ảnh hưởng `[GD]`.
- **1b. Kết thúc chương trình:** Nhân viên bấm "Kết thúc chương trình"; khuyến mãi hết hiệu lực ngay, giá sản phẩm trở về giá bán theo size; các sản phẩm được giải phóng để gắn vào khuyến mãi khác.
- **1c. Xem danh sách khuyến mãi:** Nhân viên xem danh sách khuyến mãi theo sản phẩm kèm trạng thái (sắp diễn ra, đang hiệu lực, đã kết thúc) `[GD]`.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** thiếu tên, thiếu ngày bắt đầu, hoặc phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100 `[GD]` → hệ thống báo lỗi theo từng trường, không lưu.
- **E2. Sản phẩm đã thuộc khuyến mãi khác:** một sản phẩm được chọn đang thuộc một khuyến mãi theo sản phẩm khác chưa kết thúc → hệ thống báo lỗi, không lưu.

## Postconditions
- Khuyến mãi được lưu; từ ngày bắt đầu đến khi Nhân viên kết thúc chương trình, các sản phẩm được áp dụng có giá sau giảm.

## Acceptance Criteria

### AC-1: Tạo khuyến mãi hợp lệ
Given: Nhân viên đã đăng nhập, sản phẩm A đang bán, size M giá 300.000đ, chưa thuộc khuyến mãi theo sản phẩm nào
When: Nhân viên tạo khuyến mãi giảm 10% cho sản phẩm A với ngày bắt đầu là hôm nay
Then: khuyến mãi được lưu với trạng thái đang hiệu lực
And: trang chi tiết sản phẩm A hiển thị giá gốc 300.000đ và giá sau giảm 270.000đ cho size M

### AC-2: Khuyến mãi chưa đến ngày bắt đầu
Given: khuyến mãi cho sản phẩm A có ngày bắt đầu ở tương lai
When: khách xem trang chi tiết sản phẩm A
Then: chỉ hiển thị giá bán theo size, không có giá sau giảm

### AC-3: Thiếu hoặc sai dữ liệu
Given: Nhân viên ở màn hình tạo khuyến mãi
When: Nhân viên lưu khi chưa nhập tên, hoặc nhập phần trăm giảm 0% hoặc 120%
Then: hệ thống báo lỗi tại trường tương ứng
And: không có khuyến mãi nào được tạo

### AC-4: Sản phẩm đã thuộc khuyến mãi khác
Given: sản phẩm A đang thuộc khuyến mãi X chưa kết thúc
When: Nhân viên tạo khuyến mãi Y có chọn sản phẩm A
Then: hệ thống báo lỗi sản phẩm A đã thuộc khuyến mãi khác
And: khuyến mãi Y không được lưu

### AC-5: Kết thúc chương trình
Given: khuyến mãi X đang hiệu lực cho sản phẩm A
When: Nhân viên bấm "Kết thúc chương trình" cho khuyến mãi X
Then: trang chi tiết sản phẩm A không còn hiển thị giá sau giảm
And: đơn đã tạo trước đó giữ nguyên số tiền
And: sản phẩm A có thể được gắn vào khuyến mãi khác

### AC-6: Không giới hạn số lượng áp dụng
Given: khuyến mãi X giảm 10% đang hiệu lực cho sản phẩm A
When: khách đặt nhiều đơn liên tiếp có sản phẩm A
Then: mọi đơn đều được tính giá sau giảm của khuyến mãi X cho đến khi Nhân viên kết thúc chương trình

### AC-7: Làm tròn giá sau giảm
Given: sản phẩm A size S giá 199.999đ, khuyến mãi giảm 15%
When: hệ thống tính giá sau giảm
Then: giá sau giảm = 169.999đ (169.999,15 làm tròn `ROUND_HALF_UP`)

## Dependencies
- **Upstream UC:** UC-02, UC-14, UC-16
- **Downstream UC:** UC-12, UC-31, UC-37
- **External Systems:** không có

## Notes
- Theo BR: khuyến mãi theo sản phẩm giảm trực tiếp trên giá sản phẩm và hiển thị trên trang chi tiết sản phẩm; được tính cùng với mức giảm được chọn giữa khuyến mãi hóa đơn và voucher (UC-31).
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung) cho danh sách khuyến mãi.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Khuyến mãi có loại (PRODUCT), ngày bắt đầu, ngày kết thúc, trạng thái (theo ERD).
- Khuyến mãi theo sản phẩm không áp dụng số lượng được áp dụng (promotion_quantity), không giới hạn số lượng; có hiệu lực cho đến khi Nhân viên bấm kết thúc chương trình (đã chốt 15/11/2026).
- Mỗi sản phẩm thuộc tối đa một khuyến mãi theo sản phẩm; khuyến mãi áp cho mọi biến thể của sản phẩm (theo ERD: sản phẩm có một khóa ngoại tới khuyến mãi theo sản phẩm).

**Giả định [GD]**
- Một khuyến mãi áp dụng cho một hoặc nhiều sản phẩm.
- Ngày kết thúc tự động không dùng cho loại này; ngày kết thúc được ghi khi Nhân viên kết thúc chương trình.
- Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100.
- Sửa khuyến mãi không làm thay đổi đơn đã tạo.
- Danh sách khuyến mãi hiển thị trạng thái: sắp diễn ra, đang hiệu lực, đã kết thúc.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, không giới hạn số lượng, hiệu lực đến khi Nhân viên kết thúc chương trình, mỗi sản phẩm tối đa 1 khuyến mãi (theo ERD)
