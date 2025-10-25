"""
NERDX Independent Accounting System - Demo with SQLite Database
Complete demo with database persistence and daily report generation
"""

import asyncio
from datetime import date, datetime
from typing import List, Dict
import time

# Import SQLite database functions
from database_sqlite import (
    initialize_database,
    insert_sample_data,
    get_cells,
    calculate_daily_summary,
    save_daily_summary,
    save_daily_report,
    get_database_stats
)

def generate_daily_report_html(cell: Dict, summary: Dict) -> str:
    """Generate HTML daily report for a cell"""

    # Determine profit status
    if summary['gross_profit'] > 0:
        profit_status = "PROFIT"
        profit_color = "#28a745"
        profit_emoji = "+"
    elif summary['gross_profit'] < 0:
        profit_status = "LOSS"
        profit_color = "#dc3545"
        profit_emoji = "-"
    else:
        profit_status = "BREAK-EVEN"
        profit_color = "#6c757d"
        profit_emoji = "="

    # Margin status
    margin_target = 30.0
    if summary['gross_profit_margin'] >= margin_target:
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
            <p>{cell['cell_name']}</p>
            <p>{summary['summary_date']}</p>
        </div>

        <div class="content">
            <h2>Financial Summary</h2>

            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">{summary['total_revenue']:,.0f} KRW</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{summary['total_cost']:,.0f} KRW</div>
            </div>

            <div class="profit-card">
                <h2>{profit_status}</h2>
                <div class="amount">{summary['gross_profit']:+,.0f} KRW</div>
                <div>Gross Profit</div>
                <div class="margin-badge">
                    Margin: {summary['gross_profit_margin']:.1f}% ({margin_status})
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
                    <td>{summary['gross_profit_margin']:.2f}%</td>
                </tr>
                <tr>
                    <td>Margin Target</td>
                    <td>{margin_target:.0f}%</td>
                </tr>
                <tr>
                    <td>Revenue Count</td>
                    <td>{summary['revenue_count']} records</td>
                </tr>
                <tr>
                    <td>Cost Count</td>
                    <td>{summary['cost_count']} records</td>
                </tr>
            </table>

            <h3>Insights</h3>
            <ul>
                <li>Cell Status: <strong>{cell['status'].upper()}</strong></li>
                <li>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>Data Sources: Salesforce CRM + Odoo ERP</li>
                <li>Currency: Korean Won (KRW)</li>
            </ul>
        </div>

        <div class="footer">
            <p><strong>NERDX Independent Accounting System</strong></p>
            <p>This is an automated daily report. For questions, contact your cell manager.</p>
            <p>Cell ID: {cell['cell_id']} | Manager: {cell['manager_email']}</p>
        </div>
    </body>
    </html>
    """

    return html_content

async def run_daily_reports():
    """Main function to run daily reports for all cells"""
    print("\n" + "=" * 60)
    print("RUNNING DAILY REPORT GENERATION")
    print("=" * 60)
    print()

    start_time = time.time()
    target_date = date.today()

    print(f"Report Date: {target_date}")

    # Get all active cells
    cells = get_cells()
    print(f"Active Cells: {len(cells)}")
    print()

    reports_generated = []

    for i, cell in enumerate(cells, 1):
        print(f"[{i}/{len(cells)}] Processing: {cell['cell_name']}")

        # Calculate daily summary
        summary = calculate_daily_summary(cell['cell_id'], target_date)

        # Save summary to database
        save_daily_summary(summary)

        # Generate HTML report
        html_content = generate_daily_report_html(cell, summary)

        # Save report to file
        filename = f"daily_report_{cell['cell_id']}_{target_date}.html"
        filepath = f"C:/Users/seans/nerdx-apec-mvp/independent-accounting-system/{filename}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Save report metadata to database
        save_daily_report(cell['cell_id'], target_date, html_content, filepath)

        print(f"   Revenue: {summary['total_revenue']:,.0f} KRW")
        print(f"   Cost: {summary['total_cost']:,.0f} KRW")
        print(f"   Profit: {summary['gross_profit']:+,.0f} KRW")
        print(f"   Margin: {summary['gross_profit_margin']:.1f}%")
        print(f"   [OK] Report saved: {filename}")
        print()

        reports_generated.append({
            'cell_id': cell['cell_id'],
            'cell_name': cell['cell_name'],
            'summary': summary,
            'file_path': filepath
        })

    elapsed_time = time.time() - start_time

    print("=" * 60)
    print("DAILY REPORT GENERATION COMPLETE")
    print("=" * 60)
    print()

    # System-wide summary
    total_revenue = sum(r['summary']['total_revenue'] for r in reports_generated)
    total_cost = sum(r['summary']['total_cost'] for r in reports_generated)
    total_profit = total_revenue - total_cost
    avg_margin = sum(r['summary']['gross_profit_margin'] for r in reports_generated) / len(reports_generated) if reports_generated else 0

    print("System-wide Summary:")
    print(f"   Total Revenue: {total_revenue:,.0f} KRW")
    print(f"   Total Cost: {total_cost:,.0f} KRW")
    print(f"   Total Profit: {total_profit:+,.0f} KRW")
    print(f"   Average Margin: {avg_margin:.1f}%")
    print(f"   Reports Generated: {len(reports_generated)}")
    print(f"   Execution Time: {elapsed_time:.2f} seconds")
    print()

    return reports_generated

async def main():
    """Main execution flow"""
    print("=" * 60)
    print("NERDX Independent Accounting System - Demo with Database")
    print("=" * 60)
    print()

    # Step 1: Initialize database
    print("Step 1: Initializing SQLite Database...")
    initialize_database()
    print()

    # Step 2: Insert sample data
    print("Step 2: Inserting Sample Data...")
    insert_sample_data()
    print()

    # Step 3: Show database stats
    print("Step 3: Database Statistics")
    stats = get_database_stats()
    for table, count in stats.items():
        print(f"   {table}: {count} records")
    print()

    # Step 4: Run daily reports
    print("Step 4: Generating Daily Reports...")
    reports = await run_daily_reports()

    # Step 5: Final summary
    print("=" * 60)
    print("DEMO COMPLETE - SUCCESS!")
    print("=" * 60)
    print()

    print("Generated Reports:")
    for report in reports:
        print(f"   - {report['file_path']}")
    print()

    print("Next Steps:")
    print("1. Open the generated HTML files in your browser")
    print("2. Review the SQLite database: nerdx_accounting_demo.db")
    print("3. Configure real Salesforce/Odoo credentials for production")
    print("4. Switch to PostgreSQL for production deployment")
    print("5. Set up automated cron job for daily report generation")
    print()

if __name__ == "__main__":
    asyncio.run(main())
