import { NextRequest, NextResponse } from 'next/server';
import { createHmac } from 'crypto';

/**
 * Shopify Webhook Handler
 * Receives and processes Shopify events for:
 * - orders/create
 * - orders/paid
 * - orders/fulfilled
 * - carts/update (for abandonment detection)
 * - customers/create
 */
export async function POST(req: NextRequest) {
  try {
    // Get request body and headers
    const body = await req.text();
    const hmac = req.headers.get('x-shopify-hmac-sha256');
    const topic = req.headers.get('x-shopify-topic');

    console.log(`[Webhook] Received ${topic} event`);

    // Verify HMAC signature
    if (!verifyWebhook(body, hmac)) {
      console.error('[Webhook] Invalid HMAC signature');
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 401 }
      );
    }

    // Parse webhook data
    const data = JSON.parse(body);

    // Route to appropriate handler based on event type
    switch (topic) {
      case 'orders/create':
        await handleOrderCreated(data);
        break;

      case 'orders/paid':
        await handleOrderPaid(data);
        break;

      case 'orders/fulfilled':
        await handleOrderFulfilled(data);
        break;

      case 'carts/update':
        await handleCartUpdated(data);
        break;

      case 'customers/create':
        await handleCustomerCreated(data);
        break;

      default:
        console.log(`[Webhook] Unhandled topic: ${topic}`);
    }

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error) {
    console.error('[Webhook] Error processing webhook:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

/**
 * Verify webhook HMAC signature
 * Uses SHOPIFY_WEBHOOK_SECRET (or SHOPIFY_ADMIN_API_TOKEN as fallback)
 */
function verifyWebhook(body: string, hmac: string | null): boolean {
  if (!hmac) {
    console.warn('[Webhook] No HMAC header provided');
    return false;
  }

  // Use SHOPIFY_WEBHOOK_SECRET if available, fallback to SHOPIFY_ADMIN_API_TOKEN
  const secret = process.env.SHOPIFY_WEBHOOK_SECRET || process.env.SHOPIFY_ADMIN_API_TOKEN;

  if (!secret) {
    console.error('[Webhook] No webhook secret configured');
    return false;
  }

  const hash = createHmac('sha256', secret)
    .update(body, 'utf8')
    .digest('base64');

  return hash === hmac;
}

/**
 * Handle order creation event
 * Triggered when a customer completes checkout
 */
async function handleOrderCreated(order: any) {
  try {
    console.log(`[Webhook] Order created: #${order.order_number || order.id}`);
    console.log(`[Webhook] Customer email: ${order.email}`);
    console.log(`[Webhook] Total: ${order.total_price} ${order.currency}`);

    const email = order.email;
    const isFirstOrder = order.customer?.orders_count === 1;

    if (isFirstOrder) {
      // TODO: Schedule first purchase follow-up email (3 days after purchase)
      console.log(`[Email] First purchase - scheduling follow-up for ${email}`);
      console.log(`[Email] Order ID: ${order.id}`);
      console.log(`[Email] Order Date: ${order.created_at}`);

      // TODO: Integrate with email service (e.g., SendGrid, Resend, Klaviyo)
      // await emailService.sendFirstPurchaseFollowUp({
      //   email,
      //   orderId: order.id,
      //   orderDate: order.created_at,
      //   products: order.line_items.map((item: any) => item.title)
      // });
    } else {
      // TODO: Schedule repurchase email (30 days after purchase)
      console.log(`[Email] Repeat customer - scheduling repurchase reminder for ${email}`);
      console.log(`[Email] Last Order Date: ${order.created_at}`);
      console.log(`[Email] Products: ${order.line_items.map((item: any) => item.title).join(', ')}`);

      // TODO: Integrate with email service
      // await emailService.sendRepurchaseEmail({
      //   email,
      //   lastOrderDate: order.created_at,
      //   lastOrderProducts: order.line_items.map((item: any) => item.title)
      // });
    }
  } catch (error) {
    console.error('[Webhook] Error handling order created:', error);
    throw error;
  }
}

/**
 * Handle order paid event
 * Triggered when payment is confirmed for an order
 */
async function handleOrderPaid(order: any) {
  try {
    console.log(`[Webhook] Order paid: #${order.order_number || order.id}`);
    console.log(`[Webhook] Payment status: ${order.financial_status}`);

    // TODO: Send payment confirmation email
    console.log(`[Email] Sending payment confirmation to ${order.email}`);

    // TODO: Integrate with email service
    // await emailService.sendPaymentConfirmation({
    //   email: order.email,
    //   orderNumber: order.order_number,
    //   total: order.total_price,
    //   currency: order.currency
    // });
  } catch (error) {
    console.error('[Webhook] Error handling order paid:', error);
    throw error;
  }
}

/**
 * Handle order fulfilled event
 * Triggered when an order is fulfilled/shipped
 */
async function handleOrderFulfilled(order: any) {
  try {
    console.log(`[Webhook] Order fulfilled: #${order.order_number || order.id}`);
    console.log(`[Webhook] Fulfillment status: ${order.fulfillment_status}`);

    // TODO: Send shipping notification email
    console.log(`[Email] Sending shipping notification to ${order.email}`);

    // TODO: Integrate with email service
    // await emailService.sendShippingNotification({
    //   email: order.email,
    //   orderNumber: order.order_number,
    //   trackingNumber: order.fulfillments?.[0]?.tracking_number,
    //   trackingUrl: order.fulfillments?.[0]?.tracking_url
    // });
  } catch (error) {
    console.error('[Webhook] Error handling order fulfilled:', error);
    throw error;
  }
}

/**
 * Handle cart update event
 * Used for cart abandonment detection
 */
async function handleCartUpdated(cart: any) {
  try {
    console.log(`[Webhook] Cart updated: ${cart.id}`);
    console.log(`[Webhook] Cart items: ${cart.line_items?.length || 0}`);
    console.log(`[Webhook] Last updated: ${cart.updated_at}`);

    // Cart abandonment detection logic
    const lastUpdated = new Date(cart.updated_at);
    const now = new Date();
    const hoursSinceUpdate = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);

    // Check if cart has been abandoned (1+ hour since last update and has items)
    if (hoursSinceUpdate >= 1 && cart.line_items && cart.line_items.length > 0) {
      console.log(`[Email] Cart abandoned - sending recovery email to ${cart.email}`);
      console.log(`[Email] Hours since update: ${hoursSinceUpdate.toFixed(2)}`);
      console.log(`[Email] Cart total: ${cart.total_price}`);

      // TODO: Send cart abandonment recovery email
      // TODO: Integrate with email service
      // await emailService.sendCartAbandonmentEmail({
      //   email: cart.email,
      //   cartId: cart.id,
      //   items: cart.line_items,
      //   totalPrice: parseFloat(cart.total_price),
      //   recoveryUrl: `${process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN}/cart/${cart.token}`
      // });
    } else {
      console.log(`[Webhook] Cart not abandoned yet (${hoursSinceUpdate.toFixed(2)} hours since update)`);
    }
  } catch (error) {
    console.error('[Webhook] Error handling cart updated:', error);
    throw error;
  }
}

/**
 * Handle customer creation event
 * Triggered when a new customer account is created or newsletter signup
 */
async function handleCustomerCreated(customer: any) {
  try {
    console.log(`[Webhook] Customer created: ${customer.email}`);
    console.log(`[Webhook] Accepts marketing: ${customer.accepts_marketing}`);
    console.log(`[Webhook] Name: ${customer.first_name} ${customer.last_name}`);

    // Check if customer opted in for marketing emails
    if (customer.accepts_marketing) {
      console.log(`[Email] Sending welcome email to ${customer.email}`);

      // Generate unique coupon code for welcome offer
      const couponCode = `WELCOME15-${generateUniqueCode()}`;
      console.log(`[Email] Welcome coupon: ${couponCode}`);

      // TODO: Send welcome email with discount coupon
      // TODO: Integrate with email service
      // await emailService.sendWelcomeEmail({
      //   email: customer.email,
      //   firstName: customer.first_name,
      //   couponCode: couponCode
      // });
    } else {
      console.log(`[Webhook] Customer opted out of marketing emails`);
    }
  } catch (error) {
    console.error('[Webhook] Error handling customer created:', error);
    throw error;
  }
}

/**
 * Generate unique code for coupons
 * Returns 8-character alphanumeric code
 */
function generateUniqueCode(): string {
  return Math.random().toString(36).substring(2, 10).toUpperCase();
}
