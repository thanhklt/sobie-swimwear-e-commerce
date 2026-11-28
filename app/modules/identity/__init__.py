"""Module identity — vai trò, tài khoản, phiên đăng nhập (BR-001).

Use case: specs/use-cases/identity/ (UC-01 → UC-08).
Bảng sở hữu: identity.role, identity.account, identity.session.

Phạm vi:
- Đăng ký (Khách hàng), đăng nhập bằng email hoặc SĐT, đăng xuất, đổi mật khẩu.
- Phiên đăng nhập phía server (identity.session, cookie HttpOnly + Secure + SameSite=Lax):
  storefront chỉ cho Khách hàng, portal quản trị chỉ cho Nhân viên / Admin; hạn phiên
  Khách hàng 30 phút, Nhân viên / Admin 1 giờ, gia hạn khi còn thao tác.
- Đổi mật khẩu, đổi vai trò, khóa tài khoản xóa mọi phiên của tài khoản trong cùng transaction.
- Cập nhật thông tin cá nhân của Khách hàng (họ tên, ngày sinh, địa chỉ nằm trong account).
- Admin tạo tài khoản mọi vai trò, sửa, khóa / mở khóa tài khoản.
- Đổi vai trò chỉ giữa Nhân viên và Admin; luôn còn ít nhất 1 Admin đang hoạt động.
- Cấp mã tài khoản KH- / NV- / AD- (bộ đếm 4 số riêng cho từng tiền tố); đổi vai trò NV <-> AD thì cấp mã mới.

Cửa công khai: facade.py.

Phụ thuộc module khác:
- shopping: khởi tạo giỏ hàng và danh sách yêu thích khi tạo Khách hàng.
- notification: gửi OTP qua facade.send_email.
"""
