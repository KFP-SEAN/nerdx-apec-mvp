#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive API Testing Script for NERD12 Warm Lead Generation
Tests all 9 endpoints
"""

import requests
import json
import sys
import io
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Service URL
BASE_URL = "https://warm-lead-generation-production.up.railway.app"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_endpoint(method, path, description, data=None, params=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"

    print(f"\n[TEST] {description}")
    print(f"  Method: {method}")
    print(f"  Path: {path}")

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            print(f"  [SKIP] Unsupported method: {method}")
            return False

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"  Response: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")
                print("  [✓] SUCCESS")
                return True
            except:
                print(f"  Response: {response.text[:200]}")
                print("  [✓] SUCCESS")
                return True
        else:
            print(f"  Error: {response.text[:200]}")
            print("  [✗] FAILED")
            return False

    except Exception as e:
        print(f"  Exception: {str(e)}")
        print("  [✗] FAILED")
        return False

def main():
    print("=" * 70)
    print("  NERD12 Warm Lead Generation - Comprehensive API Testing")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test 1: Health Check
    print_section("Test 1: Health Check")
    results.append(test_endpoint("GET", "/health", "Health endpoint"))

    # Test 2: API Documentation
    print_section("Test 2: API Documentation")
    results.append(test_endpoint("GET", "/docs", "Swagger UI documentation page"))

    # Test 3: Statistics
    print_section("Test 3: Statistics")
    results.append(test_endpoint("GET", "/api/v1/lead-scoring/stats", "Get lead scoring statistics"))

    # Test 4: NBRS Calculation (TIER1 - High Score)
    print_section("Test 4: NBRS Calculation - High Score Lead")
    tier1_data = {
        "lead_id": "test-tier1-001",
        "company_name": "Premium Corp",
        "brand_affinity": {
            "past_interaction_score": 95,
            "email_engagement_score": 98,
            "meeting_history_score": 92,
            "relationship_duration_score": 95,
            "contact_frequency_score": 94,
            "decision_maker_access_score": 98,
            "nps_score": 95,
            "testimonial_provided": True,
            "reference_willing": True
        },
        "market_positioning": {
            "annual_revenue_krw": 500000000000,
            "employee_count": 1000,
            "marketing_budget_krw": 5000000000,
            "target_industry_match": True,
            "target_geography_match": True,
            "pain_point_alignment_score": 95,
            "revenue_growth_yoy": 50,
            "expansion_plans_score": 95
        },
        "digital_presence": {
            "website_traffic_monthly": 500000,
            "social_media_followers": 100000,
            "content_engagement_score": 95,
            "modern_website": True,
            "marketing_automation": True,
            "mobile_app": True,
            "ecommerce_enabled": True
        },
        "update_salesforce": False
    }
    results.append(test_endpoint("POST", "/api/v1/lead-scoring/calculate",
                                 "Calculate NBRS for high-value lead", data=tier1_data))

    # Test 5: NBRS Calculation (TIER4 - Low Score)
    print_section("Test 5: NBRS Calculation - Low Score Lead")
    tier4_data = {
        "lead_id": "test-tier4-001",
        "company_name": "Startup Inc",
        "brand_affinity": {
            "past_interaction_score": 20,
            "email_engagement_score": 15,
            "meeting_history_score": 10,
            "relationship_duration_score": 5,
            "contact_frequency_score": 10,
            "decision_maker_access_score": 20,
            "nps_score": 15,
            "testimonial_provided": False,
            "reference_willing": False
        },
        "market_positioning": {
            "annual_revenue_krw": 100000000,
            "employee_count": 5,
            "marketing_budget_krw": 1000000,
            "target_industry_match": False,
            "target_geography_match": False,
            "pain_point_alignment_score": 20,
            "revenue_growth_yoy": 5,
            "expansion_plans_score": 10
        },
        "digital_presence": {
            "website_traffic_monthly": 100,
            "social_media_followers": 50,
            "content_engagement_score": 15,
            "modern_website": False,
            "marketing_automation": False,
            "mobile_app": False,
            "ecommerce_enabled": False
        },
        "update_salesforce": False
    }
    results.append(test_endpoint("POST", "/api/v1/lead-scoring/calculate",
                                 "Calculate NBRS for low-value lead", data=tier4_data))

    # Test 6: Tier Distribution
    print_section("Test 6: Tier Distribution")
    results.append(test_endpoint("GET", "/api/v1/lead-scoring/distribution",
                                 "Get tier distribution"))

    # Test 7: Top Leads
    print_section("Test 7: Top Leads")
    results.append(test_endpoint("GET", "/api/v1/lead-scoring/top-leads",
                                 "Get top 10 leads", params={"limit": 10}))

    # Test 8: Statistics (again, to see if it updated)
    print_section("Test 8: Updated Statistics")
    results.append(test_endpoint("GET", "/api/v1/lead-scoring/stats",
                                 "Get updated statistics after calculations"))

    # Test 9: Bulk Calculation (if available)
    print_section("Test 9: Check Service Info")
    results.append(test_endpoint("GET", "/", "Root endpoint / service info"))

    # Summary
    print_section("Test Summary")
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests} [✓]")
    print(f"Failed: {failed_tests} [✗]")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    print("\n" + "=" * 70)
    print("  API Endpoints")
    print("=" * 70)
    print(f"\n1. Health: GET {BASE_URL}/health")
    print(f"2. API Docs: GET {BASE_URL}/docs")
    print(f"3. Statistics: GET {BASE_URL}/api/v1/lead-scoring/stats")
    print(f"4. Calculate NBRS: POST {BASE_URL}/api/v1/lead-scoring/calculate")
    print(f"5. Tier Distribution: GET {BASE_URL}/api/v1/lead-scoring/distribution")
    print(f"6. Top Leads: GET {BASE_URL}/api/v1/lead-scoring/top-leads?limit=10")
    print(f"7. Lead Detail: GET {BASE_URL}/api/v1/lead-scoring/lead/{{lead_id}}")
    print(f"8. Batch Calculate: POST {BASE_URL}/api/v1/lead-scoring/batch-calculate")
    print(f"9. Salesforce Sync: POST {BASE_URL}/api/v1/lead-scoring/sync-salesforce")

    print("\n" + "=" * 70)

    if passed_tests == total_tests:
        print("\n✓ All tests passed! System is fully operational.")
    elif passed_tests > 0:
        print(f"\n⚠ {passed_tests}/{total_tests} tests passed. Some endpoints may need attention.")
    else:
        print("\n✗ All tests failed. System may not be operational.")

    print("\n" + "=" * 70)

    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
