# UC-28: Quản lý khuyến mãi theo sản phẩm

## Metadata
- **ID:** UC-28
- **Module:** promotion
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý khuyến mãi theo sản phẩm để tạo hoặc kết thúc (ngừng) một chương trình khuyến mãi.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Sản phẩm cần áp khuyến mãi đã tồn tại (UC-14).

## Main Flow
1. Nhân viên chọn "Tạo khuyến mãi theo sản phẩm".
2. Nhân viên nhập phần trăm giảm và chọn **một** sản phẩm được áp dụng. Không có ngày bắt đầu, ngày kết thúc.
3. Hệ thống kiểm tra dữ liệu hợp lệ và sản phẩm được chọn chưa thuộc khuyến mãi theo sản phẩm nào khác chưa kết thúc.
4. Hệ thống hiển thị popup xác nhận tóm tắt khuyến mãi: phần trăm giảm, sản phẩm, kèm lưu ý "Khuyến mãi có hiệu lực ngay khi xác nhận; đã tạo thì không thể sửa, chỉ có thể kết thúc".
5. Nhân viên bấm "Xác nhận".
6. Hệ thống lưu khuyến mãi với loại PRODUCT, trạng thái bật, ghi thời điểm tạo; khuyến mãi có hiệu lực ngay.
7. Từ lúc tạo cho đến khi Nhân viên kết thúc chương trình, giá sau giảm = giá bán theo size × (100% − phần trăm giảm), làm tròn `ROUND_HALF_UP` về số nguyên VND; giá này được hiển thị trên trang chi tiết sản phẩm (UC-12) và dùng khi tính tiền đơn (UC-31).

## Alternative Flows
- **5a. Hủy tại popup xác nhận:** Nhân viên bấm "Hủy" → hệ thống không lưu, quay lại màn hình nhập với dữ liệu đã nhập.
- **1a. Kết thúc chương trình (ngừng khuyến mãi):** Nhân viên chọn một khuyến mãi chưa kết thúc và bấm "Kết thúc chương trình" → khuyến mãi chuyển trạng thái tắt và hết hiệu lực ngay; giá sản phẩm trở về giá bán theo size cho các đơn sau; sản phẩm được giải phóng để gắn vào khuyến mãi mới. Khuyến mãi đã kết thúc không bật lại được. Đơn đã tạo không thay đổi.
- **1b. Xem danh sách khuyến mãi:** Nhân viên xem danh sách khuyến mãi theo sản phẩm kèm trạng thái: "Đang hiệu lực" (chưa kết thúc) hoặc "Đã kết thúc". Loại này không có trạng thái "Sắp diễn ra" vì có hiệu lực ngay khi tạo. Danh sách không có thao tác sửa và không có bộ lọc theo khoảng thời gian.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** không chọn sản phẩm nào, hoặc phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100 `[GD]` → hệ thống báo lỗi theo từng trường, không hiển thị popup xác nhận, không lưu.
- **E2. Sản phẩm đã thuộc khuyến mãi khác:** sản phẩm được chọn đang thuộc một khuyến mãi theo sản phẩm khác chưa kết thúc → hệ thống báo lỗi, không lưu.

## Postconditions
- Khuyến mãi được lưu sau khi Nhân viên xác nhận và có hiệu lực ngay; đến khi Nhân viên kết thúc chương trình, sản phẩm được áp dụng có giá sau giảm.
- Khuyến mãi đã tạo không thể sửa; chỉ có thể kết thúc. Khuyến mãi đã kết thúc không bật lại được.

## Acceptance Criteria

### AC-1: Tạo khuyến mãi hợp lệ
Given: Nhân viên đã đăng nhập, sản phẩm A đang bán, size M giá 300.000đ, chưa thuộc khuyến mãi theo sản phẩm nào
When: Nhân viên tạo khuyến mãi giảm 10% cho sản phẩm A và bấm "Xác nhận" ở popup
Then: khuyến mãi được lưu với trạng thái đang hiệu lực
And: trang chi tiết sản phẩm A hiển thị giá gốc 300.000đ và giá sau giảm 270.000đ cho size M

