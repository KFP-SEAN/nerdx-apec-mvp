#!/usr/bin/env python3
"""
즉시 테스트 리포트 발송 스크립트
Send immediate test report to sean@koreafnbpartners.com
"""
import asyncio
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from services.cell_manager.cell_service import cell_service
from services.financial_tracker.financial_service import financial_service
from services.report_generator.daily_report_service import daily_report_service
from models.cell_models import CellStatus


async def send_test_report():
    """Cell 5에 대한 테스트 리포트를 즉시 발송"""
    print("\n" + "=" * 60)
    print("NERDX 독립채산제 시스템")
    print("테스트 리포트 즉시 발송")
    print("=" * 60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")

    # 어제 날짜로 리포트 생성
    report_date = date.today() - timedelta(days=1)
    print(f"Report Date: {report_date}")
    print(f"Recipient: sean@koreafnbpartners.com")

    db = SessionLocal()

    try:
        # Cell 5 찾기
        cells = await cell_service.list_cells(db, status=CellStatus.ACTIVE)

        if not cells:
            print("\n✗ No active cells found")
            return

        print(f"\nFound {len(cells)} active cells:")
        for cell in cells:
            print(f"  - {cell.cell_id}: {cell.cell_name} ({cell.manager_email})")

        # Cell 5 선택 (cell-5ca00d505e2b)
        target_cell = None
        for cell in cells:
            if "5ca00d505e2b" in cell.cell_id:
                target_cell = cell
                break

        if not target_cell:
            print(f"\n⚠ Cell 5 not found, using first cell: {cells[0].cell_name}")
            target_cell = cells[0]

        print(f"\n[Target Cell]")
        print(f"  ID: {target_cell.cell_id}")
        print(f"  Name: {target_cell.cell_name}")
        print(f"  Manager: {target_cell.manager_name} <{target_cell.manager_email}>")

        # Step 1: 데이터 동기화
        print(f"\n[Step 1] Syncing data for {report_date}...")

        try:
            # Salesforce 매출 동기화
            print(f"  - Syncing revenue from Salesforce...")
            revenue_count = await financial_service.sync_cell_revenue(
                db, target_cell.cell_id, report_date
            )
            print(f"    ✓ {revenue_count} revenue records synced")
        except Exception as e:
            print(f"    ⚠ Revenue sync error: {e}")

        try:
            # Odoo 비용 동기화
            print(f"  - Syncing costs from Odoo...")
            cost_count = await financial_service.sync_cell_costs(
                db, target_cell.cell_id, report_date
            )
            print(f"    ✓ {cost_count} cost records synced")
        except Exception as e:
            print(f"    ⚠ Cost sync error: {e}")

        try:
            # 일간 요약 계산
            print(f"  - Calculating daily summary...")
            summary = await financial_service.calculate_daily_summary(
                db, target_cell.cell_id, report_date
            )
            print(f"    ✓ Summary calculated")
            print(f"      Revenue: {summary.total_revenue:,.0f} KRW ({summary.revenue_count} records)")
            print(f"      COGS: {summary.total_cogs:,.0f} KRW ({summary.cogs_count} records)")
            print(f"      Profit: {summary.gross_profit:,.0f} KRW ({summary.gross_profit_margin:.1f}%)")
        except Exception as e:
            print(f"    ⚠ Summary calculation error: {e}")

        # Step 2: 리포트 생성 및 발송
        print(f"\n[Step 2] Generating and sending report...")

        success = await daily_report_service.generate_and_send_report(
            db, target_cell.cell_id, report_date
        )

        if success:
            print(f"\n" + "=" * 60)
            print(f"✓ TEST REPORT SENT SUCCESSFULLY!")
            print(f"=" * 60)
            print(f"  Recipient: sean@koreafnbpartners.com")
            print(f"  Cell: {target_cell.cell_name}")
            print(f"  Date: {report_date}")
            print(f"\nPlease check your email inbox!")
            print("=" * 60 + "\n")
        else:
            print(f"\n✗ Failed to send test report")
            print("Check the logs above for errors\n")

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(send_test_report())
