#!/usr/bin/env python3
"""
Create NBRS custom fields using Salesforce REST API with CLI access token
"""
import json
import requests
import sys

# Salesforce org details from CLI
# TODO: Get access token from Salesforce CLI: sf org display --target-org nerdx-org --json
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # Replace with actual token from sf org display
INSTANCE_URL = "https://innovation-innovation-8209.my.salesforce.com"

def create_custom_field(field_metadata):
    """Create a custom field using Tooling API"""
    url = f"{INSTANCE_URL}/services/data/v59.0/tooling/sobjects/CustomField"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=field_metadata)
        result = response.json()

        if response.status_code == 201 and result.get("success"):
            return True, result.get("id")
        else:
            return False, result

    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("Creating NBRS Custom Fields on Lead Object")
    print("=" * 60)
    print()

    # Define fields to create
    fields = [
        {
            "FullName": "Lead.NBRS_Score__c",
            "Metadata": {
                "type": "Number",
                "label": "NBRS Score",
                "precision": 5,
                "scale": 2,
                "description": "Overall NBRS score (0-100)",
                "required": False,
                "unique": False,
                "externalId": False
            }
        },
        {
            "FullName": "Lead.Brand_Affinity_Score__c",
            "Metadata": {
                "type": "Number",
                "label": "Brand Affinity Score",
                "precision": 5,
                "scale": 2,
                "description": "Brand affinity component (0-100)",
                "required": False
            }
        },
        {
            "FullName": "Lead.Market_Positioning_Score__c",
            "Metadata": {
                "type": "Number",
                "label": "Market Positioning Score",
                "precision": 5,
                "scale": 2,
                "description": "Market positioning component (0-100)",
                "required": False
            }
        },
        {
            "FullName": "Lead.Digital_Presence_Score__c",
            "Metadata": {
                "type": "Number",
                "label": "Digital Presence Score",
                "precision": 5,
                "scale": 2,
                "description": "Digital presence component (0-100)",
                "required": False
            }
        },
        {
            "FullName": "Lead.Priority_Rank__c",
            "Metadata": {
                "type": "Number",
                "label": "Priority Rank",
                "precision": 5,
                "scale": 0,
                "description": "Ranking among all leads",
                "required": False
            }
        },
        {
            "FullName": "Lead.Next_Action__c",
            "Metadata": {
                "type": "Text",
                "label": "Next Action",
                "length": 255,
                "description": "Recommended next action",
                "required": False
            }
        },
        {
            "FullName": "Lead.NBRS_Calculated_Date__c",
            "Metadata": {
                "type": "DateTime",
                "label": "NBRS Calculated Date",
                "description": "When NBRS was last calculated",
                "required": False
            }
        },
        {
            "FullName": "Lead.NBRS_Tier__c",
            "Metadata": {
                "type": "Picklist",
                "label": "NBRS Tier",
                "description": "Lead tier classification",
                "required": False,
                "valueSet": {
                    "valueSetDefinition": {
                        "sorted": False,
                        "value": [
                            {"fullName": "TIER1", "default": False, "label": "TIER1"},
                            {"fullName": "TIER2", "default": False, "label": "TIER2"},
                            {"fullName": "TIER3", "default": False, "label": "TIER3"},
                            {"fullName": "TIER4", "default": False, "label": "TIER4"}
                        ]
                    }
                }
            }
        }
    ]

    success_count = 0
    error_count = 0

    for field in fields:
        field_name = field["FullName"].split(".")[-1]
        print(f"Creating {field_name}...", end=" ")

        success, result = create_custom_field(field)

        if success:
            print(f"OK (ID: {result})")
            success_count += 1
        else:
            print(f"FAILED")
            print(f"  Error: {json.dumps(result, indent=2)}")
            error_count += 1

    print()
    print("=" * 60)
    print(f"Results: {success_count} created, {error_count} failed")
    print("=" * 60)

    if error_count > 0:
        print()
        print("NOTE: Some errors may be expected if fields already exist.")
        print("Check Salesforce Setup to verify field creation.")

    return error_count == 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
