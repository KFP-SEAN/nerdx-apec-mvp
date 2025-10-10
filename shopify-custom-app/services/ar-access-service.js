/**
 * AR Access Service
 * Handles JWT token generation and verification for AR access
 * 90-day token expiry as per PRD specifications
 */

const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const { recordARMetrics } = require('../utils/metrics');
const { AuthenticationError, ValidationError } = require('../middleware/error-handler');

// Configuration
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_ISSUER = process.env.JWT_ISSUER || 'nerdx-apec-shopify';
const JWT_AUDIENCE = process.env.JWT_AUDIENCE || 'nerdx-apec-ar-viewer';
const AR_TOKEN_EXPIRY_DAYS = parseInt(process.env.AR_TOKEN_EXPIRY_DAYS) || 90;

class ARAccessService {
  constructor() {
    if (!JWT_SECRET) {
      logger.error('JWT_SECRET not configured');
      throw new Error('JWT_SECRET is required for AR access service');
    }
  }

  /**
   * Generate AR access token
   * @param {Object} tokenData - Token payload data
   * @returns {Object} Token and metadata
   */
  generateToken(tokenData) {
    try {
      // Validate required fields
      if (!tokenData.userId || !tokenData.email || !tokenData.productId || !tokenData.orderId) {
        throw new ValidationError('Missing required token data: userId, email, productId, orderId');
      }

      // Generate unique token ID
      const tokenId = uuidv4();

      // Calculate expiration (90 days from now)
      const expiresIn = `${AR_TOKEN_EXPIRY_DAYS}d`;
      const issuedAt = Math.floor(Date.now() / 1000);
      const expiresAt = new Date(Date.now() + (AR_TOKEN_EXPIRY_DAYS * 24 * 60 * 60 * 1000));

      // Prepare token payload
      const payload = {
        // Standard JWT claims
        jti: tokenId,
        iss: JWT_ISSUER,
        aud: JWT_AUDIENCE,
        sub: tokenData.userId,
        iat: issuedAt,

        // Custom claims
        userId: tokenData.userId,
        email: tokenData.email,
        productId: tokenData.productId,
        orderId: tokenData.orderId,

        // Optional metadata
        ...(tokenData.productTitle && { productTitle: tokenData.productTitle }),
        ...(tokenData.shopDomain && { shopDomain: tokenData.shopDomain }),
        ...(tokenData.customerId && { customerId: tokenData.customerId }),
      };

      // Sign token
      const token = jwt.sign(payload, JWT_SECRET, {
        expiresIn,
        algorithm: 'HS256',
      });

      // Record metrics
      recordARMetrics.tokenGenerated(tokenData.productId);

      logger.arAccess('Token generated', {
        tokenId,
        userId: tokenData.userId,
        email: tokenData.email,
        productId: tokenData.productId,
        orderId: tokenData.orderId,
        expiresAt: expiresAt.toISOString(),
      });

      return {
        token,
        tokenId,
        userId: tokenData.userId,
        email: tokenData.email,
        productId: tokenData.productId,
        orderId: tokenData.orderId,
        issuedAt: new Date(issuedAt * 1000).toISOString(),
        expiresAt: expiresAt.toISOString(),
        expiresIn: AR_TOKEN_EXPIRY_DAYS * 24 * 60 * 60, // seconds
      };

    } catch (error) {
      logger.error('Failed to generate AR token:', error);
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new Error('Failed to generate AR access token');
    }
  }

  /**
   * Verify AR access token
   * @param {string} token - JWT token to verify
   * @returns {Object} Decoded token data
   */
  verifyToken(token) {
    try {
      if (!token) {
        throw new ValidationError('Token is required');
      }

      // Verify and decode token
      const decoded = jwt.verify(token, JWT_SECRET, {
        issuer: JWT_ISSUER,
        audience: JWT_AUDIENCE,
        algorithms: ['HS256'],
      });

      // Record metrics
      recordARMetrics.tokenValidated(true);

      logger.arAccess('Token verified', {
        tokenId: decoded.jti,
        userId: decoded.userId,
        email: decoded.email,
        productId: decoded.productId,
      });

      return {
        valid: true,
        tokenId: decoded.jti,
        userId: decoded.userId,
        email: decoded.email,
        productId: decoded.productId,
        orderId: decoded.orderId,
        productTitle: decoded.productTitle,
        issuedAt: new Date(decoded.iat * 1000).toISOString(),
        expiresAt: new Date(decoded.exp * 1000).toISOString(),
      };

    } catch (error) {
      // Record failed validation
      recordARMetrics.tokenValidated(false);

      if (error.name === 'TokenExpiredError') {
        logger.arAccess('Token expired', { token: token.substring(0, 20) + '...' });
        throw new AuthenticationError('AR access token has expired');
      }

      if (error.name === 'JsonWebTokenError') {
        logger.arAccess('Invalid token', {
          token: token.substring(0, 20) + '...',
          error: error.message,
        });
        throw new AuthenticationError('Invalid AR access token');
      }

      logger.error('Token verification error:', error);
      throw new AuthenticationError('Failed to verify AR access token');
    }
  }

