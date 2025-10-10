const { v4: uuidv4 } = require('uuid');
const { logger } = require('../utils/logger');
const axios = require('axios');

class ARService {
  constructor() {
    this.phase1ApiUrl = process.env.PHASE1_API_URL || 'http://localhost:3001/api';
    // In production, this would use a database
    this.arUnlocks = new Map();
  }

  /**
   * Unlock AR experience for a user after purchase
   * @param {Object} unlockData - AR unlock details
   * @returns {Promise<Object>} Unlock confirmation
   */
  async unlockExperience(unlockData) {
    try {
      const { userId, productId, orderId } = unlockData;

      // Validate product has AR experience
      const product = await this.getProductDetails(productId);

      if (!product) {
        throw new Error(`Product ${productId} not found`);
      }

      if (!product.arEnabled) {
        throw new Error(`Product ${productId} does not have AR experience`);
      }

      // Generate unique AR access token
      const accessToken = this.generateARToken(userId, productId);

      // Create unlock record
      const unlockRecord = {
        id: uuidv4(),
        userId,
        productId,
        orderId,
        accessToken,
        unlockedAt: new Date().toISOString(),
        expiresAt: null, // Permanent access for purchased items
        status: 'active',
        metadata: {
          productName: product.name,
          arAssetUrl: product.arAssetUrl,
          arType: product.arType || 'model', // model, filter, effect
          platform: product.arPlatform || 'web', // web, ios, android
        }
      };

      // Store unlock (in production, save to database)
      const key = `${userId}:${productId}`;
      this.arUnlocks.set(key, unlockRecord);

      logger.info(`AR experience unlocked: ${unlockRecord.id} for user ${userId}`);

      return {
        success: true,
        unlock: unlockRecord,
        arAsset: {
          url: product.arAssetUrl,
          type: product.arType,
          platform: product.arPlatform,
          accessToken: accessToken
        }
      };

    } catch (error) {
      logger.error('Error unlocking AR experience:', error);
      throw error;
    }
  }

  /**
   * Get AR experience details for a user
   * @param {string} userId - User ID
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} AR experience details
   */
  async getARExperience(userId, productId) {
    try {
      const key = `${userId}:${productId}`;
      const unlock = this.arUnlocks.get(key);

      if (!unlock) {
        return {
          hasAccess: false,
          message: 'AR experience not unlocked. Purchase required.'
        };
      }

      // Check if access is expired (if applicable)
      if (unlock.expiresAt && new Date(unlock.expiresAt) < new Date()) {
        return {
          hasAccess: false,
          message: 'AR experience access has expired.'
        };
      }

      // Get product details for latest AR asset URL
      const product = await this.getProductDetails(productId);

      return {
        hasAccess: true,
        unlock: {
          id: unlock.id,
          unlockedAt: unlock.unlockedAt,
          status: unlock.status
        },
        arAsset: {
          url: product.arAssetUrl,
          type: product.arType,
          platform: product.arPlatform,
          accessToken: unlock.accessToken
        },
        metadata: unlock.metadata
      };

    } catch (error) {
      logger.error('Error getting AR experience:', error);
      throw error;
    }
  }

  /**
   * Get all unlocked AR experiences for a user
   * @param {string} userId - User ID
   * @returns {Promise<Array>} List of unlocked experiences
   */
  async getUserARExperiences(userId) {
    try {
      const userUnlocks = [];

      for (const [key, unlock] of this.arUnlocks) {
        if (unlock.userId === userId && unlock.status === 'active') {
          // Check expiration
          if (!unlock.expiresAt || new Date(unlock.expiresAt) >= new Date()) {
            userUnlocks.push({
              id: unlock.id,
              productId: unlock.productId,
              productName: unlock.metadata.productName,
              unlockedAt: unlock.unlockedAt,
              arType: unlock.metadata.arType,
              platform: unlock.metadata.platform
            });
          }
        }
      }

      logger.info(`Found ${userUnlocks.length} AR experiences for user ${userId}`);

      return userUnlocks;

    } catch (error) {
      logger.error('Error getting user AR experiences:', error);
      throw error;
    }
  }

  /**
   * Revoke AR access (for refunds, etc.)
   * @param {string} userId - User ID
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Revocation confirmation
   */
  async revokeAccess(userId, productId) {
    try {
      const key = `${userId}:${productId}`;
      const unlock = this.arUnlocks.get(key);

      if (!unlock) {
        throw new Error('AR unlock not found');
      }

      // Update status to revoked
      unlock.status = 'revoked';
      unlock.revokedAt = new Date().toISOString();

      this.arUnlocks.set(key, unlock);

      logger.info(`AR access revoked for user ${userId}, product ${productId}`);

      return {
        success: true,
        message: 'AR access revoked',
        revokedAt: unlock.revokedAt
      };

    } catch (error) {
      logger.error('Error revoking AR access:', error);
      throw error;
    }
  }

