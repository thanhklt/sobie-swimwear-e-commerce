# UC-29: Quản lý khuyến mãi theo giá trị hóa đơn

## Metadata
- **ID:** UC-29
- **Module:** promotion
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý khuyến mãi theo giá trị hóa đơn để tạo hoặc ngừng một khuyến mãi.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên chọn "Tạo khuyến mãi theo hóa đơn".
2. Nhân viên nhập giá trị đơn tối thiểu, phần trăm giảm, số lượng được áp dụng, ngày bắt đầu và ngày kết thúc.
3. Hệ thống kiểm tra dữ liệu hợp lệ.
4. Hệ thống hiển thị popup xác nhận tóm tắt khuyến mãi: giá trị đơn tối thiểu, phần trăm giảm, số lượng được áp dụng, thời gian hiệu lực, kèm lưu ý "Khuyến mãi đã tạo không thể sửa, chỉ có thể ngừng".
5. Nhân viên bấm "Xác nhận".
6. Hệ thống lưu khuyến mãi với loại ORDER, số lượng đã dùng = 0.
7. Trong thời gian hiệu lực và khi số lượng đã dùng còn nhỏ hơn số lượng được áp dụng, khuyến mãi được xét khi tính mức giảm cho đơn (UC-31). Mỗi đơn được tạo với khuyến mãi này làm số lượng đã dùng tăng 1.

## Alternative Flows
- **5a. Hủy tại popup xác nhận:** Nhân viên bấm "Hủy" → hệ thống không lưu, quay lại màn hình nhập với dữ liệu đã nhập.
- **1a. Ngừng khuyến mãi (kết thúc trước hạn):** Nhân viên chọn một khuyến mãi chưa kết thúc và bấm "Ngừng" → khuyến mãi chuyển trạng thái tắt, hết hiệu lực ngay, không còn được xét trong UC-31 cho các đơn sau; ngày kết thúc đã chọn khi tạo giữ nguyên; khuyến mãi không bật lại được; đơn đã tạo không thay đổi.
- **1b. Xem danh sách khuyến mãi:** Nhân viên xem danh sách khuyến mãi theo hóa đơn kèm số lượng được áp dụng, số lượng đã dùng và trạng thái: "Sắp diễn ra" (chưa tới ngày bắt đầu), "Đang hiệu lực", "Đã kết thúc" (đã tới ngày kết thúc hoặc đã bị ngừng). Danh sách không có thao tác sửa.
- **1c. Lọc theo khoảng thời gian:** Nhân viên chọn "từ ngày" và "đến ngày" → hệ thống chỉ hiển thị các khuyến mãi có thời gian hiệu lực giao với khoảng đã chọn (kể cả giao một phần).
- **7a. Hết lượt:** số lượng đã dùng bằng số lượng được áp dụng → khuyến mãi không còn được xét trong UC-31 dù còn trong thời gian hiệu lực.
- **7b. Hết hạn:** hết ngày kết thúc đã chọn (múi giờ `Asia/Ho_Chi_Minh`) → khuyến mãi tự hết hiệu lực tại mốc 00:00:00 của ngày kế tiếp, chuyển "Đã kết thúc", không cần Nhân viên thao tác.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** thiếu trường bắt buộc, giá trị đơn tối thiểu âm, phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100, số lượng được áp dụng nhỏ hơn 1, hoặc ngày kết thúc không sau ngày bắt đầu → hệ thống báo lỗi theo từng trường, không hiển thị popup xác nhận, không lưu.

## Postconditions
- Khuyến mãi được lưu sau khi Nhân viên xác nhận và được xét cho các đơn tạo trong thời gian hiệu lực, khi còn lượt.
- Khuyến mãi đã tạo không thể sửa; chỉ có thể ngừng. Khuyến mãi đã ngừng không bật lại được.

## Acceptance Criteria

### AC-1: Tạo khuyến mãi hợp lệ
Given: Nhân viên đã đăng nhập
When: Nhân viên tạo khuyến mãi giảm 10% với giá trị đơn tối thiểu 500.000đ, số lượng được áp dụng 100, thời gian hiệu lực bao gồm hiện tại, rồi bấm "Xác nhận" ở popup
Then: khuyến mãi được lưu với trạng thái đang hiệu lực, số lượng đã dùng = 0
And: đơn có tạm tính từ 500.000đ trở lên được xét khuyến mãi này trong UC-31

