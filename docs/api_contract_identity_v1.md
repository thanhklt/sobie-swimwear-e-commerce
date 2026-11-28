# API Contract Identity v1

Tài liệu mô tả các endpoint storefront và portal của [router Identity](../app/modules/identity/router/__init__.py). Router Identity dùng tiền tố `/api/v1/identity`. Mỗi cổng dùng chung đường dẫn cho GET hiển thị biểu mẫu và POST xử lý đăng nhập.

Nguồn nghiệp vụ gồm [UC-01 đến UC-08](../specs/use-cases/identity/) và [BR giai đoạn 1](../specs/business-requirements/BR-GIAIDOAN1.md).

## Quy ước trao đổi HTTP

- `GET` nhận tham số qua query string. `POST` nhận biểu mẫu HTML với `Content-Type: application/x-www-form-urlencoded`. Trang Identity trả HTML và `Cache-Control: no-store`. Chuyển hướng dùng `303` cùng header `Location`.
- Thiếu phiên hợp lệ ở endpoint yêu cầu đăng nhập dẫn tới `303` về trang đăng nhập đúng cổng. Với `HX-Request: true`, ứng dụng trả `401` kèm `HX-Redirect`. Sai vai trò trả `403`. Tham số path `account_key` phải là UUID. `page` nhận số nguyên. FastAPI trả `422` nếu các tham số này sai kiểu.
- Chống CSRF bằng cookie `SameSite=Lax` và kiểm tra `Origin`, không dùng CSRF token (BR-GIAIDOAN1, xác nhận lại 27/11/2026). Middleware kiểm tra `Origin` ở mọi request `POST`, `PUT`, `PATCH`, `DELETE`, kể cả HTMX, trước khi xác thực hoặc gia hạn phiên và truy cập Redis. Header thiếu, có giá trị `null` hoặc nguồn khác origin của request và các mục trong `ALLOWED_ORIGINS` trả `403`. Mọi trang Identity có biểu mẫu POST dùng `Referrer-Policy: strict-origin` để trình duyệt gửi `Origin` thật.
- Cookie trình duyệt `__Host-sobie-registration` chỉ dùng để định danh lượt xác minh đăng ký. Cookie có `Path=/`, `Max-Age=3600`, `Secure`, `HttpOnly`, `SameSite=Lax`. OTP và trạng thái nghiệp vụ có thời hạn riêng ở server.
- Cookie xác thực `storefront_session` và `portal_session` dùng `Path=/`, `Secure`, `HttpOnly`, `SameSite=Lax`. Storefront gia hạn 30 phút khi xác thực thành công, portal gia hạn 60 phút. Đăng nhập Google thành công cấp cookie storefront và xóa cookie đăng ký.

## Danh sách endpoint

