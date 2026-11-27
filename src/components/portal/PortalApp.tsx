import React, { useEffect, useRef, useState } from 'react';
import {
  BarChart3,
  ShoppingCart,
  Truck,
  Percent,
  Layers,
  Tag,
  Warehouse,
  FileText,
  Users,
  KeyRound,
  LogOut,
  ShieldCheck,
  Briefcase,
} from 'lucide-react';
import { gsap, useGSAP } from '../../lib/gsap';
import { useSobieSystem } from '../../context/SobieSystemContext';
import { AdminSection, AppSurface, SalerSection } from '../../types/store';
import { PortalLoginPage } from '../auth/RoleLoginPages';
import {
  AdminAccountsView,
  InternalPasswordView,
  SalerCustomersView,
} from './PortalAuthAndAdmin';
import {
  EmployeeCatalogView,
  EmployeeDashboardView,
  EmployeeTaxonomyView,
} from './EmployeeDashboardAndCatalog';
import {
  EmployeeHandoffView,
  EmployeeInventoryView,
  EmployeeInvoicesView,
  EmployeeOrdersView,
  EmployeePromotionsView,
} from './EmployeeOperationsViews';

/* ============================================================================
 * UNIFIED INTERNAL MANAGEMENT PORTAL SHELL (Admin & Saler — UC-02 AC-3 & RBAC)
 * - Unauthenticated -> Unified /admin/login (`PortalLoginPage`)
 * - Role `employee` (Saler) -> Lands on Overview Dashboard (`UC-37`) + 10 operational tabs
 * - Role `admin` (Admin) -> Lands on Account Governance Overview (`UC-06→08`) + Password (`UC-05`)
 * ============================================================================ */
