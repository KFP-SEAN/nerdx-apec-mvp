# NERDX APEC Frontend

A modern Next.js 14 frontend for the NERDX APEC MVP - an AI-powered video commerce platform featuring Sam Altman video showcases, Maeju AI shopping assistant, and personalized CAMEO video generation.

## Features

### Phase 1: Video Commerce Platform
- **Sam Altman Video Showcase**: Watch engaging product videos featuring Sam Altman
- **Product Discovery**: Browse products directly from video content
- **Responsive Video Player**: Custom video player with controls and tracking
- **Product Catalog**: Advanced filtering, search, and sorting capabilities

### Phase 2: Maeju AI Chat
- **AI Shopping Assistant**: Chat with Maeju for personalized recommendations
- **Contextual Responses**: AI understands your preferences and history
- **Product Recommendations**: Get product suggestions based on conversations
- **Video Discovery**: Find relevant videos through chat

### Phase 3: CAMEO Generation
- **Personalized Videos**: Generate custom CAMEO videos with Sam Altman
- **Multi-Step Creator**: Intuitive wizard for creating CAMEOs
- **Product Integration**: Feature selected products in your CAMEOs
- **Customizable Tones**: Choose from professional, friendly, enthusiastic, or heartfelt

### Additional Features
- **Stripe Checkout**: Secure payment processing
- **AR Experience**: View products in AR (integrated)
- **Responsive Design**: Mobile-first, works on all devices
- **Korean/English Support**: i18n ready with font optimization
- **Beautiful UI**: TailwindCSS with custom animations

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS + Custom CSS
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **State Management**: Zustand
- **Icons**: Lucide React
- **Payments**: Stripe
- **Fonts**: Inter + Noto Sans KR

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+
- Backend API running (see backend README)

### Installation

1. **Clone the repository**
```bash
cd /c/Users/seans/nerdx-apec-mvp/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

4. **Run development server**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout with fonts
│   ├── page.tsx             # Landing page
│   ├── products/            # Product catalog
│   ├── chat/                # Maeju AI chat
│   ├── cameo/               # CAMEO creator
│   └── checkout/            # Checkout flow
├── components/              # React components
│   ├── Navigation.tsx       # Main navigation
│   ├── Footer.tsx          # Footer component
│   ├── ProductCard.tsx     # Product display
│   ├── ChatInterface.tsx   # Chat UI
│   ├── CAMEOCreator.tsx    # CAMEO form
│   ├── VideoPlayer.tsx     # Video player
│   └── ProductCarousel.tsx # Product carousel
├── lib/                     # Utilities
│   └── api.ts              # API client
├── public/                  # Static assets
├── Dockerfile              # Docker configuration
└── package.json            # Dependencies

```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checks

## API Integration

The frontend integrates with the backend API through `/lib/api.ts`:

### Video API
```typescript
import { videoAPI } from '@/lib/api';

// Get featured video
const video = await videoAPI.getFeatured();

// Track video view
await videoAPI.trackView(videoId);
```

### Product API
```typescript
import { productAPI } from '@/lib/api';

// Get products with filters
const products = await productAPI.getProducts({
  category: 'Electronics',
  min_price: 0,
  max_price: 1000,
  sort_by: 'popular'
});
```

### Chat API
```typescript
import { chatAPI } from '@/lib/api';

// Initialize chat
const session = await chatAPI.init({ user_preferences: {} });

// Send message
const response = await chatAPI.sendMessage({
  session_id: session.session_id,
  message: 'Show me tech products'
});
```

### CAMEO API
```typescript
import { cameoAPI } from '@/lib/api';

// Generate CAMEO
const cameo = await cameoAPI.generate({
  occasion: 'Birthday',
  recipient_name: 'John',
  personal_message: 'Happy Birthday!',
  product_ids: ['prod_123'],
  tone: 'friendly'
});
```

### Checkout API
```typescript
import { checkoutAPI } from '@/lib/api';

// Create checkout session
const session = await checkoutAPI.createSession({
  email: 'user@example.com',
  shipping_info: { /* ... */ },
  items: cartItems,
  success_url: '/checkout?success=true',
  cancel_url: '/checkout?success=false'
});
```

## Docker Deployment

### Build Docker Image
```bash
docker build -t nerdx-apec-frontend .
```

### Run Container
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  -e NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx \
  nerdx-apec-frontend
```

### Docker Compose
```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
    depends_on:
      - backend
```

## Component Usage

### ProductCard
```tsx
<ProductCard
  product={product}
  viewMode="grid" // or "list"
/>
```

### VideoPlayer
```tsx
<VideoPlayer
  videoUrl="/videos/sam-altman.mp4"
  thumbnailUrl="/thumbnails/sam.jpg"
  title="Product Showcase"
  onPlay={() => console.log('Playing')}
  onPause={() => console.log('Paused')}
/>
```

### ChatInterface
```tsx
<ChatInterface
  message={{
    id: '1',
    role: 'assistant',
    content: 'Hello! How can I help?',
    timestamp: new Date()
  }}
/>
```

### CAMEOCreator
```tsx
<CAMEOCreator
  onSubmit={(request) => handleCreate(request)}
  isLoading={false}
/>
```

## Styling

### Custom Tailwind Classes
```css
/* Buttons */
.btn-primary
.btn-secondary
.btn-outline

/* Components */
.card
.input-field
.video-container

/* Effects */
.gradient-bg
.text-gradient
.glass-effect
```

### Animations
```tsx
// Framer Motion animations
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

## Performance Optimization

- **Image Optimization**: Next.js Image component with AVIF/WebP
- **Code Splitting**: Automatic with Next.js App Router
- **Font Optimization**: Google Fonts with display swap
- **Lazy Loading**: Components load on demand
- **Static Generation**: Pages pre-rendered at build time

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- Focus management

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe public key | Yes |
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | No |

## Troubleshooting

### Port already in use
```bash
# Kill process on port 3000
npx kill-port 3000
```

### Module not found
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

### API connection issues
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running
- Check CORS settings on backend

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

## License

Proprietary - NERDX APEC

## Support

For issues and questions:
- Email: support@nerdx-apec.com
- Documentation: [Link to docs]

---

**Built with ❤️ for APEC by NERDX Team**
