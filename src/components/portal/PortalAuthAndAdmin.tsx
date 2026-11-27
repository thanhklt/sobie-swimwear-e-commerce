import React, { useState } from 'react';
import {
  Shield,
  Plus,
  Search,
  Lock,
  Unlock,
  Edit3,
  KeyRound,
  X,
  Eye,
  Users,
  CheckCircle2,
} from 'lucide-react';
import { useSobieSystem } from '../../context/SobieSystemContext';
import { AccountRecord, RoleCode } from '../../types/store';

/* ============================================================================
 * 1. ADMIN ACCOUNT GOVERNANCE WORKSPACE (UC-06 Create, UC-07 Edit & Swap, UC-08 Lock/Unlock)
 * ============================================================================ */
export const AdminAccountsView: React.FC = () => {
  const {
    accounts,
    adminCreateAccount,
    adminEditAccount,
    adminToggleLockAccount,
  } = useSobieSystem();

  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showCreate, setShowCreate] = useState(false);
  const [editingAcc, setEditingAcc] = useState<AccountRecord | null>(null);
  const [confirmLockAcc, setConfirmLockAcc] = useState<AccountRecord | null>(
    null
  );
  const [formErr, setFormErr] = useState<string | null>(null);

  // Create fields
  const [cName, setCName] = useState('');
  const [cRole, setCRole] = useState<RoleCode>('employee');
  const [cEmail, setCEmail] = useState('');
  const [cPhone, setCPhone] = useState('');
  const [cPassword, setCPassword] = useState('');
  const [cDob, setCDob] = useState('1999-05-15');
  const [cHouse, setCHouse] = useState('');
  const [cWard, setCWard] = useState('');
  const [cCity, setCCity] = useState('');

  // Edit fields
  const [eName, setEName] = useState('');
  const [eRole, setERole] = useState<RoleCode>('employee');
  const [eEmail, setEEmail] = useState('');
  const [ePhone, setEPhone] = useState('');
  const [eDob, setEDob] = useState('');
  const [eHouse, setEHouse] = useState('');
  const [eWard, setEWard] = useState('');
  const [eCity, setECity] = useState('');

  const activeAdminCount = accounts.filter(
    (a) => a.role === 'admin' && a.status === 'ACTIVE'
  ).length;
  const employeeCount = accounts.filter((a) => a.role === 'employee').length;
  const customerCount = accounts.filter((a) => a.role === 'customer').length;
  const lockedCount = accounts.filter((a) => a.status === 'LOCKED').length;

  const filtered = accounts.filter((a) => {
    if (roleFilter && a.role !== roleFilter) return false;
    if (statusFilter && a.status !== statusFilter) return false;
    const q = query.trim().toLowerCase();
    if (!q) return true;
    return (
      a.name.toLowerCase().includes(q) ||
      a.email.toLowerCase().includes(q) ||
      a.phone.includes(q) ||
      a.accountId.toLowerCase().includes(q)
    );
  });

  const openEdit = (acc: AccountRecord) => {
    setFormErr(null);
    setEditingAcc(acc);
    setEName(acc.name);
    setERole(acc.role);
    setEEmail(acc.email);
    setEPhone(acc.phone);
    setEDob(acc.dateOfBirth);
    setEHouse(acc.houseNumber);
    setEWard(acc.ward);
    setECity(acc.city);
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormErr(null);
    const res = adminCreateAccount({
      name: cName,
      role: cRole,
      email: cEmail,
      phone: cPhone,
      password: cPassword,
      dateOfBirth: cDob,
      houseNumber: cHouse,
      ward: cWard,
      city: cCity,
    });
    if (!res.ok) {
      setFormErr(res.error ?? 'Không thể tạo tài khoản.');
      return;
    }
    setShowCreate(false);
    setCName('');
    setCEmail('');
    setCPhone('');
    setCPassword('');
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingAcc) return;
    setFormErr(null);
    const res = adminEditAccount(editingAcc.accountId, {
      name: eName,
      email: eEmail,
      phone: ePhone,
      dateOfBirth: eDob,
      houseNumber: eHouse,
      ward: eWard,
      city: eCity,
      role: eRole,
    });
    if (!res.ok) {
      setFormErr(res.error ?? 'Cập nhật không thành công.');
      return;
    }
    setEditingAcc(null);
  };

  const roleBadge = (r: RoleCode) => {
    if (r === 'admin') return 'bg-[#22261E] text-[#FAF7F2]';
    if (r === 'employee') return 'bg-[#E5ECE0] text-[#3B4B35] border border-[#C5D1BE]';
    return 'bg-[#F3EFE6] text-[#5E6658] border border-[#E4DDD0]';
  };

  const roleLabel = (r: RoleCode) =>
    r === 'admin'
      ? 'Admin'
      : r === 'employee'
      ? 'Saler / Nhân viên'
      : 'Khách hàng';

  return (
    <div className="space-y-7">
      {/* Masthead */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <Shield className="w-3.5 h-3.5" />
            <span>Không Gian Quản Trị Admin Toàn Viền · UC-06 / UC-07 / UC-08</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Quản lý tài khoản & Gán vai trò hệ thống
          </h1>
          <p className="text-xs text-[#5E6658] mt-1 max-w-3xl">
            Admin toàn quyền tạo tài khoản cho cả 3 vai trò (dùng được ngay), sửa hồ sơ (kể cả email Khách hàng theo UC-04 AC-5), hoán đổi Nhân viên ↔ Admin cấp mã `NV-` / `AD-` mới và khóa/mở khóa toàn hệ thống với bất biến luôn còn ít nhất 1 Admin Hoạt động.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setFormErr(null);
            setShowCreate(true);
          }}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#4A5D43] text-white text-xs sm:text-sm font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer shadow-xs"
        >
          <Plus className="w-4 h-4" />
          <span>Tạo tài khoản mới (UC-06)</span>
        </button>
      </div>

      {/* Full-Width 5 KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
        <div className="p-5 rounded-3xl atelier-card">
          <span className="text-xs text-[#5E6658]">Tổng tài khoản</span>
          <p className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 tabular-price">
            {accounts.length}
          </p>
        </div>
        <div className="p-5 rounded-3xl atelier-card">
          <span className="text-xs text-[#4A5D43] font-semibold">
            Admin Hoạt động (Ràng buộc ≥ 1)
          </span>
          <p className="font-editorial text-3xl font-semibold text-[#4A5D43] mt-1 tabular-price">
            {activeAdminCount}
          </p>
        </div>
        <div className="p-5 rounded-3xl atelier-card">
          <span className="text-xs text-[#5E6658]">Saler / Nhân viên</span>
          <p className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 tabular-price">
            {employeeCount}
          </p>
        </div>
        <div className="p-5 rounded-3xl atelier-card">
          <span className="text-xs text-[#5E6658]">Khách hàng</span>
          <p className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 tabular-price">
            {customerCount}
          </p>
        </div>
        <div className="p-5 rounded-3xl atelier-card">
          <span className="text-xs text-[#8E3B2E]">Đang bị khóa</span>
          <p className="font-editorial text-3xl font-semibold text-[#8E3B2E] mt-1 tabular-price">
            {lockedCount}
          </p>
        </div>
      </div>

      {/* All-Visible Filter & Search Bar (NO Horizontal Scroll!) */}
      <div className="p-5 rounded-3xl atelier-card grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
        <div className="lg:col-span-5 relative">
          <Search className="w-4 h-4 text-[#878E80] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm theo họ tên, email, SĐT hoặc mã tài khoản..."
            className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
          />
        </div>

        <div className="lg:col-span-4 flex flex-wrap items-center gap-1.5">
          {(
            [
              { id: '', label: 'Mọi vai trò' },
              { id: 'admin', label: 'Admin' },
              { id: 'employee', label: 'Saler' },
              { id: 'customer', label: 'Khách hàng' },
            ] as const
          ).map((rf) => (
            <button
              key={rf.id}
              type="button"
              onClick={() => setRoleFilter(rf.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
                roleFilter === rf.id
                  ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                  : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
              }`}
            >
              {rf.label}
            </button>
          ))}
        </div>

        <div className="lg:col-span-3 flex flex-wrap items-center lg:justify-end gap-1.5">
          {(
            [
              { id: '', label: 'Mọi trạng thái' },
              { id: 'ACTIVE', label: 'Hoạt động' },
              { id: 'LOCKED', label: 'Bị khóa' },
            ] as const
          ).map((sf) => (
            <button
              key={sf.id}
              type="button"
              onClick={() => setStatusFilter(sf.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
                statusFilter === sf.id
                  ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                  : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
              }`}
            >
              {sf.label}
            </button>
          ))}
        </div>
      </div>

      {formErr && !showCreate && !editingAcc && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] font-medium">
          {formErr}
        </div>
      )}

      {/* Full-Width Accounts Table */}
      <div className="rounded-3xl atelier-card overflow-hidden">
        <table className="w-full text-xs text-left">
          <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase tracking-wider text-[11px]">
            <tr>
              <th className="px-5 py-3.5">Mã tài khoản</th>
              <th className="px-5 py-3.5">Họ tên & Ngày sinh</th>
              <th className="px-5 py-3.5">Email & Số điện thoại</th>
              <th className="px-5 py-3.5">Địa chỉ</th>
              <th className="px-5 py-3.5">Vai trò</th>
              <th className="px-5 py-3.5">Trạng thái</th>
              <th className="px-5 py-3.5 text-right">Thao tác (UC-07/08)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4DDD0]">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-12 text-center text-[#5E6658]">
                  Không tìm thấy tài khoản (UC-07 AC-3)
                </td>
              </tr>
            ) : (
              filtered.map((acc) => (
                <tr key={acc.accountId} className="hover:bg-[#FAF7F2]">
                  <td className="px-5 py-4 font-mono font-semibold text-[#22261E]">
                    {acc.accountId}
                    {acc.googleSub && (
                      <span className="block text-[10px] font-sans text-[#4A5D43] mt-0.5">
                        Đã liên kết Google
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-4 font-medium text-[#22261E]">
                    {acc.name || '—'}
                    {acc.dateOfBirth && (
                      <span className="block text-[11px] text-[#878E80]">
                        NS: {acc.dateOfBirth}
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-[#5E6658]">
                    <div className="text-[#22261E]">{acc.email}</div>
                    <div>{acc.phone || 'Chưa bổ sung SĐT'}</div>
                  </td>
                  <td className="px-5 py-4 text-[#5E6658] max-w-xs">
                    {[acc.houseNumber, acc.ward, acc.city]
                      .filter(Boolean)
                      .join(', ') || '—'}
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${roleBadge(
                        acc.role
                      )}`}
                    >
                      {roleLabel(acc.role)}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                        acc.status === 'ACTIVE'
                          ? 'bg-[#E3F2E8] text-[#1F5E39]'
                          : 'bg-[#FBECE9] text-[#8E3B2E]'
                      }`}
                    >
                      {acc.status === 'ACTIVE' ? 'Hoạt động' : 'Bị khóa'}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right">
                    <div className="inline-flex flex-wrap justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => openEdit(acc)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-[#D4CBB8] bg-white hover:border-[#4A5D43] text-[#22261E] font-medium cursor-pointer"
                      >
                        <Edit3 className="w-3 h-3 text-[#4A5D43]" />
                        <span>Sửa</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setFormErr(null);
                          setConfirmLockAcc(acc);
                        }}
                        className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full border font-semibold cursor-pointer ${
                          acc.status === 'ACTIVE'
                            ? 'border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9]'
                            : 'border-[#B7DEC5] text-[#1F5E39] hover:bg-[#E3F2E8]'
                        }`}
                      >
                        {acc.status === 'ACTIVE' ? (
                          <>
                            <Lock className="w-3 h-3" />
                            <span>Khóa</span>
                          </>
                        ) : (
                          <>
                            <Unlock className="w-3 h-3" />
                            <span>Mở khóa</span>
                          </>
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* UC-06 Create Account Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <form
            onSubmit={handleCreateSubmit}
            className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-xl w-full p-7 space-y-4 shadow-2xl text-xs"
          >
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                Admin tạo tài khoản mới (UC-06)
              </h3>
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {formErr && (
              <div className="px-3.5 py-2.5 rounded-xl bg-[#FBECE9] text-[#8E3B2E]">
                {formErr}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="font-medium">Vai trò *</span>
                <select
                  value={cRole}
                  onChange={(e) => setCRole(e.target.value as RoleCode)}
                  className="w-full px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                >
                  <option value="employee">Nhân viên (Saler)</option>
                  <option value="admin">Admin</option>
                  <option value="customer">Khách hàng</option>
                </select>
              </label>
              <label className="space-y-1">
                <span className="font-medium">
                  Ngày sinh {cRole !== 'customer' ? '* (Bắt buộc)' : '(Tùy chọn)'}
                </span>
                <input
                  type="date"
                  required={cRole !== 'customer'}
                  value={cDob}
                  onChange={(e) => setCDob(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <input
                type="text"
                required
                value={cName}
                onChange={(e) => setCName(e.target.value)}
                placeholder="Họ và tên *"
                className="px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
              <input
                type="password"
                required
                value={cPassword}
                onChange={(e) => setCPassword(e.target.value)}
                placeholder="Mật khẩu ban đầu (≥ 6 ký tự) *"
                className="px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
              <input
                type="email"
                required
                value={cEmail}
                onChange={(e) => setCEmail(e.target.value)}
                placeholder="Email *"
                className="px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
              <input
                type="tel"
                required
                value={cPhone}
                onChange={(e) => setCPhone(e.target.value)}
                placeholder="Số điện thoại *"
                className="px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
            </div>

            <div className="grid grid-cols-3 gap-2.5">
              <input
                type="text"
                value={cHouse}
                onChange={(e) => setCHouse(e.target.value)}
                placeholder="Số nhà, đường"
                className="px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
              <input
                type="text"
                value={cWard}
                onChange={(e) => setCWard(e.target.value)}
                placeholder="Phường / Xã"
                className="px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
              <input
                type="text"
                value={cCity}
                onChange={(e) => setCCity(e.target.value)}
                placeholder="Tỉnh / Thành phố"
                className="px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
            </div>

            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="submit"
                className="px-6 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Tạo tài khoản ngay
              </button>
            </div>
          </form>
        </div>
      )}

      {/* UC-07 Edit Account Modal (Single Save Button for Profile + Role Swap) */}
      {editingAcc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <form
            onSubmit={handleEditSubmit}
            className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-xl w-full p-7 space-y-4 shadow-2xl text-xs"
          >
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <div>
                <p className="text-[11px] font-mono text-[#5E6658]">
                  {editingAcc.accountId}
                </p>
                <h3 className="font-editorial text-2xl text-[#22261E]">
                  Sửa thông tin & Vai trò tài khoản (UC-07)
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setEditingAcc(null)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {formErr && (
              <div className="px-3.5 py-2.5 rounded-xl bg-[#FBECE9] text-[#8E3B2E]">
                {formErr}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="font-medium">Họ và tên *</span>
                <input
                  type="text"
                  required
                  value={eName}
                  onChange={(e) => setEName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>

              <label className="space-y-1">
                <span className="font-medium">Vai trò (UC-07 AC-7/AC-8)</span>
                {editingAcc.role === 'customer' ? (
                  <input
                    type="text"
                    disabled
                    value="Khách hàng (Cố định vai trò)"
                    className="w-full px-3 py-2.5 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] text-[#5E6658]"
                  />
                ) : (
                  <select
                    value={eRole}
                    onChange={(e) => setERole(e.target.value as RoleCode)}
                    className="w-full px-3 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                  >
                    <option value="employee">Nhân viên (Saler)</option>
                    <option value="admin">Admin</option>
                  </select>
                )}
              </label>

              <label className="space-y-1">
                <span className="font-medium">Email * (Admin được sửa)</span>
                <input
                  type="email"
                  required
                  value={eEmail}
                  onChange={(e) => setEEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium">Số điện thoại</span>
                <input
                  type="tel"
                  value={ePhone}
                  onChange={(e) => setEPhone(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium">Ngày sinh</span>
                <input
                  type="date"
                  value={eDob}
                  onChange={(e) => setEDob(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium">Tỉnh / Thành phố</span>
                <input
                  type="text"
                  value={eCity}
                  onChange={(e) => setECity(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium">Số nhà, đường</span>
                <input
                  type="text"
                  value={eHouse}
                  onChange={(e) => setEHouse(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium">Phường / Xã</span>
                <input
                  type="text"
                  value={eWard}
                  onChange={(e) => setEWard(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
            </div>

            {editingAcc.role !== 'customer' && eRole !== editingAcc.role && (
              <div className="p-3.5 rounded-xl bg-[#FBF4E4] border border-[#E8D2A6] text-[11.5px] text-[#8A5A14]">
                Lưu ý UC-07: Bấm «Lưu» sẽ cập nhật hồ sơ và vai trò trong cùng 1 transaction, cấp mã mới (`NV-` ↔ `AD-`) và kết thúc ngay mọi phiên đang mở của tài khoản này.
              </div>
            )}

            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setEditingAcc(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="submit"
                className="px-6 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Lưu (Hồ sơ & Vai trò)
              </button>
            </div>
          </form>
        </div>
      )}

      {/* UC-08 Lock / Unlock Confirmation Modal */}
      {confirmLockAcc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-md w-full p-7 space-y-4 shadow-2xl">
            <h3 className="font-editorial text-2xl text-[#22261E]">
              {confirmLockAcc.status === 'ACTIVE'
                ? `Khóa tài khoản ${confirmLockAcc.accountId}?`
                : `Mở khóa tài khoản ${confirmLockAcc.accountId}?`}
            </h3>
            <p className="text-xs text-[#5E6658] leading-relaxed">
              {confirmLockAcc.status === 'ACTIVE'
                ? 'Tài khoản bị khóa sẽ xóa ngay mọi dòng `identity.session`, kết thúc phiên đăng nhập hiện có và giữ nguyên toàn bộ dữ liệu nghiệp vụ (UC-08).'
                : 'Tài khoản sẽ chuyển về Hoạt động để đăng nhập lại (không khôi phục phiên cũ — UC-08 1a).'}
            </p>
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setConfirmLockAcc(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white text-xs cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={() => {
                  const res = adminToggleLockAccount(confirmLockAcc.accountId);
                  if (!res.ok) setFormErr(res.error ?? null);
                  setConfirmLockAcc(null);
                }}
                className="px-5 py-2 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Xác nhận
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 2. SALER CUSTOMER MANAGEMENT VIEW (NEW IN SPECS: UC-07 AC-14/15 & UC-08 AC-8/9)
 * ============================================================================ */
export const SalerCustomersView: React.FC = () => {
  const { accounts, orders, salerLockCustomerAccount } = useSobieSystem();

  const [query, setQuery] = useState('');
  const [inspectingCustomer, setInspectingCustomer] =
    useState<AccountRecord | null>(null);
  const [confirmLockTarget, setConfirmLockTarget] =
    useState<AccountRecord | null>(null);
  const [err, setErr] = useState<string | null>(null);

  // UC-07 AC-14 & AC-15: Saler sees ONLY customer accounts (never internal employee/admin!)
  const customers = accounts
    .filter((a) => a.role === 'customer')
    .filter((a) => {
      const q = query.trim().toLowerCase();
      if (!q) return true;
      return (
        a.name.toLowerCase().includes(q) ||
        a.email.toLowerCase().includes(q) ||
        a.phone.includes(q) ||
        a.accountId.toLowerCase().includes(q)
      );
    });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <Users className="w-3.5 h-3.5" />
            <span>Quản Lý Khách Hàng Dành Cho Saler · UC-07 (1a) & UC-08 (AC-8/AC-9)</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Tra cứu hồ sơ & Khóa tài khoản Khách hàng
          </h1>
          <p className="text-xs text-[#5E6658] mt-1">
            Theo đặc tả mới trên `main`: Nhân viên được xem hồ sơ & trạng thái của tài khoản Khách hàng (không hiển thị tài khoản nội bộ, không sửa thông tin — UC-07 AC-9/14/15) và được quyền Khóa Khách hàng; quyền Mở khóa thuộc về Admin (UC-08 AC-8/9).
          </p>
        </div>
      </div>

      {err && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {err}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-8 space-y-4">
          <div className="p-4 rounded-2xl atelier-card flex items-center gap-3">
            <Search className="w-4 h-4 text-[#878E80]" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tìm Khách hàng theo họ tên, email, SĐT hoặc mã KH-..."
              className="flex-1 bg-transparent text-xs text-[#22261E] focus:outline-none"
            />
          </div>

          <div className="rounded-3xl atelier-card overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Mã KH</th>
                  <th className="px-5 py-3.5">Họ tên</th>
                  <th className="px-5 py-3.5">Email / SĐT</th>
                  <th className="px-5 py-3.5">Trạng thái</th>
                  <th className="px-5 py-3.5 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4DDD0]">
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-10 text-center text-[#5E6658]">
                      Không tìm thấy tài khoản Khách hàng
                    </td>
                  </tr>
                ) : (
                  customers.map((c) => (
                    <tr key={c.accountId} className="hover:bg-[#FAF7F2]">
                      <td className="px-5 py-3.5 font-mono font-semibold text-[#22261E]">
                        {c.accountId}
                      </td>
                      <td className="px-5 py-3.5 font-medium text-[#22261E]">
                        {c.name || 'Chưa cập nhật tên'}
                      </td>
                      <td className="px-5 py-3.5 text-[#5E6658]">
                        <div className="text-[#22261E]">{c.email}</div>
                        <div>{c.phone || '—'}</div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                            c.status === 'ACTIVE'
                              ? 'bg-[#E3F2E8] text-[#1F5E39]'
                              : 'bg-[#FBECE9] text-[#8E3B2E]'
                          }`}
                        >
                          {c.status === 'ACTIVE' ? 'Hoạt động' : 'Bị khóa'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <div className="inline-flex flex-wrap justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => setInspectingCustomer(c)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-[#D4CBB8] bg-white hover:border-[#4A5D43] text-[#22261E] cursor-pointer"
                          >
                            <Eye className="w-3.5 h-3.5 text-[#4A5D43]" />
                            <span>Xem hồ sơ</span>
                          </button>

                          {c.status === 'ACTIVE' ? (
                            <button
                              type="button"
                              onClick={() => {
                                setErr(null);
                                setConfirmLockTarget(c);
                              }}
                              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9] font-semibold cursor-pointer"
                            >
                              <Lock className="w-3 h-3" />
                              <span>Khóa (UC-08)</span>
                            </button>
                          ) : (
                            <span className="px-3 py-1.5 rounded-full bg-[#F3EFE6] text-[#878E80] text-[11px]">
                              Chỉ Admin mở khóa
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right 4-Col Read-Only Customer Profile Inspector */}
        <div className="xl:col-span-4 rounded-3xl atelier-card p-6 space-y-4 text-xs">
          <h3 className="font-editorial text-2xl text-[#22261E]">
            Chi tiết hồ sơ Khách hàng (Chỉ xem)
          </h3>
          {!inspectingCustomer ? (
            <p className="text-[#5E6658] py-8 text-center">
              Chọn nút «Xem hồ sơ» ở một dòng bên trái để kiểm tra thông tin khách hàng.
            </p>
          ) : (
            <div className="space-y-3">
              <div className="p-3.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1">
                <span className="text-[#878E80] block">Mã tài khoản</span>
                <span className="font-mono font-bold text-[#22261E]">
                  {inspectingCustomer.accountId}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]">
                  <span className="text-[#878E80] block">Họ tên</span>
                  <span className="font-semibold text-[#22261E]">
                    {inspectingCustomer.name || '—'}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]">
                  <span className="text-[#878E80] block">Ngày sinh</span>
                  <span className="font-semibold text-[#22261E]">
                    {inspectingCustomer.dateOfBirth || '—'}
                  </span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#878E80] block">Email & SĐT</span>
                <span className="font-medium text-[#22261E] block">
                  {inspectingCustomer.email}
                </span>
                <span className="text-[#5E6658]">
                  {inspectingCustomer.phone || 'Chưa lưu SĐT'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#878E80] block">Địa chỉ nhận hàng</span>
                <span className="text-[#22261E]">
                  {[
                    inspectingCustomer.houseNumber,
                    inspectingCustomer.ward,
                    inspectingCustomer.city,
                    inspectingCustomer.country,
                  ]
                    .filter(Boolean)
                    .join(', ') || 'Chưa cập nhật địa chỉ'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-[#E5ECE0] border border-[#C5D1BE] flex items-center justify-between">
                <span className="text-[#3B4B35] font-medium">
                  Tổng số đơn đã đặt
                </span>
                <span className="font-bold text-[#22261E] tabular-price">
                  {
                    orders.filter(
                      (o) => o.accountId === inspectingCustomer.accountId
                    ).length
                  }{' '}
                  đơn
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {confirmLockTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-md w-full p-7 space-y-4 shadow-2xl text-xs">
            <h3 className="font-editorial text-2xl text-[#22261E]">
              Khóa tài khoản Khách hàng {confirmLockTarget.accountId}?
            </h3>
            <p className="text-[#5E6658] leading-relaxed">
              Xác nhận khóa sẽ chuyển tài khoản sang «Bị khóa» và kết thúc ngay mọi phiên đăng nhập Storefront của khách (UC-08 AC-8). Nhân viên không thể mở khóa lại — chỉ Admin mở khóa được.
            </p>
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setConfirmLockTarget(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={() => {
                  const r = salerLockCustomerAccount(
                    confirmLockTarget.accountId
                  );
                  if (!r.ok) setErr(r.error ?? null);
                  setConfirmLockTarget(null);
                }}
                className="px-5 py-2 rounded-full bg-[#8E3B2E] text-white font-semibold cursor-pointer"
              >
                Xác nhận khóa Khách hàng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 3. SHARED INTERNAL PASSWORD CHANGE VIEW (UC-05 AC-5 for Portal: Saler & Admin)
 * ============================================================================ */
export const InternalPasswordView: React.FC = () => {
  const { changePassword, portalUser } = useSobieSystem();
  const activeAcc = portalUser;
  const [cur, setCur] = useState('');
  const [nw, setNw] = useState('');
  const [cfm, setCfm] = useState('');
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    const res = changePassword('portal', cur, nw, cfm);
    if (!res.ok) setErr(res.error ?? 'Đổi mật khẩu thất bại.');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <form
        onSubmit={handleSubmit}
        className="lg:col-span-6 rounded-3xl atelier-card p-7 sm:p-9 space-y-4"
      >
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <KeyRound className="w-4 h-4" />
          <span>UC-05 · Đổi Mật Khẩu Tài Khoản Nội Bộ</span>
        </div>
        <h2 className="font-editorial text-3xl text-[#22261E]">
          Đổi mật khẩu {activeAcc?.role === 'admin' ? 'Admin' : 'Nhân viên (Saler)'}
        </h2>

        {err && (
          <div className="px-3.5 py-2.5 rounded-xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
            {err}
          </div>
        )}

        <div className="space-y-3 text-xs">
          <input
            type="password"
            required
            value={cur}
            onChange={(e) => setCur(e.target.value)}
            placeholder="Mật khẩu hiện tại"
            className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
          />
          <input
            type="password"
            required
            value={nw}
            onChange={(e) => setNw(e.target.value)}
            placeholder="Mật khẩu mới (≥ 6 ký tự, khác mật khẩu cũ)"
            className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
          />
          <input
            type="password"
            required
            value={cfm}
            onChange={(e) => setCfm(e.target.value)}
            placeholder="Nhập lại mật khẩu mới"
            className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
          />
        </div>

        <button
          type="submit"
          className="px-7 py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
        >
          Lưu mật khẩu mới & Kết thúc phiên
        </button>
      </form>

      <div className="lg:col-span-6 rounded-3xl bg-[#F3EFE6] border border-[#E4DDD0] p-7 sm:p-9 space-y-4 text-xs text-[#5E6658]">
        <h3 className="font-editorial text-2xl text-[#22261E]">
          Quy tắc bảo mật phiên nội bộ (UC-05)
        </h3>
        <div className="space-y-2.5">
          <p className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#4A5D43] shrink-0 mt-0.5" />
            <span>
              Tài khoản đang đăng nhập:{' '}
              <strong className="font-mono text-[#22261E]">
                {activeAcc?.accountId}
              </strong>{' '}
              ({activeAcc?.email})
            </span>
          </p>
          <p className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#4A5D43] shrink-0 mt-0.5" />
            <span>
              Mật khẩu mới bắt buộc từ 6 ký tự trở lên, băm bằng `bcrypt` và khác mật khẩu hiện tại.
            </span>
          </p>
          <p className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#4A5D43] shrink-0 mt-0.5" />
            <span>
              Khi lưu thành công, hệ thống xóa mọi dòng `identity.session` trong cùng transaction và đưa bạn về màn hình đăng nhập riêng của vai trò.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};
