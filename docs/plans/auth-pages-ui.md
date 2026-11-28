# Plan: Giao diện trang Đăng nhập và Đăng ký của khách hàng theo mẫu 02 "Đường cắt thể thao"

> Dev yêu cầu 28/11/2026 (chat): "làm tương tự, chỉnh sửa lại trang đăng nhập, đăng ký của khách hàng". Dev chốt nút gửi lại mã: chỉ **1 nút**; khi bị khóa thì nút chuyển xám và hiện "Gửi lại mã sau 05:00".

## Goal

Trang `GET /api/v1/identity/login` (storefront) và `GET /api/v1/identity/register` (3 bước Email → Xác minh → Mật khẩu) trông giống mẫu:

- `docs/design/auth-mockup-login-register1.webp` (Đăng nhập; Đăng ký bước 1/3)
- `docs/design/auth-mockup-register2-3.webp` (Đăng ký bước 2/3, 3/3)

Chỉ đổi giao diện (template, CSS). **Không đổi hành vi** (route, service, form field name, action, status code, thông báo lỗi). Trang đăng nhập portal quản trị giữ nguyên giao diện hiện tại.

## Context đã đọc

- `specs/use-cases/identity/UC-01-register-account.md` (OTP 5 phút, AC-18 đếm ngược, mật khẩu ≥ 6 ký tự, xong thì chuyển đến đăng nhập), `UC-02-login.md` (đăng nhập bằng email hoặc số điện thoại; 1b/AC-10 nút "Quên mật khẩu" chưa có hành động; portal không có nút này).
- Template: `app/modules/identity/templates/{_layouts/auth.html, auth/login.html, auth/portal_login.html, registration/register.html, _partials/auth_fields.html, _partials/icons.html}`; CSS `app/modules/identity/css/{base,auth}.css`.
- Layout storefront từ trang chủ: `app/shared/web/templates/{storefront.html,_storefront/header.html,_storefront/footer.html}`, `app/static/css/storefront.css`; ảnh `app/static/images/home/hero.jpg`.
- Test có so khớp markup: `tests/identity/test_uc01_register_account.py` (AC-14 nút Google, AC-18 nút gửi lại), `tests/identity/test_uc02_login.py` (dòng 65–66 "Quên mật khẩu", dòng 164 lấy form đầu tiên).

## Mô tả mẫu

Chung cho mọi trang: header và footer storefront giống trang chủ. Thân trang là một khối rộng bằng container, chia đôi:

- **Nửa trái** (~50%): ảnh người phụ nữ đội kính bơi bên hồ bơi (cùng ảnh hero trang chủ, cắt dọc, người mẫu ở giữa), mép phải cắt chéo (đường chéo từ trên-phải xuống dưới-trái) kèm một vạch lime mảnh chạy theo đường chéo; góc dưới trái chữ trắng condensed đậm nghiêng "Bơi theo / cách của bạn." và một vạch lime ngắn bên dưới; lớp phủ tối dần ở đáy cho chữ dễ đọc.
- **Nửa phải**: nền trắng, form rộng ~360px căn giữa.

Đăng nhập: tiêu đề "ĐĂNG NHẬP" (condensed 800, nghiêng, chữ hoa, navy) · dòng phụ "Chào mừng bạn trở lại với SOBIE." · nhãn đậm "Tài khoản" + ô nhập viền navy mảnh bo góc nhỏ · "Mật khẩu" + ô có icon mắt · link xanh nhạt "Quên mật khẩu?" · nút lime đầy chiều ngang "Đăng nhập →" · vạch "hoặc" · nút trắng viền "G Đăng nhập với Google" · "Chưa có tài khoản? **Đăng ký**" (gạch chân).

Đăng ký bước 1: tiêu đề "TẠO TÀI KHOẢN" · thanh bước 3 nút tròn nối bằng đường mảnh: (1) lime đậm "Email" in đậm, (2) viền "Xác minh", (3) viền "Mật khẩu" · "Nhập email để nhận mã xác minh." · "Email" + ô "Nhập email của bạn" · nút lime "Gửi mã xác minh →" · "hoặc" · nút Google · "Đã có tài khoản? **Đăng nhập**".

Bước 2: tiêu đề "Xác minh email" · bước (1) lime có dấu ✓, (2) lime "Xác minh" in đậm, (3) viền · "Mã OTP" + ô "Nhập mã OTP" · "Mã có hiệu lực trong 5 phút." · nút lime "Xác minh →" · nút gửi lại (xem D1) · "Đã có tài khoản? **Đăng nhập**".