| Method và đường dẫn | Quyền | Dữ liệu gửi | Phản hồi chính | Sequence |
| --- | --- | --- | --- | --- |
| `GET /api/v1/identity/register` | Vãng lai | `restart=1` tùy chọn | 200 trang đăng ký hoặc bước xác minh đang dở, 303 về `/` nếu đã có phiên, 503 lỗi kho trạng thái | [Sơ đồ](sequence/identity/get-register.md) |
| `POST /api/v1/identity/register/email` | Vãng lai | Header `Origin`, form `email` | 200 nhập OTP, 400 dữ liệu hoặc lượt xác minh không hợp lệ, 403 Origin không hợp lệ, 409 xung đột, 429 lượt OTP đang bị khóa, 503 lỗi dịch vụ | [Sơ đồ](sequence/identity/post-register-email.md) |
| `POST /api/v1/identity/register/otp/resend` | Vãng lai | Header `Origin` | 200 nhập OTP mới, 400 sai lượt hoặc gửi lại quá sớm, 403 Origin không hợp lệ, 409 xung đột, 429 lượt OTP đang bị khóa, 503 lỗi dịch vụ | [Sơ đồ](sequence/identity/post-register-otp-resend.md) |
| `POST /api/v1/identity/register/otp` | Vãng lai | Header `Origin`, form `otp` | 200 tạo mật khẩu, 400 mã sai hoặc hết hạn, 403 Origin không hợp lệ, 429 mã bị khóa, 503 lỗi kho xác minh | [Sơ đồ](sequence/identity/post-register-otp.md) |
| `POST /api/v1/identity/register/password` | Vãng lai | Header `Origin`, form `password`, `password_confirmation` | 303 về đăng nhập, 400 mật khẩu hoặc lượt xác minh không hợp lệ, 403 Origin không hợp lệ, 409 email trùng, 500/503 lỗi xử lý | [Sơ đồ](sequence/identity/post-register-password.md) |
| `GET /api/v1/identity/register/google` | Vãng lai | Query `login=1` và `return_url=/api/v1/ordering/checkout` tùy chọn | 303 sang Google hoặc tới trang đích nếu có phiên, 400/409/503 lỗi khởi tạo OIDC | [Sơ đồ](sequence/identity/get-register-google.md) |
| `GET /api/v1/identity/register/google/callback` | Google / Vãng lai | Query `state`, `code` hoặc `error` | 303 tới trang chủ hoặc checkout kèm phiên, 400/409 lỗi xác minh, 500/503 lỗi xử lý | [Sơ đồ](sequence/identity/get-register-google-callback.md) |
| `GET /api/v1/identity/login` | Vãng lai / Khách | Query `return_url`, `password_changed` tùy chọn | 200 mẫu đăng nhập, 303 tới `/` hoặc checkout nếu có phiên | [Sơ đồ](sequence/identity/get-login.md) |
| `GET /` | Vãng lai / Khách hàng | Header `Accept` | 200 HTML Identity nếu `Accept` chứa `text/html`, các trường hợp còn lại trả JSON | [Sơ đồ](sequence/identity/get-home.md) |
| `GET /api/v1/identity/portal/login` | Vãng lai / Nội bộ | Query `password_changed`, `locked`, `role_changed` tùy chọn | 200 mẫu đăng nhập, 303 tới `/api/v1/identity/portal` nếu có phiên | [Sơ đồ](sequence/identity/get-admin-login.md) |
| `POST /api/v1/identity/login` | Vãng lai / Khách | Header `Origin`, form `identifier`, `password`, query `return_url` tùy chọn | 303 tới `/` hoặc checkout kèm phiên storefront khi đăng nhập thành công, 400/401/403 lỗi xác thực hoặc Origin, 429 quá giới hạn, 503 lỗi Redis | [Sơ đồ](sequence/identity/post-login.md) |
| `POST /api/v1/identity/portal/login` | Vãng lai / Nội bộ | Header `Origin`, form `identifier`, `password` | 303 tới `/api/v1/identity/portal` kèm phiên portal khi đăng nhập thành công, 400/401/403 lỗi xác thực hoặc Origin, 429 quá giới hạn, 503 lỗi Redis | [Sơ đồ](sequence/identity/post-admin-login.md) |
| `GET /api/v1/identity/portal` | Nhân viên / Admin | — | 200 trang Tổng quan với liên kết theo vai trò | [Sơ đồ](sequence/identity/get-admin.md) |
| `POST /api/v1/identity/logout` | Vãng lai / Khách hàng | Header `Origin`, cookie `storefront_session` nếu có | 303 về `/` và hết hạn cookie storefront, kể cả phiên hết hạn hoặc thiếu cookie, 403 Origin không hợp lệ | [Sơ đồ](sequence/identity/post-logout.md) |
| `POST /api/v1/identity/portal/logout` | Vãng lai / Nhân viên / Admin | Header `Origin`, cookie `portal_session` nếu có | 303 về `/` và hết hạn cookie portal, kể cả phiên hết hạn hoặc thiếu cookie, 403 Origin không hợp lệ | [Sơ đồ](sequence/identity/post-admin-logout.md) |
| `GET /api/v1/identity/account/profile` | Khách | Query `saved=1` tùy chọn | 200 hồ sơ của chủ phiên, mã tài khoản và email chỉ xem, trang dùng `Referrer-Policy: strict-origin` | [Sơ đồ](sequence/identity/get-account-profile.md) |
| `POST /api/v1/identity/account/profile` | Khách | Các trường hồ sơ được sửa. Server bỏ qua `email` nếu được gửi | 303 về hồ sơ với `saved=1`, 400 lỗi theo trường, 403 khi `Origin` không hợp lệ | [Sơ đồ](sequence/identity/post-account-profile.md) |
| `GET /api/v1/identity/account/password` | Khách | — | 200 mẫu đổi mật khẩu, 403 nếu chưa có mật khẩu Sobie | [Sơ đồ](sequence/identity/get-account-password.md) |
| `POST /api/v1/identity/account/password` | Khách | `current_password`, `password`, `password_confirmation` | 303 tới `/api/v1/identity/login?password_changed=1`, 400 lỗi theo trường, 403 khi `Origin` không hợp lệ | [Sơ đồ](sequence/identity/post-account-password.md) |
| `GET /api/v1/identity/portal/password` | Nhân viên / Admin | — | 200 mẫu đổi mật khẩu, 403 nếu chưa có mật khẩu Sobie | [Sơ đồ](sequence/identity/get-admin-password.md) |
| `POST /api/v1/identity/portal/password` | Nhân viên / Admin | `current_password`, `password`, `password_confirmation` | 303 tới `/api/v1/identity/portal/login?password_changed=1`, 400 lỗi theo trường, 403 khi `Origin` không hợp lệ | [Sơ đồ](sequence/identity/post-admin-password.md) |
| `GET /api/v1/identity/portal/accounts/new` | Admin | — | 200 mẫu tạo tài khoản với ba vai trò cố định | [Sơ đồ](sequence/identity/get-admin-accounts-new.md) |
| `POST /api/v1/identity/portal/accounts/new` | Admin | Các trường hồ sơ, `role`, `password` | 303 tới `/api/v1/identity/portal/accounts?notice=created`, 400 lỗi theo trường, 403 khi `Origin` không hợp lệ, 500 nếu transaction thất bại | [Sơ đồ](sequence/identity/post-admin-accounts-new.md) |
| `GET /api/v1/identity/portal/accounts` | Admin | Query `q`, `page`, `notice=created` hoặc `lock` tùy chọn | 200 danh sách tài khoản có phân trang và nút khóa/mở khóa | [Sơ đồ](sequence/identity/get-admin-accounts.md) |
| `GET /api/v1/identity/portal/customers` | Nhân viên | Query `q`, `page` tùy chọn | 200 danh sách tài khoản Khách hàng có phân trang | [Sơ đồ](sequence/identity/get-admin-customers.md) |
| `GET /api/v1/identity/portal/customers/{account_key}` | Nhân viên | Path `account_key`, query `lock` tùy chọn | 200 hồ sơ Khách hàng, 404 nếu tài khoản không tồn tại hoặc không phải Khách hàng | [Sơ đồ](sequence/identity/get-admin-customers-key.md) |
| `GET /api/v1/identity/portal/accounts/{account_key}/edit` | Admin | Path `account_key`, query `saved=1` hoặc `lock` tùy chọn | 200 hồ sơ và form chỉnh sửa, 404 nếu không tìm thấy tài khoản | [Sơ đồ](sequence/identity/get-admin-accounts-key-edit.md) |
| `POST /api/v1/identity/portal/accounts/{account_key}/edit` | Admin | Path `account_key`, các trường hồ sơ, `role` nếu đổi vai trò nội bộ | 303 về trang sửa với `saved=1` hoặc đăng nhập lại khi tự đổi vai trò, 400 lỗi nghiệp vụ, 403 khi `Origin` không hợp lệ, 404 nếu không tìm thấy tài khoản, 500 trang HTML báo cập nhật không thành công khi giao dịch lưu thất bại | [Sơ đồ](sequence/identity/post-admin-accounts-key-edit.md) |
| `POST /api/v1/identity/portal/accounts/{account_key}/lock` | Nhân viên / Admin | Path `account_key`, form `confirm`. Form từ danh sách Admin gửi thêm `source=accounts`, `q`, `page` | 303 về trang xuất phát hoặc đăng nhập lại nếu tự khóa, 400 nếu khóa Admin Hoạt động cuối cùng, 403 khi `Origin` không hợp lệ hoặc tài khoản đích ngoài phạm vi | [Sơ đồ](sequence/identity/post-admin-accounts-key-lock.md) |
| `POST /api/v1/identity/portal/accounts/{account_key}/unlock` | Admin | Path `account_key`, form `confirm`. Form từ danh sách Admin gửi thêm `source=accounts`, `q`, `page` | 303 về danh sách hoặc trang sửa, 403 khi `Origin` không hợp lệ hoặc tài khoản đích không tồn tại | [Sơ đồ](sequence/identity/post-admin-accounts-key-unlock.md) |

