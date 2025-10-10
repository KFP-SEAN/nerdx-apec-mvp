# Phase 3: Quick Start Guide

Get Phase 3 (Conversion) running in 5 minutes.

## Prerequisites

- Node.js 18+
- npm 9+
- Stripe account (free test account)
- Phase 1 API running (optional for local testing)

## Setup Steps

### 1. Install Dependencies (1 min)

```bash
cd phase3-conversion
npm install
```

### 2. Configure Environment (2 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your text editor
# Required fields:
# - STRIPE_SECRET_KEY (get from https://dashboard.stripe.com/test/apikeys)
# - STRIPE_WEBHOOK_SECRET (get after setting up webhook)
```

**Get Stripe Keys:**
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy "Secret key" (starts with `sk_test_`)
3. Paste into `.env` as `STRIPE_SECRET_KEY`

### 3. Start Server (30 seconds)

```bash
# Development mode with auto-reload
npm run dev

# OR production mode
npm start
```

Server starts on http://localhost:3003

### 4. Test It Works (30 seconds)

```bash
# Health check
curl http://localhost:3003/health

# Expected response:
{
  "status": "healthy",
  "service": "phase3-conversion",
  ...
}
```

### 5. Try a Feature (1 min)

**Grant AR Preview Access:**

```bash
curl -X POST http://localhost:3003/api/ar/preview \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "productId": "apec-limited-001",
    "duration": 30
  }'
```

**Create Checkout Session:**

```bash
curl -X POST http://localhost:3003/api/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "productId": "apec-limited-001",
    "quantity": 1
  }'
```

## Common Issues

### "Cannot find module"
```bash
# Solution: Install dependencies
npm install
```

### "Stripe key error"
```bash
# Solution: Check .env file has correct Stripe keys
cat .env | grep STRIPE_SECRET_KEY
```

### "Port 3003 already in use"
```bash
# Solution: Change port in .env
echo "PORT=3004" >> .env
```

### "Phase 1 API not found"
```bash
# Solution: Either start Phase 1 or comment out Phase 1 calls in services
# Phase 3 can run standalone for testing
```

## Next Steps

### Set Up Webhooks (5 min)

For testing webhooks locally:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe  # macOS
# OR download from https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3003/api/webhooks/stripe

# Copy webhook secret (starts with whsec_) to .env
```

### Import Postman Collection (2 min)

1. Open Postman
2. Import `postman_collection.json`
3. Update variables (baseUrl, userId, productId)
4. Start testing endpoints

### Try Frontend Demo (1 min)

```bash
# Open in browser
open examples/frontend-integration.html
# OR
# Windows: start examples/frontend-integration.html
# Linux: xdg-open examples/frontend-integration.html
```

### Run with Docker (3 min)

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Development Workflow

```bash
# 1. Make changes to code
# 2. Server auto-reloads (with npm run dev)
# 3. Test with curl or Postman
# 4. Check logs in terminal or logs/combined.log
```

## Testing Checklist

- [ ] Health check returns 200
- [ ] Can create checkout session
- [ ] Can grant AR preview
- [ ] Can check AR access
- [ ] Webhooks are working (with Stripe CLI)

## Production Deployment

See [README.md](README.md) for full production deployment guide.

Quick checklist:
- [ ] Set `NODE_ENV=production`
- [ ] Use live Stripe keys (`sk_live_...`)
- [ ] Configure production webhook
- [ ] Set up database
- [ ] Configure SSL/TLS
- [ ] Set up monitoring

## Resources

- **Full Documentation**: [README.md](README.md)
- **Integration Guide**: [INTEGRATION.md](INTEGRATION.md)
- **Stripe Docs**: https://stripe.com/docs
- **Test Cards**: https://stripe.com/docs/testing

## Test Credit Cards

Use these in Stripe test mode:

| Card | Number | CVC | Date |
|------|--------|-----|------|
| Success | 4242 4242 4242 4242 | Any 3 digits | Any future date |
| Decline | 4000 0000 0000 0002 | Any 3 digits | Any future date |
| Auth Required | 4000 0027 6000 3184 | Any 3 digits | Any future date |

## Quick Commands

```bash
# Health check
curl localhost:3003/health

# Create checkout
curl -X POST localhost:3003/api/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-123","productId":"prod-456","quantity":1}'

# Grant AR preview
curl -X POST localhost:3003/api/ar/preview \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-123","productId":"prod-456","duration":30}'

# Check AR access
curl "localhost:3003/api/ar/experience/prod-456?userId=user-123"

# View logs
tail -f logs/combined.log

# Stop server
# Press Ctrl+C in terminal
```

## Support

- Issues? Check [README.md](README.md) Troubleshooting section
- Questions? See [INTEGRATION.md](INTEGRATION.md)
- Stripe help? https://support.stripe.com

## What's Next?

1. ✅ Basic setup complete
2. Configure Stripe webhooks
3. Set up Phase 1 integration
4. Customize for your products
5. Deploy to production

Happy coding! 🚀
