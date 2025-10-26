"""
NBRS (NERD Brand Resonance Score) Data Models
브랜드 공명 스코어 데이터 모델
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
    Brand Affinity - 브랜드 친화도 (40%)
    Measures past interactions and relationship strength
    """
    # Past Interaction Score (15%)
    salesforce_activity_score: float = Field(0.0, ge=0, le=100, description="Salesforce 활동 이력 점수")
    email_engagement_score: float = Field(0.0, ge=0, le=100, description="이메일 인게이지먼트 점수")
    meeting_history_score: float = Field(0.0, ge=0, le=100, description="미팅 이력 점수")

    # Relationship Depth (15%)
    relationship_duration_months: int = Field(0, ge=0, description="관계 지속 기간 (개월)")
    contact_frequency_score: float = Field(0.0, ge=0, le=100, description="접촉 빈도 점수")
    decision_maker_access: bool = Field(False, description="의사결정권자 접근 가능 여부")

    # Brand Perception (10%)
    nps_score: Optional[int] = Field(None, ge=-100, le=100, description="Net Promoter Score")
    testimonial_provided: bool = Field(False, description="추천사 제공 여부")
    reference_willing: bool = Field(False, description="레퍼런스 제공 의향")

    def calculate_total(self) -> float:
        """Calculate total brand affinity score (0-100)"""
        # Past Interaction (15%)
        past_interaction = (
            self.salesforce_activity_score * 0.05 +
            self.email_engagement_score * 0.05 +
            self.meeting_history_score * 0.05
        )

        # Relationship Depth (15%)
        duration_score = min(self.relationship_duration_months / 12 * 100, 100)
        decision_maker_bonus = 20 if self.decision_maker_access else 0
        relationship_depth = (
            duration_score * 0.05 +
            self.contact_frequency_score * 0.05 +
            decision_maker_bonus * 0.05
        )

        # Brand Perception (10%)
        nps_normalized = ((self.nps_score or 0) + 100) / 2  # Convert -100~100 to 0~100
        testimonial_bonus = 30 if self.testimonial_provided else 0
        reference_bonus = 30 if self.reference_willing else 0
        brand_perception = (
            nps_normalized * 0.05 +
            testimonial_bonus * 0.025 +
            reference_bonus * 0.025
        )

        return past_interaction + relationship_depth + brand_perception


class MarketPositioningScore(BaseModel):
    """
    Market Positioning - 시장 포지셔닝 (35%)
    Measures company size, budget, and strategic alignment
    """
    # Company Size & Budget (20%)
    annual_revenue_usd: Optional[int] = Field(None, ge=0, description="연 매출 (USD)")
    employee_count: Optional[int] = Field(None, ge=0, description="직원 수")
    marketing_budget_usd: Optional[int] = Field(None, ge=0, description="마케팅 예산 (USD)")

    # Strategic Alignment (10%)
    target_industry_match: bool = Field(False, description="타겟 산업 일치 여부")
    target_geography_match: bool = Field(False, description="타겟 지역 일치 여부")
    pain_point_alignment: float = Field(0.0, ge=0, le=100, description="Pain Point 일치도")

    # Growth Potential (5%)
    revenue_growth_yoy_percent: Optional[float] = Field(None, description="YoY 매출 성장률 (%)")
    expansion_plans: bool = Field(False, description="확장 계획 유무")

    def calculate_total(self) -> float:
        """Calculate total market positioning score (0-100)"""
        # Company Size & Budget (20%)
        revenue_score = min((self.annual_revenue_usd or 0) / 10_000_000 * 100, 100)
        employee_score = min((self.employee_count or 0) / 1000 * 100, 100)
        budget_score = min((self.marketing_budget_usd or 0) / 1_000_000 * 100, 100)
        company_size_budget = (
            revenue_score * 0.10 +
            employee_score * 0.05 +
            budget_score * 0.05
        )

        # Strategic Alignment (10%)
        industry_bonus = 40 if self.target_industry_match else 0
        geography_bonus = 30 if self.target_geography_match else 0
        strategic_alignment = (
            industry_bonus * 0.04 +
            geography_bonus * 0.03 +
            self.pain_point_alignment * 0.03
        )

        # Growth Potential (5%)
        growth_score = min((self.revenue_growth_yoy_percent or 0) / 50 * 100, 100)
        expansion_bonus = 50 if self.expansion_plans else 0
        growth_potential = (
            growth_score * 0.025 +
            expansion_bonus * 0.025
        )

        return company_size_budget + strategic_alignment + growth_potential


class DigitalPresenceScore(BaseModel):
    """
    Digital Presence - 디지털 존재감 (25%)
    Measures online engagement and digital maturity
    """
    # Online Engagement (15%)
    website_traffic_monthly: Optional[int] = Field(None, ge=0, description="월간 웹사이트 트래픽")
    social_media_followers: Optional[int] = Field(None, ge=0, description="소셜 미디어 팔로워")
    content_engagement_score: float = Field(0.0, ge=0, le=100, description="콘텐츠 인게이지먼트 점수")

    # Digital Maturity (10%)
    has_modern_website: bool = Field(False, description="현대적 웹사이트 보유")
    uses_marketing_automation: bool = Field(False, description="마케팅 자동화 도구 사용")
    has_mobile_app: bool = Field(False, description="모바일 앱 보유")
    ecommerce_enabled: bool = Field(False, description="이커머스 기능 보유")

    def calculate_total(self) -> float:
        """Calculate total digital presence score (0-100)"""
        # Online Engagement (15%)
        traffic_score = min((self.website_traffic_monthly or 0) / 100_000 * 100, 100)
        followers_score = min((self.social_media_followers or 0) / 50_000 * 100, 100)
        online_engagement = (
            traffic_score * 0.05 +
            followers_score * 0.05 +
            self.content_engagement_score * 0.05
        )

        # Digital Maturity (10%)
        maturity_score = sum([
            25 if self.has_modern_website else 0,
            25 if self.uses_marketing_automation else 0,
            25 if self.has_mobile_app else 0,
            25 if self.ecommerce_enabled else 0
        ])
        digital_maturity = maturity_score * 0.10

        return online_engagement + digital_maturity


class NBRSCalculation(BaseModel):
    """
    Complete NBRS calculation combining all three pillars
    """
    lead_id: str = Field(..., description="Salesforce Lead ID")
    company_name: str = Field(..., description="회사명")

    # Three Pillars
    brand_affinity: BrandAffinityScore
    market_positioning: MarketPositioningScore
    digital_presence: DigitalPresenceScore

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_by: str = Field("system", description="계산 주체")

    def calculate_nbrs(self) -> float:
        """
        Calculate final NBRS score (0-100)
        가중치: Brand Affinity (40%) + Market Positioning (35%) + Digital Presence (25%)
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

    # Enriched data
    annual_revenue_usd: Optional[int] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    tech_stack: List[str] = []
    social_media_followers: Optional[int] = None
    website_traffic_monthly: Optional[int] = None
    funding_total_usd: Optional[int] = None

    # Metadata
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []
    confidence_score: float = Field(0.0, ge=0, le=1.0)
