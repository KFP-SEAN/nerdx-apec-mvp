#!/usr/bin/env python3
"""
Salesforce Custom Fields and Platform Event Setup Script
Salesforce에 NBRS 관련 custom fields 및 Platform Event 자동 생성
"""
import logging
from simple_salesforce import Salesforce, SalesforceLogin
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_custom_fields():
    """Create custom fields on Lead object"""
    try:
        # Login to Salesforce
        session_id, instance = SalesforceLogin(
            username=settings.salesforce_username,
            password=settings.salesforce_password,
            security_token=settings.salesforce_security_token
        )
        sf = Salesforce(instance=instance, session_id=session_id)

        logger.info(f"Connected to Salesforce: {instance}")

        # Note: Custom field creation requires Metadata API
        # simple-salesforce doesn't support Metadata API directly
        # This script provides the SOQL queries to check if fields exist

        # Check if custom fields already exist
        fields_to_check = [
            "NBRS_Score__c",
            "NBRS_Tier__c",
            "Brand_Affinity_Score__c",
            "Market_Positioning_Score__c",
            "Digital_Presence_Score__c",
            "NBRS_Calculated_Date__c",
            "Priority_Rank__c",
            "Next_Action__c"
        ]

        logger.info("\n" + "="*70)
        logger.info("Checking Custom Fields on Lead Object")
        logger.info("="*70)

        # Describe Lead object
        lead_metadata = sf.Lead.describe()
        existing_fields = {field['name']: field for field in lead_metadata['fields']}

        missing_fields = []
        existing_custom_fields = []

        for field_name in fields_to_check:
            if field_name in existing_fields:
                field_info = existing_fields[field_name]
                existing_custom_fields.append({
                    "name": field_name,
                    "label": field_info['label'],
                    "type": field_info['type']
                })
                logger.info(f"✓ {field_name} exists ({field_info['type']})")
            else:
                missing_fields.append(field_name)
                logger.warning(f"✗ {field_name} NOT FOUND")

        if missing_fields:
            logger.warning(f"\n{len(missing_fields)} custom fields are missing!")
            logger.info("\nTo create these fields, use Salesforce Setup UI or Metadata API:")
            logger.info("Setup → Object Manager → Lead → Fields & Relationships → New")

            print_field_creation_guide(missing_fields)
        else:
            logger.info(f"\n✓ All {len(fields_to_check)} custom fields exist!")

        return {
            "existing": existing_custom_fields,
            "missing": missing_fields,
            "total_checked": len(fields_to_check)
        }

    except Exception as e:
        logger.error(f"Error checking Salesforce fields: {e}")
        raise


def print_field_creation_guide(missing_fields):
    """Print guide for creating missing fields"""
    field_specs = {
        "NBRS_Score__c": {
            "label": "NBRS Score",
            "type": "Number",
            "length": "5,2",
            "description": "Overall NBRS score (0-100)"
        },
        "NBRS_Tier__c": {
            "label": "NBRS Tier",
            "type": "Picklist",
            "values": "TIER1, TIER2, TIER3, TIER4",
            "description": "Lead tier classification"
        },
        "Brand_Affinity_Score__c": {
            "label": "Brand Affinity Score",
            "type": "Number",
            "length": "5,2",
            "description": "Brand affinity component (0-100)"
        },
        "Market_Positioning_Score__c": {
            "label": "Market Positioning Score",
            "type": "Number",
            "length": "5,2",
            "description": "Market positioning component (0-100)"
        },
        "Digital_Presence_Score__c": {
            "label": "Digital Presence Score",
            "type": "Number",
            "length": "5,2",
            "description": "Digital presence component (0-100)"
        },
        "NBRS_Calculated_Date__c": {
            "label": "NBRS Calculated Date",
            "type": "DateTime",
            "description": "When NBRS was last calculated"
        },
        "Priority_Rank__c": {
            "label": "Priority Rank",
            "type": "Number",
            "length": "5,0",
            "description": "Ranking among all leads"
        },
        "Next_Action__c": {
            "label": "Next Action",
            "type": "Text",
            "length": "255",
            "description": "Recommended next action"
        }
    }

    logger.info("\n" + "="*70)
    logger.info("Field Creation Guide")
    logger.info("="*70)

    for field_name in missing_fields:
        if field_name in field_specs:
            spec = field_specs[field_name]
            logger.info(f"\nField: {field_name}")
            logger.info(f"  Label: {spec['label']}")
            logger.info(f"  Type: {spec['type']}")
            if 'length' in spec:
                logger.info(f"  Length: {spec['length']}")
            if 'values' in spec:
                logger.info(f"  Values: {spec['values']}")
            logger.info(f"  Description: {spec['description']}")


