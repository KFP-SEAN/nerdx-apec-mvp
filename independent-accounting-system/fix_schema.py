#!/usr/bin/env python3
"""
Fix Railway PostgreSQL schema - add missing manager_phone column
"""
import os
import sys

try:
    import psycopg2
except ImportError:
    print("[ERROR] psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

def fix_schema():
    """Add missing columns to cells table to match SQLAlchemy model"""

    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        print("\nUsage:")
        print('  DATABASE_URL="postgresql://..." python fix_schema.py')
        sys.exit(1)

    print(f"[INFO] Connecting to Railway PostgreSQL database...")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[STEP 1] Checking current cells table schema...")

        # Check existing columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'cells'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        print(f"[INFO] Current cells table columns:")
        for col_name, col_type in columns:
            print(f"  - {col_name} ({col_type})")

        column_names = [col[0] for col in columns]

        print("\n[STEP 2] Adding missing columns...")

        # List of columns to add (from database.py CellDB model)
        columns_to_add = [
            ("salesforce_account_ids", "JSONB DEFAULT '[]'::jsonb"),
            ("salesforce_opportunity_filters", "JSONB"),
            ("odoo_analytic_account_id", "INTEGER"),
            ("odoo_analytic_account_code", "VARCHAR(50)"),
            ("monthly_revenue_target", "NUMERIC(15, 2)"),
            ("monthly_gross_profit_target", "NUMERIC(15, 2)"),
            ("gross_profit_margin_target", "FLOAT"),
        ]

        columns_added = 0
        for col_name, col_type in columns_to_add:
            if col_name not in column_names:
                print(f"  [+] Adding column: {col_name} ({col_type})")
                cursor.execute(f"""
                    ALTER TABLE cells
                    ADD COLUMN {col_name} {col_type}
                """)
                columns_added += 1
            else:
                print(f"  [OK] Column already exists: {col_name}")

        if columns_added == 0:
            print("\n[OK] All columns already exist!")
        else:
            print(f"\n[OK] {columns_added} column(s) added successfully!")

        print("\n[STEP 3] Verifying updated schema...")

        # Verify the columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'cells'
            ORDER BY ordinal_position
        """)

        final_columns = cursor.fetchall()
        print(f"[INFO] Final cells table schema ({len(final_columns)} columns):")
        for col_name, col_type, is_nullable in final_columns:
            print(f"  - {col_name} ({col_type}, nullable={is_nullable})")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] Database schema fix complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test cell creation: curl -X POST https://your-app.railway.app/api/v1/cells/ ...")
        print("2. Verify deployment: railway logs")

        return True

    except Exception as e:
        print(f"\n[ERROR] Schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_schema()
    sys.exit(0 if success else 1)
