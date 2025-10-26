#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check and fix field-level security for NBRS fields
"""
import subprocess
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("="*60)
print("Checking NBRS Field Permissions")
print("="*60)
print()

# Get Salesforce org info
result = subprocess.run(
    ["sf", "org", "display", "--target-org", "nerdx-org", "--json"],
    capture_output=True,
    text=True
)

org_info = json.loads(result.stdout)
print(f"Connected to: {org_info['result']['username']}")
print(f"Instance: {org_info['result']['instanceUrl']}")
print()

# Try to query the Lead object with NBRS fields
print("Testing SOQL query with NBRS fields...")
query = "SELECT Id, Company FROM Lead LIMIT 1"

result = subprocess.run(
    ["sf", "data", "query", "--query", query, "--target-org", "nerdx-org", "--json"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Basic Lead query works")
else:
    print("✗ Basic Lead query failed")
    print(result.stderr)

# Try with NBRS field
print("\nTesting with NBRS_Score__c field...")
query_nbrs = "SELECT Id, Company, NBRS_Score__c FROM Lead LIMIT 1"

result = subprocess.run(
    ["sf", "data", "query", "--query", query_nbrs, "--target-org", "nerdx-org", "--json"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ NBRS field query works!")
    data = json.loads(result.stdout)
    print(f"  Retrieved {data['result']['totalSize']} records")
else:
    error_output = result.stderr
    print("✗ NBRS field query failed")
    if "No such column" in error_output:
        print("\nDIAGNOSIS: Field exists in metadata but not accessible via API")
        print("\nPossible causes:")
        print("1. Field-Level Security (FLS) not set for current profile")
        print("2. Metadata cache not refreshed")
        print("3. Field deployment incomplete")
        print("\nSolution: Need to update Field-Level Security permissions")

print("\n" + "="*60)
