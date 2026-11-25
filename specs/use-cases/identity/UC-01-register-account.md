# UC-01: Đăng ký tài khoản

## Metadata
- **ID:** UC-01
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Khách vãng lai

## Trigger
Khách vãng lai bấm "Đăng ký" trên website.

## Preconditions
- Khách vãng lai chưa đăng nhập.

## Main Flow
1. Khách vãng lai mở trang đăng ký.
2. Khách nhập email. Hệ thống kiểm tra định dạng và kiểm tra email chưa được tài khoản nào sử dụng trước khi gửi mã.
3. Hệ thống gửi mã OTP đến email đã nhập. Mã có hiệu lực trong 5 phút kể từ lúc gửi.
4. Khách nhập mã nhận được. Hệ thống xác minh mã thuộc email đang đăng ký và còn hiệu lực.
5. Sau khi xác minh OTP thành công, hệ thống chuyển khách đến màn hình tạo mật khẩu. Khách nhập mật khẩu mới và nhập lại mật khẩu để xác nhận.
6. Hệ thống kiểm tra mật khẩu hợp lệ và khớp với ô nhập lại.
7. Hệ thống băm mật khẩu bằng bcrypt và tạo tài khoản Khách hàng ở trạng thái Hoạt động với email đã xác minh và mã `KH-<YYYYMMDD ngày đăng ký>-<4 số>`. Hệ thống cấp mã, tạo tài khoản, giỏ hàng trống và danh sách yêu thích trống trong cùng một transaction.
8. Sau khi lưu tài khoản và mật khẩu thành công, hệ thống thông báo đăng ký thành công và chuyển khách đến màn hình đăng nhập.

## Alternative Flows
- **1a. Đang đăng nhập:** người dùng đã đăng nhập mở trang đăng ký thì hệ thống chuyển về trang chủ, không cho đăng ký thêm tài khoản.
- **4a. Yêu cầu gửi lại OTP:** sau khi đủ 5 phút kể từ lần gửi gần nhất, khách có thể yêu cầu mã mới. Nếu đã nhập sai 5 lần, thời gian chờ 5 phút tính từ lần sai thứ năm. Mã mới có hiệu lực 5 phút kể từ lần gửi mới. Khách tiếp tục ở bước 4.

### 1b. Đăng ký với Google
1. Trên màn hình đăng ký, khách chọn “Đăng ký với Google”. Sobie chuyển khách đến Google để xác thực qua OpenID Connect (OAuth 2.0).
2. Khi khách quay lại từ Google, Sobie kiểm tra phản hồi xác thực. Nếu xác thực thất bại, xử lý theo E8. Nếu định danh Google (`sub`) đã liên kết với một tài khoản Sobie, chuyển sang luồng đăng nhập theo E1. Nếu chưa có liên kết, Sobie xác minh email. Nếu email đã có tài khoản Sobie, xử lý theo E1. Nếu Sobie chưa thể xác minh email, xử lý theo E8.
3. Sau khi xác thực thành công với email chưa được sử dụng, khách hoàn tất đăng ký mà không qua màn hình tạo mật khẩu Sobie.
4. Trong cùng một transaction, hệ thống cấp mã `KH-<YYYYMMDD ngày đăng ký>-<4 số>`, tạo tài khoản Khách hàng ở trạng thái Hoạt động với email đã xác minh, lưu liên kết với định danh Google (`sub`) của khách và tạo giỏ hàng cùng danh sách yêu thích trống. Tài khoản được tạo không có mật khẩu Sobie.
5. Hệ thống thông báo đăng ký thành công. Khách có thể dùng “Đăng nhập với Google” ở UC-02. Sau khi tạo tài khoản qua Google, khách được chuyển đến màn hình đăng nhập.

