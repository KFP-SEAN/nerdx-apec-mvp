# API 키 연동 가이드

**날짜**: 2025-10-27
**목적**: Production 시스템에 실제 API 키 연동하기

---

## 🎯 개요

현재 시스템은 Mock 데이터로 작동하고 있습니다. 실제 데이터를 사용하려면 다음 API 키가 필요합니다:

### 필수 API 키

| API | 용도 | 시스템 | 우선순위 |
|-----|------|--------|----------|
| **Resend** | 이메일 발송 | System 1 | 🔴 High |
| **Anthropic Claude** | AI 제안서 생성 | System 3 | 🟡 Medium |
| **WIPO** | 상표 데이터 | System 3 | 🟢 Low |
| **KIS** | 기업 데이터 | System 3 | 🟢 Low |
| **Naver News** | 뉴스 데이터 | System 3 | 🟢 Low |

---

## 📋 System 1: Independent Accounting System

### 필요 API: Resend (이메일 발송)

#### Step 1: Resend API 키 발급

1. **Resend 웹사이트 접속**
   ```
   https://resend.com/
   ```

2. **회원가입/로그인**
   - GitHub 또는 Google 계정으로 가입

3. **API 키 생성**
   - Dashboard → API Keys
   - "Create API Key" 클릭
   - Name: "NERDX Production"
   - 키 복사 (예: `re_xxxxxxxxxxxxxxxxxxxxxxxx`)

4. **발신 도메인 설정** (선택사항, 더 높은 전달률)
   - Settings → Domains
   - Add Domain
   - DNS 레코드 추가 (Resend 가이드 따라)

#### Step 2: Railway 환경 변수 설정

1. **Railway Dashboard 접속**
   ```
   https://railway.app/dashboard
   ```

2. **System 1 프로젝트 선택**
   - "nerdx-accounting-system" 프로젝트 클릭

3. **환경 변수 추가**
   - Settings → Variables 탭
   - "New Variable" 클릭

   ```bash
   # Resend API Key
   RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxx

   # 발신 이메일 (verified domain 또는 @resend.dev)
   SMTP_FROM_EMAIL=onboarding@resend.dev
   # 또는 own domain:
   # SMTP_FROM_EMAIL=noreply@yourdomain.com
   ```

4. **재배포 대기**
   - 환경 변수 저장 시 자동 재배포 (2-3분)

#### Step 3: 테스트

```bash
# 테스트 이메일 발송
curl -X POST "https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/test-email?email=your-email@example.com"

# 성공 시 예상 응답:
{
  "success": true,
  "message": "Test email sent successfully",
  "recipient": "your-email@example.com"
}
```

#### Step 4: 실제 리포트 발송

```bash
# 일일 리포트 이메일 발송
curl -X POST "https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-27"
```

---

## 📋 System 3: Project Sonar (NBRS 2.0)

### 필요 API 키

1. **Anthropic Claude** (AI 제안서 생성)
2. **WIPO** (상표 데이터)
3. **KIS** (기업 데이터)
4. **Naver News** (뉴스 데이터)

---

### 1. Anthropic Claude API

#### Step 1: API 키 발급

1. **Anthropic Console 접속**
   ```
   https://console.anthropic.com/
   ```

2. **회원가입/로그인**
   - Email로 가입

3. **API 키 생성**
   - API Keys 메뉴
   - "Create Key" 클릭
   - Name: "NERDX Project Sonar"
   - 키 복사 (예: `sk-ant-api03-xxxxxxxxxxxxxx`)

4. **크레딧 충전** (필요시)
   - Billing → Add Credits
   - 최소 $5 (약 6,000 KRW)

#### Step 2: Railway 환경 변수 설정

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxx
```

#### Step 3: 테스트

```bash
# AI 협력 제안서 생성 테스트
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/collaborations/generate-brief \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX"
    },
    "target_brand": {
      "brand_name": "Starbucks",
      "company_name": "Starbucks Korea"
    },
    "resonance_data": {
      "resonance_index": 75.0,
      "tier": "TIER2"
    }
  }'
