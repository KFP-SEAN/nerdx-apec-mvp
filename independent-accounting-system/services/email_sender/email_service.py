"""
Email Sending Service
이메일 발송 서비스
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config import settings
from models.report_models import DailyReportEmail

logger = logging.getLogger(__name__)


class EmailService:
    """Email sending service using SMTP"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.use_tls = settings.smtp_use_tls

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP

        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML body
            text_body: Plain text body (optional)

        Returns:
            True if successful
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add plain text part if provided
            if text_body:
                part1 = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(part1)

            # Add HTML part
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part2)

            # Connect to SMTP server
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)

            # Login
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            # Send email
            server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
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
            subject="NERDX 독립채산제 시스템 - 테스트 이메일",
            html_body="""
            <html>
            <body>
                <h1>이메일 전송 테스트</h1>
                <p>NERDX 독립채산제 시스템에서 발송한 테스트 이메일입니다.</p>
                <p>이 이메일을 받으셨다면 이메일 설정이 정상적으로 작동하는 것입니다.</p>
            </body>
            </html>
            """,
            text_body="NERDX 독립채산제 시스템 - 이메일 전송 테스트"
        )


# Singleton instance
email_service = EmailService()
