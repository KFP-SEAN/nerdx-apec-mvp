"""
Daily Report Automation Script
일간 리포트 자동 생성 및 발송 스크립트

이 스크립트를 Cron/Task Scheduler로 매일 오전 6시에 실행하세요.

Usage:
    python daily_report_cron.py

Windows Task Scheduler:
    - Program: python.exe
    - Arguments: C:\path\to\daily_report_cron.py
    - Trigger: Daily at 6:00 AM

Linux Cron:
    0 6 * * * cd /path/to && /path/to/python daily_report_cron.py
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


async def sync_all_cells_data(db, report_date: date):
    """모든 활성 Cell의 데이터 동기화"""
    print(f"\n[Data Sync] Syncing data for {report_date}")
    print("=" * 60)

    # 모든 활성 Cell 조회
    cells = await cell_service.list_cells(db, status=CellStatus.ACTIVE)

    if not cells:
        print("⚠ No active cells found")
        return

    print(f"Found {len(cells)} active cells")

    for cell in cells:
        print(f"\n[{cell.cell_name}]")

        try:
            # Salesforce 매출 동기화
            print(f"  - Syncing revenue from Salesforce...")
            revenue_count = await financial_service.sync_cell_revenue(
                db, cell.cell_id, report_date
            )
            print(f"    ✓ {revenue_count} revenue records synced")

            # Odoo 비용 동기화
            print(f"  - Syncing costs from Odoo...")
            cost_count = await financial_service.sync_cell_costs(
                db, cell.cell_id, report_date
            )
            print(f"    ✓ {cost_count} cost records synced")

            # 일간 요약 계산
            print(f"  - Calculating daily summary...")
            summary = await financial_service.calculate_daily_summary(
                db, cell.cell_id, report_date
            )
            print(f"    ✓ Summary calculated: {summary.gross_profit:,.0f} KRW profit")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue


async def generate_all_reports(db, report_date: date):
    """모든 활성 Cell의 리포트 생성 및 이메일 발송"""
    print(f"\n[Report Generation] Generating reports for {report_date}")
    print("=" * 60)

    # 모든 활성 Cell 조회
    cells = await cell_service.list_cells(db, status=CellStatus.ACTIVE)

    success_count = 0
    failure_count = 0

    for cell in cells:
        print(f"\n[{cell.cell_name}]")
        print(f"  Manager: {cell.manager_name} <{cell.manager_email}>")

        try:
            # 리포트 생성 및 발송
            success = await daily_report_service.generate_and_send_report(
                db, cell.cell_id, report_date
            )

            if success:
                print(f"  ✓ Report sent successfully")
                success_count += 1
            else:
                print(f"  ✗ Failed to send report")
                failure_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failure_count += 1

    print(f"\n" + "=" * 60)
    print(f"Report Generation Summary:")
    print(f"  - Success: {success_count}")
    print(f"  - Failed: {failure_count}")
    print(f"  - Total: {success_count + failure_count}")


async def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("NERDX 독립채산제 시스템")
    print("일간 리포트 자동 생성 스크립트")
    print("=" * 60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 전일 데이터로 리포트 생성
    report_date = date.today() - timedelta(days=1)
    print(f"Report Date: {report_date}")

    db = SessionLocal()

    try:
        # Step 1: 데이터 동기화
        await sync_all_cells_data(db, report_date)

        # Step 2: 리포트 생성 및 발송
        await generate_all_reports(db, report_date)

        print("\n" + "=" * 60)
        print("✓ Daily report automation completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
