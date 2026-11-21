# UC-07: Sửa tài khoản

## Metadata
- **ID:** UC-07
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Admin

## Trigger
Admin mở khu vực quản lý tài khoản và chọn một tài khoản để sửa.

## Preconditions
- Admin đang đăng nhập.

## Main Flow
1. Admin mở khu vực quản lý tài khoản.
2. Hệ thống hiển thị danh sách tài khoản có phân trang `[GD]`: họ tên, email, số điện thoại, vai trò, trạng thái.
3. Admin tìm theo họ tên, email hoặc số điện thoại `[GD]` và chọn một tài khoản.
4. Admin sửa họ tên, ngày sinh, địa chỉ, email, số điện thoại. Với tài khoản Nhân viên hoặc Admin, Admin có thể đổi vai trò qua lại giữa Nhân viên và Admin. Tài khoản Khách hàng không có thao tác đổi vai trò.
5. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại không trùng tài khoản khác.
6. Trong cùng một transaction `[GD]`, hệ thống lưu thông tin và vai trò mới, báo cập nhật thành công. Họ tên, ngày sinh, địa chỉ, email, số điện thoại, mật khẩu được giữ nguyên khi đổi vai trò.
7. Nếu vai trò được đổi, hệ thống cấp mã tài khoản mới theo vai trò (`NV-...` → `AD-...` hoặc ngược lại; mã cũ không dùng lại) và xóa mọi phiên (`identity.session`) của tài khoản trong cùng transaction ở bước 6, nên mọi phiên đang mở của tài khoản đó kết thúc ngay; vai trò mới có hiệu lực ngay.

## Alternative Flows
- **3a. Không tìm thấy:** từ khóa không khớp tài khoản nào — hệ thống hiển thị danh sách rỗng kèm thông báo "Không tìm thấy tài khoản".
- **4a. Đổi Nhân viên sang Admin hoặc Admin sang Nhân viên:** lịch sử thao tác cũ (ví dụ người đổi trạng thái đơn, người lập phiếu nhập) được giữ nguyên vì gắn với tài khoản.
- **4b. Admin tự đổi vai trò của chính mình (Admin → Nhân viên):** được phép, miễn sau khi đổi hệ thống vẫn còn ít nhất 1 Admin đang hoạt động (E4); đổi xong phiên của Admin đó bị kết thúc như mọi lần đổi vai trò.

## Exceptions
- **E1. Email hoặc số điện thoại trùng tài khoản khác:** hệ thống báo trường bị trùng, không lưu.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc hoặc sai định dạng — hệ thống báo lỗi, không lưu.
- **E3. Đổi vai trò giữa Khách hàng và Nhân viên / Admin** (theo bất kỳ chiều nào): hệ thống từ chối. Giao diện không hiển thị thao tác này; nếu có yêu cầu gửi thẳng lên hệ thống thì vẫn bị từ chối.
- **E4. Đổi vai trò làm hệ thống không còn Admin nào đang hoạt động** (vai trò Admin và trạng thái Hoạt động), kể cả khi Admin tự đổi vai trò của mình — hệ thống từ chối.
- **E5. Lỗi khi lưu:** hệ thống hủy toàn bộ transaction; thông tin và vai trò giữ nguyên, phiên đăng nhập không bị kết thúc `[GD]`.

## Postconditions
- Thông tin tài khoản được cập nhật.
- Nếu đổi vai trò (chỉ giữa Nhân viên và Admin): tài khoản có vai trò mới, giữ nguyên thông tin cá nhân và thông tin đăng nhập, có mã mới theo vai trò; vai trò mới có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất và phải đăng nhập lại với vai trò mới.

## Acceptance Criteria

### AC-1: Xem danh sách tài khoản
Given: có 25 tài khoản trong hệ thống
When: Admin mở khu vực quản lý tài khoản
Then: hệ thống hiển thị danh sách có phân trang gồm họ tên, email, số điện thoại, vai trò, trạng thái

### AC-2: Tìm tài khoản
Given: có tài khoản với email "nv1@example.com"
When: Admin tìm "nv1"
Then: kết quả có tài khoản "nv1@example.com"

