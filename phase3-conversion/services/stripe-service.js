const Stripe = require('stripe');
const { v4: uuidv4 } = require('uuid');
const { logger } = require('../utils/logger');
const axios = require('axios');

class StripeService {
  constructor() {
    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
    this.webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
    this.phase1ApiUrl = process.env.PHASE1_API_URL || 'http://localhost:3001/api';
  }

  /**
   * Create a Stripe Checkout Session with Advanced Checkout Platform features
   * @param {Object} orderData - Order details
   * @returns {Promise<Object>} Checkout session
   */
  async createCheckoutSession(orderData) {
    try {
      const { userId, productId, quantity = 1, metadata = {} } = orderData;

      // Fetch product details from Phase 1
      const product = await this.fetchProductDetails(productId);

      if (!product) {
        throw new Error(`Product ${productId} not found`);
      }

      // Check APEC limited edition availability
      if (product.isLimitedEdition && product.stock < quantity) {
        throw new Error(`Insufficient stock. Only ${product.stock} items available.`);
      }

      // Create line items
      const lineItems = [{
        price_data: {
          currency: 'usd',
          product_data: {
            name: product.name,
            description: product.description,
            images: product.images || [],
            metadata: {
              productId: product.id,
              isLimitedEdition: product.isLimitedEdition || false,
              apecEdition: product.apecEdition || false,
              arEnabled: product.arEnabled || false
            }
          },
          unit_amount: Math.round(product.price * 100), // Convert to cents
        },
        quantity: quantity,
        adjustable_quantity: {
          enabled: !product.isLimitedEdition, // Disable adjustment for limited editions
          minimum: 1,
          maximum: product.isLimitedEdition ? product.stock : 10
        }
      }];

      // Fetch user details for pre-filling
      const user = await this.fetchUserDetails(userId);

      // Create checkout session with ACP features
      const session = await this.stripe.checkout.sessions.create({
        payment_method_types: ['card', 'alipay', 'wechat_pay'],
        line_items: lineItems,
        mode: 'payment',
        success_url: `${process.env.FRONTEND_URL}/order/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${process.env.FRONTEND_URL}/order/cancelled`,

        // Customer information
        customer_email: user?.email,
        customer_creation: 'always',

        // Metadata for webhook processing
        metadata: {
          userId: userId,
          productId: productId,
          orderId: uuidv4(),
          isLimitedEdition: product.isLimitedEdition || false,
          apecEdition: product.apecEdition || false,
          arEnabled: product.arEnabled || false,
          ...metadata
        },

        // Advanced features
        billing_address_collection: 'required',
        shipping_address_collection: {
          allowed_countries: ['US', 'CA', 'GB', 'AU', 'SG', 'JP', 'CN', 'HK']
        },

        // Tax calculation (if configured)
        automatic_tax: {
          enabled: process.env.STRIPE_TAX_ENABLED === 'true'
        },

        // Shipping options
        shipping_options: [
          {
            shipping_rate_data: {
              type: 'fixed_amount',
              fixed_amount: {
                amount: 1500, // $15.00
                currency: 'usd',
              },
              display_name: 'Standard Shipping',
              delivery_estimate: {
                minimum: {
                  unit: 'business_day',
                  value: 5,
                },
                maximum: {
                  unit: 'business_day',
                  value: 7,
                },
              },
            },
          },
          {
            shipping_rate_data: {
              type: 'fixed_amount',
              fixed_amount: {
                amount: 3500, // $35.00
                currency: 'usd',
              },
              display_name: 'Express Shipping',
              delivery_estimate: {
                minimum: {
                  unit: 'business_day',
                  value: 1,
                },
                maximum: {
                  unit: 'business_day',
                  value: 2,
                },
              },
            },
          },
        ],

        // Allow promotion codes
        allow_promotion_codes: true,

        // Consent collection
        consent_collection: {
          terms_of_service: 'required',
        },

        // Phone number collection for shipping
        phone_number_collection: {
          enabled: true,
        },

        // Payment intent data
        payment_intent_data: {
          description: `NerdX APEC - ${product.name}`,
          metadata: {
            productId: productId,
            userId: userId,
          },
          capture_method: 'automatic',
        },

        // Expires after 30 minutes
        expires_at: Math.floor(Date.now() / 1000) + (30 * 60),
      });

      logger.info(`Checkout session created: ${session.id} for user ${userId}`);

      return {
        sessionId: session.id,
        url: session.url,
        expiresAt: session.expires_at,
      };

    } catch (error) {
      logger.error('Error creating checkout session:', error);
      throw error;
    }
  }

