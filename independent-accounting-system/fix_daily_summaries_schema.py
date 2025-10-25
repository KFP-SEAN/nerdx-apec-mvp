#!/usr/bin/env python3
"""
Fix Railway PostgreSQL schema for daily_financial_summaries table
Change primary key from 'summary_id' (UUID) to 'id' (INTEGER) to match SQLAlchemy model
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

def fix_daily_summaries_schema():
    """Fix daily_financial_summaries table schema to match SQLAlchemy model"""

    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        print("\nUsage:")
        print('  DATABASE_URL="postgresql://..." python fix_daily_summaries_schema.py')
        sys.exit(1)

    print(f"[INFO] Connecting to Railway PostgreSQL database...")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[STEP 1] Checking current daily_financial_summaries table schema...")

        # Check existing columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'daily_financial_summaries'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        print(f"[INFO] Current daily_financial_summaries table columns:")
        for col_name, col_type, is_nullable in columns:
            print(f"  - {col_name} ({col_type}, nullable={is_nullable})")

        column_names = [col[0] for col in columns]

        print("\n[STEP 2] Fixing schema mismatches...")

        # Check if we need to rename summary_id to id
        if 'summary_id' in column_names and 'id' not in column_names:
            print("  [!] Found 'summary_id' column - need to rename to 'id'")
            print("  [+] Dropping and recreating table with correct schema...")

            # Backup existing data
            cursor.execute("SELECT COUNT(*) FROM daily_financial_summaries")
            row_count = cursor.fetchone()[0]
            print(f"  [INFO] Current table has {row_count} rows")

            if row_count > 0:
                print("  [!] WARNING: Table has data - backing up first...")
                cursor.execute("""
                    CREATE TABLE daily_financial_summaries_backup AS
                    SELECT * FROM daily_financial_summaries
                """)
                print("  [OK] Backup created: daily_financial_summaries_backup")

            # Drop existing table
            cursor.execute("DROP TABLE IF EXISTS daily_financial_summaries CASCADE")
            print("  [OK] Dropped existing table")

            # Recreate table with correct schema (matching SQLAlchemy model)
            cursor.execute("""
                CREATE TABLE daily_financial_summaries (
                    id SERIAL PRIMARY KEY,
                    cell_id VARCHAR(100) NOT NULL,
                    summary_date DATE NOT NULL,

                    -- Revenue
                    total_revenue NUMERIC(15, 2) DEFAULT 0,
                    revenue_count INTEGER DEFAULT 0,

                    -- Costs
                    total_cogs NUMERIC(15, 2) DEFAULT 0,
                    cogs_count INTEGER DEFAULT 0,

                    -- Profitability (will be calculated via application)
                    gross_profit NUMERIC(15, 2) DEFAULT 0,
                    gross_profit_margin FLOAT DEFAULT 0.0,

                    -- Currency
                    currency VARCHAR(10) DEFAULT 'KRW',

                    -- Metadata
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    -- Constraints
                    CONSTRAINT fk_cell FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE,
                    UNIQUE(cell_id, summary_date)
                )
            """)
            print("  [OK] Created new table with correct schema")

            # Create indexes
            cursor.execute("CREATE INDEX idx_daily_summaries_cell_id ON daily_financial_summaries(cell_id)")
            cursor.execute("CREATE INDEX idx_daily_summaries_date ON daily_financial_summaries(summary_date DESC)")
            cursor.execute("CREATE INDEX idx_daily_summaries_cell_date ON daily_financial_summaries(cell_id, summary_date DESC)")
            print("  [OK] Created indexes")

        elif 'id' in column_names:
            print("  [OK] Table already has 'id' column - checking other columns...")

            # Check if total_cogs exists (vs total_cost in old schema)
            if 'total_cogs' not in column_names and 'total_cost' in column_names:
                print("  [+] Renaming total_cost to total_cogs...")
                cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN total_cost TO total_cogs")
                print("  [OK] Renamed total_cost to total_cogs")

            # Check if cogs_count exists (vs cost_count in old schema)
            if 'cogs_count' not in column_names and 'cost_count' in column_names:
                print("  [+] Renaming cost_count to cogs_count...")
                cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN cost_count TO cogs_count")
                print("  [OK] Renamed cost_count to cogs_count")

            # Check if generated_at exists (vs created_at/updated_at in old schema)
            if 'generated_at' not in column_names and 'created_at' in column_names:
                print("  [+] Renaming created_at to generated_at...")
                cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN created_at TO generated_at")
                print("  [OK] Renamed created_at to generated_at")

            # Drop updated_at if exists (not in SQLAlchemy model)
            if 'updated_at' in column_names:
                print("  [+] Dropping updated_at column (not in model)...")
                cursor.execute("ALTER TABLE daily_financial_summaries DROP COLUMN IF EXISTS updated_at")
                print("  [OK] Dropped updated_at column")

        print("\n[STEP 3] Verifying updated schema...")

        # Verify the columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'daily_financial_summaries'
            ORDER BY ordinal_position
        """)

        final_columns = cursor.fetchall()
        print(f"[INFO] Final daily_financial_summaries table schema ({len(final_columns)} columns):")
        for col_name, col_type, is_nullable, col_default in final_columns:
            default_str = f", default={col_default[:30]}..." if col_default else ""
            print(f"  - {col_name} ({col_type}, nullable={is_nullable}{default_str})")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] Database schema fix complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test daily report generation:")
        print('   curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-25"')
        print("2. Check email inbox: sean@koreafnbpartners.com")

        return True

    except Exception as e:
        print(f"\n[ERROR] Schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_daily_summaries_schema()
    sys.exit(0 if success else 1)
