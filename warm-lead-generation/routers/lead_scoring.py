"""
Lead Scoring API Router
리드 스코어링 API 엔드포인트
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from models.nbrs_models import (
    NBRSResult,
    BrandAffinityScore,
    MarketPositioningScore,
    DigitalPresenceScore,
    LeadEnrichmentRequest,
    LeadTier
)
from services.nbrs_engine import nbrs_engine
from integrations.helios_client import helios_client
from integrations.salesforce_client import salesforce_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/lead-scoring", tags=["Lead Scoring"])


class CalculateNBRSRequest(BaseModel):
    """Request to calculate NBRS for a lead"""
    lead_id: str
    company_name: str
    brand_affinity: BrandAffinityScore
    market_positioning: MarketPositioningScore
    digital_presence: DigitalPresenceScore
    update_salesforce: bool = True


class EnrichAndScoreRequest(BaseModel):
    """Request to enrich and score a lead"""
    lead_id: str
    company_name: str
    company_domain: Optional[str] = None


class BatchScoreRequest(BaseModel):
    """Request to score multiple leads"""
    lead_ids: List[str]


@router.post("/calculate", response_model=NBRSResult)
async def calculate_nbrs(request: CalculateNBRSRequest):
    """
    Calculate NBRS score for a lead

    This endpoint calculates the NBRS score based on provided data.
    """
    try:
        # Calculate NBRS
        result = nbrs_engine.calculate_nbrs(
            lead_id=request.lead_id,
            company_name=request.company_name,
            brand_affinity=request.brand_affinity,
            market_positioning=request.market_positioning,
            digital_presence=request.digital_presence
        )

        # Update Salesforce if requested
        if request.update_salesforce:
            success = salesforce_client.update_lead_nbrs(request.lead_id, result)
            if success:
                # Publish Platform Event
                salesforce_client.publish_nbrs_calculated_event(result)

        return result

    except Exception as e:
        logger.error(f"Failed to calculate NBRS for {request.lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich-and-score", response_model=NBRSResult)
async def enrich_and_score(request: EnrichAndScoreRequest):
    """
    Enrich lead data via Helios and calculate NBRS

    This is the recommended endpoint for new leads.
    It fetches company intelligence from Helios and calculates NBRS.
    """
    try:
        # Step 1: Enrich lead data via Helios
        logger.info(f"[API] Enriching lead {request.lead_id} via Helios...")

        enrichment_request = LeadEnrichmentRequest(
            lead_id=request.lead_id,
            company_name=request.company_name,
            company_domain=request.company_domain
        )

        enriched_data = await helios_client.enrich_lead(enrichment_request)

        # Step 2: Fetch Salesforce activity data
        logger.info(f"[API] Fetching Salesforce activities for {request.lead_id}...")
        activities = salesforce_client.get_lead_activities(request.lead_id)

        # Step 3: Calculate component scores
        # Brand Affinity (using Salesforce activities)
        brand_affinity = BrandAffinityScore(
            salesforce_activity_score=min(activities["total_activities"] * 10, 100),
            email_engagement_score=min(len(activities["emails"]) * 20, 100),
            meeting_history_score=min(len(activities["events"]) * 25, 100),
            contact_frequency_score=70.0  # Placeholder
        )

        # Market Positioning (using Helios enriched data)
        market_positioning = MarketPositioningScore(
            annual_revenue_usd=enriched_data.annual_revenue_usd,
            employee_count=enriched_data.employee_count,
            target_industry_match=True if enriched_data.industry else False,
            pain_point_alignment=60.0  # Placeholder
        )

        # Digital Presence (using Helios enriched data)
        digital_presence = DigitalPresenceScore(
            website_traffic_monthly=enriched_data.website_traffic_monthly,
            social_media_followers=enriched_data.social_media_followers,
            content_engagement_score=50.0,  # Placeholder
            has_modern_website=True if enriched_data.tech_stack else False
        )

        # Step 4: Calculate NBRS
        result = nbrs_engine.calculate_nbrs(
            lead_id=request.lead_id,
            company_name=request.company_name,
            brand_affinity=brand_affinity,
            market_positioning=market_positioning,
            digital_presence=digital_presence
        )

        # Step 5: Update Salesforce
        salesforce_client.update_lead_nbrs(request.lead_id, result)
        salesforce_client.publish_nbrs_calculated_event(result)

        logger.info(f"[API] Successfully scored {request.company_name}: NBRS={result.nbrs_score}")

        return result

    except Exception as e:
        logger.error(f"Failed to enrich and score {request.lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-score", response_model=List[NBRSResult])
async def batch_score(request: BatchScoreRequest):
    """
    Score multiple leads in batch

    Fetches leads from Salesforce, enriches via Helios, and calculates NBRS.
    """
    try:
        logger.info(f"[API] Batch scoring {len(request.lead_ids)} leads...")

        results = []

        for lead_id in request.lead_ids:
            # Fetch lead from Salesforce
            try:
                sf_leads = salesforce_client.fetch_leads()
                lead_data = next((l for l in sf_leads if l["Id"] == lead_id), None)

                if not lead_data:
                    logger.warning(f"[API] Lead {lead_id} not found in Salesforce")
                    continue

                # Enrich and score
                enrich_request = EnrichAndScoreRequest(
                    lead_id=lead_id,
                    company_name=lead_data["Company"],
                    company_domain=lead_data.get("Website")
                )

                result = await enrich_and_score(enrich_request)
                results.append(result)

            except Exception as e:
                logger.error(f"[API] Failed to score lead {lead_id}: {e}")
                continue

        # Rank all results
        ranked_results = nbrs_engine.rank_leads(results)

        # Bulk update Salesforce
        salesforce_client.bulk_update_leads(ranked_results)

        logger.info(f"[API] Batch scoring completed: {len(ranked_results)} leads scored")

        return ranked_results

    except Exception as e:
        logger.error(f"Batch scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-leads", response_model=List[NBRSResult])
async def get_top_leads(n: int = 10):
    """
    Get top N leads by NBRS score

    Returns the top 10% of leads (default 10 leads) as per PRD requirement.
    """
    try:
        # Get all leads from calculation history
        all_results = nbrs_engine.calculation_history

        if not all_results:
            return []

        # Get top N
        top_leads = nbrs_engine.get_top_n_leads(all_results, n=n)

        return top_leads

    except Exception as e:
        logger.error(f"Failed to get top leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-tier/{tier}", response_model=List[NBRSResult])
async def get_leads_by_tier(tier: LeadTier):
    """Filter leads by tier"""
    try:
        all_results = nbrs_engine.calculation_history
        filtered = nbrs_engine.filter_by_tier(all_results, tier)
        return filtered

    except Exception as e:
        logger.error(f"Failed to filter by tier {tier}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline-value")
async def get_pipeline_value():
    """
    Calculate total pipeline value

    Returns pipeline value breakdown by tier and expected revenue.
    """
    try:
        all_results = nbrs_engine.calculation_history

        if not all_results:
            return {
                "total_leads": 0,
                "total_pipeline_value_krw": 0,
                "expected_revenue_krw": 0,
                "by_tier": {}
            }

        pipeline_value = nbrs_engine.calculate_pipeline_value(all_results)

        return pipeline_value

    except Exception as e:
        logger.error(f"Failed to calculate pipeline value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_scoring_stats():
    """Get scoring statistics"""
    try:
        all_results = nbrs_engine.calculation_history

        if not all_results:
            return {
                "total_leads_scored": 0,
                "average_nbrs": 0,
                "tier_distribution": {}
            }

        # Calculate stats
        total_leads = len(all_results)
        avg_nbrs = sum(r.nbrs_score for r in all_results) / total_leads

        tier_distribution = {}
        for tier in LeadTier:
            count = len([r for r in all_results if r.tier == tier])
            tier_distribution[tier.value] = {
                "count": count,
                "percentage": (count / total_leads * 100) if total_leads > 0 else 0
            }

        return {
            "total_leads_scored": total_leads,
            "average_nbrs": round(avg_nbrs, 2),
            "tier_distribution": tier_distribution
        }

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
