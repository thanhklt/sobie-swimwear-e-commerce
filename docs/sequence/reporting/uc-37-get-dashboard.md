# UC-37 — GET /admin/dashboard

Route phục vụ cả khi mở dashboard và khi lọc theo kỳ. Hai tham số `start_date` và `end_date` nhận ngày dạng `dd/mm/yyyy` hoặc `YYYY-MM-DD`. Khoảng ngày bao gồm cả ngày cuối theo `Asia/Ho_Chi_Minh`.

```mermaid
sequenceDiagram
    actor Employee as Nhân viên
    participant Session as SessionMiddleware
    participant Route as Reporting router
    participant Report as Reporting service
    participant Ordering as Ordering service → repository
    participant Inventory as Inventory service → repository
    participant Catalog as Catalog service → repository
    participant DB as PostgreSQL

    Employee->>Session: GET /admin/dashboard, có thể kèm bộ lọc
    Session->>Route: Phiên của portal quản trị
    Route->>Route: Kiểm tra vai trò Nhân viên và khoảng ngày
    alt Phiên hoặc vai trò không hợp lệ
        Route-->>Employee: Xử lý từ chối qua handler dùng chung
    else Khoảng ngày sai và request HTMX
        Route-->>Employee: Cập nhật vùng lỗi, giữ kết quả kỳ trước
    else Kỳ hợp lệ hoặc tải lại trang với kỳ trước
        Route->>Report: get_dashboard(kỳ báo cáo)
        Report->>Ordering: get_sales_stats(kỳ) lấy số liệu bán theo ngày giao và số đơn theo ngày tạo
        Ordering->>DB: Đọc dữ liệu đơn
        DB-->>Ordering: Kết quả tổng hợp
        Ordering-->>Report: Doanh thu, giá vốn, số lượng và trạng thái
        Report->>Inventory: get_stock() lấy tồn kho thấp, get_purchase_totals(kỳ) tính tiền nhập theo ngày lập
        Inventory->>DB: Đọc tồn kho và phiếu đã xác nhận
        DB-->>Inventory: Kết quả tổng hợp
        Inventory-->>Report: Biến thể tồn thấp và tiền nhập
        Report->>Catalog: get_variants(ids) tra tên, mã sản phẩm và SKU cho mọi trạng thái
        Catalog->>DB: Đọc sản phẩm và biến thể
        DB-->>Catalog: Thông tin biến thể
        Catalog-->>Report: Thông tin hiển thị
        Report-->>Route: Sáu chỉ số, gồm Top 10 theo sản phẩm
        Route-->>Employee: HTML đầy đủ hoặc mảnh HTMX, no-store
    end
```