export const PortalWorkspaceApp: React.FC<{
  onSwitchSurface: (s: AppSurface) => void;
}> = ({ onSwitchSurface }) => {
  const { portalUser, logoutPortal } = useSobieSystem();
  const [salerSection, setSalerSection] = useState<SalerSection>('dashboard');
  const [adminSection, setAdminSection] = useState<AdminSection>('accounts');
  const bodyRef = useRef<HTMLDivElement>(null);

  // UC-02 AC-3: Whenever a new internal session is established, land on that role's Overview tab!
  useEffect(() => {
    if (!portalUser) return;
    if (portalUser.role === 'employee') {
      setSalerSection('dashboard');
    } else if (portalUser.role === 'admin') {
      setAdminSection('accounts');
    }
  }, [portalUser?.accountId, portalUser?.role]);

  useGSAP(
    () => {
      if (!portalUser || !bodyRef.current) return;
      gsap.fromTo(
        bodyRef.current,
        { autoAlpha: 0.45, y: 10 },
        { autoAlpha: 1, y: 0, duration: 0.32, ease: 'power2.out', clearProps: 'transform' }
      );
    },
    {
      dependencies: [portalUser?.accountId, salerSection, adminSection],
      scope: bodyRef,
    }
  );

  if (!portalUser) {
    return <PortalLoginPage onSwitchSurface={onSwitchSurface} />;
  }

  const isAdmin = portalUser.role === 'admin';

  const salerMenu: {
    id: SalerSection;
    label: string;
    routeHint: string;
    icon: React.ReactNode;
  }[] = [
    {
      id: 'dashboard',
      label: 'Tổng quan · Dashboard (UC-37)',
      routeHint: '/admin/dashboard',
      icon: <BarChart3 className="w-3.5 h-3.5" />,
    },
    {
      id: 'orders',
      label: 'Đơn hàng (UC-22→25)',
      routeHint: '/admin/orders',
      icon: <ShoppingCart className="w-3.5 h-3.5" />,
    },
    {
      id: 'handoff',
      label: 'Bàn giao ship (UC-40)',
      routeHint: '/admin/shipping-handoff',
      icon: <Truck className="w-3.5 h-3.5" />,
    },
    {
      id: 'promotions',
      label: 'Khuyến mãi & Quote (UC-28→31)',
      routeHint: '/admin/promotions',
      icon: <Percent className="w-3.5 h-3.5" />,
    },
    {
      id: 'products',
      label: 'Sản phẩm & Giá size (UC-14→16)',
      routeHint: '/admin/products',
      icon: <Layers className="w-3.5 h-3.5" />,
    },
    {
      id: 'taxonomy',
      label: 'Danh mục & Thuộc tính (UC-17)',
      routeHint: '/admin/taxonomy',
      icon: <Tag className="w-3.5 h-3.5" />,
    },
    {
      id: 'stock',
      label: 'Kho, NCC & Phiếu nhập (UC-32→39)',
      routeHint: '/admin/inventory',
      icon: <Warehouse className="w-3.5 h-3.5" />,
    },
    {
      id: 'customers',
      label: 'Quản lý khách hàng (UC-07/08)',
      routeHint: '/admin/customers',
      icon: <Users className="w-3.5 h-3.5" />,
    },
    {
      id: 'invoices',
      label: 'Hóa đơn (UC-27)',
      routeHint: '/admin/invoices',
      icon: <FileText className="w-3.5 h-3.5" />,
    },
    {
      id: 'password',
      label: 'Đổi mật khẩu (UC-05)',
      routeHint: '/admin/password',
      icon: <KeyRound className="w-3.5 h-3.5" />,
    },
  ];

  const activeRouteHint = isAdmin
    ? adminSection === 'accounts'
      ? '/admin/accounts'
      : '/admin/password'
    : salerMenu.find((n) => n.id === salerSection)?.routeHint ?? '/admin/dashboard';

  return (
    <div className="min-h-[calc(100vh-44px)] bg-[#FAF7F2] flex flex-col">
      {/* FULL-BLEED UNIFIED PORTAL HEADER — ALL BUTTONS WRAPPED & VISIBLE AT ONCE! */}
      <header className="sticky top-[44px] z-30 bg-[#FFFDF9]/95 backdrop-blur-xl border-b border-[#E4DDD0] shadow-[0_8px_28px_-18px_rgba(34,38,30,0.09)]">
        <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16">
          <div className="py-3.5 flex flex-wrap items-center justify-between gap-4 border-b border-[#F3EFE6]">
            <div className="flex items-center gap-3.5">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  isAdmin
                    ? 'bg-[#22261E] text-[#FAF7F2]'
                    : 'bg-[#4A5D43] text-white'
                }`}
              >
                {isAdmin ? (
                  <ShieldCheck className="w-4 h-4 text-[#C5D1BE]" />
                ) : (
                  <Briefcase className="w-4 h-4" />
                )}
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-editorial text-2xl font-semibold tracking-[0.08em] text-[#22261E]">
                    SOBIE INTERNAL PORTAL
                  </span>
                  <span className="px-2.5 py-0.5 rounded-md bg-[#E5ECE0] border border-[#C5D1BE] font-mono text-[10.5px] text-[#3B4B35] font-semibold">
                    {activeRouteHint}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-md bg-[#F3EFE6] border border-[#E4DDD0] text-[10.5px] text-[#5E6658]">
                    `portal_session` · 60 phút
                  </span>
                </div>
                <p className="text-[11.5px] text-[#5E6658]">
                  {isAdmin
                    ? 'Phiên Quản trị viên (Admin): Chỉ quản lý tài khoản & phân quyền — tách biệt khỏi tác nghiệp bán hàng theo UC-02'
                    : 'Phiên Nhân viên (Saler): Toàn quyền điều hành cửa hàng, đơn hàng, sản phẩm, kho, khuyến mãi & khóa khách hàng'}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-[#FAF7F2] border border-[#E4DDD0] text-xs">
                <span className="font-semibold text-[#22261E]">
                  {portalUser.name}
                </span>
                <span className="hidden sm:inline font-mono text-[11px] text-[#878E80]">
                  ({portalUser.accountId})
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isAdmin
                      ? 'bg-[#22261E] text-white'
                      : 'bg-[#E5ECE0] text-[#3B4B35]'
                  }`}
                >
                  {isAdmin ? 'Admin' : 'Saler'}
                </span>
              </div>

              <button
                type="button"
                onClick={logoutPortal}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-[#E7C2BA] bg-white text-xs font-semibold text-[#8E3B2E] hover:bg-[#FBECE9] transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Đăng xuất Portal (UC-03)</span>
              </button>
            </div>
          </div>

          {/* Role-Based Navigation Bar — All Buttons Visible via flex-wrap! */}
          {isAdmin ? (
            <nav className="py-3 flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => setAdminSection('accounts')}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs transition-all cursor-pointer ${
                  adminSection === 'accounts'
                    ? 'bg-[#4A5D43] text-white font-semibold shadow-xs'
                    : 'bg-[#FAF7F2] text-[#5E6658] border border-[#E4DDD0] hover:border-[#4A5D43]'
                }`}
              >
                <Users className="w-3.5 h-3.5" />
                <span>Tổng quan · Quản lý tài khoản & Vai trò (UC-06 / UC-07 / UC-08)</span>
              </button>
              <button
                type="button"
                onClick={() => setAdminSection('password')}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs transition-all cursor-pointer ${
                  adminSection === 'password'
                    ? 'bg-[#4A5D43] text-white font-semibold shadow-xs'
                    : 'bg-[#FAF7F2] text-[#5E6658] border border-[#E4DDD0] hover:border-[#4A5D43]'
                }`}
              >
                <KeyRound className="w-3.5 h-3.5" />
                <span>Đổi mật khẩu cá nhân (UC-05)</span>
              </button>
            </nav>
          ) : (
            <nav className="py-3 flex flex-wrap items-center gap-2">
              {salerMenu.map((item) => {
                const active = salerSection === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSalerSection(item.id)}
                    className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-full text-xs transition-all cursor-pointer ${
                      active
                        ? 'bg-[#4A5D43] text-white font-semibold shadow-xs'
                        : 'bg-[#FAF7F2] text-[#5E6658] border border-[#E4DDD0] hover:border-[#4A5D43] hover:text-[#22261E]'
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          )}
        </div>
      </header>

      {/* Full-Bleed Portal Workspace Body */}
      <div
        ref={bodyRef}
        className="flex-1 w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-7 sm:py-9"
      >
        {isAdmin ? (
          adminSection === 'accounts' ? (
            <AdminAccountsView />
          ) : (
            <InternalPasswordView />
          )
        ) : (
          <>
            {salerSection === 'dashboard' && <EmployeeDashboardView />}
            {salerSection === 'orders' && <EmployeeOrdersView />}
            {salerSection === 'handoff' && <EmployeeHandoffView />}
            {salerSection === 'promotions' && <EmployeePromotionsView />}
            {salerSection === 'products' && <EmployeeCatalogView />}
            {salerSection === 'taxonomy' && <EmployeeTaxonomyView />}
            {salerSection === 'stock' && <EmployeeInventoryView />}
            {salerSection === 'customers' && <SalerCustomersView />}
            {salerSection === 'invoices' && <EmployeeInvoicesView />}
            {salerSection === 'password' && <InternalPasswordView />}
          </>
        )}
      </div>
    </div>
  );
};
