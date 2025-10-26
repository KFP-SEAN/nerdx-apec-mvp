#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get service URL from Railway
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
    return result.get('data')

def get_deployment_url(token, deployment_id):
    """Get deployment URL"""
    query = """
    query deployment($deploymentId: String!) {
        deployment(id: $deploymentId) {
            id
            status
            url
            staticUrl
        }
    }
    """

    variables = {"deploymentId": deployment_id}
    return graphql_request(token, query, variables)

def main():
    token = load_railway_config()

    # Latest successful deployment ID
    deployment_id = "631cbae0-2220-440e-baf8-77adf89107fb"

    print("Fetching deployment URL...")
    deployment_data = get_deployment_url(token, deployment_id)

    if deployment_data and deployment_data.get('deployment'):
        deployment = deployment_data['deployment']

        url = deployment.get('url') or deployment.get('staticUrl')

        if url:
            if not url.startswith('http'):
                url = f"https://{url}"

            print(f"\n{'='*70}")
            print("SERVICE URL")
            print(f"{'='*70}")
            print(f"\n{url}\n")
            print(f"{'='*70}")

            # Save to file
            with open('service_url.txt', 'w') as f:
                f.write(url)

            print(f"\nURL saved to: service_url.txt")

            return url
        else:
            print("No URL found for this deployment")
    else:
        print("Failed to fetch deployment data")

    return None

if __name__ == "__main__":
    main()
