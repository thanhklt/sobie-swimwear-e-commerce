# API Contract Identity v1

Tài liệu mô tả các endpoint storefront và portal của [router Identity](../app/modules/identity/router.py). Router đăng nhập được đăng ký tại `main.py` với tiền tố `/api/v1`. Mỗi cổng dùng chung đường dẫn cho GET hiển thị biểu mẫu và POST xử lý đăng nhập.

Nguồn nghiệp vụ gồm [UC-01 đến UC-08](../specs/use-cases/identity/) và [BR giai đoạn 1](../specs/business-requirements/BR-GIAIDOAN1.md).

## Quy ước trao đổi HTTP

- Các `GET` nhận tham số qua query string. Các `POST` nhận biểu mẫu HTML với `Content-Type: application/x-www-form-urlencoded`.
- Response hiển thị trang là `text/html`. Lỗi nghiệp vụ hiển thị thông báo trên trang. Điều hướng dùng HTTP `303` với header `Location`.
- Phản hồi do router dựng có `Cache-Control: no-store` và `Referrer-Policy: no-referrer`.
- Cookie `__Host-sobie-registration` giữ lượt xác minh của trình duyệt. Cookie có `Path=/`, `Max-Age=3600`, `Secure`, `HttpOnly`, `SameSite=Lax`. Các bước trong cùng lượt dùng cùng cookie. Thời hạn OTP và trạng thái nghiệp vụ được tính riêng ở server.
- Mọi `POST` bên dưới đều yêu cầu `csrf_token` lấy từ input ẩn trong biểu mẫu cùng với cookie đăng ký tương ứng. Cookie hoặc token thiếu, sai hoặc không khớp trả `403`.
- Phiên storefront hợp lệ thường trả `303` tới `/`. Callback Google kiểm tra tham số trùng trước khi kiểm tra phiên.
- Khi đăng nhập Google thành công, server đặt cookie `storefront_session` (`Path=/`, `Secure`, `HttpOnly`, `SameSite=Lax`) và xóa cookie đăng ký. Phiên Khách hàng phía server hết hạn sau 30 phút không hoạt động. Request xác thực thành công gia hạn phiên thêm 30 phút.

## Danh sách endpoint

