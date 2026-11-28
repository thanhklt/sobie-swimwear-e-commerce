# POST /api/v1/identity/portal/login

UC-02 · Đăng nhập bằng mật khẩu portal.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as SessionService
    participant Redis
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi Origin, identifier và password
    break Origin thiếu, null hoặc không được phép
        Route-->>Browser: 403 trước khi gia hạn phiên hoặc đếm Redis
    end
    alt Phiên portal đã hợp lệ
        Route-->>Browser: 303 tới /api/v1/identity/portal
    else Chưa có phiên
        Route->>Service: Xác thực tại portal
        Service->>Redis: Đếm lần gửi mật khẩu theo IP, chung với storefront
        alt Vượt giới hạn
            Service-->>Route: 429
        else Trong giới hạn
            Service->>Data: Kiểm tra mật khẩu, vai trò Nhân viên hoặc Admin và trạng thái
            opt Tài khoản hợp lệ
                Service->>Data: Lưu hash mã phiên và thời hạn 1 giờ
            end
            Service-->>Route: Mã phiên hoặc lỗi biểu mẫu
        end
        Route-->>Browser: 303 tới /api/v1/identity/portal kèm portal_session, hoặc lỗi
    end
```
