"""
Email Sending Service
이메일 발송 서비스 - Resend API 사용
"""
import logging
import traceback
from typing import Optional

import resend

from config import settings
from models.report_models import DailyReportEmail

logger = logging.getLogger(__name__)


class EmailService:
    """Email sending service using Resend API"""

    def __init__(self):
        self.from_email = settings.smtp_from_email
        self.resend_api_key = settings.resend_api_key
        self.last_error = None  # Store last error for debugging

        # Set Resend API key
        if self.resend_api_key:
            resend.api_key = self.resend_api_key

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email via Resend API

        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML body
            text_body: Plain text body (optional)

        Returns:
            True if successful
        """
        try:
            # Log configuration (without API key)
            logger.info(f"[Resend] Attempting to send email to {to_email}")
            logger.info(f"[Resend] From: {self.from_email}")
            logger.info(f"[Resend] API Key configured: {bool(self.resend_api_key)}")

            if not self.resend_api_key:
                raise ValueError("Resend API key not configured")

            # Create email parameters
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            }

            # Add text body if provided
            if text_body:
                params["text"] = text_body

            # Send via Resend API
            logger.info(f"[Resend] Sending email to {to_email}...")
            response = resend.Emails.send(params)

            logger.info(f"[Resend] Response: {response}")
            logger.info(f"[Resend] ✅ Email sent successfully to {to_email}")

            self.last_error = None
            return True

        except ValueError as e:
            error_msg = f"Configuration Error: {e}"
            error_detail = f"{error_msg}\n{traceback.format_exc()}"
            logger.error(f"[Resend] ❌ {error_detail}")
            self.last_error = error_detail
            return False

        except Exception as e:
            error_msg = f"Resend API Error: {type(e).__name__}: {e}"
            error_detail = f"{error_msg}\n{traceback.format_exc()}"
            logger.error(f"[Resend] ❌ {error_detail}")
            self.last_error = error_detail
            return False

    async def send_daily_report_email(self, email_data: DailyReportEmail) -> bool:
        """
        Send daily report email

        Args:
            email_data: Daily report email data

        Returns:
            True if successful
        """
        return await self.send_email(
            to_email=email_data.recipient_email,
            subject=email_data.subject,
            html_body=email_data.html_body,
            text_body=email_data.text_body
        )

    async def send_test_email(self, to_email: str) -> bool:
        """Send test email"""
        return await self.send_email(
            to_email=to_email,
            subject="NERDX 독립채산제 시스템 - 테스트 이메일 (Resend)",
            html_body="""
            <html>
            <body>
                <h1>이메일 전송 테스트</h1>
                <p>NERDX 독립채산제 시스템에서 <strong>Resend API</strong>를 통해 발송한 테스트 이메일입니다.</p>
                <p>이 이메일을 받으셨다면 Resend 설정이 정상적으로 작동하는 것입니다.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                Powered by Resend API
                </p>
            </body>
            </html>
            """,
            text_body="NERDX 독립채산제 시스템 - Resend 이메일 전송 테스트"
        )


# Singleton instance
email_service = EmailService()
