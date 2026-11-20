# UC-30: Quản lý voucher

## Metadata
- **ID:** UC-30
- **Module:** promotion
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý voucher để tạo hoặc ngừng một voucher.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên chọn "Tạo voucher".
2. Nhân viên nhập mã voucher, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng (số lượng được áp dụng), ngày bắt đầu và ngày kết thúc.
3. Hệ thống kiểm tra dữ liệu hợp lệ và mã chưa tồn tại.
4. Hệ thống hiển thị popup xác nhận tóm tắt voucher: mã, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng, thời gian hiệu lực, kèm lưu ý "Voucher đã tạo không thể sửa, chỉ có thể ngừng".
5. Nhân viên bấm "Xác nhận".
6. Hệ thống lưu voucher với loại CODE, số lượt đã dùng = 0.
7. Khách nhập mã voucher khi đặt hàng; voucher được xét trong UC-31 khi tạm tính ≥ giá trị đơn tối thiểu và còn lượt.

## Alternative Flows
- **5a. Hủy tại popup xác nhận:** Nhân viên bấm "Hủy" → hệ thống không lưu, quay lại màn hình nhập với dữ liệu đã nhập.
- **1a. Ngừng voucher (kết thúc trước hạn):** Nhân viên chọn một voucher chưa kết thúc và bấm "Ngừng" → voucher chuyển trạng thái tắt, hết hiệu lực ngay, khách nhập mã sẽ bị báo không hợp lệ `[GD]`; ngày kết thúc đã chọn khi tạo giữ nguyên; voucher không bật lại được; đơn đã tạo không thay đổi.
- **1b. Xem danh sách voucher:** Nhân viên xem danh sách voucher kèm tổng lượt dùng, số lượt đã dùng `[GD]` và trạng thái: "Sắp diễn ra" (chưa tới ngày bắt đầu), "Đang hiệu lực", "Đã kết thúc" (đã tới ngày kết thúc hoặc đã bị ngừng). Danh sách không có thao tác sửa.
- **1c. Lọc theo khoảng thời gian:** Nhân viên chọn "từ ngày" và "đến ngày" → hệ thống chỉ hiển thị các voucher có thời gian hiệu lực giao với khoảng đã chọn (kể cả giao một phần).
- **7a. Hết hạn:** tới ngày kết thúc → voucher tự hết hiệu lực, chuyển "Đã kết thúc", không cần Nhân viên thao tác.

## Exceptions
- **E1. Trùng mã:** mã voucher đã tồn tại (không phân biệt hoa thường `[GD]`) → hệ thống báo lỗi, không lưu.
- **E2. Thiếu hoặc sai dữ liệu:** thiếu mã, phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100 `[GD]`, giá trị đơn tối thiểu âm, tổng lượt dùng ≤ 0, hoặc ngày kết thúc không sau ngày bắt đầu → hệ thống báo lỗi theo từng trường, không hiển thị popup xác nhận, không lưu.

## Postconditions
- Voucher được lưu sau khi Nhân viên xác nhận và dùng được cho các đơn tạo trong thời gian hiệu lực, khi còn lượt và đạt giá trị đơn tối thiểu.
- Voucher đã tạo không thể sửa; chỉ có thể ngừng. Voucher đã ngừng không bật lại được.

## Acceptance Criteria

### AC-1: Tạo voucher hợp lệ
Given: Nhân viên đã đăng nhập, mã "SUMMER10" chưa tồn tại
When: Nhân viên tạo voucher "SUMMER10" giảm 10%, giá trị đơn tối thiểu 300.000đ, tổng lượt dùng 100, thời gian hiệu lực bao gồm hiện tại, rồi bấm "Xác nhận" ở popup
Then: voucher được lưu với số lượt đã dùng = 0

### AC-2: Popup xác nhận trước khi lưu
Given: Nhân viên đã nhập đủ dữ liệu hợp lệ cho voucher "SUMMER10"
When: Nhân viên bấm "Lưu"
Then: hệ thống hiển thị popup tóm tắt mã, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng, thời gian hiệu lực và lưu ý voucher không thể sửa
And: voucher chưa được lưu cho tới khi Nhân viên bấm "Xác nhận"

### AC-3: Hủy tại popup xác nhận
Given: popup xác nhận voucher "SUMMER10" đang hiển thị
When: Nhân viên bấm "Hủy"
Then: không có voucher "SUMMER10" nào được tạo

### AC-4: Trùng mã
Given: voucher "SUMMER10" đã tồn tại
When: Nhân viên tạo voucher mới với mã "summer10"
Then: hệ thống báo lỗi trùng mã
And: không có voucher mới được tạo

### AC-5: Dữ liệu không hợp lệ
Given: Nhân viên ở màn hình tạo voucher
When: Nhân viên lưu với tổng lượt dùng = 0, phần trăm giảm 0%, giá trị đơn tối thiểu âm, hoặc ngày kết thúc trước ngày bắt đầu
Then: hệ thống báo lỗi tại trường tương ứng
And: không hiển thị popup xác nhận và không lưu

