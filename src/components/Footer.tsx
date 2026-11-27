import React from 'react';
import {
  Phone,
  MessageCircle,
  MapPin,
  Mail,
  ShieldCheck,
  QrCode,
  Truck,
} from 'lucide-react';
import { STORE_CONFIG } from '../data/seedData';
import { useSobieSystem } from '../context/SobieSystemContext';
import { InfoTab } from '../types/store';

interface FooterProps {
  onSelectCategory: (category: string) => void;
  onOpenInfo: (tab: InfoTab) => void;
  onOpenSizeGuide: () => void;
}

export const Footer: React.FC<FooterProps> = ({
  onSelectCategory,
  onOpenInfo,
  onOpenSizeGuide,
}) => {
  const { categories } = useSobieSystem();

  return (
    <footer className="bg-[#F3EFE6] border-t border-[#E4DDD0] text-[#5E6658] mt-20">
      {/* Full-Bleed Service Pillars */}
      <div className="border-b border-[#E4DDD0]">
        <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-9 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-3.5 p-5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
            <div className="w-10 h-10 rounded-xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-[#22261E]">
                Sợi Tái Chế Kháng Muối Biển UPF 50+
              </p>
              <p className="text-xs text-[#5E6658] mt-1 leading-relaxed">
                Co giãn bốn chiều mềm mại, giữ phom bền bỉ và thân thiện với làn da dưới nắng hè.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3.5 p-5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
            <div className="w-10 h-10 rounded-xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center shrink-0">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-[#22261E]">
                Vận Chuyển Đồng Giá 12.000₫ Toàn Quốc
              </p>
              <p className="text-xs text-[#5E6658] mt-1 leading-relaxed">
                Xuất kho tập trung tại TP.HCM, theo dõi tiến trình vận đơn minh bạch từ lúc bàn giao đến khi nhận hàng.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3.5 p-5 rounded-2xl bg-[#FAF7F2] border border-[#E4DDD0]">
            <div className="w-10 h-10 rounded-xl bg-[#E5ECE0] text-[#4A5D43] flex items-center justify-center shrink-0">
              <QrCode className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-[#22261E]">
                Thanh Toán COD & VietQR SePay Tự Động
              </p>
              <p className="text-xs text-[#5E6658] mt-1 leading-relaxed">
                Tự động sinh mã VietQR chuẩn nội dung `SOBIE&lt;mã đơn&gt;`, đối soát webhook tức thì 24/7.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Full-Bleed Footer Columns */}
      <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 py-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10">
        <div className="lg:col-span-4 space-y-4">
          <div>
            <span className="font-editorial text-3xl tracking-[0.16em] text-[#22261E] font-semibold">
              SOBIE
            </span>
            <p className="text-[11px] uppercase tracking-[0.24em] text-[#878E80] mt-1 font-medium">
              Sea-Salt Cream & Olive Swimwear Atelier
            </p>
          </div>
          <p className="text-sm text-[#5E6658] leading-relaxed max-w-md">
            Không gian thương mại điện tử đồ bơi Sobie trên nền Kem muối biển & Xanh ô-liu thanh lịch — thiết kế toàn viền thoáng rộng, đồng bộ chuẩn xác từng Use Case trong đặc tả `specs/`.
          </p>
          <div className="pt-1 flex flex-wrap items-center gap-3">
            <a
              href={`tel:${STORE_CONFIG.hotlineRaw}`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#FAF7F2] border border-[#D4CBB8] text-xs font-semibold text-[#22261E] hover:border-[#4A5D43] transition-colors"
            >
              <Phone className="w-3.5 h-3.5 text-[#4A5D43]" />
              {STORE_CONFIG.hotline}
            </a>
            <a
              href={STORE_CONFIG.zaloUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#4A5D43] text-xs font-semibold text-white hover:bg-[#3B4B35] transition-colors"
            >
              <MessageCircle className="w-3.5 h-3.5" />
              Zalo cửa hàng
            </a>
          </div>
        </div>

        <div className="lg:col-span-3 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#22261E]">
            Danh mục sản phẩm
          </h4>
          <ul className="space-y-2 text-sm text-[#5E6658]">
            {categories.map((cat) => (
              <li key={cat}>
                <button
                  type="button"
                  onClick={() => onSelectCategory(cat)}
                  className="hover:text-[#4A5D43] transition-colors cursor-pointer"
                >
                  {cat}
                </button>
              </li>
            ))}
            <li>
              <button
                type="button"
                onClick={onOpenSizeGuide}
                className="text-[#4A5D43] font-semibold hover:underline transition-colors cursor-pointer"
              >
                Bảng size chung cửa hàng
              </button>
            </li>
          </ul>
        </div>

        <div className="lg:col-span-2 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#22261E]">
            Thông tin (UC-13)
          </h4>
          <ul className="space-y-2 text-sm text-[#5E6658]">
            <li>
              <button
                type="button"
                onClick={() => onOpenInfo('about')}
                className="hover:text-[#22261E] cursor-pointer"
              >
                Giới thiệu
              </button>
            </li>
            <li>
              <button
                type="button"
                onClick={() => onOpenInfo('policy')}
                className="hover:text-[#22261E] cursor-pointer"
              >
                Chính sách chung
              </button>
            </li>
            <li>
              <button
                type="button"
                onClick={() => onOpenInfo('faq')}
                className="hover:text-[#22261E] cursor-pointer"
              >
                Câu hỏi thường gặp (FAQ)
              </button>
            </li>
          </ul>
        </div>

        <div className="lg:col-span-3 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#22261E]">
            Liên hệ & Kho trung tâm
          </h4>
          <ul className="space-y-2.5 text-sm text-[#5E6658]">
            <li className="flex items-start gap-2.5">
              <MapPin className="w-4 h-4 text-[#4A5D43] shrink-0 mt-0.5" />
              <span>{STORE_CONFIG.senderAddress}</span>
            </li>
            <li className="flex items-center gap-2.5">
              <Phone className="w-4 h-4 text-[#4A5D43] shrink-0" />
              <span>Hotline: {STORE_CONFIG.hotline}</span>
            </li>
            <li className="flex items-center gap-2.5">
              <Mail className="w-4 h-4 text-[#4A5D43] shrink-0" />
              <span>{STORE_CONFIG.email}</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-[#E4DDD0] py-5 bg-[#EAE4D7]/70">
        <div className="w-full px-5 sm:px-8 lg:px-12 xl:px-16 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-[#878E80]">
          <p>
            © 2026 SOBIE Swimwear — Sea-Salt Cream & Olive Atelier (React 19 + @gsap/react).
          </p>
          <p>Đồng bộ toàn diện BR-GIAIDOAN1 & UC-01 → UC-40 (`specs/` mới nhất)</p>
        </div>
      </div>
    </footer>
  );
};
