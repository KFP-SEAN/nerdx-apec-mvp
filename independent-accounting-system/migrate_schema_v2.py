#!/usr/bin/env python3
"""
PostgreSQL Schema Migration v2 for NERDX Independent Accounting System
Adds standard Salesforce and Odoo fields to improve integration
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


def migrate_schema():
    """Add new standard fields to revenue_records and cost_records tables"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        print("\nUsage:")
        print('  DATABASE_URL="postgresql://..." python migrate_schema_v2.py')
        sys.exit(1)

    print(f"[INFO] Connecting to Railway PostgreSQL database...")
    print("=" * 70)

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # ============================================
        # STEP 1: Migrate revenue_records table
        # ============================================
        print("\n[STEP 1] Migrating revenue_records table...")
        print("-" * 70)

        # Check existing columns
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'revenue_records'
            ORDER BY ordinal_position
        """)
        revenue_cols = [r[0] for r in cursor.fetchall()]
        print(f"[INFO] Current revenue_records columns: {len(revenue_cols)}")

        # New fields to add
        revenue_fields_to_add = [
            ("opportunity_name", "VARCHAR(200)", "Standard: Opportunity.Name"),
            ("stage", "VARCHAR(100)", "Standard: Opportunity.StageName"),
            ("probability", "FLOAT", "Standard: Opportunity.Probability"),
            ("opportunity_type", "VARCHAR(100)", "Standard: Opportunity.Type"),
        ]

        revenue_added = 0
        for field_name, field_type, description in revenue_fields_to_add:
            if field_name not in revenue_cols:
                print(f"  [+] Adding column: {field_name} ({field_type}) - {description}")
                cursor.execute(f"""
                    ALTER TABLE revenue_records
                    ADD COLUMN {field_name} {field_type}
                """)
                revenue_added += 1
            else:
                print(f"  [OK] Column already exists: {field_name}")

        print(f"\n[SUMMARY] revenue_records: {revenue_added} new column(s) added")

        # ============================================
        # STEP 2: Migrate cost_records table
        # ============================================
        print("\n[STEP 2] Migrating cost_records table...")
        print("-" * 70)

        # Check existing columns
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'cost_records'
            ORDER BY ordinal_position
        """)
        cost_cols = [r[0] for r in cursor.fetchall()]
        print(f"[INFO] Current cost_records columns: {len(cost_cols)}")

        # New fields to add
        cost_fields_to_add = [
            ("odoo_invoice_line_id", "INTEGER", "Standard: account.move.line.id", True),
            ("odoo_product_id", "INTEGER", "Standard: product.product.id", False),
            ("odoo_partner_id", "INTEGER", "Standard: res.partner.id", False),
            ("product_name", "VARCHAR(200)", "Odoo: product.product.name", False),
        ]

        cost_added = 0
        for field_info in cost_fields_to_add:
            field_name, field_type, description = field_info[:3]
            create_index = field_info[3] if len(field_info) > 3 else False

            if field_name not in cost_cols:
                print(f"  [+] Adding column: {field_name} ({field_type}) - {description}")
                cursor.execute(f"""
                    ALTER TABLE cost_records
                    ADD COLUMN {field_name} {field_type}
                """)
                cost_added += 1

                # Create index if needed
                if create_index:
                    index_name = f"idx_cost_records_{field_name}"
                    print(f"    [+] Creating index: {index_name}")
                    cursor.execute(f"""
                        CREATE INDEX {index_name} ON cost_records({field_name})
                    """)
            else:
                print(f"  [OK] Column already exists: {field_name}")

        print(f"\n[SUMMARY] cost_records: {cost_added} new column(s) added")

        # ============================================
        # STEP 3: Verify final schema
        # ============================================
        print("\n[STEP 3] Verifying final schema...")
        print("=" * 70)

        # Revenue records schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'revenue_records'
            ORDER BY ordinal_position
        """)
        print(f"\n[INFO] Revenue Records final schema:")
        for col_name, col_type, is_nullable in cursor.fetchall():
            print(f"  - {col_name} ({col_type}, nullable={is_nullable})")

        # Cost records schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'cost_records'
            ORDER BY ordinal_position
        """)
        print(f"\n[INFO] Cost Records final schema:")
        for col_name, col_type, is_nullable in cursor.fetchall():
            print(f"  - {col_name} ({col_type}, nullable={is_nullable})")

        # Check indexes
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename IN ('revenue_records', 'cost_records')
            ORDER BY tablename, indexname
        """)
        print(f"\n[INFO] Indexes:")
        for index_name, index_def in cursor.fetchall():
            print(f"  - {index_name}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("[SUCCESS] Schema migration complete!")
        print("=" * 70)
        print("\nMigration Summary:")
        print(f"  • Revenue Records: {revenue_added} new standard Salesforce fields")
        print(f"  • Cost Records: {cost_added} new standard Odoo fields")
        print("\nNew Salesforce Fields (revenue_records):")
        print("  • opportunity_name - Opportunity.Name")
        print("  • stage - Opportunity.StageName (e.g., 'Closed Won')")
        print("  • probability - Opportunity.Probability (0-100)")
        print("  • opportunity_type - Opportunity.Type (e.g., 'New Business')")
        print("\nNew Odoo Fields (cost_records):")
        print("  • odoo_invoice_line_id - account.move.line.id (indexed)")
        print("  • odoo_product_id - product.product.id")
        print("  • odoo_partner_id - res.partner.id (vendor)")
        print("  • product_name - product.product.name for display")
        print("\nNext Steps:")
        print("1. Deploy updated code to Railway: git push origin main")
        print("2. Test revenue sync: POST /api/v1/financial/sync/{cell_id}/revenue")
        print("3. Test cost sync: POST /api/v1/financial/sync/{cell_id}/costs")
        print("4. Generate daily report: POST /api/v1/reports/daily/{cell_id}/send")
        print("\n" + "=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_schema()
    sys.exit(0 if success else 1)
