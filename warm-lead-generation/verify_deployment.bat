@echo off
echo ========================================================================
echo Verifying NBRS Fix Deployment
echo ========================================================================
echo.
echo Testing production API with premium lead data...
echo.

curl -X POST "https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/calculate" ^
  -H "Content-Type: application/json" ^
  -d "{\"lead_id\":\"deployment-verification\",\"company_name\":\"Premium Verification Corp\",\"brand_affinity\":{\"past_interaction_score\":95,\"email_engagement_score\":98,\"meeting_history_score\":92,\"relationship_duration_score\":95,\"contact_frequency_score\":94,\"decision_maker_access_score\":98,\"nps_score\":95,\"testimonial_provided\":true,\"reference_willing\":true},\"market_positioning\":{\"annual_revenue_krw\":500000000000,\"employee_count\":1000,\"marketing_budget_krw\":5000000000,\"target_industry_match\":true,\"target_geography_match\":true,\"pain_point_alignment_score\":95,\"revenue_growth_yoy\":50,\"expansion_plans_score\":95},\"digital_presence\":{\"website_traffic_monthly\":500000,\"social_media_followers\":100000,\"content_engagement_score\":95,\"modern_website\":true,\"marketing_automation\":true,\"mobile_app\":true,\"ecommerce_enabled\":true},\"update_salesforce\":false}"

echo.
echo.
echo ========================================================================
echo Expected Results:
echo   - nbrs_score: ~99 (NOT 15.17)
echo   - tier: tier1 (NOT tier4)
echo   - brand_affinity_score: ~100
echo   - market_positioning_score: ~99
echo   - digital_presence_score: ~99
echo ========================================================================
