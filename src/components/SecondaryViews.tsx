import React, { useState } from 'react';
import {
  X,
  ChevronDown,
  FileText,
  Package,
  Heart,
  QrCode,
  CheckCircle2,
  KeyRound,
  UserCheck,
} from 'lucide-react';
import { formatVND } from '../lib/gsap';
import {
  COMMON_SIZE_CHART,
  ORDER_STATUS_META,
  STORE_CONFIG,
} from '../data/seedData';
import { useSobieSystem } from '../context/SobieSystemContext';
import { InfoTab, InvoiceSnapshot, OrderRecord } from '../types/store';
import { ProductCard } from './ProductCard';

/* ============================================================================
 * 1. CUSTOMER PROFILE & CHANGE PASSWORD PAGE (UC-04 v7, UC-05 v4)
 * ============================================================================ */
export const CustomerProfilePage: React.FC<{
  onLoggedOutAfterPasswordChange: () => void;
}> = ({ onLoggedOutAfterPasswordChange }) => {
  const { storefrontUser, updateCustomerProfile, changePassword } =
    useSobieSystem();

  const [name, setName] = useState(storefrontUser?.name ?? '');
  const [phone, setPhone] = useState(storefrontUser?.phone ?? '');
  const [dob, setDob] = useState(storefrontUser?.dateOfBirth ?? '');
  const [house, setHouse] = useState(storefrontUser?.houseNumber ?? '');
  const [ward, setWard] = useState(storefrontUser?.ward ?? '');
  const [city, setCity] = useState(storefrontUser?.city ?? '');
  const [country, setCountry] = useState(storefrontUser?.country ?? 'Việt Nam');
  const [profileErr, setProfileErr] = useState<string | null>(null);

  const [curPw, setCurPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [cfmPw, setCfmPw] = useState('');
  const [pwErr, setPwErr] = useState<string | null>(null);

  if (!storefrontUser) return null;

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setProfileErr(null);
    const res = updateCustomerProfile({
      name,
      phone,
      dateOfBirth: dob,
      houseNumber: house,
      ward,
      city,
      country,
    });
    if (!res.ok) setProfileErr(res.error ?? 'Lỗi lưu hồ sơ.');
  };

  const handleSavePassword = (e: React.FormEvent) => {
    e.preventDefault();
    setPwErr(null);
    const res = changePassword('storefront', curPw, newPw, cfmPw);
    if (!res.ok) {
      setPwErr(res.error ?? 'Đổi mật khẩu thất bại.');
      return;
    }
    onLoggedOutAfterPasswordChange();
  };

  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* UC-04: Update Customer Profile (Email Read-Only per AC-2!) */}
      <form
        onSubmit={handleSaveProfile}
        className="lg:col-span-7 rounded-3xl atelier-card p-7 sm:p-9 space-y-5"
      >
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <UserCheck className="w-4 h-4" />
          <span>UC-04 · Cập Nhật Hồ Sơ Khách Hàng</span>
        </div>
        <h2 className="font-editorial text-3xl text-[#22261E]">
          Thông tin cá nhân & Địa chỉ nhận hàng
        </h2>
        <p className="text-xs text-[#5E6658]">
          Mã tài khoản và Email hiển thị ở chế độ chỉ xem trên Storefront (UC-04 AC-2; chỉ Admin đổi được email qua UC-07).
        </p>

        {profileErr && (
          <div className="px-4 py-2.5 rounded-xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
            {profileErr}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <label className="space-y-1">
            <span className="text-[#5E6658]">Mã tài khoản (Chỉ xem)</span>
            <input
              type="text"
              disabled
              value={storefrontUser.accountId}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] font-mono text-[#5E6658]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#5E6658]">
              Email đã xác minh (Chỉ xem · UC-04 AC-2)
            </span>
            <input
              type="email"
              disabled
              value={storefrontUser.email}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] text-[#5E6658]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">Họ và tên *</span>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">
              Số điện thoại * (Không cần xác minh lại)
            </span>
            <input
              type="tel"
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">
              Ngày sinh (Điều kiện hồ sơ đầy đủ ở Checkout)
            </span>
            <input
              type="date"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">Quốc gia</span>
            <input
              type="text"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
        </div>

        <label className="block space-y-1 text-xs">
          <span className="text-[#3E4539] font-medium">Số nhà, tên đường</span>
          <input
            type="text"
            value={house}
            onChange={(e) => setHouse(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
          />
        </label>

        <div className="grid grid-cols-2 gap-4 text-xs">
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">Phường / Xã</span>
            <input
              type="text"
              value={ward}
              onChange={(e) => setWard(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#3E4539] font-medium">Tỉnh / Thành phố</span>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
        </div>

        <button
          type="submit"
          className="px-7 py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
        >
          Lưu hồ sơ khách hàng
        </button>
      </form>

      {/* UC-05: Change Password */}
      <div className="lg:col-span-5 rounded-3xl atelier-card p-7 sm:p-9 space-y-4 self-start">
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <KeyRound className="w-4 h-4" />
          <span>UC-05 · Đổi Mật Khẩu Sobie</span>
        </div>
        <h2 className="font-editorial text-2xl text-[#22261E]">
          Bảo mật tài khoản
        </h2>

        {!storefrontUser.hasPassword ? (
          <div className="p-4 rounded-2xl bg-[#F3EFE6] border border-[#E4DDD0] text-xs text-[#5E6658] leading-relaxed">
            Tài khoản này được tạo qua <strong>Google OpenID Connect</strong> và chưa có mật khẩu Sobie (UC-01 AC-14 / UC-05 Preconditions). Bạn có thể tiếp tục đăng nhập nhanh bằng Google.
          </div>
        ) : (
          <form onSubmit={handleSavePassword} className="space-y-4">
            <p className="text-xs text-[#5E6658] leading-relaxed">
              Theo UC-05 AC-6: Sau khi đổi mật khẩu thành công, mọi phiên đăng nhập (kể cả phiên hiện tại) sẽ kết thúc ngay để bạn đăng nhập lại bằng mật khẩu mới.
            </p>

            {pwErr && (
              <div className="px-4 py-2.5 rounded-xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
                {pwErr}
              </div>
            )}

            <div className="space-y-3 text-xs">
              <input
                type="password"
                required
                value={curPw}
                onChange={(e) => setCurPw(e.target.value)}
                placeholder="Mật khẩu hiện tại"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
              />
              <input
                type="password"
                required
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                placeholder="Mật khẩu mới (≥ 6 ký tự, khác mật khẩu cũ)"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
              />
              <input
                type="password"
                required
                value={cfmPw}
                onChange={(e) => setCfmPw(e.target.value)}
                placeholder="Nhập lại mật khẩu mới"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
            >
              Đổi mật khẩu & Kết thúc phiên cũ
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

/* ============================================================================
 * 2. FULL-BLEED WISHLIST PAGE (UC-38)
 * ============================================================================ */
export const WishlistPage: React.FC<{
  onSelectProduct: (id: string) => void;
  onExploreCatalog: () => void;
  onRequireLogin: () => void;
}> = ({ onSelectProduct, onExploreCatalog, onRequireLogin }) => {
  const { activeWishlist, products } = useSobieSystem();

  const items = activeWishlist
    .map((id) => products.find((p) => p.id === id))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8">
      <div className="pb-6 border-b border-[#E4DDD0]">
        <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
          Danh Sách Yêu Thích · UC-38
        </p>
        <h1 className="font-editorial text-3xl sm:text-5xl text-[#22261E] mt-1">
          Sản phẩm đã lưu ({items.length})
        </h1>
      </div>

      {items.length === 0 ? (
        <div className="py-20 text-center space-y-4">
          <Heart className="w-10 h-10 text-[#D4CBB8] mx-auto stroke-[1.5]" />
          <p className="font-editorial text-2xl text-[#22261E]">
            Bạn chưa lưu sản phẩm yêu thích nào
          </p>
          <button
            type="button"
            onClick={onExploreCatalog}
            className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
          >
            Khám phá cửa hàng
          </button>
        </div>
      ) : (
        <div className="pt-8 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {items.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onSelectProduct={onSelectProduct}
              onRequireLogin={onRequireLogin}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 3. INVOICE SNAPSHOT MODAL & FULL-BLEED CUSTOMER ORDERS PAGE (UC-21, UC-22, UC-27)
 * ============================================================================ */
export const InvoiceModal: React.FC<{
  invoice: InvoiceSnapshot | null;
  onClose: () => void;
}> = ({ invoice, onClose }) => {
  if (!invoice) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
      <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-xl w-full max-h-[88vh] overflow-y-auto p-7 space-y-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
              HÓA ĐƠN BÁN HÀNG (CHỈ ĐỌC · UC-26 / UC-27)
            </p>
            <h3 className="font-editorial text-2xl text-[#22261E] mt-0.5">
              Mã hóa đơn: {invoice.invoiceId}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs text-[#3E4539]">
          <div>
            <p className="text-[#878E80]">Mã đơn hàng</p>
            <p className="font-mono font-semibold text-[#22261E]">
              #{invoice.orderCode}
            </p>
          </div>
          <div>
            <p className="text-[#878E80]">Thời điểm xuất (Asia/Ho_Chi_Minh)</p>
            <p className="font-medium text-[#22261E]">
              {new Date(invoice.createdAt).toLocaleString('vi-VN', {
                timeZone: 'Asia/Ho_Chi_Minh',
              })}
            </p>
          </div>
          <div className="col-span-2">
            <p className="text-[#878E80]">Snapshot Khách hàng & Địa chỉ nhận</p>
            <p className="font-medium text-[#22261E]">
              {invoice.customer.name} · {invoice.customer.phone} ·{' '}
              {invoice.customer.email}
            </p>
            <p className="text-[#5E6658]">{invoice.customer.address}</p>
          </div>
        </div>

        <div className="rounded-2xl bg-[#FFFDF9] border border-[#E4DDD0] overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#F3EFE6] text-[#3E4539]">
              <tr>
                <th className="px-3.5 py-2.5">Sản phẩm</th>
                <th className="px-3.5 py-2.5">SL</th>
                <th className="px-3.5 py-2.5 text-right">Đơn giá sau giảm</th>
                <th className="px-3.5 py-2.5 text-right">Thành tiền</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E4DDD0]">
              {invoice.items.map((it) => (
                <tr key={it.sku}>
                  <td className="px-3.5 py-2.5">
                    <p className="font-medium text-[#22261E]">
                      {it.productName}
                    </p>
                    <p className="text-[11px] text-[#5E6658]">
                      {it.color} / {it.size} ({it.sku})
                    </p>
                  </td>
                  <td className="px-3.5 py-2.5 tabular-price">{it.quantity}</td>
                  <td className="px-3.5 py-2.5 text-right tabular-price">
                    {formatVND(it.discountedUnitPrice)}
                  </td>
                  <td className="px-3.5 py-2.5 text-right font-semibold tabular-price">
                    {formatVND(it.discountedUnitPrice * it.quantity)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-1.5 text-xs border-t border-[#E4DDD0] pt-3">
          <div className="flex justify-between">
            <span className="text-[#5E6658]">Tổng giá gốc</span>
            <span className="tabular-price">{formatVND(invoice.subtotal)}</span>
          </div>
          {invoice.productDiscount > 0 && (
            <div className="flex justify-between text-[#4A5D43]">
              <span>Giảm theo khuyến mãi sản phẩm</span>
              <span className="tabular-price">
                -{formatVND(invoice.productDiscount)}
              </span>
            </div>
          )}
          {invoice.orderDiscount > 0 && (
            <div className="flex justify-between text-[#4A5D43]">
              <span>Giảm theo hóa đơn / voucher</span>
              <span className="tabular-price">
                -{formatVND(invoice.orderDiscount)}
              </span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-[#5E6658]">Phí vận chuyển</span>
            <span className="tabular-price">
              {formatVND(invoice.shippingFee)}
            </span>
          </div>
          <div className="flex justify-between text-sm font-bold text-[#22261E] pt-2 border-t border-[#E4DDD0]">
            <span>Tổng thanh toán ({invoice.paymentMethod})</span>
            <span className="tabular-price">
              {formatVND(invoice.totalPayment)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const OrdersPage: React.FC = () => {
  const {
    storefrontUser,
    orders,
    invoices,
    customerCancelOrder,
    simulateSepayWebhook,
  } = useSobieSystem();

  const [statusTab, setStatusTab] = useState<string>('');
  const [confirmCancelOrder, setConfirmCancelOrder] =
    useState<OrderRecord | null>(null);
  const [qrModalOrder, setQrModalOrder] = useState<OrderRecord | null>(null);
  const [selectedInvoice, setSelectedInvoice] =
    useState<InvoiceSnapshot | null>(null);

  const myOrders = orders
    .filter((o) => o.accountId === storefrontUser?.accountId)
    .filter((o) => (statusTab ? o.status === statusTab : true))
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8 space-y-7">
      <div className="pb-6 border-b border-[#E4DDD0] space-y-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
            Đơn Hàng Của Tôi · UC-21 / UC-22 / UC-27
          </p>
          <h1 className="font-editorial text-3xl sm:text-5xl text-[#22261E] mt-1">
            Theo dõi hành trình đơn hàng
          </h1>
        </div>

        {/* All Status Filter Buttons Visible (No Horizontal Scroll!) */}
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setStatusTab('')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
              statusTab === ''
                ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                : 'bg-[#FFFDF9] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
            }`}
          >
            Tất cả trạng thái
          </button>
          {(Object.keys(ORDER_STATUS_META) as (keyof typeof ORDER_STATUS_META)[]).map(
            (st) => (
              <button
                key={st}
                type="button"
                onClick={() => setStatusTab(statusTab === st ? '' : st)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
                  statusTab === st
                    ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                    : 'bg-[#FFFDF9] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                }`}
              >
                {ORDER_STATUS_META[st].label}
              </button>
            )
          )}
        </div>
      </div>

      {myOrders.length === 0 ? (
        <div className="py-16 text-center text-sm text-[#5E6658] rounded-3xl atelier-card">
          Không có đơn hàng nào khớp trạng thái đang chọn.
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {myOrders.map((order) => {
            const meta = ORDER_STATUS_META[order.status];
            const linkedInvoice = invoices.find(
              (inv) => inv.orderCode === order.orderCode
            );
            const nowMs = new Date('2026-11-27T19:15:00Z').getTime();
            const isOverdue24h =
              nowMs - new Date(order.createdAt).getTime() >= 24 * 3600 * 1000;
            // UC-20 [GD]: Hide QR when paid, cancelled, or overdue!
            const canShowQr =
              order.paymentMethod === 'QR' &&
              order.paymentStatus === 'UNPAID' &&
              order.status === 'PENDING' &&
              !isOverdue24h;

            return (
              <div
                key={order.orderCode}
                className="p-6 rounded-3xl atelier-card flex flex-col justify-between space-y-4"
              >
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[#E4DDD0]">
                    <div className="flex items-center gap-2.5">
                      <Package className="w-4 h-4 text-[#4A5D43]" />
                      <span className="font-mono text-sm font-bold text-[#22261E]">
                        #{order.orderCode}
                      </span>
                      <span className="text-xs text-[#878E80]">
                        {new Date(order.createdAt).toLocaleString('vi-VN', {
                          timeZone: 'Asia/Ho_Chi_Minh',
                        })}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-[#FAF7F2] border border-[#E4DDD0] text-[11px] font-medium text-[#3E4539]">
                        {order.paymentMethod} ·{' '}
                        {order.paymentStatus === 'PAID'
                          ? 'Đã thanh toán'
                          : 'Chưa thanh toán'}
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full border text-[11px] font-semibold ${meta.badgeClass}`}
                      >
                        {meta.label}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    {order.items.map((it) => (
                      <div
                        key={it.sku}
                        className="flex items-center justify-between gap-4"
                      >
                        <div className="flex items-center gap-3">
                          <img
                            src={it.image}
                            alt={it.productName}
                            className="w-12 h-16 rounded-lg object-cover bg-[#F3EFE6]"
                          />
                          <div>
                            <p className="text-xs sm:text-sm font-semibold text-[#22261E]">
                              {it.productName}
                            </p>
                            <p className="text-xs text-[#5E6658]">
                              {it.color} · Size {it.size} × {it.quantity}
                            </p>
                          </div>
                        </div>
                        <span className="text-xs sm:text-sm font-semibold text-[#22261E] tabular-price">
                          {formatVND(it.finalUnitPrice * it.quantity)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* UC-22 AC-12: Customer NEVER sees Employee cancellation reason! */}
                <div className="pt-4 border-t border-[#E4DDD0] flex flex-wrap items-center justify-between gap-4">
                  <div className="text-xs text-[#5E6658]">
                    Người nhận: {order.customerName} ({order.customerPhone}) —{' '}
                    {order.customerHouseNumber}, {order.customerWard},{' '}
                    {order.customerCity}
                  </div>

                  <div className="flex flex-wrap items-center gap-2.5">
                    {canShowQr && (
                      <button
                        type="button"
                        onClick={() => setQrModalOrder(order)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-[#E5ECE0] text-[#3B4B35] text-xs font-semibold hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
                      >
                        <QrCode className="w-3.5 h-3.5" />
                        <span>Xem lại mã QR</span>
                      </button>
                    )}

                    {order.status === 'PENDING' && (
                      <button
                        type="button"
                        onClick={() => setConfirmCancelOrder(order)}
                        className="px-3.5 py-2 rounded-full border border-[#E7C2BA] text-xs font-semibold text-[#8E3B2E] hover:bg-[#FBECE9] cursor-pointer"
                      >
                        Hủy đơn
                      </button>
                    )}

                    {order.status === 'DELIVERED' && linkedInvoice && (
                      <button
                        type="button"
                        onClick={() => setSelectedInvoice(linkedInvoice)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>Xem hóa đơn ({linkedInvoice.invoiceId})</span>
                      </button>
                    )}

                    <span className="text-base font-bold text-[#22261E] tabular-price pl-1">
                      Tổng: {formatVND(order.totalPrice)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Customer Cancel Confirmation Popup (UC-22) */}
      {confirmCancelOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-md w-full p-7 space-y-4 shadow-2xl">
            <h3 className="font-editorial text-2xl text-[#22261E]">
              Xác nhận hủy đơn #{confirmCancelOrder.orderCode}?
            </h3>
            <p className="text-xs text-[#5E6658] leading-relaxed">
              Đơn hàng đang ở trạng thái Chưa xử lý. Sau khi hủy, hệ thống sẽ tự động cộng lại tồn kho và hoàn lượt khuyến mãi đã áp (cả voucher lẫn khuyến mãi hóa đơn — UC-22).
            </p>
            {confirmCancelOrder.paymentMethod === 'QR' &&
              confirmCancelOrder.paymentStatus === 'PAID' && (
                <div className="p-3.5 rounded-2xl bg-[#FBF4E4] border border-[#E8D2A6] text-xs text-[#8A5A14]">
                  Đơn đã được thanh toán. Vui lòng liên hệ cửa hàng ({STORE_CONFIG.hotline}) để được hỗ trợ hoàn tiền ngoài hệ thống.
                </div>
              )}
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setConfirmCancelOrder(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white text-xs font-medium cursor-pointer"
              >
                Đóng
              </button>
              <button
                type="button"
                onClick={() => {
                  customerCancelOrder(confirmCancelOrder.orderCode);
                  setConfirmCancelOrder(null);
                }}
                className="px-5 py-2 rounded-full bg-[#8E3B2E] text-white text-xs font-semibold cursor-pointer"
              >
                Xác nhận hủy đơn
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Re-open QR Modal */}
      {qrModalOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-sm w-full p-6 space-y-4 text-center shadow-2xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#4A5D43]">
                Mã VietQR #{qrModalOrder.orderCode}
              </span>
              <button
                type="button"
                onClick={() => setQrModalOrder(null)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#E4DDD0] text-xs space-y-1.5 text-left">
              <p>
                STK: <strong>{STORE_CONFIG.bankInfo.accountNumber}</strong>
              </p>
              <p>
                Số tiền:{' '}
                <strong className="text-[#4A5D43]">
                  {formatVND(qrModalOrder.totalPrice)}
                </strong>
              </p>
              <p>
                Nội dung:{' '}
                <strong className="font-mono">SOBIE{qrModalOrder.orderCode}</strong>
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                simulateSepayWebhook(qrModalOrder.orderCode);
                setQrModalOrder(null);
              }}
              className="w-full py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold inline-flex items-center justify-center gap-1.5 hover:bg-[#3B4B35] cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Giả lập SePay nhận thanh toán (UC-25)</span>
            </button>
          </div>
        </div>
      )}

      <InvoiceModal
        invoice={selectedInvoice}
        onClose={() => setSelectedInvoice(null)}
      />
    </div>
  );
};

/* ============================================================================
 * 4. FULL-BLEED INFO PAGES (UC-13) & STORE-WIDE SIZE GUIDE MODAL (UC-12)
 * ============================================================================ */
export const InfoPage: React.FC<{
  activeTab: InfoTab;
  onChangeTab: (tab: InfoTab) => void;
}> = ({ activeTab, onChangeTab }) => {
  const [openFaq, setOpenFaq] = useState<number>(0);

  const faqs = [
    {
      q: 'Làm sao để chọn đúng size đồ bơi tại Sobie?',
      a: 'Cửa hàng áp dụng một Bảng size chung cố định cho toàn bộ sản phẩm Nữ, Nam và Trẻ em. Bạn có thể mở ngay trên mọi trang chi tiết sản phẩm.',
    },
    {
      q: 'Khách chưa đăng nhập có dùng được giỏ hàng tạm thời không?',
      a: 'Có. Giỏ hàng tạm thời của khách vãng lai được lưu trên trình duyệt (localStorage), luôn lấy đơn giá mới nhất từ Database. Khi đăng nhập, giỏ tự động gộp vào tài khoản mà không vượt tồn kho.',
    },
    {
      q: 'Hệ thống tính khuyến mãi theo hóa đơn và voucher như thế nào?',
      a: 'Mỗi đơn hàng được hưởng khuyến mãi trực tiếp trên sản phẩm (nếu có) cộng với tối đa 1 ưu đãi đơn hàng có lợi nhất giữa Khuyến mãi theo hóa đơn và Mã Voucher (bằng nhau ưu tiên Voucher — UC-31).',
    },
    {
      q: 'Khi nào hóa đơn được xuất?',
      a: 'Hóa đơn chỉ đọc (mã HD-<mã đơn>) được hệ thống tự động xuất ngay khi đơn vị vận chuyển cập nhật trạng thái «Giao thành công» (UC-26).',
    },
  ];

  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-10 space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 pb-6 border-b border-[#E4DDD0]">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
            Trang Thông Tin Cố Định · UC-13
          </p>
          <h1 className="font-editorial text-4xl sm:text-5xl text-[#22261E] mt-1">
            Thông tin & Chính sách Sobie
          </h1>
        </div>

        <div className="flex flex-wrap gap-2 p-1.5 rounded-full bg-[#F3EFE6] border border-[#E4DDD0]">
          {(
            [
              { id: 'about', label: 'Giới thiệu thương hiệu' },
              { id: 'policy', label: 'Chính sách chung duy nhất' },
              { id: 'faq', label: 'Câu hỏi thường gặp (FAQ)' },
            ] as { id: InfoTab; label: string }[]
          ).map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => onChangeTab(t.id)}
              className={`px-5 py-2 rounded-full text-xs font-semibold cursor-pointer transition-colors ${
                activeTab === t.id
                  ? 'bg-[#4A5D43] text-white'
                  : 'text-[#5E6658] hover:text-[#22261E]'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        {activeTab === 'about' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center rounded-3xl atelier-card p-8 sm:p-10">
            <div className="lg:col-span-7 space-y-4 text-sm text-[#3E4539] leading-relaxed">
              <h2 className="font-editorial text-3xl text-[#22261E]">
                Về thương hiệu đồ bơi Sobie Atelier
              </h2>
              <p>
                <strong>SOBIE</strong> là cửa hàng thương mại điện tử chuyên doanh trang phục đồ bơi và resortwear tối giản trên tông nền Kem muối biển & Xanh ô-liu, vận hành tập trung một kho trung tâm duy nhất tại TP.HCM.
              </p>
              <p>
                Địa chỉ kho & văn phòng: {STORE_CONFIG.senderAddress} · Hotline:{' '}
                <strong>{STORE_CONFIG.hotline}</strong>.
              </p>
            </div>
            <div className="lg:col-span-5 rounded-2xl overflow-hidden border border-[#E4DDD0] aspect-[16/10]">
              <img
                src="/images/lookbook-summer.jpg"
                alt="Sobie Atelier"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        )}

        {activeTab === 'policy' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-3xl atelier-card p-7 space-y-2 text-sm text-[#3E4539]">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                1. Chính sách vận chuyển
              </h3>
              <p className="leading-relaxed">
                Phí vận chuyển cố định <strong>12.000₫</strong> áp dụng cho mọi đơn hàng trên toàn quốc (cấu hình từ biến môi trường cửa hàng).
              </p>
            </div>
            <div className="rounded-3xl atelier-card p-7 space-y-2 text-sm text-[#3E4539]">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                2. Thanh toán & Đối soát
              </h3>
              <p className="leading-relaxed">
                Hỗ trợ COD hoặc chuyển khoản VietQR tự động đối soát qua webhook SePay trong vòng 24 giờ kể từ lúc tạo đơn.
              </p>
            </div>
            <div className="rounded-3xl atelier-card p-7 space-y-2 text-sm text-[#3E4539]">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                3. Hủy đơn & Hoàn tiền
              </h3>
              <p className="leading-relaxed">
                Khách hàng chủ động hủy đơn trên website khi đơn đang «Chưa xử lý». Đơn QR đã thanh toán khi hủy sẽ được hỗ trợ hoàn tiền ngoài hệ thống qua Hotline {STORE_CONFIG.hotline}.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'faq' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {faqs.map((f, idx) => (
              <div
                key={f.q}
                className="rounded-2xl atelier-card overflow-hidden self-start"
              >
                <button
                  type="button"
                  onClick={() => setOpenFaq(openFaq === idx ? -1 : idx)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between gap-4 cursor-pointer"
                >
                  <span className="text-sm font-semibold text-[#22261E]">
                    {f.q}
                  </span>
                  <ChevronDown
                    className={`w-4 h-4 text-[#4A5D43] transition-transform ${
                      openFaq === idx ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {openFaq === idx && (
                  <div className="px-6 pb-5 pt-2 text-sm text-[#5E6658] border-t border-[#E4DDD0] leading-relaxed">
                    {f.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export const SizeGuideModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
}> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
      <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-3xl w-full max-h-[86vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
              UC-12 AC-2 · Một Bảng Size Chung Cố Định Toàn Cửa Hàng
            </p>
            <h2 className="font-editorial text-3xl text-[#22261E]">
              Bảng thông số kích cỡ Sobie
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
            Đồ bơi Nữ
          </h3>
          <div className="rounded-2xl border border-[#E4DDD0] bg-white overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#F3EFE6] text-[#3E4539]">
                <tr>
                  <th className="px-3.5 py-2.5">Size</th>
                  <th className="px-3.5 py-2.5">Chiều cao</th>
                  <th className="px-3.5 py-2.5">Cân nặng</th>
                  <th className="px-3.5 py-2.5">Vòng 1</th>
                  <th className="px-3.5 py-2.5">Vòng 2</th>
                  <th className="px-3.5 py-2.5">Vòng 3</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4DDD0]">
                {COMMON_SIZE_CHART.women.map((r) => (
                  <tr key={r.size}>
                    <td className="px-3.5 py-2.5 font-bold text-[#4A5D43]">
                      {r.size}
                    </td>
                    <td className="px-3.5 py-2.5">{r.height}</td>
                    <td className="px-3.5 py-2.5">{r.weight}</td>
                    <td className="px-3.5 py-2.5">{r.bust}</td>
                    <td className="px-3.5 py-2.5">{r.waist}</td>
                    <td className="px-3.5 py-2.5">{r.hip}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
              Quần bơi Nam
            </h3>
            <div className="rounded-2xl border border-[#E4DDD0] bg-white overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#F3EFE6] text-[#3E4539]">
                  <tr>
                    <th className="px-3 py-2">Size</th>
                    <th className="px-3 py-2">Chiều cao</th>
                    <th className="px-3 py-2">Cân nặng</th>
                    <th className="px-3 py-2">Vòng eo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E4DDD0]">
                  {COMMON_SIZE_CHART.men.map((r) => (
                    <tr key={r.size}>
                      <td className="px-3 py-2 font-bold text-[#4A5D43]">
                        {r.size}
                      </td>
                      <td className="px-3 py-2">{r.height}</td>
                      <td className="px-3 py-2">{r.weight}</td>
                      <td className="px-3 py-2">{r.waist}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
              Đồ bơi Trẻ em
            </h3>
            <div className="rounded-2xl border border-[#E4DDD0] bg-white overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#F3EFE6] text-[#3E4539]">
                  <tr>
                    <th className="px-3 py-2">Size</th>
                    <th className="px-3 py-2">Độ tuổi</th>
                    <th className="px-3 py-2">Chiều cao</th>
                    <th className="px-3 py-2">Cân nặng</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E4DDD0]">
                  {COMMON_SIZE_CHART.kids.map((r) => (
                    <tr key={r.size}>
                      <td className="px-3 py-2 font-bold text-[#4A5D43]">
                        {r.size}
                      </td>
                      <td className="px-3 py-2">{r.age}</td>
                      <td className="px-3 py-2">{r.height}</td>
                      <td className="px-3 py-2">{r.weight}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
