#!/usr/bin/env python3
"""
Setup Railway PostgreSQL database with pgvector extensions and schema
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

def setup_database():
    """Setup pgvector extensions and initialize schema"""

    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"[INFO] Connecting to database...")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[STEP 1] Enabling pgvector extensions...")

        # Enable extensions
        extensions = [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
        ]

        for ext_sql in extensions:
            try:
                cursor.execute(ext_sql)
                print(f"[OK] Executed: {ext_sql}")
            except Exception as e:
                print(f"[WARNING] {ext_sql} - {e}")

        # Verify extensions
        print("\n[STEP 2] Verifying installed extensions...")
        cursor.execute("""
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname IN ('vector', 'uuid-ossp', 'pg_trgm')
        """)

        extensions_installed = cursor.fetchall()
        for ext_name, ext_version in extensions_installed:
            print(f"[OK] {ext_name} version {ext_version} is installed")

        print("\n[STEP 3] Initializing database schema...")

        # Read and execute init_database.sql
        schema_file = os.path.join(os.path.dirname(__file__), 'init_database.sql')

        if not os.path.exists(schema_file):
            print(f"[ERROR] Schema file not found: {schema_file}")
            sys.exit(1)

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema (split by semicolon for individual statements)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                # Print only table/index creation statements
                if 'CREATE TABLE' in statement.upper():
                    table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                    print(f"[OK] Created table: {table_name}")
                elif 'CREATE INDEX' in statement.upper():
                    print(f"[OK] Created index #{i}")
            except Exception as e:
                # Skip if already exists
                if 'already exists' in str(e).lower():
                    continue
                print(f"[WARNING] Statement {i}: {e}")

        print("\n[STEP 4] Verifying database schema...")

        # List all tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"[OK] Found {len(tables)} tables:")
        for (table_name,) in tables:
            print(f"  - {table_name}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] Database setup complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Deploy application: railway up")
        print("2. Check deployment: railway status")
        print("3. View logs: railway logs")

        return True

    except Exception as e:
        print(f"\n[ERROR] Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
