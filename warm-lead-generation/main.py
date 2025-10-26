"""
NERDX Warm Lead Generation System - Main Application
NERD12 웜리드 발굴 시스템 - 메인 애플리케이션
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import lead_scoring, lead_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NERDX Warm Lead Generation System",
    description="NERD12 웜리드 발굴 시스템 - NBRS 기반 리드 스코어링",
    version="1.1.0-lead-report"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lead_scoring.router)
app.include_router(lead_report.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NERDX Warm Lead Generation System",
        "version": "1.1.0-lead-report",
        "status": "running",
        "lead_report_enabled": True
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.api_environment,
        "helios_url": settings.helios_api_url
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 70)
    logger.info("NERDX Warm Lead Generation System Starting...")
    logger.info(f"Environment: {settings.api_environment}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"Helios API: {settings.helios_api_url}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("NERDX Warm Lead Generation System Shutting Down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.api_environment == "development")
    )
