#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway GraphQL Schema Introspection
Find available mutations for updating service configuration
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

def introspect_mutations(token):
    """Get all available mutations from Railway GraphQL schema"""
    query = """
    query IntrospectionQuery {
      __schema {
        mutationType {
          name
          fields {
            name
            description
            args {
              name
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(RAILWAY_API_URL, headers=headers, json={"query": query})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def find_service_mutations(introspection_data):
    """Find mutations related to service configuration"""
    if not introspection_data or 'data' not in introspection_data:
        return []

    mutations = introspection_data['data']['__schema']['mutationType']['fields']
    service_mutations = [m for m in mutations if 'service' in m['name'].lower()]

    return service_mutations

def main():
    print("=" * 70)
    print("Railway GraphQL Schema Introspection - Service Mutations")
    print("=" * 70)

    token = load_railway_config()

    print("\nFetching GraphQL schema...")
    data = introspect_mutations(token)

    if data:
        service_mutations = find_service_mutations(data)

        print(f"\nFound {len(service_mutations)} service-related mutations:\n")

        for mutation in service_mutations:
            print(f"- {mutation['name']}")
            if mutation.get('description'):
                print(f"  Description: {mutation['description']}")
            if mutation.get('args'):
                print(f"  Arguments:")
                for arg in mutation['args']:
                    type_info = arg['type']
                    type_name = type_info.get('name') or (type_info.get('ofType', {}).get('name', 'Unknown'))
                    print(f"    - {arg['name']}: {type_name}")
            print()

        # Save full introspection to file
        with open('railway_schema.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Full schema saved to: railway_schema.json")
    else:
        print("Failed to fetch schema")

if __name__ == "__main__":
    main()
