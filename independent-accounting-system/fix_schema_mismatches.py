#!/usr/bin/env python3
"""
Fix schema mismatches between init_database.sql and SQLAlchemy models
1. Fix UUID type issues (already handled in code)
2. Fix field name mismatches in daily_financial_summaries table
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


def fix_schema_mismatches():
    """Fix schema mismatches between SQL and SQLAlchemy models"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        print("\nUsage:")
        print('  DATABASE_URL="postgresql://..." python fix_schema_mismatches.py')
        sys.exit(1)

    print(f"[INFO] Connecting to PostgreSQL database...")
    print("=" * 70)

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # ============================================
        # STEP 1: Check current schema
        # ============================================
        print("\n[STEP 1] Checking current schema...")
        print("-" * 70)

        # Check daily_financial_summaries table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'daily_financial_summaries'
            ORDER BY ordinal_position
        """)
        current_columns = [r[0] for r in cursor.fetchall()]
        print(f"[INFO] daily_financial_summaries columns: {current_columns}")

        # ============================================
        # STEP 2: Fix field name mismatches
        # ============================================
        print("\n[STEP 2] Fixing field name mismatches...")
        print("-" * 70)

        fixes_applied = []

        # Check if we have 'summary_id' (UUID) instead of 'id' (INTEGER)
        if 'summary_id' in current_columns and 'id' not in current_columns:
            print("  [!] CRITICAL: Table uses 'summary_id' (UUID) but model expects 'id' (INTEGER)")
            print("  [!] This requires recreating the table. Backing up data first...")

            # Backup existing data
            cursor.execute("SELECT COUNT(*) FROM daily_financial_summaries")
            row_count = cursor.fetchone()[0]
            print(f"  [INFO] Current table has {row_count} rows")

            if row_count > 0:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_financial_summaries_backup AS
                    SELECT * FROM daily_financial_summaries
                """)
                print("  [OK] Backup created")

            # Drop and recreate with correct schema
            cursor.execute("DROP TABLE IF EXISTS daily_financial_summaries CASCADE")
            cursor.execute("""
                CREATE TABLE daily_financial_summaries (
                    id SERIAL PRIMARY KEY,
                    cell_id VARCHAR(100) NOT NULL,
                    summary_date DATE NOT NULL,
                    total_revenue NUMERIC(15, 2) DEFAULT 0,
                    revenue_count INTEGER DEFAULT 0,
                    total_cogs NUMERIC(15, 2) DEFAULT 0,
                    cogs_count INTEGER DEFAULT 0,
                    gross_profit NUMERIC(15, 2) DEFAULT 0,
                    gross_profit_margin FLOAT DEFAULT 0.0,
                    currency VARCHAR(10) DEFAULT 'KRW',
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_cell FOREIGN KEY (cell_id) REFERENCES cells(cell_id) ON DELETE CASCADE,
                    UNIQUE(cell_id, summary_date)
                )
            """)
            cursor.execute("CREATE INDEX idx_daily_summaries_cell_id ON daily_financial_summaries(cell_id)")
            cursor.execute("CREATE INDEX idx_daily_summaries_date ON daily_financial_summaries(summary_date DESC)")
            cursor.execute("CREATE INDEX idx_daily_summaries_cell_date ON daily_financial_summaries(cell_id, summary_date DESC)")

            fixes_applied.append("Recreated daily_financial_summaries with id (INTEGER) instead of summary_id (UUID)")
            print("  [OK] Table recreated with correct schema")

        # Check if we have 'total_cost' instead of 'total_cogs'
        elif 'total_cost' in current_columns and 'total_cogs' not in current_columns:
            print("  [+] Renaming 'total_cost' to 'total_cogs'...")
            cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN total_cost TO total_cogs")
            fixes_applied.append("Renamed total_cost to total_cogs")
            print("  [OK] Renamed total_cost to total_cogs")

        # Check if we have 'cost_count' instead of 'cogs_count'
        if 'cost_count' in current_columns and 'cogs_count' not in current_columns:
            print("  [+] Renaming 'cost_count' to 'cogs_count'...")
            cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN cost_count TO cogs_count")
            fixes_applied.append("Renamed cost_count to cogs_count")
            print("  [OK] Renamed cost_count to cogs_count")

        # Check if we have 'created_at' instead of 'generated_at'
        if 'created_at' in current_columns and 'generated_at' not in current_columns:
            print("  [+] Renaming 'created_at' to 'generated_at'...")
            cursor.execute("ALTER TABLE daily_financial_summaries RENAME COLUMN created_at TO generated_at")
            fixes_applied.append("Renamed created_at to generated_at")
            print("  [OK] Renamed created_at to generated_at")

        # Drop 'updated_at' if it exists (not in model)
        if 'updated_at' in current_columns:
            print("  [+] Dropping 'updated_at' column (not in model)...")
            cursor.execute("ALTER TABLE daily_financial_summaries DROP COLUMN updated_at")
            fixes_applied.append("Dropped updated_at column")
            print("  [OK] Dropped updated_at column")

        # ============================================
        # STEP 3: Verify UUID columns are correct type
        # ============================================
        print("\n[STEP 3] Verifying UUID columns...")
        print("-" * 70)

        # Check revenue_records.revenue_id
        cursor.execute("""
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'revenue_records' AND column_name = 'revenue_id'
        """)
        revenue_id_type = cursor.fetchone()[0]
        print(f"  [INFO] revenue_records.revenue_id type: {revenue_id_type}")

        if revenue_id_type != 'uuid':
            print("  [!] WARNING: revenue_id is not UUID type. May need manual migration.")
        else:
            print("  [OK] revenue_id is UUID type (correct)")

        # Check cost_records.cost_id
        cursor.execute("""
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'cost_records' AND column_name = 'cost_id'
        """)
        cost_id_type = cursor.fetchone()[0]
        print(f"  [INFO] cost_records.cost_id type: {cost_id_type}")

        if cost_id_type != 'uuid':
            print("  [!] WARNING: cost_id is not UUID type. May need manual migration.")
        else:
            print("  [OK] cost_id is UUID type (correct)")

        # ============================================
        # STEP 4: Verify final schema
        # ============================================
        print("\n[STEP 4] Verifying final schema...")
        print("-" * 70)

        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'daily_financial_summaries'
            ORDER BY ordinal_position
        """)

        print(f"\n[INFO] Final daily_financial_summaries schema:")
        for col_name, col_type, is_nullable in cursor.fetchall():
            print(f"  - {col_name} ({col_type}, nullable={is_nullable})")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("[SUCCESS] Schema fixes complete!")
        print("=" * 70)

        if fixes_applied:
            print("\nFixes applied:")
            for i, fix in enumerate(fixes_applied, 1):
                print(f"  {i}. {fix}")
        else:
            print("\nNo fixes needed - schema already matches model")

        print("\nNext steps:")
        print("1. Test daily report generation for Cell 5")
        print("2. Verify data flows correctly through the system")
        print("3. Check for any remaining errors")

        return True

    except Exception as e:
        print(f"\n[ERROR] Schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fix_schema_mismatches()
    sys.exit(0 if success else 1)
