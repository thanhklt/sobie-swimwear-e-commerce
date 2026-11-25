# POST /api/v1/identity/register/email

UC-01 Main 2–3, E1, E3.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router storefront
    participant Service as IdentityService
    participant Repo as IdentityRepository
    participant DB as PostgreSQL
    participant Redis as Trạng thái đăng ký (Redis)
    participant Mail as Dịch vụ email
    Browser->>Route: Gửi email kèm Origin
    break Origin thiếu, null hoặc không được phép
        Route-->>Browser: HTTP 403 trước khi xác thực phiên hoặc gọi dịch vụ
    end
    Route->>Service: Bắt đầu đăng ký cho trình duyệt này
    Service->>Service: Kiểm tra định dạng email
    alt Email không hợp lệ
        Service-->>Route: Lỗi tại trường email
    else Email hợp lệ
        Service->>Repo: Tìm tài khoản theo email
        Repo->>DB: Đọc identity.account
        alt Email đã có tài khoản
            Service-->>Route: Email đã được sử dụng
        else Email còn trống
            Service->>Redis: Ghi trạng thái OTP và giữ chỗ gửi theo email
            Service->>Mail: Gửi mã xác minh có hiệu lực 5 phút
            Service-->>Route: Yêu cầu nhập OTP
        end
    end
    Route-->>Browser: Trả biểu mẫu tương ứng
```
