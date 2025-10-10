# Phase 3: Conversion (Commerce + AR)

Phase 3 of the NerdX APEC MVP handles commerce conversion through Stripe Advanced Checkout Platform (ACP) integration and AR experience unlocking after purchase.

## Features

### Commerce
- **Stripe ACP Integration**: Full-featured checkout with Advanced Checkout Platform
- **Order Management**: Create, track, and manage orders
- **Payment Processing**: Secure payment handling with Stripe
- **Webhook Handling**: Real-time payment event processing
- **Refund Support**: Handle refunds and update AR access accordingly
- **Multi-currency Support**: Support for international payments
- **Tax Calculation**: Automatic tax calculation (when enabled)
- **Shipping Options**: Standard and express shipping

### AR Experience
- **Post-Purchase Unlock**: Automatically unlock AR experiences after successful payment
- **Access Management**: Track and verify AR access tokens
- **Preview Mode**: Grant temporary trial access to AR experiences
- **Multi-Product Support**: Handle multiple AR experiences per user
- **Analytics**: Track AR unlock metrics and conversion rates
- **Access Revocation**: Revoke AR access on refunds

### APEC Limited Edition
- **Stock Management**: Track limited edition inventory
- **Quantity Restrictions**: Enforce purchase limits for limited editions
- **Event-Based Access**: Time-bound availability during APEC event

## Architecture

```
phase3-conversion/
├── server.js                  # Express server with middleware
├── package.json              # Dependencies and scripts
├── .env.example              # Environment template
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Multi-service orchestration
├── routes/
│   ├── orders.js            # Order and checkout endpoints
│   └── ar.js                # AR experience endpoints
├── services/
│   ├── stripe-service.js    # Stripe ACP integration
│   └── ar-service.js        # AR experience management
├── middleware/
│   └── error-handler.js     # Error handling middleware
└── utils/
    └── logger.js            # Winston logging configuration
```

## API Endpoints

### Orders API (`/api/orders`)

#### Create Checkout Session
```http
POST /api/orders/checkout
Content-Type: application/json

{
  "userId": "user-123",
  "productId": "apec-limited-001",
  "quantity": 1,
  "metadata": {}
}

Response:
{
  "success": true,
  "session": {
    "sessionId": "cs_test_...",
    "url": "https://checkout.stripe.com/...",
    "expiresAt": 1234567890
  }
}
```

#### Get Session Details
```http
GET /api/orders/session/:sessionId

Response:
{
  "success": true,
  "session": {
    "id": "cs_test_...",
    "status": "complete",
    "paymentStatus": "paid",
    "amountTotal": 299.99,
    "currency": "usd",
    "order": {
      "orderId": "uuid",
      "userId": "user-123",
      "productId": "prod-456",
      "arEnabled": true
    }
  }
}
```

#### Get Order Details
```http
GET /api/orders/:orderId

Response:
{
  "success": true,
  "order": {
    "orderId": "uuid",
    "status": "completed",
    "userId": "user-123",
    "productId": "prod-456",
    "quantity": 1,
    "total": 299.99,
    "arUnlocked": true
  }
}
```

#### Get User Orders
```http
GET /api/orders/user/:userId

Response:
{
  "success": true,
  "count": 1,
  "orders": [...]
}
```

#### Request Refund
```http
POST /api/orders/:orderId/refund
Content-Type: application/json

{
  "reason": "Customer requested",
  "amount": 299.99  // Optional, full refund if omitted
}

Response:
{
  "success": true,
  "refund": {
    "id": "re_...",
    "amount": 299.99,
    "status": "succeeded"
  }
}
```

### AR API (`/api/ar`)

#### Unlock AR Experience
```http
POST /api/ar/unlock
Content-Type: application/json

{
  "userId": "user-123",
  "productId": "prod-456",
  "orderId": "order-789"
}

Response:
{
  "success": true,
  "message": "AR experience unlocked successfully",
  "unlock": {
    "id": "unlock-id",
    "unlockedAt": "2024-11-10T12:00:00Z",
    "status": "active"
  },
  "arAsset": {
    "url": "https://cdn.nerdx.com/ar/model.glb",
    "type": "model",
    "platform": "web",
    "accessToken": "token..."
  }
}
```

