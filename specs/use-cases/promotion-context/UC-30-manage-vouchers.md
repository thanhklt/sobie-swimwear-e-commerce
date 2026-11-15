# UC-30: Quản lý voucher

## Metadata
- **ID:** UC-30
- **Bounded Context:** promotion-context
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý voucher để tạo, sửa hoặc ngừng một voucher.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên chọn "Tạo voucher".
2. Nhân viên nhập mã voucher, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng (số lượng được áp dụng), ngày bắt đầu và ngày kết thúc.
3. Hệ thống kiểm tra dữ liệu hợp lệ và mã chưa tồn tại.
4. Hệ thống lưu voucher với loại CODE, số lượt đã dùng = 0.
5. Khách nhập mã voucher khi đặt hàng; voucher được xét trong UC-31 khi tạm tính ≥ giá trị đơn tối thiểu và còn lượt.

## Alternative Flows
- **1a. Sửa voucher:** Nhân viên sửa phần trăm giảm, giá trị đơn tối thiểu, thời gian hoặc tổng lượt dùng; không sửa được mã `[GD]`. Tổng lượt dùng mới không được nhỏ hơn số lượt đã dùng `[GD]`.
- **1b. Ngừng voucher:** voucher hết hiệu lực ngay, khách nhập mã sẽ bị báo không hợp lệ `[GD]`.
- **1c. Xem danh sách voucher:** Nhân viên xem danh sách voucher kèm tổng lượt dùng, số lượt đã dùng và trạng thái `[GD]`.

## Exceptions
- **E1. Trùng mã:** mã voucher đã tồn tại (không phân biệt hoa thường `[GD]`) → hệ thống báo lỗi, không lưu.
- **E2. Thiếu hoặc sai dữ liệu:** thiếu mã, phần trăm giảm không nằm trong khoảng lớn hơn 0 và nhỏ hơn 100 `[GD]`, giá trị đơn tối thiểu âm, tổng lượt dùng ≤ 0, hoặc ngày kết thúc không sau ngày bắt đầu → hệ thống báo lỗi theo từng trường, không lưu.
- **E3. Giảm tổng lượt dùng dưới số lượt đã dùng:** → hệ thống báo lỗi, không lưu.

## Postconditions
- Voucher được lưu và dùng được cho các đơn tạo trong thời gian hiệu lực, khi còn lượt và đạt giá trị đơn tối thiểu.

## Acceptance Criteria

### AC-1: Tạo voucher hợp lệ
Given: Nhân viên đã đăng nhập, mã "SUMMER10" chưa tồn tại
When: Nhân viên tạo voucher "SUMMER10" giảm 10%, giá trị đơn tối thiểu 300.000đ, tổng lượt dùng 100, thời gian hiệu lực bao gồm hiện tại
Then: voucher được lưu với số lượt đã dùng = 0

### AC-2: Trùng mã
Given: voucher "SUMMER10" đã tồn tại
When: Nhân viên tạo voucher mới với mã "summer10"
Then: hệ thống báo lỗi trùng mã
And: không có voucher mới được tạo

### AC-3: Dữ liệu không hợp lệ
Given: Nhân viên ở màn hình tạo voucher
When: Nhân viên lưu với tổng lượt dùng = 0, phần trăm giảm 0%, giá trị đơn tối thiểu âm, hoặc ngày kết thúc trước ngày bắt đầu
Then: hệ thống báo lỗi tại trường tương ứng, không lưu

### AC-4: Giảm tổng lượt dùng dưới số đã dùng
Given: voucher "SUMMER10" đã dùng 30 lượt
When: Nhân viên sửa tổng lượt dùng thành 20
Then: hệ thống báo lỗi, tổng lượt dùng giữ nguyên

### AC-5: Ngừng voucher
Given: voucher "SUMMER10" đang hiệu lực
When: Nhân viên ngừng voucher, sau đó khách nhập "SUMMER10" khi đặt hàng
Then: hệ thống báo voucher không hợp lệ

### AC-6: Một khách dùng nhiều lần
Given: voucher "SUMMER10" còn lượt, khách K đã dùng "SUMMER10" ở một đơn trước
When: khách K đặt đơn mới với "SUMMER10" và tạm tính đạt giá trị đơn tối thiểu
Then: voucher vẫn được xét cho đơn mới
And: chỉ tổng lượt dùng bị giới hạn

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-31, UC-37
- **External Systems:** không có

## Notes
- Lượt dùng được trừ và hoàn theo quy tắc ở UC-31.
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung) cho danh sách voucher.

**Quyết định đã chốt**
- Giảm theo phần trăm; không có mức giảm tối đa; tiền làm tròn `ROUND_HALF_UP` về số nguyên VND (đã chốt 15/11/2026, theo ERD).
- Voucher (loại CODE) có: mã duy nhất, phần trăm giảm, giá trị đơn tối thiểu, tổng lượt dùng (số lượng được áp dụng), số lượt đã dùng, ngày bắt đầu, ngày kết thúc, trạng thái (theo ERD).
- Voucher chỉ giới hạn tổng lượt dùng; không giới hạn số lần mỗi khách (đã chốt 15/11/2026).

**Giả định [GD]**
- Mã voucher không phân biệt hoa thường và không sửa được sau khi tạo.
- Tổng lượt dùng mới không được nhỏ hơn số lượt đã dùng.
- Có thao tác ngừng voucher.
- Phần trăm giảm hợp lệ: lớn hơn 0 và nhỏ hơn 100.
- Danh sách voucher hiển thị tổng lượt dùng, số lượt đã dùng và trạng thái.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): giảm theo phần trăm, thêm giá trị đơn tối thiểu, chốt chỉ giới hạn tổng lượt dùng (theo ERD)
