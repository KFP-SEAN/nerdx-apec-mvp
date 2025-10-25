"""
Helios Cache Manager

Orchestrates multi-layer caching (L1/L2/L3) with waterfall lookup strategy.

Lookup Strategy:
1. L1 Claude Native (5-minute TTL) - System prompt caching
2. L2 Redis Exact Match (1-hour TTL) - Hash-based exact matching
3. L3 Semantic/RAG (24-hour TTL) - Vector similarity matching

Store Strategy:
- Store in all applicable layers simultaneously
- L1: Only for prompts ≥1024 tokens
- L2: All responses
- L3: All responses with embeddings
"""

import logging
import time
from typing import Optional, Dict, Any, Tuple
from redis import Redis

from services.cache.l1_claude_native import L1ClaudeNativeService
from services.cache.l2_redis_exact import L2RedisExactService
from services.cache.l3_semantic_rag import L3SemanticRAGService

from models.helios.cache_models import (
    CacheLookupRequest,
    CacheLookupResponse,
    CacheStoreRequest,
    CacheStoreResponse,
    CacheMetrics,
    CacheLayer,
    CacheInvalidationRequest,
    CacheInvalidationResponse
)

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Multi-Layer Cache Manager

    Coordinates L1/L2/L3 caching layers with waterfall lookup.
    """

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        embedding_function: Optional[callable] = None
    ):
        """
        Initialize Cache Manager

        Args:
            redis_client: Redis client for all layers
            embedding_function: Function for L3 embeddings
        """
        self.redis = redis_client or Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Initialize all three layers
        self.l1 = L1ClaudeNativeService(redis_client=self.redis)
        self.l2 = L2RedisExactService(redis_client=self.redis)
        self.l3 = L3SemanticRAGService(
            redis_client=self.redis,
            embedding_function=embedding_function
        )

        # Metrics
        self.total_lookups = 0
        self.total_hits = 0
        self.layer_hits = {
            CacheLayer.L1_CLAUDE_NATIVE: 0,
            CacheLayer.L2_REDIS_EXACT: 0,
            CacheLayer.L3_SEMANTIC_RAG: 0
        }

        logger.info("Cache Manager initialized with L1/L2/L3 layers")

    async def lookup(self, request: CacheLookupRequest) -> CacheLookupResponse:
        """
        Waterfall cache lookup across all layers

        Args:
            request: Cache lookup request

        Returns:
            CacheLookupResponse with hit status and cached data
        """
        start_time = time.time()
        self.total_lookups += 1

        response = CacheLookupResponse(
            hit=False,
            layer=None,
            cached_response=None,
            confidence=0.0
        )

        try:
            # L1: Claude Native (system prompt caching)
            if request.use_l1 and request.system_prompt:
                l1_hit = await self.l1.lookup(request.system_prompt)
                response.l1_result = l1_hit

                if l1_hit.hit:
                    # L1 cache hit - return immediately
                    response.hit = True
                    response.layer = CacheLayer.L1_CLAUDE_NATIVE
                    response.confidence = 1.0
                    # Note: L1 only caches system prompt, not full response
                    # Continue to L2/L3 for actual response caching

                    self.total_hits += 1
                    self.layer_hits[CacheLayer.L1_CLAUDE_NATIVE] += 1

                    logger.info("Cache Manager: L1 HIT (system prompt cached)")

            # L2: Redis Exact Match
            if request.use_l2:
                l2_hit = await self.l2.lookup(request.input_text, request.task_type)
                response.l2_result = l2_hit

                if l2_hit.hit:
                    # L2 cache hit - get response
                    cached_response = await self.l2.get_cached_response(request.input_text, request.task_type)

                    if cached_response:
                        response.hit = True
                        response.layer = CacheLayer.L2_REDIS_EXACT
                        response.cached_response = cached_response
                        response.confidence = 1.0

                        self.total_hits += 1
                        self.layer_hits[CacheLayer.L2_REDIS_EXACT] += 1

                        logger.info("Cache Manager: L2 HIT (exact match)")

                        # Calculate lookup time
                        response.lookup_time_ms = (time.time() - start_time) * 1000
                        return response

            # L3: Semantic/RAG
            if request.use_l3:
                l3_hit, cached_response = await self.l3.lookup(
                    request.input_text,
                    request.task_type,
                    request.similarity_threshold
                )
                response.l3_result = l3_hit

                if l3_hit.hit:
                    # L3 cache hit - semantic match
                    response.hit = True
                    response.layer = CacheLayer.L3_SEMANTIC_RAG
                    response.cached_response = cached_response
                    response.confidence = l3_hit.confidence

                    self.total_hits += 1
                    self.layer_hits[CacheLayer.L3_SEMANTIC_RAG] += 1

                    logger.info(f"Cache Manager: L3 HIT (semantic similarity: {l3_hit.confidence:.3f})")

                    # Calculate lookup time
                    response.lookup_time_ms = (time.time() - start_time) * 1000
                    return response

            # Cache miss on all layers
            if not response.hit:
                logger.debug(f"Cache Manager: MISS on all layers (task: {request.task_type})")

            # Calculate lookup time
            response.lookup_time_ms = (time.time() - start_time) * 1000

            return response

        except Exception as e:
            logger.error(f"Cache Manager lookup error: {e}")
            response.lookup_time_ms = (time.time() - start_time) * 1000
            return response

    async def store(self, request: CacheStoreRequest) -> CacheStoreResponse:
        """
        Store response in all applicable cache layers

        Args:
            request: Cache store request

        Returns:
            CacheStoreResponse with storage status
        """
        response = CacheStoreResponse(stored=False)
        layers_stored = []
        errors = {}

        try:
            # L1: Claude Native (only if system prompt ≥1024 tokens)
            if request.store_in_l1 and request.system_prompt:
                if self.l1.should_cache(request.system_prompt):
                    success = await self.l1.store(
                        system_prompt=request.system_prompt,
                        prefix_tokens=request.tokens_used  # Approximate
                    )

                    if success:
                        layers_stored.append(CacheLayer.L1_CLAUDE_NATIVE)
                        logger.debug("Stored in L1 (Claude Native)")
                    else:
                        errors["L1"] = "Failed to store in L1"

            # L2: Redis Exact Match
            if request.store_in_l2:
                success = await self.l2.store(
                    input_text=request.input_text,
                    response_data=request.response_data,
                    task_type=request.task_type,
                    model_used=request.model_used,
                    ttl_seconds=request.l2_ttl_seconds,
                    tokens_in_response=request.tokens_used
                )

                if success:
                    layers_stored.append(CacheLayer.L2_REDIS_EXACT)
                    logger.debug("Stored in L2 (Redis Exact)")
                else:
                    errors["L2"] = "Failed to store in L2"

            # L3: Semantic/RAG
            if request.store_in_l3:
                success = await self.l3.store(
                    input_text=request.input_text,
                    response_data=request.response_data,
                    task_type=request.task_type,
                    model_used=request.model_used,
                    ttl_seconds=request.l3_ttl_seconds,
                    tokens_used=request.tokens_used
                )

                if success:
                    layers_stored.append(CacheLayer.L3_SEMANTIC_RAG)
                    logger.debug("Stored in L3 (Semantic RAG)")
                else:
                    errors["L3"] = "Failed to store in L3"

            # Update response
            response.stored = len(layers_stored) > 0
            response.layers_stored = layers_stored
            response.errors = errors

            if response.stored:
                logger.info(f"Cache Manager: Stored in {len(layers_stored)} layer(s): "
                           f"{[l.value for l in layers_stored]}")

            return response

        except Exception as e:
            logger.error(f"Cache Manager store error: {e}")
            response.errors["Manager"] = str(e)
            return response

    async def get_metrics(self) -> CacheMetrics:
        """
        Get aggregate cache metrics from all layers

        Returns:
            CacheMetrics with consolidated data
        """
        try:
            # Get metrics from each layer
            l1_metrics = await self.l1.get_metrics()
            l2_metrics = await self.l2.get_metrics()
            l3_metrics = await self.l3.get_metrics()

            # Calculate overall hit rate
            overall_hit_rate = self.total_hits / self.total_lookups if self.total_lookups > 0 else 0.0

            # Calculate per-layer hit rates
            l1_hit_rate = self.l1.get_hit_rate()
            l2_hit_rate = self.l2.get_hit_rate()
            l3_hit_rate = self.l3.get_hit_rate()

            # Aggregate savings
            total_cost_saved = (
                l1_metrics.get("total_savings_dollars", 0) +
                l2_metrics.get("actual_savings_dollars", 0) +
                l3_metrics.get("actual_savings_dollars", 0)
            )

            # Aggregate token savings
            total_tokens_saved = (
                l1_metrics.get("total_tokens_cached", 0) +
                l2_metrics.get("total_tokens_cached", 0) +
                l3_metrics.get("total_tokens_cached", 0)
            )

            # Storage counts
            l1_entries = l1_metrics.get("active_entries", 0)
            l2_entries = l2_metrics.get("active_entries", 0)
            l3_entries = l3_metrics.get("active_entries", 0)

            metrics = CacheMetrics(
                total_lookups=self.total_lookups,
                total_hits=self.total_hits,
                overall_hit_rate=overall_hit_rate,
                l1_hit_rate=l1_hit_rate,
                l2_hit_rate=l2_hit_rate,
                l3_hit_rate=l3_hit_rate,
                total_tokens_saved=total_tokens_saved,
                total_cost_saved=total_cost_saved,
                l1_entries=l1_entries,
                l2_entries=l2_entries,
                l3_entries=l3_entries
            )

            return metrics

        except Exception as e:
            logger.error(f"Cache Manager get metrics error: {e}")
            return CacheMetrics()

    async def invalidate(self, request: CacheInvalidationRequest) -> CacheInvalidationResponse:
        """
        Invalidate cache entries across layers

        Args:
            request: Invalidation request

        Returns:
            CacheInvalidationResponse with results
        """
        total_invalidated = 0
        layers_affected = []

        try:
            # Determine which layers to invalidate
            layers_to_invalidate = []

            if request.layer:
                # Specific layer
                layers_to_invalidate = [request.layer]
            else:
                # All layers
                layers_to_invalidate = [
                    CacheLayer.L1_CLAUDE_NATIVE,
                    CacheLayer.L2_REDIS_EXACT,
                    CacheLayer.L3_SEMANTIC_RAG
                ]

            for layer in layers_to_invalidate:
                count = 0

                if layer == CacheLayer.L1_CLAUDE_NATIVE:
                    count = await self.l1.invalidate_all()
                elif layer == CacheLayer.L2_REDIS_EXACT:
                    if request.task_type:
                        count = await self.l2.invalidate_by_task_type(request.task_type)
                    else:
                        count = await self.l2.invalidate_all()
                elif layer == CacheLayer.L3_SEMANTIC_RAG:
                    if request.task_type:
                        count = await self.l3.invalidate_by_task_type(request.task_type)
                    else:
                        count = await self.l3.invalidate_all()

                if count > 0:
                    total_invalidated += count
                    layers_affected.append(layer)

            logger.info(f"Cache Manager: Invalidated {total_invalidated} entries "
                       f"across {len(layers_affected)} layer(s)")

            return CacheInvalidationResponse(
                invalidated=True,
                entries_invalidated=total_invalidated,
                layers_affected=layers_affected
            )

        except Exception as e:
            logger.error(f"Cache Manager invalidation error: {e}")
            return CacheInvalidationResponse(
                invalidated=False,
                entries_invalidated=0,
                layers_affected=[]
            )

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all cache layers

        Returns:
            Health status
        """
        try:
            l1_health = await self.l1.health_check()
            l2_health = await self.l2.health_check()
            l3_health = await self.l3.health_check()

            all_healthy = (
                l1_health.get("healthy", False) and
                l2_health.get("healthy", False) and
                l3_health.get("healthy", False)
            )

            return {
                "healthy": all_healthy,
                "layers": {
                    "L1_Claude_Native": l1_health,
                    "L2_Redis_Exact": l2_health,
                    "L3_Semantic_RAG": l3_health
                },
                "overall_hit_rate": self.total_hits / self.total_lookups if self.total_lookups > 0 else 0.0,
                "total_lookups": self.total_lookups,
                "total_hits": self.total_hits
            }

        except Exception as e:
            logger.error(f"Cache Manager health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
