# GET /register

UC-01 Main 1, 1a.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router storefront
    participant Google as Google OIDC
    Browser->>Route: Mở trang đăng ký
    Route->>Route: Đọc phiên storefront do middleware xác thực
    alt Có phiên hợp lệ
        Route-->>Browser: Chuyển về trang chủ
    else Khách vãng lai
        Route-->>Browser: Biểu mẫu đăng ký qua email hoặc Google
    end
```
