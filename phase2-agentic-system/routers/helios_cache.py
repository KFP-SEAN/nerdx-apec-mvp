"""
Helios Cache Management API

REST API endpoints for multi-layer caching control and monitoring.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from services.cache.cache_manager import CacheManager
from models.helios.cache_models import (
    CacheLookupRequest,
    CacheLookupResponse,
    CacheStoreRequest,
    CacheStoreResponse,
    CacheMetrics,
    CacheInvalidationRequest,
    CacheInvalidationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/helios/cache", tags=["Helios Cache"])

# Global Cache Manager instance
cache_manager = CacheManager()


@router.post("/lookup", response_model=CacheLookupResponse)
async def lookup_cache(request: CacheLookupRequest):
    """
    Lookup cached response across all layers

    Waterfall strategy:
    1. L1 Claude Native (system prompt)
    2. L2 Redis Exact Match
    3. L3 Semantic/RAG

    Returns first hit or miss if not found.
    """
    try:
        response = await cache_manager.lookup(request)
        return response

    except Exception as e:
        logger.error(f"Cache lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/store", response_model=CacheStoreResponse)
async def store_in_cache(request: CacheStoreRequest):
    """
    Store response in cache layers

    Stores in all enabled layers:
    - L1: If system prompt ≥1024 tokens
    - L2: All responses
    - L3: All responses with embeddings
    """
    try:
        response = await cache_manager.store(request)
        return response

    except Exception as e:
        logger.error(f"Cache store error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=CacheMetrics)
async def get_cache_metrics():
    """
    Get aggregate cache metrics

    Returns:
    - Hit rates per layer
    - Total savings (tokens and cost)
    - Cache sizes
    - Lookup performance
    """
    try:
        metrics = await cache_manager.get_metrics()
        return metrics

    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate", response_model=CacheInvalidationResponse)
async def invalidate_cache(request: CacheInvalidationRequest):
    """
    Invalidate cache entries

    Options:
    - Invalidate specific layer
    - Invalidate by task type
    - Invalidate all
    """
    try:
        response = await cache_manager.invalidate(request)
        return response

    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def cache_health_check():
    """
    Health check for all cache layers

    Returns status of:
    - L1 Claude Native
    - L2 Redis Exact
    - L3 Semantic RAG
    - Redis connection
    """
    try:
        health = await cache_manager.health_check()
        return health

    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def cache_summary():
    """
    Get comprehensive cache summary

    Combines metrics and health status for dashboard view.
    """
    try:
        metrics = await cache_manager.get_metrics()
        health = await cache_manager.health_check()

        summary = {
            "status": "healthy" if health.get("healthy") else "degraded",
            "metrics": {
                "overall_hit_rate": metrics.overall_hit_rate,
                "total_lookups": metrics.total_lookups,
                "total_hits": metrics.total_hits,
                "layer_hit_rates": {
                    "L1": metrics.l1_hit_rate,
                    "L2": metrics.l2_hit_rate,
                    "L3": metrics.l3_hit_rate
                },
                "savings": {
                    "total_tokens_saved": metrics.total_tokens_saved,
                    "total_cost_saved_dollars": metrics.total_cost_saved
                },
                "storage": {
                    "L1_entries": metrics.l1_entries,
                    "L2_entries": metrics.l2_entries,
                    "L3_entries": metrics.l3_entries,
                    "total_entries": metrics.l1_entries + metrics.l2_entries + metrics.l3_entries
                }
            },
            "health": health
        }

        return summary

    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/layer/{layer}")
async def get_layer_stats(layer: str):
    """
    Get detailed statistics for specific cache layer

    Args:
        layer: "l1", "l2", or "l3"
    """
    try:
        layer_lower = layer.lower()

        if layer_lower == "l1":
            stats = await cache_manager.l1.get_metrics()
        elif layer_lower == "l2":
            stats = await cache_manager.l2.get_metrics()
        elif layer_lower == "l3":
            stats = await cache_manager.l3.get_metrics()
        else:
            raise HTTPException(status_code=400, detail="Invalid layer. Must be 'l1', 'l2', or 'l3'")

        return {
            "layer": layer_lower.upper(),
            "stats": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get layer stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