## Đăng ký qua email

Các phản hồi HTML ở bước OTP đăng ký hiển thị thời gian chờ gửi lại theo TTL cooldown của email, kể cả khi tải lại trang. Nút "Gửi lại mã" bị vô hiệu hóa trong lúc đếm ngược và được bật lại khi hết giờ. Sau lần nhập sai thứ năm, thời gian chờ 5 phút được tính từ lần sai đó.

### `GET /api/v1/identity/register`

- `200` hiển thị trang nhập email và nút “Đăng nhập với Google” khi mở lần đầu. Nếu cookie có lượt đăng ký qua email phù hợp, trang hiển thị bước nhập OTP hoặc tạo mật khẩu.
- `?restart=1` mở trang nhập email bằng cách bỏ qua bước đọc trạng thái. Thao tác này giữ cookie hợp lệ hiện có và không xóa trạng thái đang lưu.
- `503` nếu route gặp lỗi khi đọc trạng thái đăng ký. `303` tới `/` nếu đã đăng nhập.

### `POST /api/v1/identity/register/email`

- `email` là chuỗi tối đa 255 ký tự. Server bỏ khoảng trắng ở hai đầu, kiểm tra định dạng và chuẩn hóa về chữ thường.
- `200` gửi OTP đến email chưa có tài khoản và hiển thị trang nhập mã. OTP gồm 6 chữ số ASCII, có hiệu lực 5 phút tính từ lúc gửi. Mỗi mã cho tối đa 5 lần nhập sai.
- `400` nếu email sai, bị bỏ trống hoặc chưa hết thời gian chờ gửi mã cho email đó. Thời gian chờ áp dụng cả khi đổi trình duyệt.
- `409` nếu email đã được sử dụng hoặc lượt đang có yêu cầu xử lý đồng thời. `429` nếu lượt OTP đang bị khóa. `503` nếu không gửi được email hoặc dịch vụ xác minh không khả dụng.

