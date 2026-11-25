# POST /admin/accounts/{key}/edit

UC-04/07 · Lưu hồ sơ và vai trò trong một lần gửi.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Route as Router và middleware
    participant Service as IdentityService
    participant Data as Repository và PostgreSQL
    Browser->>Route: Gửi hồ sơ, vai trò nội bộ nếu có và csrf_token
    Route->>Service: Kiểm tra CSRF, khóa bảo vệ Admin và xác nhận quyền trong transaction
    Service->>Data: Kiểm tra hồ sơ, điều kiện chuyển vai trò và Admin hoạt động cuối cùng
    Service->>Data: Lưu hồ sơ trong transaction. Nếu vai trò đổi, cấp mã mới, lưu vai trò và xóa mọi phiên trong cùng transaction
    alt Lưu thành công
        Service-->>Route: Kết quả lưu
        Route-->>Browser: 303 về trang sửa hoặc đăng nhập lại khi tự đổi vai trò
    else Lỗi nghiệp vụ
        Service-->>Route: Lỗi biểu mẫu
        Route-->>Browser: 400 kèm lỗi, không hiện thông báo đã lưu
    else Lỗi khi lưu
        Service->>Data: Hoàn tác transaction
        Service-->>Route: Lỗi sau khi thoát transaction
        Route-->>Browser: 500 với trang HTML báo cập nhật không thành công
    end
```
