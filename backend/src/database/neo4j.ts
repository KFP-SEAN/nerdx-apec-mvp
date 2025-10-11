/**
 * Neo4j Database Service
 * Manages purchase relationships and recommendations
 */

import neo4j, { Driver, Session } from 'neo4j-driver';

export interface Purchase {
  userId: string;
  orderId: string;
  products: Array<{
    productId: string;
    title: string;
    quantity: number;
    price: string;
  }>;
  total: string;
  timestamp: Date;
}

class Neo4jService {
  private driver: Driver | null = null;

  async connect() {
    const uri = process.env.NEO4J_URI || 'bolt://localhost:7687';
    const user = process.env.NEO4J_USER || 'neo4j';
    const password = process.env.NEO4J_PASSWORD || '';

    this.driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

    // Verify connection
    await this.driver.verifyConnectivity();
    console.log('✅ Connected to Neo4j');
  }

  async createPurchase(purchase: Purchase) {
    if (!this.driver) throw new Error('Neo4j not connected');

    const session = this.driver.session();

    try {
      await session.writeTransaction(async (tx) => {
        // Create or merge user
        await tx.run(
          `MERGE (u:User {email: $email})
           ON CREATE SET u.createdAt = datetime()
           RETURN u`,
          { email: purchase.userId }
        );

        // Create order
        await tx.run(
          `CREATE (o:Order {
             id: $orderId,
             total: $total,
             timestamp: datetime($timestamp)
           })`,
          {
            orderId: purchase.orderId,
            total: purchase.total,
            timestamp: purchase.timestamp.toISOString()
          }
        );

        // Create relationships
        for (const product of purchase.products) {
          await tx.run(
            `MATCH (u:User {email: $email})
             MATCH (o:Order {id: $orderId})
             MERGE (p:Product {id: $productId})
             ON CREATE SET p.title = $title
             CREATE (u)-[:PLACED]->(o)
             CREATE (o)-[:CONTAINS {quantity: $quantity, price: $price}]->(p)`,
            {
              email: purchase.userId,
              orderId: purchase.orderId,
              productId: product.productId,
              title: product.title,
              quantity: product.quantity,
              price: product.price
            }
          );
        }
      });

      console.log(`Purchase recorded in Neo4j: ${purchase.orderId}`);
    } finally {
      await session.close();
    }
  }

  async getRecommendations(userId: string, limit: number = 5): Promise<string[]> {
    if (!this.driver) throw new Error('Neo4j not connected');

    const session = this.driver.session();

    try {
      const result = await session.run(
        `MATCH (u:User {email: $email})-[:PLACED]->()-[:CONTAINS]->(p:Product)
         MATCH (p)<-[:CONTAINS]-()<-[:PLACED]-(other:User)
         MATCH (other)-[:PLACED]->()-[:CONTAINS]->(rec:Product)
         WHERE NOT (u)-[:PLACED]->()-[:CONTAINS]->(rec)
         RETURN rec.id AS productId, rec.title AS title, count(*) AS score
         ORDER BY score DESC
         LIMIT $limit`,
        { email: userId, limit }
      );

      return result.records.map(record => record.get('productId'));
    } finally {
      await session.close();
    }
  }

  async close() {
    if (this.driver) {
      await this.driver.close();
      console.log('Neo4j connection closed');
    }
  }
}

export const neo4jService = new Neo4jService();
