# Phase 3 Integration Guide

This guide explains how to integrate Phase 3 (Conversion) with other phases of the NerdX APEC MVP.

## Integration Overview

```
┌─────────────────┐
│   Frontend      │
│  (User Flow)    │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         v                  v
┌─────────────────┐  ┌──────────────────┐
│   Phase 1       │  │    Phase 3       │
│  Foundation     │◄─┤   Conversion     │
│ (User/Product)  │  │ (Commerce + AR)  │
└─────────────────┘  └──────────────────┘
         │                  │
         v                  │
┌─────────────────┐         │
│   Phase 2       │         │
│  Engagement     │◄────────┘
│ (Social + AR)   │
└─────────────────┘
```

## Frontend Integration

### 1. Checkout Flow

#### Step 1: Display Product
```javascript
// Fetch product from Phase 1
const product = await fetch('http://localhost:3001/api/products/apec-limited-001')
  .then(r => r.json());

// Display product with AR preview
if (product.arEnabled) {
  showARPreviewButton();
}
```

#### Step 2: Try AR (Preview)
```javascript
// Grant temporary AR access
async function tryAR(userId, productId) {
  const response = await fetch('http://localhost:3003/api/ar/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId,
      productId,
      duration: 30 // 30 minutes
    })
  });

  const { preview, arAsset } = await response.json();

  // Load AR experience with watermark
  loadARExperience(arAsset.url, arAsset.accessToken, preview.expiresAt);
}
```

#### Step 3: Create Checkout
```javascript
async function initiateCheckout(userId, productId, quantity = 1) {
  const response = await fetch('http://localhost:3003/api/orders/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId,
      productId,
      quantity
    })
  });

  const { session } = await response.json();

  // Redirect to Stripe Checkout
  window.location.href = session.url;
}
```

#### Step 4: Handle Success
```javascript
// Success page: /order/success?session_id={CHECKOUT_SESSION_ID}
async function handleCheckoutSuccess() {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get('session_id');

  if (!sessionId) return;

  // Get session details
  const response = await fetch(
    `http://localhost:3003/api/orders/session/${sessionId}`
  );

  const { session } = await response.json();

  if (session.paymentStatus === 'paid') {
    // Show success message
    showSuccessMessage('Order completed!');

    // If AR enabled, show unlock notification
    if (session.order.arEnabled) {
      showARUnlockNotification(session.order.productId);
    }
  }
}
```

#### Step 5: Access AR Experience
```javascript
async function accessARExperience(userId, productId) {
  const response = await fetch(
    `http://localhost:3003/api/ar/experience/${productId}?userId=${userId}`
  );

  const { hasAccess, experience } = await response.json();

  if (hasAccess) {
    // Load full AR experience (no watermark)
    loadARExperience(
      experience.arAsset.url,
      experience.arAsset.accessToken
    );
  } else {
    // Show purchase prompt
    showPurchasePrompt(productId);
  }
}
```

### 2. User Dashboard Integration

#### Display User Orders
```javascript
async function loadUserOrders(userId) {
  const response = await fetch(
    `http://localhost:3003/api/orders/user/${userId}`
  );

  const { orders } = await response.json();

  return orders;
}
```

#### Display AR Experiences
```javascript
async function loadUserARExperiences(userId) {
  const response = await fetch(
    `http://localhost:3003/api/ar/user/${userId}/experiences`
  );

  const { experiences } = await response.json();

  return experiences;
}
```

## Backend Integration

### Phase 1 Integration (Product & User Data)

Phase 3 fetches data from Phase 1:

```javascript
// In stripe-service.js
async fetchProductDetails(productId) {
  const response = await axios.get(
    `${this.phase1ApiUrl}/products/${productId}`
  );
  return response.data;
}

async fetchUserDetails(userId) {
  const response = await axios.get(
    `${this.phase1ApiUrl}/users/${userId}`
  );
  return response.data;
}
```

Required Phase 1 Product Schema:
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": "number",
  "images": ["string"],
  "stock": "number",
  "isLimitedEdition": "boolean",
  "apecEdition": "boolean",
  "arEnabled": "boolean",
  "arAssetUrl": "string",
  "arType": "string",
  "arPlatform": "string"
}
```

