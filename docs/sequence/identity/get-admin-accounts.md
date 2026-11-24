# GET /admin/accounts

UC-07 · Danh sách và tìm kiếm tài khoản.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as IdentityService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Mở danh sách hoặc gửi q và page
    Route->>Service: Xác thực phiên Admin
    Service->>Data: Truy vấn trực tiếp danh sách tài khoản và vai trò có phân trang
    Service-->>Route: Dữ liệu và trạng thái phiên
    Route-->>Browser: 200 danh sách hoặc thông báo không tìm thấy
```
