# Railway Pro Plan Upgrade Guide

## 현재 상황

✅ **성공적으로 완료된 작업:**
- Database schema 완전 동기화 (UUID types, field names)
- Daily report 데이터 생성 성공
- Railway 배포 성공
- 애플리케이션 정상 작동

❌ **남은 문제:**
- 이메일 발송 실패: `[Errno 101] Network is unreachable`
- 원인: Railway Starter/Free 플랜의 outbound SMTP 포트 (587, 465, 25) 차단

## 해결 방법: Railway Pro Plan 업그레이드

### 업그레이드 혜택
- ✅ Outbound SMTP 포트 허용
- ✅ 더 많은 리소스 (메모리, CPU)
- ✅ 프로덕션 워크로드 지원
- ✅ 우선 지원

### 비용
- **$5/month** (프로젝트당)
- 추가 리소스 사용량에 따라 변동

## 업그레이드 절차 (5분)

### 1. Railway Dashboard 접속
```bash
# 브라우저에서 열기
https://railway.app/account/billing
```

### 2. Billing 페이지에서 플랜 업그레이드
1. Railway Dashboard → Account → Billing
2. "Upgrade to Pro" 버튼 클릭
3. 결제 정보 입력 (신용카드)
4. 플랜 확인 및 승인

### 3. 프로젝트에 Pro Plan 적용
1. Railway Dashboard → Projects
2. `nerdx-accounting-system` 프로젝트 선택
3. Settings → Plan
4. "Pro Plan" 선택

### 4. 배포 확인
업그레이드 후 자동으로 재배포됩니다. 아래 명령어로 상태 확인:

```bash
# Health check
curl https://nerdx-apec-mvp-production.up.railway.app/health

# Daily report 테스트
curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-25" \
  -H "Content-Type: application/json" \
  -d '{"recipients":["sean@koreafnbpartners.com"]}'
```

### 5. 이메일 수신 확인
- Gmail에서 `sean@koreafnbpartners.com` 계정 확인
- 제목: `[Test Operations Cell] 일간 리포트 - 2025-10-25`
- 내용: NERD12 매출/비용 데이터 포함

## 업그레이드 후 검증 체크리스트

- [ ] Railway Pro Plan 활성화 확인
- [ ] 프로젝트에 Pro Plan 적용 확인
- [ ] Health check API 응답 확인
- [ ] Daily report API 호출 성공
- [ ] 이메일 수신 확인 (Gmail inbox)
- [ ] Database 로그에서 "success" 상태 확인

## 대안: 업그레이드 전 임시 테스트

Railway Pro 업그레이드 전에 로컬에서 테스트하려면:

```bash
# 로컬에서 애플리케이션 실행
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system
python main.py

# 로컬에서 daily report 테스트
curl -X POST "http://localhost:8000/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-25" \
  -H "Content-Type: application/json" \
  -d '{"recipients":["sean@koreafnbpartners.com"]}'
```

로컬 환경에서는 SMTP 제한이 없으므로 이메일 발송이 성공해야 합니다.

## 비용 절감 팁

Railway Pro 비용을 최소화하려면:

1. **Sleep on Idle 활성화**: 사용하지 않을 때 자동 중지
2. **Resource Limits 설정**: CPU/메모리 상한 설정
3. **모니터링**: Railway Dashboard에서 사용량 추적

## 예상 월 비용

```
Railway Pro Plan:        $5.00/month
PostgreSQL Database:     ~$2.00/month (예상)
Compute Resources:       ~$3.00/month (예상)
Total:                   ~$10/month
```

실제 비용은 사용량에 따라 다를 수 있습니다.

## 문제 해결

### 업그레이드 후에도 이메일 발송 실패 시

1. **SMTP 환경 변수 확인**:
   ```bash
   railway variables
   ```

2. **Railway 로그 확인**:
   ```bash
   railway logs
   ```

3. **Gmail App Password 재생성**:
   - Gmail → Security → App Passwords
   - 새 App Password 생성
   - Railway 환경 변수 업데이트

## 지원

문제가 지속되면:
- Railway Support: https://railway.app/help
- Railway Discord: https://discord.gg/railway

## 다음 단계

업그레이드 완료 후:
1. ✅ 이메일 발송 테스트
2. ✅ Cron job 설정 (매일 자동 리포트)
3. ✅ Salesforce/Odoo 실제 데이터 연동
4. ✅ 프로덕션 모니터링 설정

---

**작성일**: 2025-10-25
**시스템**: NERDX Independent Accounting System
**배포 환경**: Railway Pro Plan
