# UC-31: Tính mức giảm cho đơn hàng

## Metadata
- **ID:** UC-31
- **Module:** promotion
- **Liên quan tới BR:** BR-004
- **Status:** draft

## Actor
- Hệ thống (tính mức giảm)
- Khách hàng (nhập mã voucher ở bước đặt hàng)

## Trigger
Khách hàng mở bước đặt hàng, nhập hoặc bỏ mã voucher, hoặc xác nhận đặt hàng (UC-19, UC-20).

## Preconditions
- Khách hàng đã đăng nhập và giỏ hàng có ít nhất một sản phẩm.

## Main Flow
1. Hệ thống tính giá từng dòng: nếu sản phẩm thuộc khuyến mãi theo sản phẩm đang hiệu lực (UC-28) thì dùng giá sau giảm = giá bán theo size × (100% − phần trăm giảm), làm tròn `ROUND_HALF_UP`; ngược lại dùng giá bán theo size. Khuyến mãi theo sản phẩm được ghi theo từng dòng đơn.
2. Hệ thống tính tạm tính = tổng (giá dòng × số lượng).
3. Hệ thống tìm các khuyến mãi theo hóa đơn (UC-29) đang hiệu lực, còn lượt, và tạm tính ≥ giá trị đơn tối thiểu; mức giảm = tạm tính × phần trăm giảm, làm tròn `ROUND_HALF_UP`; lấy mức giảm lớn nhất `[GD]`.
4. Nếu khách đã nhập mã voucher, hệ thống kiểm tra voucher (UC-30): tồn tại, đang hiệu lực, còn lượt, tạm tính ≥ giá trị đơn tối thiểu; mức giảm = tạm tính × phần trăm giảm, làm tròn `ROUND_HALF_UP`.
5. Hệ thống chọn **một** trong hai: khuyến mãi theo hóa đơn hoặc voucher, cái nào giảm nhiều hơn cho khách. Mỗi đơn áp tối đa một khuyến mãi loại này.
6. Hệ thống hiển thị: tạm tính (đã gồm khuyến mãi theo sản phẩm), mức giảm được chọn và nguồn của nó, phí vận chuyển cố định, tổng thanh toán.
7. Khi khách xác nhận đặt hàng, hệ thống tính lại toàn bộ bước 1–5; khuyến mãi được chọn (khuyến mãi theo hóa đơn hoặc voucher) tăng số lượng đã dùng thêm 1, trong cùng transaction với việc tạo đơn.

## Alternative Flows
- **3a. Không có khuyến mãi theo hóa đơn đủ điều kiện và không nhập voucher:** mức giảm = 0.
- **5a. Voucher hợp lệ nhưng khuyến mãi theo hóa đơn có lợi hơn:** hệ thống chọn khuyến mãi theo hóa đơn, thông báo cho khách lý do voucher không được áp; voucher không bị trừ lượt.
- **5b. Hai mức giảm bằng nhau:** ưu tiên voucher (đã chốt 15/11/2026).
- **7a. Đơn bị hủy (khách hủy, Nhân viên hủy hoặc hệ thống tự hủy):** lượt voucher và lượt khuyến mãi theo hóa đơn đã trừ được hoàn lại.

## Exceptions
- **E1. Voucher không tồn tại hoặc đã ngừng:** hệ thống báo "Voucher không hợp lệ", tính tiếp như chưa nhập voucher.
- **E2. Voucher hết hạn hoặc chưa đến thời gian hiệu lực:** hệ thống báo lỗi tương ứng, tính tiếp như chưa nhập voucher.
- **E3. Voucher hết lượt:** hệ thống báo "Voucher đã hết lượt sử dụng", tính tiếp như chưa nhập voucher.
- **E4. Chưa đạt giá trị đơn tối thiểu của voucher:** hệ thống báo số tiền tối thiểu cần đạt, tính tiếp như chưa nhập voucher.
- **E5. Khuyến mãi hoặc voucher thay đổi giữa lúc xem và lúc xác nhận:** tính lại ở bước 7 khác lần hiển thị trước về **mức giảm hoặc nguồn mức giảm** (kể cả khi số tiền giảm không đổi, ví dụ hết lượt voucher nhưng khuyến mãi hóa đơn vẫn giảm cùng số tiền) → hệ thống không tạo đơn, hiển thị kết quả mới để khách xác nhận lại.

## Postconditions
- Đơn được tạo với tạm tính, mức giảm được chọn, nguồn mức giảm (một khuyến mãi theo hóa đơn, một voucher hoặc không có), phí vận chuyển và tổng thanh toán; mỗi dòng đơn ghi khuyến mãi theo sản phẩm nếu có.
- Khuyến mãi được chọn (khuyến mãi theo hóa đơn hoặc voucher) tăng số lượng đã dùng thêm 1.

