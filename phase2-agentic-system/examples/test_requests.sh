#!/bin/bash
# Test API with example requests

BASE_URL="http://localhost:8002"

echo "=================================="
echo "Phase 2 API - Example Requests"
echo "=================================="
echo ""

# Test 1: Basic APEC video
echo "1. Testing Basic APEC Video Generation..."
JOB1=$(curl -s -X POST "$BASE_URL/api/v1/cameo/generate" \
  -H "Content-Type: application/json" \
  -d @examples/request_basic.json | jq -r '.job_id')
echo "   Job ID: $JOB1"
echo ""

# Wait a bit
sleep 2

# Test 2: Fireside chat
echo "2. Testing Fireside Chat Video..."
JOB2=$(curl -s -X POST "$BASE_URL/api/v1/cameo/generate" \
  -H "Content-Type: application/json" \
  -d @examples/request_fireside.json | jq -r '.job_id')
echo "   Job ID: $JOB2"
echo ""

# Check status
sleep 2
echo "3. Checking Status of First Job..."
curl -s "$BASE_URL/api/v1/cameo/status/$JOB1" | jq '.'
echo ""

# Check queue
echo "4. Checking Queue Status..."
curl -s "$BASE_URL/api/v1/cameo/queue/status" | jq '.'
echo ""

# Check rate limit
echo "5. Checking Rate Limit for demo_user_001..."
curl -s "$BASE_URL/api/v1/cameo/rate-limit/demo_user_001" | jq '.'
echo ""

echo "=================================="
echo "Tests Complete!"
echo "=================================="
echo ""
echo "Job IDs created:"
echo "  - $JOB1"
echo "  - $JOB2"
echo ""
echo "Monitor status at:"
echo "  curl $BASE_URL/api/v1/cameo/status/$JOB1"
