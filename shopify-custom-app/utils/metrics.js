/**
 * Prometheus Metrics Configuration
 * Track application performance and business metrics
 */

const client = require('prom-client');
const logger = require('./logger');

// Enable default metrics (CPU, memory, etc.)
const register = new client.Registry();
client.collectDefaultMetrics({ register });

// ===========================
// HTTP Metrics
// ===========================

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5, 10],
  registers: [register],
});

const httpRequestTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register],
});

// ===========================
// Webhook Metrics
// ===========================

const webhookReceived = new client.Counter({
  name: 'shopify_webhook_received_total',
  help: 'Total number of Shopify webhooks received',
  labelNames: ['topic', 'shop'],
  registers: [register],
});

const webhookProcessed = new client.Counter({
  name: 'shopify_webhook_processed_total',
  help: 'Total number of Shopify webhooks successfully processed',
  labelNames: ['topic', 'shop'],
  registers: [register],
});

const webhookFailed = new client.Counter({
  name: 'shopify_webhook_failed_total',
  help: 'Total number of Shopify webhooks that failed processing',
  labelNames: ['topic', 'shop', 'error_type'],
  registers: [register],
});

const webhookProcessingDuration = new client.Histogram({
  name: 'shopify_webhook_processing_duration_seconds',
  help: 'Duration of webhook processing in seconds',
  labelNames: ['topic'],
  buckets: [0.5, 1, 2, 5, 10, 30],
  registers: [register],
});

const webhookRetries = new client.Counter({
  name: 'shopify_webhook_retries_total',
  help: 'Total number of webhook retry attempts',
  labelNames: ['topic'],
  registers: [register],
});

// ===========================
// AR Access Metrics
// ===========================

const arTokensGenerated = new client.Counter({
  name: 'ar_tokens_generated_total',
  help: 'Total number of AR access tokens generated',
  labelNames: ['product_id'],
  registers: [register],
});

const arTokensValidated = new client.Counter({
  name: 'ar_tokens_validated_total',
  help: 'Total number of AR token validation attempts',
  labelNames: ['valid'],
  registers: [register],
});

const arAccessGranted = new client.Counter({
  name: 'ar_access_granted_total',
  help: 'Total number of AR access grants',
  labelNames: ['product_id', 'user_id'],
  registers: [register],
});

const arAccessRevoked = new client.Counter({
  name: 'ar_access_revoked_total',
  help: 'Total number of AR access revocations',
  labelNames: ['product_id', 'user_id', 'reason'],
  registers: [register],
});

// ===========================
// Neo4j Metrics
// ===========================

const neo4jOperations = new client.Counter({
  name: 'neo4j_operations_total',
  help: 'Total number of Neo4j operations',
  labelNames: ['operation', 'status'],
  registers: [register],
});

const neo4jQueryDuration = new client.Histogram({
  name: 'neo4j_query_duration_seconds',
  help: 'Duration of Neo4j queries in seconds',
  labelNames: ['operation'],
  buckets: [0.1, 0.5, 1, 2, 5],
  registers: [register],
});

const neo4jConnectionPool = new client.Gauge({
  name: 'neo4j_connection_pool_size',
  help: 'Current size of Neo4j connection pool',
  registers: [register],
});

// ===========================
// Notification Metrics
// ===========================

const notificationsSent = new client.Counter({
  name: 'notifications_sent_total',
  help: 'Total number of notifications sent',
  labelNames: ['type', 'status'],
  registers: [register],
});

const notificationDuration = new client.Histogram({
  name: 'notification_duration_seconds',
  help: 'Duration of notification sending in seconds',
  labelNames: ['type'],
  buckets: [0.5, 1, 2, 5, 10],
  registers: [register],
});

// ===========================
// Business Metrics
// ===========================

const purchasesProcessed = new client.Counter({
  name: 'purchases_processed_total',
  help: 'Total number of purchases processed',
  labelNames: ['product_id'],
  registers: [register],
});

const refundsProcessed = new client.Counter({
  name: 'refunds_processed_total',
  help: 'Total number of refunds processed',
  labelNames: ['product_id'],
  registers: [register],
});

