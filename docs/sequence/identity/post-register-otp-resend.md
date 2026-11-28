# POST /api/v1/identity/register/otp/resend

UC-01 4a, E5, AC-18.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router storefront
    participant Service as EmailRegistrationService
    participant Store as ChallengeStore
    participant Redis as Trạng thái đăng ký (Redis)
    participant Notification as notification
    participant Mail as Dịch vụ email
    Browser->>Route: Yêu cầu gửi lại OTP kèm Origin
    break Origin thiếu, null hoặc không được phép
        Route-->>Browser: HTTP 403 trước khi xác thực phiên hoặc gọi dịch vụ
    end
    Route->>Service: Gửi lại cho lượt đăng ký hiện tại
    Service->>Store: Đọc trạng thái lượt đăng ký
    Store->>Redis: GET khóa của lượt
    alt Lượt hợp lệ, đã đủ thời gian chờ và email chưa được sử dụng
        Service->>Store: Giữ chỗ gửi theo email
        Store->>Redis: Lưu trạng thái chờ gửi và giữ chỗ cooldown
        opt Giữ chỗ thành công
            Service->>Notification: facade.send_email với mẫu registration_otp
            Notification->>Mail: Gửi mã mới tới email của lượt đăng ký
            opt Gửi thành công
                Service->>Store: Lưu mã mới và đặt lại thời gian chờ
                Store->>Redis: Lưu trạng thái và cooldown mới
            end
        end
    else Không đủ điều kiện gửi lại
        Service->>Service: Chuẩn bị kết quả từ chối
    end
    opt Kết quả ở bước nhập OTP
        Service->>Store: Đọc TTL cooldown theo email
        Store->>Redis: PTTL khóa cooldown OTP
        Redis-->>Store: Mili giây còn lại
        Store-->>Service: Số giây còn lại
    end
    Service-->>Route: Kết quả bước đăng ký
    Route-->>Browser: Biểu mẫu tương ứng, đếm ngược và khóa nút gửi lại nếu còn thời gian chờ OTP
```
