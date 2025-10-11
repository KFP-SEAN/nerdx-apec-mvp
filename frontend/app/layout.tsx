import type { Metadata } from 'next';
import { Inter, Noto_Sans_KR } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import NewsletterPopup from '@/components/NewsletterPopup';
import { CartProvider } from '@/context/CartContext';
import ClientInitializer from '@/components/ClientInitializer';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoSansKR = Noto_Sans_KR({
  subsets: ['latin'],
  variable: '--font-noto-sans-kr',
  display: 'swap',
  weight: ['300', '400', '500', '700'],
});

export const metadata: Metadata = {
  title: 'NERDX APEC - Sam Altman Video Commerce Platform',
  description: 'Discover products through AI-powered video experiences. Watch Sam Altman showcase amazing products and shop with Maeju AI assistance.',
  keywords: 'video commerce, AI shopping, Sam Altman, CAMEO, personalized videos, e-commerce',
  authors: [{ name: 'NERDX' }],
  openGraph: {
    title: 'NERDX APEC - Video Commerce Platform',
    description: 'Revolutionary video commerce powered by AI',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NERDX APEC - Video Commerce Platform',
    description: 'Revolutionary video commerce powered by AI',
  },
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
  themeColor: '#0ea5e9',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${notoSansKR.variable}`}>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <CartProvider>
          <ClientInitializer />
          <div className="flex flex-col min-h-screen">
            <Navigation />
            <main className="flex-grow">
              {children}
            </main>
            <Footer />
          </div>
          <NewsletterPopup />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </CartProvider>
      </body>
    </html>
  );
}
