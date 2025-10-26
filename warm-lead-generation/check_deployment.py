#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Railway deployment status
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

def get_service_deployments(token, project_id, environment_id, service_id):
    """Get recent deployments for the service"""
    query = """
    query serviceDeployments($projectId: String!, $environmentId: String!, $serviceId: String!) {
        deployments(
            input: {
                projectId: $projectId
                environmentId: $environmentId
                serviceId: $serviceId
            }
            first: 5
        ) {
            edges {
                node {
                    id
                    status
                    createdAt
                    staticUrl
                    meta
                }
            }
        }
    }
    """

    variables = {
        "projectId": project_id,
        "environmentId": environment_id,
        "serviceId": service_id
    }

    return graphql_request(token, query, variables)

def get_service_details(token, service_id):
    """Get service details including domain"""
    query = """
    query service($serviceId: String!) {
        service(id: $serviceId) {
            id
            name
            serviceDomains {
                serviceDomains {
                    domain
                }
            }
        }
    }
    """

    variables = {"serviceId": service_id}
    return graphql_request(token, query, variables)

def main():
    print("=" * 70)
    print("Railway Deployment Status Check")
    print("=" * 70)

    token = load_railway_config()

    # Service IDs
    project_id = "53c2f700-32ca-491f-b525-8552114b6fd6"
    service_id = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"

    # Get service details
    print("\n[1/2] Fetching service details...")
    service_data = get_service_details(token, service_id)

    if service_data and service_data.get('service'):
        service = service_data['service']
        print(f"Service Name: {service['name']}")

        domains = service.get('serviceDomains', {}).get('serviceDomains', [])
        if domains:
            print(f"\nService URL:")
            for domain in domains:
                print(f"  https://{domain['domain']}")
        else:
            print("\nNo public domain configured yet")

    # Get recent deployments
    print("\n[2/2] Fetching recent deployments...")
    deployments_data = get_service_deployments(token, project_id, environment_id, service_id)

    if deployments_data and deployments_data.get('deployments'):
        deployments = deployments_data['deployments']['edges']

        if deployments:
            print(f"\nFound {len(deployments)} recent deployments:\n")

            for i, edge in enumerate(deployments, 1):
                deployment = edge['node']
                status = deployment['status']
                created_at = deployment['createdAt']
                deployment_id = deployment['id']

                # Status symbol
                status_symbol = {
                    'SUCCESS': '✓',
                    'DEPLOYING': '⋯',
                    'BUILDING': '⋯',
                    'FAILED': '✗',
                    'CRASHED': '✗',
                    'QUEUED': '⋯'
                }.get(status, '?')

                print(f"{i}. [{status_symbol}] {status}")
                print(f"   ID: {deployment_id}")
                print(f"   Created: {created_at}")

                if deployment.get('staticUrl'):
                    print(f"   URL: {deployment['staticUrl']}")

                print()

            # Check latest deployment
            latest = deployments[0]['node']
            latest_status = latest['status']

            print("=" * 70)
            print(f"Latest Deployment Status: {latest_status}")
            print("=" * 70)

            if latest_status == 'SUCCESS':
                print("\n✓ Deployment successful!")
                if latest.get('staticUrl'):
                    print(f"\nService is live at: {latest['staticUrl']}")
            elif latest_status in ['DEPLOYING', 'BUILDING', 'QUEUED']:
                print("\n⋯ Deployment in progress...")
                print("  Check Railway dashboard for live logs:")
                print(f"  https://railway.app/project/{project_id}")
            elif latest_status in ['FAILED', 'CRASHED']:
                print("\n✗ Deployment failed!")
                print("  Check Railway dashboard for error logs:")
                print(f"  https://railway.app/project/{project_id}")

        else:
            print("\nNo deployments found")
    else:
        print("\nFailed to fetch deployments")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
