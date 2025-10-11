/**
 * Product Detail Page
 * Based on SHOPIFY_PRD.md Section 2.2 specifications
 *
 * Features:
 * - Image gallery with zoom functionality
 * - Product title, price, description
 * - Metafields display (AR enabled, APEC limited, stock remaining)
 * - Quantity selector (1-10)
 * - Variant selector
 * - Add to Cart / Buy Now / Add to Wishlist buttons
 * - Share buttons
 * - Product tags
 * - AR View button (if enabled)
 * - Recommended products section
 * - SEO metadata
 * - Mobile responsive
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingCart,
  Heart,
  Share2,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  Cube,
  Tag,
  Truck,
  RefreshCw,
  Check,
  AlertCircle,
  Star,
  Facebook,
  Twitter,
  Copy,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Import Shopify services
import { shopifyService, ShopifyProduct } from '@/lib/shopify/client';
import { getOrCreateCart, cartLinesAdd } from '@/lib/shopify/cart';
import { useWishlistStore } from '@/lib/store';

interface ProductDetailPageProps {
  params: {
    handle: string;
  };
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const router = useRouter();
  const { addItem: addToWishlist, removeItem: removeFromWishlist, isInWishlist } = useWishlistStore();

  // State
  const [product, setProduct] = useState<ShopifyProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedVariantIndex, setSelectedVariantIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [isZoomed, setIsZoomed] = useState(false);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [relatedProducts, setRelatedProducts] = useState<ShopifyProduct[]>([]);

  // Load product on mount
  useEffect(() => {
    loadProduct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.handle]);

  async function loadProduct() {
    try {
      setLoading(true);
      setError(null);

      const data = await shopifyService.getProductByHandle(params.handle);

      if (!data) {
        setError('Product not found');
        return;
      }

      setProduct(data);

      // Load related products
      loadRelatedProducts(data.tags);
    } catch (err) {
      console.error('Error loading product:', err);
      setError('Failed to load product. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function loadRelatedProducts(tags?: string[]) {
    try {
      // Fetch products with similar tags
      const products = await shopifyService.getProducts({ first: 4 });
      setRelatedProducts(products.filter(p => p.handle !== params.handle).slice(0, 3));
    } catch (err) {
      console.error('Error loading related products:', err);
    }
  }

  // Add to Cart handler
  async function handleAddToCart() {
    if (!product) return;

    try {
      setIsAddingToCart(true);

      const cart = await getOrCreateCart();
      const selectedVariant = product.variants[selectedVariantIndex];

      await cartLinesAdd(cart.id, [
        {
          merchandiseId: selectedVariant.id,
          quantity: quantity,
        },
      ]);

      toast.success(
        <div className="flex items-center gap-2">
          <Check className="w-5 h-5" />
          <span>Added to cart!</span>
        </div>
      );
    } catch (err) {
      console.error('Error adding to cart:', err);
      toast.error('Failed to add to cart. Please try again.');
    } finally {
      setIsAddingToCart(false);
    }
  }

  // Buy Now handler
  async function handleBuyNow() {
    if (!product) return;

    try {
      setIsAddingToCart(true);

      const cart = await getOrCreateCart();
      const selectedVariant = product.variants[selectedVariantIndex];

      const updatedCart = await cartLinesAdd(cart.id, [
        {
          merchandiseId: selectedVariant.id,
          quantity: quantity,
        },
      ]);

      // Redirect to checkout
      if (updatedCart.checkoutUrl) {
        window.location.href = updatedCart.checkoutUrl;
      } else {
        router.push('/cart');
      }
    } catch (err) {
      console.error('Error during buy now:', err);
      toast.error('Failed to proceed to checkout. Please try again.');
      setIsAddingToCart(false);
    }
  }

  // Wishlist handlers
  function handleToggleWishlist() {
    if (!product) return;

    const productInWishlist = isInWishlist(product.id);

    if (productInWishlist) {
      removeFromWishlist(product.id);
      toast.success('Removed from wishlist');
    } else {
      addToWishlist({
        id: product.id,
        product_id: product.id,
        name: product.title,
        price: parseFloat(product.variants[selectedVariantIndex].price),
        image_url: product.images[0]?.url || '',
      });
      toast.success('Added to wishlist');
    }
  }

  // Share handlers
  function handleShare(platform: 'facebook' | 'twitter' | 'copy') {
    const url = typeof window !== 'undefined' ? window.location.href : '';

    switch (platform) {
      case 'facebook':
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
        break;
      case 'twitter':
        window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(product?.title || '')}`, '_blank');
        break;
      case 'copy':
        navigator.clipboard.writeText(url);
        toast.success('Link copied to clipboard!');
        break;
    }

    setShowShareModal(false);
  }

  // Image navigation
  function nextImage() {
    if (!product) return;
    setSelectedImageIndex((prev) => (prev + 1) % product.images.length);
  }

  function prevImage() {
    if (!product) return;
    setSelectedImageIndex((prev) => (prev - 1 + product.images.length) % product.images.length);
  }

  // Quantity handlers
  function incrementQuantity() {
    if (quantity < 10) {
      setQuantity(quantity + 1);
    }
  }

  function decrementQuantity() {
    if (quantity > 1) {
      setQuantity(quantity - 1);
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading product...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-4">Product Not Found</h1>
          <p className="text-gray-600 mb-6">
            {error || "We couldn't find the product you're looking for."}
          </p>
          <button
            onClick={() => router.push('/products')}
            className="btn-primary inline-flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Back to Products</span>
          </button>
        </div>
      </div>
    );
  }

  const selectedVariant = product.variants[selectedVariantIndex];
  const selectedImage = product.images[selectedImageIndex];
  const isProductInWishlist = isInWishlist(product.id);
  const isOutOfStock = !selectedVariant.available;
  const price = parseFloat(selectedVariant.price);
  const totalPrice = price * quantity;

  return (
    <>
      {/* SEO Metadata */}
      <title>{product.title} | NERDX APEC</title>
      <meta name="description" content={product.description} />
      <meta property="og:title" content={product.title} />
      <meta property="og:description" content={product.description} />
      <meta property="og:image" content={selectedImage?.url} />
      <meta property="og:type" content="product" />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-gray-600 mb-6">
          <Link href="/" className="hover:text-primary-600">Home</Link>
          <ChevronRight className="w-4 h-4" />
          <Link href="/products" className="hover:text-primary-600">Products</Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">{product.title}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 mb-16">
          {/* Left Column - Image Gallery */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative aspect-square bg-gray-100 rounded-2xl overflow-hidden group">
              {selectedImage ? (
                <>
                  <Image
                    src={selectedImage.url}
                    alt={selectedImage.altText || product.title}
                    fill
                    className="object-cover"
                    priority
                  />

                  {/* Zoom button */}
                  <button
                    onClick={() => setIsZoomed(true)}
                    className="absolute top-4 right-4 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-gray-700 hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <ZoomIn className="w-5 h-5" />
                  </button>

                  {/* Navigation arrows */}
                  {product.images.length > 1 && (
                    <>
                      <button
                        onClick={prevImage}
                        className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-gray-700 hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </button>
                      <button
                        onClick={nextImage}
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-gray-700 hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </>
                  )}
                </>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
                  <p>No image available</p>
                </div>
              )}
            </div>

            {/* Thumbnail Gallery */}
            {product.images.length > 1 && (
              <div className="grid grid-cols-4 gap-3">
                {product.images.map((image, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`relative aspect-square bg-gray-100 rounded-lg overflow-hidden transition-all ${
                      selectedImageIndex === index
                        ? 'ring-2 ring-primary-600 ring-offset-2'
                        : 'hover:opacity-75'
                    }`}
                  >
                    <Image
                      src={image.url}
                      alt={image.altText || `${product.title} - ${index + 1}`}
                      fill
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Right Column - Product Info */}
          <div className="space-y-6">
            {/* Badges */}
            <div className="flex flex-wrap gap-2">
              {product.metafields?.arEnabled && (
                <span className="inline-flex items-center gap-1 bg-purple-100 text-purple-700 text-xs font-semibold px-3 py-1 rounded-full">
                  <Cube className="w-3 h-3" />
                  AR Enabled
                </span>
              )}
              {product.metafields?.apecLimited && (
                <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-3 py-1 rounded-full">
                  <Star className="w-3 h-3" />
                  APEC Limited Edition
                </span>
              )}
              {product.metafields?.stockRemaining !== undefined && product.metafields.stockRemaining < 10 && (
                <span className="inline-flex items-center gap-1 bg-orange-100 text-orange-700 text-xs font-semibold px-3 py-1 rounded-full">
                  <AlertCircle className="w-3 h-3" />
                  Only {product.metafields.stockRemaining} left
                </span>
              )}
              {isOutOfStock && (
                <span className="inline-flex items-center gap-1 bg-gray-100 text-gray-700 text-xs font-semibold px-3 py-1 rounded-full">
                  Out of Stock
                </span>
              )}
            </div>

            {/* Title */}
            <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">
              {product.title}
            </h1>

            {/* Price */}
            <div className="flex items-baseline gap-3">
              <span className="text-4xl font-bold text-primary-600">
                ${price.toFixed(2)}
              </span>
              <span className="text-lg text-gray-500">
                {product.priceRange.minVariantPrice.currencyCode}
              </span>
            </div>

            {/* Description */}
            <div className="prose max-w-none">
              <div
                className="text-gray-700 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: product.descriptionHtml }}
              />
            </div>

            {/* Variant Selector */}
            {product.variants.length > 1 && (
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Options
                </label>
                <select
                  value={selectedVariantIndex}
                  onChange={(e) => setSelectedVariantIndex(Number(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all"
                >
                  {product.variants.map((variant, index) => (
                    <option key={variant.id} value={index}>
                      {variant.title} - ${variant.price} {variant.available ? '' : '(Out of Stock)'}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Quantity Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Quantity
              </label>
              <div className="flex items-center gap-4">
                <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                  <button
                    onClick={decrementQuantity}
                    disabled={quantity <= 1}
                    className="px-4 py-3 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="text-lg font-semibold">-</span>
                  </button>
                  <span className="px-6 py-3 text-lg font-semibold border-x border-gray-300">
                    {quantity}
                  </span>
                  <button
                    onClick={incrementQuantity}
                    disabled={quantity >= 10}
                    className="px-4 py-3 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="text-lg font-semibold">+</span>
                  </button>
                </div>
                <span className="text-sm text-gray-600">Maximum 10 per order</span>
              </div>

              {/* Total Price */}
              {quantity > 1 && (
                <p className="mt-2 text-sm text-gray-600">
                  Total: <span className="font-semibold text-gray-900">${totalPrice.toFixed(2)}</span>
                </p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              {/* Add to Cart */}
              <button
                onClick={handleAddToCart}
                disabled={isOutOfStock || isAddingToCart}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAddingToCart ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Adding...</span>
                  </>
                ) : (
                  <>
                    <ShoppingCart className="w-5 h-5" />
                    <span>{isOutOfStock ? 'Out of Stock' : 'Add to Cart'}</span>
                  </>
                )}
              </button>

              {/* Buy Now */}
              <button
                onClick={handleBuyNow}
                disabled={isOutOfStock || isAddingToCart}
                className="w-full bg-gray-900 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{isOutOfStock ? 'Out of Stock' : 'Buy Now'}</span>
              </button>

              {/* Secondary Actions */}
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={handleToggleWishlist}
                  className={`flex items-center justify-center gap-2 py-3 px-6 rounded-lg border-2 font-semibold transition-all ${
                    isProductInWishlist
                      ? 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Heart className={`w-5 h-5 ${isProductInWishlist ? 'fill-current' : ''}`} />
                  <span>{isProductInWishlist ? 'In Wishlist' : 'Add to Wishlist'}</span>
                </button>

                <button
                  onClick={() => setShowShareModal(true)}
                  className="flex items-center justify-center gap-2 py-3 px-6 rounded-lg border-2 border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold transition-all"
                >
                  <Share2 className="w-5 h-5" />
                  <span>Share</span>
                </button>
              </div>
            </div>

            {/* AR View Button */}
            {product.metafields?.arEnabled && product.metafields?.arAssetUrl && (
              <button
                onClick={() => router.push(`/ar-viewer?product=${product.handle}`)}
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg"
              >
                <Cube className="w-5 h-5" />
                <span>View in AR</span>
              </button>
            )}

            {/* Product Tags */}
            {product.tags && product.tags.length > 0 && (
              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Tag className="w-4 h-4" />
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <Link
                      key={tag}
                      href={`/products?tag=${encodeURIComponent(tag)}`}
                      className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
                    >
                      {tag}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Shipping & Returns Info */}
            <div className="pt-6 border-t border-gray-200 space-y-4">
              <div className="flex items-start gap-3">
                <Truck className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-gray-900">Free Shipping</h4>
                  <p className="text-sm text-gray-600">Orders over $50 ship free</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <RefreshCw className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-gray-900">Easy Returns</h4>
                  <p className="text-sm text-gray-600">30-day return policy</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Related Products Section */}
        {relatedProducts.length > 0 && (
          <div className="mt-16 pt-16 border-t border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">You May Also Like</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {relatedProducts.map((relatedProduct) => (
                <Link
                  key={relatedProduct.id}
                  href={`/products/${relatedProduct.handle}`}
                  className="group"
                >
                  <div className="card hover:shadow-xl transition-shadow">
                    <div className="relative aspect-square mb-4 bg-gray-100 rounded-lg overflow-hidden">
                      {relatedProduct.images[0] ? (
                        <Image
                          src={relatedProduct.images[0].url}
                          alt={relatedProduct.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full text-gray-400">
                          No image
                        </div>
                      )}
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                      {relatedProduct.title}
                    </h3>
                    <p className="text-primary-600 font-bold">
                      ${parseFloat(relatedProduct.variants[0].price).toFixed(2)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Share Modal */}
      <AnimatePresence>
        {showShareModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowShareModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Share Product</h3>
                <button
                  onClick={() => setShowShareModal(false)}
                  className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => handleShare('facebook')}
                  className="w-full flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <Facebook className="w-5 h-5 text-blue-600" />
                  <span className="font-medium">Share on Facebook</span>
                </button>

                <button
                  onClick={() => handleShare('twitter')}
                  className="w-full flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <Twitter className="w-5 h-5 text-sky-500" />
                  <span className="font-medium">Share on Twitter</span>
                </button>

                <button
                  onClick={() => handleShare('copy')}
                  className="w-full flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <Copy className="w-5 h-5 text-gray-700" />
                  <span className="font-medium">Copy Link</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Image Zoom Modal */}
      <AnimatePresence>
        {isZoomed && selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
            onClick={() => setIsZoomed(false)}
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
              className="relative w-full h-full max-w-6xl max-h-[90vh]"
              onClick={(e) => e.stopPropagation()}
            >
              <Image
                src={selectedImage.url}
                alt={selectedImage.altText || product.title}
                fill
                className="object-contain"
              />
              <button
                onClick={() => setIsZoomed(false)}
                className="absolute top-4 right-4 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-gray-700 hover:bg-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
