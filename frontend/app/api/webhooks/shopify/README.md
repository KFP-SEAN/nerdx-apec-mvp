# Shopify Webhooks API Route

## Overview
This API route handles incoming webhooks from Shopify for order, cart, and customer events.

## Location
`app/api/webhooks/shopify/route.ts`

## Supported Webhooks
- `orders/create` - Triggered when a new order is created
- `orders/paid` - Triggered when an order payment is confirmed
- `orders/fulfilled` - Triggered when an order is fulfilled/shipped
- `carts/update` - Triggered when a cart is updated (for abandonment detection)
- `customers/create` - Triggered when a new customer is created

## Environment Variables

Add these to your `.env.local` file:

```bash
# Shopify Webhook Secret (preferred)
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret_here

# OR use Admin API Token as fallback
SHOPIFY_ADMIN_API_TOKEN=your_admin_api_token_here
```

## Setup Instructions

### 1. Configure Webhooks in Shopify Admin

1. Go to **Settings > Notifications > Webhooks**
2. Click **Create webhook** for each event:
   - `orders/create`
   - `orders/paid`
   - `orders/fulfilled`
   - `carts/update`
   - `customers/create`

3. Set the webhook URL to:
   - Development: `https://your-ngrok-url.ngrok.io/api/webhooks/shopify`
   - Production: `https://your-domain.com/api/webhooks/shopify`

4. Select **Latest** API version
5. Save the webhook secret provided by Shopify

### 2. Test Webhooks Locally

Use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# Expose port 3000
ngrok http 3000

# Copy the HTTPS URL and use it in Shopify webhook configuration
```

### 3. Test with cURL

```bash
# Generate HMAC signature (use your webhook secret)
echo -n '{"id": "test123"}' | openssl dgst -sha256 -hmac "your_secret" -binary | base64

# Send test webhook
curl -X POST http://localhost:3000/api/webhooks/shopify \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Hmac-Sha256: GENERATED_HMAC_HERE" \
  -H "X-Shopify-Topic: orders/create" \
  -d '{"id": "test123", "email": "test@example.com", "total_price": "100.00"}'
```

## Security

- All webhooks are verified using HMAC-SHA256 signatures
- Invalid signatures return 401 Unauthorized
- Webhook secret should never be committed to version control

## Event Handlers

### handleOrderCreated
- Detects first-time vs repeat customers
- Schedules follow-up emails based on customer history
- TODO: Integrate with email service (SendGrid, Resend, Klaviyo)

### handleOrderPaid
- Logs payment confirmation
- TODO: Send payment confirmation email

### handleOrderFulfilled
- Logs fulfillment status
- TODO: Send shipping notification with tracking info

### handleCartUpdated
- Detects cart abandonment (1+ hour since last update)
- TODO: Send cart recovery email with discount code

### handleCustomerCreated
- Checks if customer accepts marketing
- Generates unique welcome coupon code
- TODO: Send welcome email with discount

## Production Checklist

- [ ] Add webhook secret to environment variables
- [ ] Configure all 5 webhooks in Shopify Admin
- [ ] Integrate with email service provider
- [ ] Set up error monitoring (Sentry, LogRocket)
- [ ] Add retry logic for failed email sends
- [ ] Implement rate limiting
- [ ] Add webhook event logging to database
- [ ] Set up alerts for webhook failures

## Email Service Integration

To enable email automation, integrate with one of these services:

### Option 1: SendGrid
```typescript
import sgMail from '@sendgrid/mail';
sgMail.setApiKey(process.env.SENDGRID_API_KEY!);
```

### Option 2: Resend
```typescript
import { Resend } from 'resend';
const resend = new Resend(process.env.RESEND_API_KEY);
```

### Option 3: Klaviyo (recommended for e-commerce)
```typescript
import { KlaviyoAPI } from 'klaviyo-api';
const klaviyo = new KlaviyoAPI(process.env.KLAVIYO_API_KEY);
```

## Monitoring

Check webhook logs:
```bash
# View recent webhook activity
curl http://localhost:3000/api/webhooks/shopify/logs

# Or check Vercel logs in production
vercel logs
```

## Troubleshooting

### Webhook Not Receiving Events
1. Check that webhook URL is correct in Shopify Admin
2. Verify ngrok is running (for local development)
3. Check firewall settings

### HMAC Verification Fails
1. Verify webhook secret matches Shopify Admin
2. Check that secret is in environment variables
3. Ensure no extra whitespace in secret

### Emails Not Sending
1. Check that email service API key is configured
2. Verify email templates exist
3. Check rate limits on email service

## References
- [Shopify Webhook Documentation](https://shopify.dev/docs/api/admin-rest/latest/resources/webhook)
- [HMAC Verification Guide](https://shopify.dev/docs/apps/webhooks/configuration/https#step-5-verify-the-webhook)
- [PRD Section 4.2](../../../../../../SHOPIFY_PRD.md#42-email-automation)