```

**예상**: AI가 생성한 3-5개의 협력 아이디어

---

### 2. WIPO API (상표 데이터)

#### Step 1: API 접근 신청

1. **WIPO Global Brand Database 접속**
   ```
   https://www.wipo.int/branddb/en/
   ```

2. **API 문서 확인**
   ```
   https://www.wipo.int/branddb/en/api_help.jsp
   ```

3. **API 키 신청**
   - Contact form으로 API 접근 요청
   - 목적: "Brand resonance analysis for partnership matching"
   - 승인까지: 1-2주 소요

#### Step 2: Railway 환경 변수 설정

```bash
# WIPO API
WIPO_API_URL=https://www.wipo.int/branddb/en/
WIPO_API_KEY=your_wipo_api_key
```

#### 대안: Mock 데이터 계속 사용

WIPO API 승인 전까지는 현재 Mock 데이터를 계속 사용할 수 있습니다.

---

### 3. KIS API (기업 데이터)

#### Step 1: KIS (한국신용평가정보) API 신청

1. **KIS 웹사이트 접속**
   ```
   https://www.kis.co.kr/
   ```

2. **API 서비스 신청**
   - 기업정보 조회 API 신청
   - 사업자등록증 필요
   - 비용: 월 약 50만원 ~ (사용량에 따라)

3. **API 키 발급**
   - API Key & Secret 발급

#### Step 2: Railway 환경 변수 설정

```bash
# KIS API
KIS_API_URL=https://api.kis.co.kr
KIS_API_KEY=your_kis_api_key
KIS_API_SECRET=your_kis_api_secret
```

#### 대안: 공개 데이터 사용

KIS API 구독 전까지:
- Open API (공공데이터포털)
- 크롤링 (주의: 저작권 확인 필요)
- Mock 데이터

---

### 4. Naver News API

#### Step 1: Naver Developers API 키 발급

1. **Naver Developers 접속**
   ```
   https://developers.naver.com/
   ```

2. **애플리케이션 등록**
   - Application → 애플리케이션 등록
   - Application Name: "NERDX Project Sonar"
   - 사용 API: 검색 (뉴스)

3. **Client ID & Secret 확인**
   - Client ID: `xxxxxxxxxxxxxx`
   - Client Secret: `xxxxxxxxxx`

#### Step 2: Railway 환경 변수 설정

```bash
# Naver News API
NEWS_API_URL=https://openapi.naver.com/v1/search/news.json
NEWS_API_CLIENT_ID=your_naver_client_id
NEWS_API_CLIENT_SECRET=your_naver_client_secret
```

#### Step 3: 테스트

```python
# Python 테스트 스크립트
import requests

url = "https://openapi.naver.com/v1/search/news.json"
headers = {
    "X-Naver-Client-Id": "your_client_id",
    "X-Naver-Client-Secret": "your_client_secret"
}
params = {
    "query": "NERDX 브랜드 협력",
    "display": 10
}

response = requests.get(url, headers=headers, params=params)
print(response.json())
```

---

## 🔧 Railway 환경 변수 설정 전체 요약

### System 1 Variables
```bash
# Email Service (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=onboarding@resend.dev

# Database (이미 설정됨)
DATABASE_URL=postgresql://...

# Environment
API_ENVIRONMENT=production
API_HOST=0.0.0.0
```

### System 3 Variables
```bash
# API Configuration (이미 설정됨)
API_ENVIRONMENT=production
API_HOST=0.0.0.0
NBRS_MODEL_VERSION=2.0.0
NBRS_UPDATE_FREQUENCY=daily

# AI Service
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxx

# Data Sources (선택사항 - 승인 후)
WIPO_API_URL=https://www.wipo.int/branddb/en/
WIPO_API_KEY=your_wipo_key

KIS_API_URL=https://api.kis.co.kr
KIS_API_KEY=your_kis_key
KIS_API_SECRET=your_kis_secret

