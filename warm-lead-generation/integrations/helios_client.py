"""
Helios Integration Client
Helios 모델 연동 클라이언트 - 리드 데이터 강화
"""
import logging
import httpx
from typing import Optional, List
from datetime import datetime

from config import settings
from models.nbrs_models import LeadEnrichmentRequest, LeadEnrichmentResult

logger = logging.getLogger(__name__)


class HeliosClient:
    """Helios API client for lead data enrichment"""

    def __init__(self):
        self.api_url = settings.helios_api_url
        self.api_key = settings.helios_api_key
        self.timeout = 30.0

    async def enrich_lead(self, request: LeadEnrichmentRequest) -> LeadEnrichmentResult:
        """
        Enrich lead data using Helios model

        Args:
            request: Lead enrichment request

        Returns:
            Enriched lead data
        """
        try:
            logger.info(f"[Helios] Enriching lead: {request.company_name} (ID: {request.lead_id})")

            # Call Helios API for company intelligence
            enriched_data = await self._fetch_company_intelligence(
                company_name=request.company_name,
                company_domain=request.company_domain,
                enrich_fields=request.enrich_fields
            )

            result = LeadEnrichmentResult(
                lead_id=request.lead_id,
                company_name=request.company_name,
                **enriched_data
            )

            logger.info(
                f"[Helios] Enrichment completed for {request.company_name}: "
                f"confidence={result.confidence_score:.2f}, "
                f"sources={len(result.data_sources)}"
            )

            return result

        except Exception as e:
            logger.error(f"[Helios] Enrichment failed for {request.company_name}: {e}")
            # Return empty result on failure
            return LeadEnrichmentResult(
                lead_id=request.lead_id,
                company_name=request.company_name,
                confidence_score=0.0
            )

    async def _fetch_company_intelligence(
        self,
        company_name: str,
        company_domain: Optional[str],
        enrich_fields: List[str]
    ) -> dict:
        """
        Fetch company intelligence from Helios

        This is a placeholder implementation that calls Helios.
        In production, this would call the actual Helios API endpoints.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Helios API call for company data enrichment
                payload = {
                    "company_name": company_name,
                    "company_domain": company_domain,
                    "enrich_fields": enrich_fields,
                    "mode": "comprehensive"
                }

                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                response = await client.post(
                    f"{self.api_url}/api/enrich/company",
                    json=payload,
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_helios_response(data)
                else:
                    logger.warning(
                        f"[Helios] API returned status {response.status_code} "
                        f"for {company_name}"
                    )
                    return self._get_fallback_data(company_name)

        except httpx.TimeoutException:
            logger.warning(f"[Helios] Timeout enriching {company_name}")
            return self._get_fallback_data(company_name)
        except Exception as e:
            logger.error(f"[Helios] Error fetching data for {company_name}: {e}")
            return self._get_fallback_data(company_name)

    def _parse_helios_response(self, data: dict) -> dict:
        """Parse Helios API response into enrichment data"""
        return {
            "annual_revenue_usd": data.get("revenue", {}).get("annual_usd"),
            "employee_count": data.get("company_size", {}).get("employees"),
            "industry": data.get("industry"),
            "tech_stack": data.get("technology", {}).get("stack", []),
            "social_media_followers": data.get("social", {}).get("total_followers"),
            "website_traffic_monthly": data.get("web_analytics", {}).get("monthly_visits"),
            "funding_total_usd": data.get("funding", {}).get("total_raised_usd"),
            "data_sources": data.get("sources", []),
            "confidence_score": data.get("confidence_score", 0.0)
        }

    def _get_fallback_data(self, company_name: str) -> dict:
        """Return fallback data when Helios is unavailable"""
        logger.info(f"[Helios] Using fallback data for {company_name}")
        return {
            "annual_revenue_usd": None,
            "employee_count": None,
            "industry": None,
            "tech_stack": [],
            "social_media_followers": None,
            "website_traffic_monthly": None,
            "funding_total_usd": None,
            "data_sources": ["fallback"],
            "confidence_score": 0.0
        }

    async def batch_enrich(
        self,
        requests: List[LeadEnrichmentRequest],
        max_concurrent: int = 5
    ) -> List[LeadEnrichmentResult]:
        """
        Enrich multiple leads in batch

        Args:
            requests: List of enrichment requests
            max_concurrent: Max concurrent API calls

        Returns:
            List of enrichment results
        """
        import asyncio

        logger.info(f"[Helios] Batch enriching {len(requests)} leads")

        # Process in batches to avoid overwhelming the API
        results = []
        for i in range(0, len(requests), max_concurrent):
            batch = requests[i:i + max_concurrent]
            batch_results = await asyncio.gather(
                *[self.enrich_lead(req) for req in batch],
                return_exceptions=True
            )

            # Filter out exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"[Helios] Batch enrichment error: {result}")
                else:
                    results.append(result)

        logger.info(f"[Helios] Batch enrichment completed: {len(results)} successful")

        return results


# Singleton instance
helios_client = HeliosClient()
