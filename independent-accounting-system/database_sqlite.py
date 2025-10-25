"""
NERDX Independent Accounting System - SQLite Database Implementation
Lightweight demo database for testing without PostgreSQL
"""

import sqlite3
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import os

DATABASE_PATH = "nerdx_accounting_demo.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def initialize_database():
    """Create database schema for SQLite"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS cell_embeddings")
        cursor.execute("DROP TABLE IF EXISTS daily_reports")
        cursor.execute("DROP TABLE IF EXISTS daily_financial_summaries")
        cursor.execute("DROP TABLE IF EXISTS cost_records")
        cursor.execute("DROP TABLE IF EXISTS revenue_records")
        cursor.execute("DROP TABLE IF EXISTS cells")

        # Cells table
        cursor.execute("""
            CREATE TABLE cells (
                cell_id TEXT PRIMARY KEY,
                cell_name TEXT NOT NULL,
                cell_type TEXT DEFAULT 'other',
                status TEXT DEFAULT 'active',
                manager_name TEXT,
                manager_email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Revenue records
        cursor.execute("""
            CREATE TABLE revenue_records (
                revenue_id TEXT PRIMARY KEY,
                cell_id TEXT NOT NULL,
                revenue_date DATE NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'KRW',
                source TEXT DEFAULT 'Salesforce CRM',
                salesforce_opportunity_id TEXT,
                salesforce_account_id TEXT,
                opportunity_name TEXT,
                stage TEXT,
                description TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE
            )
        """)

        # Cost records
        cursor.execute("""
            CREATE TABLE cost_records (
                cost_id TEXT PRIMARY KEY,
                cell_id TEXT NOT NULL,
                cost_date DATE NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'KRW',
                category TEXT DEFAULT 'operational',
                source TEXT DEFAULT 'Odoo ERP',
                odoo_invoice_id TEXT,
                odoo_analytic_account_id TEXT,
                vendor_name TEXT,
                invoice_number TEXT,
                description TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE
            )
        """)

        # Daily financial summaries
        cursor.execute("""
            CREATE TABLE daily_financial_summaries (
                summary_id TEXT PRIMARY KEY,
                cell_id TEXT NOT NULL,
                summary_date DATE NOT NULL,
                total_revenue REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                gross_profit_margin REAL DEFAULT 0,
                revenue_count INTEGER DEFAULT 0,
                cost_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cell_id, summary_date),
                FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE
            )
        """)

        # Daily reports
        cursor.execute("""
            CREATE TABLE daily_reports (
                report_id TEXT PRIMARY KEY,
                cell_id TEXT NOT NULL,
                report_date DATE NOT NULL,
                html_content TEXT,
                email_subject TEXT,
                email_sent INTEGER DEFAULT 0,
                email_sent_at TIMESTAMP,
                generation_time_ms INTEGER,
                file_path TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cell_id, report_date),
                FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX idx_revenue_cell_date ON revenue_records(cell_id, revenue_date DESC)")
        cursor.execute("CREATE INDEX idx_cost_cell_date ON cost_records(cell_id, cost_date DESC)")
        cursor.execute("CREATE INDEX idx_summary_cell_date ON daily_financial_summaries(cell_id, summary_date DESC)")
        cursor.execute("CREATE INDEX idx_reports_cell_date ON daily_reports(cell_id, report_date DESC)")

        print("[OK] SQLite database schema created successfully")
        print(f"[OK] Database file: {os.path.abspath(DATABASE_PATH)}")

def insert_sample_data():
    """Insert sample data for testing"""
    import uuid
    from datetime import timedelta

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert sample cells
        cells = [
            ("CELL-001", "Product Development Team", "product", "John Doe", "pd@nerdx.com", "Core product development and R&D"),
            ("CELL-002", "Marketing Operations", "marketing", "Jane Smith", "marketing@nerdx.com", "Marketing campaigns and brand management"),
            ("CELL-003", "Sales Team Korea", "sales", "Kim Min-jun", "sales@nerdx.com", "B2B sales and customer acquisition"),
        ]

        for cell_id, cell_name, cell_type, manager_name, manager_email, description in cells:
            cursor.execute("""
                INSERT OR REPLACE INTO cells (cell_id, cell_name, cell_type, manager_name, manager_email, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cell_id, cell_name, cell_type, manager_name, manager_email, description))

        print(f"[OK] Inserted {len(cells)} cells")

        # Generate revenue data (last 7 days)
        today = date.today()
        revenue_count = 0

        for cell_id, _, _, _, _, _ in cells:
            for days_ago in range(7):
                revenue_date = today - timedelta(days=days_ago)
                amount = 1000000 + (days_ago * 100000)  # 1M ~ 1.6M KRW
                revenue_id = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO revenue_records (revenue_id, cell_id, revenue_date, amount, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (revenue_id, cell_id, revenue_date, amount, "Salesforce CRM"))
                revenue_count += 1

        print(f"[OK] Inserted {revenue_count} revenue records")

        # Generate cost data (last 7 days)
        cost_count = 0

        for cell_id, _, _, _, _, _ in cells:
            for days_ago in range(7):
                cost_date = today - timedelta(days=days_ago)
                amount = 700000 + (days_ago * 50000)  # 700K ~ 1M KRW
                cost_id = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO cost_records (cost_id, cell_id, cost_date, amount, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (cost_id, cell_id, cost_date, amount, "operational"))
                cost_count += 1

        print(f"[OK] Inserted {cost_count} cost records")

def get_cells() -> List[Dict[str, Any]]:
    """Get all active cells"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cell_id, cell_name, cell_type, manager_name, manager_email, status
            FROM cells
            WHERE status = 'active'
        """)
        return [dict(row) for row in cursor.fetchall()]

