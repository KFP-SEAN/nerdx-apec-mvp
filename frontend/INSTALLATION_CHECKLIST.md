# Installation & Setup Checklist

Complete checklist for setting up the NERDX APEC Frontend.

## ✅ Pre-Installation Requirements

- [ ] Node.js 18+ installed (`node -v` to check)
- [ ] npm 9+ installed (`npm -v` to check)
- [ ] Git installed (for version control)
- [ ] Code editor (VS Code recommended)
- [ ] Backend API available (running on port 8000)

## ✅ Installation Steps

### Step 1: Get the Code
```bash
cd /c/Users/seans/nerdx-apec-mvp/frontend
```

### Step 2: Install Dependencies
```bash
npm install
```
**Expected output**: ~100+ packages installed
**Time**: 2-3 minutes

### Step 3: Environment Setup
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51...
```

### Step 4: Verify Installation
```bash
npm run type-check
npm run lint
```

### Step 5: Start Development Server
```bash
npm run dev
```

**Expected**: Server running at http://localhost:3000

## ✅ Verification Tests

### 1. Homepage Test
- [ ] Visit http://localhost:3000
- [ ] See "NERDX APEC" logo
- [ ] See hero section with Sam Altman video
- [ ] See navigation menu (Products, Chat, CAMEO)
- [ ] See footer with links

### 2. Products Page Test
- [ ] Visit http://localhost:3000/products
- [ ] See product grid
- [ ] Search bar works
- [ ] Filters can be opened
- [ ] Products can be sorted
- [ ] Toggle grid/list view

### 3. Chat Page Test
- [ ] Visit http://localhost:3000/chat
- [ ] See Maeju AI interface
- [ ] Can type message
- [ ] Suggested questions visible
- [ ] Session info displays

### 4. CAMEO Page Test
- [ ] Visit http://localhost:3000/cameo
- [ ] See step indicator
- [ ] Can select occasion
- [ ] Can enter recipient name
- [ ] Multi-step form works

### 5. Checkout Page Test
- [ ] Visit http://localhost:3000/checkout
- [ ] See form fields
- [ ] Can enter shipping info
- [ ] Order summary visible

## ✅ Component Verification

### Navigation Component
- [ ] Logo clickable (goes to home)
- [ ] Products link works
- [ ] Chat link works
- [ ] CAMEO link works
- [ ] Mobile menu toggles
- [ ] Cart counter visible

### Footer Component
- [ ] All link sections visible
- [ ] Social media icons present
- [ ] Language selector present
- [ ] Copyright year correct

### Product Card
- [ ] Image loads
- [ ] Product name visible
- [ ] Price formatted correctly
- [ ] Hover effects work
- [ ] Add to cart button present
- [ ] Like/heart icon toggles

### Video Player
- [ ] Video loads
- [ ] Play/pause works
- [ ] Volume control works
- [ ] Progress bar moves
- [ ] Fullscreen toggle works

### Chat Interface
- [ ] Messages display
- [ ] User/assistant distinction clear
- [ ] Timestamps visible
- [ ] Avatars present
- [ ] Scrolling works

### CAMEO Creator
- [ ] Step 1: Occasion selection works
- [ ] Step 2: Message textarea works
- [ ] Step 3: Product selection works
- [ ] Step 4: Review displays all info
- [ ] Navigation buttons work
- [ ] Validation prevents empty submission

## ✅ API Integration Tests

### Check API Connection
```bash
# Test if backend is running
curl http://localhost:8000/health
```

Should return: `{"status": "healthy"}`

### Test API Endpoints
- [ ] GET /videos/featured returns data
- [ ] GET /products returns product list
- [ ] POST /chat/init creates session
- [ ] POST /cameo/generate (mock test)
- [ ] GET /cart returns cart data

### API Client Tests
Open browser console on any page:
```javascript
// Test API client
import { api } from '@/lib/api';

