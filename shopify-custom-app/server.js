/**
 * NERDX APEC MVP - Shopify Custom App
 * Main Express Server
 */

require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

// Import utilities
const logger = require('./utils/logger');
const { metricsMiddleware, metricsEndpoint } = require('./utils/metrics');

// Import middleware
const errorHandler = require('./middleware/error-handler');
const { authenticate } = require('./middleware/auth');

// Import routes
const webhookRoutes = require('./routes/webhooks');
const arAccessRoutes = require('./routes/ar-access');

// Import services (initialize connections)
const neo4jSyncService = require('./services/neo4j-sync-service');
const notificationService = require('./services/notification-service');

// Configuration
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Initialize Express app
const app = express();

// ===========================
// Security & Middleware Setup
// ===========================

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
}));

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Shopify-Hmac-Sha256', 'X-Shopify-Topic', 'X-Shopify-Shop-Domain'],
  credentials: true,
}));

// Compression
app.use(compression());

// Request logging
if (NODE_ENV === 'production') {
  app.use(morgan('combined', { stream: logger.stream }));
} else {
  app.use(morgan('dev'));
}

// Metrics collection
app.use(metricsMiddleware);

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => {
    // Skip rate limiting for health checks and metrics
    return req.path === '/health' || req.path === '/metrics';
  },
});
app.use(limiter);

// ===========================
// Routes
// ===========================

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    // Check Neo4j connection
    const neo4jHealthy = await neo4jSyncService.healthCheck();

    const health = {
      status: neo4jHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: NODE_ENV,
      services: {
        neo4j: neo4jHealthy ? 'up' : 'down',
        email: notificationService.isConfigured() ? 'configured' : 'not_configured',
      },
      version: process.env.npm_package_version || '1.0.0',
    };

    const statusCode = neo4jHealthy ? 200 : 503;
    res.status(statusCode).json(health);
  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
});

// Readiness probe (for Kubernetes)
app.get('/ready', async (req, res) => {
  try {
    const neo4jHealthy = await neo4jSyncService.healthCheck();
    if (neo4jHealthy) {
      res.status(200).json({ status: 'ready' });
    } else {
      res.status(503).json({ status: 'not_ready', reason: 'neo4j_unavailable' });
    }
  } catch (error) {
    res.status(503).json({ status: 'not_ready', reason: error.message });
  }
});

// Liveness probe (for Kubernetes)
app.get('/live', (req, res) => {
  res.status(200).json({ status: 'alive' });
});

// Metrics endpoint (Prometheus)
app.get('/metrics', metricsEndpoint);

// API routes
app.use('/webhooks', webhookRoutes); // Shopify webhooks (no auth middleware - uses HMAC verification)
app.use('/api/ar-access', authenticate, arAccessRoutes); // AR access API (requires auth)

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'NERDX APEC Shopify Custom App',
    version: process.env.npm_package_version || '1.0.0',
    environment: NODE_ENV,
    status: 'running',
    endpoints: {
      health: '/health',
      ready: '/ready',
      live: '/live',
      metrics: '/metrics',
      webhooks: '/webhooks',
      arAccess: '/api/ar-access',
    },
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`,
    timestamp: new Date().toISOString(),
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// ===========================
// Server Startup
// ===========================

let server;

const startServer = async () => {
  try {
    // Verify Neo4j connection
    logger.info('Connecting to Neo4j...');
    await neo4jSyncService.verifyConnection();
    logger.info('Neo4j connection verified');

    // Verify notification service configuration
    if (notificationService.isConfigured()) {
      logger.info('Email notification service configured');
    } else {
      logger.warn('Email notification service not configured - emails will not be sent');
    }

    // Start Express server
    server = app.listen(PORT, () => {
      logger.info(`NERDX APEC Shopify Custom App started`);
      logger.info(`Environment: ${NODE_ENV}`);
      logger.info(`Server listening on port ${PORT}`);
      logger.info(`Health check: http://localhost:${PORT}/health`);
      logger.info(`Metrics: http://localhost:${PORT}/metrics`);
    });

    // Handle server errors
    server.on('error', (error) => {
      if (error.code === 'EADDRINUSE') {
        logger.error(`Port ${PORT} is already in use`);
      } else {
        logger.error('Server error:', error);
      }
      process.exit(1);
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

// ===========================
// Graceful Shutdown
// ===========================

const gracefulShutdown = async (signal) => {
  logger.info(`${signal} received, starting graceful shutdown...`);

  // Stop accepting new connections
  if (server) {
    server.close(async () => {
      logger.info('HTTP server closed');

      try {
        // Close Neo4j connection
        await neo4jSyncService.close();
        logger.info('Neo4j connection closed');

        // Close notification service
        await notificationService.close();
        logger.info('Notification service closed');

        logger.info('Graceful shutdown completed');
        process.exit(0);
      } catch (error) {
        logger.error('Error during shutdown:', error);
        process.exit(1);
      }
    });

    // Force shutdown after 30 seconds
    setTimeout(() => {
      logger.error('Forced shutdown after timeout');
      process.exit(1);
    }, 30000);
  } else {
    process.exit(0);
  }
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  gracefulShutdown('UNCAUGHT_EXCEPTION');
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  gracefulShutdown('UNHANDLED_REJECTION');
});

// Start the server
if (require.main === module) {
  startServer();
}

// Export for testing
module.exports = app;
