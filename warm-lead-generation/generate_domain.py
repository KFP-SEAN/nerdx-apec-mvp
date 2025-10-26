#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Railway domain for the service
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
    result = response.json()

    if 'errors' in result:
        print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
        return None

    return result.get('data')

def create_service_domain(token, environment_id, service_id):
    """Create a Railway-generated domain for the service"""
    query = """
    mutation serviceDomainCreate($input: ServiceDomainCreateInput!) {
        serviceDomainCreate(input: $input) {
            id
            domain
        }
    }
    """

    variables = {
        "input": {
            "environmentId": environment_id,
            "serviceId": service_id
        }
    }

    return graphql_request(token, query, variables)

def main():
    print("=" * 70)
    print("Generate Railway Domain")
    print("=" * 70)

    token = load_railway_config()

    # Service IDs
    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"

    print("\nCreating Railway domain...")

    result = create_service_domain(token, environment_id, service_id)

    if result and result.get('serviceDomainCreate'):
        domain_data = result['serviceDomainCreate']
        domain = domain_data['domain']
        url = f"https://{domain}"

        print(f"\n{'='*70}")
        print("✓ Domain Created Successfully!")
        print(f"{'='*70}")
        print(f"\nService URL: {url}")
        print(f"{'='*70}\n")

        # Save to file
        with open('service_url.txt', 'w') as f:
            f.write(url)

        print(f"URL saved to: service_url.txt")

        return url
    else:
        print("\nFailed to create domain. It may already exist.")
        print("Check Railway Dashboard:")
        print("https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
