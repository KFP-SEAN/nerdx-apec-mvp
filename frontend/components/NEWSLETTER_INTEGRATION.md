# Newsletter Components Integration Guide

## Overview
Newsletter components for NERDX APEC MVP based on SHOPIFY_PRD.md Section 4.1.

## Created Files

### 1. Components
- **C:\Users\seans\nerdx-apec-mvp\frontend\components\NewsletterSignup.tsx** - Main newsletter signup component
- **C:\Users\seans\nerdx-apec-mvp\frontend\components\NewsletterPopup.tsx** - Modal popup component

### 2. API Route
- **C:\Users\seans\nerdx-apec-mvp\frontend\app\api\newsletter\subscribe\route.ts** - Newsletter subscription endpoint

## Component Usage

### NewsletterSignup Component

#### Default Variant (Full Featured)
```tsx
import NewsletterSignup from '@/components/NewsletterSignup';

// In Footer or dedicated section
<NewsletterSignup source="footer" variant="default" />
```

#### Compact Variant (Simple)
```tsx
import NewsletterSignup from '@/components/NewsletterSignup';

// In checkout page
<NewsletterSignup
  source="checkout"
  variant="compact"
  onSuccess={() => console.log('User subscribed!')}
/>
```

### NewsletterPopup Component

Add to your root layout to show site-wide:

```tsx
// app/layout.tsx
import NewsletterPopup from '@/components/NewsletterPopup';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <NewsletterPopup />
      </body>
    </html>
  );
}
```

## Integration Examples

### 1. Footer Integration

Update `components/Footer.tsx` to include newsletter signup:

```tsx
import NewsletterSignup from './NewsletterSignup';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      {/* Newsletter Section - Add before bottom bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NewsletterSignup source="footer" variant="default" />
      </div>

      {/* Existing footer content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* ... existing footer links ... */}
      </div>
    </footer>
  );
}
```

### 2. Checkout Page Integration

```tsx
// app/checkout/page.tsx
import NewsletterSignup from '@/components/NewsletterSignup';

export default function CheckoutPage() {
  return (
    <div>
      {/* After order summary */}
      <div className="mt-8 border-t pt-8">
        <h3 className="text-lg font-semibold mb-4">💡 한 가지 더!</h3>
        <p className="text-gray-600 mb-4">
          뉴스레터를 구독하시고 다음 주문 시 10% 할인 받으세요
        </p>
        <NewsletterSignup
          source="checkout"
          variant="compact"
        />
      </div>
    </div>
  );
}
```

### 3. Homepage Integration

```tsx
// app/page.tsx
import NewsletterSignup from '@/components/NewsletterSignup';
import NewsletterPopup from '@/components/NewsletterPopup';

export default function HomePage() {
  return (
    <main>
      {/* ... homepage content ... */}

      {/* Newsletter Section */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4">
          <NewsletterSignup source="footer" variant="default" />
        </div>
      </section>

      {/* Newsletter Popup (shows after 30s or exit intent) */}
      <NewsletterPopup />
    </main>
  );
}
```

## Features

### NewsletterSignup Component

**Props:**
- `source` (required): 'footer' | 'popup' | 'checkout' - Tracks where the signup originated
- `variant` (optional): 'default' | 'compact' - Display style (default: 'default')
- `onSuccess` (optional): Callback function when subscription succeeds

**Variants:**

1. **Default Variant** - Full featured with:
   - Benefits display (4 benefit cards)
   - Email input field
   - Submit button
   - Success state with coupon display
   - Coupon modal popup
   - Social proof (subscriber count)

2. **Compact Variant** - Minimal:
   - Email input field
   - Submit button only

**Features:**
- Email validation
- Loading state during submission
- Success state showing coupon code
- Coupon modal popup on success
- Toast notifications for feedback
- Responsive design

### NewsletterPopup Component

**Features:**
- Appears after 30 seconds OR on exit intent (mouse leaving top of page)
- Shows newsletter benefits
- Uses compact NewsletterSignup variant
- "Maybe later" close button
- localStorage tracking to prevent reshowing for 30 days
- Responsive modal design
- Smooth animations

**Behavior:**
- Won't show if user already subscribed (checks localStorage)
- Won't show if dismissed within last 30 days
- Auto-closes 3 seconds after successful subscription
- Click outside to close

## API Endpoint

### POST /api/newsletter/subscribe

**Request:**
```json
{
  "email": "user@example.com",
  "firstName": "지현",  // optional
  "source": "footer"    // optional: 'footer' | 'popup' | 'checkout'
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "구독이 완료되었습니다!",
  "couponCode": "WELCOME15-ABC12345"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "올바른 이메일 주소를 입력해주세요"
}
```

## Backend Integration

The newsletter components use the `subscribeToNewsletter()` function from `lib/shopify/newsletter.ts`, which:

1. Creates/updates Shopify customer with `acceptsMarketing: true`
2. Generates unique 15% discount code (WELCOME15-XXXXXXXX)
3. Triggers welcome email (configured in Shopify)
4. Tracks analytics event

## Styling Requirements

Make sure your `globals.css` includes these utility classes:

```css
.btn-primary {
  @apply bg-primary-600 text-white px-6 py-2 rounded-lg font-semibold
         hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed
         transition-colors;
}

.primary-50 {
  /* Light primary color for backgrounds */
}

.primary-600 {
  /* Primary brand color */
}

.secondary-50 {
  /* Light secondary color for gradients */
}
```

## Testing Checklist

- [ ] Newsletter signup works from footer
- [ ] Newsletter signup works from popup
- [ ] Newsletter signup works from checkout
- [ ] Email validation shows errors
- [ ] Success message displays with coupon code
- [ ] Coupon modal pops up after subscription
- [ ] Popup shows after 30 seconds
- [ ] Popup shows on exit intent
- [ ] Popup doesn't reshow after dismissal
- [ ] Toast notifications appear correctly
- [ ] Loading states work properly
- [ ] Mobile responsive design
- [ ] API endpoint returns correct responses

## Customization

### Change Popup Timing
Edit `NewsletterPopup.tsx`:
```tsx
const timer = setTimeout(() => {
  // ...
}, 30000); // Change 30000ms (30s) to desired time
```

### Change Popup Dismiss Duration
Edit `lib/shopify/newsletter.ts`:
```tsx
// In shouldShowNewsletterPopup()
return Date.now() - timestamp >= 30 * 24 * 60 * 60 * 1000; // 30 days
```

### Customize Benefits
Edit `NewsletterSignup.tsx`:
```tsx
<div className="grid grid-cols-2 gap-4 mb-6">
  <div className="bg-white rounded-lg p-4">
    <div className="text-2xl mb-1">✨</div>
    <div className="text-sm font-semibold">Your custom benefit</div>
  </div>
  {/* Add more benefits */}
</div>
```

## Next Steps

1. Add NewsletterSignup to Footer component
2. Add NewsletterPopup to root layout
3. Test newsletter flow end-to-end
4. Configure Shopify email templates
5. Set up analytics tracking
6. Monitor conversion rates

## Support

For questions or issues, refer to:
- SHOPIFY_PRD.md Section 4.1 for requirements
- lib/shopify/newsletter.ts for backend functions
- Shopify Admin for email template configuration
