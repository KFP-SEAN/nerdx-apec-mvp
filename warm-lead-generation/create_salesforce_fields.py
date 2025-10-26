#!/usr/bin/env python3
"""
Create NBRS custom fields on Lead object in Salesforce
Uses Metadata API to create fields programmatically
"""
import sys
from simple_salesforce import Salesforce, SalesforceLogin
from config import settings

def create_custom_fields():
    """Create all NBRS custom fields on Lead object"""
    try:
        # Login to Salesforce
        print("Logging into Salesforce...")
        session_id, instance = SalesforceLogin(
            username=settings.salesforce_username,
            password=settings.salesforce_password,
            security_token=settings.salesforce_security_token
        )
        sf = Salesforce(instance=instance, session_id=session_id)
        print(f"✓ Connected to {instance}\n")

        # Define custom fields
        fields_to_create = [
            {
                "fullName": "Lead.NBRS_Score__c",
                "label": "NBRS Score",
                "type": "Number",
                "precision": 5,
                "scale": 2,
                "description": "Overall NBRS score (0-100)"
            },
            {
                "fullName": "Lead.NBRS_Tier__c",
                "label": "NBRS Tier",
                "type": "Picklist",
                "description": "Lead tier classification (TIER1=Top, TIER4=Low)",
                "picklist": {
                    "picklistValues": [
                        {"fullName": "TIER1", "default": False},
                        {"fullName": "TIER2", "default": False},
                        {"fullName": "TIER3", "default": False},
                        {"fullName": "TIER4", "default": False}
                    ],
                    "sorted": False
                }
            },
            {
                "fullName": "Lead.Brand_Affinity_Score__c",
                "label": "Brand Affinity Score",
                "type": "Number",
                "precision": 5,
                "scale": 2,
                "description": "Brand affinity component (0-100)"
            },
            {
                "fullName": "Lead.Market_Positioning_Score__c",
                "label": "Market Positioning Score",
                "type": "Number",
                "precision": 5,
                "scale": 2,
                "description": "Market positioning component (0-100)"
            },
            {
                "fullName": "Lead.Digital_Presence_Score__c",
                "label": "Digital Presence Score",
                "type": "Number",
                "precision": 5,
                "scale": 2,
                "description": "Digital presence component (0-100)"
            },
            {
                "fullName": "Lead.NBRS_Calculated_Date__c",
                "label": "NBRS Calculated Date",
                "type": "DateTime",
                "description": "When NBRS was last calculated"
            },
            {
                "fullName": "Lead.Priority_Rank__c",
                "label": "Priority Rank",
                "type": "Number",
                "precision": 5,
                "scale": 0,
                "description": "Ranking among all leads (#1 = highest priority)"
            },
            {
                "fullName": "Lead.Next_Action__c",
                "label": "Next Action",
                "type": "Text",
                "length": 255,
                "description": "Recommended next action for this lead"
            }
        ]

        # Check existing fields first
        print("Checking existing fields...")
        try:
            result = sf.query("SELECT QualifiedApiName FROM FieldDefinition WHERE EntityDefinition.QualifiedApiName = 'Lead' AND QualifiedApiName LIKE 'NBRS%'")
            existing_fields = {rec['QualifiedApiName'] for rec in result['records']}
            print(f"Found {len(existing_fields)} existing NBRS fields: {existing_fields}\n")
        except Exception as e:
            print(f"Could not query existing fields: {e}\n")
            existing_fields = set()

        # Try using Tooling API to create fields
        print("Creating custom fields using Tooling API...\n")

        for field_def in fields_to_create:
            field_name = field_def["fullName"].split(".")[-1]

            # Skip if field already exists
            if field_name.replace("__c", "") in str(existing_fields):
                print(f"⊘ {field_name} already exists, skipping")
                continue

            try:
                # Prepare field metadata for Tooling API
                metadata = {
                    "FullName": field_name,
                    "Metadata": {
                        "label": field_def["label"],
                        "type": field_def["type"],
                        "description": field_def.get("description", "")
                    }
                }

                # Add type-specific attributes
                if field_def["type"] == "Number":
                    metadata["Metadata"]["precision"] = field_def["precision"]
                    metadata["Metadata"]["scale"] = field_def["scale"]
                elif field_def["type"] == "Text":
                    metadata["Metadata"]["length"] = field_def["length"]
                elif field_def["type"] == "Picklist":
                    metadata["Metadata"]["picklist"] = field_def["picklist"]

                # Use Tooling API
                response = sf.restful(f"tooling/sobjects/CustomField", method='POST', json=metadata)

                if response.get("success"):
                    print(f"✓ Created {field_name}")
                else:
                    print(f"✗ Failed to create {field_name}: {response}")

            except Exception as e:
                print(f"✗ Error creating {field_name}: {e}")

        print("\n" + "="*60)
        print("Field creation process completed!")
        print("="*60)
        print("\nNote: If fields were not created via API, please create them manually in Salesforce Setup:")
        print("Setup → Object Manager → Lead → Fields & Relationships → New")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_custom_fields()
    sys.exit(0 if success else 1)
