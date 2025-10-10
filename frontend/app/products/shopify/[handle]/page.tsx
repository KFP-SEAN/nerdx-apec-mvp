/**
 * Shopify Product Detail Page
 *
 * Displays detailed product information with:
 * - Image gallery
 * - Variant selection
 * - AR preview (if enabled)
 * - Add to cart / Buy now
 * - Stock information
 */

'use client';

import { useState, useEffect } from 'react';
import { shopifyService, ShopifyProduct } from '@/lib/shopify/client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { ArrowLeft, Cube, ShoppingCart, CreditCard, Package, Info } from 'lucide-react';

interface ProductDetailPageProps {
  params: {
    handle: string;
  };
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const router = useRouter();
  const [product, setProduct] = useState<ShopifyProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVariantId, setSelectedVariantId] = useState<string>('');
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [addingToCart, setAddingToCart] = useState(false);
  const [showARPreview, setShowARPreview] = useState(false);

  useEffect(() => {
    loadProduct();
  }, [params.handle]);

  async function loadProduct() {
    try {
      setLoading(true);
      setError(null);

      const data = await shopifyService.getProductByHandle(params.handle);

      if (!data) {
        setError('상품을 찾을 수 없습니다.');
        return;
      }

      setProduct(data);

      // Set default variant
      if (data.variants.length > 0) {
        setSelectedVariantId(data.variants[0].id);
      }
    } catch (err) {
      console.error('Error loading product:', err);
      setError('상품을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddToCart() {
    if (!product || !selectedVariantId) return;

    try {
      setAddingToCart(true);

      // Get or create checkout from localStorage
      let checkoutId = localStorage.getItem('shopify_checkout_id');
      let checkout;

      if (checkoutId) {
        // Add to existing checkout
        checkout = await shopifyService.addToCheckout(checkoutId, [{
          variantId: selectedVariantId,
          quantity,
          customAttributes: product.metafields?.arEnabled ? [
            { key: 'ar_enabled', value: 'true' }
          ] : undefined
        }]);
      } else {
        // Create new checkout
        checkout = await shopifyService.createCheckout([{
          variantId: selectedVariantId,
          quantity,
          customAttributes: product.metafields?.arEnabled ? [
            { key: 'ar_enabled', value: 'true' }
          ] : undefined
        }]);
        localStorage.setItem('shopify_checkout_id', checkout.id);
      }

      // Show success message
      alert(`${product.title}이(가) 장바구니에 추가되었습니다.`);

      // Optionally navigate to cart
      // router.push('/cart');
    } catch (err) {
      console.error('Error adding to cart:', err);
      alert('장바구니 추가에 실패했습니다.');
    } finally {
      setAddingToCart(false);
    }
  }

  async function handleBuyNow() {
    if (!product || !selectedVariantId) return;

    try {
      const checkout = await shopifyService.createCheckout([{
        variantId: selectedVariantId,
        quantity,
        customAttributes: product.metafields?.arEnabled ? [
          { key: 'ar_enabled', value: 'true' }
        ] : undefined
      }]);

      // Redirect to Shopify Checkout
      window.location.href = checkout.webUrl;
    } catch (err) {
      console.error('Error creating checkout:', err);
      alert('주문 생성에 실패했습니다.');
    }
  }

  function openARPreview() {
    if (!product?.metafields?.arAssetUrl) return;

    setShowARPreview(true);

    // Open AR viewer in new window or modal
    // This will be integrated with the AR service later
    window.open(
      `/ar-viewer?asset=${encodeURIComponent(product.metafields.arAssetUrl)}&product=${product.handle}`,
      '_blank',
      'width=800,height=600'
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">상품 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl">{error || '상품을 찾을 수 없습니다.'}</p>
          <button
            onClick={() => router.push('/products/shopify')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            상품 목록으로
          </button>
        </div>
      </div>
    );
  }

  const selectedVariant = product.variants.find(v => v.id === selectedVariantId);
  const currentPrice = selectedVariant?.price || product.priceRange.minVariantPrice.amount;
  const isAvailable = selectedVariant?.available !== false;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.push('/products/shopify')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            상품 목록으로
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Images */}
          <div>
            {/* Main Image */}
            <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-4">
              <div className="relative h-96 lg:h-[500px] bg-gray-100">
                {product.images[selectedImageIndex] ? (
                  <Image
                    src={product.images[selectedImageIndex].url}
                    alt={product.images[selectedImageIndex].altText || product.title}
                    fill
                    className="object-contain p-4"
                    priority
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    No Image
                  </div>
                )}
              </div>
            </div>

            {/* Thumbnail Gallery */}
            {product.images.length > 1 && (
              <div className="grid grid-cols-5 gap-2">
                {product.images.map((image, index) => (
                  <button
                    key={image.url}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`relative h-20 bg-white rounded-lg overflow-hidden border-2 transition ${
                      selectedImageIndex === index
                        ? 'border-blue-600'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Image
                      src={image.url}
                      alt={image.altText || `${product.title} ${index + 1}`}
                      fill
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            )}

            {/* AR Preview Button */}
            {product.metafields?.arEnabled && (
              <button
                onClick={openARPreview}
                className="w-full mt-4 px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center justify-center space-x-2"
              >
                <Cube className="w-5 h-5" />
                <span className="font-semibold">AR로 미리보기</span>
              </button>
            )}
          </div>

          {/* Right Column - Product Info */}
          <div>
            <div className="bg-white rounded-lg shadow-lg p-6 lg:p-8">
              {/* Badges */}
              <div className="flex flex-wrap gap-2 mb-4">
                {product.metafields?.arEnabled && (
                  <span className="bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full font-medium">
                    AR 체험 가능
                  </span>
                )}
                {product.metafields?.apecLimited && (
                  <span className="bg-red-100 text-red-800 text-sm px-3 py-1 rounded-full font-medium">
                    APEC 한정판
                  </span>
                )}
              </div>

              {/* Title */}
              <h1 className="text-3xl lg:text-4xl font-bold mb-4">{product.title}</h1>

              {/* Price */}
              <div className="mb-6">
                <div className="flex items-baseline space-x-2">
                  <span className="text-4xl font-bold text-blue-600">
                    ${currentPrice}
                  </span>
                  <span className="text-gray-500">
                    {product.priceRange.minVariantPrice.currencyCode}
                  </span>
                </div>
              </div>

              {/* Stock Info */}
              {product.metafields?.stockRemaining !== undefined && (
                <div className="mb-6 flex items-center space-x-2 text-sm">
                  <Package className="w-4 h-4 text-gray-500" />
                  <span className={product.metafields.stockRemaining > 0 ? 'text-green-600' : 'text-red-600'}>
                    재고: {product.metafields.stockRemaining}개
                  </span>
                </div>
              )}

              {/* Availability */}
              <div className="mb-6">
                {isAvailable ? (
                  <span className="text-green-600 font-medium">재고 있음</span>
                ) : (
                  <span className="text-red-600 font-medium">품절</span>
                )}
              </div>

              {/* Variant Selection */}
              {product.variants.length > 1 && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    옵션 선택
                  </label>
                  <select
                    value={selectedVariantId}
                    onChange={(e) => setSelectedVariantId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {product.variants.map((variant) => (
                      <option key={variant.id} value={variant.id}>
                        {variant.title} - ${variant.price}
                        {!variant.available && ' (품절)'}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Quantity */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  수량
                </label>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <span className="text-xl font-medium w-12 text-center">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    disabled={!isAvailable}
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 mb-6">
                <button
                  onClick={handleBuyNow}
                  disabled={!isAvailable}
                  className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <CreditCard className="w-5 h-5" />
                  <span className="font-semibold">바로 구매</span>
                </button>
                <button
                  onClick={handleAddToCart}
                  disabled={!isAvailable || addingToCart}
                  className="w-full px-6 py-4 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition disabled:border-gray-300 disabled:text-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  <span className="font-semibold">
                    {addingToCart ? '추가 중...' : '장바구니에 추가'}
                  </span>
                </button>
              </div>

              {/* Description */}
              <div className="border-t pt-6">
                <h2 className="text-xl font-bold mb-3 flex items-center">
                  <Info className="w-5 h-5 mr-2" />
                  상품 정보
                </h2>
                <div
                  className="prose prose-sm max-w-none text-gray-600"
                  dangerouslySetInnerHTML={{ __html: product.descriptionHtml }}
                />
              </div>

              {/* AR Info */}
              {product.metafields?.arEnabled && (
                <div className="border-t mt-6 pt-6">
                  <div className="bg-purple-50 rounded-lg p-4">
                    <h3 className="font-bold text-purple-900 mb-2 flex items-center">
                      <Cube className="w-5 h-5 mr-2" />
                      AR 체험 안내
                    </h3>
                    <p className="text-sm text-purple-800">
                      이 상품을 구매하시면 AR(증강현실)로 제품을 체험하실 수 있습니다.
                      구매 후 이메일로 전송되는 AR 액세스 코드를 사용하여
                      실제 환경에서 제품을 미리 확인해보세요.
                    </p>
                  </div>
                </div>
              )}

              {/* APEC Limited Info */}
              {product.metafields?.apecLimited && (
                <div className="border-t mt-6 pt-6">
                  <div className="bg-red-50 rounded-lg p-4">
                    <h3 className="font-bold text-red-900 mb-2">
                      APEC 한정판
                    </h3>
                    <p className="text-sm text-red-800">
                      APEC 2024를 기념하여 제작된 한정판 상품입니다.
                      수량이 제한되어 있으며, 품절 시 재입고되지 않습니다.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Related Products / Recently Viewed */}
        {/* TODO: Implement related products section */}
      </div>
    </div>
  );
}
