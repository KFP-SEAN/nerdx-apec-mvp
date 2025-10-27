"""
Brands Router - 브랜드 프로필 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from agents.market_intel_agent import market_intel_agent


router = APIRouter(prefix="/api/v1/brands", tags=["Brands"])


class BrandProfile(BaseModel):
    """브랜드 프로필"""
    brand_id: str
    brand_name: str
    company_name: str
    nice_classification: List[str]
    registration_date: str
    status: str
    country: str
    financial_data: Optional[dict] = None
    news_data: Optional[dict] = None


@router.get("/", response_model=List[dict])
async def get_brands(
    country: str = Query("KR", description="국가 코드"),
    limit: int = Query(50, description="조회 개수")
):
    """
    브랜드 목록 조회

    **MarketIntelAgent**가 WIPO, KIS 데이터를 수집합니다.
    """
    task = {
        "task_id": f"get_brands_{country}",
        "task_type": "collect_brand_data",
        "parameters": {
            "country": country,
            "limit": limit
        }
    }

    result = await market_intel_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    return result["result"]


@router.get("/{brand_name}/profile", response_model=dict)
async def get_brand_profile(
    brand_name: str,
    company_name: str = Query(..., description="기업명")
):
    """
    브랜드 종합 프로필 조회

    WIPO + KIS + 뉴스 데이터 통합
    """
    profile = await market_intel_agent.get_brand_profile(brand_name, company_name)

    return profile


@router.get("/{brand_name}/news", response_model=dict)
async def get_brand_news(
    brand_name: str,
    days: int = Query(7, description="조회 기간 (일)")
):
    """
    브랜드 뉴스 및 감성 분석
    """
    task = {
        "task_id": f"news_{brand_name}",
        "task_type": "monitor_news",
        "parameters": {
            "brand_name": brand_name,
            "days": days
        }
    }

    result = await market_intel_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]
