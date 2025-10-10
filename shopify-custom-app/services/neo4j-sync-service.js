/**
 * Neo4j Sync Service
 * Handles synchronization of purchase data with Phase 1 Neo4j database
 * Creates PURCHASED and HAS_AR_ACCESS relationships
 */

const neo4j = require('neo4j-driver');
const logger = require('../utils/logger');
const { recordNeo4jMetrics } = require('../utils/metrics');
const { DatabaseError } = require('../middleware/error-handler');

// Neo4j Configuration
const NEO4J_URI = process.env.NEO4J_URI || 'bolt://localhost:7687';
const NEO4J_USER = process.env.NEO4J_USER || 'neo4j';
const NEO4J_PASSWORD = process.env.NEO4J_PASSWORD;
const NEO4J_DATABASE = process.env.NEO4J_DATABASE || 'neo4j';

// Connection pool configuration
const NEO4J_MAX_CONNECTION_LIFETIME = parseInt(process.env.NEO4J_MAX_CONNECTION_LIFETIME) || 3600000; // 1 hour
const NEO4J_MAX_CONNECTION_POOL_SIZE = parseInt(process.env.NEO4J_MAX_CONNECTION_POOL_SIZE) || 50;
const NEO4J_CONNECTION_ACQUISITION_TIMEOUT = parseInt(process.env.NEO4J_CONNECTION_ACQUISITION_TIMEOUT) || 60000; // 60s

class Neo4jSyncService {
  constructor() {
    this.driver = null;
    this.isConnected = false;
  }

  /**
   * Initialize Neo4j driver
   */
  initialize() {
    if (this.driver) {
      logger.warn('Neo4j driver already initialized');
      return;
    }

    try {
      this.driver = neo4j.driver(
        NEO4J_URI,
        neo4j.auth.basic(NEO4J_USER, NEO4J_PASSWORD),
        {
          maxConnectionLifetime: NEO4J_MAX_CONNECTION_LIFETIME,
          maxConnectionPoolSize: NEO4J_MAX_CONNECTION_POOL_SIZE,
          connectionAcquisitionTimeout: NEO4J_CONNECTION_ACQUISITION_TIMEOUT,
          disableLosslessIntegers: true,
        }
      );

      logger.info('Neo4j driver initialized', {
        uri: NEO4J_URI,
        database: NEO4J_DATABASE,
      });

    } catch (error) {
      logger.error('Failed to initialize Neo4j driver:', error);
      throw new DatabaseError('initialize', error);
    }
  }

