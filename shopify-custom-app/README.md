# NERDX APEC Shopify Custom App

**AR Access Management & Purchase Sync Service**

A production-ready Node.js/Express application that handles Shopify webhooks, manages AR access tokens, syncs purchase data to Neo4j, and sends email notifications.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Webhook Integration](#webhook-integration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

The NERDX APEC Shopify Custom App integrates with Shopify to automatically:
- Process order payments and grant AR access
- Handle order cancellations and refunds
- Generate and manage JWT tokens (90-day expiry)
- Sync purchase data to Neo4j Phase 1 database
- Send email notifications to customers

---

## Features

### Core Functionality
- **Webhook Processing**: Orders/paid, orders/cancelled, refunds/create
- **AR Token Management**: JWT generation with 90-day expiry
- **Neo4j Integration**: Creates PURCHASED and HAS_AR_ACCESS relationships
- **Email Notifications**: Branded emails for AR unlock events
- **Idempotency**: Prevents duplicate webhook processing
- **Retry Logic**: Exponential backoff with Dead Letter Queue

### Security
- **HMAC-SHA256 Verification**: Validates Shopify webhook signatures
- **API Key Authentication**: Protects internal endpoints
- **JWT Tokens**: Secure AR access with expiration
- **Rate Limiting**: Prevents abuse
- **Helmet.js**: Security headers

### Observability
- **Winston Logging**: Structured logs with daily rotation
- **Prometheus Metrics**: Business and technical metrics
- **Health Checks**: Kubernetes-ready probes
- **Error Tracking**: Comprehensive error handling

---

## Architecture

```
┌─────────────┐
│   Shopify   │
└──────┬──────┘
       │ Webhooks (HMAC)
       ▼
┌─────────────────────────────────┐
│  Express Server (Port 3000)     │
│  ┌────────────────────────────┐ │
│  │  Webhook Handler           │ │
│  │  - Signature Verification  │ │
│  │  - Idempotency Check       │ │
│  │  - Retry Logic             │ │
│  └────────────┬───────────────┘ │
│               ▼                  │
│  ┌────────────────────────────┐ │
│  │  AR Access Service         │ │
│  │  - JWT Generation          │ │
│  │  - Token Verification      │ │
│  └────────────┬───────────────┘ │
│               ▼                  │
│  ┌────────────────────────────┐ │
│  │  Neo4j Sync Service        │ │
│  │  - Create Users/Products   │ │
│  │  - PURCHASED relationship  │ │
│  │  - HAS_AR_ACCESS relation  │ │
│  └────────────┬───────────────┘ │
│               ▼                  │
│  ┌────────────────────────────┐ │
│  │  Notification Service      │ │
│  │  - Email Templates         │ │
│  │  - SMTP Delivery           │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   Neo4j     │      │    SMTP     │
│  Database   │      │   Server    │
└─────────────┘      └─────────────┘
```

---

## Prerequisites

- **Node.js** 18+
- **npm** 9+
- **Neo4j** 5.x (Phase 1 database)
- **SMTP Server** (Gmail, SendGrid, etc.)
- **Shopify Store** with admin access

---

## Installation

### 1. Clone the Repository

```bash
cd /c/Users/seans/nerdx-apec-mvp/shopify-custom-app
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Start the Server

```bash
# Development
npm run dev

# Production
npm start
```

---

## Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Server
NODE_ENV=production
PORT=3000

# Shopify
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com

# Security
API_KEY=your_secure_api_key
JWT_SECRET=your_jwt_secret

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
EMAIL_FROM=noreply@nerdx.com

# AR Configuration
AR_TOKEN_EXPIRY_DAYS=90
AR_VIEWER_URL=https://ar.nerdx.com
```

### Neo4j Database Schema

The app expects these node labels and relationships:

```cypher
// Nodes
(:User {userId, email, firstName, lastName})
(:Product {productId, title, hasAR})

// Relationships
(:User)-[:PURCHASED {orderId, amount, status}]->(:Product)
(:User)-[:HAS_AR_ACCESS {tokenId, expiresAt, status}]->(:Product)
```

---

## Usage

### Starting the Server

```bash
# Development with auto-reload
npm run dev

# Production
npm start

# Docker
docker-compose up -d
```

### Testing Webhooks Locally

Use ngrok to expose your local server:

```bash
ngrok http 3000
```

Then configure Shopify webhooks to point to your ngrok URL:
```
https://your-ngrok-url.ngrok.io/webhooks/orders/paid
```

---

## API Documentation

### Webhook Endpoints

#### POST `/webhooks/orders/paid`
Processes order payment and grants AR access.

**Headers:**
```
X-Shopify-Topic: orders/paid
X-Shopify-Shop-Domain: your-shop.myshopify.com
X-Shopify-Hmac-Sha256: <signature>
```

**Response:**
```json
{
  "success": true,
  "orderId": "12345",
  "results": [
    {
      "productId": "67890",
      "success": true,
      "tokenId": "uuid"
    }
  ]
}
```

#### POST `/webhooks/orders/cancelled`
Revokes AR access for cancelled orders.

#### POST `/webhooks/refunds/create`
Revokes AR access for refunded items.

---

### AR Access API Endpoints

All AR access endpoints require API key authentication:
```
Authorization: API-Key your_api_key_here
```

#### POST `/api/ar-access/generate`
Generate a new AR access token.

**Request:**
```json
{
  "userId": "user123",
  "email": "user@example.com",
  "productId": "prod456",
  "orderId": "order789",
  "productTitle": "Product Name"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "tokenId": "uuid",
    "expiresAt": "2024-04-15T00:00:00.000Z",
    "expiresIn": 7776000
  }
}
```

#### POST `/api/ar-access/verify`
Verify an AR access token (public endpoint).

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "data": {
    "userId": "user123",
    "email": "user@example.com",
    "productId": "prod456",
    "hasActiveAccess": true
  }
}
```

#### POST `/api/ar-access/refresh`
Refresh an expired or expiring token (public endpoint).

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### GET `/api/ar-access/check/:email/:productId`
Check if user has AR access (requires API key).

#### GET `/api/ar-access/user/:email`
Get user's purchases and AR access status (requires API key).

#### POST `/api/ar-access/revoke`
Manually revoke AR access (requires API key).

**Request:**
```json
{
  "email": "user@example.com",
  "productId": "prod456",
  "reason": "manual_revocation"
}
```

---

### Health Check Endpoints

#### GET `/health`
Overall service health.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 12345,
  "services": {
    "neo4j": "up",
    "email": "configured"
  }
}
```

