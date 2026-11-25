# GET /api/v1/identity/register/google

UC-01 1b.1 và UC-02 1c, AC-7.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router storefront
    participant Service as IdentityService
    participant Redis as Trạng thái đăng ký (Redis)
    participant Google as Google OIDC
    Browser->>Route: Chọn Google, kèm login và return_to nếu bắt đầu từ checkout
    Route->>Service: Khởi tạo lượt OIDC
    Service->>Redis: Lưu chế độ, đích checkout nếu có, nonce và PKCE verifier theo cặp trình duyệt và state
    Service-->>Route: URL ủy quyền Google
    Route-->>Browser: Chuyển hướng
    Browser->>Google: Xác thực với Google
```