### `POST /api/v1/identity/register/otp/resend`

- Server lấy email từ lượt hiện tại. `200` gửi mã mới sau khi đã đủ 5 phút kể từ lần gửi gần nhất, vô hiệu hóa mã trước và hiển thị lại trang nhập OTP.
- `400` nếu thiếu lượt OTP hợp lệ hoặc yêu cầu gửi lại quá sớm. Trạng thái của lượt OTP đăng ký có thể được giữ đến 30 phút kể từ lần gửi gần nhất để hỗ trợ gửi lại.
- `409` nếu email đã được sử dụng hoặc có yêu cầu đồng thời. `429` nếu lượt OTP đang bị khóa. `503` nếu dịch vụ xác minh hoặc gửi mail gặp lỗi.

### `POST /api/v1/identity/register/otp`

- Gửi `otp` dưới dạng chuỗi 6 chữ số ASCII để giữ được số `0` ở đầu.
- `200` xác minh email, tiêu thụ mã và hiển thị trang tạo mật khẩu. Người dùng có 10 phút để hoàn tất bước tạo mật khẩu.
- `400` nếu mã sai, không đúng định dạng, hết hạn hoặc trạng thái không ở bước xác minh email. Lần nhập sai thứ năm khóa mã và trả `429`. `503` nếu dịch vụ xác minh gặp lỗi.

### `POST /api/v1/identity/register/password`

- `password` và `password_confirmation` phải có giá trị và khớp nhau. Mật khẩu có tối thiểu 6 ký tự, tối đa 72 byte UTF-8 và không chứa ký tự NUL.
- `303` tới `/api/v1/identity/login` sau khi tạo tài khoản Khách hàng ở trạng thái Hoạt động, băm mật khẩu bằng bcrypt và tạo giỏ hàng cùng danh sách yêu thích trống trong một transaction.
- `400` nếu mật khẩu không hợp lệ, bước xác minh đã hết hạn hoặc trạng thái lượt không phù hợp. `409` nếu phát hiện email đã được sử dụng ở bước kiểm tra lại.
- `500` nếu thao tác lưu đăng ký thất bại và transaction được hoàn tác. `503` nếu lỗi thoát ra khỏi tầng xử lý đăng ký.

