# Kế hoạch sửa UC-01 · Đăng ký tài khoản

**Trạng thái** Đã thực thi trên nhánh `feature/identity`.

Đối chiếu với [kế hoạch UC-01](UC-01.md), [đặc tả UC-01](../../specs/use-cases/identity/UC-01-register-account.md), [đặc tả UC-02](../../specs/use-cases/identity/UC-02-login.md) và [schema PostgreSQL](../../infra/postgres/init.sql).

## Hiện trạng và phạm vi

- Cả bộ UC-01 và toàn suite cho kết quả **20 đạt, 9 lỗi**. Cả 9 ca lỗi vì adapter OIDC giả khai báo `authorization_url` đồng bộ trong khi service gọi bằng `await`. Khi bọc riêng adapter giả bằng hàm async trong bộ nhớ, **29/29 ca đạt**.
- Chuyển các nghiệp vụ và thao tác dữ liệu hiện có trong `identity` sang `IdentityService` và `IdentityRepository`. Dùng SQLModel ORM cho các bảng do `identity` sở hữu. Các thay đổi ngoài module tập trung vào khởi tạo ứng dụng, middleware phiên, kiểm thử và tài liệu UC-01.
- Giữ các quyết định D1–D6 và hành vi của 9 endpoint đã có. `identity` gọi service công khai của `shopping` để tạo giỏ và danh sách yêu thích. Đăng nhập bằng mật khẩu, rate limit và các luồng khác của UC-02 thuộc đợt triển khai riêng.

## 1. Sửa fixture và lấy mốc kiểm thử

- Tại `tests/identity/conftest.py`, đổi OIDC giả thành `async def authorization_url(...)` để khớp adapter thật. Tại `tests/identity/test_uc01_register_account.py`, kiểm tra redirect thành công trước khi đọc `Location` để báo lỗi đúng ở bước khởi tạo Google.
- Chạy cả hai lệnh nghiệm thu bên dưới. Kỳ vọng 29/29 ca đạt với fixture đã sửa trong repo trước khi chuyển sang ORM.

## 2. Khai báo model và chuyển repository sang SQLModel

- Tại `app/modules/identity/models.py`, khai báo model bảng cho `identity.role`, `identity.account` và `identity.session`. Ánh xạ tên cột, UUID, khóa ngoại, trường nullable, giá trị mặc định do PostgreSQL sinh và `timestamptz` theo schema hiện có. Giữ `infra/postgres/init.sql` làm nguồn khởi tạo schema.
- Tại `app/modules/identity/repository.py`, chuyển truy vấn và ghi dữ liệu vào phương thức của `IdentityRepository`. Mỗi phương thức nhận `AsyncSession` từ service. Dùng `flush()` khi cần lấy khóa UUID do PostgreSQL sinh. Service quản lý commit và rollback.
- Dùng `select()` trên model để tra tài khoản và vai trò. Giữ tra email không phân biệt hoa thường cho dữ liệu cũ và khóa hàng tài khoản tương đương `FOR UPDATE OF account` ở các nhánh Google hiện có. Dùng model cho insert/update tài khoản và phiên. Bảo toàn cách xử lý vi phạm UNIQUE của email và Google `sub`.
- Chuyển gia hạn phiên sang biểu thức `UPDATE … RETURNING` trên model. Giữ kiểm tra và cập nhật trong cùng một câu lệnh nguyên tử. Chỉ chấp nhận phiên còn hạn, tài khoản `ACTIVE` và vai trò đúng cổng. Request đến muộn không được kéo lùi thời điểm hoạt động hoặc hết hạn.
- Gọi `identity.next_account_suffix` và `pgcrypto` bằng biểu thức hàm với tham số bind. Giữ bộ đếm trong transaction đăng ký, cost bcrypt hiện tại và `hide_parameters=True`. Kiểm tra log khi có lỗi để mật khẩu không xuất hiện trong log. Việc ánh xạ ORM dùng schema hiện có, không cần migration hay `create_all()`.

## 3. Đưa nghiệp vụ vào IdentityService và chuyển caller

