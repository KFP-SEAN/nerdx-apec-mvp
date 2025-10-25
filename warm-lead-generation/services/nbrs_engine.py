"""
NBRS Engine - Core Lead Scoring Service
NBRS 엔진 - 리드 스코어링 핵심 서비스
"""
import logging
from typing import List, Optional
from datetime import datetime

from models.nbrs_models import (
    NBRSCalculation,
    NBRSResult,
    BrandAffinityScore,
    MarketPositioningScore,
    DigitalPresenceScore,
    LeadTier
)

logger = logging.getLogger(__name__)


class NBRSEngine:
    """NBRS Calculation Engine"""

    def __init__(self):
        self.calculation_history = []

    def calculate_nbrs(
        self,
        lead_id: str,
        company_name: str,
        brand_affinity: BrandAffinityScore,
        market_positioning: MarketPositioningScore,
        digital_presence: DigitalPresenceScore
    ) -> NBRSResult:
        """
        Calculate NBRS score for a lead

        Args:
            lead_id: Salesforce Lead ID
            company_name: Company name
            brand_affinity: Brand affinity score data
            market_positioning: Market positioning score data
            digital_presence: Digital presence score data

        Returns:
            NBRSResult with final score and tier
        """
        # Create calculation object
        calculation = NBRSCalculation(
            lead_id=lead_id,
            company_name=company_name,
            brand_affinity=brand_affinity,
            market_positioning=market_positioning,
            digital_presence=digital_presence
        )

        # Calculate individual pillar scores
        ba_score = brand_affinity.calculate_total()
        mp_score = market_positioning.calculate_total()
        dp_score = digital_presence.calculate_total()

        # Calculate final NBRS
        nbrs_score = calculation.calculate_nbrs()
        tier = calculation.get_tier()

        # Create result
        result = NBRSResult(
            lead_id=lead_id,
            company_name=company_name,
            nbrs_score=nbrs_score,
            tier=tier,
            brand_affinity_score=round(ba_score, 2),
            market_positioning_score=round(mp_score, 2),
            digital_presence_score=round(dp_score, 2),
            calculated_at=datetime.utcnow(),
            next_action=self._determine_next_action(tier, nbrs_score)
        )

        # Store in history
        self.calculation_history.append(result)

        logger.info(
            f"[NBRS] Calculated score for {company_name} (ID: {lead_id}): "
            f"NBRS={nbrs_score}, Tier={tier.value}, "
            f"BA={ba_score:.1f}, MP={mp_score:.1f}, DP={dp_score:.1f}"
        )

        return result

    def _determine_next_action(self, tier: LeadTier, nbrs_score: float) -> str:
        """Determine recommended next action based on tier"""
        if tier == LeadTier.TIER1:
            return "즉시 세일즈팀 배정 및 맞춤 제안서 작성 (Assign to sales team immediately)"
        elif tier == LeadTier.TIER2:
            return "영업 전략 회의 후 접근 (Strategy meeting before approach)"
        elif tier == LeadTier.TIER3:
            return "너처링 캠페인 배정 (Assign to nurturing campaign)"
        else:
            return "저우선순위 리드 풀 배정 (Add to low-priority lead pool)"

    def rank_leads(self, results: List[NBRSResult]) -> List[NBRSResult]:
        """
        Rank leads by NBRS score (highest first)

        Args:
            results: List of NBRS results

        Returns:
            Sorted list with priority_rank assigned
        """
        # Sort by NBRS score (descending)
        sorted_results = sorted(results, key=lambda x: x.nbrs_score, reverse=True)

        # Assign ranks
        for i, result in enumerate(sorted_results):
            result.priority_rank = i + 1

        logger.info(f"[NBRS] Ranked {len(sorted_results)} leads")

        return sorted_results

    def filter_by_tier(self, results: List[NBRSResult], tier: LeadTier) -> List[NBRSResult]:
        """Filter leads by tier"""
        filtered = [r for r in results if r.tier == tier]
        logger.info(f"[NBRS] Filtered {len(filtered)} leads for tier {tier.value}")
        return filtered

    def get_top_n_leads(self, results: List[NBRSResult], n: int = 10) -> List[NBRSResult]:
        """
        Get top N leads by NBRS score

        Args:
            results: List of NBRS results
            n: Number of top leads to return (default 10 for PRD requirement)

        Returns:
            Top N leads sorted by NBRS
        """
        ranked = self.rank_leads(results)
        top_n = ranked[:n]

        logger.info(
            f"[NBRS] Top {n} leads: "
            f"{', '.join([f'{r.company_name} ({r.nbrs_score})' for r in top_n])}"
        )

        return top_n

    def calculate_pipeline_value(
        self,
        results: List[NBRSResult],
        avg_deal_size_krw: int = 50_000_000  # 5천만원 평균 딜 사이즈
    ) -> dict:
        """
        Calculate total pipeline value based on NBRS scores

        Args:
            results: List of NBRS results
            avg_deal_size_krw: Average deal size in KRW

        Returns:
            Pipeline value breakdown by tier
        """
        tier_counts = {
            LeadTier.TIER1: 0,
            LeadTier.TIER2: 0,
            LeadTier.TIER3: 0,
            LeadTier.TIER4: 0
        }

        for result in results:
            tier_counts[result.tier] += 1

        # Conversion probability by tier
        conversion_rates = {
            LeadTier.TIER1: 0.50,  # 50% conversion for top tier
            LeadTier.TIER2: 0.30,  # 30% conversion
            LeadTier.TIER3: 0.15,  # 15% conversion
            LeadTier.TIER4: 0.05   # 5% conversion
        }

        pipeline_value = {
            "total_leads": len(results),
            "by_tier": {},
            "total_pipeline_value_krw": 0,
            "expected_revenue_krw": 0
        }

        total_pipeline = 0
        total_expected = 0

        for tier, count in tier_counts.items():
            tier_pipeline = count * avg_deal_size_krw
            tier_expected = tier_pipeline * conversion_rates[tier]

            pipeline_value["by_tier"][tier.value] = {
                "count": count,
                "pipeline_value_krw": tier_pipeline,
                "expected_revenue_krw": tier_expected,
                "conversion_rate": conversion_rates[tier]
            }

            total_pipeline += tier_pipeline
            total_expected += tier_expected

        pipeline_value["total_pipeline_value_krw"] = total_pipeline
        pipeline_value["expected_revenue_krw"] = total_expected

        logger.info(
            f"[NBRS] Pipeline Value: Total={total_pipeline:,} KRW, "
            f"Expected={total_expected:,} KRW, Leads={len(results)}"
        )

        return pipeline_value


# Singleton instance
nbrs_engine = NBRSEngine()
