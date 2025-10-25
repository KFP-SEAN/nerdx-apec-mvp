"""
NERDX Independent Accounting System - Demo Integration Script
Demonstrates Cell management and daily report generation
"""

import asyncio
import smtplib
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import json

# Mock Data Structures
class Cell:
    def __init__(self, cell_id: str, cell_name: str, manager_email: str):
        self.cell_id = cell_id
        self.cell_name = cell_name
        self.manager_email = manager_email
        self.status = "active"
        self.created_at = datetime.now()

class RevenueRecord:
    def __init__(self, cell_id: str, amount: float, source: str, revenue_date: date):
        self.cell_id = cell_id
        self.amount = amount
        self.source = source
        self.revenue_date = revenue_date

class CostRecord:
    def __init__(self, cell_id: str, amount: float, category: str, cost_date: date):
        self.cell_id = cell_id
        self.amount = amount
        self.category = category
        self.cost_date = cost_date

class DailyFinancialSummary:
    def __init__(self, cell_id: str, summary_date: date):
        self.cell_id = cell_id
        self.summary_date = summary_date
        self.total_revenue = 0.0
        self.total_cost = 0.0
        self.gross_profit = 0.0
        self.gross_profit_margin = 0.0

# In-Memory Database (Demo)
CELLS_DB: List[Cell] = []
REVENUE_DB: List[RevenueRecord] = []
COST_DB: List[CostRecord] = []
SUMMARY_DB: List[DailyFinancialSummary] = []

def initialize_demo_data():
    """Initialize demo data with sample cells and financial records"""
    global CELLS_DB, REVENUE_DB, COST_DB

    print("=" * 60)
    print("NERDX Independent Accounting System - Demo")
    print("=" * 60)
    print()

    # Create sample cells
    cells = [
        Cell("CELL-001", "Product Development Team", "pd@nerdx.com"),
        Cell("CELL-002", "Marketing Operations", "marketing@nerdx.com"),
        Cell("CELL-003", "Sales Team Korea", "sales@nerdx.com"),
    ]
    CELLS_DB.extend(cells)
    print(f"[OK] Created {len(cells)} cells")

    # Generate sample revenue data (last 7 days)
    today = date.today()
    for cell in cells:
        for days_ago in range(7):
            revenue_date = today - timedelta(days=days_ago)
            revenue = RevenueRecord(
                cell_id=cell.cell_id,
                amount=1000000 + (days_ago * 100000),  # 1M ~ 1.6M KRW
                source="Salesforce CRM",
                revenue_date=revenue_date
            )
            REVENUE_DB.append(revenue)

    print(f"[OK] Generated {len(REVENUE_DB)} revenue records")

    # Generate sample cost data
    for cell in cells:
        for days_ago in range(7):
            cost_date = today - timedelta(days=days_ago)
            cost = CostRecord(
                cell_id=cell.cell_id,
                amount=700000 + (days_ago * 50000),  # 700K ~ 1M KRW
                category="Odoo ERP",
                cost_date=cost_date
            )
            COST_DB.append(cost)

    print(f"[OK] Generated {len(COST_DB)} cost records")
    print()

def calculate_daily_summary(cell_id: str, target_date: date) -> DailyFinancialSummary:
    """Calculate financial summary for a cell on a specific date"""
    summary = DailyFinancialSummary(cell_id, target_date)

    # Calculate total revenue
    revenue_records = [r for r in REVENUE_DB
                      if r.cell_id == cell_id and r.revenue_date == target_date]
    summary.total_revenue = sum(r.amount for r in revenue_records)

    # Calculate total cost
    cost_records = [c for c in COST_DB
                   if c.cell_id == cell_id and c.cost_date == target_date]
    summary.total_cost = sum(c.amount for c in cost_records)

    # Calculate profit and margin
    summary.gross_profit = summary.total_revenue - summary.total_cost
    if summary.total_revenue > 0:
        summary.gross_profit_margin = (summary.gross_profit / summary.total_revenue) * 100

    return summary