### AC-2: Popup xác nhận trước khi lưu
Given: Nhân viên đã nhập đủ dữ liệu hợp lệ cho khuyến mãi giảm 10% cho sản phẩm A
When: Nhân viên bấm "Lưu"
Then: hệ thống hiển thị popup tóm tắt phần trăm giảm, sản phẩm A và lưu ý khuyến mãi có hiệu lực ngay, không thể sửa
And: khuyến mãi chưa được lưu cho tới khi Nhân viên bấm "Xác nhận"

### AC-3: Hủy tại popup xác nhận
Given: popup xác nhận đang hiển thị
When: Nhân viên bấm "Hủy"
Then: không có khuyến mãi nào được tạo
And: sản phẩm A vẫn không thuộc khuyến mãi nào

### AC-4: Có hiệu lực ngay khi tạo
Given: sản phẩm A size M giá 300.000đ, chưa thuộc khuyến mãi theo sản phẩm nào
When: Nhân viên xác nhận tạo khuyến mãi giảm 10% cho sản phẩm A, ngay sau đó khách mở trang chi tiết sản phẩm A
Then: trang hiển thị giá sau giảm 270.000đ cho size M
And: màn hình tạo khuyến mãi không có ô nhập ngày bắt đầu hay ngày kết thúc

### AC-5: Thiếu hoặc sai dữ liệu
Given: Nhân viên ở màn hình tạo khuyến mãi
When: Nhân viên lưu khi chưa chọn sản phẩm, hoặc nhập phần trăm giảm 0% hoặc 120%
Then: hệ thống báo lỗi tại trường tương ứng
And: không hiển thị popup xác nhận và không có khuyến mãi nào được tạo

### AC-6: Sản phẩm đã thuộc khuyến mãi khác
Given: sản phẩm A đang thuộc khuyến mãi X chưa kết thúc
When: Nhân viên tạo khuyến mãi Y có chọn sản phẩm A
Then: hệ thống báo lỗi sản phẩm A đã thuộc khuyến mãi khác
And: khuyến mãi Y không được lưu

### AC-7: Không có thao tác sửa
Given: khuyến mãi X đã được tạo
When: Nhân viên mở danh sách hoặc chi tiết khuyến mãi X
Then: không có thao tác sửa phần trăm giảm hay sản phẩm
And: chỉ có thao tác "Kết thúc chương trình" nếu X chưa kết thúc

### AC-8: Kết thúc chương trình
Given: khuyến mãi X đang hiệu lực cho sản phẩm A
When: Nhân viên bấm "Kết thúc chương trình" cho khuyến mãi X
Then: trang chi tiết sản phẩm A không còn hiển thị giá sau giảm
And: khuyến mãi X hiển thị trạng thái "Đã kết thúc"
And: đơn đã tạo trước đó giữ nguyên số tiền
And: sản phẩm A có thể được gắn vào khuyến mãi khác
And: khuyến mãi X không có thao tác bật lại

### AC-9: Không giới hạn số lượng áp dụng
Given: khuyến mãi X giảm 10% đang hiệu lực cho sản phẩm A
When: khách đặt nhiều đơn liên tiếp có sản phẩm A
Then: mọi đơn đều được tính giá sau giảm của khuyến mãi X cho đến khi Nhân viên kết thúc chương trình

### AC-10: Làm tròn giá sau giảm
Given: sản phẩm A size S giá 199.999đ, khuyến mãi giảm 15%
When: hệ thống tính giá sau giảm
Then: giá sau giảm = 169.999đ (169.999,15 làm tròn `ROUND_HALF_UP`)

## Dependencies
- **Upstream UC:** UC-02, UC-14, UC-16
- **Downstream UC:** UC-12, UC-31, UC-37
- **External Systems:** không có

