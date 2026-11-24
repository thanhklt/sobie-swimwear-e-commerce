# POST /admin/accounts/{key}/unlock

UC-08 · Mở khóa tài khoản.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as IdentityService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi xác nhận và csrf_token
    Route->>Service: Kiểm tra CSRF và xác nhận quyền Admin trong transaction
    Service->>Data: Chuyển tài khoản sang ACTIVE
    Service-->>Route: Kết quả xử lý nghiệp vụ
    Route-->>Browser: 303 về trang chi tiết, phiên mới được cấp khi đăng nhập lại
```
