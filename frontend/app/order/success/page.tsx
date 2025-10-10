/**
 * Order Success Page
 *
 * Shown after successful Shopify checkout
 * Displays order confirmation and AR access info
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle, Package, Mail, Box, ArrowRight, Download } from 'lucide-react';
import Link from 'next/link';

export default function OrderSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [orderInfo, setOrderInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Get order ID from URL params
  const orderId = searchParams.get('order_id');
  const checkoutId = searchParams.get('checkout_id');

  useEffect(() => {
    // Clear cart from localStorage
    localStorage.removeItem('shopify_checkout_id');

    // Fetch order details if order ID is provided
    if (orderId) {
      fetchOrderDetails();
    } else {
      setLoading(false);
    }
  }, [orderId]);

  async function fetchOrderDetails() {
    try {
      // This would call your backend API to get order details
      // For now, we'll just use the URL params
      setOrderInfo({
        orderId,
        checkoutId
      });
    } catch (error) {
      console.error('Error fetching order details:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">주문 확인 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          {/* Success Icon */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              주문이 완료되었습니다!
            </h1>
            <p className="text-gray-600">
              주문해주셔서 감사합니다. 확인 메일이 곧 발송됩니다.
            </p>
          </div>

          {/* Order Number */}
          {orderId && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">주문 번호</p>
                  <p className="text-xl font-bold text-gray-900">{orderId}</p>
                </div>
                <Package className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          )}

          {/* What's Next */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">다음 단계</h2>

            <div className="space-y-4">
              {/* Email Confirmation */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <Mail className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">주문 확인 메일</h3>
                  <p className="text-sm text-gray-600">
                    주문 상세 내역과 배송 정보가 담긴 확인 메일을 발송했습니다.
                  </p>
                </div>
              </div>

              {/* AR Access */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <Box className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">AR 체험 액세스</h3>
                  <p className="text-sm text-gray-600">
                    AR 체험 가능한 상품을 구매하신 경우, AR 액세스 코드가 별도 메일로 발송됩니다.
                    이 코드로 구매하신 제품을 증강현실로 미리 체험해보실 수 있습니다.
                  </p>
                </div>
              </div>

              {/* Shipping */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <Package className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">배송 안내</h3>
                  <p className="text-sm text-gray-600">
                    주문 상품은 영업일 기준 2-3일 이내에 배송 시작됩니다.
                    배송 추적 정보는 이메일로 안내드립니다.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* AR Access Info (if applicable) */}
          <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 mb-6">
            <div className="flex items-start space-x-3">
              <Box className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-purple-900 mb-2">
                  AR 체험 액세스 안내
                </h3>
                <p className="text-sm text-purple-800 mb-3">
                  구매하신 제품을 증강현실(AR)로 체험하실 수 있습니다.
                  주문 확인 후 5-10분 이내에 AR 액세스 코드가 이메일로 발송됩니다.
                </p>
                <ul className="text-sm text-purple-800 space-y-1 ml-4 list-disc">
                  <li>AR 액세스 코드는 90일간 유효합니다</li>
                  <li>스마트폰 또는 AR 지원 기기에서 사용 가능</li>
                  <li>실제 환경에 제품을 배치하여 미리 확인할 수 있습니다</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Link
              href="/orders"
              className="block w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-center font-semibold"
            >
              주문 내역 보기
            </Link>

            <Link
              href="/products/shopify"
              className="block w-full px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-center font-semibold"
            >
              쇼핑 계속하기
            </Link>
          </div>

          {/* Support */}
          <div className="mt-8 text-center text-sm text-gray-600">
            <p>
              주문에 문제가 있으신가요?{' '}
              <Link href="/support" className="text-blue-600 hover:underline">
                고객 지원팀에 문의하기
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
