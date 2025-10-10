/**
 * Winston Logger Configuration
 * Centralized logging with file rotation and multiple transports
 */

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const path = require('path');

const LOG_DIR = process.env.LOG_DIR || path.join(__dirname, '..', 'logs');
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';
const NODE_ENV = process.env.NODE_ENV || 'development';

// Define log format
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(meta).length > 0) {
      msg += ` ${JSON.stringify(meta, null, 2)}`;
    }
    return msg;
  })
);

// Create transports
const transports = [];

// Console transport (always enabled)
transports.push(
  new winston.transports.Console({
    format: NODE_ENV === 'production' ? logFormat : consoleFormat,
    level: LOG_LEVEL,
  })
);

// File transports (disabled in test environment)
if (NODE_ENV !== 'test') {
  // Combined log file (all levels)
  transports.push(
    new DailyRotateFile({
      filename: path.join(LOG_DIR, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d',
      format: logFormat,
      level: LOG_LEVEL,
    })
  );

  // Error log file (errors only)
  transports.push(
    new DailyRotateFile({
      filename: path.join(LOG_DIR, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '30d',
      format: logFormat,
      level: 'error',
    })
  );

  // Webhook log file (for audit trail)
  transports.push(
    new DailyRotateFile({
      filename: path.join(LOG_DIR, 'webhook-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '50m',
      maxFiles: '90d',
      format: logFormat,
      level: 'info',
    })
  );
}

// Create logger instance
const logger = winston.createLogger({
  level: LOG_LEVEL,
  format: logFormat,
  defaultMeta: {
    service: 'nerdx-apec-shopify-app',
    environment: NODE_ENV,
  },
  transports,
  exitOnError: false,
});

// Create stream for Morgan HTTP logging
logger.stream = {
  write: (message) => {
    logger.info(message.trim());
  },
};

// Custom logging methods for specific use cases
logger.webhook = (topic, data) => {
  logger.info('Webhook received', {
    category: 'webhook',
    topic,
    data,
  });
};

logger.arAccess = (action, data) => {
  logger.info('AR Access event', {
    category: 'ar_access',
    action,
    data,
  });
};

logger.neo4j = (operation, data) => {
  logger.info('Neo4j operation', {
    category: 'neo4j',
    operation,
    data,
  });
};

logger.notification = (type, data) => {
  logger.info('Notification sent', {
    category: 'notification',
    type,
    data,
  });
};

logger.security = (event, data) => {
  logger.warn('Security event', {
    category: 'security',
    event,
    data,
  });
};

// Log unhandled errors
logger.on('error', (error) => {
  console.error('Logger error:', error);
});

module.exports = logger;