## Đăng ký và đăng nhập bằng Google

### `GET /api/v1/identity/register/google`

- `303` điều hướng tới Google OpenID Connect. Server tạo cookie đăng ký nếu cần và lưu trạng thái OIDC trong 10 phút. Luồng dùng scope `openid email` và PKCE `S256`.
- Trang đăng ký và đăng nhập dùng chung luồng Google. Khi có cả `login=1` và `return_url=/api/v1/ordering/checkout`, server lưu đích checkout trong lượt OIDC.
- `400` nếu không lưu được trạng thái do xung đột. `409` nếu lượt đang được xử lý. `503` nếu cấu hình Google thiếu hoặc dịch vụ xác minh không khả dụng.

### `GET /api/v1/identity/register/google/callback`

- `state` phải khớp lượt Google còn hạn của cookie đăng ký và chỉ dùng một lần. `code` là mã Google trả khi người dùng chấp thuận. `error` khác rỗng hoặc `email_verified` khác `true` được xử lý như xác thực thất bại.

| Thứ tự tìm tài khoản | Xử lý |
| --- | --- |
| Tìm thấy tài khoản Khách hàng đang Hoạt động theo `sub` | Cấp phiên cho tài khoản đã liên kết. |
| Email đã xác minh trùng tài khoản Khách hàng đang Hoạt động chưa liên kết Google | Lưu `sub` rồi cấp phiên trong cùng transaction, không gửi OTP. |
| Chưa có tài khoản theo `sub` hoặc email đã xác minh | Tạo tài khoản Khách hàng kèm `sub`, giỏ hàng và danh sách yêu thích trống, rồi cấp phiên trong cùng transaction. Tài khoản mới không cần mật khẩu Sobie. |

- Khi thành công, server đặt cookie `storefront_session`, xóa cookie đăng ký và trả `303` tới checkout nếu lượt OIDC bắt đầu từ checkout, hoặc tới `/`.
- `400` nếu cookie hoặc trạng thái không hợp lệ, tham số `state`, `code` hay `error` lặp, người dùng hủy, xác thực thất bại, tài khoản sai vai trò hoặc bị khóa, hoặc email trùng với tài khoản đã liên kết một `sub` khác.
- `409` nếu có yêu cầu đồng thời đang xử lý trạng thái đăng ký của trình duyệt. Nếu hai lượt xung đột trên ràng buộc duy nhất của email hoặc `sub`, server hoàn tác lần ghi thất bại và tra lại tài khoản. `500` nếu thao tác tài khoản hoặc phiên thất bại. `503` nếu dịch vụ xác minh gặp lỗi.

## `GET /api/v1/identity/login`

- `200` hiển thị form đăng nhập bằng mật khẩu, nút Quên mật khẩu, liên kết Google và đăng ký. Sau khi tạo tài khoản bằng email, thông báo “Đăng ký thành công.” có thể hiển thị một lần trong 2 phút khi dùng cùng cookie đăng ký. Nếu không đọc được thông báo, trang vẫn trả `200`.
- `303` nếu đã có phiên storefront hợp lệ, tới checkout khi `return_url` khớp chính xác đường dẫn checkout, hoặc tới `/` trong các trường hợp còn lại. Biểu mẫu mật khẩu và liên kết Google giữ đích checkout khi có.

## Đăng nhập bằng mật khẩu và phiên

