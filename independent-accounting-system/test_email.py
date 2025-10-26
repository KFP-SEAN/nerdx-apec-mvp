"""
Email Service Test Script
이메일 서비스 테스트 스크립트

Usage:
    python test_email.py <recipient_email>

Example:
    python test_email.py your_email@example.com
"""
import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.email_sender.email_service import email_service
from config import settings


async def test_email(recipient_email: str):
    """
    Test email sending via Resend API

    Args:
        recipient_email: Email address to send test email to
    """
    print("\n" + "="*80)
    print("NERDX Email Service Test - Resend API")
    print("="*80 + "\n")

    # Check configuration
    print("Configuration Check:")
    print(f"  - Resend API Key configured: {bool(settings.resend_api_key)}")
    print(f"  - From Email: {settings.smtp_from_email}")
    print(f"  - Recipient Email: {recipient_email}")

    if not settings.resend_api_key:
        print("\n❌ ERROR: RESEND_API_KEY not configured!")
        print("\nPlease set RESEND_API_KEY in your .env file:")
        print("  1. Go to https://resend.com and sign up/login")
        print("  2. Create an API key at https://resend.com/api-keys")
        print("  3. Add to .env file: RESEND_API_KEY=re_your_key_here")
        print("  4. Also set: SMTP_FROM_EMAIL=noreply@yourdomain.com")
        return False

    if not settings.smtp_from_email:
        print("\n❌ ERROR: SMTP_FROM_EMAIL not configured!")
        print("\nPlease set SMTP_FROM_EMAIL in your .env file:")
        print("  SMTP_FROM_EMAIL=noreply@yourdomain.com")
        print("\nNote: The domain must be verified in Resend")
        return False

    print("\n" + "-"*80)
    print("Sending test email...")
    print("-"*80 + "\n")

    # Send test email
    success = await email_service.send_test_email(recipient_email)

    print("\n" + "="*80)
    if success:
        print("✅ TEST PASSED: Email sent successfully!")
        print("\nPlease check your inbox at: " + recipient_email)
        print("\nIf you don't receive the email:")
        print("  1. Check your spam folder")
        print("  2. Verify the domain in Resend dashboard")
        print("  3. Check Resend logs at https://resend.com/emails")
    else:
        print("❌ TEST FAILED: Email sending failed")
        print("\nLast error:")
        print(f"  {email_service.last_error}")
        print("\nTroubleshooting:")
        print("  1. Check that RESEND_API_KEY is valid")
        print("  2. Verify your domain in Resend dashboard")
        print("  3. Check Resend dashboard for errors: https://resend.com/emails")
        print("  4. Check API key permissions")
    print("="*80 + "\n")

    return success


async def test_custom_email(recipient_email: str):
    """
    Test sending a custom email

    Args:
        recipient_email: Email address to send to
    """
    print("\n" + "="*80)
    print("Testing Custom Email")
    print("="*80 + "\n")

    subject = "NERDX Accounting System - Daily Report Test"
    html_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #4A90E2; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .metrics { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .metric-item { margin: 10px 0; }
            .footer { background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>NERDX 독립채산제 시스템</h1>
            <p>Daily Report Test</p>
        </div>
        <div class="content">
            <h2>이메일 전송 테스트</h2>
            <p>이 이메일은 NERDX 독립채산제 시스템의 이메일 전송 기능을 테스트하기 위해 발송되었습니다.</p>

            <div class="metrics">
                <h3>테스트 메트릭</h3>
                <div class="metric-item"><strong>발송 시각:</strong> 2025-10-27 (테스트)</div>
                <div class="metric-item"><strong>이메일 서비스:</strong> Resend API</div>
                <div class="metric-item"><strong>환경:</strong> Railway Production</div>
            </div>

            <p>이 이메일을 받으셨다면 이메일 전송이 정상적으로 작동하고 있습니다.</p>

            <h3>Railway 환경에서의 이메일 전송</h3>
            <ul>
                <li>✅ Railway는 SMTP 포트 (25/587)를 차단합니다</li>
                <li>✅ Resend API를 통한 HTTP 기반 이메일 전송을 사용합니다</li>
                <li>✅ 안정적이고 빠른 이메일 전송이 가능합니다</li>
            </ul>
        </div>
        <div class="footer">
            <p>Powered by Resend API | NERDX Independent Accounting System</p>
        </div>
    </body>
    </html>
    """

    text_body = """
NERDX 독립채산제 시스템 - Daily Report Test

이메일 전송 테스트

이 이메일은 NERDX 독립채산제 시스템의 이메일 전송 기능을 테스트하기 위해 발송되었습니다.

테스트 메트릭:
- 발송 시각: 2025-10-27 (테스트)
- 이메일 서비스: Resend API
- 환경: Railway Production

이 이메일을 받으셨다면 이메일 전송이 정상적으로 작동하고 있습니다.

Railway 환경에서의 이메일 전송:
✅ Railway는 SMTP 포트 (25/587)를 차단합니다
✅ Resend API를 통한 HTTP 기반 이메일 전송을 사용합니다
✅ 안정적이고 빠른 이메일 전송이 가능합니다

Powered by Resend API | NERDX Independent Accounting System
    """

    success = await email_service.send_email(
        to_email=recipient_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body
    )

    if success:
        print("✅ Custom email sent successfully!")
    else:
        print("❌ Custom email sending failed")
        print(f"Error: {email_service.last_error}")

    return success


async def main():
    """Main test runner"""
    if len(sys.argv) < 2:
        print("Usage: python test_email.py <recipient_email>")
        print("Example: python test_email.py your_email@example.com")
        sys.exit(1)

    recipient_email = sys.argv[1]

    # Validate email format (basic check)
    if '@' not in recipient_email or '.' not in recipient_email:
        print("❌ Invalid email format!")
        print(f"Provided: {recipient_email}")
        sys.exit(1)

    # Run tests
    print("\n" + "="*80)
    print("NERDX Email Service Test Suite")
    print("="*80 + "\n")

    # Test 1: Simple test email
    test1_passed = await test_email(recipient_email)

    # Test 2: Custom formatted email
    if test1_passed:
        print("\nRunning additional test with custom email format...")
        test2_passed = await test_custom_email(recipient_email)
    else:
        test2_passed = False
        print("\nSkipping custom email test due to previous failure")

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (Simple Email): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Custom Email): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("="*80 + "\n")

    if test1_passed and test2_passed:
        print("🎉 All tests passed! Email service is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