  /**
   * Verify connection to Neo4j
   */
  async verifyConnection() {
    if (!this.driver) {
      this.initialize();
    }

    const session = this.driver.session({ database: NEO4J_DATABASE });

    try {
      const result = await session.run('RETURN 1 as test');
      this.isConnected = true;
      logger.info('Neo4j connection verified');
      return result.records.length > 0;
    } catch (error) {
      this.isConnected = false;
      logger.error('Neo4j connection verification failed:', error);
      throw new DatabaseError('verify_connection', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    if (!this.driver) {
      return false;
    }

    const session = this.driver.session({ database: NEO4J_DATABASE });

    try {
      await session.run('RETURN 1 as health');
      return true;
    } catch (error) {
      logger.error('Neo4j health check failed:', error);
      return false;
    } finally {
      await session.close();
    }
  }

  /**
   * Create or update user node
   */
  async createOrUpdateUser(userData) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MERGE (u:User {email: $email})
        ON CREATE SET
          u.userId = $userId,
          u.createdAt = datetime(),
          u.shopifyCustomerId = $shopifyCustomerId,
          u.firstName = $firstName,
          u.lastName = $lastName,
          u.phone = $phone
        ON MATCH SET
          u.updatedAt = datetime(),
          u.shopifyCustomerId = COALESCE($shopifyCustomerId, u.shopifyCustomerId),
          u.firstName = COALESCE($firstName, u.firstName),
          u.lastName = COALESCE($lastName, u.lastName),
          u.phone = COALESCE($phone, u.phone)
        RETURN u
      `;

      const result = await session.run(query, {
        userId: userData.userId,
        email: userData.email,
        shopifyCustomerId: userData.shopifyCustomerId || null,
        firstName: userData.firstName || null,
        lastName: userData.lastName || null,
        phone: userData.phone || null,
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('create_user', duration);
      recordNeo4jMetrics.operation('create_user', 'success');

      logger.neo4j('User created/updated', { email: userData.email });

      return result.records[0]?.get('u').properties;

    } catch (error) {
      logger.error('Failed to create/update user:', error);
      recordNeo4jMetrics.operation('create_user', 'error');
      throw new DatabaseError('create_user', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Create or update product node
   */
  async createOrUpdateProduct(productData) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MERGE (p:Product {productId: $productId})
        ON CREATE SET
          p.createdAt = datetime(),
          p.shopifyProductId = $shopifyProductId,
          p.title = $title,
          p.variantId = $variantId,
          p.sku = $sku,
          p.price = $price,
          p.currency = $currency,
          p.hasAR = $hasAR
        ON MATCH SET
          p.updatedAt = datetime(),
          p.shopifyProductId = COALESCE($shopifyProductId, p.shopifyProductId),
          p.title = COALESCE($title, p.title),
          p.variantId = COALESCE($variantId, p.variantId),
          p.sku = COALESCE($sku, p.sku),
          p.price = COALESCE($price, p.price),
          p.currency = COALESCE($currency, p.currency),
          p.hasAR = COALESCE($hasAR, p.hasAR)
        RETURN p
      `;

      const result = await session.run(query, {
        productId: productData.productId,
        shopifyProductId: productData.shopifyProductId || null,
        title: productData.title || null,
        variantId: productData.variantId || null,
        sku: productData.sku || null,
        price: productData.price || null,
        currency: productData.currency || 'USD',
        hasAR: productData.hasAR !== false, // Default to true
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('create_product', duration);
      recordNeo4jMetrics.operation('create_product', 'success');

      logger.neo4j('Product created/updated', { productId: productData.productId });

      return result.records[0]?.get('p').properties;

    } catch (error) {
      logger.error('Failed to create/update product:', error);
      recordNeo4jMetrics.operation('create_product', 'error');
      throw new DatabaseError('create_product', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Create PURCHASED relationship
   */
  async createPurchaseRelationship(purchaseData) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH (u:User {email: $email})
        MATCH (p:Product {productId: $productId})
        MERGE (u)-[r:PURCHASED {orderId: $orderId}]->(p)
        ON CREATE SET
          r.createdAt = datetime(),
          r.purchasedAt = datetime($purchasedAt),
          r.amount = $amount,
          r.currency = $currency,
          r.quantity = $quantity,
          r.status = $status,
          r.shopifyOrderId = $shopifyOrderId,
          r.shopifyOrderNumber = $shopifyOrderNumber
        ON MATCH SET
          r.updatedAt = datetime(),
          r.status = $status
        RETURN r
      `;

      const result = await session.run(query, {
        email: purchaseData.email,
        productId: purchaseData.productId,
        orderId: purchaseData.orderId,
        shopifyOrderId: purchaseData.shopifyOrderId,
        shopifyOrderNumber: purchaseData.shopifyOrderNumber || null,
        purchasedAt: purchaseData.purchasedAt || new Date().toISOString(),
        amount: purchaseData.amount,
        currency: purchaseData.currency || 'USD',
        quantity: purchaseData.quantity || 1,
        status: purchaseData.status || 'paid',
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('create_purchase', duration);
      recordNeo4jMetrics.operation('create_purchase', 'success');

      logger.neo4j('Purchase relationship created', {
        email: purchaseData.email,
        productId: purchaseData.productId,
        orderId: purchaseData.orderId,
      });

      return result.records[0]?.get('r').properties;

    } catch (error) {
      logger.error('Failed to create purchase relationship:', error);
      recordNeo4jMetrics.operation('create_purchase', 'error');
      throw new DatabaseError('create_purchase', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Create HAS_AR_ACCESS relationship
   */
  async grantARAccess(accessData) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH (u:User {email: $email})
        MATCH (p:Product {productId: $productId})
        MERGE (u)-[r:HAS_AR_ACCESS]->(p)
        ON CREATE SET
          r.createdAt = datetime(),
          r.grantedAt = datetime($grantedAt),
          r.expiresAt = datetime($expiresAt),
          r.orderId = $orderId,
          r.tokenId = $tokenId,
          r.status = 'active'
        ON MATCH SET
          r.updatedAt = datetime(),
          r.expiresAt = datetime($expiresAt),
          r.status = 'active'
        RETURN r
      `;

      const result = await session.run(query, {
        email: accessData.email,
        productId: accessData.productId,
        orderId: accessData.orderId,
        tokenId: accessData.tokenId,
        grantedAt: accessData.grantedAt || new Date().toISOString(),
        expiresAt: accessData.expiresAt,
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('grant_ar_access', duration);
      recordNeo4jMetrics.operation('grant_ar_access', 'success');

      logger.neo4j('AR access granted', {
        email: accessData.email,
        productId: accessData.productId,
      });

      return result.records[0]?.get('r').properties;

    } catch (error) {
      logger.error('Failed to grant AR access:', error);
      recordNeo4jMetrics.operation('grant_ar_access', 'error');
      throw new DatabaseError('grant_ar_access', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Revoke AR access (for refunds/cancellations)
   */
  async revokeARAccess(email, productId, reason) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH (u:User {email: $email})-[r:HAS_AR_ACCESS]->(p:Product {productId: $productId})
        SET r.status = 'revoked',
            r.revokedAt = datetime(),
            r.revokeReason = $reason,
            r.updatedAt = datetime()
        RETURN r
      `;

      const result = await session.run(query, {
        email,
        productId,
        reason,
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('revoke_ar_access', duration);
      recordNeo4jMetrics.operation('revoke_ar_access', 'success');

      logger.neo4j('AR access revoked', { email, productId, reason });

      return result.records.length > 0;

    } catch (error) {
      logger.error('Failed to revoke AR access:', error);
      recordNeo4jMetrics.operation('revoke_ar_access', 'error');
      throw new DatabaseError('revoke_ar_access', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Update purchase status (for cancellations)
   */
  async updatePurchaseStatus(orderId, status) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH ()-[r:PURCHASED {orderId: $orderId}]->()
        SET r.status = $status,
            r.updatedAt = datetime()
        RETURN r
      `;

      const result = await session.run(query, {
        orderId,
        status,
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('update_purchase_status', duration);
      recordNeo4jMetrics.operation('update_purchase_status', 'success');

      logger.neo4j('Purchase status updated', { orderId, status });

      return result.records.length > 0;

    } catch (error) {
      logger.error('Failed to update purchase status:', error);
      recordNeo4jMetrics.operation('update_purchase_status', 'error');
      throw new DatabaseError('update_purchase_status', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Check if user has AR access to product
   */
  async hasARAccess(email, productId) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH (u:User {email: $email})-[r:HAS_AR_ACCESS]->(p:Product {productId: $productId})
        WHERE r.status = 'active' AND datetime(r.expiresAt) > datetime()
        RETURN r
      `;

      const result = await session.run(query, {
        email,
        productId,
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('check_ar_access', duration);
      recordNeo4jMetrics.operation('check_ar_access', 'success');

      return result.records.length > 0;

    } catch (error) {
      logger.error('Failed to check AR access:', error);
      recordNeo4jMetrics.operation('check_ar_access', 'error');
      throw new DatabaseError('check_ar_access', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Get user's purchases with AR access status
   */
  async getUserPurchases(email) {
    const session = this.driver.session({ database: NEO4J_DATABASE });
    const startTime = Date.now();

    try {
      const query = `
        MATCH (u:User {email: $email})-[p:PURCHASED]->(prod:Product)
        OPTIONAL MATCH (u)-[ar:HAS_AR_ACCESS]->(prod)
        RETURN
          prod.productId as productId,
          prod.title as title,
          p.orderId as orderId,
          p.purchasedAt as purchasedAt,
          p.amount as amount,
          p.currency as currency,
          p.status as purchaseStatus,
          ar.status as arStatus,
          ar.expiresAt as arExpiresAt
        ORDER BY p.purchasedAt DESC
      `;

      const result = await session.run(query, { email });

      const duration = (Date.now() - startTime) / 1000;
      recordNeo4jMetrics.queryDuration('get_user_purchases', duration);
      recordNeo4jMetrics.operation('get_user_purchases', 'success');

      return result.records.map(record => ({
        productId: record.get('productId'),
        title: record.get('title'),
        orderId: record.get('orderId'),
        purchasedAt: record.get('purchasedAt'),
        amount: record.get('amount'),
        currency: record.get('currency'),
        purchaseStatus: record.get('purchaseStatus'),
        arStatus: record.get('arStatus'),
        arExpiresAt: record.get('arExpiresAt'),
      }));

    } catch (error) {
      logger.error('Failed to get user purchases:', error);
      recordNeo4jMetrics.operation('get_user_purchases', 'error');
      throw new DatabaseError('get_user_purchases', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Complete purchase sync (creates user, product, purchase, and AR access)
   */
  async syncCompletePurchase(purchaseData) {
    const session = this.driver.session({ database: NEO4J_DATABASE });

    try {
      // Use a transaction for atomicity
      const result = await session.executeWrite(async (tx) => {
        // Create/update user
        await tx.run(`
          MERGE (u:User {email: $email})
          ON CREATE SET
            u.userId = $userId,
            u.createdAt = datetime(),
            u.firstName = $firstName,
            u.lastName = $lastName
          ON MATCH SET
            u.updatedAt = datetime()
          RETURN u
        `, {
          userId: purchaseData.userId,
          email: purchaseData.email,
          firstName: purchaseData.firstName,
          lastName: purchaseData.lastName,
        });

        // Create/update product
        await tx.run(`
          MERGE (p:Product {productId: $productId})
          ON CREATE SET
            p.createdAt = datetime(),
            p.title = $title,
            p.hasAR = true
          ON MATCH SET
            p.updatedAt = datetime()
          RETURN p
        `, {
          productId: purchaseData.productId,
          title: purchaseData.productTitle,
        });

        // Create purchase relationship
        await tx.run(`
          MATCH (u:User {email: $email})
          MATCH (p:Product {productId: $productId})
          MERGE (u)-[r:PURCHASED {orderId: $orderId}]->(p)
          ON CREATE SET
            r.createdAt = datetime(),
            r.purchasedAt = datetime(),
            r.amount = $amount,
            r.currency = $currency,
            r.status = 'paid'
          RETURN r
        `, {
          email: purchaseData.email,
          productId: purchaseData.productId,
          orderId: purchaseData.orderId,
          amount: purchaseData.amount,
          currency: purchaseData.currency,
        });

        // Grant AR access
        await tx.run(`
          MATCH (u:User {email: $email})
          MATCH (p:Product {productId: $productId})
          MERGE (u)-[r:HAS_AR_ACCESS]->(p)
          ON CREATE SET
            r.createdAt = datetime(),
            r.grantedAt = datetime(),
            r.expiresAt = datetime($expiresAt),
            r.orderId = $orderId,
            r.tokenId = $tokenId,
            r.status = 'active'
          RETURN r
        `, {
          email: purchaseData.email,
          productId: purchaseData.productId,
          orderId: purchaseData.orderId,
          tokenId: purchaseData.tokenId,
          expiresAt: purchaseData.expiresAt,
        });

        return true;
      });

      logger.neo4j('Complete purchase synced', {
        email: purchaseData.email,
        productId: purchaseData.productId,
        orderId: purchaseData.orderId,
      });

      return result;

    } catch (error) {
      logger.error('Failed to sync complete purchase:', error);
      throw new DatabaseError('sync_complete_purchase', error);
    } finally {
      await session.close();
    }
  }

  /**
   * Close Neo4j driver
   */
  async close() {
    if (this.driver) {
      await this.driver.close();
      this.isConnected = false;
      logger.info('Neo4j driver closed');
    }
  }
}

// Create singleton instance
const neo4jSyncService = new Neo4jSyncService();

// Initialize on module load
if (NEO4J_PASSWORD) {
  neo4jSyncService.initialize();
} else {
  logger.warn('Neo4j password not configured. Service will not be initialized.');
}

module.exports = neo4jSyncService;
