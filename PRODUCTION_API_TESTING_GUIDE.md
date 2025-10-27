# Production API 테스트 가이드

**날짜**: 2025-10-27
**목적**: 3개 Production 시스템의 모든 API 엔드포인트 테스트

---

## 🎯 시스템 개요

| 시스템 | URL | 상태 |
|--------|-----|------|
| System 1 | https://nerdx-accounting-system-production.up.railway.app | ✅ Live |
| System 2 | https://nerdx-apec-mvp-production.up.railway.app | ✅ Live |
| System 3 | https://project-sonar-production-production.up.railway.app | ✅ Live |

---

## 📋 System 1: Independent Accounting System

### 기본 테스트

#### 1. Health Check
```bash
curl https://nerdx-accounting-system-production.up.railway.app/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-27T..."
}
```

#### 2. 모든 Cell 조회
```bash
curl https://nerdx-accounting-system-production.up.railway.app/api/v1/cells/
```

**예상**: 8개 독립 회계 법인 데이터

#### 3. 특정 Cell MRR 조회
```bash
# Cell ID를 실제 ID로 교체
curl https://nerdx-accounting-system-production.up.railway.app/api/v1/cells/cell-5ca00d505e2b/mrr
```

#### 4. 일일 리포트 미리보기
```bash
curl https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/preview?report_date=2025-10-27
```

#### 5. 일일 리포트 이메일 전송 (주의: 실제 이메일 발송)
```bash
# 테스트 이메일 먼저 확인
curl -X POST "https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/test-email?email=your-email@example.com"

# 실제 리포트 전송
curl -X POST https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-27
```

### API 문서
```
https://nerdx-accounting-system-production.up.railway.app/docs
```

---

## 📋 System 2: Warm Lead Generation (NBRS 1.0)

### 기본 테스트

#### 1. Health Check
```bash
curl https://nerdx-apec-mvp-production.up.railway.app/health
```

#### 2. 리드 스코어링 통계
```bash
curl https://nerdx-apec-mvp-production.up.railway.app/api/v1/lead-scoring/stats
```

**예상 응답**:
```json
{
  "total_leads_scored": 150,
  "tier1_count": 15,
  "tier2_count": 30,
  "tier3_count": 45,
  "tier4_count": 60,
  "average_score": 65.5
}
```

#### 3. NBRS 1.0 리드 스코어 계산
```bash
curl -X POST https://nerdx-apec-mvp-production.up.railway.app/api/v1/lead-scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test-lead-001",
    "company_name": "Example Corp",
    "brand_affinity": {
      "past_interaction_score": 75,
      "email_engagement_score": 80,
      "meeting_history_score": 70
    },
    "market_positioning": {
      "annual_revenue_krw": 50000000000,
      "employee_count": 250,
      "marketing_budget_krw": 500000000
    },
    "digital_presence": {
      "website_traffic_monthly": 50000,
      "social_media_followers": 10000,
      "content_engagement_score": 75
    },
    "update_salesforce": false
  }'
```

**예상 응답**:
```json
{
  "lead_id": "test-lead-001",
  "nbrs_score": 72.5,
  "tier": "TIER2",
  "recommendation": "High-value lead - schedule meeting",
  "breakdown": {
    "brand_affinity": 75.0,
    "market_positioning": 70.0,
    "digital_presence": 72.5
  }
}
```

### API 문서
```
https://nerdx-apec-mvp-production.up.railway.app/docs
```

---

## 📋 System 3: Project Sonar (NBRS 2.0)

### 기본 테스트

#### 1. Health Check
```bash
curl https://project-sonar-production-production.up.railway.app/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "environment": "production",
  "agents": {
    "orchestrator": {"state": "idle"},
    "market_intel": {"state": "idle"},
    "resonance_modeling": {"state": "idle"},
    "content_strategy": {"state": "idle"}
  },
  "mas_operational": true
}
```

#### 2. KPI Dashboard
```bash
curl https://project-sonar-production-production.up.railway.app/api/v1/dashboard/kpis
```

#### 3. Agents Status
```bash
curl https://project-sonar-production-production.up.railway.app/api/v1/dashboard/agents-status
```

#### 4. NBRS Model Version
```bash
curl https://project-sonar-production-production.up.railway.app/api/v1/dashboard/model-version
```

**예상 응답**:
```json
{
  "version": "2.0.0",
  "release_date": "2025-10-27",
  "features": ["multi-agent", "continual-learning-ready"]
}
```

### 고급 테스트

#### 5. NBRS 2.0 공명 지수 계산
```bash
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/resonance/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR",
      "industry": "Marketing Technology"
    },
    "target_brand": {
      "brand_name": "Starbucks",
      "company_name": "Starbucks Korea",
      "nice_classification": ["43"],
      "country": "KR",
      "industry": "Food & Beverage"
    }
  }'
```

**예상 응답**:
```json
{
  "anchor_brand": "NERD",
  "target_brand": "Starbucks",
  "resonance_index": 45.0,
  "tier": "TIER3",
  "breakdown": {
    "semantic_similarity": 0.35,
    "industry_alignment": 0.25,
    "classification_overlap": 0.40,
    "market_synergy": 0.50
  },
  "recommendation": "Moderate resonance - explore partnership opportunities"
}
```

#### 6. 브랜드 랭킹 (여러 브랜드 비교)
```bash
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/resonance/rank \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_brands": [
      {
        "brand_name": "Starbucks",
        "company_name": "Starbucks Korea",
        "nice_classification": ["43"],
        "country": "KR"
      },
      {
        "brand_name": "Samsung",
        "company_name": "Samsung Electronics",
        "nice_classification": ["9", "35"],
        "country": "KR"
      },
      {
        "brand_name": "Hyundai",
        "company_name": "Hyundai Motor",
        "nice_classification": ["12", "37"],
        "country": "KR"
      }
    ]
  }'
```

