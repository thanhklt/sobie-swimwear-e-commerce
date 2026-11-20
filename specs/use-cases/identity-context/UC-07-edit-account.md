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
2. Hệ thống hiển thị danh sách tài khoản có phân trang `[GD]`: họ tên, email, số điện thoại, vai trò, trạng thái.
3. Admin tìm theo họ tên, email hoặc số điện thoại `[GD]` và chọn một tài khoản.
4. Admin sửa họ tên, ngày sinh, địa chỉ, email, số điện thoại, và có thể đổi vai trò sang bất kỳ vai trò nào trong 3 vai trò cố định: Khách hàng, Nhân viên, Admin.
5. Hệ thống kiểm tra dữ liệu hợp lệ và email, số điện thoại không trùng tài khoản khác.
6. Trong cùng một transaction `[GD]`, hệ thống lưu thông tin và vai trò mới, báo cập nhật thành công. Họ tên, ngày sinh, địa chỉ, email, số điện thoại, mật khẩu được giữ nguyên khi đổi vai trò.
7. Nếu vai trò được đổi, hệ thống kết thúc ngay mọi phiên đang mở của tài khoản đó; vai trò mới có hiệu lực ngay.

## Alternative Flows
- **3a. Không tìm thấy:** từ khóa không khớp tài khoản nào — hệ thống hiển thị danh sách rỗng kèm thông báo "Không tìm thấy tài khoản".
- **4a. Đổi Khách hàng sang Nhân viên hoặc Admin:** lịch sử đơn hàng và hóa đơn của tài khoản được giữ nguyên; tài khoản không còn đặt hàng, xem giỏ hàng, danh sách yêu thích hay theo dõi đơn ở phía khách `[GD]`. Đơn đang xử lý của tài khoản vẫn tiếp tục vòng đời bình thường `[GD]`.
- **4b. Đổi Nhân viên hoặc Admin sang Khách hàng:** lịch sử thao tác cũ (ví dụ người đổi trạng thái đơn) được giữ nguyên; tài khoản mất quyền vào khu vực quản trị và dùng được các chức năng của Khách hàng như tài khoản khách tự đăng ký `[GD]`.

## Exceptions
- **E1. Email hoặc số điện thoại trùng tài khoản khác:** hệ thống báo trường bị trùng, không lưu.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc hoặc sai định dạng — hệ thống báo lỗi, không lưu.
- **E3. Admin tự đổi vai trò của chính mình** `[GD]` — hệ thống từ chối.
- **E4. Đổi vai trò làm hệ thống không còn Admin nào đang hoạt động** `[GD]` — hệ thống từ chối.
- **E5. Lỗi khi lưu:** hệ thống hủy toàn bộ transaction; thông tin và vai trò giữ nguyên, phiên đăng nhập không bị kết thúc `[GD]`.

## Postconditions
- Thông tin tài khoản được cập nhật.
- Nếu đổi vai trò: tài khoản có vai trò mới, giữ nguyên thông tin cá nhân và thông tin đăng nhập; vai trò mới có hiệu lực ngay; tài khoản đang đăng nhập bị đăng xuất và phải đăng nhập lại với vai trò mới.

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
Then: tài khoản có vai trò Admin
And: họ tên, ngày sinh, địa chỉ, email, số điện thoại không đổi

### AC-6: Email trùng
Given: đã có tài khoản khác dùng email "nv2@example.com"
When: Admin đổi email của "nv1@example.com" thành "nv2@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: tài khoản giữ nguyên email cũ

### AC-7: Đổi vai trò Khách hàng sang Nhân viên
Given: tài khoản "a@example.com" có vai trò Khách hàng, đã có 2 đơn hàng
When: Admin đổi vai trò của tài khoản này thành Nhân viên và bấm "Lưu"
Then: tài khoản có vai trò Nhân viên, đăng nhập lại thì vào khu vực quản trị
And: 2 đơn hàng cũ vẫn còn trong hệ thống, Nhân viên vẫn xem được trong trang quản lý đơn
And: họ tên, ngày sinh, địa chỉ, email, số điện thoại không đổi