#### GET `/ready`
Kubernetes readiness probe.

#### GET `/live`
Kubernetes liveness probe.

#### GET `/metrics`
Prometheus metrics endpoint.

---

## Webhook Integration

### Shopify Configuration

1. Go to **Settings** > **Notifications** > **Webhooks**
2. Create webhooks for:
   - `orders/paid` → `https://your-domain.com/webhooks/orders/paid`
   - `orders/cancelled` → `https://your-domain.com/webhooks/orders/cancelled`
   - `refunds/create` → `https://your-domain.com/webhooks/refunds/create`
3. Format: **JSON**
4. API version: **Latest stable**

### Webhook Secret

Copy the webhook signing secret from Shopify and add to `.env`:
```env
SHOPIFY_WEBHOOK_SECRET=your_secret_here
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t nerdx-apec-shopify:latest .

# Run container
docker run -d \
  --name nerdx-apec-shopify \
  -p 3000:3000 \
  --env-file .env \
  nerdx-apec-shopify:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    env_file:
      - .env
    depends_on:
      - neo4j
    restart: unless-stopped

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nerdx-apec-shopify
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nerdx-apec-shopify
  template:
    metadata:
      labels:
        app: nerdx-apec-shopify
    spec:
      containers:
      - name: app
        image: nerdx-apec-shopify:latest
        ports:
        - containerPort: 3000
        envFrom:
        - secretRef:
            name: shopify-secrets
        livenessProbe:
          httpGet:
            path: /live
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## Monitoring

### Prometheus Metrics

Available at `/metrics`:

- `http_request_duration_seconds` - HTTP request latency
- `shopify_webhook_received_total` - Webhooks received
- `shopify_webhook_processed_total` - Webhooks processed
- `shopify_webhook_failed_total` - Webhook failures
- `ar_tokens_generated_total` - AR tokens created
- `neo4j_operations_total` - Neo4j operations
- `notifications_sent_total` - Emails sent

### Logging

Logs are written to:
- Console (stdout/stderr)
- `logs/combined-YYYY-MM-DD.log` (all levels)
- `logs/error-YYYY-MM-DD.log` (errors only)
- `logs/webhook-YYYY-MM-DD.log` (webhook audit trail)

### Grafana Dashboard

Import the included Grafana dashboard:
```bash
# TODO: Add dashboard JSON
```

---

## Security

### Best Practices

1. **Rotate Secrets Regularly**
   ```bash
   # Generate new JWT secret
   node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
   ```

2. **Use Environment Variables**
   - Never commit `.env` to version control
   - Use secret management (AWS Secrets Manager, Vault)

3. **HTTPS Only**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates

4. **Rate Limiting**
   - Default: 100 requests per 15 minutes
   - Adjust in `.env`: `RATE_LIMIT_MAX_REQUESTS`

5. **API Key Security**
   - Use strong, random API keys
   - Implement key rotation
   - Log all API access

### Webhook Security

- HMAC-SHA256 signature verification
- Idempotency checks prevent replay attacks
- Request body validation

---

## Troubleshooting

### Common Issues

#### Webhook Signature Verification Fails

**Problem:** `Invalid webhook signature` error

**Solution:**
1. Verify `SHOPIFY_WEBHOOK_SECRET` matches Shopify
2. Ensure raw body is captured before JSON parsing
3. Check webhook format is JSON (not XML)

#### Neo4j Connection Errors

**Problem:** `Neo4j connection verification failed`

**Solution:**
1. Verify Neo4j is running: `docker ps` or check service
2. Check credentials in `.env`
3. Test connection:
   ```bash
   cypher-shell -a bolt://localhost:7687 -u neo4j -p password
   ```

#### Email Notifications Not Sending

**Problem:** No emails received

**Solution:**
1. Check SMTP credentials in `.env`
2. Enable "Less secure apps" for Gmail (or use app password)
3. Check logs for SMTP errors:
   ```bash
   tail -f logs/error-*.log | grep -i smtp
   ```

#### JWT Token Expired

**Problem:** Token expired before 90 days

**Solution:**
1. Verify `AR_TOKEN_EXPIRY_DAYS=90` in `.env`
2. Use refresh endpoint: `POST /api/ar-access/refresh`

### Debug Mode

Enable verbose logging:
```env
LOG_LEVEL=debug
NODE_ENV=development
```

---

## Contributing

### Development Setup

```bash
# Install dependencies
npm install

