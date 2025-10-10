/**
 * Webhook Routes
 * Handles Shopify webhook endpoints
 */

const express = require('express');
const router = express.Router();
const webhookHandler = require('../services/webhook-handler');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/error-handler');

/**
 * Middleware to capture raw body for webhook verification
 * This must be applied before express.json() middleware
 */
router.use(express.json({
  verify: (req, res, buf, encoding) => {
    // Store raw body for HMAC verification
    req.rawBody = buf.toString(encoding || 'utf8');
  },
}));

/**
 * POST /webhooks/orders/paid
 * Handle order paid webhook
 */
router.post('/orders/paid', asyncHandler(async (req, res) => {
  logger.info('Received orders/paid webhook', {
    orderId: req.body?.id,
    shop: req.headers['x-shopify-shop-domain'],
  });

  const result = await webhookHandler.processWebhook(req);

  res.status(200).json({
    success: true,
    message: 'Webhook processed successfully',
    ...result,
  });
}));

/**
 * POST /webhooks/orders/cancelled
 * Handle order cancelled webhook
 */
router.post('/orders/cancelled', asyncHandler(async (req, res) => {
  logger.info('Received orders/cancelled webhook', {
    orderId: req.body?.id,
    shop: req.headers['x-shopify-shop-domain'],
  });

  const result = await webhookHandler.processWebhook(req);

  res.status(200).json({
    success: true,
    message: 'Webhook processed successfully',
    ...result,
  });
}));

/**
 * POST /webhooks/refunds/create
 * Handle refund created webhook
 */
router.post('/refunds/create', asyncHandler(async (req, res) => {
  logger.info('Received refunds/create webhook', {
    refundId: req.body?.id,
    orderId: req.body?.order_id,
    shop: req.headers['x-shopify-shop-domain'],
  });

  const result = await webhookHandler.processWebhook(req);

  res.status(200).json({
    success: true,
    message: 'Webhook processed successfully',
    ...result,
  });
}));

/**
 * POST /webhooks/test
 * Test endpoint for webhook verification (responds to Shopify webhook creation)
 */
router.post('/test', (req, res) => {
  logger.info('Received webhook test', {
    topic: req.headers['x-shopify-topic'],
    shop: req.headers['x-shopify-shop-domain'],
  });

  res.status(200).json({
    success: true,
    message: 'Webhook test received',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /webhooks/health
 * Health check for webhook service
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'webhooks',
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
