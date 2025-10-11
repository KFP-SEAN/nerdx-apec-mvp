'use client';

import { useState } from 'react';
import { Mail, Sparkles, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface NewsletterSignupProps {
  source: 'footer' | 'popup' | 'checkout';
  variant?: 'default' | 'compact';
  onSuccess?: () => void;
}

export default function NewsletterSignup({
  source,
  variant = 'default',
  onSuccess
}: NewsletterSignupProps) {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [couponCode, setCouponCode] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      toast.error('올바른 이메일 주소를 입력해주세요');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || '구독 실패');
      }

      setIsSubscribed(true);
      setCouponCode(data.couponCode);
      toast.success('🎉 환영합니다! 이메일을 확인해주세요.');

      // 쿠폰 모달 표시
      setTimeout(() => {
        showCouponModal(data.couponCode);
      }, 1000);

      onSuccess?.();

    } catch (error: any) {
      console.error('Subscription error:', error);
      toast.error(error.message || '구독에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  }

  function showCouponModal(code: string) {
    // Show modal with coupon code
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white rounded-2xl p-8 max-w-md mx-4 text-center">
          <div class="text-4xl mb-4">🎉</div>
          <h3 class="text-2xl font-bold mb-2">환영합니다!</h3>
          <p class="text-gray-600 mb-4">첫 구매 15% 할인 쿠폰을 받으셨어요</p>
          <div class="bg-primary-50 rounded-lg p-4 mb-4">
            <div class="text-sm text-gray-600 mb-1">쿠폰 코드</div>
            <div class="text-2xl font-bold text-primary-600">${code}</div>
          </div>
          <button onclick="this.parentElement.parentElement.remove()" class="btn-primary w-full">
            쇼핑 시작하기
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  if (isSubscribed) {
    return (
      <div className="text-center py-8">
        <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary-600" />
        <h3 className="text-xl font-bold mb-2">구독 완료!</h3>
        <p className="text-gray-600 mb-4">
          이메일로 15% 할인 쿠폰을 보내드렸어요
        </p>
        {couponCode && (
          <div className="inline-block bg-primary-50 rounded-lg px-6 py-3">
            <div className="text-sm text-gray-600 mb-1">쿠폰 코드</div>
            <div className="text-xl font-bold text-primary-600">{couponCode}</div>
          </div>
        )}
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="이메일 주소"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary whitespace-nowrap"
        >
          {isLoading ? '구독 중...' : '구독'}
        </button>
      </form>
    );
  }

  return (
    <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-2xl p-8">
      <div className="max-w-xl mx-auto text-center">
        <Mail className="w-12 h-12 mx-auto mb-4 text-primary-600" />

        <h3 className="text-2xl font-bold mb-2">
          🍶 Join the NERDX Community
        </h3>

        <p className="text-gray-700 mb-6">
          전통주를 사랑하는 커뮤니티에 가입하고 특별한 혜택을 받아보세요
        </p>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">✨</div>
            <div className="text-sm font-semibold">첫 구매 15% 할인</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">🎁</div>
            <div className="text-sm font-semibold">한정판 우선 구매</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">📚</div>
            <div className="text-sm font-semibold">전통주 가이드</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">🎬</div>
            <div className="text-sm font-semibold">무료 CAMEO</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary px-8 py-3 text-lg whitespace-nowrap"
          >
            {isLoading ? '구독 중...' : '구독하기'}
          </button>
        </form>

        <p className="text-sm text-gray-500">
          12,453명이 이미 참여하고 있어요 💜
        </p>

        <p className="text-xs text-gray-400 mt-2">
          구독 시 개인정보 처리방침에 동의하게 됩니다
        </p>
      </div>
    </div>
  );
}
