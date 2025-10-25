"""
Financial Tracking Service
재무 추적 핵심 서비스
"""
import logging
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from uuid import uuid4
from decimal import Decimal

from database import (
    RevenueRecordDB, CostRecordDB, DailyFinancialSummaryDB, CellDB
)
from models.financial_models import (
    RevenueRecord, CostRecord, DailyFinancialSummary, MonthlyFinancialSummary
)
from services.integrations.salesforce_service import salesforce_service
from services.integrations.odoo_service import odoo_service

logger = logging.getLogger(__name__)


class FinancialService:
    """Financial tracking and reporting service"""

    async def sync_cell_revenue(
        self,
        db: Session,
        cell_id: str,
        target_date: date
    ) -> int:
        """
        Sync revenue from Salesforce for a cell

        Args:
            db: Database session
            cell_id: Cell ID
            target_date: Date to sync

        Returns:
            Number of revenue records synced
        """
        try:
            # Get cell info
            cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()
            if not cell or not cell.salesforce_account_ids:
                logger.warning(f"Cell {cell_id} not found or has no Salesforce accounts")
                return 0

            # Get revenue from Salesforce
            revenue_records = await salesforce_service.get_daily_revenue(
                account_ids=cell.salesforce_account_ids,
                target_date=target_date
            )

            # Save to database
            count = 0
            for record in revenue_records:
                record_id = f"rev-{uuid4().hex[:12]}"

                db_record = RevenueRecordDB(
                    record_id=record_id,
                    cell_id=cell_id,
                    salesforce_opportunity_id=record['salesforce_opportunity_id'],
                    salesforce_account_id=record['salesforce_account_id'],
                    revenue_date=record['revenue_date'],
                    revenue_amount=record['revenue_amount'],
                    product_name=record.get('product_name'),
                    quantity=record.get('quantity'),
                    unit_price=record.get('unit_price'),
                    description=record.get('description')
                )

                db.add(db_record)
                count += 1

            db.commit()
            logger.info(f"Synced {count} revenue records for cell {cell_id} on {target_date}")

            return count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to sync revenue for cell {cell_id}: {e}")
            raise

    async def sync_cell_costs(
        self,
        db: Session,
        cell_id: str,
        target_date: date
    ) -> int:
        """
        Sync costs from Odoo for a cell

        Args:
            db: Database session
            cell_id: Cell ID
            target_date: Date to sync

        Returns:
            Number of cost records synced
        """
        try:
            # Get cell info
            cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()
            if not cell or not cell.odoo_analytic_account_id:
                logger.warning(f"Cell {cell_id} not found or has no Odoo account")
                return 0

            # Get costs from Odoo
            cost_records = await odoo_service.get_daily_costs(
                analytic_account_id=cell.odoo_analytic_account_id,
                target_date=target_date
            )

            # Save to database
            count = 0
            for record in cost_records:
                record_id = f"cost-{uuid4().hex[:12]}"

                db_record = CostRecordDB(
                    record_id=record_id,
                    cell_id=cell_id,
                    odoo_invoice_id=record.get('odoo_invoice_id'),
                    odoo_invoice_line_id=record['odoo_invoice_line_id'],
                    cost_date=record['cost_date'],
                    cost_amount=record['cost_amount'],
                    cost_category=record['cost_category'],
                    related_product=record.get('related_product'),
                    description=record.get('description')
                )

                db.add(db_record)
                count += 1

            db.commit()
            logger.info(f"Synced {count} cost records for cell {cell_id} on {target_date}")

            return count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to sync costs for cell {cell_id}: {e}")
            raise

    async def calculate_daily_summary(
        self,
        db: Session,
        cell_id: str,
        summary_date: date
    ) -> DailyFinancialSummary:
        """
        Calculate daily financial summary for a cell

        Args:
            db: Database session
            cell_id: Cell ID
            summary_date: Summary date

        Returns:
            Daily financial summary
        """
        try:
            # Get revenue total
            revenue_result = db.query(
                func.sum(RevenueRecordDB.revenue_amount).label('total'),
                func.count(RevenueRecordDB.record_id).label('count')
            ).filter(
                and_(
                    RevenueRecordDB.cell_id == cell_id,
                    RevenueRecordDB.revenue_date == summary_date
                )
            ).first()

            total_revenue = Decimal(str(revenue_result.total or 0))
            revenue_count = revenue_result.count or 0

            # Get cost total (COGS)
            cost_result = db.query(
                func.sum(CostRecordDB.cost_amount).label('total'),
                func.count(CostRecordDB.record_id).label('count')
            ).filter(
                and_(
                    CostRecordDB.cell_id == cell_id,
                    CostRecordDB.cost_date == summary_date,
                    CostRecordDB.cost_category == 'COGS'
                )
            ).first()

            total_cogs = Decimal(str(cost_result.total or 0))
            cogs_count = cost_result.count or 0

            # Calculate gross profit
            gross_profit = total_revenue - total_cogs
            gross_profit_margin = float(gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

            # Create or update summary
            db_summary = db.query(DailyFinancialSummaryDB).filter(
                and_(
                    DailyFinancialSummaryDB.cell_id == cell_id,
                    DailyFinancialSummaryDB.summary_date == summary_date
                )
            ).first()

            if db_summary:
                # Update existing
                db_summary.total_revenue = total_revenue
                db_summary.revenue_count = revenue_count
                db_summary.total_cogs = total_cogs
                db_summary.cogs_count = cogs_count
                db_summary.gross_profit = gross_profit
                db_summary.gross_profit_margin = gross_profit_margin
                db_summary.generated_at = datetime.utcnow()
            else:
                # Create new
                db_summary = DailyFinancialSummaryDB(
                    cell_id=cell_id,
                    summary_date=summary_date,
                    total_revenue=total_revenue,
                    revenue_count=revenue_count,
                    total_cogs=total_cogs,
                    cogs_count=cogs_count,
                    gross_profit=gross_profit,
                    gross_profit_margin=gross_profit_margin
                )
                db.add(db_summary)

            db.commit()
            db.refresh(db_summary)

            logger.info(f"Calculated daily summary for cell {cell_id} on {summary_date}")

            # Convert to Pydantic model
            return DailyFinancialSummary(
                cell_id=db_summary.cell_id,
                summary_date=db_summary.summary_date,
                total_revenue=db_summary.total_revenue,
                revenue_count=db_summary.revenue_count,
                total_cogs=db_summary.total_cogs,
                cogs_count=db_summary.cogs_count,
                gross_profit=db_summary.gross_profit,
                gross_profit_margin=db_summary.gross_profit_margin,
                generated_at=db_summary.generated_at
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to calculate daily summary: {e}")
            raise

    async def get_monthly_summary(
        self,
        db: Session,
        cell_id: str,
        year: int,
        month: int
    ) -> MonthlyFinancialSummary:
        """
        Calculate monthly financial summary (MTD)

        Args:
            db: Database session
            cell_id: Cell ID
            year: Year
            month: Month

        Returns:
            Monthly financial summary
        """
        try:
            # Get cell info for targets
            cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()

            # Calculate date range
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)

            # Aggregate daily summaries
            summaries = db.query(
                func.sum(DailyFinancialSummaryDB.total_revenue).label('total_revenue'),
                func.sum(DailyFinancialSummaryDB.total_cogs).label('total_cogs'),
                func.count(DailyFinancialSummaryDB.id).label('days_count')
            ).filter(
                and_(
                    DailyFinancialSummaryDB.cell_id == cell_id,
                    DailyFinancialSummaryDB.summary_date >= start_date,
                    DailyFinancialSummaryDB.summary_date <= end_date
                )
            ).first()

            total_revenue = Decimal(str(summaries.total_revenue or 0))
            total_cogs = Decimal(str(summaries.total_cogs or 0))
            gross_profit = total_revenue - total_cogs
            gross_profit_margin = float(gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

            # Calculate achievement rates
            revenue_achievement_rate = None
            if cell and cell.monthly_revenue_target:
                revenue_achievement_rate = float(total_revenue / Decimal(str(cell.monthly_revenue_target)) * 100)

            profit_achievement_rate = None
            if cell and cell.monthly_gross_profit_target:
                profit_achievement_rate = float(gross_profit / Decimal(str(cell.monthly_gross_profit_target)) * 100)

            return MonthlyFinancialSummary(
                cell_id=cell_id,
                year=year,
                month=month,
                total_revenue=total_revenue,
                total_cogs=total_cogs,
                gross_profit=gross_profit,
                gross_profit_margin=gross_profit_margin,
                revenue_target=Decimal(str(cell.monthly_revenue_target)) if cell and cell.monthly_revenue_target else None,
                revenue_achievement_rate=revenue_achievement_rate,
                gross_profit_target=Decimal(str(cell.monthly_gross_profit_target)) if cell and cell.monthly_gross_profit_target else None,
                gross_profit_achievement_rate=profit_achievement_rate
            )

        except Exception as e:
            logger.error(f"Failed to calculate monthly summary: {e}")
            raise


# Singleton instance
financial_service = FinancialService()