### AC-3: Không tìm thấy
Given: không có tài khoản nào khớp "zzz"
When: Admin tìm "zzz"
Then: hệ thống hiển thị "Không tìm thấy tài khoản"

### AC-4: Sửa thông tin thành công
Given: Admin chọn tài khoản Nhân viên "nv1@example.com"
When: Admin đổi họ tên và bấm "Lưu"
Then: hệ thống lưu họ tên mới và báo thành công

### AC-5: Đổi vai trò Nhân viên sang Admin
Given: tài khoản "nv1@example.com" có vai trò Nhân viên, mã `NV-NGUYENVANAN-19990105-0001`
When: Admin đổi vai trò thành Admin và bấm "Lưu"
Then: tài khoản có vai trò Admin, được cấp mã mới dạng `AD-NGUYENVANAN-19990105-<4 số>`
And: họ tên, ngày sinh, địa chỉ, email, số điện thoại không đổi

### AC-6: Email trùng
Given: đã có tài khoản khác dùng email "nv2@example.com"
When: Admin đổi email của "nv1@example.com" thành "nv2@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: tài khoản giữ nguyên email cũ

### AC-7: Không đổi vai trò của tài khoản Khách hàng
Given: tài khoản "a@example.com" có vai trò Khách hàng
When: Admin mở tài khoản này để sửa
Then: không có thao tác đổi vai trò
And: nếu có yêu cầu đổi vai trò của "a@example.com" thành Nhân viên hoặc Admin gửi lên hệ thống, hệ thống từ chối và vai trò giữ nguyên Khách hàng

### AC-8: Không đổi Nhân viên hoặc Admin sang Khách hàng
Given: tài khoản "nv1@example.com" có vai trò Nhân viên
When: có yêu cầu đổi vai trò của tài khoản này thành Khách hàng
Then: hệ thống từ chối, vai trò giữ nguyên Nhân viên
And: danh sách vai trò có thể chọn cho tài khoản này chỉ gồm Nhân viên và Admin

### AC-9: Vai trò khác không truy cập được
Given: Nhân viên đang đăng nhập
When: Nhân viên truy cập khu vực quản lý tài khoản
Then: hệ thống từ chối truy cập

### AC-10: Đổi vai trò đăng xuất tài khoản đang đăng nhập
Given: tài khoản "nv1@example.com" có vai trò Nhân viên và đang đăng nhập
When: Admin đổi vai trò của tài khoản này thành Admin và bấm "Lưu"
Then: phiên đang mở của "nv1@example.com" bị kết thúc ngay
And: thao tác tiếp theo trên phiên cũ bị chuyển về trang đăng nhập
And: sau khi đăng nhập lại, tài khoản dùng vai trò Admin

### AC-11: Admin tự đổi vai trò của mình
Given: Admin "admin@example.com" đang đăng nhập; hệ thống còn Admin "admin2@example.com" đang hoạt động
When: Admin "admin@example.com" đổi vai trò của chính mình thành Nhân viên và bấm "Lưu"
Then: tài khoản "admin@example.com" có vai trò Nhân viên
And: phiên đang mở của "admin@example.com" bị kết thúc, đăng nhập lại thì dùng vai trò Nhân viên

### AC-12: Lỗi khi lưu
Given: tài khoản "nv1@example.com" có vai trò Nhân viên
When: Admin đổi vai trò thành Admin nhưng việc lưu thất bại
Then: vai trò vẫn là Nhân viên, thông tin không đổi
And: phiên đăng nhập của "nv1@example.com" không bị kết thúc
And: hệ thống báo cập nhật không thành công

