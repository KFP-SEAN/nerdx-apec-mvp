"""
NBRS (NERD Brand Resonance Score) Data Models - SIMPLIFIED & FIXED
브랜드 공명 스코어 데이터 모델 - 단순화 및 수정됨

Scoring Philosophy:
- Each pillar calculates a score from 0-100
- All input scores are already 0-100, so we just average them
- Final NBRS = weighted average of three pillars
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadTier(str, Enum):
    """Lead tier classification based on NBRS"""
    TIER1 = "tier1"  # 80-100: Top priority
    TIER2 = "tier2"  # 60-79: High priority
    TIER3 = "tier3"  # 40-59: Medium priority
    TIER4 = "tier4"  # 0-39: Low priority


class BrandAffinityScore(BaseModel):
    """
    Brand Affinity - 브랜드 친화도 (40% weight in final NBRS)
    All inputs are 0-100 scores, output is 0-100
    """
    # All scores 0-100
    past_interaction_score: float = Field(0.0, ge=0, le=100, description="과거 상호작용 점수")
    email_engagement_score: float = Field(0.0, ge=0, le=100, description="이메일 인게이지먼트 점수")
    meeting_history_score: float = Field(0.0, ge=0, le=100, description="미팅 이력 점수")
    relationship_duration_score: float = Field(0.0, ge=0, le=100, description="관계 지속 기간 점수")
    contact_frequency_score: float = Field(0.0, ge=0, le=100, description="접촉 빈도 점수")
    decision_maker_access_score: float = Field(0.0, ge=0, le=100, description="의사결정권자 접근 점수")
    nps_score: float = Field(0.0, ge=0, le=100, description="Net Promoter Score (normalized 0-100)")
    testimonial_provided: bool = Field(False, description="추천사 제공 여부")
    reference_willing: bool = Field(False, description="레퍼런스 제공 의향")

    def calculate_total(self) -> float:
        """
        Calculate Brand Affinity score (0-100)
        Simple average of all scores, with bonus for testimonial/reference
        """
        # Average all numeric scores
        scores = [
            self.past_interaction_score,
            self.email_engagement_score,
            self.meeting_history_score,
            self.relationship_duration_score,
            self.contact_frequency_score,
            self.decision_maker_access_score,
            self.nps_score
        ]

        base_score = sum(scores) / len(scores)

        # Add bonus for testimonial and reference (up to +10 points)
        bonus = 0
        if self.testimonial_provided:
            bonus += 5
        if self.reference_willing:
            bonus += 5

        return min(base_score + bonus, 100.0)


class MarketPositioningScore(BaseModel):
    """
    Market Positioning - 시장 포지셔닝 (35% weight in final NBRS)
    Converts KRW amounts to 0-100 scores
    """
    # Financial metrics in KRW
    annual_revenue_krw: Optional[int] = Field(None, ge=0, description="연 매출 (KRW)")
    employee_count: Optional[int] = Field(None, ge=0, description="직원 수")
    marketing_budget_krw: Optional[int] = Field(None, ge=0, description="마케팅 예산 (KRW)")

    # Strategic fit (0-100 scores)
    target_industry_match: bool = Field(False, description="타겟 산업 일치 여부")
    target_geography_match: bool = Field(False, description="타겟 지역 일치 여부")
    pain_point_alignment_score: float = Field(0.0, ge=0, le=100, description="Pain Point 일치도")

    # Growth indicators
    revenue_growth_yoy: float = Field(0.0, description="YoY 매출 성장률 (%)")
    expansion_plans_score: float = Field(0.0, ge=0, le=100, description="확장 계획 점수")

    def calculate_total(self) -> float:
        """
        Calculate Market Positioning score (0-100)

        Scoring benchmarks (Korean market):
        - Revenue: 100B KRW = 50점, 1000B KRW = 100점
        - Employees: 100명 = 50점, 1000명 = 100점
        - Marketing Budget: 1B KRW = 50점, 10B KRW = 100점
        - Growth: 20% YoY = 50점, 100% YoY = 100점
        """
        scores = []

        # Revenue score (0-100)
        if self.annual_revenue_krw:
            # 100B = 50, 1000B = 100
            revenue_score = min((self.annual_revenue_krw / 100_000_000_000) * 50, 100)
            scores.append(revenue_score)

        # Employee count score (0-100)
        if self.employee_count:
            # 100 employees = 50, 1000 = 100
            employee_score = min((self.employee_count / 100) * 50, 100)
            scores.append(employee_score)

        # Marketing budget score (0-100)
        if self.marketing_budget_krw:
            # 1B = 50, 10B = 100
            budget_score = min((self.marketing_budget_krw / 1_000_000_000) * 50, 100)
            scores.append(budget_score)

        # Strategic alignment scores
        industry_score = 100 if self.target_industry_match else 0
        geography_score = 100 if self.target_geography_match else 0
        scores.extend([industry_score, geography_score, self.pain_point_alignment_score])

        # Growth scores
        # 20% growth = 50, 100% growth = 100
        growth_score = min((self.revenue_growth_yoy / 20) * 50, 100)
        scores.extend([growth_score, self.expansion_plans_score])

        # Average all scores
        return sum(scores) / len(scores) if scores else 0.0


class DigitalPresenceScore(BaseModel):
    """
    Digital Presence - 디지털 존재감 (25% weight in final NBRS)
    Measures online engagement and digital maturity
    """
    # Traffic metrics
    website_traffic_monthly: Optional[int] = Field(None, ge=0, description="월간 웹사이트 트래픽")
    social_media_followers: Optional[int] = Field(None, ge=0, description="소셜 미디어 팔로워")
    content_engagement_score: float = Field(0.0, ge=0, le=100, description="콘텐츠 인게이지먼트 점수")

    # Digital capabilities (boolean → converted to scores)
    modern_website: bool = Field(False, description="현대적 웹사이트 보유")
    marketing_automation: bool = Field(False, description="마케팅 자동화 도구 사용")
    mobile_app: bool = Field(False, description="모바일 앱 보유")
    ecommerce_enabled: bool = Field(False, description="이커머스 기능 보유")

    def calculate_total(self) -> float:
        """
        Calculate Digital Presence score (0-100)

        Benchmarks:
        - Website traffic: 10K/month = 50점, 100K/month = 100점
        - Social followers: 5K = 50점, 50K = 100점
        """
        scores = []

        # Website traffic score (0-100)
        if self.website_traffic_monthly:
            # 10K = 50, 100K = 100
            traffic_score = min((self.website_traffic_monthly / 10_000) * 50, 100)
            scores.append(traffic_score)

        # Social media followers score (0-100)
        if self.social_media_followers:
            # 5K = 50, 50K = 100
            followers_score = min((self.social_media_followers / 5_000) * 50, 100)
            scores.append(followers_score)

        # Content engagement (already 0-100)
        scores.append(self.content_engagement_score)

        # Digital maturity: each capability = 25 points
        maturity_score = sum([
            25 if self.modern_website else 0,
            25 if self.marketing_automation else 0,
            25 if self.mobile_app else 0,
            25 if self.ecommerce_enabled else 0
        ])
        scores.append(maturity_score)

        # Average all scores
        return sum(scores) / len(scores) if scores else 0.0


class NBRSCalculation(BaseModel):
    """
    Complete NBRS calculation combining all three pillars
    """
    lead_id: str = Field(..., description="Salesforce Lead ID")
    company_name: str = Field(..., description="회사명")

    # Three Pillars (each outputs 0-100)
    brand_affinity: BrandAffinityScore
    market_positioning: MarketPositioningScore
    digital_presence: DigitalPresenceScore

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_by: str = Field("system", description="계산 주체")

    def calculate_nbrs(self) -> float:
        """
        Calculate final NBRS score (0-100)

        Weighted average:
        - Brand Affinity: 40%
        - Market Positioning: 35%
        - Digital Presence: 25%

        Each pillar returns 0-100, so final NBRS is also 0-100
        """
        ba_score = self.brand_affinity.calculate_total()
        mp_score = self.market_positioning.calculate_total()
        dp_score = self.digital_presence.calculate_total()

        # Weighted average
        nbrs = (ba_score * 0.40) + (mp_score * 0.35) + (dp_score * 0.25)

        return round(nbrs, 2)

    def get_tier(self) -> LeadTier:
        """Determine lead tier based on NBRS score"""
        nbrs = self.calculate_nbrs()

        if nbrs >= 80:
            return LeadTier.TIER1
        elif nbrs >= 60:
            return LeadTier.TIER2
        elif nbrs >= 40:
            return LeadTier.TIER3
        else:
            return LeadTier.TIER4


class NBRSResult(BaseModel):
    """Final NBRS result with tier classification"""
    lead_id: str
    company_name: str
    nbrs_score: float = Field(..., ge=0, le=100)
    tier: LeadTier

    # Component scores
    brand_affinity_score: float
    market_positioning_score: float
    digital_presence_score: float

    # Metadata
    calculated_at: datetime
    next_action: Optional[str] = None
    priority_rank: Optional[int] = None


class LeadEnrichmentRequest(BaseModel):
    """Request for lead data enrichment via Helios"""
    lead_id: str
    company_name: str
    company_domain: Optional[str] = None
    enrich_fields: List[str] = Field(
        default=[
            "company_size",
            "revenue",
            "industry",
            "tech_stack",
            "social_presence",
            "funding_info"
        ]
    )


class LeadEnrichmentResult(BaseModel):
    """Enriched lead data from Helios"""
    lead_id: str
    company_name: str

    # Enriched data - KRW 기준
    annual_revenue_krw: Optional[int] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    tech_stack: List[str] = []
    social_media_followers: Optional[int] = None
    website_traffic_monthly: Optional[int] = None
    funding_total_krw: Optional[int] = None

    # Metadata
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []
    confidence_score: float = Field(0.0, ge=0, le=1.0)
