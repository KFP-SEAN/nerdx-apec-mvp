'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  ShoppingCart,
  Heart,
  Eye,
  Star,
  Video,
  ArrowRight,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  category?: string;
  rating?: number;
  reviews_count?: number;
  video_url?: string;
  stock?: number;
}

interface ProductCardProps {
  product: Product;
  viewMode?: 'grid' | 'list';
}

export default function ProductCard({ product, viewMode = 'grid' }: ProductCardProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    toast.success(`Added ${product.name} to cart!`);
  };

  const handleToggleLike = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsLiked(!isLiked);
    toast.success(isLiked ? 'Removed from wishlist' : 'Added to wishlist');
  };

  if (viewMode === 'list') {
    return (
      <Link href={`/products/${product.id}`}>
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="card flex gap-6 hover:shadow-xl transition-shadow duration-300"
        >
          <div className="relative w-48 h-48 flex-shrink-0">
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover rounded-lg"
            />
            {product.video_url && (
              <div className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm text-white px-2 py-1 rounded-full flex items-center gap-1 text-xs">
                <Video className="w-3 h-3" />
                <span>Video</span>
              </div>
            )}
          </div>

          <div className="flex-1 flex flex-col justify-between">
            <div>
              {product.category && (
                <span className="text-xs text-primary-600 font-semibold uppercase tracking-wide">
                  {product.category}
                </span>
              )}
              <h3 className="text-xl font-bold mt-1 mb-2">{product.name}</h3>
              <p className="text-gray-600 line-clamp-2 mb-4">{product.description}</p>

              {product.rating && (
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.floor(product.rating!)
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">
                    {product.rating} ({product.reviews_count} reviews)
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div>
                <span className="text-3xl font-bold text-primary-600">
                  ${product.price.toFixed(2)}
                </span>
                {product.stock !== undefined && product.stock < 10 && (
                  <p className="text-sm text-red-600 mt-1">
                    Only {product.stock} left in stock!
                  </p>
                )}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleToggleLike}
                  className={`p-3 rounded-lg border transition-colors ${
                    isLiked
                      ? 'bg-red-50 border-red-200 text-red-600'
                      : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                </button>
                <button
                  onClick={handleAddToCart}
                  className="btn-primary flex items-center gap-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  <span>Add to Cart</span>
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </Link>
    );
  }

  return (
    <Link href={`/products/${product.id}`}>
      <motion.div
        whileHover={{ y: -8 }}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        className="card product-card group relative overflow-hidden"
      >
        {/* Image */}
        <div className="relative aspect-square mb-4 overflow-hidden rounded-lg">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          />

          {/* Video Badge */}
          {product.video_url && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm text-white px-3 py-1 rounded-full flex items-center gap-1 text-sm"
            >
              <Video className="w-4 h-4" />
              <span>Video</span>
            </motion.div>
          )}

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute top-2 right-2 flex flex-col gap-2"
          >
            <button
              onClick={handleToggleLike}
              className={`w-10 h-10 rounded-full flex items-center justify-center backdrop-blur-sm transition-colors ${
                isLiked
                  ? 'bg-red-500 text-white'
                  : 'bg-white/90 text-gray-700 hover:bg-white'
              }`}
            >
              <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
            </button>
            <button className="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-gray-700 hover:bg-white transition-colors">
              <Eye className="w-5 h-5" />
            </button>
          </motion.div>

          {/* Overlay on Hover */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end justify-center pb-4"
          >
            <button
              onClick={handleAddToCart}
              className="bg-white text-primary-600 px-6 py-2 rounded-lg font-semibold flex items-center gap-2 hover:bg-gray-100 transition-colors"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Add to Cart</span>
            </button>
          </motion.div>
        </div>

        {/* Content */}
        <div>
          {product.category && (
            <span className="text-xs text-primary-600 font-semibold uppercase tracking-wide">
              {product.category}
            </span>
          )}

          <h3 className="font-bold text-lg mt-1 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
            {product.name}
          </h3>

          <p className="text-gray-600 text-sm line-clamp-2 mb-3">{product.description}</p>

          {/* Rating */}
          {product.rating && (
            <div className="flex items-center gap-2 mb-3">
              <div className="flex items-center gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < Math.floor(product.rating!)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-600">
                ({product.reviews_count})
              </span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-primary-600">
              ${product.price.toFixed(2)}
            </span>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
          </div>

          {/* Stock Warning */}
          {product.stock !== undefined && product.stock < 10 && (
            <p className="text-sm text-red-600 mt-2 font-medium">
              Only {product.stock} left!
            </p>
          )}
        </div>
      </motion.div>
    </Link>
  );
}
