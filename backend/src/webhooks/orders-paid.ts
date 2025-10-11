/**
 * Orders Paid Webhook Handler
 * Triggers when order is successfully paid
 */

import { Request, Response } from 'express';
import { verifyShopifyWebhook } from '../middleware/shopify-hmac';
import { neo4jService } from '../database/neo4j';
import { arAccessControl } from '../services/ar-access';

export async function handleOrdersPaid(req: Request, res: Response) {
  try {
    // Verify webhook authenticity
    if (!verifyShopifyWebhook(req)) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const order = req.body;

    console.log(`Order paid: ${order.id}`);

    // Grant AR access for AR-enabled products
    const arProducts = order.line_items.filter((item: any) =>
      item.properties?.some((p: any) => p.name === 'ar_enabled' && p.value === 'true')
    );

    for (const item of arProducts) {
      await arAccessControl.grantAccess({
        productId: item.product_id,
        userId: order.customer.email,
        orderId: order.id
      });
    }

    // Create purchase relationship in Neo4j
    await neo4jService.createPurchase({
      userId: order.customer.email,
      orderId: order.id,
      products: order.line_items.map((item: any) => ({
        productId: item.product_id,
        title: item.title,
        quantity: item.quantity,
        price: item.price
      })),
      total: order.total_price,
      timestamp: new Date(order.created_at)
    });

    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error handling orders/paid webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
