# UC-06: Admin tạo tài khoản

## Metadata
- **ID:** UC-06
- **Module:** identity
- **Liên quan tới BR:** BR-001
- **Status:** draft

## Actor
Admin

## Trigger
Admin bấm "Tạo tài khoản" trong khu vực quản lý tài khoản.

## Preconditions
- Admin đang đăng nhập.

## Main Flow
1. Admin mở form tạo tài khoản.
2. Admin nhập họ tên, ngày sinh, địa chỉ, email, số điện thoại và mật khẩu ban đầu. Admin chọn vai trò từ danh sách thả xuống gồm Khách hàng, Nhân viên và Admin. Ngày sinh bắt buộc với Nhân viên và Admin (mã tài khoản dùng ngày sinh).
3. Hệ thống kiểm tra dữ liệu hợp lệ, gồm mật khẩu ban đầu có ít nhất 6 ký tự, vai trò thuộc danh sách cho phép và email, số điện thoại chưa được dùng.
4. Trong cùng một transaction, hệ thống cấp mã tài khoản theo vai trò (`KH-<YYYYMMDD ngày tạo>-<4 số>`, `NV-` / `AD-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>`) và tạo account gồm email, số điện thoại, mật khẩu đã hash, vai trò đã chọn, trạng thái Hoạt động, họ tên, ngày sinh, địa chỉ. Nếu vai trò là Khách hàng, hệ thống đồng thời tạo giỏ hàng và danh sách yêu thích trống (đã chốt 21/11/2026).
5. Hệ thống báo tạo thành công; tài khoản mới hiện trong danh sách tài khoản (UC-07).

## Alternative Flows
- —

## Exceptions
- **E1. Email hoặc số điện thoại đã được dùng:** hệ thống báo trường bị trùng, không tạo tài khoản.
- **E2. Dữ liệu không hợp lệ:** thiếu trường bắt buộc, sai định dạng hoặc mật khẩu ban đầu dưới 6 ký tự — hệ thống báo lỗi tại trường tương ứng, không tạo tài khoản.
- **E4. Thiếu ngày sinh khi tạo Nhân viên hoặc Admin:** hệ thống báo lỗi ở ô ngày sinh, không tạo.

## Postconditions
- Có account mới, đăng nhập được ngay bằng mật khẩu ban đầu (UC-02), không bắt buộc đổi mật khẩu ở lần đăng nhập đầu.
- Account có mã theo vai trò (`KH-`, `NV-` hoặc `AD-`).
- Tài khoản vai trò Khách hàng có 1 giỏ hàng trống và 1 danh sách yêu thích trống (UC-18, UC-38).

## Acceptance Criteria

### AC-1: Tạo tài khoản Nhân viên
Given: Admin đang đăng nhập, email "nv1@example.com" chưa được dùng
When: Admin nhập đủ thông tin, chọn vai trò Nhân viên và bấm "Tạo"
Then: hệ thống tạo account vai trò Nhân viên, trạng thái Hoạt động
And: account có mã dạng `NV-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>`
And: tài khoản đăng nhập được bằng mật khẩu ban đầu

### AC-2: Tạo tài khoản Admin
Given: Admin đang đăng nhập
When: Admin tạo tài khoản với vai trò Admin
Then: hệ thống tạo account vai trò Admin
And: account có mã dạng `AD-<HỌ TÊN>-<YYYYMMDD ngày sinh>-<4 số>`

### AC-3: Email hoặc số điện thoại trùng
Given: đã có tài khoản dùng email "nv1@example.com"
When: Admin tạo tài khoản với email "nv1@example.com"
Then: hệ thống báo "Email đã được sử dụng"
And: không có tài khoản mới nào được tạo

### AC-4: Tạo tài khoản Khách hàng
Given: Admin đang đăng nhập, email "kh1@example.com" và số điện thoại "0901234567" chưa được dùng
When: Admin nhập đủ thông tin, chọn vai trò Khách hàng và bấm "Tạo"
Then: hệ thống tạo account vai trò Khách hàng, trạng thái Hoạt động
And: account có mã dạng `KH-<YYYYMMDD ngày tạo>-<4 số>`
And: tài khoản đăng nhập được ngay và đặt hàng được như tài khoản khách tự đăng ký, không bị yêu cầu đổi mật khẩu

### AC-5: Vai trò khác không tạo được tài khoản
Given: Nhân viên hoặc Khách hàng đang đăng nhập
When: người dùng truy cập chức năng tạo tài khoản
Then: hệ thống từ chối truy cập

### AC-6: Chọn vai trò khi tạo tài khoản
Given: Admin đang đăng nhập
When: Admin mở biểu mẫu tạo tài khoản
Then: trường vai trò là danh sách thả xuống với đúng ba lựa chọn Khách hàng, Nhân viên và Admin

