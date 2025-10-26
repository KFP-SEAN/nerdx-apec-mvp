#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update existing NERDHOUSE BUKCHON lead with NBRS data
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
LEAD_ID = "00QdJ000003iy5BUAQ"  # Existing NERDHOUSE BUKCHON lead

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("="*60)
print("Updating NERDHOUSE BUKCHON Lead with NBRS Data")
print("="*60)
print()

# NBRS data for NERDHOUSE BUKCHON (from previous calculation)
nbrs_data = {
    "NBRS_Score__c": 86.63,
    "NBRS_Tier__c": "TIER1",
    "Brand_Affinity_Score__c": 95.71,
    "Market_Positioning_Score__c": 69.38,
    "Digital_Presence_Score__c": 96.25,
    "Priority_Rank__c": 1,
    "Next_Action__c": "즉시 세일즈팀 배정 및 맞춤 제안서 작성"
}

print(f"Updating Lead ID: {LEAD_ID}...")
print(f"  NBRS Score: {nbrs_data['NBRS_Score__c']}")
print(f"  Tier: {nbrs_data['NBRS_Tier__c']}")
print()

response = requests.patch(
    f"{INSTANCE_URL}/services/data/v59.0/sobjects/Lead/{LEAD_ID}",
    headers=headers,
    json=nbrs_data
)

if response.status_code == 204:
    print("✓ Lead updated successfully with NBRS data")
else:
    print(f"✗ Failed to update Lead: {response.status_code}")
    print(response.text)
    exit(1)

print()

# Query the Lead to verify
print("Querying Lead to verify NBRS data...")
query = f"""
SELECT Id, Company, NBRS_Score__c, NBRS_Tier__c,
       Brand_Affinity_Score__c, Market_Positioning_Score__c,
       Digital_Presence_Score__c, Priority_Rank__c, Next_Action__c
FROM Lead
WHERE Id = '{LEAD_ID}'
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
print("Update completed successfully!")
print("="*60)
print(f"\nView in Salesforce: {INSTANCE_URL}/lightning/r/Lead/{LEAD_ID}/view")
