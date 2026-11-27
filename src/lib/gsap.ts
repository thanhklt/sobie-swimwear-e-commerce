import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

// Register GSAP plugins once before any component renders
gsap.registerPlugin(useGSAP, ScrollTrigger);

gsap.defaults({
  duration: 0.65,
  ease: 'power3.out',
});

/**
 * Format integer VND price cleanly (AGENTS.md: integer VND, ROUND_HALF_UP)
 */
export function formatVND(amount: number): string {
  const rounded = Math.round(amount);
  return `${new Intl.NumberFormat('vi-VN').format(rounded)}₫`;
}

/**
 * Compute discounted price using ROUND_HALF_UP integer VND math
 */
export function calcDiscountedPrice(
  originalPrice: number,
  discountPercent?: number | null
): number {
  if (!discountPercent || discountPercent <= 0) return originalPrice;
  const raw = (originalPrice * (100 - discountPercent)) / 100;
  return Math.floor(raw + 0.5);
}

/**
 * Compute percentage discount amount using ROUND_HALF_UP integer VND math (UC-19 AC-3)
 */
export function calcDiscountAmount(subtotal: number, discountPercent: number): number {
  if (discountPercent <= 0 || subtotal <= 0) return 0;
  const raw = (subtotal * discountPercent) / 100;
  return Math.min(subtotal, Math.floor(raw + 0.5));
}

/**
 * Strip Vietnamese accents for UC-11 accent-insensitive search & natural IDs
 */
export function removeVietnameseTones(str: string): string {
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D');
}

/**
 * Uppercase slug token for natural IDs (<HỌ TÊN>, <MÀU>, <SIZE> per data_model_v2.dbml)
 */
export function toNaturalToken(str: string): string {
  return removeVietnameseTones(str)
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');
}

const CROCKFORD_ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

/**
 * Generate 8-character Crockford Base32 order code (UC-20 AC-2b)
 */
export function generateOrderCode(existingCodes: Set<string>): string {
  for (let attempt = 0; attempt < 50; attempt++) {
    let code = '';
    for (let i = 0; i < 8; i++) {
      const idx = Math.floor(Math.random() * CROCKFORD_ALPHABET.length);
      code += CROCKFORD_ALPHABET[idx];
    }
    if (!existingCodes.has(code)) return code;
  }
  return '7K3M9Q2X';
}

export { gsap, ScrollTrigger, useGSAP };
