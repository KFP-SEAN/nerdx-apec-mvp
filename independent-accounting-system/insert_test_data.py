#!/usr/bin/env python3
"""
Insert test revenue and cost data for NERD12 product on 2025-10-25
"""
import os
import sys
from datetime import date
import uuid

try:
    import psycopg2
except ImportError:
    print("[ERROR] psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2


def insert_test_data():
    """Insert test revenue and cost data"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"[INFO] Connecting to Railway PostgreSQL database...")
    print("=" * 70)

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # Test data parameters
        cell_id = "cell-5ca00d505e2b"  # Existing cell
        test_date = date(2025, 10, 25)

        # Generate UUIDs
        revenue_uuid = str(uuid.uuid4())
        cost_uuid = str(uuid.uuid4())

        print(f"\n[STEP 1] Inserting test revenue record...")
        print(f"  Cell ID: {cell_id}")
        print(f"  Date: {test_date}")
        print(f"  Product: NERD12")
        print(f"  Revenue UUID: {revenue_uuid}")

        # Insert revenue record
        cursor.execute("""
            INSERT INTO revenue_records (
                revenue_id, cell_id, revenue_date, revenue_amount, currency,
                salesforce_opportunity_id, salesforce_account_id,
                opportunity_name, stage, probability, opportunity_type,
                product_name, product_category, quantity, unit_price,
                description, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                NOW(), NOW()
            )
        """, (
            revenue_uuid,
            cell_id,
            test_date,
            1500000.00,  # 1.5M KRW revenue
            'KRW',
            'test-opp-001',
            'test-acct-001',
            'NERD12 Product Sale - Test',
            'Closed Won',
            100.0,  # 100% probability
            'New Business',
            'NERD12',
            'Hardware',
            10,  # 10 units
            150000.00,  # 150K KRW per unit
            'Test revenue record for NERD12 product sale on 2025-10-25'
        ))

        print(f"  [OK] Revenue record inserted: {revenue_uuid}")

        print(f"\n[STEP 2] Inserting test cost record...")
        print(f"  Cost UUID: {cost_uuid}")

        # Insert cost record
        cursor.execute("""
            INSERT INTO cost_records (
                cost_id, cell_id, cost_date, cost_amount, currency,
                category, source,
                odoo_invoice_id, odoo_invoice_line_id, odoo_analytic_account_id,
                odoo_product_id, odoo_partner_id,
                vendor_name, invoice_number, product_name,
                description, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                NOW(), NOW()
            )
        """, (
            cost_uuid,
            cell_id,
            test_date,
            600000.00,  # 600K KRW cost (40% margin)
            'KRW',
            'COGS',
            'odoo',
            101,  # test invoice ID
            1001,  # test invoice line ID
            5001,  # test analytic account
            2001,  # test product ID
            3001,  # test partner ID
            'Test Vendor Inc.',
            'INV-2025-001',
            'NERD12',
            'Test cost record for NERD12 COGS on 2025-10-25'
        ))

        print(f"  [OK] Cost record inserted: {cost_uuid}")

        # Verify insertion
        print(f"\n[STEP 3] Verifying inserted data...")

        cursor.execute("""
            SELECT revenue_id, product_name, revenue_amount, revenue_date
            FROM revenue_records
            WHERE cell_id = %s AND revenue_date = %s
        """, (cell_id, test_date))

        revenue_rows = cursor.fetchall()
        print(f"\n[INFO] Revenue records for {test_date}:")
        for row in revenue_rows:
            print(f"  - {row[0][:8]}...: {row[1]} - {row[2]:,.0f} KRW on {row[3]}")

        cursor.execute("""
            SELECT cost_id, product_name, cost_amount, cost_date
            FROM cost_records
            WHERE cell_id = %s AND cost_date = %s
        """, (cell_id, test_date))

        cost_rows = cursor.fetchall()
        print(f"\n[INFO] Cost records for {test_date}:")
        for row in cost_rows:
            print(f"  - {row[0][:8]}...: {row[1]} - {row[2]:,.0f} KRW on {row[3]}")

        # Calculate summary
        total_revenue = sum(row[2] for row in revenue_rows)
        total_cost = sum(row[2] for row in cost_rows)
        gross_profit = total_revenue - total_cost
        margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        print(f"\n[SUMMARY] Financial data for {test_date}:")
        print(f"  Total Revenue: {total_revenue:,.0f} KRW")
        print(f"  Total Cost (COGS): {total_cost:,.0f} KRW")
        print(f"  Gross Profit: {gross_profit:,.0f} KRW")
        print(f"  Margin: {margin:.1f}%")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("[SUCCESS] Test data inserted successfully!")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Generate daily financial summary")
        print("2. Send daily report email")
        print(f"\nAPI Call:")
        print(f'curl -s -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/{cell_id}/send?report_date={test_date}" -H "Content-Type: application/json" -d \'{{"recipients":["sean@koreafnbpartners.com"]}}\'')
        print("\n" + "=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to insert test data: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = insert_test_data()
    sys.exit(0 if success else 1)
