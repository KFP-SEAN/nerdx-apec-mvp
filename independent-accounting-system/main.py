"""
NERDX Independent Accounting System - Main Application
NERDX 독립채산제 시스템 메인 애플리케이션
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers import cells, financial, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting NERDX Independent Accounting System")
    logger.info(f"Environment: {settings.api_environment}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down NERDX Independent Accounting System")


app = FastAPI(
    title="NERDX Independent Accounting System",
    description="독립채산제 셀별 P&L 추적 및 일간 리포트 자동화 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cells.router)
app.include_router(financial.router)
app.include_router(reports.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nerdx-independent-accounting-system",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NERDX Independent Accounting System",
        "version": "1.0.0",
        "description": "독립채산제 셀별 P&L 추적 및 일간 리포트 자동화",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",

            # Cell management
            "create_cell": "POST /api/v1/cells/",
            "get_cell": "GET /api/v1/cells/{cell_id}",
            "list_cells": "GET /api/v1/cells/",
            "update_cell": "PUT /api/v1/cells/{cell_id}",
            "delete_cell": "DELETE /api/v1/cells/{cell_id}",

            # Financial tracking
            "sync_revenue": "POST /api/v1/financial/sync/{cell_id}/revenue",
            "sync_costs": "POST /api/v1/financial/sync/{cell_id}/costs",
            "get_daily_summary": "GET /api/v1/financial/summary/daily/{cell_id}",
            "get_monthly_summary": "GET /api/v1/financial/summary/monthly/{cell_id}",

            # Reports
            "get_daily_report": "GET /api/v1/reports/daily/{cell_id}",
            "send_daily_report": "POST /api/v1/reports/daily/{cell_id}/send",
            "test_email": "POST /api/v1/reports/test-email"
        },
        "integrations": {
            "salesforce": "Revenue data from CRM",
            "odoo": "Cost data from ERP",
            "email": "Daily report delivery"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_environment == "development",
        log_level="info"
    )
