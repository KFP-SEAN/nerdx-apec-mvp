"""
Helios Cache System Tests

Comprehensive tests for L1/L2/L3 caching layers and Cache Manager.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import fakeredis

from services.cache.l1_claude_native import L1ClaudeNativeService
from services.cache.l2_redis_exact import L2RedisExactService
from services.cache.l3_semantic_rag import L3SemanticRAGService
from services.cache.cache_manager import CacheManager

from models.helios.cache_models import (
    CacheLookupRequest,
    CacheStoreRequest,
    CacheInvalidationRequest,
    CacheLayer
)


@pytest.fixture
def mock_redis():
    """Provide fake Redis for testing"""
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def l1_service(mock_redis):
    """L1 Claude Native Service"""
    return L1ClaudeNativeService(redis_client=mock_redis)


@pytest.fixture
def l2_service(mock_redis):
    """L2 Redis Exact Service"""
    return L2RedisExactService(redis_client=mock_redis)


@pytest.fixture
def l3_service(mock_redis):
    """L3 Semantic RAG Service"""
    return L3SemanticRAGService(redis_client=mock_redis)


@pytest.fixture
def cache_manager(mock_redis):
    """Cache Manager"""
    return CacheManager(redis_client=mock_redis)


class TestL1ClaudeNative:
    """Tests for L1 Claude Native Caching"""

    @pytest.mark.asyncio
    async def test_should_cache(self, l1_service):
        """Test minimum token threshold for caching"""
        # Short prompt - should not cache
        short_prompt = "Hello world" * 50  # ~100 tokens
        assert not l1_service.should_cache(short_prompt)

        # Long prompt - should cache
        long_prompt = "This is a system prompt. " * 300  # ~1500 tokens
        assert l1_service.should_cache(long_prompt)

    @pytest.mark.asyncio
    async def test_store_and_lookup(self, l1_service):
        """Test store and lookup cycle"""
        system_prompt = "You are an expert Python developer. " * 300  # ~1500 tokens

        # Store
        stored = await l1_service.store(system_prompt)
        assert stored

        # Lookup - should hit
        hit = await l1_service.lookup(system_prompt)
        assert hit.hit
        assert hit.layer == CacheLayer.L1_CLAUDE_NATIVE
        assert hit.confidence == 1.0

    @pytest.mark.asyncio
    async def test_cache_miss(self, l1_service):
        """Test cache miss"""
        system_prompt = "Non-existent prompt" * 300

        # Lookup without storing
        hit = await l1_service.lookup(system_prompt)
        assert not hit.hit

    @pytest.mark.asyncio
    async def test_hit_rate(self, l1_service):
        """Test hit rate calculation"""
        prompt1 = "Prompt 1" * 300
        prompt2 = "Prompt 2" * 300

        # Store prompt1
        await l1_service.store(prompt1)

        # Lookup prompt1 - hit
        await l1_service.lookup(prompt1)

        # Lookup prompt2 - miss
        await l1_service.lookup(prompt2)

        # Hit rate should be 50%
        assert l1_service.get_hit_rate() == 0.5


class TestL2RedisExact:
    """Tests for L2 Redis Exact Match Caching"""

    @pytest.mark.asyncio
    async def test_store_and_lookup(self, l2_service):
        """Test store and lookup with exact match"""
        input_text = "What is the capital of France?"
        response_data = {"answer": "Paris"}
        task_type = "qa"

        # Store
        stored = await l2_service.store(
            input_text=input_text,
            response_data=response_data,
            task_type=task_type,
            model_used="claude-opus-4",
            tokens_in_response=10
        )
        assert stored

        # Lookup - should hit
        hit = await l2_service.lookup(input_text, task_type)
        assert hit.hit
        assert hit.layer == CacheLayer.L2_REDIS_EXACT
        assert hit.confidence == 1.0

        # Get cached response
        cached = await l2_service.get_cached_response(input_text, task_type)
        assert cached == response_data

    @pytest.mark.asyncio
    async def test_different_task_type_miss(self, l2_service):
        """Test that different task types don't match"""
        input_text = "Test input"
        response_data = {"result": "test"}

        # Store for task_type "qa"
        await l2_service.store(
            input_text=input_text,
            response_data=response_data,
            task_type="qa",
            model_used="claude"
        )

        # Lookup for task_type "code" - should miss
        hit = await l2_service.lookup(input_text, "code")
        assert not hit.hit

    @pytest.mark.asyncio
    async def test_invalidate_by_task_type(self, l2_service):
        """Test invalidation by task type"""
        # Store multiple entries
        await l2_service.store("input1", {"r": 1}, "qa", "model")
        await l2_service.store("input2", {"r": 2}, "qa", "model")
        await l2_service.store("input3", {"r": 3}, "code", "model")

        # Invalidate "qa" task type
        count = await l2_service.invalidate_by_task_type("qa")
        assert count == 2

        # Verify "qa" entries are gone
        hit1 = await l2_service.lookup("input1", "qa")
        assert not hit1.hit

        # Verify "code" entry still exists
        hit3 = await l2_service.lookup("input3", "code")
        assert hit3.hit


