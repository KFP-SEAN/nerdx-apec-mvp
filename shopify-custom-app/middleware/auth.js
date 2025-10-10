/**
 * Authentication Middleware
 * Handles API key and JWT authentication for internal API endpoints
 */

const jwt = require('jsonwebtoken');
const logger = require('../utils/logger');
const { recordError } = require('../utils/metrics');

// API Key Authentication
const API_KEY = process.env.API_KEY;
const JWT_SECRET = process.env.JWT_SECRET;

/**
 * API Key Authentication Middleware
 * Validates the API key from Authorization header
 */
const authenticateAPIKey = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      logger.security('Missing authorization header', {
        ip: req.ip,
        path: req.path,
      });
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Missing authorization header',
      });
    }

    // Support both "Bearer <token>" and "API-Key <key>" formats
    const [scheme, credentials] = authHeader.split(' ');

    if (!credentials) {
      logger.security('Invalid authorization header format', {
        ip: req.ip,
        path: req.path,
      });
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid authorization header format',
      });
    }

    // Verify API key
    if (scheme === 'API-Key' || scheme === 'Bearer') {
      if (credentials !== API_KEY) {
        logger.security('Invalid API key', {
          ip: req.ip,
          path: req.path,
        });
        recordError('authentication_failed', 'warning');
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Invalid API key',
        });
      }

      // API key is valid
      req.auth = {
        type: 'api_key',
        authenticated: true,
      };

      return next();
    }

    logger.security('Unsupported authentication scheme', {
      ip: req.ip,
      path: req.path,
      scheme,
    });
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Unsupported authentication scheme',
    });

  } catch (error) {
    logger.error('Authentication error:', error);
    recordError('authentication_error', 'error');
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'Authentication failed',
    });
  }
};

/**
 * JWT Authentication Middleware
 * Validates JWT tokens (used for AR access tokens)
 */
const authenticateJWT = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Missing authorization header',
      });
    }

    const [scheme, token] = authHeader.split(' ');

    if (scheme !== 'Bearer' || !token) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid authorization header format. Expected: Bearer <token>',
      });
    }

    // Verify JWT token
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        logger.security('Invalid JWT token', {
          ip: req.ip,
          path: req.path,
          error: err.message,
        });
        recordError('jwt_verification_failed', 'warning');

        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({
            error: 'Unauthorized',
            message: 'Token expired',
          });
        }

        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Invalid token',
        });
      }

      // Token is valid, attach decoded data to request
      req.auth = {
        type: 'jwt',
        authenticated: true,
        userId: decoded.userId,
        email: decoded.email,
        productId: decoded.productId,
        orderId: decoded.orderId,
        iat: decoded.iat,
        exp: decoded.exp,
      };

      next();
    });

  } catch (error) {
    logger.error('JWT authentication error:', error);
    recordError('jwt_authentication_error', 'error');
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'Authentication failed',
    });
  }
};

/**
 * Combined Authentication Middleware
 * Accepts either API key or JWT token
 */
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Missing authorization header',
    });
  }

  const [scheme] = authHeader.split(' ');

  // Route to appropriate authentication method
  if (scheme === 'API-Key') {
    return authenticateAPIKey(req, res, next);
  } else if (scheme === 'Bearer') {
    // Try JWT first, fall back to API key
    const [, token] = authHeader.split(' ');

    // Check if it looks like a JWT (has three parts separated by dots)
    if (token && token.split('.').length === 3) {
      return authenticateJWT(req, res, next);
    } else {
      return authenticateAPIKey(req, res, next);
    }
  }

  return res.status(401).json({
    error: 'Unauthorized',
    message: 'Unsupported authentication scheme. Use API-Key or Bearer',
  });
};

/**
 * Optional Authentication Middleware
 * Attempts to authenticate but doesn't fail if no credentials provided
 */
const optionalAuth = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    req.auth = { authenticated: false };
    return next();
  }

  // Try to authenticate, but don't fail
  authenticate(req, res, (err) => {
    if (err) {
      req.auth = { authenticated: false };
      return next();
    }
    next();
  });
};

/**
 * Role-based Access Control Middleware
 * Checks if authenticated user has required role
 */
const requireRole = (...roles) => {
  return (req, res, next) => {
    if (!req.auth || !req.auth.authenticated) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    if (!req.auth.role || !roles.includes(req.auth.role)) {
      logger.security('Insufficient permissions', {
        ip: req.ip,
        path: req.path,
        userRole: req.auth.role,
        requiredRoles: roles,
      });
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient permissions',
      });
    }

    next();
  };
};

/**
 * Validate request has required authentication type
 */
const requireAuthType = (type) => {
  return (req, res, next) => {
    if (!req.auth || !req.auth.authenticated) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    if (req.auth.type !== type) {
      return res.status(403).json({
        error: 'Forbidden',
        message: `This endpoint requires ${type} authentication`,
      });
    }

    next();
  };
};

module.exports = {
  authenticate,
  authenticateAPIKey,
  authenticateJWT,
  optionalAuth,
  requireRole,
  requireAuthType,
};
