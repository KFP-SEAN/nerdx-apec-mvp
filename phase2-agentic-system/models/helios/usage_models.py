"""
Helios Usage Tracking Models

Data models for Claude Max usage tracking and budget management.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    """Claude model types"""
    OPUS = "claude-opus-4"
    SONNET = "claude-sonnet-4"


class UsageWindow(BaseModel):
    """
    5-hour usage window tracking

    Claude Max provides ~900 messages per 5-hour window.
    This model tracks usage within a single window.
    """
    window_id: str = Field(..., description="Unique window identifier (timestamp-based)")
    start_time: datetime = Field(..., description="Window start time")
    end_time: datetime = Field(..., description="Window end time (start + 5 hours)")

    # Message counts
    total_messages: int = Field(default=0, description="Total messages used in this window")
    opus_messages: int = Field(default=0, description="Opus messages count")
    sonnet_messages: int = Field(default=0, description="Sonnet messages count")

    # Economic tracking (Opus costs 5x more than Sonnet)
    opus_cost_units: float = Field(default=0.0, description="Opus cost in normalized units (5x)")
    sonnet_cost_units: float = Field(default=0.0, description="Sonnet cost in normalized units (1x)")
    total_cost_units: float = Field(default=0.0, description="Total cost in normalized units")

    # Token tracking
    total_input_tokens: int = Field(default=0, description="Total input tokens")
    total_output_tokens: int = Field(default=0, description="Total output tokens")

    # Status
    is_active: bool = Field(default=True, description="Whether this window is currently active")
    throttle_activated: bool = Field(default=False, description="Whether throttling is active (80%+ usage)")

    def update_usage(self, model_type: ModelType, messages: int = 1,
                    input_tokens: int = 0, output_tokens: int = 0):
        """
        Update usage metrics for this window

        Args:
            model_type: Which model was used (Opus or Sonnet)
            messages: Number of messages (default 1)
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        """
        self.total_messages += messages
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        if model_type == ModelType.OPUS:
            self.opus_messages += messages
            self.opus_cost_units += messages * 5.0  # Opus costs 5x
        else:
            self.sonnet_messages += messages
            self.sonnet_cost_units += messages * 1.0

        self.total_cost_units = self.opus_cost_units + self.sonnet_cost_units

        # Activate throttling if over 80% of estimated budget
        # Assuming 900 message budget = 4500 cost units (if all Opus)
        # Conservative estimate: 80% of 900 messages = 720 messages
        if self.total_messages >= 720:
            self.throttle_activated = True

    def get_usage_percentage(self) -> float:
        """Get current usage as percentage of 900 message budget"""
        return (self.total_messages / 900.0) * 100.0

    def get_remaining_budget(self) -> int:
        """Get remaining message budget"""
        return max(0, 900 - self.total_messages)

    def should_throttle(self) -> bool:
        """Check if throttling should be activated"""
        return self.throttle_activated or self.total_messages >= 720


class BudgetStatus(BaseModel):
    """
    Current budget status across all active windows
    """
    current_window: Optional[UsageWindow] = None
    previous_windows: List[UsageWindow] = Field(default_factory=list)

    # Aggregate statistics
    total_messages_today: int = Field(default=0, description="Total messages used today")
    total_opus_messages_today: int = Field(default=0, description="Total Opus messages today")
    total_sonnet_messages_today: int = Field(default=0, description="Total Sonnet messages today")
    total_cost_units_today: float = Field(default=0.0, description="Total cost units today")

    # Ratios and KPIs
    opus_sonnet_ratio: float = Field(default=0.0, description="Current Opus/Sonnet ratio")
    average_cost_per_message: float = Field(default=0.0, description="Average cost per message")

    # Throttling status
    is_throttling: bool = Field(default=False, description="Whether throttling is active")
    throttle_reason: Optional[str] = None

    # Budget health
    budget_health: str = Field(default="healthy", description="green/yellow/red")
    estimated_messages_remaining_today: int = Field(default=900, description="Estimated remaining budget")

    def calculate_metrics(self):
        """Calculate aggregate metrics from all windows"""
        all_windows = [self.current_window] + self.previous_windows if self.current_window else self.previous_windows

        self.total_messages_today = sum(w.total_messages for w in all_windows)
        self.total_opus_messages_today = sum(w.opus_messages for w in all_windows)
        self.total_sonnet_messages_today = sum(w.sonnet_messages for w in all_windows)
        self.total_cost_units_today = sum(w.total_cost_units for w in all_windows)

        # Calculate ratios
        if self.total_sonnet_messages_today > 0:
            self.opus_sonnet_ratio = self.total_opus_messages_today / self.total_sonnet_messages_today
        else:
            self.opus_sonnet_ratio = 0.0

        if self.total_messages_today > 0:
            self.average_cost_per_message = self.total_cost_units_today / self.total_messages_today
        else:
            self.average_cost_per_message = 0.0

        # Update throttling status
        if self.current_window:
            self.is_throttling = self.current_window.should_throttle()
            if self.is_throttling:
                self.throttle_reason = f"Current window at {self.current_window.get_usage_percentage():.1f}% capacity"

            # Budget health assessment
            usage_pct = self.current_window.get_usage_percentage()
            if usage_pct < 60:
                self.budget_health = "green"
            elif usage_pct < 80:
                self.budget_health = "yellow"
            else:
                self.budget_health = "red"

            self.estimated_messages_remaining_today = self.current_window.get_remaining_budget()


class TaskResourceRequest(BaseModel):
    """
    Resource request for a task execution
    """
    task_id: str
    project_id: str
    agent_type: str
    preferred_model: ModelType = ModelType.SONNET
    estimated_messages: int = Field(default=1, description="Estimated messages needed")
    estimated_input_tokens: int = Field(default=0)
    estimated_output_tokens: int = Field(default=0)
    priority: int = Field(default=5, ge=1, le=10, description="Task priority 1-10")
    can_use_cache: bool = Field(default=True, description="Whether task can use cached results")
    requires_opus: bool = Field(default=False, description="Whether task specifically requires Opus")

    # Economic parameters
    max_cost_units: Optional[float] = Field(default=None, description="Maximum cost willing to pay")
    deadline: Optional[datetime] = Field(default=None, description="Task deadline")


class ResourceAllocation(BaseModel):
    """
    Resource allocation decision for a task
    """
    task_id: str
    allocated: bool = Field(..., description="Whether resources were allocated")
    allocated_model: Optional[ModelType] = None
    estimated_cost_units: float = Field(default=0.0)

    # Allocation metadata
    allocation_time: datetime = Field(default_factory=datetime.utcnow)
    window_id: Optional[str] = None

    # Decision reasoning
    decision_reason: str = Field(..., description="Why this allocation decision was made")
    alternative_suggestion: Optional[str] = Field(default=None, description="Alternative if denied")

    # Scheduling
    scheduled_time: Optional[datetime] = Field(default=None, description="When task should execute")
    estimated_wait_time_seconds: int = Field(default=0, description="Estimated wait before execution")


class UsageMetrics(BaseModel):
    """
    Detailed usage metrics for monitoring and analytics
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Current state
    current_window_id: Optional[str] = None
    current_usage_percentage: float = 0.0
    current_budget_health: str = "green"

    # Throughput metrics
    messages_per_hour: float = 0.0
    average_tokens_per_message: float = 0.0

    # Economic metrics
    cost_efficiency: float = Field(default=0.0, description="Sonnet usage % (higher is more efficient)")
    opus_usage_percentage: float = 0.0
    sonnet_usage_percentage: float = 0.0

    # Performance metrics
    cache_hit_rate: float = 0.0
    average_task_latency_ms: float = 0.0
    throttle_events_count: int = 0

    # Quality metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_queued: int = 0
    success_rate: float = 0.0
