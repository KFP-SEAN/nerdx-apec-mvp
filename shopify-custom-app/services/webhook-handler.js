/**
 * Webhook Handler Service
 * Handles Shopify webhook verification, processing, and routing
 * Implements HMAC-SHA256 verification, idempotency, and retry logic
 */

const crypto = require('crypto');
const logger = require('../utils/logger');
const { recordWebhookMetrics, recordBusinessMetrics } = require('../utils/metrics');
const neo4jSyncService = require('./neo4j-sync-service');
const arAccessService = require('./ar-access-service');
const notificationService = require('./notification-service');
const { ValidationError, ExternalServiceError } = require('../middleware/error-handler');

// Configuration
const SHOPIFY_WEBHOOK_SECRET = process.env.SHOPIFY_WEBHOOK_SECRET;
const ENABLE_IDEMPOTENCY = process.env.ENABLE_IDEMPOTENCY !== 'false';
const MAX_RETRY_ATTEMPTS = parseInt(process.env.MAX_RETRY_ATTEMPTS) || 3;
const RETRY_DELAY_MS = parseInt(process.env.RETRY_DELAY_MS) || 1000;

// In-memory idempotency store (use Redis in production)
const processedWebhooks = new Map();
const IDEMPOTENCY_TTL = 24 * 60 * 60 * 1000; // 24 hours

class WebhookHandler {
  constructor() {
    if (!SHOPIFY_WEBHOOK_SECRET) {
      logger.error('SHOPIFY_WEBHOOK_SECRET not configured');
      throw new Error('SHOPIFY_WEBHOOK_SECRET is required');
    }

    // Cleanup idempotency store periodically
    if (ENABLE_IDEMPOTENCY) {
      setInterval(() => this.cleanupIdempotencyStore(), 60 * 60 * 1000); // Every hour
    }
  }

  /**
   * Verify Shopify webhook signature (HMAC-SHA256)
   */
  verifyWebhookSignature(body, hmacHeader) {
    try {
      if (!hmacHeader) {
        logger.security('Missing HMAC signature header');
        return false;
      }

      // Calculate HMAC
      const hash = crypto
        .createHmac('sha256', SHOPIFY_WEBHOOK_SECRET)
        .update(body, 'utf8')
        .digest('base64');

      // Compare signatures (timing-safe comparison)
      const isValid = crypto.timingSafeEqual(
        Buffer.from(hash),
        Buffer.from(hmacHeader)
      );

      if (!isValid) {
        logger.security('Invalid webhook HMAC signature', {
          expected: hash.substring(0, 10) + '...',
          received: hmacHeader.substring(0, 10) + '...',
        });
      }

      return isValid;

    } catch (error) {
      logger.error('Error verifying webhook signature:', error);
      return false;
    }
  }

  /**
   * Check if webhook has already been processed (idempotency)
   */
  isWebhookProcessed(webhookId) {
    if (!ENABLE_IDEMPOTENCY) {
      return false;
    }

    return processedWebhooks.has(webhookId);
  }

  /**
   * Mark webhook as processed
   */
  markWebhookProcessed(webhookId) {
    if (!ENABLE_IDEMPOTENCY) {
      return;
    }

    processedWebhooks.set(webhookId, {
      timestamp: Date.now(),
      processed: true,
    });
  }

  /**
   * Cleanup expired idempotency records
   */
  cleanupIdempotencyStore() {
    const now = Date.now();
    let cleaned = 0;

    for (const [key, value] of processedWebhooks.entries()) {
      if (now - value.timestamp > IDEMPOTENCY_TTL) {
        processedWebhooks.delete(key);
        cleaned++;
      }
    }

    if (cleaned > 0) {
      logger.info(`Cleaned up ${cleaned} expired idempotency records`);
    }
  }

  /**
   * Extract customer data from Shopify order
   */
  extractCustomerData(order) {
    return {
      userId: order.customer?.id?.toString() || order.email,
      email: order.email || order.customer?.email,
      firstName: order.customer?.first_name || order.billing_address?.first_name,
      lastName: order.customer?.last_name || order.billing_address?.last_name,
      phone: order.customer?.phone || order.billing_address?.phone,
      shopifyCustomerId: order.customer?.id?.toString(),
    };
  }

  /**
   * Extract product data from line items
   */
  extractProductData(lineItems) {
    return lineItems.map(item => ({
      productId: item.product_id?.toString(),
      shopifyProductId: item.product_id?.toString(),
      title: item.title || item.name,
      variantId: item.variant_id?.toString(),
      sku: item.sku,
      price: parseFloat(item.price),
      quantity: item.quantity,
    }));
  }

