"""
Workflows Router - 워크플로우 실행
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.orchestrator_agent import orchestrator_agent


router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


class ExecuteWorkflowRequest(BaseModel):
    """워크플로우 실행 요청"""
    workflow_name: str
    parameters: dict


@router.post("/execute", response_model=dict)
async def execute_workflow(request: ExecuteWorkflowRequest):
    """
    워크플로우 실행

    **사용 가능한 워크플로우**:
    - `find_top_resonant_brands`: 상위 10% 공명 브랜드 발굴
    - `generate_partnership_pipeline`: 전체 파이프라인 (데이터 수집 → 분석 → 개요서 → NotebookLM)
    """
    task = {
        "task_id": f"workflow_{request.workflow_name}",
        "task_type": "execute_workflow",
        "parameters": request.parameters | {"workflow_name": request.workflow_name}
    }

    result = await orchestrator_agent.execute_task(task)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result["result"]


@router.post("/find-top-brands", response_model=dict)
async def find_top_brands(
    anchor_brand: dict,
    target_country: str = "KR"
):
    """
    상위 10% 공명 브랜드 발굴 (워크플로우 단축키)

    **Steps**:
    1. MarketIntelAgent: 브랜드 데이터 수집
    2. ResonanceModelingAgent: 공명 지수 계산 및 랭킹
    3. ContentStrategyAgent: 협력 개요서 생성
    """
    request = ExecuteWorkflowRequest(
        workflow_name="find_top_resonant_brands",
        parameters={
            "anchor_brand": anchor_brand,
            "target_country": target_country
        }
    )

    return await execute_workflow(request)


@router.post("/partnership-pipeline", response_model=dict)
async def partnership_pipeline(
    anchor_brand: dict,
    target_country: str = "KR"
):
    """
    파트너십 파이프라인 (전체 프로세스)

    **Steps**:
    1. 브랜드 데이터 수집
    2. 공명 분석
    3. 협력 개요서 생성
    4. NotebookLM 데이터 준비
    5. Google Docs 내보내기 준비
    """
    request = ExecuteWorkflowRequest(
        workflow_name="partnership_pipeline",
        parameters={
            "anchor_brand": anchor_brand,
            "target_country": target_country
        }
    )

    return await execute_workflow(request)


@router.post("/evaluate-workflow", response_model=dict)
async def evaluate_workflow(workflow_result: dict):
    """
    워크플로우 품질 평가 (Critic)

    **평가 지표**:
    - Completion Rate
    - Data Quality
    - Execution Time
    - Overall Score
    """
    evaluation = await orchestrator_agent.evaluate_workflow_quality(workflow_result)

    return evaluation
