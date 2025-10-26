#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Deployment Script - Set Remaining Variables
Sets only the variables that haven't been set yet
"""

import json
import requests
import sys
import io
import time
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Railway API Configuration
RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

def load_railway_config():
    """Load Railway token and project info from config file"""
    config_path = Path.home() / ".railway" / "config.json"

    if not config_path.exists():
        print("Railway config not found. Please run 'railway login' first.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    token = config['user']['token']
    project_id = config['projects'].get(
        str(Path.cwd().parent / "independent-accounting-system"), {}
    ).get('project')

    if not project_id:
        projects = list(config['projects'].values())
        if projects:
            project_id = projects[0]['project']

    return token, project_id

def graphql_request(token, query, variables=None):
    """Make a GraphQL request to Railway API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "variables": variables or {}
    }

    response = requests.post(RAILWAY_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"API request failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()

    if 'errors' in result:
        raise Exception(json.dumps(result['errors'], indent=2))

    return result['data']

def set_environment_variable(token, project_id, service_id, environment_id, var_name, var_value):
    """Set a single environment variable for a service"""
    query = """
    mutation variableUpsert($input: VariableUpsertInput!) {
        variableUpsert(input: $input)
    }
    """

    variables = {
        "input": {
            "projectId": project_id,
            "serviceId": service_id,
            "environmentId": environment_id,
            "name": var_name,
            "value": var_value
        }
    }

    data = graphql_request(token, query, variables)
    return data

def main():
    print("=" * 70)
    print("Railway - Set Remaining Variables")
    print("=" * 70)

    # Load configuration
    print("\n[1/3] Loading configuration...")
    token, project_id = load_railway_config()
    print(f"Loaded token and project ID: {project_id}")

    # Service and environment IDs (from previous run)
    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"

    print(f"Service ID: {service_id}")
    print(f"Environment ID: {environment_id}")

    # Remaining variables to set (the ones that failed due to rate limit)
    remaining_vars = {
        "NBRS_WEIGHT_BRAND_AFFINITY": "0.40",
        "NBRS_WEIGHT_MARKET_POSITIONING": "0.35",
        "NBRS_WEIGHT_DIGITAL_PRESENCE": "0.25",
        "NBRS_THRESHOLD_TIER1": "80.0",
        "NBRS_THRESHOLD_TIER2": "60.0",
        "NBRS_THRESHOLD_TIER3": "40.0",
        "TARGET_MONTHLY_REVENUE_KRW": "500000000"
    }

    print(f"\n[2/3] Setting {len(remaining_vars)} remaining variables...")
    print("(Waiting 2 seconds between each variable to avoid rate limits)")

    results = []
    for i, (var_name, var_value) in enumerate(remaining_vars.items()):
        try:
            set_environment_variable(token, project_id, service_id, environment_id, var_name, var_value)
            results.append((var_name, True))
            print(f"  [OK] {var_name}")
            # Wait to avoid rate limiting
            if i < len(remaining_vars) - 1:
                time.sleep(2.0)
        except Exception as e:
            results.append((var_name, False))
            print(f"  [FAIL] {var_name}")
            # If we hit rate limit again, wait longer
            if "rate limit" in str(e).lower():
                print("    Rate limit hit. Waiting 10 seconds...")
                time.sleep(10.0)

    success_count = sum(1 for _, success in results if success)
    print(f"\n[3/3] Summary: {success_count}/{len(remaining_vars)} variables set successfully")

    print("\n" + "=" * 70)
    print("IMPORTANT: Update placeholder values in Railway Dashboard:")
    print("=" * 70)
    print("1. SALESFORCE_INSTANCE_URL (currently placeholder)")
    print("2. SALESFORCE_USERNAME (currently placeholder)")
    print("3. SALESFORCE_PASSWORD (currently placeholder)")
    print("4. SALESFORCE_SECURITY_TOKEN (currently placeholder)")
    print("5. SALESFORCE_CONSUMER_KEY (currently placeholder)")
    print("6. SALESFORCE_CONSUMER_SECRET (currently placeholder)")
    print("7. HELIOS_API_URL (currently placeholder)")
    print("8. HELIOS_API_KEY (currently placeholder)")
    print(f"\nGo to: https://railway.app/project/{project_id}/{environment_id}")
    print("=" * 70)

    print("\nDeployment configured successfully!")
    print("Railway will auto-deploy once you update the variables.")

if __name__ == "__main__":
    main()
