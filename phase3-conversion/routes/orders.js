const express = require('express');
const { body, param, validationResult } = require('express-validator');
const stripeService = require('../services/stripe-service');
const { logger } = require('../utils/logger');

const router = express.Router();

/**
 * Validation middleware
 */
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      errors: errors.array()
    });
  }
  next();
};

/**
 * Create checkout session
 * POST /api/orders/checkout
 */
router.post('/checkout',
  [
    body('userId').notEmpty().withMessage('User ID is required'),
    body('productId').notEmpty().withMessage('Product ID is required'),
    body('quantity').optional().isInt({ min: 1, max: 10 }).withMessage('Quantity must be between 1 and 10'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId, productId, quantity, metadata } = req.body;

      logger.info(`Creating checkout session for user ${userId}, product ${productId}`);

      const session = await stripeService.createCheckoutSession({
        userId,
        productId,
        quantity: quantity || 1,
        metadata: metadata || {}
      });

      res.status(200).json({
        success: true,
        session: {
          sessionId: session.sessionId,
          url: session.url,
          expiresAt: session.expiresAt
        }
      });

    } catch (error) {
      logger.error('Error creating checkout session:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to create checkout session'
      });
    }
  }
);

/**
 * Get checkout session details
 * GET /api/orders/session/:sessionId
 */
router.get('/session/:sessionId',
  [
    param('sessionId').notEmpty().withMessage('Session ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { sessionId } = req.params;

      logger.info(`Retrieving session ${sessionId}`);

      const session = await stripeService.getCheckoutSession(sessionId);

      // Extract relevant information
      const sessionData = {
        id: session.id,
        status: session.status,
        paymentStatus: session.payment_status,
        amountTotal: session.amount_total / 100, // Convert from cents
        currency: session.currency,
        customer: session.customer,
        metadata: session.metadata,
        created: new Date(session.created * 1000).toISOString(),
        expiresAt: new Date(session.expires_at * 1000).toISOString()
      };

      // If payment succeeded, include order details
      if (session.payment_status === 'paid') {
        sessionData.order = {
          orderId: session.metadata.orderId,
          userId: session.metadata.userId,
          productId: session.metadata.productId,
          arEnabled: session.metadata.arEnabled
        };
      }

      res.status(200).json({
        success: true,
        session: sessionData
      });

    } catch (error) {
      logger.error('Error retrieving session:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to retrieve session'
      });
    }
  }
);

/**
 * Get order details by order ID
 * GET /api/orders/:orderId
 */
router.get('/:orderId',
  [
    param('orderId').isUUID().withMessage('Invalid order ID format'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { orderId } = req.params;

      logger.info(`Retrieving order ${orderId}`);

      // In production, fetch from database
      // For now, return mock data
      const order = {
        orderId: orderId,
        status: 'completed',
        userId: 'user-123',
        productId: 'prod-456',
        quantity: 1,
        total: 299.99,
        currency: 'usd',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        shipping: {
          address: 'Sample Address',
          status: 'pending'
        },
        arUnlocked: true
      };

      res.status(200).json({
        success: true,
        order
      });

    } catch (error) {
      logger.error('Error retrieving order:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to retrieve order'
      });
    }
  }
);

/**
 * Get all orders for a user
 * GET /api/orders/user/:userId
 */
router.get('/user/:userId',
  [
    param('userId').notEmpty().withMessage('User ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId } = req.params;

      logger.info(`Retrieving orders for user ${userId}`);

      // In production, fetch from database
      // For now, return mock data
      const orders = [
        {
          orderId: 'order-1',
          productId: 'apec-limited-001',
          productName: 'APEC 2024 Limited Edition Tee',
          quantity: 1,
          total: 299.99,
          status: 'completed',
          arUnlocked: true,
          createdAt: new Date().toISOString()
        }
      ];

      res.status(200).json({
        success: true,
        count: orders.length,
        orders
      });

    } catch (error) {
      logger.error('Error retrieving user orders:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to retrieve orders'
      });
    }
  }
);

/**
 * Request refund
 * POST /api/orders/:orderId/refund
 */
router.post('/:orderId/refund',
  [
    param('orderId').isUUID().withMessage('Invalid order ID format'),
    body('reason').optional().isString().withMessage('Reason must be a string'),
    body('amount').optional().isFloat({ min: 0 }).withMessage('Amount must be a positive number'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { orderId } = req.params;
      const { reason, amount } = req.body;

      logger.info(`Processing refund for order ${orderId}`);

      // In production, fetch payment intent ID from database
      const paymentIntentId = 'pi_example'; // Placeholder

      const refund = await stripeService.createRefund(paymentIntentId, amount);

      res.status(200).json({
        success: true,
        refund: {
          id: refund.id,
          amount: refund.amount / 100,
          currency: refund.currency,
          status: refund.status,
          reason: reason || 'requested_by_customer'
        }
      });

    } catch (error) {
      logger.error('Error processing refund:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to process refund'
      });
    }
  }
);

/**
 * Stripe webhook endpoint
 * POST /api/webhooks/stripe
 *
 * NOTE: This endpoint receives raw body (configured in server.js)
 */
router.post('/webhooks/stripe', async (req, res) => {
  try {
    const signature = req.headers['stripe-signature'];

    if (!signature) {
      logger.error('Missing Stripe signature header');
      return res.status(400).json({
        success: false,
        error: 'Missing signature'
      });
    }

    // Process webhook with raw body
    const result = await stripeService.handleWebhook(req.body, signature);

    logger.info(`Webhook processed: ${result.type}`);

    res.status(200).json({
      success: true,
      received: true
    });

  } catch (error) {
    logger.error('Webhook error:', error);

    // Return 400 for webhook signature verification failures
    if (error.message.includes('signature')) {
      return res.status(400).json({
        success: false,
        error: 'Webhook signature verification failed'
      });
    }

    res.status(500).json({
      success: false,
      error: 'Webhook processing failed'
    });
  }
});

module.exports = router;