### AC-7: Tạo tài khoản thất bại giữa chừng
Given: Admin gửi thông tin hợp lệ để tạo tài khoản Khách hàng
When: việc lưu tài khoản, giỏ hàng hoặc danh sách yêu thích thất bại sau khi cấp mã
Then: hệ thống hoàn tác toàn bộ transaction, gồm cấp mã và tạo các bản ghi liên quan

### AC-8: Mật khẩu ban đầu quá ngắn
Given: Admin đang ở biểu mẫu tạo tài khoản với các thông tin khác hợp lệ
When: Admin gửi mật khẩu ban đầu dưới 6 ký tự
Then: hệ thống báo lỗi tại trường mật khẩu và không tạo tài khoản

### AC-9: Tài khoản Admin có sẵn khi khởi tạo
Given: hệ thống chưa được khởi tạo
When: hệ thống hoàn tất khởi tạo lần đầu
Then: hệ thống có sẵn một tài khoản Admin ở trạng thái Hoạt động để quản lý tài khoản

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập
- **Downstream UC:** UC-07 Sửa tài khoản, UC-08 Khóa và mở khóa tài khoản
- **External Systems:** —

## Notes
- 3 vai trò cố định; không tạo vai trò mới hoặc cấu hình quyền (Out of Scope).
- Danh sách vai trò giới hạn lựa chọn trên giao diện. Khi nhận yêu cầu tạo tài khoản, hệ thống vẫn xác thực vai trò ở phía máy chủ và từ chối dữ liệu ngoài ba giá trị cho phép.

### Quyết định đã chốt
- Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; mọi thao tác vận hành cửa hàng do Nhân viên thực hiện (đã chốt 15/11/2026).
- Account gồm thông tin đăng nhập (email unique, số điện thoại unique, mật khẩu đã hash, vai trò, trạng thái) và thông tin cá nhân (họ tên, ngày sinh, địa chỉ) cho cả 3 vai trò; không có username riêng (đã chốt 21/11/2026, data model v2, thay quyết định hồ sơ riêng theo vai trò ngày 15/11/2026).
- Mã tài khoản do hệ thống cấp theo vai trò, bộ đếm 4 số riêng cho từng tiền tố `KH`, `NV`, `AD`; ngày sinh bắt buộc với Nhân viên và Admin (đã chốt 21/11/2026).
- Admin toàn quyền tạo tài khoản với mọi vai trò: Khách hàng, Nhân viên, Admin (đã chốt 20/11/2026).
- Tài khoản do Admin tạo dùng được ngay, không bắt buộc đổi mật khẩu ở lần đăng nhập đầu (đã chốt 20/11/2026).
- Tài khoản do Admin tạo bắt buộc có email và số điện thoại chưa được tài khoản khác sử dụng.
- Ngày đăng ký trong mã `KH-` lấy theo giờ `Asia/Ho_Chi_Minh` của `account_created_at` (đã chốt 21/11/2026).
- Mật khẩu băm bằng bcrypt (đã chốt 21/11/2026).
- Khi tạo tài khoản Khách hàng, giỏ hàng và danh sách yêu thích trống được tạo cùng transaction tạo account; module identity gọi service công khai của shopping (đã chốt 21/11/2026, Q39).
- Cấp mã và tạo tài khoản trong cùng một transaction. Admin đặt mật khẩu ban đầu có ít nhất 6 ký tự. Hệ thống có sẵn một tài khoản Admin ở trạng thái Hoạt động khi khởi tạo lần đầu (đã chốt 23/11/2026).
- Vai trò được chọn từ danh sách thả xuống gồm ba vai trò cố định (đã chốt 23/11/2026).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt phạm vi quyền của Admin
- v3 (2026-11-15): theo ERD — tạo account và hồ sơ Employee/Admin riêng theo vai trò
- v4 (2026-11-20): Admin tạo được tài khoản mọi vai trò (thêm Khách hàng, tạo hồ sơ Customer); đổi tên UC và file thành `UC-06-create-account.md`; tài khoản dùng được ngay, không bắt buộc đổi mật khẩu
- v5 (2026-11-21): theo data model v2 — bỏ hồ sơ riêng theo vai trò, thông tin cá nhân nằm trong account; cấp mã theo vai trò (bước 4, AC-1, AC-2, AC-4); thêm E4 thiếu ngày sinh cho Nhân viên / Admin
- v6 (2026-11-21): chốt bcrypt và múi giờ của mã `KH-`, bổ sung giả định tạo giỏ hàng và danh sách yêu thích cho Khách hàng
- v7 (2026-11-21): chốt tạo giỏ hàng và danh sách yêu thích cùng transaction tạo tài khoản Khách hàng (Q39)
- v8 (2026-11-23): chốt các giả định của UC-06 và dùng danh sách thả xuống để chọn vai trò. Kiểm tra vai trò ngoài danh sách thuộc xử lý phía máy chủ.
