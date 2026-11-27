import React, { useRef } from 'react';
import { Heart, ArrowUpRight } from 'lucide-react';
import { calcDiscountedPrice, formatVND, gsap, useGSAP } from '../lib/gsap';
import { useSobieSystem } from '../context/SobieSystemContext';
import { ProductRecord } from '../types/store';

interface ProductCardProps {
  product: ProductRecord;
  rankNumber?: number;
  soldQtyBadge?: number;
  featured?: boolean;
  onSelectProduct: (productId: string) => void;
  onRequireLogin: () => void;
  className?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  rankNumber,
  soldQtyBadge,
  featured = false,
  onSelectProduct,
  onRequireLogin,
  className = '',
}) => {
  const {
    colors,
    activeWishlist,
    storefrontUser,
    getActiveProductPromo,
    getProductMinPrice,
    hasMultipleSizePrices,
    getValidPricedVariants,
    isProductSoldOut,
    toggleWishlist,
  } = useSobieSystem();

  const cardRef = useRef<HTMLElement>(null);
  const primaryImgRef = useRef<HTMLImageElement>(null);
  const secondaryImgRef = useRef<HTMLImageElement>(null);
  const heartBtnRef = useRef<HTMLButtonElement>(null);

  const isDiscontinued = product.status === 'INACTIVE';
  const minPrice = getProductMinPrice(product.id) ?? 0;
  const multiPrice = hasMultipleSizePrices(product.id);
  const activePromo = getActiveProductPromo(product.id);
  const finalPrice = calcDiscountedPrice(
    minPrice,
    activePromo?.discountPercentage
  );
  const soldOut = isProductSoldOut(product.id);
  const isWishlisted = Boolean(
    storefrontUser && activeWishlist.includes(product.id)
  );

  const orderedGallery = [...product.gallery].sort(
    (a, b) => a.orderNo - b.orderNo
  );
  const hasSecondImage = orderedGallery.length > 1;

  const validVariants = getValidPricedVariants(product.id);
  const distinctColors = Array.from(new Set(validVariants.map((v) => v.color)));

  const { contextSafe } = useGSAP({ scope: cardRef });

  const handleMouseEnter = contextSafe(() => {
    if (isDiscontinued) return;
    if (cardRef.current) {
      gsap.to(cardRef.current, {
        y: -4,
        duration: 0.35,
        ease: 'power2.out',
      });
    }
    if (primaryImgRef.current) {
      gsap.to(primaryImgRef.current, {
        scale: 1.045,
        duration: 0.6,
        ease: 'power2.out',
      });
    }
    if (hasSecondImage && secondaryImgRef.current) {
      gsap.to(secondaryImgRef.current, {
        autoAlpha: 1,
        scale: 1.02,
        duration: 0.45,
        ease: 'power2.out',
      });
    }
  });

  const handleMouseLeave = contextSafe(() => {
    if (cardRef.current) {
      gsap.to(cardRef.current, {
        y: 0,
        duration: 0.35,
        ease: 'power2.out',
      });
    }
    if (primaryImgRef.current) {
      gsap.to(primaryImgRef.current, {
        scale: 1,
        duration: 0.6,
        ease: 'power2.out',
      });
    }
    if (hasSecondImage && secondaryImgRef.current) {
      gsap.to(secondaryImgRef.current, {
        autoAlpha: 0,
        scale: 1,
        duration: 0.4,
        ease: 'power2.out',
      });
    }
  });

  const handleHeartClick = contextSafe((e: React.MouseEvent) => {
    e.stopPropagation();
    const res = toggleWishlist(product.id);
    if (res.requireLogin) {
      onRequireLogin();
      return;
    }
    if (heartBtnRef.current) {
      gsap.fromTo(
        heartBtnRef.current,
        { scale: 0.8 },
        { scale: 1, duration: 0.45, ease: 'back.out(2.4)' }
      );
    }
  });

  return (
    <article
      ref={cardRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={() => {
        // UC-38 AC-7: Discontinued product in wishlist cannot open detail page
        if (!isDiscontinued) onSelectProduct(product.id);
      }}
      className={`group flex flex-col rounded-2xl bg-[#FFFDF9] border border-[#E4DDD0] hover:border-[#4A5D43]/55 p-3 shadow-[0_8px_24px_-14px_rgba(34,38,30,0.08)] transition-colors gsap-will-transform ${
        featured ? 'h-full p-4 rounded-3xl' : ''
      } ${isDiscontinued ? 'cursor-not-allowed' : 'cursor-pointer'} ${className}`}
    >
      {/* Sea-Salt Image Frame */}
      <div
        className={`relative rounded-xl overflow-hidden bg-[#F3EFE6] border border-[#E4DDD0] ${
          featured
            ? 'aspect-[4/4.4] lg:aspect-auto lg:flex-1 lg:min-h-[380px]'
            : 'aspect-[3/3.85]'
        }`}
      >
        <img
          ref={primaryImgRef}
          src={orderedGallery[0]?.url ?? '/images/sp-0001-1.jpg'}
          alt={product.name}
          loading="lazy"
          className={`w-full h-full object-cover object-center gsap-will-transform ${
            soldOut || isDiscontinued ? 'opacity-60 grayscale-[28%]' : ''
          }`}
        />

        {hasSecondImage && !isDiscontinued && (
          <img
            ref={secondaryImgRef}
            src={orderedGallery[1].url}
            alt={`${product.name} ảnh 2`}
            loading="lazy"
            className="absolute inset-0 w-full h-full object-cover object-center opacity-0 invisible gsap-will-transform"
          />
        )}

        {/* Top-left Status & Rank Badges */}
        <div className="absolute top-2.5 left-2.5 flex flex-col items-start gap-1.5 z-10">
          {typeof rankNumber === 'number' && (
            <span
              className={`px-2.5 py-1 rounded-lg backdrop-blur-md text-[11px] font-semibold tracking-wider shadow-2xs ${
                rankNumber === 1
                  ? 'bg-[#4A5D43] text-white'
                  : 'bg-[#22261E]/90 text-[#FAF7F2]'
              }`}
            >
              #{String(rankNumber).padStart(2, '0')}
              {typeof soldQtyBadge === 'number' ? ` · Đã bán ${soldQtyBadge}` : ''}
            </span>
          )}
          {isDiscontinued ? (
            <span className="px-2.5 py-1 rounded-lg bg-[#6E7368]/95 text-white text-[11px] font-semibold">
              Ngừng bán
            </span>
          ) : soldOut ? (
            <span className="px-2.5 py-1 rounded-lg bg-[#22261E]/90 text-white text-[11px] font-semibold">
              Hết hàng
            </span>
          ) : (
            activePromo && (
              <span className="px-2.5 py-1 rounded-lg bg-[#A84A3B] text-white text-[11px] font-semibold shadow-2xs">
                -{activePromo.discountPercentage}%
              </span>
            )
          )}
        </div>

        {/* Wishlist Heart Button (UC-38) */}
        <button
          ref={heartBtnRef}
          type="button"
          onClick={handleHeartClick}
          aria-label="Yêu thích"
          className={`absolute top-2.5 right-2.5 z-10 w-8 h-8 rounded-full backdrop-blur-md border flex items-center justify-center transition-colors cursor-pointer ${
            isWishlisted
              ? 'bg-[#FFFDF9] border-[#A84A3B]/35 text-[#A84A3B] shadow-xs'
              : 'bg-[#FFFDF9]/88 border-[#E4DDD0] text-[#5E6658] hover:bg-white hover:text-[#A84A3B]'
          }`}
        >
          <Heart
            className={`w-3.5 h-3.5 ${
              isWishlisted ? 'fill-[#A84A3B] text-[#A84A3B]' : 'stroke-[1.8]'
            }`}
          />
        </button>

        {/* Price Pill (UC-10 Q1: "Từ <min>₫" when multiple size prices exist!) */}
        <div className="absolute bottom-2.5 left-2.5 right-2.5 z-10 flex items-center justify-between gap-2 pointer-events-none">
          <div className="inline-flex items-baseline gap-1.5 px-2.5 py-1 rounded-lg bg-[#FFFDF9]/94 backdrop-blur-md border border-[#E4DDD0] shadow-xs tabular-price">
            {multiPrice && minPrice > 0 && (
              <span className="text-[10.5px] text-[#5E6658] font-medium">Từ</span>
            )}
            <span
              className={`font-semibold text-[#22261E] ${
                featured ? 'text-base' : 'text-[13px]'
              }`}
            >
              {minPrice > 0 ? formatVND(finalPrice) : 'Tạm ngừng'}
            </span>
            {activePromo && minPrice > 0 && (
              <span className="text-[11px] text-[#878E80] line-through">
                {formatVND(minPrice)}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Card Body */}
      <div
        className={`pt-3 px-1 flex flex-col justify-between ${
          featured ? 'space-y-2.5' : 'space-y-1.5 flex-1'
        }`}
      >
        <div>
          <div className="flex items-center justify-between text-[10.5px] uppercase tracking-wider text-[#878E80] font-medium">
            <span className="truncate">{product.category}</span>
            <span className="font-mono">{product.id}</span>
          </div>
          <h3
            className={`font-medium text-[#22261E] group-hover:text-[#4A5D43] transition-colors mt-0.5 ${
              featured
                ? 'font-editorial text-xl sm:text-2xl leading-snug'
                : 'text-[14.5px] line-clamp-1'
            }`}
          >
            {product.name}
          </h3>
          {featured && (
            <p className="text-xs text-[#5E6658] line-clamp-2 mt-1 leading-relaxed">
              {product.subtitle}
            </p>
          )}
        </div>

        <div className="pt-1.5 flex items-center justify-between gap-2 border-t border-[#F3EFE6]">
          <div className="flex flex-wrap items-center gap-1.5">
            {distinctColors.slice(0, 6).map((cName) => {
              const found = colors.find((c) => c.name === cName);
              return (
                <span
                  key={cName}
                  title={cName}
                  className="w-3 h-3 rounded-full border border-[#22261E]/20 shadow-2xs"
                  style={{ backgroundColor: found?.hex ?? '#878E80' }}
                />
              );
            })}
            {distinctColors.length === 0 && (
              <span className="text-[11px] text-[#878E80]">Chưa mở biến thể</span>
            )}
          </div>

          <span className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-[#4A5D43] opacity-85 group-hover:opacity-100 transition-opacity">
            <span>{featured ? 'Khám phá quán quân' : 'Chi tiết'}</span>
            <ArrowUpRight className="w-3 h-3" />
          </span>
        </div>
      </div>
    </article>
  );
};
