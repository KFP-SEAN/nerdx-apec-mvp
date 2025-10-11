/**
 * Orders Cancelled Webhook Handler
 */

import { Request, Response } from 'express';
import { verifyShopifyWebhook } from '../middleware/shopify-hmac';
import { arAccessControl } from '../services/ar-access';

export async function handleOrdersCancelled(req: Request, res: Response) {
  try {
    if (!verifyShopifyWebhook(req)) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const order = req.body;
    console.log(`Order cancelled: ${order.id}`);

    // Revoke AR access
    for (const item of order.line_items) {
      await arAccessControl.revokeAccess({
        productId: item.product_id,
        userId: order.customer.email,
        orderId: order.id
      });
    }

    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error handling orders/cancelled webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
