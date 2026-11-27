import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowLeft,
  Heart,
  Ruler,
  CheckCircle2,
  AlertCircle,
  Minus,
  Plus,
  ShoppingBag,
  Sparkles,
} from 'lucide-react';
import { calcDiscountedPrice, formatVND, gsap, useGSAP } from '../lib/gsap';
import { useSobieSystem } from '../context/SobieSystemContext';
import { ProductCard } from './ProductCard';

interface ProductDetailPageProps {
  productId: string;
  onBack: () => void;
  onSelectCategory: (cat: string) => void;
  onSelectProduct: (productId: string) => void;
  onOpenSizeGuide: () => void;
  onOpenCartDrawer: () => void;
  onRequireLogin: () => void;
}

export const ProductDetailPage: React.FC<ProductDetailPageProps> = ({
  productId,
  onBack,
  onSelectCategory,
  onSelectProduct,
  onOpenSizeGuide,
  onOpenCartDrawer,
  onRequireLogin,
}) => {
  const {
    products,
    colors,
    storefrontUser,
    activeWishlist,
    getValidPricedVariants,
    getProductMinPrice,
    getActiveProductPromo,
    isProductEligibleForListing,
    addToCart,
    toggleWishlist,
  } = useSobieSystem();

  const detailRef = useRef<HTMLDivElement>(null);

  const product = products.find(
    (p) => p.id === productId && p.status === 'ACTIVE'
  );
  // UC-12-Q9b: Only ACTIVE variants with sellPrice > 0 participate
  const validVariants = useMemo(
    () => (product ? getValidPricedVariants(product.id) : []),
    [product, getValidPricedVariants]
  );

  const temporarilyUnavailable = validVariants.length === 0;

  const availableColors = useMemo(
    () => Array.from(new Set(validVariants.map((v) => v.color))),
    [validVariants]
  );
  const availableSizes = useMemo(
    () => Array.from(new Set(validVariants.map((v) => v.size))),
    [validVariants]
  );

  const [selectedColor, setSelectedColor] = useState<string>('');
  const [selectedSize, setSelectedSize] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [hint, setHint] = useState<string>('');

  useEffect(() => {
    setSelectedColor('');
    setSelectedSize('');
    setQuantity(1);
    setHint('');
  }, [productId]);

  useGSAP(
    () => {
      if (!product) return;
      gsap.from('.pdp-reveal', {
        y: 18,
        autoAlpha: 0,
        duration: 0.55,
        stagger: 0.06,
        ease: 'power3.out',
      });
    },
    { dependencies: [product?.id], scope: detailRef, revertOnUpdate: true }
  );

  // Min-max price range before size selection; exact size price once selected (UC-10-Q9 / UC-12 AC-5, AC-6)
  const priceBounds = useMemo(() => {
    if (!product || validVariants.length === 0) return { min: 0, max: 0 };
    const prices = validVariants.map((v) => v.sellPrice!);
    return { min: Math.min(...prices), max: Math.max(...prices) };
  }, [product, validVariants]);

  const sizePrice = useMemo(() => {
    if (!product) return 0;
    if (selectedSize) {
      const v = validVariants.find((vr) => vr.size === selectedSize);
      return v?.sellPrice ?? getProductMinPrice(product.id) ?? 0;
    }
    return getProductMinPrice(product.id) ?? 0;
  }, [selectedSize, validVariants, product, getProductMinPrice]);

  const selectedVariant = useMemo(() => {
    if (!selectedColor || !selectedSize) return undefined;
    return validVariants.find(
      (v) => v.color === selectedColor && v.size === selectedSize
    );
  }, [validVariants, selectedColor, selectedSize]);

  // UC-12 E1 / AC-11: Parent INACTIVE or non-existent -> 404 screen
  if (!product) {
    return (
      <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-20 text-center">
        <div className="max-w-2xl mx-auto p-12 rounded-3xl atelier-card space-y-4">
          <h1 className="font-editorial text-3xl text-[#22261E]">
            Không tìm thấy sản phẩm (404)
          </h1>
          <p className="text-sm text-[#5E6658]">
            Sản phẩm này không tồn tại hoặc sản phẩm cha đã ngừng bán (UC-12 AC-11).
          </p>
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] cursor-pointer"
          >
            Quay lại cửa hàng
          </button>
        </div>
      </div>
    );
  }

  const orderedGallery = [...product.gallery].sort(
    (a, b) => a.orderNo - b.orderNo
  );
  const activePromo = getActiveProductPromo(product.id);
  const isWishlisted = Boolean(
    storefrontUser && activeWishlist.includes(product.id)
  );
  const discountedPrice = calcDiscountedPrice(
    sizePrice,
    activePromo?.discountPercentage
  );
  const discountedMin = calcDiscountedPrice(
    priceBounds.min,
    activePromo?.discountPercentage
  );
  const discountedMax = calcDiscountedPrice(
    priceBounds.max,
    activePromo?.discountPercentage
  );

  const handleAdd = () => {
    if (temporarilyUnavailable) return;
    if (!selectedColor || !selectedSize) {
      setHint('Vui lòng chọn màu và size');
      return;
    }
    if (!selectedVariant || selectedVariant.stockQuantity <= 0) {
      setHint('Hết hàng');
      return;
    }
    const res = addToCart(selectedVariant.sku, product.id, quantity);
    if (!res.ok) {
      setHint(res.error ?? 'Không thể thêm vào giỏ');
      return;
    }
    setHint('');
    onOpenCartDrawer();
  };

  const related = products
    .filter(
      (p) =>
        isProductEligibleForListing(p.id) &&
        p.id !== product.id &&
        p.category === product.category
    )
    .slice(0, 4);

  return (
    <div
      ref={detailRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8"
    >
      {/* Breadcrumb Bar */}
      <div className="pdp-reveal flex flex-wrap items-center justify-between gap-4 pb-6 text-xs text-[#5E6658]">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#FFFDF9] border border-[#E4DDD0] text-[#22261E] hover:border-[#4A5D43] font-medium cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5 text-[#4A5D43]" />
            <span>Quay lại danh mục</span>
          </button>
          <span className="text-[#D4CBB8]">/</span>
          <button
            type="button"
            onClick={() => onSelectCategory(product.category)}
            className="hover:text-[#22261E] cursor-pointer"
          >
            {product.category}
          </button>
          <span className="text-[#D4CBB8]">/</span>
          <span className="text-[#22261E] font-semibold">{product.name}</span>
        </div>
        <span className="font-mono text-[#5E6658] bg-[#FFFDF9] px-3 py-1 rounded-lg border border-[#E4DDD0]">
          {product.id}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 xl:gap-12 items-start">
        {/* LEFT 7 COLS: EDITORIAL GALLERY GRID (UC-12 AC-3, AC-4: Color NEVER swaps gallery!) */}
        <div className="lg:col-span-7 space-y-5">
          {orderedGallery.length > 1 && (
            <div className="pdp-reveal flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 rounded-2xl atelier-card text-xs text-[#5E6658]">
              <span className="inline-flex items-center gap-1.5 font-medium text-[#22261E]">
                <Sparkles className="w-3.5 h-3.5 text-[#4A5D43]" />
                <span>
                  Thư viện ảnh theo thứ tự ({orderedGallery.length} ảnh — giữ nguyên khi đổi màu theo UC-12 AC-4)
                </span>
              </span>
              <div className="flex flex-wrap items-center gap-1.5">
                {orderedGallery.map((g) => (
                  <a
                    key={`jump-${g.orderNo}`}
                    href={`#pdp-photo-${g.orderNo}`}
                    className="px-2.5 py-1 rounded-full bg-[#E5ECE0] hover:bg-[#4A5D43] hover:text-white text-[11px] font-mono text-[#3B4B35] font-semibold transition-colors"
                  >
                    Ảnh #{g.orderNo}
                  </a>
                ))}
              </div>
            </div>
          )}

          <div
            className={`grid gap-5 ${
              orderedGallery.length > 1 ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1'
            }`}
          >
            {orderedGallery.map((g, idx) => (
              <figure
                key={`${g.url}-${g.orderNo}`}
                id={`pdp-photo-${g.orderNo}`}
                className={`pdp-reveal relative rounded-3xl overflow-hidden atelier-card p-2.5 ${
                  orderedGallery.length === 1 ? 'max-w-2xl' : ''
                }`}
              >
                <div className="relative rounded-2xl overflow-hidden bg-[#F3EFE6] aspect-[4/4.8]">
                  <img
                    src={g.url}
                    alt={`${product.name} — Ảnh #${g.orderNo}`}
                    className="w-full h-full object-cover object-center"
                  />

                  {idx === 0 && (
                    <div className="absolute top-4 left-4 flex flex-wrap gap-2">
                      {activePromo && (
                        <span className="px-3 py-1 rounded-full bg-[#A84A3B] text-white text-xs font-semibold shadow-xs">
                          -{activePromo.discountPercentage}% ({activePromo.promotionId})
                        </span>
                      )}
                      {product.collections.map((col) => (
                        <span
                          key={col}
                          className="px-3 py-1 rounded-full bg-[#FFFDF9]/92 backdrop-blur-md border border-[#E4DDD0] text-xs font-medium text-[#22261E]"
                        >
                          {col}
                        </span>
                      ))}
                    </div>
                  )}

                  <span className="absolute bottom-3.5 right-3.5 px-2.5 py-1 rounded-lg bg-[#FFFDF9]/92 backdrop-blur-md border border-[#E4DDD0] font-mono text-[11px] font-semibold text-[#5E6658]">
                    Ảnh #{g.orderNo}
                  </span>
                </div>
              </figure>
            ))}
          </div>
        </div>

        {/* RIGHT 5 COLS: STICKY SEA-SALT CREAM & OLIVE PURCHASE STUDIO */}
        <div className="lg:col-span-5 lg:sticky lg:top-28 self-start">
          <div className="pdp-reveal rounded-3xl atelier-card p-6 sm:p-8 shadow-[0_18px_44px_-20px_rgba(34,38,30,0.12)] space-y-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
                  {product.category} · {product.gender}
                </p>
                <h1 className="font-editorial text-3xl sm:text-[36px] leading-tight text-[#22261E] mt-1">
                  {product.name}
                </h1>
                <p className="text-xs sm:text-sm text-[#5E6658] mt-1.5">
                  {product.subtitle}
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  const res = toggleWishlist(product.id);
                  if (res.requireLogin) onRequireLogin();
                }}
                className={`w-11 h-11 rounded-full border flex items-center justify-center shrink-0 transition-colors cursor-pointer ${
                  isWishlisted
                    ? 'bg-[#FBECE9] border-[#A84A3B]/40 text-[#A84A3B]'
                    : 'bg-[#FAF7F2] border-[#E4DDD0] text-[#5E6658] hover:border-[#A84A3B] hover:text-[#A84A3B]'
                }`}
                title="Thả tim yêu thích (UC-38)"
              >
                <Heart
                  className={`w-5 h-5 ${
                    isWishlisted ? 'fill-[#A84A3B] text-[#A84A3B]' : ''
                  }`}
                />
              </button>
            </div>

            {/* UC-12-Q9b: Active parent without valid active priced variants */}
            {temporarilyUnavailable ? (
              <div className="p-4 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] font-semibold">
                Sản phẩm tạm ngừng kinh doanh (UC-12-Q9b: Chưa có biến thể đang bán có giá hợp lệ).
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] flex flex-wrap items-baseline justify-between gap-4">
                <div className="flex items-baseline gap-2.5 tabular-price">
                  <span className="text-2xl sm:text-3xl font-bold text-[#22261E]">
                    {selectedSize || discountedMin === discountedMax
                      ? formatVND(discountedPrice)
                      : `${formatVND(discountedMin)} – ${formatVND(discountedMax)}`}
                  </span>
                  {activePromo && (
                    <span className="text-sm text-[#878E80] line-through">
                      {selectedSize || priceBounds.min === priceBounds.max
                        ? formatVND(sizePrice)
                        : `${formatVND(priceBounds.min)} – ${formatVND(priceBounds.max)}`}
                    </span>
                  )}
                </div>
                <span className="text-[11.5px] font-semibold text-[#4A5D43]">
                  {selectedSize
                    ? `Giá cố định Size ${selectedSize} (mọi màu)`
                    : 'Chọn size để xem đúng đơn giá'}
                </span>
              </div>
            )}

            {/* 1. Color Selector — All buttons visible */}
            <div className="space-y-2.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#22261E]">
                1. Chọn màu sắc:{' '}
                <span className="font-normal text-[#5E6658] normal-case">
                  {selectedColor || 'Chưa chọn'}
                </span>
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {availableColors.map((cName) => {
                  const cObj = colors.find((c) => c.name === cName);
                  const active = selectedColor === cName;
                  return (
                    <button
                      key={cName}
                      type="button"
                      disabled={temporarilyUnavailable}
                      onClick={() => {
                        setSelectedColor(cName);
                        setHint('');
                      }}
                      className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-full border text-xs transition-all cursor-pointer disabled:opacity-45 ${
                        active
                          ? 'border-[#4A5D43] bg-[#E5ECE0] font-semibold text-[#22261E] ring-2 ring-[#4A5D43]/15'
                          : 'border-[#E4DDD0] bg-[#FAF7F2] text-[#5E6658] hover:border-[#4A5D43]'
                      }`}
                    >
                      <span
                        className="w-3.5 h-3.5 rounded-full border border-[#22261E]/20"
                        style={{ backgroundColor: cObj?.hex ?? '#878E80' }}
                      />
                      <span>{cName}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 2. Size Selector + Common Store Size Chart Modal Trigger */}
            <div className="space-y-2.5">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="font-semibold uppercase tracking-wider text-[#22261E]">
                  2. Chọn size:{' '}
                  <span className="font-normal text-[#5E6658] normal-case">
                    {selectedSize || 'Chưa chọn'}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={onOpenSizeGuide}
                  className="inline-flex items-center gap-1.5 text-[#4A5D43] hover:underline font-semibold cursor-pointer"
                >
                  <Ruler className="w-3.5 h-3.5" />
                  <span>Bảng size chung cửa hàng (UC-12)</span>
                </button>
              </div>

              <div className="flex flex-wrap gap-2.5">
                {availableSizes.map((sz) => {
                  const active = selectedSize === sz;
                  const matchVar = selectedColor
                    ? validVariants.find(
                        (v) => v.color === selectedColor && v.size === sz
                      )
                    : undefined;
                  const oos =
                    selectedColor !== '' &&
                    (!matchVar || matchVar.stockQuantity <= 0);

                  return (
                    <button
                      key={sz}
                      type="button"
                      disabled={temporarilyUnavailable}
                      onClick={() => {
                        setSelectedSize(sz);
                        setQuantity(1);
                        setHint('');
                      }}
                      className={`min-w-[78px] py-2.5 px-4 rounded-xl border text-xs font-semibold transition-all cursor-pointer disabled:opacity-45 ${
                        active
                          ? 'bg-[#4A5D43] text-white border-[#4A5D43] shadow-xs'
                          : oos
                          ? 'bg-[#F3EFE6] text-[#878E80] border-[#E4DDD0] line-through'
                          : 'bg-[#FAF7F2] text-[#22261E] border-[#E4DDD0] hover:border-[#4A5D43]'
                      }`}
                    >
                      Size {sz}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Real-time Variant Availability Status */}
            {!temporarilyUnavailable && (
              <div>
                {!selectedColor || !selectedSize ? (
                  <div className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] text-xs text-[#5E6658]">
                    <AlertCircle className="w-4 h-4 text-[#4A5D43]" />
                    <span>Vui lòng chọn màu và size</span>
                  </div>
                ) : selectedVariant && selectedVariant.stockQuantity > 0 ? (
                  <div className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#E3F2E8] border border-[#B7DEC5] text-xs text-[#1F5E39] font-medium">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>
                      Còn hàng ({selectedVariant.stockQuantity} sản phẩm · SKU:{' '}
                      <strong className="font-mono">{selectedVariant.sku}</strong>)
                    </span>
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] font-semibold">
                    <AlertCircle className="w-4 h-4" />
                    <span>Hết hàng</span>
                  </div>
                )}
              </div>
            )}

            {hint && (
              <p className="text-xs text-[#8E3B2E] font-semibold">{hint}</p>
            )}

            {/* Quantity Stepper & Olive Add to Cart CTA */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="inline-flex items-center rounded-full bg-[#FAF7F2] border border-[#E4DDD0] h-12 px-2">
                <button
                  type="button"
                  disabled={temporarilyUnavailable}
                  onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-[#22261E] hover:bg-[#E5ECE0] cursor-pointer disabled:opacity-40"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
                <span className="w-10 text-center text-sm font-semibold text-[#22261E] tabular-price">
                  {quantity}
                </span>
                <button
                  type="button"
                  disabled={temporarilyUnavailable}
                  onClick={() => {
                    const max = selectedVariant?.stockQuantity ?? 99;
                    if (quantity + 1 > max) {
                      setHint(`Chỉ còn ${max} sản phẩm`);
                      return;
                    }
                    setHint('');
                    setQuantity((q) => q + 1);
                  }}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-[#22261E] hover:bg-[#E5ECE0] cursor-pointer disabled:opacity-40"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              </div>

              <button
                type="button"
                onClick={handleAdd}
                disabled={
                  temporarilyUnavailable ||
                  !selectedColor ||
                  !selectedSize ||
                  !selectedVariant ||
                  selectedVariant.stockQuantity <= 0
                }
                className="flex-1 min-w-[200px] h-12 px-6 rounded-full bg-[#4A5D43] text-white text-sm font-semibold hover:bg-[#3B4B35] disabled:bg-[#D4CBB8] disabled:text-[#5E6658] transition-colors inline-flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed shadow-xs"
              >
                <ShoppingBag className="w-4 h-4" />
                <span>Thêm vào giỏ hàng tạm</span>
              </button>
            </div>

            {/* Product Editorial Description */}
            <div className="pt-4 border-t border-[#E4DDD0] space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#22261E]">
                Chi tiết chất liệu & Thiết kế
              </h3>
              <p className="text-sm text-[#5E6658] leading-relaxed">
                {product.description}
              </p>
            </div>
          </div>
        </div>
      </div>

      {related.length > 0 && (
        <section className="mt-20 pt-14 border-t border-[#E4DDD0]">
          <h2 className="font-editorial text-3xl text-[#22261E] mb-8">
            Thiết kế cùng danh mục {product.category}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
            {related.map((item) => (
              <ProductCard
                key={item.id}
                product={item}
                onSelectProduct={onSelectProduct}
                onRequireLogin={onRequireLogin}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
