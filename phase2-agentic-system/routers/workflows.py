"""
Workflow API Endpoints
Phase 3A: Master Planner Workflows
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from services.agents.master_planner import get_master_planner

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class CreateGoalRequest(BaseModel):
    """Create goal request"""
    title: str
    description: str
    objective: str
    parameters: Dict[str, Any]
    use_template: Optional[str] = None
    target_completion_days: int = 14

class ExecuteGoalRequest(BaseModel):
    """Execute goal request"""
    goal_id: str
    async_mode: bool = True


# Workflow Endpoints

@router.post("/create-goal")
async def create_goal(request: CreateGoalRequest):
    """
    Create new goal with task decomposition

    The Master Planner will break down the goal into executable tasks.
    """
    try:
        from datetime import datetime
        planner = await get_master_planner()

        task_id = f"create-goal-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await planner.execute_task(
            task_id=task_id,
            task_type="create_goal",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Goal creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/execute-goal")
async def execute_goal(request: ExecuteGoalRequest):
    """
    Execute goal workflow

    Executes all tasks required to achieve the goal.
    """
    try:
        from datetime import datetime
        planner = await get_master_planner()

        task_id = f"execute-goal-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await planner.execute_task(
            task_id=task_id,
            task_type="execute_goal",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Goal execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/goal-status/{goal_id}")
async def get_goal_status(goal_id: str):
    """
    Get goal execution status

    Returns current progress and task statuses.
    """
    try:
        from datetime import datetime
        planner = await get_master_planner()

        task_id = f"goal-status-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await planner.execute_task(
            task_id=task_id,
            task_type="get_goal_status",
            parameters={"goal_id": goal_id}
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Goal status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/cancel-goal/{goal_id}")
async def cancel_goal(goal_id: str):
    """Cancel active goal"""
    try:
        from datetime import datetime
        planner = await get_master_planner()

        task_id = f"cancel-goal-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await planner.execute_task(
            task_id=task_id,
            task_type="cancel_goal",
            parameters={"goal_id": goal_id}
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Goal cancellation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Pre-built Workflow Templates

@router.post("/new-product-launch")
async def new_product_launch_workflow(
    product_name: str,
    product_description: str = "",
    key_ingredients: List[str] = [],
    target_audience: str = "Sophisticated millennials",
    target_channels: List[str] = ["instagram", "tiktok", "youtube"]
):
    """
    End-to-end new product launch workflow

    Automated workflow: Trends → Opportunities → Story → Campaign
    """
    try:
        from datetime import datetime
        planner = await get_master_planner()

        # Create goal with template
        task_id = f"product-launch-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        create_response = await planner.execute_task(
            task_id=task_id,
            task_type="create_goal",
            parameters={
                "title": f"Launch {product_name}",
                "description": f"End-to-end product launch for {product_name}",
                "objective": "launch_product",
                "use_template": "new_product_launch",
                "parameters": {
                    "product_name": product_name,
                    "product_description": product_description,
                    "key_ingredients": key_ingredients,
                    "target_audience": target_audience,
                    "target_channels": target_channels
                },
                "target_completion_days": 14
            }
        )

        goal_id = create_response.result["goal"]["goal_id"]

        # Execute immediately
        execute_response = await planner.execute_task(
            task_id=f"execute-{goal_id}",
            task_type="execute_goal",
            parameters={
                "goal_id": goal_id,
                "async_mode": True
            }
        )

        return {
            "workflow": "new_product_launch",
            "goal_id": goal_id,
            "status": execute_response.status,
            "result": execute_response.result
        }

    except Exception as e:
        logger.error(f"Product launch workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/seasonal-campaign")
async def seasonal_campaign_workflow(
    product_name: str,
    campaign_objective: str = "seasonal_promotion",
    target_channels: List[str] = ["instagram", "tiktok"]
):
    """
    Seasonal campaign workflow

    Automated workflow: Platform Analysis → Campaign → Content Atomization
    """
    try:
        from datetime import datetime
        planner = await get_master_planner()

        task_id = f"seasonal-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        create_response = await planner.execute_task(
            task_id=task_id,
            task_type="create_goal",
            parameters={
                "title": f"Seasonal Campaign: {product_name}",
                "description": "Create and atomize seasonal campaign content",
                "objective": "create_campaign",
                "use_template": "seasonal_campaign",
                "parameters": {
                    "product_name": product_name,
                    "campaign_objective": campaign_objective,
                    "target_channels": target_channels
                },
                "target_completion_days": 7
            }
        )

        goal_id = create_response.result["goal"]["goal_id"]

        execute_response = await planner.execute_task(
            task_id=f"execute-{goal_id}",
            task_type="execute_goal",
            parameters={
                "goal_id": goal_id,
                "async_mode": True
            }
        )

        return {
            "workflow": "seasonal_campaign",
            "goal_id": goal_id,
            "status": execute_response.status,
            "result": execute_response.result
        }

    except Exception as e:
        logger.error(f"Seasonal campaign workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
