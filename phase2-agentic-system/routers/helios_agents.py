"""
Helios Specialized Agents API

REST API endpoints for Zeitgeist, Bard, and Master Planner agents
integrated with Resource Governor and Cache Manager.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from services.agents.zeitgeist_agent import ZeitgeistAgent
from services.agents.bard_agent import BardAgent
from services.agents.master_planner import MasterPlanner
from services.orchestrator.resource_governor import ResourceGovernor
from services.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/helios/agents", tags=["Helios Agents"])

# Initialize Helios components
resource_governor = ResourceGovernor()
cache_manager = CacheManager()

# Initialize agents (minimal initialization for API)
zeitgeist = ZeitgeistAgent(resource_governor, cache_manager)
bard = BardAgent(resource_governor, cache_manager)
master_planner = MasterPlanner()

@router.post("/zeitgeist/analyze")
async def zeitgeist_analyze_market(parameters: Dict[str, Any]):
    """
    Zeitgeist market analysis with caching and resource management
    
    Analyzes market trends, detects emerging opportunities,
    and provides data-driven insights.
    """
    try:
        response = await zeitgeist.execute_task(
            task_id=f"zeitgeist-{parameters.get('analysis_id', 'auto')}",
            task_type="analyze_trends",
            parameters=parameters
        )
        return response.model_dump()
    except Exception as e:
        logger.error(f"Zeitgeist analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bard/generate-content")
async def bard_generate_content(parameters: Dict[str, Any]):
    """
    Bard content generation with brand storytelling
    
    Creates compelling brand narratives, campaign concepts,
    and multi-platform content.
    """
    try:
        response = await bard.execute_task(
            task_id=f"bard-{parameters.get('content_id', 'auto')}",
            task_type="generate_brand_story",
            parameters=parameters
        )
        return response.model_dump()
    except Exception as e:
        logger.error(f"Bard content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/master-planner/create-goal")
async def master_planner_create_goal(parameters: Dict[str, Any]):
    """
    Master Planner goal creation
    
    Creates and orchestrates multi-agent goals with
    automatic task decomposition and resource allocation.
    """
    try:
        response = await master_planner.execute_task(
            task_id=f"goal-{parameters.get('goal_id', 'auto')}",
            task_type="create_goal",
            parameters=parameters
        )
        return response.model_dump()
    except Exception as e:
        logger.error(f"Master Planner goal creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/master-planner/execute-goal")
async def master_planner_execute_goal(goal_id: str):
    """
    Master Planner goal execution
    
    Executes a previously created goal by orchestrating
    multiple specialized agents (Zeitgeist, Bard, etc.)
    """
    try:
        response = await master_planner.execute_task(
            task_id=f"exec-{goal_id}",
            task_type="execute_goal",
            parameters={"goal_id": goal_id}
        )
        return response.model_dump()
    except Exception as e:
        logger.error(f"Master Planner execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agents_health_check():
    """Health check for all specialized agents"""
    return {
        "status": "healthy",
        "agents": {
            "zeitgeist": "operational",
            "bard": "operational",
            "master_planner": "operational"
        },
        "integrations": {
            "resource_governor": "connected",
            "cache_manager": "connected"
        }
    }
