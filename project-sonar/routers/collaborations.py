"""
Collaborations Router - 협력 개요서 생성
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from agents.content_strategy_agent import content_strategy_agent


router = APIRouter(prefix="/api/v1/collaborations", tags=["Collaborations"])


class GenerateBriefRequest(BaseModel):
    """협력 개요서 생성 요청"""
    anchor_brand: dict
    target_brand: dict
    resonance_data: dict


class BatchBriefRequest(BaseModel):
    """일괄 개요서 생성 요청"""
    anchor_brand: dict
    target_brands: List[dict]
    resonance_results: List[dict]


@router.post("/generate-brief", response_model=dict)
async def generate_brief(request: GenerateBriefRequest):
    """
    협력 개요서 생성 (AI 기반)

    **LLM (Claude/Gemini)**을 사용하여 자동 생성:
    - Executive Summary
    - 파트너십 아이디어 2-3개
    - 예상 성과 (정량적 + 정성적)
    - Next Steps
    """
    task = {
        "task_id": f"brief_{request.anchor_brand.get('brand_name')}_{request.target_brand.get('brand_name')}",
        "task_type": "generate_brief",
        "parameters": {
            "anchor_brand": request.anchor_brand,
            "target_brand": request.target_brand,
            "resonance_data": request.resonance_data
        }
    }

    result = await content_strategy_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.post("/generate-batch-briefs", response_model=List[dict])
async def generate_batch_briefs(request: BatchBriefRequest):
    """
    일괄 협력 개요서 생성

    상위 10% 브랜드에 대해 일괄 생성
    """
    task = {
        "task_id": f"batch_briefs_{request.anchor_brand.get('brand_name')}",
        "task_type": "generate_batch_briefs",
        "parameters": {
            "anchor_brand": request.anchor_brand,
            "target_brands": request.target_brands,
            "resonance_results": request.resonance_results
        }
    }

    result = await content_strategy_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.post("/prepare-notebooklm", response_model=dict)
async def prepare_notebooklm_data(
    brand_data: dict,
    resonance_data: dict,
    brief: dict
):
    """
    NotebookLM 최적화 데이터 생성

    **Google NotebookLM** 포맷:
    - 엔티티 태깅 (브랜드, 인물, 장소, 개념)
    - 관계 그래프 (Triples)
    - 제안 프롬프트
    """
    task = {
        "task_id": f"notebooklm_{brand_data.get('brand_name')}",
        "task_type": "prepare_notebooklm_data",
        "parameters": {
            "brand_data": brand_data,
            "resonance_data": resonance_data,
            "brief": brief
        }
    }

    result = await content_strategy_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]