## Exceptions
- **E1. Đã có tài khoản Sobie:** trong luồng email OTP, hệ thống báo "Email đã được sử dụng" và không gửi OTP nếu phát hiện ở bước 2 của luồng chính. Trong luồng Google, nếu định danh Google đã liên kết hoặc email đã xác minh trùng với tài khoản Sobie hiện có, Sobie tiếp tục luồng Google ở UC-02 bằng kết quả xác thực vừa nhận. Nếu chưa liên kết Google, khách xác minh OTP gửi đến email đã lưu trên tài khoản Sobie theo UC-02, nhánh 1d. Khách đăng nhập vào tài khoản Khách hàng hiện có sau khi đáp ứng các điều kiện của UC-02, không cần tạo hoặc nhập mật khẩu Sobie. Sobie không tạo tài khoản mới trong cả hai trường hợp.
- **E3. Email không hợp lệ:** nếu email bị bỏ trống hoặc sai định dạng, hệ thống báo lỗi tại trường email và không gửi OTP.
- **E4. OTP không hợp lệ:** nếu mã sai, không thuộc email đang đăng ký hoặc đã hết hạn, hệ thống báo lỗi tại màn hình xác minh. Khách chỉ được chuyển đến màn hình tạo mật khẩu sau khi xác minh thành công.
- **E5. Yêu cầu gửi lại OTP quá sớm:** nếu chưa đủ 5 phút từ lần gửi gần nhất, hệ thống từ chối yêu cầu và không gửi mã mới.
- **E6. Lỗi khi cấp mã hoặc lưu dữ liệu đăng ký:** hệ thống hoàn tác transaction, bao gồm dữ liệu liên kết Google nếu có, và thông báo đăng ký không thành công.
- **E7. Mật khẩu không hợp lệ:** nếu khách bỏ trống mật khẩu hoặc ô xác nhận, nhập mật khẩu dưới 6 ký tự hoặc nhập hai giá trị không khớp, hệ thống báo lỗi và giữ khách ở màn hình tạo mật khẩu. Hệ thống chưa tạo tài khoản.
- **E8. Xác thực Google chưa thành công:** nếu khách hủy, phản hồi xác thực không hợp lệ hoặc Sobie chưa thể xác minh email, hệ thống chưa tạo tài khoản.

## Postconditions
- Có một tài khoản mới vai trò Khách hàng, trạng thái Hoạt động, với email đã xác minh và mã `KH-...`.
- Tài khoản đăng ký qua OTP có mật khẩu Sobie đã được băm bằng bcrypt. Khách được chuyển đến màn hình đăng nhập.
- Tài khoản đăng ký qua Google có liên kết Google để đăng nhập theo UC-02 và không có mật khẩu Sobie.
- Họ tên, số điện thoại, ngày sinh và địa chỉ nhận hàng để trống khi tạo tài khoản. Khách bổ sung các thông tin này ở UC-04.
- Tài khoản có 1 giỏ hàng trống và 1 danh sách yêu thích trống (UC-18, UC-38).

## Acceptance Criteria

### AC-1: Tạo mật khẩu và hoàn tất đăng ký qua email
Given: khách ở màn hình tạo mật khẩu sau khi xác minh email "a@example.com" bằng OTP
When: khách gửi mật khẩu hợp lệ và xác nhận đúng mật khẩu
Then: hệ thống tạo tài khoản Khách hàng ở trạng thái Hoạt động với email đã xác minh, mật khẩu được băm bằng bcrypt và mã `KH-<YYYYMMDD ngày đăng ký>-<4 số>`
And: họ tên, số điện thoại, ngày sinh và địa chỉ nhận hàng để trống
And: tài khoản có một giỏ hàng trống và một danh sách yêu thích trống
And: khách được chuyển đến màn hình đăng nhập với thông báo đăng ký thành công

### AC-2: Email đã tồn tại trong luồng đăng ký bằng OTP
Given: đã có tài khoản dùng email "a@example.com"
When: khách vãng lai gửi email "a@example.com" để đăng ký bằng OTP
Then: hệ thống báo "Email đã được sử dụng"
And: hệ thống không gửi OTP và không tạo tài khoản mới

### AC-4: Email không hợp lệ
Given: khách vãng lai đang ở trang đăng ký
When: khách gửi biểu mẫu với email bỏ trống hoặc sai định dạng
Then: hệ thống báo lỗi tại trường email, không gửi OTP và không tạo tài khoản

### AC-5: Người đã đăng nhập không đăng ký được
Given: người dùng đang đăng nhập
When: người dùng mở trang đăng ký
Then: hệ thống chuyển về trang chủ