  /**
   * Process orders/paid webhook
   */
  async processOrderPaid(webhookData) {
    const startTime = Date.now();
    const order = webhookData.data;
    const shop = webhookData.shop;

    try {
      logger.webhook('orders/paid', {
        orderId: order.id,
        orderNumber: order.order_number,
        email: order.email,
        totalPrice: order.total_price,
        shop,
      });

      // Extract customer and product data
      const customerData = this.extractCustomerData(order);
      const products = this.extractProductData(order.line_items);

      // Validate required data
      if (!customerData.email) {
        throw new ValidationError('Order missing customer email');
      }

      if (products.length === 0) {
        throw new ValidationError('Order has no line items');
      }

      // Process each product
      const results = [];

      for (const product of products) {
        try {
          // Create/update user in Neo4j
          await neo4jSyncService.createOrUpdateUser(customerData);

          // Create/update product in Neo4j
          await neo4jSyncService.createOrUpdateProduct(product);

          // Create purchase relationship
          await neo4jSyncService.createPurchaseRelationship({
            email: customerData.email,
            productId: product.productId,
            orderId: order.id.toString(),
            shopifyOrderId: order.id.toString(),
            shopifyOrderNumber: order.order_number,
            purchasedAt: order.created_at,
            amount: product.price * product.quantity,
            currency: order.currency || 'USD',
            quantity: product.quantity,
            status: 'paid',
          });

          // Generate AR access token
          const tokenData = arAccessService.generateToken({
            userId: customerData.userId,
            email: customerData.email,
            productId: product.productId,
            orderId: order.id.toString(),
            productTitle: product.title,
            shopDomain: shop,
            customerId: customerData.shopifyCustomerId,
          });

          // Grant AR access in Neo4j
          await neo4jSyncService.grantARAccess({
            email: customerData.email,
            productId: product.productId,
            orderId: order.id.toString(),
            tokenId: tokenData.tokenId,
            grantedAt: new Date().toISOString(),
            expiresAt: tokenData.expiresAt,
          });

          // Send notification email
          await notificationService.sendARUnlockedEmail(
            {
              email: customerData.email,
              firstName: customerData.firstName,
              lastName: customerData.lastName,
            },
            {
              token: tokenData.token,
              productId: product.productId,
              productTitle: product.title,
              orderId: order.id.toString(),
              expiresAt: tokenData.expiresAt,
            }
          );

          // Record business metrics
          recordBusinessMetrics.purchase(
            product.productId,
            product.price * product.quantity * 100, // Convert to cents
            order.currency || 'USD'
          );

          results.push({
            productId: product.productId,
            success: true,
            tokenId: tokenData.tokenId,
          });

        } catch (error) {
          logger.error(`Failed to process product ${product.productId}:`, error);
          results.push({
            productId: product.productId,
            success: false,
            error: error.message,
          });
        }
      }

      const duration = (Date.now() - startTime) / 1000;
      recordWebhookMetrics.processed('orders/paid', shop, duration);

      logger.webhook('orders/paid processed', {
        orderId: order.id,
        results,
        duration,
      });

      return {
        success: true,
        orderId: order.id,
        results,
      };

    } catch (error) {
      recordWebhookMetrics.failed('orders/paid', shop, error.name);
      logger.error('Failed to process orders/paid webhook:', error);
      throw error;
    }
  }

  /**
   * Process orders/cancelled webhook
   */
  async processOrderCancelled(webhookData) {
    const startTime = Date.now();
    const order = webhookData.data;
    const shop = webhookData.shop;

    try {
      logger.webhook('orders/cancelled', {
        orderId: order.id,
        orderNumber: order.order_number,
        email: order.email,
        shop,
      });

      const customerData = this.extractCustomerData(order);
      const products = this.extractProductData(order.line_items);

      // Update purchase status and revoke AR access
      const results = [];

      for (const product of products) {
        try {
          // Update purchase status
          await neo4jSyncService.updatePurchaseStatus(
            order.id.toString(),
            'cancelled'
          );

          // Revoke AR access
          await neo4jSyncService.revokeARAccess(
            customerData.email,
            product.productId,
            'order_cancelled'
          );

          // Send notification
          await notificationService.sendARRevokedEmail(
            {
              email: customerData.email,
              firstName: customerData.firstName,
            },
            {
              productTitle: product.title,
              orderId: order.id.toString(),
            },
            'cancellation'
          );

          // Record business metrics
          recordBusinessMetrics.cancellation(product.productId);

          results.push({
            productId: product.productId,
            success: true,
          });

        } catch (error) {
          logger.error(`Failed to process cancellation for product ${product.productId}:`, error);
          results.push({
            productId: product.productId,
            success: false,
            error: error.message,
          });
        }
      }

      const duration = (Date.now() - startTime) / 1000;
      recordWebhookMetrics.processed('orders/cancelled', shop, duration);

      return {
        success: true,
        orderId: order.id,
        results,
      };

    } catch (error) {
      recordWebhookMetrics.failed('orders/cancelled', shop, error.name);
      logger.error('Failed to process orders/cancelled webhook:', error);
      throw error;
    }
  }

