import React, { useRef, useState } from 'react';
import {
  Store,
  ShieldCheck,
  Truck,
  CheckCircle2,
} from 'lucide-react';
import { gsap, ScrollTrigger, useGSAP } from './lib/gsap';
import {
  SobieSystemProvider,
  useSobieSystem,
} from './context/SobieSystemContext';
import {
  AppSurface,
  CatalogFilters,
  InfoTab,
  StorefrontRoute,
} from './types/store';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { HomePage } from './components/HomePage';
import { CatalogPage } from './components/CatalogPage';
import { ProductDetailPage } from './components/ProductDetailPage';
import { CartDrawer, CartPage } from './components/CartAndCheckout';
import {
  CustomerProfilePage,
  InfoPage,
  OrdersPage,
  SizeGuideModal,
  WishlistPage,
} from './components/SecondaryViews';
import { UserAuthPage } from './components/auth/RoleLoginPages';
import { PortalWorkspaceApp } from './components/portal/PortalApp';
import { ShippingSimulatorApp } from './components/shipping/ShippingSimulatorApp';

const DEFAULT_FILTERS: CatalogFilters = {
  category: '',
  gender: '',
  size: '',
  collection: '',
  search: '',
  sort: 'newest',
  page: 1,
};

const InnerSystemShell: React.FC = () => {
  const {
    storefrontUser,
    portalUser,
    shippingSession,
    orders,
    toastMessage,
  } = useSobieSystem();

  const surfaceWrapRef = useRef<HTMLDivElement>(null);
  const toastRef = useRef<HTMLDivElement>(null);

  const [surface, setSurface] = useState<AppSurface>('storefront');
  const [route, setRoute] = useState<StorefrontRoute>('home');
  const [returnAfterLogin, setReturnAfterLogin] =
    useState<StorefrontRoute>('home');
  const [selectedProductId, setSelectedProductId] = useState<string>('SP-0003');
  const [infoTab, setInfoTab] = useState<InfoTab>('about');
  const [filters, setFilters] = useState<CatalogFilters>(DEFAULT_FILTERS);

  const [cartDrawerOpen, setCartDrawerOpen] = useState(false);
  const [sizeGuideOpen, setSizeGuideOpen] = useState(false);

  const pendingSalerCount = orders.filter((o) =>
    ['PENDING', 'CONFIRMED'].includes(o.status)
  ).length;
  const activeCarrierCount = orders.filter((o) =>
    ['AWAITING_PICKUP', 'SHIPPING'].includes(o.status)
  ).length;

  useGSAP(
    () => {
      window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
      if (surfaceWrapRef.current) {
        gsap.fromTo(
          surfaceWrapRef.current,
          { autoAlpha: 0.45, y: 8 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.35,
            ease: 'power2.out',
            clearProps: 'transform',
            onComplete: () => {
              ScrollTrigger.refresh();
            },
          }
        );
      }
    },
    { dependencies: [surface, route, selectedProductId] }
  );

  useGSAP(
    () => {
      if (!toastMessage || !toastRef.current) return;
      gsap.fromTo(
        toastRef.current,
        { y: 18, autoAlpha: 0 },
        { y: 0, autoAlpha: 1, duration: 0.3, ease: 'power3.out' }
      );
    },
    { dependencies: [toastMessage] }
  );

  const navigateCategory = (category: string) => {
    setFilters({ ...DEFAULT_FILTERS, category });
    setRoute('catalog');
  };

  const navigateCollection = (collection: string) => {
    setFilters({ ...DEFAULT_FILTERS, collection });
    setRoute('catalog');
  };

  const handleSearch = (search: string) => {
    setFilters({ ...DEFAULT_FILTERS, search });
    setRoute('catalog');
  };

  // UC-02 v12: Safe return_url contract ONLY for Checkout ('cart') & Product Detail ('product')!
  const requireStorefrontLogin = (returnTo?: StorefrontRoute) => {
    const allowedReturn: StorefrontRoute =
      returnTo === 'cart' || returnTo === 'product' ? returnTo : 'home';
    setReturnAfterLogin(allowedReturn);
    setRoute('login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF7F2] text-[#22261E]">
      {/* FULL-BLEED 3-PORTAL SYSTEM BAR (Storefront / Unified Internal Portal / Shipping) */}
      <div className="sticky top-0 z-40 min-h-[44px] py-1.5 bg-[#22261E] text-[#FAF7F2] border-b border-[#3E4539]">
        <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="hidden xl:flex items-center gap-2 text-[11px] text-[#D4CBB8]">
            <span className="w-2 h-2 rounded-full bg-[#8AB07D]" />
            <span>
              SOBIE SYSTEM · Kem Muối Biển & Xanh Ô-Liu (Chuẩn 3 Cổng Đặc Tả UC):
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {/* 1. USER (STOREFRONT) */}
            <button
              type="button"
              onClick={() => setSurface('storefront')}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11.5px] transition-colors cursor-pointer ${
                surface === 'storefront'
                  ? 'bg-[#FAF7F2] text-[#22261E] font-semibold shadow-2xs'
                  : 'text-[#D4CBB8] hover:text-white hover:bg-white/10'
              }`}
            >
              <Store className="w-3.5 h-3.5" />
              <span>1. Storefront (Khách hàng)</span>
              <span className="px-1.5 py-0.2 rounded-full bg-[#4A5D43] text-white text-[10px]">
                {storefrontUser ? 'Đã đăng nhập' : 'Vãng lai / Login'}
              </span>
            </button>

            {/* 2. UNIFIED INTERNAL PORTAL (ADMIN & SALER — UC-02) */}
            <button
              type="button"
              onClick={() => setSurface('portal')}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11.5px] transition-colors cursor-pointer ${
                surface === 'portal'
                  ? 'bg-[#FAF7F2] text-[#22261E] font-semibold shadow-2xs'
                  : 'text-[#D4CBB8] hover:text-white hover:bg-white/10'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>2. Portal Quản trị (Admin / Saler)</span>
              <span className="px-1.5 py-0.2 rounded-full bg-[#4A5D43] text-white text-[10px]">
                {portalUser
                  ? portalUser.role === 'admin'
                    ? 'Đang trực: Admin'
                    : `Saler · ${pendingSalerCount} đơn chờ`
                  : `/admin/login · ${pendingSalerCount} đơn`}
              </span>
            </button>

            {/* 3. SHIPPING */}
            <button
              type="button"
              onClick={() => setSurface('shipping')}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11.5px] transition-colors cursor-pointer ${
                surface === 'shipping'
                  ? 'bg-[#FAF7F2] text-[#22261E] font-semibold shadow-2xs'
                  : 'text-[#D4CBB8] hover:text-white hover:bg-white/10'
              }`}
            >
              <Truck className="w-3.5 h-3.5" />
              <span>3. Shipping Simulator (:8001)</span>
              <span className="px-1.5 py-0.2 rounded-full bg-[#A84A3B] text-white text-[10px]">
                {shippingSession
                  ? `${activeCarrierCount} vận đơn`
                  : `UC-36 · ${activeCarrierCount} đơn`}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Active Surface Body */}
      <div ref={surfaceWrapRef} className="flex-1 flex flex-col">
        {surface === 'storefront' && (
          <>
            <Header
              currentRoute={route}
              activeCategory={filters.category}
              searchQuery={filters.search}
              onNavigate={(nextRoute) => {
                // UC-01 AC-5: Logged-in customer visiting register is redirected to home
                if (nextRoute === 'register' && storefrontUser) {
                  setRoute('home');
                  return;
                }
                if (nextRoute === 'login') {
                  setReturnAfterLogin('home');
                }
                setRoute(nextRoute);
              }}
              onSelectCategory={navigateCategory}
              onSearchSubmit={handleSearch}
              onOpenCartDrawer={() => setCartDrawerOpen(true)}
              onOpenInfo={(tab) => {
                setInfoTab(tab);
                setRoute('info');
              }}
            />

            <main className="flex-1">
              {route === 'home' && (
                <HomePage
                  onSelectProduct={(id) => {
                    setSelectedProductId(id);
                    setRoute('product');
                  }}
                  onSelectCategory={navigateCategory}
                  onSelectCollection={navigateCollection}
                  onRequireLogin={() => requireStorefrontLogin('home')}
                />
              )}

              {route === 'catalog' && (
                <CatalogPage
                  filters={filters}
                  onUpdateFilters={(patch) =>
                    setFilters((prev) => ({ ...prev, ...patch }))
                  }
                  onResetFilters={() => setFilters(DEFAULT_FILTERS)}
                  onSelectProduct={(id) => {
                    setSelectedProductId(id);
                    setRoute('product');
                  }}
                  onRequireLogin={() => requireStorefrontLogin('home')}
                />
              )}

              {route === 'product' && (
                <ProductDetailPage
                  productId={selectedProductId}
                  onBack={() => setRoute('catalog')}
                  onSelectCategory={navigateCategory}
                  onSelectProduct={(id) => setSelectedProductId(id)}
                  onOpenSizeGuide={() => setSizeGuideOpen(true)}
                  onOpenCartDrawer={() => setCartDrawerOpen(true)}
                  onRequireLogin={() => requireStorefrontLogin('product')}
                />
              )}

              {route === 'cart' && (
                <CartPage
                  onSelectProduct={(id) => {
                    setSelectedProductId(id);
                    setRoute('product');
                  }}
                  onRequireLogin={() => requireStorefrontLogin('cart')}
                  onOrderCompleted={() => setRoute('orders')}
                  onContinueShopping={() => navigateCategory('')}
                />
              )}

              {route === 'wishlist' &&
                (storefrontUser ? (
                  <WishlistPage
                    onSelectProduct={(id) => {
                      setSelectedProductId(id);
                      setRoute('product');
                    }}
                    onExploreCatalog={() => navigateCategory('')}
                    onRequireLogin={() => requireStorefrontLogin('home')}
                  />
                ) : (
                  <UserAuthPage
                    initialMode="login"
                    onSuccessLogin={() => setRoute('wishlist')}
                    onSwitchMode={(m) => setRoute(m)}
                    onSwitchSurface={setSurface}
                  />
                ))}

              {route === 'orders' &&
                (storefrontUser ? (
                  <OrdersPage />
                ) : (
                  <UserAuthPage
                    initialMode="login"
                    onSuccessLogin={() => setRoute('orders')}
                    onSwitchMode={(m) => setRoute(m)}
                    onSwitchSurface={setSurface}
                  />
                ))}

              {route === 'profile' &&
                (storefrontUser ? (
                  <CustomerProfilePage
                    onLoggedOutAfterPasswordChange={() => setRoute('login')}
                  />
                ) : (
                  <UserAuthPage
                    initialMode="login"
                    onSuccessLogin={() => setRoute('profile')}
                    onSwitchMode={(m) => setRoute(m)}
                    onSwitchSurface={setSurface}
                  />
                ))}

              {(route === 'login' || route === 'register') && (
                <UserAuthPage
                  initialMode={route}
                  returnUrlLabel={
                    returnAfterLogin === 'cart'
                      ? '/checkout (Trang đặt hàng)'
                      : returnAfterLogin === 'product'
                      ? `/products/${selectedProductId} (Trang chi tiết SP)`
                      : undefined
                  }
                  onSuccessLogin={() => setRoute(returnAfterLogin)}
                  onSwitchMode={(m) => setRoute(m)}
                  onSwitchSurface={setSurface}
                />
              )}

              {route === 'info' && (
                <InfoPage activeTab={infoTab} onChangeTab={setInfoTab} />
              )}
            </main>

            <Footer
              onSelectCategory={navigateCategory}
              onOpenInfo={(tab) => {
                setInfoTab(tab);
                setRoute('info');
              }}
              onOpenSizeGuide={() => setSizeGuideOpen(true)}
            />

            <CartDrawer
              isOpen={cartDrawerOpen}
              onClose={() => setCartDrawerOpen(false)}
              onGoToFullCart={() => setRoute('cart')}
              onSelectProduct={(id) => {
                setSelectedProductId(id);
                setRoute('product');
              }}
            />

            <SizeGuideModal
              isOpen={sizeGuideOpen}
              onClose={() => setSizeGuideOpen(false)}
            />
          </>
        )}

        {surface === 'portal' && (
          <PortalWorkspaceApp onSwitchSurface={setSurface} />
        )}

        {surface === 'shipping' && (
          <ShippingSimulatorApp onSwitchSurface={setSurface} />
        )}
      </div>

      {/* Global Toast Notification */}
      {toastMessage && (
        <div
          ref={toastRef}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-[#22261E]/95 backdrop-blur-md border border-[#4A5D43] text-[#FAF7F2] text-xs font-medium shadow-xl max-w-md"
        >
          <CheckCircle2 className="w-4 h-4 text-[#8AB07D] shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
};

export const App: React.FC = () => (
  <SobieSystemProvider>
    <InnerSystemShell />
  </SobieSystemProvider>
);

export default App;
