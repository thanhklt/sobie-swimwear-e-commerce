# Kế hoạch sửa bộ kiểm thử UC-04 · Cập nhật hồ sơ khách hàng

**Trạng thái** Đã thực thi và kiểm chứng.

Đối chiếu [đặc tả UC-04](../../specs/use-cases/identity/UC-04-update-customer-profile.md), [helper kiểm thử](../../tests/identity/identity_support.py) và [bộ test UC-04](../../tests/identity/test_uc04_profile.py).

## Mốc kiểm thử

- Lần chạy nguyên trạng trên PostgreSQL tạm lỗi cả 5 ca tại bước đăng nhập. `identity_support.login()` gọi `post(client, page, path, ...)`, trong khi helper UC-01 hiện nhận `post(client, path, ...)`.
- Lần chạy có helper tương thích trong bộ nhớ đạt 7 ca gồm 5 ca sẵn có và 2 ca đối chiếu bổ sung. Bản sửa chính thức cần chạy bằng helper trong repo.

## Các bước sửa

1. Đưa helper HTTP cấp thấp `post(client, path, *, headers=None, **data)` vào `tests/identity/identity_support.py`. Giữ hành vi mặc định gửi `Origin` cùng site, hỗ trợ truyền header tường minh và trả nguyên phản hồi redirect. Chuyển UC-01 và UC-02 sang import helper dùng chung để tránh phụ thuộc giữa các file test.
2. Trong cùng module, thêm helper gửi CSRF token của trình duyệt. Mã hiện tại tạo token từ cookie `__Host-sobie-registration` và dùng chung giá trị giữa các biểu mẫu khi cookie còn hiệu lực. Phiên đăng nhập storefront và portal được xác thực riêng. Đọc hidden input `csrf_token` từ một trang đã tải bằng cùng HTTP client rồi gửi token cùng các trường của POST. `submit` tải trang đích trước khi gửi. Đăng nhập và đăng xuất dùng helper cấp thấp với `Origin`. Với ca kiểm tra quyền, lấy token hợp lệ từ một trang mà tác nhân được mở để lỗi CSRF thiếu không che lỗi quyền.
3. Sửa UC-04 cùng các caller bị ảnh hưởng ở UC-05 đến UC-08. Rà cả các ca UC-06, UC-07 và UC-08 gọi trực tiếp chữ ký ba đối số. Giữ nguyên cơ chế truyền header tùy ý ở các ca kiểm tra `Origin` của UC-01 và UC-02.
4. Siết các khẳng định của UC-04 theo AC. Với AC-1, dùng ngày sinh khác dữ liệu seed và kiểm tra toàn bộ trường đã đổi trong phản hồi GET và PostgreSQL. Với AC-2, kiểm tra email và số điện thoại mới đăng nhập được sau khi đăng xuất và email cũ bị từ chối. Với AC-3 và AC-4, kiểm tra lỗi nằm cạnh trường tương ứng và so sánh toàn bộ hồ sơ trước và sau. Với AC-5, xác nhận tài khoản được chọn đổi dữ liệu, khách thấy kết quả và mã `KH-` giữ nguyên.

## Nghiệm thu

1. Khởi tạo database PostgreSQL riêng tên `uc01test` từ `infra/postgres/init.sql` và nạp tiếp `infra/postgres/seed.sql` để có biến thể và tồn kho cho UC-02 AC-7. Thiết lập `UC01_TEST_DATABASE_URL`. Áp dụng `infra/postgres/uc02-cart-merge.sql` nếu schema chưa có bảng gộp giỏ. Fixture có `TRUNCATE` nên cần database kiểm thử riêng. Với UC-06 AC-9, nạp riêng `init.sql` vào database `uc01bootstrap` và đặt `UC06_BOOTSTRAP_DATABASE_URL`.
2. Chạy `python -m pytest -q tests/identity/test_uc04_profile.py` với helper trong repo. Cả 5 tiêu chí chấp nhận phải đạt.
3. Chạy UC-01, UC-02 và UC-05 đến UC-08 để xác minh các caller dùng chung. Chạy thêm UC-03 trong môi trường có PostgreSQL và Redis local theo cấu hình của bộ test rồi chạy suite Identity khi đủ dịch vụ. Báo rõ lệnh, số ca đạt và lỗi còn lại.
4. Đối chiếu bằng tìm kiếm để xác nhận hết các lời gọi `post(client, page, path, ...)`. Kiểm tra diff để xác nhận phần triển khai kế hoạch chỉ chạm vào các helper và ca kiểm thử liên quan.

## Kết quả

- UC-04 đạt 5/5 ca với helper chính thức. Suite Identity đạt 139/139 ca sau khi nạp dữ liệu mẫu vào database kiểm thử.
- TestClient xác nhận hai form hồ sơ và đổi mật khẩu nhận cùng CSRF token trong cùng trình duyệt. Hai trình duyệt có cookie riêng nhận token khác nhau khi dùng cùng phiên đăng nhập giả lập.
- Suite ghi nhận 51 cảnh báo `DeprecationWarning` từ các repository dùng `session.execute()` trong luồng checkout UC-02. Hai database kiểm thử tạm đã được dọn.
