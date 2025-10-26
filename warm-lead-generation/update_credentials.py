#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update warm-lead-generation service with found Salesforce credentials
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
    """Load Railway token"""
    config_path = Path.home() / ".railway" / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['user']['token']

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
        return None

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
    print("Update warm-lead-generation with Found Credentials")
    print("=" * 70)

    token = load_railway_config()

    # Service IDs
    project_id = "53c2f700-32ca-491f-b525-8552114b6fd6"
    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"  # warm-lead-generation
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"  # production

    # Load found credentials
    with open('nerdx_apec_mvp_credentials.json', 'r') as f:
        found_creds = json.load(f)

    print("\nFound credentials from nerdx-apec-mvp:")
    print(f"  - SALESFORCE_INSTANCE_URL")
    print(f"  - SALESFORCE_CLIENT_ID (will map to CONSUMER_KEY)")
    print(f"  - SALESFORCE_CLIENT_SECRET (will map to CONSUMER_SECRET)")
    print(f"  - SALESFORCE_TOKEN_URL")

    # Map credentials
    # CLIENT_ID and CONSUMER_KEY are the same thing in Salesforce
    # CLIENT_SECRET and CONSUMER_SECRET are the same thing
    credentials_to_update = {
        "SALESFORCE_INSTANCE_URL": found_creds["SALESFORCE_INSTANCE_URL"],
        "SALESFORCE_CONSUMER_KEY": found_creds["SALESFORCE_CLIENT_ID"],
        "SALESFORCE_CONSUMER_SECRET": found_creds["SALESFORCE_CLIENT_SECRET"]
    }

    # For OAuth2 flow, we don't need USERNAME, PASSWORD, SECURITY_TOKEN
    # But the service might be expecting them, so set them to empty or special values
    # indicating OAuth2 is being used
    credentials_to_update.update({
        "SALESFORCE_USERNAME": "oauth2",  # Placeholder indicating OAuth2 flow
        "SALESFORCE_PASSWORD": "oauth2",  # Placeholder indicating OAuth2 flow
        "SALESFORCE_SECURITY_TOKEN": ""   # Not needed for OAuth2
    })

    # For Helios, since we don't have it yet, keep placeholders or set to local
    credentials_to_update.update({
        "HELIOS_API_URL": "http://localhost:8002",  # Will update after Helios deployment
        "HELIOS_API_KEY": ""  # Will update after Helios deployment
    })

    print("\n" + "=" * 70)
    print("Updating Variables")
    print("=" * 70)

    for var_name, var_value in credentials_to_update.items():
        try:
            set_environment_variable(token, project_id, service_id, environment_id, var_name, var_value)
            print(f"  [OK] {var_name}")
            time.sleep(1.5)  # Avoid rate limiting
        except Exception as e:
            print(f"  [FAIL] {var_name}: {e}")
            if "rate limit" in str(e).lower():
                print("    Waiting 10 seconds...")
                time.sleep(10)

    print("\n" + "=" * 70)
    print("Update Complete!")
    print("=" * 70)

    print("\nUpdated variables:")
    for key in credentials_to_update.keys():
        print(f"  - {key}")

    print("\nNOTE: The service is configured to use Salesforce OAuth2 credentials.")
    print("      If the service expects username/password flow, you may need to:")
    print("      1. Update SALESFORCE_USERNAME with real username")
    print("      2. Update SALESFORCE_PASSWORD with real password")
    print("      3. Update SALESFORCE_SECURITY_TOKEN with real token")

    print("\nHelios integration set to localhost (disabled for now).")
    print("Deploy Helios service and update HELIOS_API_URL and HELIOS_API_KEY later.")

    print("\nRailway will automatically redeploy the service now.")

if __name__ == "__main__":
    main()