#### Get AR Experience
```http
GET /api/ar/experience/:productId?userId=user-123

Response:
{
  "success": true,
  "hasAccess": true,
  "experience": {
    "unlock": {...},
    "arAsset": {...},
    "metadata": {...}
  }
}
```

#### Get User AR Experiences
```http
GET /api/ar/user/:userId/experiences

Response:
{
  "success": true,
  "count": 3,
  "experiences": [...]
}
```

#### Grant Preview Access
```http
POST /api/ar/preview
Content-Type: application/json

{
  "userId": "user-123",
  "productId": "prod-456",
  "duration": 30  // Minutes
}

Response:
{
  "success": true,
  "preview": {
    "id": "preview-id",
    "expiresAt": "2024-11-10T12:30:00Z",
    "status": "preview"
  },
  "arAsset": {
    "url": "...",
    "watermark": true
  }
}
```

#### Verify Access Token
```http
POST /api/ar/verify
Content-Type: application/json

{
  "accessToken": "token..."
}

Response:
{
  "success": true,
  "valid": true,
  "unlock": {
    "userId": "user-123",
    "productId": "prod-456",
    "isPreview": false
  }
}
```

#### Get AR Analytics
```http
GET /api/ar/analytics/:productId

Response:
{
  "success": true,
  "analytics": {
    "totalUnlocks": 150,
    "activeUnlocks": 145,
    "previewUnlocks": 300,
    "revokedUnlocks": 5,
    "conversionRate": "48.33"
  }
}
```

### Webhooks

#### Stripe Webhook
```http
POST /api/webhooks/stripe
Stripe-Signature: t=...,v1=...
Content-Type: application/json

{
  "type": "checkout.session.completed",
  "data": {...}
}

Response:
{
  "success": true,
  "received": true
}
```

## Setup & Installation

### Prerequisites
- Node.js 18+
- npm 9+
- Stripe account
- Phase 1 API running (for product/user data)

### Environment Setup

1. Copy environment template:
```bash
cp .env.example .env
```

2. Configure Stripe:
```env
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret
```

3. Configure services:
```env
PHASE1_API_URL=http://localhost:3001/api
FRONTEND_URL=http://localhost:3000
```

### Installation

```bash
# Install dependencies
npm install

# Development mode with auto-reload
npm run dev

# Production mode
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f phase3-conversion

# Stop services
docker-compose down
```

## Stripe Configuration

### 1. Create Stripe Account
Visit [https://stripe.com](https://stripe.com) and create an account

### 2. Get API Keys
- Dashboard → Developers → API Keys
- Copy Secret Key and Publishable Key
- Use test keys for development (`sk_test_...` and `pk_test_...`)

### 3. Configure Webhooks
- Dashboard → Developers → Webhooks
- Add endpoint: `https://yourdomain.com/api/webhooks/stripe`
- Select events:
  - `checkout.session.completed`
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `charge.refunded`
- Copy webhook signing secret

### 4. Enable Advanced Features
- Dashboard → Settings → Checkout
- Enable:
  - Shipping address collection
  - Phone number collection
  - Promotion codes
  - Terms of service

### 5. Configure Payment Methods
- Dashboard → Settings → Payment methods
- Enable:
  - Cards
  - Alipay (for China)
  - WeChat Pay (for China)

### 6. Tax Configuration (Optional)
- Dashboard → Settings → Tax
- Enable Stripe Tax for automatic calculation

## Integration with Phase 1

Phase 3 integrates with Phase 1 (Foundation) for:

### Product Data
```javascript
// Fetch product details including AR configuration
GET ${PHASE1_API_URL}/products/:productId

Response:
{
  "id": "prod-123",
  "name": "APEC Limited Edition",
  "price": 299.99,
  "stock": 50,
  "isLimitedEdition": true,
  "arEnabled": true,
  "arAssetUrl": "https://cdn.nerdx.com/ar/model.glb",
  "arType": "model",
  "arPlatform": "web"
}
```

### User Data
```javascript
// Fetch user details for checkout pre-fill
GET ${PHASE1_API_URL}/users/:userId

Response:
{
  "id": "user-123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

## Stripe ACP Features

### Advanced Checkout Platform Capabilities

1. **Multiple Payment Methods**
   - Credit/Debit Cards
   - Alipay
   - WeChat Pay
   - More (configurable)

2. **Address Collection**
   - Billing address (required)
   - Shipping address (8 countries)

3. **Shipping Options**
   - Standard (5-7 business days, $15)
   - Express (1-2 business days, $35)

4. **Promotion Codes**
   - Create codes in Stripe Dashboard
   - Automatic validation and application

5. **Tax Calculation**
   - Automatic tax calculation (when enabled)
   - Based on shipping address

6. **Adjustable Quantities**
   - Customers can adjust quantities
   - Disabled for limited editions
   - Min/max constraints

7. **Session Expiration**
   - Sessions expire after 30 minutes
   - Prevents inventory issues

8. **Terms of Service**
   - Required acceptance
   - Customizable in Stripe Dashboard

## Security

### Implemented Security Measures

1. **Rate Limiting**
   - 100 requests per 15 minutes per IP
   - Separate limits for webhooks

2. **Helmet.js**
   - Security headers
   - XSS protection
   - Content Security Policy

3. **CORS**
   - Configured allowed origins
   - Credentials support

4. **Webhook Verification**
   - Stripe signature verification
   - Prevents unauthorized webhooks

5. **Input Validation**
   - Express-validator
   - Joi schema validation

6. **Non-Root Docker User**
   - Runs as nodejs user (UID 1001)
   - Limited container privileges

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "message": "Error description"
  },
  "timestamp": "2024-11-10T12:00:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (no access)
- `404` - Not Found
- `500` - Internal Server Error

## Logging

Winston logger with multiple transports:
- Console output (colored)
- Combined logs: `logs/combined.log`
- Error logs: `logs/error.log`
- HTTP access logs (Morgan)

Log levels: `error`, `warn`, `info`, `http`, `debug`

## Testing

### Manual Testing with cURL

#### Create Checkout Session
```bash
curl -X POST http://localhost:3003/api/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "productId": "apec-limited-001",
    "quantity": 1
  }'