### AC-2: Popup xác nhận trước khi lưu
Given: Nhân viên đã nhập đủ dữ liệu hợp lệ
When: Nhân viên bấm "Lưu"
Then: hệ thống hiển thị popup tóm tắt giá trị đơn tối thiểu, phần trăm giảm, số lượng được áp dụng, thời gian hiệu lực và lưu ý khuyến mãi không thể sửa
And: khuyến mãi chưa được lưu cho tới khi Nhân viên bấm "Xác nhận"

### AC-3: Hủy tại popup xác nhận
Given: popup xác nhận đang hiển thị
When: Nhân viên bấm "Hủy"
Then: không có khuyến mãi nào được tạo

### AC-4: Dữ liệu không hợp lệ
Given: Nhân viên ở màn hình tạo khuyến mãi
When: Nhân viên lưu với giá trị đơn tối thiểu âm, phần trăm giảm 0%, số lượng được áp dụng 0, hoặc ngày kết thúc trước ngày bắt đầu
Then: hệ thống báo lỗi tại trường tương ứng
And: không hiển thị popup xác nhận và không có khuyến mãi nào được tạo

### AC-5: Không có thao tác sửa
Given: khuyến mãi X đã được tạo
When: Nhân viên mở danh sách hoặc chi tiết khuyến mãi X
Then: không có thao tác sửa bất kỳ thông tin nào của X
And: chỉ có thao tác "Ngừng" nếu X chưa kết thúc

### AC-6: Ngừng khuyến mãi
Given: khuyến mãi X đang hiệu lực, đơn D đã được tạo với khuyến mãi X
When: Nhân viên ngừng khuyến mãi X
Then: đơn tạo sau đó không được xét khuyến mãi X
And: số tiền giảm của đơn D giữ nguyên
And: khuyến mãi X hiển thị "Đã kết thúc", ngày kết thúc vẫn là ngày đã chọn khi tạo
And: khuyến mãi X không có thao tác bật lại

### AC-7: Hết lượt áp dụng
Given: khuyến mãi X có số lượng được áp dụng 2 và đã dùng 2, vẫn trong thời gian hiệu lực
When: khách đặt đơn có tạm tính đạt giá trị đơn tối thiểu của X
Then: khuyến mãi X không được xét cho đơn này

### AC-8: Tăng số lượng đã dùng
Given: khuyến mãi X có số lượng đã dùng 5
When: một đơn được tạo với khuyến mãi X là mức giảm được chọn
Then: số lượng đã dùng của X = 6

### AC-9: Lọc theo khoảng thời gian
Given: khuyến mãi X hiệu lực 01/11 → 10/11, khuyến mãi Y hiệu lực 20/11 → 30/11, khuyến mãi Z hiệu lực 05/12 → 31/12
When: Nhân viên lọc danh sách từ 05/11 đến 25/11
Then: danh sách hiển thị X và Y
And: không hiển thị Z

### AC-10: Trạng thái hiển thị
Given: hôm nay 20/11; khuyến mãi P hiệu lực 25/11 → 30/11, Q hiệu lực 15/11 → 25/11, R hiệu lực 01/11 → 10/11, S hiệu lực 15/11 → 30/11 nhưng đã bị ngừng
When: Nhân viên mở danh sách khuyến mãi theo hóa đơn
Then: P hiển thị "Sắp diễn ra", Q hiển thị "Đang hiệu lực", R và S hiển thị "Đã kết thúc"
And: đơn đặt hôm nay không được xét P, R, S

### AC-11: Hết hiệu lực đúng mốc hết ngày kết thúc
Given: khuyến mãi X có ngày kết thúc 20/11/2026 theo lịch `Asia/Ho_Chi_Minh` (mốc hết hiệu lực = 00:00:00 ngày 21/11/2026 `Asia/Ho_Chi_Minh`, lưu UTC)
When: tại thời điểm ngay trước mốc (23:59:59 ngày 20/11/2026 `Asia/Ho_Chi_Minh`), hệ thống tính mức giảm cho đơn đủ điều kiện của X
Then: X vẫn "Đang hiệu lực" và được xét trong UC-31
When: tại đúng mốc 00:00:00 ngày 21/11/2026 `Asia/Ho_Chi_Minh`
Then: X hiển thị "Đã kết thúc" và không còn được xét trong UC-31

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-31, UC-37
- **External Systems:** không có

