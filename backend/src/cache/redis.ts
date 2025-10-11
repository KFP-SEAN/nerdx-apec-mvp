/**
 * Redis Cache Service
 * Caches frequently accessed data
 */

import Redis from 'ioredis';

class RedisService {
  private client: Redis | null = null;

  async connect() {
    const url = process.env.REDIS_URL || 'redis://localhost:6379';
    this.client = new Redis(url);

    this.client.on('connect', () => {
      console.log('✅ Connected to Redis');
    });

    this.client.on('error', (err) => {
      console.error('Redis error:', err);
    });
  }

  async get<T>(key: string): Promise<T | null> {
    if (!this.client) return null;

    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    if (!this.client) return;

    const serialized = JSON.stringify(value);

    if (ttl) {
      await this.client.setex(key, ttl, serialized);
    } else {
      await this.client.set(key, serialized);
    }
  }

  async del(key: string): Promise<void> {
    if (!this.client) return;
    await this.client.del(key);
  }

  async close() {
    if (this.client) {
      await this.client.quit();
      console.log('Redis connection closed');
    }
  }
}

export const redisService = new RedisService();
