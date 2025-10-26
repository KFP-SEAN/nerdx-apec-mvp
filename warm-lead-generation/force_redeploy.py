#!/usr/bin/env python3
"""
Force Railway redeploy by creating a service instance deployment via GraphQL API
"""
import os
import requests
import json
import time

# Read credentials
credentials_file = os.path.expanduser("~/.railway_credentials")
if os.path.exists(credentials_file):
    with open(credentials_file, "r") as f:
        creds = json.load(f)
        RAILWAY_TOKEN = creds.get("token")
else:
    RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")

PROJECT_ID = "53c2f700-32ca-491f-b525-8552114b6fd6"
SERVICE_ID = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
ENVIRONMENT_ID = "6e3ec050-fb84-4158-b2f3-ea5da58ca2d1"

API_URL = "https://backboard.railway.com/graphql/v2"

def trigger_deployment():
    """Trigger a new deployment by redeploying the service"""

    # Method 1: Try serviceInstanceRedeploy mutation
    query = """
    mutation serviceInstanceRedeploy($environmentId: String!, $serviceId: String!) {
        serviceInstanceRedeploy(environmentId: $environmentId, serviceId: $serviceId)
    }
    """

    variables = {
        "environmentId": ENVIRONMENT_ID,
        "serviceId": SERVICE_ID
    }

    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }

    print("=" * 70)
    print("Force Redeploying warm-lead-generation service...")
    print("=" * 70)
    print()

    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()

    if "errors" in data:
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}")

        # Method 2: Try creating a new deployment directly
        print("\nTrying alternative method: deploymentTrigger...")

        query2 = """
        mutation deploymentTrigger($environmentId: String!, $projectId: String!, $serviceId: String!) {
            deploymentTrigger(environmentId: $environmentId, projectId: $projectId, serviceId: $serviceId) {
                id
            }
        }
        """

        variables2 = {
            "environmentId": ENVIRONMENT_ID,
            "projectId": PROJECT_ID,
            "serviceId": SERVICE_ID
        }

        response2 = requests.post(
            API_URL,
            json={"query": query2, "variables": variables2},
            headers=headers
        )

        data2 = response2.json()

        if "errors" in data2:
            print(f"Alternative method also failed: {json.dumps(data2['errors'], indent=2)}")
            return False

        deployment_id = data2.get("data", {}).get("deploymentTrigger", {}).get("id")
        if deployment_id:
            print(f"✓ New deployment triggered! Deployment ID: {deployment_id}")
            return True
        else:
            print("Failed to trigger deployment")
            return False

    result = data.get("data", {}).get("serviceInstanceRedeploy")
    if result:
        print("✓ Service redeploy triggered successfully!")
        print("\nDeployment is starting...")
        print("This will take 1-2 minutes.")
        print("\nMonitoring deployment status...")

        # Wait and monitor
        time.sleep(10)
        check_deployment_status()

        return True
    else:
        print("Failed to trigger redeploy")
        print(f"Response: {json.dumps(data, indent=2)}")
        return False

def check_deployment_status():
    """Check the latest deployment status"""
    query = """
    query deployments($projectId: String!, $first: Int!) {
        deployments(input: {projectId: $projectId}, first: $first) {
            edges {
                node {
                    id
                    status
                    createdAt
                    service {
                        name
                    }
                }
            }
        }
    }
    """

    variables = {
        "projectId": PROJECT_ID,
        "first": 3
    }

    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()

    if "errors" in data:
        print(f"Error checking status: {json.dumps(data['errors'], indent=2)}")
        return

    deployments = data.get("data", {}).get("deployments", {}).get("edges", [])

    if deployments:
        print("\nRecent deployments:")
        for edge in deployments[:3]:
            node = edge["node"]
            service_name = node.get("service", {}).get("name", "Unknown")
            if "warm-lead" in service_name.lower():
                print(f"  [{node['status']}] {node['createdAt'][:19]} - {service_name}")

        latest = deployments[0]["node"]
        if "warm-lead" in latest.get("service", {}).get("name", "").lower():
            status = latest["status"]
            print(f"\nLatest deployment status: {status}")

            if status == "BUILDING":
                print("→ Building new image with latest code...")
            elif status == "DEPLOYING":
                print("→ Deploying new version...")
            elif status == "SUCCESS":
                print("✓ Deployment successful!")
            elif status == "FAILED":
                print("✗ Deployment failed - check Railway logs")

if __name__ == "__main__":
    if not RAILWAY_TOKEN:
        print("Error: RAILWAY_TOKEN not found")
        print("\nPlease ensure ~/.railway_credentials file exists with your token")
        exit(1)

    success = trigger_deployment()

    if success:
        print("\n" + "=" * 70)
        print("Deployment triggered!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Wait 1-2 minutes for deployment to complete")
        print("2. Check Railway Dashboard for deployment status")
        print("3. Run verification test:")
        print("\n   cd warm-lead-generation && verify_deployment.bat")
        print("\n" + "=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Failed to trigger deployment via API")
        print("=" * 70)
        print("\nPlease try manual deployment via Railway Dashboard:")
        print("1. Go to: https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6")
        print("2. Click 'warm-lead-generation' service")
        print("3. Click 'Redeploy' or add a dummy environment variable")
        print("=" * 70)
