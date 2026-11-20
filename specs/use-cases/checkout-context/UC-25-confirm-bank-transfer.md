# UC-25: Tự đối soát chuyển khoản qua webhook SePay

## Metadata
- **ID:** UC-25
- **Bounded Context:** checkout-context
- **Liên quan tới BR:** BR-006, BR-003
- **Status:** draft

## Actor
SePay (dịch vụ theo dõi biến động số dư, gửi webhook về website). Không có người bấm xác nhận.

## Trigger
Tài khoản ngân hàng của cửa hàng nhận một khoản tiền; SePay gửi webhook về địa chỉ nhận webhook của website.

## Preconditions
- Tài khoản ngân hàng của cửa hàng đã liên kết với SePay; SePay đã cấu hình URL webhook trỏ về website (giai đoạn demo: địa chỉ ngrok) và API key.
- Cấu hình nhận diện mã thanh toán trên SePay dùng tiền tố `SOBIE` và phần mã 8 ký tự.
- API key webhook được nạp từ biến môi trường của website.

## Main Flow
1. SePay gửi webhook gồm: mã giao dịch của SePay, ngân hàng, số tài khoản nhận, số tiền vào, nội dung chuyển khoản, mã tham chiếu, thời điểm giao dịch.
2. Hệ thống kiểm tra API key trong request khớp với API key cấu hình.
3. Hệ thống kiểm tra mã giao dịch SePay chưa từng được xử lý.
4. Hệ thống tìm trong nội dung chuyển khoản chuỗi `SOBIE` + 8 ký tự Crockford Base32 và lấy ra mã đơn `[GD]`.
5. Trong cùng một database transaction, hệ thống:
   1. Tìm đơn có mã đơn đó, khóa dòng đơn để chống cập nhật song song.
   2. Kiểm tra đơn là đơn chuyển khoản QR, đang "Chưa xử lý", "Chưa thanh toán", chưa quá hạn 24 giờ, và số tiền vào ≥ tổng thanh toán của đơn.
   3. Chuyển trạng thái thanh toán của đơn sang "Đã thanh toán".
   4. Lưu giao dịch với kết quả "Khớp", gắn với đơn.
6. Hệ thống trả kết quả thành công cho SePay.
7. Khách mở chi tiết đơn (UC-21) thấy "Đã thanh toán", mã QR không còn hiển thị. Nhân viên có thể xác nhận đơn (UC-23).

## Alternative Flows
- **5a. Chuyển thừa tiền:** số tiền vào > tổng thanh toán → vẫn khớp, đơn chuyển "Đã thanh toán"; phần thừa xử lý ngoài hệ thống.
- **5b. Chuyển lại sau một lần không khớp:** khách đã chuyển thiếu hoặc sai nội dung trước đó, sau đó chuyển một giao dịch mới đúng mã đơn và đủ tiền khi đơn vẫn "Chưa xử lý", "Chưa thanh toán", còn hạn → giao dịch mới khớp, đơn chuyển "Đã thanh toán". Các giao dịch trước không được cộng dồn.

## Exceptions
- **E1. Sai hoặc thiếu API key:** hệ thống từ chối request, không lưu giao dịch, không đổi đơn.
- **E2. Webhook gửi trùng:** mã giao dịch SePay đã được xử lý → hệ thống không thay đổi gì và trả thành công để SePay không gửi lại.
- **E3. Không khớp được đơn:** nội dung không có mã đơn, mã đơn không tồn tại, đơn không phải đơn QR, đơn đã thanh toán, đã hủy hoặc quá hạn, hoặc số tiền vào < tổng thanh toán → đơn giữ nguyên; giao dịch được lưu với kết quả "Không khớp"; hệ thống vẫn trả thành công cho SePay. Khách chủ động liên hệ cửa hàng để giải quyết khoản tiền này (ngoài hệ thống).
- **E4. Webhook đến cùng lúc với tác vụ tự hủy (UC-24):** khóa dòng đơn ở bước 5.1 bảo đảm chỉ một bên thắng. Nếu UC-24 hủy trước, giao dịch thành "Không khớp" (xử lý như E3).

## Postconditions
- Mỗi webhook hợp lệ tạo đúng 1 bản ghi giao dịch (khớp hoặc không khớp).
- Đơn khớp ở trạng thái thanh toán "Đã thanh toán"; trạng thái đơn vẫn "Chưa xử lý" chờ Nhân viên xác nhận (UC-23).
- Lịch sử trạng thái đơn không có dòng mới (thay đổi trạng thái thanh toán không ghi lịch sử).

## Acceptance Criteria

### AC-1: Chuyển khoản đúng
Given: đơn QR mã 7K3M9Q2X "Chưa xử lý", "Chưa thanh toán", tổng 14.000đ, còn hạn
When: SePay gửi webhook số tiền 14.000đ, nội dung "SOBIE7K3M9Q2X", API key đúng
Then: đơn 7K3M9Q2X có trạng thái thanh toán "Đã thanh toán"
And: trạng thái đơn vẫn "Chưa xử lý"
And: có 1 giao dịch "Khớp" gắn với đơn 7K3M9Q2X
And: lịch sử trạng thái đơn không có dòng mới

### AC-2: Chuyển thừa
Given: đơn QR 7K3M9Q2X "Chưa thanh toán", tổng 14.000đ
When: SePay gửi webhook 20.000đ, nội dung "SOBIE7K3M9Q2X"
Then: đơn chuyển "Đã thanh toán"

### AC-3: Chuyển thiếu
Given: đơn QR 7K3M9Q2X "Chưa thanh toán", tổng 14.000đ
When: SePay gửi webhook 10.000đ, nội dung "SOBIE7K3M9Q2X"
Then: đơn vẫn "Chưa thanh toán"
And: giao dịch được lưu với kết quả "Không khớp"

