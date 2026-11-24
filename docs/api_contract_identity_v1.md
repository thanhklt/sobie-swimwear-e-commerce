# API Contract Identity v1

Tài liệu mô tả 9 endpoint storefront đã đăng ký trong [router Identity](../app/modules/identity/router.py). `v1` là phiên bản tài liệu. Đường dẫn giữ nguyên như router, không có tiền tố `/api/v1`.

Nguồn nghiệp vụ gồm [UC-01 Đăng ký tài khoản](../specs/use-cases/identity/UC-01-register-account.md) và [UC-02 Đăng nhập](../specs/use-cases/identity/UC-02-login.md). Các luồng dùng mật khẩu để đăng nhập, đăng nhập portal và các chức năng thuộc UC-03–UC-08 chưa có endpoint trong router này.

## Quy ước trao đổi HTTP

- Các `GET` nhận tham số qua query string. Các `POST` nhận biểu mẫu HTML với `Content-Type: application/x-www-form-urlencoded`.
- Response hiển thị trang là `text/html`. Lỗi nghiệp vụ hiển thị thông báo trên trang. Điều hướng dùng HTTP `303` với header `Location`.
- Phản hồi do router dựng có `Cache-Control: no-store` và `Referrer-Policy: no-referrer`.
- Cookie `__Host-sobie-registration` giữ lượt xác minh của trình duyệt. Cookie có `Path=/`, `Max-Age=3600`, `Secure`, `HttpOnly`, `SameSite=Lax`. Các bước trong cùng lượt dùng cùng cookie. Thời hạn OTP và trạng thái nghiệp vụ được tính riêng ở server.
- Mọi `POST` bên dưới đều yêu cầu `csrf_token` lấy từ input ẩn trong biểu mẫu cùng với cookie đăng ký tương ứng. Cookie hoặc token thiếu, sai hoặc không khớp trả `403` và trang đăng ký.
- Phiên storefront hợp lệ thường trả `303` tới `/`. Callback Google kiểm tra tham số trùng trước khi kiểm tra phiên.
- Khi đăng nhập Google thành công, server đặt cookie `storefront_session` (`Path=/`, `Secure`, `HttpOnly`, `SameSite=Lax`) và xóa cookie đăng ký. Phiên Khách hàng phía server hết hạn sau 30 phút không hoạt động. Request xác thực thành công gia hạn phiên thêm 30 phút.

## Danh sách endpoint

| Method và đường dẫn | Input | Thành công | Sequence |
| --- | --- | --- | --- |
| `GET /register` | Query `restart` tùy chọn | `200` trang đăng ký hoặc bước xác minh đang dở | [Sơ đồ](sequence/identity/get-register.md) |
| `POST /register/email` | Form `email`, `csrf_token` | `200` trang nhập OTP | [Sơ đồ](sequence/identity/post-register-email.md) |
| `POST /register/otp/resend` | Form `csrf_token` | `200` trang nhập OTP mới | [Sơ đồ](sequence/identity/post-register-otp-resend.md) |
| `POST /register/otp` | Form `otp`, `csrf_token` | `200` trang tạo mật khẩu | [Sơ đồ](sequence/identity/post-register-otp.md) |
| `POST /register/password` | Form `password`, `password_confirmation`, `csrf_token` | `303` tới `/login` | [Sơ đồ](sequence/identity/post-register-password.md) |
| `GET /register/google` | Query `login` tùy chọn | `303` tới Google | [Sơ đồ](sequence/identity/get-register-google.md) |
| `GET /register/google/callback` | Query `state`, `code` hoặc `error` | `303` tới `/login` hoặc `/`, hoặc `200` trang nhập OTP liên kết | [Sơ đồ](sequence/identity/get-register-google-callback.md) |
| `POST /register/google/link/otp` | Form `otp`, `csrf_token` | `303` tới `/` và cấp cookie phiên | [Sơ đồ](sequence/identity/post-register-google-link-otp.md) |
| `GET /login` | Không có tham số | `200` trang đăng nhập | [Sơ đồ](sequence/identity/get-login.md) |

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
- `303` tới `/login` sau khi tạo tài khoản Khách hàng ở trạng thái Hoạt động, băm mật khẩu bằng bcrypt và tạo giỏ hàng cùng danh sách yêu thích trống trong một transaction.
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
| Email đã xác minh chưa có tài khoản và lượt cho phép đăng ký | `303` tới `/login` sau khi tạo tài khoản Google mới, giỏ hàng và danh sách yêu thích trống. Tài khoản được tạo không cần mật khẩu Sobie. |

- `400` nếu thiếu cookie hoặc trạng thái hợp lệ, tham số `state`, `code` hay `error` lặp, người dùng hủy, xác thực thất bại, tài khoản không đủ điều kiện, lượt chỉ đăng nhập không tìm được tài khoản hoặc yêu cầu gửi OTP đang trong thời gian chờ.
- `409` nếu trạng thái thay đổi khi chuẩn bị gửi OTP liên kết. `500` nếu thao tác với tài khoản hoặc phiên thất bại. `503` nếu gửi OTP liên kết hoặc dịch vụ xác minh gặp lỗi.

### `POST /register/google/link/otp`

- `otp` là chuỗi 6 chữ số ASCII. Mã có hiệu lực 5 phút và tối đa 5 lần nhập sai. Trang liên kết có biểu mẫu xác minh và liên kết bắt đầu lại.
- `303` tới `/` sau khi xác minh mã, liên kết `sub` với tài khoản Sobie và cấp phiên storefront trong cùng transaction.
- `400` nếu mã sai, hết hạn, hết lượt thử, không có lượt liên kết phù hợp hoặc tài khoản không còn đủ điều kiện. `500` nếu lưu liên kết hoặc tạo phiên thất bại. `503` nếu dịch vụ xác minh gặp lỗi.

## `GET /login`

- `200` hiển thị trang đăng nhập với liên kết Google và đăng ký. Sau khi tạo tài khoản, thông báo “Đăng ký thành công.” có thể hiển thị một lần trong 2 phút khi dùng cùng cookie đăng ký. Nếu không đọc được thông báo, trang vẫn trả `200`.
- `303` tới `/` nếu đã có phiên storefront hợp lệ. Router hiện chưa cung cấp `POST /login`.

## Các điểm cần đối chiếu khi review

- **UC-02 và giao diện hiện tại.** UC-02 mô tả đăng nhập bằng mật khẩu và nút “Quên mật khẩu” ở storefront. [Template hiện tại](../app/modules/identity/templates/login.html) chỉ có liên kết Google và đăng ký.
- **Cấu hình Redis.** [`REDIS_URL`](../app/config/settings.py) được truyền trực tiếp cho Redis. Nếu Redis yêu cầu mật khẩu, URL phải có thông tin xác thực phù hợp. Lỗi truy cập kho trạng thái có thể khiến các bước đăng ký trả `503`.