- `POST /api/v1/identity/login` chỉ nhận Khách hàng. `POST /api/v1/identity/portal/login` chỉ nhận Nhân viên và Admin. Hai biểu mẫu gửi `identifier` (email hoặc số điện thoại) và `password`. Middleware trả `403` khi thiếu header `Origin`, giá trị là `null` hoặc origin không được phép, trước khi xác thực hoặc gia hạn phiên và truy cập Redis, kể cả request HTMX.
- Thiếu trường trả `400`, sai thông tin hoặc sai cổng trả `401`, tài khoản bị khóa trả `403`. Hai cổng chia sẻ Redis đếm theo IP. Lần thứ sáu trong cửa sổ 60 giây trả `429` trước khi tra mật khẩu. Google không dùng bộ đếm này.
- Portal dùng `/api/v1/identity/portal` làm điểm vào Tổng quan. Cả đăng nhập thành công và mở lại trang đăng nhập với phiên hợp lệ đều dẫn tới điểm vào này.
- Storefront cấp `storefront_session` với hạn trượt 30 phút. Portal cấp `portal_session` với hạn trượt 1 giờ. Đăng xuất xóa phiên hiện tại và cookie của cổng đó. Đổi mật khẩu, đổi vai trò và khóa tài khoản thu hồi tất cả phiên của tài khoản đích.

## Đăng xuất (UC-03)

- Hai `POST` đăng xuất dùng kiểm tra `Origin` Phương án A. Middleware trả `403` nếu thiếu `Origin`, giá trị là `null` hoặc origin không khớp origin của request hay một mục trong `ALLOWED_ORIGINS`. Kiểm tra chạy trước khi xác thực phiên hoặc cập nhật `last_seen_at` và `expires_at`, kể cả với HTMX.
- Với `Origin` hợp lệ, server xóa phiên theo hash cookie và vai trò của cổng. Phản hồi `303` có `Location: /` và làm hết hạn đúng cookie của cổng đó. Kết quả vẫn là `303` khi thiếu cookie, phiên đã hết hạn hoặc đã bị xóa. Cả `303` và `403` đều có `Cache-Control: no-store`.
- Trang chủ, hồ sơ Khách hàng, Tổng quan portal và trang danh sách tài khoản có `Referrer-Policy: strict-origin` khi hiển thị form đăng xuất để trình duyệt gửi `Origin` khi bấm nút.

## Hồ sơ (UC-04)

- Khách hàng thao tác trên hồ sơ của chủ phiên tại `/api/v1/identity/account/profile`. Trang hiển thị mã tài khoản và email ở dạng chỉ xem. POST lưu `name`, `date_of_birth`, `house_number`, `ward`, `city`, `country`, `phone_number` và bỏ qua `email` nếu được gửi. Số điện thoại mới phải đúng định dạng và chưa được tài khoản khác dùng. Đổi số điện thoại không yêu cầu xác minh lại.
- Admin sửa hồ sơ của khách hàng được chọn qua endpoint sửa tài khoản portal của UC-07.

## Đổi mật khẩu (UC-05)

- GET hiển thị form cho tài khoản đã có mật khẩu Sobie. POST kiểm tra mật khẩu hiện tại, tính hợp lệ của mật khẩu mới và ô nhập lại. Nếu mật khẩu mới dưới 6 ký tự hoặc trùng mật khẩu hiện tại, lỗi nằm ở trường `password`. Nếu nhập lại không khớp với mật khẩu mới hợp lệ, lỗi ở trường `password_confirmation` có nội dung “Mật khẩu nhập lại không khớp”.
- Khi đổi thành công, hệ thống băm mật khẩu mới và xóa mọi phiên của tài khoản cùng transaction. Phản hồi làm hết hạn cookie của cổng hiện tại và chuyển tới trang đăng nhập tương ứng với `password_changed=1`.

## Tạo tài khoản (UC-06)

- Admin tạo được cả `customer`, `employee` và `admin`. Form nhận các trường hồ sơ, `role` và `password`. Họ tên, email và số điện thoại là bắt buộc. Ngày sinh bắt buộc với Nhân viên và Admin. Mật khẩu có ít nhất 6 ký tự, tối đa 72 byte UTF-8 và không chứa NUL.
- Khi tạo thành công, hệ thống cấp mã và lưu mật khẩu bcrypt trong cùng transaction. Với Khách hàng, transaction tạo thêm giỏ hàng và danh sách yêu thích trống. Account ở trạng thái Hoạt động, đăng nhập bằng mật khẩu ban đầu và không cần đổi mật khẩu ở lần đầu.
- Admin bootstrap được tạo khi nạp `init.sql`. Để dùng tài khoản ngay, cấu hình `sobie.bootstrap_admin_password_hash` bằng hash bcrypt tương thích với `pgcrypto` khi khởi tạo. Nếu thiếu cấu hình, hệ thống tạo mật khẩu ngẫu nhiên và không công bố. [SQL khởi tạo](../infra/postgres/init.sql)

