"""
Helios Monitoring & Metrics Models

Data models for system monitoring, metrics collection, and analytics.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemMetrics(BaseModel):
    """Overall system metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Resource Governor metrics
    total_budget_used: int = 0
    budget_utilization_percent: float = 0.0
    current_window_messages: int = 0
    throttle_active: bool = False
    
    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_l1_hits: int = 0
    cache_l2_hits: int = 0
    cache_l3_hits: int = 0
    total_cache_lookups: int = 0
    
    # Agent metrics
    zeitgeist_calls: int = 0
    bard_calls: int = 0
    master_planner_calls: int = 0
    total_agent_calls: int = 0
    
    # Cost metrics
    total_cost_dollars: float = 0.0
    total_tokens_used: int = 0
    cost_saved_by_cache: float = 0.0


class AgentPerformanceMetrics(BaseModel):
    """Performance metrics for individual agents"""
    agent_type: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_latency_ms: float = 0.0
    average_confidence: float = 0.0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    
    # Time windows
    calls_last_hour: int = 0
    calls_last_day: int = 0
    
    # Model usage
    opus_calls: int = 0
    sonnet_calls: int = 0


class CostBreakdown(BaseModel):
    """Detailed cost breakdown"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # By model
    opus_cost: float = 0.0
    sonnet_cost: float = 0.0
    
    # By agent
    zeitgeist_cost: float = 0.0
    bard_cost: float = 0.0
    master_planner_cost: float = 0.0
    
    # Savings
    cache_savings: float = 0.0
    routing_savings: float = 0.0  # From using Sonnet instead of Opus
    
    total_cost: float = 0.0
    total_savings: float = 0.0


class Alert(BaseModel):
    """System alert"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str  # Component that generated alert
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Component health status"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    uptime_seconds: float
    last_check: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)


class MonitoringDashboard(BaseModel):
    """Complete monitoring dashboard data"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    system_metrics: SystemMetrics
    agent_metrics: List[AgentPerformanceMetrics]
    cost_breakdown: CostBreakdown
    health_statuses: List[HealthStatus]
    active_alerts: List[Alert]
    
    # Summary stats
    total_requests_today: int = 0
    success_rate_percent: float = 100.0
    average_response_time_ms: float = 0.0


class MetricQuery(BaseModel):
    """Query for historical metrics"""
    metric_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    granularity: str = "1h"  # "1m", "5m", "1h", "1d"
    filters: Dict[str, Any] = Field(default_factory=dict)


class MetricDataPoint(BaseModel):
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)


class MetricQueryResponse(BaseModel):
    """Response to metric query"""
    metric_name: str
    data_points: List[MetricDataPoint]
    aggregation: Optional[Dict[str, float]] = None  # min, max, avg, sum