## Notes
- Theo BR: hệ thống tự chọn mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher (UC-31).
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách khuyến mãi.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Khuyến mãi theo hóa đơn có: loại (ORDER), phần trăm giảm, giá trị đơn tối thiểu, số lượng được áp dụng, số lượng đã dùng, ngày bắt đầu, ngày kết thúc, trạng thái (theo ERD).
- Số lượng được áp dụng là số lượt tối đa; mỗi đơn được áp tính 1 lượt; hết lượt thì không còn được xét (đã chốt 15/11/2026).
- Khuyến mãi đã tạo thì không được sửa; chỉ có thể ngừng để các đơn sau không được áp nữa; đơn đã tạo không đổi (đã chốt 15/11/2026).
- Hết hiệu lực theo 2 cách: hết ngày kết thúc đã chọn, hoặc Nhân viên ngừng trước hạn; ngừng trước hạn chỉ đổi trạng thái sang tắt, ngày kết thúc giữ nguyên (đã chốt 20/11/2026, data model v2, Q25, Q28).
- Nhân viên chọn ngày bắt đầu / ngày kết thúc theo lịch `Asia/Ho_Chi_Minh`. Ngày bắt đầu có hiệu lực từ 00:00:00 ngày đó; ngày kết thúc áp dụng đến hết ngày đã chọn — hết hiệu lực tại 00:00:00 của ngày kế tiếp (`Asia/Ho_Chi_Minh`). Hệ thống lưu các mốc dạng `timestamptz` UTC; điều kiện hiệu lực: `start <= now < end` (đã chốt 24/11/2026).
- Khuyến mãi đã ngừng không bật lại được; muốn áp lại thì tạo khuyến mãi mới (đã chốt 20/11/2026, data model v2, Q22).
- Trạng thái hiển thị: Sắp diễn ra, Đang hiệu lực, Đã kết thúc — tính từ trạng thái bật / tắt và ngày bắt đầu / kết thúc, không lưu riêng (đã chốt 20/11/2026, data model v2, Q23c, Q27).
- Khi tạo khuyến mãi, hệ thống hiển thị popup xác nhận; chỉ lưu khi Nhân viên bấm xác nhận (đã chốt 15/11/2026).
- Khuyến mãi không có tên, nhận diện bằng mã khuyến mãi (theo ERD, đã chốt 15/11/2026).
- Danh sách khuyến mãi lọc được theo khoảng thời gian để Nhân viên tra cứu (đã chốt 15/11/2026).
- Lọc theo khoảng thời gian: hiển thị khuyến mãi có thời gian hiệu lực giao với khoảng đã chọn, kể cả giao một phần (đã chốt 15/11/2026).

**Giả định [GD]**
- Được phép có nhiều khuyến mãi theo hóa đơn cùng hiệu lực; UC-31 chọn cái giảm nhiều nhất trong số đủ điều kiện.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, thêm số lượng được áp dụng / đã dùng và AC hết lượt (theo ERD)
- v3 (2026-11-15): bỏ thao tác sửa khuyến mãi (chỉ ngừng); thêm popup xác nhận khi tạo
- v4 (2026-11-15): bỏ tên khuyến mãi; thêm lọc danh sách theo khoảng thời gian (1c, AC-9)
- v5 (2026-11-15): chốt quy tắc lọc theo thời gian (giao khoảng)
- v6 (2026-11-20): đồng bộ BR-GIAIDOAN1 — bỏ "Bị từ chối" (Nhân viên chỉ còn "Hủy đơn")
- v7 (2026-11-20): theo data model v2 — ngừng trước hạn giữ ngày kết thúc, không bật lại (1a, AC-6); thêm 7b hết hạn; chốt trạng thái Sắp diễn ra / Đang hiệu lực / Đã kết thúc (1b, AC-10)
- v8 (2026-11-23): đồng bộ ràng buộc dữ liệu và quy tắc hoàn lượt khuyến mãi theo hóa đơn khi hủy đơn với data model v2; loại các quy tắc đã chốt khỏi mục giả định
- v9 (2026-11-24): chốt mốc hết hiệu lực = hết ngày kết thúc theo `Asia/Ho_Chi_Minh` (7b, Quyết định đã chốt); thêm AC-11 nghiệm thu ngay trước và đúng tại mốc
