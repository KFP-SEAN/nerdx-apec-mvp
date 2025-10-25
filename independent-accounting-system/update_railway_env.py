#!/usr/bin/env python3
"""
Railway Environment Variable Updater
Directly updates SMTP_PASSWORD via Railway GraphQL API
"""
import os
import sys
import requests
import json

def update_railway_env_var():
    """Update Railway environment variable using GraphQL API"""

    # Railway API endpoint
    RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

    # Check for Railway token
    print("\n" + "="*70)
    print("[INFO] Railway Environment Variable Updater")
    print("="*70)

    # Get Railway token from user
    print("\n[STEP 1] Get Railway API Token")
    print("Visit: https://railway.app/account/tokens")
    print("Create a new token and paste it here:")

    token = input("\nRailway API Token: ").strip()

    if not token:
        print("[ERROR] No token provided")
        return False

    # Get project ID
    print("\n[STEP 2] Get Project ID")
    print("Visit your project settings in Railway Dashboard")
    print("The Project ID is in the URL: railway.app/project/PROJECT_ID")

    project_id = input("\nProject ID: ").strip()

    if not project_id:
        print("[ERROR] No project ID provided")
        return False

    # Get service ID (optional - we'll try to find it)
    print("\n[STEP 3] Get Service ID (optional - we can try to auto-detect)")
    service_id = input("\nService ID (press Enter to auto-detect): ").strip()

    # GraphQL query to get services
    if not service_id:
        print("\n[INFO] Fetching services...")

        query = """
        query project($id: String!) {
            project(id: $id) {
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

        response = requests.post(
            RAILWAY_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "variables": {"id": project_id}
            }
        )

        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch services: {response.text}")
            return False

        data = response.json()
        services = data.get("data", {}).get("project", {}).get("services", {}).get("edges", [])

        if not services:
            print("[ERROR] No services found in project")
            return False

        print("\n[INFO] Available services:")
        for i, edge in enumerate(services):
            service = edge["node"]
            print(f"  {i+1}. {service['name']} (ID: {service['id']})")

        if len(services) == 1:
            service_id = services[0]["node"]["id"]
            print(f"\n[INFO] Auto-selected service: {services[0]['node']['name']}")
        else:
            choice = input("\nSelect service number: ").strip()
            try:
                service_id = services[int(choice)-1]["node"]["id"]
            except (ValueError, IndexError):
                print("[ERROR] Invalid selection")
                return False

    # Update environment variable
    print("\n[STEP 4] Updating SMTP_PASSWORD...")

    mutation = """
    mutation variableUpsert($input: VariableUpsertInput!) {
        variableUpsert(input: $input)
    }
    """

    smtp_password = "cbkzetdulcsidlxp"  # The working password from local test

    response = requests.post(
        RAILWAY_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "query": mutation,
            "variables": {
                "input": {
                    "projectId": project_id,
                    "serviceId": service_id,
                    "name": "SMTP_PASSWORD",
                    "value": smtp_password
                }
            }
        }
    )

    if response.status_code != 200:
        print(f"[ERROR] Failed to update variable: {response.text}")
        return False

    result = response.json()

    if "errors" in result:
        print(f"[ERROR] GraphQL errors: {result['errors']}")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] SMTP_PASSWORD updated successfully!")
    print("="*70)
    print("\nRailway will automatically redeploy the service (2-3 minutes)")
    print("\nAfter deployment, test with:")
    print('curl -s -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-25" -H "Content-Type: application/json" -d \'{"recipients":["sean@koreafnbpartners.com"]}\'')
    print("\n" + "="*70)

    return True

if __name__ == "__main__":
    try:
        success = update_railway_env_var()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
