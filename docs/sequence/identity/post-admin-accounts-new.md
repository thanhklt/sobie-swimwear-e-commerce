# POST /admin/accounts/new

UC-06 · Tạo tài khoản.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as IdentityService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi vai trò, hồ sơ, mật khẩu và csrf_token
    Route->>Service: Kiểm tra CSRF và xác nhận quyền Admin trong transaction
    Service->>Data: Kiểm tra dữ liệu, cấp mã, băm mật khẩu và ghi account
    Service->>Data: Nếu vai trò Khách hàng, gọi ShoppingService tạo cart và wishlist trong cùng transaction
    Service-->>Route: Kết quả xử lý nghiệp vụ
    Route-->>Browser: 303 về danh sách tài khoản hoặc 400 lỗi theo trường
```