Bước 3: tiêu đề "Tạo mật khẩu" · (1) ✓, (2) ✓, (3) lime "Mật khẩu" in đậm · "Mật khẩu" + ô có mắt + "Ít nhất 6 ký tự." · "Xác nhận mật khẩu" + ô "Nhập lại mật khẩu" có mắt · nút lime "Hoàn tất đăng ký →" · "Sau khi hoàn tất, vui lòng đăng nhập."

## Quyết định

- **D1 (dev chốt).** Bước 2 chỉ có **một** nút gửi lại mã, đặt ngay dưới nút "Xác minh", rộng bằng nút đó:
  - Bị khóa (`result.resend_after > 0`): nút xám (nền xám nhạt, chữ xám), `disabled`, nội dung `Gửi lại mã sau <span>MM:SS</span>`; giữ `role="timer"`/`data-resend-after` để JS đếm ngược và cập nhật `<span>`. Hết giờ thì JS bật nút và đổi chữ thành "Gửi lại mã". Không còn dòng đếm ngược riêng bên ngoài nút.
  - Mở (`resend_after == 0`): nút viền (kiểu secondary) "Gửi lại mã". Bấm thì submit như hiện tại và JS khóa nút ngay để chống bấm lặp.
  - Áp dụng cả khi `otp_locked` (sai 5 lần): không có form OTP, chỉ còn nút gửi lại đếm ngược.
- **D2 `[GD]`.** Cập nhật test UC-01 AC-18 theo markup mới (D1): nút khóa khớp `<button\b[^>]*\bdisabled[^>]*>\s*Gửi lại mã sau <span>05:00</span>\s*</button>` (tương tự 03:00), nút mở khớp `<button\b[^>]*>\s*Gửi lại mã\s*</button>` và không có `disabled`; giữ assert `data-resend-after`. Không nới lỏng điều kiện khác.
- **D3 `[GD]`.** Header storefront có form tìm kiếm đứng trước form đăng nhập nên regex dòng 164 của `tests/identity/test_uc02_login.py` (lấy `<form` đầu tiên) sẽ lấy nhầm. Đổi regex để lấy form có `class="identity-form"` (chính xác hơn, không làm yếu test).
- **D4 `[GD]`** (theo nguyên tắc "theo mẫu + bù phần spec" dev đã chọn cho trang chủ):
  - Ô "Tài khoản" có placeholder "Nhập email hoặc số điện thoại" (UC-02 bước 2) thay cho "Nhập thông tin đăng nhập" của mẫu; giữ `id/name="identifier"`.
  - Bỏ checkbox "Ghi nhớ đăng nhập" (không có trong mẫu, không có trong spec, không có tác dụng).
  - "Quên mật khẩu?" vẫn là `<button type="button">` (UC-02 AC-10, test dòng 65), trông như link.
  - Bước 2 giữ một dòng nhỏ màu muted "Mã đã gửi đến **email**" dưới thanh bước, và link nhỏ "Bắt đầu lại" cạnh "Đã có tài khoản? Đăng nhập". Bước 3 giữ dòng nhỏ "Email đã xác minh: **email**".
  - Giữ mọi thông báo hiện có (đăng ký thành công, đổi mật khẩu thành công, đã khóa tài khoản, đổi vai trò, lỗi chung, lỗi từng trường với `aria-invalid`/`aria-describedby`).
- **D5 `[GD]`.** Tiêu đề 4 màn hình dùng chung một kiểu (condensed 800 nghiêng chữ hoa) cho nhất quán: "ĐĂNG NHẬP", "TẠO TÀI KHOẢN", "XÁC MINH EMAIL", "TẠO MẬT KHẨU" (mẫu bước 2, 3 dùng font thường, nhiều khả năng do mẫu không đồng nhất).
- **D6 `[GD]`.** Header trên trang đăng nhập/đăng ký không tô "Trang chủ" là mục đang chọn (mẫu có tô). Mục đang chọn của menu chuyển thành biến/khối do từng trang đặt; trang chủ vẫn tô "Trang chủ".
- **D7.** Portal login (`auth/portal_login.html`) giữ giao diện hiện tại. Vì đang `extends "identity/auth/login.html"`, tách để portal dùng layout cũ `identity/_layouts/auth.html` với cùng form đăng nhập (vẫn không có "Quên mật khẩu", không có Google).

