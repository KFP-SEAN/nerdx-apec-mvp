"""
Helios Monitoring & Analytics API

REST API endpoints for system monitoring, metrics, and dashboards.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Optional

from models.helios.monitoring_models import *
from services.monitoring.metrics_collector import MetricsCollector
from services.orchestrator.resource_governor import ResourceGovernor
from services.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/helios/monitoring", tags=["Helios Monitoring"])

# Initialize components
resource_governor = ResourceGovernor()
cache_manager = CacheManager()
metrics_collector = MetricsCollector(resource_governor, cache_manager)


@router.get("/dashboard", response_model=MonitoringDashboard)
async def get_monitoring_dashboard():
    """
    Get complete monitoring dashboard
    
    Returns comprehensive system metrics, agent performance,
    cost breakdown, health status, and active alerts.
    """
    try:
        dashboard = await metrics_collector.get_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/system", response_model=SystemMetrics)
async def get_system_metrics():
    """
    Get current system metrics
    
    Returns real-time metrics for Resource Governor,
    Cache Manager, and Agent usage.
    """
    try:
        metrics = await metrics_collector.collect_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/agent/{agent_type}", response_model=AgentPerformanceMetrics)
async def get_agent_metrics(agent_type: str):
    """
    Get performance metrics for specific agent
    
    Args:
        agent_type: "zeitgeist", "bard", or "master_planner"
    """
    try:
        if agent_type not in ["zeitgeist", "bard", "master_planner"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid agent type. Must be 'zeitgeist', 'bard', or 'master_planner'"
            )
        
        metrics = await metrics_collector.collect_agent_performance(agent_type)
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-breakdown", response_model=CostBreakdown)
async def get_cost_breakdown():
    """
    Get detailed cost breakdown
    
    Returns costs by model, by agent, and total savings
    from caching and intelligent routing.
    """
    try:
        cost_breakdown = await metrics_collector.collect_cost_breakdown()
        return cost_breakdown
    except Exception as e:
        logger.error(f"Failed to get cost breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=List[HealthStatus])
async def get_health_status():
    """
    Get health status of all components
    
    Returns health checks for Resource Governor,
    Cache Manager, and Specialized Agents.
    """
    try:
        health_statuses = await metrics_collector.check_component_health()
        return health_statuses
    except Exception as e:
        logger.error(f"Failed to check health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[Alert])
async def get_alerts(level: Optional[str] = None, resolved: bool = False):
    """
    Get system alerts
    
    Args:
        level: Filter by alert level ("info", "warning", "error", "critical")
        resolved: Include resolved alerts (default: False)
    """
    try:
        alerts = metrics_collector.alerts
        
        # Filter by level
        if level:
            alerts = [a for a in alerts if a.level.value == level]
        
        # Filter by resolved status
        if not resolved:
            alerts = [a for a in alerts if not a.resolved]
        
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    try:
        for alert in metrics_collector.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return {"message": "Alert acknowledged", "alert_id": alert_id}
        
        raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_monitoring_summary():
    """
    Get concise monitoring summary
    
    Returns key metrics for quick overview.
    """
    try:
        dashboard = await metrics_collector.get_dashboard()
        
        return {
            "status": "operational",
            "budget_utilization": f"{dashboard.system_metrics.budget_utilization_percent:.1f}%",
            "cache_hit_rate": f"{dashboard.system_metrics.cache_hit_rate:.1%}",
            "total_agent_calls": dashboard.system_metrics.total_agent_calls,
            "cost_saved_today": f"${dashboard.cost_breakdown.total_savings:.2f}",
            "active_alerts": len(dashboard.active_alerts),
            "components_healthy": sum(
                1 for h in dashboard.health_statuses if h.status == "healthy"
            ),
            "components_total": len(dashboard.health_statuses)
        }
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
