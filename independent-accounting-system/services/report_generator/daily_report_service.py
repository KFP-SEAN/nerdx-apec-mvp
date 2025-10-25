"""
Daily Report Generation Service
일간 리포트 자동생성 서비스
"""
import logging
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from decimal import Decimal

from database import (
    CellDB, DailyFinancialSummaryDB, RevenueRecordDB, CostRecordDB,
    ReportScheduleDB, ReportGenerationLogDB
)
from models.report_models import (
    DailyReportData, DailyReportEmail, ReportSchedule
)
from services.financial_tracker.financial_service import financial_service
from services.email_sender.email_service import email_service

logger = logging.getLogger(__name__)


class DailyReportService:
    """Daily report generation and delivery service"""

    async def generate_report_data(
        self,
        db: Session,
        cell_id: str,
        report_date: date
    ) -> DailyReportData:
        """
        Generate daily report data for a cell

        Args:
            db: Database session
            cell_id: Cell ID
            report_date: Report date

        Returns:
            Daily report data
        """
        try:
            # Get cell info
            cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()
            if not cell:
                raise ValueError(f"Cell {cell_id} not found")

            # Get daily summary
            daily_summary = db.query(DailyFinancialSummaryDB).filter(
                and_(
                    DailyFinancialSummaryDB.cell_id == cell_id,
                    DailyFinancialSummaryDB.summary_date == report_date
                )
            ).first()

            if not daily_summary:
                # Calculate if not exists
                daily_summary_model = await financial_service.calculate_daily_summary(
                    db, cell_id, report_date
                )
                daily_revenue = daily_summary_model.total_revenue
                revenue_count = daily_summary_model.revenue_count
                daily_cogs = daily_summary_model.total_cogs
                cogs_count = daily_summary_model.cogs_count
                gross_profit = daily_summary_model.gross_profit
                gross_profit_margin = daily_summary_model.gross_profit_margin
            else:
                daily_revenue = daily_summary.total_revenue
                revenue_count = daily_summary.revenue_count
                daily_cogs = daily_summary.total_cogs
                cogs_count = daily_summary.cogs_count
                gross_profit = daily_summary.gross_profit
                gross_profit_margin = daily_summary.gross_profit_margin

            # Get top revenue items
            top_revenue_items = await self._get_top_revenue_items(db, cell_id, report_date, limit=5)

            # Get major cost items
            major_cost_items = await self._get_major_cost_items(db, cell_id, report_date, limit=5)

            # Get MTD (Month-To-Date) summary
            mtd_summary = await financial_service.get_monthly_summary(
                db, cell_id, report_date.year, report_date.month
            )

            # Get previous day data for comparison
            prev_date = report_date - timedelta(days=1)
            prev_day_summary = db.query(DailyFinancialSummaryDB).filter(
                and_(
                    DailyFinancialSummaryDB.cell_id == cell_id,
                    DailyFinancialSummaryDB.summary_date == prev_date
                )
            ).first()

            prev_day_revenue = prev_day_summary.total_revenue if prev_day_summary else None
            prev_day_profit = prev_day_summary.gross_profit if prev_day_summary else None

            revenue_change_rate = None
            profit_change_rate = None

            if prev_day_revenue and prev_day_revenue > 0:
                revenue_change_rate = float((daily_revenue - prev_day_revenue) / prev_day_revenue * 100)

            if prev_day_profit and prev_day_profit > 0:
                profit_change_rate = float((gross_profit - prev_day_profit) / prev_day_profit * 100)

            # Calculate target achievement
            revenue_achievement_rate = None
            profit_achievement_rate = None

            if cell.monthly_revenue_target and mtd_summary.total_revenue:
                revenue_achievement_rate = float(
                    mtd_summary.total_revenue / Decimal(str(cell.monthly_revenue_target)) * 100
                )

            if cell.monthly_gross_profit_target and mtd_summary.gross_profit:
                profit_achievement_rate = float(
                    mtd_summary.gross_profit / Decimal(str(cell.monthly_gross_profit_target)) * 100
                )

            # Build report data
            report_data = DailyReportData(
                cell_id=cell_id,
                cell_name=cell.cell_name,
                report_date=report_date,

                # Daily data
                daily_revenue=daily_revenue,
                revenue_count=revenue_count,
                top_revenue_items=top_revenue_items,
                daily_cogs=daily_cogs,
                cogs_count=cogs_count,
                major_cost_items=major_cost_items,
                gross_profit=gross_profit,
                gross_profit_margin=gross_profit_margin,

                # MTD data
                mtd_revenue=mtd_summary.total_revenue,
                mtd_cogs=mtd_summary.total_cogs,
                mtd_gross_profit=mtd_summary.gross_profit,
                mtd_gross_profit_margin=mtd_summary.gross_profit_margin,

                # Target comparison
                monthly_revenue_target=Decimal(str(cell.monthly_revenue_target)) if cell.monthly_revenue_target else None,
                revenue_achievement_rate=revenue_achievement_rate,
                monthly_profit_target=Decimal(str(cell.monthly_gross_profit_target)) if cell.monthly_gross_profit_target else None,
                profit_achievement_rate=profit_achievement_rate,

                # Previous day comparison
                prev_day_revenue=prev_day_revenue,
                revenue_change_rate=revenue_change_rate,
                prev_day_profit=prev_day_profit,
                profit_change_rate=profit_change_rate
            )

            logger.info(f"Generated report data for cell {cell_id} on {report_date}")
            return report_data

        except Exception as e:
            logger.error(f"Failed to generate report data: {e}")
            raise

    async def _get_top_revenue_items(
        self,
        db: Session,
        cell_id: str,
        target_date: date,
        limit: int = 5
    ) -> List[Dict]:
        """Get top revenue items for the day"""
        records = db.query(RevenueRecordDB).filter(
            and_(
                RevenueRecordDB.cell_id == cell_id,
                RevenueRecordDB.revenue_date == target_date
            )
        ).order_by(desc(RevenueRecordDB.revenue_amount)).limit(limit).all()

        return [
            {
                'product_name': r.product_name or 'N/A',
                'revenue_amount': float(r.revenue_amount),
                'quantity': r.quantity,
                'description': r.description
            }
            for r in records
        ]

    async def _get_major_cost_items(
        self,
        db: Session,
        cell_id: str,
        target_date: date,
        limit: int = 5
    ) -> List[Dict]:
        """Get major cost items for the day"""
        records = db.query(CostRecordDB).filter(
            and_(
                CostRecordDB.cell_id == cell_id,
                CostRecordDB.cost_date == target_date
            )
        ).order_by(desc(CostRecordDB.cost_amount)).limit(limit).all()

        return [
            {
                'cost_category': r.cost_category,
                'cost_amount': float(r.cost_amount),
                'related_product': r.related_product or 'N/A',
                'description': r.description
            }
            for r in records
        ]

    async def generate_and_send_report(
        self,
        db: Session,
        cell_id: str,
        report_date: date
    ) -> bool:
        """
        Generate and send daily report via email

        Args:
            db: Database session
            cell_id: Cell ID
            report_date: Report date

        Returns:
            True if successful
        """
        execution_start = datetime.utcnow()

        try:
            # Generate report data
            report_data = await self.generate_report_data(db, cell_id, report_date)

            # Get cell manager email
            cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()

            # Generate HTML report
            html_body = await self._generate_html_report(report_data)

            # Create email
            email_data = DailyReportEmail(
                recipient_email=cell.manager_email,
                recipient_name=cell.manager_name,
                subject=f"[{cell.cell_name}] 일간 리포트 - {report_date.strftime('%Y-%m-%d')}",
                html_body=html_body,
                report_data=report_data
            )

            # Send email
            success = await email_service.send_daily_report_email(email_data)

            # Log execution
            execution_duration = (datetime.utcnow() - execution_start).total_seconds()

            log = ReportGenerationLogDB(
                log_id=f"log-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{cell_id}",
                cell_id=cell_id,
                report_date=report_date,
                execution_time=execution_start,
                generation_status="success" if success else "failed",
                execution_duration_seconds=execution_duration,
                emails_sent=1 if success else 0,
                emails_failed=0 if success else 1
            )

            db.add(log)
            db.commit()

            logger.info(f"Successfully generated and sent report for cell {cell_id}")
            return success

        except Exception as e:
            execution_duration = (datetime.utcnow() - execution_start).total_seconds()

            # Log failure
            log = ReportGenerationLogDB(
                log_id=f"log-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{cell_id}",
                cell_id=cell_id,
                report_date=report_date,
                execution_time=execution_start,
                generation_status="failed",
                execution_duration_seconds=execution_duration,
                emails_sent=0,
                emails_failed=1,
                error_message=str(e)
            )

            db.add(log)
            db.commit()

            logger.error(f"Failed to generate and send report: {e}")
            return False

    async def _generate_html_report(self, report_data: DailyReportData) -> str:
        """Generate HTML report from data"""
        # Simple HTML template
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Malgun Gothic', Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; }}
                .metric {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_data.cell_name} 일간 리포트</h1>
                <p>{report_data.report_date.strftime('%Y년 %m월 %d일')}</p>
            </div>

            <div class="metric">
                <h2>📊 당일 실적</h2>
                <p><strong>매출:</strong> {report_data.daily_revenue:,.0f} 원 ({report_data.revenue_count}건)</p>
                <p><strong>매출원가:</strong> {report_data.daily_cogs:,.0f} 원 ({report_data.cogs_count}건)</p>
                <p><strong>매출총이익:</strong> {report_data.gross_profit:,.0f} 원 ({report_data.gross_profit_margin:.1f}%)</p>
            </div>

            <div class="metric">
                <h2>📈 월간 누적 (MTD)</h2>
                <p><strong>누적 매출:</strong> {report_data.mtd_revenue:,.0f} 원</p>
                <p><strong>누적 총이익:</strong> {report_data.mtd_gross_profit:,.0f} 원 ({report_data.mtd_gross_profit_margin:.1f}%)</p>
                {'<p><strong>목표 달성률:</strong> ' + f'{report_data.revenue_achievement_rate:.1f}%</p>' if report_data.revenue_achievement_rate else ''}
            </div>

            <div class="metric">
                <h2>🏆 주요 매출 항목</h2>
                <table>
                    <tr>
                        <th>제품/서비스</th>
                        <th>금액</th>
                    </tr>
                    {''.join([f'<tr><td>{item["product_name"]}</td><td>{item["revenue_amount"]:,.0f} 원</td></tr>' for item in report_data.top_revenue_items])}
                </table>
            </div>

            <p style="color: #666; font-size: 12px; margin-top: 40px;">
                이 리포트는 NERDX 독립채산제 시스템에서 자동 생성되었습니다.
            </p>
        </body>
        </html>
        """

        return html


# Singleton instance
daily_report_service = DailyReportService()