```

#### Get AR Experience
```bash
curl http://localhost:3003/api/ar/experience/apec-limited-001?userId=user-123
```

#### Grant Preview Access
```bash
curl -X POST http://localhost:3003/api/ar/preview \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "productId": "apec-limited-001",
    "duration": 30
  }'
```

### Webhook Testing

Use Stripe CLI for local webhook testing:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3003/api/webhooks/stripe

# Trigger test events
stripe trigger checkout.session.completed
```

## Production Deployment

### Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Use live Stripe keys (`sk_live_...`)
- [ ] Configure production webhook endpoint
- [ ] Set strong `SESSION_SECRET`
- [ ] Configure production `FRONTEND_URL`
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up Redis for session storage
- [ ] Configure email service
- [ ] Set up monitoring (Sentry, DataDog, etc.)
- [ ] Configure log aggregation
- [ ] Set up backup strategy
- [ ] Configure CDN for AR assets
- [ ] Load test checkout flow
- [ ] Test webhook delivery
- [ ] Set up alerts for failed payments

### Environment Variables
```env
NODE_ENV=production
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=warn
```

## Monitoring

### Health Check
```bash
curl http://localhost:3003/health
```

### Docker Health
```bash
docker-compose ps
```

### Logs
```bash
# Application logs
docker-compose logs -f phase3-conversion

# Stripe webhook logs
stripe logs tail
```

## APEC Limited Edition Features

- **Time-bound availability**: Only available during APEC event dates
- **Stock tracking**: Real-time inventory management
- **Purchase limits**: Max quantity enforcement
- **Exclusive AR content**: Premium AR experiences for APEC buyers
- **Limited quantities**: 500 units maximum

## Troubleshooting

### Common Issues

**Webhook signature verification failed**
- Check `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- Ensure raw body is sent to webhook endpoint
- Verify endpoint is publicly accessible

**AR experience not unlocking**
- Check Phase 1 API is accessible
- Verify product has `arEnabled: true`
- Check webhook is being processed successfully

**Payment fails at checkout**
- Verify Stripe API keys are correct
- Check product price is valid (>$0.50 USD)
- Ensure payment methods are enabled

**Session expired**
- Checkout sessions expire after 30 minutes
- Create new session for customer

## Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test webhook handling thoroughly
5. Ensure security best practices

## License

MIT

## Support

For issues and questions:
- Email: support@nerdx.com
- Stripe Support: https://support.stripe.com

## Related Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Phase 1 API Documentation](../phase1-foundation/README.md)
- [Phase 2 Engagement Documentation](../phase2-engagement/README.md)
