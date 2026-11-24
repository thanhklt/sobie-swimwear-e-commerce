# POST /logout

UC-03 · Đăng xuất storefront.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as IdentityService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi csrf_token cùng storefront_session
    Route->>Service: Kiểm tra CSRF
    Service->>Data: Xóa dòng phiên theo hash cookie storefront và vai trò Khách hàng
    Service-->>Route: Kết quả xử lý nghiệp vụ
    Route-->>Browser: 303 / và xóa cookie storefront_session
```