## Acceptance Criteria

### AC-1: Khuyến mãi theo sản phẩm được tính vào tạm tính
Given: sản phẩm A size M giá 300.000đ, đang thuộc khuyến mãi theo sản phẩm giảm 10%
When: khách đặt 2 sản phẩm A size M
Then: giá dòng = 270.000đ, tạm tính = 540.000đ

### AC-2: Chọn voucher khi voucher giảm nhiều hơn
Given: tạm tính 500.000đ, khuyến mãi theo hóa đơn đủ điều kiện giảm 6% (30.000đ), voucher hợp lệ giảm 10% (50.000đ)
When: khách nhập voucher
Then: mức giảm được chọn = 50.000đ, nguồn là voucher
And: tổng thanh toán = 500.000 − 50.000 + phí vận chuyển cố định

### AC-3: Chọn khuyến mãi theo hóa đơn khi có lợi hơn
Given: tạm tính 500.000đ, khuyến mãi theo hóa đơn giảm 10% (50.000đ), voucher hợp lệ giảm 6% (30.000đ)
When: khách nhập voucher và đặt hàng
Then: mức giảm được chọn = 50.000đ, nguồn là khuyến mãi theo hóa đơn
And: khách thấy thông báo voucher không được áp
And: số lượt đã dùng của voucher không đổi

### AC-4: Hai mức giảm bằng nhau
Given: tạm tính 500.000đ, khuyến mãi theo hóa đơn và voucher cùng giảm 8% (40.000đ)
When: khách đặt hàng với voucher
Then: nguồn mức giảm là voucher
And: voucher bị trừ 1 lượt khi đơn được tạo

### AC-5: Khuyến mãi theo sản phẩm cộng với mức giảm được chọn
Given: sản phẩm A thuộc khuyến mãi theo sản phẩm, đơn đủ điều kiện một khuyến mãi theo hóa đơn
When: khách đặt hàng
Then: giá dòng dùng giá sau giảm của sản phẩm
And: mức giảm theo hóa đơn vẫn được tính trên tạm tính đó

### AC-6: Voucher hết lượt
Given: voucher "SUMMER10" có tổng lượt 100 và đã dùng 100
When: khách nhập "SUMMER10"
Then: hệ thống báo "Voucher đã hết lượt sử dụng"
And: mức giảm được tính như chưa nhập voucher

### AC-7: Voucher không hợp lệ hoặc hết hạn
Given: mã "ABC" không tồn tại, voucher "OLD" đã hết hạn
When: khách nhập lần lượt "ABC" và "OLD"
Then: hệ thống báo lỗi tương ứng cho từng mã, không áp mức giảm của voucher

### AC-8: Chưa đạt giá trị đơn tối thiểu của voucher
Given: voucher "SUMMER10" có giá trị đơn tối thiểu 300.000đ, tạm tính 250.000đ
When: khách nhập "SUMMER10"
Then: hệ thống báo cần đạt tối thiểu 300.000đ
And: mức giảm được tính như chưa nhập voucher

### AC-9: Trừ lượt khi đặt hàng
Given: voucher "SUMMER10" đã dùng 10 lượt và được chọn cho đơn
When: khách xác nhận đặt hàng thành công
Then: số lượt đã dùng = 11
And: đơn lưu nguồn mức giảm là voucher "SUMMER10"

### AC-10: Hết lượt ngay lúc xác nhận
Given: voucher "SUMMER10" còn 1 lượt; khuyến mãi theo hóa đơn đủ điều kiện cũng giảm đúng 40.000đ trên cùng tạm tính; hai khách cùng xác nhận đặt hàng với voucher này (lần hiển thị trước đều chọn nguồn voucher, mức giảm 40.000đ)
When: hai yêu cầu được xử lý đồng thời
Then: chỉ một đơn được áp voucher, số lượt đã dùng không vượt tổng lượt
And: khách còn lại nhận kết quả tính lại: mức giảm vẫn 40.000đ nhưng nguồn là khuyến mãi theo hóa đơn
And: hệ thống không tạo đơn cho khách còn lại cho tới khi khách xác nhận lại với nguồn mới (E5)

### AC-11: Hoàn lượt khi đơn bị hủy
Given: đơn D1 dùng voucher "SUMMER10" (đã dùng = 11); đơn D2 dùng khuyến mãi theo hóa đơn H (đã dùng = 5)
When: D1 và D2 chuyển sang "Đã hủy" (khách hủy, Nhân viên hủy hoặc hệ thống tự hủy)
Then: "SUMMER10" còn 10 lượt đã dùng
And: H còn 4 lượt đã dùng

