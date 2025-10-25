"""
L3 Semantic/RAG Caching Service

Implements semantic similarity-based caching using vector embeddings.

Key Features:
- Vector embeddings for semantic matching
- Cosine similarity threshold (default 0.85)
- OpenAI text-embedding-3-small (1536 dimensions)
- Redis for vector storage
- Approximate nearest neighbor search

Note: For production, consider using specialized vector databases like:
- Pinecone
- Weaviate
- Qdrant
- Redis with RediSearch module
"""

import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from redis import Redis
import json

from models.helios.cache_models import (
    L3SemanticEmbedding,
    CacheHit,
    CacheLayer
)

logger = logging.getLogger(__name__)


class L3SemanticRAGService:
    """
    L3 Semantic/RAG Caching Service

    Uses vector embeddings for semantic similarity matching.
    """

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        embedding_function: Optional[callable] = None
    ):
        """
        Initialize L3 Semantic RAG Service

        Args:
            redis_client: Redis client instance
            embedding_function: Function to generate embeddings (input: str -> List[float])
        """
        self.redis = redis_client or Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.embedding_function = embedding_function or self._mock_embedding_function

        # Configuration
        self.similarity_threshold = 0.85  # 85% similarity required for hit
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
        self.default_ttl_seconds = 86400  # 24 hours
        self.max_ttl_seconds = 604800  # 7 days

        # Metrics
        self.total_lookups = 0
        self.total_hits = 0
        self.similarity_scores = []

        logger.info(f"L3 Semantic RAG Cache initialized "
                   f"(similarity threshold: {self.similarity_threshold}, dim: {self.embedding_dimension})")

    def _mock_embedding_function(self, text: str) -> List[float]:
        """
        Mock embedding function for testing

        Args:
            text: Input text

        Returns:
            Random 1536-dim vector (normalized)
        """
        # For production, replace with actual embedding API call
        # e.g., OpenAI, Cohere, or local model
        np.random.seed(hash(text) % (2**32))
        vector = np.random.randn(self.embedding_dimension)
        # Normalize
        vector = vector / np.linalg.norm(vector)
        return vector.tolist()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0.0 to 1.0)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Cosine similarity = dot(v1, v2) / (norm(v1) * norm(v2))
        # If vectors are normalized, this simplifies to dot(v1, v2)
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)

        if norm_product == 0:
            return 0.0

        return dot_product / norm_product

    def _generate_embedding_id(self, input_text: str, task_type: str) -> str:
        """
        Generate unique embedding ID

        Args:
            input_text: Input text
            task_type: Task type

        Returns:
            Unique ID
        """
        combined = f"{task_type}:{input_text}:{datetime.utcnow().isoformat()}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    async def lookup(
        self,
        input_text: str,
        task_type: str,
        similarity_threshold: Optional[float] = None
    ) -> Tuple[CacheHit, Optional[Dict[str, Any]]]:
        """
        Lookup cached response by semantic similarity

        Args:
            input_text: Input text to lookup
            task_type: Type of task
            similarity_threshold: Custom threshold (default: 0.85)

        Returns:
            Tuple of (CacheHit, cached_response)
        """
        self.total_lookups += 1
        threshold = similarity_threshold or self.similarity_threshold

        try:
            # Generate embedding for input
            query_embedding = self.embedding_function(input_text)

            # Get all embeddings for this task type
            embedding_keys = self.redis.keys(f"helios:l3_cache:{task_type}:*")

            if not embedding_keys:
                logger.debug(f"L3 cache MISS: No embeddings for task type {task_type}")
                return CacheHit(hit=False), None

            best_match = None
            best_similarity = 0.0
            best_entry = None

            # Scan all embeddings and find best match
            for key in embedding_keys:
                cache_data = self.redis.get(key)
                if not cache_data:
                    continue

                try:
                    entry = L3SemanticEmbedding.parse_raw(cache_data)

                    # Check if expired
                    if entry.is_expired():
                        self.redis.delete(key)
                        continue

                    # Calculate similarity
                    similarity = self._cosine_similarity(query_embedding, entry.embedding_vector)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = key
                        best_entry = entry

                except Exception as e:
                    logger.error(f"Error processing embedding {key}: {e}")
                    continue

            # Check if best match exceeds threshold
            if best_similarity >= threshold:
                # Cache hit!
                best_entry.access_count += 1
                best_entry.last_accessed = datetime.utcnow()

                # Update average similarity
                if best_entry.avg_similarity_on_hit == 0:
                    best_entry.avg_similarity_on_hit = best_similarity
                else:
                    # Exponential moving average
                    alpha = 0.3
                    best_entry.avg_similarity_on_hit = (
                        alpha * best_similarity +
                        (1 - alpha) * best_entry.avg_similarity_on_hit
                    )

                # Save updated entry
                remaining_ttl = best_entry.ttl_seconds - int(
                    (datetime.utcnow() - best_entry.created_at).total_seconds()
                )

                if remaining_ttl > 0:
                    self.redis.set(best_match, best_entry.json(), ex=remaining_ttl)

                self.total_hits += 1
                self.similarity_scores.append(best_similarity)

                logger.info(f"L3 cache HIT for task {task_type} "
                           f"(similarity: {best_similarity:.3f}, access #{best_entry.access_count})")

                return (
                    CacheHit(
                        hit=True,
                        layer=CacheLayer.L3_SEMANTIC_RAG,
                        confidence=best_similarity,
                        entry_id=best_entry.embedding_id,
                        created_at=best_entry.created_at,
                        ttl_seconds=remaining_ttl
                    ),
                    best_entry.cached_response
                )
            else:
                # No match above threshold
                logger.debug(f"L3 cache MISS: Best similarity {best_similarity:.3f} < {threshold}")
                return CacheHit(hit=False), None

        except Exception as e:
            logger.error(f"L3 cache lookup error: {e}")
            return CacheHit(hit=False), None

    async def store(
        self,
        input_text: str,
        response_data: Dict[str, Any],
        task_type: str,
        model_used: str,
        ttl_seconds: Optional[int] = None,
        tokens_used: int = 0
    ) -> bool:
        """
        Store response with semantic embedding

        Args:
            input_text: Input text
            response_data: Response to cache
            task_type: Type of task
            model_used: Model that generated response
            ttl_seconds: Time to live (default: 24 hours)
            tokens_used: Tokens in response

        Returns:
            True if stored successfully
        """
        embedding_id = self._generate_embedding_id(input_text, task_type)

        # Use default or provided TTL
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl_seconds
        else:
            ttl_seconds = min(ttl_seconds, self.max_ttl_seconds)

        try:
            # Generate embedding
            embedding_vector = self.embedding_function(input_text)

            cache_entry = L3SemanticEmbedding(
                embedding_id=embedding_id,
                input_text=input_text,
                embedding_vector=embedding_vector,
                cached_response=response_data,
                task_type=task_type,
                model_used=model_used,
                created_at=datetime.utcnow(),
                ttl_seconds=ttl_seconds
            )

            # Estimate cost savings
            if tokens_used > 0:
                output_cost = (tokens_used / 1_000_000) * 15.0  # $15/1M output tokens
                cache_entry.cost_saved = output_cost

            # Store in Redis
            key = f"helios:l3_cache:{task_type}:{embedding_id}"
            self.redis.set(key, cache_entry.json(), ex=ttl_seconds)

            logger.info(f"L3 cache STORED: {embedding_id[:8]}... "
                       f"(task: {task_type}, TTL: {ttl_seconds}s, tokens: {tokens_used})")

            # Update metrics
            self._update_metrics(cache_entry)

            return True

        except Exception as e:
            logger.error(f"L3 cache store error: {e}")
            return False

    def _update_metrics(self, cache_entry: L3SemanticEmbedding):
        """
        Update aggregate metrics

        Args:
            cache_entry: Cache entry to add to metrics
        """
        try:
            self.redis.hincrby("helios:l3_metrics", "total_entries", 1)
            self.redis.hincrby("helios:l3_metrics", "total_tokens_cached", cache_entry.tokens_saved)
            self.redis.hincrbyfloat("helios:l3_metrics", "total_potential_savings", cache_entry.cost_saved)

        except Exception as e:
            logger.error(f"Failed to update L3 metrics: {e}")

    def get_hit_rate(self) -> float:
        """
        Get L3 cache hit rate

        Returns:
            Hit rate (0.0 to 1.0)
        """
        if self.total_lookups == 0:
            return 0.0
        return self.total_hits / self.total_lookups

    def get_avg_similarity(self) -> float:
        """
        Get average similarity score on hits

        Returns:
            Average similarity (0.0 to 1.0)
        """
        if not self.similarity_scores:
            return 0.0
        return sum(self.similarity_scores) / len(self.similarity_scores)

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get L3 cache metrics

        Returns:
            Metrics dictionary
        """
        try:
            metrics = self.redis.hgetall("helios:l3_metrics")

            total_entries = int(metrics.get("total_entries", 0))
            total_tokens = int(metrics.get("total_tokens_cached", 0))
            total_savings = float(metrics.get("total_potential_savings", 0.0))

            # Get current cache size
            keys = self.redis.keys("helios:l3_cache:*")
            active_entries = len(keys) if keys else 0

            # Actual savings
            actual_savings = total_savings * self.total_hits if total_savings > 0 else 0

            return {
                "layer": "L3_Semantic_RAG",
                "hit_rate": self.get_hit_rate(),
                "avg_similarity_on_hit": self.get_avg_similarity(),
                "similarity_threshold": self.similarity_threshold,
                "total_lookups": self.total_lookups,
                "total_hits": self.total_hits,
                "total_entries_stored": total_entries,
                "active_entries": active_entries,
                "total_tokens_cached": total_tokens,
                "potential_savings_per_hit_dollars": total_savings,
                "actual_savings_dollars": actual_savings,
                "embedding_dimension": self.embedding_dimension,
                "default_ttl_seconds": self.default_ttl_seconds
            }

        except Exception as e:
            logger.error(f"Failed to get L3 metrics: {e}")
            return {
                "layer": "L3_Semantic_RAG",
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
            keys = self.redis.keys(f"helios:l3_cache:{task_type}:*")
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Invalidated {count} L3 cache entries for task type: {task_type}")
                return count
            return 0

        except Exception as e:
            logger.error(f"L3 invalidation error: {e}")
            return 0

    async def invalidate_all(self) -> int:
        """
        Invalidate all L3 cache entries

        Returns:
            Number of entries invalidated
        """
        try:
            keys = self.redis.keys("helios:l3_cache:*")
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Invalidated {count} L3 cache entries")
                return count
            return 0

        except Exception as e:
            logger.error(f"L3 invalidation error: {e}")
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
            keys = self.redis.keys("helios:l3_cache:*")
            active_entries = len(keys) if keys else 0

            # Estimate cache size (embeddings are larger)
            cache_size_mb = 0.0
            if keys:
                sample_keys = keys[:min(50, len(keys))]  # Sample first 50
                total_size = sum(len(self.redis.get(k) or "") for k in sample_keys)
                avg_size = total_size / len(sample_keys) if sample_keys else 0
                cache_size_mb = (avg_size * len(keys)) / (1024 * 1024)

            return {
                "healthy": redis_healthy,
                "redis_connected": redis_healthy,
                "active_entries": active_entries,
                "hit_rate": self.get_hit_rate(),
                "avg_similarity": self.get_avg_similarity(),
                "cache_size_mb": cache_size_mb,
                "similarity_threshold": self.similarity_threshold,
                "embedding_dimension": self.embedding_dimension
            }

        except Exception as e:
            logger.error(f"L3 health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