### Phase 2 Integration (Social Engagement)

After AR unlock, notify Phase 2 for social features:

```javascript
// In ar-service.js - after unlock
async notifyPhase2(userId, productId, unlockId) {
  try {
    await axios.post('http://localhost:3002/api/ar/unlock-notification', {
      userId,
      productId,
      unlockId,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Failed to notify Phase 2:', error);
    // Non-critical, don't throw
  }
}
```

Phase 2 can then:
- Enable AR sharing features
- Track social engagement with AR
- Create AR-specific content feeds

## Webhook Integration

### Stripe → Phase 3 Flow

```
1. Payment Success
   Stripe → POST /api/webhooks/stripe

2. Phase 3 Processing
   - Verify webhook signature
   - Update order status
   - Unlock AR experience

3. Phase 3 → Phase 1
   - Update inventory
   - Update user purchase history

4. Phase 3 → Phase 2
   - Notify AR unlock
   - Enable social features
```

### Webhook Event Handlers

```javascript
// checkout.session.completed
async handleCheckoutCompleted(session) {
  const { userId, productId, orderId, arEnabled } = session.metadata;

  // 1. Update order status in database
  await this.updateOrderStatus(orderId, 'completed');

  // 2. Unlock AR if enabled
  if (arEnabled === 'true') {
    await this.unlockARExperience(userId, productId, orderId);
  }

  // 3. Update Phase 1 inventory
  await this.updateInventory(productId, -1);

  // 4. Notify Phase 2
  await this.notifyPhase2(userId, productId, orderId);

  // 5. Send confirmation email
  await this.sendOrderConfirmation(session);
}
```

## API Gateway Pattern (Recommended)

For production, use an API Gateway to route requests:

```
                    ┌──────────────┐
                    │ API Gateway  │
                    │ (nginx/Kong) │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         v                 v                 v
  ┌───────────┐    ┌──────────────┐   ┌──────────┐
  │  Phase 1  │    │   Phase 3    │   │ Phase 2  │
  │  :3001    │    │    :3003     │   │  :3002   │
  └───────────┘    └──────────────┘   └──────────┘
```

nginx configuration:
```nginx
upstream phase1 {
  server phase1:3001;
}

upstream phase3 {
  server phase3:3003;
}

server {
  listen 80;

  location /api/products {
    proxy_pass http://phase1;
  }

  location /api/users {
    proxy_pass http://phase1;
  }

  location /api/orders {
    proxy_pass http://phase3;
  }

  location /api/ar {
    proxy_pass http://phase3;
  }

  location /api/webhooks/stripe {
    proxy_pass http://phase3;
  }
}
```

## Database Considerations

### Phase 3 Tables (PostgreSQL Example)

```sql
-- Orders table
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL,
  product_id VARCHAR(255) NOT NULL,
  stripe_session_id VARCHAR(255) UNIQUE,
  stripe_payment_intent_id VARCHAR(255),
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'usd',
  quantity INTEGER DEFAULT 1,
  status VARCHAR(50) NOT NULL,
  shipping_address JSONB,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- AR unlocks table
CREATE TABLE ar_unlocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL,
  product_id VARCHAR(255) NOT NULL,
  order_id UUID REFERENCES orders(id),
  access_token VARCHAR(255) UNIQUE NOT NULL,
  status VARCHAR(50) NOT NULL,
  unlocked_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  revoked_at TIMESTAMP,
  metadata JSONB,
  UNIQUE(user_id, product_id)
);

-- Indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_ar_unlocks_user_id ON ar_unlocks(user_id);
CREATE INDEX idx_ar_unlocks_product_id ON ar_unlocks(product_id);
```

### Cross-Phase Data Sharing

**Option 1: Service-to-Service API Calls** (Current)
- Simple to implement
- Each service is independent
- Can be slower (network latency)

**Option 2: Shared Database**
- Faster data access
- Tight coupling between services
- Harder to scale independently

**Option 3: Event-Driven Architecture** (Recommended for Production)
- Use message queue (RabbitMQ, Kafka)
- Services publish/subscribe to events
- Loose coupling, scalable
- More complex setup

