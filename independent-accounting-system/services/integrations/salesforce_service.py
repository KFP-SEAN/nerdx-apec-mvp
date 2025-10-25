"""
Salesforce CRM Integration Service
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from simple_salesforce import Salesforce, SalesforceLogin
from config import settings

logger = logging.getLogger(__name__)


class SalesforceService:
    """Salesforce CRM integration for revenue data"""

    def __init__(self):
        self.sf: Optional[Salesforce] = None
        self._session_id: Optional[str] = None
        self._instance: Optional[str] = None

    async def connect(self):
        """Connect to Salesforce"""
        try:
            # Login to Salesforce
            session_id, instance = SalesforceLogin(
                username=settings.salesforce_username,
                password=settings.salesforce_password,
                security_token=settings.salesforce_security_token
            )

            self._session_id = session_id
            self._instance = instance

            # Create Salesforce instance
            self.sf = Salesforce(
                instance=instance,
                session_id=session_id
            )

            logger.info(f"Connected to Salesforce instance: {instance}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            raise

    async def get_opportunities_by_account(
        self,
        account_ids: List[str],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get opportunities (deals) by Salesforce account IDs

        Args:
            account_ids: List of Salesforce account IDs
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of opportunity records
        """
        if not self.sf:
            await self.connect()

        try:
            # Build SOQL query
            account_ids_str = "','".join(account_ids)
            query = f"""
                SELECT Id, Name, AccountId, Amount, CloseDate, StageName,
                       Probability, Type, Product__c, Quantity__c, UnitPrice__c
                FROM Opportunity
                WHERE AccountId IN ('{account_ids_str}')
                AND CloseDate >= {start_date.isoformat()}
                AND CloseDate <= {end_date.isoformat()}
                AND StageName = 'Closed Won'
                ORDER BY CloseDate DESC
            """

            # Execute query
            result = self.sf.query_all(query)
            opportunities = result['records']

            logger.info(f"Retrieved {len(opportunities)} opportunities from Salesforce")
            return opportunities

        except Exception as e:
            logger.error(f"Failed to query Salesforce opportunities: {e}")
            raise

    async def get_daily_revenue(
        self,
        account_ids: List[str],
        target_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get daily revenue (closed opportunities) for specific accounts

        Args:
            account_ids: List of Salesforce account IDs
            target_date: Target date

        Returns:
            List of revenue records
        """
        opportunities = await self.get_opportunities_by_account(
            account_ids=account_ids,
            start_date=target_date,
            end_date=target_date
        )

        revenue_records = []
        for opp in opportunities:
            record = {
                'salesforce_opportunity_id': opp['Id'],
                'salesforce_account_id': opp['AccountId'],
                'revenue_date': datetime.strptime(opp['CloseDate'], '%Y-%m-%d').date(),
                'revenue_amount': opp.get('Amount', 0),
                'product_name': opp.get('Product__c'),
                'quantity': opp.get('Quantity__c'),
                'unit_price': opp.get('UnitPrice__c'),
                'description': opp.get('Name')
            }
            revenue_records.append(record)

        return revenue_records

    async def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Get Salesforce account information"""
        if not self.sf:
            await self.connect()

        try:
            account = self.sf.Account.get(account_id)
            return account

        except Exception as e:
            logger.error(f"Failed to get account {account_id}: {e}")
            raise

    async def health_check(self) -> bool:
        """Check Salesforce connection health"""
        try:
            if not self.sf:
                await self.connect()

            # Simple query to test connection
            result = self.sf.query("SELECT Id FROM Account LIMIT 1")
            return True

        except Exception as e:
            logger.error(f"Salesforce health check failed: {e}")
            return False


# Singleton instance
salesforce_service = SalesforceService()