def calculate_daily_summary(cell_id: str, target_date: date) -> Dict[str, Any]:
    """Calculate financial summary for a cell on a specific date"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Calculate total revenue
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_revenue, COUNT(*) as revenue_count
            FROM revenue_records
            WHERE cell_id = ? AND revenue_date = ?
        """, (cell_id, target_date))
        revenue_result = cursor.fetchone()
        total_revenue = revenue_result['total_revenue']
        revenue_count = revenue_result['revenue_count']

        # Calculate total cost
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_cost, COUNT(*) as cost_count
            FROM cost_records
            WHERE cell_id = ? AND cost_date = ?
        """, (cell_id, target_date))
        cost_result = cursor.fetchone()
        total_cost = cost_result['total_cost']
        cost_count = cost_result['cost_count']

        # Calculate profit and margin
        gross_profit = total_revenue - total_cost
        gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            'cell_id': cell_id,
            'summary_date': target_date,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'gross_profit': gross_profit,
            'gross_profit_margin': gross_profit_margin,
            'revenue_count': revenue_count,
            'cost_count': cost_count
        }

def save_daily_summary(summary: Dict[str, Any]):
    """Save daily summary to database"""
    import uuid

    with get_db_connection() as conn:
        cursor = conn.cursor()

        summary_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO daily_financial_summaries
            (summary_id, cell_id, summary_date, total_revenue, total_cost,
             gross_profit, gross_profit_margin, revenue_count, cost_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            summary_id,
            summary['cell_id'],
            summary['summary_date'],
            summary['total_revenue'],
            summary['total_cost'],
            summary['gross_profit'],
            summary['gross_profit_margin'],
            summary['revenue_count'],
            summary['cost_count']
        ))

def save_daily_report(cell_id: str, report_date: date, html_content: str, file_path: str):
    """Save daily report to database"""
    import uuid

    with get_db_connection() as conn:
        cursor = conn.cursor()

        report_id = str(uuid.uuid4())
        email_subject = f"Daily P&L Report - {cell_id} - {report_date}"

        cursor.execute("""
            INSERT OR REPLACE INTO daily_reports
            (report_id, cell_id, report_date, html_content, email_subject, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (report_id, cell_id, report_date, html_content, email_subject, file_path))

def get_database_stats():
    """Get database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        stats = {}

        tables = ['cells', 'revenue_records', 'cost_records', 'daily_financial_summaries', 'daily_reports']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = cursor.fetchone()['count']

        return stats

if __name__ == "__main__":
    print("=" * 60)
    print("NERDX Independent Accounting System - SQLite Database Setup")
    print("=" * 60)
    print()

    # Initialize database
    initialize_database()
    print()

    # Insert sample data
    print("Inserting sample data...")
    insert_sample_data()
    print()

    # Show database stats
    print("Database Statistics:")
    stats = get_database_stats()
    for table, count in stats.items():
        print(f"  {table}: {count} records")
    print()

    # Test query
    print("Active Cells:")
    cells = get_cells()
    for cell in cells:
        print(f"  - {cell['cell_id']}: {cell['cell_name']} ({cell['manager_email']})")
    print()

    print("=" * 60)
    print("SQLite Database Setup Complete!")
    print("=" * 60)
