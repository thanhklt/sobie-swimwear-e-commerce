import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  X,
  Trash2,
  Minus,
  Plus,
  ShoppingBag,
  Tag,
  QrCode,
  Truck,
  CheckCircle2,
  ArrowRight,
  Lock,
  AlertTriangle,
  Sparkles,
  UserCheck,
  ShieldCheck,
  Gift,
} from 'lucide-react';
import { calcDiscountedPrice, formatVND, gsap, useGSAP } from '../lib/gsap';
import { STORE_CONFIG } from '../data/seedData';
import { useSobieSystem } from '../context/SobieSystemContext';
import { OrderRecord } from '../types/store';

function useEnrichedCartLines() {
  const {
    activeCart,
    products,
    variants,
    colors,
    getActiveProductPromo,
  } = useSobieSystem();

  return useMemo(() => {
    return activeCart.map((c) => {
      const product = products.find((p) => p.id === c.productId);
      const variant = variants.find((v) => v.sku === c.sku);
      const isDiscontinued =
        !product ||
        product.status !== 'ACTIVE' ||
        !variant ||
        variant.status !== 'ACTIVE';
      const stock = variant?.stockQuantity ?? 0;
      const isOutOfStock = stock <= 0;
      const unavailable = isDiscontinued || isOutOfStock;

      const rawPrice = variant?.sellPrice ?? 0;
      const promo = product ? getActiveProductPromo(product.id) : undefined;
      const unitPrice = calcDiscountedPrice(rawPrice, promo?.discountPercentage);
      const colorHex =
        colors.find((cl) => cl.name === variant?.color)?.hex ?? '#878E80';

      return {
        sku: c.sku,
        productId: c.productId,
        category: product?.category ?? 'Đồ bơi',
        productName: product?.name ?? c.sku,
        image: product?.gallery[0]?.url ?? '/images/sp-0001-1.jpg',
        color: variant?.color ?? '—',
        colorHex,
        size: variant?.size ?? '—',
        quantity: c.quantity,
        stock,
        rawPrice,
        unitPrice,
        discountPercent: promo?.discountPercentage,
        promoId: promo?.promotionId,
        // UC-18 E2 / AC-7: Unavailable lines are excluded from subtotal!
        lineTotal: unavailable ? 0 : unitPrice * c.quantity,
        unavailable,
        unavailableReason: isDiscontinued ? 'Ngừng bán' : 'Hết hàng',
      };
    });
  }, [activeCart, products, variants, colors, getActiveProductPromo]);
}

/* ============================================================================
 * 1. GRAND ATELIER TEMPORARY CART DRAWER (UC-18 + UC-31 Live Preview)
 * ============================================================================ */
