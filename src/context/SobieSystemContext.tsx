import React, { createContext, useContext, useMemo, useState } from 'react';
import {
  calcDiscountAmount,
  calcDiscountedPrice,
  generateOrderCode,
  toNaturalToken,
} from '../lib/gsap';
import {
  SEED_ACCOUNTS,
  SEED_CATEGORIES,
  SEED_COLLECTIONS,
  SEED_COLORS,
  SEED_GENDERS,
  SEED_INVOICES,
  SEED_ORDERS,
  SEED_PRODUCTS,
  SEED_PROMOTIONS,
  SEED_RECEIPTS,
  SEED_SIZES,
  SEED_SUPPLIERS,
  SEED_VARIANTS,
  STORE_CONFIG,
} from '../data/seedData';
import {
  AccountRecord,
  CartItem,
  ColorItem,
  GalleryItem,
  GoodsReceiptRecord,
  InvoiceSnapshot,
  OrderRecord,
  PaymentMethod,
  ProductRecord,
  PromotionDisplayStatus,
  PromotionRecord,
  PromotionType,
  RoleCode,
  ShippingOperatorSession,
  SupplierRecord,
  VariantRecord,
} from '../types/store';

export interface DiscountQuoteResult {
  subtotal: number;
  selectedDiscount: number;
  selectedSource: 'NONE' | 'ORDER' | 'CODE';
  selectedPromotionId?: string;
  selectedPromotionLabel: string;
  payableBeforeShipping: number;
  notice: string;
  voucherError?: string;
}

export interface OtpChallengeState {
  email: string;
  code: string;
  sentAtMs: number;
  expiresAtMs: number;
  resendAvailableAtMs: number;
  wrongAttempts: number;
  locked: boolean;
  verified: boolean;
}

interface SobieContextValue {
  // Taxonomies (UC-17)
  categories: string[];
  collections: string[];
  genders: string[];
  sizes: string[];
  colors: ColorItem[];

  // Core Entities
  accounts: AccountRecord[];
  products: ProductRecord[];
  variants: VariantRecord[];
  promotions: PromotionRecord[];
  orders: OrderRecord[];
  invoices: InvoiceSnapshot[];
  suppliers: SupplierRecord[];
  receipts: GoodsReceiptRecord[];

  // 3 Separate Portal Sessions matching UC-02 & UC-36 (Storefront / Unified Internal Portal / Shipping)
  storefrontUser: AccountRecord | null;
  portalUser: AccountRecord | null;
  shippingSession: ShippingOperatorSession | null;

  // Cart & Wishlist
  activeCart: CartItem[];
  guestCart: CartItem[];
  activeWishlist: string[]; // ordered newest-added first (UC-38)

  // Toast helper
  toastMessage: string | null;
  notify: (msg: string) => void;

  // Helpers
  getActiveProductPromo: (productId: string) => PromotionRecord | undefined;
  getPromotionDisplayStatus: (promo: PromotionRecord) => PromotionDisplayStatus;
  getProductVariants: (productId: string) => VariantRecord[];
  getValidPricedVariants: (productId: string) => VariantRecord[];
  getProductMinPrice: (productId: string) => number | null;
  hasMultipleSizePrices: (productId: string) => boolean;
  isProductEligibleForListing: (productId: string) => boolean;
  isProductSoldOut: (productId: string) => boolean;
  hasConfirmedReceiptForProduct: (productId: string) => boolean;
  isProfileCompleteForAutofill: (acc: AccountRecord | null) => boolean;
  quoteOrderDiscount: (subtotal: number, voucherCode?: string) => DiscountQuoteResult;
  getTop5BestSellers7Days: () => { product: ProductRecord; soldQty: number }[];

  // Identity Actions — User (UC-01, UC-02, UC-03, UC-04, UC-05)
  otpChallenge: OtpChallengeState | null;
  requestRegisterOtp: (email: string) => { ok: boolean; demoCode?: string; error?: string };
  resendRegisterOtp: () => { ok: boolean; demoCode?: string; error?: string };
  verifyRegisterOtp: (code: string) => { ok: boolean; locked429?: boolean; error?: string };
  completeOtpRegistration: (
    password: string,
    confirmPassword: string
  ) => { ok: boolean; email?: string; error?: string };
  resetOtpFlow: () => void;

  loginStorefront: (identifier: string, password: string) => { ok: boolean; status429?: boolean; error?: string };
  loginOrRegisterWithGoogle: (
    googleEmail: string,
    googleDisplayName?: string
  ) => { ok: boolean; createdNew?: boolean; error?: string };
  logoutStorefront: () => void;
  updateCustomerProfile: (payload: {
    name: string;
    phone: string;
    dateOfBirth: string;
    houseNumber: string;
    ward: string;
    city: string;
    country: string;
  }) => { ok: boolean; error?: string };

  // Identity Actions — Unified Internal Portal (Admin & Saler per UC-02) & Shipping
  loginPortal: (
    identifier: string,
    password: string
  ) => { ok: boolean; role?: RoleCode; status429?: boolean; error?: string };
  logoutPortal: () => void;
  loginShippingPartner: (
    stationCode: string,
    identifier: string,
    password: string
  ) => { ok: boolean; error?: string };
  enterPublicShippingSimulator: () => void;
  logoutShipping: () => void;

  changePassword: (
    target: 'storefront' | 'portal',
    currentPassword: string,
    newPassword: string,
    confirmPassword: string
  ) => { ok: boolean; error?: string };

  // Admin & Saler Account Governance (UC-06, UC-07, UC-08)
  adminCreateAccount: (payload: {
    name: string;
    role: RoleCode;
    email: string;
    phone: string;
    password: string;
    dateOfBirth: string;
    houseNumber: string;
    ward: string;
    city: string;
  }) => { ok: boolean; error?: string };
  adminEditAccount: (
    accountId: string,
    payload: {
      name: string;
      email: string;
      phone: string;
      dateOfBirth: string;
      houseNumber: string;
      ward: string;
      city: string;
      role: RoleCode;
    }
  ) => { ok: boolean; error?: string };
  adminToggleLockAccount: (accountId: string) => { ok: boolean; error?: string };
  salerLockCustomerAccount: (accountId: string) => { ok: boolean; error?: string };

  // Shopping Actions (UC-18, UC-38)
  addToCart: (sku: string, productId: string, qty: number) => { ok: boolean; error?: string };
  updateCartQty: (sku: string, nextQty: number) => { ok: boolean; error?: string };
  removeFromCart: (sku: string) => void;
  clearUnavailableFromCart: () => void;
  toggleWishlist: (productId: string) => { ok: boolean; requireLogin?: boolean };

  // Ordering & Shipping Actions (UC-19 -> UC-27, UC-35, UC-36, UC-40)
  placeOrder: (payload: {
    paymentMethod: PaymentMethod;
    voucherCode?: string;
    customerName: string;
    phone: string;
    houseNumber: string;
    ward: string;
    city: string;
    country: string;
    selectedSkus?: string[];
    expectedTotal?: number;
  }) => { ok: boolean; order?: OrderRecord; requireReconfirm?: boolean; error?: string };
  simulateSepayWebhook: (orderCode: string, transferAmount?: number) => { ok: boolean; error?: string };
  runAutoCancelOverdueQrJob: () => { cancelledCount: number };
  customerCancelOrder: (orderCode: string) => { ok: boolean; error?: string };
  employeeConfirmOrder: (orderCode: string) => { ok: boolean; error?: string };
  employeeCancelOrder: (orderCode: string, reason: string) => { ok: boolean; error?: string };
  employeeHandoffOrder: (orderCode: string) => { ok: boolean; error?: string };
  carrierUpdateShipment: (
    orderCode: string,
    action: 'received' | 'delivered' | 'failed'
  ) => { ok: boolean; statusLabel?: string; error?: string };

  // Catalog Management (UC-14 -> UC-17)
  saveProduct: (payload: {
    id?: string;
    name: string;
    subtitle: string;
    description: string;
    category: string;
    gender: string;
    collections: string[];
    gallery: GalleryItem[];
  }) => { ok: boolean; error?: string };
  toggleProductStatus: (productId: string) => { ok: boolean; error?: string };
  deleteProduct: (productId: string) => { ok: boolean; error?: string };
  generateVariantsMatrix: (
    productId: string,
    selectedColors: string[],
    selectedSizes: string[]
  ) => { ok: boolean; createdCount?: number; error?: string };
  toggleVariantStatus: (sku: string) => { ok: boolean; error?: string };
  deleteVariant: (sku: string) => { ok: boolean; error?: string };
  updateSizePrices: (
    productId: string,
    sizePriceMap: Record<string, number>
  ) => { ok: boolean; error?: string };
  manageTaxonomy: (
    kind: 'category' | 'collection' | 'gender' | 'size' | 'color',
    action: 'add' | 'rename' | 'delete',
    value: string,
    newValue?: string,
    hex?: string
  ) => { ok: boolean; error?: string };

  // Promotion Management (UC-28 -> UC-30)
  createPromotion: (payload: {
    type: PromotionType;
    discountPercentage: number;
    productId?: string;
    thresholdPrice?: number;
    quantity?: number;
    code?: string;
    startDate?: string;
    endDate?: string;
  }) => { ok: boolean; error?: string };
  endPromotion: (promotionId: string) => { ok: boolean; error?: string };

  // Inventory Management (UC-32 -> UC-34)
  saveSupplier: (payload: {
    supplierId?: string;
    name: string;
    phone: string;
    email: string;
    address: string;
  }) => { ok: boolean; error?: string };
  toggleSupplierStatus: (supplierId: string) => void;
  deleteSupplier: (supplierId: string) => { ok: boolean; error?: string };
  saveDraftReceipt: (payload: {
    receiptId?: string;
    supplierId: string;
    lines: { sku: string; quantity: number; unitPrice: number }[];
  }) => { ok: boolean; error?: string };
  confirmReceipt: (receiptId: string) => { ok: boolean; error?: string };
  cancelReceipt: (receiptId: string) => { ok: boolean; error?: string };
}

const SobieContext = createContext<SobieContextValue | null>(null);

const TODAY_STR = '2026-11-27';
const GUEST_STORAGE_KEY = 'sobie_guest_cart_olive_v2';
const NOW_ISO = () => new Date().toISOString();

const INITIAL_GUEST_DEMO_CART: CartItem[] = [
  { sku: 'SP-0003-XANHOLIVE-M', productId: 'SP-0003', quantity: 1 },
  { sku: 'SP-0002-DO-S', productId: 'SP-0002', quantity: 1 },
];