| Method và đường dẫn | Input | Thành công | Sequence |
| --- | --- | --- | --- |
| `GET /register` | Query `restart` tùy chọn | `200` trang đăng ký hoặc bước xác minh đang dở | [Sơ đồ](sequence/identity/get-register.md) |
| `POST /register/email` | Form `email`, `csrf_token` | `200` trang nhập OTP | [Sơ đồ](sequence/identity/post-register-email.md) |
| `POST /register/otp/resend` | Form `csrf_token` | `200` trang nhập OTP mới | [Sơ đồ](sequence/identity/post-register-otp-resend.md) |
| `POST /register/otp` | Form `otp`, `csrf_token` | `200` trang tạo mật khẩu | [Sơ đồ](sequence/identity/post-register-otp.md) |
| `POST /register/password` | Form `password`, `password_confirmation`, `csrf_token` | `303` tới `/api/v1/login` | [Sơ đồ](sequence/identity/post-register-password.md) |
| `GET /register/google` | Query `login` tùy chọn | `303` tới Google | [Sơ đồ](sequence/identity/get-register-google.md) |
| `GET /register/google/callback` | Query `state`, `code` hoặc `error` | `303` tới `/api/v1/login` hoặc `/`, hoặc `200` trang nhập OTP liên kết | [Sơ đồ](sequence/identity/get-register-google-callback.md) |
| `POST /register/google/link/otp` | Form `otp`, `csrf_token` | `303` tới `/` và cấp cookie phiên | [Sơ đồ](sequence/identity/post-register-google-link-otp.md) |
| `GET /api/v1/login` | Không có tham số | `200` trang đăng nhập | [Sơ đồ](sequence/identity/get-login.md) |
| `GET /` | Accept: text/html | 200 HTML với liên kết hồ sơ và đăng xuất hoặc đăng nhập và đăng ký | [Sơ đồ](sequence/identity/get-home.md) |
| `GET /api/v1/admin/login` | Mở trang đăng nhập quản trị | 200 biểu mẫu có CSRF hoặc 303 /admin nếu đã đăng nhập | [Sơ đồ](sequence/identity/get-admin-login.md) |
| `POST /api/v1/login` | Form `identifier`, `password`, `csrf_token` | `303` tới `/` kèm `storefront_session` | [Sơ đồ](sequence/identity/post-api-v1-login.md) |
| `POST /api/v1/admin/login` | Form `identifier`, `password`, `csrf_token` | `303` tới `/admin` kèm `portal_session` | [Sơ đồ](sequence/identity/post-api-v1-admin-login.md) |
| `POST /login` | Gửi identifier, password và csrf_token | 303 / kèm storefront_session hoặc lỗi biểu mẫu | [Sơ đồ](sequence/identity/post-login.md) |
| `POST /admin/login` | Gửi identifier, password và csrf_token | 303 /admin kèm portal_session hoặc lỗi biểu mẫu | [Sơ đồ](sequence/identity/post-admin-login.md) |
| `GET /admin` | Cookie portal hợp lệ | 200 trang Tổng quan tạm theo vai trò Admin hoặc Nhân viên | [Sơ đồ](sequence/identity/get-admin.md) |
| `POST /logout` | Gửi csrf_token cùng storefront_session | 303 / và xóa cookie storefront_session | [Sơ đồ](sequence/identity/post-logout.md) |
| `POST /admin/logout` | Gửi csrf_token cùng portal_session | 303 / và xóa cookie portal_session | [Sơ đồ](sequence/identity/post-admin-logout.md) |
| `GET /account/profile` | Mở hồ sơ với phiên Khách hàng | 200 hồ sơ kèm mã tài khoản chỉ đọc và CSRF | [Sơ đồ](sequence/identity/get-account-profile.md) |
| `POST /account/profile` | Gửi trường hồ sơ và csrf_token | 303 về hồ sơ kèm thông báo hoặc 400 lỗi theo trường | [Sơ đồ](sequence/identity/post-account-profile.md) |
| `GET /account/password` | Mở trang với phiên Khách hàng | 200 biểu mẫu đổi mật khẩu có CSRF hoặc 403 | [Sơ đồ](sequence/identity/get-account-password.md) |
| `POST /account/password` | Gửi mật khẩu hiện tại, mật khẩu mới, xác nhận và csrf_token | 303 /api/v1/login để đăng nhập lại hoặc 400 lỗi theo trường | [Sơ đồ](sequence/identity/post-account-password.md) |
| `GET /admin/password` | Mở trang với phiên nội bộ | 200 biểu mẫu đổi mật khẩu có CSRF | [Sơ đồ](sequence/identity/get-admin-password.md) |
| `POST /admin/password` | Gửi mật khẩu hiện tại, mật khẩu mới, xác nhận và csrf_token | 303 /api/v1/admin/login để đăng nhập lại hoặc 400 lỗi theo trường | [Sơ đồ](sequence/identity/post-admin-password.md) |
| `GET /admin/accounts/new` | Mở trang với phiên Admin | 200 biểu mẫu tạo tài khoản có CSRF | [Sơ đồ](sequence/identity/get-admin-accounts-new.md) |
| `POST /admin/accounts/new` | Gửi vai trò, hồ sơ, mật khẩu và csrf_token | 303 về danh sách tài khoản hoặc 400 lỗi theo trường | [Sơ đồ](sequence/identity/post-admin-accounts-new.md) |
| `GET /admin/accounts` | Mở danh sách hoặc gửi q và page | 200 danh sách hoặc thông báo không tìm thấy | [Sơ đồ](sequence/identity/get-admin-accounts.md) |
| `GET /admin/customers` | Mở danh sách hoặc gửi q và page | 200 danh sách Khách hàng với điều hướng | [Sơ đồ](sequence/identity/get-admin-customers.md) |
| `GET /admin/customers/{key}` | Chọn tài khoản Khách hàng | 200 hồ sơ và trạng thái hoặc 404 | [Sơ đồ](sequence/identity/get-admin-customers-key.md) |
| `GET /admin/accounts/{key}/edit` | Chọn account theo khóa | 200 biểu mẫu hồ sơ và thao tác tài khoản hoặc 404 | [Sơ đồ](sequence/identity/get-admin-accounts-key-edit.md) |
| `POST /admin/accounts/{key}/edit` | Gửi hồ sơ, vai trò nội bộ nếu có và csrf_token trong cùng biểu mẫu | 303 tới chi tiết hoặc đăng nhập lại hoặc 400 khi bị từ chối | [Sơ đồ](sequence/identity/post-admin-accounts-key-edit.md) |
| `POST /admin/accounts/{key}/lock` | Gửi xác nhận và csrf_token | 303 tới trang chi tiết hoặc đăng nhập lại khi tự khóa | [Sơ đồ](sequence/identity/post-admin-accounts-key-lock.md) |
| `POST /admin/accounts/{key}/unlock` | Gửi xác nhận và csrf_token | 303 về trang chi tiết, phiên mới được cấp khi đăng nhập lại | [Sơ đồ](sequence/identity/post-admin-accounts-key-unlock.md) |

## Đăng ký qua email

### `GET /register`

