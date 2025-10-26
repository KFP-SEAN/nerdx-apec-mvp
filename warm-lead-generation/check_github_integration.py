#!/usr/bin/env python3
"""
Check Railway GitHub integration and deployment settings
"""
import os
import requests
import json

# Read token from .railway_credentials file
credentials_file = os.path.expanduser("~/.railway_credentials")
if os.path.exists(credentials_file):
    with open(credentials_file, "r") as f:
        creds = json.load(f)
        RAILWAY_TOKEN = creds.get("token")
else:
    RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")

PROJECT_ID = "53c2f700-32ca-491f-b525-8552114b6fd6"
SERVICE_ID = "31e0581c-9ec4-4805-a9e2-abf4c7ad907e"

API_URL = "https://backboard.railway.com/graphql/v2"

def check_service_details():
    """Get service details including GitHub repo configuration"""
    query = """
    query service($id: String!) {
        service(id: $id) {
            id
            name
            repoTriggers {
                provider
                repo
                branch
            }
            source {
                repo
                repoName
                branch
            }
        }
    }
    """

    variables = {"id": SERVICE_ID}

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
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}")
        return None

    service = data.get("data", {}).get("service")
    if service:
        print("Service Details:")
        print(f"  Name: {service['name']}")
        print(f"\nSource:")
        print(f"  {json.dumps(service.get('source'), indent=2)}")
        print(f"\nRepo Triggers:")
        print(f"  {json.dumps(service.get('repoTriggers'), indent=2)}")
        return service

if __name__ == "__main__":
    if not RAILWAY_TOKEN:
        print("Error: RAILWAY_TOKEN not found")
        exit(1)

    check_service_details()