Example event-driven flow:
```javascript
// Phase 3 publishes event
eventBus.publish('order.completed', {
  orderId,
  userId,
  productId,
  amount,
  arEnabled
});

// Phase 1 subscriber
eventBus.subscribe('order.completed', async (event) => {
  await updateInventory(event.productId, -1);
  await updateUserPurchases(event.userId, event.orderId);
});

// Phase 2 subscriber
eventBus.subscribe('order.completed', async (event) => {
  if (event.arEnabled) {
    await enableSocialFeatures(event.userId, event.productId);
  }
});
```

## Testing Integration

### Integration Test Example
```javascript
const request = require('supertest');

describe('Full Purchase Flow Integration', () => {
  it('should complete purchase and unlock AR', async () => {
    // 1. Fetch product from Phase 1
    const product = await request('http://localhost:3001')
      .get('/api/products/apec-limited-001')
      .expect(200);

    expect(product.body.arEnabled).toBe(true);

    // 2. Create checkout session
    const checkout = await request('http://localhost:3003')
      .post('/api/orders/checkout')
      .send({
        userId: 'test-user',
        productId: 'apec-limited-001',
        quantity: 1
      })
      .expect(200);

    expect(checkout.body.session.url).toBeDefined();

    // 3. Simulate webhook (payment success)
    // ... webhook test

    // 4. Verify AR unlock
    const arAccess = await request('http://localhost:3003')
      .get('/api/ar/experience/apec-limited-001?userId=test-user')
      .expect(200);

    expect(arAccess.body.hasAccess).toBe(true);
  });
});
```

## Error Handling Across Services

### Retry Logic
```javascript
async function fetchWithRetry(url, options = {}, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response.json();

      if (i === retries - 1) throw new Error('Max retries reached');

      // Exponential backoff
      await new Promise(resolve =>
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    } catch (error) {
      if (i === retries - 1) throw error;
    }
  }
}
```

### Circuit Breaker Pattern
```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failureCount = 0;
    this.threshold = threshold;
    this.timeout = timeout;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }

  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}

// Usage
const phase1Breaker = new CircuitBreaker();

async function fetchProductSafe(productId) {
  return phase1Breaker.call(() =>
    fetchProductDetails(productId)
  );
}
```

## Monitoring Integration

### Health Check Aggregation
```javascript
app.get('/health/all', async (req, res) => {
  const services = {
    phase3: { status: 'healthy' },
    phase1: await checkPhase1Health(),
    stripe: await checkStripeHealth(),
    redis: await checkRedisHealth()
  };

  const isHealthy = Object.values(services)
    .every(s => s.status === 'healthy');

  res.status(isHealthy ? 200 : 503).json({
    status: isHealthy ? 'healthy' : 'degraded',
    services
  });
});
```

### Distributed Tracing
Use OpenTelemetry or similar for tracing requests across services:

```javascript
const { trace } = require('@opentelemetry/api');

app.use((req, res, next) => {
  const tracer = trace.getTracer('phase3-conversion');
  const span = tracer.startSpan('http_request', {
    attributes: {
      'http.method': req.method,
      'http.url': req.url
    }
  });

  req.span = span;
  res.on('finish', () => {
    span.setAttribute('http.status_code', res.statusCode);
    span.end();
  });

  next();
});
```

## Security Considerations

### API Authentication
```javascript
// JWT verification for inter-service communication
const jwt = require('jsonwebtoken');

function verifyServiceToken(req, res, next) {
  const token = req.headers['x-service-token'];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.SERVICE_SECRET);
    req.service = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

// Protect internal endpoints
app.post('/api/ar/unlock', verifyServiceToken, async (req, res) => {
  // Only other services can call this
});
```

## Deployment Checklist

- [ ] Phase 1 API accessible
- [ ] Stripe webhooks configured
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Redis connected
- [ ] Health checks passing
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Integration tests passing
- [ ] Circuit breakers configured
- [ ] Rate limiting enabled

## Support

For integration issues:
- Check service logs
- Verify network connectivity
- Test individual services
- Review API documentation
- Check webhook delivery
