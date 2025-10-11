# Custom Shopify App API Documentation

## Overview

This custom Shopify app provides:
- Webhook handlers for order events
- AR access management
- Purchase relationship tracking
- Product recommendations

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Shopify   │─────▶│  App Server  │─────▶│   Neo4j     │
│  (Webhooks) │      │  (Express)   │      │  (Graph DB) │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Redis    │
                     │   (Cache)   │
                     └─────────────┘
```

## Webhooks

### orders/paid
Triggered when an order is successfully paid.

**Handler**: `src/webhooks/orders-paid.ts`

**Actions**:
1. Verify webhook authenticity (HMAC)
2. Grant AR access for AR-enabled products
3. Create purchase relationship in Neo4j
4. Cache order data in Redis

### orders/cancelled
Triggered when an order is cancelled.

**Handler**: `src/webhooks/orders-cancelled.ts`

**Actions**:
1. Verify webhook authenticity
2. Revoke AR access
3. Update purchase status

## API Endpoints

### POST /api/ar-access/verify
Verify if user has AR access for a product.

**Request**:
```json
{
  "productId": "9018574471422",
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "hasAccess": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2025-11-10T00:00:00Z"
}
```

### GET /api/recommendations/:email
Get product recommendations based on purchase history.

**Response**:
```json
{
  "recommendations": [
    "9018574471422",
    "9018574504190"
  ]
}
```

## Database Schema

### Neo4j
```cypher
// Nodes
(:User {email, createdAt})
(:Order {id, total, timestamp})
(:Product {id, title})

// Relationships
(User)-[:PLACED]->(Order)
(Order)-[:CONTAINS {quantity, price}]->(Product)
```

### Redis Keys
```
ar:access:{productId}:{email} → { hasAccess, expiresAt }
order:{orderId} → { ...orderData }
recommendations:{email} → [productIds]
```

## Setup

1. Install dependencies:
```bash
cd backend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start services:
```bash
docker-compose up -d neo4j redis
```

4. Run server:
```bash
npm run dev
```

## Testing Webhooks

Use Shopify CLI to test webhooks locally:

```bash
shopify webhook trigger orders/paid
```

Or use ngrok for public URL:

```bash
ngrok http 3001
# Update webhook URL in Shopify dashboard
```

## Deployment

### Docker
```bash
docker build -t nerdx-app .
docker run -p 3001:3001 --env-file .env nerdx-app
```

### AWS / Heroku
See deployment guide in `docs/DEPLOYMENT_BACKEND.md`
