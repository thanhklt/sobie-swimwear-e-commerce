# POST /api/v1/identity/portal/accounts/{account_key}/lock

UC-08 · Khóa tài khoản.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as AdminAccountService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi Origin, confirm và ngữ cảnh danh sách nếu có
    break Origin thiếu, null hoặc không được phép
        Route-->>Browser: 403 trước khi xác thực hoặc gia hạn phiên
    end
    Route->>Route: Kiểm tra phiên và vai trò
    alt Hủy xác nhận
        Route-->>Browser: 303 về danh sách hoặc trang chi tiết đã gửi form
    else Xác nhận khóa
        Route->>Service: Khóa tài khoản trong phạm vi được phép
        Service->>Data: Kiểm tra quyền và bảo toàn Admin Hoạt động cuối cùng
        Service->>Data: Ghi LOCKED và xóa mọi phiên trong cùng transaction
        Service-->>Route: Kết quả xử lý
        Route-->>Browser: 303 về trang xuất phát hoặc đăng nhập lại khi tự khóa, 400 nếu vướng ràng buộc Admin, 403 nếu ngoài phạm vi
    end
```
