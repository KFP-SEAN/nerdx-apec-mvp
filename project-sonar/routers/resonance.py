"""
Resonance Router - 브랜드 공명 분석
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from agents.resonance_modeling_agent import resonance_modeling_agent


router = APIRouter(prefix="/api/v1/resonance", tags=["Resonance"])


class CalculateResonanceRequest(BaseModel):
    """공명 지수 계산 요청"""
    anchor_brand: dict
    target_brand: dict


class RankBrandsRequest(BaseModel):
    """브랜드 랭킹 요청"""
    anchor_brand: dict
    target_brands: List[dict]


@router.post("/calculate", response_model=dict)
async def calculate_resonance(request: CalculateResonanceRequest):
    """
    브랜드 간 공명 지수 계산

    **NBRS 2.0 모델**을 사용하여 5가지 요소 분석:
    - 브랜드 카테고리 중복 (30%)
    - 타겟 고객 유사성 (25%)
    - 미디어 동시 언급 (20%)
    - 시장 포지셔닝 (15%)
    - 지리적 중복 (10%)
    """
    task = {
        "task_id": f"calculate_{request.anchor_brand.get('brand_name')}_{request.target_brand.get('brand_name')}",
        "task_type": "calculate_resonance",
        "parameters": {
            "anchor_brand": request.anchor_brand,
            "target_brand": request.target_brand
        }
    }

    result = await resonance_modeling_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.post("/rank", response_model=List[dict])
async def rank_brands(request: RankBrandsRequest):
    """
    브랜드 공명 지수 순위 정렬

    **상위 10%** 웜리드 발굴 (NERD12 목표)
    """
    task = {
        "task_id": f"rank_{request.anchor_brand.get('brand_name')}",
        "task_type": "rank_brands",
        "parameters": {
            "anchor_brand": request.anchor_brand,
            "target_brands": request.target_brands
        }
    }

    result = await resonance_modeling_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.post("/retrain", response_model=dict)
async def retrain_model(training_data: List[dict]):
    """
    NBRS 모델 재학습 (Continual Learning)

    실제 파트너십 성과 데이터를 사용하여 모델 개선
    """
    task = {
        "task_id": "retrain_model",
        "task_type": "retrain_model",
        "parameters": {
            "training_data": training_data
        }
    }

    result = await resonance_modeling_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.get("/model-performance", response_model=dict)
async def get_model_performance():
    """
    NBRS 모델 성능 지표

    - AUC (Area Under Curve)
    - 학습 속도 (Learning Speed)
    - 모델 버전
    """
    task = {
        "task_id": "evaluate_model",
        "task_type": "evaluate_model",
        "parameters": {
            "test_data": []  # 실제로는 검증 데이터 필요
        }
    }

    result = await resonance_modeling_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]