## Notes
- Theo BR: khuyến mãi theo sản phẩm giảm trực tiếp trên giá sản phẩm và hiển thị trên trang chi tiết sản phẩm; được tính cùng với mức giảm được chọn giữa khuyến mãi hóa đơn và voucher (UC-31).
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách khuyến mãi.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Khuyến mãi theo sản phẩm chỉ có tạo rồi kết thúc: không có ngày bắt đầu, ngày kết thúc; có hiệu lực ngay khi tạo, hết hiệu lực khi Nhân viên bấm kết thúc chương trình (đã chốt 20/11/2026, data model v2, Q29).
- Khuyến mãi có loại (PRODUCT), trạng thái bật / tắt; kết thúc chương trình chuyển trạng thái sang tắt (đã chốt 20/11/2026, data model v2, Q7).
- Trạng thái hiển thị của loại này: "Đang hiệu lực" hoặc "Đã kết thúc"; không có "Sắp diễn ra" (đã chốt 20/11/2026, data model v2, Q27, Q29).
- Khuyến mãi theo sản phẩm không áp dụng số lượng được áp dụng (promotion_quantity), không giới hạn số lượng; có hiệu lực cho đến khi Nhân viên bấm kết thúc chương trình (đã chốt 15/11/2026).
- Mỗi khuyến mãi theo sản phẩm gắn đúng một sản phẩm; muốn giảm cho nhiều sản phẩm thì tạo nhiều khuyến mãi (đã chốt 20/11/2026, theo ERD: `product_promotion` có khóa ngoại tới `product`; data model v2, Q2).
- Mỗi sản phẩm thuộc tối đa một khuyến mãi theo sản phẩm chưa kết thúc; sản phẩm có thể có nhiều khuyến mãi theo thời gian; khuyến mãi áp cho mọi biến thể của sản phẩm.
- Khuyến mãi đã tạo thì không được sửa; chỉ có thể ngừng (kết thúc chương trình) để các đơn sau không được áp nữa; đơn đã tạo không đổi (đã chốt 15/11/2026).
- Khuyến mãi đã kết thúc không bật lại được; muốn áp lại thì tạo khuyến mãi mới (đã chốt 20/11/2026, data model v2, Q22).
- Khi tạo khuyến mãi, hệ thống hiển thị popup xác nhận; chỉ lưu khi Nhân viên bấm xác nhận (đã chốt 15/11/2026).
- Khuyến mãi không có tên, nhận diện bằng mã khuyến mãi `KM-<4 số>` (đã chốt 20/11/2026, data model v2, Q21).
- Danh sách khuyến mãi theo sản phẩm không lọc theo khoảng thời gian, vì loại này không có ngày bắt đầu / kết thúc và hệ thống không lưu thời điểm tạo / kết thúc (đã chốt 20/11/2026, data model v2, Q30; thay quyết định lọc theo thời gian ngày 15/11/2026).

**Giả định [GD]**
- Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, không giới hạn số lượng, hiệu lực đến khi Nhân viên kết thúc chương trình, mỗi sản phẩm tối đa 1 khuyến mãi (theo ERD)
- v3 (2026-11-15): bỏ thao tác sửa khuyến mãi (chỉ kết thúc); thêm popup xác nhận khi tạo
- v4 (2026-11-15): bỏ tên khuyến mãi; thêm lọc danh sách theo khoảng thời gian (1c, AC-11)
- v5 (2026-11-15): chốt quy tắc lọc theo thời gian (giao khoảng; chưa kết thúc tính đến hiện tại)
- v6 (2026-11-20): theo data model v2 — mỗi khuyến mãi gắn đúng 1 sản phẩm (bỏ giả định nhiều sản phẩm); khuyến mãi đã kết thúc không bật lại được (thêm vào 1a, Postconditions, AC-8)
- v7 (2026-11-20): theo data model v2 — bỏ ngày bắt đầu / ngày kết thúc, khuyến mãi có hiệu lực ngay khi tạo (bước 2, 4, 6, 7; E1; AC-1, AC-2, AC-5, AC-7); thay AC-4 bằng "Có hiệu lực ngay khi tạo"; trạng thái chỉ còn Đang hiệu lực / Đã kết thúc (1b); lọc theo thời điểm tạo → kết thúc (1c, AC-11)
- v8 (2026-11-20): theo data model v2, Q30 — bỏ lọc theo khoảng thời gian (xóa 1c, AC-11); không ghi thời điểm kết thúc (1a)