export const SobieSystemProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [categories, setCategories] = useState<string[]>(SEED_CATEGORIES);
  const [collections, setCollections] = useState<string[]>(SEED_COLLECTIONS);
  const [genders, setGenders] = useState<string[]>(SEED_GENDERS);
  const [sizes, setSizes] = useState<string[]>(SEED_SIZES);
  const [colors, setColors] = useState<ColorItem[]>(SEED_COLORS);

  const [accounts, setAccounts] = useState<AccountRecord[]>(SEED_ACCOUNTS);
  const [products, setProducts] = useState<ProductRecord[]>(SEED_PRODUCTS);
  const [variants, setVariants] = useState<VariantRecord[]>(SEED_VARIANTS);
  const [promotions, setPromotions] = useState<PromotionRecord[]>(SEED_PROMOTIONS);
  const [orders, setOrders] = useState<OrderRecord[]>(SEED_ORDERS);
  const [invoices, setInvoices] = useState<InvoiceSnapshot[]>(SEED_INVOICES);
  const [suppliers, setSuppliers] = useState<SupplierRecord[]>(SEED_SUPPLIERS);
  const [receipts, setReceipts] = useState<GoodsReceiptRecord[]>(SEED_RECEIPTS);

  // 3 Separate Portal Sessions (Storefront `storefront_session` / Unified Internal `portal_session` / Shipping)
  const [storefrontAccountId, setStorefrontAccountId] = useState<string | null>(null);
  const [portalAccountId, setPortalAccountId] = useState<string | null>(null);
  const [shippingSession, setShippingSession] =
    useState<ShippingOperatorSession | null>(null);

  // UC-02 E5 / AC-13: Password login rate limit (5 attempts / 60s per IP)
  const [passwordAttemptsTimestamps, setPasswordAttemptsTimestamps] = useState<
    number[]
  >([]);

  // UC-01 v15: Email OTP Registration Challenge State
  const [otpChallenge, setOtpChallenge] = useState<OtpChallengeState | null>(null);

  // Guest temporary cart in localStorage vs per-account DB cart (UC-18)
  const [guestCart, setGuestCart] = useState<CartItem[]>(() => {
    try {
      const raw = localStorage.getItem(GUEST_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) return parsed;
      }
      localStorage.setItem(
        GUEST_STORAGE_KEY,
        JSON.stringify(INITIAL_GUEST_DEMO_CART)
      );
    } catch {
      // ignore
    }
    return INITIAL_GUEST_DEMO_CART;
  });

  const [accountCarts, setAccountCarts] = useState<Record<string, CartItem[]>>({
    'KH-20261127-0001': [
      { sku: 'SP-0001-DEN-M', productId: 'SP-0001', quantity: 1 },
      { sku: 'SP-0002-DO-M', productId: 'SP-0002', quantity: 2 },
    ],
    'KH-20261126-0002': [
      { sku: 'SP-0004-CATKEM-M', productId: 'SP-0004', quantity: 1 },
    ],
  });

  // Per-account wishlists, newest added first (UC-38)
  const [accountWishlists, setAccountWishlists] = useState<
    Record<string, string[]>
  >({
    'KH-20261127-0001': ['SP-0002', 'SP-0003', 'SP-0001'],
    'KH-20261126-0002': ['SP-0004'],
  });

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const notify = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((prev) => (prev === msg ? null : prev));
    }, 3600);
  };

  const storefrontUser = useMemo(
    () =>
      accounts.find(
        (a) =>
          a.accountId === storefrontAccountId &&
          a.role === 'customer' &&
          a.status === 'ACTIVE'
      ) ?? null,
    [accounts, storefrontAccountId]
  );

  const portalUser = useMemo(
    () =>
      accounts.find(
        (a) =>
          a.accountId === portalAccountId &&
          (a.role === 'employee' || a.role === 'admin') &&
          a.status === 'ACTIVE'
      ) ?? null,
    [accounts, portalAccountId]
  );

  const activeCart = storefrontUser
    ? accountCarts[storefrontUser.accountId] ?? []
    : guestCart;

  const activeWishlist = storefrontUser
    ? accountWishlists[storefrontUser.accountId] ?? []
    : [];

  const saveGuestCart = (next: CartItem[]) => {
    setGuestCart(next);
    try {
      localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore
    }
  };

  /* --------------------------------------------------------------------------
   * DOMAIN HELPERS (Synced with specs/README.md)
   * -------------------------------------------------------------------------- */
  const getPromotionDisplayStatus = (
    promo: PromotionRecord
  ): PromotionDisplayStatus => {
    if (promo.status === 'DISABLED') return 'Đã kết thúc';
    if (promo.type === 'PRODUCT') return 'Đang hiệu lực';
    if (promo.endDate && TODAY_STR > promo.endDate) return 'Đã kết thúc';
    if (promo.startDate && TODAY_STR < promo.startDate) return 'Sắp diễn ra';
    return 'Đang hiệu lực';
  };

  const getActiveProductPromo = (productId: string) =>
    promotions.find(
      (p) =>
        p.type === 'PRODUCT' &&
        p.productId === productId &&
        p.status === 'ENABLED'
    );

  const getProductVariants = (productId: string) =>
    variants.filter((v) => v.productId === productId && v.status === 'ACTIVE');

  // UC-10 Q9 / UC-12 Q9b: Only ACTIVE variants with sellPrice > 0 participate in storefront pricing & stock label
  const getValidPricedVariants = (productId: string) =>
    variants.filter(
      (v) =>
        v.productId === productId &&
        v.status === 'ACTIVE' &&
        v.sellPrice !== null &&
        v.sellPrice > 0
    );

  const getProductMinPrice = (productId: string): number | null => {
    const pv = getValidPricedVariants(productId);
    if (pv.length === 0) return null;
    return Math.min(...pv.map((v) => v.sellPrice!));
  };

  const hasMultipleSizePrices = (productId: string): boolean => {
    const pv = getValidPricedVariants(productId);
    if (pv.length <= 1) return false;
    const distinct = new Set(pv.map((v) => v.sellPrice!));
    return distinct.size > 1;
  };

  // UC-10 Q10: Eligible for Home / Category / Search listing if parent ACTIVE AND >= 1 ACTIVE variant with price > 0
  const isProductEligibleForListing = (productId: string): boolean => {
    const p = products.find((x) => x.id === productId);
    if (!p || p.status !== 'ACTIVE') return false;
    return getValidPricedVariants(productId).length > 0;
  };

  const isProductSoldOut = (productId: string): boolean => {
    const pv = getValidPricedVariants(productId);
    if (pv.length === 0) return true;
    return pv.every((v) => v.stockQuantity <= 0);
  };

  // UC-14-Q11 / UC-15 / UC-16 / UC-17-Q7: Freeze product/variant/price/taxonomy edits after CONFIRMED receipt!
  const hasConfirmedReceiptForProduct = (productId: string): boolean => {
    const pSkus = new Set(
      variants.filter((v) => v.productId === productId).map((v) => v.sku)
    );
    return receipts.some(
      (r) =>
        r.status === 'CONFIRMED' && r.lines.some((ln) => pSkus.has(ln.sku))
    );
  };

  // UC-04 v7 / UC-19 v14: Profile autofill requires name, DOB, phone, and address!
  const isProfileCompleteForAutofill = (acc: AccountRecord | null): boolean => {
    if (!acc) return false;
    return Boolean(
      acc.name.trim() &&
        acc.dateOfBirth.trim() &&
        /^[0-9+\s]{8,15}$/.test(acc.phone.trim()) &&
        acc.houseNumber.trim() &&
        acc.ward.trim() &&
        acc.city.trim()
    );
  };

  // UC-09 AC-7..AC-11 (specs/README.md line 128): Top 5 Best-Sellers in 168h UTC, exclude CANCELLED & DELIVERY_FAILED
  const getTop5BestSellers7Days = () => {
    const cutoffMs =
      new Date('2026-11-27T23:59:59Z').getTime() - 168 * 3600 * 1000;
    const stats: Record<string, { qty: number; latestMs: number }> = {};

    for (const o of orders) {
      if (o.status === 'CANCELLED' || o.status === 'DELIVERY_FAILED') continue;
      const createdMs = new Date(o.createdAt).getTime();
      if (createdMs < cutoffMs) continue;
      for (const item of o.items) {
        const cur = stats[item.productId] ?? { qty: 0, latestMs: 0 };
        stats[item.productId] = {
          qty: cur.qty + item.quantity,
          latestMs: Math.max(cur.latestMs, createdMs),
        };
      }
    }

    // Take top 15 from reporting, then filter eligible active catalog products -> max 5
    return Object.entries(stats)
      .sort(([idA, a], [idB, b]) => {
        if (b.qty !== a.qty) return b.qty - a.qty;
        if (b.latestMs !== a.latestMs) return b.latestMs - a.latestMs;
        return idA.localeCompare(idB);
      })
      .slice(0, 15)
      .map(([pid, s]) => ({
        product: products.find((p) => p.id === pid),
        soldQty: s.qty,
      }))
      .filter(
        (entry): entry is { product: ProductRecord; soldQty: number } =>
          Boolean(
            entry.product &&
              isProductEligibleForListing(entry.product.id) &&
              entry.soldQty > 0
          )
      )
      .slice(0, 5);
  };

  // UC-31: Quote best order discount between ORDER promotions & CODE voucher (tie -> CODE wins!)
  const quoteOrderDiscount = (
    subtotal: number,
    voucherCode?: string
  ): DiscountQuoteResult => {
    const cleanCode = (voucherCode ?? '').trim().toUpperCase();
    let voucherError: string | undefined;
    let voucherCandidate: { promo: PromotionRecord; discount: number } | null =
      null;

    if (cleanCode) {
      const foundCode = promotions.find(
        (p) => p.type === 'CODE' && p.code?.toUpperCase() === cleanCode
      );
      if (!foundCode) {
        voucherError = 'Mã voucher không tồn tại.';
      } else if (getPromotionDisplayStatus(foundCode) !== 'Đang hiệu lực') {
        voucherError =
          'Mã voucher hiện không trong thời gian hiệu lực hoặc đã ngừng.';
      } else if (
        foundCode.quantity !== undefined &&
        foundCode.usedAmount >= foundCode.quantity
      ) {
        voucherError = 'Mã voucher đã hết lượt sử dụng.';
      } else if (
        foundCode.thresholdPrice !== undefined &&
        subtotal < foundCode.thresholdPrice
      ) {
        voucherError = `Đơn tối thiểu cho mã ${foundCode.code} là ${new Intl.NumberFormat(
          'vi-VN'
        ).format(foundCode.thresholdPrice)}₫.`;
      } else {
        voucherCandidate = {
          promo: foundCode,
          discount: calcDiscountAmount(subtotal, foundCode.discountPercentage),
        };
      }
    }

    let bestOrderCandidate: { promo: PromotionRecord; discount: number } | null =
      null;
    for (const p of promotions) {
      if (p.type !== 'ORDER') continue;
      if (getPromotionDisplayStatus(p) !== 'Đang hiệu lực') continue;
      if (p.quantity !== undefined && p.usedAmount >= p.quantity) continue;
      if (p.thresholdPrice !== undefined && subtotal < p.thresholdPrice)
        continue;
      const d = calcDiscountAmount(subtotal, p.discountPercentage);
      if (!bestOrderCandidate || d > bestOrderCandidate.discount) {
        bestOrderCandidate = { promo: p, discount: d };
      }
    }

    if (
      voucherCandidate &&
      (!bestOrderCandidate ||
        voucherCandidate.discount >= bestOrderCandidate.discount)
    ) {
      const note = bestOrderCandidate
        ? `Hệ thống tự chọn voucher ${voucherCandidate.promo.code} (-${voucherCandidate.promo.discountPercentage}%) có lợi hơn khuyến mãi hóa đơn ${bestOrderCandidate.promo.promotionId} (-${bestOrderCandidate.promo.discountPercentage}%).`
        : `Áp dụng voucher ${voucherCandidate.promo.code} (-${voucherCandidate.promo.discountPercentage}%).`;
      return {
        subtotal,
        selectedDiscount: voucherCandidate.discount,
        selectedSource: 'CODE',
        selectedPromotionId: voucherCandidate.promo.promotionId,
        selectedPromotionLabel: `Voucher ${voucherCandidate.promo.code} (${voucherCandidate.promo.promotionId} · -${voucherCandidate.promo.discountPercentage}%)`,
        payableBeforeShipping: subtotal - voucherCandidate.discount,
        notice: note,
        voucherError,
      };
    }

    if (bestOrderCandidate && bestOrderCandidate.discount > 0) {
      const note = voucherCandidate
        ? `Khuyến mãi hóa đơn ${bestOrderCandidate.promo.promotionId} (-${bestOrderCandidate.promo.discountPercentage}%) có lợi hơn voucher ${voucherCandidate.promo.code}, hệ thống tự chọn mức giảm cao hơn.`
        : `Tự động áp dụng khuyến mãi hóa đơn ${bestOrderCandidate.promo.promotionId} (-${bestOrderCandidate.promo.discountPercentage}%).`;
      return {
        subtotal,
        selectedDiscount: bestOrderCandidate.discount,
        selectedSource: 'ORDER',
        selectedPromotionId: bestOrderCandidate.promo.promotionId,
        selectedPromotionLabel: `KM Hóa đơn ${bestOrderCandidate.promo.promotionId} (-${bestOrderCandidate.promo.discountPercentage}%)`,
        payableBeforeShipping: subtotal - bestOrderCandidate.discount,
        notice: voucherError ? `${voucherError} ${note}` : note,
        voucherError,
      };
    }

    return {
      subtotal,
      selectedDiscount: 0,
      selectedSource: 'NONE',
      selectedPromotionLabel: 'Không có ưu đãi đơn hàng đủ điều kiện',
      payableBeforeShipping: subtotal,
      notice: voucherError ?? 'Chưa đạt ngưỡng khuyến mãi theo hóa đơn.',
      voucherError,
    };
  };

  /* --------------------------------------------------------------------------
   * IDENTITY ACTIONS (UC-01 -> UC-08 + 4 Dedicated Role Logins)
   * -------------------------------------------------------------------------- */
  const nextCounter = (prefix: 'KH' | 'NV' | 'AD', currentList = accounts) => {
    const matching = currentList.filter((a) =>
      a.accountId.startsWith(`${prefix}-`)
    );
    const nums = matching.map((a) => {
      const tail = a.accountId.split('-').pop() ?? '0';
      return parseInt(tail, 10) || 0;
    });
    const next = (nums.length ? Math.max(...nums) : 0) + 1;
    return String(next).padStart(4, '0');
  };

  const checkPasswordRateLimit = (): boolean => {
    const now = Date.now();
    const recent = passwordAttemptsTimestamps.filter((t) => now - t < 60_000);
    if (recent.length >= 5) {
      setPasswordAttemptsTimestamps(recent);
      return false;
    }
    setPasswordAttemptsTimestamps([...recent, now]);
    return true;
  };

  // UC-18 2b / 2c / AC-6: Merge guest localStorage cart into customer account cart on login
  const mergeGuestCartIntoAccount = (targetAccountId: string) => {
    if (guestCart.length === 0) return;
    setAccountCarts((prev) => {
      const current = [...(prev[targetAccountId] ?? [])];
      for (const gItem of guestCart) {
        const p = products.find((pr) => pr.id === gItem.productId);
        const v = variants.find((vr) => vr.sku === gItem.sku);
        const isAvailable =
          p &&
          p.status === 'ACTIVE' &&
          v &&
          v.status === 'ACTIVE' &&
          v.stockQuantity > 0;
        const idx = current.findIndex((c) => c.sku === gItem.sku);

        if (isAvailable && v) {
          if (idx >= 0) {
            current[idx] = {
              ...current[idx],
              quantity: Math.min(
                v.stockQuantity,
                current[idx].quantity + gItem.quantity
              ),
            };
          } else {
            current.push({
              ...gItem,
              quantity: Math.min(v.stockQuantity, gItem.quantity),
            });
          }
        } else {
          // UC-18 2c: Out-of-stock / discontinued lines keep chosen quantity (summed if duplicate), marked unavailable in cart UI
          if (idx >= 0) {
            current[idx] = {
              ...current[idx],
              quantity: current[idx].quantity + gItem.quantity,
            };
          } else {
            current.push({ ...gItem });
          }
        }
      }
      return { ...prev, [targetAccountId]: current };
    });
    saveGuestCart([]);
  };

  // UC-01 Step 2-3: Request Email OTP
  const requestRegisterOtp: SobieContextValue['requestRegisterOtp'] = (email) => {
    const clean = email.trim().toLowerCase();
    if (!clean || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(clean)) {
      return { ok: false, error: 'Email không hợp lệ. Vui lòng kiểm tra lại định dạng.' };
    }
    if (accounts.some((a) => a.email.toLowerCase() === clean)) {
      return { ok: false, error: 'Email đã được sử dụng.' };
    }
    const now = Date.now();
    const code = String(Math.floor(100000 + Math.random() * 900000));
    setOtpChallenge({
      email: email.trim(),
      code,
      sentAtMs: now,
      expiresAtMs: now + 5 * 60 * 1000,
      resendAvailableAtMs: now + 5 * 60 * 1000,
      wrongAttempts: 0,
      locked: false,
      verified: false,
    });
    notify(`Module notification đã gửi OTP (${code}) tới ${email.trim()} — hiệu lực 5 phút.`);
    return { ok: true, demoCode: code };
  };

  const resendRegisterOtp: SobieContextValue['resendRegisterOtp'] = () => {
    if (!otpChallenge) return { ok: false, error: 'Chưa khởi tạo yêu cầu OTP.' };
    const now = Date.now();
    if (now < otpChallenge.resendAvailableAtMs) {
      return {
        ok: false,
        error: 'Chưa đủ 5 phút kể từ lần gửi/khóa gần nhất (UC-01 AC-8).',
      };
    }
    const code = String(Math.floor(100000 + Math.random() * 900000));
    setOtpChallenge({
      ...otpChallenge,
      code,
      sentAtMs: now,
      expiresAtMs: now + 5 * 60 * 1000,
      resendAvailableAtMs: now + 5 * 60 * 1000,
      wrongAttempts: 0,
      locked: false,
      verified: false,
    });
    notify(`Đã gửi mã OTP mới (${code}) tới ${otpChallenge.email}.`);
    return { ok: true, demoCode: code };
  };

  const verifyRegisterOtp: SobieContextValue['verifyRegisterOtp'] = (code) => {
    if (!otpChallenge) return { ok: false, error: 'Vui lòng nhập email nhận OTP trước.' };
    const now = Date.now();
    if (otpChallenge.locked) {
      return {
        ok: false,
        locked429: true,
        error: 'HTTP 429: Mã OTP đã bị khóa sau 5 lần nhập sai. Vui lòng chờ hết 5 phút để gửi mã mới.',
      };
    }
    if (now > otpChallenge.expiresAtMs) {
      return { ok: false, error: 'Mã OTP đã hết hạn hiệu lực 5 phút.' };
    }
    if (code.trim() !== otpChallenge.code) {
      const nextWrong = otpChallenge.wrongAttempts + 1;
      if (nextWrong >= 5) {
        setOtpChallenge({
          ...otpChallenge,
          wrongAttempts: nextWrong,
          locked: true,
          resendAvailableAtMs: now + 5 * 60 * 1000, // AC-17 / AC-18: 5 min from 5th wrong attempt!
        });
        return {
          ok: false,
          locked429: true,
          error: 'HTTP 429: Nhập sai lần thứ 5 — mã OTP đã bị khóa. Vui lòng chờ 5 phút để yêu cầu mã mới.',
        };
      }
      setOtpChallenge({ ...otpChallenge, wrongAttempts: nextWrong });
      return {
        ok: false,
        error: `Mã OTP không đúng (đã sai ${nextWrong}/5 lần).`,
      };
    }

    setOtpChallenge({ ...otpChallenge, verified: true });
    notify('Xác minh email OTP thành công! Vui lòng tạo mật khẩu Sobie.');
    return { ok: true };
  };

  const completeOtpRegistration: SobieContextValue['completeOtpRegistration'] = (
    password,
    confirmPassword
  ) => {
    if (!otpChallenge || !otpChallenge.verified) {
      return { ok: false, error: 'Vui lòng xác minh OTP trước khi tạo mật khẩu.' };
    }
    if (!password || password.length < 6) {
      return { ok: false, error: 'Mật khẩu Sobie phải có tối thiểu 6 ký tự (UC-01 E7).' };
    }
    if (password !== confirmPassword) {
      return { ok: false, error: 'Mật khẩu xác nhận không khớp (UC-01 E7).' };
    }
    if (
      accounts.some(
        (a) => a.email.toLowerCase() === otpChallenge.email.toLowerCase()
      )
    ) {
      return { ok: false, error: 'Email đã được sử dụng.' };
    }

    const newId = `KH-20261127-${nextCounter('KH')}`;
    const newAcc: AccountRecord = {
      key: `acc-${Date.now()}`,
      accountId: newId,
      role: 'customer',
      email: otpChallenge.email,
      phone: '',
      passwordPlain: password,
      hasPassword: true,
      status: 'ACTIVE',
      name: '',
      dateOfBirth: '',
      houseNumber: '',
      ward: '',
      city: '',
      country: 'Việt Nam',
      createdAt: NOW_ISO(),
    };

    setAccounts((prev) => [newAcc, ...prev]);
    setAccountCarts((prev) => ({ ...prev, [newId]: [] }));
    setAccountWishlists((prev) => ({ ...prev, [newId]: [] }));
    const registeredEmail = otpChallenge.email;
    setOtpChallenge(null);
    notify(`Đăng ký thành công mã ${newId}! Vui lòng đăng nhập.`);
    return { ok: true, email: registeredEmail };
  };

  const resetOtpFlow = () => setOtpChallenge(null);

  // UC-02: Storefront Customer Password Login
  const loginStorefront: SobieContextValue['loginStorefront'] = (
    identifier,
    password
  ) => {
    if (!identifier.trim() || !password) {
      return { ok: false, error: 'Vui lòng nhập đầy đủ Email/SĐT và mật khẩu.' };
    }
    if (!checkPasswordRateLimit()) {
      return {
        ok: false,
        status429: true,
        error: 'HTTP 429: Quá 5 yêu cầu đăng nhập mật khẩu trong 1 phút. Vui lòng đợi hoặc dùng Google.',
      };
    }
    const idClean = identifier.trim().toLowerCase();
    const acc = accounts.find(
      (a) =>
        a.email.toLowerCase() === idClean ||
        (a.phone.trim() !== '' && a.phone.trim() === identifier.trim())
    );
    // UC-02 E1 / E4 / AC-8 / AC-18: Wrong credentials, non-customer role, or Google-only account -> generic error!
    if (
      !acc ||
      acc.role !== 'customer' ||
      !acc.hasPassword ||
      acc.passwordPlain !== password
    ) {
      return { ok: false, error: 'Thông tin đăng nhập không đúng.' };
    }
    if (acc.status === 'LOCKED') {
      return { ok: false, error: 'Tài khoản đã bị khóa.' };
    }

    mergeGuestCartIntoAccount(acc.accountId);
    setStorefrontAccountId(acc.accountId);
    notify(
      `Đăng nhập thành công (${acc.name || acc.email}) — Giỏ tạm trình duyệt đã được đồng bộ!`
    );
    return { ok: true };
  };

  // UC-01 1b & UC-02 1c/1d: Unified Google Sign-In / Sign-Up (Bypasses password rate limit!)
  const loginOrRegisterWithGoogle: SobieContextValue['loginOrRegisterWithGoogle'] = (
    googleEmail,
    googleDisplayName
  ) => {
    const emailClean = googleEmail.trim().toLowerCase();
    if (!emailClean || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailClean)) {
      return { ok: false, error: 'Email xác thực từ Google không hợp lệ.' };
    }

    const existing = accounts.find((a) => a.email.toLowerCase() === emailClean);
    if (existing) {
      if (existing.role !== 'customer') {
        return { ok: false, error: 'Thông tin đăng nhập không đúng.' };
      }
      if (existing.status === 'LOCKED') {
        return { ok: false, error: 'Tài khoản đã bị khóa.' };
      }
      // UC-02 1d / AC-17: Link googleSub if not yet linked, without OTP
      if (!existing.googleSub) {
        setAccounts((prev) =>
          prev.map((a) =>
            a.accountId === existing.accountId
              ? { ...a, googleSub: `google-sub-${Date.now()}` }
              : a
          )
        );
      }
      mergeGuestCartIntoAccount(existing.accountId);
      setStorefrontAccountId(existing.accountId);
      notify(`Đã đăng nhập Google vào tài khoản ${existing.accountId}!`);
      return { ok: true, createdNew: false };
    }

    // UC-01 1b / AC-14: Create new customer account without Sobie password & sign in immediately
    const newId = `KH-20261127-${nextCounter('KH')}`;
    const newAcc: AccountRecord = {
      key: `acc-google-${Date.now()}`,
      accountId: newId,
      role: 'customer',
      email: googleEmail.trim(),
      phone: '',
      passwordPlain: '',
      hasPassword: false,
      googleSub: `google-sub-${Date.now()}`,
      status: 'ACTIVE',
      name: googleDisplayName?.trim() ?? '',
      dateOfBirth: '',
      houseNumber: '',
      ward: '',
      city: '',
      country: 'Việt Nam',
      createdAt: NOW_ISO(),
    };
    setAccounts((prev) => [newAcc, ...prev]);
    setAccountCarts((prev) => ({ ...prev, [newId]: [] }));
    setAccountWishlists((prev) => ({ ...prev, [newId]: [] }));
    mergeGuestCartIntoAccount(newId);
    setStorefrontAccountId(newId);
    notify(`Đã tạo tài khoản Khách hàng ${newId} qua Google và cấp phiên ngay!`);
    return { ok: true, createdNew: true };
  };

  const logoutStorefront = () => {
    setStorefrontAccountId(null);
    notify('Đã đăng xuất khỏi Cổng Khách Hàng.');
  };

  // UC-02: Unified Internal Portal Login (/admin/login -> accepts ONLY employee & admin, rejects customer per E4/AC-9)
  const loginPortal: SobieContextValue['loginPortal'] = (identifier, password) => {
    if (!identifier.trim() || !password) {
      return { ok: false, error: 'Vui lòng nhập đầy đủ Email/SĐT và mật khẩu.' };
    }
    if (!checkPasswordRateLimit()) {
      return {
        ok: false,
        status429: true,
        error: 'HTTP 429: Vượt quá 5 lần thử mật khẩu trong 1 phút.',
      };
    }
    const idClean = identifier.trim().toLowerCase();
    const acc = accounts.find(
      (a) =>
        a.email.toLowerCase() === idClean ||
        (a.phone.trim() !== '' && a.phone.trim() === identifier.trim())
    );
    if (
      !acc ||
      (acc.role !== 'employee' && acc.role !== 'admin') ||
      !acc.hasPassword ||
      acc.passwordPlain !== password
    ) {
      return { ok: false, error: 'Thông tin đăng nhập không đúng.' };
    }
    if (acc.status === 'LOCKED') {
      return { ok: false, error: 'Tài khoản đã bị khóa.' };
    }
    setPortalAccountId(acc.accountId);
    notify(
      acc.role === 'admin'
        ? `Đã đăng nhập Portal Quản trị với vai trò Admin (${acc.name}) → Chuyển tới Tổng quan Tài khoản (UC-02 AC-3).`
        : `Đã đăng nhập Portal Quản trị với vai trò Nhân viên (${acc.name}) → Chuyển tới Dashboard báo cáo (UC-02 AC-3).`
    );
    return { ok: true, role: acc.role };
  };

  const logoutPortal = () => {
    setPortalAccountId(null);
    notify('Đã đăng xuất khỏi Portal Quản trị nội bộ (UC-03).');
  };

  // Dedicated Shipping Login + Public Simulator Direct Entry (UC-36 AC-1)
  const loginShippingPartner: SobieContextValue['loginShippingPartner'] = (
    stationCode,
    identifier,
    password
  ) => {
    const demo = STORE_CONFIG.shippingDemoCredentials;
    if (
      identifier.trim().toLowerCase() !== demo.email.toLowerCase() ||
      password !== demo.password
    ) {
      return { ok: false, error: 'Thông tin trạm điều phối không đúng.' };
    }
    setShippingSession({
      stationId: stationCode.trim().toUpperCase() || demo.stationCode,
      operatorName: 'Điều Phối Viên Giao Nhận',
      mode: 'authenticated',
      signedInAt: NOW_ISO(),
    });
    notify(`Đã kết nối Cổng Điều phối Vận chuyển (${stationCode || demo.stationCode}).`);
    return { ok: true };
  };

  const enterPublicShippingSimulator = () => {
    setShippingSession({
      stationId: 'PUBLIC-SIM-8001',
      operatorName: 'Chế độ Giả lập Công khai (UC-36 AC-1)',
      mode: 'public-simulator',
      signedInAt: NOW_ISO(),
    });
    notify('Đã mở Trang giả lập vận chuyển độc lập (UC-36 AC-1 — Không cần đăng nhập).');
  };

  const logoutShipping = () => {
    setShippingSession(null);
    notify('Đã rời Cổng Vận chuyển.');
  };

  // UC-04 v7: Customer updates own profile (Email is read-only on Storefront!)
  const updateCustomerProfile: SobieContextValue['updateCustomerProfile'] = (
    payload
  ) => {
    if (!storefrontUser) return { ok: false, error: 'Vui lòng đăng nhập.' };
    if (!payload.name.trim()) {
      return { ok: false, error: 'Họ và tên không được để trống.' };
    }
    const cleanPhone = payload.phone.trim();
    if (!cleanPhone || !/^[0-9+\s]{8,15}$/.test(cleanPhone)) {
      return { ok: false, error: 'Số điện thoại không hợp lệ.' };
    }
    if (
      accounts.some(
        (a) =>
          a.accountId !== storefrontUser.accountId &&
          a.phone.trim() !== '' &&
          a.phone.trim() === cleanPhone
      )
    ) {
      return { ok: false, error: 'Số điện thoại đã được sử dụng.' };
    }

    setAccounts((prev) =>
      prev.map((a) =>
        a.accountId === storefrontUser.accountId
          ? {
              ...a,
              name: payload.name.trim(),
              // UC-04 AC-2: Email on storefront profile is strictly preserved!
              phone: cleanPhone,
              dateOfBirth: payload.dateOfBirth,
              houseNumber: payload.houseNumber.trim(),
              ward: payload.ward.trim(),
              city: payload.city.trim(),
              country: payload.country.trim() || 'Việt Nam',
            }
          : a
      )
    );
    notify('Đã cập nhật hồ sơ khách hàng thành công.');
    return { ok: true };
  };

  // UC-05: Change Password revokes ALL sessions of that account including current session
  const changePassword: SobieContextValue['changePassword'] = (
    target,
    currentPassword,
    newPassword,
    confirmPassword
  ) => {
    const activeAcc = target === 'storefront' ? storefrontUser : portalUser;
    if (!activeAcc) return { ok: false, error: 'Chưa đăng nhập.' };
    if (!activeAcc.hasPassword) {
      return {
        ok: false,
        error: 'Tài khoản đăng ký qua Google chưa có mật khẩu Sobie (UC-05 Preconditions).',
      };
    }
    if (activeAcc.passwordPlain !== currentPassword) {
      return { ok: false, error: 'Mật khẩu hiện tại không đúng.' };
    }
    if (newPassword.length < 6) {
      return { ok: false, error: 'Mật khẩu mới tối thiểu 6 ký tự.' };
    }
    if (newPassword === currentPassword) {
      return { ok: false, error: 'Mật khẩu mới phải khác mật khẩu hiện tại.' };
    }
    if (newPassword !== confirmPassword) {
      return { ok: false, error: 'Mật khẩu nhập lại không khớp.' };
    }

    setAccounts((prev) =>
      prev.map((a) =>
        a.accountId === activeAcc.accountId
          ? { ...a, passwordPlain: newPassword, hasPassword: true }
          : a
      )
    );
    if (target === 'storefront') setStorefrontAccountId(null);
    if (target === 'portal') setPortalAccountId(null);
    notify(
      'Đổi mật khẩu thành công. Mọi phiên đăng nhập đã kết thúc, vui lòng đăng nhập lại.'
    );
    return { ok: true };
  };

  // UC-06: Admin creates account for ANY role
  const adminCreateAccount: SobieContextValue['adminCreateAccount'] = (
    payload
  ) => {
    if (!portalUser || portalUser.role !== 'admin') {
      return { ok: false, error: 'Chỉ Admin mới có quyền tạo tài khoản.' };
    }
    const emailClean = payload.email.trim().toLowerCase();
    const phoneClean = payload.phone.trim();
    if (!payload.name.trim() || !emailClean || !phoneClean) {
      return { ok: false, error: 'Họ tên, email và số điện thoại là bắt buộc.' };
    }
    if (payload.password.length < 6) {
      return { ok: false, error: 'Mật khẩu ban đầu tối thiểu 6 ký tự.' };
    }
    if (
      (payload.role === 'employee' || payload.role === 'admin') &&
      !payload.dateOfBirth
    ) {
      return {
        ok: false,
        error: 'Ngày sinh bắt buộc đối với Nhân viên và Admin.',
      };
    }
    if (accounts.some((a) => a.email.toLowerCase() === emailClean)) {
      return { ok: false, error: 'Email đã được sử dụng.' };
    }
    if (accounts.some((a) => a.phone !== '' && a.phone === phoneClean)) {
      return { ok: false, error: 'Số điện thoại đã được sử dụng.' };
    }

    let generatedId = '';
    if (payload.role === 'customer') {
      generatedId = `KH-20261127-${nextCounter('KH')}`;
    } else {
      const prefix = payload.role === 'admin' ? 'AD' : 'NV';
      const dobToken = payload.dateOfBirth.replace(/-/g, '');
      generatedId = `${prefix}-${toNaturalToken(payload.name)}-${dobToken}-${nextCounter(
        prefix
      )}`;
    }

    const newAcc: AccountRecord = {
      key: `acc-${Date.now()}`,
      accountId: generatedId,
      role: payload.role,
      email: payload.email.trim(),
      phone: phoneClean,
      passwordPlain: payload.password,
      hasPassword: true,
      status: 'ACTIVE',
      name: payload.name.trim(),
      dateOfBirth: payload.dateOfBirth,
      houseNumber: payload.houseNumber.trim(),
      ward: payload.ward.trim(),
      city: payload.city.trim(),
      country: 'Việt Nam',
      createdAt: NOW_ISO(),
    };
    setAccounts((prev) => [newAcc, ...prev]);
    if (payload.role === 'customer') {
      setAccountCarts((prev) => ({ ...prev, [generatedId]: [] }));
      setAccountWishlists((prev) => ({ ...prev, [generatedId]: [] }));
    }
    notify(`Đã tạo tài khoản ${generatedId} (dùng được ngay).`);
    return { ok: true };
  };

  // UC-07: Admin edits account & swaps role strictly between employee <-> admin
  const adminEditAccount: SobieContextValue['adminEditAccount'] = (
    accountId,
    payload
  ) => {
    if (!portalUser || portalUser.role !== 'admin') {
      return { ok: false, error: 'Không có quyền thực hiện.' };
    }
    const target = accounts.find((a) => a.accountId === accountId);
    if (!target) return { ok: false, error: 'Không tìm thấy tài khoản.' };

    if (
      (target.role === 'customer' && payload.role !== 'customer') ||
      (target.role !== 'customer' && payload.role === 'customer')
    ) {
      return {
        ok: false,
        error: 'Chỉ được đổi vai trò qua lại giữa Nhân viên và Admin (UC-07 E3).',
      };
    }

    const activeAdmins = accounts.filter(
      (a) => a.role === 'admin' && a.status === 'ACTIVE'
    );
    if (
      target.role === 'admin' &&
      target.status === 'ACTIVE' &&
      payload.role !== 'admin' &&
      activeAdmins.length <= 1
    ) {
      return {
        ok: false,
        error:
          'Không thể đổi vai trò của Admin đang hoạt động cuối cùng trong hệ thống (UC-07 E4).',
      };
    }

    if (
      accounts.some(
        (a) =>
          a.accountId !== accountId &&
          a.email.toLowerCase() === payload.email.trim().toLowerCase()
      )
    ) {
      return { ok: false, error: 'Email đã được sử dụng.' };
    }
    if (
      payload.phone.trim() !== '' &&
      accounts.some(
        (a) => a.accountId !== accountId && a.phone === payload.phone.trim()
      )
    ) {
      return { ok: false, error: 'Số điện thoại đã được sử dụng.' };
    }

    const roleChanged = target.role !== payload.role;
    let finalAccountId = target.accountId;
    if (
      roleChanged &&
      (payload.role === 'admin' || payload.role === 'employee')
    ) {
      const prefix = payload.role === 'admin' ? 'AD' : 'NV';
      const dob = (
        payload.dateOfBirth ||
        target.dateOfBirth ||
        '1999-01-01'
      ).replace(/-/g, '');
      finalAccountId = `${prefix}-${toNaturalToken(
        payload.name
      )}-${dob}-${nextCounter(prefix)}`;
    }

    setAccounts((prev) =>
      prev.map((a) =>
        a.accountId === accountId
          ? {
              ...a,
              accountId: finalAccountId,
              role: payload.role,
              name: payload.name.trim(),
              email: payload.email.trim(),
              phone: payload.phone.trim(),
              dateOfBirth: payload.dateOfBirth,
              houseNumber: payload.houseNumber.trim(),
              ward: payload.ward.trim(),
              city: payload.city.trim(),
            }
          : a
      )
    );

    if (roleChanged) {
      if (portalAccountId === accountId) setPortalAccountId(null);
      notify(
        `Đã đổi vai trò và cấp mã mới ${finalAccountId}. Mọi phiên đang mở đã kết thúc.`
      );
    } else {
      notify(`Đã cập nhật thông tin tài khoản ${finalAccountId}.`);
    }
    return { ok: true };
  };

  // UC-08: Admin locks / unlocks ANY role (protects last active Admin)
  const adminToggleLockAccount = (accountId: string) => {
    if (!portalUser || portalUser.role !== 'admin') {
      return { ok: false, error: 'Chỉ Admin mới có quyền khóa/mở khóa mọi vai trò.' };
    }
    const target = accounts.find((a) => a.accountId === accountId);
    if (!target) return { ok: false, error: 'Không tìm thấy tài khoản.' };

    const willLock = target.status === 'ACTIVE';
    if (willLock && target.role === 'admin') {
      const activeAdmins = accounts.filter(
        (a) => a.role === 'admin' && a.status === 'ACTIVE'
      );
      if (activeAdmins.length <= 1) {
        return {
          ok: false,
          error:
            'Không thể khóa Admin đang hoạt động cuối cùng của hệ thống (UC-08 AC-7).',
        };
      }
    }

    setAccounts((prev) =>
      prev.map((a) =>
        a.accountId === accountId
          ? { ...a, status: willLock ? 'LOCKED' : 'ACTIVE' }
          : a
      )
    );

    if (willLock) {
      if (storefrontAccountId === accountId) setStorefrontAccountId(null);
      if (portalAccountId === accountId) setPortalAccountId(null);
      notify(`Đã khóa tài khoản ${accountId} và kết thúc ngay mọi phiên đang mở.`);
    } else {
      notify(`Đã mở khóa tài khoản ${accountId}.`);
    }
    return { ok: true };
  };

  // UC-08 AC-8 / AC-9: Saler (Employee) can LOCK Customer accounts ONLY, CANNOT unlock!
  const salerLockCustomerAccount = (accountId: string) => {
    if (!portalUser || portalUser.role !== 'employee') {
      return { ok: false, error: 'Cần đăng nhập vai trò Nhân viên (Saler).' };
    }
    const target = accounts.find((a) => a.accountId === accountId);
    if (!target || target.role !== 'customer') {
      return {
        ok: false,
        error: 'Nhân viên chỉ được thao tác khóa trên tài khoản Khách hàng (UC-08 E2).',
      };
    }
    if (target.status === 'LOCKED') {
      return {
        ok: false,
        error: 'Quyền mở khóa tài khoản thuộc về Admin (UC-08 AC-9).',
      };
    }
    setAccounts((prev) =>
      prev.map((a) =>
        a.accountId === accountId ? { ...a, status: 'LOCKED' } : a
      )
    );
    if (storefrontAccountId === accountId) setStorefrontAccountId(null);
    notify(
      `Nhân viên đã khóa tài khoản Khách hàng ${accountId} và xóa mọi phiên đang mở (UC-08 AC-8).`
    );
    return { ok: true };
  };

  /* --------------------------------------------------------------------------
   * SHOPPING ACTIONS (UC-18, UC-38)
   * -------------------------------------------------------------------------- */
  const addToCart = (sku: string, productId: string, qty: number) => {
    // UC-18 Step 2 / E7: Check both parent product ACTIVE and variant ACTIVE + live DB stock
    const p = products.find((pr) => pr.id === productId);
    const v = variants.find((vr) => vr.sku === sku);
    if (!p || p.status !== 'ACTIVE' || !v || v.status !== 'ACTIVE') {
      return {
        ok: false,
        error: 'Sản phẩm hoặc phân loại này hiện không còn được bán (UC-18 E7).',
      };
    }
    if (v.stockQuantity <= 0) {
      return { ok: false, error: 'Phân loại sản phẩm hiện đã hết hàng.' };
    }
    const existing = activeCart.find((c) => c.sku === sku);
    const totalWanted = (existing?.quantity ?? 0) + qty;
    if (totalWanted > v.stockQuantity) {
      return { ok: false, error: `Chỉ còn ${v.stockQuantity} sản phẩm.` };
    }

    const nextCart = existing
      ? activeCart.map((c) =>
          c.sku === sku ? { ...c, quantity: totalWanted } : c
        )
      : [...activeCart, { sku, productId, quantity: qty }];

    if (storefrontUser) {
      setAccountCarts((prev) => ({
        ...prev,
        [storefrontUser.accountId]: nextCart,
      }));
    } else {
      saveGuestCart(nextCart);
    }
    notify(`Đã thêm ${p.name} (${v.color} / ${v.size}) vào giỏ hàng.`);
    return { ok: true };
  };

  const updateCartQty = (sku: string, nextQty: number) => {
    if (nextQty <= 0 || !Number.isInteger(nextQty)) {
      return { ok: false, error: 'Số lượng không hợp lệ.' };
    }
    const v = variants.find((vr) => vr.sku === sku);
    const maxStock = v?.stockQuantity ?? 0;
    if (nextQty > maxStock) {
      return { ok: false, error: `Chỉ còn ${maxStock} sản phẩm.` };
    }

    const nextCart = activeCart.map((c) =>
      c.sku === sku ? { ...c, quantity: nextQty } : c
    );
    if (storefrontUser) {
      setAccountCarts((prev) => ({
        ...prev,
        [storefrontUser.accountId]: nextCart,
      }));
    } else {
      saveGuestCart(nextCart);
    }
    return { ok: true };
  };

  const removeFromCart = (sku: string) => {
    const nextCart = activeCart.filter((c) => c.sku !== sku);
    if (storefrontUser) {
      setAccountCarts((prev) => ({
        ...prev,
        [storefrontUser.accountId]: nextCart,
      }));
    } else {
      saveGuestCart(nextCart);
    }
  };

  const clearUnavailableFromCart = () => {
    const nextCart = activeCart.filter((c) => {
      const p = products.find((pr) => pr.id === c.productId);
      const v = variants.find((vr) => vr.sku === c.sku);
      return (
        p &&
        p.status === 'ACTIVE' &&
        v &&
        v.status === 'ACTIVE' &&
        v.stockQuantity > 0
      );
    });
    if (storefrontUser) {
      setAccountCarts((prev) => ({
        ...prev,
        [storefrontUser.accountId]: nextCart,
      }));
    } else {
      saveGuestCart(nextCart);
    }
    notify('Đã dọn các dòng hết hàng / ngừng bán khỏi giỏ.');
  };

  // UC-38 AC-5 & UC-02 AC-23: Guest clicking heart redirects to login without auto-modifying wishlist
  const toggleWishlist = (productId: string) => {
    if (!storefrontUser) {
      notify(
        'Vui lòng đăng nhập tài khoản Khách hàng để lưu sản phẩm yêu thích (UC-38).'
      );
      return { ok: false, requireLogin: true };
    }
    const current = accountWishlists[storefrontUser.accountId] ?? [];
    const exists = current.includes(productId);
    const next = exists
      ? current.filter((id) => id !== productId)
      : [productId, ...current];
    setAccountWishlists((prev) => ({
      ...prev,
      [storefrontUser.accountId]: next,
    }));
    notify(
      exists
        ? 'Đã xóa khỏi danh sách yêu thích.'
        : 'Đã lưu vào danh sách yêu thích.'
    );
    return { ok: true };
  };

  /* --------------------------------------------------------------------------
   * ORDERING, PAYMENT & SHIPPING LIFECYCLE (UC-19 -> UC-27, UC-35, UC-36, UC-40)
   * -------------------------------------------------------------------------- */
  const placeOrder: SobieContextValue['placeOrder'] = (payload) => {
    if (!storefrontUser) {
      return { ok: false, error: 'Vui lòng đăng nhập trước khi đặt hàng.' };
    }
    if (
      !payload.customerName.trim() ||
      !payload.phone.trim() ||
      !payload.houseNumber.trim() ||
      !payload.ward.trim() ||
      !payload.city.trim()
    ) {
      return {
        ok: false,
        error: 'Vui lòng nhập đầy đủ họ tên, số điện thoại và địa chỉ nhận hàng (UC-19 E3).',
      };
    }

    const chosenCart = payload.selectedSkus
      ? activeCart.filter((c) => payload.selectedSkus!.includes(c.sku))
      : activeCart;

    if (chosenCart.length === 0) {
      return { ok: false, error: 'Vui lòng chọn ít nhất 1 sản phẩm để đặt hàng.' };
    }

    let subtotal = 0;
    const orderLines: OrderRecord['items'] = [];

    for (const c of chosenCart) {
      const p = products.find((pr) => pr.id === c.productId);
      const v = variants.find((vr) => vr.sku === c.sku);
      if (!p || p.status !== 'ACTIVE' || !v || v.status !== 'ACTIVE') {
        return {
          ok: false,
          error: `Dòng "${p?.name ?? c.sku}" không còn được bán trong Database (UC-19 E7). Đã hoàn tác giao dịch.`,
        };
      }
      if (v.stockQuantity < c.quantity || v.sellPrice === null || v.sellPrice <= 0) {
        return {
          ok: false,
          error: `Phân loại ${p.name} (${v.color}/${v.size}) không đủ tồn kho (còn ${v.stockQuantity}).`,
        };
      }
      const prodPromo = getActiveProductPromo(p.id);
      const finalUnit = calcDiscountedPrice(
        v.sellPrice,
        prodPromo?.discountPercentage
      );
      subtotal += finalUnit * c.quantity;
      orderLines.push({
        sku: v.sku,
        productId: p.id,
        productName: p.name,
        image: p.gallery[0]?.url ?? '/images/sp-0001-1.jpg',
        color: v.color,
        size: v.size,
        quantity: c.quantity,
        originalUnitPrice: v.sellPrice,
        productPromotionId: prodPromo?.promotionId,
        discountPercent: prodPromo?.discountPercentage,
        finalUnitPrice: finalUnit,
        costPriceAtSale: v.costPrice,
      });
    }

    const quote = quoteOrderDiscount(subtotal, payload.voucherCode);
    if (
      payload.voucherCode?.trim() &&
      quote.voucherError &&
      quote.selectedSource !== 'CODE'
    ) {
      return { ok: false, error: quote.voucherError };
    }

    const computedTotal =
      subtotal - quote.selectedDiscount + STORE_CONFIG.shippingFee;
    if (
      payload.expectedTotal !== undefined &&
      payload.expectedTotal !== computedTotal
    ) {
      return {
        ok: false,
        requireReconfirm: true,
        error:
          'Giá hoặc mức giảm khuyến mãi vừa thay đổi — hệ thống đã tính lại tổng thanh toán mới. Vui lòng kiểm tra và bấm xác nhận lại (UC-19 E4 / UC-31 E5).',
      };
    }

    const existingCodes = new Set(orders.map((o) => o.orderCode));
    const code = generateOrderCode(existingCodes);
    const createdIso = NOW_ISO();

    const newOrder: OrderRecord = {
      orderCode: code,
      accountId: storefrontUser.accountId,
      paymentMethod: payload.paymentMethod,
      paymentStatus: 'UNPAID',
      orderPromotionId:
        quote.selectedSource === 'ORDER' ? quote.selectedPromotionId : undefined,
      codePromotionId:
        quote.selectedSource === 'CODE' ? quote.selectedPromotionId : undefined,
      appliedPromoLabel:
        quote.selectedSource !== 'NONE'
          ? quote.selectedPromotionLabel
          : undefined,
      customerName: payload.customerName.trim(),
      customerPhone: payload.phone.trim(),
      customerHouseNumber: payload.houseNumber.trim(),
      customerWard: payload.ward.trim(),
      customerCity: payload.city.trim(),
      customerCountry: payload.country.trim() || 'Việt Nam',
      subtotalAfterProductPromo: subtotal,
      discountAmount: quote.selectedDiscount,
      shippingFee: STORE_CONFIG.shippingFee,
      totalPrice: computedTotal,
      status: 'PENDING',
      createdAt: createdIso,
      updatedAt: createdIso,
      history: [
        {
          fromStatus: null,
          toStatus: 'PENDING',
          source: 'CUSTOMER',
          changedByAccountId: storefrontUser.accountId,
          changedAt: createdIso,
        },
      ],
      items: orderLines,
    };

    // Deduct variant stock
    setVariants((prev) =>
      prev.map((vr) => {
        const line = orderLines.find((l) => l.sku === vr.sku);
        return line
          ? { ...vr, stockQuantity: vr.stockQuantity - line.quantity }
          : vr;
      })
    );

    // Increment promotion used_amount
    if (quote.selectedPromotionId) {
      setPromotions((prev) =>
        prev.map((pr) =>
          pr.promotionId === quote.selectedPromotionId
            ? { ...pr, usedAmount: pr.usedAmount + 1 }
            : pr
        )
      );
    }

    // UC-19 [GD]: Remove ONLY placed lines from customer cart!
    const placedSkuSet = new Set(orderLines.map((l) => l.sku));
    setAccountCarts((prev) => ({
      ...prev,
      [storefrontUser.accountId]: (prev[storefrontUser.accountId] ?? []).filter(
        (c) => !placedSkuSet.has(c.sku)
      ),
    }));
    setOrders((prev) => [newOrder, ...prev]);
    notify(`Đã tạo đơn hàng #${code} thành công!`);
    return { ok: true, order: newOrder };
  };

  const simulateSepayWebhook = (orderCode: string, transferAmount?: number) => {
    const target = orders.find((o) => o.orderCode === orderCode);
    if (!target) return { ok: false, error: 'Không tìm thấy đơn hàng.' };
    if (target.paymentMethod !== 'QR') {
      return { ok: false, error: 'Chỉ áp dụng cho đơn chuyển khoản QR.' };
    }
    if (target.status !== 'PENDING' || target.paymentStatus === 'PAID') {
      return {
        ok: false,
        error: 'Đơn đã thanh toán hoặc không còn ở trạng thái chờ.',
      };
    }
    const amt = transferAmount ?? target.totalPrice;
    if (amt < target.totalPrice) {
      return {
        ok: false,
        error: `Số tiền chuyển (${amt}₫) thấp hơn tổng đơn (${target.totalPrice}₫) -> lưu bank_transaction UNMATCHED, đơn giữ Chưa thanh toán.`,
      };
    }

    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === orderCode ? { ...o, paymentStatus: 'PAID' } : o
      )
    );
    notify(
      `Webhook SePay khớp thành công nội dung SOBIE${orderCode} — Đơn đã chuyển sang Đã thanh toán!`
    );
    return { ok: true };
  };

  const restoreOrderStockAndPromo = (order: OrderRecord) => {
    setVariants((prev) =>
      prev.map((vr) => {
        const line = order.items.find((i) => i.sku === vr.sku);
        return line
          ? { ...vr, stockQuantity: vr.stockQuantity + line.quantity }
          : vr;
      })
    );
    const promoId = order.codePromotionId ?? order.orderPromotionId;
    if (promoId) {
      setPromotions((prev) =>
        prev.map((pr) =>
          pr.promotionId === promoId
            ? { ...pr, usedAmount: Math.max(0, pr.usedAmount - 1) }
            : pr
        )
      );
    }
  };

  const runAutoCancelOverdueQrJob = () => {
    const nowMs = new Date('2026-11-27T19:15:00Z').getTime();
    const overdueList = orders.filter(
      (o) =>
        o.paymentMethod === 'QR' &&
        o.status === 'PENDING' &&
        o.paymentStatus === 'UNPAID' &&
        nowMs - new Date(o.createdAt).getTime() >= 24 * 3600 * 1000
    );

    if (overdueList.length === 0) {
      notify('Tác vụ UC-24: Không có đơn chuyển khoản QR nào quá hạn 24 giờ.');
      return { cancelledCount: 0 };
    }

    for (const ord of overdueList) {
      restoreOrderStockAndPromo(ord);
    }

    const overdueCodes = new Set(overdueList.map((o) => o.orderCode));
    const ts = NOW_ISO();
    setOrders((prev) =>
      prev.map((o) =>
        overdueCodes.has(o.orderCode)
          ? {
              ...o,
              status: 'CANCELLED',
              updatedAt: ts,
              history: [
                ...o.history,
                {
                  fromStatus: 'PENDING',
                  toStatus: 'CANCELLED',
                  source: 'SYSTEM',
                  note: 'Quá hạn thanh toán 24 giờ',
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );
    notify(
      `Tác vụ tự động UC-24: Đã hủy ${overdueList.length} đơn QR quá hạn 24h (${overdueList
        .map((x) => '#' + x.orderCode)
        .join(', ')}), hoàn lại tồn kho và lượt khuyến mãi.`
    );
    return { cancelledCount: overdueList.length };
  };

  const customerCancelOrder = (orderCode: string) => {
    if (!storefrontUser) return { ok: false, error: 'Vui lòng đăng nhập.' };
    const target = orders.find(
      (o) =>
        o.orderCode === orderCode && o.accountId === storefrontUser.accountId
    );
    if (!target) return { ok: false, error: 'Không tìm thấy đơn hàng.' };
    if (target.status !== 'PENDING') {
      return {
        ok: false,
        error: `Đơn đang ở trạng thái khác; Khách hàng chỉ hủy được khi đơn «Chưa xử lý» (UC-22 E1).`,
      };
    }

    restoreOrderStockAndPromo(target);
    const ts = NOW_ISO();
    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === orderCode
          ? {
              ...o,
              status: 'CANCELLED',
              updatedAt: ts,
              history: [
                ...o.history,
                {
                  fromStatus: 'PENDING',
                  toStatus: 'CANCELLED',
                  source: 'CUSTOMER',
                  changedByAccountId: storefrontUser.accountId,
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );
    notify(`Đã hủy đơn hàng #${orderCode}, hoàn lại tồn kho và lượt khuyến mãi.`);
    return { ok: true };
  };

  const employeeConfirmOrder = (orderCode: string) => {
    if (!portalUser || portalUser.role !== 'employee') {
      return { ok: false, error: 'Chỉ Nhân viên (Saler) mới được xác nhận đơn.' };
    }
    const target = orders.find((o) => o.orderCode === orderCode);
    if (!target) return { ok: false, error: 'Không tìm thấy đơn hàng.' };
    if (target.status !== 'PENDING') {
      return { ok: false, error: 'Đơn không còn ở trạng thái Chưa xử lý.' };
    }
    if (target.paymentMethod === 'QR' && target.paymentStatus !== 'PAID') {
      return {
        ok: false,
        error: 'Không cho xác nhận đơn chuyển khoản QR khi chưa thanh toán (UC-23).',
      };
    }

    const ts = NOW_ISO();
    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === orderCode
          ? {
              ...o,
              status: 'CONFIRMED',
              updatedAt: ts,
              history: [
                ...o.history,
                {
                  fromStatus: 'PENDING',
                  toStatus: 'CONFIRMED',
                  source: 'EMPLOYEE',
                  changedByAccountId: portalUser.accountId,
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );
    notify(`Đã xác nhận đơn #${orderCode}. Đơn sẵn sàng bàn giao vận chuyển.`);
    return { ok: true };
  };

  const employeeCancelOrder = (orderCode: string, reason: string) => {
    if (!portalUser || portalUser.role !== 'employee') {
      return { ok: false, error: 'Chỉ Nhân viên (Saler) mới có quyền hủy đơn.' };
    }
    const cleanReason = reason.trim();
    if (!cleanReason) {
      return { ok: false, error: 'Vui lòng nhập lý do hủy đơn (UC-22 E3).' };
    }
    if (cleanReason.length > 500) {
      return { ok: false, error: 'Lý do hủy tối đa 500 ký tự (UC-22 E3).' };
    }
    const target = orders.find((o) => o.orderCode === orderCode);
    if (!target) return { ok: false, error: 'Không tìm thấy đơn hàng.' };
    if (!['PENDING', 'CONFIRMED', 'AWAITING_PICKUP'].includes(target.status)) {
      return {
        ok: false,
        error:
          'Không thể hủy đơn sau khi đơn vị vận chuyển đã nhận hàng hoặc đơn đã kết thúc (UC-22 E2 / E6).',
      };
    }

    restoreOrderStockAndPromo(target);
    const ts = NOW_ISO();
    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === orderCode
          ? {
              ...o,
              status: 'CANCELLED',
              updatedAt: ts,
              history: [
                ...o.history,
                {
                  fromStatus: target.status,
                  toStatus: 'CANCELLED',
                  source: 'EMPLOYEE',
                  changedByAccountId: portalUser.accountId,
                  note: cleanReason,
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );
    notify(
      `Đã hủy đơn #${orderCode}, hoàn lại tồn kho và lượt khuyến mãi (khách không thấy lý do nội bộ).`
    );
    return { ok: true };
  };

  // UC-40 v4: Single-order handoff with distinct E1 vs E2 messages
  const employeeHandoffOrder = (orderCode: string) => {
    if (!portalUser || portalUser.role !== 'employee') {
      return { ok: false, error: 'Chỉ Nhân viên mới có quyền bàn giao vận chuyển.' };
    }
    const target = orders.find(
      (o) => o.orderCode.toUpperCase() === orderCode.trim().toUpperCase()
    );
    if (!target) {
      return { ok: false, error: 'Không tìm thấy đơn hàng (UC-40 E2).' };
    }
    if (target.status !== 'CONFIRMED') {
      return {
        ok: false,
        error: `Đơn đang ở trạng thái «${ORDER_STATUS_META_LABELS[target.status]}»; chỉ bàn giao được khi đơn «Đã xác nhận» (UC-40 E1).`,
      };
    }

    const ts = NOW_ISO();
    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === target.orderCode
          ? {
              ...o,
              status: 'AWAITING_PICKUP',
              updatedAt: ts,
              history: [
                ...o.history,
                {
                  fromStatus: 'CONFIRMED',
                  toStatus: 'AWAITING_PICKUP',
                  source: 'EMPLOYEE',
                  changedByAccountId: portalUser.accountId,
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );
    notify(
      `Đã bàn giao đơn #${target.orderCode} sang Cổng Vận chuyển (Chờ lấy hàng).`
    );
    return { ok: true };
  };

  // UC-36 + UC-26 (Auto Invoice) + UC-35 (Auto Restock on Failed Delivery)
  const carrierUpdateShipment: SobieContextValue['carrierUpdateShipment'] = (
    orderCode,
    action
  ) => {
    const transitions = {
      received: { from: 'AWAITING_PICKUP', to: 'SHIPPING', label: 'Đang giao' },
      delivered: {
        from: 'SHIPPING',
        to: 'DELIVERED',
        label: 'Giao thành công',
      },
      failed: {
        from: 'SHIPPING',
        to: 'DELIVERY_FAILED',
        label: 'Giao không thành công',
      },
    } as const;

    const rule = transitions[action];
    const target = orders.find(
      (o) => o.orderCode.toUpperCase() === orderCode.trim().toUpperCase()
    );
    if (!target) {
      return { ok: false, error: 'Không tìm thấy đơn hàng (UC-36 E2).' };
    }
    if (target.status !== rule.from) {
      return {
        ok: false,
        error: `Đơn đang ở trạng thái «${ORDER_STATUS_META_LABELS[target.status]}», không thể thực hiện thao tác này (UC-36 E1).`,
      };
    }

    const ts = NOW_ISO();

    // UC-35: Restore stock on failed delivery (even if product/variant is INACTIVE!)
    if (rule.to === 'DELIVERY_FAILED') {
      setVariants((prev) =>
        prev.map((vr) => {
          const line = target.items.find((i) => i.sku === vr.sku);
          return line
            ? { ...vr, stockQuantity: vr.stockQuantity + line.quantity }
            : vr;
        })
      );
    }

    // UC-26: Issue read-only snapshot Invoice HD-<orderCode> & mark COD as PAID on DELIVERED
    if (rule.to === 'DELIVERED') {
      const custAcc = accounts.find((a) => a.accountId === target.accountId);
      const rawSubtotal = target.items.reduce(
        (s, l) => s + l.originalUnitPrice * l.quantity,
        0
      );
      const prodDisc = target.items.reduce(
        (s, l) => s + (l.originalUnitPrice - l.finalUnitPrice) * l.quantity,
        0
      );
      const snap: InvoiceSnapshot = {
        invoiceId: `HD-${target.orderCode}`,
        orderCode: target.orderCode,
        createdAt: ts,
        paymentMethod: target.paymentMethod,
        customer: {
          name: target.customerName,
          phone: target.customerPhone,
          email: custAcc?.email ?? '',
          address: [
            target.customerHouseNumber,
            target.customerWard,
            target.customerCity,
            target.customerCountry,
          ]
            .filter(Boolean)
            .join(', '),
        },
        items: target.items.map((l) => ({
          productName: l.productName,
          sku: l.sku,
          color: l.color,
          size: l.size,
          unitPrice: l.originalUnitPrice,
          discountedUnitPrice: l.finalUnitPrice,
          quantity: l.quantity,
          discountAmount: (l.originalUnitPrice - l.finalUnitPrice) * l.quantity,
        })),
        subtotal: rawSubtotal,
        productDiscount: prodDisc,
        orderDiscount: target.discountAmount,
        shippingFee: target.shippingFee,
        totalPayment: target.totalPrice,
      };
      setInvoices((prev) => [
        snap,
        ...prev.filter((inv) => inv.orderCode !== target.orderCode),
      ]);
    }

    setOrders((prev) =>
      prev.map((o) =>
        o.orderCode === target.orderCode
          ? {
              ...o,
              status: rule.to,
              paymentStatus:
                rule.to === 'DELIVERED' ? 'PAID' : o.paymentStatus,
              updatedAt: ts,
              deliveredAt: rule.to === 'DELIVERED' ? ts : o.deliveredAt,
              history: [
                ...o.history,
                {
                  fromStatus: rule.from,
                  toStatus: rule.to,
                  source: 'SHIPPING_SIMULATOR',
                  changedAt: ts,
                },
              ],
            }
          : o
      )
    );

    return { ok: true, statusLabel: rule.label };
  };

  /* --------------------------------------------------------------------------
   * CATALOG MANAGEMENT (UC-14 -> UC-17 + CONFIRMED Receipt Freeze UC-14-Q11)
   * -------------------------------------------------------------------------- */
  const saveProduct: SobieContextValue['saveProduct'] = (payload) => {
    const trimmedName = payload.name.trim();
    if (!trimmedName) return { ok: false, error: 'Tên sản phẩm là bắt buộc.' };

    // UC-14-Q9: Unique LOWER(TRIM(product_name))
    if (
      products.some(
        (p) =>
          p.id !== payload.id &&
          p.name.trim().toLowerCase() === trimmedName.toLowerCase()
      )
    ) {
      return {
        ok: false,
        error: 'Tên sản phẩm đã tồn tại (không phân biệt hoa/thường sau khi trim — UC-14-Q9).',
      };
    }

    if (payload.id) {
      const existing = products.find((p) => p.id === payload.id);
      if (!existing) return { ok: false, error: 'Không tìm thấy sản phẩm.' };

      // UC-14-Q11: Once product has a CONFIRMED receipt, ONLY description may be updated!
      if (hasConfirmedReceiptForProduct(payload.id)) {
        setProducts((prev) =>
          prev.map((p) =>
            p.id === payload.id
              ? { ...p, description: payload.description.trim() }
              : p
          )
        );
        notify(
          `Sản phẩm ${payload.id} đã có phiếu nhập Đã xác nhận — chỉ cập nhật Mô tả, giữ nguyên các trường đã khóa (UC-14-Q11).`
        );
        return { ok: true };
      }

      if (!payload.category || !payload.gender) {
        return { ok: false, error: 'Danh mục và Giới tính là trường bắt buộc.' };
      }
      if (existing.status === 'ACTIVE' && payload.gallery.length === 0) {
        return {
          ok: false,
          error: 'Sản phẩm Đang bán phải có ít nhất 1 ảnh gallery (UC-14 Q7).',
        };
      }

      const normalizedGallery =
        payload.gallery.length > 0
          ? payload.gallery.map((g, idx) => ({ orderNo: idx + 1, url: g.url }))
          : [{ orderNo: 1, url: '/images/prod-olive-onepiece.jpg' }];

      setProducts((prev) =>
        prev.map((p) =>
          p.id === payload.id
            ? {
                ...p,
                name: trimmedName,
                subtitle: payload.subtitle.trim(),
                description: payload.description.trim(),
                category: payload.category,
                gender: payload.gender,
                collections: payload.collections,
                gallery: normalizedGallery,
              }
            : p
        )
      );
      notify(`Đã cập nhật sản phẩm ${payload.id}.`);
      return { ok: true };
    }

    if (!payload.category) return { ok: false, error: 'Danh mục là bắt buộc.' };
    if (!payload.gender) return { ok: false, error: 'Giới tính là bắt buộc.' };

    const normalizedGallery =
      payload.gallery.length > 0
        ? payload.gallery.map((g, idx) => ({ orderNo: idx + 1, url: g.url }))
        : [{ orderNo: 1, url: '/images/prod-olive-onepiece.jpg' }];

    const nums = products.map(
      (p) => parseInt(p.id.replace('SP-', ''), 10) || 0
    );
    const nextNum = (nums.length ? Math.max(...nums) : 0) + 1;
    const newId = `SP-${String(nextNum).padStart(4, '0')}`;

    const newProd: ProductRecord = {
      id: newId,
      name: trimmedName,
      subtitle: payload.subtitle.trim() || 'Thiết kế đồ bơi Sobie Atelier',
      description: payload.description.trim(),
      status: 'INACTIVE', // UC-14: newly created product starts as INACTIVE!
      category: payload.category,
      gender: payload.gender,
      collections: payload.collections,
      gallery: normalizedGallery,
      createdAt: TODAY_STR,
    };
    setProducts((prev) => [newProd, ...prev]);
    notify(
      `Đã tạo sản phẩm ${newId} ở trạng thái Ngừng bán. Hãy thêm biến thể & đặt giá size trước khi mở bán.`
    );
    return { ok: true };
  };

  const toggleProductStatus = (productId: string) => {
    const prod = products.find((p) => p.id === productId);
    if (!prod) return { ok: false, error: 'Không tìm thấy sản phẩm.' };

    if (hasConfirmedReceiptForProduct(productId)) {
      return {
        ok: false,
        error: `Sản phẩm ${productId} đã có phiếu nhập Đã xác nhận — đã khóa đổi trạng thái bán (UC-14-Q11).`,
      };
    }

    if (prod.status === 'INACTIVE') {
      if (prod.gallery.length === 0) {
        return {
          ok: false,
          error: 'Sản phẩm phải có ít nhất 1 ảnh gallery mới được mở bán (UC-14).',
        };
      }
      const pVars = variants.filter((v) => v.productId === productId);
      if (pVars.length === 0) {
        return {
          ok: false,
          error: 'Sản phẩm chưa có biến thể nào — không thể chuyển sang Đang bán.',
        };
      }
      const missingSize = pVars.find((v) => !v.sellPrice || v.sellPrice <= 0);
      if (missingSize) {
        return {
          ok: false,
          error: `Size ${missingSize.size} chưa có giá bán > 0 — vui lòng đặt giá theo size (UC-16) trước.`,
        };
      }
    }

    const nextStatus = prod.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    setProducts((prev) =>
      prev.map((p) => (p.id === productId ? { ...p, status: nextStatus } : p))
    );
    notify(
      `Đã chuyển ${productId} sang trạng thái ${
        nextStatus === 'ACTIVE' ? 'Đang bán' : 'Ngừng bán'
      }.`
    );
    return { ok: true };
  };

  // UC-14 Q2/Q6: Block delete if in orders, in any receipt, ever had product promo, or stock > 0
  const deleteProduct = (productId: string) => {
    const pVars = variants.filter((v) => v.productId === productId);
    const pSkus = pVars.map((v) => v.sku);
    const hasStock = pVars.some((v) => v.stockQuantity > 0);
    const inOrders = orders.some((o) =>
      o.items.some((i) => i.productId === productId || pSkus.includes(i.sku))
    );
    const inReceipts = receipts.some((r) =>
      r.lines.some((l) => pSkus.includes(l.sku))
    );
    const hadPromo = promotions.some(
      (pr) => pr.type === 'PRODUCT' && pr.productId === productId
    );
    if (hasStock || inOrders || inReceipts || hadPromo) {
      return {
        ok: false,
        error:
          'Chặn xóa (UC-14): Sản phẩm còn tồn kho hoặc đã từng liên kết đơn hàng, phiếu nhập (kể cả nháp) hoặc khuyến mãi sản phẩm.',
      };
    }
    setVariants((prev) => prev.filter((v) => v.productId !== productId));
    setProducts((prev) => prev.filter((p) => p.id !== productId));
    notify(`Đã xóa sản phẩm ${productId} và dọn dữ liệu biến thể/tồn kho.`);
    return { ok: true };
  };

  const generateVariantsMatrix: SobieContextValue['generateVariantsMatrix'] = (
    productId,
    selectedColors,
    selectedSizes
  ) => {
    if (hasConfirmedReceiptForProduct(productId)) {
      return {
        ok: false,
        error: `Sản phẩm ${productId} đã có phiếu nhập Đã xác nhận — khóa thêm biến thể mới (UC-15 / UC-14-Q11).`,
      };
    }
    if (selectedColors.length === 0 || selectedSizes.length === 0) {
      return { ok: false, error: 'Vui lòng chọn ít nhất 1 màu và 1 size.' };
    }
    const prod = products.find((p) => p.id === productId);
    const newItems: VariantRecord[] = [];
    for (const c of selectedColors) {
      for (const s of selectedSizes) {
        const exists = variants.some(
          (v) => v.productId === productId && v.color === c && v.size === s
        );
        if (exists) continue;
        const sameSizeVar = variants.find(
          (v) =>
            v.productId === productId && v.size === s && v.sellPrice !== null
        );
        // If product is ACTIVE, any newly added size must already have price > 0!
        if (
          prod?.status === 'ACTIVE' &&
          (!sameSizeVar?.sellPrice || sameSizeVar.sellPrice <= 0)
        ) {
          return {
            ok: false,
            error: `Sản phẩm đang ACTIVE: chưa thể thêm size mới "${s}" khi chưa có giá > 0. Hãy chuyển INACTIVE trước (UC-14 bất biến).`,
          };
        }
        const sku = `${productId}-${toNaturalToken(c)}-${toNaturalToken(s)}`;
        newItems.push({
          sku,
          productId,
          color: c,
          size: s,
          sellPrice: sameSizeVar?.sellPrice ?? null,
          status: 'ACTIVE',
          stockQuantity: 0,
          costPrice: 0,
        });
      }
    }
    if (newItems.length > 0) {
      setVariants((prev) => [...prev, ...newItems]);
    }
    notify(
      `Đã tạo thêm ${newItems.length} biến thể mới (tồn kho & giá vốn ban đầu = 0).`
    );
    return { ok: true, createdCount: newItems.length };
  };

  const toggleVariantStatus = (sku: string) => {
    const target = variants.find((v) => v.sku === sku);
    if (!target) return { ok: false, error: 'Không tìm thấy biến thể.' };
    if (hasConfirmedReceiptForProduct(target.productId)) {
      return {
        ok: false,
        error: 'Sản phẩm đã có phiếu nhập Đã xác nhận — khóa đổi trạng thái biến thể (UC-15 E7).',
      };
    }
    const nextStatus = target.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    setVariants((prev) =>
      prev.map((v) => (v.sku === sku ? { ...v, status: nextStatus } : v))
    );
    notify(
      `Đã chuyển biến thể ${sku} sang ${
        nextStatus === 'ACTIVE' ? 'Đang bán' : 'Ngừng bán'
      }.`
    );
    return { ok: true };
  };

  const deleteVariant = (sku: string) => {
    const target = variants.find((v) => v.sku === sku);
    if (!target) return { ok: false, error: 'Không tìm thấy biến thể.' };
    if (hasConfirmedReceiptForProduct(target.productId)) {
      return {
        ok: false,
        error: 'Sản phẩm đã có phiếu nhập Đã xác nhận — khóa xóa biến thể (UC-15).',
      };
    }
    const siblingCount = variants.filter(
      (v) => v.productId === target.productId
    ).length;
    const prod = products.find((p) => p.id === target.productId);
    if (prod?.status === 'ACTIVE' && siblingCount <= 1) {
      return {
        ok: false,
        error: 'Không thể xóa biến thể cuối cùng khi sản phẩm cha đang ACTIVE (UC-14).',
      };
    }
    const used =
      target.stockQuantity > 0 ||
      orders.some((o) => o.items.some((i) => i.sku === sku)) ||
      receipts.some((r) => r.lines.some((l) => l.sku === sku));
    if (used) {
      return {
        ok: false,
        error: 'Biến thể còn tồn kho hoặc đã có trong đơn hàng / phiếu nhập — không thể xóa (UC-15).',
      };
    }
    setVariants((prev) => prev.filter((v) => v.sku !== sku));
    notify(`Đã xóa biến thể ${sku}.`);
    return { ok: true };
  };

  const updateSizePrices: SobieContextValue['updateSizePrices'] = (
    productId,
    sizePriceMap
  ) => {
    if (hasConfirmedReceiptForProduct(productId)) {
      return {
        ok: false,
        error: `Sản phẩm ${productId} đã có phiếu nhập Đã xác nhận — không được đổi giá bán nữa (UC-16 / UC-14-Q11).`,
      };
    }
    for (const [sz, val] of Object.entries(sizePriceMap)) {
      if (!Number.isInteger(val) || val <= 0) {
        return {
          ok: false,
          error: `Giá bán của size ${sz} phải là số nguyên dương VND.`,
        };
      }
    }
    setVariants((prev) =>
      prev.map((v) =>
        v.productId === productId && sizePriceMap[v.size] !== undefined
          ? { ...v, sellPrice: sizePriceMap[v.size] }
          : v
      )
    );
    notify(`Đã lưu bảng giá theo size cho sản phẩm ${productId}.`);
    return { ok: true };
  };

  const manageTaxonomy: SobieContextValue['manageTaxonomy'] = (
    kind,
    action,
    value,
    newValue,
    hex
  ) => {
    const clean = value.trim();
    const cleanNew = (newValue ?? '').trim();

    if (action === 'add') {
      if (!clean) return { ok: false, error: 'Tên không được để trống.' };
      const list =
        kind === 'category'
          ? categories
          : kind === 'collection'
          ? collections
          : kind === 'gender'
          ? genders
          : kind === 'size'
          ? sizes
          : colors.map((c) => c.name);
      if (list.some((x) => x.toLowerCase() === clean.toLowerCase())) {
        return { ok: false, error: 'Tên thuộc tính đã tồn tại.' };
      }
      if (kind === 'category') setCategories((p) => [...p, clean]);
      if (kind === 'collection') setCollections((p) => [...p, clean]);
      if (kind === 'gender') setGenders((p) => [...p, clean]);
      if (kind === 'size') setSizes((p) => [...p, clean]);
      if (kind === 'color')
        setColors((p) => [...p, { name: clean, hex: hex ?? '#4A5D43' }]);
      notify(`Đã thêm "${clean}".`);
      return { ok: true };
    }

    if (action === 'rename') {
      if (!cleanNew) return { ok: false, error: 'Tên mới không được để trống.' };

      // UC-17-Q7: Block renaming taxonomy linked to any product with CONFIRMED receipt!
      const lockedByConfirmed = products.some((p) => {
        if (!hasConfirmedReceiptForProduct(p.id)) return false;
        if (kind === 'category') return p.category === clean;
        if (kind === 'collection') return p.collections.includes(clean);
        if (kind === 'gender') return p.gender === clean;
        const pVars = variants.filter((v) => v.productId === p.id);
        if (kind === 'size') return pVars.some((v) => v.size === clean);
        if (kind === 'color') return pVars.some((v) => v.color === clean);
        return false;
      });
      if (lockedByConfirmed) {
        return {
          ok: false,
          error: `Không thể đổi tên "${clean}" vì đang gắn với sản phẩm đã có phiếu nhập Đã xác nhận (UC-17-Q7).`,
        };
      }

      if (kind === 'category') {
        setCategories((p) => p.map((x) => (x === clean ? cleanNew : x)));
        setProducts((p) =>
          p.map((pr) =>
            pr.category === clean ? { ...pr, category: cleanNew } : pr
          )
        );
      } else if (kind === 'collection') {
        setCollections((p) => p.map((x) => (x === clean ? cleanNew : x)));
        setProducts((p) =>
          p.map((pr) => ({
            ...pr,
            collections: pr.collections.map((c) =>
              c === clean ? cleanNew : c
            ),
          }))
        );
      } else if (kind === 'gender') {
        setGenders((p) => p.map((x) => (x === clean ? cleanNew : x)));
        setProducts((p) =>
          p.map((pr) =>
            pr.gender === clean ? { ...pr, gender: cleanNew } : pr
          )
        );
      } else if (kind === 'size') {
        setSizes((p) => p.map((x) => (x === clean ? cleanNew : x)));
        setVariants((v) =>
          v.map((vr) => (vr.size === clean ? { ...vr, size: cleanNew } : vr))
        );
      } else if (kind === 'color') {
        setColors((p) =>
          p.map((c) =>
            c.name === clean ? { name: cleanNew, hex: hex ?? c.hex } : c
          )
        );
        setVariants((v) =>
          v.map((vr) => (vr.color === clean ? { ...vr, color: cleanNew } : vr))
        );
      }
      notify(`Đã đổi tên thành "${cleanNew}".`);
      return { ok: true };
    }

    let usageCount = 0;
    if (kind === 'category')
      usageCount = products.filter((p) => p.category === clean).length;
    if (kind === 'collection')
      usageCount = products.filter((p) => p.collections.includes(clean)).length;
    if (kind === 'gender')
      usageCount = products.filter((p) => p.gender === clean).length;
    if (kind === 'size')
      usageCount = variants.filter((v) => v.size === clean).length;
    if (kind === 'color')
      usageCount = variants.filter((v) => v.color === clean).length;

    if (usageCount > 0) {
      return {
        ok: false,
        error: `Đang có ${usageCount} sản phẩm/biến thể sử dụng "${clean}" — không thể xóa (UC-17).`,
      };
    }

    if (kind === 'category') setCategories((p) => p.filter((x) => x !== clean));
    if (kind === 'collection')
      setCollections((p) => p.filter((x) => x !== clean));
    if (kind === 'gender') setGenders((p) => p.filter((x) => x !== clean));
    if (kind === 'size') setSizes((p) => p.filter((x) => x !== clean));
    if (kind === 'color') setColors((p) => p.filter((c) => c.name !== clean));
    notify(`Đã xóa "${clean}".`);
    return { ok: true };
  };

  /* --------------------------------------------------------------------------
   * PROMOTION MANAGEMENT (UC-28, UC-29, UC-30)
   * -------------------------------------------------------------------------- */
  const createPromotion: SobieContextValue['createPromotion'] = (payload) => {
    if (
      !payload.discountPercentage ||
      payload.discountPercentage <= 0 ||
      payload.discountPercentage >= 100
    ) {
      return {
        ok: false,
        error: 'Phần trăm giảm phải lớn hơn 0 và nhỏ hơn 100.',
      };
    }

    if (payload.type === 'PRODUCT') {
      if (!payload.productId) return { ok: false, error: 'Vui lòng chọn sản phẩm.' };
      const existingActive = promotions.find(
        (p) =>
          p.type === 'PRODUCT' &&
          p.productId === payload.productId &&
          p.status === 'ENABLED'
      );
      if (existingActive) {
        return {
          ok: false,
          error: `Sản phẩm ${payload.productId} đang có khuyến mãi ${existingActive.promotionId} hiệu lực. Hãy kết thúc trước khi tạo mới.`,
        };
      }
    } else {
      if (payload.thresholdPrice === undefined || payload.thresholdPrice < 0) {
        return { ok: false, error: 'Giá trị đơn tối thiểu không hợp lệ.' };
      }
      if (!payload.quantity || payload.quantity < 1) {
        return { ok: false, error: 'Số lượt áp dụng tối đa phải từ 1 trở lên.' };
      }
      if (!payload.startDate || !payload.endDate) {
        return {
          ok: false,
          error: 'Vui lòng chọn ngày bắt đầu và ngày kết thúc (Asia/Ho_Chi_Minh).',
        };
      }
      if (payload.endDate < payload.startDate) {
        return {
          ok: false,
          error: 'Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.',
        };
      }
      if (payload.type === 'CODE') {
        const cleanCode = (payload.code ?? '').trim().toUpperCase();
        if (!cleanCode) return { ok: false, error: 'Vui lòng nhập mã voucher.' };
        if (
          promotions.some(
            (p) => p.type === 'CODE' && p.code?.toUpperCase() === cleanCode
          )
        ) {
          return {
            ok: false,
            error: 'Mã voucher đã tồn tại (không phân biệt hoa thường).',
          };
        }
      }
    }

    const nums = promotions.map(
      (p) => parseInt(p.promotionId.replace('KM-', ''), 10) || 0
    );
    const nextNum = (nums.length ? Math.max(...nums) : 0) + 1;
    const newPromoId = `KM-${String(nextNum).padStart(4, '0')}`;

    const newPromo: PromotionRecord = {
      promotionId: newPromoId,
      type: payload.type,
      discountPercentage: payload.discountPercentage,
      status: 'ENABLED',
      usedAmount: 0,
      productId: payload.type === 'PRODUCT' ? payload.productId : undefined,
      thresholdPrice:
        payload.type !== 'PRODUCT' ? payload.thresholdPrice : undefined,
      quantity: payload.type !== 'PRODUCT' ? payload.quantity : undefined,
      startDate: payload.type !== 'PRODUCT' ? payload.startDate : undefined,
      endDate: payload.type !== 'PRODUCT' ? payload.endDate : undefined,
      code:
        payload.type === 'CODE' ? payload.code?.trim().toUpperCase() : undefined,
    };

    setPromotions((prev) => [newPromo, ...prev]);
    notify(`Đã tạo chương trình khuyến mãi ${newPromoId}.`);
    return { ok: true };
  };

  const endPromotion = (promotionId: string) => {
    const target = promotions.find((p) => p.promotionId === promotionId);
    if (!target || getPromotionDisplayStatus(target) === 'Đã kết thúc') {
      return { ok: false, error: 'Khuyến mãi không tồn tại hoặc đã kết thúc.' };
    }
    setPromotions((prev) =>
      prev.map((p) =>
        p.promotionId === promotionId ? { ...p, status: 'DISABLED' } : p
      )
    );
    notify(`Đã kết thúc chương trình ${promotionId} (giữ nguyên mốc ngày kết thúc cũ).`);
    return { ok: true };
  };

  /* --------------------------------------------------------------------------
   * INVENTORY MANAGEMENT (UC-32 -> UC-34)
   * -------------------------------------------------------------------------- */
  const saveSupplier: SobieContextValue['saveSupplier'] = (payload) => {
    const cleanName = payload.name.trim();
    if (!cleanName || !payload.phone.trim()) {
      return {
        ok: false,
        error: 'Tên nhà cung cấp và số điện thoại là bắt buộc.',
      };
    }
    // UC-32: Trim + case-insensitive, accent-sensitive uniqueness across ALL suppliers (even INACTIVE)
    if (
      suppliers.some(
        (s) =>
          s.supplierId !== payload.supplierId &&
          s.name.trim().toLowerCase() === cleanName.toLowerCase()
      )
    ) {
      return {
        ok: false,
        error: 'Tên nhà cung cấp đã tồn tại (kể cả nhà cung cấp ngừng hợp tác — UC-32).',
      };
    }

    if (payload.supplierId) {
      setSuppliers((prev) =>
        prev.map((s) =>
          s.supplierId === payload.supplierId
            ? {
                ...s,
                name: cleanName,
                phone: payload.phone.trim(),
                email: payload.email.trim(),
                address: payload.address.trim(),
              }
            : s
        )
      );
      notify(`Đã cập nhật nhà cung cấp ${payload.supplierId}.`);
      return { ok: true };
    }

    const nums = suppliers.map(
      (s) => parseInt(s.supplierId.replace('NCC-', ''), 10) || 0
    );
    const nextId = `NCC-${String(
      (nums.length ? Math.max(...nums) : 0) + 1
    ).padStart(4, '0')}`;
    setSuppliers((prev) => [
      {
        supplierId: nextId,
        name: cleanName,
        phone: payload.phone.trim(),
        email: payload.email.trim(),
        address: payload.address.trim(),
        status: 'ACTIVE',
      },
      ...prev,
    ]);
    notify(`Đã thêm nhà cung cấp ${nextId}.`);
    return { ok: true };
  };

  const toggleSupplierStatus = (supplierId: string) => {
    setSuppliers((prev) =>
      prev.map((s) =>
        s.supplierId === supplierId
          ? { ...s, status: s.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE' }
          : s
      )
    );
  };

  const deleteSupplier = (supplierId: string) => {
    if (receipts.some((r) => r.supplierId === supplierId)) {
      return {
        ok: false,
        error:
          'Nhà cung cấp đã có phiếu nhập tham chiếu — từ chối xóa, vui lòng chuyển sang «Ngừng hợp tác» (UC-32).',
      };
    }
    setSuppliers((prev) => prev.filter((s) => s.supplierId !== supplierId));
    notify(`Đã xóa nhà cung cấp ${supplierId}.`);
    return { ok: true };
  };

  const saveDraftReceipt: SobieContextValue['saveDraftReceipt'] = (payload) => {
    if (!portalUser || portalUser.role !== 'employee') {
      return { ok: false, error: 'Chỉ Nhân viên mới được lập phiếu nhập.' };
    }
    const sup = suppliers.find(
      (s) => s.supplierId === payload.supplierId && s.status === 'ACTIVE'
    );
    if (!sup) {
      return {
        ok: false,
        error: 'Chỉ được chọn/lưu phiếu với nhà cung cấp Đang hợp tác (UC-33).',
      };
    }
    if (payload.lines.length === 0) {
      return { ok: false, error: 'Phiếu nhập phải có ít nhất 1 dòng biến thể.' };
    }
    const skuSet = new Set<string>();
    for (const l of payload.lines) {
      if (skuSet.has(l.sku)) {
        return {
          ok: false,
          error: `Biến thể ${l.sku} bị lặp — mỗi biến thể chỉ xuất hiện 1 dòng trong 1 phiếu (UC-33).`,
        };
      }
      skuSet.add(l.sku);
      if (!Number.isInteger(l.quantity) || l.quantity <= 0) {
        return {
          ok: false,
          error: `Số lượng của ${l.sku} phải là số nguyên dương.`,
        };
      }
      if (!Number.isInteger(l.unitPrice) || l.unitPrice < 0) {
        return {
          ok: false,
          error: `Giá nhập của ${l.sku} phải là số nguyên VND ≥ 0.`,
        };
      }
    }

    const builtLines = payload.lines.map((l) => ({
      sku: l.sku,
      quantity: l.quantity,
      unitPrice: l.unitPrice,
      totalPrice: l.quantity * l.unitPrice,
    }));
    const finalPrice = builtLines.reduce((s, l) => s + l.totalPrice, 0);

    if (payload.receiptId) {
      const existing = receipts.find((r) => r.receiptId === payload.receiptId);
      if (!existing || existing.status !== 'DRAFT') {
        return { ok: false, error: 'Chỉ sửa được phiếu nhập ở trạng thái Nháp.' };
      }
      setReceipts((prev) =>
        prev.map((r) =>
          r.receiptId === payload.receiptId
            ? {
                ...r,
                supplierId: payload.supplierId,
                lines: builtLines,
                finalPrice,
              }
            : r
        )
      );
      notify(`Đã cập nhật phiếu nháp ${payload.receiptId}.`);
      return { ok: true };
    }

    const nums = receipts.map(
      (r) => parseInt(r.receiptId.replace('PN-', ''), 10) || 0
    );
    const nextId = `PN-${String(
      (nums.length ? Math.max(...nums) : 0) + 1
    ).padStart(4, '0')}`;

    setReceipts((prev) => [
      {
        receiptId: nextId,
        supplierId: payload.supplierId,
        createdByAccountId: portalUser.accountId,
        createdAt: NOW_ISO(),
        status: 'DRAFT',
        finalPrice,
        lines: builtLines,
      },
      ...prev,
    ]);
    notify(`Đã lưu phiếu nhập ${nextId} ở trạng thái Nháp.`);
    return { ok: true };
  };

  // UC-34: Confirm DRAFT receipt (still allowed even if supplier became INACTIVE after draft was saved!)
  const confirmReceipt = (receiptId: string) => {
    const target = receipts.find((r) => r.receiptId === receiptId);
    if (!target || target.status !== 'DRAFT') {
      return { ok: false, error: 'Chỉ xác nhận được phiếu ở trạng thái Nháp.' };
    }

    setVariants((prev) =>
      prev.map((vr) => {
        const line = target.lines.find((l) => l.sku === vr.sku);
        if (!line) return vr;
        const oldQty = vr.stockQuantity;
        const newQty = oldQty + line.quantity;
        const newCost =
          oldQty <= 0
            ? line.unitPrice
            : Math.floor(
                (oldQty * vr.costPrice + line.quantity * line.unitPrice) /
                  newQty +
                  0.5
              );
        return {
          ...vr,
          stockQuantity: newQty,
          costPrice: newCost,
        };
      })
    );

    setReceipts((prev) =>
      prev.map((r) =>
        r.receiptId === receiptId ? { ...r, status: 'CONFIRMED' } : r
      )
    );
    notify(
      `Đã xác nhận phiếu nhập ${receiptId} — Đã cộng tồn kho, tính lại giá vốn bình quân và kích hoạt khóa cấu hình sản phẩm (UC-34 / UC-14-Q11)!`
    );
    return { ok: true };
  };

  const cancelReceipt = (receiptId: string) => {
    const target = receipts.find((r) => r.receiptId === receiptId);
    if (!target || target.status !== 'DRAFT') {
      return { ok: false, error: 'Chỉ hủy được phiếu ở trạng thái Nháp.' };
    }
    setReceipts((prev) =>
      prev.map((r) =>
        r.receiptId === receiptId ? { ...r, status: 'CANCELLED' } : r
      )
    );
    notify(`Đã hủy phiếu nháp ${receiptId}.`);
    return { ok: true };
  };

  return (
    <SobieContext.Provider
      value={{
        categories,
        collections,
        genders,
        sizes,
        colors,
        accounts,
        products,
        variants,
        promotions,
        orders,
        invoices,
        suppliers,
        receipts,
        storefrontUser,
        portalUser,
        shippingSession,
        activeCart,
        guestCart,
        activeWishlist,
        toastMessage,
        notify,
        getActiveProductPromo,
        getPromotionDisplayStatus,
        getProductVariants,
        getValidPricedVariants,
        getProductMinPrice,
        hasMultipleSizePrices,
        isProductEligibleForListing,
        isProductSoldOut,
        hasConfirmedReceiptForProduct,
        isProfileCompleteForAutofill,
        quoteOrderDiscount,
        getTop5BestSellers7Days,
        otpChallenge,
        requestRegisterOtp,
        resendRegisterOtp,
        verifyRegisterOtp,
        completeOtpRegistration,
        resetOtpFlow,
        loginStorefront,
        loginOrRegisterWithGoogle,
        logoutStorefront,
        updateCustomerProfile,
        loginPortal,
        logoutPortal,
        loginShippingPartner,
        enterPublicShippingSimulator,
        logoutShipping,
        changePassword,
        adminCreateAccount,
        adminEditAccount,
        adminToggleLockAccount,
        salerLockCustomerAccount,
        addToCart,
        updateCartQty,
        removeFromCart,
        clearUnavailableFromCart,
        toggleWishlist,
        placeOrder,
        simulateSepayWebhook,
        runAutoCancelOverdueQrJob,
        customerCancelOrder,
        employeeConfirmOrder,
        employeeCancelOrder,
        employeeHandoffOrder,
        carrierUpdateShipment,
        saveProduct,
        toggleProductStatus,
        deleteProduct,
        generateVariantsMatrix,
        toggleVariantStatus,
        deleteVariant,
        updateSizePrices,
        manageTaxonomy,
        createPromotion,
        endPromotion,
        saveSupplier,
        toggleSupplierStatus,
        deleteSupplier,
        saveDraftReceipt,
        confirmReceipt,
        cancelReceipt,
      }}
    >
      {children}
    </SobieContext.Provider>
  );
};

const ORDER_STATUS_META_LABELS: Record<OrderRecord['status'], string> = {
  PENDING: 'Chưa xử lý',
  CONFIRMED: 'Đã xác nhận',
  AWAITING_PICKUP: 'Chờ lấy hàng',
  SHIPPING: 'Đang giao',
  DELIVERED: 'Giao thành công',
  DELIVERY_FAILED: 'Giao không thành công',
  CANCELLED: 'Đã hủy',
};

export function useSobieSystem() {
  const ctx = useContext(SobieContext);
  if (!ctx) {
    throw new Error('useSobieSystem must be used inside SobieSystemProvider');
  }
  return ctx;
}
