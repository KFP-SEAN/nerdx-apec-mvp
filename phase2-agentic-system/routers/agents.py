"""
Agent API Endpoints
Phase 3A: Zeitgeist & Bard Agents
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from services.agents.zeitgeist_agent import get_zeitgeist_agent
from services.agents.bard_agent import get_bard_agent

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class AgentTaskRequest(BaseModel):
    """Generic agent task request"""
    task_type: str
    parameters: Dict[str, Any]

class AgentTaskResponse(BaseModel):
    """Generic agent task response"""
    agent_id: str
    agent_type: str
    task_id: str
    status: str
    confidence: float
    result: Dict[str, Any]
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


# Zeitgeist Agent Endpoints

@router.post("/zeitgeist/analyze-trends")
async def zeitgeist_analyze_trends(
    days_back: int = 7,
    categories: Optional[List[str]] = None,
    min_confidence: float = 0.6
):
    """
    Analyze market trends using Zeitgeist agent

    Detects trending topics across social media, NERDX platform, and e-commerce.
    """
    try:
        agent = get_zeitgeist_agent()

        task_id = f"trend-analysis-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="analyze_trends",
            parameters={
                "days_back": days_back,
                "categories": categories or [],
                "min_confidence": min_confidence
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/zeitgeist/identify-opportunities")
async def zeitgeist_identify_opportunities(
    trend_data: Optional[List[Dict[str, Any]]] = None,
    min_opportunity_score: float = 0.7,
    max_opportunities: int = 5
):
    """
    Identify product opportunities from market trends

    Analyzes trends and recommends concrete product opportunities.
    """
    try:
        agent = get_zeitgeist_agent()

        task_id = f"opportunity-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="identify_opportunities",
            parameters={
                "trend_data": trend_data,
                "min_opportunity_score": min_opportunity_score,
                "max_opportunities": max_opportunities
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Opportunity identification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/zeitgeist/weekly-report")
async def zeitgeist_weekly_report(
    week_start: Optional[str] = None,
    include_opportunities: bool = True
):
    """
    Generate comprehensive weekly trend report

    Full market intelligence report with trends, opportunities, and recommendations.
    """
    try:
        from datetime import datetime
        agent = get_zeitgeist_agent()

        task_id = f"weekly-report-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        params = {"include_opportunities": include_opportunities}
        if week_start:
            params["week_start"] = datetime.fromisoformat(week_start)

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_weekly_report",
            parameters=params
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Bard Agent Endpoints

@router.post("/bard/generate-story")
async def bard_generate_story(
    product_name: str,
    product_description: str = "",
    key_ingredients: List[str] = [],
    origin_story: str = "",
    storytelling_style: str = "luxury",
    target_audience: str = "Sophisticated millennials"
):
    """
    Generate luxury brand narrative

    Creates Moët Hennessy-style brand storytelling for products.
    """
    try:
        from datetime import datetime
        agent = get_bard_agent()

        task_id = f"story-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_brand_story",
            parameters={
                "product_name": product_name,
                "product_description": product_description,
                "key_ingredients": key_ingredients,
                "origin_story": origin_story,
                "storytelling_style": storytelling_style,
                "target_audience": target_audience
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bard/create-campaign")
async def bard_create_campaign(
    product_name: str,
    campaign_objective: str = "product launch",
    target_channels: List[str] = ["instagram", "tiktok", "youtube"],
    budget_range: str = "medium",
    timeline: str = "4 weeks",
    brand_narrative: Optional[Dict[str, Any]] = None
):
    """
    Create comprehensive marketing campaign

    Generates full 360° campaign with content across all channels.
    """
    try:
        from datetime import datetime
        agent = get_bard_agent()

        task_id = f"campaign-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="create_campaign",
            parameters={
                "product_name": product_name,
                "campaign_objective": campaign_objective,
                "target_channels": target_channels,
                "budget_range": budget_range,
                "timeline": timeline,
                "brand_narrative": brand_narrative
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Campaign creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bard/atomize-content")
async def bard_atomize_content(
    pillar_content: str,
    content_type: str = "blog",
    target_formats: List[str] = ["social_post", "video_script", "email"],
    count_per_format: int = 3
):
    """
    Atomize content using Turkey Slice method

    Transforms one pillar content into multiple micro-content pieces.
    """
    try:
        from datetime import datetime
        agent = get_bard_agent()

        task_id = f"atomize-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="atomize_content",
            parameters={
                "pillar_content": pillar_content,
                "content_type": content_type,
                "target_formats": target_formats,
                "count_per_format": count_per_format
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Content atomization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bard/content-piece")
async def bard_generate_content_piece(
    format: str,  # social_post, video_script, email, etc.
    platform: str = "instagram",
    product_name: str = "",
    key_message: str = "",
    tone: str = "aspirational",
    duration_seconds: Optional[int] = None
):
    """
    Generate single optimized content piece

    Creates platform-specific content optimized for engagement.
    """
    try:
        from datetime import datetime
        agent = get_bard_agent()

        task_id = f"content-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_content_piece",
            parameters={
                "format": format,
                "platform": platform,
                "product_name": product_name,
                "key_message": key_message,
                "tone": tone,
                "duration_seconds": duration_seconds
            }
        )

        return AgentTaskResponse(**response.model_dump())

    except Exception as e:
        logger.error(f"Content piece generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
