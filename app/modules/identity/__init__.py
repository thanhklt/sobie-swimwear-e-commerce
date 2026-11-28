"""Module identity — vai trò, tài khoản, phiên đăng nhập, sổ địa chỉ (BR-001).

Use case: specs/use-cases/identity/ (UC-01 → UC-08, UC-41).
Bảng sở hữu: identity.role, identity.account, identity.session, identity.shipping_address.

Phạm vi:
- Đăng ký (Khách hàng), đăng nhập bằng email hoặc SĐT, đăng xuất, đổi mật khẩu.
- Phiên đăng nhập phía server (identity.session, cookie HttpOnly + Secure + SameSite=Lax).
- Sổ địa chỉ giao hàng (UC-41): nhiều địa chỉ / khách, đúng 1 mặc định; mirror lên account_*.
- Admin tạo / sửa / khóa tài khoản; đổi vai trò NV ↔ Admin.

Service công khai (cho ordering / shopping):
- list_shipping_addresses / get_default_shipping_address / add_shipping_address /
  set_default_shipping_address / get_shipping_address
- authenticate_session

Phụ thuộc module khác (chỉ qua service công khai):
- (không có)
"""