### AC-13: Không để hệ thống hết Admin đang hoạt động
Given: "admin@example.com" là Admin đang hoạt động duy nhất (các Admin khác đều bị khóa hoặc không có)
When: có yêu cầu đổi vai trò của "admin@example.com" (kể cả tự đổi) thành Nhân viên
Then: hệ thống từ chối, vai trò giữ nguyên Admin

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản
- **Downstream UC:** UC-08 Khóa và mở khóa tài khoản
- **External Systems:** —

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung).
- Admin không đặt lại mật khẩu cho người khác trong UC này (không có trong BR).
- Data model v2 (`specs/entity-model/data_model_v2.dbml`): vai trò lưu ở bảng `identity.role`; `identity.account` có `account_role_key`, mã `account_id` và thông tin cá nhân (không còn bảng hồ sơ riêng theo vai trò, đã chốt 21/11/2026).
- Kết thúc phiên khi đổi vai trò bằng cách xóa các dòng `identity.session` của tài khoản (BR-GIAIDOAN1, Constraints chung — Xác thực; data model v2.15, Q35, đã chốt 21/11/2026). Sửa thông tin mà không đổi vai trò thì không xóa phiên. Lỗi khi lưu (E5) thì transaction bị hủy, các phiên giữ nguyên.

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Chỉ đổi vai trò qua lại giữa Nhân viên và Admin. Không đổi Khách hàng sang Nhân viên / Admin và không đổi Nhân viên / Admin sang Khách hàng; không tạo vai trò mới hoặc cấu hình quyền (đã chốt 20/11/2026, thay quyết định cho đổi sang mọi vai trò cùng ngày).
- Vai trò mới có hiệu lực ngay khi được đổi; nếu tài khoản đang đăng nhập thì bị đăng xuất (đã chốt 15/11/2026).
- Admin được tự đổi vai trò của mình; ràng buộc duy nhất là hệ thống luôn có ít nhất 1 Admin đang hoạt động (đã chốt 20/11/2026, data model v2, Q23b, Q24).
- Mỗi tài khoản đúng 1 vai trò (đã chốt 20/11/2026, data model v2, Q17).
- Đổi vai trò thì tài khoản được cấp mã mới theo vai trò: `NV-` / `AD-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>`, bộ đếm riêng cho từng tiền tố; mã cũ không dùng lại. Đây là trường hợp duy nhất mã tài khoản thay đổi (đã chốt 21/11/2026, data model v2, Q16, Q32).

### Giả định [GD]
- Việc xem và tìm danh sách tài khoản gộp vào UC này.
- Danh sách có phân trang; tìm theo họ tên, email hoặc số điện thoại.
- Admin sửa được thông tin mọi tài khoản.
- Đổi vai trò giữ nguyên thông tin cá nhân, email, số điện thoại, mật khẩu; lưu thông tin và vai trò trong một transaction, lỗi thì hủy toàn bộ.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): chốt Admin chỉ gán vai trò (Nhân viên ↔ Admin), không tạo vai trò mới
- v4 (2026-11-15): chốt vai trò mới có hiệu lực ngay, tài khoản đang đăng nhập bị đăng xuất; thêm AC-9
- v5 (2026-11-15): theo ERD — tách account và hồ sơ theo vai trò; đổi vai trò chuyển hồ sơ giữa Employee và Admin; thêm E4, AC-10
- v6 (2026-11-20): cho đổi sang mọi vai trò (gồm Khách hàng ↔ Nhân viên/Admin); bỏ mô tả chuyển hồ sơ giữa các bảng (không dựa vào data model hiện tại); thêm E4 không để hệ thống hết Admin, AC-7, AC-8, AC-11, AC-12
- v7 (2026-11-20): theo data model v2 — Admin được tự đổi vai trò (4c, AC-11), chỉ chặn khi hết Admin đang hoạt động (E4, AC-13); đổi vai trò cấp mã mới (bước 7); thay E3 bằng yêu cầu ngày sinh khi đổi sang Nhân viên/Admin `[GD]`
- v8 (2026-11-20): chỉ đổi vai trò giữa Nhân viên và Admin — bỏ đổi Khách hàng ↔ Nhân viên/Admin (bước 4, 4a, 4b, E3, AC-7, AC-8 viết lại); bỏ giả định về ngày sinh và mã `KH-` khi đổi vai trò (không còn cần); AC-5 thêm mã mới
- v9 (2026-11-21): theo data model v2 — không còn bảng hồ sơ riêng; đổi vai trò cấp mã mới trên account (bước 7, 4a, Notes)
- v10 (2026-11-21): theo BR-GIAIDOAN1 v20 — kết thúc phiên khi đổi vai trò bằng `account_token_version` (bước 7, Notes)
- v11 (2026-11-21): theo BR-GIAIDOAN1 v21 — kết thúc phiên bằng xóa `identity.session` thay cho `account_token_version` (bước 7, Notes)
