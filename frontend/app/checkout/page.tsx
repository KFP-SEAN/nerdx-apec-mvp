'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ShoppingCart,
  CreditCard,
  CheckCircle,
  Loader2,
  Lock,
  ArrowLeft,
  Package,
  Truck,
} from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''
);

interface CartItem {
  id: string;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url: string;
}

interface CheckoutSession {
  session_id: string;
  status: 'pending' | 'completed' | 'failed';
  total_amount: number;
  items: CartItem[];
}

export default function CheckoutPage() {
  const searchParams = useSearchParams();
  const [checkoutSession, setCheckoutSession] = useState<CheckoutSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [orderComplete, setOrderComplete] = useState(false);

  // Form state
  const [email, setEmail] = useState('');
  const [shippingInfo, setShippingInfo] = useState({
    fullName: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'US',
  });

  useEffect(() => {
    loadCheckoutSession();
    checkPaymentStatus();
  }, []);

  const loadCheckoutSession = async () => {
    try {
      setLoading(true);
      const sessionId = searchParams.get('session_id');

      if (sessionId) {
        const response = await api.get(`/checkout/session/${sessionId}`);
        setCheckoutSession(response.data);
      } else {
        // Load from cart
        const response = await api.get('/cart');
        setCheckoutSession({
          session_id: '',
          status: 'pending',
          total_amount: response.data.total,
          items: response.data.items,
        });
      }
    } catch (error) {
      console.error('Failed to load checkout session:', error);
      toast.error('Failed to load checkout information');
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = () => {
    const success = searchParams.get('success');
    if (success === 'true') {
      setOrderComplete(true);
      toast.success('Payment successful!');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !shippingInfo.fullName || !shippingInfo.address) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setProcessing(true);

      // Create Stripe checkout session
      const response = await api.post('/checkout/create-session', {
        email,
        shipping_info: shippingInfo,
        items: checkoutSession?.items,
        success_url: `${window.location.origin}/checkout?success=true`,
        cancel_url: `${window.location.origin}/checkout?success=false`,
      });

      const stripe = await stripePromise;
      if (!stripe) {
        throw new Error('Stripe failed to load');
      }

      // Redirect to Stripe Checkout
      const { error } = await stripe.redirectToCheckout({
        sessionId: response.data.session_id,
      });

      if (error) {
        throw error;
      }
    } catch (error) {
      console.error('Checkout failed:', error);
      toast.error('Failed to process checkout. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (orderComplete) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="card max-w-2xl w-full text-center"
        >
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold mb-4">Order Confirmed!</h1>
          <p className="text-xl text-gray-600 mb-8">
            Thank you for your purchase. We've sent a confirmation email with your order details.
          </p>

          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <div className="bg-gray-50 rounded-lg p-6">
              <Package className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Order Processing</h3>
              <p className="text-sm text-gray-600">
                Your order is being prepared for shipment
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-6">
              <Truck className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Estimated Delivery</h3>
              <p className="text-sm text-gray-600">3-5 business days</p>
            </div>
          </div>

          <div className="flex gap-4 justify-center">
            <a href="/products">
              <button className="btn-primary">Continue Shopping</button>
            </a>
            <a href="/orders">
              <button className="btn-outline">View Orders</button>
            </a>
          </div>
        </motion.div>
      </div>
    );
  }

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
          <a href="/products" className="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-4">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Products</span>
          </a>
          <h1 className="text-4xl font-bold mb-2">Checkout</h1>
          <p className="text-gray-600">Complete your purchase securely</p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Checkout Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-2"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Contact Information */}
              <div className="card">
                <h2 className="text-2xl font-bold mb-6">Contact Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      className="input-field"
                    />
                  </div>
                </div>
              </div>

              {/* Shipping Information */}
              <div className="card">
                <h2 className="text-2xl font-bold mb-6">Shipping Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      value={shippingInfo.fullName}
                      onChange={(e) =>
                        setShippingInfo({ ...shippingInfo, fullName: e.target.value })
                      }
                      placeholder="John Doe"
                      required
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2">
                      Address *
                    </label>
                    <input
                      type="text"
                      value={shippingInfo.address}
                      onChange={(e) =>
                        setShippingInfo({ ...shippingInfo, address: e.target.value })
                      }
                      placeholder="123 Main St"
                      required
                      className="input-field"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold mb-2">
                        City *
                      </label>
                      <input
                        type="text"
                        value={shippingInfo.city}
                        onChange={(e) =>
                          setShippingInfo({ ...shippingInfo, city: e.target.value })
                        }
                        placeholder="New York"
                        required
                        className="input-field"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold mb-2">
                        State *
                      </label>
                      <input
                        type="text"
                        value={shippingInfo.state}
                        onChange={(e) =>
                          setShippingInfo({ ...shippingInfo, state: e.target.value })
                        }
                        placeholder="NY"
                        required
                        className="input-field"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold mb-2">
                        ZIP Code *
                      </label>
                      <input
                        type="text"
                        value={shippingInfo.zipCode}
                        onChange={(e) =>
                          setShippingInfo({ ...shippingInfo, zipCode: e.target.value })
                        }
                        placeholder="10001"
                        required
                        className="input-field"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold mb-2">
                        Country *
                      </label>
                      <select
                        value={shippingInfo.country}
                        onChange={(e) =>
                          setShippingInfo({ ...shippingInfo, country: e.target.value })
                        }
                        required
                        className="input-field"
                      >
                        <option value="US">United States</option>
                        <option value="CA">Canada</option>
                        <option value="UK">United Kingdom</option>
                        <option value="KR">South Korea</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Payment Button */}
              <button
                type="submit"
                disabled={processing}
                className="btn-primary w-full flex items-center justify-center gap-3 py-4 text-lg"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-6 h-6" />
                    <span>Proceed to Payment</span>
                  </>
                )}
              </button>

              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <Lock className="w-4 h-4" />
                <span>Secure checkout powered by Stripe</span>
              </div>
            </form>
          </motion.div>

          {/* Order Summary */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="card sticky top-24">
              <h2 className="text-2xl font-bold mb-6">Order Summary</h2>

              {/* Items */}
              <div className="space-y-4 mb-6">
                {checkoutSession?.items.map((item) => (
                  <div key={item.id} className="flex gap-4">
                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold line-clamp-2">{item.name}</h3>
                      <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                      <p className="font-semibold text-primary-600">
                        ${item.price.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="border-t border-gray-200 pt-4 space-y-3">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>${checkoutSession?.total_amount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span>Free</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="border-t border-gray-200 pt-3 flex justify-between text-xl font-bold">
                  <span>Total</span>
                  <span className="text-primary-600">
                    ${checkoutSession?.total_amount.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Trust Badges */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-center text-sm">
                  <div>
                    <Lock className="w-6 h-6 text-green-600 mx-auto mb-2" />
                    <p className="font-semibold">Secure Payment</p>
                  </div>
                  <div>
                    <Truck className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <p className="font-semibold">Fast Shipping</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
