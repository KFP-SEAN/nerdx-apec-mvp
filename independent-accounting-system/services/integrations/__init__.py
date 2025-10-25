"""Integration services for external systems"""
from services.integrations.salesforce_service import salesforce_service
from services.integrations.odoo_service import odoo_service

__all__ = ["salesforce_service", "odoo_service"]
