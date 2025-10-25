"""
Helios Resource Management API

REST API endpoints for Resource Governor - Claude Max budget management.

Endpoints:
- GET /helios/budget/status - Current budget status
- POST /helios/budget/request - Request resource allocation
- GET /helios/budget/metrics - Current usage metrics
- GET /helios/budget/history - Window history
- POST /helios/budget/throttle - Manual throttle control
- GET /helios/budget/health - Health check
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from services.orchestrator.resource_governor import ResourceGovernor
from models.helios.usage_models import (
    BudgetStatus,
    TaskResourceRequest,
    ResourceAllocation,
    UsageMetrics,
    UsageWindow,
    ModelType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/helios/budget", tags=["Helios Resource Management"])

# Global Resource Governor instance
_resource_governor: Optional[ResourceGovernor] = None


def get_resource_governor() -> ResourceGovernor:
    """Dependency injection for Resource Governor"""
    global _resource_governor
    if _resource_governor is None:
        _resource_governor = ResourceGovernor()
    return _resource_governor


# Request/Response Models
class ThrottleRequest(BaseModel):
    """Request to manually control throttling"""
    action: str  # "activate" or "clear"
    reason: Optional[str] = "Manual override"


class BudgetStatusResponse(BaseModel):
    """Response with current budget status"""
    status: str = "success"
    budget: BudgetStatus
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Response with current metrics"""
    status: str = "success"
    metrics: UsageMetrics
    timestamp: datetime


class WindowHistoryResponse(BaseModel):
    """Response with window history"""
    status: str = "success"
    windows: List[UsageWindow]
    count: int
    timestamp: datetime


# API Endpoints
@router.get("/status", response_model=BudgetStatusResponse)
async def get_budget_status(governor: ResourceGovernor = Depends(get_resource_governor)):
    """
    Get current Claude Max budget status

    Returns:
        Current budget status including:
        - Active window information
        - Usage percentages
        - Throttle status
        - Budget health (green/yellow/red)
        - Remaining message budget
    """
    try:
        budget = governor.get_budget_status()

        return BudgetStatusResponse(
            status="success",
            budget=budget,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to get budget status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request", response_model=ResourceAllocation)
async def request_resources(
    request: TaskResourceRequest,
    governor: ResourceGovernor = Depends(get_resource_governor)
):
    """
    Request resource allocation for a task

    The Resource Governor will:
    1. Check current budget availability
    2. Evaluate task priority and requirements
    3. Make allocation decision (approve/deny/schedule)
    4. Route to appropriate model (Opus/Sonnet)
    5. Update usage tracking if allocated

    Args:
        request: Task resource request with:
            - task_id: Unique task identifier
            - preferred_model: Opus or Sonnet
            - estimated_messages: Expected message count
            - priority: 1-10 (higher = more important)
            - requires_opus: Whether Opus is mandatory

    Returns:
        ResourceAllocation decision with:
        - allocated: Whether resources were granted
        - allocated_model: Which model to use
        - decision_reason: Explanation
        - scheduled_time: When to execute (if queued)
    """
    try:
        allocation = await governor.request_resources(request)

        logger.info(f"Resource allocation for {request.task_id}: {allocation.allocated} "
                   f"({allocation.decision_reason})")

        return allocation

    except Exception as e:
        logger.error(f"Failed to process resource request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=MetricsResponse)
async def get_usage_metrics(governor: ResourceGovernor = Depends(get_resource_governor)):
    """
    Get current usage metrics and KPIs

    Returns:
        UsageMetrics including:
        - Throughput (messages per hour)
        - Economic metrics (Opus/Sonnet ratio, cost efficiency)
        - Performance metrics (cache hit rate, latency)
        - Quality metrics (success rate, completion rate)
    """
    try:
        metrics = governor.get_usage_metrics()

        return MetricsResponse(
            status="success",
            metrics=metrics,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to get usage metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=WindowHistoryResponse)
async def get_window_history(
    limit: int = 24,
    governor: ResourceGovernor = Depends(get_resource_governor)
):
    """
    Get historical usage windows

    Args:
        limit: Maximum number of windows to return (default 24 = ~5 days)

    Returns:
        List of historical UsageWindow objects
    """
    try:
        windows = governor.get_window_history(limit=limit)

        return WindowHistoryResponse(
            status="success",
            windows=windows,
            count=len(windows),
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to get window history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/throttle")
async def control_throttle(
    request: ThrottleRequest,
    governor: ResourceGovernor = Depends(get_resource_governor)
):
    """
    Manually control throttling

    Actions:
    - "activate": Force throttle activation
    - "clear": Clear throttle flag

    Args:
        request: Throttle control request

    Returns:
        Updated budget status
    """
    try:
        if request.action == "activate":
            governor.force_throttle(request.reason)
            message = f"Throttling activated: {request.reason}"

        elif request.action == "clear":
            governor.clear_throttle()
            message = "Throttling cleared"

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {request.action}. Use 'activate' or 'clear'"
            )

        budget = governor.get_budget_status()

        return {
            "status": "success",
            "message": message,
            "budget": budget,
            "timestamp": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control throttle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(governor: ResourceGovernor = Depends(get_resource_governor)):
    """
    Health check for Resource Governor

    Checks:
    - Redis connectivity
    - Window validity
    - Overall system health

    Returns:
        Health status dictionary
    """
    try:
        health = await governor.health_check()

        status_code = 200 if health.get("healthy") else 503

        return {
            "status": "healthy" if health.get("healthy") else "unhealthy",
            "details": health,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }


@router.post("/record-usage")
async def record_usage(
    model_type: ModelType,
    messages: int = 1,
    input_tokens: int = 0,
    output_tokens: int = 0,
    governor: ResourceGovernor = Depends(get_resource_governor)
):
    """
    Manually record usage (for external integrations)

    Args:
        model_type: Model used (Opus or Sonnet)
        messages: Number of messages
        input_tokens: Input tokens consumed
        output_tokens: Output tokens consumed

    Returns:
        Updated budget status
    """
    try:
        governor._record_usage(
            model_type=model_type,
            messages=messages,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        budget = governor.get_budget_status()

        return {
            "status": "success",
            "message": f"Recorded {messages} messages for {model_type.value}",
            "budget": budget,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Failed to record usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_budget_summary(governor: ResourceGovernor = Depends(get_resource_governor)):
    """
    Get a comprehensive budget summary

    Returns:
        Consolidated view of budget status, metrics, and health
    """
    try:
        budget = governor.get_budget_status()
        metrics = governor.get_usage_metrics()
        health = await governor.health_check()

        return {
            "status": "success",
            "summary": {
                "budget_health": budget.budget_health,
                "is_throttling": budget.is_throttling,
                "throttle_reason": budget.throttle_reason,
                "usage_percentage": budget.current_window.get_usage_percentage() if budget.current_window else 0,
                "messages_remaining": budget.estimated_messages_remaining_today,
                "opus_sonnet_ratio": budget.opus_sonnet_ratio,
                "cost_efficiency": metrics.cost_efficiency,
                "messages_per_hour": metrics.messages_per_hour,
                "system_health": health.get("healthy", False)
            },
            "budget": budget,
            "metrics": metrics,
            "health": health,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Failed to get budget summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