NEWS_API_URL=https://openapi.naver.com/v1/search/news.json
NEWS_API_CLIENT_ID=your_naver_client_id
NEWS_API_CLIENT_SECRET=your_naver_client_secret
```

---

## 📊 API 비용 예상

### 월간 비용 (예상)

| API | 무료 티어 | 유료 시작 | 예상 월 비용 |
|-----|-----------|-----------|--------------|
| Resend | 3,000 emails/month | $20/month | $0 ~ $20 |
| Anthropic Claude | $5 credit | Pay-as-you-go | $20 ~ $50 |
| WIPO | API access 요청 필요 | TBD | $0 (공개 API) |
| KIS | - | ~500,000 KRW/month | 협상 필요 |
| Naver News | 25,000 calls/day | Free | $0 |

**총 예상 비용**: 약 $40 ~ $100/month (약 50,000 ~ 130,000 KRW)

---

## 🎯 우선순위별 연동 계획

### Phase 1: 즉시 (이번 주)
1. ✅ **Resend** - 이메일 발송 (System 1)
2. ✅ **Anthropic Claude** - AI 제안서 생성 (System 3)

**이유**: 핵심 기능, 비용 저렴, 빠른 승인

### Phase 2: 2주 내
3. **Naver News** - 뉴스 데이터 (System 3)

**이유**: 무료, 즉시 승인, 한국 시장 중요

### Phase 3: 1개월 내
4. **WIPO** - 상표 데이터 (System 3)
5. **KIS** - 기업 데이터 (System 3)

**이유**: 승인 기간 필요, 비용 협상 필요

---

## 🧪 API 연동 테스트 체크리스트

### Resend (System 1)
- [ ] API 키 발급
- [ ] Railway 환경 변수 설정
- [ ] 테스트 이메일 발송 성공
- [ ] 실제 리포트 이메일 수신 확인

### Anthropic Claude (System 3)
- [ ] API 키 발급
- [ ] Railway 환경 변수 설정
- [ ] AI 제안서 생성 테스트
- [ ] 응답 품질 확인

### Naver News (System 3)
- [ ] Client ID/Secret 발급
- [ ] Railway 환경 변수 설정
- [ ] 뉴스 검색 테스트
- [ ] 데이터 파싱 확인

### WIPO (System 3)
- [ ] API 접근 신청
- [ ] 승인 대기
- [ ] API 키 발급
- [ ] 상표 데이터 조회 테스트

### KIS (System 3)
- [ ] 서비스 상담
- [ ] 계약 체결
- [ ] API 키 발급
- [ ] 기업 데이터 조회 테스트

---

## 🐛 트러블슈팅

### 문제 1: Resend 이메일이 스팸함으로 이동

**해결책**:
1. Own domain 설정 (SPF, DKIM 레코드)
2. Verified sender 등록
3. 첫 이메일에 "Add to contacts" 요청

### 문제 2: Anthropic API Rate Limit

**해결책**:
1. Retry logic 구현 (exponential backoff)
2. Tier 업그레이드 요청
3. 캐싱 구현

### 문제 3: Naver API 일일 한도 초과

**해결책**:
1. 애플리케이션 추가 등록 (다중 Client ID)
2. 캐싱으로 중복 호출 방지
3. Enterprise 플랜 문의

---

## 📞 지원 연락처

### Resend Support
- Website: https://resend.com/support
- Discord: https://discord.gg/resend

### Anthropic Support
- Email: support@anthropic.com
- Docs: https://docs.anthropic.com/

### Naver Developers
- 고객센터: https://developers.naver.com/support
- 문의: dl_platformcenter@naver.com

---

## 🎉 다음 단계

**API 연동 후**:
1. Mock 데이터 → 실제 데이터 전환 확인
2. 성능 벤치마크 재측정
3. 비용 모니터링 시작
4. 고객 파일럿 테스트 시작

---

**작성일**: 2025-10-27
**버전**: 1.0
**상태**: API Integration Guide

🔐 **Let's integrate real APIs!**