def check_platform_event():
    """Check if NBRS_Calculation__e Platform Event exists"""
    try:
        session_id, instance = SalesforceLogin(
            username=settings.salesforce_username,
            password=settings.salesforce_password,
            security_token=settings.salesforce_security_token
        )
        sf = Salesforce(instance=instance, session_id=session_id)

        logger.info("\n" + "="*70)
        logger.info("Checking Platform Event: NBRS_Calculation__e")
        logger.info("="*70)

        # Try to describe the Platform Event
        try:
            pe_metadata = sf.describe()

            # Look for Platform Event in sobjects
            platform_events = [obj for obj in pe_metadata['sobjects']
                             if obj['name'].endswith('__e')]

            nbrs_event_exists = any(obj['name'] == 'NBRS_Calculation__e'
                                   for obj in platform_events)

            if nbrs_event_exists:
                logger.info("✓ NBRS_Calculation__e Platform Event exists!")

                # Get event fields
                event_desc = sf.NBRS_Calculation__e.describe()
                logger.info(f"\nEvent has {len(event_desc['fields'])} fields:")
                for field in event_desc['fields']:
                    if field['name'].endswith('__c'):
                        logger.info(f"  - {field['name']} ({field['type']})")

                return True
            else:
                logger.warning("✗ NBRS_Calculation__e Platform Event NOT FOUND")
                logger.info("\nTo create Platform Event:")
                logger.info("Setup → Integrations → Platform Events → New Platform Event")
                print_platform_event_guide()
                return False

        except Exception as e:
            logger.warning(f"Could not access Platform Event: {e}")
            logger.info("\nPlatform Event may not exist or user lacks permissions")
            return False

    except Exception as e:
        logger.error(f"Error checking Platform Event: {e}")
        raise


def print_platform_event_guide():
    """Print guide for creating Platform Event"""
    logger.info("\n" + "="*70)
    logger.info("Platform Event Creation Guide")
    logger.info("="*70)
    logger.info("\nEvent Name: NBRS_Calculation")
    logger.info("API Name: NBRS_Calculation__e")
    logger.info("\nFields to create:")

    event_fields = [
        ("Lead_ID__c", "Text", "18", "Salesforce Lead ID"),
        ("Company_Name__c", "Text", "255", "Company name"),
        ("NBRS_Score__c", "Number", "5,2", "Calculated NBRS score"),
        ("NBRS_Tier__c", "Text", "10", "Tier classification"),
        ("Brand_Affinity_Score__c", "Number", "5,2", "Brand affinity score"),
        ("Market_Positioning_Score__c", "Number", "5,2", "Market positioning score"),
        ("Digital_Presence_Score__c", "Number", "5,2", "Digital presence score"),
        ("Priority_Rank__c", "Number", "5,0", "Priority ranking"),
        ("Calculated_At__c", "DateTime", "", "Calculation timestamp")
    ]

    for field_name, field_type, length, description in event_fields:
        logger.info(f"\n  {field_name}")
        logger.info(f"    Type: {field_type}")
        if length:
            logger.info(f"    Length: {length}")
        logger.info(f"    Description: {description}")


def main():
    """Main setup function"""
    logger.info("="*70)
    logger.info("NERDX Warm Lead Generation - Salesforce Setup")
    logger.info("="*70)

    try:
        # Check custom fields
        field_results = create_custom_fields()

        # Check platform event
        platform_event_exists = check_platform_event()

        # Summary
        logger.info("\n" + "="*70)
        logger.info("Setup Summary")
        logger.info("="*70)
        logger.info(f"\nCustom Fields:")
        logger.info(f"  Existing: {len(field_results['existing'])}")
        logger.info(f"  Missing: {len(field_results['missing'])}")

        logger.info(f"\nPlatform Event:")
        logger.info(f"  NBRS_Calculation__e: {'✓ EXISTS' if platform_event_exists else '✗ NOT FOUND'}")

        if field_results['missing'] or not platform_event_exists:
            logger.warning("\n⚠️  Setup incomplete! Manual configuration required.")
            logger.info("\nNext steps:")
            logger.info("1. Create missing custom fields using Salesforce Setup UI")
            if not platform_event_exists:
                logger.info("2. Create NBRS_Calculation__e Platform Event")
            logger.info("3. Create Flow for auto-assignment (see SALESFORCE_SETUP.md)")
            logger.info("4. Re-run this script to verify")
        else:
            logger.info("\n✓ Salesforce setup complete!")
            logger.info("\nNext steps:")
            logger.info("1. Create Flow for auto-assignment (see SALESFORCE_SETUP.md)")
            logger.info("2. Test NBRS calculation with update_salesforce=true")

    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        logger.info("\nPlease check:")
        logger.info("- Salesforce credentials in .env")
        logger.info("- User has API access and appropriate permissions")
        logger.info("- Salesforce instance is accessible")


if __name__ == "__main__":
    main()
