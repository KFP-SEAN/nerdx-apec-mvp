#!/usr/bin/env python3
"""Test the fixed NBRS model with correct field names"""

from models.nbrs_models import (
    BrandAffinityScore,
    MarketPositioningScore,
    DigitalPresenceScore,
    NBRSCalculation
)

def test_tier1_lead():
    """Test high-value lead - should get TIER1"""
    print("\n" + "="*70)
    print("Test 1: Premium Corp (High-Value Lead)")
    print("="*70)

    brand_affinity = BrandAffinityScore(
        past_interaction_score=95,
        email_engagement_score=98,
        meeting_history_score=92,
        relationship_duration_score=95,
        contact_frequency_score=94,
        decision_maker_access_score=98,
        nps_score=95,
        testimonial_provided=True,
        reference_willing=True
    )

    market_positioning = MarketPositioningScore(
        annual_revenue_krw=500_000_000_000,  # 5000억원
        employee_count=1000,
        marketing_budget_krw=5_000_000_000,  # 50억원
        target_industry_match=True,
        target_geography_match=True,
        pain_point_alignment_score=95,
        revenue_growth_yoy=50,
        expansion_plans_score=95
    )

    digital_presence = DigitalPresenceScore(
        website_traffic_monthly=500_000,
        social_media_followers=100_000,
        content_engagement_score=95,
        modern_website=True,
        marketing_automation=True,
        mobile_app=True,
        ecommerce_enabled=True
    )

    calculation = NBRSCalculation(
        lead_id="test-tier1-001",
        company_name="Premium Corp",
        brand_affinity=brand_affinity,
        market_positioning=market_positioning,
        digital_presence=digital_presence
    )

    ba_score = brand_affinity.calculate_total()
    mp_score = market_positioning.calculate_total()
    dp_score = digital_presence.calculate_total()
    nbrs = calculation.calculate_nbrs()
    tier = calculation.get_tier()

    print(f"\nComponent Scores:")
    print(f"  Brand Affinity: {ba_score:.2f} (weight 40%)")
    print(f"  Market Positioning: {mp_score:.2f} (weight 35%)")
    print(f"  Digital Presence: {dp_score:.2f} (weight 25%)")
    print(f"\nFinal NBRS: {nbrs:.2f}")
    print(f"Tier: {tier.value.upper()}")
    print(f"Expected: TIER1 (≥80)")
    print(f"Result: {'✓ PASS' if tier.value == 'tier1' else '✗ FAIL'}")

    return tier.value == 'tier1'


def test_tier2_lead():
    """Test medium-high value lead - should get TIER2"""
    print("\n" + "="*70)
    print("Test 2: Test Production Corp (Medium-High Value)")
    print("="*70)

    brand_affinity = BrandAffinityScore(
        past_interaction_score=75,
        email_engagement_score=80,
        meeting_history_score=70,
        relationship_duration_score=85,
        contact_frequency_score=75,
        decision_maker_access_score=90,
        nps_score=80,
        testimonial_provided=True,
        reference_willing=True
    )

    market_positioning = MarketPositioningScore(
        annual_revenue_krw=100_000_000_000,  # 1000억원
        employee_count=500,
        marketing_budget_krw=1_000_000_000,  # 10억원
        target_industry_match=True,
        target_geography_match=True,
        pain_point_alignment_score=85,
        revenue_growth_yoy=30,
        expansion_plans_score=80
    )

    digital_presence = DigitalPresenceScore(
        website_traffic_monthly=100_000,
        social_media_followers=25_000,
        content_engagement_score=85,
        modern_website=True,
        marketing_automation=True,
        mobile_app=True,
        ecommerce_enabled=True
    )

    calculation = NBRSCalculation(
        lead_id="test-tier2-001",
        company_name="Test Production Corp",
        brand_affinity=brand_affinity,
        market_positioning=market_positioning,
        digital_presence=digital_presence
    )

    ba_score = brand_affinity.calculate_total()
    mp_score = market_positioning.calculate_total()
    dp_score = digital_presence.calculate_total()
    nbrs = calculation.calculate_nbrs()
    tier = calculation.get_tier()

    print(f"\nComponent Scores:")
    print(f"  Brand Affinity: {ba_score:.2f} (weight 40%)")
    print(f"  Market Positioning: {mp_score:.2f} (weight 35%)")
    print(f"  Digital Presence: {dp_score:.2f} (weight 25%)")
    print(f"\nFinal NBRS: {nbrs:.2f}")
    print(f"Tier: {tier.value.upper()}")
    print(f"Expected: TIER2 (60-79)")
    print(f"Result: {'✓ PASS' if tier.value == 'tier2' else '✗ FAIL'}")

    return tier.value == 'tier2'


def test_tier4_lead():
    """Test low-value lead - should get TIER4"""
    print("\n" + "="*70)
    print("Test 3: Startup Inc (Low-Value Lead)")
    print("="*70)

    brand_affinity = BrandAffinityScore(
        past_interaction_score=20,
        email_engagement_score=15,
        meeting_history_score=10,
        relationship_duration_score=5,
        contact_frequency_score=10,
        decision_maker_access_score=20,
        nps_score=15,
        testimonial_provided=False,
        reference_willing=False
    )

    market_positioning = MarketPositioningScore(
        annual_revenue_krw=100_000_000,  # 1억원
        employee_count=5,
        marketing_budget_krw=1_000_000,  # 100만원
        target_industry_match=False,
        target_geography_match=False,
        pain_point_alignment_score=20,
        revenue_growth_yoy=5,
        expansion_plans_score=10
    )

    digital_presence = DigitalPresenceScore(
        website_traffic_monthly=100,
        social_media_followers=50,
        content_engagement_score=15,
        modern_website=False,
        marketing_automation=False,
        mobile_app=False,
        ecommerce_enabled=False
    )

    calculation = NBRSCalculation(
        lead_id="test-tier4-001",
        company_name="Startup Inc",
        brand_affinity=brand_affinity,
        market_positioning=market_positioning,
        digital_presence=digital_presence
    )

    ba_score = brand_affinity.calculate_total()
    mp_score = market_positioning.calculate_total()
    dp_score = digital_presence.calculate_total()
    nbrs = calculation.calculate_nbrs()
    tier = calculation.get_tier()

    print(f"\nComponent Scores:")
    print(f"  Brand Affinity: {ba_score:.2f} (weight 40%)")
    print(f"  Market Positioning: {mp_score:.2f} (weight 35%)")
    print(f"  Digital Presence: {dp_score:.2f} (weight 25%)")
    print(f"\nFinal NBRS: {nbrs:.2f}")
    print(f"Tier: {tier.value.upper()}")
    print(f"Expected: TIER4 (<40)")
    print(f"Result: {'✓ PASS' if tier.value == 'tier4' else '✗ FAIL'}")

    return tier.value == 'tier4'


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NBRS Model Testing - Fixed Version (KRW-based)")
    print("="*70)

    results = []
    results.append(("TIER1 Lead", test_tier1_lead()))
    results.append(("TIER2 Lead", test_tier2_lead()))
    results.append(("TIER4 Lead", test_tier4_lead()))

    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! NBRS model is working correctly.")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review scoring logic.")
