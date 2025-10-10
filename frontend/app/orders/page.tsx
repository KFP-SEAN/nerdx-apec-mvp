/**
 * My Orders Page
 *
 * Displays user's order history from Shopify
 * Shows AR access buttons for eligible products
 * Integrates with custom Shopify app for AR tokens
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
  Package,
  Cube,
  ExternalLink,
  Calendar,
  DollarSign,
  CheckCircle,
  Clock,
  XCircle,
  Mail,
  Download,
  Eye
} from 'lucide-react';

interface Order {
  id: string;
  orderNumber: string;
  email: string;
  createdAt: string;
  totalPrice: string;
  currencyCode: string;
  financialStatus: string;
  fulfillmentStatus: string;
  lineItems: Array<{
    id: string;
    title: string;
    quantity: number;
    variantTitle: string;
    price: string;
    image?: string;
    hasARAccess?: boolean;
    arAccessToken?: string;
    arAssetUrl?: string;
  }>;
}

export default function OrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState('');
  const [showEmailPrompt, setShowEmailPrompt] = useState(false);

  useEffect(() => {
    // Check if user email is stored
    const storedEmail = localStorage.getItem('user_email');
    if (storedEmail) {
      setUserEmail(storedEmail);
      loadOrders(storedEmail);
    } else {
      setShowEmailPrompt(true);
      setLoading(false);
    }
  }, []);

  async function loadOrders(email: string) {
    try {
      setLoading(true);
      setError(null);

      // Call custom Shopify app API to get user's orders
      const response = await fetch(`${process.env.NEXT_PUBLIC_SHOPIFY_APP_URL}/api/orders/user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch orders');
      }

      const data = await response.json();
      setOrders(data.orders || []);
    } catch (err) {
      console.error('Error loading orders:', err);
      setError('주문 내역을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  async function handleEmailSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!userEmail.trim()) return;

    // Store email
    localStorage.setItem('user_email', userEmail);
    setShowEmailPrompt(false);
    loadOrders(userEmail);
  }

  async function handleARAccess(orderId: string, productId: string) {
    try {
      // Request AR access token from custom Shopify app
      const response = await fetch(`${process.env.NEXT_PUBLIC_SHOPIFY_APP_URL}/api/ar-access/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          orderId,
          productId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate AR access token');
      }

      const data = await response.json();

      // Open AR viewer with access token
      window.open(
        `/ar-viewer?token=${data.token}&product=${productId}`,
        '_blank',
        'width=800,height=600'
      );
    } catch (err) {
      console.error('Error accessing AR:', err);
      alert('AR 체험 액세스에 실패했습니다. 잠시 후 다시 시도해주세요.');
    }
  }

  function getStatusIcon(status: string) {
    switch (status?.toLowerCase()) {
      case 'paid':
      case 'fulfilled':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'pending':
      case 'unfulfilled':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'cancelled':
      case 'refunded':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Package className="w-5 h-5 text-gray-600" />;
    }
  }

  function getStatusText(financialStatus: string, fulfillmentStatus: string) {
    if (financialStatus === 'refunded') return '환불 완료';
    if (financialStatus === 'pending') return '결제 대기 중';
    if (fulfillmentStatus === 'fulfilled') return '배송 완료';
    if (fulfillmentStatus === 'unfulfilled') return '배송 준비 중';
    if (fulfillmentStatus === 'partial') return '부분 배송';
    return '처리 중';
  }

  // Email Prompt Modal
  if (showEmailPrompt) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <Mail className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">주문 내역 확인</h2>
            <p className="text-gray-600">
              주문 시 사용하신 이메일 주소를 입력해주세요
            </p>
          </div>

          <form onSubmit={handleEmailSubmit}>
            <input
              type="email"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              placeholder="이메일 주소"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-4"
            />
            <button
              type="submit"
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              주문 내역 조회
            </button>
          </form>

          <p className="text-xs text-gray-500 text-center mt-4">
            입력하신 이메일 주소는 주문 조회 목적으로만 사용됩니다
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">주문 내역 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl">{error}</p>
          <button
            onClick={() => loadOrders(userEmail)}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">주문 내역</h1>
          <p className="text-gray-600">
            {userEmail}님의 주문 내역입니다
            <button
              onClick={() => {
                localStorage.removeItem('user_email');
                setShowEmailPrompt(true);
              }}
              className="ml-2 text-blue-600 hover:underline text-sm"
            >
              (이메일 변경)
            </button>
          </p>
        </div>

        {/* Orders List */}
        {orders.length === 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <Package className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              주문 내역이 없습니다
            </h2>
            <p className="text-gray-500 mb-6">
              아직 주문하신 상품이 없습니다
            </p>
            <button
              onClick={() => router.push('/products/shopify')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              쇼핑 시작하기
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
                {/* Order Header */}
                <div className="bg-gray-50 border-b px-6 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        {getStatusIcon(order.financialStatus)}
                        <span className="font-bold text-lg">
                          주문 #{order.orderNumber}
                        </span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600 space-x-4">
                        <span className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          {new Date(order.createdAt).toLocaleDateString('ko-KR')}
                        </span>
                        <span className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />
                          {order.totalPrice} {order.currencyCode}
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                        {getStatusText(order.financialStatus, order.fulfillmentStatus)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Order Items */}
                <div className="p-6">
                  <div className="space-y-4">
                    {order.lineItems.map((item) => (
                      <div key={item.id} className="flex space-x-4">
                        {/* Product Image */}
                        <div className="relative w-20 h-20 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                          {item.image ? (
                            <Image
                              src={item.image}
                              alt={item.title}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                              No Image
                            </div>
                          )}
                        </div>

                        {/* Product Info */}
                        <div className="flex-1">
                          <h3 className="font-bold">{item.title}</h3>
                          {item.variantTitle && item.variantTitle !== 'Default Title' && (
                            <p className="text-sm text-gray-600">{item.variantTitle}</p>
                          )}
                          <p className="text-sm text-gray-600">
                            수량: {item.quantity} × ${item.price}
                          </p>
                        </div>

                        {/* AR Access Button */}
                        {item.hasARAccess && (
                          <button
                            onClick={() => handleARAccess(order.id, item.id)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center space-x-2 h-fit"
                          >
                            <Cube className="w-4 h-4" />
                            <span className="text-sm font-medium">AR 체험</span>
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
