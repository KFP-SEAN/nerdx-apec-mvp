"""
Odoo ERP Integration Service
"""
import logging
import xmlrpc.client
from typing import List, Dict, Optional, Any
from datetime import date
from decimal import Decimal
from config import settings

logger = logging.getLogger(__name__)


class OdooService:
    """Odoo ERP integration for cost data and analytic accounts"""

    def __init__(self):
        self.url = settings.odoo_url
        self.db = settings.odoo_db
        self.username = settings.odoo_username
        self.password = settings.odoo_password

        self.uid: Optional[int] = None
        self.common: Optional[xmlrpc.client.ServerProxy] = None
        self.models: Optional[xmlrpc.client.ServerProxy] = None

    async def connect(self):
        """Connect to Odoo via XML-RPC"""
        try:
            # Connect to common endpoint
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Authenticate
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.password,
                {}
            )

            if not self.uid:
                raise Exception("Odoo authentication failed")

            # Connect to object endpoint
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            logger.info(f"Connected to Odoo as user ID: {self.uid}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise

    def _execute_kw(self, model: str, method: str, args: list, kwargs: dict = None):
        """Execute Odoo model method"""
        if kwargs is None:
            kwargs = {}

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs
        )

    async def create_analytic_account(
        self,
        name: str,
        code: str,
        partner_id: Optional[int] = None
    ) -> int:
        """
        Create analytic account for cell

        Args:
            name: Account name (e.g., "국내셀")
            code: Account code (e.g., "CELL-DOM-001")
            partner_id: Related partner/customer ID

        Returns:
            Analytic account ID
        """
        if not self.uid:
            await self.connect()

        try:
            account_id = self._execute_kw(
                'account.analytic.account',
                'create',
                [{
                    'name': name,
                    'code': code,
                    'partner_id': partner_id,
                    'active': True
                }]
            )

            logger.info(f"Created analytic account: {name} (ID: {account_id})")
            return account_id

        except Exception as e:
            logger.error(f"Failed to create analytic account: {e}")
            raise

    async def get_invoices_by_analytic_account(
        self,
        analytic_account_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get vendor bills (invoices) by analytic account for COGS

        Args:
            analytic_account_id: Odoo analytic account ID
            start_date: Start date
            end_date: End date

        Returns:
            List of invoice records
        """
        if not self.uid:
            await self.connect()

        try:
            # Search for invoice lines with analytic account
            invoice_line_ids = self._execute_kw(
                'account.move.line',
                'search',
                [[
                    ('analytic_account_id', '=', analytic_account_id),
                    ('move_id.invoice_date', '>=', start_date.isoformat()),
                    ('move_id.invoice_date', '<=', end_date.isoformat()),
                    ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),  # Vendor bills
                    ('move_id.state', '=', 'posted')  # Posted invoices only
                ]]
            )

            # Read invoice line details
            invoice_lines = self._execute_kw(
                'account.move.line',
                'read',
                [invoice_line_ids],
                {
                    'fields': [
                        'id', 'move_id', 'analytic_account_id', 'product_id',
                        'name', 'quantity', 'price_unit', 'price_subtotal',
                        'account_id', 'tax_ids'
                    ]
                }
            )

            logger.info(f"Retrieved {len(invoice_lines)} invoice lines from Odoo")
            return invoice_lines

        except Exception as e:
            logger.error(f"Failed to query Odoo invoices: {e}")
            raise

    async def get_daily_costs(
        self,
        analytic_account_id: int,
        target_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get daily costs (COGS) for specific analytic account

        Args:
            analytic_account_id: Odoo analytic account ID
            target_date: Target date

        Returns:
            List of cost records
        """
        invoice_lines = await self.get_invoices_by_analytic_account(
            analytic_account_id=analytic_account_id,
            start_date=target_date,
            end_date=target_date
        )

        cost_records = []
        for line in invoice_lines:
            record = {
                'odoo_invoice_line_id': line['id'],
                'odoo_invoice_id': line['move_id'][0] if line.get('move_id') else None,
                'cost_date': target_date,
                'cost_amount': Decimal(str(line.get('price_subtotal', 0))),
                'cost_category': 'COGS',  # Cost of Goods Sold
                'related_product': line.get('product_id', [None, ''])[1] if line.get('product_id') else None,
                'description': line.get('name', '')
            }
            cost_records.append(record)

        return cost_records

    async def get_analytic_account(self, account_id: int) -> Dict[str, Any]:
        """Get analytic account information"""
        if not self.uid:
            await self.connect()

        try:
            account = self._execute_kw(
                'account.analytic.account',
                'read',
                [[account_id]],
                {'fields': ['id', 'name', 'code', 'partner_id', 'active']}
            )

            return account[0] if account else None

        except Exception as e:
            logger.error(f"Failed to get analytic account {account_id}: {e}")
            raise

    async def health_check(self) -> bool:
        """Check Odoo connection health"""
        try:
            if not self.uid:
                await self.connect()

            # Test connection with version query
            version = self.common.version()
            logger.info(f"Odoo version: {version}")
            return True

        except Exception as e:
            logger.error(f"Odoo health check failed: {e}")
            return False


# Singleton instance
odoo_service = OdooService()
