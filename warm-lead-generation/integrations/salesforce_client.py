"""
Salesforce Integration Client
Salesforce 플랫폼 이벤트 연동 및 리드 관리
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from simple_salesforce import Salesforce, SalesforceLogin

from config import settings
from models.nbrs_models import NBRSResult, LeadTier

logger = logging.getLogger(__name__)


class SalesforceClient:
    """Salesforce API client for lead management and Platform Events"""

    def __init__(self):
        self.instance_url = settings.salesforce_instance_url
        self.username = settings.salesforce_username
        self.password = settings.salesforce_password
        self.security_token = settings.salesforce_security_token
        self.consumer_key = settings.salesforce_consumer_key
        self.consumer_secret = settings.salesforce_consumer_secret
        self._sf_client: Optional[Salesforce] = None

    def _get_client(self) -> Salesforce:
        """Get or create Salesforce client"""
        if self._sf_client is None:
            try:
                session_id, instance = SalesforceLogin(
                    username=self.username,
                    password=self.password,
                    security_token=self.security_token
                )
                self._sf_client = Salesforce(instance=instance, session_id=session_id)
                logger.info(f"[Salesforce] Connected to {instance}")
            except Exception as e:
                logger.error(f"[Salesforce] Login failed: {e}")
                raise

        return self._sf_client

    def fetch_leads(
        self,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads from Salesforce

        Args:
            status: Lead status filter (e.g., "Open", "Qualified")
            limit: Maximum number of leads to fetch

        Returns:
            List of lead records
        """
        try:
            sf = self._get_client()

            # Build SOQL query
            query = f"""
                SELECT Id, Company, Name, Email, Phone, Status, Industry,
                       AnnualRevenue, NumberOfEmployees, Website,
                       Description, LeadSource, CreatedDate, LastModifiedDate
                FROM Lead
            """

            if status:
                query += f" WHERE Status = '{status}'"

            query += f" LIMIT {limit}"

            result = sf.query(query)
            leads = result.get("records", [])

            logger.info(f"[Salesforce] Fetched {len(leads)} leads")

            return leads

        except Exception as e:
            logger.error(f"[Salesforce] Failed to fetch leads: {e}")
            return []

    def update_lead_nbrs(
        self,
        lead_id: str,
        nbrs_result: NBRSResult
    ) -> bool:
        """
        Update lead with NBRS score and tier

        Args:
            lead_id: Salesforce Lead ID
            nbrs_result: NBRS calculation result

        Returns:
            True if successful
        """
        try:
            sf = self._get_client()

            # Update lead record with NBRS fields
            update_data = {
                "NBRS_Score__c": nbrs_result.nbrs_score,
                "NBRS_Tier__c": nbrs_result.tier.value.upper(),
                "Brand_Affinity_Score__c": nbrs_result.brand_affinity_score,
                "Market_Positioning_Score__c": nbrs_result.market_positioning_score,
                "Digital_Presence_Score__c": nbrs_result.digital_presence_score,
                "NBRS_Calculated_Date__c": nbrs_result.calculated_at.isoformat(),
                "Priority_Rank__c": nbrs_result.priority_rank,
                "Next_Action__c": nbrs_result.next_action
            }

            sf.Lead.update(lead_id, update_data)

            logger.info(
                f"[Salesforce] Updated Lead {lead_id} with NBRS={nbrs_result.nbrs_score}, "
                f"Tier={nbrs_result.tier.value}"
            )

            return True

        except Exception as e:
            logger.error(f"[Salesforce] Failed to update Lead {lead_id}: {e}")
            return False

    def publish_platform_event(
        self,
        event_name: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """
        Publish Salesforce Platform Event

        Args:
            event_name: Platform Event API name (e.g., "NBRS_Calculation__e")
            event_data: Event payload

        Returns:
            True if successful
        """
        try:
            sf = self._get_client()

            # Publish platform event
            result = sf.sobjects.PlatformEvent.create({
                "EventType": event_name,
                **event_data
            })

            if result.get("success"):
                logger.info(f"[Salesforce] Published Platform Event: {event_name}")
                return True
            else:
                logger.error(f"[Salesforce] Failed to publish event: {result}")
                return False

        except Exception as e:
            logger.error(f"[Salesforce] Platform Event error: {e}")
            return False

    def publish_nbrs_calculated_event(
        self,
        nbrs_result: NBRSResult
    ) -> bool:
        """
        Publish NBRS Calculated Platform Event

        This event triggers automation in Salesforce (e.g., assignment rules)

        Args:
            nbrs_result: NBRS calculation result

        Returns:
            True if successful
        """
        event_data = {
            "Lead_ID__c": nbrs_result.lead_id,
            "Company_Name__c": nbrs_result.company_name,
            "NBRS_Score__c": nbrs_result.nbrs_score,
            "NBRS_Tier__c": nbrs_result.tier.value.upper(),
            "Brand_Affinity_Score__c": nbrs_result.brand_affinity_score,
            "Market_Positioning_Score__c": nbrs_result.market_positioning_score,
            "Digital_Presence_Score__c": nbrs_result.digital_presence_score,
            "Priority_Rank__c": nbrs_result.priority_rank,
            "Calculated_At__c": nbrs_result.calculated_at.isoformat()
        }

        return self.publish_platform_event("NBRS_Calculation__e", event_data)

    def bulk_update_leads(
        self,
        nbrs_results: List[NBRSResult]
    ) -> Dict[str, int]:
        """
        Bulk update leads with NBRS scores

        Args:
            nbrs_results: List of NBRS results

        Returns:
            Summary of successes and failures
        """
        success_count = 0
        failure_count = 0

        for result in nbrs_results:
            if self.update_lead_nbrs(result.lead_id, result):
                success_count += 1
            else:
                failure_count += 1

        logger.info(
            f"[Salesforce] Bulk update completed: "
            f"{success_count} success, {failure_count} failures"
        )

        return {
            "total": len(nbrs_results),
            "success": success_count,
            "failures": failure_count
        }

    def get_lead_activities(
        self,
        lead_id: str
    ) -> Dict[str, Any]:
        """
        Fetch lead activity history for NBRS calculation

        Args:
            lead_id: Salesforce Lead ID

        Returns:
            Activity summary
        """
        try:
            sf = self._get_client()

            # Fetch tasks
            tasks_query = f"""
                SELECT Id, Subject, Status, CreatedDate
                FROM Task
                WHERE WhoId = '{lead_id}'
                ORDER BY CreatedDate DESC
                LIMIT 100
            """
            tasks = sf.query(tasks_query).get("records", [])

            # Fetch events (meetings)
            events_query = f"""
                SELECT Id, Subject, StartDateTime, EndDateTime
                FROM Event
                WHERE WhoId = '{lead_id}'
                ORDER BY StartDateTime DESC
                LIMIT 100
            """
            events = sf.query(events_query).get("records", [])

            # Fetch email messages
            emails_query = f"""
                SELECT Id, Subject, CreatedDate, Status
                FROM EmailMessage
                WHERE RelatedToId = '{lead_id}'
                ORDER BY CreatedDate DESC
                LIMIT 100
            """
            emails = sf.query(emails_query).get("records", [])

            return {
                "tasks": tasks,
                "events": events,
                "emails": emails,
                "total_activities": len(tasks) + len(events) + len(emails)
            }

        except Exception as e:
            logger.error(f"[Salesforce] Failed to fetch activities for {lead_id}: {e}")
            return {
                "tasks": [],
                "events": [],
                "emails": [],
                "total_activities": 0
            }


# Singleton instance
salesforce_client = SalesforceClient()
