# ⚡ Quick Start Guide - NERDX APEC MVP

> **Get up and running in 15 minutes**

This guide will help you quickly set up the NERDX APEC MVP Shopify Headless Commerce platform on your local machine.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Node.js 18+** installed ([Download](https://nodejs.org/))
- [ ] **npm 8+** (comes with Node.js)
- [ ] **Git** ([Download](https://git-scm.com/))
- [ ] **Shopify Partner Account** ([Sign up](https://partners.shopify.com/signup))
- [ ] **Code editor** (VS Code recommended)

**Time Required:** 15 minutes

---

## 🚀 Step 1: Clone Repository (1 minute)

```bash
# Clone the repository
git clone https://github.com/nerdx/nerdx-apec-mvp.git

# Navigate to project directory
cd nerdx-apec-mvp

# Navigate to frontend
cd frontend
```

---

## 📦 Step 2: Install Dependencies (2 minutes)

```bash
# Install all npm packages
npm install

# This will install:
# - Next.js 14
# - React 18
# - Tailwind CSS
# - Shopify SDKs
# - Testing libraries
# - And more...
```

**Expected output:**
```
added 500+ packages in 45s
```

---

## 🔐 Step 3: Set Up Shopify Store (5 minutes)

### 3.1 Create Development Store

1. Go to [Shopify Partners](https://partners.shopify.com/)
2. Click **Stores** → **Add store** → **Development store**
3. Fill in store details:
   - **Store name:** nerdx-test (or your choice)
   - **Store URL:** nerdx-test.myshopify.com
   - **Purpose:** Test an app or theme
4. Click **Save**

### 3.2 Create Storefront API Token

1. In your Development Store, go to **Settings** → **Apps and sales channels**
2. Click **Develop apps**
3. Click **Create an app**
4. Name it "NERDX Frontend"
5. Go to **Configuration** tab
6. Under **Storefront API**, click **Configure**
7. Enable these permissions:
   - ✅ Read products, variants, and collections
   - ✅ Read product listings
   - ✅ Read customer tags
   - ✅ Manage checkouts
8. Click **Save**
9. Go to **API credentials** tab
10. Click **Install app**
11. Copy the **Storefront API access token** (starts with `shpat_`)

---

## ⚙️ Step 4: Configure Environment Variables (2 minutes)

```bash
# In the frontend directory, copy the example env file
cp .env.local.example .env.local

# Open .env.local in your code editor
```

Update `.env.local` with your Shopify credentials:

```env
# Shopify Storefront API
NEXT_PUBLIC_SHOPIFY_DOMAIN=nerdx-test.myshopify.com
NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=shpat_xxxxx

# Custom Shopify App (use localhost for now)
NEXT_PUBLIC_SHOPIFY_APP_URL=http://localhost:3001
```

**Important:** Replace `nerdx-test.myshopify.com` and `shpat_xxxxx` with your actual values!

---

## 📝 Step 5: Add Test Product (3 minutes)

### 5.1 Create a Product

1. In Shopify Admin, go to **Products** → **Add product**
2. Fill in:
   - **Title:** NERD Brewery Experience Pack
   - **Description:** Premium Korean craft beer tasting experience
   - **Price:** $99.00
   - **Compare at price:** $149.00 (optional)
   - **SKU:** NERD-001
3. Upload a product image (use any placeholder image)
4. Click **Save**

### 5.2 Add Metafields

1. Scroll down to **Metafields** section
2. Click **Add definition** if no metafields exist
3. Add these three metafields:

**Metafield 1: AR Enabled**
- **Namespace:** `custom`
- **Key:** `ar_enabled`
- **Type:** Boolean
- **Value:** ✅ (checked)

**Metafield 2: APEC Limited**
- **Namespace:** `custom`
- **Key:** `apec_limited`
- **Type:** Boolean
- **Value:** ✅ (checked)

**Metafield 3: Stock Remaining**
- **Namespace:** `custom`
- **Key:** `stock_remaining`
- **Type:** Number (Integer)
- **Value:** 50

4. Click **Save**

---

## 🎯 Step 6: Run Development Server (1 minute)

```bash
# Make sure you're in the frontend directory
cd frontend

# Start the Next.js dev server
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.2.20
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.5s
```

---

## 🎉 Step 7: Test Your Setup (1 minute)

Open your browser and navigate to:

1. **Homepage:** http://localhost:3000
   - Should see NERDX branding and hero section

2. **Product Listing:** http://localhost:3000/products/shopify
   - Should see your "NERD Brewery Experience Pack" product
   - Should see AR-enabled badge
   - Should see APEC Limited Edition badge

3. **Product Detail:** Click on the product
   - Should see full product details
   - Should see "Buy Now" and "Add to Cart" buttons
   - Should see stock remaining: "50 남음"

4. **Add to Cart:** Click "Add to Cart"
   - Should see success message
   - Navigate to http://localhost:3000/cart
   - Should see your product in cart

---

## ✅ Success Checklist

Verify everything is working:

- [ ] Development server running at http://localhost:3000
- [ ] Homepage loads without errors
- [ ] Product listing shows your test product
- [ ] Product detail page displays correctly
- [ ] "Add to Cart" functionality works
- [ ] Shopping cart displays items
- [ ] No console errors in browser DevTools

---

## 🧪 Next Steps

### Run Tests

```bash
# Run unit and integration tests
npm test

# Run with coverage
npm run test:coverage

# Expected output: 24/24 tests passing
```

### Explore Features

1. **Product Browsing**
   - Try the search functionality
   - Test filters (AR-enabled, APEC limited)
   - Try sorting options

2. **Shopping Cart**
   - Update quantities
   - Remove items
   - Test checkout button (redirects to Shopify)

3. **Responsive Design**
   - Open DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Test on mobile view

### Add More Products

Create 2-3 more test products to see the full experience:

**Product Ideas:**
- NERD Signature Makgeolli Set
- NERD Premium Soju Collection
- NERD AR Experience Bundle

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch products"

**Cause:** Invalid Shopify credentials or network issue

**Solution:**
1. Check `.env.local` has correct values
2. Verify Storefront API token is active
3. Ensure Development Store is not paused
4. Restart dev server: `npm run dev`

### Issue: "Product not showing on listing page"

**Cause:** Product not published to Online Store channel

**Solution:**
1. In Shopify Admin, edit the product
2. Scroll to **Product availability**
3. Ensure **Online Store** is checked
4. Click **Save**
5. Refresh browser

### Issue: "Cannot add to cart"

**Cause:** Product has no variants or inventory

**Solution:**
1. Check product has at least 1 variant
2. Ensure variant has inventory > 0
3. Check variant is available

### Issue: "Port 3000 already in use"

**Solution:**
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use a different port
npm run dev -- -p 3001
```

### Issue: Environment variables not loading

**Solution:**
1. Ensure `.env.local` is in `frontend/` directory (not root)
2. Variable names must start with `NEXT_PUBLIC_` for client-side access
3. Restart dev server after changing `.env.local`

---

## 📚 Additional Resources

### Documentation

- [Full README](README.md) - Complete project documentation
- [Testing Guide](TESTING_REPORT.md) - Comprehensive testing documentation
- [Shopify Store Setup](SHOPIFY_STORE_SETUP_GUIDE.md) - Detailed Shopify configuration
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions

### External Links

- [Next.js Docs](https://nextjs.org/docs)
- [Shopify Storefront API](https://shopify.dev/docs/api/storefront)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Getting Help

- **GitHub Issues:** [Report bugs](https://github.com/nerdx/nerdx-apec-mvp/issues)
- **Email:** apec-support@nerdx.com
- **Slack:** #nerdx-apec-mvp

---

## 🚀 Ready for More?

Now that you have the basics running, explore these advanced features:

### 1. Custom Shopify App (Optional)

Set up the Custom Shopify App for webhook processing and AR access:

```bash
cd ../shopify-custom-app
npm install
# See DEPLOYMENT_GUIDE.md for full setup
```

### 2. E2E Testing

Install Playwright and run end-to-end tests:

```bash
cd frontend
npm run playwright:install
npm run test:e2e
```

### 3. Production Build

Test the production build locally:

```bash
npm run build
npm start

# Visit http://localhost:3000
```

### 4. Deploy to Vercel

Deploy your frontend to production:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

---

## 📊 Development Commands

Quick reference for common commands:

```bash
# Development
npm run dev                 # Start dev server
npm run build              # Create production build
npm start                  # Run production build

# Testing
npm test                   # Run unit/integration tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Generate coverage report
npm run test:e2e           # Run E2E tests
npm run test:e2e:ui        # Run E2E tests in UI mode

# Code Quality
npm run lint               # Run ESLint
npm run type-check         # Run TypeScript type checking
npm run format             # Format code with Prettier

# Playwright
npm run playwright:install # Install browsers
npx playwright codegen     # Generate test code
npx playwright show-report # View test report
```

---

## 🎯 What's Next?

1. ✅ **You are here:** Local development setup complete
2. ⏭️ **Add more products:** Create a full product catalog
3. ⏭️ **Customize styling:** Modify Tailwind CSS to match brand
4. ⏭️ **Run all tests:** Verify everything works
5. ⏭️ **Deploy to staging:** Test on Vercel preview
6. ⏭️ **Production launch:** Deploy to production with custom domain

---

## 🏁 Congratulations!

You've successfully set up the NERDX APEC MVP on your local machine! 🎉

**Time taken:** ~15 minutes
**Status:** ✅ Ready for development

---

*Last Updated: 2025-10-11*
*Version: 1.0.0*