# Run linter
npm run lint

# Fix linting issues
npm run lint:fix

# Run tests (TODO)
npm test
```

### Code Style

- ESLint with Airbnb config
- Use async/await over callbacks
- Follow existing patterns

### Commit Messages

```
feat: Add batch token generation endpoint
fix: Resolve Neo4j connection pool leak
docs: Update API documentation
refactor: Simplify webhook handler logic
```

---

## Project Structure

```
shopify-custom-app/
├── server.js                 # Express server entry point
├── package.json              # Dependencies
├── .env.example              # Environment template
├── Dockerfile                # Docker configuration
├── README.md                 # This file
│
├── middleware/
│   ├── auth.js              # API key & JWT auth
│   └── error-handler.js     # Error handling
│
├── routes/
│   ├── webhooks.js          # Webhook endpoints
│   └── ar-access.js         # AR access API
│
├── services/
│   ├── webhook-handler.js   # Webhook processing
│   ├── ar-access-service.js # JWT token management
│   ├── neo4j-sync-service.js # Neo4j integration
│   └── notification-service.js # Email notifications
│
├── utils/
│   ├── logger.js            # Winston logging
│   └── metrics.js           # Prometheus metrics
│
└── logs/                    # Log files (auto-generated)
```

---

## License

MIT License - NERDX 2024

---

## Support

For issues and questions:
- GitHub Issues: [Create an issue](#)
- Email: support@nerdx.com
- Slack: #nerdx-apec-support

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Shopify webhook integration
- AR token generation (90-day expiry)
- Neo4j sync service
- Email notifications
- Prometheus metrics
- Docker support

---

**Built with Node.js, Express, Neo4j, and JWT**
