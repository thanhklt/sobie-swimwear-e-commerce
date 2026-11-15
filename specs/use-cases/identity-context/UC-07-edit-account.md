# UC-07: Sửa tài khoản

## Metadata
- **ID:** UC-07
- **Bounded Context:** identity-context
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
2. Hệ thống hiển thị danh sách tài khoản có phân trang `[GD]`: họ tên (từ hồ sơ theo vai trò), email, số điện thoại, vai trò, trạng thái (từ account).
3. Admin tìm theo họ tên, email hoặc số điện thoại `[GD]` và chọn một tài khoản.
4. Admin sửa họ tên, ngày sinh, địa chỉ (hồ sơ), email, số điện thoại (account); với tài khoản nội bộ có thể đổi vai trò giữa Nhân viên và Admin.
5. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại không trùng account khác.
6. Hệ thống lưu thay đổi vào account và hồ sơ tương ứng, báo cập nhật thành công.
7. Nếu vai trò được đổi, trong cùng một transaction `[GD]` hệ thống đổi vai trò trên account và chuyển hồ sơ sang bảng của vai trò mới: tạo hồ sơ ở bảng mới (Employee hoặc Admin) với cùng thông tin, rồi xóa hồ sơ ở bảng cũ `[GD]`.
8. Nếu vai trò được đổi, hệ thống kết thúc ngay mọi phiên đang mở của tài khoản đó; vai trò mới có hiệu lực ngay.

## Alternative Flows
- **3a. Không tìm thấy:** từ khóa không khớp tài khoản nào — hệ thống hiển thị danh sách rỗng kèm thông báo "Không tìm thấy tài khoản".

## Exceptions
- **E1. Email hoặc số điện thoại trùng tài khoản khác:** hệ thống báo trường bị trùng, không lưu.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc hoặc sai định dạng — hệ thống báo lỗi, không lưu.
- **E3. Đổi vai trò không hợp lệ:** đổi tài khoản Khách hàng sang vai trò nội bộ, đổi tài khoản nội bộ sang Khách hàng, hoặc Admin tự đổi vai trò của chính mình `[GD]` — hệ thống từ chối.
- **E4. Lỗi khi chuyển hồ sơ:** tạo hồ sơ ở bảng mới hoặc xóa hồ sơ cũ thất bại — hệ thống hủy toàn bộ transaction; vai trò và hồ sơ giữ nguyên, phiên đăng nhập không bị kết thúc `[GD]`.

## Postconditions
- Thông tin account và hồ sơ được cập nhật.
- Nếu đổi vai trò: account có vai trò mới; hồ sơ nằm ở bảng của vai trò mới (Employee hoặc Admin), không còn ở bảng cũ; vai trò mới có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất và phải đăng nhập lại với vai trò mới.

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
Given: tài khoản "nv1@example.com" có vai trò Nhân viên
When: Admin đổi vai trò thành Admin và bấm "Lưu"
Then: account có vai trò Admin
And: hồ sơ của tài khoản nằm ở bảng Admin với cùng họ tên, ngày sinh, địa chỉ
And: bảng Employee không còn hồ sơ của tài khoản này

### AC-6: Email trùng
Given: đã có tài khoản khác dùng email "nv2@example.com"
When: Admin đổi email của "nv1@example.com" thành "nv2@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: tài khoản giữ nguyên email cũ

### AC-7: Đổi vai trò không hợp lệ
Given: tài khoản "a@example.com" có vai trò Khách hàng
When: Admin đổi vai trò của tài khoản này thành Nhân viên
Then: hệ thống từ chối
And: vai trò giữ nguyên Khách hàng

### AC-8: Vai trò khác không truy cập được
Given: Nhân viên đang đăng nhập
When: Nhân viên truy cập khu vực quản lý tài khoản
Then: hệ thống từ chối truy cập

### AC-9: Đổi vai trò đăng xuất tài khoản đang đăng nhập
Given: tài khoản "nv1@example.com" có vai trò Nhân viên và đang đăng nhập
When: Admin đổi vai trò của tài khoản này thành Admin và bấm "Lưu"
Then: phiên đang mở của "nv1@example.com" bị kết thúc ngay
And: thao tác tiếp theo trên phiên cũ bị chuyển về trang đăng nhập
And: sau khi đăng nhập lại, tài khoản dùng vai trò Admin

### AC-10: Lỗi khi chuyển hồ sơ
Given: tài khoản "nv1@example.com" có vai trò Nhân viên
When: Admin đổi vai trò thành Admin nhưng việc tạo hồ sơ ở bảng Admin thất bại
Then: vai trò vẫn là Nhân viên và hồ sơ vẫn nằm ở bảng Employee
And: phiên đăng nhập của "nv1@example.com" không bị kết thúc
And: hệ thống báo cập nhật không thành công

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-01, UC-06
- **Downstream UC:** UC-08 Khóa và mở khóa tài khoản
- **External Systems:** —

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung).
- Admin không đặt lại mật khẩu cho người khác trong UC này (không có trong BR).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Gán vai trò = đổi vai trò giữa Nhân viên và Admin cho tài khoản nội bộ; không tạo vai trò mới hoặc cấu hình quyền (đã chốt 15/11/2026).
- Vai trò mới có hiệu lực ngay khi được đổi; nếu tài khoản đang đăng nhập thì bị đăng xuất (đã chốt 15/11/2026).
- Account giữ email, số điện thoại, mật khẩu, vai trò, trạng thái; họ tên, ngày sinh, địa chỉ nằm ở hồ sơ riêng theo vai trò (Customer / Employee / Admin) có khóa ngoại tới account (theo ERD, đã chốt 15/11/2026).

### Giả định [GD]
- Việc xem và tìm danh sách tài khoản gộp vào UC này.
- Danh sách có phân trang; tìm theo họ tên, email hoặc số điện thoại.
- Admin sửa được thông tin mọi tài khoản.
- Admin không tự đổi vai trò của chính mình.
- Đổi vai trò Nhân viên ↔ Admin: tạo hồ sơ ở bảng của vai trò mới với cùng thông tin rồi xóa hồ sơ ở bảng cũ, cùng với đổi vai trò trên account, trong một transaction; lỗi thì hủy toàn bộ.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): chốt Admin chỉ gán vai trò (Nhân viên ↔ Admin), không tạo vai trò mới
- v4 (2026-11-15): chốt vai trò mới có hiệu lực ngay, tài khoản đang đăng nhập bị đăng xuất; thêm AC-9
- v5 (2026-11-15): theo ERD — tách account và hồ sơ theo vai trò; đổi vai trò chuyển hồ sơ giữa Employee và Admin; thêm E4, AC-10