## Quản lý tài khoản (UC-07, UC-08)

- Admin xem danh sách toàn bộ và sửa tài khoản theo `account_key`. Nhân viên xem danh sách và hồ sơ Khách hàng. Danh sách nhận query `q` và `page`.
- Admin đổi vai trò giữa Nhân viên và Admin. Đổi vai trò cấp lại mã và thu hồi mọi phiên của tài khoản đích. Khi tự đổi vai trò, Admin được đưa về đăng nhập portal. Hệ thống giữ ít nhất một Admin Hoạt động khi đổi vai trò hoặc khóa.
- Nhân viên chỉ khóa được Khách hàng từ trang chi tiết. Admin khóa và mở khóa được tài khoản từ danh sách hoặc trang sửa. `confirm=yes` thực hiện thao tác. Các giá trị khác hủy thao tác và chuyển về trang xuất phát. Khi quay về danh sách, ứng dụng giữ `q` và `page`. Khóa xóa mọi phiên của tài khoản. Khi tự khóa, Admin được chuyển về đăng nhập portal. Sau khi mở khóa, phiên mới được cấp khi đăng nhập lại.

## Quay lại checkout (UC-02 AC-7)

- `GET /api/v1/ordering/checkout` trả `303` đến trang đăng nhập storefront với query `return_url=/api/v1/ordering/checkout` khi chưa có phiên. Đăng nhập bằng mật khẩu hoặc Google thành công đều chuyển về checkout khi luồng khởi đầu từ checkout. Checkout hiển thị giỏ tài khoản. [Sơ đồ checkout](sequence/ordering/get-checkout.md)
- Trình duyệt đọc key `sobie.guest-cart` trong `localStorage` có dạng `{"items":[{"variant_key":"<uuid>","quantity":2}]}`. Checkout thêm `merge_key` là UUID vào bản ghi trước lần gửi đầu tiên và giữ khóa khi thử lại. Khi nhận `200`, trình duyệt xóa bản ghi đã gửi nếu bản ghi chưa bị thay đổi và tải giỏ đã gộp.
- `POST /api/v1/shopping/cart/merge` yêu cầu phiên Khách hàng và `Origin` hợp lệ. Form gửi `merge_key` và hai trường lặp `variant_key`, `quantity` theo từng cặp. `200` trả JSON `items` với `variant_key`, `sku`, `quantity`, `added` và `status` (`merged`, `limited`, `unavailable`). Dòng trùng cộng dồn tối đa bằng tồn kho. Biến thể hết hàng, ngừng bán hoặc không có giá bị bỏ qua. Dữ liệu sai trả `400`; gửi lại cùng khóa và cùng giỏ trả nguyên kết quả; cùng khóa với giỏ khác trả `409`. [Sơ đồ gộp giỏ](sequence/shopping/post-cart-merge.md)
- Với PostgreSQL đã khởi tạo, áp dụng [lệnh cập nhật schema](../infra/postgres/uc02-cart-merge.sql) trước khi bật checkout.

### Câu hỏi mở

- [GD] Module Shopping có chốt dùng key `sobie.guest-cart` và cấu trúc snapshot trên cho trình ghi giỏ vãng lai không?
- [GD] Module Shopping có chốt dùng JSON cho kết quả gộp khi tích hợp các màn hình giỏ về sau không?

## Cấu hình triển khai
- `ALLOWED_ORIGINS` mặc định rỗng. Đặt danh sách origin bổ sung theo dạng `https://host[:port]`, phân cách bằng dấu phẩy. Origin của request dùng scheme và host công khai. Khi có reverse proxy, ứng dụng dùng `X-Forwarded-Proto` và `X-Forwarded-Host` nếu được gửi. Proxy phải ghi đè các header này khi chuyển tiếp request.
- **Cấu hình Redis.** [`REDIS_URL`](../app/config/settings.py) được truyền trực tiếp cho Redis. Nếu Redis yêu cầu mật khẩu, URL phải có thông tin xác thực phù hợp. Lỗi truy cập kho trạng thái có thể khiến các bước đăng ký trả `503`.
