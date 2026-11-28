# GET /

Trang chủ catalog render với dữ liệu mẫu tạm thời từ `catalog/home_sample.py`. UC-09 sẽ thay nguồn dữ liệu trong service.

```mermaid
sequenceDiagram
    actor Browser as Trình duyệt
    participant Main as main.root
    participant Router as catalog.router
    participant Service as catalog.service
    participant Sample as catalog.home_sample
    participant Render as Jinja
    Browser->>Main: GET /
    alt Accept chứa text/html
        Main->>Router: storefront_home(request)
        Router->>Service: get_home_page()
        Service->>Sample: Đọc dữ liệu mẫu
        Sample-->>Service: HomePage
        Service-->>Router: HomePage
        Router->>Render: catalog/home.html + HomePage + request
        Render-->>Router: HTML (khu vực tài khoản dựa trên phiên middleware đã xác thực)
        Router-->>Main: HTML (private, no-cache; Vary: Accept)
        Main-->>Browser: 200 HTML
    else Accept khác
        Main-->>Browser: 200 JSON (Vary: Accept)
    end
```
