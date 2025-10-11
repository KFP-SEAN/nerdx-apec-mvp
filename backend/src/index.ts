/**
 * Custom Shopify App Server
 * Handles webhooks, AR access, and data management
 */

import express from 'express';
import { handleOrdersPaid } from './webhooks/orders-paid';
import { handleOrdersCancelled } from './webhooks/orders-cancelled';
import { neo4jService } from './database/neo4j';
import { redisService } from './cache/redis';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(express.json());
app.use(express.raw({ type: 'application/json' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date() });
});

// Webhooks
app.post('/webhooks/orders/paid', handleOrdersPaid);
app.post('/webhooks/orders/cancelled', handleOrdersCancelled);

// AR Access API
app.post('/api/ar-access/verify', async (req, res) => {
  const { productId, email } = req.body;

  // Check if user has purchased this product
  // Return AR access token if valid
  res.json({ hasAccess: true, token: 'placeholder' });
});

// Recommendations API
app.get('/api/recommendations/:email', async (req, res) => {
  const { email } = req.params;

  const recommendations = await neo4jService.getRecommendations(email);
  res.json({ recommendations });
});

// Start server
async function start() {
  await neo4jService.connect();
  await redisService.connect();

  app.listen(PORT, () => {
    console.log(`✅ Custom Shopify App running on port ${PORT}`);
  });
}

start().catch(console.error);

// Graceful shutdown
process.on('SIGTERM', async () => {
  await neo4jService.close();
  await redisService.close();
  process.exit(0);
});
