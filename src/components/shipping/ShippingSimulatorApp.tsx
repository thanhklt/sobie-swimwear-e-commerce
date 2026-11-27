import React, { useMemo, useRef, useState } from 'react';
import {
  Shield,
  Search,
  Copy,
  Check,
  Truck,
  CheckCircle2,
  XCircle,
  LogOut,
  History,
} from 'lucide-react';
import { gsap, useGSAP } from '../../lib/gsap';
import { ORDER_STATUS_META } from '../../data/seedData';
import { useSobieSystem } from '../../context/SobieSystemContext';
import { AppSurface } from '../../types/store';
import { ShippingLoginPage } from '../auth/RoleLoginPages';

export const ShippingSimulatorApp: React.FC<{
  onSwitchSurface: (s: AppSurface) => void;
}> = ({ onSwitchSurface }) => {
  const {
    orders,
    shippingSession,
    logoutShipping,
    carrierUpdateShipment,
  } = useSobieSystem();
  const rootRef = useRef<HTMLDivElement>(null);

  const [q, setQ] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [directCode, setDirectCode] = useState('');
  const [directAction, setDirectAction] = useState<
    'received' | 'delivered' | 'failed'
  >('received');
  const [feedback, setFeedback] = useState<{
    kind: 'ok' | 'err';
    msg: string;
  } | null>(null);

  // UC-36 v5 Main Flow Step 2 & AC-2 / AC-4:
  // Active dispatch list ONLY shows AWAITING_PICKUP ("Chờ lấy hàng") & SHIPPING ("Đang giao")!
  // Delivered / Failed orders disappear from active dispatch list immediately!
  const activeCarrierOrders = useMemo(() => {
    return orders.filter((o) => {
      if (o.status !== 'AWAITING_PICKUP' && o.status !== 'SHIPPING') {
        return false;
      }
      if (statusFilter && o.status !== statusFilter) return false;
      if (
        q.trim() &&
        !o.orderCode.toLowerCase().includes(q.trim().toLowerCase())
      ) {
        return false;
      }
      return true;
    });
  }, [orders, q, statusFilter]);

  // Non-PII Recent Completed Log (Order code + status only, zero PII/COD)
  const completedCarrierOrders = useMemo(
    () =>
      orders.filter((o) =>
        ['DELIVERED', 'DELIVERY_FAILED'].includes(o.status)
      ),
    [orders]
  );

  const awaitingCount = orders.filter(
    (o) => o.status === 'AWAITING_PICKUP'
  ).length;
  const shippingCount = orders.filter((o) => o.status === 'SHIPPING').length;

  useGSAP(
    () => {
      if (!shippingSession) return;
      gsap.from('.sim-kpi', {
        y: 14,
        autoAlpha: 0,
        duration: 0.45,
        stagger: 0.06,
        ease: 'power2.out',
      });
    },
    { dependencies: [Boolean(shippingSession)], scope: rootRef }
  );

  const { contextSafe } = useGSAP({ scope: rootRef });

  const handleAction = contextSafe(
    (orderCode: string, action: 'received' | 'delivered' | 'failed') => {
      const res = carrierUpdateShipment(orderCode, action);
      if (!res.ok) {
        setFeedback({ kind: 'err', msg: res.error ?? 'Thao tác thất bại.' });
        return;
      }
      const extraNote =
        action === 'delivered'
          ? ` — Đã tự xuất hóa đơn HD-${orderCode} (UC-26) và rời danh sách đang giao (UC-36 AC-4)`
          : action === 'failed'
          ? ' — Đã tự cộng hoàn tồn kho biến thể (UC-35) và rời danh sách đang giao'
          : ' — Chuyển sang Đang giao (Nhân viên không còn hủy được đơn này theo UC-22)';
      setFeedback({
        kind: 'ok',
        msg: `Đã cập nhật vận đơn #${orderCode} sang «${res.statusLabel}»${extraNote}.`,
      });
    }
  );

  if (!shippingSession) {
    return <ShippingLoginPage onSwitchSurface={onSwitchSurface} />;
  }

  return (
    <div
      ref={rootRef}
      className="min-h-[calc(100vh-44px)] bg-[#FAF7F2] py-8 px-5 sm:px-8 lg:px-12 xl:px-16"
    >
      <div className="w-full space-y-6">
        {/* FULL-BLEED SHIPPING DISPATCH HEADER */}
        <header className="p-6 sm:p-7 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-[#4A5D43]">
              <span className="w-2 h-2 rounded-full bg-[#4A5D43] ring-4 ring-[#4A5D43]/15" />
              <span>
                SOBIE LOGISTICS DISPATCH · `shipping:8001` · UC-36 (v5)
              </span>
            </div>
            <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
              Điều phối & Cập nhật trạng thái giao hàng
            </h1>
            <p className="text-xs sm:text-sm text-[#5E6658] mt-1 max-w-3xl">
              Đúng quy tắc `UC-36`: Danh sách tác nghiệp chỉ hiển thị <strong>Mã đơn</strong> và <strong>Trạng thái</strong> của đơn «Chờ lấy hàng» & «Đang giao» — tuyệt đối không công khai họ tên, SĐT, địa chỉ hoặc số tiền COD của khách hàng.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-xs font-semibold text-[#3B4B35]">
              <Shield className="w-3.5 h-3.5" />
              <span>
                {shippingSession.stationId} · {shippingSession.operatorName}
              </span>
            </div>
            <button
              type="button"
              onClick={logoutShipping}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full border border-[#E7C2BA] bg-white text-xs font-semibold text-[#8E3B2E] hover:bg-[#FBECE9] cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Về màn hình Login Shipping</span>
            </button>
          </div>
        </header>

        {/* 4 Full-Bleed KPI Cards */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="sim-kpi p-5 rounded-3xl atelier-card">
            <span className="text-xs text-[#5E6658]">Vận đơn đang tác nghiệp</span>
            <p className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 tabular-price">
              {awaitingCount + shippingCount}
            </p>
          </div>
          <div className="sim-kpi p-5 rounded-3xl atelier-card">
            <span className="text-xs text-[#8A5A14] font-semibold">
              1. Chờ lấy hàng (AWAITING_PICKUP)
            </span>
            <p className="font-editorial text-3xl font-semibold text-[#8A5A14] mt-1 tabular-price">
              {awaitingCount}
            </p>
          </div>
          <div className="sim-kpi p-5 rounded-3xl atelier-card">
            <span className="text-xs text-[#4A5D43] font-semibold">
              2. Đang giao (SHIPPING)
            </span>
            <p className="font-editorial text-3xl font-semibold text-[#4A5D43] mt-1 tabular-price">
              {shippingCount}
            </p>
          </div>
          <div className="sim-kpi p-5 rounded-3xl atelier-card">
            <span className="text-xs text-[#1F5E39] font-semibold">
              Đã hoàn tất giao nhận
            </span>
            <p className="font-editorial text-3xl font-semibold text-[#1F5E39] mt-1 tabular-price">
              {completedCarrierOrders.length}
            </p>
          </div>
        </section>

        {feedback && (
          <div
            className={`px-5 py-3.5 rounded-2xl border text-xs font-medium flex items-center justify-between ${
              feedback.kind === 'ok'
                ? 'bg-[#E3F2E8] border-[#B7DEC5] text-[#1F5E39]'
                : 'bg-[#FBECE9] border-[#E7C2BA] text-[#8E3B2E]'
            }`}
          >
            <span>{feedback.msg}</span>
            <button
              type="button"
              onClick={() => setFeedback(null)}
              className="opacity-70 hover:opacity-100 cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          {/* LEFT 8 COLS: ACTIVE UC-36 DISPATCH QUEUE */}
          <div className="xl:col-span-8 space-y-4">
            {/* Search & All Status Filter Pills Visible */}
            <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4 text-xs">
              <div className="relative flex-1 min-w-[220px]">
                <Search className="w-3.5 h-3.5 text-[#878E80] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Tìm mã đơn (VD: C8V6N3Q5, D5W9H2K7)..."
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E] font-mono"
                />
              </div>

              <div className="flex flex-wrap gap-1.5">
                {(
                  [
                    { id: '', label: 'Tất cả đơn đang giao nhận' },
                    { id: 'AWAITING_PICKUP', label: 'Chờ lấy hàng' },
                    { id: 'SHIPPING', label: 'Đang giao' },
                  ] as const
                ).map((st) => (
                  <button
                    key={st.id}
                    type="button"
                    onClick={() => setStatusFilter(st.id)}
                    className={`px-3.5 py-2 rounded-full font-semibold border cursor-pointer ${
                      statusFilter === st.id
                        ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                        : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                    }`}
                  >
                    {st.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-3xl atelier-card overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
                  <tr>
                    <th className="px-5 py-3.5 w-14 text-center">#</th>
                    <th className="px-5 py-3.5">Mã đơn (Ẩn PII & COD)</th>
                    <th className="px-5 py-3.5">Trạng thái hiện tại</th>
                    <th className="px-5 py-3.5 text-right">
                      Nút theo trạng thái (UC-36)
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E4DDD0]">
                  {activeCarrierOrders.length === 0 ? (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-5 py-14 text-center text-[#5E6658]"
                      >
                        Hiện không còn vận đơn nào ở «Chờ lấy hàng» hoặc «Đang giao». (Saler có thể bàn giao thêm đơn «Đã xác nhận» tại Cổng Saler → Bàn giao ship).
                      </td>
                    </tr>
                  ) : (
                    activeCarrierOrders.map((o, idx) => {
                      const meta = ORDER_STATUS_META[o.status];
                      return (
                        <tr key={o.orderCode} className="hover:bg-[#FAF7F2]">
                          <td className="px-5 py-4 text-center text-[#878E80] tabular-price">
                            {idx + 1}
                          </td>
                          <td className="px-5 py-4">
                            <div className="inline-flex items-center gap-2">
                              <span className="px-3 py-1 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] font-mono text-xs font-bold tracking-wider text-[#22261E]">
                                {o.orderCode}
                              </span>
                              <button
                                type="button"
                                onClick={() => {
                                  navigator.clipboard?.writeText(o.orderCode);
                                  setCopiedCode(o.orderCode);
                                  setTimeout(() => setCopiedCode(null), 1500);
                                }}
                                className="p-1.5 text-[#878E80] hover:text-[#22261E] cursor-pointer"
                                title="Sao chép mã đơn"
                              >
                                {copiedCode === o.orderCode ? (
                                  <Check className="w-3.5 h-3.5 text-[#1F5E39]" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>
                            </div>
                          </td>
                          <td className="px-5 py-4">
                            <span
                              className={`inline-block px-3 py-1 rounded-full border text-xs font-semibold ${meta.badgeClass}`}
                            >
                              {meta.label}
                            </span>
                          </td>
                          <td className="px-5 py-4 text-right">
                            {o.status === 'AWAITING_PICKUP' && (
                              <button
                                type="button"
                                onClick={() =>
                                  handleAction(o.orderCode, 'received')
                                }
                                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                              >
                                <Truck className="w-3.5 h-3.5" />
                                <span>Đã nhận hàng</span>
                              </button>
                            )}

                            {o.status === 'SHIPPING' && (
                              <div className="inline-flex flex-wrap justify-end gap-2">
                                <button
                                  type="button"
                                  onClick={() =>
                                    handleAction(o.orderCode, 'delivered')
                                  }
                                  className="inline-flex items-center gap-1 px-4 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                                >
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>Đã giao</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() =>
                                    handleAction(o.orderCode, 'failed')
                                  }
                                  className="inline-flex items-center gap-1 px-4 py-2 rounded-full border border-[#E7C2BA] bg-white text-[#8E3B2E] font-semibold hover:bg-[#FBECE9] transition-colors cursor-pointer"
                                >
                                  <XCircle className="w-3.5 h-3.5" />
                                  <span>Giao không thành công</span>
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* RIGHT 4 COLS: E1/E2 EXCEPTION TESTER & NON-PII COMPLETED LOG */}
          <div className="xl:col-span-4 space-y-5 text-xs">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAction(directCode, directAction);
              }}
              className="rounded-3xl atelier-card p-6 space-y-4"
            >
              <h3 className="font-editorial text-2xl text-[#22261E]">
                Kiểm thử ngoại lệ E1 / E2 (UC-36 AC-6/7/8)
              </h3>
              <p className="text-[#5E6658] leading-relaxed">
                Thử gửi cập nhật cho đơn đã giao (`7K3M9Q2X`), đơn chưa nhận hàng hoặc mã không tồn tại để kiểm chứng hệ thống từ chối an toàn.
              </p>
              <input
                type="text"
                required
                value={directCode}
                onChange={(e) => setDirectCode(e.target.value)}
                placeholder="Mã đơn (VD: 7K3M9Q2X)..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] font-mono uppercase"
              />
              <div className="flex flex-wrap gap-1.5">
                {(
                  [
                    { id: 'received', label: 'Đã nhận hàng' },
                    { id: 'delivered', label: 'Đã giao' },
                    { id: 'failed', label: 'Giao thất bại' },
                  ] as const
                ).map((act) => (
                  <button
                    key={act.id}
                    type="button"
                    onClick={() => setDirectAction(act.id)}
                    className={`px-3 py-1.5 rounded-full font-semibold border cursor-pointer ${
                      directAction === act.id
                        ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                        : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                    }`}
                  >
                    {act.label}
                  </button>
                ))}
              </div>
              <button
                type="submit"
                className="w-full py-2.5 rounded-full bg-[#22261E] text-white font-semibold hover:bg-[#4A5D43] cursor-pointer"
              >
                Gửi lệnh cập nhật trạng thái
              </button>
            </form>

            <div className="rounded-3xl atelier-card p-6 space-y-3">
              <div className="flex items-center gap-2 font-semibold text-[#22261E]">
                <History className="w-4 h-4 text-[#4A5D43]" />
                <span>Nhật ký vận đơn đã kết thúc (Chỉ mã đơn)</span>
              </div>
              <div className="divide-y divide-[#E4DDD0] max-h-56 overflow-y-auto">
                {completedCarrierOrders.map((co) => (
                  <div
                    key={co.orderCode}
                    className="py-2.5 flex items-center justify-between gap-2"
                  >
                    <span className="font-mono font-semibold text-[#22261E]">
                      #{co.orderCode}
                    </span>
                    <span
                      className={`px-2.5 py-0.5 rounded-full border text-[11px] font-semibold ${
                        ORDER_STATUS_META[co.status].badgeClass
                      }`}
                    >
                      {ORDER_STATUS_META[co.status].label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
