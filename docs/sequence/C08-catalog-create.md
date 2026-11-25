# C08: POST /api/v1/catalog/staff/products/new

Endpoint trả HTML; vai trò Nhân viên cho đường dẫn staff. CATALOG_DEMO=true bỏ đăng nhập chỉ trong môi trường demo.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Catalog Route
    participant Service as Catalog Service
    participant Repository as Catalog Repository
    participant DB as PostgreSQL catalog
    Browser->>Route: POST /api/v1/catalog/staff/products/new
    Route->>Route: Kiểm tra demo hoặc quyền employee
    Route->>Route: Kiểm tra Origin và parse form
    Route->>Service: Dữ liệu đầu vào
    Service->>Service: Validate dữ liệu và nghiệp vụ
    Service->>DB: BEGIN
    alt Cần service ngoài catalog chưa triển khai
        Service-->>Route: Chưa hỗ trợ (503), không ghi
        Service->>DB: ROLLBACK
    else Thao tác chỉ cần catalog
        Service->>Repository: Kiểm tra, khóa và ghi dữ liệu
        Repository->>DB: SQL parameterized
        DB-->>Repository: Kết quả
        Repository-->>Service: Kết quả
        Service->>DB: COMMIT
        Service-->>Route: Thành công
    end
    Route-->>Browser: 303 khi lưu thành công; HTML 400/404/409/503 khi lỗi
```
