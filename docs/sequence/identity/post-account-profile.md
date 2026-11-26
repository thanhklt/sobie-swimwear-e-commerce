# POST /account/profile

UC-04 · Lưu hồ sơ của mình.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as AccountService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi các trường hồ sơ được sửa và csrf_token
    Route->>Route: Kiểm tra CSRF
    Route->>Service: Cập nhật hồ sơ của chủ phiên Khách hàng
    Service->>Service: Bỏ qua email nếu được gửi và kiểm tra dữ liệu được sửa
    Service->>Data: Khóa tài khoản, kiểm tra phiên và số điện thoại trùng
    Service->>Data: Lưu các trường được sửa trong transaction
    Service-->>Route: Kết quả xử lý nghiệp vụ
    Route-->>Browser: 303 về hồ sơ kèm thông báo hoặc 400 lỗi theo trường
```
