"""
Dashboard Router - MVP 명령 콘솔
"""
from fastapi import APIRouter
from agents.orchestrator_agent import orchestrator_agent
from agents.market_intel_agent import market_intel_agent
from agents.resonance_modeling_agent import resonance_modeling_agent
from agents.content_strategy_agent import content_strategy_agent


router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/agents-status", response_model=dict)
async def get_agents_status():
    """
    모든 에이전트 상태 조회

    **Multi-Agent System (MAS)** 헬스 체크
    """
    return {
        "orchestrator": orchestrator_agent.get_status(),
        "market_intel": market_intel_agent.get_status(),
        "resonance_modeling": resonance_modeling_agent.get_status(),
        "content_strategy": content_strategy_agent.get_status()
    }


@router.get("/kpis", response_model=dict)
async def get_kpis():
    """
    핵심 KPI 대시보드

    **새로운 KPI 프레임워크**:
    - 공명 조정 LTV/CAC 비율
    - 자동화된 의사결정 비율
    - 모델 학습 속도
    - 에이전트 생성 수익
    """
    # Mock KPIs (실제로는 DB/Redis에서 조회)
    return {
        "north_star_metric": {
            "name": "공명 조정 LTV/CAC 비율",
            "value": 5.2,
            "target": 5.0,
            "status": "above_target"
        },
        "autonomy_kpis": {
            "automated_decision_rate": {
                "name": "자동화된 의사결정 비율",
                "value": 0.87,
                "target": 0.95,
                "unit": "ratio"
            },
            "model_learning_speed": {
                "name": "모델 학습 속도 (주간 AUC 상승률)",
                "value": 0.043,
                "target": 0.05,
                "unit": "ratio"
            }
        },
        "business_impact_kpis": {
            "agent_generated_revenue_mrr": {
                "name": "에이전트 생성 수익 (MRR)",
                "value": 120_000_000,  # 1.2억
                "target": 500_000_000,  # 5억
                "unit": "KRW"
            }
        },
        "t2d3_progress": {
            "current_arr": 60_000_000_000,  # 600억 (가정)
            "year1_target": 180_000_000_000,  # 1,800억
            "progress_percentage": 33.3
        }
    }


@router.get("/model-version", response_model=dict)
async def get_model_version():
    """
    현재 NBRS 모델 버전 정보
    """
    from config import settings

    return {
        "nbrs_version": settings.nbrs_model_version,
        "update_frequency": settings.nbrs_update_frequency,
        "last_updated": "2025-10-27T12:00:00Z",  # Mock
        "model_weights": resonance_modeling_agent.model_weights
    }


@router.get("/prediction-history", response_model=list)
async def get_prediction_history(limit: int = 100):
    """
    공명 지수 계산 이력

    **지속적 학습 (CL)**을 위한 데이터 소스
    """
    history = resonance_modeling_agent.prediction_history[-limit:]
    return history
