#!/bin/bash
# Railway 배포 테스트 스크립트

RAILWAY_URL="$1"

if [ -z "$RAILWAY_URL" ]; then
    echo "Usage: ./test_deployment.sh <railway-url>"
    echo "Example: ./test_deployment.sh https://warm-lead-generation-production.up.railway.app"
    exit 1
fi

echo "========================================="
echo "Testing NERD12 Warm Lead Generation API"
echo "URL: $RAILWAY_URL"
echo "========================================="

# Test 1: Health Check
echo -e "\n[1] Health Check..."
curl -s "$RAILWAY_URL/health" | python -m json.tool

# Test 2: API Documentation
echo -e "\n[2] API Documentation available at:"
echo "$RAILWAY_URL/docs"

# Test 3: Statistics
echo -e "\n[3] Statistics Endpoint..."
curl -s "$RAILWAY_URL/api/v1/lead-scoring/stats" | python -m json.tool

# Test 4: NBRS Calculation (샘플 데이터)
echo -e "\n[4] NBRS Calculation Test..."
curl -s -X POST "$RAILWAY_URL/api/v1/lead-scoring/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test-railway-001",
    "company_name": "Railway Test Corp",
    "brand_affinity": {
      "past_interaction_score": 75,
      "email_engagement_score": 80,
      "meeting_history_score": 70,
      "relationship_duration_score": 85,
      "contact_frequency_score": 75,
      "decision_maker_access_score": 90,
      "nps_score": 80,
      "testimonial_provided": true,
      "reference_willing": true
    },
    "market_positioning": {
      "annual_revenue_krw": 50000000000,
      "employee_count": 250,
      "marketing_budget_krw": 500000000,
      "target_industry_match": true,
      "target_geography_match": true,
      "pain_point_alignment_score": 85,
      "revenue_growth_yoy": 25,
      "expansion_plans_score": 80
    },
    "digital_presence": {
      "website_traffic_monthly": 50000,
      "social_media_followers": 10000,
      "content_engagement_score": 75,
      "modern_website": true,
      "marketing_automation": true,
      "mobile_app": false,
      "ecommerce_enabled": true
    },
    "update_salesforce": false
  }' | python -m json.tool

echo -e "\n========================================="
echo "Deployment test completed!"
echo "========================================="
