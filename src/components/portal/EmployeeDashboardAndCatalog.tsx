import React, { useMemo, useRef, useState } from 'react';
import {
  BarChart3,
  AlertTriangle,
  Plus,
  Trash2,
  Edit3,
  Layers,
  Tag,
  ArrowUp,
  ArrowDown,
  X,
  Lock,
} from 'lucide-react';
import { formatVND, gsap, useGSAP } from '../../lib/gsap';
import { ORDER_STATUS_META, STORE_CONFIG } from '../../data/seedData';
import { useSobieSystem } from '../../context/SobieSystemContext';
import { OrderStatus, ProductRecord } from '../../types/store';

/* ============================================================================
 * 1. SALER / EMPLOYEE DASHBOARD VIEW (UC-37 — Full-Bleed 6 Metrics)
 * ============================================================================ */
export const EmployeeDashboardView: React.FC = () => {
  const { orders, variants, products, receipts, suppliers } = useSobieSystem();
  const dashRef = useRef<HTMLDivElement>(null);

  const [inputStart, setInputStart] = useState('2026-11-01');
  const [inputEnd, setInputEnd] = useState('2026-11-30');
  const [appliedPeriod, setAppliedPeriod] = useState({
    start: '2026-11-01',
    end: '2026-11-30',
  });
  const [dateError, setDateError] = useState<string | null>(null);

  useGSAP(
    () => {
      gsap.from('.dash-card', {
        y: 16,
        autoAlpha: 0,
        duration: 0.45,
        stagger: 0.06,
        ease: 'power2.out',
      });
    },
    { dependencies: [appliedPeriod.start, appliedPeriod.end], scope: dashRef }
  );

  const handleApplyPeriod = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputStart || !inputEnd || inputStart >= inputEnd) {
      setDateError(
        'Ngày bắt đầu phải nhỏ hơn ngày kết thúc (UC-37 AC-7). Đang giữ kết quả kỳ hợp lệ trước đó.'
      );
      return;
    }
    setDateError(null);
    setAppliedPeriod({ start: inputStart, end: inputEnd });
  };

  const toVNDateStr = (iso: string) =>
    new Date(iso).toLocaleDateString('sv-SE', { timeZone: 'Asia/Ho_Chi_Minh' });

  const metrics = useMemo(() => {
    const { start, end } = appliedPeriod;

    const deliveredInPeriod = orders.filter((o) => {
      if (o.status !== 'DELIVERED' || !o.deliveredAt) return false;
      const d = toVNDateStr(o.deliveredAt);
      return d >= start && d <= end;
    });

    let revenue = 0;
    let totalCogs = 0;
    const productQtyMap: Record<string, { name: string; qty: number }> = {};

    for (const o of deliveredInPeriod) {
      const orderNetGoods = Math.max(
        0,
        o.subtotalAfterProductPromo - o.discountAmount
      );
      revenue += orderNetGoods;
      for (const line of o.items) {
        totalCogs += line.quantity * line.costPriceAtSale;
        if (!productQtyMap[line.productId]) {
          productQtyMap[line.productId] = { name: line.productName, qty: 0 };
        }
        productQtyMap[line.productId].qty += line.quantity;
      }
    }

    const grossProfit = revenue - totalCogs;

    const allStatuses: OrderStatus[] = [
      'PENDING',
      'CONFIRMED',
      'AWAITING_PICKUP',
      'SHIPPING',
      'DELIVERED',
      'DELIVERY_FAILED',
      'CANCELLED',
    ];
    const statusCounts: Record<OrderStatus, number> = {
      PENDING: 0,
      CONFIRMED: 0,
      AWAITING_PICKUP: 0,
      SHIPPING: 0,
      DELIVERED: 0,
      DELIVERY_FAILED: 0,
      CANCELLED: 0,
    };
    for (const o of orders) {
      const createdD = toVNDateStr(o.createdAt);
      if (createdD >= start && createdD <= end) {
        statusCounts[o.status] += 1;
      }
    }

    const top10Products = Object.entries(productQtyMap)
      .map(([id, info]) => ({ id, ...info }))
      .sort((a, b) => b.qty - a.qty)
      .slice(0, 10);

    const lowStockList = variants
      .filter((v) => v.stockQuantity <= STORE_CONFIG.lowStockThreshold)
      .map((v) => ({
        ...v,
        productName:
          products.find((p) => p.id === v.productId)?.name ?? v.productId,
      }))
      .sort((a, b) => a.stockQuantity - b.stockQuantity);

    const supplierSpendMap: Record<string, number> = {};
    for (const r of receipts) {
      if (r.status !== 'CONFIRMED') continue;
      const rDate = toVNDateStr(r.createdAt);
      if (rDate >= start && rDate <= end) {
        supplierSpendMap[r.supplierId] =
          (supplierSpendMap[r.supplierId] ?? 0) + r.finalPrice;
      }
    }
    const supplierSpend = Object.entries(supplierSpendMap).map(
      ([sid, amount]) => ({
        supplierId: sid,
        supplierName: suppliers.find((s) => s.supplierId === sid)?.name ?? sid,
        amount,
      })
    );

    return {
      revenue,
      grossProfit,
      allStatuses,
      statusCounts,
      top10Products,
      lowStockList,
      supplierSpend,
    };
  }, [appliedPeriod, orders, variants, products, receipts, suppliers]);

  return (
    <div ref={dashRef} className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Báo Cáo Kinh Doanh Toàn Viền · UC-37 (Chỉ đọc · Không cache)</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Dashboard vận hành cửa hàng Sobie
          </h1>
          <p className="text-xs text-[#5E6658] mt-0.5">
            Kỳ đang xem: <strong>{appliedPeriod.start}</strong> đến{' '}
            <strong>{appliedPeriod.end}</strong> (Múi giờ Asia/Ho_Chi_Minh · Doanh thu & LN gộp ghi nhận theo ngày Giao thành công).
          </p>
        </div>

        <form
          onSubmit={handleApplyPeriod}
          className="flex flex-wrap items-end gap-2.5 atelier-card p-3.5 rounded-2xl text-xs"
        >
          <label className="space-y-1">
            <span className="text-[#5E6658]">Từ ngày</span>
            <input
              type="date"
              value={inputStart}
              onChange={(e) => setInputStart(e.target.value)}
              className="block px-3 py-1.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[#5E6658]">Đến ngày</span>
            <input
              type="date"
              value={inputEnd}
              onChange={(e) => setInputEnd(e.target.value)}
              className="block px-3 py-1.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
            />
          </label>
          <button
            type="submit"
            className="px-5 py-2 rounded-xl bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
          >
            Xem kỳ báo cáo
          </button>
        </form>
      </div>

      {dateError && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {dateError}
        </div>
      )}

      {/* 1 & 2: Revenue & Gross Profit */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="dash-card p-7 rounded-3xl atelier-card">
          <p className="text-xs uppercase tracking-wider text-[#5E6658] font-semibold">
            1. Doanh thu thuần (Đơn Giao thành công · Không gồm phí ship)
          </p>
          <p className="font-editorial text-4xl sm:text-5xl font-semibold text-[#22261E] mt-2 tabular-price">
            {formatVND(metrics.revenue)}
          </p>
        </div>
        <div className="dash-card p-7 rounded-3xl atelier-card">
          <p className="text-xs uppercase tracking-wider text-[#4A5D43] font-semibold">
            2. Lợi nhuận gộp (Doanh thu − Giá vốn bình quân tại thời điểm bán)
          </p>
          <p className="font-editorial text-4xl sm:text-5xl font-semibold text-[#4A5D43] mt-2 tabular-price">
            {formatVND(metrics.grossProfit)}
          </p>
        </div>
      </div>

      {/* 3: Order Counts by Status (All 7 cards visible in grid) */}
      <div className="dash-card p-6 rounded-3xl atelier-card space-y-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
          3. Số đơn tạo trong kỳ theo 7 trạng thái vòng đời đơn
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {metrics.allStatuses.map((st) => (
            <div
              key={st}
              className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]"
            >
              <p className="text-[11px] text-[#5E6658] font-medium">
                {ORDER_STATUS_META[st].label}
              </p>
              <p className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 tabular-price">
                {metrics.statusCounts[st]}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 4, 5, 6 Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="dash-card p-6 rounded-3xl atelier-card space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
            4. Top 10 sản phẩm bán chạy (Theo ngày Giao thành công)
          </h3>
          {metrics.top10Products.length === 0 ? (
            <p className="text-xs text-[#878E80] py-4">
              Chưa có đơn giao thành công trong kỳ.
            </p>
          ) : (
            <div className="divide-y divide-[#E4DDD0] text-xs">
              {metrics.top10Products.map((p, idx) => (
                <div key={p.id} className="py-2.5 flex justify-between gap-2">
                  <span className="text-[#22261E]">
                    <strong>#{idx + 1}</strong> · {p.name}
                  </span>
                  <span className="font-semibold text-[#4A5D43] tabular-price shrink-0">
                    {p.qty} SP
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dash-card p-6 rounded-3xl atelier-card space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E] flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-[#A84A3B]" />
            <span>
              5. Biến thể tồn kho thấp hiện tại (≤ {STORE_CONFIG.lowStockThreshold})
            </span>
          </h3>
          <div className="max-h-64 overflow-y-auto divide-y divide-[#E4DDD0] text-xs">
            {metrics.lowStockList.map((v) => (
              <div key={v.sku} className="py-2.5 flex justify-between gap-2">
                <div>
                  <p className="font-medium text-[#22261E]">{v.productName}</p>
                  <p className="text-[11px] text-[#5E6658] font-mono">
                    {v.color} / {v.size} ({v.sku})
                  </p>
                </div>
                <span
                  className={`font-semibold tabular-price self-center ${
                    v.stockQuantity === 0 ? 'text-[#8E3B2E]' : 'text-[#8A5A14]'
                  }`}
                >
                  Tồn: {v.stockQuantity}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="dash-card p-6 rounded-3xl atelier-card space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
            6. Tiền nhập hàng theo NCC (Phiếu CONFIRMED theo ngày lập)
          </h3>
          {metrics.supplierSpend.length === 0 ? (
            <p className="text-xs text-[#878E80] py-4">
              Chưa có phiếu nhập Đã xác nhận trong kỳ.
            </p>
          ) : (
            <div className="divide-y divide-[#E4DDD0] text-xs">
              {metrics.supplierSpend.map((s) => (
                <div
                  key={s.supplierId}
                  className="py-2.5 flex justify-between gap-2"
                >
                  <span className="text-[#3E4539]">
                    {s.supplierName} ({s.supplierId})
                  </span>
                  <span className="font-semibold text-[#22261E] tabular-price">
                    {formatVND(s.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/* ============================================================================
 * 2. SALER PRODUCT, VARIANT & SIZE-PRICE STUDIO (UC-14, UC-15, UC-16 + Receipt Freeze!)
 * ============================================================================ */
export const EmployeeCatalogView: React.FC = () => {
  const {
    products,
    variants,
    categories,
    genders,
    collections,
    colors,
    sizes,
    hasConfirmedReceiptForProduct,
    saveProduct,
    toggleProductStatus,
    deleteProduct,
    generateVariantsMatrix,
    toggleVariantStatus,
    deleteVariant,
    updateSizePrices,
  } = useSobieSystem();

  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const [bannerErr, setBannerErr] = useState<string | null>(null);

  // Product Form Modal (UC-14)
  const [editingProd, setEditingProd] = useState<ProductRecord | 'new' | null>(
    null
  );
  const [pName, setPName] = useState('');
  const [pSub, setPSub] = useState('');
  const [pDesc, setPDesc] = useState('');
  const [pCat, setPCat] = useState(categories[0] ?? '');
  const [pGen, setPGen] = useState(genders[0] ?? '');
  const [pCols, setPCols] = useState<string[]>([]);
  const [pGallery, setPGallery] = useState<string[]>([
    '/images/prod-olive-onepiece.jpg',
  ]);
  const [newImgUrl, setNewImgUrl] = useState('');

  // Variant & Price Modal (UC-15, UC-16)
  const [managingProdId, setManagingProdId] = useState<string | null>(null);
  const [selColors, setSelColors] = useState<string[]>([]);
  const [selSizes, setSelSizes] = useState<string[]>([]);
  const [priceDraft, setPriceDraft] = useState<Record<string, string>>({});

  const filtered = products.filter((p) => {
    if (catFilter && p.category !== catFilter) return false;
    return `${p.name} ${p.id}`
      .toLowerCase()
      .includes(search.trim().toLowerCase());
  });

  const openProductForm = (target: ProductRecord | 'new') => {
    setBannerErr(null);
    setEditingProd(target);
    if (target === 'new') {
      setPName('');
      setPSub('');
      setPDesc('');
      setPCat(categories[0] ?? '');
      setPGen(genders[0] ?? '');
      setPCols([]);
      setPGallery(['/images/prod-olive-onepiece.jpg']);
    } else {
      setPName(target.name);
      setPSub(target.subtitle);
      setPDesc(target.description);
      setPCat(target.category);
      setPGen(target.gender);
      setPCols(target.collections);
      setPGallery(
        [...target.gallery]
          .sort((a, b) => a.orderNo - b.orderNo)
          .map((g) => g.url)
      );
    }
  };

  const openVariantManager = (p: ProductRecord) => {
    setBannerErr(null);
    setManagingProdId(p.id);
    setSelColors([]);
    setSelSizes([]);
    const pVars = variants.filter((v) => v.productId === p.id);
    const map: Record<string, string> = {};
    for (const v of pVars) {
      if (v.sellPrice !== null && !map[v.size]) {
        map[v.size] = String(v.sellPrice);
      }
    }
    setPriceDraft(map);
  };

  const handleSaveProduct = (e: React.FormEvent) => {
    e.preventDefault();
    const res = saveProduct({
      id: editingProd !== 'new' && editingProd ? editingProd.id : undefined,
      name: pName,
      subtitle: pSub,
      description: pDesc,
      category: pCat,
      gender: pGen,
      collections: pCols,
      gallery: pGallery.map((url, i) => ({ orderNo: i + 1, url })),
    });
    if (!res.ok) {
      setBannerErr(res.error ?? 'Lỗi lưu sản phẩm.');
      return;
    }
    setEditingProd(null);
  };

  const managedProd = products.find((p) => p.id === managingProdId);
  const managedLocked = managedProd
    ? hasConfirmedReceiptForProduct(managedProd.id)
    : false;
  const managedVariants = variants.filter((v) => v.productId === managingProdId);
  const distinctManagedSizes = Array.from(
    new Set(managedVariants.map((v) => v.size))
  );
  const editingLocked =
    editingProd && editingProd !== 'new'
      ? hasConfirmedReceiptForProduct(editingProd.id)
      : false;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
            <Layers className="w-3.5 h-3.5" />
            <span>
              Sản Phẩm, Biến Thể Màu × Size & Giá Size · UC-14 / UC-15 / UC-16
            </span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
            Quản lý danh mục sản phẩm cửa hàng
          </h1>
          <p className="text-xs text-[#5E6658] mt-0.5">
            Đồng bộ quy tắc `UC-14-Q11`: Sản phẩm đã phát sinh phiếu nhập `CONFIRMED` (`SP-0001`, `SP-0002` từ `PN-0001`) sẽ khóa cấu hình, giá bán & biến thể — chỉ cho phép sửa Mô tả.
          </p>
        </div>

        <button
          type="button"
          onClick={() => openProductForm('new')}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer shadow-xs"
        >
          <Plus className="w-4 h-4" />
          <span>Thêm sản phẩm mới (UC-14)</span>
        </button>
      </div>

      {bannerErr && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {bannerErr}
        </div>
      )}

      {/* Search + All Category Buttons Visible */}
      <div className="p-4 rounded-3xl atelier-card flex flex-wrap items-center justify-between gap-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Tìm theo tên hoặc mã sản phẩm..."
          className="w-full sm:w-80 px-4 py-2.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
        />
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => setCatFilter('')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
              catFilter === ''
                ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0]'
            }`}
          >
            Tất cả ({products.length})
          </button>
          {categories.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCatFilter(catFilter === c ? '' : c)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border cursor-pointer ${
                catFilter === c
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
        <table className="w-full text-xs text-left">
          <thead className="bg-[#F3EFE6] text-[#3E4539] uppercase text-[11px]">
            <tr>
              <th className="px-5 py-3.5">Sản phẩm</th>
              <th className="px-5 py-3.5">Phân loại & Bộ sưu tập</th>
              <th className="px-5 py-3.5">Biến thể</th>
              <th className="px-5 py-3.5">Khóa nhập kho</th>
              <th className="px-5 py-3.5">Trạng thái</th>
              <th className="px-5 py-3.5 text-right">Nghiệp vụ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4DDD0]">
            {filtered.map((p) => {
              const pVars = variants.filter((v) => v.productId === p.id);
              const locked = hasConfirmedReceiptForProduct(p.id);
              return (
                <tr key={p.id} className="hover:bg-[#FAF7F2]">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <img
                        src={p.gallery[0]?.url}
                        alt={p.name}
                        className="w-12 h-15 rounded-xl object-cover bg-[#F3EFE6]"
                      />
                      <div>
                        <p className="font-mono text-[11px] text-[#878E80]">
                          {p.id}
                        </p>
                        <p className="font-semibold text-[#22261E]">{p.name}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-[#5E6658]">
                    <p className="text-[#22261E] font-medium">
                      {p.category} · {p.gender}
                    </p>
                    <p className="text-[11px] text-[#878E80]">
                      BST: {p.collections.join(', ') || '—'}
                    </p>
                  </td>
                  <td className="px-5 py-3.5 tabular-price font-medium">
                    {pVars.length} biến thể
                  </td>
                  <td className="px-5 py-3.5">
                    {locked ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FBF4E4] border border-[#E8D2A6] text-[11px] font-semibold text-[#8A5A14]">
                        <Lock className="w-3 h-3" />
                        <span>Đã khóa (PN CONFIRMED)</span>
                      </span>
                    ) : (
                      <span className="text-[11px] text-[#4A5D43] font-medium">
                        Cho phép cấu hình
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <button
                      type="button"
                      onClick={() => {
                        setBannerErr(null);
                        const r = toggleProductStatus(p.id);
                        if (!r.ok) setBannerErr(r.error ?? null);
                      }}
                      className={`px-3 py-1 rounded-full text-[11px] font-semibold cursor-pointer ${
                        p.status === 'ACTIVE'
                          ? 'bg-[#E3F2E8] text-[#1F5E39]'
                          : 'bg-[#EFECE6] text-[#6E7368]'
                      }`}
                    >
                      {p.status === 'ACTIVE' ? 'Đang bán' : 'Ngừng bán'}
                    </button>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <div className="inline-flex flex-wrap justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => openVariantManager(p)}
                        className="px-3.5 py-1.5 rounded-full bg-[#E5ECE0] text-[#3B4B35] font-semibold hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
                      >
                        Biến thể & Giá size
                      </button>
                      <button
                        type="button"
                        onClick={() => openProductForm(p)}
                        className="p-1.5 rounded-full border border-[#D4CBB8] bg-white hover:border-[#4A5D43] text-[#22261E] cursor-pointer"
                        title="Sửa sản phẩm"
                      >
                        <Edit3 className="w-3.5 h-3.5 inline" />
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setBannerErr(null);
                          const r = deleteProduct(p.id);
                          if (!r.ok) setBannerErr(r.error ?? null);
                        }}
                        className="p-1.5 rounded-full border border-[#E7C2BA] text-[#8E3B2E] hover:bg-[#FBECE9] cursor-pointer"
                        title="Xóa sản phẩm"
                      >
                        <Trash2 className="w-3.5 h-3.5 inline" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* UC-14 Product Create / Edit Modal */}
      {editingProd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <form
            onSubmit={handleSaveProduct}
            className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-xl w-full max-h-[88vh] overflow-y-auto p-7 space-y-4 shadow-2xl text-xs"
          >
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <h3 className="font-editorial text-2xl text-[#22261E]">
                {editingProd === 'new'
                  ? 'Thêm sản phẩm mới (Mặc định Ngừng bán — UC-14)'
                  : `Sửa sản phẩm ${editingProd.id}`}
              </h3>
              <button
                type="button"
                onClick={() => setEditingProd(null)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {editingLocked && (
              <div className="p-3.5 rounded-2xl bg-[#FBF4E4] border border-[#E8D2A6] text-[#8A5A14] leading-relaxed">
                <strong>UC-14-Q11 (Đã có phiếu nhập CONFIRMED):</strong> Chỉ được phép cập nhật trường <strong>Mô tả</strong>; Tên, Danh mục, Giới tính, Bộ sưu tập và Ảnh gallery đã bị khóa cố định.
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <label className="col-span-2 space-y-1">
                <span className="font-medium">Tên sản phẩm * (Unique sau trim)</span>
                <input
                  type="text"
                  required
                  disabled={editingLocked}
                  value={pName}
                  onChange={(e) => setPName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white disabled:bg-[#F3EFE6] border border-[#E4DDD0]"
                />
              </label>

              <label className="space-y-1">
                <span className="font-medium">Danh mục *</span>
                <select
                  disabled={editingLocked}
                  value={pCat}
                  onChange={(e) => setPCat(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-white disabled:bg-[#F3EFE6] border border-[#E4DDD0]"
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>

              <label className="space-y-1">
                <span className="font-medium">Giới tính *</span>
                <select
                  disabled={editingLocked}
                  value={pGen}
                  onChange={(e) => setPGen(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-white disabled:bg-[#F3EFE6] border border-[#E4DDD0]"
                >
                  {genders.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="space-y-1">
              <span className="font-medium">Bộ sưu tập (Chọn nhiều)</span>
              <div className="flex flex-wrap gap-2 pt-1">
                {collections.map((col) => {
                  const checked = pCols.includes(col);
                  return (
                    <button
                      key={col}
                      type="button"
                      disabled={editingLocked}
                      onClick={() =>
                        setPCols((prev) =>
                          checked
                            ? prev.filter((x) => x !== col)
                            : [...prev, col]
                        )
                      }
                      className={`px-3 py-1.5 rounded-full border cursor-pointer disabled:opacity-50 ${
                        checked
                          ? 'bg-[#4A5D43] text-white border-[#4A5D43]'
                          : 'bg-white border-[#E4DDD0]'
                      }`}
                    >
                      {col}
                    </button>
                  );
                })}
              </div>
            </div>

            <label className="block space-y-1">
              <span className="font-medium">
                Mô tả sản phẩm (Luôn cho phép sửa kể cả sau CONFIRMED)
              </span>
              <textarea
                rows={3}
                value={pDesc}
                onChange={(e) => setPDesc(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#E4DDD0]"
              />
            </label>

            {!editingLocked && (
              <div className="space-y-2">
                <span className="font-medium">
                  Bộ ảnh theo thứ tự hiển thị (UC-14 AC-12)
                </span>
                <div className="space-y-1.5">
                  {pGallery.map((url, idx) => (
                    <div
                      key={`${url}-${idx}`}
                      className="flex items-center justify-between gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#E4DDD0]"
                    >
                      <span className="truncate font-mono text-[11px]">
                        #{idx + 1} · {url}
                      </span>
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          type="button"
                          disabled={idx === 0}
                          onClick={() => {
                            const arr = [...pGallery];
                            [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
                            setPGallery(arr);
                          }}
                          className="p-1 hover:bg-[#F3EFE6] rounded disabled:opacity-30 cursor-pointer"
                        >
                          <ArrowUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          disabled={idx === pGallery.length - 1}
                          onClick={() => {
                            const arr = [...pGallery];
                            [arr[idx + 1], arr[idx]] = [arr[idx], arr[idx + 1]];
                            setPGallery(arr);
                          }}
                          className="p-1 hover:bg-[#F3EFE6] rounded disabled:opacity-30 cursor-pointer"
                        >
                          <ArrowDown className="w-3.5 h-3.5" />
                        </button>
                        {pGallery.length > 1 && (
                          <button
                            type="button"
                            onClick={() =>
                              setPGallery(pGallery.filter((_, i) => i !== idx))
                            }
                            className="p-1 text-[#8E3B2E] cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <select
                    value={newImgUrl}
                    onChange={(e) => setNewImgUrl(e.target.value)}
                    className="flex-1 px-3 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                  >
                    <option value="">Chọn ảnh studio có sẵn để thêm...</option>
                    <option value="/images/prod-olive-onepiece.jpg">
                      /images/prod-olive-onepiece.jpg
                    </option>
                    <option value="/images/prod-sand-bikini.jpg">
                      /images/prod-sand-bikini.jpg
                    </option>
                    <option value="/images/prod-terracotta-onepiece.jpg">
                      /images/prod-terracotta-onepiece.jpg
                    </option>
                    <option value="/images/prod-ocean-bikini.jpg">
                      /images/prod-ocean-bikini.jpg
                    </option>
                    <option value="/images/sp-0002-1.jpg">
                      /images/sp-0002-1.jpg
                    </option>
                    <option value="/images/sp-0002-2.jpg">
                      /images/sp-0002-2.jpg
                    </option>
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      if (newImgUrl) {
                        setPGallery((p) => [...p, newImgUrl]);
                        setNewImgUrl('');
                      }
                    }}
                    className="px-4 py-2 rounded-xl bg-[#22261E] text-white font-semibold cursor-pointer"
                  >
                    Thêm ảnh
                  </button>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingProd(null)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="submit"
                className="px-6 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Lưu sản phẩm
              </button>
            </div>
          </form>
        </div>
      )}

      {/* UC-15 Variants Matrix & UC-16 Size-Price Modal */}
      {managedProd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <div className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-4xl w-full max-h-[88vh] overflow-y-auto p-7 space-y-6 shadow-2xl text-xs">
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <div>
                <p className="text-[11px] uppercase tracking-wider text-[#4A5D43] font-semibold">
                  UC-15 Biến thể Màu × Size & UC-16 Giá bán theo Size
                </p>
                <h3 className="font-editorial text-2xl text-[#22261E]">
                  {managedProd.id} — {managedProd.name}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setManagingProdId(null)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {managedLocked && (
              <div className="p-4 rounded-2xl bg-[#FBF4E4] border border-[#E8D2A6] text-[#8A5A14] flex items-center gap-2.5">
                <Lock className="w-4 h-4 shrink-0" />
                <span>
                  Sản phẩm đã có phiếu nhập Đã xác nhận (`CONFIRMED`) — Đã khóa thêm/xóa/đổi trạng thái biến thể và khóa đổi giá bán theo size (UC-14-Q11 / UC-15 / UC-16).
                </span>
              </div>
            )}

            {!managedLocked && (
              <>
                <div className="p-5 rounded-2xl bg-white border border-[#E4DDD0] space-y-3">
                  <p className="font-semibold text-[#22261E]">
                    1. Tạo tổ hợp biến thể Màu × Size mới (Tồn kho & giá vốn ban đầu = 0)
                  </p>
                  <div className="space-y-1.5">
                    <span className="text-[#5E6658]">Chọn các màu:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {colors.map((c) => {
                        const on = selColors.includes(c.name);
                        return (
                          <button
                            key={c.name}
                            type="button"
                            onClick={() =>
                              setSelColors((p) =>
                                on
                                  ? p.filter((x) => x !== c.name)
                                  : [...p, c.name]
                              )
                            }
                            className={`px-3 py-1.5 rounded-full border cursor-pointer ${
                              on
                                ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                                : 'bg-[#FAF7F2] border-[#E4DDD0]'
                            }`}
                          >
                            {c.name}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-[#5E6658]">Chọn các size:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {sizes.map((s) => {
                        const on = selSizes.includes(s);
                        return (
                          <button
                            key={s}
                            type="button"
                            onClick={() =>
                              setSelSizes((p) =>
                                on ? p.filter((x) => x !== s) : [...p, s]
                              )
                            }
                            className={`px-3 py-1.5 rounded-full border cursor-pointer ${
                              on
                                ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                                : 'bg-[#FAF7F2] border-[#E4DDD0]'
                            }`}
                          >
                            Size {s}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      const r = generateVariantsMatrix(
                        managedProd.id,
                        selColors,
                        selSizes
                      );
                      if (!r.ok) setBannerErr(r.error ?? null);
                    }}
                    className="px-5 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
                  >
                    Tạo tổ hợp biến thể (UC-15)
                  </button>
                </div>

                {distinctManagedSizes.length > 0 && (
                  <div className="p-5 rounded-2xl bg-white border border-[#E4DDD0] space-y-3">
                    <p className="font-semibold text-[#22261E]">
                      2. Quản lý giá bán theo Size (UC-16 — Cùng size mọi màu nhận cùng 1 giá)
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {distinctManagedSizes.map((sz) => (
                        <label key={sz} className="space-y-1">
                          <span className="font-medium">Giá Size {sz} (VND)</span>
                          <input
                            type="number"
                            min={1}
                            step={1}
                            value={priceDraft[sz] ?? ''}
                            onChange={(e) =>
                              setPriceDraft((p) => ({
                                ...p,
                                [sz]: e.target.value,
                              }))
                            }
                            placeholder="Chưa có giá"
                            className="w-full px-3 py-2 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                          />
                        </label>
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        const parsed: Record<string, number> = {};
                        for (const sz of distinctManagedSizes) {
                          parsed[sz] = Number(priceDraft[sz] ?? 0);
                        }
                        const r = updateSizePrices(managedProd.id, parsed);
                        if (!r.ok) setBannerErr(r.error ?? null);
                      }}
                      className="px-5 py-2 rounded-full bg-[#22261E] text-white font-semibold hover:bg-[#4A5D43] cursor-pointer"
                    >
                      Lưu bảng giá theo size (UC-16)
                    </button>
                  </div>
                )}
              </>
            )}

            {/* Existing Variants Table */}
            <div className="rounded-2xl bg-white border border-[#E4DDD0] overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-[#F3EFE6]">
                  <tr>
                    <th className="px-4 py-2.5">SKU</th>
                    <th className="px-4 py-2.5">Màu × Size</th>
                    <th className="px-4 py-2.5">Giá bán</th>
                    <th className="px-4 py-2.5">Trạng thái</th>
                    <th className="px-4 py-2.5">Tồn kho (Chỉ đọc)</th>
                    <th className="px-4 py-2.5 text-right">Xóa</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E4DDD0]">
                  {managedVariants.map((v) => (
                    <tr key={v.sku}>
                      <td className="px-4 py-2.5 font-mono">{v.sku}</td>
                      <td className="px-4 py-2.5">
                        {v.color} × {v.size}
                      </td>
                      <td className="px-4 py-2.5 tabular-price font-medium">
                        {v.sellPrice ? (
                          formatVND(v.sellPrice)
                        ) : (
                          <span className="text-[#A84A3B]">Chưa có giá</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5">
                        <button
                          type="button"
                          disabled={managedLocked}
                          onClick={() => {
                            const r = toggleVariantStatus(v.sku);
                            if (!r.ok) setBannerErr(r.error ?? null);
                          }}
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold cursor-pointer disabled:opacity-60 ${
                            v.status === 'ACTIVE'
                              ? 'bg-[#E3F2E8] text-[#1F5E39]'
                              : 'bg-[#EFECE6] text-[#6E7368]'
                          }`}
                        >
                          {v.status === 'ACTIVE' ? 'Đang bán' : 'Ngừng bán'}
                        </button>
                      </td>
                      <td className="px-4 py-2.5 tabular-price">
                        {v.stockQuantity}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        {!managedLocked && (
                          <button
                            type="button"
                            onClick={() => {
                              const r = deleteVariant(v.sku);
                              if (!r.ok) setBannerErr(r.error ?? null);
                            }}
                            className="text-[#8E3B2E] hover:underline cursor-pointer"
                          >
                            Xóa
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ============================================================================
 * 3. FULL-BLEED 5-COLUMN TAXONOMY BOARD (UC-17 — All 5 Visible Simultaneously!)
 * ============================================================================ */
export const EmployeeTaxonomyView: React.FC = () => {
  const {
    categories,
    collections,
    genders,
    sizes,
    colors,
    manageTaxonomy,
  } = useSobieSystem();

  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [newHex, setNewHex] = useState('#4A5D43');
  const [err, setErr] = useState<string | null>(null);

  const columns: {
    id: 'category' | 'collection' | 'gender' | 'color' | 'size';
    title: string;
    items: string[];
  }[] = [
    { id: 'category', title: '1. Danh mục (1 cấp)', items: categories },
    { id: 'collection', title: '2. Bộ sưu tập', items: collections },
    { id: 'gender', title: '3. Giới tính', items: genders },
    { id: 'color', title: '4. Màu sắc', items: colors.map((c) => c.name) },
    { id: 'size', title: '5. Kích cỡ (Size)', items: sizes },
  ];

  return (
    <div className="space-y-6">
      <div>
        <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
          <Tag className="w-3.5 h-3.5" />
          <span>Bảng Phân Loại & Thuộc Tính Toàn Viền · UC-17</span>
        </div>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
          5 nhóm phân loại & thuộc tính hiển thị đồng thời
        </h1>
        <p className="text-xs text-[#5E6658] mt-0.5">
          Chặn xóa khi đang có sản phẩm/biến thể sử dụng; chặn đổi tên nếu thuộc tính gắn với sản phẩm đã có phiếu nhập `CONFIRMED` (`UC-17-Q7`).
        </p>
      </div>

      {err && (
        <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
          {err}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-5 items-start">
        {columns.map((col) => (
          <div
            key={col.id}
            className="rounded-3xl atelier-card p-5 space-y-4 text-xs"
          >
            <div className="flex items-center justify-between border-b border-[#E4DDD0] pb-3">
              <h3 className="font-semibold text-[#22261E]">{col.title}</h3>
              <span className="px-2 py-0.5 rounded-full bg-[#E5ECE0] text-[#3B4B35] font-semibold tabular-price">
                {col.items.length}
              </span>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                const val = drafts[col.id] ?? '';
                const r = manageTaxonomy(
                  col.id,
                  'add',
                  val,
                  undefined,
                  col.id === 'color' ? newHex : undefined
                );
                if (!r.ok) setErr(r.error ?? null);
                else setDrafts((p) => ({ ...p, [col.id]: '' }));
              }}
              className="flex gap-1.5"
            >
              <input
                type="text"
                required
                value={drafts[col.id] ?? ''}
                onChange={(e) =>
                  setDrafts((p) => ({ ...p, [col.id]: e.target.value }))
                }
                placeholder="Thêm mới..."
                className="flex-1 min-w-0 px-3 py-2 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
              />
              {col.id === 'color' && (
                <input
                  type="color"
                  value={newHex}
                  onChange={(e) => setNewHex(e.target.value)}
                  className="w-9 h-9 rounded-xl bg-white border border-[#E4DDD0] p-0.5 cursor-pointer shrink-0"
                />
              )}
              <button
                type="submit"
                className="px-3 py-2 rounded-xl bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer shrink-0"
              >
                +
              </button>
            </form>

            <div className="divide-y divide-[#E4DDD0]">
              {col.items.map((item) => (
                <div
                  key={item}
                  className="py-2.5 flex items-center justify-between gap-2"
                >
                  <div className="flex items-center gap-2 font-medium text-[#22261E] min-w-0">
                    {col.id === 'color' && (
                      <span
                        className="w-3.5 h-3.5 rounded-full border border-[#22261E]/20 shrink-0"
                        style={{
                          backgroundColor:
                            colors.find((c) => c.name === item)?.hex ?? '#878E80',
                        }}
                      />
                    )}
                    <span className="truncate">{item}</span>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => {
                        setErr(null);
                        const renamed = prompt(`Đổi tên "${item}" thành:`, item);
                        if (renamed && renamed.trim() && renamed.trim() !== item) {
                          const r = manageTaxonomy(
                            col.id,
                            'rename',
                            item,
                            renamed
                          );
                          if (!r.ok) setErr(r.error ?? null);
                        }
                      }}
                      className="text-[#4A5D43] font-semibold hover:underline cursor-pointer"
                    >
                      Sửa
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setErr(null);
                        const r = manageTaxonomy(col.id, 'delete', item);
                        if (!r.ok) setErr(r.error ?? null);
                      }}
                      className="text-[#8E3B2E] hover:underline cursor-pointer"
                    >
                      Xóa
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