## Thay đổi file

| File | Thay đổi |
|---|---|
| `app/modules/identity/templates/_layouts/storefront_auth.html` (mới) | Extends `storefront.html`; khối chia đôi: ảnh trái (dùng `/static/images/home/hero.jpg`, `object-fit: cover`, `object-position` để người mẫu vào giữa khung dọc; nếu cắt xấu thì sinh ảnh dọc mới `app/static/images/auth/side.jpg` bằng image generation, cùng phong cách) + khối `auth_content`. Nạp `/static/identity/storefront-auth.css`. |
| `app/modules/identity/css/storefront-auth.css` (mới) | Style khối chia đôi, đường cắt chéo + vạch lime (clip-path), tiêu đề, ô nhập, nút lime/nút viền/nút xám, thanh bước, divider "hoặc", link. Dùng lại token màu/font của `storefront.css`. Responsive: < 900px ảnh thành dải ngang thấp phía trên (hoặc ẩn), form full width; 375px không tràn ngang. |
| `app/modules/identity/templates/auth/login.html` | Chuyển sang `storefront_auth.html`, bố cục theo mẫu và D4. Giữ form `method="post" action="{{ form_action }}"` class `identity-form`, nút Google giữ đúng markup test AC-14: `<a class="identity-button identity-button--secondary"` xuống dòng `href="...">{{ google() }} Đăng nhập với Google</a>`. Giữ script ẩn/hiện mật khẩu. |
| `app/modules/identity/templates/auth/portal_login.html` | Theo D7: extends `identity/_layouts/auth.html`, giữ nội dung và giao diện như hiện tại. |
| `app/modules/identity/templates/_partials/auth_fields.html` | Macro `credentials` nhận tham số nhãn/placeholder để storefront dùng "Tài khoản"/"Nhập email hoặc số điện thoại", portal giữ "Email hoặc số điện thoại". |
| `app/modules/identity/templates/registration/register.html` | Chuyển sang `storefront_auth.html`; thêm thanh bước; bố cục từng bước theo mẫu, D1, D4, D5. Giữ nguyên action, field name, `data-otp-request`, logic JS chống bấm lặp/đếm ngược (sửa cho hợp D1). Nút Google giữ đúng markup như trang đăng nhập (test AC-14 so sánh hai nút bằng nhau). |
| `app/modules/identity/templates/_partials/icons.html` | Nếu cần: icon mũi tên, dấu ✓; icon Google nhiều màu (giữ là `<svg>` để test AC-14 khớp). |
| `app/shared/web/templates/_storefront/header.html`, `storefront.html`, `app/modules/catalog/templates/home.html` | D6: mục menu đang chọn do trang đặt (vd. biến `active_nav`); trang chủ đặt "home". Không đổi gì khác. |
| `app/main.py` | Chỉ khi cần mount thêm static; `/static/identity` đã mount sẵn thư mục `identity/css`. |
| `tests/identity/test_uc01_register_account.py` | D2: chỉ sửa regex/assert của `test_uc01_ac18_resend_countdown`. |
| `tests/identity/test_uc02_login.py` | D3: chỉ sửa regex dòng 164. |
| `.artifact/auth_preview_app.py` (mới, không commit) | App xem trước: import `app.main.app`, thêm route `/__preview/login`, `/__preview/register/{email,otp,otp-locked,password}` render template thật với `RegistrationResult` giả (resend_after 300/0, lỗi trường…) để chụp màn hình từng bước mà không cần gửi email. |

Không đổi router/service/schemas của identity. Không đổi `account/*`, `admin/*`, `_layouts/account.html`.

## Ràng buộc cho Codex

- Không dùng skill superpowers và gitnexus.
- Không commit/push; không động DB, Docker, `infra/`, seed; không đổi `pyproject.toml`/`poetry.lock`.
- Chỉ sửa file trong bảng; buộc phải sửa file khác thì báo lý do.
- Giữ nguyên hành vi: route, action, tên field, status, thông báo, `aria-*`. Không sửa test ngoài D2, D3.

## Kiểm chứng

