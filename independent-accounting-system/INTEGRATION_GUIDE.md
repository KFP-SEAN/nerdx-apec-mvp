# NERDX 독립채산제 시스템 - 실제 연동 가이드

> Salesforce CRM + Odoo ERP 실제 환경 연동 완벽 가이드

---

## 📋 사전 준비사항

### 1. Salesforce CRM 설정

**필요한 정보**:
- Salesforce Instance URL
- Username
- Password
- Security Token
- Consumer Key (Connected App)
- Consumer Secret (Connected App)

#### Salesforce Connected App 생성

1. **Setup → App Manager → New Connected App** 이동
2. 다음 정보 입력:
   - Connected App Name: `NERDX Accounting System`
   - API Name: `NERDX_Accounting_System`
   - Contact Email: 관리자 이메일

3. **Enable OAuth Settings** 체크
   - Callback URL: `http://localhost`
   - Selected OAuth Scopes:
     - `Full access (full)`
     - `Perform requests on your behalf at any time (refresh_token, offline_access)`

4. **Save** 후 Consumer Key와 Consumer Secret 복사

#### Security Token 발급

1. **Setup → Personal Settings → Reset My Security Token**
2. 이메일로 전송된 Security Token 복사

### 2. Odoo ERP 설정

**필요한 정보**:
- Odoo URL (예: https://your-company.odoo.com)
- Database Name
- Username (이메일)
- Password

#### API Access 권한 확인

1. Odoo에 로그인
2. **Settings → Users & Companies → Users**
3. 사용할 계정의 Access Rights 확인:
   - `Accounting / Adviser` 이상 권한 필요
   - `Analytic Accounting` 권한 필요

### 3. PostgreSQL 데이터베이스

**설치 및 설정**:

```bash
# PostgreSQL 설치 (Windows)
# https://www.postgresql.org/download/windows/ 에서 다운로드

# 데이터베이스 생성
psql -U postgres
CREATE DATABASE nerdx_accounting;
CREATE USER nerdx_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nerdx_accounting TO nerdx_user;
\q
```

### 4. SMTP 이메일 설정

**Gmail 사용 시**:

1. Google 계정 → Security → 2-Step Verification 활성화
2. App Password 생성:
   - Security → App passwords
   - Select app: `Mail`
   - Select device: `Other (Custom name)`
   - 이름: `NERDX Accounting`
   - 생성된 16자리 비밀번호 복사

---

## 🔧 환경 설정

### 1. .env 파일 생성

```bash
cd nerdx-apec-mvp/independent-accounting-system
cp .env.example .env
```

### 2. .env 파일 편집

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8003
API_ENVIRONMENT=production

# Salesforce CRM (실제 값으로 교체)
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_USERNAME=your-email@company.com
SALESFORCE_PASSWORD=YourPassword123
SALESFORCE_SECURITY_TOKEN=YourSecurityToken123
SALESFORCE_CONSUMER_KEY=3MVG9...YourConsumerKey
SALESFORCE_CONSUMER_SECRET=ABC123...YourConsumerSecret

# Odoo ERP (실제 값으로 교체)
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your-database-name
ODOO_USERNAME=your-email@company.com
ODOO_PASSWORD=YourOdooPassword123

# PostgreSQL Database
DATABASE_URL=postgresql://nerdx_user:your_password@localhost:5432/nerdx_accounting

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-16-chars
SMTP_FROM_EMAIL=noreply@nerdx.com
SMTP_USE_TLS=True

# Report Configuration
REPORT_GENERATION_HOUR=6
REPORT_TIMEZONE=Asia/Seoul
```

---

## 🚀 시스템 초기화 및 실행

### 1. 데이터베이스 초기화

```bash
cd nerdx-apec-mvp/independent-accounting-system

# 데이터베이스 테이블 생성
python -c "from database import init_db; init_db(); print('Database initialized!')"
```

### 2. 연결 테스트

**Salesforce 연결 테스트**:
```python
python -c "
import asyncio
from services.integrations.salesforce_service import salesforce_service

async def test():
    healthy = await salesforce_service.health_check()
    print(f'Salesforce Connection: {'OK' if healthy else 'FAILED'}')

asyncio.run(test())
"
```

**Odoo 연결 테스트**:
```python
python -c "
import asyncio
from services.integrations.odoo_service import odoo_service

async def test():
    healthy = await odoo_service.health_check()
    print(f'Odoo Connection: {'OK' if healthy else 'FAILED'}')

asyncio.run(test())
"
```

### 3. 애플리케이션 실행

```bash
# 개발 모드 (자동 재시작)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### 4. API 문서 확인

브라우저에서 열기:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **Health Check**: http://localhost:8003/health

---

## 📝 실제 사용 예제

### 1. Cell(셀) 생성

```bash
curl -X POST http://localhost:8003/api/v1/cells/ \
  -H "Content-Type: application/json" \
  -d '{
    "cell_name": "국내셀 - 서울",
    "cell_type": "domestic",
    "manager_name": "김철수",
    "manager_email": "kim@nerdx.com",
    "salesforce_account_ids": ["001xxxxxxxxxxxxxxx"],
    "monthly_revenue_target": 100000000,
    "monthly_gross_profit_target": 30000000
  }'
```

**응답 예시**:
```json
{
  "cell_id": "cell-abc123def456",
  "cell_name": "국내셀 - 서울",
  "cell_type": "domestic",
  "manager_name": "김철수",
  "manager_email": "kim@nerdx.com",
  "odoo_analytic_account_id": 42,
  "odoo_analytic_account_code": "CELL-DOM-DEF456",
  "status": "active"
}
```

### 2. Salesforce 매출 데이터 동기화

```bash
curl -X POST "http://localhost:8003/api/v1/financial/sync/cell-abc123def456/revenue?target_date=2025-10-24"
```

**응답 예시**:
```json
{
  "message": "Synced 15 revenue records",
  "cell_id": "cell-abc123def456",
  "date": "2025-10-24",
  "count": 15
}
```

### 3. Odoo 비용 데이터 동기화

```bash
curl -X POST "http://localhost:8003/api/v1/financial/sync/cell-abc123def456/costs?target_date=2025-10-24"
```

### 4. 일간 재무 요약 조회

```bash
curl -X GET "http://localhost:8003/api/v1/financial/summary/daily/cell-abc123def456?summary_date=2025-10-24"
```

**응답 예시**:
```json
{
  "cell_id": "cell-abc123def456",
  "summary_date": "2025-10-24",
  "total_revenue": 45000000,
  "revenue_count": 15,
  "total_cogs": 30000000,
  "cogs_count": 8,
  "gross_profit": 15000000,
  "gross_profit_margin": 33.33,
  "currency": "KRW"
}
```

### 5. 일간 리포트 생성 및 이메일 발송

```bash
curl -X POST "http://localhost:8003/api/v1/reports/daily/cell-abc123def456/send?report_date=2025-10-24"
```

**응답 예시**:
```json
{
  "message": "Daily report sent successfully",
  "cell_id": "cell-abc123def456",
  "report_date": "2025-10-24"
}
```

---

## 🧪 통합 테스트 실행

### 전체 통합 테스트

```bash
cd nerdx-apec-mvp/independent-accounting-system

# pytest 설치 (아직 안했다면)
pip install pytest pytest-asyncio

# 통합 테스트 실행
pytest tests/test_integration.py -v -s
```

**테스트 항목**:
- ✅ Salesforce 연결 테스트
- ✅ Salesforce Opportunity 조회
- ✅ Odoo 연결 테스트
- ✅ Odoo Analytic Account 생성
- ✅ 데이터베이스 초기화
- ✅ End-to-End 전체 프로세스

---

## 🔍 Salesforce 데이터 매핑

### Opportunity → Revenue Record

| Salesforce Field | 시스템 Field | 설명 |
|-----------------|--------------|------|
| `Id` | `salesforce_opportunity_id` | Opportunity ID |
| `AccountId` | `salesforce_account_id` | 고객 Account ID |
| `CloseDate` | `revenue_date` | 매출 발생일 |
| `Amount` | `revenue_amount` | 매출 금액 |
| `Name` | `description` | 거래 설명 |
| `Product__c` | `product_name` | 제품/서비스명 |
| `Quantity__c` | `quantity` | 수량 |
| `UnitPrice__c` | `unit_price` | 단가 |

**필터 조건**:
- `StageName = 'Closed Won'` (성사된 거래만)
- `CloseDate` 범위 내
- `AccountId`가 Cell의 `salesforce_account_ids`에 포함

---

## 🔍 Odoo 데이터 매핑

### Invoice Line → Cost Record

| Odoo Field | 시스템 Field | 설명 |
|-----------|--------------|------|
| `id` | `odoo_invoice_line_id` | Invoice Line ID |
| `move_id` | `odoo_invoice_id` | Invoice (Move) ID |
| `analytic_account_id` | Cell의 Analytic Account | 셀 연결 |
| `move_id.invoice_date` | `cost_date` | 비용 발생일 |
| `price_subtotal` | `cost_amount` | 비용 금액 |
| `product_id.name` | `related_product` | 제품명 |
| `name` | `description` | 비용 설명 |

**필터 조건**:
- `analytic_account_id`가 Cell의 Analytic Account와 일치
- `move_id.move_type IN ('in_invoice', 'in_refund')` (매입 거래)
- `move_id.state = 'posted'` (확정된 송장만)
- `invoice_date` 범위 내

---

## 🎯 자동화 설정

### 일간 리포트 자동 발송 (Cron)

**Linux/Mac**:
```bash
# crontab 편집
crontab -e

# 매일 오전 6시 실행
0 6 * * * cd /path/to/independent-accounting-system && /path/to/python daily_report_cron.py
```

**Windows (Task Scheduler)**:
1. Task Scheduler 열기
2. Create Basic Task
3. Trigger: Daily at 6:00 AM
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\daily_report_cron.py`

**daily_report_cron.py 스크립트**:
```python
import asyncio
from datetime import date, timedelta
from database import SessionLocal
from services.cell_manager.cell_service import cell_service
from services.report_generator.daily_report_service import daily_report_service

async def main():
    db = SessionLocal()
    try:
        # 모든 활성 Cell 조회
        cells = await cell_service.list_cells(db, status="active")

        # 전일 데이터로 리포트 생성
        report_date = date.today() - timedelta(days=1)

        for cell in cells:
            print(f"Generating report for {cell.cell_name}...")
            await daily_report_service.generate_and_send_report(
                db, cell.cell_id, report_date
            )
            print(f"✓ Report sent to {cell.manager_email}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🐛 문제 해결 (Troubleshooting)

### Salesforce 연결 오류

**증상**: `INVALID_LOGIN` 오류
**해결**:
1. Security Token이 정확한지 확인
2. Password + Security Token 합쳐서 입력 (`Password123YourToken`)
3. IP 제한이 있는 경우 Salesforce에서 IP 화이트리스트 추가

### Odoo 연결 오류

**증상**: `Access Denied` 또는 `404 Not Found`
**해결**:
1. URL 형식 확인 (https://your-company.odoo.com, 끝에 / 없음)
2. Database 이름 확인
3. 사용자 권한 확인 (Accounting / Adviser 이상)

### 이메일 발송 실패

**증상**: `SMTPAuthenticationError`
**해결**:
1. Gmail App Password 사용 (일반 비밀번호 X)
2. "Less secure app access" 비활성화 확인
3. 2-Step Verification 활성화 확인

---

## 📊 모니터링 및 로그

### 로그 확인

애플리케이션 로그는 콘솔에 출력됩니다:

```bash
# 로그 파일로 저장
python main.py > logs/app.log 2>&1

# 실시간 로그 확인
tail -f logs/app.log
```

### API 상태 모니터링

```bash
# Health check
curl http://localhost:8003/health

# Metrics (Prometheus format)
curl http://localhost:8003/metrics
```

---

## 🔐 보안 권장사항

1. **.env 파일 보호**:
   ```bash
   chmod 600 .env
   ```

2. **Git에서 제외**:
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Production 환경**:
   - HTTPS 사용
   - 방화벽 설정
   - API Rate Limiting 설정
   - 정기적인 비밀번호 변경

---

## 📞 지원

문제 발생 시:
1. 로그 파일 확인
2. API Documentation 참조: http://localhost:8003/docs
3. Integration Test 실행: `pytest tests/test_integration.py -v`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-25
**Maintained by**: NERD Development Team