### AC-6: Lỗi giữa chừng không để lại dữ liệu dở dang
Given: khách đã xác minh email và dữ liệu đăng ký hợp lệ
When: việc cấp mã hoặc lưu tài khoản, giỏ hàng, danh sách yêu thích hay liên kết Google (nếu đăng ký qua Google) thất bại giữa chừng
Then: toàn bộ transaction bị hủy, không để lại dữ liệu đăng ký dở dang và bộ đếm mã `KH-` không bị dùng mất số
And: hệ thống báo đăng ký không thành công

### AC-7: OTP sai hoặc hết hạn
Given: hệ thống đã gửi OTP đến email đăng ký
When: khách nhập sai mã, nhập mã của email khác hoặc nhập mã sau khi đã hết hiệu lực
Then: hệ thống báo lỗi, không xác minh email và không tạo tài khoản
And: khách ở lại màn hình xác minh OTP

### AC-8: Từ chối gửi lại OTP trước 5 phút
Given: hệ thống đã gửi OTP đến email đăng ký
When: khách yêu cầu gửi lại trước khi đủ 5 phút từ lần gửi gần nhất
Then: hệ thống từ chối yêu cầu và không gửi mã mới

### AC-11: Gửi lại OTP khi đã đủ 5 phút
Given: hệ thống đã gửi OTP đến email đăng ký
When: khách yêu cầu gửi lại khi đã đủ 5 phút kể từ lần gửi gần nhất
Then: hệ thống gửi mã mới đến email đăng ký
And: mã mới có hiệu lực trong 5 phút kể từ lần gửi mới

### AC-12: Xác minh OTP thành công
Given: hệ thống đã gửi OTP đến email đăng ký hợp lệ và chưa được dùng
When: khách nhập đúng mã trong thời hạn 5 phút
Then: hệ thống xác minh email và chuyển khách đến màn hình tạo mật khẩu
And: tài khoản chưa được tạo ở bước này

### AC-13: Mật khẩu không hợp lệ
Given: khách ở màn hình tạo mật khẩu sau khi xác minh OTP
When: khách bỏ trống mật khẩu hoặc ô xác nhận, nhập mật khẩu dưới 6 ký tự hoặc xác nhận mật khẩu không khớp
Then: hệ thống hiển thị lỗi và giữ khách ở màn hình tạo mật khẩu
And: hệ thống không tạo tài khoản

### AC-14: Đăng ký thành công bằng Google mà không cần mật khẩu Sobie
Given: khách chọn “Đăng ký với Google” trên màn hình đăng ký
When: khách hoàn tất đăng ký sau khi Sobie xác thực phản hồi Google và xác minh được email chưa dùng
Then: hệ thống tạo tài khoản Khách hàng ở trạng thái Hoạt động với email đã xác minh, mã `KH-<YYYYMMDD ngày đăng ký>-<4 số>` và liên kết Google
And: họ tên, số điện thoại, ngày sinh và địa chỉ nhận hàng để trống
And: tài khoản có một giỏ hàng trống và một danh sách yêu thích trống
And: khách không phải qua màn hình tạo mật khẩu và tài khoản không có mật khẩu Sobie

### AC-15: Xác thực Google chưa thành công
Given: khách đã bắt đầu đăng ký với Google
When: khách hủy, phản hồi xác thực không hợp lệ hoặc Sobie chưa thể xác minh email
Then: hệ thống không tạo tài khoản

### AC-16: Dùng Google khi đã có tài khoản Sobie
Given: khách dùng Google từ màn hình đăng ký và đã có tài khoản Khách hàng Hoạt động trên Sobie
When: Sobie xác thực Google và xác nhận tài khoản hiện có theo liên kết Google hoặc theo OTP liên kết lần đầu ở UC-02
Then: Sobie cấp phiên cho tài khoản hiện có theo UC-02, không yêu cầu mật khẩu Sobie
And: không tạo tài khoản, giỏ hàng hoặc danh sách yêu thích mới