// Should log response
api.get('/health').then(console.log);
```

## ✅ Styling Verification

### Tailwind CSS
- [ ] Colors working (primary blue, secondary purple)
- [ ] Custom classes available (.btn-primary, .card, etc.)
- [ ] Responsive breakpoints work (resize browser)
- [ ] Animations smooth (hover effects, transitions)
- [ ] Font loading (Inter for English, Noto Sans KR for Korean)

### Custom CSS
- [ ] Gradient backgrounds work
- [ ] Video controls overlay correctly
- [ ] Chat bubbles styled properly
- [ ] Loading spinners animate
- [ ] Card shadows visible

## ✅ Responsive Design Tests

### Desktop (1920x1080)
- [ ] Layout uses full width
- [ ] Navigation horizontal
- [ ] Product grid 4 columns
- [ ] All content readable

### Tablet (768x1024)
- [ ] Navigation adapts
- [ ] Product grid 2-3 columns
- [ ] Chat interface comfortable
- [ ] Forms well-spaced

### Mobile (375x667)
- [ ] Hamburger menu appears
- [ ] Product grid 1 column
- [ ] Chat full width
- [ ] Touch targets large enough
- [ ] Text readable without zoom

## ✅ Browser Compatibility

### Chrome/Edge
- [ ] All features work
- [ ] No console errors
- [ ] Smooth animations

### Firefox
- [ ] All features work
- [ ] Video playback works
- [ ] Forms submit correctly

### Safari
- [ ] All features work
- [ ] Font rendering correct
- [ ] Video controls work

## ✅ Performance Tests

### Lighthouse Audit
Run in Chrome DevTools:
```bash
# Or via CLI
npx lighthouse http://localhost:3000 --view
```

Target scores:
- [ ] Performance: 90+
- [ ] Accessibility: 95+
- [ ] Best Practices: 95+
- [ ] SEO: 90+

### Bundle Size
```bash
npm run build
```

Check output:
- [ ] Total bundle < 500KB (gzipped)
- [ ] First Load JS < 200KB
- [ ] No duplicate dependencies

### Loading Speed
- [ ] Initial page load < 2s
- [ ] Route transitions < 500ms
- [ ] Images load progressively
- [ ] No layout shift (CLS < 0.1)

## ✅ Error Handling Tests

### Network Errors
- [ ] Disconnect internet → shows error toast
- [ ] Wrong API URL → shows connection error
- [ ] Timeout → shows timeout error

### Form Validation
- [ ] Empty fields → shows validation message
- [ ] Invalid email → shows format error
- [ ] Required fields → prevents submission

### 404 Handling
- [ ] Visit /invalid-page → shows 404 (or redirects)
- [ ] Invalid product ID → shows error

## ✅ State Management Tests

### Cart Store
```javascript
// In browser console
import { useCartStore } from '@/lib/store';

const store = useCartStore.getState();
store.addItem({ /* item data */ });
console.log(store.items);
```

- [ ] Add to cart works
- [ ] Remove from cart works
- [ ] Update quantity works
- [ ] Cart persists on refresh
- [ ] Total calculations correct

### Wishlist Store
- [ ] Add to wishlist works
- [ ] Remove from wishlist works
- [ ] Wishlist persists
- [ ] Heart icon toggles

### Chat Store
- [ ] Messages stored
- [ ] Session ID saved
- [ ] History persists
- [ ] Clear messages works

## ✅ Accessibility Tests

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Enter activates buttons/links
- [ ] Escape closes modals/menus
- [ ] Focus indicators visible

### Screen Reader
- [ ] Images have alt text
- [ ] Buttons have labels
- [ ] Form fields labeled
- [ ] Headings hierarchical
- [ ] Landmarks present

### Color Contrast
- [ ] Text readable on all backgrounds
- [ ] Links distinguishable
- [ ] Error states clear
- [ ] Focus states visible

## ✅ Security Tests

### HTTPS
- [ ] Development uses HTTP (OK)
- [ ] Production will use HTTPS

### Environment Variables
- [ ] No secrets in client code
- [ ] NEXT_PUBLIC_ prefix used correctly
- [ ] .env files in .gitignore

### API Security
- [ ] Auth tokens in headers
- [ ] CSRF protection ready
- [ ] XSS protection enabled

## ✅ Docker Tests (Optional)

### Build Docker Image
```bash
docker build -t nerdx-frontend .
```
- [ ] Build succeeds
- [ ] No errors in logs
- [ ] Image size reasonable (<500MB)

### Run Container
```bash
docker run -p 3000:3000 nerdx-frontend
```
- [ ] Container starts
- [ ] App accessible on port 3000
- [ ] No runtime errors

## ✅ Production Build Test

### Build for Production
```bash
npm run build
```

Expected output:
- [ ] Build completes successfully
- [ ] No TypeScript errors
- [ ] All pages generated
- [ ] Bundle analysis looks good

### Start Production Server
```bash
npm run start
```
- [ ] Server starts on port 3000
- [ ] All routes work
- [ ] Static assets load
- [ ] No console errors

## ✅ Documentation Review

- [ ] README.md comprehensive
- [ ] QUICKSTART.md easy to follow
- [ ] DEPLOYMENT.md covers all methods
- [ ] PROJECT_SUMMARY.md accurate
- [ ] API documentation clear
- [ ] Component usage documented

## 🎯 Final Checklist

### Development
- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Dev server runs without errors
- [ ] Hot reload works
- [ ] TypeScript compiles
- [ ] Linting passes

### Features
- [ ] Video player works
- [ ] Product catalog functional
- [ ] Chat interface operational
- [ ] CAMEO creator complete
- [ ] Checkout flow works
- [ ] Cart management works

### Quality
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Responsive on all devices
- [ ] Accessible (WCAG AA)
- [ ] Good performance scores

### Ready for Production
- [ ] Production build works
- [ ] Environment configs ready
- [ ] Docker image builds
- [ ] Documentation complete
- [ ] Security measures in place
- [ ] Monitoring configured

## 📝 Notes

- Keep this checklist updated with new features
- Run through tests before each deployment
- Document any issues found
- Share feedback with team

## 🆘 Troubleshooting

If anything doesn't work:

1. Check the console for errors
2. Verify API is running (http://localhost:8000)
3. Confirm environment variables set correctly
4. Try clearing cache: `rm -rf .next node_modules && npm install`
5. Check README.md troubleshooting section
6. Contact: support@nerdx-apec.com

---

**Checklist Version**: 1.0
**Last Updated**: 2025-10-10
**Status**: Ready for Testing
