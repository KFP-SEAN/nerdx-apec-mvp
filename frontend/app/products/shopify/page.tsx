/**
 * Shopify Products Page
 *
 * Displays products from Shopify with filtering, sorting, and AR badges
 */

'use client';

import { useState, useEffect } from 'react';
import { shopifyService, ShopifyProduct } from '@/lib/shopify/client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function ShopifyProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<ShopifyProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState({
    search: '',
    sortBy: 'title' as 'title' | 'price-asc' | 'price-desc' | 'newest',
    arOnly: false,
    apecOnly: false
  });

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    try {
      setLoading(true);
      setError(null);

      const data = await shopifyService.getProducts();
      setProducts(data);
    } catch (err) {
      console.error('Error loading products:', err);
      setError('상품을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  // Filter and sort products
  const filteredProducts = products
    .filter(product => {
      // Search filter
      if (filter.search && !product.title.toLowerCase().includes(filter.search.toLowerCase())) {
        return false;
      }

      // AR only filter
      if (filter.arOnly && !product.metafields?.arEnabled) {
        return false;
      }

      // APEC limited only filter
      if (filter.apecOnly && !product.metafields?.apecLimited) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      switch (filter.sortBy) {
        case 'price-asc':
          return parseFloat(a.priceRange.minVariantPrice.amount) - parseFloat(b.priceRange.minVariantPrice.amount);
        case 'price-desc':
          return parseFloat(b.priceRange.minVariantPrice.amount) - parseFloat(a.priceRange.minVariantPrice.amount);
        case 'title':
          return a.title.localeCompare(b.title);
        case 'newest':
        default:
          return 0;
      }
    });

  async function handleBuyNow(product: ShopifyProduct) {
    try {
      const checkout = await shopifyService.createCheckout([
        {
          variantId: product.variants[0].id,
          quantity: 1,
          customAttributes: product.metafields?.arEnabled ? [
            { key: 'ar_enabled', value: 'true' }
          ] : undefined
        }
      ]);

      // Redirect to Shopify Checkout
      window.location.href = checkout.webUrl;
    } catch (err) {
      console.error('Error creating checkout:', err);
      alert('주문 생성에 실패했습니다.');
    }
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

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl">{error}</p>
          <button
            onClick={loadProducts}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">NERD 제품</h1>
        <p className="text-gray-600">Shopify로 구동되는 프리미엄 한국 전통주</p>
      </div>

      {/* Filters */}
      <div className="mb-8 bg-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <input
            type="text"
            placeholder="상품 검색..."
            value={filter.search}
            onChange={(e) => setFilter({ ...filter, search: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          {/* Sort */}
          <select
            value={filter.sortBy}
            onChange={(e) => setFilter({ ...filter, sortBy: e.target.value as any })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="title">이름순</option>
            <option value="price-asc">가격 낮은순</option>
            <option value="price-desc">가격 높은순</option>
            <option value="newest">최신순</option>
          </select>

          {/* AR Only */}
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filter.arOnly}
              onChange={(e) => setFilter({ ...filter, arOnly: e.target.checked })}
              className="w-5 h-5"
            />
            <span>AR 체험 가능만</span>
          </label>

          {/* APEC Only */}
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filter.apecOnly}
              onChange={(e) => setFilter({ ...filter, apecOnly: e.target.checked })}
              className="w-5 h-5"
            />
            <span>APEC 한정판만</span>
          </label>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          {filteredProducts.length}개의 상품
        </div>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <div
            key={product.id}
            className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            onClick={() => router.push(`/products/shopify/${product.handle}`)}
          >
            {/* Product Image */}
            <div className="relative h-64 bg-gray-100">
              {product.images[0] ? (
                <Image
                  src={product.images[0].url}
                  alt={product.images[0].altText || product.title}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
                  No Image
                </div>
              )}

              {/* Badges */}
              <div className="absolute top-2 left-2 flex flex-col space-y-2">
                {product.metafields?.arEnabled && (
                  <span className="bg-purple-600 text-white text-xs px-3 py-1 rounded-full">
                    AR 체험 가능
                  </span>
                )}
                {product.metafields?.apecLimited && (
                  <span className="bg-red-600 text-white text-xs px-3 py-1 rounded-full">
                    APEC 한정판
                  </span>
                )}
              </div>

              {/* Stock */}
              {product.metafields?.stockRemaining !== undefined && (
                <div className="absolute top-2 right-2">
                  <span className="bg-black bg-opacity-70 text-white text-xs px-3 py-1 rounded-full">
                    재고: {product.metafields.stockRemaining}개
                  </span>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="p-4">
              <h3 className="text-xl font-bold mb-2 line-clamp-2">{product.title}</h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {product.description}
              </p>

              {/* Price */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-2xl font-bold text-blue-600">
                    ${product.priceRange.minVariantPrice.amount}
                  </span>
                  <span className="text-gray-500 text-sm ml-2">
                    {product.priceRange.minVariantPrice.currencyCode}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/products/shopify/${product.handle}`);
                  }}
                  className="flex-1 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
                >
                  상세보기
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleBuyNow(product);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  바로 구매
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-xl">검색 결과가 없습니다.</p>
          <button
            onClick={() => setFilter({
              search: '',
              sortBy: 'title',
              arOnly: false,
              apecOnly: false
            })}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            필터 초기화
          </button>
        </div>
      )}
    </div>
  );
}
