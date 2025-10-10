const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const orderRoutes = require('./routes/orders');
const arRoutes = require('./routes/ar');
const { logger } = require('./utils/logger');
const { errorHandler, notFoundHandler } = require('./middleware/error-handler');

const app = express();
const PORT = process.env.PORT || 3003;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', limiter);

// Stripe webhook rate limiting (more lenient)
const webhookLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000,
  skip: (req) => req.path !== '/api/webhooks/stripe'
});

app.use('/api/webhooks/', webhookLimiter);

// Body parsing middleware
// NOTE: Stripe webhooks require raw body, so we handle this specially in routes
app.use('/api/webhooks/stripe', express.raw({ type: 'application/json' }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Compression
app.use(compression());

// Logging
app.use(morgan('combined', {
  stream: { write: message => logger.info(message.trim()) }
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'phase3-conversion',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.use('/api/orders', orderRoutes);
app.use('/api/ar', arRoutes);

// Stripe webhook endpoint (handled in orders route)
// /api/webhooks/stripe

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'NerdX APEC MVP - Phase 3: Conversion (Commerce + AR)',
    version: '1.0.0',
    phase: 3,
    features: [
      'Stripe ACP Integration',
      'Order Management',
      'AR Experience Unlocking',
      'APEC Limited Edition Handling',
      'Payment Webhooks'
    ],
    endpoints: {
      health: '/health',
      orders: '/api/orders',
      ar: '/api/ar',
      webhooks: '/api/webhooks/stripe'
    }
  });
});

// Error handling
app.use(notFoundHandler);
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

// Start server
const server = app.listen(PORT, () => {
  logger.info(`Phase 3 Conversion Service running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`Stripe Mode: ${process.env.STRIPE_SECRET_KEY?.startsWith('sk_live') ? 'LIVE' : 'TEST'}`);
});

module.exports = app;
