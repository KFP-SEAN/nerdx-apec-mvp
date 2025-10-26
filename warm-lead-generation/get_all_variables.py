#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get ALL environment variables from nerdx-apec-mvp service
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

def get_service_variables(token, project_id, service_id, environment_id):
    """Get ALL environment variables for nerdx-apec-mvp service"""
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
    print("Get ALL Variables from nerdx-apec-mvp Service")
    print("=" * 70)

    token = load_railway_config()

    # IDs from previous output
    project_id = "53c2f700-32ca-491f-b525-8552114b6fd6"
    service_id = "3397ff6d-bfeb-497b-9f8f-d94c6a951ba2"  # nerdx-apec-mvp
    environment_id = "69a62047-a360-4d70-8793-b7c6542f6dc0"  # production

    print(f"\nFetching variables for service: nerdx-apec-mvp")

    variables_data = get_service_variables(token, project_id, service_id, environment_id)

    if variables_data and variables_data.get('variables'):
        vars_dict = variables_data['variables']

        print(f"\nFound {len(vars_dict)} environment variables:\n")

        # Filter for Salesforce and Helios
        salesforce_vars = {}
        helios_vars = {}
        other_vars = {}

        for key, value in vars_dict.items():
            if key.startswith('SALESFORCE_'):
                salesforce_vars[key] = value
            elif key.startswith('HELIOS_'):
                helios_vars[key] = value
            else:
                other_vars[key] = value

        # Display Salesforce credentials
        if salesforce_vars:
            print("SALESFORCE CREDENTIALS:")
            for key, value in salesforce_vars.items():
                # Mask sensitive values
                if 'PASSWORD' in key or 'SECRET' in key or 'TOKEN' in key:
                    display_value = value[:10] + "..." if len(value) > 10 else value
                else:
                    display_value = value
                print(f"  {key} = {display_value}")
        else:
            print("No Salesforce credentials found")

        # Display Helios credentials
        if helios_vars:
            print("\nHELIOS CREDENTIALS:")
            for key, value in helios_vars.items():
                # Mask API key
                if 'KEY' in key:
                    display_value = value[:10] + "..." if len(value) > 10 else value
                else:
                    display_value = value
                print(f"  {key} = {display_value}")
        else:
            print("\nNo Helios credentials found")

        # Save to file
        credentials = {**salesforce_vars, **helios_vars}

        if credentials:
            output_file = 'nerdx_apec_mvp_credentials.json'
            with open(output_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            print(f"\nCredentials saved to: {output_file}")

            # Check completeness
            required_salesforce = [
                'SALESFORCE_INSTANCE_URL',
                'SALESFORCE_USERNAME',
                'SALESFORCE_PASSWORD',
                'SALESFORCE_SECURITY_TOKEN',
                'SALESFORCE_CONSUMER_KEY',
                'SALESFORCE_CONSUMER_SECRET'
            ]

            required_helios = [
                'HELIOS_API_URL',
                'HELIOS_API_KEY'
            ]

            salesforce_complete = all(k in salesforce_vars for k in required_salesforce)
            helios_complete = all(k in helios_vars for k in required_helios)

            print("\n" + "=" * 70)
            print("Completeness Check:")
            print("=" * 70)
            print(f"Salesforce: {'✓ COMPLETE' if salesforce_complete else '✗ INCOMPLETE'}")

            if not salesforce_complete:
                missing = [k for k in required_salesforce if k not in salesforce_vars]
                print(f"  Missing: {', '.join(missing)}")

            print(f"Helios: {'✓ COMPLETE' if helios_complete else '✗ INCOMPLETE'}")

            if not helios_complete:
                missing = [k for k in required_helios if k not in helios_vars]
                print(f"  Missing: {', '.join(missing)}")

    else:
        print("No variables found for this service")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