### AC-6: Không có thao tác sửa
Given: voucher "SUMMER10" đã được tạo
When: Nhân viên mở danh sách hoặc chi tiết voucher "SUMMER10"
Then: không có thao tác sửa mã, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng hay thời gian
And: chỉ có thao tác "Ngừng" nếu voucher chưa kết thúc

### AC-7: Ngừng voucher
Given: voucher "SUMMER10" đang hiệu lực, đơn D đã được tạo với "SUMMER10"
When: Nhân viên ngừng voucher, sau đó khách nhập "SUMMER10" khi đặt hàng
Then: hệ thống báo voucher không hợp lệ
And: số tiền giảm của đơn D giữ nguyên
And: voucher "SUMMER10" hiển thị "Đã kết thúc", ngày kết thúc vẫn là ngày đã chọn khi tạo
And: voucher "SUMMER10" không có thao tác bật lại

### AC-8: Một khách dùng nhiều lần
Given: voucher "SUMMER10" còn lượt, khách K đã dùng "SUMMER10" ở một đơn trước
When: khách K đặt đơn mới với "SUMMER10" và tạm tính đạt giá trị đơn tối thiểu
Then: voucher vẫn được xét cho đơn mới
And: chỉ tổng lượt dùng bị giới hạn

### AC-9: Lọc theo khoảng thời gian
Given: voucher "A1" hiệu lực 01/11 → 10/11, voucher "B2" hiệu lực 20/11 → 30/11, voucher "C3" hiệu lực 05/12 → 31/12
When: Nhân viên lọc danh sách từ 05/11 đến 25/11
Then: danh sách hiển thị "A1" và "B2"
And: không hiển thị "C3"

### AC-10: Trạng thái hiển thị
Given: hôm nay 20/11; voucher "P1" hiệu lực 25/11 → 30/11, "Q1" hiệu lực 15/11 → 25/11, "R1" hiệu lực 01/11 → 10/11
When: Nhân viên mở danh sách voucher, sau đó khách nhập "P1" khi đặt hàng hôm nay
Then: "P1" hiển thị "Sắp diễn ra", "Q1" hiển thị "Đang hiệu lực", "R1" hiển thị "Đã kết thúc"
And: hệ thống báo "P1" chưa đến thời gian hiệu lực (UC-31 E2)

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-31, UC-37
- **External Systems:** không có

## Notes
- Lượt dùng được trừ và hoàn theo quy tắc ở UC-31.
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung) cho danh sách voucher.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Voucher (loại CODE) có: mã duy nhất, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng (số lượng được áp dụng), số lượt đã dùng, ngày bắt đầu, ngày kết thúc, trạng thái (theo ERD).
- Voucher chỉ giới hạn tổng lượt dùng; không giới hạn số lần mỗi khách (đã chốt 15/11/2026).
- Voucher đã tạo thì không được sửa (kể cả mã, phần trăm, giá trị đơn tối thiểu, tổng lượt dùng, thời gian); chỉ có thể ngừng để các đơn sau không được áp nữa; đơn đã tạo không đổi (đã chốt 15/11/2026).
- Hết hiệu lực theo 2 cách: tới ngày kết thúc, hoặc Nhân viên ngừng trước hạn; ngừng trước hạn chỉ đổi trạng thái sang tắt, ngày kết thúc giữ nguyên (đã chốt 20/11/2026, data model v2, Q25, Q28).
- Voucher đã ngừng không bật lại được; muốn áp lại thì tạo voucher mới (đã chốt 20/11/2026, data model v2, Q22).
- Trạng thái hiển thị: Sắp diễn ra, Đang hiệu lực, Đã kết thúc — tính từ trạng thái bật / tắt và ngày bắt đầu / kết thúc, không lưu riêng (đã chốt 20/11/2026, data model v2, Q23c, Q27).
- Khi tạo voucher, hệ thống hiển thị popup xác nhận; chỉ lưu khi Nhân viên bấm xác nhận (đã chốt 15/11/2026).
- Danh sách voucher lọc được theo khoảng thời gian để Nhân viên tra cứu (đã chốt 15/11/2026).
- Lọc theo khoảng thời gian: hiển thị voucher có thời gian hiệu lực giao với khoảng đã chọn, kể cả giao một phần (đã chốt 15/11/2026).

**Giả định [GD]**
- Mã voucher không phân biệt hoa thường.
- Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100.
- Danh sách voucher hiển thị tổng lượt dùng và số lượt đã dùng.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, thêm giá trị đơn tối thiểu, chốt chỉ giới hạn tổng lượt dùng (theo ERD)
- v3 (2026-11-15): bỏ thao tác sửa voucher (chỉ ngừng); thêm popup xác nhận khi tạo
- v4 (2026-11-15): thêm lọc danh sách theo khoảng thời gian (1c, AC-9)
- v5 (2026-11-15): chốt quy tắc lọc theo thời gian (giao khoảng)
- v6 (2026-11-20): theo data model v2 — ngừng trước hạn giữ ngày kết thúc, không bật lại (1a, AC-7); thêm 7a hết hạn; chốt trạng thái Sắp diễn ra / Đang hiệu lực / Đã kết thúc (1b, AC-10)