const ordersCancelled = new client.Counter({
  name: 'orders_cancelled_total',
  help: 'Total number of cancelled orders processed',
  labelNames: ['product_id'],
  registers: [register],
});

const revenueTracked = new client.Counter({
  name: 'revenue_tracked_total',
  help: 'Total revenue tracked in cents',
  labelNames: ['currency', 'product_id'],
  registers: [register],
});

// ===========================
// Error Metrics
// ===========================

const errors = new client.Counter({
  name: 'errors_total',
  help: 'Total number of errors',
  labelNames: ['type', 'severity'],
  registers: [register],
});

const apiErrors = new client.Counter({
  name: 'api_errors_total',
  help: 'Total number of API errors',
  labelNames: ['endpoint', 'status_code'],
  registers: [register],
});

// ===========================
// Middleware
// ===========================

/**
 * Express middleware to track HTTP metrics
 */
const metricsMiddleware = (req, res, next) => {
  const start = Date.now();

  // Track response
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path || 'unknown';
    const method = req.method;
    const statusCode = res.statusCode;

    // Record metrics
    httpRequestDuration.labels(method, route, statusCode).observe(duration);
    httpRequestTotal.labels(method, route, statusCode).inc();

    // Track API errors
    if (statusCode >= 400) {
      apiErrors.labels(route, statusCode).inc();
    }
  });

  next();
};

/**
 * Metrics endpoint handler
 */
const metricsEndpoint = async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    const metrics = await register.metrics();
    res.end(metrics);
  } catch (error) {
    logger.error('Error generating metrics:', error);
    res.status(500).end();
  }
};

// ===========================
// Helper Functions
// ===========================

/**
 * Record webhook metrics
 */
const recordWebhookMetrics = {
  received: (topic, shop) => {
    webhookReceived.labels(topic, shop).inc();
  },

  processed: (topic, shop, duration) => {
    webhookProcessed.labels(topic, shop).inc();
    webhookProcessingDuration.labels(topic).observe(duration);
  },

  failed: (topic, shop, errorType) => {
    webhookFailed.labels(topic, shop, errorType).inc();
  },

  retry: (topic) => {
    webhookRetries.labels(topic).inc();
  },
};

/**
 * Record AR access metrics
 */
const recordARMetrics = {
  tokenGenerated: (productId) => {
    arTokensGenerated.labels(productId).inc();
  },

  tokenValidated: (valid) => {
    arTokensValidated.labels(valid.toString()).inc();
  },

  accessGranted: (productId, userId) => {
    arAccessGranted.labels(productId, userId).inc();
  },

  accessRevoked: (productId, userId, reason) => {
    arAccessRevoked.labels(productId, userId, reason).inc();
  },
};

/**
 * Record Neo4j metrics
 */
const recordNeo4jMetrics = {
  operation: (operation, status) => {
    neo4jOperations.labels(operation, status).inc();
  },

  queryDuration: (operation, duration) => {
    neo4jQueryDuration.labels(operation).observe(duration);
  },

  connectionPool: (size) => {
    neo4jConnectionPool.set(size);
  },
};

/**
 * Record notification metrics
 */
const recordNotificationMetrics = {
  sent: (type, status, duration) => {
    notificationsSent.labels(type, status).inc();
    notificationDuration.labels(type).observe(duration);
  },
};

/**
 * Record business metrics
 */
const recordBusinessMetrics = {
  purchase: (productId, amount, currency) => {
    purchasesProcessed.labels(productId).inc();
    if (amount && currency) {
      revenueTracked.labels(currency, productId).inc(amount);
    }
  },

  refund: (productId) => {
    refundsProcessed.labels(productId).inc();
  },

  cancellation: (productId) => {
    ordersCancelled.labels(productId).inc();
  },
};

/**
 * Record error metrics
 */
const recordError = (type, severity = 'error') => {
  errors.labels(type, severity).inc();
};

// ===========================
// Exports
// ===========================

module.exports = {
  register,
  metricsMiddleware,
  metricsEndpoint,
  recordWebhookMetrics,
  recordARMetrics,
  recordNeo4jMetrics,
  recordNotificationMetrics,
  recordBusinessMetrics,
  recordError,
};
