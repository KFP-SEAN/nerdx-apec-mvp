"""
Helios Resource Governor

Manages Claude Max budget allocation with 5-hour window tracking,
dynamic throttling, and economic routing between Opus/Sonnet models.

Key Features:
- 5-hour usage window management
- Dynamic throttling at 80% capacity
- Budget-aware task scheduling
- Redis-backed persistence
- Real-time usage metrics
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from redis import Redis
import asyncio

from models.helios.usage_models import (
    UsageWindow,
    BudgetStatus,
    TaskResourceRequest,
    ResourceAllocation,
    UsageMetrics,
    ModelType
)
from services.orchestrator.economic_router import EconomicRouter

logger = logging.getLogger(__name__)


class ResourceGovernor:
    """
    Central resource management for Claude Max optimization

    Responsibilities:
    1. Track usage across 5-hour windows
    2. Make allocation decisions based on budget
    3. Implement dynamic throttling
    4. Persist state to Redis
    5. Provide real-time metrics
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize Resource Governor

        Args:
            redis_client: Redis client for state persistence
        """
        self.redis = redis_client or Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.current_window: Optional[UsageWindow] = None
        self.budget_status = BudgetStatus()

        # Configuration
        self.max_messages_per_window = 900
        self.throttle_threshold = 0.8  # 80%
        self.window_duration_hours = 5

        # Metrics tracking
        self.metrics_history: List[UsageMetrics] = []

        # Economic Router integration
        self.economic_router = EconomicRouter()

        # Load existing state from Redis
        self._load_state()

        logger.info("Resource Governor initialized with Economic Router")

    def _load_state(self):
        """Load persisted state from Redis"""
        try:
            # Load current window
            window_data = self.redis.get("helios:current_window")
            if window_data:
                self.current_window = UsageWindow.parse_raw(window_data)
                logger.info(f"Loaded existing window: {self.current_window.window_id}")

                # Check if window expired
                if datetime.utcnow() > self.current_window.end_time:
                    logger.info("Current window expired, rotating...")
                    self._rotate_window()
            else:
                # Create new window
                self._create_new_window()

            # Load budget status
            self._update_budget_status()

        except Exception as e:
            logger.error(f"Failed to load state from Redis: {e}")
            self._create_new_window()

    def _save_state(self):
        """Persist current state to Redis"""
        try:
            if self.current_window:
                self.redis.set(
                    "helios:current_window",
                    self.current_window.json(),
                    ex=int(self.window_duration_hours * 3600)
                )

                # Also save to history
                self.redis.lpush(
                    "helios:window_history",
                    self.current_window.json()
                )
                self.redis.ltrim("helios:window_history", 0, 23)  # Keep last 24 windows (5 days)

        except Exception as e:
            logger.error(f"Failed to save state to Redis: {e}")

    def _create_new_window(self):
        """Create a new 5-hour usage window"""
        now = datetime.utcnow()
        window_id = now.strftime("%Y%m%d_%H%M%S")

        self.current_window = UsageWindow(
            window_id=window_id,
            start_time=now,
            end_time=now + timedelta(hours=self.window_duration_hours),
            is_active=True
        )

        logger.info(f"Created new window: {window_id} (expires at {self.current_window.end_time})")
        self._save_state()

    def _rotate_window(self):
        """Rotate to a new window, archiving the current one"""
        if self.current_window:
            self.current_window.is_active = False
            self._save_state()

            # Add to budget status history
            if self.budget_status.current_window:
                self.budget_status.previous_windows.append(self.budget_status.current_window)
                # Keep only today's windows
                today = datetime.utcnow().date()
                self.budget_status.previous_windows = [
                    w for w in self.budget_status.previous_windows
                    if w.start_time.date() == today
                ]

        self._create_new_window()
        self._update_budget_status()

    def _update_budget_status(self):
        """Update budget status with current metrics"""
        self.budget_status.current_window = self.current_window
        self.budget_status.calculate_metrics()
        self._save_state()

    async def request_resources(self, request: TaskResourceRequest) -> ResourceAllocation:
        """
        Request resource allocation for a task

        Args:
            request: Task resource request details

        Returns:
            ResourceAllocation decision
        """
        # Check if window needs rotation
        if datetime.utcnow() > self.current_window.end_time:
            self._rotate_window()

        # Get current budget status
        remaining = self.current_window.get_remaining_budget()
        usage_pct = self.current_window.get_usage_percentage()

        logger.info(f"Resource request for {request.task_id}: "
                   f"remaining={remaining}, usage={usage_pct:.1f}%, "
                   f"preferred={request.preferred_model}")

        # Decision logic
        allocation = await self._make_allocation_decision(request, remaining, usage_pct)

        # If allocated, update usage
        if allocation.allocated:
            self._record_usage(
                model_type=allocation.allocated_model,
                messages=request.estimated_messages,
                input_tokens=request.estimated_input_tokens,
                output_tokens=request.estimated_output_tokens
            )

        return allocation

    async def _make_allocation_decision(
        self,
        request: TaskResourceRequest,
        remaining_budget: int,
        usage_percentage: float
    ) -> ResourceAllocation:
        """
        Make resource allocation decision based on budget and priorities

        Decision Matrix (integrated with Economic Router):
        1. Budget exhausted (0 remaining): DENY
        2. Critical throttle zone (>95%): Only high priority (≥8) tasks
        3. Throttle zone (80-95%): Prefer Sonnet, queue Opus requests
        4. Normal zone (<80%): Use Economic Router for optimal model selection
        """
        allocated = False
        allocated_model = None
        estimated_cost = 0.0
        reason = ""
        alternative = None
        scheduled_time = None
        wait_time = 0

        # Get Economic Router recommendation
        recommended_model, confidence, router_reasoning = self.economic_router.recommend_model(
            request,
            self.budget_status,
            force_constraints=True
        )

        # Budget exhausted
        if remaining_budget == 0:
            allocated = False
            reason = "Budget exhausted for current window"
            alternative = f"Wait until next window at {self.current_window.end_time}"
            wait_time = int((self.current_window.end_time - datetime.utcnow()).total_seconds())

        # Critical throttle zone (>95%)
        elif usage_percentage > 95:
            if request.priority >= 8:
                # Only allow high-priority tasks, force Sonnet
                allocated = True
                allocated_model = ModelType.SONNET
                estimated_cost = request.estimated_messages * 1.0
                reason = f"Critical zone: High-priority task ({request.priority}) forced to Sonnet"
            else:
                allocated = False
                reason = f"Critical zone: Priority {request.priority} too low (need ≥8)"
                alternative = "Increase priority or wait for next window"
                wait_time = int((self.current_window.end_time - datetime.utcnow()).total_seconds())

        # Throttle zone (80-95%)
        elif usage_percentage > 80:
            if request.requires_opus:
                # Opus required but in throttle zone - queue for next window
                allocated = False
                reason = "Throttle zone: Opus requests queued for next window"
                alternative = "Task will execute in next window with Opus"
                scheduled_time = self.current_window.end_time
                wait_time = int((self.current_window.end_time - datetime.utcnow()).total_seconds())
            else:
                # Allow with Sonnet
                allocated = True
                allocated_model = ModelType.SONNET
                estimated_cost = request.estimated_messages * 1.0
                reason = "Throttle zone: Allocated with Sonnet for cost efficiency"

        # Normal zone (<80%)
        else:
            # Use Economic Router for intelligent model selection
            allocated = True
            allocated_model = recommended_model
            cost_multiplier = 5.0 if allocated_model == ModelType.OPUS else 1.0
            estimated_cost = request.estimated_messages * cost_multiplier
            reason = f"Normal zone: {router_reasoning} (confidence: {confidence:.2f})"

        allocation = ResourceAllocation(
            task_id=request.task_id,
            allocated=allocated,
            allocated_model=allocated_model,
            estimated_cost_units=estimated_cost,
            window_id=self.current_window.window_id,
            decision_reason=reason,
            alternative_suggestion=alternative,
            scheduled_time=scheduled_time,
            estimated_wait_time_seconds=wait_time
        )

        logger.info(f"Allocation decision for {request.task_id}: "
                   f"allocated={allocated}, model={allocated_model}, reason={reason}")

        return allocation

    def _record_usage(
        self,
        model_type: ModelType,
        messages: int = 1,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        """
        Record actual usage in current window

        Args:
            model_type: Model used
            messages: Number of messages
            input_tokens: Input tokens consumed
            output_tokens: Output tokens consumed
        """
        if not self.current_window:
            self._create_new_window()

        self.current_window.update_usage(
            model_type=model_type,
            messages=messages,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        self._update_budget_status()
        self._save_state()

        logger.info(f"Recorded usage: {model_type.value} - {messages} msg, "
                   f"{input_tokens} in_tok, {output_tokens} out_tok | "
                   f"Window at {self.current_window.get_usage_percentage():.1f}%")

    def get_budget_status(self) -> BudgetStatus:
        """Get current budget status"""
        self._update_budget_status()
        return self.budget_status

    def get_usage_metrics(self) -> UsageMetrics:
        """
        Calculate current usage metrics

        Returns:
            UsageMetrics with current statistics
        """
        metrics = UsageMetrics(
            current_window_id=self.current_window.window_id if self.current_window else None,
            current_usage_percentage=self.current_window.get_usage_percentage() if self.current_window else 0,
            current_budget_health=self.budget_status.budget_health
        )

        if self.current_window:
            # Calculate throughput
            elapsed_hours = (datetime.utcnow() - self.current_window.start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                metrics.messages_per_hour = self.current_window.total_messages / elapsed_hours

            # Calculate average tokens per message
            if self.current_window.total_messages > 0:
                total_tokens = self.current_window.total_input_tokens + self.current_window.total_output_tokens
                metrics.average_tokens_per_message = total_tokens / self.current_window.total_messages

            # Economic metrics
            total = self.current_window.opus_messages + self.current_window.sonnet_messages
            if total > 0:
                metrics.sonnet_usage_percentage = (self.current_window.sonnet_messages / total) * 100
                metrics.opus_usage_percentage = (self.current_window.opus_messages / total) * 100
                metrics.cost_efficiency = metrics.sonnet_usage_percentage  # Higher Sonnet % = more efficient

            # Throttle events
            metrics.throttle_events_count = 1 if self.current_window.throttle_activated else 0

        # Save metrics to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:  # Keep last 1000 metrics
            self.metrics_history = self.metrics_history[-1000:]

        # Persist to Redis
        try:
            self.redis.lpush("helios:metrics_history", metrics.json())
            self.redis.ltrim("helios:metrics_history", 0, 999)
        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}")

        return metrics

    def force_throttle(self, reason: str):
        """
        Manually activate throttling

        Args:
            reason: Reason for manual throttle
        """
        if self.current_window:
            self.current_window.throttle_activated = True
            self.budget_status.is_throttling = True
            self.budget_status.throttle_reason = f"Manual: {reason}"
            self._save_state()
            logger.warning(f"Throttling manually activated: {reason}")

    def clear_throttle(self):
        """Clear throttling flag"""
        if self.current_window:
            self.current_window.throttle_activated = False
            self.budget_status.is_throttling = False
            self.budget_status.throttle_reason = None
            self._save_state()
            logger.info("Throttling cleared")

    def get_window_history(self, limit: int = 24) -> List[UsageWindow]:
        """
        Get historical usage windows

        Args:
            limit: Maximum number of windows to return

        Returns:
            List of historical UsageWindow objects
        """
        try:
            history_data = self.redis.lrange("helios:window_history", 0, limit - 1)
            return [UsageWindow.parse_raw(data) for data in history_data]
        except Exception as e:
            logger.error(f"Failed to load window history: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Resource Governor

        Returns:
            Health status dictionary
        """
        try:
            # Check Redis connection
            redis_healthy = self.redis.ping()

            # Check window validity
            window_valid = self.current_window is not None and datetime.utcnow() < self.current_window.end_time

            # Overall health
            healthy = redis_healthy and window_valid

            return {
                "healthy": healthy,
                "redis_connected": redis_healthy,
                "window_valid": window_valid,
                "current_window": self.current_window.window_id if self.current_window else None,
                "budget_health": self.budget_status.budget_health,
                "is_throttling": self.budget_status.is_throttling,
                "usage_percentage": self.current_window.get_usage_percentage() if self.current_window else 0,
                "messages_remaining": self.current_window.get_remaining_budget() if self.current_window else 0
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
