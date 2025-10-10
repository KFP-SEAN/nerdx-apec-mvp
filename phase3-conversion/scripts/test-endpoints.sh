#!/bin/bash

# Phase 3: Conversion - Endpoint Testing Script
# Tests all Phase 3 endpoints with sample data

BASE_URL="${BASE_URL:-http://localhost:3003}"
USER_ID="test-user-123"
PRODUCT_ID="apec-limited-001"

echo "================================"
echo "Phase 3 Endpoint Testing"
echo "================================"
echo "Base URL: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local name=$4

    echo -e "${YELLOW}Testing: $name${NC}"
    echo "  $method $endpoint"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✓ Success ($status_code)${NC}"
    else
        echo -e "${RED}✗ Failed ($status_code)${NC}"
    fi

    echo "  Response: $(echo $body | head -c 100)..."
    echo ""
}

# Health Checks
echo "=== Health & Status ==="
echo ""
test_endpoint "GET" "/health" "" "Service Health Check"
test_endpoint "GET" "/" "" "Root Info"
test_endpoint "GET" "/api/ar/health" "" "AR Service Health"

# Orders
echo "=== Orders API ==="
echo ""

# Create checkout session
CHECKOUT_DATA="{
  \"userId\": \"$USER_ID\",
  \"productId\": \"$PRODUCT_ID\",
  \"quantity\": 1
}"
test_endpoint "POST" "/api/orders/checkout" "$CHECKOUT_DATA" "Create Checkout Session"

# Get user orders
test_endpoint "GET" "/api/orders/user/$USER_ID" "" "Get User Orders"

# AR Experiences
echo "=== AR API ==="
echo ""

# Grant preview access
PREVIEW_DATA="{
  \"userId\": \"$USER_ID\",
  \"productId\": \"$PRODUCT_ID\",
  \"duration\": 30
}"
test_endpoint "POST" "/api/ar/preview" "$PREVIEW_DATA" "Grant Preview Access"

# Get AR experience
test_endpoint "GET" "/api/ar/experience/$PRODUCT_ID?userId=$USER_ID" "" "Get AR Experience"

# Get user AR experiences
test_endpoint "GET" "/api/ar/user/$USER_ID/experiences" "" "Get User AR Experiences"

# Verify access token (with dummy token)
VERIFY_DATA="{
  \"accessToken\": \"$USER_ID:$PRODUCT_ID:1234567890:dummytoken\"
}"
test_endpoint "POST" "/api/ar/verify" "$VERIFY_DATA" "Verify Access Token"

# Get AR analytics
test_endpoint "GET" "/api/ar/analytics/$PRODUCT_ID" "" "Get AR Analytics"

# Summary
echo "================================"
echo "Testing Complete!"
echo "================================"
echo ""
echo "Note: Some tests may fail if Phase 1 API is not running"
echo "or if products don't exist in the database."
echo ""
echo "For full integration testing:"
echo "  1. Start Phase 1 API"
echo "  2. Ensure test products exist"
echo "  3. Configure Stripe test keys"
echo "  4. Run this script again"
echo ""
