"""Module identity — vai trò, tài khoản, hồ sơ (BR-001).

Use case: specs/use-cases/identity/ (UC-01 → UC-08).
Bảng sở hữu: identity.role, identity.account, identity.customer, identity.employee, identity.admin.

Phạm vi:
- Đăng ký (Khách hàng), đăng nhập bằng email hoặc SĐT, đăng xuất, đổi mật khẩu.
- Cập nhật hồ sơ Khách hàng.
- Admin tạo tài khoản mọi vai trò, sửa, khóa / mở khóa tài khoản.
- Đổi vai trò chỉ giữa Nhân viên và Admin; luôn còn ít nhất 1 Admin đang hoạt động.
- Cấp mã tự nhiên KH- / NV- / AD- (bộ đếm 4 số chung cho cả bảng).

Phụ thuộc module khác (chỉ qua service công khai):
- (không có)
"""
