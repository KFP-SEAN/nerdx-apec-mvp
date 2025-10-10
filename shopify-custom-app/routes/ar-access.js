/**
 * AR Access Routes
 * API endpoints for AR access token management and verification
 */

const express = require('express');
const router = express.Router();
const arAccessService = require('../services/ar-access-service');
const neo4jSyncService = require('../services/neo4j-sync-service');
const logger = require('../utils/logger');
const { asyncHandler, ValidationError, NotFoundError } = require('../middleware/error-handler');
const { requireAuthType } = require('../middleware/auth');

/**
 * POST /api/ar-access/generate
 * Generate new AR access token
 * Requires API key authentication
 */
router.post('/generate', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const { userId, email, productId, orderId, productTitle, shopDomain, customerId } = req.body;

  // Validate required fields
  if (!userId || !email || !productId || !orderId) {
    throw new ValidationError('Missing required fields: userId, email, productId, orderId');
  }

  // Generate token
  const tokenData = arAccessService.generateToken({
    userId,
    email,
    productId,
    orderId,
    productTitle,
    shopDomain,
    customerId,
  });

  logger.arAccess('Token generated via API', {
    userId,
    email,
    productId,
    orderId,
  });

  res.status(201).json({
    success: true,
    message: 'AR access token generated successfully',
    data: tokenData,
  });
}));

/**
 * POST /api/ar-access/verify
 * Verify AR access token
 * Public endpoint (no authentication required)
 */
router.post('/verify', asyncHandler(async (req, res) => {
  const { token } = req.body;

  if (!token) {
    throw new ValidationError('Token is required');
  }

  // Verify token
  const decoded = arAccessService.verifyToken(token);

  // Check if user still has access in Neo4j
  const hasAccess = await neo4jSyncService.hasARAccess(decoded.email, decoded.productId);

  res.status(200).json({
    success: true,
    valid: decoded.valid && hasAccess,
    data: {
      ...decoded,
      hasActiveAccess: hasAccess,
    },
  });
}));

/**
 * POST /api/ar-access/refresh
 * Refresh an expired or expiring token
 * Public endpoint (accepts expired tokens)
 */
router.post('/refresh', asyncHandler(async (req, res) => {
  const { token } = req.body;

  if (!token) {
    throw new ValidationError('Token is required');
  }

  // Decode token (don't verify - allow expired)
  const metadata = arAccessService.getTokenMetadata(token);

  if (!metadata) {
    throw new ValidationError('Invalid token format');
  }

  // Check if user still has access in Neo4j
  const hasAccess = await neo4jSyncService.hasARAccess(metadata.email, metadata.productId);

  if (!hasAccess) {
    throw new ValidationError('AR access has been revoked');
  }

  // Refresh token
  const newTokenData = arAccessService.refreshToken(token);

  logger.arAccess('Token refreshed', {
    oldTokenId: metadata.tokenId,
    newTokenId: newTokenData.tokenId,
    userId: metadata.userId,
    email: metadata.email,
    productId: metadata.productId,
  });

  res.status(200).json({
    success: true,
    message: 'Token refreshed successfully',
    data: newTokenData,
  });
}));

/**
 * GET /api/ar-access/check/:email/:productId
 * Check if user has AR access to a product
 * Requires API key authentication
 */
router.get('/check/:email/:productId', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const { email, productId } = req.params;

  if (!email || !productId) {
    throw new ValidationError('Email and productId are required');
  }

  const hasAccess = await neo4jSyncService.hasARAccess(email, productId);

  res.status(200).json({
    success: true,
    hasAccess,
    email,
    productId,
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/ar-access/user/:email
 * Get user's purchases and AR access status
 * Requires API key authentication
 */
router.get('/user/:email', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const { email } = req.params;

  if (!email) {
    throw new ValidationError('Email is required');
  }

  const purchases = await neo4jSyncService.getUserPurchases(email);

  res.status(200).json({
    success: true,
    email,
    purchases,
    count: purchases.length,
  });
}));

/**
 * POST /api/ar-access/revoke
 * Revoke AR access for a user/product
 * Requires API key authentication
 */
router.post('/revoke', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const { email, productId, reason } = req.body;

  if (!email || !productId) {
    throw new ValidationError('Email and productId are required');
  }

  const revoked = await neo4jSyncService.revokeARAccess(
    email,
    productId,
    reason || 'manual_revocation'
  );

  if (!revoked) {
    throw new NotFoundError('AR access relationship');
  }

  logger.arAccess('Access revoked via API', {
    email,
    productId,
    reason,
  });

  res.status(200).json({
    success: true,
    message: 'AR access revoked successfully',
    email,
    productId,
    reason,
  });
}));

/**
 * POST /api/ar-access/grant
 * Manually grant AR access (for testing or special cases)
 * Requires API key authentication
 */
router.post('/grant', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const {
    userId,
    email,
    productId,
    orderId,
    productTitle,
    shopDomain,
    customerId,
  } = req.body;

  // Validate required fields
  if (!userId || !email || !productId || !orderId) {
    throw new ValidationError('Missing required fields: userId, email, productId, orderId');
  }

  // Generate token
  const tokenData = arAccessService.generateToken({
    userId,
    email,
    productId,
    orderId,
    productTitle,
    shopDomain,
    customerId,
  });

  // Grant AR access in Neo4j
  await neo4jSyncService.grantARAccess({
    email,
    productId,
    orderId,
    tokenId: tokenData.tokenId,
    grantedAt: new Date().toISOString(),
    expiresAt: tokenData.expiresAt,
  });

  logger.arAccess('Access granted via API', {
    email,
    productId,
    orderId,
  });

  res.status(201).json({
    success: true,
    message: 'AR access granted successfully',
    data: tokenData,
  });
}));

/**
 * POST /api/ar-access/batch-generate
 * Generate tokens for multiple products
 * Requires API key authentication
 */
router.post('/batch-generate', requireAuthType('api_key'), asyncHandler(async (req, res) => {
  const { userData, products } = req.body;

  if (!userData || !products || !Array.isArray(products)) {
    throw new ValidationError('userData and products array are required');
  }

  if (!userData.userId || !userData.email) {
    throw new ValidationError('userData must include userId and email');
  }

  // Generate tokens for all products
  const tokens = arAccessService.batchGenerateTokens(userData, products);

  logger.arAccess('Batch tokens generated', {
    userId: userData.userId,
    email: userData.email,
    count: tokens.length,
  });

  res.status(201).json({
    success: true,
    message: `Generated ${tokens.length} AR access tokens`,
    count: tokens.length,
    data: tokens,
  });
}));

/**
 * GET /api/ar-access/token/metadata
 * Get token metadata without verification
 * Public endpoint
 */
router.get('/token/metadata', asyncHandler(async (req, res) => {
  const token = req.query.token || req.headers.authorization?.split(' ')[1];

  if (!token) {
    throw new ValidationError('Token is required (query param or Authorization header)');
  }

  const metadata = arAccessService.getTokenMetadata(token);

  if (!metadata) {
    throw new ValidationError('Invalid token format');
  }

  res.status(200).json({
    success: true,
    data: metadata,
  });
}));

/**
 * GET /api/ar-access/health
 * Health check for AR access service
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'ar-access',
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
