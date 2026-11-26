# GET /admin/accounts/new

UC-06 · Mở form tạo tài khoản.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as SessionService
    Browser->>Route: Mở trang với phiên Admin
    Route->>Service: Xác thực phiên và quyền Admin
    Service-->>Route: Trạng thái phiên
    Route->>Route: Chuẩn bị biểu mẫu có ba vai trò cố định
    Route-->>Browser: 200 biểu mẫu tạo tài khoản có CSRF
```