  /**
   * Process refunds/create webhook
   */
  async processRefundCreate(webhookData) {
    const startTime = Date.now();
    const refund = webhookData.data;
    const shop = webhookData.shop;

    try {
      logger.webhook('refunds/create', {
        refundId: refund.id,
        orderId: refund.order_id,
        shop,
      });

      // Get refunded line items
      const refundedItems = refund.refund_line_items || [];

      if (refundedItems.length === 0) {
        logger.warn('Refund has no line items', { refundId: refund.id });
        return { success: true, message: 'No items to process' };
      }

      // Process each refunded item
      const results = [];

      for (const item of refundedItems) {
        try {
          const productId = item.line_item?.product_id?.toString();
          const email = refund.email; // May need to fetch from order

          if (!productId || !email) {
            logger.warn('Refund item missing required data', {
              refundId: refund.id,
              productId,
              email,
            });
            continue;
          }

          // Revoke AR access
          await neo4jSyncService.revokeARAccess(
            email,
            productId,
            'refund'
          );

          // Send notification
          await notificationService.sendARRevokedEmail(
            { email },
            {
              productTitle: item.line_item?.title,
              orderId: refund.order_id?.toString(),
            },
            'refund'
          );

          // Record business metrics
          recordBusinessMetrics.refund(productId);

          results.push({
            productId,
            success: true,
          });

        } catch (error) {
          logger.error(`Failed to process refund for item:`, error);
          results.push({
            success: false,
            error: error.message,
          });
        }
      }

      const duration = (Date.now() - startTime) / 1000;
      recordWebhookMetrics.processed('refunds/create', shop, duration);

      return {
        success: true,
        refundId: refund.id,
        results,
      };

    } catch (error) {
      recordWebhookMetrics.failed('refunds/create', shop, error.name);
      logger.error('Failed to process refunds/create webhook:', error);
      throw error;
    }
  }

  /**
   * Route webhook to appropriate handler with retry logic
   */
  async handleWebhook(topic, webhookData, attempt = 1) {
    try {
      switch (topic) {
        case 'orders/paid':
          return await this.processOrderPaid(webhookData);

        case 'orders/cancelled':
          return await this.processOrderCancelled(webhookData);

        case 'refunds/create':
          return await this.processRefundCreate(webhookData);

        default:
          logger.warn('Unsupported webhook topic', { topic });
          return {
            success: false,
            message: `Unsupported webhook topic: ${topic}`,
          };
      }

    } catch (error) {
      // Retry logic
      if (attempt < MAX_RETRY_ATTEMPTS) {
        logger.warn(`Webhook processing failed, retrying (${attempt}/${MAX_RETRY_ATTEMPTS})`, {
          topic,
          error: error.message,
        });

        recordWebhookMetrics.retry(topic);

        // Exponential backoff
        const delay = RETRY_DELAY_MS * Math.pow(2, attempt - 1);
        await new Promise(resolve => setTimeout(resolve, delay));

        return this.handleWebhook(topic, webhookData, attempt + 1);
      }

      // Max retries reached - send to Dead Letter Queue
      logger.error('Webhook processing failed after max retries', {
        topic,
        webhookData,
        error: error.message,
      });

      // In production, send to DLQ (SQS, RabbitMQ, etc.)
      this.sendToDeadLetterQueue(topic, webhookData, error);

      throw error;
    }
  }

  /**
   * Send failed webhook to Dead Letter Queue
   */
  sendToDeadLetterQueue(topic, webhookData, error) {
    // TODO: Implement actual DLQ integration (SQS, RabbitMQ, etc.)
    logger.error('Webhook sent to Dead Letter Queue', {
      topic,
      orderId: webhookData.data?.id,
      error: error.message,
      timestamp: new Date().toISOString(),
    });

    // For now, just log to a special file
    // In production, integrate with your queue system
  }

  /**
   * Process webhook with full validation and idempotency
   */
  async processWebhook(req) {
    const topic = req.headers['x-shopify-topic'];
    const shop = req.headers['x-shopify-shop-domain'];
    const hmac = req.headers['x-shopify-hmac-sha256'];
    const webhookId = req.headers['x-shopify-webhook-id'];

    // Record webhook received
    recordWebhookMetrics.received(topic, shop);

    // Verify webhook signature
    const rawBody = req.rawBody || JSON.stringify(req.body);
    if (!this.verifyWebhookSignature(rawBody, hmac)) {
      logger.security('Webhook signature verification failed', {
        topic,
        shop,
      });
      throw new ValidationError('Invalid webhook signature');
    }

    // Check idempotency
    if (webhookId && this.isWebhookProcessed(webhookId)) {
      logger.info('Duplicate webhook ignored', {
        webhookId,
        topic,
        shop,
      });
      return {
        success: true,
        message: 'Webhook already processed',
        duplicate: true,
      };
    }

    // Process webhook
    const result = await this.handleWebhook(topic, {
      data: req.body,
      shop,
      topic,
    });

    // Mark as processed
    if (webhookId) {
      this.markWebhookProcessed(webhookId);
    }

    return result;
  }
}

// Create singleton instance
const webhookHandler = new WebhookHandler();

module.exports = webhookHandler;
