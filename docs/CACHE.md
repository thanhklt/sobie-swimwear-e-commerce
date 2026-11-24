# Redis trong module identity

## Dữ liệu đăng ký của UC-01

Một khách có thể đóng tab, gửi lại biểu mẫu hoặc quay lại từ Google bằng một request khác. Trong các bước này, Redis giữ tiến độ của lượt đăng ký cho đến khi khách hoàn tất hoặc lượt đó hết hạn. Trình duyệt giữ mã lượt ngẫu nhiên trong cookie `HttpOnly`, `Secure`, `SameSite=Lax`.

| Khi nào ghi | Dữ liệu và mục đích | Khi nào hết hiệu lực |
|---|---|---|
| Gửi OTP đăng ký | Mã lượt gắn với trình duyệt, email, mục đích đăng ký, giá trị kiểm tra OTP được bảo vệ bằng khóa bí mật, thời điểm gửi/hết hạn và số lần nhập sai. Các giá trị này ràng buộc mã với đúng lượt xác minh. | OTP có hiệu lực 300 giây từ lúc gửi. Xác minh thành công sẽ chuyển lượt sang bước tạo mật khẩu. Mã cũ mất hiệu lực sau khi cấp mã mới. |
| Gửi OTP tới cùng địa chỉ | Một khóa riêng cho email đã chuẩn hóa và mục đích gửi, dùng chung giữa các trình duyệt. | Khóa chặn gửi lại trong 300 giây kể từ lần gửi gần nhất. |
| Xác minh OTP thành công | Lượt đã xác minh được email và có quyền gửi mật khẩu từ cùng trình duyệt. | Quyền ngắn hạn dùng một lần. Nếu hết hạn, khách xác minh email lại. |
| Chuyển trình duyệt sang Google | `state` ràng buộc callback với lượt ban đầu; `nonce` đối chiếu với ID token; PKCE verifier dùng khi đổi mã ủy quyền. | Dùng một lần cho callback hoặc tự hết hạn. |
| Google xác nhận email trùng tài khoản Sobie | Định danh Google đang chờ liên kết, khóa tài khoản hiện có, email đang lưu và trạng thái OTP cho lần liên kết. | Khi xác minh thành công, Sobie ghi liên kết và cấp phiên cho tài khoản hiện có. Quá hạn, khách bắt đầu lại theo hướng dẫn của màn hình. |
| Hoàn tất đăng ký mới | Dấu hiệu đăng ký thành công để màn hình đăng nhập hiển thị thông báo sau redirect. | Xóa sau khi hiển thị hoặc khi hết hạn. |

Mật khẩu khách nhập, mã OTP gốc và khóa bí mật ứng dụng không được đưa vào dữ liệu Redis. Tài khoản, liên kết Google đã xác nhận, giỏ hàng, danh sách yêu thích và phiên đăng nhập có bản ghi lâu dài trong PostgreSQL. Khi Redis mất dữ liệu giữa luồng, khách có thể bắt đầu lại; các tài khoản đã tạo vẫn tồn tại.

## Dự kiến cho UC-02

Spec đăng nhập yêu cầu bộ đếm số yêu cầu đăng nhập **bằng mật khẩu** từ cùng một IP, áp dụng cho hai cổng. Trong một phút, năm yêu cầu đầu được xử lý; từ yêu cầu thứ sáu, Sobie trả HTTP 429 trước khi kiểm tra mật khẩu. Luồng Google không tham gia bộ đếm. Tên khóa và thao tác Redis sẽ được ghi khi UC-02 được triển khai.

Nguồn nghiệp vụ: [UC-01 · Đăng ký](../specs/use-cases/identity/UC-01-register-account.md) và [UC-02 · Đăng nhập](../specs/use-cases/identity/UC-02-login.md).
