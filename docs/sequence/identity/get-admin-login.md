# GET /api/v1/identity/portal/login

UC-02 · Hiển thị đăng nhập portal.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as SessionService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Mở trang đăng nhập quản trị
    Route->>Service: Middleware kiểm tra portal_session nếu có
    Service->>Data: Đọc và gia hạn phiên hợp lệ
    Service-->>Route: Dữ liệu và trạng thái phiên
    Route-->>Browser: 200 strict-origin và biểu mẫu đăng nhập hoặc 303 /api/v1/identity/portal nếu đã có phiên
```
