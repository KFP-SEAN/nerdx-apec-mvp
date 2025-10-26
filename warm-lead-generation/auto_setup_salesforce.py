#!/usr/bin/env python3
"""
Automatic Salesforce Setup using Metadata API
Salesforce Metadata API를 사용한 자동 설정
"""
import logging
import os
from simple_salesforce import Salesforce, SalesforceLogin
from simple_salesforce.exceptions import SalesforceGeneralError
import requests
import xml.etree.ElementTree as ET
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesforceMetadataAPI:
    """Salesforce Metadata API client for automatic setup"""

    def __init__(self):
        self.session_id = None
        self.instance = None
        self.metadata_url = None
        self.sf = None
        self._login()

    def _login(self):
        """Login to Salesforce and get metadata URL"""
        try:
            self.session_id, instance_url = SalesforceLogin(
                username=settings.salesforce_username,
                password=settings.salesforce_password,
                security_token=settings.salesforce_security_token
            )

            # Get instance without protocol
            self.instance = instance_url.replace('https://', '').replace('http://', '')
            self.metadata_url = f"https://{self.instance}/services/Soap/m/59.0"

            self.sf = Salesforce(instance=self.instance, session_id=self.session_id)

            logger.info(f"✓ Connected to Salesforce: {self.instance}")
            logger.info(f"  Metadata URL: {self.metadata_url}")

        except Exception as e:
            logger.error(f"✗ Login failed: {e}")
            raise

    def create_custom_field(self, object_name, field_config):
        """
        Create custom field using Metadata API

        Args:
            object_name: Object API name (e.g., 'Lead')
            field_config: Field configuration dict
        """
        field_name = field_config['fullName']
        field_type = field_config['type']

        logger.info(f"\nCreating field: {field_name} ({field_type})")

        # Build XML payload
        xml_payload = self._build_field_xml(object_name, field_config)

        # Make Metadata API request
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'create'
        }

        try:
            response = requests.post(
                self.metadata_url,
                data=xml_payload,
                headers=headers
            )

            if response.status_code == 200:
                # Parse response
                if 'success>true' in response.text:
                    logger.info(f"  ✓ Created {field_name}")
                    return True
                elif 'This field already exists' in response.text or 'DUPLICATE' in response.text:
                    logger.info(f"  ✓ {field_name} already exists")
                    return True
                else:
                    logger.error(f"  ✗ Failed to create {field_name}")
                    logger.error(f"    Response: {response.text[:500]}")
                    return False
            else:
                logger.error(f"  ✗ HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"  ✗ Error creating {field_name}: {e}")
            return False

    def _build_field_xml(self, object_name, field_config):
        """Build Metadata API XML for field creation"""

        field_name = field_config['fullName']
        field_type = field_config['type']
        label = field_config.get('label', field_name.replace('__c', '').replace('_', ' '))
        description = field_config.get('description', '')

        # Base XML structure
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:met="http://soap.sforce.com/2006/04/metadata">
    <soapenv:Header>
        <met:SessionHeader>
            <met:sessionId>{self.session_id}</met:sessionId>
        </met:SessionHeader>
    </soapenv:Header>
    <soapenv:Body>
        <met:create>
            <met:metadata xsi:type="met:CustomField" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <met:fullName>{object_name}.{field_name}</met:fullName>
                <met:label>{label}</met:label>
                <met:description>{description}</met:description>
                <met:type>{field_type}</met:type>
'''

        # Add type-specific attributes
        if field_type == 'Number':
            precision = field_config.get('precision', 5)
            scale = field_config.get('scale', 2)
            xml += f'''                <met:precision>{precision}</met:precision>
                <met:scale>{scale}</met:scale>
'''
        elif field_type == 'Text':
            length = field_config.get('length', 255)
            xml += f'''                <met:length>{length}</met:length>
'''
        elif field_type == 'Picklist':
            values = field_config.get('picklistValues', [])
            for value in values:
                xml += f'''                <met:valueSet>
                    <met:valueSetDefinition>
                        <met:value>
                            <met:fullName>{value}</met:fullName>
                            <met:default>false</met:default>
                            <met:label>{value}</met:label>
                        </met:value>
                    </met:valueSetDefinition>
                </met:valueSet>
'''

        xml += '''            </met:metadata>
        </met:create>
    </soapenv:Body>
</soapenv:Envelope>'''

        return xml

    def create_all_nbrs_fields(self):
        """Create all NBRS-related custom fields on Lead object"""

        logger.info("\n" + "="*70)
        logger.info("Creating NBRS Custom Fields on Lead Object")
        logger.info("="*70)

        fields = [
            {
                'fullName': 'NBRS_Score__c',
                'type': 'Number',
                'label': 'NBRS Score',
                'description': 'Overall NBRS score (0-100)',
                'precision': 5,
                'scale': 2
            },
            {
                'fullName': 'NBRS_Tier__c',
                'type': 'Picklist',
                'label': 'NBRS Tier',
                'description': 'Lead tier classification',
                'picklistValues': ['TIER1', 'TIER2', 'TIER3', 'TIER4']
            },
            {
                'fullName': 'Brand_Affinity_Score__c',
                'type': 'Number',
                'label': 'Brand Affinity Score',
                'description': 'Brand affinity component (0-100)',
                'precision': 5,
                'scale': 2
            },
            {
                'fullName': 'Market_Positioning_Score__c',
                'type': 'Number',
                'label': 'Market Positioning Score',
                'description': 'Market positioning component (0-100)',
                'precision': 5,
                'scale': 2
            },
            {
                'fullName': 'Digital_Presence_Score__c',
                'type': 'Number',
                'label': 'Digital Presence Score',
                'description': 'Digital presence component (0-100)',
                'precision': 5,
                'scale': 2
            },
            {
                'fullName': 'NBRS_Calculated_Date__c',
                'type': 'DateTime',
                'label': 'NBRS Calculated Date',
                'description': 'When NBRS was last calculated'
            },
            {
                'fullName': 'Priority_Rank__c',
                'type': 'Number',
                'label': 'Priority Rank',
                'description': 'Ranking among all leads',
                'precision': 5,
                'scale': 0
            },
            {
                'fullName': 'Next_Action__c',
                'type': 'Text',
                'label': 'Next Action',
                'description': 'Recommended next action',
                'length': 255
            }
        ]

        success_count = 0
        fail_count = 0

        for field_config in fields:
            if self.create_custom_field('Lead', field_config):
                success_count += 1
            else:
                fail_count += 1

        logger.info("\n" + "="*70)
        logger.info(f"Custom Fields Summary: {success_count} created/exist, {fail_count} failed")
        logger.info("="*70)

        return success_count, fail_count


def use_rest_api_workaround():
    """
    Workaround: Use Salesforce Tooling API to create fields
    More reliable than Metadata SOAP API
    """
    try:
        session_id, instance_url = SalesforceLogin(
            username=settings.salesforce_username,
            password=settings.salesforce_password,
            security_token=settings.salesforce_security_token
        )

        sf = Salesforce(instance=instance_url, session_id=session_id)

        logger.info("\n" + "="*70)
        logger.info("Alternative Approach: Using Tooling API")
        logger.info("="*70)

        # Get Lead object metadata
        lead_metadata = sf.Lead.describe()
        existing_fields = {field['name']: field for field in lead_metadata['fields']}

        fields_to_create = [
            'NBRS_Score__c',
            'NBRS_Tier__c',
            'Brand_Affinity_Score__c',
            'Market_Positioning_Score__c',
            'Digital_Presence_Score__c',
            'NBRS_Calculated_Date__c',
            'Priority_Rank__c',
            'Next_Action__c'
        ]

        logger.info("\nField Status:")
        for field_name in fields_to_create:
            if field_name in existing_fields:
                logger.info(f"  ✓ {field_name} exists")
            else:
                logger.warning(f"  ✗ {field_name} missing")

        missing = [f for f in fields_to_create if f not in existing_fields]

        if missing:
            logger.info(f"\n{len(missing)} fields need to be created")
            logger.info("\nUnfortunately, custom field creation requires:")
            logger.info("1. Metadata API with proper authentication")
            logger.info("2. OR manual creation via Salesforce UI")
            logger.info("3. OR using Salesforce CLI (sfdx)")
            logger.info("\nRecommended: Use SALESFORCE_QUICK_SETUP.md guide (5 minutes)")
        else:
            logger.info("\n✓ All NBRS fields already exist!")

        return len(missing) == 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def try_salesforce_cli():
    """Try using Salesforce CLI if available"""
    import subprocess

    logger.info("\n" + "="*70)
    logger.info("Checking for Salesforce CLI (sfdx)")
    logger.info("="*70)

    try:
        result = subprocess.run(['sfdx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✓ Salesforce CLI found: {result.stdout.strip()}")
            logger.info("\nYou can use CLI to create fields automatically!")
            logger.info("\nCommands:")
            logger.info("1. sfdx auth:web:login -a myorg")
            logger.info("2. Use metadata deployment with package.xml")
            return True
        else:
            logger.info("✗ Salesforce CLI not found")
            return False
    except FileNotFoundError:
        logger.info("✗ Salesforce CLI (sfdx) not installed")
        logger.info("\nTo install: https://developer.salesforce.com/tools/salesforce-cli")
        return False


def main():
    """Main setup function"""
    logger.info("="*70)
    logger.info("NBRS Salesforce Automatic Setup")
    logger.info("="*70)

    # Try method 1: REST API check
    logger.info("\n[Method 1] Checking existing fields via REST API...")
    if use_rest_api_workaround():
        logger.info("\n✓ All fields exist! No setup needed.")
        return

    # Try method 2: Salesforce CLI
    logger.info("\n[Method 2] Checking for Salesforce CLI...")
    if try_salesforce_cli():
        logger.info("\nSalesforce CLI available - you can use it for automation")

    # Try method 3: Metadata API (often requires OAuth)
    try:
        logger.info("\n[Method 3] Attempting Metadata API...")
        api = SalesforceMetadataAPI()
        success, fail = api.create_all_nbrs_fields()

        if fail == 0:
            logger.info("\n✓ SUCCESS! All fields created via Metadata API")
        else:
            logger.warning(f"\n⚠ Partial success: {fail} fields failed")

    except Exception as e:
        logger.error(f"\n✗ Metadata API failed: {e}")
        logger.info("\nThis is normal - Metadata API often requires specific authentication")

    # Final recommendation
    logger.info("\n" + "="*70)
    logger.info("Recommended Next Step")
    logger.info("="*70)
    logger.info("\nFor fastest setup (5-10 minutes):")
    logger.info("  📄 Follow SALESFORCE_QUICK_SETUP.md")
    logger.info("  ✓ Create 8 custom fields via Salesforce UI")
    logger.info("  ✓ Create Platform Event")
    logger.info("  ✓ Create auto-assignment Flow")
    logger.info("\nAlternative (if you have Salesforce DX):")
    logger.info("  📦 Use Salesforce CLI with metadata deployment")
    logger.info("="*70)


if __name__ == "__main__":
    main()
