import React, { useMemo, useRef } from 'react';
import {
  ArrowRight,
  Sparkles,
  TrendingUp,
  Sun,
  Waves,
  Phone,
  MessageCircle,
  ShieldCheck,
  Tag,
} from 'lucide-react';
import { gsap, ScrollTrigger, useGSAP } from '../lib/gsap';
import { STORE_CONFIG } from '../data/seedData';
import { useSobieSystem } from '../context/SobieSystemContext';
import { ProductCard } from './ProductCard';

interface HomePageProps {
  onSelectProduct: (productId: string) => void;
  onSelectCategory: (category: string) => void;
  onSelectCollection: (collection: string) => void;
  onRequireLogin: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  onSelectProduct,
  onSelectCategory,
  onSelectCollection,
  onRequireLogin,
}) => {
  const {
    products,
    categories,
    collections,
    isProductEligibleForListing,
    getTop5BestSellers7Days,
  } = useSobieSystem();
  const homeRef = useRef<HTMLDivElement>(null);
  const ctaBtnRef = useRef<HTMLButtonElement>(null);

  // UC-09 / UC-10 Q10: Filter eligible products (ACTIVE parent + >= 1 ACTIVE variant with price > 0)
  const eligibleProducts = useMemo(
    () => products.filter((p) => isProductEligibleForListing(p.id)),
    [products, isProductEligibleForListing]
  );

  // Block 1 (UC-09): Top 5 Best-Selling Products in last 168h UTC
  const bestSellers = useMemo(
    () => getTop5BestSellers7Days(),
    [getTop5BestSellers7Days]
  );

  // Block 2 (UC-09 Q1): Up to 8 newest eligible products sorted by createdAt DESC, productId ASC
  const newArrivals = useMemo(
    () =>
      [...eligibleProducts]
        .sort((a, b) => {
          const cmp = b.createdAt.localeCompare(a.createdAt);
          return cmp !== 0 ? cmp : a.id.localeCompare(b.id);
        })
        .slice(0, 8),
    [eligibleProducts]
  );

  // Block 3 (UC-09): Up to 4 newest eligible products per Collection (hide empty blocks!)
  const collectionBlocks = useMemo(() => {
    return collections
      .map((colName) => ({
        name: colName,
        items: [...eligibleProducts]
          .filter((p) => p.collections.includes(colName))
          .sort((a, b) => {
            const cmp = b.createdAt.localeCompare(a.createdAt);
            return cmp !== 0 ? cmp : a.id.localeCompare(b.id);
          })
          .slice(0, 4),
      }))
      .filter((blk) => blk.items.length > 0);
  }, [collections, eligibleProducts]);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add(
        {
          isDesktop: '(min-width: 768px)',
          reduceMotion: '(prefers-reduced-motion: reduce)',
        },
        (context) => {
          const { isDesktop, reduceMotion } = context.conditions as {
            isDesktop: boolean;
            reduceMotion: boolean;
          };

          if (reduceMotion) return;

          const heroTl = gsap.timeline({
            defaults: { ease: 'power3.out', duration: 0.8 },
          });
          heroTl
            .from('.hero-eyebrow', { y: 14, autoAlpha: 0, duration: 0.5 })
            .from(
              '.hero-headline-line',
              { yPercent: 100, autoAlpha: 0, stagger: 0.1 },
              '-=0.25'
            )
            .from('.hero-copy', { y: 14, autoAlpha: 0, duration: 0.6 }, '-=0.35')
            .from('.hero-actions', { y: 12, autoAlpha: 0, duration: 0.55 }, '-=0.35')
            .fromTo(
              '.hero-panorama-frame',
              {
                clipPath: 'inset(6% 3% 6% 3% round 24px)',
                scale: 0.98,
                autoAlpha: 0,
              },
              {
                clipPath: 'inset(0% 0% 0% 0% round 24px)',
                scale: 1,
                autoAlpha: 1,
                duration: 1.0,
                ease: 'power3.out',
                clearProps: 'clipPath',
              },
              0.15
            )
            .from(
              '.hero-glass-chip',
              { y: 16, autoAlpha: 0, stagger: 0.12, duration: 0.55 },
              '-=0.45'
            );

          if (isDesktop) {
            gsap.to('.hero-parallax-img', {
              yPercent: 8,
              ease: 'none',
              scrollTrigger: {
                trigger: '.hero-panorama-frame',
                start: 'top bottom',
                end: 'bottom top',
                scrub: 1,
              },
            });
          }

          gsap.set('.home-product-card', { y: 20, autoAlpha: 0 });
          ScrollTrigger.batch('.home-product-card', {
            start: 'top 90%',
            once: true,
            onEnter: (batch) => {
              gsap.to(batch, {
                y: 0,
                autoAlpha: 1,
                duration: 0.55,
                stagger: 0.06,
                ease: 'power3.out',
                overwrite: true,
              });
            },
          });
        }
      );

      const btn = ctaBtnRef.current;
      if (!btn) return;
      const xTo = gsap.quickTo(btn, 'x', { duration: 0.35, ease: 'power3.out' });
      const yTo = gsap.quickTo(btn, 'y', { duration: 0.35, ease: 'power3.out' });
      const onMove = (e: MouseEvent) => {
        const rect = btn.getBoundingClientRect();
        xTo((e.clientX - (rect.left + rect.width / 2)) * 0.14);
        yTo((e.clientY - (rect.top + rect.height / 2)) * 0.18);
      };
      const onLeave = () => {
        xTo(0);
        yTo(0);
      };
      btn.addEventListener('mousemove', onMove);
      btn.addEventListener('mouseleave', onLeave);

      return () => {
        btn.removeEventListener('mousemove', onMove);
        btn.removeEventListener('mouseleave', onLeave);
        mm.revert();
      };
    },
    { dependencies: [eligibleProducts.length, bestSellers.length], scope: homeRef }
  );

  const topOne = bestSellers[0];
  const restBestSellers = bestSellers.slice(1, 5);

  return (
    <div ref={homeRef} className="space-y-16 sm:space-y-20 pb-10">
      {/* FULL-BLEED 12-COLUMN WIDESCREEN EDITORIAL HERO */}
      <section className="pt-4 sm:pt-7">
        <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 xl:gap-12 items-center">
            {/* Left 5-Col Editorial Masthead */}
            <div className="lg:col-span-5 space-y-6">
              <div className="hero-eyebrow inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-[#3B4B35] text-[11.5px] font-semibold tracking-[0.14em] uppercase">
                <Sparkles className="w-3.5 h-3.5" />
                <span>SOBIE ATELIER · BỘ SƯU TẬP HÈ 2026</span>
              </div>

              <h1 className="font-editorial text-4xl sm:text-5xl xl:text-[62px] leading-[1.08] font-medium text-[#22261E]">
                <span className="block overflow-hidden pb-1">
                  <span className="hero-headline-line block">
                    Vẻ đẹp thuần khiết
                  </span>
                </span>
                <span className="block overflow-hidden pb-1">
                  <span className="hero-headline-line block italic font-normal text-[#4A5D43]">
                    cát muối biển & nhành ô-liu.
                  </span>
                </span>
              </h1>

              <p className="hero-copy text-sm sm:text-[15.5px] text-[#5E6658] leading-relaxed">
                Thiết kế đồ bơi dệt gân cao cấp kháng tia cực tím UPF 50+, tôn vinh đường nét tự nhiên. Trải nghiệm giỏ hàng thông minh tự tính ưu đãi có lợi nhất, thanh toán VietQR SePay tự động và phí ship cố định 12.000₫.
              </p>

              {/* All Category Quick Pills Visible Without Horizontal Scroll */}
              <div className="hero-actions space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    ref={ctaBtnRef}
                    type="button"
                    onClick={() => onSelectCategory('')}
                    className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-full bg-[#4A5D43] text-white text-xs sm:text-sm font-semibold hover:bg-[#3B4B35] transition-colors shadow-[0_12px_26px_-10px_rgba(74,93,67,0.45)] cursor-pointer gsap-will-transform"
                  >
                    <span>Khám phá toàn bộ sản phẩm</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  <a
                    href={STORE_CONFIG.zaloUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-3.5 rounded-full bg-[#FFFDF9] border border-[#D4CBB8] text-[#22261E] text-xs sm:text-sm font-semibold hover:border-[#4A5D43] transition-colors"
                  >
                    <MessageCircle className="w-4 h-4 text-[#4A5D43]" />
                    <span>Tư vấn Zalo · {STORE_CONFIG.hotline}</span>
                  </a>
                </div>

                {/* Visible Category Chips (NO horizontal scrollbar!) */}
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => onSelectCategory(cat)}
                      className="px-3.5 py-1.5 rounded-full bg-[#F3EFE6] border border-[#E4DDD0] hover:border-[#4A5D43] hover:bg-[#E5ECE0] text-xs font-medium text-[#3E4539] transition-colors cursor-pointer"
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Right 7-Col Edge-to-Edge Panoramic Frame */}
            <div className="lg:col-span-7">
              <div className="hero-panorama-frame relative rounded-3xl p-2.5 sm:p-3.5 bg-[#FFFDF9] border border-[#E4DDD0] shadow-[0_24px_54px_-24px_rgba(34,38,30,0.16)] gsap-will-transform">
                <div className="relative aspect-[16/10] sm:aspect-[16/9.5] rounded-2xl overflow-hidden bg-[#F3EFE6]">
                  <img
                    src="/images/hero-editorial.jpg"
                    alt="Sobie Sea-Salt & Olive Collection"
                    className="hero-parallax-img w-full h-[116%] -mt-[6%] object-cover object-center gsap-will-transform"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#22261E]/45 via-transparent to-transparent pointer-events-none" />

                  <div className="hero-glass-chip hidden sm:flex items-center gap-3.5 absolute bottom-4 left-4 md:bottom-6 md:left-6 p-3.5 pr-5 rounded-2xl bg-[#FFFDF9]/92 backdrop-blur-xl border border-[#E4DDD0] shadow-lg max-w-xs">
                    <div className="w-10 h-10 rounded-xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center shrink-0">
                      <ShieldCheck className="w-5 h-5" />
                    </div>
                    <div className="text-left">
                      <p className="text-xs font-semibold text-[#22261E]">
                        Chuẩn Vải Biển UPF 50+
                      </p>
                      <p className="text-[11px] text-[#5E6658] flex items-center gap-1 mt-0.5">
                        <Phone className="w-3 h-3 text-[#4A5D43]" />
                        <span>Hotline: {STORE_CONFIG.hotline}</span>
                      </p>
                    </div>
                  </div>

                  <div className="hero-glass-chip hidden sm:flex items-center gap-3.5 absolute bottom-4 right-4 md:bottom-6 md:right-6 p-3.5 pr-5 rounded-2xl bg-[#FFFDF9]/92 backdrop-blur-xl border border-[#E4DDD0] shadow-lg max-w-xs">
                    <div className="w-10 h-10 rounded-xl bg-[#FBECE9] text-[#A84A3B] flex items-center justify-center shrink-0">
                      <Tag className="w-5 h-5" />
                    </div>
                    <div className="text-left">
                      <p className="text-xs font-semibold text-[#22261E]">
                        Voucher <span className="font-mono text-[#4A5D43]">HE2026</span> (-15%)
                      </p>
                      <p className="text-[11px] text-[#5E6658] mt-0.5">
                        Đơn từ 300.000₫ · Ship 12.000₫
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* BLOCK 1: FULL-BLEED BENTO SHOWCASE — TOP 5 BEST-SELLERS IN LAST 7 DAYS (UC-09) */}
      {bestSellers.length > 0 && topOne && (
        <section className="bg-[#F3EFE6] border-y border-[#E4DDD0] py-16">
          <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-9">
              <div>
                <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span>Khối Bán Chạy 7 Ngày Gần Nhất · UC-09</span>
                </div>
                <h2 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                  Top {bestSellers.length} thiết kế được yêu thích nhất tuần qua
                </h2>
              </div>
              <p className="text-xs text-[#5E6658] max-w-lg leading-relaxed">
                Tổng hợp số lượng bán thực tế trong 168 giờ UTC gần nhất (loại trừ đơn Đã hủy / Giao không thành công; tự động ẩn tức thì sản phẩm Ngừng bán).
              </p>
            </div>

            {restBestSellers.length === 0 ? (
              <div className="max-w-xl">
                <ProductCard
                  product={topOne.product}
                  rankNumber={1}
                  soldQtyBadge={topOne.soldQty}
                  featured
                  onSelectProduct={onSelectProduct}
                  onRequireLogin={onRequireLogin}
                  className="home-product-card"
                />
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
                <div className="lg:col-span-5 flex">
                  <ProductCard
                    product={topOne.product}
                    rankNumber={1}
                    soldQtyBadge={topOne.soldQty}
                    featured
                    onSelectProduct={onSelectProduct}
                    onRequireLogin={onRequireLogin}
                    className="home-product-card w-full"
                  />
                </div>

                <div className="lg:col-span-7 grid grid-cols-2 xl:grid-cols-4 lg:grid-cols-2 gap-5 content-start">
                  {restBestSellers.map((entry, idx) => (
                    <ProductCard
                      key={entry.product.id}
                      product={entry.product}
                      rankNumber={idx + 2}
                      soldQtyBadge={entry.soldQty}
                      onSelectProduct={onSelectProduct}
                      onRequireLogin={onRequireLogin}
                      className="home-product-card"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* BLOCK 2: FULL-BLEED NEW ARRIVALS — UP TO 8 NEWEST PRODUCTS (UC-09 Q1) */}
      {newArrivals.length > 0 && (
        <section className="w-full px-5 sm:px-8 lg:px-12 xl:px-16">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
                <Sun className="w-3.5 h-3.5" />
                <span>Hàng Mới Đang Bán · Tối Đa 8 Sản Phẩm Mới Nhất (UC-09)</span>
              </div>
              <h2 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                Thiết kế mới cập bến Sobie
              </h2>
            </div>
            <button
              type="button"
              onClick={() => onSelectCategory('')}
              className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-[#4A5D43] text-xs font-semibold text-white hover:bg-[#3B4B35] transition-colors cursor-pointer"
            >
              <span>Xem toàn bộ danh mục</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
            {newArrivals.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onSelectProduct={onSelectProduct}
                onRequireLogin={onRequireLogin}
                className="home-product-card"
              />
            ))}
          </div>
        </section>
      )}

      {/* BLOCK 3: FULL-BLEED COLLECTION SHOWCASES (UC-09 — Auto-hide empty blocks) */}
      {collectionBlocks.map((colBlock) => (
        <section
          key={colBlock.name}
          className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 pt-2"
        >
          <div className="p-6 sm:p-9 rounded-3xl atelier-card space-y-7">
            <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E4DDD0] pb-5">
              <div>
                <div className="inline-flex items-center gap-1.5 text-xs uppercase tracking-[0.18em] text-[#4A5D43] font-semibold">
                  <Waves className="w-3.5 h-3.5" />
                  <span>Bộ Sưu Tập Tuyển Chọn · Tối Đa 4 Thiết Kế Mới Nhất</span>
                </div>
                <h2 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                  Bộ sưu tập {colBlock.name}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => onSelectCollection(colBlock.name)}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-xs font-semibold text-[#3B4B35] hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
              >
                <span>Lọc BST {colBlock.name}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
              {colBlock.items.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onSelectProduct={onSelectProduct}
                  onRequireLogin={onRequireLogin}
                  className="home-product-card"
                />
              ))}
            </div>
          </div>
        </section>
      ))}
    </div>
  );
};
