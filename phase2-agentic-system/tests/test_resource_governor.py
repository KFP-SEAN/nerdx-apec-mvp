"""
Unit Tests for Resource Governor

Tests Claude Max budget management, allocation decisions, and throttling logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import fakeredis

from services.orchestrator.resource_governor import ResourceGovernor
from models.helios.usage_models import (
    TaskResourceRequest,
    ModelType,
    UsageWindow
)


@pytest.fixture
def mock_redis():
    """Provide a fake Redis client for testing"""
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def resource_governor(mock_redis):
    """Provide a ResourceGovernor instance with mocked Redis"""
    return ResourceGovernor(redis_client=mock_redis)


class TestResourceGovernorInitialization:
    """Test Resource Governor initialization"""

    def test_creates_new_window_on_init(self, resource_governor):
        """Should create a new usage window on initialization"""
        assert resource_governor.current_window is not None
        assert resource_governor.current_window.is_active
        assert resource_governor.current_window.total_messages == 0

    def test_window_duration_is_5_hours(self, resource_governor):
        """Window should be 5 hours"""
        window = resource_governor.current_window
        duration = (window.end_time - window.start_time).total_seconds() / 3600
        assert duration == 5.0

    def test_max_messages_per_window(self, resource_governor):
        """Should have 900 message limit"""
        assert resource_governor.max_messages_per_window == 900


class TestAllocationDecisions:
    """Test resource allocation decision logic"""

    @pytest.mark.asyncio
    async def test_normal_zone_honors_opus_preference(self, resource_governor):
        """Normal zone (<80%) should honor Opus preference"""
        request = TaskResourceRequest(
            task_id="test-1",
            project_id="proj-1",
            agent_type="prd_agent",
            preferred_model=ModelType.OPUS,
            estimated_messages=10,
            priority=5
        )

        allocation = await resource_governor.request_resources(request)

        assert allocation.allocated is True
        assert allocation.allocated_model == ModelType.OPUS
        assert "Normal zone" in allocation.decision_reason

    @pytest.mark.asyncio
    async def test_normal_zone_honors_sonnet_preference(self, resource_governor):
        """Normal zone should honor Sonnet preference"""
        request = TaskResourceRequest(
            task_id="test-2",
            project_id="proj-1",
            agent_type="code_agent",
            preferred_model=ModelType.SONNET,
            estimated_messages=10,
            priority=5
        )

        allocation = await resource_governor.request_resources(request)

        assert allocation.allocated is True
        assert allocation.allocated_model == ModelType.SONNET

    @pytest.mark.asyncio
    async def test_throttle_zone_forces_sonnet(self, resource_governor):
        """Throttle zone (80-95%) should force Sonnet for non-Opus-required tasks"""
        # Simulate 80% usage
        resource_governor.current_window.total_messages = 720

        request = TaskResourceRequest(
            task_id="test-3",
            project_id="proj-1",
            agent_type="prd_agent",
            preferred_model=ModelType.OPUS,
            estimated_messages=10,
            priority=5,
            requires_opus=False
        )

        allocation = await resource_governor.request_resources(request)

        assert allocation.allocated is True
        assert allocation.allocated_model == ModelType.SONNET
        assert "Throttle zone" in allocation.decision_reason

    @pytest.mark.asyncio
    async def test_throttle_zone_queues_opus_required(self, resource_governor):
        """Throttle zone should queue Opus-required tasks"""
        # Simulate 80% usage
        resource_governor.current_window.total_messages = 720

        request = TaskResourceRequest(
            task_id="test-4",
            project_id="proj-1",
            agent_type="prd_agent",
            preferred_model=ModelType.OPUS,
            estimated_messages=10,
            priority=5,
            requires_opus=True
        )

        allocation = await resource_governor.request_resources(request)

        assert allocation.allocated is False
        assert allocation.scheduled_time is not None
        assert "queued for next window" in allocation.decision_reason

    @pytest.mark.asyncio
    async def test_critical_zone_only_high_priority(self, resource_governor):
        """Critical zone (>95%) should only allow high-priority tasks"""
        # Simulate 96% usage
        resource_governor.current_window.total_messages = 864

        # Low priority request
        low_priority = TaskResourceRequest(
            task_id="test-5",
            project_id="proj-1",
            agent_type="code_agent",
            preferred_model=ModelType.SONNET,
            estimated_messages=10,
            priority=5
        )

        allocation_low = await resource_governor.request_resources(low_priority)
        assert allocation_low.allocated is False

        # High priority request
        high_priority = TaskResourceRequest(
            task_id="test-6",
            project_id="proj-1",
            agent_type="code_agent",
            preferred_model=ModelType.SONNET,
            estimated_messages=10,
            priority=9
        )

        allocation_high = await resource_governor.request_resources(high_priority)
        assert allocation_high.allocated is True
        assert allocation_high.allocated_model == ModelType.SONNET

    @pytest.mark.asyncio
    async def test_budget_exhausted_denies_all(self, resource_governor):
        """Exhausted budget should deny all requests"""
        # Simulate full usage
        resource_governor.current_window.total_messages = 900

        request = TaskResourceRequest(
            task_id="test-7",
            project_id="proj-1",
            agent_type="code_agent",
            preferred_model=ModelType.SONNET,
            estimated_messages=10,
            priority=10
        )

        allocation = await resource_governor.request_resources(request)

        assert allocation.allocated is False
        assert "Budget exhausted" in allocation.decision_reason


class TestUsageTracking:
    """Test usage tracking functionality"""

    def test_record_opus_usage(self, resource_governor):
        """Should correctly track Opus usage"""
        resource_governor._record_usage(
            model_type=ModelType.OPUS,
            messages=10,
            input_tokens=5000,
            output_tokens=3000
        )

        window = resource_governor.current_window
        assert window.total_messages == 10
        assert window.opus_messages == 10
        assert window.sonnet_messages == 0
        assert window.opus_cost_units == 50.0  # 10 * 5
        assert window.total_input_tokens == 5000
        assert window.total_output_tokens == 3000

    def test_record_sonnet_usage(self, resource_governor):
        """Should correctly track Sonnet usage"""
        resource_governor._record_usage(
            model_type=ModelType.SONNET,
            messages=10,
            input_tokens=3000,
            output_tokens=2000
        )

        window = resource_governor.current_window
        assert window.total_messages == 10
        assert window.opus_messages == 0
        assert window.sonnet_messages == 10
        assert window.sonnet_cost_units == 10.0  # 10 * 1
        assert window.total_input_tokens == 3000
        assert window.total_output_tokens == 2000

    def test_mixed_usage_tracking(self, resource_governor):
        """Should correctly track mixed Opus and Sonnet usage"""
        resource_governor._record_usage(ModelType.OPUS, messages=5)
        resource_governor._record_usage(ModelType.SONNET, messages=10)

        window = resource_governor.current_window
        assert window.total_messages == 15
        assert window.opus_messages == 5
        assert window.sonnet_messages == 10
        assert window.opus_cost_units == 25.0  # 5 * 5
        assert window.sonnet_cost_units == 10.0  # 10 * 1
        assert window.total_cost_units == 35.0


class TestThrottling:
    """Test throttling behavior"""

    def test_manual_throttle_activation(self, resource_governor):
        """Should allow manual throttle activation"""
        resource_governor.force_throttle("Testing manual throttle")

        assert resource_governor.current_window.throttle_activated is True
        assert resource_governor.budget_status.is_throttling is True
        assert "Testing manual throttle" in resource_governor.budget_status.throttle_reason

    def test_throttle_clearing(self, resource_governor):
        """Should allow clearing throttle"""
        resource_governor.force_throttle("Test")
        resource_governor.clear_throttle()

        assert resource_governor.current_window.throttle_activated is False
        assert resource_governor.budget_status.is_throttling is False

    def test_automatic_throttle_at_80_percent(self, resource_governor):
        """Should automatically throttle at 80% usage"""
        # Record usage to reach 80%
        resource_governor._record_usage(ModelType.SONNET, messages=720)

        assert resource_governor.current_window.should_throttle() is True


class TestWindowRotation:
    """Test window rotation logic"""

    def test_window_rotation(self, resource_governor):
        """Should rotate window when expired"""
        # Simulate expired window
        old_window = resource_governor.current_window
        old_window.end_time = datetime.utcnow() - timedelta(minutes=1)
        old_window_id = old_window.window_id

        resource_governor._rotate_window()

        # Should have new window
        assert resource_governor.current_window.window_id != old_window_id
        assert resource_governor.current_window.total_messages == 0
        assert resource_governor.current_window.is_active is True

    def test_expired_window_auto_rotation(self, resource_governor):
        """Should automatically rotate on request when window expired"""
        # Mock expired window
        resource_governor.current_window.end_time = datetime.utcnow() - timedelta(seconds=1)
        old_window_id = resource_governor.current_window.window_id

        # Request resources - should trigger rotation
        request = TaskResourceRequest(
            task_id="test-rotation",
            project_id="proj-1",
            agent_type="prd_agent",
            preferred_model=ModelType.SONNET,
            estimated_messages=1,
            priority=5
        )

        import asyncio
        allocation = asyncio.run(resource_governor.request_resources(request))

        # Should have rotated to new window
        assert resource_governor.current_window.window_id != old_window_id


class TestBudgetStatus:
    """Test budget status calculations"""

    def test_budget_status_green(self, resource_governor):
        """Budget health should be green below 60% usage"""
        resource_governor._record_usage(ModelType.SONNET, messages=500)
        budget = resource_governor.get_budget_status()

        assert budget.budget_health == "green"

    def test_budget_status_yellow(self, resource_governor):
        """Budget health should be yellow at 60-80% usage"""
        resource_governor._record_usage(ModelType.SONNET, messages=650)
        budget = resource_governor.get_budget_status()

        assert budget.budget_health == "yellow"

    def test_budget_status_red(self, resource_governor):
        """Budget health should be red above 80% usage"""
        resource_governor._record_usage(ModelType.SONNET, messages=750)
        budget = resource_governor.get_budget_status()

        assert budget.budget_health == "red"


class TestHealthCheck:
    """Test health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, resource_governor):
        """Should report healthy when all systems operational"""
        health = await resource_governor.health_check()

        assert health["healthy"] is True
        assert health["redis_connected"] is True
        assert health["window_valid"] is True

    @pytest.mark.asyncio
    async def test_health_check_with_expired_window(self, resource_governor):
        """Should report unhealthy with expired window"""
        resource_governor.current_window.end_time = datetime.utcnow() - timedelta(seconds=1)

        health = await resource_governor.health_check()

        assert health["healthy"] is False
        assert health["window_valid"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
