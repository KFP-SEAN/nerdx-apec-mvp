"""
Project Sonar - Main Application
AI 브랜드 공명 분석 시스템
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import brands, resonance, collaborations, workflows, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Project Sonar - AI 브랜드 공명 분석 시스템",
    description="""
    **프로젝트 소나 (Project Sonar)**

    NERD12 AI-Native 시스템의 자율적, 자기 진화형 에이전트 플랫폼

    ## 핵심 기능

    - **Multi-Agent System (MAS)**: 전문화된 에이전트 협업
    - **NBRS 2.0**: 브랜드 공명 지수 계산
    - **자동화된 협력 개요서 생성**: AI 기반 파트너십 제안
    - **지속적 학습 (Continual Learning)**: 자기 개선 시스템

    ## 에이전트

    1. **OrchestratorAgent**: 작업 분해 및 위임
    2. **MarketIntelAgent**: WIPO, KIS, 뉴스 데이터 수집
    3. **ResonanceModelingAgent**: 공명 지수 계산 및 모델 최적화
    4. **ContentStrategyAgent**: AI 기반 협력 개요서 생성

    ## T2D3 목표

    - 1-2년차: 180억 ARR (Triple)
    - 3년차: 540억 ARR (Triple)
    - 4년차: 1,080억 ARR (Double)
    - 5년차: 2,160억 ARR (Double)
    - 6년차+: 4,320억 ARR (Double)
    """,
    version="1.0.0-mvp",
    contact={
        "name": "NERDX Team",
        "email": "sean@koreafnbpartners.com"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(brands.router)
app.include_router(resonance.router)
app.include_router(collaborations.router)
app.include_router(workflows.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Project Sonar - AI 브랜드 공명 분석 시스템",
        "version": "1.0.0-mvp",
        "status": "running",
        "description": "공명 경제(Resonance Economy) 창출을 위한 자율 에이전트 플랫폼",
        "endpoints": {
            "brands": "/api/v1/brands",
            "resonance": "/api/v1/resonance",
            "collaborations": "/api/v1/collaborations",
            "workflows": "/api/v1/workflows",
            "dashboard": "/api/v1/dashboard"
        },
        "t2d3_goal": "MRR 5억 → 1000억 (200x 성장)",
        "target_market": "대한민국 (MVP)"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from agents.orchestrator_agent import orchestrator_agent
    from agents.market_intel_agent import market_intel_agent
    from agents.resonance_modeling_agent import resonance_modeling_agent
    from agents.content_strategy_agent import content_strategy_agent

    agents_status = {
        "orchestrator": orchestrator_agent.get_status(),
        "market_intel": market_intel_agent.get_status(),
        "resonance_modeling": resonance_modeling_agent.get_status(),
        "content_strategy": content_strategy_agent.get_status()
    }

    return {
        "status": "healthy",
        "environment": settings.api_environment,
        "agents": agents_status,
        "mas_operational": all(agent["state"] != "error" for agent in agents_status.values())
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 70)
    logger.info("Project Sonar - AI 브랜드 공명 분석 시스템 Starting...")
    logger.info(f"Environment: {settings.api_environment}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"NBRS Model Version: {settings.nbrs_model_version}")
    logger.info("=" * 70)
    logger.info("Multi-Agent System (MAS) Initialized:")
    logger.info("  - OrchestratorAgent")
    logger.info("  - MarketIntelAgent")
    logger.info("  - ResonanceModelingAgent")
    logger.info("  - ContentStrategyAgent")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Project Sonar Shutting Down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.api_environment == "development")
    )
