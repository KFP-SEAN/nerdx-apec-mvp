"""
L1 Claude Native Caching Service

Implements Claude's Prompt Caching API for caching system prompts.

Key Features:
- Cache prompt prefixes up to 5 minutes
- ~90% cost savings on cached tokens
- Automatic cache breakpoint insertion
- Minimum 1024 tokens for caching benefit

References:
- https://docs.anthropic.com/claude/docs/prompt-caching
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from redis import Redis

from models.helios.cache_models import (
    L1ClaudeNativeCache,
    CacheHit,
    CacheLayer,
    CacheStatus
)

logger = logging.getLogger(__name__)


class L1ClaudeNativeService:
    """
    L1 Claude Native Caching Service

    Manages Claude's Prompt Caching API integration.
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize L1 Claude Native Service

        Args:
            redis_client: Redis client for metadata storage
        """
        self.redis = redis_client or Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Configuration
        self.cache_duration_minutes = 5
        self.min_tokens_for_caching = 1024  # Minimum for cost benefit
        self.cache_cost_multiplier = 0.1  # Cached tokens cost 10% of regular

        # Metrics
        self.total_lookups = 0
        self.total_hits = 0

        logger.info("L1 Claude Native Cache initialized (5-minute TTL)")

    def _generate_cache_id(self, system_prompt: str) -> str:
        """
        Generate unique cache ID from system prompt

        Args:
            system_prompt: System prompt text

        Returns:
            MD5 hash of system prompt
        """
        return hashlib.md5(system_prompt.encode('utf-8')).hexdigest()

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 chars per token
        return len(text) // 4

    def should_cache(self, system_prompt: str) -> bool:
        """
        Determine if system prompt should be cached

        Args:
            system_prompt: System prompt text

        Returns:
            True if worth caching (≥1024 tokens)
        """
        estimated_tokens = self._estimate_tokens(system_prompt)
        return estimated_tokens >= self.min_tokens_for_caching

    async def lookup(self, system_prompt: str) -> CacheHit:
        """
        Lookup system prompt in L1 cache

        Args:
            system_prompt: System prompt to lookup

        Returns:
            CacheHit result
        """
        self.total_lookups += 1
        cache_id = self._generate_cache_id(system_prompt)

        try:
            # Check Redis for cache metadata
            cache_data = self.redis.get(f"helios:l1_cache:{cache_id}")

            if cache_data:
                cache_entry = L1ClaudeNativeCache.parse_raw(cache_data)

                # Check if still valid
                if cache_entry.is_valid():
                    # Update access metrics
                    cache_entry.access_count += 1
                    cache_entry.last_accessed = datetime.utcnow()

                    # Save updated metrics
                    self.redis.set(
                        f"helios:l1_cache:{cache_id}",
                        cache_entry.json(),
                        ex=int((cache_entry.expires_at - datetime.utcnow()).total_seconds())
                    )

                    self.total_hits += 1

                    logger.info(f"L1 cache HIT for {cache_id} (access #{cache_entry.access_count})")

                    return CacheHit(
                        hit=True,
                        layer=CacheLayer.L1_CLAUDE_NATIVE,
                        confidence=1.0,
                        entry_id=cache_id,
                        created_at=cache_entry.created_at,
                        ttl_seconds=int((cache_entry.expires_at - datetime.utcnow()).total_seconds())
                    )
                else:
                    # Expired
                    logger.info(f"L1 cache EXPIRED for {cache_id}")
                    self.redis.delete(f"helios:l1_cache:{cache_id}")

            # Cache miss
            logger.debug(f"L1 cache MISS for {cache_id}")
            return CacheHit(hit=False)

        except Exception as e:
            logger.error(f"L1 cache lookup error: {e}")
            return CacheHit(hit=False)

    async def store(
        self,
        system_prompt: str,
        prefix_tokens: Optional[int] = None
    ) -> bool:
        """
        Store system prompt in L1 cache

        Args:
            system_prompt: System prompt to cache
            prefix_tokens: Actual token count (if known)

        Returns:
            True if stored successfully
        """
        cache_id = self._generate_cache_id(system_prompt)

        # Estimate tokens if not provided
        if prefix_tokens is None:
            prefix_tokens = self._estimate_tokens(system_prompt)

        # Check if worth caching
        if prefix_tokens < self.min_tokens_for_caching:
            logger.debug(f"L1 cache SKIP: {prefix_tokens} tokens < {self.min_tokens_for_caching} minimum")
            return False

        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=self.cache_duration_minutes)

            cache_entry = L1ClaudeNativeCache(
                cache_id=cache_id,
                system_prompt=system_prompt,
                prefix_tokens=prefix_tokens,
                created_at=now,
                expires_at=expires_at
            )

            # Store in Redis with TTL
            ttl_seconds = int(self.cache_duration_minutes * 60)
            self.redis.set(
                f"helios:l1_cache:{cache_id}",
                cache_entry.json(),
                ex=ttl_seconds
            )

            logger.info(f"L1 cache STORED: {cache_id} ({prefix_tokens} tokens, {self.cache_duration_minutes} min TTL)")

            # Update metrics
            self._update_metrics(cache_entry)

            return True

        except Exception as e:
            logger.error(f"L1 cache store error: {e}")
            return False

    def _update_metrics(self, cache_entry: L1ClaudeNativeCache):
        """
        Update aggregate metrics

        Args:
            cache_entry: Cache entry to add to metrics
        """
        try:
            # Track savings
            savings = cache_entry.estimate_savings()

            # Update Redis metrics
            self.redis.hincrby("helios:l1_metrics", "total_entries", 1)
            self.redis.hincrbyfloat("helios:l1_metrics", "total_savings", savings)
            self.redis.hincrby("helios:l1_metrics", "total_tokens_cached", cache_entry.prefix_tokens)

        except Exception as e:
            logger.error(f"Failed to update L1 metrics: {e}")

    def prepare_cached_messages(
        self,
        system_prompt: str,
        user_messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages with cache breakpoint for Claude API

        Args:
            system_prompt: System prompt to cache
            user_messages: User messages

        Returns:
            Messages formatted for Claude API with cache_control
        """
        messages = []

        # Add system message with cache breakpoint
        if system_prompt:
            messages.append({
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # Cache breakpoint
                    }
                ]
            })

        # Add user messages
        messages.extend(user_messages)

        return messages

    def get_hit_rate(self) -> float:
        """
        Get L1 cache hit rate

        Returns:
            Hit rate (0.0 to 1.0)
        """
        if self.total_lookups == 0:
            return 0.0
        return self.total_hits / self.total_lookups

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get L1 cache metrics

        Returns:
            Metrics dictionary
        """
        try:
            metrics = self.redis.hgetall("helios:l1_metrics")

            total_entries = int(metrics.get("total_entries", 0))
            total_savings = float(metrics.get("total_savings", 0.0))
            total_tokens = int(metrics.get("total_tokens_cached", 0))

            return {
                "layer": "L1_Claude_Native",
                "hit_rate": self.get_hit_rate(),
                "total_lookups": self.total_lookups,
                "total_hits": self.total_hits,
                "total_entries": total_entries,
                "total_tokens_cached": total_tokens,
                "total_savings_dollars": total_savings,
                "cache_duration_minutes": self.cache_duration_minutes
            }

        except Exception as e:
            logger.error(f"Failed to get L1 metrics: {e}")
            return {
                "layer": "L1_Claude_Native",
                "error": str(e)
            }

    async def invalidate_all(self) -> int:
        """
        Invalidate all L1 cache entries

        Returns:
            Number of entries invalidated
        """
        try:
            # Find all L1 cache keys
            keys = self.redis.keys("helios:l1_cache:*")
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Invalidated {count} L1 cache entries")
                return count
            return 0

        except Exception as e:
            logger.error(f"L1 invalidation error: {e}")
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
            keys = self.redis.keys("helios:l1_cache:*")
            active_entries = len(keys) if keys else 0

            return {
                "healthy": redis_healthy,
                "redis_connected": redis_healthy,
                "active_entries": active_entries,
                "hit_rate": self.get_hit_rate(),
                "cache_duration_minutes": self.cache_duration_minutes
            }

        except Exception as e:
            logger.error(f"L1 health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
