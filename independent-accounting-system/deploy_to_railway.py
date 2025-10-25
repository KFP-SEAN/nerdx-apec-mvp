#!/usr/bin/env python3
"""
NERDX Independent Accounting System - Automated Railway Deployment Script

This script automates the Railway deployment process including:
1. Railway login (opens browser for authentication)
2. Project initialization
3. PostgreSQL database setup
4. Environment variable configuration
5. Database schema initialization
6. Deployment

Usage:
    python deploy_to_railway.py
"""

import os
import sys
import subprocess
import time
from typing import Optional, Dict

class RailwayDeployer:
    """Automated Railway deployment orchestrator"""

    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.railway_cli = "railway"

    def run_command(self, command: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Execute shell command"""
        print(f"\n[EXECUTING] {command}")
        print("=" * 60)

        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_dir,
                    check=check,
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(f"[STDERR] {result.stderr}")
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_dir,
                    check=check
                )

            print("=" * 60)
            return result
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Command failed: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"[STDOUT] {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"[STDERR] {e.stderr}")
            if check:
                raise
            return e

    def check_railway_cli(self) -> bool:
        """Check if Railway CLI is installed"""
        print("\n[STEP 1] Checking Railway CLI installation...")
        try:
            result = self.run_command("railway --version", capture_output=True)
            print(f"[OK] Railway CLI is installed: {result.stdout.strip()}")
            return True
        except:
            print("[ERROR] Railway CLI not installed!")
            print("\nPlease install Railway CLI:")
            print("  Windows (PowerShell): iwr https://railway.app/install.ps1 | iex")
            print("  macOS/Linux: curl -fsSL https://railway.app/install.sh | sh")
            return False

    def railway_login(self) -> bool:
        """Login to Railway (opens browser)"""
        print("\n[STEP 2] Railway Login...")
        print("\nIMPORTANT: This will open your browser for authentication.")
        print("Please complete the login in your browser, then return here.")

        input("\nPress ENTER to open browser for Railway login...")

        try:
            # This will open browser for authentication
            self.run_command("railway login", check=False)

            # Verify login
            print("\n[VERIFYING] Checking Railway authentication...")
            result = self.run_command("railway whoami", check=False, capture_output=True)

            if result.returncode == 0:
                print(f"[OK] Logged in as: {result.stdout.strip()}")
                return True
            else:
                print("[ERROR] Login failed or not completed")
                return False
        except Exception as e:
            print(f"[ERROR] Login error: {e}")
            return False

    def initialize_project(self, project_name: str = "nerdx-accounting-system") -> bool:
        """Initialize Railway project"""
        print(f"\n[STEP 3] Initializing Railway project: {project_name}...")

        try:
            # Check if already linked
            result = self.run_command("railway status", check=False, capture_output=True)
            if result.returncode == 0 and "Project:" in result.stdout:
                print("[OK] Project already linked")
                print(result.stdout)
                return True

            # Initialize new project
            print(f"\n[CREATING] New Railway project: {project_name}")
            self.run_command(f"railway init --name {project_name}")

            print("[OK] Project initialized successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Project initialization failed: {e}")
            return False

    def add_postgresql(self) -> bool:
        """Add PostgreSQL database"""
        print("\n[STEP 4] Adding PostgreSQL database...")

        try:
            self.run_command("railway add --database postgresql")
            print("[OK] PostgreSQL database added")

            # Wait for database to be ready
            print("\n[WAITING] Waiting for database to be ready (10 seconds)...")
            time.sleep(10)

            # Verify DATABASE_URL is set
            result = self.run_command("railway variables", capture_output=True)
            if "DATABASE_URL" in result.stdout:
                print("[OK] DATABASE_URL is configured")
                return True
            else:
                print("[WARNING] DATABASE_URL not found in environment variables")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to add PostgreSQL: {e}")
            return False

    def enable_pgvector(self) -> bool:
        """Enable pgvector extension"""
        print("\n[STEP 5] Enabling pgvector extension...")

        try:
            # Connect to PostgreSQL and enable extensions
            print("\n[INFO] Connecting to Railway PostgreSQL...")

            sql_commands = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp', 'pg_trgm');
"""

            # Create temporary SQL file
            sql_file = os.path.join(self.project_dir, "enable_extensions.sql")
            with open(sql_file, "w") as f:
                f.write(sql_commands)

            # Execute SQL via Railway
            self.run_command(f'railway run psql $DATABASE_URL -f {sql_file}')

            # Clean up
            os.remove(sql_file)

            print("[OK] pgvector extension enabled")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to enable pgvector: {e}")
            print("\n[MANUAL STEP REQUIRED]")
            print("Please run manually:")
            print("  railway connect postgresql")
            print("  CREATE EXTENSION IF NOT EXISTS vector;")
            return False

    def initialize_database_schema(self) -> bool:
        """Initialize database schema"""
        print("\n[STEP 6] Initializing database schema...")

        try:
            schema_file = os.path.join(self.project_dir, "init_database.sql")

            if not os.path.exists(schema_file):
                print(f"[ERROR] Schema file not found: {schema_file}")
                return False

            print(f"[EXECUTING] Running schema initialization...")
            self.run_command(f'railway run psql $DATABASE_URL -f {schema_file}')

            print("[OK] Database schema initialized")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to initialize schema: {e}")
            return False

    def set_environment_variables(self, env_vars: Dict[str, str]) -> bool:
        """Set environment variables"""
        print("\n[STEP 7] Setting environment variables...")

        required_vars = [
            "SALESFORCE_INSTANCE_URL",
            "SALESFORCE_USERNAME",
            "SALESFORCE_PASSWORD",
            "SALESFORCE_SECURITY_TOKEN",
            "ODOO_URL",
            "ODOO_DB",
            "ODOO_USERNAME",
            "ODOO_PASSWORD",
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "SMTP_FROM_EMAIL",
            "SECRET_KEY",
            "JWT_SECRET_KEY"
        ]

        print("\n[INFO] Required environment variables:")
        for var in required_vars:
            print(f"  - {var}")

        print("\n[OPTION 1] Set variables interactively")
        print("[OPTION 2] Set variables from .env file")
        print("[OPTION 3] Skip (set manually later)")

        choice = input("\nChoose option (1/2/3): ").strip()

        if choice == "1":
            # Interactive input
            for var in required_vars:
                value = input(f"Enter {var}: ").strip()
                if value:
                    try:
                        self.run_command(f'railway variables --set {var}="{value}"')
                    except:
                        print(f"[WARNING] Failed to set {var}")

        elif choice == "2":
            # Load from .env file
            env_file = os.path.join(self.project_dir, ".env")
            if os.path.exists(env_file):
                print(f"[LOADING] Environment variables from {env_file}")
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            var_name, var_value = line.split("=", 1)
                            var_name = var_name.strip()
                            var_value = var_value.strip().strip('"').strip("'")

                            if var_name in required_vars:
                                try:
                                    self.run_command(f'railway variables --set {var_name}="{var_value}"')
                                    print(f"[OK] Set {var_name}")
                                except:
                                    print(f"[WARNING] Failed to set {var_name}")
            else:
                print(f"[ERROR] .env file not found: {env_file}")
                return False

        else:
            print("[SKIPPED] You can set variables later using:")
            print('  railway variables --set KEY="VALUE"')

        # Set default application variables
        try:
            self.run_command('railway variables --set API_ENVIRONMENT="production"')
            self.run_command('railway variables --set DEBUG_MODE="False"')
            print("[OK] Application variables set")
        except:
            print("[WARNING] Failed to set some application variables")

        return True

    def deploy(self) -> bool:
        """Deploy to Railway"""
        print("\n[STEP 8] Deploying to Railway...")

        try:
            print("\n[INFO] Starting deployment...")
            print("[INFO] This may take 2-5 minutes...")

            self.run_command("railway up")

            print("\n[OK] Deployment initiated successfully")
            print("\n[NEXT] Monitor deployment with: railway logs")
            return True
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")
            return False

    def verify_deployment(self) -> bool:
        """Verify deployment"""
        print("\n[STEP 9] Verifying deployment...")

        try:
            # Get deployment URL
            result = self.run_command("railway domain", capture_output=True)

            if result.returncode == 0 and result.stdout.strip():
                domain = result.stdout.strip()
                print(f"\n[OK] Application deployed at: https://{domain}")
                print(f"\n[API DOCS] https://{domain}/docs")
                print(f"[HEALTH CHECK] https://{domain}/health")
                return True
            else:
                print("[INFO] Domain not yet assigned")
                print("[MANUAL] Generate domain with: railway domain")
                return False
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            return False

    def run_deployment(self):
        """Run complete deployment workflow"""
        print("=" * 60)
        print("NERDX Independent Accounting System")
        print("Railway Deployment Automation")
        print("=" * 60)

        steps = [
            ("Railway CLI Check", self.check_railway_cli),
            ("Railway Login", self.railway_login),
            ("Initialize Project", self.initialize_project),
            ("Add PostgreSQL", self.add_postgresql),
            ("Enable pgvector", self.enable_pgvector),
            ("Initialize Schema", self.initialize_database_schema),
            ("Set Environment Variables", lambda: self.set_environment_variables({})),
            ("Deploy Application", self.deploy),
            ("Verify Deployment", self.verify_deployment)
        ]

        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n\n{'=' * 60}")
            print(f"STEP {i}/{len(steps)}: {step_name}")
            print('=' * 60)

            try:
                success = step_func()
                if not success:
                    print(f"\n[WARNING] {step_name} completed with warnings")

                    if step_name not in ["Enable pgvector", "Set Environment Variables", "Verify Deployment"]:
                        user_choice = input("\nContinue anyway? (y/n): ").strip().lower()
                        if user_choice != 'y':
                            print("\n[STOPPED] Deployment stopped by user")
                            return False
            except Exception as e:
                print(f"\n[ERROR] {step_name} failed: {e}")
                user_choice = input("\nContinue anyway? (y/n): ").strip().lower()
                if user_choice != 'y':
                    print("\n[STOPPED] Deployment stopped")
                    return False

        print("\n\n" + "=" * 60)
        print("DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print("\n[NEXT STEPS]")
        print("1. Monitor deployment: railway logs")
        print("2. Check status: railway status")
        print("3. Open application: railway open")
        print("4. View API docs: https://your-domain.railway.app/docs")
        print("\n[DOCUMENTATION]")
        print("- RAILWAY_DEPLOYMENT_GUIDE.md: Complete deployment guide")
        print("- PGVECTOR_AI_GUIDE.md: AI integration guide")
        print("- QUICK_START_GUIDE.md: Quick start guide")

        return True


if __name__ == "__main__":
    deployer = RailwayDeployer()

    try:
        success = deployer.run_deployment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
