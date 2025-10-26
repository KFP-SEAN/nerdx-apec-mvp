"""
Lead Report Router
Salesforce Lead 데이터 기반 일일 리포트 API
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import date
from services.lead_report_service import lead_report_service

router = APIRouter(prefix="/api/v1/lead-report", tags=["Lead Report"])


@router.post("/send")
async def send_lead_report(
    email: str = Query(..., description="Report recipient email")
):
    """
    Send Lead daily report via email

    Args:
        email: Recipient email address

    Returns:
        Report send status
    """
    try:
        success = lead_report_service.generate_and_send_report(email)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate or send report"
            )

        # Get basic stats for response
        access_token = lead_report_service.get_salesforce_access_token()
        leads = []
        if access_token:
            leads = lead_report_service.get_all_leads(access_token)

        tier1_count = len([l for l in leads if l.get("NBRS_Tier__c") == "TIER1"])
        tier2_count = len([l for l in leads if l.get("NBRS_Tier__c") == "TIER2"])

        return {
            "message": "Lead report sent successfully",
            "email": email,
            "report_date": date.today().isoformat(),
            "total_leads": len(leads),
            "tier1_count": tier1_count,
            "tier2_count": tier2_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