### AC-17: Khóa OTP sau 5 lần nhập sai
Given: khách đã nhận OTP đăng ký qua email
When: khách nhập sai lần thứ năm trong thời hạn của mã
Then: hệ thống khóa mã và trả `429` cho lần thứ năm và các lần xác minh tiếp theo đối với mã đã khóa
And: khách có thể yêu cầu mã khác sau đủ 5 phút kể từ lần sai thứ năm

## Dependencies
- **Upstream UC:** —
- **Downstream UC:** UC-02 Đăng nhập, UC-04 Cập nhật hồ sơ khách hàng
- **External Systems:** Dịch vụ gửi email OTP, Google (OpenID Connect).

## Notes
- Khách có thể xác minh email bằng OTP hoặc qua Google.

### Quyết định đã chốt
- Thông tin đăng nhập và thông tin cá nhân nằm trong cùng bản ghi tài khoản. Email là duy nhất (data model v2, đã chốt 21/11/2026).
- Cả hai luồng đăng ký đều bỏ qua các trường hồ sơ. UC-04 kiểm tra định dạng và tính duy nhất của số điện thoại khi khách bổ sung hoặc cập nhật hồ sơ (đã chốt 23/11/2026).
- Mã tài khoản Khách hàng `KH-<YYYYMMDD ngày đăng ký>-<4 số>`, hệ thống cấp, không sửa; bộ đếm riêng cho tiền tố `KH` (đã chốt 21/11/2026).
- Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` của `account_created_at` (đã chốt 21/11/2026).
- Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026).
- Luồng đăng ký qua OTP yêu cầu tạo mật khẩu Sobie. Đăng ký qua Google dùng định danh Google và khách không cần tạo mật khẩu Sobie (đã chốt 23/11/2026).
- Nếu khách dùng Google và đã có tài khoản Sobie, hệ thống chuyển sang đăng nhập tài khoản hiện có theo UC-02 (đã chốt 23/11/2026).
- Giỏ hàng và danh sách yêu thích trống được tạo cùng transaction tạo account; module identity gọi service công khai của shopping (đã chốt 21/11/2026, Q39).

### Quyết định bổ sung đã duyệt

- Mật khẩu Sobie có tối thiểu 6 ký tự.
- Người đã đăng nhập mở trang đăng ký được chuyển về trang chủ.
- Sau đăng ký mới qua Google, khách được chuyển đến màn hình đăng nhập.
- Khách mới có thể để trống họ tên và số điện thoại. Tài khoản Google lưu định danh Google và có thể chưa có hash mật khẩu.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt đăng ký đủ email và số điện thoại
- v3 (2026-11-15): theo ERD — tách account (thông tin đăng nhập) và hồ sơ Customer; thêm AC-6
- v4 (2026-11-21): theo data model v2 — bỏ hồ sơ Customer, thông tin cá nhân nằm trong account; cấp mã `KH-` (bước 4, AC-1, AC-6)
- v5 (2026-11-21): chốt bcrypt và múi giờ của mã `KH-`, bổ sung giả định tạo giỏ hàng và danh sách yêu thích khi đăng ký
- v6 (2026-11-21): chốt tạo giỏ hàng và danh sách yêu thích cùng transaction tạo account (Q39)
- v7 (2026-11-23): xác minh email bằng OTP, quy định thời hạn và gửi lại mã, chuyển các trường còn lại thành tùy chọn.
- v8 (2026-11-23): bổ sung màn hình tạo mật khẩu sau khi xác minh OTP, chuyển đến màn hình đăng nhập khi đăng ký thành công và thêm nhánh đăng ký với Google.
- v9 (2026-11-23): chốt đăng ký bằng Google không cần mật khẩu Sobie và nối với luồng đăng nhập Google ở UC-02.
- v10 (2026-11-23): cập nhật E1 và AC-16 để khách dùng Google có thể đăng nhập vào tài khoản Sobie hiện có.
- v11 (2026-11-23): bỏ các trường hồ sơ khỏi hai luồng đăng ký và bỏ E2, AC-3, AC-9, AC-10 liên quan.
- v12 (2026-11-23): đồng bộ E1 và AC-16 với xác minh OTP khi liên kết Google lần đầu ở UC-02.
