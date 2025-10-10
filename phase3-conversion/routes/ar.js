const express = require('express');
const { body, param, query, validationResult } = require('express-validator');
const arService = require('../services/ar-service');
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
 * Unlock AR experience (called internally after purchase)
 * POST /api/ar/unlock
 */
router.post('/unlock',
  [
    body('userId').notEmpty().withMessage('User ID is required'),
    body('productId').notEmpty().withMessage('Product ID is required'),
    body('orderId').notEmpty().withMessage('Order ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId, productId, orderId } = req.body;

      logger.info(`Unlocking AR experience for user ${userId}, product ${productId}`);

      const result = await arService.unlockExperience({
        userId,
        productId,
        orderId
      });

      res.status(200).json({
        success: true,
        message: 'AR experience unlocked successfully',
        unlock: {
          id: result.unlock.id,
          unlockedAt: result.unlock.unlockedAt,
          status: result.unlock.status
        },
        arAsset: result.arAsset
      });

    } catch (error) {
      logger.error('Error unlocking AR experience:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to unlock AR experience'
      });
    }
  }
);

/**
 * Get AR experience for a specific product
 * GET /api/ar/experience/:productId
 */
router.get('/experience/:productId',
  [
    param('productId').notEmpty().withMessage('Product ID is required'),
    query('userId').notEmpty().withMessage('User ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { productId } = req.params;
      const { userId } = req.query;

      logger.info(`Getting AR experience for user ${userId}, product ${productId}`);

      const experience = await arService.getARExperience(userId, productId);

      if (!experience.hasAccess) {
        return res.status(403).json({
          success: false,
          hasAccess: false,
          message: experience.message
        });
      }

      res.status(200).json({
        success: true,
        hasAccess: true,
        experience: {
          unlock: experience.unlock,
          arAsset: experience.arAsset,
          metadata: experience.metadata
        }
      });

    } catch (error) {
      logger.error('Error getting AR experience:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to get AR experience'
      });
    }
  }
);

/**
 * Get all unlocked AR experiences for a user
 * GET /api/ar/user/:userId/experiences
 */
router.get('/user/:userId/experiences',
  [
    param('userId').notEmpty().withMessage('User ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId } = req.params;

      logger.info(`Getting all AR experiences for user ${userId}`);

      const experiences = await arService.getUserARExperiences(userId);

      res.status(200).json({
        success: true,
        count: experiences.length,
        experiences
      });

    } catch (error) {
      logger.error('Error getting user AR experiences:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to get AR experiences'
      });
    }
  }
);

/**
 * Grant preview/trial access to AR experience
 * POST /api/ar/preview
 */
router.post('/preview',
  [
    body('userId').notEmpty().withMessage('User ID is required'),
    body('productId').notEmpty().withMessage('Product ID is required'),
    body('duration').optional().isInt({ min: 5, max: 120 }).withMessage('Duration must be between 5 and 120 minutes'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId, productId, duration } = req.body;

      logger.info(`Granting AR preview for user ${userId}, product ${productId}`);

      const preview = await arService.grantPreviewAccess(
        userId,
        productId,
        duration || 30
      );

      res.status(200).json({
        success: true,
        message: preview.message || 'Preview access granted',
        preview: {
          id: preview.preview.id,
          unlockedAt: preview.preview.unlockedAt,
          expiresAt: preview.preview.expiresAt,
          status: preview.preview.status
        },
        arAsset: preview.arAsset
      });

    } catch (error) {
      logger.error('Error granting preview access:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to grant preview access'
      });
    }
  }
);

/**
 * Verify AR access token
 * POST /api/ar/verify
 */
router.post('/verify',
  [
    body('accessToken').notEmpty().withMessage('Access token is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { accessToken } = req.body;

      logger.info('Verifying AR access token');

      const verification = await arService.verifyAccessToken(accessToken);

      if (!verification.valid) {
        return res.status(401).json({
          success: false,
          valid: false,
          message: verification.message
        });
      }

      res.status(200).json({
        success: true,
        valid: true,
        unlock: verification.unlock
      });

    } catch (error) {
      logger.error('Error verifying access token:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to verify access token'
      });
    }
  }
);

/**
 * Revoke AR access (for refunds)
 * DELETE /api/ar/access
 */
router.delete('/access',
  [
    body('userId').notEmpty().withMessage('User ID is required'),
    body('productId').notEmpty().withMessage('Product ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { userId, productId } = req.body;

      logger.info(`Revoking AR access for user ${userId}, product ${productId}`);

      const result = await arService.revokeAccess(userId, productId);

      res.status(200).json({
        success: true,
        message: result.message,
        revokedAt: result.revokedAt
      });

    } catch (error) {
      logger.error('Error revoking AR access:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to revoke AR access'
      });
    }
  }
);

/**
 * Get AR analytics for a product
 * GET /api/ar/analytics/:productId
 */
router.get('/analytics/:productId',
  [
    param('productId').notEmpty().withMessage('Product ID is required'),
    handleValidationErrors
  ],
  async (req, res) => {
    try {
      const { productId } = req.params;

      logger.info(`Getting AR analytics for product ${productId}`);

      const analytics = await arService.getARAnalytics(productId);

      res.status(200).json({
        success: true,
        analytics: analytics.analytics
      });

    } catch (error) {
      logger.error('Error getting AR analytics:', error);

      res.status(500).json({
        success: false,
        error: error.message || 'Failed to get AR analytics'
      });
    }
  }
);

/**
 * Health check for AR service
 * GET /api/ar/health
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    success: true,
    service: 'AR Service',
    status: 'operational',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
