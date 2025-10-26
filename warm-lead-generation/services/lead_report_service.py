"""
Lead Daily Report Service
Salesforce Lead 데이터 기반 일일 리포트 생성 및 발송
"""
import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings as config


class LeadReportService:
    """Lead 리포트 생성 및 발송 서비스"""

    def __init__(self):
        self.sf_username = config.salesforce_username or os.getenv("SALESFORCE_USERNAME")
        self.sf_password = config.salesforce_password or os.getenv("SALESFORCE_PASSWORD")
        self.sf_security_token = config.salesforce_security_token or os.getenv("SALESFORCE_SECURITY_TOKEN", "")
        self.sf_consumer_key = config.salesforce_consumer_key or os.getenv("SALESFORCE_CONSUMER_KEY")
        self.sf_consumer_secret = config.salesforce_consumer_secret or os.getenv("SALESFORCE_CONSUMER_SECRET")
        self.sf_instance_url = config.salesforce_instance_url or os.getenv("SALESFORCE_INSTANCE_URL")
        self.sf_domain = os.getenv("SALESFORCE_DOMAIN", "login")
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "onboarding@resend.dev")

    def get_salesforce_access_token(self) -> Optional[str]:
        """Salesforce OAuth2 인증"""
        try:
            # OAuth2 password flow
            token_url = f"https://{self.sf_domain}.salesforce.com/services/oauth2/token"

            data = {
                "grant_type": "password",
                "client_id": self.sf_consumer_key,
                "client_secret": self.sf_consumer_secret,
                "username": self.sf_username,
                "password": f"{self.sf_password}{self.sf_security_token}"
            }

            response = requests.post(token_url, data=data, timeout=30)

            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                print(f"Auth error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Failed to get access token: {e}")
            return None

    def get_all_leads(self, access_token: str) -> List[Dict]:
        """Salesforce에서 모든 Lead 조회"""
        try:
            query = """
            SELECT Id, Company, FirstName, LastName, Email, Status, Phone,
                   NBRS_Score__c, NBRS_Tier__c, Brand_Affinity_Score__c,
                   Market_Positioning_Score__c, Digital_Presence_Score__c,
                   Priority_Rank__c, Next_Action__c, CreatedDate, LastModifiedDate
            FROM Lead
            ORDER BY NBRS_Score__c DESC NULLS LAST, CreatedDate DESC
            """

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{self.sf_instance_url}/services/data/v59.0/query",
                headers=headers,
                params={"q": query},
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get("records", [])
            else:
                print(f"Query error: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            print(f"Failed to query leads: {e}")
            return []

    def generate_html_report(self, leads: List[Dict], report_date: date) -> str:
        """HTML 리포트 생성"""

        # Lead 분류
        tier1_leads = [l for l in leads if l.get("NBRS_Tier__c") == "TIER1"]
        tier2_leads = [l for l in leads if l.get("NBRS_Tier__c") == "TIER2"]
        tier3_leads = [l for l in leads if l.get("NBRS_Tier__c") == "TIER3"]
        unscored_leads = [l for l in leads if not l.get("NBRS_Score__c")]

        # 상태별 집계
        status_counts = {}
        for lead in leads:
            status = lead.get("Status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # 최근 추가된 Lead (7일 이내)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_leads = [
            l for l in leads
            if datetime.fromisoformat(l["CreatedDate"].replace("+0000", "+00:00")) > seven_days_ago
        ]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 28px;
                }}
                .header p {{
                    margin: 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                }}
                .summary-card .number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}
                .summary-card .label {{
                    color: #666;
                    font-size: 14px;
                }}
                .section {{
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 20px;
                }}
                .section h2 {{
                    margin: 0 0 20px 0;
                    color: #667eea;
                    font-size: 22px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                th {{
                    background: #f5f5f5;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    border-bottom: 2px solid #ddd;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                .tier1 {{ background-color: #e8f5e9; }}
                .tier2 {{ background-color: #fff9c4; }}
                .tier3 {{ background-color: #ffe0b2; }}
                .tier-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .tier1-badge {{
                    background: #4caf50;
                    color: white;
                }}
                .tier2-badge {{
                    background: #ffc107;
                    color: #333;
                }}
                .tier3-badge {{
                    background: #ff9800;
                    color: white;
                }}
                .score {{
                    font-weight: bold;
                    color: #667eea;
                }}
                .status-new {{ color: #2196f3; }}
                .status-working {{ color: #ff9800; }}
                .status-nurturing {{ color: #9c27b0; }}
                .footer {{
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 NERDX Lead 일일 리포트</h1>
                <p>{report_date.strftime('%Y년 %m월 %d일')} | Salesforce 실시간 데이터</p>
            </div>

            <div class="summary-grid">
                <div class="summary-card">
                    <div class="label">📊 전체 Lead</div>
                    <div class="number">{len(leads)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">⭐ TIER 1 (최우선)</div>
                    <div class="number">{len(tier1_leads)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">🌟 TIER 2 (우선)</div>
                    <div class="number">{len(tier2_leads)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">💫 TIER 3 (일반)</div>
                    <div class="number">{len(tier3_leads)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">🆕 최근 7일 신규</div>
                    <div class="number">{len(recent_leads)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">📝 미평가</div>
                    <div class="number">{len(unscored_leads)}</div>
                </div>
            </div>

            <div class="section">
                <h2>🏆 TIER 1 - 최우선 Lead (NBRS 80+)</h2>
                {self._generate_lead_table(tier1_leads, "tier1") if tier1_leads else "<p style='text-align:center; color:#999;'>TIER 1 Lead가 없습니다.</p>"}
            </div>

            <div class="section">
                <h2>⭐ TIER 2 - 우선 Lead (NBRS 60-79)</h2>
                {self._generate_lead_table(tier2_leads, "tier2") if tier2_leads else "<p style='text-align:center; color:#999;'>TIER 2 Lead가 없습니다.</p>"}
            </div>

            <div class="section">
                <h2>📌 상태별 Lead 현황</h2>
                <table>
                    <tr>
                        <th>상태</th>
                        <th>개수</th>
                    </tr>
                    {''.join([f'<tr><td>{status}</td><td>{count}</td></tr>' for status, count in status_counts.items()])}
                </table>
            </div>

            <div class="section">
                <h2>🆕 최근 7일 신규 Lead</h2>
                {self._generate_lead_table(recent_leads[:10], "recent") if recent_leads else "<p style='text-align:center; color:#999;'>최근 신규 Lead가 없습니다.</p>"}
            </div>

            <div class="footer">
                <p>이 리포트는 NERDX Warm Lead Generation 시스템에서 자동 생성되었습니다.</p>
                <p>Salesforce 데이터 기준: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}</p>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_lead_table(self, leads: List[Dict], tier_class: str) -> str:
        """Lead 테이블 HTML 생성"""
        if not leads:
            return ""

        rows = []
        for lead in leads:
            company = lead.get("Company", "N/A")
            name = f"{lead.get('FirstName', '')} {lead.get('LastName', '')}".strip() or "N/A"
            email = lead.get("Email", "N/A")
            status = lead.get("Status", "N/A")
            nbrs_score = lead.get("NBRS_Score__c")
            nbrs_tier = lead.get("NBRS_Tier__c")
            next_action = lead.get("Next_Action__c", "평가 필요")

            score_html = f"<span class='score'>{nbrs_score:.2f}</span>" if nbrs_score else "<span style='color:#999;'>-</span>"
            tier_badge = ""
            if nbrs_tier == "TIER1":
                tier_badge = "<span class='tier-badge tier1-badge'>TIER 1</span>"
            elif nbrs_tier == "TIER2":
                tier_badge = "<span class='tier-badge tier2-badge'>TIER 2</span>"
            elif nbrs_tier == "TIER3":
                tier_badge = "<span class='tier-badge tier3-badge'>TIER 3</span>"

            rows.append(f"""
                <tr class="{tier_class}">
                    <td><strong>{company}</strong></td>
                    <td>{name}</td>
                    <td>{email}</td>
                    <td>{status}</td>
                    <td>{score_html}</td>
                    <td>{tier_badge}</td>
                    <td>{next_action}</td>
                </tr>
            """)

        table_html = f"""
        <table>
            <tr>
                <th>회사명</th>
                <th>담당자</th>
                <th>이메일</th>
                <th>상태</th>
                <th>NBRS 점수</th>
                <th>등급</th>
                <th>다음 액션</th>
            </tr>
            {''.join(rows)}
        </table>
        """

        return table_html

    def send_email_via_resend(self, to_email: str, subject: str, html_content: str) -> bool:
        """Resend API로 이메일 발송"""
        try:
            import resend

            resend.api_key = self.resend_api_key

            params = {
                "from": f"NERDX Lead Report <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            email = resend.Emails.send(params)
            print(f"✓ Lead report email sent to {to_email}")
            print(f"  Email ID: {email.get('id')}")
            return True

        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False

    def generate_and_send_report(self, recipient_email: str) -> bool:
        """Lead 리포트 생성 및 발송"""
        print("="*60)
        print("NERDX Lead Daily Report Generation")
        print("="*60)
        print(f"Recipient: {recipient_email}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
        print()

        # Step 1: Salesforce 인증
        print("[1/4] Authenticating with Salesforce...")
        access_token = self.get_salesforce_access_token()

        if not access_token:
            print("✗ Failed to authenticate with Salesforce")
            return False

        print("✓ Authentication successful")

        # Step 2: Lead 데이터 조회
        print("\n[2/4] Fetching Lead data from Salesforce...")
        leads = self.get_all_leads(access_token)

        if not leads:
            print("⚠ No leads found")
            # 데이터가 없어도 리포트는 보냄
        else:
            print(f"✓ Found {len(leads)} leads")

        # Step 3: HTML 리포트 생성
        print("\n[3/4] Generating HTML report...")
        report_date = date.today()
        html_content = self.generate_html_report(leads, report_date)
        print(f"✓ Report generated ({len(html_content)} characters)")

        # Step 4: 이메일 발송
        print("\n[4/4] Sending email report...")
        subject = f"🎯 NERDX Lead 일일 리포트 - {report_date.strftime('%Y-%m-%d')}"
        success = self.send_email_via_resend(recipient_email, subject, html_content)

        if success:
            print("\n" + "="*60)
            print("✓ LEAD REPORT SENT SUCCESSFULLY!")
            print("="*60)
            print(f"Total Leads: {len(leads)}")
            print(f"Tier 1: {len([l for l in leads if l.get('NBRS_Tier__c') == 'TIER1'])}")
            print(f"Tier 2: {len([l for l in leads if l.get('NBRS_Tier__c') == 'TIER2'])}")
            print(f"Tier 3: {len([l for l in leads if l.get('NBRS_Tier__c') == 'TIER3'])}")
            print("="*60)
        else:
            print("\n✗ Failed to send report")

        return success


# Singleton instance
lead_report_service = LeadReportService()


if __name__ == "__main__":
    # 테스트 실행
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "sean@koreafnbpartners.com"

    lead_report_service.generate_and_send_report(email)