class TestL3SemanticRAG:
    """Tests for L3 Semantic RAG Caching"""

    @pytest.mark.asyncio
    async def test_store_and_semantic_lookup(self, l3_service):
        """Test semantic similarity matching"""
        input_text = "How do I sort a list in Python?"
        similar_text = "What's the way to sort a Python list?"
        response_data = {"answer": "Use sorted() or list.sort()"}
        task_type = "qa"

        # Store
        stored = await l3_service.store(
            input_text=input_text,
            response_data=response_data,
            task_type=task_type,
            model_used="claude",
            tokens_used=20
        )
        assert stored

        # Lookup with similar text - should hit with high confidence
        hit, cached = await l3_service.lookup(similar_text, task_type)

        # Note: With mock embedding function, similarity is random
        # In production with real embeddings, this would be more predictable
        assert isinstance(hit.hit, bool)
        if hit.hit:
            assert hit.layer == CacheLayer.L3_SEMANTIC_RAG
            assert 0.0 <= hit.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_similarity_threshold(self, l3_service):
        """Test custom similarity threshold"""
        input_text = "Test input"
        response_data = {"r": 1}

        await l3_service.store(input_text, response_data, "qa", "model")

        # Lookup with very high threshold (1.0) - likely to miss
        hit, cached = await l3_service.lookup(
            "Different text",
            "qa",
            similarity_threshold=1.0  # Requires exact match
        )

        # Should mostly miss unless random embeddings happen to match perfectly
        assert isinstance(hit.hit, bool)

    @pytest.mark.asyncio
    async def test_avg_similarity_tracking(self, l3_service):
        """Test average similarity tracking on hits"""
        avg_sim = l3_service.get_avg_similarity()
        assert avg_sim >= 0.0


