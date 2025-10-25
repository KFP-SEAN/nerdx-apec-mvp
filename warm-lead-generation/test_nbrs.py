"""
Quick NBRS calculation test
"""
from models.nbrs_models import BrandAffinityScore, MarketPositioningScore, DigitalPresenceScore, NBRSCalculation

# Test data: High-value lead
brand_affinity = BrandAffinityScore(
    salesforce_activity_score=80,
    email_engagement_score=85,
    meeting_history_score=75,
    relationship_duration_months=18,
    contact_frequency_score=80,
    decision_maker_access=True,
    nps_score=70,
    testimonial_provided=True,
    reference_willing=True
)

market_positioning = MarketPositioningScore(
    annual_revenue_usd=50_000_000,  # $50M revenue
    employee_count=250,
    marketing_budget_usd=2_000_000,  # $2M marketing budget
    target_industry_match=True,
    target_geography_match=True,
    pain_point_alignment=85,
    revenue_growth_yoy_percent=25,
    expansion_plans=True
)

digital_presence = DigitalPresenceScore(
    website_traffic_monthly=100_000,
    social_media_followers=15_000,
    content_engagement_score=75,
    has_modern_website=True,
    uses_marketing_automation=True,
    has_mobile_app=False,
    ecommerce_enabled=True
)

# Calculate scores
print("=" * 60)
print("NBRS Score Components Test")
print("=" * 60)

ba_total = brand_affinity.calculate_total()
mp_total = market_positioning.calculate_total()
dp_total = digital_presence.calculate_total()

print(f"\nBrand Affinity Score: {ba_total:.2f} / 100")
print(f"Market Positioning Score: {mp_total:.2f} / 100")
print(f"Digital Presence Score: {dp_total:.2f} / 100")

# Calculate final NBRS
calculation = NBRSCalculation(
    lead_id="test-001",
    company_name="High Value Corp",
    brand_affinity=brand_affinity,
    market_positioning=market_positioning,
    digital_presence=digital_presence
)

nbrs_score = calculation.calculate_nbrs()
tier = calculation.get_tier()

print(f"\nFinal NBRS Score: {nbrs_score:.2f} / 100")
print(f"Tier: {tier.value.upper()}")
print("=" * 60)