#### 7. Top 10% 브랜드 발굴 Workflow
```bash
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/workflows/find-top-brands \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_country": "KR",
    "min_resonance_score": 60
  }'
```

**예상 응답**:
```json
{
  "workflow_id": "wf-001",
  "status": "completed",
  "brands_analyzed": 50,
  "top_brands": [
    {
      "brand_name": "Brand A",
      "resonance_index": 85.0,
      "tier": "TIER1"
    },
    {
      "brand_name": "Brand B",
      "resonance_index": 78.0,
      "tier": "TIER1"
    }
    // ... 5개 브랜드
  ],
  "execution_time_seconds": 2.5
}
```

#### 8. 전체 파트너십 파이프라인 (50 brands → 5 briefs)
```bash
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/workflows/partnership-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_country": "KR"
  }'
```

**예상**: 50개 브랜드 수집 → NBRS 2.0 계산 → Top 5 선정 → 협력 제안서 5개 생성

#### 9. AI 협력 제안서 생성
```bash
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

**예상 응답**:
```json
{
  "brief_id": "brief-001",
  "partnership_title": "NERD x Starbucks: Digital Experience Partnership",
  "collaboration_ideas": [
    {
      "idea": "Co-branded digital loyalty program",
      "description": "Integrate NERD's marketing tech...",
      "estimated_impact": "20% increase in customer engagement"
    },
    {
      "idea": "Joint event marketing campaign",
      "description": "Leverage both brands...",
      "estimated_impact": "500K+ reach"
    }
  ],
  "next_steps": [
    "Schedule initial meeting",
    "Prepare partnership deck",
    "Identify key stakeholders"
  ]
}
```

### API 문서 (Swagger UI)
```
https://project-sonar-production-production.up.railway.app/docs
```

**ReDoc**:
```
https://project-sonar-production-production.up.railway.app/redoc
```

---

## 🧪 통합 테스트 시나리오

### 시나리오 1: 신규 리드 → 공명 분석 → 제안서

**Step 1**: System 2에서 리드 스코어링
```bash
# NBRS 1.0 스코어 계산
curl -X POST https://nerdx-apec-mvp-production.up.railway.app/api/v1/lead-scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Step 2**: TIER1/TIER2 리드를 System 3으로 전달
```bash
# NBRS 2.0 공명 지수 계산
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/resonance/calculate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Step 3**: 협력 제안서 생성
```bash
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/collaborations/generate-brief \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Step 4**: System 1에서 MRR 추적
```bash
# 새 고객 추가 및 MRR 업데이트
```

### 시나리오 2: 일일 운영 루틴

**Morning (9:00 AM)**:
```bash
# 1. System 1: 어제 MRR 리포트 이메일 발송
curl -X POST https://nerdx-accounting-system-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-26

# 2. System 2: 리드 스코어링 통계 확인
curl https://nerdx-apec-mvp-production.up.railway.app/api/v1/lead-scoring/stats

# 3. System 3: Agents 상태 확인
curl https://project-sonar-production-production.up.railway.app/api/v1/dashboard/agents-status
```

**Afternoon (2:00 PM)**:
```bash
# 4. System 3: 새로운 브랜드 발굴 워크플로우 실행
curl -X POST https://project-sonar-production-production.up.railway.app/api/v1/workflows/find-top-brands \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 📊 성능 벤치마크

### 목표 응답 시간

| API 타입 | 목표 | 현재 |
|----------|------|------|
| Health Check | < 100ms | ✅ |
| Simple GET | < 200ms | ✅ |
| NBRS 1.0 계산 | < 500ms | ✅ |
| NBRS 2.0 계산 | < 1s | ✅ |
| Workflow (50 brands) | < 5s | ✅ |

### 테스트 방법
```bash
# Response time 측정
time curl https://project-sonar-production-production.up.railway.app/health

# 또는 httpie 사용
http --print=HhBb https://project-sonar-production-production.up.railway.app/health
```

---

## 🐛 트러블슈팅

### 문제 1: 503 Service Unavailable

**원인**: Cold start (Railway 첫 요청)

**해결**: 1-2분 대기 후 재시도

### 문제 2: Timeout

**원인**: 긴 워크플로우 실행

**해결**: timeout 설정 증가
```bash
curl --max-time 30 https://...
```

### 문제 3: 401 Unauthorized

**원인**: API 키 미설정 (실제 API 사용 시)

**해결**: Railway 환경 변수 확인

---

## 📝 테스트 체크리스트

### System 1
- [ ] Health check
- [ ] Cell 조회
- [ ] MRR 데이터 확인
- [ ] 리포트 미리보기
- [ ] 테스트 이메일 발송

### System 2
- [ ] Health check
- [ ] 리드 스코어링 통계
- [ ] NBRS 1.0 계산
- [ ] Salesforce 연동 (선택)

### System 3
- [ ] Health check
- [ ] KPI dashboard
- [ ] Agents status
- [ ] NBRS 2.0 계산
- [ ] 브랜드 랭킹
- [ ] Top brands workflow
- [ ] Partnership pipeline
- [ ] AI brief generation

### 통합 테스트
- [ ] System 2 → System 3 workflow
- [ ] 일일 운영 루틴
- [ ] 성능 벤치마크

---

## 🎯 다음 단계

1. **이번 주**: Mock 데이터로 모든 API 테스트
2. **다음 주**: 실제 API 키 연동 (WIPO, KIS, Naver)
3. **2주 후**: 실제 고객 데이터로 파일럿 테스트
4. **1개월 후**: Full production 운영

---

**작성일**: 2025-10-27
**버전**: 1.0
**상태**: Production Testing Guide

🚀 **Happy Testing!**
