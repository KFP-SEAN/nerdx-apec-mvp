/**
 * Shopping Cart Page
 *
 * Displays cart items from Shopify checkout
 * Allows quantity updates and removal
 * Shows pricing summary and checkout button
 */

'use client';

import { useState, useEffect } from 'react';
import { shopifyService, ShopifyCheckout } from '@/lib/shopify/client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Trash2, Plus, Minus, ShoppingBag, ArrowRight, ArrowLeft } from 'lucide-react';

export default function CartPage() {
  const router = useRouter();
  const [checkout, setCheckout] = useState<ShopifyCheckout | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadCart();
  }, []);

  async function loadCart() {
    try {
      setLoading(true);
      setError(null);

      const checkoutId = localStorage.getItem('shopify_checkout_id');

      if (!checkoutId) {
        setCheckout(null);
        setLoading(false);
        return;
      }

      const data = await shopifyService.getCheckout(checkoutId);
      setCheckout(data);
    } catch (err) {
      console.error('Error loading cart:', err);
      setError('장바구니를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  async function updateQuantity(lineItemId: string, newQuantity: number) {
    if (!checkout) return;

    try {
      setUpdatingItems(prev => new Set(prev).add(lineItemId));

      if (newQuantity === 0) {
        await removeItem(lineItemId);
        return;
      }

      const updatedCheckout = await shopifyService.updateCheckoutLineItem(
        checkout.id,
        lineItemId,
        newQuantity
      );

      setCheckout(updatedCheckout);
    } catch (err) {
      console.error('Error updating quantity:', err);
      alert('수량 변경에 실패했습니다.');
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(lineItemId);
        return newSet;
      });
    }
  }

  async function removeItem(lineItemId: string) {
    if (!checkout) return;

    const confirmed = confirm('이 상품을 장바구니에서 삭제하시겠습니까?');
    if (!confirmed) return;

    try {
      setUpdatingItems(prev => new Set(prev).add(lineItemId));

      const updatedCheckout = await shopifyService.removeFromCheckout(
        checkout.id,
        lineItemId
      );

      setCheckout(updatedCheckout);

      // If cart is now empty, clear localStorage
      if (updatedCheckout.lineItems.length === 0) {
        localStorage.removeItem('shopify_checkout_id');
      }
    } catch (err) {
      console.error('Error removing item:', err);
      alert('상품 삭제에 실패했습니다.');
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(lineItemId);
        return newSet;
      });
    }
  }

  async function handleCheckout() {
    if (!checkout) return;

    // Redirect to Shopify Checkout
    window.location.href = checkout.webUrl;
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">장바구니 불러오는 중...</p>
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
            onClick={loadCart}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  // Empty cart
  if (!checkout || checkout.lineItems.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-8">장바구니</h1>

          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <ShoppingBag className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              장바구니가 비어있습니다
            </h2>
            <p className="text-gray-500 mb-6">
              쇼핑을 시작하고 마음에 드는 상품을 담아보세요
            </p>
            <button
              onClick={() => router.push('/products/shopify')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-flex items-center"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              쇼핑 계속하기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">장바구니</h1>
          <button
            onClick={() => router.push('/products/shopify')}
            className="text-blue-600 hover:text-blue-700 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-1" />
            쇼핑 계속하기
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {checkout.lineItems.map((item: any) => {
              const isUpdating = updatingItems.has(item.id);
              const itemImage = item.variant?.image?.src || item.variant?.product?.images?.[0]?.src;

              return (
                <div
                  key={item.id}
                  className="bg-white rounded-lg shadow p-4 flex space-x-4"
                >
                  {/* Product Image */}
                  <div className="relative w-24 h-24 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                    {itemImage ? (
                      <Image
                        src={itemImage}
                        alt={item.title}
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                        No Image
                      </div>
                    )}
                  </div>

                  {/* Product Info */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-bold text-lg">{item.title}</h3>
                        {item.variant?.title !== 'Default Title' && (
                          <p className="text-sm text-gray-600">{item.variant?.title}</p>
                        )}

                        {/* AR Badge */}
                        {item.customAttributes?.some((attr: any) => attr.key === 'ar_enabled') && (
                          <span className="inline-block mt-1 bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                            AR 체험 포함
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => removeItem(item.id)}
                        disabled={isUpdating}
                        className="text-red-500 hover:text-red-700 disabled:text-gray-300"
                        title="삭제"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          disabled={isUpdating || item.quantity <= 1}
                          className="p-1 border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="w-12 text-center font-medium">
                          {isUpdating ? '...' : item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          disabled={isUpdating}
                          className="p-1 border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Price */}
                      <div className="text-right">
                        <div className="font-bold text-lg text-blue-600">
                          ${(parseFloat(item.variant?.price?.amount || '0') * item.quantity).toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-500">
                          ${item.variant?.price?.amount} × {item.quantity}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-8">
              <h2 className="text-xl font-bold mb-4">주문 요약</h2>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-gray-600">
                  <span>소계</span>
                  <span>${parseFloat(checkout.subtotalPrice).toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-gray-600">
                  <span>세금</span>
                  <span>${parseFloat(checkout.totalTax).toFixed(2)}</span>
                </div>

                <div className="border-t pt-3 flex justify-between font-bold text-lg">
                  <span>합계</span>
                  <span className="text-blue-600">
                    ${parseFloat(checkout.totalPrice).toFixed(2)}
                  </span>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold flex items-center justify-center space-x-2"
              >
                <span>결제하기</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <p className="text-xs text-gray-500 text-center mt-4">
                Shopify 안전 결제로 이동합니다
              </p>

              {/* AR Access Info */}
              {checkout.lineItems.some((item: any) =>
                item.customAttributes?.some((attr: any) => attr.key === 'ar_enabled')
              ) && (
                <div className="mt-6 p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-purple-800">
                    <strong>AR 체험 안내:</strong> 구매 완료 후 AR 액세스 코드가 이메일로 전송됩니다.
                  </p>
                </div>
              )}

              {/* Item Count */}
              <div className="mt-6 text-center text-sm text-gray-600">
                총 {checkout.lineItems.length}개 상품
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
