export type AppSurface = 'storefront' | 'portal' | 'shipping';

export type RoleCode = 'customer' | 'employee' | 'admin';
export type AccountStatus = 'ACTIVE' | 'LOCKED';

export interface AccountRecord {
  key: string;
  accountId: string; // KH-YYYYMMDD-0001 | NV-HOTEN-YYYYMMDD-0001 | AD-HOTEN-YYYYMMDD-0001
  role: RoleCode;
  email: string;
  phone: string;
  passwordPlain: string; // Empty string '' if Google-only account (UC-01 AC-14 / UC-02 AC-18)
  hasPassword: boolean;
  googleSub?: string; // Linked Google OpenID sub (UC-01 / UC-02)
  status: AccountStatus;
  name: string;
  dateOfBirth: string; // YYYY-MM-DD or ''
  houseNumber: string;
  ward: string;
  city: string;
  country: string;
  createdAt: string; // ISO UTC
}

export interface ShippingOperatorSession {
  stationId: string;
  operatorName: string;
  mode: 'authenticated' | 'public-simulator';
  signedInAt: string;
}

export type ProductStatus = 'ACTIVE' | 'INACTIVE';
export type VariantStatus = 'ACTIVE' | 'INACTIVE';

export interface ColorItem {
  name: string;
  hex: string;
}

export interface VariantRecord {
  sku: string; // <SP>-<MAU>-<SIZE>
  productId: string;
  color: string;
  size: string;
  sellPrice: number | null; // NULL = size chưa có giá (UC-16)
  status: VariantStatus;
  stockQuantity: number; // inventory.stock.stock_quantity
  costPrice: number; // inventory.stock.stock_cost_price (weighted average)
}

export interface GalleryItem {
  orderNo: number;
  url: string;
}

export interface ProductRecord {
  id: string; // SP-0001
  name: string;
  subtitle: string;
  description: string;
  status: ProductStatus;
  category: string;
  gender: string;
  collections: string[];
  gallery: GalleryItem[];
  createdAt: string; // YYYY-MM-DD
}

export interface CartItem {
  sku: string;
  productId: string;
  quantity: number;
}

export type PromotionType = 'PRODUCT' | 'ORDER' | 'CODE';
export type PromotionStatusFlag = 'ENABLED' | 'DISABLED';
export type PromotionDisplayStatus = 'Đang hiệu lực' | 'Sắp diễn ra' | 'Đã kết thúc';

export interface PromotionRecord {
  promotionId: string; // KM-0001
  type: PromotionType;
  discountPercentage: number; // 0 < x < 100
  status: PromotionStatusFlag;
  // PRODUCT only
  productId?: string;
  // ORDER & CODE only
  thresholdPrice?: number;
  quantity?: number;
  usedAmount: number;
  startDate?: string; // YYYY-MM-DD (Asia/Ho_Chi_Minh calendar date)
  endDate?: string;   // YYYY-MM-DD
  // CODE only
  code?: string;
}

export type OrderStatus =
  | 'PENDING'
  | 'CONFIRMED'
  | 'AWAITING_PICKUP'
  | 'SHIPPING'
  | 'DELIVERED'
  | 'DELIVERY_FAILED'
  | 'CANCELLED';

export type PaymentMethod = 'COD' | 'QR';
export type PaymentStatus = 'UNPAID' | 'PAID';
export type StatusSource = 'CUSTOMER' | 'EMPLOYEE' | 'SYSTEM' | 'SHIPPING_SIMULATOR';

export interface OrderLineRecord {
  sku: string;
  productId: string;
  productName: string;
  image: string;
  color: string;
  size: string;
  quantity: number;
  originalUnitPrice: number; // order_detail_unit_price
  productPromotionId?: string;
  discountPercent?: number;
  finalUnitPrice: number;
  costPriceAtSale: number; // order_detail_cost_price
}

export interface OrderStatusHistoryEntry {
  fromStatus: OrderStatus | null;
  toStatus: OrderStatus;
  source: StatusSource;
  changedByAccountId?: string;
  note?: string; // order_status_history_note (reason when cancelled by EMPLOYEE — hidden from customer!)
  changedAt: string; // ISO string
}

export interface OrderRecord {
  orderCode: string; // 8-char Crockford Base32
  accountId: string;
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
  orderPromotionId?: string;
  codePromotionId?: string;
  appliedPromoLabel?: string;
  customerName: string;
  customerPhone: string;
  customerHouseNumber: string;
  customerWard: string;
  customerCity: string;
  customerCountry: string;
  subtotalAfterProductPromo: number;
  discountAmount: number;
  shippingFee: number;
  totalPrice: number;
  status: OrderStatus;
  createdAt: string; // ISO string
  updatedAt: string; // ISO string
  deliveredAt?: string; // ISO string (used by UC-37 dashboard period!)
  history: OrderStatusHistoryEntry[];
  items: OrderLineRecord[];
}

export interface InvoiceSnapshot {
  invoiceId: string; // HD-<orderCode>
  orderCode: string;
  createdAt: string; // ISO string when DELIVERED
  paymentMethod: PaymentMethod;
  customer: {
    name: string;
    phone: string;
    email: string;
    address: string;
  };
  items: {
    productName: string;
    sku: string;
    color: string;
    size: string;
    unitPrice: number;
    discountedUnitPrice: number;
    quantity: number;
    discountAmount: number;
  }[];
  subtotal: number; // sum(original * qty)
  productDiscount: number;
  orderDiscount: number;
  shippingFee: number;
  totalPayment: number;
}

export type SupplierStatus = 'ACTIVE' | 'INACTIVE';

export interface SupplierRecord {
  supplierId: string; // NCC-0001
  name: string;
  phone: string;
  email: string;
  address: string;
  status: SupplierStatus;
}

export type GoodsReceiptStatus = 'DRAFT' | 'CONFIRMED' | 'CANCELLED';

export interface GoodsReceiptLine {
  sku: string;
  quantity: number;
  unitPrice: number; // >= 0 integer VND
  totalPrice: number;
}

export interface GoodsReceiptRecord {
  receiptId: string; // PN-0001
  supplierId: string;
  createdByAccountId: string;
  createdAt: string; // ISO string
  status: GoodsReceiptStatus;
  finalPrice: number;
  lines: GoodsReceiptLine[];
}

export type StorefrontRoute =
  | 'home'
  | 'catalog'
  | 'product'
  | 'cart'
  | 'wishlist'
  | 'orders'
  | 'profile'
  | 'info'
  | 'login'
  | 'register';

export type InfoTab = 'about' | 'policy' | 'faq';

export type SalerSection =
  | 'dashboard'
  | 'orders'
  | 'handoff'
  | 'promotions'
  | 'products'
  | 'taxonomy'
  | 'stock'
  | 'customers'
  | 'invoices'
  | 'password';

export type AdminSection = 'accounts' | 'password';

export interface CatalogFilters {
  category: string;
  gender: string;
  size: string;
  collection: string;
  search: string;
  sort: 'newest' | 'price-asc' | 'price-desc';
  page: number;
}
