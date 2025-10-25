#!/usr/bin/env python3
"""
Fix Railway PostgreSQL column names for revenue_records and cost_records
SQLAlchemy models use revenue_amount/cost_amount but SQL schema uses just 'amount'
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

def fix_column_names():
    """Rename columns to match SQLAlchemy models"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"[INFO] Connecting to Railway PostgreSQL database...")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[STEP 1] Checking revenue_records table columns...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'revenue_records'
            AND column_name IN ('amount', 'revenue_amount', 'revenue_date')
            ORDER BY column_name
        """)
        revenue_cols = [r[0] for r in cursor.fetchall()]
        print(f"[INFO] Revenue columns found: {revenue_cols}")

        if 'amount' in revenue_cols and 'revenue_amount' not in revenue_cols:
            print("  [+] Renaming 'amount' to 'revenue_amount' in revenue_records...")
            cursor.execute("ALTER TABLE revenue_records RENAME COLUMN amount TO revenue_amount")
            print("  [OK] Renamed successfully")
        else:
            print("  [OK] Column already correct")

        print("\n[STEP 2] Checking cost_records table columns...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'cost_records'
            AND column_name IN ('amount', 'cost_amount', 'cost_date')
            ORDER BY column_name
        """)
        cost_cols = [r[0] for r in cursor.fetchall()]
        print(f"[INFO] Cost columns found: {cost_cols}")

        if 'amount' in cost_cols and 'cost_amount' not in cost_cols:
            print("  [+] Renaming 'amount' to 'cost_amount' in cost_records...")
            cursor.execute("ALTER TABLE cost_records RENAME COLUMN amount TO cost_amount")
            print("  [OK] Renamed successfully")
        else:
            print("  [OK] Column already correct")

        print("\n[STEP 3] Verifying final schema...")

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'revenue_records'
            ORDER BY ordinal_position
        """)
        print("\n[INFO] Revenue Records final schema:")
        for col_name, col_type in cursor.fetchall():
            print(f"  - {col_name} ({col_type})")

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'cost_records'
            ORDER BY ordinal_position
        """)
        print("\n[INFO] Cost Records final schema:")
        for col_name, col_type in cursor.fetchall():
            print(f"  - {col_name} ({col_type})")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] Column names fixed!")
        print("=" * 60)
        print("\nNext: Retry daily report generation")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to fix columns: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_column_names()
    sys.exit(0 if success else 1)
