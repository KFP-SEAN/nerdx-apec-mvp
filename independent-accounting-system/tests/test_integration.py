"""
Integration Tests for NERDX Independent Accounting System
Salesforce + Odoo 실제 연동 테스트
"""
import pytest
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal

# NOTE: 이 테스트는 실제 Salesforce와 Odoo 자격증명이 필요합니다.
# .env 파일에 실제 자격증명을 설정해야 합니다.


class TestSalesforceIntegration:
    """Salesforce CRM 통합 테스트"""

    @pytest.mark.asyncio
    async def test_salesforce_connection(self):
        """Salesforce 연결 테스트"""
        from services.integrations.salesforce_service import salesforce_service

        # Health check
        is_healthy = await salesforce_service.health_check()
        assert is_healthy, "Salesforce connection failed"
        print("✓ Salesforce connection successful")

    @pytest.mark.asyncio
    async def test_get_opportunities(self):
        """Salesforce Opportunity 조회 테스트"""
        from services.integrations.salesforce_service import salesforce_service

        # 테스트용 Account ID 설정 (실제 Salesforce Account ID로 교체)
        test_account_ids = ["001XXXXXXXXXXXXXXX"]  # TODO: 실제 Account ID로 교체

        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        opportunities = await salesforce_service.get_opportunities_by_account(
            account_ids=test_account_ids,
            start_date=start_date,
            end_date=end_date
        )

        print(f"✓ Retrieved {len(opportunities)} opportunities from Salesforce")

        if opportunities:
            print(f"  - Sample opportunity: {opportunities[0]['Name']}")
            print(f"  - Amount: {opportunities[0].get('Amount', 0)}")


class TestOdooIntegration:
    """Odoo ERP 통합 테스트"""

    @pytest.mark.asyncio
    async def test_odoo_connection(self):
        """Odoo 연결 테스트"""
        from services.integrations.odoo_service import odoo_service

        # Health check
        is_healthy = await odoo_service.health_check()
        assert is_healthy, "Odoo connection failed"
        print("✓ Odoo connection successful")

    @pytest.mark.asyncio
    async def test_create_analytic_account(self):
        """Odoo Analytic Account 생성 테스트"""
        from services.integrations.odoo_service import odoo_service

        test_name = f"TEST-CELL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_code = f"TEST-{datetime.now().strftime('%H%M%S')}"

        account_id = await odoo_service.create_analytic_account(
            name=test_name,
            code=test_code
        )

        assert account_id is not None
        print(f"✓ Created Odoo analytic account: {account_id}")

        # Cleanup: 테스트 계정 조회 확인
        account = await odoo_service.get_analytic_account(account_id)
        assert account['name'] == test_name
        print(f"  - Account verified: {account['name']}")


class TestEndToEndFlow:
    """전체 프로세스 통합 테스트"""

    @pytest.mark.asyncio
    async def test_complete_flow(self):
        """
        완전한 End-to-End 테스트:
        1. Cell 생성
        2. Salesforce에서 매출 동기화
        3. Odoo에서 비용 동기화
        4. 일간 요약 계산
        5. 리포트 생성
        """
        from database import SessionLocal, init_db
        from services.cell_manager.cell_service import cell_service
        from services.financial_tracker.financial_service import financial_service
        from services.report_generator.daily_report_service import daily_report_service
        from models.cell_models import CellCreateRequest, CellType

        # Database 초기화
        init_db()
        db = SessionLocal()

        try:
            print("\n=== End-to-End Integration Test ===\n")

            # Step 1: Create Cell
            print("[Step 1] Creating test cell...")
            cell_request = CellCreateRequest(
                cell_name="테스트 셀 - 통합테스트",
                cell_type=CellType.DOMESTIC,
                manager_name="테스트 매니저",
                manager_email="test@nerdx.com",
                salesforce_account_ids=["001XXXXXXXXXXXXXXX"],  # TODO: 실제 Account ID
                monthly_revenue_target=100000000,
                monthly_gross_profit_target=30000000
            )

            cell = await cell_service.create_cell(db, cell_request)
            assert cell is not None
            print(f"✓ Cell created: {cell.cell_id} - {cell.cell_name}")
            print(f"  - Odoo Account ID: {cell.odoo_analytic_account_id}")

            # Step 2: Sync Revenue from Salesforce
            print("\n[Step 2] Syncing revenue from Salesforce...")
            target_date = date.today() - timedelta(days=1)  # 어제 데이터

            revenue_count = await financial_service.sync_cell_revenue(
                db, cell.cell_id, target_date
            )
            print(f"✓ Synced {revenue_count} revenue records")

            # Step 3: Sync Costs from Odoo
            print("\n[Step 3] Syncing costs from Odoo...")
            cost_count = await financial_service.sync_cell_costs(
                db, cell.cell_id, target_date
            )
            print(f"✓ Synced {cost_count} cost records")

            # Step 4: Calculate Daily Summary
            print("\n[Step 4] Calculating daily financial summary...")
            summary = await financial_service.calculate_daily_summary(
                db, cell.cell_id, target_date
            )
            print(f"✓ Daily summary calculated:")
            print(f"  - Revenue: {summary.total_revenue:,.0f} KRW ({summary.revenue_count} records)")
            print(f"  - COGS: {summary.total_cogs:,.0f} KRW ({summary.cogs_count} records)")
            print(f"  - Gross Profit: {summary.gross_profit:,.0f} KRW ({summary.gross_profit_margin:.1f}%)")

            # Step 5: Generate Report
            print("\n[Step 5] Generating daily report...")
            report_data = await daily_report_service.generate_report_data(
                db, cell.cell_id, target_date
            )
            assert report_data is not None
            print(f"✓ Report generated:")
            print(f"  - Cell: {report_data.cell_name}")
            print(f"  - Date: {report_data.report_date}")
            print(f"  - Daily Profit: {report_data.gross_profit:,.0f} KRW")
            print(f"  - MTD Revenue: {report_data.mtd_revenue:,.0f} KRW")

            print("\n=== Integration Test Completed Successfully! ===\n")

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            raise

        finally:
            db.close()


class TestDatabaseOperations:
    """데이터베이스 작업 테스트"""

    def test_database_initialization(self):
        """데이터베이스 초기화 테스트"""
        from database import init_db, engine

        # Initialize database
        init_db()
        print("✓ Database initialized successfully")

        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            assert result is not None
            print("✓ Database connection successful")


# Main test runner
if __name__ == "__main__":
    print("=" * 60)
    print("NERDX Independent Accounting System")
    print("Integration Test Suite")
    print("=" * 60)
    print()
    print("⚠ Important: Make sure .env file is configured with:")
    print("  - Salesforce credentials")
    print("  - Odoo credentials")
    print("  - PostgreSQL database URL")
    print("  - SMTP email settings")
    print()
    print("=" * 60)
    print()

    # Run tests
    pytest.main([__file__, "-v", "-s"])
