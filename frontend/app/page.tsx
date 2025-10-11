'use client';

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
  Share2,
} from 'lucide-react';

export default function HomePage() {
  // Using hardcoded Google Drive video
  const GOOGLE_DRIVE_VIDEO_ID = '19lUs8oMOtY8Ah3vUp37X7R7J0jcb811k';
  const videoEmbedUrl = `https://drive.google.com/file/d/${GOOGLE_DRIVE_VIDEO_ID}/preview`;

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
            <div className="space-y-4">
              {/* Google Drive Video Embed */}
              <div className="video-container relative overflow-hidden rounded-2xl shadow-xl">
                <iframe
                  src={videoEmbedUrl}
                  className="w-full h-full absolute inset-0"
                  allow="autoplay"
                  allowFullScreen
                  title="Featured Video"
                />
              </div>

              {/* Video Info */}
              <div className="card">
                <h3 className="text-xl font-bold mb-2">Sam Altman's Product Showcase</h3>
                <p className="text-gray-600 mb-4">
                  Watch as Sam Altman introduces the latest innovative products.
                  Discover cutting-edge technology and shop directly from the video.
                </p>

                <div className="flex items-center gap-6 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    <span>Featured Video</span>
                  </div>
                  <button className="flex items-center gap-2 hover:text-primary-600 transition-colors">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

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