- `200` hiển thị trang nhập email khi mở lần đầu. Nếu cookie có lượt xác minh phù hợp, trang hiển thị bước nhập OTP, tạo mật khẩu hoặc nhập OTP liên kết Google tương ứng.
- `?restart=1` mở trang nhập email bằng cách bỏ qua bước đọc trạng thái. Thao tác này giữ cookie hợp lệ hiện có và không xóa trạng thái đang lưu.
- `503` nếu route gặp lỗi khi đọc trạng thái đăng ký. `303` tới `/` nếu đã đăng nhập.

### `POST /register/email`

- `email` là chuỗi tối đa 255 ký tự. Server bỏ khoảng trắng ở hai đầu, kiểm tra định dạng và chuẩn hóa về chữ thường.
- `200` gửi OTP đến email chưa có tài khoản và hiển thị trang nhập mã. OTP gồm 6 chữ số ASCII, có hiệu lực 5 phút tính từ lúc gửi. Mỗi mã cho tối đa 5 lần nhập sai.
- `400` nếu email sai, bị bỏ trống hoặc chưa hết thời gian chờ gửi mã cho email đó. Thời gian chờ áp dụng cả khi đổi trình duyệt.
- `409` nếu email đã được sử dụng hoặc lượt đang có yêu cầu xử lý đồng thời. `503` nếu không gửi được email hoặc dịch vụ xác minh không khả dụng.

### `POST /register/otp/resend`

- Server lấy email từ lượt hiện tại. `200` gửi mã mới sau khi đã đủ 5 phút kể từ lần gửi gần nhất, vô hiệu hóa mã trước và hiển thị lại trang nhập OTP.
- `400` nếu thiếu lượt OTP hợp lệ hoặc yêu cầu gửi lại quá sớm. Trạng thái của lượt OTP đăng ký có thể được giữ đến 30 phút kể từ lần gửi gần nhất để hỗ trợ gửi lại.
- `409` nếu email đã được sử dụng hoặc có yêu cầu đồng thời. `503` nếu dịch vụ xác minh hoặc gửi mail gặp lỗi.

### `POST /register/otp`

- Gửi `otp` dưới dạng chuỗi 6 chữ số ASCII để giữ được số `0` ở đầu.
- `200` xác minh email, tiêu thụ mã và hiển thị trang tạo mật khẩu. Người dùng có 10 phút để hoàn tất bước tạo mật khẩu.
- `400` nếu mã sai, không đúng định dạng, hết hạn, đã hết lượt thử hoặc trạng thái không ở bước xác minh email. `503` nếu dịch vụ xác minh gặp lỗi.

### `POST /register/password`

- `password` và `password_confirmation` phải có giá trị và khớp nhau. Mật khẩu có tối thiểu 6 ký tự, tối đa 72 byte UTF-8 và không chứa ký tự NUL.
- `303` tới `/api/v1/login` sau khi tạo tài khoản Khách hàng ở trạng thái Hoạt động, băm mật khẩu bằng bcrypt và tạo giỏ hàng cùng danh sách yêu thích trống trong một transaction.
- `400` nếu mật khẩu không hợp lệ, bước xác minh đã hết hạn hoặc trạng thái lượt không phù hợp. `409` nếu phát hiện email đã được sử dụng ở bước kiểm tra lại.
- `500` nếu thao tác lưu đăng ký thất bại và transaction được hoàn tác. `503` nếu lỗi thoát ra khỏi tầng xử lý đăng ký.

## Đăng ký và đăng nhập bằng Google

### `GET /register/google`

- `303` điều hướng tới Google OpenID Connect. Server tạo cookie đăng ký nếu cần và lưu trạng thái OIDC trong 10 phút. Luồng dùng scope `openid email` và PKCE `S256`.
- `/register/google` cho phép tạo tài khoản mới. `?login=1` dùng kết quả Google cho tài khoản Sobie đã có.
- `400` nếu không lưu được trạng thái do xung đột. `409` nếu lượt đang được xử lý. `503` nếu cấu hình Google thiếu hoặc dịch vụ xác minh không khả dụng.

### `GET /register/google/callback`

- `state` phải khớp lượt Google còn hạn của cookie đăng ký. `code` là mã Google trả khi người dùng chấp thuận. `error` khác rỗng được xử lý như xác thực thất bại.

| Kết quả xác thực | Phản hồi |
| --- | --- |
| Tìm thấy tài khoản Khách hàng đang hoạt động theo `sub` | `303` tới `/` và cấp cookie phiên storefront. |
| Email Google đã xác minh trùng tài khoản Khách hàng đang hoạt động chưa liên kết Google | `200` trang nhập OTP. Mã được gửi đến email đã lưu trên tài khoản Sobie. |
| Email đã xác minh chưa có tài khoản và lượt cho phép đăng ký | `303` tới `/api/v1/login` sau khi tạo tài khoản Google mới, giỏ hàng và danh sách yêu thích trống. Tài khoản được tạo không cần mật khẩu Sobie. |

