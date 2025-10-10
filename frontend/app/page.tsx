'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  PlayCircle,
  MessageSquare,
  Video,
  ShoppingCart,
  Sparkles,
  ArrowRight,
  Eye,
  Heart,
  Share2,
} from 'lucide-react';
import VideoPlayer from '@/components/VideoPlayer';
import ProductCarousel from '@/components/ProductCarousel';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface VideoData {
  id: string;
  title: string;
  description: string;
  video_url: string;
  thumbnail_url: string;
  views: number;
  likes: number;
  products: Array<{
    id: string;
    name: string;
    price: number;
    image_url: string;
  }>;
}

export default function HomePage() {
  const [featuredVideo, setFeaturedVideo] = useState<VideoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    loadFeaturedVideo();
  }, []);

  const loadFeaturedVideo = async () => {
    try {
      setLoading(true);
      const response = await api.get('/videos/featured');
      setFeaturedVideo(response.data);
    } catch (error) {
      console.error('Failed to load featured video:', error);
      toast.error('Failed to load featured video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen gradient-bg">
      {/* Hero Section with Sam Altman Video */}
      <section className="section-container pt-20 pb-12">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Hero Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-semibold">
              <Sparkles className="w-4 h-4" />
              <span>AI-Powered Video Commerce</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
              Discover Products
              <span className="text-gradient block mt-2">
                Through Video
              </span>
            </h1>

            <p className="text-xl text-gray-600 leading-relaxed">
              Watch Sam Altman showcase amazing products. Chat with Maeju AI to find what you love.
              Get personalized CAMEO videos from your favorite creators.
            </p>

            <div className="flex flex-wrap gap-4">
              <Link href="/products">
                <button className="btn-primary flex items-center gap-2 group">
                  <ShoppingCart className="w-5 h-5" />
                  <span>Browse Products</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>

              <Link href="/chat">
                <button className="btn-outline flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  <span>Chat with Maeju AI</span>
                </button>
              </Link>
            </div>

            {/* Stats */}
            <div className="flex gap-8 pt-6">
              <div>
                <div className="text-3xl font-bold text-primary-600">10K+</div>
                <div className="text-sm text-gray-600">Products</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary-600">50K+</div>
                <div className="text-sm text-gray-600">Happy Customers</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary-600">1M+</div>
                <div className="text-sm text-gray-600">Videos Watched</div>
              </div>
            </div>
          </motion.div>

          {/* Featured Video Player */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            {loading ? (
              <div className="video-container bg-gray-200 skeleton" />
            ) : featuredVideo ? (
              <div className="space-y-4">
                <VideoPlayer
                  videoUrl={featuredVideo.video_url}
                  thumbnailUrl={featuredVideo.thumbnail_url}
                  title={featuredVideo.title}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />

                {/* Video Info */}
                <div className="card">
                  <h3 className="text-xl font-bold mb-2">{featuredVideo.title}</h3>
                  <p className="text-gray-600 mb-4">{featuredVideo.description}</p>

                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <Eye className="w-4 h-4" />
                      <span>{featuredVideo.views.toLocaleString()} views</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Heart className="w-4 h-4" />
                      <span>{featuredVideo.likes.toLocaleString()} likes</span>
                    </div>
                    <button className="flex items-center gap-2 hover:text-primary-600 transition-colors">
                      <Share2 className="w-4 h-4" />
                      <span>Share</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="video-container bg-gray-100 flex items-center justify-center">
                <PlayCircle className="w-20 h-20 text-gray-400" />
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Featured Products */}
      {featuredVideo && featuredVideo.products.length > 0 && (
        <section className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">Featured in This Video</h2>
                <p className="text-gray-600">Products Sam Altman recommends</p>
              </div>
              <Link href="/products">
                <button className="btn-secondary flex items-center gap-2">
                  <span>View All</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>

            <ProductCarousel products={featuredVideo.products} />
          </motion.div>
        </section>
      )}

      {/* Features Section */}
      <section className="section-container py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold mb-4">
            Why Choose <span className="text-gradient">NERDX APEC</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience the future of online shopping with AI-powered video commerce
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: PlayCircle,
              title: 'Video Discovery',
              description: 'Watch engaging product videos featuring Sam Altman and discover items in context',
              link: '/products',
              linkText: 'Browse Videos',
            },
            {
              icon: MessageSquare,
              title: 'AI Shopping Assistant',
              description: 'Chat with Maeju AI to get personalized recommendations and instant answers',
              link: '/chat',
              linkText: 'Start Chatting',
            },
            {
              icon: Video,
              title: 'Custom CAMEO Videos',
              description: 'Get personalized video messages from creators showcasing your favorite products',
              link: '/cameo',
              linkText: 'Create CAMEO',
            },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="card hover:shadow-xl transition-shadow duration-300 group"
            >
              <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary-600 transition-colors duration-300">
                <feature.icon className="w-7 h-7 text-primary-600 group-hover:text-white transition-colors duration-300" />
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-gray-600 mb-4">{feature.description}</p>
              <Link href={feature.link}>
                <button className="text-primary-600 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                  <span>{feature.linkText}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-container py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="card bg-gradient-to-r from-primary-600 to-secondary-600 text-white text-center p-12"
        >
          <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Shopping?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of happy customers discovering products through video
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/products">
              <button className="bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 flex items-center gap-2">
                <ShoppingCart className="w-5 h-5" />
                <span>Start Shopping</span>
              </button>
            </Link>
            <Link href="/cameo">
              <button className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white/10 transition-colors duration-200 flex items-center gap-2">
                <Video className="w-5 h-5" />
                <span>Create CAMEO</span>
              </button>
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
