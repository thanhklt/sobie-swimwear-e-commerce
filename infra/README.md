# Hạ tầng Sobie

## Tài khoản test

| Vai trò | Email |
| --- | --- |
| Admin | `admin@gmail.com` |
| Nhân viên | `employee@gmail.com` |
| Khách hàng | `customer@gmail.com` |

Các tài khoản này dành cho môi trường dev/demo. Để cả ba dùng chung một mật khẩu, truyền hash bcrypt của mật khẩu qua tùy chọn `-c sobie.seed_test_password_hash=...` trong biến môi trường `PGOPTIONS` của tiến trình chạy `postgres/seed.sql`. Nếu đặt `sobie.seed_employee_password_hash` hoặc `sobie.seed_customer_password_hash`, giá trị riêng được ưu tiên cho tài khoản tương ứng.

Docker Compose nạp seed khi khởi tạo volume PostgreSQL trống. Nếu không cấp hash chung, Admin giữ mật khẩu từ bước khởi tạo và các tài khoản còn lại dùng hash riêng đã cấp hoặc mật khẩu ngẫu nhiên.