- `400` nếu thiếu cookie hoặc trạng thái hợp lệ, tham số `state`, `code` hay `error` lặp, người dùng hủy, xác thực thất bại, tài khoản không đủ điều kiện, yêu cầu gửi OTP đang trong thời gian chờ hoặc lượt chỉ đăng nhập không tìm được tài khoản. Ở trường hợp cuối, thông báo hướng dẫn chọn Đăng ký với Google.
- `409` nếu trạng thái thay đổi khi chuẩn bị gửi OTP liên kết. `500` nếu thao tác với tài khoản hoặc phiên thất bại. `503` nếu gửi OTP liên kết hoặc dịch vụ xác minh gặp lỗi.

### `POST /register/google/link/otp`

- `otp` là chuỗi 6 chữ số ASCII. Mã có hiệu lực 5 phút và tối đa 5 lần nhập sai. Trang liên kết có biểu mẫu xác minh và liên kết bắt đầu lại.
- `303` tới `/` sau khi xác minh mã, liên kết `sub` với tài khoản Sobie và cấp phiên storefront trong cùng transaction.
- `400` nếu mã sai, hết hạn, hết lượt thử, không có lượt liên kết phù hợp hoặc tài khoản không còn đủ điều kiện. `500` nếu lưu liên kết hoặc tạo phiên thất bại. `503` nếu dịch vụ xác minh gặp lỗi.

## `GET /api/v1/login`

- `200` hiển thị form đăng nhập bằng mật khẩu, nút Quên mật khẩu, liên kết Google và đăng ký. Sau khi tạo tài khoản, thông báo “Đăng ký thành công.” có thể hiển thị một lần trong 2 phút khi dùng cùng cookie đăng ký. Nếu không đọc được thông báo, trang vẫn trả `200`.
- `303` tới `/` nếu đã có phiên storefront hợp lệ. Biểu mẫu gửi tới `POST /api/v1/login`.

## Đăng nhập bằng mật khẩu, phiên và hồ sơ

- `POST /api/v1/login` chỉ nhận Khách hàng. `POST /api/v1/admin/login` chỉ nhận Nhân viên và Admin. Cả hai nhận `identifier` (email hoặc số điện thoại), `password` và `csrf_token` từ biểu mẫu HTML. Thiếu trường trả `400`, sai thông tin hoặc sai cổng trả `401`, tài khoản bị khóa trả `403`. Hai cổng chia sẻ Redis đếm theo IP. Lần thứ sáu trong cửa sổ 60 giây trả `429` trước khi tra mật khẩu. Google không dùng bộ đếm này.
- `GET /api/v1/admin/login` hiển thị biểu mẫu gửi tới `POST /api/v1/admin/login`. Hai đường dẫn cũ `/login` và `/admin/login` vẫn nhận GET và POST để tương thích.
- Portal dùng `/admin` làm điểm vào Tổng quan. Cả đăng nhập thành công và mở lại trang đăng nhập với phiên hợp lệ đều dẫn tới điểm vào này. Trang tạm hiển thị vai trò và liên kết quản lý tương ứng.
- Storefront cấp `storefront_session` với hạn trượt 30 phút. Portal cấp `portal_session` với hạn trượt 1 giờ. Đăng xuất xóa phiên hiện tại và cookie của cổng đó. Đổi mật khẩu, đổi vai trò và khóa tài khoản thu hồi tất cả phiên của tài khoản đích.
- Form hồ sơ dùng `name`, `date_of_birth`, `house_number`, `ward`, `city`, `country`, `email`, `phone_number`. Email và điện thoại mới được lưu sau kiểm tra định dạng và trùng lặp. Form đổi mật khẩu dùng `current_password`, `password`, `password_confirmation`.
- Admin có quyền tạo tài khoản, xem toàn bộ, sửa hồ sơ, đổi vai trò của tài khoản nội bộ, khóa và mở khóa. Nhân viên xem và khóa tài khoản Khách hàng. `confirm=yes` thực hiện thao tác khóa hoặc mở khóa. Các giá trị khác trở về trang chi tiết.
- UC-02 AC-7 còn phụ thuộc trang thanh toán của ordering và dịch vụ gộp giỏ vãng lai của shopping. Redirect sau đăng nhập hiện dùng trang đích theo cổng.

## Cấu hình triển khai
- **Cấu hình Redis.** [`REDIS_URL`](../app/config/settings.py) được truyền trực tiếp cho Redis. Nếu Redis yêu cầu mật khẩu, URL phải có thông tin xác thực phù hợp. Lỗi truy cập kho trạng thái có thể khiến các bước đăng ký trả `503`.