### AC-12: Khuyến mãi theo hóa đơn hết lượt không được xét
Given: khuyến mãi theo hóa đơn X đã dùng hết số lượng được áp dụng, tạm tính đạt giá trị đơn tối thiểu của X
When: hệ thống tính mức giảm
Then: X không được xét
And: nguồn mức giảm không phải X

## Dependencies
- **Upstream UC:** UC-18, UC-28, UC-29, UC-30
- **Downstream UC:** UC-19, UC-20, UC-22, UC-23, UC-24, UC-37
- **External Systems:** không có

## Notes
- Theo BR: hệ thống tự chọn mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher; khuyến mãi theo sản phẩm được tính cùng mức giảm được chọn đó.
- Kiểm tra và trừ lượt khuyến mãi/voucher chạy trong cùng transaction với tạo đơn và trừ tồn kho (AGENTS.md, mục Toàn vẹn Transaction).
- Tiền tính bằng số nguyên VND, làm tròn `ROUND_HALF_UP`.

**Quyết định đã chốt**
- Hai mức giảm (khuyến mãi theo hóa đơn và voucher) bằng nhau thì ưu tiên voucher (đã chốt 15/11/2026).
- Đơn bị hủy (khách hủy, Nhân viên hủy hoặc hệ thống tự hủy) thì cộng lại tồn kho và hoàn lượt của khuyến mãi đã áp — cả voucher lẫn khuyến mãi theo hóa đơn (`promotion_used_amount`) (đã chốt 15/11/2026; xác nhận lại 23/11/2026 theo data model v2).
- Khi tính lại lúc xác nhận, nếu mức giảm **hoặc nguồn mức giảm** khác lần hiển thị trước thì không tạo đơn, yêu cầu khách xác nhận lại — kể cả khi số tiền giảm không đổi (đã chốt 24/11/2026).
- Mọi loại khuyến mãi giảm theo phần trăm; không có mức giảm tối đa (đã chốt 15/11/2026, theo ERD).
- Mỗi đơn áp tối đa một khuyến mãi theo hóa đơn hoặc voucher; khuyến mãi theo sản phẩm ghi theo từng dòng đơn (theo ERD).
- Khuyến mãi theo hóa đơn và voucher chỉ hợp lệ khi tạm tính ≥ giá trị đơn tối thiểu và còn lượt (số lượng đã dùng < số lượng được áp dụng); voucher không giới hạn số lần mỗi khách (đã chốt 15/11/2026, theo ERD).
- Khuyến mãi đã tạo không được sửa, chỉ có thể ngừng (đã chốt 15/11/2026). Vì vậy mỗi dòng đơn chỉ lưu đơn giá gốc theo size (`order_detail_unit_price`) và khuyến mãi theo sản phẩm đã áp (`order_detail_product_promotion_id`); đơn giá sau giảm = đơn giá gốc × (100% − phần trăm của khuyến mãi đó), làm tròn `ROUND_HALF_UP`, luôn ổn định sau khi đặt (theo data model v1).

**Giả định [GD]**
- Có nhiều khuyến mãi theo hóa đơn đủ điều kiện thì lấy mức giảm lớn nhất.
- Mức giảm theo hóa đơn hoặc voucher tính trên tạm tính (đã gồm khuyến mãi theo sản phẩm), không áp vào phí vận chuyển, và không vượt quá tạm tính.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt ưu tiên voucher khi hai mức giảm bằng nhau, hoàn lượt voucher khi hủy/từ chối
- v3 (2026-11-15): giảm theo phần trăm, giá trị đơn tối thiểu cho voucher, lượt áp dụng cho khuyến mãi theo hóa đơn, mỗi đơn tối đa một khuyến mãi (theo ERD)
- v4 (2026-11-15): ghi rõ dòng đơn lưu đơn giá gốc và khuyến mãi theo sản phẩm; đơn giá sau giảm ổn định vì khuyến mãi không sửa được (theo data model v1)
- v5 (2026-11-20): đồng bộ BR-GIAIDOAN1 — bỏ "Bị từ chối"; hủy đơn gồm cả Nhân viên hủy
- v6 (2026-11-23): xác nhận hoàn lượt khuyến mãi theo hóa đơn khi hủy đơn theo data model v2; bỏ quy tắc này khỏi mục giả định
- v7 (2026-11-24): làm rõ E5/AC-10 khi chỉ đổi nguồn giảm (số tiền không đổi); bổ sung ca ORDER vào AC-11; chốt yêu cầu xác nhận lại khi đổi nguồn
