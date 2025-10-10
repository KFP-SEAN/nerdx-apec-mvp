/**
 * Order Cancelled Page
 *
 * Shown when user cancels Shopify checkout
 * Provides options to return to cart or continue shopping
 */

'use client';

import { useRouter } from 'next/navigation';
import { XCircle, ShoppingCart, ArrowLeft, HelpCircle } from 'lucide-react';
import Link from 'next/link';

export default function OrderCancelledPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          {/* Cancelled Icon */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-4">
              <XCircle className="w-12 h-12 text-red-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              주문이 취소되었습니다
            </h1>
            <p className="text-gray-600">
              결제가 완료되지 않았으며, 장바구니 내역은 유지됩니다.
            </p>
          </div>

          {/* Information */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">무슨 일이 있었나요?</h2>

            <div className="space-y-3 text-gray-700">
              <p>다음과 같은 이유로 주문이 취소될 수 있습니다:</p>
              <ul className="list-disc ml-6 space-y-2 text-sm">
                <li>결제 페이지에서 '뒤로 가기' 버튼을 누르셨습니다</li>
                <li>결제 시간이 초과되었습니다</li>
                <li>결제 정보 입력을 완료하지 않으셨습니다</li>
                <li>직접 주문을 취소하셨습니다</li>
              </ul>
            </div>
          </div>

          {/* Cart Status */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
            <div className="flex items-start space-x-3">
              <ShoppingCart className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-blue-900 mb-2">
                  장바구니 상품은 안전합니다
                </h3>
                <p className="text-sm text-blue-800">
                  걱정하지 마세요! 장바구니에 담으신 상품들은 그대로 유지됩니다.
                  준비가 되시면 언제든지 다시 결제를 진행하실 수 있습니다.
                </p>
              </div>
            </div>
          </div>

          {/* Common Issues */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <HelpCircle className="w-6 h-6 mr-2 text-gray-600" />
              자주 발생하는 문제
            </h2>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">결제 수단이 거부되었나요?</h3>
                <p className="text-sm text-gray-600">
                  다른 카드를 사용하시거나 카드사에 문의하여 결제 한도를 확인해보세요.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-1">배송 주소에 문제가 있나요?</h3>
                <p className="text-sm text-gray-600">
                  결제 시 정확한 배송 주소를 입력했는지 확인해주세요.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-1">상품 재고가 없나요?</h3>
                <p className="text-sm text-gray-600">
                  일부 상품의 재고가 소진되었을 수 있습니다. 장바구니를 확인하여 재고를 체크해보세요.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-1">기술적 문제가 발생했나요?</h3>
                <p className="text-sm text-gray-600">
                  페이지를 새로고침하거나 다른 브라우저를 사용해보세요.
                  문제가 지속되면 고객 지원팀에 문의해주세요.
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => router.push('/cart')}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold flex items-center justify-center space-x-2"
            >
              <ShoppingCart className="w-5 h-5" />
              <span>장바구니로 돌아가기</span>
            </button>

            <button
              onClick={() => router.push('/products/shopify')}
              className="w-full px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold flex items-center justify-center space-x-2"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>쇼핑 계속하기</span>
            </button>
          </div>

          {/* Support */}
          <div className="mt-8 text-center text-sm text-gray-600">
            <p>
              도움이 필요하신가요?{' '}
              <Link href="/support" className="text-blue-600 hover:underline">
                고객 지원팀에 문의하기
              </Link>
            </p>
          </div>

          {/* Additional Info */}
          <div className="mt-6 p-4 bg-gray-100 rounded-lg">
            <p className="text-xs text-gray-600 text-center">
              이 페이지는 결제가 완료되지 않았음을 알려드립니다.
              카드에서 금액이 청구되지 않았으며, 어떠한 주문도 생성되지 않았습니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