export const CartDrawer: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onGoToFullCart: () => void;
  onSelectProduct: (productId: string) => void;
}> = ({ isOpen, onClose, onGoToFullCart, onSelectProduct }) => {
  const {
    storefrontUser,
    products,
    variants,
    addToCart,
    updateCartQty,
    removeFromCart,
    clearUnavailableFromCart,
    quoteOrderDiscount,
  } = useSobieSystem();

  const lines = useEnrichedCartLines();
  const subtotal = lines.reduce((s, l) => s + l.lineTotal, 0);
  const totalUnits = lines
    .filter((l) => !l.unavailable)
    .reduce((s, l) => s + l.quantity, 0);
  const hasUnavailable = lines.some((l) => l.unavailable);

  // Live UC-31 Preview with HE2026 vs Automatic Order Promotion
  const liveQuote = useMemo(
    () => quoteOrderDiscount(subtotal, 'HE2026'),
    [subtotal, quoteOrderDiscount]
  );

  // Tiered unlock progress toward 500.000₫ (KM-0003 -10% auto order promo)
  const tierGoal = 500000;
  const progressPct = Math.min(100, Math.round((subtotal / tierGoal) * 100));
  const remainingToTier = Math.max(0, tierGoal - subtotal);

  // Quick curated companion recommendations not yet in cart
  const quickRecommendations = useMemo(() => {
    const inCartProductIds = new Set(lines.map((l) => l.productId));
    return products
      .filter((p) => p.status === 'ACTIVE' && !inCartProductIds.has(p.id))
      .map((p) => {
        const firstInStockVar = variants.find(
          (v) =>
            v.productId === p.id &&
            v.status === 'ACTIVE' &&
            v.stockQuantity > 0 &&
            v.sellPrice &&
            v.sellPrice > 0
        );
        return firstInStockVar ? { product: p, variant: firstInStockVar } : null;
      })
      .filter(
        (x): x is { product: (typeof products)[number]; variant: (typeof variants)[number] } =>
          Boolean(x)
      )
      .slice(0, 2);
  }, [products, variants, lines]);

  const wrapperRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const meterBarRef = useRef<HTMLDivElement>(null);
  const [alertMsg, setAlertMsg] = useState<string | null>(null);

  const { contextSafe } = useGSAP(
    () => {
      if (!isOpen) return;
      gsap.fromTo(
        backdropRef.current,
        { autoAlpha: 0 },
        { autoAlpha: 1, duration: 0.3, ease: 'power2.out' }
      );
      gsap.fromTo(
        panelRef.current,
        { xPercent: 100 },
        { xPercent: 0, duration: 0.45, ease: 'power3.out' }
      );
      gsap.from('.drawer-stagger', {
        y: 14,
        autoAlpha: 0,
        duration: 0.4,
        stagger: 0.05,
        delay: 0.12,
        ease: 'power2.out',
      });
    },
    { dependencies: [isOpen], scope: wrapperRef }
  );

  useGSAP(
    () => {
      if (!isOpen || !meterBarRef.current) return;
      gsap.to(meterBarRef.current, {
        width: `${progressPct}%`,
        duration: 0.55,
        ease: 'power3.out',
      });
    },
    { dependencies: [isOpen, progressPct], scope: wrapperRef }
  );

  const handleClose = contextSafe(() => {
    const tl = gsap.timeline({ onComplete: onClose });
    tl.to(panelRef.current, {
      xPercent: 100,
      duration: 0.3,
      ease: 'power2.in',
    }).to(backdropRef.current, { autoAlpha: 0, duration: 0.22 }, '<');
  });

  if (!isOpen) return null;

  const estimatedShipping = subtotal > 0 ? STORE_CONFIG.shippingFee : 0;
  const estimatedPayable = Math.max(
    0,
    subtotal - liveQuote.selectedDiscount + estimatedShipping
  );

  return (
    <div ref={wrapperRef} className="fixed inset-0 z-50 flex justify-end">
      <div
        ref={backdropRef}
        onClick={handleClose}
        className="fixed inset-0 bg-[#22261E]/45 backdrop-blur-[4px]"
      />

      {/* GRAND LUXURY TEMPORARY CART STUDIO PANEL (Wide max-w-2xl) */}
      <aside
        ref={panelRef}
        className="relative z-10 w-full max-w-2xl bg-[#FAF7F2] h-full shadow-[0_0_60px_rgba(34,38,30,0.28)] border-l border-[#D4CBB8] flex flex-col gsap-will-transform"
      >
        {/* 1. ARCHITECTURAL HEADER */}
        <div className="px-6 sm:px-8 py-5 border-b border-[#E4DDD0] bg-[#FFFDF9]">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-[10.5px] font-semibold uppercase tracking-[0.14em] text-[#3B4B35]">
                  <Sparkles className="w-3 h-3" />
                  {storefrontUser
                    ? `Giỏ Đồng Bộ Tài Khoản · ${storefrontUser.accountId}`
                    : 'Giỏ Hàng Tạm Thời · Browser localStorage (UC-18)'}
                </span>
                <span className="text-[11px] text-[#878E80]">
                  Giá cập nhật trực tiếp từ Catalog DB
                </span>
              </div>
              <div className="flex items-baseline gap-3">
                <h2 className="font-editorial text-2xl sm:text-3xl text-[#22261E]">
                  Túi đồ đi biển của bạn
                </h2>
                <span className="text-xs font-semibold text-[#4A5D43] tabular-price">
                  ({lines.length} dòng · {totalUnits} sản phẩm)
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleClose}
              className="p-2.5 rounded-full bg-[#F3EFE6] text-[#3E4539] hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
              aria-label="Đóng giỏ hàng"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* 2. DYNAMIC PROMOTION UNLOCK PROGRESS METER */}
          <div className="mt-4 p-3.5 rounded-2xl bg-[#F3EFE6] border border-[#E4DDD0] space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="inline-flex items-center gap-1.5 font-medium text-[#22261E]">
                <Gift className="w-4 h-4 text-[#4A5D43]" />
                {subtotal >= tierGoal ? (
                  <span>
                    Tuyệt vời! Bạn đã mở khóa{' '}
                    <strong className="text-[#4A5D43]">
                      Ưu đãi Hóa đơn KM-0003 (-10%) & Voucher HE2026 (-15%)
                    </strong>
                  </span>
                ) : subtotal >= 300000 ? (
                  <span>
                    Đã đủ điều kiện áp <strong>HE2026 (-15%)</strong>! Mua thêm{' '}
                    <strong className="text-[#4A5D43] tabular-price">
                      {formatVND(remainingToTier)}
                    </strong>{' '}
                    để mở thêm mốc KM Hóa đơn 500k.
                  </span>
                ) : (
                  <span>
                    Thêm{' '}
                    <strong className="text-[#4A5D43] tabular-price">
                      {formatVND(Math.max(0, 300000 - subtotal))}
                    </strong>{' '}
                    để mở khóa Voucher <strong>HE2026 (-15%)</strong>
                  </span>
                )}
              </span>
              <span className="font-mono text-[11px] font-semibold text-[#4A5D43] tabular-price">
                {progressPct}%
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-[#E4DDD0] overflow-hidden">
              <div
                ref={meterBarRef}
                style={{ width: `${progressPct}%` }}
                className="h-full rounded-full bg-gradient-to-r from-[#607558] to-[#4A5D43]"
              />
            </div>
          </div>
        </div>

        {/* ALERTS & UNAVAILABLE CLEANUP */}
        {alertMsg && (
          <div className="mx-6 sm:mx-8 mt-3 px-4 py-2.5 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] flex items-center justify-between">
            <span>{alertMsg}</span>
            <button
              type="button"
              onClick={() => setAlertMsg(null)}
              className="font-semibold underline cursor-pointer"
            >
              Đóng
            </button>
          </div>
        )}

        {hasUnavailable && (
          <div className="mx-6 sm:mx-8 mt-3 px-4 py-2.5 rounded-2xl bg-[#FBF4E4] border border-[#E8D2A6] text-xs text-[#8A5A14] flex flex-wrap items-center justify-between gap-2">
            <span>
              Có dòng Hết hàng / Ngừng bán (không tính tiền, giữ nguyên số lượng theo UC-18 E2).
            </span>
            <button
              type="button"
              onClick={clearUnavailableFromCart}
              className="px-3 py-1 rounded-full bg-[#8A5A14] text-white font-semibold cursor-pointer"
            >
              Dọn ngay
            </button>
          </div>
        )}

        {/* 3. SCROLLABLE CART LINES + CURATED COMPANION UPSELL */}
        <div className="flex-1 overflow-y-auto px-6 sm:px-8 py-5 space-y-4">
          {lines.length === 0 ? (
            <div className="py-16 text-center space-y-4 rounded-3xl bg-[#FFFDF9] border border-[#E4DDD0] p-8">
              <div className="w-14 h-14 rounded-2xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center mx-auto">
                <ShoppingBag className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="font-editorial text-2xl text-[#22261E]">
                  Giỏ hàng tạm thời đang trống
                </p>
                <p className="text-xs text-[#5E6658] max-w-sm mx-auto leading-relaxed">
                  Khách vãng lai chưa đăng nhập vẫn thoải mái chọn mẫu đồ bơi yêu thích; giỏ sẽ lưu trên trình duyệt và tự gộp khi bạn đăng nhập.
                </p>
              </div>
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Khám phá bộ sưu tập
              </button>
            </div>
          ) : (
            <div className="space-y-3.5">
              {lines.map((line) => (
                <article
                  key={line.sku}
                  className={`drawer-stagger p-4 rounded-2xl border transition-all flex gap-4 ${
                    line.unavailable
                      ? 'bg-[#F3EFE6]/85 border-[#D4CBB8]'
                      : 'bg-[#FFFDF9] border-[#E4DDD0] hover:border-[#4A5D43]/50 shadow-[0_6px_20px_-14px_rgba(34,38,30,0.08)]'
                  }`}
                >
                  <img
                    src={line.image}
                    alt={line.productName}
                    onClick={() => {
                      if (!line.unavailable) {
                        onSelectProduct(line.productId);
                        onClose();
                      }
                    }}
                    className="w-20 h-28 rounded-xl object-cover bg-[#F3EFE6] border border-[#E4DDD0] shrink-0 cursor-pointer"
                  />

                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2 text-[10.5px] text-[#878E80]">
                          <span className="uppercase tracking-wider font-semibold text-[#4A5D43]">
                            {line.category}
                          </span>
                          <span>•</span>
                          <span className="font-mono">{line.sku}</span>
                        </div>
                        <h4
                          onClick={() => {
                            if (!line.unavailable) {
                              onSelectProduct(line.productId);
                              onClose();
                            }
                          }}
                          className="text-sm font-semibold text-[#22261E] hover:text-[#4A5D43] cursor-pointer"
                        >
                          {line.productName}
                        </h4>
                        <div className="flex flex-wrap items-center gap-2 pt-0.5">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#F3EFE6] border border-[#E4DDD0] text-[11px] text-[#3E4539]">
                            <span
                              className="w-2.5 h-2.5 rounded-full border border-[#22261E]/20"
                              style={{ backgroundColor: line.colorHex }}
                            />
                            {line.color}
                          </span>
                          <span className="px-2.5 py-0.5 rounded-full bg-[#F3EFE6] border border-[#E4DDD0] text-[11px] font-semibold text-[#22261E]">
                            Size {line.size}
                          </span>
                          {!line.unavailable && (
                            <span className="text-[11px] text-[#5E6658]">
                              Kho còn {line.stock}
                            </span>
                          )}
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeFromCart(line.sku)}
                        className="p-1.5 rounded-lg text-[#878E80] hover:text-[#8E3B2E] hover:bg-[#FBECE9] transition-colors cursor-pointer"
                        title="Xóa khỏi giỏ"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {line.unavailable ? (
                      <div className="pt-2 flex items-center justify-between">
                        <span className="px-2.5 py-1 rounded-full bg-[#FBECE9] text-[#8E3B2E] text-[11px] font-semibold">
                          {line.unavailableReason} — Không tính vào tạm tính
                        </span>
                        <span className="text-xs text-[#878E80]">
                          SL đã chọn: {line.quantity}
                        </span>
                      </div>
                    ) : (
                      <div className="pt-3 mt-2 border-t border-[#F3EFE6] flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-baseline gap-2 tabular-price">
                          <span className="text-xs font-semibold text-[#22261E]">
                            {formatVND(line.unitPrice)}
                          </span>
                          {line.discountPercent && (
                            <>
                              <span className="text-[11px] text-[#878E80] line-through">
                                {formatVND(line.rawPrice)}
                              </span>
                              <span className="px-1.5 py-0.5 rounded bg-[#FBECE9] text-[#A84A3B] text-[10px] font-bold">
                                -{line.discountPercent}%
                              </span>
                            </>
                          )}
                        </div>

                        <div className="flex items-center gap-3">
                          <div className="inline-flex items-center rounded-full border border-[#D4CBB8] bg-[#FAF7F2] p-0.5">
                            <button
                              type="button"
                              onClick={() => {
                                setAlertMsg(null);
                                if (line.quantity > 1) {
                                  updateCartQty(line.sku, line.quantity - 1);
                                }
                              }}
                              className="w-7 h-7 rounded-full flex items-center justify-center text-[#22261E] hover:bg-[#E5ECE0] cursor-pointer"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="w-8 text-center text-xs font-bold text-[#22261E] tabular-price">
                              {line.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => {
                                const r = updateCartQty(
                                  line.sku,
                                  line.quantity + 1
                                );
                                setAlertMsg(r.ok ? null : r.error ?? null);
                              }}
                              className="w-7 h-7 rounded-full flex items-center justify-center text-[#22261E] hover:bg-[#E5ECE0] cursor-pointer"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>

                          <span className="text-sm font-bold text-[#22261E] tabular-price min-w-[92px] text-right">
                            {formatVND(line.lineTotal)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}

          {/* QUICK COMPANION UPSELL INSIDE TEMPORARY CART */}
          {quickRecommendations.length > 0 && (
            <div className="pt-3 space-y-2.5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#5E6658]">
                Gợi ý phối thêm cho kỳ nghỉ biển (1 chạm thêm vào giỏ tạm)
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {quickRecommendations.map(({ product, variant }) => {
                  const promo = getActivePromoInline(product.id, lines);
                  return (
                    <div
                      key={variant.sku}
                      className="p-3 rounded-2xl bg-[#F3EFE6] border border-[#E4DDD0] flex items-center gap-3"
                    >
                      <img
                        src={product.gallery[0]?.url}
                        alt={product.name}
                        className="w-12 h-16 rounded-lg object-cover bg-[#FAF7F2] shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-[#22261E] truncate">
                          {product.name}
                        </p>
                        <p className="text-[11px] text-[#5E6658]">
                          {variant.color} · {variant.size} ·{' '}
                          <strong className="tabular-price text-[#22261E]">
                            {formatVND(variant.sellPrice ?? 0)}
                          </strong>
                          {promo ? '' : ''}
                        </p>
                        <button
                          type="button"
                          onClick={() => {
                            const r = addToCart(variant.sku, product.id, 1);
                            if (!r.ok) setAlertMsg(r.error ?? null);
                          }}
                          className="mt-1.5 inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#4A5D43] text-white text-[10.5px] font-semibold hover:bg-[#3B4B35] cursor-pointer"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Thêm nhanh</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* 4. GRAND EXECUTIVE SUMMARY FOOTER */}
        {lines.length > 0 && (
          <div className="px-6 sm:px-8 py-5 bg-[#FFFDF9] border-t border-[#D4CBB8] space-y-3.5">
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between text-[#5E6658]">
                <span>Tạm tính hiện tại (sau ưu đãi sản phẩm)</span>
                <span className="font-semibold text-[#22261E] tabular-price">
                  {formatVND(subtotal)}
                </span>
              </div>
              {liveQuote.selectedDiscount > 0 && (
                <div className="flex justify-between text-[#4A5D43]">
                  <span className="font-medium">
                    Ước tính {liveQuote.selectedPromotionLabel}
                  </span>
                  <span className="font-semibold tabular-price">
                    -{formatVND(liveQuote.selectedDiscount)}
                  </span>
                </div>
              )}
              <div className="flex justify-between text-[#5E6658]">
                <span>Phí vận chuyển cố định toàn quốc</span>
                <span className="tabular-price text-[#22261E]">
                  {formatVND(estimatedShipping)}
                </span>
              </div>
              <div className="pt-2 border-t border-[#E4DDD0] flex justify-between items-baseline">
                <span className="text-sm font-semibold text-[#22261E]">
                  Tổng ước tính thanh toán
                </span>
                <span className="font-editorial text-2xl font-semibold text-[#22261E] tabular-price">
                  {formatVND(estimatedPayable)}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onGoToFullCart();
                }}
                className="py-3.5 px-4 rounded-full bg-[#F3EFE6] border border-[#D4CBB8] hover:border-[#4A5D43] text-xs font-semibold text-[#22261E] transition-colors cursor-pointer"
              >
                Xem Giỏ hàng toàn màn hình
              </button>
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onGoToFullCart();
                }}
                className="py-3.5 px-5 rounded-full bg-[#4A5D43] text-white text-xs sm:text-sm font-semibold hover:bg-[#3B4B35] transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-xs"
              >
                <span>Tiến hành đặt hàng</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
};

function getActivePromoInline(productId: string, _lines: unknown[]) {
  return Boolean(productId);
}

/* ============================================================================
 * 2. FULL-BLEED CART & CHECKOUT STUDIO (UC-18, UC-19 v14, UC-20, UC-04 1b, UC-31)
 * ============================================================================ */
export const CartPage: React.FC<{
  onSelectProduct: (productId: string) => void;
  onRequireLogin: () => void;
  onOrderCompleted: () => void;
  onContinueShopping: () => void;
}> = ({
  onSelectProduct,
  onRequireLogin,
  onOrderCompleted,
  onContinueShopping,
}) => {
  const {
    storefrontUser,
    isProfileCompleteForAutofill,
    updateCustomerProfile,
    updateCartQty,
    removeFromCart,
    clearUnavailableFromCart,
    quoteOrderDiscount,
    placeOrder,
    simulateSepayWebhook,
    notify,
  } = useSobieSystem();

  const lines = useEnrichedCartLines();
  const pageRef = useRef<HTMLDivElement>(null);

  // Selective checkout SKUs (UC-19 [GD]: only placed lines are removed from cart!)
  const [selectedSkus, setSelectedSkus] = useState<string[]>([]);

  useEffect(() => {
    const validSkus = lines.filter((l) => !l.unavailable).map((l) => l.sku);
    setSelectedSkus((prev) => {
      if (prev.length === 0) return validSkus;
      const kept = prev.filter((s) => validSkus.includes(s));
      const newlyAdded = validSkus.filter((s) => !prev.includes(s));
      return [...kept, ...newlyAdded];
    });
  }, [lines.length]);

  const [voucherInput, setVoucherInput] = useState('HE2026');
  const [appliedVoucher, setAppliedVoucher] = useState('HE2026');
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // UC-19 v14: Manual entry by default; explicit "Sử dụng thông tin hồ sơ" button copies profile!
  const [paymentMethod, setPaymentMethod] = useState<'COD' | 'QR'>('QR');
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [houseNumber, setHouseNumber] = useState('');
  const [ward, setWard] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('Việt Nam');

  // UC-04 1b / UC-19 2a: Inline Profile Completion Modal when profile is incomplete
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const [pName, setPName] = useState('');
  const [pPhone, setPPhone] = useState('');
  const [pDob, setPDob] = useState('');
  const [pHouse, setPHouse] = useState('');
  const [pWard, setPWard] = useState('');
  const [pCity, setPCity] = useState('');
  const [pCountry, setPCountry] = useState('Việt Nam');
  const [pModalErr, setPModalErr] = useState<string | null>(null);

  const [createdQrOrder, setCreatedQrOrder] = useState<OrderRecord | null>(null);

  useGSAP(
    () => {
      gsap.from('.cart-reveal', {
        y: 16,
        autoAlpha: 0,
        duration: 0.55,
        stagger: 0.06,
        ease: 'power3.out',
      });
    },
    { scope: pageRef }
  );

  const chosenLines = lines.filter(
    (l) => !l.unavailable && selectedSkus.includes(l.sku)
  );
  const subtotal = chosenLines.reduce((s, l) => s + l.lineTotal, 0);
  const hasUnavailableLine = lines.some((l) => l.unavailable);

  const quote = useMemo(
    () => quoteOrderDiscount(subtotal, appliedVoucher),
    [subtotal, appliedVoucher, quoteOrderDiscount]
  );

  const shippingFee = subtotal > 0 ? STORE_CONFIG.shippingFee : 0;
  const totalPayment = Math.max(
    0,
    subtotal - quote.selectedDiscount + shippingFee
  );

  // UC-19 AC-15, AC-18, AC-19: Explicit "Sử dụng thông tin hồ sơ" handler
  const handleUseProfileInfo = () => {
    if (!storefrontUser) return;
    if (isProfileCompleteForAutofill(storefrontUser)) {
      setCustomerName(storefrontUser.name);
      setPhone(storefrontUser.phone);
      setHouseNumber(storefrontUser.houseNumber);
      setWard(storefrontUser.ward);
      setCity(storefrontUser.city);
      setCountry(storefrontUser.country || 'Việt Nam');
      notify('Đã sao chép thông tin nhận hàng từ hồ sơ tài khoản (UC-19 AC-15).');
      return;
    }

    // Profile incomplete -> Open inline UC-04 1b completion modal!
    setPModalErr(null);
    setPName(storefrontUser.name || customerName);
    setPPhone(storefrontUser.phone || phone);
    setPDob(storefrontUser.dateOfBirth || '');
    setPHouse(storefrontUser.houseNumber || houseNumber);
    setPWard(storefrontUser.ward || ward);
    setPCity(storefrontUser.city || city);
    setPCountry(storefrontUser.country || 'Việt Nam');
    setProfileModalOpen(true);
  };

  const handleSaveInlineProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setPModalErr(null);
    if (!pDob.trim()) {
      setPModalErr(
        'Vui lòng bổ sung Ngày sinh để hoàn thiện điều kiện hồ sơ tự điền (UC-04 v7).'
      );
      return;
    }
    if (!pHouse.trim() || !pWard.trim() || !pCity.trim()) {
      setPModalErr('Vui lòng nhập đầy đủ Số nhà, Phường/Xã và Tỉnh/Thành phố.');
      return;
    }
    const res = updateCustomerProfile({
      name: pName,
      phone: pPhone,
      dateOfBirth: pDob,
      houseNumber: pHouse,
      ward: pWard,
      city: pCity,
      country: pCountry,
    });
    if (!res.ok) {
      setPModalErr(res.error ?? 'Không thể lưu hồ sơ.');
      return;
    }
    // Auto-fill checkout fields after saving valid profile (UC-19 AC-18)
    setCustomerName(pName.trim());
    setPhone(pPhone.trim());
    setHouseNumber(pHouse.trim());
    setWard(pWard.trim());
    setCity(pCity.trim());
    setCountry(pCountry.trim() || 'Việt Nam');
    setProfileModalOpen(false);
  };

  const handleCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorBanner(null);
    const res = placeOrder({
      paymentMethod,
      voucherCode: appliedVoucher,
      customerName,
      phone,
      houseNumber,
      ward,
      city,
      country,
      selectedSkus,
      expectedTotal: totalPayment,
    });
    if (!res.ok || !res.order) {
      setErrorBanner(res.error ?? 'Đặt hàng không thành công.');
      return;
    }
    if (paymentMethod === 'QR') {
      setCreatedQrOrder(res.order);
    } else {
      onOrderCompleted();
    }
  };

  // UC-20 Step 5 & UC-25 SePay Webhook Simulation Screen
  if (createdQrOrder) {
    const deadline = new Date(
      new Date(createdQrOrder.createdAt).getTime() + 24 * 3600 * 1000
    ).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

    return (
      <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-12">
        <div className="max-w-3xl mx-auto rounded-3xl atelier-card p-8 sm:p-10 space-y-6 text-center shadow-[0_18px_44px_-20px_rgba(34,38,30,0.12)]">
          <div className="w-12 h-12 rounded-2xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center mx-auto">
            <QrCode className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
              UC-20 · Mã VietQR Tự Động Đối Soát SePay
            </p>
            <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
              Đơn hàng #{createdQrOrder.orderCode}
            </h1>
            <p className="text-xs text-[#5E6658] mt-1">
              Hạn thanh toán (24 giờ): <strong>{deadline}</strong> (quá hạn tự hủy theo UC-24)
            </p>
          </div>

          <div className="max-w-sm mx-auto p-5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-3">
            <div className="aspect-square rounded-xl bg-white border border-[#E4DDD0] p-4 flex flex-col items-center justify-center">
              <svg
                viewBox="0 0 120 120"
                className="w-44 h-44 text-[#22261E]"
                fill="currentColor"
              >
                <rect x="8" y="8" width="32" height="32" rx="4" fill="none" stroke="currentColor" strokeWidth="6" />
                <rect x="18" y="18" width="12" height="12" rx="2" />
                <rect x="80" y="8" width="32" height="32" rx="4" fill="none" stroke="currentColor" strokeWidth="6" />
                <rect x="90" y="18" width="12" height="12" rx="2" />
                <rect x="8" y="80" width="32" height="32" rx="4" fill="none" stroke="currentColor" strokeWidth="6" />
                <rect x="18" y="90" width="12" height="12" rx="2" />
                <rect x="48" y="14" width="10" height="10" />
                <rect x="64" y="14" width="8" height="16" />
                <rect x="14" y="48" width="16" height="8" />
                <rect x="50" y="48" width="20" height="20" rx="3" fill="#4A5D43" />
                <rect x="78" y="48" width="12" height="16" />
                <rect x="48" y="76" width="14" height="10" />
                <rect x="68" y="76" width="18" height="12" />
                <rect x="50" y="92" width="12" height="18" />
                <rect x="88" y="88" width="22" height="22" rx="3" />
              </svg>
              <span className="text-[10px] tracking-widest uppercase text-[#4A5D43] font-semibold mt-1">
                VietQR · Napas 247
              </span>
            </div>

            <div className="text-left text-xs space-y-1.5 pt-1">
              <div className="flex justify-between">
                <span className="text-[#5E6658]">Ngân hàng:</span>
                <span className="font-medium text-[#22261E]">
                  {STORE_CONFIG.bankInfo.bankName}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#5E6658]">Số tài khoản:</span>
                <span className="font-mono font-medium text-[#22261E]">
                  {STORE_CONFIG.bankInfo.accountNumber}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#5E6658]">Số tiền:</span>
                <span className="font-bold text-[#4A5D43] tabular-price">
                  {formatVND(createdQrOrder.totalPrice)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#5E6658]">Nội dung CK (UC-20 AC-2):</span>
                <span className="font-mono font-semibold text-[#22261E]">
                  SOBIE{createdQrOrder.orderCode}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 justify-center pt-2">
            <button
              type="button"
              onClick={() => {
                simulateSepayWebhook(createdQrOrder.orderCode);
                onOrderCompleted();
              }}
              className="px-6 py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] transition-colors inline-flex items-center justify-center gap-2 cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Giả lập Webhook SePay nhận đủ tiền (UC-25)</span>
            </button>
            <button
              type="button"
              onClick={onOrderCompleted}
              className="px-6 py-3 rounded-full bg-[#F3EFE6] border border-[#D4CBB8] text-[#22261E] text-xs font-semibold hover:border-[#4A5D43] transition-colors cursor-pointer"
            >
              Thanh toán sau (Xem trong Đơn hàng của tôi)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={pageRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8"
    >
      {/* Full-Bleed Header */}
      <div className="cart-reveal pb-6 border-b border-[#E4DDD0] flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
            Không Gian Giỏ Hàng & Thanh Toán Toàn Viền · UC-18 / UC-19 / UC-20 / UC-31
          </p>
          <h1 className="font-editorial text-3xl sm:text-5xl text-[#22261E] mt-1">
            Giỏ hàng Sobie Atelier
          </h1>
        </div>
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-xs font-semibold text-[#3B4B35]">
          <ShieldCheck className="w-4 h-4" />
          <span>
            {storefrontUser
              ? `Đang đồng bộ Giỏ Tài Khoản (${storefrontUser.accountId})`
              : 'Đang lưu Giỏ Tạm Trình Duyệt (localStorage · Không lưu giá cũ)'}
          </span>
        </div>
      </div>

      {lines.length === 0 ? (
        <div className="cart-reveal py-20 text-center space-y-4">
          <p className="font-editorial text-3xl text-[#22261E]">
            Giỏ hàng đang trống
          </p>
          <button
            type="button"
            onClick={onContinueShopping}
            className="px-7 py-3 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
          >
            Tiếp tục khám phá sản phẩm
          </button>
        </div>
      ) : (
        <div className="pt-8 grid grid-cols-1 lg:grid-cols-12 gap-8 xl:gap-12 items-start">
          {/* LEFT 7 COLS: CART LINES WITH SELECTIVE CHECKOUT */}
          <div className="cart-reveal lg:col-span-7 space-y-4">
            {errorBanner && (
              <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] font-medium">
                {errorBanner}
              </div>
            )}

            {hasUnavailableLine && (
              <div className="px-4 py-3 rounded-2xl bg-[#FBF4E4] border border-[#E8D2A6] text-xs text-[#8A5A14] flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>
                    Có sản phẩm Hết hàng / Ngừng bán trong giỏ (không tính vào tạm tính — UC-18 E2).
                  </span>
                </div>
                <button
                  type="button"
                  onClick={clearUnavailableFromCart}
                  className="px-3 py-1 rounded-full bg-[#8A5A14] text-white font-semibold cursor-pointer"
                >
                  Dọn dòng không khả dụng
                </button>
              </div>
            )}

            {lines.map((line) => {
              const checked =
                !line.unavailable && selectedSkus.includes(line.sku);
              return (
                <div
                  key={line.sku}
                  className={`p-4 sm:p-5 rounded-3xl border flex gap-4 items-center transition-colors ${
                    line.unavailable
                      ? 'bg-[#F3EFE6]/85 border-[#D4CBB8]'
                      : checked
                      ? 'atelier-card border-[#4A5D43]/45'
                      : 'atelier-card opacity-75'
                  }`}
                >
                  <input
                    type="checkbox"
                    disabled={line.unavailable}
                    checked={checked}
                    onChange={() =>
                      setSelectedSkus((prev) =>
                        checked
                          ? prev.filter((s) => s !== line.sku)
                          : [...prev, line.sku]
                      )
                    }
                    className="w-4 h-4 accent-[#4A5D43] cursor-pointer shrink-0"
                  />

                  <img
                    src={line.image}
                    alt={line.productName}
                    onClick={() => {
                      if (!line.unavailable) onSelectProduct(line.productId);
                    }}
                    className="w-20 h-28 rounded-2xl object-cover bg-[#F3EFE6] border border-[#E4DDD0] shrink-0 cursor-pointer"
                  />

                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10.5px] uppercase tracking-wider font-semibold text-[#4A5D43]">
                          {line.category}
                        </span>
                        <h3 className="text-sm sm:text-base font-semibold text-[#22261E]">
                          {line.productName}
                        </h3>
                        <p className="text-xs text-[#5E6658] font-mono mt-0.5">
                          {line.color} · Size {line.size} · {line.sku}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFromCart(line.sku)}
                        className="p-1.5 text-[#878E80] hover:text-[#8E3B2E] cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {line.unavailable ? (
                      <span className="inline-block px-3 py-1 rounded-full bg-[#FBECE9] text-[#8E3B2E] text-xs font-semibold">
                        {line.unavailableReason} (Không thể đặt)
                      </span>
                    ) : (
                      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                        <div className="flex items-baseline gap-2 tabular-price">
                          <span className="text-sm font-semibold text-[#22261E]">
                            {formatVND(line.unitPrice)}
                          </span>
                          {line.unitPrice < line.rawPrice && (
                            <span className="text-xs text-[#878E80] line-through">
                              {formatVND(line.rawPrice)}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-4">
                          <div className="inline-flex items-center rounded-full border border-[#D4CBB8] bg-[#FAF7F2] px-1.5 py-0.5">
                            <button
                              type="button"
                              onClick={() => {
                                setErrorBanner(null);
                                if (line.quantity > 1) {
                                  updateCartQty(line.sku, line.quantity - 1);
                                }
                              }}
                              className="w-7 h-7 flex items-center justify-center text-[#22261E] cursor-pointer"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="w-8 text-center text-xs font-semibold text-[#22261E] tabular-price">
                              {line.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => {
                                const r = updateCartQty(
                                  line.sku,
                                  line.quantity + 1
                                );
                                setErrorBanner(r.ok ? null : r.error ?? null);
                              }}
                              className="w-7 h-7 flex items-center justify-center text-[#22261E] cursor-pointer"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>

                          <span className="text-sm font-bold text-[#22261E] tabular-price min-w-[96px] text-right">
                            {formatVND(line.lineTotal)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* RIGHT 5 COLS: DISCOUNT QUOTE & CHECKOUT STUDIO (UC-31, UC-19, UC-20) */}
          <div className="cart-reveal lg:col-span-5 lg:sticky lg:top-28">
            <div className="p-6 sm:p-8 rounded-3xl atelier-card shadow-[0_16px_40px_-20px_rgba(34,38,30,0.12)] space-y-5">
              <h2 className="font-editorial text-2xl sm:text-3xl text-[#22261E]">
                Tính mức giảm & Đặt hàng
              </h2>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  setAppliedVoucher(voucherInput.trim());
                }}
                className="space-y-2"
              >
                <label className="text-xs font-medium text-[#3E4539] flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-[#4A5D43]" />
                  <span>Mã voucher (UC-30/31 — Thử `HE2026` hoặc xóa trống)</span>
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={voucherInput}
                    onChange={(e) => setVoucherInput(e.target.value)}
                    placeholder="VD: HE2026"
                    className="flex-1 px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs uppercase tracking-wider text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2.5 rounded-xl bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                  >
                    Áp dụng
                  </button>
                </div>
              </form>

              <div className="space-y-2.5 pt-3 border-t border-[#E4DDD0] text-sm">
                <div className="flex justify-between text-[#5E6658]">
                  <span>Tạm tính ({chosenLines.length} dòng chọn đặt)</span>
                  <span className="tabular-price text-[#22261E] font-semibold">
                    {formatVND(subtotal)}
                  </span>
                </div>

                {quote.selectedDiscount > 0 && (
                  <div className="flex justify-between text-[#4A5D43]">
                    <span className="text-xs font-semibold">
                      {quote.selectedPromotionLabel}
                    </span>
                    <span className="tabular-price font-semibold">
                      -{formatVND(quote.selectedDiscount)}
                    </span>
                  </div>
                )}

                <div className="flex justify-between text-[#5E6658]">
                  <span className="inline-flex items-center gap-1.5">
                    <Truck className="w-3.5 h-3.5 text-[#4A5D43]" />
                    Phí vận chuyển cố định
                  </span>
                  <span className="tabular-price text-[#22261E]">
                    {formatVND(shippingFee)}
                  </span>
                </div>

                {quote.notice && (
                  <p className="text-[11.5px] text-[#3B4B35] bg-[#E5ECE0] border border-[#C5D1BE] px-3.5 py-2.5 rounded-xl leading-relaxed">
                    {quote.notice}
                  </p>
                )}

                <div className="pt-3 border-t border-[#E4DDD0] flex justify-between items-baseline">
                  <span className="font-semibold text-[#22261E]">
                    Tổng thanh toán
                  </span>
                  <span className="font-editorial text-3xl font-semibold text-[#22261E] tabular-price">
                    {formatVND(totalPayment)}
                  </span>
                </div>
              </div>

              {!storefrontUser ? (
                <div className="p-4 rounded-2xl bg-[#F3EFE6] border border-[#E4DDD0] space-y-3">
                  <div className="flex items-start gap-2.5 text-xs text-[#3E4539]">
                    <Lock className="w-4 h-4 text-[#4A5D43] shrink-0 mt-0.5" />
                    <span>
                      Khách vãng lai cần đăng nhập tài khoản Khách hàng để đặt hàng (UC-19 0a). Sau khi đăng nhập, hệ thống sẽ kiểm tra `return_url` hợp lệ, gộp giỏ tạm và quay lại ngay màn hình thanh toán này!
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={onRequireLogin}
                    className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white text-xs sm:text-sm font-semibold hover:bg-[#3B4B35] cursor-pointer"
                  >
                    Đăng nhập để đặt hàng (Tự gộp giỏ)
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={handleCheckout}
                  className="space-y-3.5 pt-3 border-t border-[#E4DDD0]"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
                      Thông tin nhận hàng (UC-19 / UC-20)
                    </p>
                    <button
                      type="button"
                      onClick={handleUseProfileInfo}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-[11px] font-semibold text-[#3B4B35] hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
                    >
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Sử dụng thông tin hồ sơ</span>
                    </button>
                  </div>

                  <p className="text-[11px] text-[#5E6658]">
                    Nhập tay cho riêng đơn này hoặc bấm «Sử dụng thông tin hồ sơ» (hồ sơ tài khoản gốc không bị ghi đè khi sửa tại đây — UC-19 AC-16).
                  </p>

                  <div className="grid grid-cols-2 gap-2.5">
                    <input
                      type="text"
                      required
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      placeholder="Tên người nhận *"
                      className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                    />
                    <input
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="SĐT nhận hàng *"
                      className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                    />
                  </div>
                  <input
                    type="text"
                    required
                    value={houseNumber}
                    onChange={(e) => setHouseNumber(e.target.value)}
                    placeholder="Số nhà và tên đường *"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                  />
                  <div className="grid grid-cols-2 gap-2.5">
                    <input
                      type="text"
                      required
                      value={ward}
                      onChange={(e) => setWard(e.target.value)}
                      placeholder="Phường / Xã *"
                      className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                    />
                    <input
                      type="text"
                      required
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      placeholder="Tỉnh / Thành phố *"
                      className="px-3.5 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2.5 pt-1">
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('QR')}
                      className={`p-3 rounded-xl border text-left transition-colors cursor-pointer ${
                        paymentMethod === 'QR'
                          ? 'border-[#4A5D43] bg-[#E5ECE0]'
                          : 'border-[#E4DDD0] bg-[#FAF7F2]'
                      }`}
                    >
                      <p className="text-xs font-semibold text-[#22261E]">
                        Chuyển khoản QR
                      </p>
                      <p className="text-[11px] text-[#5E6658]">
                        UC-20 · VietQR SePay
                      </p>
                    </button>
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('COD')}
                      className={`p-3 rounded-xl border text-left transition-colors cursor-pointer ${
                        paymentMethod === 'COD'
                          ? 'border-[#4A5D43] bg-[#E5ECE0]'
                          : 'border-[#E4DDD0] bg-[#FAF7F2]'
                      }`}
                    >
                      <p className="text-xs font-semibold text-[#22261E]">
                        Thanh toán COD
                      </p>
                      <p className="text-[11px] text-[#5E6658]">
                        UC-19 · Khi nhận hàng
                      </p>
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={chosenLines.length === 0 || subtotal <= 0}
                    className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white text-sm font-semibold hover:bg-[#3B4B35] disabled:bg-[#D4CBB8] disabled:text-[#5E6658] transition-colors cursor-pointer disabled:cursor-not-allowed shadow-xs"
                  >
                    Xác nhận đặt hàng ({formatVND(totalPayment)})
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      {/* INLINE CHECKOUT PROFILE COMPLETION MODAL (UC-04 1b / UC-19 2a, AC-18, AC-19) */}
      {profileModalOpen && storefrontUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#22261E]/45 backdrop-blur-[3px]">
          <form
            onSubmit={handleSaveInlineProfile}
            className="bg-[#FAF7F2] border border-[#D4CBB8] rounded-3xl max-w-lg w-full p-7 space-y-4 shadow-2xl text-xs"
          >
            <div className="flex items-start justify-between gap-3 border-b border-[#E4DDD0] pb-3">
              <div>
                <p className="text-[11px] uppercase tracking-wider font-semibold text-[#4A5D43]">
                  UC-04 (1b) & UC-19 (2a) · Bổ Sung Hồ Sơ Để Tự Điền
                </p>
                <h3 className="font-editorial text-2xl text-[#22261E] mt-0.5">
                  Hoàn thiện hồ sơ khách hàng
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setProfileModalOpen(false)}
                className="p-1.5 rounded-full hover:bg-[#F3EFE6] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-[#5E6658] leading-relaxed">
              Hồ sơ của bạn hiện còn thiếu thông tin (Họ tên, Ngày sinh, SĐT hoặc Địa chỉ). Lưu hợp lệ để hệ thống tự điền ngay vào đơn hàng, hoặc đóng lại để tiếp tục nhập tay (AC-19).
            </p>

            {pModalErr && (
              <div className="px-3.5 py-2.5 rounded-xl bg-[#FBECE9] border border-[#E7C2BA] text-[#8E3B2E]">
                {pModalErr}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="text-[#5E6658]">Email (Chỉ xem · UC-04 AC-2)</span>
                <input
                  type="email"
                  disabled
                  value={storefrontUser.email}
                  className="w-full px-3.5 py-2 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] text-[#5E6658]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium text-[#22261E]">Ngày sinh *</span>
                <input
                  type="date"
                  required
                  value={pDob}
                  onChange={(e) => setPDob(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium text-[#22261E]">Họ và tên *</span>
                <input
                  type="text"
                  required
                  value={pName}
                  onChange={(e) => setPName(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium text-[#22261E]">Số điện thoại *</span>
                <input
                  type="tel"
                  required
                  value={pPhone}
                  onChange={(e) => setPPhone(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
            </div>

            <label className="block space-y-1">
              <span className="font-medium text-[#22261E]">Số nhà, tên đường *</span>
              <input
                type="text"
                required
                value={pHouse}
                onChange={(e) => setPHouse(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
              />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="font-medium text-[#22261E]">Phường / Xã *</span>
                <input
                  type="text"
                  required
                  value={pWard}
                  onChange={(e) => setPWard(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
              <label className="space-y-1">
                <span className="font-medium text-[#22261E]">Tỉnh / Thành phố *</span>
                <input
                  type="text"
                  required
                  value={pCity}
                  onChange={(e) => setPCity(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                />
              </label>
            </div>

            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setProfileModalOpen(false)}
                className="px-4 py-2 rounded-full border border-[#D4CBB8] bg-white text-[#22261E] cursor-pointer"
              >
                Đóng & Nhập tay
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
              >
                Lưu hồ sơ & Tự điền
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
