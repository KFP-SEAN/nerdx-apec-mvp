"""
L2 Redis Exact Match Caching Service

Implements hash-based exact string matching for caching AI responses.

Key Features:
- MD5 hash-based exact matching
- Configurable TTL (default 1 hour)
- Fast O(1) lookup performance
- Automatic expiration handling
- Hit/miss metrics tracking
"""

import logging
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from redis import Redis

from models.helios.cache_models import (
    L2RedisExactMatch,
    CacheHit,
    CacheLayer
)

logger = logging.getLogger(__name__)


class L2RedisExactService:
    """
    L2 Redis Exact Match Caching Service

    Fast exact-match caching using MD5 hashing.
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize L2 Redis Exact Match Service

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client or Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Configuration
        self.default_ttl_seconds = 3600  # 1 hour
        self.max_ttl_seconds = 86400  # 24 hours

        # Metrics
        self.total_lookups = 0
        self.total_hits = 0

        logger.info(f"L2 Redis Exact Match Cache initialized (default TTL: {self.default_ttl_seconds}s)")

    def _generate_cache_key(self, input_text: str, task_type: str) -> str:
        """
        Generate cache key from input text and task type

        Args:
            input_text: Input text
            task_type: Task type

        Returns:
            MD5 hash key
        """
        # Combine input and task type for uniqueness
        combined = f"{task_type}:{input_text}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    def _generate_input_hash(self, input_text: str) -> str:
        """
        Generate hash of input text only

        Args:
            input_text: Input text

        Returns:
            MD5 hash
        """
        return hashlib.md5(input_text.encode('utf-8')).hexdigest()

    async def lookup(self, input_text: str, task_type: str) -> CacheHit:
        """
        Lookup cached response by exact match

        Args:
            input_text: Input text to lookup
            task_type: Type of task

        Returns:
            CacheHit result
        """
        self.total_lookups += 1
        cache_key = self._generate_cache_key(input_text, task_type)

        try:
            # Check Redis
            cache_data = self.redis.get(f"helios:l2_cache:{cache_key}")

            if cache_data:
                cache_entry = L2RedisExactMatch.parse_raw(cache_data)

                # Check if expired
                if not cache_entry.is_expired():
                    # Update access metrics
                    cache_entry.access_count += 1
                    cache_entry.last_accessed = datetime.utcnow()

                    # Save updated entry
                    remaining_ttl = cache_entry.ttl_seconds - int(
                        (datetime.utcnow() - cache_entry.created_at).total_seconds()
                    )

                    if remaining_ttl > 0:
                        self.redis.set(
                            f"helios:l2_cache:{cache_key}",
                            cache_entry.json(),
                            ex=remaining_ttl
                        )

                    self.total_hits += 1

                    logger.info(f"L2 cache HIT for {cache_key[:8]}... "
                               f"(task: {task_type}, access #{cache_entry.access_count})")

                    return CacheHit(
                        hit=True,
                        layer=CacheLayer.L2_REDIS_EXACT,
                        confidence=1.0,  # Exact match = 100% confidence
                        entry_id=cache_key,
                        created_at=cache_entry.created_at,
                        ttl_seconds=remaining_ttl
                    )
                else:
                    # Expired
                    logger.debug(f"L2 cache EXPIRED for {cache_key[:8]}...")
                    self.redis.delete(f"helios:l2_cache:{cache_key}")

            # Cache miss
            logger.debug(f"L2 cache MISS for {cache_key[:8]}... (task: {task_type})")
            return CacheHit(hit=False)

        except Exception as e:
            logger.error(f"L2 cache lookup error: {e}")
            return CacheHit(hit=False)

    async def get_cached_response(
        self,
        input_text: str,
        task_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if exists

        Args:
            input_text: Input text
            task_type: Task type

        Returns:
            Cached response or None
        """
        cache_key = self._generate_cache_key(input_text, task_type)

        try:
            cache_data = self.redis.get(f"helios:l2_cache:{cache_key}")

            if cache_data:
                cache_entry = L2RedisExactMatch.parse_raw(cache_data)

                if not cache_entry.is_expired():
                    return cache_entry.cached_response

            return None

        except Exception as e:
            logger.error(f"L2 get cached response error: {e}")
            return None

    async def store(
        self,
        input_text: str,
        response_data: Dict[str, Any],
        task_type: str,
        model_used: str,
        ttl_seconds: Optional[int] = None,
        tokens_in_response: int = 0
    ) -> bool:
        """
        Store response in cache

        Args:
            input_text: Input text
            response_data: Response to cache
            task_type: Type of task
            model_used: Model that generated response
            ttl_seconds: Time to live (default: 1 hour)
            tokens_in_response: Token count in response

        Returns:
            True if stored successfully
        """
        cache_key = self._generate_cache_key(input_text, task_type)
        input_hash = self._generate_input_hash(input_text)

        # Use default or provided TTL
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl_seconds
        else:
            ttl_seconds = min(ttl_seconds, self.max_ttl_seconds)

        try:
            cache_entry = L2RedisExactMatch(
                cache_key=cache_key,
                input_hash=input_hash,
                cached_response=response_data,
                task_type=task_type,
                model_used=model_used,
                created_at=datetime.utcnow(),
                ttl_seconds=ttl_seconds,
                tokens_in_cached_response=tokens_in_response
            )

            # Estimate cost saved per hit (assuming Sonnet pricing)
            # Input: $3/1M tokens, Output: $15/1M tokens
            if tokens_in_response > 0:
                output_cost = (tokens_in_response / 1_000_000) * 15.0
                cache_entry.cost_saved_per_hit = output_cost

            # Store in Redis
            self.redis.set(
                f"helios:l2_cache:{cache_key}",
                cache_entry.json(),
                ex=ttl_seconds
            )

            logger.info(f"L2 cache STORED: {cache_key[:8]}... "
                       f"(task: {task_type}, TTL: {ttl_seconds}s, tokens: {tokens_in_response})")

            # Update metrics
            self._update_metrics(cache_entry)

            return True

        except Exception as e:
            logger.error(f"L2 cache store error: {e}")
            return False

    def _update_metrics(self, cache_entry: L2RedisExactMatch):
        """
        Update aggregate metrics

        Args:
            cache_entry: Cache entry to add to metrics
        """
        try:
            self.redis.hincrby("helios:l2_metrics", "total_entries", 1)
            self.redis.hincrby("helios:l2_metrics", "total_tokens_cached", cache_entry.tokens_in_cached_response)
            self.redis.hincrbyfloat("helios:l2_metrics", "total_potential_savings", cache_entry.cost_saved_per_hit)

        except Exception as e:
            logger.error(f"Failed to update L2 metrics: {e}")

    def get_hit_rate(self) -> float:
        """
        Get L2 cache hit rate

        Returns:
            Hit rate (0.0 to 1.0)
        """
        if self.total_lookups == 0:
            return 0.0
        return self.total_hits / self.total_lookups

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get L2 cache metrics

        Returns:
            Metrics dictionary
        """
        try:
            metrics = self.redis.hgetall("helios:l2_metrics")

            total_entries = int(metrics.get("total_entries", 0))
            total_tokens = int(metrics.get("total_tokens_cached", 0))
            total_savings = float(metrics.get("total_potential_savings", 0.0))

            # Get current cache size
            keys = self.redis.keys("helios:l2_cache:*")
            active_entries = len(keys) if keys else 0

            # Estimate actual savings (based on hits)
            actual_savings = total_savings * self.total_hits if total_savings > 0 else 0

            return {
                "layer": "L2_Redis_Exact",
                "hit_rate": self.get_hit_rate(),
                "total_lookups": self.total_lookups,
                "total_hits": self.total_hits,
                "total_entries_stored": total_entries,
                "active_entries": active_entries,
                "total_tokens_cached": total_tokens,
                "potential_savings_per_hit_dollars": total_savings,
                "actual_savings_dollars": actual_savings,
                "default_ttl_seconds": self.default_ttl_seconds
            }

        except Exception as e:
            logger.error(f"Failed to get L2 metrics: {e}")
            return {
                "layer": "L2_Redis_Exact",
                "error": str(e)
            }

    async def invalidate_by_task_type(self, task_type: str) -> int:
        """
        Invalidate all cache entries for a task type

        Args:
            task_type: Task type to invalidate

        Returns:
            Number of entries invalidated
        """
        try:
            count = 0
            keys = self.redis.keys("helios:l2_cache:*")

            if keys:
                for key in keys:
                    cache_data = self.redis.get(key)
                    if cache_data:
                        try:
                            entry = L2RedisExactMatch.parse_raw(cache_data)
                            if entry.task_type == task_type:
                                self.redis.delete(key)
                                count += 1
                        except:
                            continue

            logger.info(f"Invalidated {count} L2 cache entries for task type: {task_type}")
            return count

        except Exception as e:
            logger.error(f"L2 invalidation error: {e}")
            return 0

    async def invalidate_all(self) -> int:
        """
        Invalidate all L2 cache entries

        Returns:
            Number of entries invalidated
        """
        try:
            keys = self.redis.keys("helios:l2_cache:*")
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Invalidated {count} L2 cache entries")
                return count
            return 0

        except Exception as e:
            logger.error(f"L2 invalidation error: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check

        Returns:
            Health status
        """
        try:
            redis_healthy = self.redis.ping()

            # Get current cache count
            keys = self.redis.keys("helios:l2_cache:*")
            active_entries = len(keys) if keys else 0

            # Estimate cache size
            cache_size_mb = 0.0
            if keys:
                sample_keys = keys[:min(100, len(keys))]  # Sample first 100
                total_size = sum(len(self.redis.get(k) or "") for k in sample_keys)
                avg_size = total_size / len(sample_keys) if sample_keys else 0
                cache_size_mb = (avg_size * len(keys)) / (1024 * 1024)

            return {
                "healthy": redis_healthy,
                "redis_connected": redis_healthy,
                "active_entries": active_entries,
                "hit_rate": self.get_hit_rate(),
                "cache_size_mb": cache_size_mb,
                "default_ttl_seconds": self.default_ttl_seconds
            }

        except Exception as e:
            logger.error(f"L2 health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
