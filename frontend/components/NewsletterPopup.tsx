'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import NewsletterSignup from './NewsletterSignup';
import {
  shouldShowNewsletterPopup,
  dismissNewsletterPopup,
  markAsSubscribed
} from '@/lib/shopify/newsletter-simple';

export default function NewsletterPopup() {
  const [isVisible, setIsVisible] = useState(false);
  const [hasShown, setHasShown] = useState(false);

  useEffect(() => {
    // Don't show if already dismissed or subscribed
    if (!shouldShowNewsletterPopup() || hasShown) {
      return;
    }

    // Track mouse movement for exit intent
    let exitIntentTriggered = false;

    const handleMouseLeave = (e: MouseEvent) => {
      // Check if mouse is leaving from the top of the page
      if (e.clientY <= 0 && !exitIntentTriggered) {
        exitIntentTriggered = true;
        setIsVisible(true);
        setHasShown(true);
      }
    };

    // Show after 30 seconds if exit intent hasn't triggered
    const timer = setTimeout(() => {
      if (!exitIntentTriggered && !hasShown) {
        setIsVisible(true);
        setHasShown(true);
      }
    }, 30000); // 30 seconds

    // Add exit intent listener
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [hasShown]);

  const handleClose = () => {
    setIsVisible(false);
    dismissNewsletterPopup();
  };

  const handleSuccess = () => {
    markAsSubscribed();
    // Close popup after a delay to show success message
    setTimeout(() => {
      setIsVisible(false);
    }, 3000);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleClose}
    >
      <div
        className="bg-white rounded-2xl max-w-lg w-full relative animate-in fade-in zoom-in duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
          aria-label="닫기"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>

        {/* Content */}
        <div className="p-8">
          <div className="text-center mb-6">
            <div className="text-5xl mb-4">🍶</div>
            <h2 className="text-3xl font-bold mb-3">
              Welcome to NERDX APEC!
            </h2>
            <p className="text-gray-700 text-lg">
              전통주 여정을 시작해보세요
            </p>
          </div>

          {/* Benefits */}
          <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl p-6 mb-6">
            <p className="font-semibold text-gray-800 mb-4">
              지금 커뮤니티에 가입하시면:
            </p>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <span className="text-green-600 mt-0.5">✅</span>
                <span className="text-gray-700">첫 주문 15% 할인</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-600 mt-0.5">✅</span>
                <span className="text-gray-700">무료 배송 쿠폰 (5만원 이상)</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-600 mt-0.5">✅</span>
                <span className="text-gray-700">전통주 초보자 가이드 PDF</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-600 mt-0.5">✅</span>
                <span className="text-gray-700">한정판 제품 우선 구매권</span>
              </li>
            </ul>
          </div>

          {/* Newsletter signup form - compact variant */}
          <div className="mb-4">
            <NewsletterSignup
              source="popup"
              variant="compact"
              onSuccess={handleSuccess}
            />
          </div>

          {/* Maybe later link */}
          <button
            onClick={handleClose}
            className="w-full text-center text-gray-500 hover:text-gray-700 text-sm py-2 transition-colors"
          >
            나중에 가입하기
          </button>
        </div>
      </div>
    </div>
  );
}
