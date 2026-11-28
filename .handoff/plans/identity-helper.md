# Kế hoạch tách helper của module identity

**Trạng thái** Đã thực thi.

## Hiện trạng

`app/modules/identity/schemas.py` chứa hai hàm kiểm tra dữ liệu và chưa có model. `IdentityService` là nơi duy nhất import trực tiếp hai hàm này. `models.py` đã chứa các model SQLModel của `identity`.

## Thay đổi dự kiến

1. Tạo `app/modules/identity/helper.py`. Chuyển `normalize_email()` và `password_validation_error()` sang file này, giữ nguyên cách chuẩn hóa email, thứ tự kiểm tra, giới hạn và thông báo lỗi theo UC-01.
2. Chuyển các hàm hỗ trợ độc lập đang đặt trong `service.py` sang cùng file: `utc_now()`, `generate_otp()` và hàm chuyển đồng hồ UTC sang timestamp. Cập nhật `service.py` gọi qua module `helper` và đổi vị trí monkeypatch đồng hồ, bộ sinh OTP trong `tests/identity/conftest.py`.
3. Để `IdentityService` điều phối gửi, xác minh, đọc và ghi trạng thái OTP, xác thực Google và transaction. Helper chỉ chứa hàm hỗ trợ không gọi repository, Redis, SMTP hay OIDC. Các thao tác đặt cookie, redirect và dựng phản hồi tiếp tục do router xử lý.
4. Bỏ `app/modules/identity/schemas.py` sau khi đổi các import. Dùng `rg` để xác nhận không còn tham chiếu đến `identity.schemas`. Các model của module tiếp tục nằm trong `models.py`.

## Kiểm chứng sau khi duyệt

- Chạy các ca UC-01 trên PostgreSQL 16 trong Docker bằng database riêng `uc01test` và `UC01_TEST_DATABASE_URL`. Tập trung kiểm tra email sai, mật khẩu sai, OTP hết hạn, gửi lại OTP và cả hai nhánh Google.
- Chạy lại toàn suite. Mốc đối chiếu là 30/30 ca theo [kết quả UC-01](UC-01-fix.md#kết-quả-và-môi-trường-kiểm-thử). Đợt này di chuyển mã hỗ trợ trong module identity, còn cấu hình Redis, SMTP và Google phục vụ kiểm thử thủ công được xử lý độc lập.

## Kết quả

Đã chuyển năm hàm hỗ trợ sang `helper.py`, cập nhật `IdentityService` và fixture, rồi bỏ `identity/schemas.py`. Tìm kiếm trong mã nguồn và bộ test xác nhận không còn import từ file cũ.

Bộ UC-01 và toàn bộ suite đều đạt 30/30 ca trên PostgreSQL 16.15 trong Docker. Redis, SMTP và Google OIDC dùng adapter giả của bộ nghiệm thu.
