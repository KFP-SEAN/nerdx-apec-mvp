/**
 * Global Error Handler Middleware
 * Centralized error handling with logging and metrics
 */

const logger = require('../utils/logger');
const { recordError } = require('../utils/metrics');

/**
 * Custom Application Error Classes
 */
class AppError extends Error {
  constructor(message, statusCode = 500, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.timestamp = new Date().toISOString();
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message, details = null) {
    super(message, 400);
    this.name = 'ValidationError';
    this.details = details;
  }
}

class AuthenticationError extends AppError {
  constructor(message = 'Authentication failed') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

class AuthorizationError extends AppError {
  constructor(message = 'Insufficient permissions') {
    super(message, 403);
    this.name = 'AuthorizationError';
  }
}

class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404);
    this.name = 'NotFoundError';
  }
}

class ConflictError extends AppError {
  constructor(message = 'Resource conflict') {
    super(message, 409);
    this.name = 'ConflictError';
  }
}

class RateLimitError extends AppError {
  constructor(message = 'Too many requests') {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

class ExternalServiceError extends AppError {
  constructor(service, originalError = null) {
    super(`External service error: ${service}`, 502);
    this.name = 'ExternalServiceError';
    this.service = service;
    this.originalError = originalError;
  }
}

class DatabaseError extends AppError {
  constructor(operation, originalError = null) {
    super(`Database error during ${operation}`, 500);
    this.name = 'DatabaseError';
    this.operation = operation;
    this.originalError = originalError;
  }
}

/**
 * Error Handler Middleware
 */
const errorHandler = (err, req, res, next) => {
  // Default error properties
  let error = err;

  // Convert non-AppError errors to AppError
  if (!(err instanceof AppError)) {
    error = new AppError(
      err.message || 'Internal Server Error',
      err.statusCode || 500,
      false // Non-operational error
    );
    error.stack = err.stack;
  }

  // Determine severity level
  const severity = error.statusCode >= 500 ? 'error' : 'warning';

  // Log error
  const errorLog = {
    name: error.name,
    message: error.message,
    statusCode: error.statusCode,
    isOperational: error.isOperational,
    timestamp: error.timestamp,
    path: req.path,
    method: req.method,
    ip: req.ip,
    userId: req.auth?.userId,
    headers: {
      'user-agent': req.headers['user-agent'],
      'x-shopify-topic': req.headers['x-shopify-topic'],
      'x-shopify-shop-domain': req.headers['x-shopify-shop-domain'],
    },
  };

  // Add stack trace for server errors
  if (error.statusCode >= 500) {
    errorLog.stack = error.stack;
  }

  // Add error details if available
  if (error.details) {
    errorLog.details = error.details;
  }

  // Add original error for wrapped errors
  if (error.originalError) {
    errorLog.originalError = {
      message: error.originalError.message,
      stack: error.originalError.stack,
    };
  }

  // Log the error
  logger.error('Request error:', errorLog);

  // Record metrics
  recordError(error.name || 'UnknownError', severity);

  // Prepare response
  const response = {
    error: error.name || 'Error',
    message: error.message,
    statusCode: error.statusCode,
    timestamp: error.timestamp,
  };

  // Add request ID if available
  if (req.id) {
    response.requestId = req.id;
  }

  // Add validation details in development
  if (process.env.NODE_ENV === 'development' && error.details) {
    response.details = error.details;
  }

  // Add stack trace in development
  if (process.env.NODE_ENV === 'development' && error.stack) {
    response.stack = error.stack;
  }

  // Send response
  res.status(error.statusCode).json(response);

  // For non-operational errors, consider shutting down
  if (!error.isOperational) {
    logger.error('Non-operational error detected. Consider restarting the service.');
    // In production, you might want to trigger alerts or implement graceful shutdown
    // process.exit(1);
  }
};

/**
 * Async Route Handler Wrapper
 * Catches async errors and passes them to error handler
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * 404 Not Found Handler
 */
const notFoundHandler = (req, res, next) => {
  const error = new NotFoundError(`Route ${req.method} ${req.path}`);
  next(error);
};

/**
 * Validation Error Handler
 * Converts Joi validation errors to ValidationError
 */
const handleValidationError = (error) => {
  if (error.isJoi) {
    const details = error.details.map(detail => ({
      field: detail.path.join('.'),
      message: detail.message,
      type: detail.type,
    }));

    return new ValidationError('Validation failed', details);
  }
  return error;
};

/**
 * Database Error Handler
 * Converts Neo4j errors to DatabaseError
 */
const handleDatabaseError = (error, operation = 'unknown') => {
  if (error.code && error.code.startsWith('Neo')) {
    return new DatabaseError(operation, error);
  }
  return error;
};

/**
 * External Service Error Handler
 * Converts external API errors to ExternalServiceError
 */
const handleExternalServiceError = (error, service) => {
  if (error.response || error.request) {
    return new ExternalServiceError(service, error);
  }
  return error;
};

/**
 * JWT Error Handler
 * Converts JWT errors to AuthenticationError
 */
const handleJWTError = (error) => {
  if (error.name === 'JsonWebTokenError') {
    return new AuthenticationError('Invalid token');
  }
  if (error.name === 'TokenExpiredError') {
    return new AuthenticationError('Token expired');
  }
  return error;
};

/**
 * Error Response Helper
 * Creates standardized error response
 */
const createErrorResponse = (message, statusCode = 500, details = null) => {
  const response = {
    error: true,
    message,
    statusCode,
    timestamp: new Date().toISOString(),
  };

  if (details) {
    response.details = details;
  }

  return response;
};

module.exports = {
  // Error classes
  AppError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ConflictError,
  RateLimitError,
  ExternalServiceError,
  DatabaseError,

  // Middleware
  errorHandler,
  asyncHandler,
  notFoundHandler,

  // Error handlers
  handleValidationError,
  handleDatabaseError,
  handleExternalServiceError,
  handleJWTError,

  // Helpers
  createErrorResponse,
};
