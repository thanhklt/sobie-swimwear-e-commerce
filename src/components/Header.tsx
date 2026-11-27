import React, { useEffect, useRef, useState } from 'react';
import {
  Search,
  Heart,
  ShoppingBag,
  User,
  Phone,
  MessageCircle,
  Menu,
  X,
  PackageCheck,
  LogOut,
  ChevronDown,
} from 'lucide-react';
import { gsap, useGSAP } from '../lib/gsap';
import { STORE_CONFIG } from '../data/seedData';
import { useSobieSystem } from '../context/SobieSystemContext';
import { InfoTab, StorefrontRoute } from '../types/store';

interface HeaderProps {
  currentRoute: StorefrontRoute;
  activeCategory: string;
  searchQuery: string;
  onNavigate: (route: StorefrontRoute) => void;
  onSelectCategory: (category: string) => void;
  onSearchSubmit: (query: string) => void;
  onOpenCartDrawer: () => void;
  onOpenInfo: (tab: InfoTab) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentRoute,
  activeCategory,
  searchQuery,
  onNavigate,
  onSelectCategory,
  onSearchSubmit,
  onOpenCartDrawer,
  onOpenInfo,
}) => {
  const {
    categories,
    storefrontUser,
    activeCart,
    activeWishlist,
    logoutStorefront,
    notify,
  } = useSobieSystem();

  const headerRef = useRef<HTMLElement>(null);
  const cartBadgeRef = useRef<HTMLSpanElement>(null);
  const wishBadgeRef = useRef<HTMLSpanElement>(null);

  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);
  const [accountDropdownOpen, setAccountDropdownOpen] = useState(false);

  const cartCount = activeCart.reduce((s, c) => s + c.quantity, 0);
  const wishlistCount = activeWishlist.length;

  useEffect(() => {
    setLocalSearch(searchQuery);
  }, [searchQuery]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 18);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useGSAP(
    () => {
      if (cartCount > 0 && cartBadgeRef.current) {
        gsap.fromTo(
          cartBadgeRef.current,
          { scale: 1.35 },
          { scale: 1, duration: 0.4, ease: 'back.out(2)' }
        );
      }
    },
    { dependencies: [cartCount], scope: headerRef }
  );

  useGSAP(
    () => {
      if (wishlistCount > 0 && wishBadgeRef.current) {
        gsap.fromTo(
          wishBadgeRef.current,
          { scale: 1.35 },
          { scale: 1, duration: 0.4, ease: 'back.out(2)' }
        );
      }
    },
    { dependencies: [wishlistCount], scope: headerRef }
  );

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!localSearch.trim()) {
      notify('Vui lòng nhập từ khóa tìm kiếm (UC-11).');
      return;
    }
    onSearchSubmit(localSearch.trim());
    setMobileMenuOpen(false);
  };

  return (
    <header
      ref={headerRef}
      className="sticky top-[44px] z-30 pt-2 pb-2 transition-all duration-300"
    >
      {/* FULL-BLEED WIDESCREEN CONTAINER */}
      <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 space-y-2">
        {/* Static Contact Micro-Bar (UC-09 AC-4 — NO horizontal marquee/scroll) */}
        <div
          className={`flex flex-wrap items-center justify-between gap-3 px-2 text-[11.5px] text-[#5E6658] transition-all duration-300 ${
            scrolled ? 'hidden sm:flex py-0.5 opacity-95' : 'py-1'
          }`}
        >
          <div className="flex flex-wrap items-center gap-3.5">
            <a
              href={`tel:${STORE_CONFIG.hotlineRaw}`}
              className="inline-flex items-center gap-1.5 hover:text-[#22261E] transition-colors"
            >
              <Phone className="w-3.5 h-3.5 text-[#4A5D43]" />
              <span>
                Hotline:{' '}
                <strong className="font-semibold text-[#22261E]">
                  {STORE_CONFIG.hotline}
                </strong>
              </span>
            </a>
            <span className="text-[#D4CBB8]">•</span>
            <a
              href={STORE_CONFIG.zaloUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 hover:text-[#4A5D43] transition-colors font-medium"
            >
              <MessageCircle className="w-3.5 h-3.5 text-[#4A5D43]" />
              <span>Zalo cửa hàng</span>
            </a>
            <span className="hidden xl:inline text-[#D4CBB8]">•</span>
            <span className="hidden xl:inline text-[#5E6658]">
              Giao hàng đồng giá <strong className="text-[#22261E]">12.000₫</strong> toàn quốc
            </span>
          </div>

          <div className="hidden md:flex flex-wrap items-center gap-5">
            <button
              type="button"
              onClick={() => onOpenInfo('about')}
              className="hover:text-[#22261E] transition-colors cursor-pointer"
            >
              Giới thiệu
            </button>
            <button
              type="button"
              onClick={() => onOpenInfo('policy')}
              className="hover:text-[#22261E] transition-colors cursor-pointer"
            >
              Chính sách
            </button>
            <button
              type="button"
              onClick={() => onOpenInfo('faq')}
              className="hover:text-[#22261E] transition-colors cursor-pointer"
            >
              FAQ
            </button>
          </div>
        </div>

        {/* Full-Bleed Sea-Salt Cream Architectural Bar */}
        <div
          className={`rounded-2xl transition-all duration-300 px-4 sm:px-6 py-2.5 ${
            scrolled
              ? 'bg-[#FFFDF9]/96 backdrop-blur-xl border border-[#D4CBB8] shadow-[0_12px_34px_-16px_rgba(34,38,30,0.14)]'
              : 'bg-[#FFFDF9]/92 backdrop-blur-md border border-[#E4DDD0] shadow-[0_6px_22px_-14px_rgba(34,38,30,0.08)]'
          }`}
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 -ml-2 rounded-xl text-[#22261E] hover:bg-[#F3EFE6] cursor-pointer"
                aria-label="Menu"
              >
                {mobileMenuOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>

              {/* Brand Wordmark */}
              <button
                type="button"
                onClick={() => onNavigate('home')}
                className="text-left shrink-0 cursor-pointer group"
              >
                <span className="block font-editorial text-2xl sm:text-[28px] font-semibold tracking-[0.16em] text-[#22261E] group-hover:text-[#4A5D43] transition-colors leading-none">
                  SOBIE
                </span>
                <span className="block text-[9.5px] tracking-[0.24em] uppercase text-[#878E80] mt-1 font-medium">
                  Sea-Salt & Olive
                </span>
              </button>
            </div>

            {/* Category Navigation — ALL VISIBLE WITH FLEX-WRAP, ZERO HORIZONTAL SCROLL! */}
            <nav className="hidden lg:flex flex-wrap items-center gap-1.5 flex-1 justify-center px-2">
              <button
                type="button"
                onClick={() => onNavigate('home')}
                className={`px-3.5 py-2 rounded-full text-[13px] transition-all cursor-pointer ${
                  currentRoute === 'home'
                    ? 'bg-[#4A5D43] text-white font-semibold shadow-2xs'
                    : 'text-[#5E6658] hover:text-[#22261E] hover:bg-[#F3EFE6]'
                }`}
              >
                Trang chủ
              </button>
              <button
                type="button"
                onClick={() => onSelectCategory('')}
                className={`px-3.5 py-2 rounded-full text-[13px] transition-all cursor-pointer ${
                  currentRoute === 'catalog' && activeCategory === ''
                    ? 'bg-[#4A5D43] text-white font-semibold shadow-2xs'
                    : 'text-[#5E6658] hover:text-[#22261E] hover:bg-[#F3EFE6]'
                }`}
              >
                Tất cả sản phẩm
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => onSelectCategory(cat)}
                  className={`px-3.5 py-2 rounded-full text-[13px] transition-all cursor-pointer ${
                    currentRoute === 'catalog' && activeCategory === cat
                      ? 'bg-[#4A5D43] text-white font-semibold shadow-2xs'
                      : 'text-[#5E6658] hover:text-[#22261E] hover:bg-[#F3EFE6]'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </nav>

            {/* Right Search + Actions */}
            <div className="flex items-center gap-2 shrink-0">
              <form
                onSubmit={handleFormSubmit}
                className="hidden md:flex items-center relative w-52 xl:w-72"
              >
                <Search className="w-3.5 h-3.5 text-[#878E80] absolute left-3.5 pointer-events-none" />
                <input
                  type="text"
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                  placeholder="Tìm tên, mô tả sản phẩm..."
                  className="w-full pl-9 pr-3.5 py-2 rounded-full bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] placeholder:text-[#878E80] focus:outline-none focus:bg-white focus:border-[#4A5D43] transition-colors"
                />
              </form>

              {/* Wishlist (UC-38) */}
              <button
                type="button"
                onClick={() => {
                  if (!storefrontUser) {
                    onNavigate('login');
                  } else {
                    onNavigate('wishlist');
                  }
                }}
                className="relative p-2.5 rounded-full text-[#22261E] hover:bg-[#F3EFE6] transition-colors cursor-pointer"
                title="Danh sách yêu thích (UC-38)"
              >
                <Heart className="w-[18px] h-[18px] stroke-[1.75]" />
                {storefrontUser && wishlistCount > 0 && (
                  <span
                    ref={wishBadgeRef}
                    className="absolute top-1 right-1 min-w-[16px] h-[16px] px-1 rounded-full bg-[#A84A3B] text-white text-[10px] font-semibold flex items-center justify-center"
                  >
                    {wishlistCount}
                  </span>
                )}
              </button>

              {/* Customer Account Menu */}
              <div className="relative">
                {storefrontUser ? (
                  <>
                    <button
                      type="button"
                      onClick={() => setAccountDropdownOpen((v) => !v)}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-[#F3EFE6] hover:bg-[#E5ECE0] border border-[#E4DDD0] text-xs font-medium text-[#22261E] transition-colors cursor-pointer"
                    >
                      <User className="w-3.5 h-3.5 text-[#4A5D43]" />
                      <span className="hidden sm:inline max-w-[120px] truncate">
                        {storefrontUser.name || storefrontUser.email}
                      </span>
                      <ChevronDown className="w-3 h-3 text-[#878E80] hidden sm:inline" />
                    </button>

                    {accountDropdownOpen && (
                      <div
                        onMouseLeave={() => setAccountDropdownOpen(false)}
                        className="absolute right-0 mt-2.5 w-64 rounded-2xl bg-[#FFFDF9] border border-[#E4DDD0] shadow-xl py-2 z-50 text-xs"
                      >
                        <div className="px-4 py-2.5 border-b border-[#E4DDD0]">
                          <p className="font-semibold text-[#22261E] truncate">
                            {storefrontUser.name || 'Khách hàng mới (Chưa cập nhật tên)'}
                          </p>
                          <p className="text-[11px] text-[#878E80] font-mono mt-0.5">
                            {storefrontUser.accountId}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setAccountDropdownOpen(false);
                            onNavigate('profile');
                          }}
                          className="w-full px-4 py-2.5 text-left text-[#3E4539] hover:bg-[#F3EFE6] flex items-center gap-2 cursor-pointer"
                        >
                          <User className="w-3.5 h-3.5 text-[#4A5D43]" />
                          <span>Hồ sơ & Đổi mật khẩu (UC-04/05)</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setAccountDropdownOpen(false);
                            onNavigate('orders');
                          }}
                          className="w-full px-4 py-2.5 text-left text-[#3E4539] hover:bg-[#F3EFE6] flex items-center gap-2 cursor-pointer"
                        >
                          <PackageCheck className="w-3.5 h-3.5 text-[#4A5D43]" />
                          <span>Đơn hàng của tôi (UC-21)</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setAccountDropdownOpen(false);
                            logoutStorefront();
                            onNavigate('home');
                          }}
                          className="w-full px-4 py-2.5 text-left text-[#8E3B2E] hover:bg-[#FBECE9] flex items-center gap-2 border-t border-[#E4DDD0] mt-1 cursor-pointer"
                        >
                          <LogOut className="w-3.5 h-3.5" />
                          <span>Đăng xuất (UC-03)</span>
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => onNavigate('login')}
                      className="px-3.5 py-2 rounded-full text-xs font-semibold text-[#22261E] hover:bg-[#F3EFE6] transition-colors cursor-pointer"
                    >
                      Đăng nhập
                    </button>
                    <button
                      type="button"
                      onClick={() => onNavigate('register')}
                      className="hidden sm:inline-flex px-3.5 py-2 rounded-full border border-[#C5D1BE] bg-[#E5ECE0] text-xs font-semibold text-[#3B4B35] hover:bg-[#4A5D43] hover:text-white transition-colors cursor-pointer"
                    >
                      Đăng ký OTP
                    </button>
                  </div>
                )}
              </div>

              {/* Olive Green Cart Pill Button (Opens Grand Temporary Cart Drawer) */}
              <button
                type="button"
                onClick={onOpenCartDrawer}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#4A5D43] text-white hover:bg-[#3B4B35] transition-colors shadow-2xs cursor-pointer"
              >
                <ShoppingBag className="w-4 h-4 stroke-[1.75]" />
                <span className="text-xs font-semibold hidden sm:inline">
                  Giỏ tạm
                </span>
                <span
                  ref={cartBadgeRef}
                  className="min-w-[20px] h-[20px] px-1 rounded-full bg-[#FAF7F2] text-[#22261E] text-[11px] font-bold flex items-center justify-center tabular-price"
                >
                  {cartCount}
                </span>
              </button>
            </div>
          </div>

          {/* Mobile Drawer */}
          {mobileMenuOpen && (
            <div className="lg:hidden border-t border-[#E4DDD0] mt-3 pt-4 space-y-3">
              <form onSubmit={handleFormSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                  placeholder="Tìm kiếm sản phẩm..."
                  className="flex-1 px-4 py-2 rounded-full bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E]"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-full bg-[#4A5D43] text-white text-xs font-semibold"
                >
                  Tìm
                </button>
              </form>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    onNavigate('home');
                    setMobileMenuOpen(false);
                  }}
                  className="px-3.5 py-2 rounded-full bg-[#F3EFE6] text-xs font-semibold text-[#22261E]"
                >
                  Trang chủ
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onSelectCategory('');
                    setMobileMenuOpen(false);
                  }}
                  className="px-3.5 py-2 rounded-full bg-[#F3EFE6] text-xs font-medium text-[#5E6658]"
                >
                  Tất cả sản phẩm
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => {
                      onSelectCategory(cat);
                      setMobileMenuOpen(false);
                    }}
                    className="px-3.5 py-2 rounded-full bg-[#F3EFE6] text-xs font-medium text-[#5E6658]"
                  >
                    {cat}
                  </button>
                ))}
              </div>
              <div className="pt-2 flex flex-wrap items-center gap-4 text-xs text-[#4A5D43] font-medium">
                <button
                  type="button"
                  onClick={() => {
                    onOpenInfo('about');
                    setMobileMenuOpen(false);
                  }}
                >
                  Giới thiệu
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onOpenInfo('policy');
                    setMobileMenuOpen(false);
                  }}
                >
                  Chính sách
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onOpenInfo('faq');
                    setMobileMenuOpen(false);
                  }}
                >
                  FAQ
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
