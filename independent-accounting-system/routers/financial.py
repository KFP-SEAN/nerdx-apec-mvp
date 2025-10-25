"""
Financial Tracking API Router
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models.financial_models import DailyFinancialSummary, MonthlyFinancialSummary
from services.financial_tracker.financial_service import financial_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/financial", tags=["Financial"])


@router.post("/sync/{cell_id}/revenue")
async def sync_revenue(
    cell_id: str,
    target_date: date,
    db: Session = Depends(get_db)
):
    """Sync revenue from Salesforce"""
    try:
        count = await financial_service.sync_cell_revenue(db, cell_id, target_date)
        return {
            "message": f"Synced {count} revenue records",
            "cell_id": cell_id,
            "date": target_date.isoformat(),
            "count": count
        }
    except Exception as e:
        logger.error(f"Failed to sync revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/{cell_id}/costs")
async def sync_costs(
    cell_id: str,
    target_date: date,
    db: Session = Depends(get_db)
):
    """Sync costs from Odoo"""
    try:
        count = await financial_service.sync_cell_costs(db, cell_id, target_date)
        return {
            "message": f"Synced {count} cost records",
            "cell_id": cell_id,
            "date": target_date.isoformat(),
            "count": count
        }
    except Exception as e:
        logger.error(f"Failed to sync costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/daily/{cell_id}", response_model=DailyFinancialSummary)
async def get_daily_summary(
    cell_id: str,
    summary_date: date,
    db: Session = Depends(get_db)
):
    """Get daily financial summary"""
    try:
        summary = await financial_service.calculate_daily_summary(
            db, cell_id, summary_date
        )
        return summary
    except Exception as e:
        logger.error(f"Failed to get daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/monthly/{cell_id}", response_model=MonthlyFinancialSummary)
async def get_monthly_summary(
    cell_id: str,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get monthly financial summary (MTD)"""
    try:
        summary = await financial_service.get_monthly_summary(
            db, cell_id, year, month
        )
        return summary
    except Exception as e:
        logger.error(f"Failed to get monthly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