### AC-4: Không cộng dồn, chuyển lại đúng thì tự cập nhật
Given: đơn QR 7K3M9Q2X tổng 14.000đ đã nhận 1 giao dịch 10.000đ "Không khớp", đơn còn hạn
When: SePay gửi webhook giao dịch mới 4.000đ, nội dung "SOBIE7K3M9Q2X"
Then: đơn vẫn "Chưa thanh toán"
When: SePay gửi webhook giao dịch mới 14.000đ, nội dung "SOBIE7K3M9Q2X"
Then: đơn chuyển "Đã thanh toán"

### AC-5: Nội dung không có mã đơn
Given: có đơn QR 7K3M9Q2X "Chưa thanh toán"
When: SePay gửi webhook 14.000đ, nội dung "chuyen tien ao boi"
Then: không đơn nào đổi trạng thái thanh toán
And: giao dịch được lưu với kết quả "Không khớp", không gắn đơn

### AC-6: Đơn đã hủy hoặc quá hạn
Given: đơn QR 7K3M9Q2X đã "Đã hủy" (tự hủy quá hạn hoặc bị hủy)
When: SePay gửi webhook 14.000đ, nội dung "SOBIE7K3M9Q2X"
Then: đơn vẫn "Đã hủy" và "Chưa thanh toán"
And: giao dịch được lưu với kết quả "Không khớp"

### AC-7: Webhook gửi trùng
Given: giao dịch SePay mã 92704 đã được xử lý và đơn 7K3M9Q2X đã "Đã thanh toán"
When: SePay gửi lại webhook mã 92704
Then: không có giao dịch mới được lưu, dữ liệu không đổi, hệ thống trả thành công

### AC-8: Sai API key
Given: đơn QR 7K3M9Q2X "Chưa thanh toán"
When: một request webhook gửi tới với API key sai
Then: hệ thống từ chối request
And: không lưu giao dịch và đơn vẫn "Chưa thanh toán"

### AC-9: Demo với sản phẩm 2.000đ
Given: sản phẩm demo giá 2.000đ, phí vận chuyển 12.000đ (biến môi trường), khách đặt 1 sản phẩm demo bằng QR
When: người demo quét mã QR bằng app ngân hàng và chuyển 14.000đ với nội dung điền sẵn
Then: sau khi SePay gửi webhook, khách mở lại chi tiết đơn thấy "Đã thanh toán" mà không ai bấm xác nhận

## Dependencies
- **Upstream UC:** UC-20 Đặt hàng thanh toán chuyển khoản QR
- **Downstream UC:** UC-23 Xác nhận đơn hàng, UC-24 Tự hủy đơn chuyển khoản quá hạn, UC-21 Theo dõi đơn hàng
- **External Systems:** SePay (webhook biến động số dư); ngrok (giai đoạn demo)

## Notes
- BR-GIAIDOAN1 (BR-006): mọi đơn chuyển khoản dùng chung 1 tài khoản ngân hàng; SePay gửi webhook, website tự đối soát; không còn trang giả lập xác nhận chuyển khoản.
- Endpoint webhook không yêu cầu đăng nhập người dùng; xác thực bằng API key (AGENTS.md: không hard-code secret).
- Webhook đi qua Route → Service → Repository; ghi giao dịch và cập nhật trạng thái thanh toán trong cùng một database transaction (AGENTS.md).

### Quyết định đã chốt
- Dùng SePay; giai đoạn demo dùng ngrok forward cổng local (đã chốt 20/11/2026).
- Nội dung chuyển khoản = `SOBIE` + mã đơn 8 ký tự Crockford Base32 (đã chốt 20/11/2026).
- Khớp khi đúng mã đơn và số tiền ≥ tổng thanh toán; chuyển thừa vẫn tính đã thanh toán; chuyển thiếu là không khớp; mỗi giao dịch xét riêng, không cộng dồn (đã chốt 20/11/2026).
- Không khớp: không cập nhật đơn; khách chủ động liên hệ cửa hàng; chuyển lại đúng thì tự cập nhật (đã chốt 20/11/2026).
- Thay đổi trạng thái thanh toán không ghi vào lịch sử trạng thái đơn (đã chốt 15/11/2026).

### Giả định [GD]
- Mã đơn được tìm trong nội dung chuyển khoản không phân biệt vị trí, không phân biệt hoa thường; ngân hàng có thể thêm chữ trước/sau nội dung.
- Mọi giao dịch nhận được đều được lưu (bảng `bank_transaction`); không có màn hình riêng cho Nhân viên xem giao dịch không khớp.
- Webhook không khớp vẫn trả thành công cho SePay để SePay không gửi lại.
- Dự phòng khi demo: công cụ gửi webhook mẫu đúng định dạng SePay, có API key, chỉ bật ở môi trường dev/demo.

## History
- v1 (2026-11-15): initial — trang giả lập xác nhận chuyển khoản
- v2 (2026-11-15): chốt trang giả lập không cần đăng nhập, 1 trang, chỉ bấm nút xác nhận (bỏ nhập và kiểm tra số tiền); thêm lưu lịch sử (theo ERD)
- v3 (2026-11-15): không ghi thay đổi trạng thái thanh toán vào lịch sử, không lưu thời điểm thanh toán (theo data model v1)
- v4 (2026-11-20): viết lại theo BR-GIAIDOAN1 — bỏ trang giả lập; tự đối soát qua webhook SePay, nội dung `SOBIE` + mã đơn, quy tắc khớp/không khớp, chống trùng, lưu giao dịch
