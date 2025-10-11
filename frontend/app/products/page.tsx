'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Grid3x3,
  List,
  ChevronDown,
  X,
  Loader2,
} from 'lucide-react';
import ProductCard from '@/components/ProductCard';
import { shopifyService, ShopifyProduct } from '@/lib/shopify/client';
import toast from 'react-hot-toast';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  category: string;
  tags: string[];
  stock: number;
  rating: number;
  reviews_count: number;
  video_url?: string;
}

interface Filters {
  category: string;
  minPrice: number;
  maxPrice: number;
  tags: string[];
  sortBy: string;
  apecLimited: boolean;
  arAvailable: boolean;
  inStock: boolean;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    category: '',
    minPrice: 0,
    maxPrice: 100000,
    tags: [],
    sortBy: 'recommended',
    apecLimited: false,
    arAvailable: false,
    inStock: false,
  });

  const categories = [
    'All',
    '막걸리',
    '소주',
    '청주',
    '과실주',
  ];

  const sortOptions = [
    { value: 'recommended', label: 'Recommended' },
    { value: 'newest', label: 'Newest' },
    { value: 'price_low', label: 'Price: Low to High' },
    { value: 'price_high', label: 'Price: High to Low' },
    { value: 'best_selling', label: 'Best Selling' },
  ];

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      loadProducts();
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [filters, searchQuery]);

  const loadProducts = async () => {
    try {
      setLoading(true);

      // Fetch products from Shopify
      const shopifyProducts = await shopifyService.getProducts({ first: 50 });

      // Transform Shopify products to our Product interface
      let transformedProducts: Product[] = shopifyProducts.map((sp: ShopifyProduct) => ({
        id: sp.id,
        name: sp.title,
        description: sp.description,
        price: parseFloat(sp.priceRange.minVariantPrice.amount),
        image_url: sp.images[0]?.url || '',
        category: sp.handle.split('-')[0] || 'Electronics', // Extract category from handle
        tags: [], // Can be extracted from Shopify tags if available
        stock: sp.metafields?.stockRemaining || 100,
        rating: 4.5, // Default rating
        reviews_count: Math.floor(Math.random() * 100), // Random review count
        video_url: undefined,
      }));

      // Apply filters
      if (searchQuery) {
        transformedProducts = transformedProducts.filter(p =>
          p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.description.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }

      if (filters.category && filters.category !== 'All') {
        transformedProducts = transformedProducts.filter(p =>
          p.category.toLowerCase() === filters.category.toLowerCase()
        );
      }

      // Filter by price range
      transformedProducts = transformedProducts.filter(p =>
        p.price >= filters.minPrice && p.price <= filters.maxPrice
      );

      // Filter by APEC Limited
      if (filters.apecLimited) {
        transformedProducts = transformedProducts.filter(p =>
          p.tags.includes('apec-limited') || p.name.toLowerCase().includes('apec')
        );
      }

      // Filter by AR Available
      if (filters.arAvailable) {
        transformedProducts = transformedProducts.filter(p =>
          p.tags.includes('ar-enabled') || p.video_url
        );
      }

      // Filter by In Stock
      if (filters.inStock) {
        transformedProducts = transformedProducts.filter(p => p.stock > 0);
      }

      // Sort products
      switch (filters.sortBy) {
        case 'price_low':
          transformedProducts.sort((a, b) => a.price - b.price);
          break;
        case 'price_high':
          transformedProducts.sort((a, b) => b.price - a.price);
          break;
        case 'best_selling':
          transformedProducts.sort((a, b) => b.reviews_count - a.reviews_count);
          break;
        case 'newest':
          // Already in newest order from Shopify
          break;
        default: // recommended
          transformedProducts.sort((a, b) => b.rating - a.rating);
      }

      setProducts(transformedProducts);
    } catch (error) {
      console.error('Failed to load products:', error);
      toast.error('Failed to load products from Shopify');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadProducts();
  };

  const clearFilters = () => {
    setFilters({
      category: '',
      minPrice: 0,
      maxPrice: 100000,
      tags: [],
      sortBy: 'recommended',
      apecLimited: false,
      arAvailable: false,
      inStock: false,
    });
    setSearchQuery('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="section-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-4">
            Discover <span className="text-gradient">Korean Traditional Liquors</span>
          </h1>
          <p className="text-xl text-gray-600">
            Browse our curated collection of premium 전통주 with AR experiences
          </p>
          {!loading && (
            <p className="text-sm text-gray-500 mt-2">
              {products.length} product{products.length !== 1 ? 's' : ''} found
            </p>
          )}
        </motion.div>

        {/* Search and Filters Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="card mb-8"
        >
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </form>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary flex items-center gap-2 whitespace-nowrap"
            >
              <Filter className="w-5 h-5" />
              <span>Filters</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${
                  showFilters ? 'rotate-180' : ''
                }`}
              />
            </button>

            {/* Sort */}
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            {/* View Mode Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-3 rounded-lg border ${
                  viewMode === 'grid'
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-3 rounded-lg border ${
                  viewMode === 'list'
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Expanded Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 pt-6 border-t border-gray-200 space-y-6"
            >
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-semibold mb-3">Category</label>
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() =>
                        setFilters({ ...filters, category: category === 'All' ? '' : category })
                      }
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        (category === 'All' && !filters.category) || filters.category === category
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-semibold mb-3">
                  Price Range (₩{filters.minPrice.toLocaleString()} - ₩{filters.maxPrice.toLocaleString()})
                </label>
                <div className="flex gap-4 items-center">
                  <div className="flex-1">
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.minPrice}
                      onChange={(e) =>
                        setFilters({ ...filters, minPrice: Number(e.target.value) })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <span className="text-gray-500">-</span>
                  <div className="flex-1">
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.maxPrice}
                      onChange={(e) =>
                        setFilters({ ...filters, maxPrice: Number(e.target.value) })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100000"
                  step="1000"
                  value={filters.maxPrice}
                  onChange={(e) =>
                    setFilters({ ...filters, maxPrice: Number(e.target.value) })
                  }
                  className="w-full mt-3"
                />
              </div>

              {/* Additional Filters */}
              <div>
                <label className="block text-sm font-semibold mb-3">Additional Filters</label>
                <div className="space-y-3">
                  {/* APEC Limited */}
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.apecLimited}
                      onChange={(e) =>
                        setFilters({ ...filters, apecLimited: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <span className="text-gray-700">APEC Limited Edition</span>
                  </label>

                  {/* AR Available */}
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.arAvailable}
                      onChange={(e) =>
                        setFilters({ ...filters, arAvailable: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <span className="text-gray-700">AR Experience Available</span>
                  </label>

                  {/* In Stock */}
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.inStock}
                      onChange={(e) =>
                        setFilters({ ...filters, inStock: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <span className="text-gray-700">In Stock Only</span>
                  </label>
                </div>
              </div>

              {/* Clear Filters */}
              <div className="flex justify-end">
                <button
                  onClick={clearFilters}
                  className="btn-secondary flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  <span>Clear All Filters</span>
                </button>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Products Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold mb-2">No products found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your filters or search query
            </p>
            <button onClick={clearFilters} className="btn-primary">
              Clear Filters
            </button>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                : 'space-y-4'
            }
          >
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
              >
                <ProductCard product={product} viewMode={viewMode} />
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Load More */}
        {!loading && products.length > 0 && (
          <div className="text-center mt-12">
            <button className="btn-outline">Load More Products</button>
          </div>
        )}
      </div>
    </div>
  );
}
