#!/usr/bin/env python3
"""
Trigger Railway redeploy via GraphQL API
"""
import os
import requests
import json

RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
PROJECT_ID = "53c2f700-32ca-491f-b525-8552114b6fd6"
SERVICE_ID = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"
ENVIRONMENT_ID = "6e3ec050-fb84-4158-b2f3-ea5da58ca2d1"

API_URL = "https://backboard.railway.com/graphql/v2"

def trigger_redeploy():
    """Trigger a new deployment"""
    query = """
    mutation serviceInstanceRedeploy($serviceId: String!, $environmentId: String!) {
        serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
    }
    """

    variables = {
        "serviceId": SERVICE_ID,
        "environmentId": ENVIRONMENT_ID
    }

    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }

    print("Triggering Railway redeploy...")
    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()

    if "errors" in data:
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}")
        return False

    if data.get("data", {}).get("serviceInstanceRedeploy"):
        print("✓ Redeploy triggered successfully!")
        print("\nWait 1-2 minutes for deployment to complete, then test again.")
        return True
    else:
        print("Failed to trigger redeploy")
        print(f"Response: {json.dumps(data, indent=2)}")
        return False

if __name__ == "__main__":
    if not RAILWAY_TOKEN:
        print("Error: RAILWAY_TOKEN environment variable not set")
        exit(1)

    trigger_redeploy()
