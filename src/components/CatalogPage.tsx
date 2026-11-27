import React, { useMemo, useRef } from 'react';
import {
  SlidersHorizontal,
  X,
  ChevronLeft,
  ChevronRight,
  Search,
  ArrowUpDown,
} from 'lucide-react';
import {
  calcDiscountedPrice,
  gsap,
  removeVietnameseTones,
  useGSAP,
} from '../lib/gsap';
import { useSobieSystem } from '../context/SobieSystemContext';
import { CatalogFilters, ProductRecord } from '../types/store';
import { ProductCard } from './ProductCard';

interface CatalogPageProps {
  filters: CatalogFilters;
  onUpdateFilters: (patch: Partial<CatalogFilters>) => void;
  onResetFilters: () => void;
  onSelectProduct: (productId: string) => void;
  onRequireLogin: () => void;
}

const ITEMS_PER_PAGE = 12;

export const CatalogPage: React.FC<CatalogPageProps> = ({
  filters,
  onUpdateFilters,
  onResetFilters,
  onSelectProduct,
  onRequireLogin,
}) => {
  const {
    categories,
    collections,
    genders,
    sizes,
    products,
    variants,
    isProductEligibleForListing,
    getProductMinPrice,
    getActiveProductPromo,
  } = useSobieSystem();

  const containerRef = useRef<HTMLDivElement>(null);

  const effectiveMinPrice = (p: ProductRecord) => {
    const raw = getProductMinPrice(p.id) ?? 0;
    const promo = getActiveProductPromo(p.id);
    return calcDiscountedPrice(raw, promo?.discountPercentage);
  };

  // UC-10 + UC-11: Filter & accent-insensitive Vietnamese search + deterministic tie-break productId ASC
  const filteredProducts = useMemo(() => {
    const qNorm = removeVietnameseTones(filters.search.trim().toLowerCase());

    // UC-10 Q8: Ignore non-existent filter values gracefully
    const validCategory =
      !filters.category || categories.includes(filters.category)
        ? filters.category
        : '';
    const validGender =
      !filters.gender || genders.includes(filters.gender) ? filters.gender : '';
    const validSize =
      !filters.size || sizes.includes(filters.size) ? filters.size : '';
    const validCollection =
      !filters.collection || collections.includes(filters.collection)
        ? filters.collection
        : '';

    const list = products.filter((p) => {
      // UC-10 Q10: Filter eligible products before count/pagination
      if (!isProductEligibleForListing(p.id)) return false;
      if (validCategory && p.category !== validCategory) return false;
      if (validGender && p.gender !== validGender) return false;
      // UC-10 Q3: Product has >= 1 variant of chosen size, regardless of stock
      if (validSize) {
        const pVars = variants.filter((v) => v.productId === p.id);
        if (!pVars.some((v) => v.size === validSize)) return false;
      }
      if (validCollection && !p.collections.includes(validCollection)) {
        return false;
      }
      // UC-11 Q1: Accent-insensitive substring match on product name & description
      if (qNorm) {
        const targetText = removeVietnameseTones(
          `${p.name} ${p.description} ${p.id}`.toLowerCase()
        );
        if (!targetText.includes(qNorm)) return false;
      }
      return true;
    });

    list.sort((a, b) => {
      if (filters.sort === 'price-asc') {
        const diff = effectiveMinPrice(a) - effectiveMinPrice(b);
        return diff !== 0 ? diff : a.id.localeCompare(b.id);
      }
      if (filters.sort === 'price-desc') {
        const diff = effectiveMinPrice(b) - effectiveMinPrice(a);
        return diff !== 0 ? diff : a.id.localeCompare(b.id);
      }
      const dateCmp = b.createdAt.localeCompare(a.createdAt);
      return dateCmp !== 0 ? dateCmp : a.id.localeCompare(b.id);
    });

    return list;
  }, [
    products,
    variants,
    filters,
    categories,
    genders,
    sizes,
    collections,
    isProductEligibleForListing,
    getProductMinPrice,
    getActiveProductPromo,
  ]);

  const totalPages = Math.max(
    1,
    Math.ceil(filteredProducts.length / ITEMS_PER_PAGE)
  );
  // UC-10 Q5: Clamp out-of-range page to [1, totalPages]
  const safePage = Math.min(Math.max(1, filters.page), totalPages);

  const paginatedProducts = useMemo(() => {
    const start = (safePage - 1) * ITEMS_PER_PAGE;
    return filteredProducts.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredProducts, safePage]);

  useGSAP(
    () => {
      const cards = containerRef.current?.querySelectorAll('.catalog-card');
      if (!cards || cards.length === 0) return;
      gsap.fromTo(
        cards,
        { y: 18, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.45,
          stagger: 0.04,
          ease: 'power2.out',
          clearProps: 'transform',
        }
      );
    },
    {
      dependencies: [
        filters.category,
        filters.gender,
        filters.size,
        filters.collection,
        filters.search,
        filters.sort,
        safePage,
        filteredProducts.length,
      ],
      scope: containerRef,
      revertOnUpdate: true,
    }
  );

  const hasActiveFilter = Boolean(
    filters.category ||
      filters.gender ||
      filters.size ||
      filters.collection ||
      filters.search
  );

  return (
    <div
      ref={containerRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-6 sm:pt-8 space-y-7"
    >
      {/* Page Masthead */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
            Danh Mục & Tìm Kiếm Toàn Viền · UC-10 / UC-11
          </p>
          <h1 className="font-editorial text-3xl sm:text-5xl text-[#22261E] mt-1">
            {filters.category
              ? filters.category
              : filters.collection
              ? `Bộ sưu tập ${filters.collection}`
              : filters.search
              ? `Kết quả cho "${filters.search}"`
              : 'Tất cả thiết kế đang mở bán'}
          </h1>
        </div>

        <p className="text-xs text-[#5E6658] tabular-price">
          Hiển thị{' '}
          <strong className="text-[#22261E] font-semibold">
            {filteredProducts.length}
          </strong>{' '}
          thiết kế đủ điều kiện mở bán (12 sản phẩm / trang)
        </p>
      </div>

      {/* EXPANDED ALL-VISIBLE FILTER BOARD (NO dropdowns or horizontal scrollbars!) */}
      <section className="rounded-3xl atelier-card p-5 sm:p-7 space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#E4DDD0]">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#22261E]">
            <SlidersHorizontal className="w-4 h-4 text-[#4A5D43]" />
            <span>Bộ lọc trực quan kết hợp VÀ (UC-10) — Hiển thị toàn bộ nút chọn</span>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {hasActiveFilter && (
              <button
                type="button"
                onClick={onResetFilters}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#FBECE9] text-[#8E3B2E] text-xs font-semibold hover:bg-[#F5D6D0] transition-colors cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
                <span>Xóa toàn bộ bộ lọc</span>
              </button>
            )}

            {/* All 3 Sort Buttons Visible Directly (No Scroll / No Hidden Select) */}
            <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-full bg-[#F3EFE6] border border-[#E4DDD0]">
              <span className="inline-flex items-center gap-1 pl-2.5 pr-1 text-[11px] font-semibold text-[#5E6658]">
                <ArrowUpDown className="w-3 h-3 text-[#4A5D43]" />
                Sắp xếp:
              </span>
              {(
                [
                  { id: 'newest', label: 'Mới nhất' },
                  { id: 'price-asc', label: 'Giá tăng dần' },
                  { id: 'price-desc', label: 'Giá giảm dần' },
                ] as const
              ).map((sOpt) => (
                <button
                  key={sOpt.id}
                  type="button"
                  onClick={() => onUpdateFilters({ sort: sOpt.id, page: 1 })}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors cursor-pointer ${
                    filters.sort === sOpt.id
                      ? 'bg-[#4A5D43] text-white'
                      : 'text-[#5E6658] hover:text-[#22261E]'
                  }`}
                >
                  {sOpt.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Full-Width Multi-Group Button Matrix (Zero Horizontal Scroll!) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Search Input (UC-11) */}
          <div className="lg:col-span-3 space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
              Tìm kiếm từ khóa (UC-11)
            </span>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#878E80] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) =>
                  onUpdateFilters({ search: e.target.value, page: 1 })
                }
                placeholder="Tìm tên, mô tả (có/không dấu)..."
                className="w-full pl-9 pr-3.5 py-2.5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] placeholder:text-[#878E80] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
              />
            </div>
          </div>

          {/* 1. Danh mục — All buttons visible */}
          <div className="lg:col-span-3 space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
              1. Danh mục sản phẩm
            </span>
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => onUpdateFilters({ category: '', page: 1 })}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                  filters.category === ''
                    ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                    : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                }`}
              >
                Tất cả
              </button>
              {categories.map((cat) => {
                const active = filters.category === cat;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() =>
                      onUpdateFilters({
                        category: active ? '' : cat,
                        page: 1,
                      })
                    }
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                      active
                        ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                        : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Giới tính & 3. Size — All buttons visible */}
          <div className="lg:col-span-3 space-y-3">
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
                2. Giới tính
              </span>
              <div className="flex flex-wrap gap-1.5">
                <button
                  type="button"
                  onClick={() => onUpdateFilters({ gender: '', page: 1 })}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                    filters.gender === ''
                      ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                      : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                  }`}
                >
                  Tất cả
                </button>
                {genders.map((g) => {
                  const active = filters.gender === g;
                  return (
                    <button
                      key={g}
                      type="button"
                      onClick={() =>
                        onUpdateFilters({ gender: active ? '' : g, page: 1 })
                      }
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                        active
                          ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                          : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                      }`}
                    >
                      {g}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
                3. Kích cỡ (Size)
              </span>
              <div className="flex flex-wrap gap-1.5">
                <button
                  type="button"
                  onClick={() => onUpdateFilters({ size: '', page: 1 })}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                    filters.size === ''
                      ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                      : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                  }`}
                >
                  Tất cả
                </button>
                {sizes.map((s) => {
                  const active = filters.size === s;
                  return (
                    <button
                      key={s}
                      type="button"
                      onClick={() =>
                        onUpdateFilters({ size: active ? '' : s, page: 1 })
                      }
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                        active
                          ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                          : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                      }`}
                    >
                      Size {s}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* 4. Bộ sưu tập — All buttons visible */}
          <div className="lg:col-span-3 space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
              4. Bộ sưu tập
            </span>
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => onUpdateFilters({ collection: '', page: 1 })}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                  filters.collection === ''
                    ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                    : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                }`}
              >
                Tất cả BST
              </button>
              {collections.map((col) => {
                const active = filters.collection === col;
                return (
                  <button
                    key={col}
                    type="button"
                    onClick={() =>
                      onUpdateFilters({
                        collection: active ? '' : col,
                        page: 1,
                      })
                    }
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                      active
                        ? 'bg-[#4A5D43] text-white border-[#4A5D43] font-semibold'
                        : 'bg-[#FAF7F2] text-[#5E6658] border-[#E4DDD0] hover:border-[#4A5D43]'
                    }`}
                  >
                    {col}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* FULL-BLEED PRODUCT GRID & 12 ITEMS/PAGE PAGINATION */}
      {paginatedProducts.length === 0 ? (
        <div className="rounded-3xl atelier-card p-14 text-center space-y-4">
          <p className="font-editorial text-2xl text-[#22261E]">
            {filters.search.trim() &&
            !filters.category &&
            !filters.gender &&
            !filters.size &&
            !filters.collection
              ? `Không tìm thấy sản phẩm phù hợp với '${filters.search.trim()}'`
              : filters.category &&
                !filters.gender &&
                !filters.size &&
                !filters.collection &&
                !filters.search
              ? 'Chưa có sản phẩm trong danh mục này'
              : 'Không có sản phẩm phù hợp với tổ hợp bộ lọc đã chọn'}
          </p>
          <button
            type="button"
            onClick={onResetFilters}
            className="px-6 py-2.5 rounded-full bg-[#4A5D43] text-white text-xs font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
          >
            Đặt lại bộ lọc
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
            {paginatedProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onSelectProduct={onSelectProduct}
                onRequireLogin={onRequireLogin}
                className="catalog-card"
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pt-6 border-t border-[#E4DDD0] flex flex-wrap items-center justify-between gap-4">
              <p className="text-xs text-[#5E6658]">
                Trang <strong>{safePage}</strong> / {totalPages} · Tổng{' '}
                {filteredProducts.length} sản phẩm (12 SP/trang)
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  disabled={safePage <= 1}
                  onClick={() => onUpdateFilters({ page: safePage - 1 })}
                  className="p-2 rounded-full border border-[#E4DDD0] bg-[#FFFDF9] text-[#22261E] disabled:opacity-40 hover:border-[#4A5D43] cursor-pointer"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                {Array.from({ length: totalPages }, (_, idx) => idx + 1).map(
                  (pNum) => (
                    <button
                      key={pNum}
                      type="button"
                      onClick={() => onUpdateFilters({ page: pNum })}
                      className={`w-9 h-9 rounded-full text-xs font-semibold cursor-pointer transition-colors ${
                        pNum === safePage
                          ? 'bg-[#4A5D43] text-white'
                          : 'bg-[#FFFDF9] border border-[#E4DDD0] text-[#5E6658] hover:border-[#4A5D43]'
                      }`}
                    >
                      {pNum}
                    </button>
                  )
                )}
                <button
                  type="button"
                  disabled={safePage >= totalPages}
                  onClick={() => onUpdateFilters({ page: safePage + 1 })}
                  className="p-2 rounded-full border border-[#E4DDD0] bg-[#FFFDF9] text-[#22261E] disabled:opacity-40 hover:border-[#4A5D43] cursor-pointer"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