  /**
   * Grant temporary AR preview access (trial/demo)
   * @param {string} userId - User ID
   * @param {string} productId - Product ID
   * @param {number} durationMinutes - Duration in minutes
   * @returns {Promise<Object>} Preview access details
   */
  async grantPreviewAccess(userId, productId, durationMinutes = 30) {
    try {
      const product = await this.getProductDetails(productId);

      if (!product || !product.arEnabled) {
        throw new Error('Product does not have AR experience');
      }

      // Check if user already has full access
      const key = `${userId}:${productId}`;
      const existingUnlock = this.arUnlocks.get(key);

      if (existingUnlock && existingUnlock.status === 'active' && !existingUnlock.expiresAt) {
        return {
          success: true,
          message: 'User already has full access',
          unlock: existingUnlock
        };
      }

      // Generate preview token
      const previewToken = this.generateARToken(userId, productId, 'preview');

      // Create temporary unlock
      const previewUnlock = {
        id: uuidv4(),
        userId,
        productId,
        orderId: null,
        accessToken: previewToken,
        unlockedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + durationMinutes * 60 * 1000).toISOString(),
        status: 'preview',
        metadata: {
          productName: product.name,
          arAssetUrl: product.arAssetUrl,
          arType: product.arType,
          platform: product.arPlatform,
          isPreview: true
        }
      };

      // Store preview unlock
      const previewKey = `${userId}:${productId}:preview`;
      this.arUnlocks.set(previewKey, previewUnlock);

      logger.info(`AR preview granted: ${previewUnlock.id} for user ${userId}, expires at ${previewUnlock.expiresAt}`);

      return {
        success: true,
        preview: previewUnlock,
        arAsset: {
          url: product.arAssetUrl,
          type: product.arType,
          platform: product.arPlatform,
          accessToken: previewToken,
          watermark: true // Preview mode includes watermark
        }
      };

    } catch (error) {
      logger.error('Error granting preview access:', error);
      throw error;
    }
  }

  /**
   * Verify AR access token
   * @param {string} accessToken - AR access token
   * @returns {Promise<Object>} Token verification result
   */
  async verifyAccessToken(accessToken) {
    try {
      // In production, use JWT or similar
      // For now, simple token validation
      const [userId, productId, timestamp, signature] = accessToken.split(':');

      if (!userId || !productId || !timestamp || !signature) {
        return { valid: false, message: 'Invalid token format' };
      }

      // Find matching unlock
      const key = `${userId}:${productId}`;
      const unlock = this.arUnlocks.get(key);

      if (!unlock || unlock.accessToken !== accessToken) {
        return { valid: false, message: 'Token not found or mismatch' };
      }

      if (unlock.status !== 'active' && unlock.status !== 'preview') {
        return { valid: false, message: 'Access revoked or inactive' };
      }

      // Check expiration
      if (unlock.expiresAt && new Date(unlock.expiresAt) < new Date()) {
        return { valid: false, message: 'Token expired' };
      }

      return {
        valid: true,
        unlock: {
          userId: unlock.userId,
          productId: unlock.productId,
          status: unlock.status,
          isPreview: unlock.status === 'preview'
        }
      };

    } catch (error) {
      logger.error('Error verifying access token:', error);
      return { valid: false, message: 'Verification error' };
    }
  }

  /**
   * Get AR analytics for a product
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} AR analytics
   */
  async getARAnalytics(productId) {
    try {
      let totalUnlocks = 0;
      let activeUnlocks = 0;
      let previewUnlocks = 0;
      let revokedUnlocks = 0;

      for (const [key, unlock] of this.arUnlocks) {
        if (unlock.productId === productId) {
          totalUnlocks++;
          if (unlock.status === 'active') activeUnlocks++;
          if (unlock.status === 'preview') previewUnlocks++;
          if (unlock.status === 'revoked') revokedUnlocks++;
        }
      }

      return {
        productId,
        analytics: {
          totalUnlocks,
          activeUnlocks,
          previewUnlocks,
          revokedUnlocks,
          conversionRate: previewUnlocks > 0 ? (activeUnlocks / previewUnlocks * 100).toFixed(2) : 0
        }
      };

    } catch (error) {
      logger.error('Error getting AR analytics:', error);
      throw error;
    }
  }

  /**
   * Generate AR access token
   * @param {string} userId - User ID
   * @param {string} productId - Product ID
   * @param {string} type - Token type (full/preview)
   * @returns {string} Access token
   */
  generateARToken(userId, productId, type = 'full') {
    // In production, use proper JWT or signed tokens
    const timestamp = Date.now();
    const signature = Buffer.from(`${userId}:${productId}:${timestamp}:${type}`).toString('base64');
    return `${userId}:${productId}:${timestamp}:${signature}`;
  }

  /**
   * Get product details from Phase 1
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Product details
   */
  async getProductDetails(productId) {
    try {
      const response = await axios.get(`${this.phase1ApiUrl}/products/${productId}`);
      return response.data;
    } catch (error) {
      logger.error(`Error fetching product ${productId}:`, error.message);
      return null;
    }
  }
}

module.exports = new ARService();
