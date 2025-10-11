'use client';

import Link from 'next/link';
import {
  Video,
  Mail,
  Globe,
  Github,
  Twitter,
  Linkedin,
  Facebook,
  Instagram,
  Youtube,
  CreditCard,
  Truck,
  RotateCcw,
  FileText,
  Shield,
  HelpCircle
} from 'lucide-react';
import NewsletterSignup from './NewsletterSignup';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    quickLinks: [
      { name: 'Products', href: '/products' },
      { name: 'About', href: '/about' },
      { name: 'Contact', href: '/contact' },
      { name: 'FAQ', href: '/faq' },
    ],
    customerService: [
      { name: 'Shipping', href: '/shipping', icon: Truck },
      { name: 'Returns', href: '/returns', icon: RotateCcw },
      { name: 'Terms of Service', href: '/terms', icon: FileText },
      { name: 'Privacy Policy', href: '/privacy', icon: Shield },
    ],
    company: [
      { name: 'About Us', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Careers', href: '/careers' },
      { name: 'Press', href: '/press' },
    ],
  };

  return (
    <footer className="bg-gray-900 text-gray-300">
      {/* Newsletter Section */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-white mb-2">Stay Connected</h3>
              <p className="text-gray-400">
                Subscribe to get special offers, free giveaways, and exclusive deals.
              </p>
            </div>
            <NewsletterSignup source="footer" variant="compact" />
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4 group">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform">
                <Video className="w-7 h-7 text-white" />
              </div>
              <div>
                <div className="text-xl font-bold text-white">NERDX APEC</div>
                <div className="text-xs text-gray-400">Video Commerce Platform</div>
              </div>
            </Link>
            <p className="text-sm mb-6 max-w-md">
              Revolutionizing online shopping with AI-powered video commerce. Discover products
              through engaging video content and personalized experiences.
            </p>

            {/* Social Links */}
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-white mb-3">Follow Us</h4>
              <div className="flex gap-3">
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a
                  href="https://facebook.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors"
                  aria-label="Facebook"
                >
                  <Facebook className="w-5 h-5" />
                </a>
                <a
                  href="https://instagram.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram className="w-5 h-5" />
                </a>
                <a
                  href="https://youtube.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors"
                  aria-label="YouTube"
                >
                  <Youtube className="w-5 h-5" />
                </a>
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Payment Methods */}
            <div>
              <h4 className="text-sm font-semibold text-white mb-3">We Accept</h4>
              <div className="flex items-center gap-2">
                <div className="px-3 py-2 bg-gray-800 rounded-md">
                  <span className="text-xs font-medium">VISA</span>
                </div>
                <div className="px-3 py-2 bg-gray-800 rounded-md">
                  <span className="text-xs font-medium">MC</span>
                </div>
                <div className="px-3 py-2 bg-gray-800 rounded-md">
                  <span className="text-xs font-medium">AMEX</span>
                </div>
                <div className="px-3 py-2 bg-gray-800 rounded-md">
                  <span className="text-xs font-medium">PayPal</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Quick Links</h3>
            <ul className="space-y-3">
              {footerLinks.quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm hover:text-primary-400 transition-colors inline-flex items-center gap-1"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h3 className="font-semibold text-white mb-4">Customer Service</h3>
            <ul className="space-y-3">
              {footerLinks.customerService.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm hover:text-primary-400 transition-colors inline-flex items-center gap-2"
                  >
                    <link.icon className="w-4 h-4" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-white mb-4">Company</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm hover:text-primary-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-col md:flex-row items-center gap-4">
              <p className="text-sm text-gray-400">
                &copy; {currentYear} NERDX APEC. All rights reserved.
              </p>
              <div className="hidden md:block w-px h-4 bg-gray-700"></div>
              <p className="text-sm text-gray-500">
                Powered by AI Video Commerce Technology
              </p>
            </div>

            <div className="flex items-center gap-6 text-sm">
              <a
                href="mailto:support@nerdx-apec.com"
                className="flex items-center gap-2 hover:text-primary-400 transition-colors"
              >
                <Mail className="w-4 h-4" />
                <span className="hidden sm:inline">support@nerdx-apec.com</span>
              </a>
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                <select className="bg-transparent border-none text-sm focus:ring-0 cursor-pointer hover:text-primary-400 transition-colors">
                  <option value="en">English</option>
                  <option value="ko">한국어</option>
                  <option value="ja">日本語</option>
                </select>
              </div>
            </div>
          </div>

          {/* Trust Badges */}
          <div className="mt-6 pt-6 border-t border-gray-800">
            <div className="flex flex-wrap justify-center items-center gap-6 text-xs text-gray-500">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                <span>Secure Shopping</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-gray-700"></div>
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4" />
                <span>Free Shipping Over $50</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-gray-700"></div>
              <div className="flex items-center gap-2">
                <RotateCcw className="w-4 h-4" />
                <span>30-Day Returns</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-gray-700"></div>
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4" />
                <span>24/7 Support</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
