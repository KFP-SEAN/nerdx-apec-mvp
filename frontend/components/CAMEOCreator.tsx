'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  MessageSquare,
  User,
  Wand2,
  Loader2,
  Package,
} from 'lucide-react';
import ProductCard from './ProductCard';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface CAMEOCreatorProps {
  onSubmit: (request: {
    occasion: string;
    recipientName: string;
    personalMessage: string;
    selectedProducts: string[];
    tone: string;
    deliveryDate?: string;
  }) => void;
  isLoading: boolean;
}

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  category: string;
}

export default function CAMEOCreator({ onSubmit, isLoading }: CAMEOCreatorProps) {
  const [step, setStep] = useState(1);
  const [occasion, setOccasion] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [personalMessage, setPersonalMessage] = useState('');
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [tone, setTone] = useState('professional');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  const occasions = [
    'Birthday',
    'Anniversary',
    'Holiday',
    'Thank You',
    'Congratulations',
    'Get Well Soon',
    'Just Because',
    'Custom',
  ];

  const tones = [
    { value: 'professional', label: 'Professional', description: 'Formal and business-like' },
    { value: 'friendly', label: 'Friendly', description: 'Warm and approachable' },
    { value: 'enthusiastic', label: 'Enthusiastic', description: 'Energetic and exciting' },
    { value: 'heartfelt', label: 'Heartfelt', description: 'Sincere and emotional' },
  ];

  useEffect(() => {
    if (step === 3) {
      loadProducts();
    }
  }, [step]);

  const loadProducts = async () => {
    try {
      setLoadingProducts(true);
      const response = await api.get('/products?limit=12');
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Failed to load products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleToggleProduct = (productId: string) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter((id) => id !== productId));
    } else {
      if (selectedProducts.length >= 5) {
        toast.error('You can select up to 5 products');
        return;
      }
      setSelectedProducts([...selectedProducts, productId]);
    }
  };

  const handleSubmit = () => {
    if (!occasion || !recipientName || !personalMessage || selectedProducts.length === 0) {
      toast.error('Please fill in all required fields');
      return;
    }

    onSubmit({
      occasion,
      recipientName,
      personalMessage,
      selectedProducts,
      tone,
      deliveryDate,
    });
  };

  const canProceedToNextStep = () => {
    if (step === 1) return occasion && recipientName;
    if (step === 2) return personalMessage;
    if (step === 3) return selectedProducts.length > 0;
    return true;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        {/* Step Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {['Details', 'Message', 'Products', 'Review'].map((label, index) => (
              <div
                key={label}
                className={`flex-1 text-center ${
                  index < step
                    ? 'text-primary-600'
                    : index === step
                    ? 'text-primary-600 font-semibold'
                    : 'text-gray-400'
                }`}
              >
                <div className="text-sm mb-2">{label}</div>
                <div
                  className={`h-2 rounded-full ${
                    index < step
                      ? 'bg-primary-600'
                      : index === step
                      ? 'bg-primary-600'
                      : 'bg-gray-200'
                  }`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Basic Details */}
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-semibold mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Occasion *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {occasions.map((occ) => (
                  <button
                    key={occ}
                    onClick={() => setOccasion(occ)}
                    className={`px-4 py-3 rounded-lg font-medium transition-all ${
                      occasion === occ
                        ? 'bg-primary-600 text-white shadow-lg scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {occ}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2 flex items-center gap-2">
                <User className="w-4 h-4" />
                Recipient Name *
              </label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="Enter recipient's name"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Delivery Date (Optional)
              </label>
              <input
                type="date"
                value={deliveryDate}
                onChange={(e) => setDeliveryDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="input-field"
              />
            </div>
          </motion.div>
        )}

        {/* Step 2: Personal Message */}
        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-semibold mb-2 flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Personal Message *
              </label>
              <textarea
                value={personalMessage}
                onChange={(e) => setPersonalMessage(e.target.value)}
                placeholder="Write a personal message for the recipient..."
                rows={6}
                maxLength={500}
                className="input-field resize-none"
              />
              <div className="text-sm text-gray-500 mt-2">
                {personalMessage.length}/500 characters
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-3 flex items-center gap-2">
                <Wand2 className="w-4 h-4" />
                Video Tone
              </label>
              <div className="grid md:grid-cols-2 gap-4">
                {tones.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setTone(t.value)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      tone === t.value
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-semibold mb-1">{t.label}</div>
                    <div className="text-sm text-gray-600">{t.description}</div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 3: Product Selection */}
        {step === 3 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-semibold mb-3 flex items-center gap-2">
                <Package className="w-4 h-4" />
                Select Products (Max 5) *
              </label>
              <p className="text-sm text-gray-600 mb-4">
                Choose products you'd like featured in your CAMEO video
              </p>

              {loadingProducts ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
                </div>
              ) : (
                <div className="grid md:grid-cols-3 gap-4">
                  {products.map((product) => {
                    const isSelected = selectedProducts.includes(product.id);
                    return (
                      <div
                        key={product.id}
                        onClick={() => handleToggleProduct(product.id)}
                        className={`cursor-pointer border-2 rounded-xl p-2 transition-all ${
                          isSelected
                            ? 'border-primary-600 bg-primary-50 shadow-lg'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="relative aspect-square mb-2 overflow-hidden rounded-lg">
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                          {isSelected && (
                            <div className="absolute inset-0 bg-primary-600/20 flex items-center justify-center">
                              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                                ✓
                              </div>
                            </div>
                          )}
                        </div>
                        <h4 className="font-semibold text-sm line-clamp-2 mb-1">
                          {product.name}
                        </h4>
                        <p className="text-primary-600 font-bold">
                          ${product.price.toFixed(2)}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}

              {selectedProducts.length > 0 && (
                <div className="mt-4 p-4 bg-primary-50 rounded-lg">
                  <p className="text-sm font-semibold text-primary-700">
                    {selectedProducts.length} product{selectedProducts.length !== 1 ? 's' : ''} selected
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <h3 className="text-xl font-bold mb-6">Review Your CAMEO Request</h3>

            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 mb-1">Occasion</div>
                <div className="font-semibold">{occasion}</div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 mb-1">Recipient</div>
                <div className="font-semibold">{recipientName}</div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 mb-1">Message</div>
                <div className="text-gray-700">{personalMessage}</div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 mb-1">Tone</div>
                <div className="font-semibold capitalize">{tone}</div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 mb-3">
                  Selected Products ({selectedProducts.length})
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {products
                    .filter((p) => selectedProducts.includes(p.id))
                    .map((product) => (
                      <div key={product.id} className="aspect-square rounded-lg overflow-hidden">
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-4 mt-8 pt-6 border-t border-gray-200">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              disabled={isLoading}
              className="btn-secondary flex-1"
            >
              Back
            </button>
          )}

          {step < 4 ? (
            <button
              onClick={() => setStep(step + 1)}
              disabled={!canProceedToNextStep()}
              className="btn-primary flex-1"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Generate CAMEO</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