- Tại `app/modules/identity/service.py`, chuyển các điểm vào nghiệp vụ đăng ký, OIDC, thông báo thành công và xác thực phiên vào `IdentityService`. Inject repository và session factory. Giữ Redis, SMTP và OIDC ở biên để thay bằng adapter giả trong test. Các helper thuần có thể giữ ở phạm vi nội bộ.
- Tại `app/main.py`, khởi tạo repository và service khi dựng ứng dụng. Cho router identity và `SessionMiddleware` tại `app/security/session.py` lấy cùng đối tượng service từ ứng dụng. Hai object chỉ giữ dependency, mỗi thao tác DB mở và đóng session theo vòng đời hiện hành. Giữ các kiểu kết quả công khai. Sau khi chuyển các caller, bỏ các điểm vào nghiệp vụ dạng hàm cấp module.
- Tạo tài khoản qua email hoặc Google trong một transaction gồm cấp mã KH, ghi tài khoản và `sub` nếu có, rồi gọi `initialize_customer_shopping` với **cùng session**. Khi liên kết Google lần đầu, xác minh OTP rồi khóa và kiểm tra lại tài khoản, ghi `sub` và cấp phiên trong một transaction.
- Giữ URL, tên route, redirect, thông báo, thuộc tính cookie và thời hạn phiên của storefront/portal. Cập nhật các sơ đồ sequence bị ảnh hưởng theo tên lớp, lời gọi và ranh giới transaction thực tế.

## 4. Kiểm thử và ghi kết quả

| Kiểm tra | Tiêu chí |
|---|---|
| HTTP theo AC | Chạy đủ 13 AC qua các endpoint. Điều chỉnh fixture theo cơ chế inject mới. Giữ các ca OTP ở mốc 299/300 giây, tạo mật khẩu, redirect và cả hai nhánh đăng nhập Google vào tài khoản hiện có. |
| Toàn vẹn dữ liệu | Với AC-6, tiêm lỗi sau khi thao tác ghi đã thực thi, rồi dùng kết nối đọc độc lập để kiểm tra bộ đếm KH, tài khoản, giỏ, danh sách yêu thích và `sub`. Với nhánh liên kết lần đầu của AC-16, kiểm tra lỗi ghi phiên hoàn tác liên kết vừa cập nhật. |
| Repository trên PostgreSQL kiểm thử | Dùng database kiểm thử tách biệt và repository thật để kiểm tra ánh xạ UUID/default/null, bcrypt qua pgcrypto, cấp mã và rollback, khóa hàng, UNIQUE và gia hạn phiên nguyên tử. Các kiểm tra kỹ thuật ngoài AC đặt trong `.artifact/` theo `AGENTS.md`. Ghi rõ hạng mục nào chưa được xác minh nếu thiếu môi trường kiểm thử. |

~~~powershell
poetry run pytest -q -p no:cacheprovider tests/identity/test_uc01_register_account.py
poetry run pytest -q -p no:cacheprovider tests
~~~

Ghi kết quả hai lệnh vào mục **Kết quả** của [kế hoạch gốc](UC-01.md), kèm phạm vi kiểm thử bằng adapter giả và bằng PostgreSQL. Đối chiếu các mục `[GD]` còn sót trong đặc tả với D1–D4 đã duyệt để đồng bộ ngưỡng mật khẩu, redirect, luồng Google và các trường nullable. Đạt nghiệm thu khi đủ 13/13 AC đạt và toàn suite không có lỗi mới.



## Kết quả và môi trường kiểm thử

Ngày 24/11/2026, cả bộ UC-01 và toàn suite đạt 30/30 ca trên PostgreSQL 16 trong Docker. Fixture chạy repository thật, `pgcrypto` và schema từ `infra/postgres/init.sql`. Redis, SMTP và Google OIDC dùng adapter giả. Đã kiểm tra gia hạn phiên và vai trò cổng bằng repository thật. Chưa kiểm thử tích hợp Redis, SMTP và Google thật.

Thiết lập database PostgreSQL tách biệt tên `uc01test` với schema từ `infra/postgres/init.sql`, sau đó đặt `UC01_TEST_DATABASE_URL` thành URL PostgreSQL của database đó trước khi chạy pytest. Fixture xóa các tài khoản và dữ liệu liên quan, đồng thời đặt lại bộ đếm KH trước mỗi ca. Database này dành riêng cho kiểm thử.
