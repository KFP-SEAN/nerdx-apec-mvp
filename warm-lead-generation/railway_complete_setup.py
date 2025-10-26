#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Complete Setup Script
Sets root directory using serviceInstanceUpdate mutation
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
    """Load Railway token"""
    config_path = Path.home() / ".railway" / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['user']['token'], list(config['projects'].values())[0]['project']

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

    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    return result.get('data')

def update_service_instance(token, service_id, environment_id, root_directory):
    """Update service instance with root directory using serviceInstanceUpdate"""
    query = """
    mutation serviceInstanceUpdate($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) {
        serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input)
    }
    """

    variables = {
        "serviceId": service_id,
        "environmentId": environment_id,
        "input": {
            "source": {
                "rootDirectory": root_directory
            }
        }
    }

    print(f"\nAttempting serviceInstanceUpdate...")
    print(f"Variables: {json.dumps(variables, indent=2)}")

    return graphql_request(token, query, variables)

def connect_service_with_root(token, service_id, root_directory):
    """Try using serviceConnect to set root directory"""
    query = """
    mutation serviceConnect($id: String!, $input: ServiceConnectInput!) {
        serviceConnect(id: $id, input: $input)
    }
    """

    variables = {
        "id": service_id,
        "input": {
            "repo": "KFP-SEAN/nerdx-apec-mvp",
            "rootDirectory": root_directory
        }
    }

    print(f"\nAttempting serviceConnect...")
    print(f"Variables: {json.dumps(variables, indent=2)}")

    return graphql_request(token, query, variables)

def main():
    print("=" * 70)
    print("Railway Complete Setup - Set Root Directory")
    print("=" * 70)

    token, project_id = load_railway_config()

    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"
    root_directory = "warm-lead-generation"

    print(f"\nConfiguration:")
    print(f"Project ID: {project_id}")
    print(f"Service ID: {service_id}")
    print(f"Environment ID: {environment_id}")
    print(f"Root Directory: {root_directory}")

    # Try method 1: serviceInstanceUpdate
    print("\n" + "=" * 70)
    print("Method 1: serviceInstanceUpdate")
    print("=" * 70)
    result1 = update_service_instance(token, service_id, environment_id, root_directory)

    # Try method 2: serviceConnect
    print("\n" + "=" * 70)
    print("Method 2: serviceConnect")
    print("=" * 70)
    result2 = connect_service_with_root(token, service_id, root_directory)

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    if result1 or result2:
        print("\nOne of the methods succeeded!")
        print("Check Railway Dashboard to verify root directory is set.")
    else:
        print("\nBoth automatic methods failed.")
        print("\nManual setup required in Railway Dashboard:")
        print(f"1. Go to: https://railway.app/project/{project_id}")
        print("2. Click on 'warm-lead-generation' service")
        print("3. Go to Settings -> Source")
        print(f"4. Set Root Directory: {root_directory}")
        print("5. Save")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
