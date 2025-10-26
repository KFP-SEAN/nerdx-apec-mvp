# Daily Report Automation Setup

## 📅 스케줄: 매일 한국시간 오전 6시 (KST 06:00)

---

## ✅ 설정 완료

### 1. GitHub Actions 자동화 (권장)

**파일**: `.github/workflows/daily-report.yml`

**스케줄**:
- UTC 21:00 (전날) = KST 06:00 (다음날)
- Cron: `0 21 * * *`

**동작**:
- 매일 자동으로 실행
- Cell 5의 어제 데이터로 리포트 생성
- sean@koreafnbpartners.com으로 이메일 발송

**수동 실행**:
1. GitHub Repository 이동: https://github.com/KFP-SEAN/nerdx-apec-mvp
2. Actions 탭 클릭
3. "Daily Report Automation" 워크플로우 선택
4. "Run workflow" 버튼 클릭

---

## 🔄 API 엔드포인트

### 일일 리포트 발송
```bash
POST /api/v1/reports/daily/{cell_id}/send?report_date={YYYY-MM-DD}

# 예시
curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-26" \
  -H "Content-Type: application/json"

# Response
{
  "message": "Daily report sent successfully",
  "cell_id": "cell-5ca00d505e2b",
  "report_date": "2025-10-26"
}
```

---

## 🧪 테스트

### 즉시 테스트 리포트 발송
```bash
# 오늘 테스트
curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=$(date -d yesterday +%Y-%m-%d)" \
  -H "Content-Type: application/json"

# Windows PowerShell
$yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=$yesterday" -H "Content-Type: application/json"
```

### 테스트 이메일 발송
```bash
curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/test-email?email=sean@koreafnbpartners.com"
```

---

## 📊 리포트 내용

**발송 대상**: sean@koreafnbpartners.com (Cell 5 Manager)

**리포트 포함 내용**:
1. **일간 실적**
   - 총 매출 (Revenue)
   - 총 원가 (COGS)
   - 매출총이익 (Gross Profit)
   - 매출총이익률 (%)

2. **월간 누적 실적**
   - MTD 매출
   - MTD 원가
   - MTD 매출총이익
   - MTD 매출총이익률

3. **데이터 상세**
   - 매출 건수
   - 원가 건수
   - 리포트 생성 시간

---

## 🔧 대안 방법

### Option 1: External Cron Service (현재 권장)

**GitHub Actions** (이미 설정됨)
- ✅ 무료
- ✅ 설정 간단
- ✅ 로그 확인 가능
- ✅ 수동 실행 가능

### Option 2: EasyCron / Cron-job.org

무료 외부 cron 서비스:

1. https://www.easycron.com 가입
2. 새 cron job 생성:
   - URL: `https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=YESTERDAY`
   - Schedule: Daily at 06:00 (KST)
   - Method: POST
3. 저장 및 활성화

### Option 3: Railway에서 별도 Cron 서비스

Railway에 별도 cron 서비스 배포:

```python
# cron_service.py
import asyncio
import schedule
import time
from datetime import date, timedelta
import requests

def send_daily_reports():
    report_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date={report_date}"

    response = requests.post(url)
    print(f"Report sent: {response.json()}")

# 매일 06:00 KST (UTC+9)
schedule.every().day.at("06:00").do(send_daily_reports)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📝 로그 확인

### GitHub Actions 로그
1. Repository → Actions 탭
2. 최근 workflow run 클릭
3. 상세 로그 확인

### Railway 로그
```bash
railway logs --service nerdx-apec-mvp | grep -i "daily report"
```

### API 로그 (Railway Dashboard)
1. https://railway.app/dashboard
2. nerdx-accounting-system 프로젝트
3. nerdx-apec-mvp 서비스
4. Deployments → Logs

---

## ✅ 확인 사항

- [x] GitHub Actions workflow 생성
- [x] API 엔드포인트 작동 확인
- [x] 테스트 리포트 발송 성공
- [x] Cell 5 설정 확인 (cell-5ca00d505e2b)
- [x] 이메일 서비스 설정 (Resend API)
- [x] Resend API 키 설정 확인

---

## 🚨 트러블슈팅

### 리포트가 안 오는 경우

1. **GitHub Actions 확인**
   ```
   Repository → Actions → Daily Report Automation
   ```
   - 워크플로우가 실행되었는지 확인
   - 에러 로그 확인

2. **수동으로 API 호출**
   ```bash
   curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-26"
   ```

3. **이메일 서비스 확인**
   - Resend Dashboard: https://resend.com/emails
   - Railway 로그에서 이메일 발송 확인

4. **스팸 폴더 확인**
   - Resend test domain을 사용중이므로 스팸으로 분류될 수 있음

---

## 📧 이메일 설정 개선

현재 발송 주소: `onboarding@resend.dev` (Resend 테스트 도메인)

**프로덕션 개선**:
1. Resend에서 커스텀 도메인 설정
2. 예: `noreply@nerdx.com` 또는 `reports@koreafnbpartners.com`
3. DNS 레코드 추가로 도메인 인증
4. Railway 환경 변수 업데이트: `SMTP_FROM_EMAIL`

---

## 📅 타임존 참고

- **한국 시간 (KST)**: UTC+9
- **UTC**: KST - 9시간
- **KST 06:00** = **UTC 21:00 (전날)**

예시:
- 한국: 2025-10-27 06:00 → 2025-10-26 데이터 리포트
- UTC: 2025-10-26 21:00 → 2025-10-26 데이터 리포트

---

**설정 완료일**: 2025-10-27
**다음 자동 실행**: 매일 한국시간 06:00
