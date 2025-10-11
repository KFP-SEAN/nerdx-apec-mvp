/**
 * Shopping Cart Page
 * Full-featured cart with Shopify integration
 */

'use client';

import { useEffect, useState } from 'react';
import { useCartStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Minus, Plus, X, ShoppingBag, Truck, Tag, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';

const FREE_SHIPPING_THRESHOLD = 50000; // 50,000 KRW

export default function CartPage() {
  const router = useRouter();
  const {
    cart,
    isLoading,
    updateItem,
    removeItem,
    clearCart,
    syncWithServer,
    getTotalItems,
    getTotalPrice
  } = useCartStore();

  const [couponCode, setCouponCode] = useState('');
  const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Sync with server on mount
  useEffect(() => {
    setIsMounted(true);
    syncWithServer();
  }, [syncWithServer]);

  // Handle quantity update
  const handleUpdateQuantity = async (lineId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      await updateItem(lineId, newQuantity);
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  };

  // Handle remove item
  const handleRemoveItem = async (lineId: string) => {
    try {
      await removeItem(lineId);
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  // Handle apply coupon
  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) {
      toast.error('Please enter a coupon code');
      return;
    }

    setIsApplyingCoupon(true);
    try {
      // TODO: Implement discount code application with cartDiscountCodesUpdate
      toast.info('Coupon feature coming soon!');
    } catch (error) {
      toast.error('Failed to apply coupon');
    } finally {
      setIsApplyingCoupon(false);
    }
  };

  // Handle checkout
  const handleCheckout = () => {
    if (!cart?.checkoutUrl) {
      toast.error('Unable to proceed to checkout');
      return;
    }
    window.location.href = cart.checkoutUrl;
  };

  // Calculate free shipping progress
  const subtotal = getTotalPrice();
  const shippingProgress = Math.min((subtotal / FREE_SHIPPING_THRESHOLD) * 100, 100);
  const amountToFreeShipping = Math.max(FREE_SHIPPING_THRESHOLD - subtotal, 0);

  // Don't render until mounted (avoid hydration mismatch)
  if (!isMounted) {
    return null;
  }

  // Loading state
  if (isLoading && !cart) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  // Empty cart state
  if (!cart || cart.lines.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-md mx-auto text-center">
          <div className="mb-8">
            <ShoppingBag className="w-24 h-24 mx-auto text-gray-300" />
          </div>
          <h1 className="text-3xl font-bold mb-4">Your cart is empty</h1>
          <p className="text-gray-600 mb-8">
            Looks like you haven't added anything to your cart yet.
          </p>
          <button
            onClick={() => router.push('/products')}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold inline-flex items-center gap-2"
          >
            <ShoppingBag className="w-5 h-5" />
            Start Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push('/products')}
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Continue Shopping
        </button>
        <h1 className="text-3xl font-bold">Shopping Cart</h1>
        <p className="text-gray-600 mt-2">
          {getTotalItems()} {getTotalItems() === 1 ? 'item' : 'items'} in your cart
        </p>
      </div>

      {/* Free Shipping Progress Bar */}
      {shippingProgress < 100 && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Truck className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-blue-900 font-medium">
              Add {amountToFreeShipping.toLocaleString('ko-KR')} KRW more for FREE shipping!
            </p>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${shippingProgress}%` }}
            />
          </div>
        </div>
      )}

      {shippingProgress === 100 && (
        <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-green-600" />
            <p className="text-sm text-green-900 font-medium">
              Congratulations! You qualify for FREE shipping!
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.lines.map((line) => (
            <div
              key={line.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex gap-4">
                {/* Product Image */}
                <div className="relative h-24 w-24 bg-gray-100 rounded flex-shrink-0 overflow-hidden">
                  {line.merchandise.product.featuredImage?.url ? (
                    <Image
                      src={line.merchandise.product.featuredImage.url}
                      alt={line.merchandise.product.featuredImage.altText || line.merchandise.product.title}
                      fill
                      className="object-cover"
                      sizes="96px"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                      No Image
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-lg mb-1 truncate">
                    {line.merchandise.product.title}
                  </h3>
                  {line.merchandise.title !== 'Default Title' && (
                    <p className="text-sm text-gray-600 mb-2">
                      {line.merchandise.title}
                    </p>
                  )}
                  <p className="text-gray-900 font-medium">
                    {parseFloat(line.merchandise.price.amount).toLocaleString('ko-KR')} {line.merchandise.price.currencyCode}
                  </p>
                </div>

                {/* Quantity Controls */}
                <div className="flex flex-col items-end gap-4">
                  <button
                    onClick={() => handleRemoveItem(line.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                    disabled={isLoading}
                  >
                    <X className="w-5 h-5" />
                  </button>

                  <div className="flex items-center gap-2 bg-gray-100 rounded-lg">
                    <button
                      onClick={() => handleUpdateQuantity(line.id, line.quantity - 1)}
                      className="p-2 hover:bg-gray-200 rounded-l-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={isLoading || line.quantity <= 1}
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="font-semibold min-w-[2rem] text-center">
                      {line.quantity}
                    </span>
                    <button
                      onClick={() => handleUpdateQuantity(line.id, line.quantity + 1)}
                      className="p-2 hover:bg-gray-200 rounded-r-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={isLoading}
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Line Total */}
                  <div className="text-right">
                    <p className="font-bold text-lg text-blue-600">
                      {parseFloat(line.cost.totalAmount.amount).toLocaleString('ko-KR')} {line.cost.totalAmount.currencyCode}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Clear Cart Button */}
          <div className="flex justify-end pt-4">
            <button
              onClick={() => {
                if (confirm('Are you sure you want to clear your cart?')) {
                  clearCart();
                }
              }}
              className="text-sm text-red-600 hover:text-red-800 hover:underline"
            >
              Clear Cart
            </button>
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 sticky top-4">
            <h2 className="text-xl font-bold mb-6">Order Summary</h2>

            {/* Coupon Code */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Coupon Code
              </label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                    placeholder="ENTER CODE"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={handleApplyCoupon}
                  disabled={isApplyingCoupon || !couponCode.trim()}
                  className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  Apply
                </button>
              </div>
              {cart.discountCodes && cart.discountCodes.length > 0 && (
                <div className="mt-2">
                  {cart.discountCodes.map((discount) => (
                    <div key={discount.code} className="text-sm text-green-600 flex items-center gap-1">
                      <Tag className="w-3 h-3" />
                      {discount.code} {discount.applicable ? 'applied' : '(not applicable)'}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Price Breakdown */}
            <div className="space-y-3 mb-6 pb-6 border-b border-gray-200">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span className="font-medium">
                  {parseFloat(cart.cost.subtotalAmount.amount).toLocaleString('ko-KR')} {cart.cost.subtotalAmount.currencyCode}
                </span>
              </div>

              <div className="flex justify-between text-gray-600">
                <span>Shipping</span>
                <span className="font-medium text-green-600">
                  {shippingProgress === 100 ? 'FREE' : 'Calculated at checkout'}
                </span>
              </div>

              {cart.cost.totalTaxAmount && parseFloat(cart.cost.totalTaxAmount.amount) > 0 && (
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span className="font-medium">
                    {parseFloat(cart.cost.totalTaxAmount.amount).toLocaleString('ko-KR')} {cart.cost.totalTaxAmount.currencyCode}
                  </span>
                </div>
              )}
            </div>

            {/* Total */}
            <div className="flex justify-between items-center mb-6">
              <span className="text-lg font-bold">Total</span>
              <span className="text-2xl font-bold text-blue-600">
                {parseFloat(cart.cost.totalAmount.amount).toLocaleString('ko-KR')} {cart.cost.totalAmount.currencyCode}
              </span>
            </div>

            {/* Checkout Button */}
            <button
              onClick={handleCheckout}
              disabled={isLoading}
              className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-3"
            >
              Proceed to Checkout
            </button>

            {/* Continue Shopping */}
            <button
              onClick={() => router.push('/products')}
              className="w-full px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-semibold transition-colors"
            >
              Continue Shopping
            </button>

            {/* Payment Methods */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center mb-3">
                We accept
              </p>
              <div className="flex justify-center gap-2 flex-wrap">
                <div className="px-3 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                  VISA
                </div>
                <div className="px-3 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                  Mastercard
                </div>
                <div className="px-3 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                  KakaoPay
                </div>
                <div className="px-3 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                  NaverPay
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
