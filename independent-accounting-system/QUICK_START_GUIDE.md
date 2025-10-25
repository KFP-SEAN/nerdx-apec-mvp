# NERDX 독립채산제 시스템 - Quick Start Guide

**빠른 시작 가이드** - Production 배포까지 30분 안에!

---

## 🚀 1단계: 데모 확인 (이미 완료!)

✅ **완료된 작업**:
- 3개 Cell 생성
- 21건 재무 데이터 생성
- 3개 HTML 일간 리포트 생성
- 데이터베이스 최적화 분석 완료

**생성된 리포트 확인**:
```bash
# 브라우저에서 HTML 리포트 열기
start daily_report_CELL-001_2025-10-25.html
start daily_report_CELL-002_2025-10-25.html
start daily_report_CELL-003_2025-10-25.html
```

---

## 📋 2단계: 환경 설정 (15분)

### 2.1 필수 자격증명 입력

`.env` 파일을 열고 다음 항목을 실제 값으로 변경:

```bash
# 1. Salesforce CRM
SALESFORCE_INSTANCE_URL=https://YOUR_INSTANCE.salesforce.com
SALESFORCE_USERNAME=your_email@company.com
SALESFORCE_PASSWORD=YOUR_PASSWORD
SALESFORCE_SECURITY_TOKEN=YOUR_TOKEN

# 2. Odoo ERP
ODOO_URL=https://YOUR_COMPANY.odoo.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=YOUR_PASSWORD

# 3. Email (Gmail 예시)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=YOUR_APP_SPECIFIC_PASSWORD

# 4. Database (PostgreSQL)
DATABASE_URL=postgresql://nerdx_user:SECURE_PASSWORD@localhost:5432/nerdx_accounting
```

### 2.2 Gmail App Password 생성 (이메일 발송용)

1. https://myaccount.google.com/apppasswords 방문
2. "앱 비밀번호" 생성
3. 생성된 16자리 비밀번호를 `SMTP_PASSWORD`에 입력

### 2.3 Salesforce Security Token 획득

1. Salesforce 로그인
2. Settings → Reset My Security Token
3. 이메일로 받은 토큰을 `SALESFORCE_SECURITY_TOKEN`에 입력

---

## 🗄️ 3단계: PostgreSQL 데이터베이스 설정 (10분)

### Option A: 로컬 PostgreSQL (개발 환경)

```bash
# 1. PostgreSQL 설치 (Windows)
# https://www.postgresql.org/download/windows/

# 2. 데이터베이스 생성
psql -U postgres
CREATE DATABASE nerdx_accounting;
CREATE USER nerdx_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nerdx_accounting TO nerdx_user;
\q

# 3. 스키마 초기화
psql -U nerdx_user -d nerdx_accounting -f init_database.sql

# 4. 확인
psql -U nerdx_user -d nerdx_accounting
\dt  -- 테이블 목록
SELECT * FROM v_active_cells_summary;  -- Sample data 확인
```

### Option B: Railway (Production 권장)

```bash
# 1. Railway CLI 설치 (이미 설치됨)
railway --version

# 2. Railway 로그인
railway login --browserless
# 브라우저에서 인증 링크 클릭

# 3. PostgreSQL Plugin 추가
railway add postgresql

# 4. DATABASE_URL 자동 설정됨 (변경 불필요)
railway variables
```

---

## 🚀 4단계: 애플리케이션 실행 (5분)

### 로컬 실행

```bash
# 1. 디렉토리 이동
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system

# 2. Python 패키지 설치 (이미 완료된 경우 스킵)
pip install fastapi uvicorn sqlalchemy python-dotenv simple-salesforce

# 3. 애플리케이션 시작
python main.py

# 또는 Uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### 실행 확인

```bash
# Health Check
curl http://localhost:8003/health

# API 문서
start http://localhost:8003/docs

# Cells 조회
curl http://localhost:8003/api/cells
```

---

## ✅ 5단계: 일간 리포트 테스트 (5분)

### 수동 실행

```bash
# 데모 스크립트 재실행
python demo_integration.py

# 실제 데이터로 리포트 생성 (구현 후)
python daily_report_cron.py
```

### Cron Job 설정 (매일 오전 6시)

**Linux/Mac**:
```bash
# Crontab 편집
crontab -e

# 매일 오전 6시 실행
0 6 * * * cd /path/to/independent-accounting-system && python daily_report_cron.py
```

**Windows Task Scheduler**:
```powershell
# PowerShell에서 실행
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Users\seans\nerdx-apec-mvp\independent-accounting-system\daily_report_cron.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 6am
Register-ScheduledTask -TaskName "NERDX Daily Reports" -Action $action -Trigger $trigger
```

---

## 🚢 6단계: Production 배포 (Railway)

### 6.1 프로젝트 초기화

```bash
# 1. Railway 프로젝트 생성
railway init

# 2. 환경 변수 설정
railway variables --set SALESFORCE_USERNAME=your_email@company.com
railway variables --set SALESFORCE_PASSWORD=YOUR_PASSWORD
railway variables --set ODOO_URL=https://your-company.odoo.com
railway variables --set SMTP_USERNAME=your_email@gmail.com
railway variables --set SMTP_PASSWORD=YOUR_APP_PASSWORD

# 3. DATABASE_URL은 자동 설정됨 (PostgreSQL plugin)
```

### 6.2 배포 파일 생성

**Procfile** (Railway 배포 명령):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**runtime.txt** (Python 버전):
```
python-3.11.5
```

### 6.3 배포 실행

```bash
# Railway에 배포
railway up

# 배포 상태 확인
railway status

