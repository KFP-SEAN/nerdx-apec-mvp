"""
Helios Integration Tests

Comprehensive integration tests for all Helios components.
"""

import pytest
import asyncio
from datetime import datetime

# Import all Helios components
from services.orchestrator.resource_governor import ResourceGovernor
from services.orchestrator.economic_router import EconomicRouter
from services.cache.cache_manager import CacheManager
from services.monitoring.metrics_collector import MetricsCollector
from models.helios.usage_models import *
from models.helios.cache_models import *
from models.helios.monitoring_models import *


@pytest.mark.asyncio
async def test_resource_governor_basic():
    """Test Resource Governor basic operations"""
    governor = ResourceGovernor()
    
    # Get budget status
    status = await governor.get_budget_status()
    assert status.max_messages_per_window == 900
    assert status.utilization_percentage >= 0
    
    # Request resources
    request = TaskResourceRequest(
        task_id="test-001",
        task_type="test",
        estimated_complexity=TaskComplexity.MODERATE,
        priority=TaskPriority.NORMAL,
        estimated_tokens=1000
    )
    
    allocation = await governor.request_resources(request)
    assert allocation.approved == True
    assert allocation.model_allocated in [ModelType.OPUS_4, ModelType.SONNET_4_5]
    
    print(f"✅ Resource Governor test passed - Model: {allocation.model_allocated}")


@pytest.mark.asyncio
async def test_cache_manager_workflow():
    """Test Cache Manager complete workflow"""
    cache_manager = CacheManager()
    
    # 1. Lookup (should miss)
    lookup_request = CacheLookupRequest(
        input_text="test query",
        task_type="test",
        system_prompt="You are a test assistant",
        use_l1=True,
        use_l2=True,
        use_l3=True
    )
    
    lookup_response = await cache_manager.lookup(lookup_request)
    assert lookup_response.hit == False
    
    # 2. Store
    store_request = CacheStoreRequest(
        input_text="test query",
        response_data={"answer": "test answer"},
        task_type="test",
        model_used="claude-sonnet-4.5",
        system_prompt="You are a test assistant",
        tokens_used=100,
        store_in_l1=True,
        store_in_l2=True,
        store_in_l3=True
    )
    
    store_response = await cache_manager.store(store_request)
    assert len(store_response.layers_stored) > 0
    
    print(f"✅ Cache Manager test passed - Stored in: {store_response.layers_stored}")


@pytest.mark.asyncio
async def test_metrics_collector():
    """Test Metrics Collector"""
    governor = ResourceGovernor()
    cache_manager = CacheManager()
    metrics = MetricsCollector(governor, cache_manager)
    
    # Record some agent calls
    metrics.record_agent_call("zeitgeist", 150.0, success=True)
    metrics.record_agent_call("bard", 200.0, success=True)
    
    # Get system metrics
    system_metrics = await metrics.collect_system_metrics()
    assert system_metrics.total_agent_calls >= 2
    
    # Get dashboard
    dashboard = await metrics.get_dashboard()
    assert dashboard.system_metrics is not None
    assert len(dashboard.agent_metrics) == 3  # zeitgeist, bard, master_planner
    
    print(f"✅ Metrics Collector test passed - Calls: {system_metrics.total_agent_calls}")


@pytest.mark.asyncio
async def test_economic_router():
    """Test Economic Router decision making"""
    router = EconomicRouter()
    
    # Create test request
    request = TaskResourceRequest(
        task_id="test-002",
        task_type="test",
        estimated_complexity=TaskComplexity.SIMPLE,
        priority=TaskPriority.NORMAL,
        estimated_tokens=500
    )
    
    # Create budget status
    budget_status = BudgetStatus(
        current_window=UsageWindow(
            window_id="test",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            total_messages=100
        ),
        max_messages_per_window=900,
        total_messages_used=100,
        utilization_percentage=11.1
    )
    
    # Get recommendation
    model, confidence, reasoning = router.recommend_model(request, budget_status)
    
    assert model in [ModelType.OPUS_4, ModelType.SONNET_4_5]
    assert 0 <= confidence <= 1.0
    assert len(reasoning) > 0
    
    print(f"✅ Economic Router test passed - Recommended: {model} (confidence: {confidence:.2f})")


@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🔄 Running end-to-end workflow test...")
    
    # Initialize all components
    governor = ResourceGovernor()
    cache_manager = CacheManager()
    metrics = MetricsCollector(governor, cache_manager)
    
    # Simulate agent request
    task_id = f"e2e-test-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # 1. Check cache
    cache_lookup = CacheLookupRequest(
        input_text="What is AI?",
        task_type="qa",
        system_prompt="You are an AI expert",
        use_l1=True,
        use_l2=True,
        use_l3=False
    )
    
    cache_result = await cache_manager.lookup(cache_lookup)
    print(f"   Cache lookup: {'HIT' if cache_result.hit else 'MISS'}")
    
    if not cache_result.hit:
        # 2. Request resources
        resource_request = TaskResourceRequest(
            task_id=task_id,
            task_type="qa",
            estimated_complexity=TaskComplexity.MODERATE,
            priority=TaskPriority.NORMAL,
            estimated_tokens=1000
        )
        
        allocation = await governor.request_resources(resource_request)
        print(f"   Resource allocated: {allocation.model_allocated}")
        
        # 3. Simulate AI call (mock)
        response_data = {"answer": "AI is artificial intelligence"}
        
        # 4. Store in cache
        cache_store = CacheStoreRequest(
            input_text="What is AI?",
            response_data=response_data,
            task_type="qa",
            model_used=allocation.model_allocated.value,
            system_prompt="You are an AI expert",
            tokens_used=1000,
            store_in_l2=True
        )
        
        await cache_manager.store(cache_store)
        print(f"   Response cached")
        
        # 5. Record usage
        await governor.record_usage(task_id, allocation.model_allocated, 1000, True)
        print(f"   Usage recorded")
    
    # 6. Update metrics
    metrics.record_agent_call("qa_agent", 250.0, success=True)
    
    # 7. Get final metrics
    dashboard = await metrics.get_dashboard()
    print(f"   Final metrics - Total calls: {dashboard.system_metrics.total_agent_calls}")
    
    print("✅ End-to-end workflow test passed")


if __name__ == "__main__":
    print("🧪 Running Helios Integration Tests\n")
    
    # Run all tests
    asyncio.run(test_resource_governor_basic())
    asyncio.run(test_cache_manager_workflow())
    asyncio.run(test_metrics_collector())
    asyncio.run(test_economic_router())
    asyncio.run(test_end_to_end_workflow())
    
    print("\n✅ All integration tests passed!")