  /**
   * Retrieve checkout session details
   * @param {string} sessionId - Stripe session ID
   * @returns {Promise<Object>} Session details
   */
  async getCheckoutSession(sessionId) {
    try {
      const session = await this.stripe.checkout.sessions.retrieve(sessionId, {
        expand: ['payment_intent', 'customer', 'line_items']
      });

      return session;
    } catch (error) {
      logger.error(`Error retrieving session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Process Stripe webhook events
   * @param {Buffer} rawBody - Raw request body
   * @param {string} signature - Stripe signature header
   * @returns {Promise<Object>} Event data
   */
  async handleWebhook(rawBody, signature) {
    try {
      const event = this.stripe.webhooks.constructEvent(
        rawBody,
        signature,
        this.webhookSecret
      );

      logger.info(`Webhook received: ${event.type}`);

      switch (event.type) {
        case 'checkout.session.completed':
          await this.handleCheckoutCompleted(event.data.object);
          break;

        case 'payment_intent.succeeded':
          await this.handlePaymentSucceeded(event.data.object);
          break;

        case 'payment_intent.payment_failed':
          await this.handlePaymentFailed(event.data.object);
          break;

        case 'charge.refunded':
          await this.handleRefund(event.data.object);
          break;

        case 'customer.created':
          logger.info(`Customer created: ${event.data.object.id}`);
          break;

        default:
          logger.info(`Unhandled event type: ${event.type}`);
      }

      return { received: true, type: event.type };

    } catch (error) {
      logger.error('Webhook error:', error);
      throw error;
    }
  }

  /**
   * Handle successful checkout completion
   * @param {Object} session - Checkout session object
   */
  async handleCheckoutCompleted(session) {
    try {
      logger.info(`Checkout completed: ${session.id}`);

      const { userId, productId, orderId, arEnabled } = session.metadata;

      // Update order status
      // In production, this would update your database
      logger.info(`Order ${orderId} completed for user ${userId}`);

      // Unlock AR experience if applicable
      if (arEnabled === 'true' || arEnabled === true) {
        await this.unlockARExperience(userId, productId, orderId);
      }

      // Send confirmation email (integration point)
      await this.sendOrderConfirmation(session);

    } catch (error) {
      logger.error('Error handling checkout completion:', error);
      throw error;
    }
  }

  /**
   * Handle successful payment
   * @param {Object} paymentIntent - Payment intent object
   */
  async handlePaymentSucceeded(paymentIntent) {
    logger.info(`Payment succeeded: ${paymentIntent.id}`);

    // Additional payment processing logic
    // Update inventory, trigger fulfillment, etc.
  }

  /**
   * Handle failed payment
   * @param {Object} paymentIntent - Payment intent object
   */
  async handlePaymentFailed(paymentIntent) {
    logger.error(`Payment failed: ${paymentIntent.id}`);

    // Notify user, retry logic, etc.
  }

  /**
   * Handle refund
   * @param {Object} charge - Charge object
   */
  async handleRefund(charge) {
    logger.info(`Refund processed: ${charge.id}`);

    // Revoke AR access, update order status, etc.
  }

  /**
   * Unlock AR experience after purchase
   * @param {string} userId - User ID
   * @param {string} productId - Product ID
   * @param {string} orderId - Order ID
   */
  async unlockARExperience(userId, productId, orderId) {
    try {
      // Call AR service to unlock experience
      const arServiceUrl = process.env.AR_SERVICE_URL || 'http://localhost:3003/api/ar';

      await axios.post(`${arServiceUrl}/unlock`, {
        userId,
        productId,
        orderId,
        unlockedAt: new Date().toISOString()
      });

      logger.info(`AR experience unlocked for user ${userId}, product ${productId}`);
    } catch (error) {
      logger.error('Error unlocking AR experience:', error);
      // Don't throw - AR unlock failure shouldn't break payment processing
    }
  }

  /**
   * Send order confirmation
   * @param {Object} session - Checkout session
   */
  async sendOrderConfirmation(session) {
    try {
      // Integration point for email service
      logger.info(`Sending order confirmation for session ${session.id}`);

      // Example: Call email service
      // await emailService.sendOrderConfirmation(session);

    } catch (error) {
      logger.error('Error sending order confirmation:', error);
    }
  }

  /**
   * Fetch product details from Phase 1
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Product details
   */
  async fetchProductDetails(productId) {
    try {
      const response = await axios.get(`${this.phase1ApiUrl}/products/${productId}`);
      return response.data;
    } catch (error) {
      logger.error(`Error fetching product ${productId}:`, error.message);
      return null;
    }
  }

  /**
   * Fetch user details from Phase 1
   * @param {string} userId - User ID
   * @returns {Promise<Object>} User details
   */
  async fetchUserDetails(userId) {
    try {
      const response = await axios.get(`${this.phase1ApiUrl}/users/${userId}`);
      return response.data;
    } catch (error) {
      logger.error(`Error fetching user ${userId}:`, error.message);
      return null;
    }
  }

  /**
   * Create a refund
   * @param {string} paymentIntentId - Payment intent ID
   * @param {number} amount - Amount to refund (optional, full refund if not specified)
   * @returns {Promise<Object>} Refund object
   */
  async createRefund(paymentIntentId, amount = null) {
    try {
      const refundData = {
        payment_intent: paymentIntentId
      };

      if (amount) {
        refundData.amount = Math.round(amount * 100); // Convert to cents
      }

      const refund = await this.stripe.refunds.create(refundData);

      logger.info(`Refund created: ${refund.id} for payment ${paymentIntentId}`);

      return refund;
    } catch (error) {
      logger.error('Error creating refund:', error);
      throw error;
    }
  }
}

module.exports = new StripeService();
