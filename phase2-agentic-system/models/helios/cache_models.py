"""
Helios Cache Models

Data models for multi-layer caching system (L1/L2/L3).

L1: Claude Native Caching (Prompt Caching API)
L2: Redis Exact Match (Hash-based)
L3: Semantic/RAG Caching (Vector embeddings)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CacheLayer(str, Enum):
    """Cache layer types"""
    L1_CLAUDE_NATIVE = "l1_claude_native"
    L2_REDIS_EXACT = "l2_redis_exact"
    L3_SEMANTIC_RAG = "l3_semantic_rag"


class CacheStatus(str, Enum):
    """Cache entry status"""
    VALID = "valid"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"


class CacheHit(BaseModel):
    """Represents a cache hit result"""
    hit: bool = Field(default=False, description="Whether cache was hit")
    layer: Optional[CacheLayer] = Field(default=None, description="Which layer hit")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score (L3 only)")
    entry_id: Optional[str] = Field(default=None, description="Cache entry ID")
    created_at: Optional[datetime] = None
    ttl_seconds: Optional[int] = None


class L1ClaudeNativeCache(BaseModel):
    """
    L1: Claude Native Caching using Prompt Caching API

    Caches prompt prefixes up to 5 minutes.
    Cost: ~10% of regular tokens.
    """
    cache_id: str = Field(..., description="Unique cache identifier")
    system_prompt: str = Field(..., description="Cached system prompt")
    prefix_tokens: int = Field(default=0, description="Number of cached tokens")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Cache expiration (5 min)")
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0, description="Number of times accessed")

    # Status
    status: CacheStatus = Field(default=CacheStatus.VALID)

    # Metrics
    tokens_saved: int = Field(default=0, description="Total tokens saved by caching")
    cost_saved: float = Field(default=0.0, description="Cost saved in dollars")

    def is_valid(self) -> bool:
        """Check if cache is still valid"""
        return self.status == CacheStatus.VALID and datetime.utcnow() < self.expires_at

    def estimate_savings(self, input_cost_per_million: float = 3.0) -> float:
        """
        Estimate cost savings

        Args:
            input_cost_per_million: Cost per million input tokens

        Returns:
            Estimated savings in dollars
        """
        # Cached tokens cost ~10% of regular
        regular_cost = (self.prefix_tokens / 1_000_000) * input_cost_per_million
        cached_cost = regular_cost * 0.1
        return regular_cost - cached_cost


class L2RedisExactMatch(BaseModel):
    """
    L2: Redis Exact Match Caching

    Hash-based exact string matching.
    TTL: Configurable (default 1 hour).
    """
    cache_key: str = Field(..., description="MD5 hash of input")
    input_hash: str = Field(..., description="Input text hash")
    cached_response: Dict[str, Any] = Field(..., description="Cached response data")

    # Metadata
    task_type: str = Field(..., description="Type of task cached")
    model_used: str = Field(..., description="Model that generated response")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int = Field(default=3600, description="Time to live (1 hour)")

    # Access tracking
    access_count: int = Field(default=0)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    # Metrics
    tokens_in_cached_response: int = Field(default=0)
    cost_saved_per_hit: float = Field(default=0.0)

    def is_expired(self) -> bool:
        """Check if cache entry expired"""
        age_seconds = (datetime.utcnow() - self.created_at).total_seconds()
        return age_seconds > self.ttl_seconds


class L3SemanticEmbedding(BaseModel):
    """
    L3: Semantic/RAG Caching with Vector Embeddings

    Uses cosine similarity for semantic matching.
    Threshold: 0.85+ for cache hit.
    """
    embedding_id: str = Field(..., description="Unique embedding ID")
    input_text: str = Field(..., description="Original input text")
    embedding_vector: List[float] = Field(..., description="Embedding vector (e.g., 1536 dims)")
    cached_response: Dict[str, Any] = Field(..., description="Cached response")

    # Metadata
    task_type: str = Field(..., description="Type of task")
    model_used: str = Field(..., description="Model used")
    embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int = Field(default=86400, description="24 hour TTL")

    # Access tracking
    access_count: int = Field(default=0)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    avg_similarity_on_hit: float = Field(default=0.0, description="Average similarity score")

    # Metrics
    tokens_saved: int = Field(default=0)
    cost_saved: float = Field(default=0.0)

    def is_expired(self) -> bool:
        """Check if embedding cache expired"""
        age_seconds = (datetime.utcnow() - self.created_at).total_seconds()
        return age_seconds > self.ttl_seconds


class CacheLookupRequest(BaseModel):
    """Request to lookup in cache"""
    input_text: str = Field(..., description="Input to lookup")
    task_type: str = Field(..., description="Type of task")
    system_prompt: Optional[str] = Field(default=None, description="System prompt (L1)")

    # Cache layer preferences
    use_l1: bool = Field(default=True, description="Enable L1 Claude Native")
    use_l2: bool = Field(default=True, description="Enable L2 Redis Exact")
    use_l3: bool = Field(default=True, description="Enable L3 Semantic")

    # L3 semantic matching threshold
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)


class CacheLookupResponse(BaseModel):
    """Response from cache lookup"""
    hit: bool = Field(default=False, description="Whether any cache hit")
    layer: Optional[CacheLayer] = None
    cached_response: Optional[Dict[str, Any]] = None
    confidence: float = Field(default=0.0, description="Confidence in cache hit")

    # Layer-specific results
    l1_result: Optional[CacheHit] = None
    l2_result: Optional[CacheHit] = None
    l3_result: Optional[CacheHit] = None

    # Metrics
    lookup_time_ms: float = Field(default=0.0, description="Time to lookup")
    tokens_saved: int = Field(default=0)
    cost_saved: float = Field(default=0.0)


class CacheStoreRequest(BaseModel):
    """Request to store in cache"""
    input_text: str = Field(..., description="Input text")
    response_data: Dict[str, Any] = Field(..., description="Response to cache")
    task_type: str = Field(..., description="Type of task")
    model_used: str = Field(..., description="Model that generated response")

    # Optional metadata
    system_prompt: Optional[str] = Field(default=None, description="System prompt (L1)")
    tokens_used: int = Field(default=0, description="Tokens in response")

    # Layer selection
    store_in_l1: bool = Field(default=True)
    store_in_l2: bool = Field(default=True)
    store_in_l3: bool = Field(default=True)

    # TTL configuration
    l2_ttl_seconds: int = Field(default=3600, description="L2 TTL (1 hour)")
    l3_ttl_seconds: int = Field(default=86400, description="L3 TTL (24 hours)")


class CacheStoreResponse(BaseModel):
    """Response from cache store operation"""
    stored: bool = Field(default=False, description="Whether stored successfully")
    layers_stored: List[CacheLayer] = Field(default_factory=list)
    cache_ids: Dict[str, str] = Field(default_factory=dict, description="Cache IDs per layer")

    # Errors
    errors: Dict[str, str] = Field(default_factory=dict, description="Errors per layer")


class CacheMetrics(BaseModel):
    """Aggregate cache metrics"""

    # Hit rates
    total_lookups: int = Field(default=0)
    total_hits: int = Field(default=0)
    overall_hit_rate: float = Field(default=0.0)

    # Per-layer hit rates
    l1_hit_rate: float = Field(default=0.0)
    l2_hit_rate: float = Field(default=0.0)
    l3_hit_rate: float = Field(default=0.0)

    # Savings
    total_tokens_saved: int = Field(default=0)
    total_cost_saved: float = Field(default=0.0, description="Total savings in dollars")

    # Latency
    avg_lookup_time_ms: float = Field(default=0.0)
    avg_l1_time_ms: float = Field(default=0.0)
    avg_l2_time_ms: float = Field(default=0.0)
    avg_l3_time_ms: float = Field(default=0.0)

    # Storage
    l1_entries: int = Field(default=0)
    l2_entries: int = Field(default=0)
    l3_entries: int = Field(default=0)
    total_cache_size_mb: float = Field(default=0.0)


class CacheInvalidationRequest(BaseModel):
    """Request to invalidate cache entries"""
    layer: Optional[CacheLayer] = Field(default=None, description="Specific layer or all")
    task_type: Optional[str] = Field(default=None, description="Invalidate by task type")
    older_than_hours: Optional[int] = Field(default=None, description="Invalidate older entries")


class CacheInvalidationResponse(BaseModel):
    """Response from cache invalidation"""
    invalidated: bool = Field(default=True)
    entries_invalidated: int = Field(default=0)
    layers_affected: List[CacheLayer] = Field(default_factory=list)
