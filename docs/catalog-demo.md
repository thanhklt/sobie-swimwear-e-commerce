# Catalog demo

Phạm vi đã chốt ngày 26/11/2026: catalog và UI HTML; không mở rộng inventory, ordering, promotion, reporting, shopping hoặc identity. Không thêm redirect /about, /policy, /faq. Trang thông tin dùng /api/v1/catalog/pages/{slug}.

## Chạy

1. Cài dependency đã khóa: `poetry install --no-root`.
2. Chuẩn bị PostgreSQL bằng hướng dẫn hiện có trong README. Database mới chạy `infra/postgres/init.sql` rồi `seed.sql`. Database hiện có chạy các file trong `infra/postgres/migrations/` theo thứ tự; không reset volume.
3. Chép `.env.example` thành `.env`, điền DATABASE_URL đúng database thực tế (Compose mặc định dùng sobieDB), SECRET_KEY và các cấu hình có sẵn.
4. Đặt `CATALOG_DEMO=true` trong `.env` để dùng vai trò Nhân viên không đăng nhập. Chỉ bật trên máy demo.
5. Chạy `poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000`.
6. Mở http://127.0.0.1:8000/api/v1/catalog/home hoặc http://127.0.0.1:8000/api/v1/catalog/staff/products.

CATALOG_DEMO mặc định false: staff dùng require_roles(employee) và portal_session. Không triển khai đăng nhập mới. URL gốc / giữ response API hiện có.

## Có thể thử trực tiếp

- Đọc sản phẩm seed trên trang chủ, theo danh mục, tìm tên/mô tả không phân biệt dấu; lọc, sắp xếp giá gốc, phân trang.
- Xem gallery, mô tả, khoảng giá từ biến thể ACTIVE có giá; chọn/bỏ chọn màu và size.
- Quản lý năm loại taxonomy; chặn tên trống/trùng và xóa mục đang dùng.
- Tạo sản phẩm INACTIVE cùng ảnh URL và bộ sưu tập; sửa thông tin và gallery khi sản phẩm chưa có biến thể.
- Sản phẩm có biến thể vẫn được sửa mô tả; các trường còn lại giữ nguyên.
- Xem danh sách biến thể, giá theo size, trạng thái sản phẩm và biểu mẫu cho từng endpoint.
- POST thành công redirect 303; lỗi trả HTML có thông báo và giữ dữ liệu nhập (form sản phẩm hoặc bảng dữ liệu vừa gửi).
- Trang thông tin: about, policies, faq. Nội dung chính sách và bảng size chính thức chưa được cung cấp, không tạo nội dung kinh doanh giả.

## Giới hạn do loại các module ngoài phạm vi

Đây là demo catalog có giới hạn, chưa đáp ứng toàn bộ AC UC-09–17. Các kiểm tra an toàn cần service ngoài catalog không được thay bằng dữ liệu giả hoặc đọc trực tiếp bảng module khác:

| Thao tác | Hành vi hiện tại |
|---|---|
| Tạo biến thể | 503: inventory chưa thể tạo dòng tồn kho trong cùng transaction |
| Đổi giá, trạng thái biến thể; sửa cấu trúc/gallery/trạng thái sản phẩm có biến thể | 503: chưa xác minh được lịch sử nhập CONFIRMED |
| Xóa sản phẩm/biến thể | 503: chưa kiểm tra lịch sử đơn, nhập kho, khuyến mãi và dọn tồn |
| Đổi tên taxonomy liên quan sản phẩm có biến thể | 503: chưa xác minh được khóa sau nhập kho |
| Mở bán sản phẩm mới chưa có biến thể | 409: thiếu điều kiện mở bán |
| Tồn kho, giảm giá, bán chạy, giỏ hàng/yêu thích | Hiển thị chưa tích hợp; không giả báo còn/hết hàng hoặc thành công |
| Redis catalog_version | Chưa tích hợp; request đọc DB trực tiếp, không cache HTML hoặc dữ liệu catalog |

Gallery nhận URL ảnh http/https hoặc /static/, không upload file. Xóa ảnh bằng cách bỏ URL và đánh lại thứ tự liên tiếp từ 1. Mọi thao tác ghi có transaction; dữ liệu người dùng được bind parameter; tên bảng và cột động lấy từ allowlist.

Tên sản phẩm và taxonomy có unique index không phân biệt hoa/thường. Migration từ chối nếu dữ liệu cũ vi phạm; cần xử lý dữ liệu trùng trước khi chạy lại, không tự xóa hoặc đổi tên dữ liệu.

## Tài liệu

Mỗi endpoint có một sequence tại docs/sequence/C01–C21. C21 là POST /api/v1/catalog/staff/products/{product_key}/variants/{variant_key}/status được developer đồng ý bổ sung. Những nhánh chưa hỗ trợ được mô tả rõ bằng phản hồi 503.

Không có giả định nghiệp vụ mới cần chốt. Các giới hạn tích hợp ở trên xuất phát từ quyết định bỏ phần ngoài catalog. Không thêm test tự động theo yêu cầu; kiểm tra import/template và gọi thử HTTP với PostgreSQL tách biệt.