def generate_daily_report(cell: Cell, summary: DailyFinancialSummary) -> str:
    """Generate HTML daily report for a cell"""

    # Determine profit status
    if summary.gross_profit > 0:
        profit_status = "PROFIT"
        profit_color = "#28a745"
        profit_emoji = ""
    elif summary.gross_profit < 0:
        profit_status = "LOSS"
        profit_color = "#dc3545"
        profit_emoji = ""
    else:
        profit_status = "BREAK-EVEN"
        profit_color = "#6c757d"
        profit_emoji = ""

    # Margin status
    margin_target = 30.0
    if summary.gross_profit_margin >= margin_target:
        margin_status = "Above Target"
        margin_color = "#28a745"
    else:
        margin_status = "Below Target"
        margin_color = "#ffc107"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px 10px 0 0;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .content {{
                background: white;
                padding: 30px;
                border: 1px solid #e0e0e0;
                border-top: none;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .metric-label {{
                font-size: 12px;
                text-transform: uppercase;
                color: #6c757d;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 28px;
                font-weight: bold;
                color: #212529;
            }}
            .profit-card {{
                background: {profit_color};
                color: white;
                padding: 25px;
                margin: 20px 0;
                border-radius: 8px;
                text-align: center;
            }}
            .profit-card h2 {{
                margin: 0;
                font-size: 20px;
            }}
            .profit-card .amount {{
                font-size: 36px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .margin-badge {{
                display: inline-block;
                background: {margin_color};
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                margin-top: 10px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                border: 1px solid #e0e0e0;
                border-top: none;
                font-size: 12px;
                color: #6c757d;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            th {{
                background: #667eea;
                color: white;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{profit_emoji} Daily P&L Report</h1>
            <p>{cell.cell_name}</p>
            <p>{summary.summary_date.strftime('%Y-%m-%d (%A)')}</p>
        </div>

        <div class="content">
            <h2>Financial Summary</h2>

            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">{summary.total_revenue:,.0f} KRW</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{summary.total_cost:,.0f} KRW</div>
            </div>

            <div class="profit-card">
                <h2>{profit_status}</h2>
                <div class="amount">{summary.gross_profit:+,.0f} KRW</div>
                <div>Gross Profit</div>
                <div class="margin-badge">
                    Margin: {summary.gross_profit_margin:.1f}% ({margin_status})
                </div>
            </div>

            <h3>Key Metrics</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Revenue Recognition</td>
                    <td>Salesforce CRM</td>
                </tr>
                <tr>
                    <td>Cost Tracking</td>
                    <td>Odoo ERP</td>
                </tr>
                <tr>
                    <td>Gross Profit Margin</td>
                    <td>{summary.gross_profit_margin:.2f}%</td>
                </tr>
                <tr>
                    <td>Margin Target</td>
                    <td>{margin_target:.0f}%</td>
                </tr>
            </table>

            <h3>Insights</h3>
            <ul>
                <li>Cell Status: <strong>{cell.status.upper()}</strong></li>
                <li>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>Data Sources: Salesforce CRM + Odoo ERP</li>
                <li>Currency: Korean Won (KRW)</li>
            </ul>
        </div>

        <div class="footer">
            <p><strong>NERDX Independent Accounting System</strong></p>
            <p>This is an automated daily report. For questions, contact your cell manager.</p>
            <p>Cell ID: {cell.cell_id} | Manager: {cell.manager_email}</p>
        </div>
    </body>
    </html>
    """

    return html_content

def send_email_report(cell: Cell, html_content: str, summary: DailyFinancialSummary):
    """Send email report (Demo - prints to console)"""
    print(f"[EMAIL] Sending daily report to: {cell.manager_email}")
    print(f"   Cell: {cell.cell_name}")
    print(f"   Date: {summary.summary_date}")
    print(f"   Revenue: {summary.total_revenue:,.0f} KRW")
    print(f"   Cost: {summary.total_cost:,.0f} KRW")
    print(f"   Profit: {summary.gross_profit:+,.0f} KRW")
    print(f"   Margin: {summary.gross_profit_margin:.1f}%")

    # Save HTML report to file (instead of sending email)
    filename = f"daily_report_{cell.cell_id}_{summary.summary_date}.html"
    filepath = f"C:/Users/seans/nerdx-apec-mvp/independent-accounting-system/{filename}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"   [OK] Report saved: {filename}")
    print()

async def run_daily_reports():
    """Main function to run daily reports for all cells"""
    print("\n" + "=" * 60)
    print("RUNNING DAILY REPORT GENERATION")
    print("=" * 60)
    print()

    target_date = date.today()
    print(f"Report Date: {target_date.strftime('%Y-%m-%d (%A)')}")
    print(f"Active Cells: {len(CELLS_DB)}")
    print()

    for i, cell in enumerate(CELLS_DB, 1):
        print(f"[{i}/{len(CELLS_DB)}] Processing: {cell.cell_name}")

        # Calculate daily summary
        summary = calculate_daily_summary(cell.cell_id, target_date)
        SUMMARY_DB.append(summary)

        # Generate report
        html_content = generate_daily_report(cell, summary)

        # Send email (or save to file in demo)
        send_email_report(cell, html_content, summary)

    print("=" * 60)
    print("[OK] DAILY REPORT GENERATION COMPLETE")
    print("=" * 60)
    print()

    # Summary statistics
    total_revenue = sum(s.total_revenue for s in SUMMARY_DB)
    total_cost = sum(s.total_cost for s in SUMMARY_DB)
    total_profit = total_revenue - total_cost
    avg_margin = sum(s.gross_profit_margin for s in SUMMARY_DB) / len(SUMMARY_DB) if SUMMARY_DB else 0

    print(" System-wide Summary:")
    print(f"   Total Revenue: {total_revenue:,.0f} KRW")
    print(f"   Total Cost: {total_cost:,.0f} KRW")
    print(f"   Total Profit: {total_profit:+,.0f} KRW")
    print(f"   Average Margin: {avg_margin:.1f}%")
    print()

def api_simulation():
    """Simulate API endpoints"""
    print("\n" + "=" * 60)
    print("API ENDPOINT SIMULATION")
    print("=" * 60)
    print()

    # GET /api/cells
    print("[API] GET /api/cells")
    cells_data = [
        {
            "cell_id": c.cell_id,
            "cell_name": c.cell_name,
            "manager_email": c.manager_email,
            "status": c.status
        }
        for c in CELLS_DB
    ]
    print(json.dumps(cells_data, indent=2))
    print()

    # GET /api/financial/summary
    print("[API] GET /api/financial/summary")
    summary_data = [
        {
            "cell_id": s.cell_id,
            "date": s.summary_date.isoformat(),
            "revenue": s.total_revenue,
            "cost": s.total_cost,
            "profit": s.gross_profit,
            "margin_percent": round(s.gross_profit_margin, 2)
        }
        for s in SUMMARY_DB
    ]
    print(json.dumps(summary_data[:3], indent=2))  # Show first 3
    print(f"... and {len(summary_data) - 3} more records")
    print()

async def main():
    """Main execution flow"""
    # Step 1: Initialize demo data
    initialize_demo_data()

    # Step 2: Run daily reports
    await run_daily_reports()

    # Step 3: Simulate API
    api_simulation()

    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Check generated HTML reports in the current directory")
    print("2. Configure real Salesforce/Odoo credentials in .env")
    print("3. Set up PostgreSQL database for production")
    print("4. Configure SMTP for email delivery")
    print("5. Deploy to production (Railway, AWS, etc.)")
    print()

if __name__ == "__main__":
    asyncio.run(main())
