"""
Daily Reports API Router
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models.report_models import DailyReportData
from services.report_generator.daily_report_service import daily_report_service
from services.email_sender.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get("/daily/{cell_id}", response_model=DailyReportData)
async def get_daily_report(
    cell_id: str,
    report_date: date,
    db: Session = Depends(get_db)
):
    """Get daily report data"""
    try:
        report_data = await daily_report_service.generate_report_data(
            db, cell_id, report_date
        )
        return report_data
    except Exception as e:
        logger.error(f"Failed to generate report data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily/{cell_id}/send")
async def send_daily_report(
    cell_id: str,
    report_date: date,
    db: Session = Depends(get_db)
):
    """Generate and send daily report via email"""
    try:
        success = await daily_report_service.generate_and_send_report(
            db, cell_id, report_date
        )

        if success:
            return {
                "message": "Daily report sent successfully",
                "cell_id": cell_id,
                "report_date": report_date.isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send report")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email(email: str):
    """Send test email"""
    try:
        success = await email_service.send_test_email(email)

        if success:
            return {"message": f"Test email sent to {email}"}
        else:
            error_detail = email_service.last_error or "Failed to send test email (no error details)"
            raise HTTPException(status_code=500, detail=error_detail)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
