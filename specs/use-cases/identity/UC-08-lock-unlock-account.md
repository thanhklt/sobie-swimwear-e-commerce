# UC-08: Khóa và mở khóa tài khoản

## Metadata
- **ID:** UC-08
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
- Admin khóa hoặc mở khóa tài khoản.
- Nhân viên khóa tài khoản Khách hàng.

## Trigger
Admin bấm "Khóa" hoặc "Mở khóa" trong danh sách tài khoản. Nhân viên bấm "Khóa" trên tài khoản Khách hàng trong chức năng "Quản lý khách hàng" (UC-07).

## Preconditions
- Admin hoặc Nhân viên đang đăng nhập ở portal quản trị.
- Tài khoản cần thao tác tồn tại.

## Main Flow
1. Người thao tác chọn một tài khoản đang Hoạt động trong phạm vi được phép và bấm "Khóa". Với Nhân viên, tài khoản được chọn phải có vai trò Khách hàng.
2. Hệ thống yêu cầu xác nhận.
3. Người thao tác xác nhận.
4. Hệ thống kiểm tra quyền thao tác. Trong cùng một transaction, hệ thống kiểm tra ràng buộc còn ít nhất một Admin ở trạng thái Hoạt động (E1), chuyển tài khoản sang Bị khóa và xóa mọi phiên (`identity.session`) của tài khoản đó.
5. Hệ thống báo khóa thành công.

## Alternative Flows
- **1a. Mở khóa:** Admin chọn tài khoản đang Bị khóa và bấm "Mở khóa" — sau khi xác nhận, hệ thống chuyển tài khoản về Hoạt động; tài khoản đăng nhập lại được (không có phiên cũ nào được khôi phục).
- **1b. Admin tự khóa chính mình:** được phép khi hệ thống còn ít nhất 1 Admin khác đang hoạt động (E1). Sau khi khóa, phiên của Admin đó bị kết thúc và không đăng nhập lại được cho tới khi một Admin khác mở khóa.
- **3a. Hủy xác nhận:** người thao tác bấm "Hủy". Trạng thái tài khoản giữ nguyên.

## Exceptions
- **E1. Khóa làm hệ thống hết Admin đang hoạt động:** hệ thống từ chối thao tác nếu sau khi khóa không còn tài khoản vai trò Admin ở trạng thái Hoạt động. Trạng thái và các phiên của tài khoản giữ nguyên.
- **E2. Thiếu quyền:** hệ thống từ chối nếu Nhân viên yêu cầu khóa tài khoản Nhân viên hoặc Admin, yêu cầu mở khóa tài khoản, hoặc nếu người yêu cầu không có quyền thao tác. Trạng thái tài khoản và các phiên đăng nhập giữ nguyên.

## Postconditions
- Tài khoản Bị khóa không đăng nhập được (UC-02, E2); tài khoản được mở khóa đăng nhập lại được.
- Sau mỗi thao tác thành công, hệ thống vẫn có ít nhất một tài khoản Admin ở trạng thái Hoạt động.
- Hồ sơ, đơn hàng và dữ liệu nghiệp vụ gắn với tài khoản giữ nguyên khi khóa hoặc mở khóa.

## Acceptance Criteria

### AC-1: Khóa tài khoản
Given: tài khoản Khách hàng "a@example.com" trạng thái Hoạt động
When: Admin bấm "Khóa" và xác nhận
Then: tài khoản chuyển sang Bị khóa
And: đăng nhập bằng "a@example.com" bị từ chối với thông báo "Tài khoản đã bị khóa"
And: hồ sơ và đơn hàng của Khách hàng giữ nguyên

### AC-2: Khóa kết thúc phiên đang mở
Given: Nhân viên "nv1@example.com" đang đăng nhập
When: Admin khóa tài khoản "nv1@example.com"
Then: thao tác tiếp theo của Nhân viên này bị yêu cầu đăng nhập lại

### AC-3: Mở khóa tài khoản
Given: tài khoản "a@example.com" trạng thái Bị khóa
When: Admin bấm "Mở khóa" và xác nhận
Then: tài khoản chuyển về Hoạt động
And: "a@example.com" đăng nhập được

### AC-4: Hủy xác nhận
Given: tài khoản "a@example.com" trạng thái Hoạt động
When: Admin bấm "Khóa" rồi bấm "Hủy" ở bước xác nhận
Then: tài khoản vẫn Hoạt động

### AC-5: Admin tự khóa chính mình
Given: Admin "admin@example.com" đang đăng nhập; hệ thống còn Admin "admin2@example.com" đang hoạt động
When: "admin@example.com" khóa tài khoản của chính mình và xác nhận
Then: "admin@example.com" chuyển sang Bị khóa, phiên đang mở bị kết thúc
And: "admin2@example.com" mở khóa được "admin@example.com"

