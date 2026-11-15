# UC-29: Quản lý khuyến mãi theo giá trị hóa đơn

## Metadata
- **ID:** UC-29
- **Bounded Context:** promotion-context
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý khuyến mãi theo giá trị hóa đơn để tạo, sửa hoặc ngừng một khuyến mãi.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên chọn "Tạo khuyến mãi theo hóa đơn".
2. Nhân viên nhập tên, giá trị đơn tối thiểu, phần trăm giảm, số lượng được áp dụng, ngày bắt đầu và ngày kết thúc.
3. Hệ thống kiểm tra dữ liệu hợp lệ.
4. Hệ thống lưu khuyến mãi với loại ORDER, số lượng đã dùng = 0.
5. Trong thời gian hiệu lực và khi số lượng đã dùng còn nhỏ hơn số lượng được áp dụng, khuyến mãi được xét khi tính mức giảm cho đơn (UC-31). Mỗi đơn được tạo với khuyến mãi này làm số lượng đã dùng tăng 1.

## Alternative Flows
- **1a. Sửa khuyến mãi:** Nhân viên sửa thông tin, hệ thống kiểm tra như bước 3 rồi lưu. Đơn đã tạo không bị ảnh hưởng `[GD]`.
- **1b. Ngừng khuyến mãi:** khuyến mãi hết hiệu lực ngay, không còn được xét trong UC-31 `[GD]`.
- **1c. Xem danh sách khuyến mãi:** Nhân viên xem danh sách khuyến mãi theo hóa đơn kèm số lượng được áp dụng, số lượng đã dùng và trạng thái `[GD]`.
- **5a. Hết lượt:** số lượng đã dùng bằng số lượng được áp dụng → khuyến mãi không còn được xét trong UC-31 dù còn trong thời gian hiệu lực.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** thiếu tên, giá trị đơn tối thiểu âm, phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100 `[GD]`, số lượng được áp dụng nhỏ hơn 1 hoặc nhỏ hơn số lượng đã dùng `[GD]`, hoặc ngày kết thúc không sau ngày bắt đầu → hệ thống báo lỗi theo từng trường, không lưu.

## Postconditions
- Khuyến mãi được lưu và được xét cho các đơn tạo trong thời gian hiệu lực, khi còn lượt.

## Acceptance Criteria

### AC-1: Tạo khuyến mãi hợp lệ
Given: Nhân viên đã đăng nhập
When: Nhân viên tạo khuyến mãi giảm 10% với giá trị đơn tối thiểu 500.000đ, số lượng được áp dụng 100, thời gian hiệu lực bao gồm hiện tại
Then: khuyến mãi được lưu với trạng thái đang hiệu lực, số lượng đã dùng = 0
And: đơn có tạm tính từ 500.000đ trở lên được xét khuyến mãi này trong UC-31

### AC-2: Dữ liệu không hợp lệ
Given: Nhân viên ở màn hình tạo khuyến mãi
When: Nhân viên lưu với giá trị đơn tối thiểu âm, phần trăm giảm 0%, số lượng được áp dụng 0, hoặc ngày kết thúc trước ngày bắt đầu
Then: hệ thống báo lỗi tại trường tương ứng
And: không có khuyến mãi nào được tạo

### AC-3: Ngừng khuyến mãi
Given: khuyến mãi X đang hiệu lực
When: Nhân viên ngừng khuyến mãi X
Then: đơn tạo sau đó không được xét khuyến mãi X
And: đơn đã tạo trước đó giữ nguyên số tiền

### AC-4: Sửa khuyến mãi không ảnh hưởng đơn cũ
Given: đơn D đã được tạo với khuyến mãi X
When: Nhân viên đổi phần trăm giảm của khuyến mãi X
Then: số tiền giảm của đơn D không đổi

### AC-5: Hết lượt áp dụng
Given: khuyến mãi X có số lượng được áp dụng 2 và đã dùng 2, vẫn trong thời gian hiệu lực
When: khách đặt đơn có tạm tính đạt giá trị đơn tối thiểu của X
Then: khuyến mãi X không được xét cho đơn này

### AC-6: Tăng số lượng đã dùng
Given: khuyến mãi X có số lượng đã dùng 5
When: một đơn được tạo với khuyến mãi X là mức giảm được chọn
Then: số lượng đã dùng của X = 6

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-31, UC-37
- **External Systems:** không có

## Notes
- Theo BR: hệ thống tự chọn mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher (UC-31).
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung) cho danh sách khuyến mãi.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Khuyến mãi theo hóa đơn có: loại (ORDER), phần trăm giảm, giá trị đơn tối thiểu, số lượng được áp dụng, số lượng đã dùng, ngày bắt đầu, ngày kết thúc, trạng thái (theo ERD).
- Số lượng được áp dụng là số lượt tối đa; mỗi đơn được áp tính 1 lượt; hết lượt thì không còn được xét (đã chốt 15/11/2026).

**Giả định [GD]**
- Được phép có nhiều khuyến mãi theo hóa đơn cùng hiệu lực; UC-31 chọn cái giảm nhiều nhất trong số đủ điều kiện.
- Sửa hoặc ngừng khuyến mãi không làm thay đổi đơn đã tạo.
- Đơn bị hủy hoặc bị từ chối thì hoàn lượt khuyến mãi theo hóa đơn (giảm số lượng đã dùng 1).
- Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100; số lượng được áp dụng ≥ 1 và không nhỏ hơn số lượng đã dùng.
- Danh sách khuyến mãi hiển thị số lượng được áp dụng, số lượng đã dùng và trạng thái.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, thêm số lượng được áp dụng / đã dùng và AC hết lượt (theo ERD)
