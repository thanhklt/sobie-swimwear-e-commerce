import React, { useMemo, useState } from 'react';
import {
  CheckCircle2,
  Truck,
  Percent,
  Warehouse,
  FileText,
  Search,
  AlertTriangle,
  Plus,
  X,
  QrCode,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { formatVND } from '../../lib/gsap';
import { ORDER_STATUS_META, STORE_CONFIG } from '../../data/seedData';
import { useSobieSystem } from '../../context/SobieSystemContext';
import {
  InvoiceSnapshot,
  OrderRecord,
  OrderStatus,
  PromotionType,
} from '../../types/store';
import { InvoiceModal } from '../SecondaryViews';

/* ============================================================================
 * 1. SALER ORDER MANAGEMENT (UC-23 Confirm, UC-22 Cancel, UC-24 Overdue Job, UC-25 SePay)
 * ============================================================================ */
export const EmployeeOrdersView: React.FC = () => {
  const {
    orders,
    invoices,
    employeeConfirmOrder,
    employeeCancelOrder,
    runAutoCancelOverdueQrJob,
    simulateSepayWebhook,
  } = useSobieSystem();

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchCode, setSearchCode] = useState('');
  const [detailOrder, setDetailOrder] = useState<OrderRecord | null>(null);
  const [cancelOrderTarget, setCancelOrderTarget] =
    useState<OrderRecord | null>(null);
  const [cancelReason, setCancelReason] = useState('');
  const [errMsg, setErrMsg] = useState<string | null>(null);
  const [viewingInvoice, setViewingInvoice] =
    useState<InvoiceSnapshot | null>(null);

  const filtered = orders
    .filter((o) => (statusFilter ? o.status === statusFilter : true))
    .filter((o) =>
      searchCode.trim()
        ? `${o.orderCode} ${o.customerName} ${o.customerPhone}`
            .toLowerCase()
            .includes(searchCode.trim().toLowerCase())
        : true
    )
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            Quản Lý Đơn Hàng Toàn Viền · UC-22 / UC-23 / UC-24 / UC-25
          </p>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Xác nhận, Hủy có lý do & Đối soát đơn hàng
          </h1>
          <p className="text-xs text-[#5E6658] mt-0.5">
            Không có thao tác «Từ chối» riêng (UC-23). Nhân viên hủy được đơn trước khi vận chuyển nhận hàng, bắt buộc nhập lý do ≤ 500 ký tự lưu nội bộ (khách không thấy).
          </p>
        </div>

        <button
          type="button"
          onClick={() => runAutoCancelOverdueQrJob()}
          className="px-5 py-2.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-xs font-semibold text-[#3B4B35] hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
        >
          Chạy tác vụ quét hủy đơn QR quá 24h (UC-24)
        </button>
      </div>

      {/* All Status Filter Buttons Visible Simultaneously — NO Horizontal Scroll! */}
      <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setStatusFilter('')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
              statusFilter === ''
                ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
            }`}
          >
            Tất cả ({orders.length})
          </button>
          {(Object.keys(ORDER_STATUS_META) as OrderStatus[]).map((st) => (
            <button
              key={st}
              type="button"
              onClick={() => setStatusFilter(statusFilter === st ? '' : st)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
                statusFilter === st
                  ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                  : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
              }`}
            >
              {ORDER_STATUS_META[st].label}
            </button>
          ))}
        </div>

        <input
          type="text"
          value={searchCode}
          onChange={(e) => setSearchCode(e.target.value)}
          placeholder="Tìm mã đơn, tên hoặc SĐT khách..."
          className="w-full sm:w-68 px-4 py-2 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
        />
      </div>

      {errMsg && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {errMsg}
        </div>
      )}

      <div className="rounded-3xl atelier-card overflow-hidden">
        <table className="w-full text-xs text-left">
          <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
            <tr>
              <th className="px-5 py-3.5">Mã đơn & Thời gian</th>
              <th className="px-5 py-3.5">Khách nhận hàng</th>
              <th className="px-5 py-3.5">Thanh toán</th>
              <th className="px-5 py-3.5">Tổng tiền</th>
              <th className="px-5 py-3.5">Trạng thái</th>
              <th className="px-5 py-3.5 text-right">Thao tác nghiệp vụ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4DDD0]">
            {filtered.map((o) => {
              const meta = ORDER_STATUS_META[o.status];
              const canEmpCancel = [
                'PENDING',
                'CONFIRMED',
                'AWAITING_PICKUP',
              ].includes(o.status);
              const inv = invoices.find((i) => i.orderCode === o.orderCode);

              return (
                <tr key={o.orderCode} className="hover:bg-[#FAF7F2]">
                  <td className="px-5 py-3.5">
                    <span className="font-mono font-bold text-[#22261E] block">
                      #{o.orderCode}
                    </span>
                    <span className="text-[11px] text-[#878E80]">
                      {new Date(o.createdAt).toLocaleString('vi-VN', {
                        timeZone: 'Asia/Ho_Chi_Minh',
                      })}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-[#22261E]">
                      {o.customerName}
                    </p>
                    <p className="text-[11px] text-[#5E6658]">
                      {o.customerPhone} · {o.customerCity}
                    </p>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-medium">{o.paymentMethod}</span> ·{' '}
                    <span
                      className={
                        o.paymentStatus === 'PAID'
                          ? 'text-[#1F5E39] font-semibold'
                          : 'text-[#8A5A14]'
                      }
                    >
                      {o.paymentStatus === 'PAID'
                        ? 'Đã thanh toán'
                        : 'Chưa thanh toán'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-semibold text-[#22261E] tabular-price">
                    {formatVND(o.totalPrice)}
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`px-2.5 py-1 rounded-full border text-[11px] font-semibold ${meta.badgeClass}`}
                    >
                      {meta.label}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <div className="inline-flex flex-wrap justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setDetailOrder(o)}
                        className="px-3 py-1.5 rounded-full border border-[#D4CBB8] bg-white text-[#22261E] hover:border-[#4A5D43] cursor-pointer"
                      >
                        Chi tiết & Lịch sử
                      </button>

                      {o.paymentMethod === 'QR' &&
                        o.paymentStatus === 'UNPAID' &&
                        o.status === 'PENDING' && (
                          <button
                            type="button"
                            onClick={() => {
                              setErrMsg(null);
                              const r = simulateSepayWebhook(o.orderCode);
                              if (!r.ok) setErrMsg(r.error ?? null);
                            }}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-[#E5ECE0] text-[#3B4B35] font-semibold hover:bg-[#4A5D43] hover:text-white cursor-pointer"
                          >
                            <QrCode className="w-3.5 h-3.5" />
                            <span>SePay khớp QR (UC-25)</span>
                          </button>
                        )}

                      {o.status === 'PENDING' && (
                        <button
                          type="button"
                          onClick={() => {
                            setErrMsg(null);
                            const r = employeeConfirmOrder(o.orderCode);
                            if (!r.ok) setErrMsg(r.error ?? null);
                          }}
                          className="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Xác nhận</span>
                        </button>
                      )}

                      {canEmpCancel && (
                        <button
                          type="button"
                          onClick={() => {
                            setErrMsg(null);
                            setCancelReason('');
                            setCancelOrderTarget(o);
                          }}
                          className="px-3 py-1.5 rounded-full border border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9] font-semibold cursor-pointer"
                        >
                          Hủy đơn
                        </button>
                      )}

                      {inv && (
                        <button
                          type="button"
                          onClick={() => setViewingInvoice(inv)}
                          className="px-3 py-1.5 rounded-full bg-[#22261E] text-white cursor-pointer"
                        >
                          Hóa đơn
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Employee Mandatory Reason Cancel Modal (UC-22) */}
      {cancelOrderTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const r = employeeCancelOrder(
                cancelOrderTarget.orderCode,
                cancelReason
              );
              if (!r.ok) {
                setErrMsg(r.error ?? null);
                return;
              }
              setCancelOrderTarget(null);
            }}
            className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-md w-full p-7 space-y-4 shadow-2xl text-xs"
          >
            <h3 className="font-editorial text-2xl text-[#22261E]">
              Hủy đơn hàng #{cancelOrderTarget.orderCode} (UC-22)
            </h3>
            {cancelOrderTarget.paymentStatus === 'PAID' && (
              <div className="p-3 rounded-xl bg-[#FBF4E4] border border-[#E8D2A6] text-[#8A5A14]">
                Đơn đã thanh toán. Việc hoàn tiền cho khách được xử lý ngoài hệ thống.
              </div>
            )}
            <label className="block space-y-1.5">
              <div className="flex justify-between">
                <span className="font-medium text-[#22261E]">
                  Lý do hủy * (Chỉ lưu nội bộ `order_status_history_note`)
                </span>
                <span className="text-[#878E80]">{cancelReason.length}/500</span>
              </div>
              <textarea
                rows={3}
                maxLength={500}
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="VD: Khách gọi điện đổi mẫu / Sai địa chỉ giao..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
            </label>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setCancelOrderTarget(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Đóng
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-full bg-[#8E3B2E] text-white font-semibold cursor-pointer"
              >
                Xác nhận hủy đơn
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Order Detail + Internal Status History Modal */}
      {detailOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-xl w-full max-h-[86vh] overflow-y-auto p-7 space-y-4 shadow-2xl text-xs">
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                Chi tiết & Lịch sử trạng thái #{detailOrder.orderCode}
              </h3>
              <button
                type="button"
                onClick={() => setDetailOrder(null)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2">
              <p className="font-semibold uppercase tracking-wider text-[#4A5D43]">
                Lịch sử chuyển trạng thái (`ordering.order_status_history`)
              </p>
              <div className="rounded-2xl bg-white border border-[#E4DDD0] divide-y divide-[#E4DDD0]">
                {detailOrder.history.map((h, i) => (
                  <div key={i} className="p-3.5 space-y-1">
                    <div className="flex justify-between font-medium text-[#22261E]">
                      <span>
                        {h.fromStatus
                          ? `${ORDER_STATUS_META[h.fromStatus].label} → `
                          : 'Khởi tạo → '}
                        {ORDER_STATUS_META[h.toStatus].label}
                      </span>
                      <span className="text-[11px] text-[#878E80]">
                        {h.source}
                      </span>
                    </div>
                    {h.note && (
                      <p className="text-[#8E3B2E] bg-[#FBECE9] px-2.5 py-1.5 rounded-lg">
                        Ghi chú / Lý do hủy nội bộ: {h.note}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <InvoiceModal
        invoice={viewingInvoice}
        onClose={() => setViewingInvoice(null)}
      />
    </div>
  );
};

/* ============================================================================
 * 2. FULL-BLEED SHIPPING HANDOFF DESK (UC-40 v4 — Single Order + E1/E2 Tester)
 * ============================================================================ */
export const EmployeeHandoffView: React.FC = () => {
  const { orders, employeeHandoffOrder } = useSobieSystem();
  const [q, setQ] = useState('');
  const [directCode, setDirectCode] = useState('');
  const [err, setErr] = useState<string | null>(null);

  const readyOrders = orders.filter(
    (o) =>
      o.status === 'CONFIRMED' &&
      o.orderCode.toLowerCase().includes(q.trim().toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <Truck className="w-3.5 h-3.5" />
          <span>Bàn Giao Vận Chuyển Toàn Viền · UC-40 (v4)</span>
        </div>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
          Bàn giao từng đơn «Đã xác nhận» sang «Chờ lấy hàng»
        </h1>
        <p className="text-xs text-[#5E6658] mt-0.5">
          Mỗi lần thao tác bàn giao đúng 1 đơn; thông báo lỗi E1 (sai trạng thái — báo đúng trạng thái thực tế) và E2 (không tìm thấy đơn) được phân biệt rõ ràng.
        </p>
      </div>

      {err && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] font-medium">
          {err}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-8 space-y-4">
          <div className="p-4 rounded-2xl atelier-card flex gap-3 items-center text-xs">
            <Search className="w-4 h-4 text-[#878E80]" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Lọc nhanh mã đơn chờ bàn giao (VD: B6TQ2R5D)..."
              className="flex-1 bg-transparent text-[#22261E] focus:outline-none font-mono"
            />
            {q && (
              <button
                type="button"
                onClick={() => setQ('')}
                className="px-3 py-1 rounded-lg border border-[#E4DDD0] cursor-pointer"
              >
                Xóa lọc
              </button>
            )}
          </div>

          <div className="space-y-3">
            {readyOrders.length === 0 ? (
              <div className="p-10 rounded-3xl atelier-card text-xs text-[#5E6658] text-center">
                Hiện không có đơn «Đã xác nhận» nào khớp bộ lọc chờ bàn giao.
              </div>
            ) : (
              readyOrders.map((o) => (
                <article
                  key={o.orderCode}
                  className="p-5 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4"
                >
                  <div>
                    <div className="font-mono text-base font-bold tracking-wider text-[#22261E]">
                      #{o.orderCode}
                    </div>
                    <div className="text-xs text-[#5E6658] mt-0.5">
                      Khách: {o.customerName} · Đặt lúc:{' '}
                      {new Date(o.createdAt).toLocaleString('vi-VN', {
                        timeZone: 'Asia/Ho_Chi_Minh',
                      })}{' '}
                      · Tổng: <strong>{formatVND(o.totalPrice)}</strong>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setErr(null);
                      const r = employeeHandoffOrder(o.orderCode);
                      if (!r.ok) setErr(r.error ?? null);
                    }}
                    className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                  >
                    Bàn giao vận chuyển
                  </button>
                </article>
              ))
            )}
          </div>
        </div>

        {/* Right 4-Col E1 / E2 Direct Order Code Tester */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            const r = employeeHandoffOrder(directCode);
            if (!r.ok) setErr(r.error ?? null);
            else setDirectCode('');
          }}
          className="xl:col-span-4 rounded-3xl atelier-card p-6 space-y-4 text-xs"
        >
          <h3 className="font-editorial text-2xl text-[#22261E]">
            Bàn giao theo mã / Kiểm thử E1 & E2
          </h3>
          <p className="text-[#5E6658] leading-relaxed">
            Nhập mã đơn bất kỳ (VD: `C8V6N3Q5` đang Chờ lấy hàng → kiểm tra E1; hoặc `ZZZZ9999` không tồn tại → kiểm tra E2).
          </p>
          <input
            type="text"
            required
            value={directCode}
            onChange={(e) => setDirectCode(e.target.value)}
            placeholder="Nhập mã đơn 8 ký tự..."
            className="w-full px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] font-mono uppercase text-[#22261E]"
          />
          <button
            type="submit"
            className="w-full py-3 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
          >
            Gửi yêu cầu bàn giao (UC-40)
          </button>
        </form>
      </div>
    </div>
  );
};

/* ============================================================================
 * 3. FULL-BLEED PROMOTIONS & QUOTE SIMULATOR (UC-28, UC-29, UC-30, UC-31)
 * ============================================================================ */
export const EmployeePromotionsView: React.FC = () => {
  const {
    promotions,
    products,
    getPromotionDisplayStatus,
    createPromotion,
    endPromotion,
    quoteOrderDiscount,
  } = useSobieSystem();

  const [pType, setPType] = useState<PromotionType>('PRODUCT');
  const [discountPct, setDiscountPct] = useState('15');
  const [productId, setProductId] = useState('SP-0003');
  const [thresholdPrice, setThresholdPrice] = useState('500000');
  const [quantity, setQuantity] = useState('50');
  const [code, setCode] = useState('');
  const [startDate, setStartDate] = useState('2026-11-27');
  const [endDate, setEndDate] = useState('2026-12-31');
  const [formErr, setFormErr] = useState<string | null>(null);
  const [confirmCreateOpen, setConfirmCreateOpen] = useState(false);

  const [simSubtotal, setSimSubtotal] = useState('510000');
  const [simVoucher, setSimVoucher] = useState('HE2026');

  const [filterKind, setFilterKind] = useState<string>('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const activeProducts = products.filter((p) => p.status === 'ACTIVE');

  const quotePreview = useMemo(() => {
    const sub = Math.max(0, parseInt(simSubtotal, 10) || 0);
    return quoteOrderDiscount(sub, simVoucher);
  }, [simSubtotal, simVoucher, quoteOrderDiscount]);

  const filteredPromotions = useMemo(() => {
    return promotions.filter((p) => {
      if (filterKind && p.type !== filterKind) return false;
      if ((dateFrom || dateTo) && filterKind !== 'PRODUCT') {
        if (p.type === 'PRODUCT') return false;
        if (dateTo && p.startDate && p.startDate > dateTo) return false;
        if (dateFrom && p.endDate && p.endDate < dateFrom) return false;
      }
      return true;
    });
  }, [promotions, filterKind, dateFrom, dateTo]);

  const executeCreate = () => {
    setFormErr(null);
    const res = createPromotion({
      type: pType,
      discountPercentage: Number(discountPct),
      productId: pType === 'PRODUCT' ? productId : undefined,
      thresholdPrice: pType !== 'PRODUCT' ? Number(thresholdPrice) : undefined,
      quantity: pType !== 'PRODUCT' ? Number(quantity) : undefined,
      code: pType === 'CODE' ? code : undefined,
      startDate: pType !== 'PRODUCT' ? startDate : undefined,
      endDate: pType !== 'PRODUCT' ? endDate : undefined,
    });
    setConfirmCreateOpen(false);
    if (!res.ok) setFormErr(res.error ?? null);
    else setCode('');
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <Percent className="w-3.5 h-3.5" />
          <span>Khuyến Mãi & Công Cụ Tính Thử Ưu Đãi Toàn Viền · UC-28 → UC-31</span>
        </div>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
          Quản lý 3 loại khuyến mãi & Mô phỏng UC-31
        </h1>
        <p className="text-xs text-[#5E6658] mt-0.5">
          Khuyến mãi hóa đơn & voucher áp dụng theo ngày lịch `Asia/Ho_Chi_Minh` (hết hiệu lực tại `00:00:00` ngày kế tiếp). Đã tạo không được sửa, chỉ được kết thúc sớm.
        </p>
      </div>

      {formErr && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {formErr}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left 7-Col Create Promotion Studio */}
        <section className="xl:col-span-7 p-6 sm:p-7 rounded-3xl atelier-card space-y-4 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="font-editorial text-2xl text-[#22261E]">
              Tạo chương trình khuyến mãi mới
            </h2>
            {/* All 3 Type Buttons Visible */}
            <div className="flex flex-wrap gap-1.5">
              {(
                [
                  { id: 'PRODUCT', label: 'Theo sản phẩm (UC-28)' },
                  { id: 'ORDER', label: 'Theo hóa đơn (UC-29)' },
                  { id: 'CODE', label: 'Voucher (UC-30)' },
                ] as const
              ).map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setPType(t.id)}
                  className={`px-3 py-1.5 rounded-full font-semibold border cursor-pointer ${
                    pType === t.id
                      ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                      : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              setConfirmCreateOpen(true);
            }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 items-end"
          >
            <label className="space-y-1">
              <span className="text-[#3E4539] font-medium">
                Phần trăm giảm (%) *
              </span>
              <input
                type="number"
                min={0.01}
                max={99.99}
                step={0.01}
                required
                value={discountPct}
                onChange={(e) => setDiscountPct(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              />
            </label>

            {pType === 'PRODUCT' && (
              <label className="sm:col-span-2 space-y-1">
                <span className="text-[#3E4539] font-medium">
                  Sản phẩm đang bán (Không giới hạn lượt · Có hiệu lực ngay)
                </span>
                <select
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                >
                  {activeProducts.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id} — {p.name}
                    </option>
                  ))}
                </select>
              </label>
            )}

            {pType !== 'PRODUCT' && (
              <>
                <label className="space-y-1">
                  <span className="text-[#3E4539] font-medium">
                    Đơn tối thiểu (₫)
                  </span>
                  <input
                    type="number"
                    min={0}
                    required
                    value={thresholdPrice}
                    onChange={(e) => setThresholdPrice(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-[#3E4539] font-medium">
                    Tổng số lượt áp dụng
                  </span>
                  <input
                    type="number"
                    min={1}
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                </label>

                {pType === 'CODE' && (
                  <label className="space-y-1">
                    <span className="text-[#3E4539] font-medium">Mã voucher</span>
                    <input
                      type="text"
                      required
                      maxLength={50}
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="VD: BIEN2026"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] uppercase"
                    />
                  </label>
                )}

                <label className="space-y-1">
                  <span className="text-[#3E4539] font-medium">
                    Ngày bắt đầu (ICT)
                  </span>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-[#3E4539] font-medium">
                    Ngày kết thúc (Hết 23:59:59)
                  </span>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                </label>
              </>
            )}

            <button
              type="submit"
              className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
            >
              Lưu chương trình
            </button>
          </form>
        </section>

        {/* Right 5-Col Quote Preview Simulator (UC-31) */}
        <section className="xl:col-span-5 p-6 sm:p-7 rounded-3xl atelier-card space-y-4 text-xs">
          <div>
            <h2 className="font-editorial text-2xl text-[#22261E]">
              Công cụ tính thử ưu đãi (UC-31 Quote)
            </h2>
            <p className="text-[#5E6658] mt-0.5">
              Chỉ tính thử, không tạo đơn và không thay đổi số lượt đã dùng.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <label className="space-y-1">
              <span className="font-medium">Tạm tính sau KM SP (₫)</span>
              <input
                type="number"
                min={0}
                value={simSubtotal}
                onChange={(e) => setSimSubtotal(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              />
            </label>
            <label className="space-y-1">
              <span className="font-medium">Mã voucher</span>
              <input
                type="text"
                value={simVoucher}
                onChange={(e) => setSimVoucher(e.target.value)}
                placeholder="VD: HE2026"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] uppercase"
              />
            </label>
          </div>

          <div className="p-4 rounded-2xl bg-[#E5ECE0] border border-[#C5D1BE] space-y-2.5">
            <div className="flex justify-between">
              <span className="text-[#3B4B35]">Ưu đãi được chọn:</span>
              <span className="font-semibold text-[#22261E]">
                {quotePreview.selectedPromotionLabel}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#3B4B35]">Tiền giảm (ROUND_HALF_UP):</span>
              <span className="font-bold text-[#4A5D43] tabular-price">
                -{formatVND(quotePreview.selectedDiscount)}
              </span>
            </div>
            <div className="flex justify-between pt-2 border-t border-[#C5D1BE]">
              <span className="font-semibold text-[#22261E]">
                Còn lại trước phí vận chuyển:
              </span>
              <span className="font-bold text-sm text-[#22261E] tabular-price">
                {formatVND(quotePreview.payableBeforeShipping)}
              </span>
            </div>
            {quotePreview.notice && (
              <p className="text-[11px] text-[#3B4B35] pt-1">
                {quotePreview.notice}
              </p>
            )}
          </div>
        </section>
      </div>

      {/* Promotions List & Filter */}
      <section className="space-y-4 text-xs">
        <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap gap-1.5">
            {(
              [
                { id: '', label: 'Tất cả loại' },
                { id: 'PRODUCT', label: 'Sản phẩm' },
                { id: 'ORDER', label: 'Hóa đơn' },
                { id: 'CODE', label: 'Voucher' },
              ] as const
            ).map((fk) => (
              <button
                key={fk.id}
                type="button"
                onClick={() => setFilterKind(fk.id)}
                className={`px-3.5 py-1.5 rounded-full font-semibold border cursor-pointer ${
                  filterKind === fk.id
                    ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                    : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                }`}
              >
                {fk.label}
              </button>
            ))}
          </div>

          {filterKind !== 'PRODUCT' && (
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="text-[#5E6658]">Lọc giao khoảng hiệu lực:</span>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              />
              <span>→</span>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              />
            </div>
          )}
        </div>

        <div className="rounded-3xl atelier-card overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
              <tr>
                <th className="px-5 py-3.5">Mã KM</th>
                <th className="px-5 py-3.5">Loại</th>
                <th className="px-5 py-3.5">Đối tượng / Code</th>
                <th className="px-5 py-3.5">Mức giảm</th>
                <th className="px-5 py-3.5">Đơn tối thiểu</th>
                <th className="px-5 py-3.5">Đã dùng / Tổng</th>
                <th className="px-5 py-3.5">Thời gian hiệu lực</th>
                <th className="px-5 py-3.5">Trạng thái</th>
                <th className="px-5 py-3.5 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E4DDD0]">
              {filteredPromotions.map((p) => {
                const dispStatus = getPromotionDisplayStatus(p);
                return (
                  <tr key={p.promotionId} className="hover:bg-[#FAF7F2]">
                    <td className="px-5 py-3.5 font-mono font-semibold text-[#22261E]">
                      {p.promotionId}
                    </td>
                    <td className="px-5 py-3.5">
                      {p.type === 'PRODUCT'
                        ? 'Sản phẩm'
                        : p.type === 'ORDER'
                        ? 'Hóa đơn'
                        : 'Voucher'}
                    </td>
                    <td className="px-5 py-3.5 font-mono font-semibold">
                      {p.productId ?? p.code ?? '—'}
                    </td>
                    <td className="px-5 py-3.5 font-bold text-[#4A5D43]">
                      -{p.discountPercentage}%
                    </td>
                    <td className="px-5 py-3.5 tabular-price">
                      {p.thresholdPrice !== undefined
                        ? formatVND(p.thresholdPrice)
                        : '—'}
                    </td>
                    <td className="px-5 py-3.5 tabular-price">
                      {p.usedAmount}
                      {p.quantity !== undefined
                        ? ` / ${p.quantity}`
                        : ' (Không giới hạn)'}
                    </td>
                    <td className="px-5 py-3.5 text-[#5E6658]">
                      {p.startDate
                        ? `${p.startDate} → ${p.endDate}`
                        : 'Ngay khi tạo'}
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                          dispStatus === 'Đang hiệu lực'
                            ? 'bg-[#E3F2E8] text-[#1F5E39]'
                            : dispStatus === 'Sắp diễn ra'
                            ? 'bg-[#FBF4E4] text-[#8A5A14]'
                            : 'bg-[#EFECE6] text-[#6E7368]'
                        }`}
                      >
                        {dispStatus}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      {dispStatus !== 'Đã kết thúc' && (
                        <button
                          type="button"
                          onClick={() => endPromotion(p.promotionId)}
                          className="px-3 py-1 rounded-full border border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9] font-semibold cursor-pointer"
                        >
                          {p.type === 'PRODUCT'
                            ? 'Kết thúc chương trình'
                            : 'Ngừng trước hạn'}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {confirmCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-md w-full p-7 space-y-4 shadow-2xl text-xs">
            <h3 className="font-editorial text-2xl text-[#22261E]">
              Xác nhận tạo chương trình khuyến mãi?
            </h3>
            <p className="text-[#5E6658] leading-relaxed">
              Mức giảm <strong>{discountPct}%</strong>. Theo đặc tả BR-004: Khuyến mãi đã tạo <strong>không được chỉnh sửa</strong>, chỉ có thể bấm ngừng/kết thúc.
            </p>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setConfirmCreateOpen(false)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={executeCreate}
                className="px-5 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Xác nhận tạo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 4. SALER INVENTORY: STOCK (UC-39), SUPPLIERS (UC-32), RECEIPTS (UC-33/34)
 * ============================================================================ */
export const EmployeeInventoryView: React.FC = () => {
  const {
    variants,
    products,
    categories,
    suppliers,
    receipts,
    saveSupplier,
    toggleSupplierStatus,
    deleteSupplier,
    saveDraftReceipt,
    confirmReceipt,
    cancelReceipt,
  } = useSobieSystem();

  const [tab, setTab] = useState<'stock' | 'suppliers' | 'receipts'>('stock');
  const [err, setErr] = useState<string | null>(null);

  // UC-39 Stock state (20/page, sorted productName ASC then SKU ASC, NO cost price!)
  const [stockSearch, setStockSearch] = useState('');
  const [stockCat, setStockCat] = useState('');
  const [stockPage, setStockPage] = useState(1);

  // UC-32 Supplier state
  const [supQuery, setSupQuery] = useState('');
  const [sName, setSName] = useState('');
  const [sPhone, setSPhone] = useState('');
  const [sEmail, setSEmail] = useState('');
  const [sAddr, setSAddr] = useState('');

  // UC-33 / UC-34 Receipt state
  const activeSuppliers = suppliers.filter((s) => s.status === 'ACTIVE');
  const [rSupplierId, setRSupplierId] = useState(
    activeSuppliers[0]?.supplierId ?? ''
  );
  const [rLines, setRLines] = useState<
    { sku: string; quantity: number; unitPrice: number }[]
  >([{ sku: variants[0]?.sku ?? '', quantity: 10, unitPrice: 150000 }]);
  const [rcStatusFilter, setRcStatusFilter] = useState('');
  const [rcSupFilter, setRcSupFilter] = useState('');

  const filteredStockRows = useMemo(() => {
    const kw = stockSearch.trim().toLowerCase();
    return variants
      .map((v) => {
        const p = products.find((pr) => pr.id === v.productId);
        return {
          ...v,
          productName: p?.name ?? v.productId,
          productStatus: p?.status ?? 'INACTIVE',
          category: p?.category ?? '',
        };
      })
      .filter((r) => {
        if (stockCat && r.category !== stockCat) return false;
        // UC-39: Case-insensitive, accent-sensitive substring match on productName
        if (kw && !r.productName.toLowerCase().includes(kw)) return false;
        return true;
      })
      .sort((a, b) => {
        const nameCmp = a.productName.localeCompare(b.productName, 'vi');
        return nameCmp !== 0 ? nameCmp : a.sku.localeCompare(b.sku);
      });
  }, [variants, products, stockCat, stockSearch]);

  const STOCK_PER_PAGE = 20;
  const totalStockPages = Math.max(
    1,
    Math.ceil(filteredStockRows.length / STOCK_PER_PAGE)
  );
  const safeStockPage = Math.min(stockPage, totalStockPages);
  const pagedStockRows = filteredStockRows.slice(
    (safeStockPage - 1) * STOCK_PER_PAGE,
    safeStockPage * STOCK_PER_PAGE
  );

  const filteredSuppliers = suppliers.filter((s) =>
    s.name.trim().toLowerCase().includes(supQuery.trim().toLowerCase())
  );

  const filteredReceipts = receipts.filter((rc) => {
    if (rcStatusFilter && rc.status !== rcStatusFilter) return false;
    if (rcSupFilter && rc.supplierId !== rcSupFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <Warehouse className="w-3.5 h-3.5" />
            <span>Kho Hàng, Nhà Cung Cấp & Phiếu Nhập Toàn Viền · UC-32 / 33 / 34 / 39</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Quản lý tồn kho & Nhập hàng bình quân gia quyền
          </h1>
        </div>

        {/* All 3 Sub-Tabs Visible */}
        <div className="flex flex-wrap gap-2 p-1.5 rounded-full bg-[#F3EFE6] border border-[#E4DDD0] text-xs">
          <button
            type="button"
            onClick={() => setTab('stock')}
            className={`px-4 py-2 rounded-full font-semibold cursor-pointer ${
              tab === 'stock' ? 'bg-[#4A5D43] text-white' : 'text-[#5E6658]'
            }`}
          >
            Xem tồn kho (UC-39)
          </button>
          <button
            type="button"
            onClick={() => setTab('suppliers')}
            className={`px-4 py-2 rounded-full font-semibold cursor-pointer ${
              tab === 'suppliers' ? 'bg-[#4A5D43] text-white' : 'text-[#5E6658]'
            }`}
          >
            Nhà cung cấp (UC-32)
          </button>
          <button
            type="button"
            onClick={() => setTab('receipts')}
            className={`px-4 py-2 rounded-full font-semibold cursor-pointer ${
              tab === 'receipts' ? 'bg-[#4A5D43] text-white' : 'text-[#5E6658]'
            }`}
          >
            Phiếu nhập kho (UC-33/34)
          </button>
        </div>
      </div>

      {err && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {err}
        </div>
      )}

      {/* TAB 1: UC-39 VIEW STOCK (20/page, sorted productName ASC -> SKU ASC, NO cost price!) */}
      {tab === 'stock' && (
        <div className="space-y-4 text-xs">
          <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
            <input
              type="text"
              value={stockSearch}
              onChange={(e) => {
                setStockSearch(e.target.value);
                setStockPage(1);
              }}
              placeholder="Tìm theo tên sản phẩm (không phân biệt hoa/thường, có phân biệt dấu)..."
              className="w-full sm:w-96 px-4 py-2.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]"
            />
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => {
                  setStockCat('');
                  setStockPage(1);
                }}
                className={`px-3.5 py-1.5 rounded-full font-semibold border cursor-pointer ${
                  stockCat === ''
                    ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                    : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                }`}
              >
                Tất cả danh mục
              </button>
              {categories.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => {
                    setStockCat(stockCat === c ? '' : c);
                    setStockPage(1);
                  }}
                  className={`px-3.5 py-1.5 rounded-full font-semibold border cursor-pointer ${
                    stockCat === c
                      ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                      : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-3xl atelier-card overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Tên sản phẩm (Tăng dần)</th>
                  <th className="px-5 py-3.5">Mã SKU</th>
                  <th className="px-5 py-3.5">Màu sắc</th>
                  <th className="px-5 py-3.5">Size</th>
                  <th className="px-5 py-3.5">Số lượng tồn (Chỉ xem · Ẩn giá vốn)</th>
                  <th className="px-5 py-3.5">Đánh dấu (Tồn ≤ 5)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4DDD0]">
                {pagedStockRows.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-5 py-10 text-center text-[#5E6658]">
                      Không tìm thấy biến thể phù hợp
                    </td>
                  </tr>
                ) : (
                  pagedStockRows.map((r) => {
                    const low = r.stockQuantity <= STORE_CONFIG.lowStockThreshold;
                    return (
                      <tr key={r.sku} className="hover:bg-[#FAF7F2]">
                        <td className="px-5 py-3.5 font-medium text-[#22261E]">
                          {r.productName}
                          {(r.productStatus === 'INACTIVE' ||
                            r.status === 'INACTIVE') && (
                            <span className="ml-2 px-2 py-0.5 rounded bg-[#EFECE6] text-[#6E7368] text-[10px]">
                              Ngừng bán
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-[#5E6658]">
                          {r.sku}
                        </td>
                        <td className="px-5 py-3.5">{r.color}</td>
                        <td className="px-5 py-3.5 font-semibold">{r.size}</td>
                        <td className="px-5 py-3.5 font-bold text-[#22261E] tabular-price">
                          {r.stockQuantity}
                        </td>
                        <td className="px-5 py-3.5">
                          {low ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FBF4E4] text-[#8A5A14] font-semibold">
                              <AlertTriangle className="w-3 h-3" />
                              {r.stockQuantity === 0
                                ? 'Hết tồn (0)'
                                : `Tồn kho thấp (≤ ${STORE_CONFIG.lowStockThreshold})`}
                            </span>
                          ) : (
                            <span className="text-[#4A5D43]">Đủ hàng</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {totalStockPages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <span className="text-[#5E6658]">
                Trang {safeStockPage} / {totalStockPages} (20 biến thể / trang · Giữ bộ lọc khi chuyển trang)
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={safeStockPage <= 1}
                  onClick={() => setStockPage((p) => Math.max(1, p - 1))}
                  className="p-2 rounded-full border border-[#E4DDD0] bg-white disabled:opacity-40 cursor-pointer"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  disabled={safeStockPage >= totalStockPages}
                  onClick={() =>
                    setStockPage((p) => Math.min(totalStockPages, p + 1))
                  }
                  className="p-2 rounded-full border border-[#E4DDD0] bg-white disabled:opacity-40 cursor-pointer"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: UC-32 SUPPLIERS */}
      {tab === 'suppliers' && (
        <div className="space-y-5 text-xs">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              const r = saveSupplier({
                name: sName,
                phone: sPhone,
                email: sEmail,
                address: sAddr,
              });
              if (!r.ok) setErr(r.error ?? null);
              else {
                setSName('');
                setSPhone('');
                setSEmail('');
                setSAddr('');
              }
            }}
            className="p-6 rounded-3xl atelier-card grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end"
          >
            <input
              type="text"
              required
              value={sName}
              onChange={(e) => setSName(e.target.value)}
              placeholder="Tên nhà cung cấp * (Unique)"
              className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
            />
            <input
              type="tel"
              required
              value={sPhone}
              onChange={(e) => setSPhone(e.target.value)}
              placeholder="Số điện thoại *"
              className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
            />
            <input
              type="email"
              value={sEmail}
              onChange={(e) => setSEmail(e.target.value)}
              placeholder="Email liên hệ"
              className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
            />
            <input
              type="text"
              value={sAddr}
              onChange={(e) => setSAddr(e.target.value)}
              placeholder="Địa chỉ"
              className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
            >
              Thêm Nhà cung cấp
            </button>
          </form>

          <div className="p-4 rounded-2xl atelier-card flex items-center gap-3">
            <Search className="w-4 h-4 text-[#878E80]" />
            <input
              type="text"
              value={supQuery}
              onChange={(e) => setSupQuery(e.target.value)}
              placeholder="Tìm kiếm tên nhà cung cấp..."
              className="flex-1 bg-transparent focus:outline-none"
            />
          </div>

          <div className="rounded-3xl atelier-card overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Mã NCC</th>
                  <th className="px-5 py-3.5">Tên nhà cung cấp</th>
                  <th className="px-5 py-3.5">Thông tin liên hệ</th>
                  <th className="px-5 py-3.5">Trạng thái hợp tác</th>
                  <th className="px-5 py-3.5 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4DDD0]">
                {filteredSuppliers.map((s) => (
                  <tr key={s.supplierId} className="hover:bg-[#FAF7F2]">
                    <td className="px-5 py-3.5 font-mono font-semibold text-[#22261E]">
                      {s.supplierId}
                    </td>
                    <td className="px-5 py-3.5 font-medium text-[#22261E]">
                      {s.name}
                    </td>
                    <td className="px-5 py-3.5 text-[#5E6658]">
                      {s.phone} · {s.email || '—'} · {s.address || '—'}
                    </td>
                    <td className="px-5 py-3.5">
                      <button
                        type="button"
                        onClick={() => toggleSupplierStatus(s.supplierId)}
                        className={`px-3 py-1 rounded-full font-semibold cursor-pointer ${
                          s.status === 'ACTIVE'
                            ? 'bg-[#E3F2E8] text-[#1F5E39]'
                            : 'bg-[#EFECE6] text-[#6E7368]'
                        }`}
                      >
                        {s.status === 'ACTIVE'
                          ? 'Đang hợp tác'
                          : 'Ngừng hợp tác'}
                      </button>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        type="button"
                        onClick={() => {
                          setErr(null);
                          const r = deleteSupplier(s.supplierId);
                          if (!r.ok) setErr(r.error ?? null);
                        }}
                        className="text-[#8E3B2E] font-semibold hover:underline cursor-pointer"
                      >
                        Xóa hẳn
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: UC-33 CREATE DRAFT RECEIPT & UC-34 CONFIRM RECEIPT */}
      {tab === 'receipts' && (
        <div className="space-y-6 text-xs">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              const r = saveDraftReceipt({
                supplierId: rSupplierId,
                lines: rLines,
              });
              if (!r.ok) setErr(r.error ?? null);
            }}
            className="p-6 sm:p-7 rounded-3xl atelier-card space-y-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-editorial text-2xl text-[#22261E]">
                  Lập phiếu nhập mới (Lưu trạng thái Nháp — UC-33)
                </h3>
                <p className="text-[#5E6658]">
                  Chỉ chọn nhà cung cấp Đang hợp tác; mỗi biến thể tối đa 1 dòng; đơn giá nhập số nguyên VND ≥ 0.
                </p>
              </div>
              <select
                value={rSupplierId}
                onChange={(e) => setRSupplierId(e.target.value)}
                className="px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              >
                {activeSuppliers.map((s) => (
                  <option key={s.supplierId} value={s.supplierId}>
                    {s.supplierId} — {s.name} (Đang hợp tác)
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2.5">
              {rLines.map((ln, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 items-center"
                >
                  <select
                    value={ln.sku}
                    onChange={(e) =>
                      setRLines((prev) =>
                        prev.map((x, i) =>
                          i === idx ? { ...x, sku: e.target.value } : x
                        )
                      )
                    }
                    className="sm:col-span-6 px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] font-mono"
                  >
                    {variants.map((v) => (
                      <option key={v.sku} value={v.sku}>
                        {v.sku} (Tồn hiện tại: {v.stockQuantity})
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min={1}
                    value={ln.quantity}
                    onChange={(e) =>
                      setRLines((prev) =>
                        prev.map((x, i) =>
                          i === idx
                            ? { ...x, quantity: Number(e.target.value) }
                            : x
                        )
                      )
                    }
                    placeholder="Số lượng"
                    className="sm:col-span-2 px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                  <input
                    type="number"
                    min={0}
                    value={ln.unitPrice}
                    onChange={(e) =>
                      setRLines((prev) =>
                        prev.map((x, i) =>
                          i === idx
                            ? { ...x, unitPrice: Number(e.target.value) }
                            : x
                        )
                      )
                    }
                    placeholder="Đơn giá nhập (≥ 0)"
                    className="sm:col-span-3 px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                  />
                  {rLines.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setRLines((prev) => prev.filter((_, i) => i !== idx))
                      }
                      className="sm:col-span-1 text-[#8E3B2E] font-semibold cursor-pointer"
                    >
                      Xóa
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="flex flex-wrap justify-between items-center gap-3 pt-2">
              <button
                type="button"
                onClick={() =>
                  setRLines((p) => [
                    ...p,
                    {
                      sku: variants[1]?.sku ?? variants[0]?.sku ?? '',
                      quantity: 10,
                      unitPrice: 150000,
                    },
                  ])
                }
                className="inline-flex items-center gap-1.5 text-[#4A5D43] font-semibold cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Thêm dòng biến thể</span>
              </button>

              <button
                type="submit"
                className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
              >
                Lưu phiếu Nháp (Chưa cộng tồn)
              </button>
            </div>
          </form>

          {/* Receipt Filters (UC-33 [GD]) */}
          <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap gap-1.5">
              {(
                [
                  { id: '', label: 'Tất cả trạng thái' },
                  { id: 'DRAFT', label: 'Nháp' },
                  { id: 'CONFIRMED', label: 'Đã xác nhận' },
                  { id: 'CANCELLED', label: 'Đã hủy' },
                ] as const
              ).map((st) => (
                <button
                  key={st.id}
                  type="button"
                  onClick={() => setRcStatusFilter(st.id)}
                  className={`px-3.5 py-1.5 rounded-full font-semibold border cursor-pointer ${
                    rcStatusFilter === st.id
                      ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                      : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>

            <select
              value={rcSupFilter}
              onChange={(e) => setRcSupFilter(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
            >
              <option value="">Tất cả nhà cung cấp</option>
              {suppliers.map((s) => (
                <option key={s.supplierId} value={s.supplierId}>
                  {s.supplierId} — {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-3xl atelier-card overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Mã phiếu</th>
                  <th className="px-5 py-3.5">Nhà cung cấp</th>
                  <th className="px-5 py-3.5">Ngày lập</th>
                  <th className="px-5 py-3.5">Tổng tiền</th>
                  <th className="px-5 py-3.5">Trạng thái</th>
                  <th className="px-5 py-3.5 text-right">Nghiệp vụ (UC-34)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E4DDD0]">
                {filteredReceipts.map((rc) => (
                  <tr key={rc.receiptId} className="hover:bg-[#FAF7F2]">
                    <td className="px-5 py-3.5 font-mono font-semibold text-[#22261E]">
                      {rc.receiptId}
                    </td>
                    <td className="px-5 py-3.5">
                      {suppliers.find((s) => s.supplierId === rc.supplierId)
                        ?.name ?? rc.supplierId}
                    </td>
                    <td className="px-5 py-3.5 text-[#5E6658]">
                      {new Date(rc.createdAt).toLocaleString('vi-VN', {
                        timeZone: 'Asia/Ho_Chi_Minh',
                      })}
                    </td>
                    <td className="px-5 py-3.5 font-semibold tabular-price">
                      {formatVND(rc.finalPrice)}
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`px-2.5 py-1 rounded-full font-semibold ${
                          rc.status === 'CONFIRMED'
                            ? 'bg-[#E3F2E8] text-[#1F5E39]'
                            : rc.status === 'DRAFT'
                            ? 'bg-[#FBF4E4] text-[#8A5A14]'
                            : 'bg-[#EFECE6] text-[#6E7368]'
                        }`}
                      >
                        {rc.status === 'CONFIRMED'
                          ? 'Đã xác nhận'
                          : rc.status === 'DRAFT'
                          ? 'Nháp'
                          : 'Đã hủy'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-2">
                      {rc.status === 'DRAFT' && (
                        <>
                          <button
                            type="button"
                            onClick={() => confirmReceipt(rc.receiptId)}
                            className="px-4 py-1.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
                          >
                            Xác nhận nhập kho
                          </button>
                          <button
                            type="button"
                            onClick={() => cancelReceipt(rc.receiptId)}
                            className="px-3 py-1.5 rounded-full border border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9] cursor-pointer"
                          >
                            Hủy nháp
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 5. FULL-BLEED SALER INVOICES REGISTRY (UC-27 — Newest First, Read-Only)
 * ============================================================================ */
export const EmployeeInvoicesView: React.FC = () => {
  const { invoices } = useSobieSystem();
  const [q, setQ] = useState('');
  const [selected, setSelected] = useState<InvoiceSnapshot | null>(null);

  const list = [...invoices]
    .filter((inv) =>
      `${inv.invoiceId} ${inv.orderCode}`
        .toLowerCase()
        .includes(q.trim().toLowerCase())
    )
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <FileText className="w-3.5 h-3.5" />
            <span>Danh Sách Hóa Đơn Toàn Viền · UC-27 (Chỉ đọc · Mới nhất trước)</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Tra cứu hóa đơn đã tự động xuất (UC-26)
          </h1>
        </div>

        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Tìm theo mã hóa đơn (HD-...) hoặc mã đơn..."
          className="w-full sm:w-80 px-4 py-2.5 rounded-2xl bg-[#FFFDF9] border border-[#E4DDD0] text-xs font-mono text-[#22261E]"
        />
      </div>

      <div className="rounded-3xl atelier-card overflow-hidden text-xs">
        <table className="w-full text-left">
          <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
            <tr>
              <th className="px-5 py-3.5">Mã hóa đơn</th>
              <th className="px-5 py-3.5">Mã đơn hàng</th>
              <th className="px-5 py-3.5">Thời điểm xuất</th>
              <th className="px-5 py-3.5">Khách hàng</th>
              <th className="px-5 py-3.5">Phương thức</th>
              <th className="px-5 py-3.5">Tổng thanh toán</th>
              <th className="px-5 py-3.5 text-right">Xem snapshot</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4DDD0]">
            {list.map((inv) => (
              <tr key={inv.invoiceId} className="hover:bg-[#FAF7F2]">
                <td className="px-5 py-3.5 font-mono font-semibold text-[#22261E]">
                  {inv.invoiceId}
                </td>
                <td className="px-5 py-3.5 font-mono text-[#5E6658]">
                  #{inv.orderCode}
                </td>
                <td className="px-5 py-3.5 text-[#5E6658]">
                  {new Date(inv.createdAt).toLocaleString('vi-VN', {
                    timeZone: 'Asia/Ho_Chi_Minh',
                  })}
                </td>
                <td className="px-5 py-3.5 text-[#22261E] font-medium">
                  {inv.customer.name}
                </td>
                <td className="px-5 py-3.5">{inv.paymentMethod}</td>
                <td className="px-5 py-3.5 font-semibold text-[#22261E] tabular-price">
                  {formatVND(inv.totalPayment)}
                </td>
                <td className="px-5 py-3.5 text-right">
                  <button
                    type="button"
                    onClick={() => setSelected(inv)}
                    className="px-4 py-1.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
                  >
                    Xem hóa đơn
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <InvoiceModal invoice={selected} onClose={() => setSelected(null)} />
    </div>
  );
};