### AC-7: Không khóa Admin đang hoạt động cuối cùng
Given: "admin@example.com" là Admin đang hoạt động duy nhất và các tài khoản Admin khác đang Bị khóa
When: "admin@example.com" khóa tài khoản của chính mình
Then: hệ thống từ chối
And: tài khoản vẫn Hoạt động và phiên đăng nhập hiện tại còn hiệu lực

### AC-6: Nhân viên không khóa được tài khoản nội bộ
Given: Nhân viên đang đăng nhập
When: Nhân viên gửi yêu cầu khóa một tài khoản Nhân viên hoặc Admin
Then: hệ thống từ chối yêu cầu và trạng thái tài khoản mục tiêu giữ nguyên

### AC-8: Nhân viên khóa tài khoản Khách hàng
Given: Nhân viên đang đăng nhập và một tài khoản Khách hàng đang Hoạt động có phiên hợp lệ
When: Nhân viên bấm "Khóa" và xác nhận trong chức năng "Quản lý khách hàng"
Then: tài khoản Khách hàng chuyển sang Bị khóa và mọi phiên của tài khoản đó kết thúc ngay

### AC-9: Nhân viên không mở khóa tài khoản
Given: Nhân viên đang đăng nhập và một tài khoản Khách hàng đang Bị khóa
When: Nhân viên yêu cầu mở khóa tài khoản đó
Then: hệ thống từ chối yêu cầu và tài khoản vẫn Bị khóa

### AC-10: Khóa và đổi vai trò diễn ra đồng thời
Given: hệ thống có đúng hai Admin ở trạng thái Hoạt động
When: một Admin xác nhận tự khóa và Admin còn lại đồng thời xác nhận tự đổi vai trò thành Nhân viên qua UC-07
Then: tối đa một thao tác thành công và hệ thống vẫn có ít nhất một Admin ở trạng thái Hoạt động

## Dependencies
- **Upstream UC:** UC-07 Sửa tài khoản (danh sách tài khoản cho Admin và chức năng Quản lý khách hàng cho Nhân viên)
- **Downstream UC:** UC-02 Đăng nhập
- **External Systems:** —

## Notes

### Quyết định đã chốt
- Từ khi khởi tạo, hệ thống luôn có ít nhất một tài khoản vai trò Admin ở trạng thái Hoạt động. Cả thao tác khóa (UC-08) và đổi vai trò (UC-07) phải giữ ràng buộc này (xác nhận lại 23/11/2026).
- Kiểm tra ràng buộc trong cùng transaction với cập nhật tài khoản. UC-07 và UC-08 dùng chung cơ chế khóa các dòng tài khoản Admin để các thao tác đồng thời không cùng vượt qua kiểm tra.
- Admin được tự khóa chính mình khi còn ít nhất 1 Admin khác đang hoạt động (đã chốt 20/11/2026).
- Khóa tài khoản kết thúc ngay mọi phiên đăng nhập đang mở của tài khoản đó, bằng cách xóa các dòng `identity.session` của tài khoản trong cùng transaction với thao tác khóa (đã chốt 21/11/2026; BR-GIAIDOAN1, Constraints chung — Xác thực; data model v2.15, Q35).
- Nhân viên được khóa tài khoản có vai trò Khách hàng. Quyền mở khóa thuộc Admin (đã chốt 23/11/2026).
- Admin có thể khóa và mở khóa tài khoản của cả ba vai trò, tuân theo E1. Khóa và mở khóa giữ nguyên dữ liệu nghiệp vụ của tài khoản (đã chốt 23/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-20): theo data model v2 — không khóa Admin đang hoạt động cuối cùng (E2, AC-7)
- v3 (2026-11-20): cho Admin tự khóa chính mình khi còn Admin khác đang hoạt động (bỏ E1 cũ, thêm 1b, AC-5 viết lại); E2 đổi thành E1, AC-7 viết lại
- v4 (2026-11-21): chốt khóa kết thúc ngay mọi phiên bằng `account_token_version` (bước 4, 1a, Notes)
- v5 (2026-11-21): theo BR-GIAIDOAN1 v21 — kết thúc phiên bằng xóa `identity.session` thay cho `account_token_version` (bước 4, 1a, Notes)
- v6 (2026-11-23): thêm quyền Nhân viên khóa tài khoản Khách hàng và phân biệt với quyền mở khóa của Admin.
- v7 (2026-11-23): chốt phạm vi khóa và mở khóa của Admin, giữ dữ liệu tài khoản và đồng bộ ràng buộc còn ít nhất một Admin hoạt động với UC-07.