### AC-8: Đổi vai trò Nhân viên sang Khách hàng
Given: tài khoản "nv1@example.com" có vai trò Nhân viên, từng xác nhận đơn 7K3M9Q2X
When: Admin đổi vai trò của tài khoản này thành Khách hàng và bấm "Lưu"
Then: tài khoản có vai trò Khách hàng, không vào được khu vực quản trị
And: tài khoản đặt hàng được như tài khoản khách tự đăng ký
And: lịch sử trạng thái đơn 7K3M9Q2X vẫn ghi "nv1@example.com" là người xác nhận

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

### AC-11: Admin không tự đổi vai trò của mình
Given: Admin "admin@example.com" đang đăng nhập
When: Admin đổi vai trò của chính mình thành Nhân viên
Then: hệ thống từ chối, vai trò giữ nguyên Admin

### AC-12: Lỗi khi lưu
Given: tài khoản "nv1@example.com" có vai trò Nhân viên
When: Admin đổi vai trò thành Khách hàng nhưng việc lưu thất bại
Then: vai trò vẫn là Nhân viên, thông tin không đổi
And: phiên đăng nhập của "nv1@example.com" không bị kết thúc
And: hệ thống báo cập nhật không thành công

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-01 Đăng ký tài khoản, UC-06 Admin tạo tài khoản
- **Downstream UC:** UC-08 Khóa và mở khóa tài khoản
- **External Systems:** —

## Notes
- Áp dụng constraint cache danh sách (BR-GIAIDOAN1, Constraints chung).
- Admin không đặt lại mật khẩu cho người khác trong UC này (không có trong BR).
- UC mô tả ở mức nghiệp vụ, không ràng buộc cách lưu hồ sơ theo vai trò; data model sẽ được developer thiết kế lại (20/11/2026).

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Admin đổi được vai trò của tài khoản sang bất kỳ vai trò nào trong 3 vai trò cố định (Khách hàng, Nhân viên, Admin); không tạo vai trò mới hoặc cấu hình quyền (đã chốt 15/11/2026, mở rộng 20/11/2026).
- Vai trò mới có hiệu lực ngay khi được đổi; nếu tài khoản đang đăng nhập thì bị đăng xuất (đã chốt 15/11/2026).

### Giả định [GD]
- Việc xem và tìm danh sách tài khoản gộp vào UC này.
- Danh sách có phân trang; tìm theo họ tên, email hoặc số điện thoại.
- Admin sửa được thông tin mọi tài khoản.
- Admin không tự đổi vai trò của chính mình.
- Không cho đổi vai trò khiến hệ thống không còn Admin nào đang hoạt động.
- Đổi vai trò giữ nguyên thông tin cá nhân, email, số điện thoại, mật khẩu; lưu thông tin và vai trò trong một transaction, lỗi thì hủy toàn bộ.
- Khách hàng đổi sang vai trò nội bộ: giữ lịch sử đơn hàng và hóa đơn; đơn đang xử lý tiếp tục bình thường; không còn dùng chức năng phía khách.
- Nhân viên/Admin đổi sang Khách hàng: giữ lịch sử thao tác cũ; dùng chức năng Khách hàng như tài khoản tự đăng ký.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): chốt Admin chỉ gán vai trò (Nhân viên ↔ Admin), không tạo vai trò mới
- v4 (2026-11-15): chốt vai trò mới có hiệu lực ngay, tài khoản đang đăng nhập bị đăng xuất; thêm AC-9
- v5 (2026-11-15): theo ERD — tách account và hồ sơ theo vai trò; đổi vai trò chuyển hồ sơ giữa Employee và Admin; thêm E4, AC-10
- v6 (2026-11-20): cho đổi sang mọi vai trò (gồm Khách hàng ↔ Nhân viên/Admin); bỏ mô tả chuyển hồ sơ giữa các bảng (không dựa vào data model hiện tại); thêm E4 không để hệ thống hết Admin, AC-7, AC-8, AC-11, AC-12
