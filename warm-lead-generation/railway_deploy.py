#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Deployment Script
Automates service creation and environment variable configuration via Railway GraphQL API
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
        print("❌ Railway config not found. Please run 'railway login' first.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    token = config['user']['token']
    project_id = config['projects'].get(
        str(Path.cwd().parent / "independent-accounting-system"), {}
    ).get('project')

    if not project_id:
        # Try to get the first project
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
        print(f"❌ API request failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()

    if 'errors' in result:
        print(f"❌ GraphQL errors: {json.dumps(result['errors'], indent=2)}")
        sys.exit(1)

    return result['data']

def get_project_info(token, project_id):
    """Get project information including environments and services"""
    query = """
    query getProject($projectId: String!) {
        project(id: $projectId) {
            id
            name
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            services {
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
    data = graphql_request(token, query, variables)
    return data['project']

def create_service(token, project_id, environment_id, service_name):
    """Create a new service in the project"""
    query = """
    mutation serviceCreate($input: ServiceCreateInput!) {
        serviceCreate(input: $input) {
            id
            name
        }
    }
    """

    variables = {
        "input": {
            "name": service_name,
            "projectId": project_id,
            "source": {
                "repo": "KFP-SEAN/nerdx-apec-mvp"
            }
        }
    }

    data = graphql_request(token, query, variables)
    return data['serviceCreate']

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

def set_environment_variables(token, project_id, service_id, environment_id, variables_dict):
    """Set multiple environment variables for a service"""
    results = []
    for i, (var_name, var_value) in enumerate(variables_dict.items()):
        try:
            result = set_environment_variable(token, project_id, service_id, environment_id, var_name, var_value)
            results.append((var_name, True))
            print(f"  [OK] {var_name}")
            # Add delay to avoid rate limiting (except for the last variable)
            if i < len(variables_dict) - 1:
                time.sleep(0.5)
        except Exception as e:
            results.append((var_name, False))
            print(f"  [FAIL] {var_name}: {e}")
    return results

def main():
    print("=" * 70)
    print("Railway Deployment Script - NERD12 Warm Lead Generation")
    print("=" * 70)

    # Load Railway configuration
    print("\n[1/5] Loading Railway configuration...")
    token, project_id = load_railway_config()
    print(f"✅ Loaded token and project ID: {project_id}")

    # Get project information
    print("\n[2/5] Fetching project information...")
    project_info = get_project_info(token, project_id)
    print(f"✅ Project: {project_info['name']}")

    # Get production environment
    environments = project_info['environments']['edges']
    prod_env = next((e['node'] for e in environments if e['node']['name'] == 'production'), None)

    if not prod_env:
        print("❌ Production environment not found")
        sys.exit(1)

    print(f"✅ Environment: {prod_env['name']} ({prod_env['id']})")

    # Check if service already exists
    services = project_info['services']['edges']
    existing_service = next((s['node'] for s in services if s['node']['name'] == 'warm-lead-generation'), None)

    if existing_service:
        print(f"\n[3/5] Service already exists: {existing_service['name']}")
        service_id = existing_service['id']
    else:
        print("\n[3/5] Creating new service...")
        service = create_service(token, project_id, prod_env['id'], 'warm-lead-generation')
        service_id = service['id']
        print(f"✅ Created service: {service['name']} ({service_id})")

    # Set environment variables
    print("\n[4/5] Setting environment variables...")

    env_vars = {
        "API_ENVIRONMENT": "production",
        "API_HOST": "0.0.0.0",
        # Salesforce - User needs to provide actual values
        "SALESFORCE_INSTANCE_URL": "https://your-instance.salesforce.com",
        "SALESFORCE_USERNAME": "your-username@domain.com",
        "SALESFORCE_PASSWORD": "your-password",
        "SALESFORCE_SECURITY_TOKEN": "your-token",
        "SALESFORCE_CONSUMER_KEY": "your-consumer-key",
        "SALESFORCE_CONSUMER_SECRET": "your-consumer-secret",
        # Helios - User needs to provide actual values
        "HELIOS_API_URL": "https://your-helios-instance.railway.app",
        "HELIOS_API_KEY": "your-helios-api-key",
        # NBRS Configuration
        "NBRS_WEIGHT_BRAND_AFFINITY": "0.40",
        "NBRS_WEIGHT_MARKET_POSITIONING": "0.35",
        "NBRS_WEIGHT_DIGITAL_PRESENCE": "0.25",
        "NBRS_THRESHOLD_TIER1": "80.0",
        "NBRS_THRESHOLD_TIER2": "60.0",
        "NBRS_THRESHOLD_TIER3": "40.0",
        # Target Revenue
        "TARGET_MONTHLY_REVENUE_KRW": "500000000"
    }

    results = set_environment_variables(token, project_id, service_id, prod_env['id'], env_vars)
    success_count = sum(1 for _, success in results if success)
    print(f"✅ Set {success_count}/{len(env_vars)} environment variables successfully")

    print("\n[5/5] Deployment summary...")
    print(f"✅ Service ID: {service_id}")
    print(f"✅ Environment: {prod_env['name']}")
    print(f"✅ Variables configured: {len(env_vars)}")

    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT: Update the following placeholder values in Railway Dashboard:")
    print("=" * 70)
    print("1. SALESFORCE_INSTANCE_URL")
    print("2. SALESFORCE_USERNAME")
    print("3. SALESFORCE_PASSWORD")
    print("4. SALESFORCE_SECURITY_TOKEN")
    print("5. SALESFORCE_CONSUMER_KEY")
    print("6. SALESFORCE_CONSUMER_SECRET")
    print("7. HELIOS_API_URL")
    print("8. HELIOS_API_KEY")
    print("\nGo to: https://railway.app/project/{}/{}".format(
        project_id, prod_env['id']
    ))
    print("=" * 70)

    print("\n✅ Deployment script completed!")
    print("🚀 Railway will automatically deploy after you update the environment variables")

if __name__ == "__main__":
    main()
