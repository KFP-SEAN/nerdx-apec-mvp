#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Service Update - Set Root Directory
Updates service to use correct root directory
"""

import json
import requests
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Railway API Configuration
RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

def load_railway_config():
    """Load Railway token and project info from config file"""
    config_path = Path.home() / ".railway" / "config.json"

    with open(config_path, 'r') as f:
        config = json.load(f)

    token = config['user']['token']
    project_id = list(config['projects'].values())[0]['project']

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
        return None

    result = response.json()

    if 'errors' in result:
        print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
        return None

    return result['data']

def update_service(token, service_id, root_directory):
    """Update service with root directory"""
    # Try serviceUpdate mutation
    query = """
    mutation serviceUpdate($input: ServiceUpdateInput!) {
        serviceUpdate(input: $input) {
            id
            name
        }
    }
    """

    variables = {
        "input": {
            "serviceId": service_id,
            "rootDirectory": root_directory
        }
    }

    data = graphql_request(token, query, variables)
    return data

def main():
    print("=" * 70)
    print("Railway - Set Root Directory")
    print("=" * 70)

    # Load configuration
    print("\n[1/2] Loading configuration...")
    token, project_id = load_railway_config()
    print(f"Loaded token and project ID: {project_id}")

    # Service ID from previous run
    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
    root_directory = "warm-lead-generation"

    print(f"Service ID: {service_id}")
    print(f"Root Directory: {root_directory}")

    # Update service
    print(f"\n[2/2] Updating service root directory...")
    result = update_service(token, service_id, root_directory)

    if result:
        print(f"Success! Service updated.")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to update service. You may need to set this manually in Railway Dashboard.")
        print(f"\nGo to: https://railway.app/project/{project_id}")
        print("-> Select warm-lead-generation service")
        print("-> Settings -> Source")
        print(f"-> Set Root Directory: {root_directory}")

    print("\n" * 70)

if __name__ == "__main__":
    main()