1. `poetry run python -c "from app.main import app"`.
2. Server `poetry run uvicorn app.main:app --port 8000`: `GET /api/v1/identity/login`, `/api/v1/identity/register`, `/api/v1/identity/portal/login` (Accept: text/html) → 200; CSS/ảnh → 200; portal không có "Quên mật khẩu", không có nút Google, giao diện như cũ.
3. Grep markup: `type="button">Quên mật khẩu` có ở login storefront; nút Google ở login và register khớp regex test AC-14 và giống hệt nhau.
4. Preview app (`.artifact/auth_preview_app.py`, cổng 8001): chụp 4 màn hình + OTP bị khóa ở 1440px và 375px, so với mẫu; kiểm tra nút gửi lại xám "Gửi lại mã sau 05:00" và JS đếm ngược.
5. `poetry run python -m pytest -q -p no:cacheprovider tests` — baseline `6 passed, 1 skipped, 102 errors` (thiếu `UC01_TEST_DATABASE_URL`); không có lỗi mới. Test identity không chạy được nếu không có DB `uc01test` — dev chưa cho tạo, nên D2/D3 chỉ kiểm bằng cách chạy regex mới trên HTML thật (lưu script ở `.artifact/`).

## Câu hỏi mở [GD]

1. D2, D3: sửa regex test UC-01 AC-18 và UC-02 AC-7 — dev xác nhận.
2. D4: placeholder đăng nhập, bỏ "Ghi nhớ đăng nhập", giữ "Bắt đầu lại" và dòng email ở bước 2, 3.
3. D5: đồng nhất kiểu tiêu đề 4 màn hình.
4. D6: không tô "Trang chủ" trên trang đăng nhập/đăng ký.
5. Có tạo DB `uc01test` trong Docker để chạy đủ test identity không (chưa được trả lời).

## Kết quả

Thực thi 28/11/2026 — Codex 2 lượt (lượt đầu + vòng sửa 1: phóng to chữ/ô nhập/nút/thanh bước ~1,4 lần, khối cao 720px, sinh ảnh dọc mới), Claude kiểm chứng bằng trình duyệt có font thật.

- File: `app/modules/identity/templates/_layouts/storefront_auth.html` (mới), `app/modules/identity/css/storefront-auth.css` (mới), `app/static/images/auth/side.jpg` (mới, 1086×1448, 392KB, sinh bằng image generation), `auth/login.html`, `auth/portal_login.html`, `registration/register.html`, `_partials/auth_fields.html`, `app/shared/web/templates/_storefront/header.html`, `app/modules/catalog/templates/home.html` (D6); test chỉ sửa D2 (`test_uc01_ac18_resend_countdown`) và D3 (regex dòng 164 `test_uc02_login.py`). Không đổi router/service/schemas. Công cụ kiểm trong `.artifact/` (`auth_preview_app.py`, `auth_regex_check.py`, ảnh chụp) — không commit.
- So với mẫu ở 1200px: đủ 4 màn hình, bố cục chia đôi, đường cắt chéo + vạch lime, tiêu đề, thanh bước, ô nhập, nút lime, nút Google, link dưới cùng khớp mẫu. Nút gửi lại duy nhất, xám "Gửi lại mã sau 05:00", đếm ngược và tự bật lại (D1). 375px: ảnh thành dải ngang, không tràn ngang (scrollWidth = 375). Console không lỗi.
- Portal login giữ giao diện cũ, không có "Quên mật khẩu", không có Google.
- `from app.main import app`: OK. `.artifact/auth_regex_check.py`: PASS 6/6 (D2, D3, AC-14). pytest (chưa có DB): `6 passed, 1 skipped, 102 errors` — khớp baseline. Sau khi dev cho tạo DB `uc01test` (Docker, nạp `init.sql`, `seed.sql`, `uc02-cart-merge.sql`) và đặt `UC01_TEST_DATABASE_URL`: **`108 passed, 1 skipped`**, gồm cả test đã sửa D2 (UC-01 AC-18) và D3 (UC-02 AC-7). 1 test skip là UC-06 AC-9 (cần thêm DB `uc01bootstrap` qua `UC06_BOOTSTRAP_DATABASE_URL`, chưa tạo).
- Phát hiện ngoài phạm vi: `specs/use-cases/identity/UC-01-register-account.md` dòng 188–191 còn dấu merge conflict ở mục History; API contract trên Drive còn `return_to` và nhánh OTP liên kết Google cũ, lệch UC-02 (`return_url`).
- Codex không dùng skill superpowers/gitnexus (kiểm trong log).
