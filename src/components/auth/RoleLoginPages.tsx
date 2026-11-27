import React, { useEffect, useRef, useState } from 'react';
import {
  ShieldCheck,
  Store,
  Briefcase,
  Truck,
  Mail,
  KeyRound,
  CheckCircle2,
  ArrowRight,
  Clock,
  Sparkles,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { gsap, useGSAP } from '../../lib/gsap';
import { STORE_CONFIG } from '../../data/seedData';
import { useSobieSystem } from '../../context/SobieSystemContext';
import { AppSurface } from '../../types/store';

/* ============================================================================
 * SHARED PORTAL DIRECTORY STRIP (3 UC-Aligned Portals — All visible, NO scroll!)
 * ============================================================================ */
const RolePortalDirectoryStrip: React.FC<{
  activeSurface: AppSurface;
  onSelectSurface: (s: AppSurface) => void;
}> = ({ activeSurface, onSelectSurface }) => {
  const portals: {
    id: AppSurface;
    title: string;
    subtitle: string;
    icon: React.ReactNode;
  }[] = [
    {
      id: 'storefront',
      title: '1. Cổng Khách hàng (Storefront)',
      subtitle: 'Đăng nhập, Email OTP & Google · UC-01/02',
      icon: <Store className="w-4 h-4" />,
    },
    {
      id: 'portal',
      title: '2. Portal Nội bộ (Admin & Saler)',
      subtitle: 'Cổng chung /admin/login · Tự định tuyến theo vai trò (UC-02 AC-3)',
      icon: <ShieldCheck className="w-4 h-4" />,
    },
    {
      id: 'shipping',
      title: '3. Đơn vị Vận chuyển (Shipping)',
      subtitle: 'Điều phối độc lập shipping:8001 · UC-36',
      icon: <Truck className="w-4 h-4" />,
    },
  ];

  return (
    <div className="space-y-2">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#5E6658]">
        Kiến trúc 3 cổng truy cập chuẩn đặc tả Use Case
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {portals.map((p) => {
          const active = p.id === activeSurface;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelectSurface(p.id)}
              className={`p-3.5 rounded-2xl border text-left transition-all cursor-pointer flex items-start gap-3 ${
                active
                  ? 'bg-[#4A5D43] text-[#FAF7F2] border-[#4A5D43] shadow-sm'
                  : 'bg-[#FAF7F2] text-[#22261E] border-[#E4DDD0] hover:border-[#4A5D43]/60 hover:bg-[#F3EFE6]'
              }`}
            >
              <span
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  active
                    ? 'bg-white/15 text-white'
                    : 'bg-[#E5ECE0] text-[#4A5D43]'
                }`}
              >
                {p.icon}
              </span>
              <span className="min-w-0">
                <span className="block text-xs font-semibold leading-snug">
                  {p.title}
                </span>
                <span
                  className={`block text-[11px] mt-0.5 leading-snug ${
                    active ? 'text-[#E5ECE0]' : 'text-[#5E6658]'
                  }`}
                >
                  {p.subtitle}
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

/* ============================================================================
 * 1. USER (CUSTOMER) FULL-BLEED LOGIN & EMAIL OTP / GOOGLE REGISTER (UC-01, UC-02)
 * ============================================================================ */
export const UserAuthPage: React.FC<{
  initialMode: 'login' | 'register';
  returnUrlLabel?: string;
  onSuccessLogin: () => void;
  onSwitchMode: (mode: 'login' | 'register') => void;
  onSwitchSurface: (s: AppSurface) => void;
}> = ({
  initialMode,
  returnUrlLabel,
  onSuccessLogin,
  onSwitchMode,
  onSwitchSurface,
}) => {
  const {
    guestCart,
    otpChallenge,
    requestRegisterOtp,
    resendRegisterOtp,
    verifyRegisterOtp,
    completeOtpRegistration,
    resetOtpFlow,
    loginStorefront,
    loginOrRegisterWithGoogle,
  } = useSobieSystem();

  const rootRef = useRef<HTMLDivElement>(null);

  // Login state
  const [identifier, setIdentifier] = useState('khachhang@example.com');
  const [password, setPassword] = useState('Customer@Sobie2026');
  const [forgotNotice, setForgotNotice] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // OTP Registration state (UC-01 v15)
  const [regEmail, setRegEmail] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [lastDemoOtp, setLastDemoOtp] = useState<string | null>(null);
  const [remainingSeconds, setRemainingSeconds] = useState(0);

  // Google simulation modal/selector
  const [googleEmail, setGoogleEmail] = useState('linh.google@example.com');
  const [showGooglePicker, setShowGooglePicker] = useState(false);

  useEffect(() => {
    setError(null);
    setForgotNotice(false);
  }, [initialMode]);

  // UC-01 AC-18: Live 5-minute resend countdown timer
  useEffect(() => {
    if (!otpChallenge) {
      setRemainingSeconds(0);
      return;
    }
    const tick = () => {
      const diff = Math.max(
        0,
        Math.ceil((otpChallenge.resendAvailableAtMs - Date.now()) / 1000)
      );
      setRemainingSeconds(diff);
    };
    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [otpChallenge]);

  useGSAP(
    () => {
      gsap.from('.auth-reveal', {
        y: 16,
        autoAlpha: 0,
        duration: 0.5,
        stagger: 0.06,
        ease: 'power3.out',
      });
    },
    { dependencies: [initialMode], scope: rootRef }
  );

  const handlePasswordLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const res = loginStorefront(identifier, password);
    if (!res.ok) {
      setError(res.error ?? 'Thông tin đăng nhập không đúng.');
      return;
    }
    onSuccessLogin();
  };

  const handleGoogleContinue = (emailToUse: string, displayName?: string) => {
    setError(null);
    const res = loginOrRegisterWithGoogle(emailToUse, displayName);
    if (!res.ok) {
      setError(res.error ?? 'Xác thực Google không thành công.');
      return;
    }
    setShowGooglePicker(false);
    onSuccessLogin();
  };

  const formatCountdown = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const guestItemCount = guestCart.reduce((sum, i) => sum + i.quantity, 0);

  return (
    <div
      ref={rootRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-8 sm:py-12"
    >
      <div className="w-full space-y-6">
        <div className="auth-reveal p-5 rounded-3xl atelier-card">
          <RolePortalDirectoryStrip
            activeSurface="storefront"
            onSelectSurface={onSwitchSurface}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          {/* LEFT 7 COLUMNS: FULL-BLEED EDITORIAL SHOWCASE & SPEC RULES */}
          <div className="auth-reveal lg:col-span-7 rounded-3xl overflow-hidden border border-[#E4DDD0] bg-[#F3EFE6] flex flex-col justify-between relative min-h-[540px]">
            <div className="relative h-64 sm:h-80 lg:h-88 overflow-hidden">
              <img
                src="/images/hero-editorial.jpg"
                alt="Sobie Coastal Swimwear"
                className="w-full h-full object-cover object-center"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#22261E]/75 via-[#22261E]/25 to-transparent" />
              <div className="absolute bottom-6 left-6 right-6 text-[#FAF7F2] space-y-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4A5D43] text-white text-[11px] font-semibold uppercase tracking-[0.16em]">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Cổng Khách Hàng Storefront · UC-01 & UC-02</span>
                </span>
                <h2 className="font-editorial text-3xl sm:text-4xl leading-tight">
                  Trải nghiệm mua sắm đồ bơi tinh tế trên nền Kem muối biển.
                </h2>
              </div>
            </div>

            <div className="p-6 sm:p-8 space-y-5 bg-[#F3EFE6]">
              {guestItemCount > 0 && (
                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#C5D1BE] flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#4A5D43] shrink-0 mt-0.5" />
                  <div className="text-xs space-y-1">
                    <p className="font-semibold text-[#22261E]">
                      Đang lưu {guestItemCount} sản phẩm trong Giỏ tạm trình duyệt (`localStorage`)
                    </p>
                    <p className="text-[#5E6658] leading-relaxed">
                      Ngay khi bạn đăng nhập bằng mật khẩu Sobie hoặc Google, hệ thống sẽ tự động gộp giỏ tạm vào giỏ tài khoản và giới hạn an toàn theo tồn kho thực tế (UC-18 AC-6).
                    </p>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 text-xs">
                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1">
                  <p className="font-semibold text-[#22261E]">Đăng ký Email OTP</p>
                  <p className="text-[#5E6658] leading-relaxed">
                    Xác minh mã OTP 5 phút qua `notification`, đếm ngược gửi lại, khóa 429 sau 5 lần sai rồi mới tạo mật khẩu (UC-01 v15).
                  </p>
                </div>
                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1">
                  <p className="font-semibold text-[#22261E]">Google Hợp Nhất</p>
                  <p className="text-[#5E6658] leading-relaxed">
                    Tự liên kết tài khoản Khách hàng trùng email hoặc tạo mới `KH-...` và cấp phiên ngay không cần mật khẩu Sobie.
                  </p>
                </div>
                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1">
                  <p className="font-semibold text-[#22261E]">Phiên Cookie Độc Lập</p>
                  <p className="text-[#5E6658] leading-relaxed">
                    Hạn phiên 30 phút gia hạn trượt; tách biệt hoàn toàn với phiên Portal Nội bộ trên cùng trình duyệt (UC-02 AC-20).
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT 5 COLUMNS: LOGIN / OTP REGISTER FORM STUDIO */}
          <div className="auth-reveal lg:col-span-5 rounded-3xl atelier-card p-6 sm:p-9 flex flex-col justify-between space-y-6">
            <div className="space-y-5">
              {/* Mode Switcher Tabs (Visible side-by-side, no scroll) */}
              <div className="grid grid-cols-2 gap-2 p-1.5 rounded-2xl bg-[#F3EFE6] border border-[#E4DDD0]">
                <button
                  type="button"
                  onClick={() => onSwitchMode('login')}
                  className={`py-2.5 px-4 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    initialMode === 'login'
                      ? 'bg-[#4A5D43] text-white shadow-xs'
                      : 'text-[#5E6658] hover:text-[#22261E]'
                  }`}
                >
                  Đăng nhập Khách hàng (UC-02)
                </button>
                <button
                  type="button"
                  onClick={() => onSwitchMode('register')}
                  className={`py-2.5 px-4 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    initialMode === 'register'
                      ? 'bg-[#4A5D43] text-white shadow-xs'
                      : 'text-[#5E6658] hover:text-[#22261E]'
                  }`}
                >
                  Đăng ký Email OTP (UC-01)
                </button>
              </div>

              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
                  {initialMode === 'login'
                    ? 'STOREFRONT · ĐĂNG NHẬP KHÁCH HÀNG'
                    : 'STOREFRONT · ĐĂNG KÝ TÀI KHOẢN MỚI'}
                </p>
                <h1 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                  {initialMode === 'login'
                    ? 'Chào mừng trở lại Sobie'
                    : 'Xác thực Email & Tạo tài khoản'}
                </h1>
                {returnUrlLabel && (
                  <p className="text-xs text-[#4A5D43] font-medium mt-1">
                    Sau khi đăng nhập sẽ quay lại an toàn: {returnUrlLabel} (`return_url` hợp lệ · UC-02)
                  </p>
                )}
              </div>

              {error && (
                <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {forgotNotice && initialMode === 'login' && (
                <div className="px-4 py-3 rounded-2xl bg-[#F3EFE6] border border-[#D4CBB8] text-xs text-[#5E6658]">
                  Theo đặc tả UC-02 (1b / AC-10): Ở Giai đoạn 1, nút «Quên mật khẩu» hiển thị trên Storefront nhưng chưa thực hiện hành động; chức năng khôi phục mật khẩu sẽ triển khai ở Giai đoạn 2.
                </div>
              )}

              {/* UNIFIED GOOGLE BUTTON (UC-01 1b & UC-02 1c) */}
              <div className="space-y-2.5">
                <button
                  type="button"
                  onClick={() => setShowGooglePicker((v) => !v)}
                  className="w-full py-3 px-4 rounded-2xl bg-white border border-[#D4CBB8] hover:border-[#4A5D43] text-xs font-semibold text-[#22261E] flex items-center justify-center gap-2.5 transition-colors cursor-pointer shadow-2xs"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M23.745 12.27c0-.79-.07-1.54-.19-2.27h-11.3v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82Z"
                    />
                    <path
                      fill="#34A853"
                      d="M12.255 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96h-3.98v3.09C3.515 21.3 7.565 24 12.255 24Z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.525 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62h-3.98a11.86 11.86 0 0 0 0 10.76l3.98-3.09Z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12.255 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C18.205 1.19 15.495 0 12.255 0c-4.69 0-8.74 2.7-10.71 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96Z"
                    />
                  </svg>
                  <span>Đăng nhập với Google (OpenID Connect · UC-01/02)</span>
                </button>

                {showGooglePicker && (
                  <div className="p-4 rounded-2xl bg-[#F3EFE6] border border-[#D4CBB8] space-y-3 text-xs">
                    <p className="font-semibold text-[#22261E]">
                      Mô phỏng phản hồi xác thực Google OAuth 2.0:
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          handleGoogleContinue(
                            'linh.google@example.com',
                            'Trần Khánh Linh'
                          )
                        }
                        className="p-2.5 rounded-xl bg-white border border-[#E4DDD0] hover:border-[#4A5D43] text-left cursor-pointer"
                      >
                        <span className="font-semibold block text-[#22261E]">
                          linh.google@example.com
                        </span>
                        <span className="text-[11px] text-[#5E6658]">
                          TK Google mẫu (Hồ sơ trống → test UC-04 checkout)
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          handleGoogleContinue(
                            'khachhang@example.com',
                            'Khách Hàng Demo'
                          )
                        }
                        className="p-2.5 rounded-xl bg-white border border-[#E4DDD0] hover:border-[#4A5D43] text-left cursor-pointer"
                      >
                        <span className="font-semibold block text-[#22261E]">
                          khachhang@example.com
                        </span>
                        <span className="text-[11px] text-[#5E6658]">
                          Tự liên kết TK Sobie trùng email (AC-17)
                        </span>
                      </button>
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="email"
                        value={googleEmail}
                        onChange={(e) => setGoogleEmail(e.target.value)}
                        placeholder="Hoặc nhập email Google mới..."
                        className="flex-1 px-3 py-2 rounded-xl bg-white border border-[#E4DDD0]"
                      />
                      <button
                        type="button"
                        onClick={() => handleGoogleContinue(googleEmail)}
                        className="px-4 py-2 rounded-xl bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] cursor-pointer"
                      >
                        Xác nhận
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="relative flex items-center py-1">
                <div className="flex-grow border-t border-[#E4DDD0]" />
                <span className="shrink mx-3 text-[11px] uppercase tracking-wider text-[#878E80]">
                  hoặc dùng mật khẩu / OTP Sobie
                </span>
                <div className="flex-grow border-t border-[#E4DDD0]" />
              </div>

              {initialMode === 'login' ? (
                <form onSubmit={handlePasswordLogin} className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setIdentifier('khachhang@example.com');
                        setPassword('Customer@Sobie2026');
                        setError(null);
                      }}
                      className="p-2.5 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] hover:border-[#4A5D43] text-left text-xs cursor-pointer"
                    >
                      <span className="font-semibold text-[#22261E] block">
                        Điền nhanh Email KH
                      </span>
                      <span className="text-[11px] text-[#5E6658] font-mono">
                        khachhang@example.com
                      </span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setIdentifier('0900000003');
                        setPassword('Customer@Sobie2026');
                        setError(null);
                      }}
                      className="p-2.5 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] hover:border-[#4A5D43] text-left text-xs cursor-pointer"
                    >
                      <span className="font-semibold text-[#22261E] block">
                        Điền nhanh SĐT KH
                      </span>
                      <span className="text-[11px] text-[#5E6658] font-mono">
                        0900000003
                      </span>
                    </button>
                  </div>

                  <label className="block space-y-1.5 text-xs">
                    <span className="font-medium text-[#3E4539]">
                      Email hoặc Số điện thoại đã lưu
                    </span>
                    <input
                      type="text"
                      required
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder="khachhang@example.com hoặc 0900000003"
                      className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                    />
                  </label>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-[#3E4539]">
                        Mật khẩu Sobie
                      </span>
                      <button
                        type="button"
                        onClick={() => setForgotNotice(true)}
                        className="text-[11px] text-[#5E6658] hover:text-[#4A5D43] cursor-pointer"
                      >
                        Quên mật khẩu
                      </button>
                    </div>
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white text-xs sm:text-sm font-semibold hover:bg-[#3B4B35] transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                  >
                    <span>Đăng nhập Cổng Khách hàng</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </form>
              ) : (
                /* 3-STEP EMAIL OTP REGISTRATION (UC-01 v15) */
                <div className="space-y-4 text-xs">
                  <div className="grid grid-cols-3 gap-2 text-[11px]">
                    <div
                      className={`p-2 rounded-xl border text-center font-semibold ${
                        !otpChallenge
                          ? 'bg-[#E5ECE0] border-[#4A5D43] text-[#3B4B35]'
                          : 'bg-[#FAF7F2] border-[#E4DDD0] text-[#5E6658]'
                      }`}
                    >
                      1. Nhập Email
                    </div>
                    <div
                      className={`p-2 rounded-xl border text-center font-semibold ${
                        otpChallenge && !otpChallenge.verified
                          ? 'bg-[#E5ECE0] border-[#4A5D43] text-[#3B4B35]'
                          : 'bg-[#FAF7F2] border-[#E4DDD0] text-[#5E6658]'
                      }`}
                    >
                      2. Xác minh OTP
                    </div>
                    <div
                      className={`p-2 rounded-xl border text-center font-semibold ${
                        otpChallenge?.verified
                          ? 'bg-[#E5ECE0] border-[#4A5D43] text-[#3B4B35]'
                          : 'bg-[#FAF7F2] border-[#E4DDD0] text-[#5E6658]'
                      }`}
                    >
                      3. Tạo mật khẩu
                    </div>
                  </div>

                  {!otpChallenge && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        setError(null);
                        const res = requestRegisterOtp(regEmail);
                        if (!res.ok) {
                          setError(res.error ?? 'Không thể gửi OTP.');
                          return;
                        }
                        setLastDemoOtp(res.demoCode ?? null);
                        setOtpInput(res.demoCode ?? '');
                      }}
                      className="space-y-3.5"
                    >
                      <label className="block space-y-1.5">
                        <span className="font-medium text-[#3E4539]">
                          Email đăng ký * (Hồ sơ cá nhân bổ sung sau ở UC-04)
                        </span>
                        <div className="relative">
                          <Mail className="w-4 h-4 text-[#878E80] absolute left-3.5 top-1/2 -translate-y-1/2" />
                          <input
                            type="email"
                            required
                            value={regEmail}
                            onChange={(e) => setRegEmail(e.target.value)}
                            placeholder="tenban@example.com"
                            className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                          />
                        </div>
                      </label>
                      <button
                        type="submit"
                        className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                      >
                        Gửi mã OTP xác minh (Hiệu lực 5 phút)
                      </button>
                    </form>
                  )}

                  {otpChallenge && !otpChallenge.verified && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        setError(null);
                        const res = verifyRegisterOtp(otpInput);
                        if (!res.ok) setError(res.error ?? 'OTP không hợp lệ.');
                      }}
                      className="space-y-3.5"
                    >
                      <div className="p-3.5 rounded-2xl bg-[#E5ECE0] border border-[#C5D1BE] space-y-1">
                        <p className="font-semibold text-[#22261E]">
                          Đã gửi mã tới: {otpChallenge.email}
                        </p>
                        {lastDemoOtp && (
                          <p className="text-[#3B4B35]">
                            Hộp thư demo (`notification/facade.py`): Mã OTP của bạn là{' '}
                            <strong className="font-mono text-sm underline">
                              {lastDemoOtp}
                            </strong>
                          </p>
                        )}
                      </div>

                      <label className="block space-y-1.5">
                        <span className="font-medium text-[#3E4539]">
                          Nhập mã OTP 6 chữ số
                        </span>
                        <input
                          type="text"
                          required
                          maxLength={6}
                          value={otpInput}
                          onChange={(e) => setOtpInput(e.target.value)}
                          placeholder="Nhập 6 chữ số..."
                          className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] font-mono text-base tracking-[0.25em] text-center text-[#22261E]"
                        />
                      </label>

                      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#5E6658]">
                        <span className="inline-flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-[#4A5D43]" />
                          {remainingSeconds > 0
                            ? `Được gửi lại mã sau: ${formatCountdown(remainingSeconds)}`
                            : 'Đã đủ 5 phút — có thể gửi lại mã mới'}
                        </span>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            disabled={remainingSeconds > 0}
                            onClick={() => {
                              const r = resendRegisterOtp();
                              if (!r.ok) setError(r.error ?? null);
                              else setLastDemoOtp(r.demoCode ?? null);
                            }}
                            className="inline-flex items-center gap-1 font-semibold text-[#4A5D43] disabled:text-[#878E80] disabled:cursor-not-allowed cursor-pointer"
                          >
                            <RefreshCw className="w-3 h-3" />
                            <span>Gửi lại mã</span>
                          </button>
                          <span>·</span>
                          <button
                            type="button"
                            onClick={() => {
                              resetOtpFlow();
                              setError(null);
                            }}
                            className="text-[#8E3B2E] hover:underline cursor-pointer"
                          >
                            Đổi email
                          </button>
                        </div>
                      </div>

                      <button
                        type="submit"
                        className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                      >
                        Xác minh mã OTP (UC-01 AC-12)
                      </button>
                    </form>
                  )}

                  {otpChallenge?.verified && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        setError(null);
                        const res = completeOtpRegistration(
                          newPassword,
                          confirmPassword
                        );
                        if (!res.ok) {
                          setError(res.error ?? 'Tạo mật khẩu thất bại.');
                          return;
                        }
                        setIdentifier(res.email ?? regEmail);
                        setPassword(newPassword);
                        setNewPassword('');
                        setConfirmPassword('');
                        onSwitchMode('login');
                      }}
                      className="space-y-3.5"
                    >
                      <div className="p-3 rounded-xl bg-[#E5ECE0] text-[#3B4B35] font-medium">
                        Email <strong>{otpChallenge.email}</strong> đã xác minh! Hãy đặt mật khẩu Sobie để hoàn tất tạo tài khoản.
                      </div>
                      <label className="block space-y-1">
                        <span className="font-medium text-[#3E4539]">
                          Mật khẩu mới * (Tối thiểu 6 ký tự)
                        </span>
                        <input
                          type="password"
                          required
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                        />
                      </label>
                      <label className="block space-y-1">
                        <span className="font-medium text-[#3E4539]">
                          Nhập lại mật khẩu *
                        </span>
                        <input
                          type="password"
                          required
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0]"
                        />
                      </label>
                      <button
                        type="submit"
                        className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white font-semibold hover:bg-[#3B4B35] transition-colors cursor-pointer"
                      >
                        Hoàn tất tạo tài khoản & Chuyển tới Đăng nhập
                      </button>
                    </form>
                  )}
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-[#E4DDD0] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#5E6658]">
              <span>Bảo vệ bởi bcrypt + HttpOnly Session + Rate Limit 5/phút</span>
              <span>Cookie: `storefront_session` (30 phút)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ============================================================================
 * 2. UNIFIED INTERNAL PORTAL LOGIN PAGE (/admin/login — Admin & Saler per UC-02)
 * ============================================================================ */
export const PortalLoginPage: React.FC<{
  onSwitchSurface: (s: AppSurface) => void;
}> = ({ onSwitchSurface }) => {
  const { loginPortal, orders, accounts } = useSobieSystem();
  const rootRef = useRef<HTMLDivElement>(null);

  const [identifier, setIdentifier] = useState('nhanvien@example.com');
  const [password, setPassword] = useState('Staff@Sobie2026');
  const [error, setError] = useState<string | null>(null);

  const pendingOrders = orders.filter((o) => o.status === 'PENDING').length;
  const readyHandoff = orders.filter((o) => o.status === 'CONFIRMED').length;
  const activeAdminCount = accounts.filter(
    (a) => a.role === 'admin' && a.status === 'ACTIVE'
  ).length;

  useGSAP(
    () => {
      gsap.from('.portal-auth-reveal', {
        y: 16,
        autoAlpha: 0,
        duration: 0.5,
        stagger: 0.07,
        ease: 'power3.out',
      });
    },
    { scope: rootRef }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const res = loginPortal(identifier, password);
    if (!res.ok) setError(res.error ?? 'Thông tin đăng nhập không đúng.');
  };

  return (
    <div
      ref={rootRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-8 sm:py-12"
    >
      <div className="w-full space-y-6">
        <div className="portal-auth-reveal p-5 rounded-3xl atelier-card">
          <RolePortalDirectoryStrip
            activeSurface="portal"
            onSelectSurface={onSwitchSurface}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          {/* Left 7-Col Unified Internal Portal Architecture (Admin + Saler) */}
          <div className="portal-auth-reveal lg:col-span-7 rounded-3xl border border-[#E4DDD0] bg-[#F3EFE6] p-7 sm:p-10 flex flex-col justify-between space-y-8">
            <div className="space-y-4">
              <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-[#3B4B35] text-xs font-semibold uppercase tracking-[0.16em]">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>PORTAL QUẢN TRỊ NỘI BỘ HỢP NHẤT · `/admin/login` (UC-02)</span>
              </span>
              <h1 className="font-editorial text-4xl sm:text-5xl text-[#22261E] leading-tight">
                Một cổng đăng nhập chung cho Nhân viên & Admin — tự động phân luồng theo vai trò.
              </h1>
              <p className="text-sm text-[#5E6658] leading-relaxed max-w-3xl">
                Đúng chuẩn đặc tả `UC-02` (`POST /api/v1/identity/portal/login`): Nhân viên (Saler) và Admin đăng nhập chung trên một cổng quản trị độc lập với Storefront (`portal_session` hạn 60 phút). Ngay sau khi xác thực thành công, hệ thống tự chuyển tới đúng tab Tổng quan và thanh công cụ của vai trò tương ứng (`UC-02 AC-3`).
              </p>

              {/* Role Routing Preview Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2 text-xs">
                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1.5">
                  <div className="inline-flex items-center gap-1.5 font-semibold text-[#3B4B35]">
                    <Briefcase className="w-4 h-4 text-[#4A5D43]" />
                    <span>Khi đăng nhập tài khoản Nhân viên (`NV-...`)</span>
                  </div>
                  <p className="text-[#5E6658] leading-relaxed">
                    Chuyển thẳng về <strong>Dashboard báo cáo (UC-37)</strong> và mở 10 phân hệ vận hành: Đơn hàng, Bàn giao vận chuyển, Sản phẩm/Giá size, Phân loại, Khuyến mãi, Kho/Phiếu nhập, Hóa đơn & Xem/Khóa Khách hàng (`UC-07/08`).
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0] space-y-1.5">
                  <div className="inline-flex items-center gap-1.5 font-semibold text-[#22261E]">
                    <ShieldCheck className="w-4 h-4 text-[#4A5D43]" />
                    <span>Khi đăng nhập tài khoản Admin (`AD-...`)</span>
                  </div>
                  <p className="text-[#5E6658] leading-relaxed">
                    Chuyển thẳng về <strong>Tổng quan Quản trị Tài khoản (UC-06→08)</strong>: Tạo tài khoản 3 vai trò, sửa hồ sơ & hoán đổi Nhân viên ↔ Admin cấp mã mới, Khóa/Mở khóa toàn hệ thống (không truy cập vận hành bán hàng).
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 text-xs">
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Đơn chờ xử lý</span>
                <span className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 block tabular-price">
                  {pendingOrders}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Chờ bàn giao ship</span>
                <span className="font-editorial text-3xl font-semibold text-[#4A5D43] mt-1 block tabular-price">
                  {readyHandoff}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Admin Hoạt động (≥ 1)</span>
                <span className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 block tabular-price">
                  {activeAdminCount}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Hạn phiên Portal</span>
                <span className="font-editorial text-3xl font-semibold text-[#22261E] mt-1 block">
                  60 phút
                </span>
              </div>
            </div>
          </div>

          {/* Right 5-Col Unified Portal Sign-In Form (NO Forgot Password per UC-02 1b/AC-10!) */}
          <div className="portal-auth-reveal lg:col-span-5 rounded-3xl atelier-card p-7 sm:p-10 flex flex-col justify-between space-y-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
                  INTERNAL PORTAL · `/admin/login` (ẨN QUÊN MẬT KHẨU THEO UC-02)
                </p>
                <h2 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                  Đăng nhập Quản trị & Vận hành
                </h2>
                <p className="text-xs text-[#5E6658] mt-1">
                  Chỉ chấp nhận tài khoản <strong>Nhân viên (Saler)</strong> hoặc <strong>Admin</strong> đang Hoạt động. Tài khoản Khách hàng đăng nhập tại đây sẽ bị từ chối với thông báo chung «Thông tin đăng nhập không đúng» (`UC-02 AC-9`).
                </p>
              </div>

              {error && (
                <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E] flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Quick-fill Demo Credentials for BOTH Saler & Admin + AC-9 Test */}
              <div className="space-y-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-[#5E6658] block">
                  Chọn nhanh tài khoản mẫu để kiểm thử phân luồng vai trò:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setIdentifier('nhanvien@example.com');
                      setPassword('Staff@Sobie2026');
                      setError(null);
                    }}
                    className="p-3 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] hover:border-[#4A5D43] text-left cursor-pointer"
                  >
                    <span className="font-semibold text-[#3B4B35] block">
                      1. Nhân viên (Saler) · Email
                    </span>
                    <span className="text-[11px] font-mono text-[#5E6658]">
                      nhanvien@example.com
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIdentifier('admin@example.com');
                      setPassword('Admin@Sobie2026');
                      setError(null);
                    }}
                    className="p-3 rounded-xl bg-[#F3EFE6] border border-[#E4DDD0] hover:border-[#4A5D43] text-left cursor-pointer"
                  >
                    <span className="font-semibold text-[#22261E] block">
                      2. Quản trị viên (Admin) · Email
                    </span>
                    <span className="text-[11px] font-mono text-[#5E6658]">
                      admin@example.com
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIdentifier('0900000002');
                      setPassword('Staff@Sobie2026');
                      setError(null);
                    }}
                    className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] hover:border-[#4A5D43] text-left cursor-pointer"
                  >
                    <span className="font-semibold text-[#3E4539] block">
                      Nhân viên theo SĐT (AC-3)
                    </span>
                    <span className="text-[11px] font-mono text-[#5E6658]">
                      0900000002
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIdentifier('khachhang@example.com');
                      setPassword('Customer@Sobie2026');
                      setError(null);
                    }}
                    className="p-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] hover:border-[#A84A3B] text-left cursor-pointer"
                  >
                    <span className="font-semibold text-[#8E3B2E] block">
                      Test chặn Khách hàng (AC-9)
                    </span>
                    <span className="text-[11px] font-mono text-[#5E6658]">
                      khachhang@example.com
                    </span>
                  </button>
                </div>
              </div>

              <label className="block space-y-1.5 text-xs">
                <span className="font-medium text-[#3E4539]">
                  Email hoặc Số điện thoại nội bộ
                </span>
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="nhanvien@example.com / admin@example.com"
                  className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                />
              </label>

              <label className="block space-y-1.5 text-xs">
                <span className="font-medium text-[#3E4539]">Mật khẩu</span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-xs text-[#22261E] focus:outline-none focus:bg-white focus:border-[#4A5D43]"
                />
              </label>

              <button
                type="submit"
                className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white text-sm font-semibold hover:bg-[#3B4B35] transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-xs"
              >
                <KeyRound className="w-4 h-4" />
                <span>Đăng nhập Portal Quản trị</span>
              </button>
            </form>

            <div className="pt-4 border-t border-[#E4DDD0] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#5E6658]">
              <span>Độc lập với phiên Khách hàng (UC-02 AC-20)</span>
              <span>Cookie: `portal_session` (60 phút)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ============================================================================
 * 3. SHIPPING PARTNER FULL-BLEED LOGIN & UC-36 PUBLIC ACCESS GATE
 * ============================================================================ */
export const ShippingLoginPage: React.FC<{
  onSwitchSurface: (s: AppSurface) => void;
}> = ({ onSwitchSurface }) => {
  const {
    loginShippingPartner,
    enterPublicShippingSimulator,
    orders,
  } = useSobieSystem();
  const rootRef = useRef<HTMLDivElement>(null);

  const demo = STORE_CONFIG.shippingDemoCredentials;
  const [stationCode, setStationCode] = useState(demo.stationCode);
  const [identifier, setIdentifier] = useState(demo.email);
  const [password, setPassword] = useState(demo.password);
  const [error, setError] = useState<string | null>(null);

  const awaitingPickup = orders.filter(
    (o) => o.status === 'AWAITING_PICKUP'
  ).length;
  const inTransit = orders.filter((o) => o.status === 'SHIPPING').length;

  useGSAP(
    () => {
      gsap.from('.ship-auth-reveal', {
        y: 16,
        autoAlpha: 0,
        duration: 0.5,
        stagger: 0.07,
        ease: 'power3.out',
      });
    },
    { scope: rootRef }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const res = loginShippingPartner(stationCode, identifier, password);
    if (!res.ok) setError(res.error ?? 'Không thể đăng nhập trạm giao vận.');
  };

  return (
    <div
      ref={rootRef}
      className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-8 sm:py-12"
    >
      <div className="w-full space-y-6">
        <div className="ship-auth-reveal p-5 rounded-3xl atelier-card">
          <RolePortalDirectoryStrip
            activeSurface="shipping"
            onSelectSurface={onSwitchSurface}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          <div className="ship-auth-reveal lg:col-span-7 rounded-3xl border border-[#E4DDD0] bg-[#F3EFE6] p-7 sm:p-10 flex flex-col justify-between space-y-8">
            <div className="space-y-4">
              <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#E5ECE0] border border-[#C5D1BE] text-[#3B4B35] text-xs font-semibold uppercase tracking-[0.16em]">
                <Truck className="w-3.5 h-3.5" />
                <span>CỔNG ĐƠN VỊ VẬN CHUYỂN (`shipping:8001` · UC-36)</span>
              </span>
              <h1 className="font-editorial text-4xl sm:text-5xl text-[#22261E] leading-tight">
                Trạm điều phối giao nhận độc lập — bảo mật tuyệt đối PII & COD.
              </h1>
              <p className="text-sm text-[#5E6658] leading-relaxed max-w-2xl">
                Hỗ trợ đồng thời <strong>Đăng nhập ca trực Đối tác Vận chuyển</strong> (`[GD]`) và nút <strong>Truy cập thẳng Trang Giả lập Công khai không cần đăng nhập</strong> đúng nguyên bản `UC-36 AC-1`. Tuyệt đối ẩn họ tên, SĐT, địa chỉ và số tiền của khách!
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 text-xs">
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Đơn Chờ lấy hàng</span>
                <span className="font-editorial text-3xl font-semibold text-[#8A5A14] mt-1 block tabular-price">
                  {awaitingPickup}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Đơn Đang giao</span>
                <span className="font-editorial text-3xl font-semibold text-[#4A5D43] mt-1 block tabular-price">
                  {inTransit}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
                <span className="text-[#5E6658] block">Tác động tự động</span>
                <span className="font-semibold text-[#22261E] mt-1.5 block leading-relaxed">
                  Đã giao → Xuất HĐ (UC-26) · Thất bại → Cộng tồn (UC-35)
                </span>
              </div>
            </div>
          </div>

          <div className="ship-auth-reveal lg:col-span-5 rounded-3xl atelier-card p-7 sm:p-10 flex flex-col justify-between space-y-6">
            <div className="space-y-5">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-[#4A5D43] font-semibold">
                  SHIPPING DISPATCH · `shipping:8001`
                </p>
                <h2 className="font-editorial text-3xl sm:text-4xl text-[#22261E] mt-1">
                  Đối tác Vận chuyển
                </h2>
              </div>

              {error && (
                <div className="px-4 py-3 rounded-2xl bg-[#FBECE9] border border-[#E7C2BA] text-xs text-[#8E3B2E]">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
                <label className="block space-y-1">
                  <span className="font-medium text-[#3E4539]">Mã bưu cục / Trạm điều phối</span>
                  <input
                    type="text"
                    required
                    value={stationCode}
                    onChange={(e) => setStationCode(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] font-mono text-[#22261E]"
                  />
                </label>
                <label className="block space-y-1">
                  <span className="font-medium text-[#3E4539]">Email điều phối viên</span>
                  <input
                    type="email"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
                  />
                </label>
                <label className="block space-y-1">
                  <span className="font-medium text-[#3E4539]">Mật khẩu ca trực</span>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#FAF7F2] border border-[#E4DDD0] text-[#22261E]"
                  />
                </label>

                <button
                  type="submit"
                  className="w-full py-3.5 rounded-full bg-[#4A5D43] text-white text-sm font-semibold hover:bg-[#3B4B35] transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                >
                  <Truck className="w-4 h-4" />
                  <span>Đăng nhập Ca trực Vận chuyển</span>
                </button>
              </form>

              <div className="relative flex items-center py-1">
                <div className="flex-grow border-t border-[#E4DDD0]" />
                <span className="shrink mx-3 text-[11px] uppercase tracking-wider text-[#878E80]">
                  hoặc theo chuẩn UC-36 AC-1
                </span>
                <div className="flex-grow border-t border-[#E4DDD0]" />
              </div>

              <button
                type="button"
                onClick={enterPublicShippingSimulator}
                className="w-full py-3 rounded-full bg-[#F3EFE6] border border-[#D4CBB8] hover:border-[#4A5D43] text-xs font-semibold text-[#22261E] transition-colors cursor-pointer"
              >
                Mở thẳng Trang Giả lập Công khai (Không cần đăng nhập · UC-36 AC-1)
              </button>
            </div>

            <div className="pt-4 border-t border-[#E4DDD0] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#5E6658]">
              <span>Service: `shipping:8001`</span>
              <span>Ẩn 100% thông tin cá nhân & COD</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