# 로그 확인
railway logs
```

### 6.4 배포 확인

```bash
# Railway URL 확인
railway open

# Health Check
curl https://your-app.railway.app/health

# API 문서
start https://your-app.railway.app/docs
```

---

## 📊 7단계: 모니터링 설정

### Grafana 대시보드 (선택)

```bash
# PostgreSQL Exporter 설치
docker run -d \
  --name postgres-exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://nerdx_user:password@localhost:5432/nerdx_accounting?sslmode=disable" \
  prometheuscommunity/postgres-exporter

# Grafana Dashboard Import
# Dashboard ID: 9628 (PostgreSQL Database)
```

### Sentry 에러 트래킹 (선택)

```bash
# .env 파일에 추가
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

---

## 🧪 8단계: End-to-End 테스트

### 테스트 시나리오

```bash
# 1. Cell 생성
curl -X POST http://localhost:8003/api/cells \
  -H "Content-Type: application/json" \
  -d '{
    "cell_id": "TEST-001",
    "cell_name": "Test Cell",
    "manager_email": "test@nerdx.com"
  }'

# 2. Revenue 추가
curl -X POST http://localhost:8003/api/financial/revenue \
  -H "Content-Type: application/json" \
  -d '{
    "cell_id": "TEST-001",
    "amount": 5000000,
    "revenue_date": "2025-10-25",
    "source": "Test Data"
  }'

# 3. Cost 추가
curl -X POST http://localhost:8003/api/financial/cost \
  -H "Content-Type: application/json" \
  -d '{
    "cell_id": "TEST-001",
    "amount": 3000000,
    "cost_date": "2025-10-25",
    "category": "operational"
  }'

# 4. 일간 리포트 생성
curl -X POST http://localhost:8003/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "cell_id": "TEST-001",
    "report_date": "2025-10-25"
  }'

# 5. 리포트 조회
curl http://localhost:8003/api/reports/TEST-001/2025-10-25
```

---

## 🎯 다음 단계

### 실제 데이터 연동

1. **Salesforce Integration**:
   - `services/integrations/salesforce_service.py` 구현
   - Opportunity → Revenue 자동 동기화
   - 매일 1회 또는 실시간 Webhook

2. **Odoo Integration**:
   - `services/integrations/odoo_service.py` 구현
   - Vendor Bill → Cost 자동 동기화
   - Analytic Account 매핑

3. **AI 임베딩 추가** (선택):
   ```sql
   -- pgvector extension 활성화
   CREATE EXTENSION vector;

   -- 임베딩 저장
   INSERT INTO cell_embeddings (cell_id, report_date, embedding)
   VALUES ('CELL-001', '2025-10-25', '[0.1, 0.2, ...]'::vector);

   -- 유사 Cell 검색
   SELECT cell_id, embedding <-> '[0.1, 0.2, ...]'::vector AS distance
   FROM cell_embeddings
   ORDER BY distance
   LIMIT 5;
   ```

### 대시보드 구축

- Grafana + PostgreSQL
- Power BI 연동
- React/Next.js 프론트엔드

### 알림 설정

- Slack Webhook
- Microsoft Teams
- Discord

---

## 📚 참고 문서

| 문서 | 설명 |
|-----|------|
| `README.md` | 시스템 개요 |
| `DATABASE_OPTIMIZATION_ANALYSIS.md` | DB 선택 및 최적화 |
| `INTEGRATION_GUIDE.md` | Salesforce/Odoo 연동 |
| `DEPLOYMENT_COMPLETE.md` | 배포 체크리스트 |
| `DEMO_EXECUTION_COMPLETE.md` | 데모 실행 보고서 |

---

## 🆘 문제 해결

### PostgreSQL 연결 실패

```bash
# 연결 테스트
psql -U nerdx_user -d nerdx_accounting

# 포트 확인
netstat -an | grep 5432

# PostgreSQL 서비스 시작
sudo service postgresql start  # Linux
net start postgresql-x64-14    # Windows
```

### Salesforce 인증 실패

```bash
# Security Token 재발급
# Settings → Reset My Security Token

# API 버전 확인
curl https://YOUR_INSTANCE.salesforce.com/services/data/
```

### 이메일 발송 실패

```bash
# Gmail App Password 확인
# https://myaccount.google.com/apppasswords

# SMTP 테스트
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email@gmail.com', 'app_password')
print('OK')
"
```

---

## 💰 비용 예상 (월간)

| 서비스 | 옵션 | 비용 |
|--------|------|------|
| **Compute** | Railway Hobby | $5 |
| **Database** | Railway PostgreSQL | $10 |
| **Email** | Gmail (무료) | $0 |
| **Total** | | **$15/월** |

**5년 TCO**: $900 (vs Pinecone $42,000 = **$41,100 절감**)

---

## ✅ 체크리스트

**배포 전 확인사항**:
- [ ] `.env` 파일 모든 자격증명 입력
- [ ] PostgreSQL 데이터베이스 초기화
- [ ] Health check 응답 정상
- [ ] API 문서 접근 가능
- [ ] 테스트 Cell 생성 성공
- [ ] 일간 리포트 생성 성공
- [ ] 이메일 발송 성공

**Production 배포 후**:
- [ ] HTTPS 설정 (Railway 자동)
- [ ] 환경 변수 암호화
- [ ] 백업 스케줄 설정
- [ ] 모니터링 대시보드 구축
- [ ] 에러 트래킹 (Sentry)
- [ ] 로그 수집 (CloudWatch/DataDog)

---

**작성일**: 2025-10-25
**버전**: 1.0
**다음 업데이트**: Production 배포 후