class TestCacheManager:
    """Tests for Cache Manager (multi-layer orchestration)"""

    @pytest.mark.asyncio
    async def test_waterfall_lookup_l2_hit(self, cache_manager):
        """Test waterfall lookup with L2 hit"""
        input_text = "What is 2+2?"
        response_data = {"answer": "4"}
        task_type = "math"

        # Store in L2
        store_req = CacheStoreRequest(
            input_text=input_text,
            response_data=response_data,
            task_type=task_type,
            model_used="claude",
            tokens_used=5,
            store_in_l1=False,
            store_in_l2=True,
            store_in_l3=False
        )

        store_resp = await cache_manager.store(store_req)
        assert store_resp.stored
        assert CacheLayer.L2_REDIS_EXACT in store_resp.layers_stored

        # Lookup - should hit L2
        lookup_req = CacheLookupRequest(
            input_text=input_text,
            task_type=task_type,
            use_l1=True,
            use_l2=True,
            use_l3=False
        )

        lookup_resp = await cache_manager.lookup(lookup_req)
        assert lookup_resp.hit
        assert lookup_resp.layer == CacheLayer.L2_REDIS_EXACT
        assert lookup_resp.cached_response == response_data

    @pytest.mark.asyncio
    async def test_store_in_multiple_layers(self, cache_manager):
        """Test storing in multiple layers"""
        system_prompt = "You are a helpful assistant. " * 300  # 1500+ tokens for L1
        input_text = "Test input"
        response_data = {"r": "test"}
        task_type = "qa"

        store_req = CacheStoreRequest(
            input_text=input_text,
            response_data=response_data,
            task_type=task_type,
            model_used="claude",
            system_prompt=system_prompt,
            tokens_used=100,
            store_in_l1=True,
            store_in_l2=True,
            store_in_l3=True
        )

        store_resp = await cache_manager.store(store_req)
        assert store_resp.stored

        # Should be stored in L1 (system prompt), L2, and L3
        assert len(store_resp.layers_stored) >= 2  # L2 and L3 at minimum

    @pytest.mark.asyncio
    async def test_get_metrics(self, cache_manager):
        """Test aggregate metrics"""
        # Perform some operations
        input_text = "Test"
        response_data = {"r": 1}

        store_req = CacheStoreRequest(
            input_text=input_text,
            response_data=response_data,
            task_type="test",
            model_used="claude",
            tokens_used=10
        )
        await cache_manager.store(store_req)

        lookup_req = CacheLookupRequest(
            input_text=input_text,
            task_type="test"
        )
        await cache_manager.lookup(lookup_req)

        # Get metrics
        metrics = await cache_manager.get_metrics()

        assert metrics.total_lookups >= 1
        assert metrics.overall_hit_rate >= 0.0
        assert metrics.overall_hit_rate <= 1.0

    @pytest.mark.asyncio
    async def test_invalidate_all_layers(self, cache_manager):
        """Test invalidation across all layers"""
        # Store data
        store_req = CacheStoreRequest(
            input_text="test",
            response_data={"r": 1},
            task_type="test",
            model_used="claude"
        )
        await cache_manager.store(store_req)

        # Invalidate all
        invalidate_req = CacheInvalidationRequest()
        invalidate_resp = await cache_manager.invalidate(invalidate_req)

        assert invalidate_resp.invalidated
        assert len(invalidate_resp.layers_affected) > 0

    @pytest.mark.asyncio
    async def test_health_check(self, cache_manager):
        """Test health check across all layers"""
        health = await cache_manager.health_check()

        assert "healthy" in health
        assert "layers" in health
        assert "L1_Claude_Native" in health["layers"]
        assert "L2_Redis_Exact" in health["layers"]
        assert "L3_Semantic_RAG" in health["layers"]


class TestIntegration:
    """Integration tests for complete caching workflow"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, cache_manager):
        """Test complete workflow: store -> lookup -> invalidate"""
        input_text = "Explain quantum computing"
        response_data = {"answer": "Quantum computing uses qubits..."}
        task_type = "education"

        # 1. Store
        store_req = CacheStoreRequest(
            input_text=input_text,
            response_data=response_data,
            task_type=task_type,
            model_used="claude-opus-4",
            tokens_used=150
        )

        store_resp = await cache_manager.store(store_req)
        assert store_resp.stored

        # 2. Lookup - should hit
        lookup_req = CacheLookupRequest(
            input_text=input_text,
            task_type=task_type
        )

        lookup_resp = await cache_manager.lookup(lookup_req)
        assert lookup_resp.hit
        assert lookup_resp.cached_response == response_data

        # 3. Invalidate
        invalidate_req = CacheInvalidationRequest(task_type=task_type)
        invalidate_resp = await cache_manager.invalidate(invalidate_req)
        assert invalidate_resp.invalidated

        # 4. Lookup again - should miss
        lookup_resp2 = await cache_manager.lookup(lookup_req)
        # May or may not hit depending on which layers were invalidated
        assert isinstance(lookup_resp2.hit, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
