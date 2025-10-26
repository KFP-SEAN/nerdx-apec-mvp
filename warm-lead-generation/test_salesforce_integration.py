#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Salesforce integration by creating a Lead and updating with NBRS data
"""
import requests
import json
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# TODO: Get access token from Salesforce CLI: sf org display --target-org nerdx-org --json
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # Replace with actual token from sf org display
INSTANCE_URL = "https://innovation-innovation-8209.my.salesforce.com"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("="*60)
print("Testing Salesforce NBRS Integration")
print("="*60)
print()

# Step 1: Create a test Lead
print("Step 1: Creating test Lead for NERDHOUSE BUKCHON...")
lead_data = {
    "Company": "NERDHOUSE BUKCHON",
    "LastName": "Test",
    "FirstName": "NBRS",
    "Email": "test@nerdhouse-bukchon.com",
    "Status": "Open - Not Contacted"
}

response = requests.post(
    f"{INSTANCE_URL}/services/data/v59.0/sobjects/Lead",
    headers=headers,
    json=lead_data
)

if response.status_code == 201:
    result = response.json()
    lead_id = result["id"]
    print(f"✓ Lead created successfully: {lead_id}")
else:
    print(f"✗ Failed to create Lead: {response.status_code}")
    print(response.json())
    exit(1)

print()

# Step 2: Update Lead with NBRS data
print("Step 2: Updating Lead with NBRS data...")
nbrs_data = {
    "NBRS_Score__c": 86.63,
    "NBRS_Tier__c": "TIER1",
    "Brand_Affinity_Score__c": 95.71,
    "Market_Positioning_Score__c": 69.38,
    "Digital_Presence_Score__c": 96.25,
    "Priority_Rank__c": 1,
    "Next_Action__c": "즉시 세일즈팀 배정 및 맞춤 제안서 작성"
}

response = requests.patch(
    f"{INSTANCE_URL}/services/data/v59.0/sobjects/Lead/{lead_id}",
    headers=headers,
    json=nbrs_data
)

if response.status_code == 204:
    print("✓ Lead updated successfully with NBRS data")
else:
    print(f"✗ Failed to update Lead: {response.status_code}")
    print(response.json())

print()

# Step 3: Query the Lead to verify
print("Step 3: Querying Lead to verify data...")
query = f"""
SELECT Id, Company, NBRS_Score__c, NBRS_Tier__c,
       Brand_Affinity_Score__c, Market_Positioning_Score__c,
       Digital_Presence_Score__c, Priority_Rank__c, Next_Action__c
FROM Lead
WHERE Id = '{lead_id}'
"""

response = requests.get(
    f"{INSTANCE_URL}/services/data/v59.0/query",
    headers=headers,
    params={"q": query}
)

if response.status_code == 200:
    result = response.json()
    if result["totalSize"] > 0:
        lead = result["records"][0]
        print("✓ Lead data verified:")
        print(f"  Company: {lead.get('Company')}")
        print(f"  NBRS Score: {lead.get('NBRS_Score__c')}")
        print(f"  NBRS Tier: {lead.get('NBRS_Tier__c')}")
        print(f"  Brand Affinity: {lead.get('Brand_Affinity_Score__c')}")
        print(f"  Market Positioning: {lead.get('Market_Positioning_Score__c')}")
        print(f"  Digital Presence: {lead.get('Digital_Presence_Score__c')}")
        print(f"  Priority Rank: {lead.get('Priority_Rank__c')}")
        print(f"  Next Action: {lead.get('Next_Action__c')}")
    else:
        print("✗ No Lead found")
else:
    print(f"✗ Failed to query Lead: {response.status_code}")
    print(response.json())

print()
print("="*60)
print("Integration test completed!")
print("="*60)
print(f"\nLead ID: {lead_id}")
print(f"View in Salesforce: {INSTANCE_URL}/lightning/r/Lead/{lead_id}/view")
