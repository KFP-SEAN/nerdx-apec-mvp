"""
Helios Metrics Collector

Collects and aggregates metrics from all Helios components.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from models.helios.monitoring_models import *
from services.orchestrator.resource_governor import ResourceGovernor
from services.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Centralized metrics collection and aggregation
    
    Collects metrics from:
    - Resource Governor
    - Cache Manager
    - Specialized Agents
    - Economic Router
    """
    
    def __init__(
        self,
        resource_governor: Optional[ResourceGovernor] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        self.resource_governor = resource_governor
        self.cache_manager = cache_manager
        
        # In-memory metric storage (use TimescaleDB/Prometheus in production)
        self.metrics_buffer: List[Dict] = []
        self.agent_call_counts = defaultdict(int)
        self.agent_latencies = defaultdict(list)
        self.alerts: List[Alert] = []
        
        self.start_time = datetime.utcnow()
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        
        # Get Resource Governor metrics
        governor_metrics = {}
        if self.resource_governor:
            try:
                budget_status = await self.resource_governor.get_budget_status()
                governor_metrics = {
                    "total_budget_used": budget_status.total_messages_used,
                    "budget_utilization_percent": budget_status.utilization_percentage,
                    "current_window_messages": budget_status.current_window.total_messages,
                    "throttle_active": budget_status.throttle_active
                }
            except Exception as e:
                logger.error(f"Failed to collect governor metrics: {e}")
        
        # Get Cache Manager metrics
        cache_metrics = {}
        if self.cache_manager:
            try:
                cache_stats = await self.cache_manager.get_metrics()
                cache_metrics = {
                    "cache_hit_rate": cache_stats.overall_hit_rate,
                    "cache_l1_hits": cache_stats.l1_hits,
                    "cache_l2_hits": cache_stats.l2_hits,
                    "cache_l3_hits": cache_stats.l3_hits,
                    "total_cache_lookups": cache_stats.total_lookups,
                    "cost_saved_by_cache": cache_stats.total_cost_saved
                }
            except Exception as e:
                logger.error(f"Failed to collect cache metrics: {e}")
        
        # Agent metrics
        agent_metrics = {
            "zeitgeist_calls": self.agent_call_counts.get("zeitgeist", 0),
            "bard_calls": self.agent_call_counts.get("bard", 0),
            "master_planner_calls": self.agent_call_counts.get("master_planner", 0),
            "total_agent_calls": sum(self.agent_call_counts.values())
        }
        
        return SystemMetrics(
            **governor_metrics,
            **cache_metrics,
            **agent_metrics
        )
    
    async def collect_agent_performance(self, agent_type: str) -> AgentPerformanceMetrics:
        """Collect performance metrics for specific agent"""
        
        latencies = self.agent_latencies.get(agent_type, [])
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        return AgentPerformanceMetrics(
            agent_type=agent_type,
            total_calls=self.agent_call_counts.get(agent_type, 0),
            average_latency_ms=avg_latency
        )
    
    async def collect_cost_breakdown(self) -> CostBreakdown:
        """Collect detailed cost breakdown"""
        
        cost_breakdown = CostBreakdown()
        
        # Get cache savings
        if self.cache_manager:
            try:
                cache_metrics = await self.cache_manager.get_metrics()
                cost_breakdown.cache_savings = cache_metrics.total_cost_saved
            except Exception as e:
                logger.error(f"Failed to get cost breakdown: {e}")
        
        return cost_breakdown
    
    async def get_dashboard(self) -> MonitoringDashboard:
        """Get complete monitoring dashboard"""
        
        system_metrics = await self.collect_system_metrics()
        
        agent_metrics = []
        for agent_type in ["zeitgeist", "bard", "master_planner"]:
            metrics = await self.collect_agent_performance(agent_type)
            agent_metrics.append(metrics)
        
        cost_breakdown = await self.collect_cost_breakdown()
        
        health_statuses = await self.check_component_health()
        
        # Calculate summary stats
        total_calls = sum(self.agent_call_counts.values())
        
        return MonitoringDashboard(
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            cost_breakdown=cost_breakdown,
            health_statuses=health_statuses,
            active_alerts=[a for a in self.alerts if not a.resolved],
            total_requests_today=total_calls
        )
    
    async def check_component_health(self) -> List[HealthStatus]:
        """Check health of all components"""
        
        health_statuses = []
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Resource Governor health
        if self.resource_governor:
            try:
                await self.resource_governor.get_budget_status()
                health_statuses.append(HealthStatus(
                    component="resource_governor",
                    status="healthy",
                    uptime_seconds=uptime
                ))
            except Exception as e:
                health_statuses.append(HealthStatus(
                    component="resource_governor",
                    status="unhealthy",
                    uptime_seconds=uptime,
                    details={"error": str(e)}
                ))
        
        # Cache Manager health
        if self.cache_manager:
            try:
                await self.cache_manager.health_check()
                health_statuses.append(HealthStatus(
                    component="cache_manager",
                    status="healthy",
                    uptime_seconds=uptime
                ))
            except Exception as e:
                health_statuses.append(HealthStatus(
                    component="cache_manager",
                    status="unhealthy",
                    uptime_seconds=uptime,
                    details={"error": str(e)}
                ))
        
        return health_statuses
    
    def record_agent_call(
        self,
        agent_type: str,
        latency_ms: float,
        success: bool = True
    ):
        """Record agent call for metrics"""
        self.agent_call_counts[agent_type] += 1
        self.agent_latencies[agent_type].append(latency_ms)
    
    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            alert_id=f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            level=level,
            title=title,
            message=message,
            source=source
        )
        self.alerts.append(alert)
        logger.warning(f"Alert created: [{level}] {title} - {message}")
        return alert
