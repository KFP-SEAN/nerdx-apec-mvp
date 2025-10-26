#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get existing credentials from Railway services
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

    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
            return None
        return result.get('data')
    else:
        print(f"API request failed: {response.status_code}")
        return None

def get_all_services(token, project_id):
    """Get all services in the project"""
    query = """
    query getProject($projectId: String!) {
        project(id: $projectId) {
            id
            name
            services {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
    }
    """

    variables = {"projectId": project_id}
    return graphql_request(token, query, variables)

def get_service_variables(token, project_id, service_id, environment_id):
    """Get environment variables for a specific service"""
    query = """
    query variables($projectId: String!, $environmentId: String!, $serviceId: String) {
        variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
    }
    """

    variables = {
        "projectId": project_id,
        "environmentId": environment_id,
        "serviceId": service_id
    }

    return graphql_request(token, query, variables)

def main():
    print("=" * 70)
    print("Get Existing Credentials from Railway")
    print("=" * 70)

    token, project_id = load_railway_config()
    print(f"\nProject ID: {project_id}")

    # Get all services
    print("\nFetching services...")
    project_data = get_all_services(token, project_id)

    if not project_data:
        print("Failed to fetch project data")
        return

    services = project_data['project']['services']['edges']
    environments = project_data['project']['environments']['edges']

    print(f"\nFound {len(services)} services:")
    for service in services:
        print(f"  - {service['node']['name']} (ID: {service['node']['id']})")

    print(f"\nFound {len(environments)} environments:")
    for env in environments:
        print(f"  - {env['node']['name']} (ID: {env['node']['id']})")

    # Get production environment
    prod_env = next((e['node'] for e in environments if e['node']['name'] == 'production'), None)

    if not prod_env:
        print("\nNo production environment found")
        return

    print(f"\nUsing environment: {prod_env['name']}")

    # Check each service for Salesforce/Helios credentials
    print("\n" + "=" * 70)
    print("Searching for Salesforce and Helios credentials...")
    print("=" * 70)

    found_credentials = {}

    for service in services:
        service_name = service['node']['name']
        service_id = service['node']['id']

        print(f"\nChecking service: {service_name}")

        variables_data = get_service_variables(token, project_id, service_id, prod_env['id'])

        if variables_data and variables_data.get('variables'):
            vars_dict = variables_data['variables']

            # Look for Salesforce credentials
            salesforce_keys = [
                'SALESFORCE_INSTANCE_URL',
                'SALESFORCE_USERNAME',
                'SALESFORCE_PASSWORD',
                'SALESFORCE_SECURITY_TOKEN',
                'SALESFORCE_CONSUMER_KEY',
                'SALESFORCE_CONSUMER_SECRET'
            ]

            # Look for Helios credentials
            helios_keys = [
                'HELIOS_API_URL',
                'HELIOS_API_KEY'
            ]

            for key in salesforce_keys + helios_keys:
                if key in vars_dict:
                    value = vars_dict[key]
                    # Don't show full value if it looks like a real credential
                    if value and not value.startswith('your-') and not value.startswith('https://your-'):
                        found_credentials[key] = value
                        print(f"  Found: {key} = {value[:20]}..." if len(value) > 20 else f"  Found: {key} = {value}")
                    else:
                        print(f"  Placeholder: {key}")

    # Save found credentials
    if found_credentials:
        print("\n" + "=" * 70)
        print("Found Credentials Summary")
        print("=" * 70)

        salesforce_complete = all(k in found_credentials for k in [
            'SALESFORCE_INSTANCE_URL',
            'SALESFORCE_USERNAME',
            'SALESFORCE_PASSWORD',
            'SALESFORCE_SECURITY_TOKEN',
            'SALESFORCE_CONSUMER_KEY',
            'SALESFORCE_CONSUMER_SECRET'
        ])

        helios_complete = all(k in found_credentials for k in [
            'HELIOS_API_URL',
            'HELIOS_API_KEY'
        ])

        print(f"\nSalesforce: {'COMPLETE' if salesforce_complete else 'INCOMPLETE'}")
        print(f"Helios: {'COMPLETE' if helios_complete else 'INCOMPLETE'}")

        # Save to file
        output_file = 'found_credentials.json'
        with open(output_file, 'w') as f:
            json.dump(found_credentials, f, indent=2)

        print(f"\nCredentials saved to: {output_file}")
        print("\nFound credentials:")
        for key in found_credentials:
            print(f"  - {key}")

    else:
        print("\nNo real credentials found. All services have placeholder values.")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
