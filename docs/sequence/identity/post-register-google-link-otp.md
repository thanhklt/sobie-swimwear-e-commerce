# POST /register/google/link/otp

UC-01 E1, AC-16 và UC-02 1d.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router storefront
    participant Service as IdentityService
    participant Repo as IdentityRepository
    participant DB as PostgreSQL
    participant Redis as Trạng thái đăng ký (Redis)
    participant Google as Google OIDC
    Browser->>Route: Nộp OTP liên kết
    Route->>Service: Xác minh lượt liên kết Google
    Service->>Redis: Kiểm tra lượt, mã và hạn dùng
    alt Xác minh thất bại
        Route-->>Browser: Báo lỗi xác minh
    else OTP đúng
        Service->>Repo: Kiểm tra lại tài khoản, vai trò, email và liên kết
        Repo->>DB: Đọc tài khoản trong transaction
        alt Khách hàng hoạt động và còn đủ điều kiện
            Service->>Repo: Liên kết sub và cấp phiên storefront
            Repo->>DB: Lưu liên kết và phiên cùng transaction
            Route-->>Browser: Đặt cookie phiên và chuyển trang
        else Tài khoản không còn đủ điều kiện
            Route-->>Browser: Từ chối liên kết và đăng nhập
        end
    end
```