  /**
   * Decode token without verification (for debugging)
   * @param {string} token - JWT token to decode
   * @returns {Object} Decoded token data
   */
  decodeToken(token) {
    try {
      const decoded = jwt.decode(token, { complete: true });

      if (!decoded) {
        return null;
      }

      return {
        header: decoded.header,
        payload: decoded.payload,
      };
    } catch (error) {
      logger.error('Failed to decode token:', error);
      return null;
    }
  }

  /**
   * Check if token is expired
   * @param {string} token - JWT token to check
   * @returns {boolean} True if expired
   */
  isTokenExpired(token) {
    try {
      const decoded = jwt.decode(token);

      if (!decoded || !decoded.exp) {
        return true;
      }

      const now = Math.floor(Date.now() / 1000);
      return decoded.exp < now;
    } catch (error) {
      return true;
    }
  }

  /**
   * Get token expiration date
   * @param {string} token - JWT token
   * @returns {Date|null} Expiration date
   */
  getTokenExpiration(token) {
    try {
      const decoded = jwt.decode(token);

      if (!decoded || !decoded.exp) {
        return null;
      }

      return new Date(decoded.exp * 1000);
    } catch (error) {
      return null;
    }
  }

  /**
   * Refresh token (generate new token with same data but new expiry)
   * @param {string} oldToken - Existing token to refresh
   * @returns {Object} New token and metadata
   */
  refreshToken(oldToken) {
    try {
      // Decode old token (don't verify - allow expired tokens to be refreshed)
      const decoded = jwt.decode(oldToken);

      if (!decoded) {
        throw new ValidationError('Invalid token format');
      }

      // Generate new token with same data
      return this.generateToken({
        userId: decoded.userId,
        email: decoded.email,
        productId: decoded.productId,
        orderId: decoded.orderId,
        productTitle: decoded.productTitle,
        shopDomain: decoded.shopDomain,
        customerId: decoded.customerId,
      });

    } catch (error) {
      logger.error('Failed to refresh token:', error);
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new Error('Failed to refresh AR access token');
    }
  }

  /**
   * Validate token data structure
   * @param {Object} tokenData - Token data to validate
   * @returns {boolean} True if valid
   */
  validateTokenData(tokenData) {
    const requiredFields = ['userId', 'email', 'productId', 'orderId'];

    for (const field of requiredFields) {
      if (!tokenData[field]) {
        logger.error(`Missing required token field: ${field}`);
        return false;
      }
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(tokenData.email)) {
      logger.error('Invalid email format');
      return false;
    }

    return true;
  }

  /**
   * Extract token from Authorization header
   * @param {string} authHeader - Authorization header value
   * @returns {string|null} Extracted token
   */
  extractTokenFromHeader(authHeader) {
    if (!authHeader) {
      return null;
    }

    const parts = authHeader.split(' ');

    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      return null;
    }

    return parts[1];
  }

  /**
   * Get token metadata without verification
   * @param {string} token - JWT token
   * @returns {Object|null} Token metadata
   */
  getTokenMetadata(token) {
    try {
      const decoded = jwt.decode(token);

      if (!decoded) {
        return null;
      }

      return {
        tokenId: decoded.jti,
        userId: decoded.userId,
        email: decoded.email,
        productId: decoded.productId,
        orderId: decoded.orderId,
        issuedAt: decoded.iat ? new Date(decoded.iat * 1000).toISOString() : null,
        expiresAt: decoded.exp ? new Date(decoded.exp * 1000).toISOString() : null,
        expired: this.isTokenExpired(token),
      };
    } catch (error) {
      logger.error('Failed to get token metadata:', error);
      return null;
    }
  }

  /**
   * Batch generate tokens for multiple products
   * @param {Object} userData - User data
   * @param {Array} products - Array of product data
   * @returns {Array} Array of tokens
   */
  batchGenerateTokens(userData, products) {
    try {
      const tokens = [];

      for (const product of products) {
        const token = this.generateToken({
          userId: userData.userId,
          email: userData.email,
          productId: product.productId,
          orderId: product.orderId,
          productTitle: product.title,
          customerId: userData.customerId,
          shopDomain: userData.shopDomain,
        });

        tokens.push(token);
      }

      logger.arAccess('Batch tokens generated', {
        userId: userData.userId,
        count: tokens.length,
      });

      return tokens;

    } catch (error) {
      logger.error('Failed to batch generate tokens:', error);
      throw new Error('Failed to generate AR access tokens');
    }
  }
}

// Create singleton instance
const arAccessService = new ARAccessService();

module.exports = arAccessService;
