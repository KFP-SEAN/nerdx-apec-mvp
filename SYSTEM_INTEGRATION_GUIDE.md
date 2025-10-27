# NERDX APEC MVP - 시스템 통합 가이드

**버전**: 1.0.0-MVP
**작성일**: 2025-10-27
**목표**: MRR 5억 → 1000억 KRW (200x 성장)

---

## 📊 시스템 개요

NERDX APEC MVP는 3개의 핵심 시스템으로 구성된 통합 플랫폼입니다:

```
┌─────────────────────────────────────────────────────────────┐
│                    NERDX APEC Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   System 1   │  │   System 2   │  │   System 3   │    │
│  │              │  │              │  │              │    │
│  │ Independent  │  │ Warm Lead    │  │   Project    │    │
│  │ Accounting   │  │ Generation   │  │    Sonar     │    │
│  │              │  │              │  │              │    │
│  │   Port:      │  │   Port:      │  │   Port:      │    │
│  │    8003      │  │    8004      │  │    8005      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 System 1: Independent Accounting System

### 목적
독립 회계법인 Cell 단위 MRR 추적 및 보고

### 핵심 기능
- **Cell 기반 회계**: 8개 Cell 독립 MRR 추적
- **자동 일일 보고서**: 매일 오전 9시 이메일 발송
- **고객 관리**: 활성/비활성 고객 구분
- **재무 메트릭**: MRR, Churn Rate, ARPU 계산

### 기술 스택
- FastAPI + PostgreSQL
- Resend (이메일)
- Jinja2 (HTML 템플릿)

### 배포 정보
- **Port**: 8003
- **Railway URL**: `nerdx-accounting-system-production.up.railway.app`
- **Database**: PostgreSQL (Railway 제공)
- **상태**: ✅ Production 배포 완료

### 주요 엔드포인트
```
GET  /health
GET  /api/v1/reports/dashboard
POST /api/v1/reports/daily/{cell_name}/send
GET  /api/v1/customers/
POST /api/v1/customers/
```

### 데이터베이스 스키마
- `customers`: 고객 정보 (6개 테이블)
- `transactions`: 거래 내역 (6개 테이블)
- `monthly_reports`: 월간 리포트 (6개 테이블)

---

## 🎯 System 2: Warm Lead Generation (NBRS 1.0)

### 목적
상위 10% Warm Lead 발굴 → MRR 500M KRW 달성

### 핵심 기능
- **NBRS 1.0 스코어링**: Brand Affinity + Market Positioning + Digital Presence
- **Salesforce 연동**: Platform Events로 자동 동기화
- **Helios 데이터 연동**: 기업 데이터 enrichment
- **티어 분류**: TIER1-4 자동 분류

### NBRS 1.0 구성요소
| 요소 | 가중치 | 데이터 소스 |
|------|--------|-------------|
| Brand Affinity | 40% | 과거 상호작용, 이메일, 미팅 |
| Market Positioning | 35% | 매출, 직원수, 마케팅 예산 |
| Digital Presence | 25% | 웹사이트, 소셜미디어, 앱 |

### 기술 스택
- FastAPI + PostgreSQL
- Salesforce API (simple-salesforce)
- Helios API

### 배포 정보
- **Port**: 8004
- **Railway URL**: `nerdx-apec-mvp-production.up.railway.app`
- **Database**: PostgreSQL
- **상태**: ✅ Production 배포 완료

### 주요 엔드포인트
```
POST /api/v1/lead-scoring/calculate
POST /api/v1/lead-scoring/batch
GET  /api/v1/lead-scoring/stats
POST /api/v1/salesforce/sync
GET  /api/v1/helios/enrich/{company_id}
```

---

## 🎯 System 3: Project Sonar (NBRS 2.0)

### 목적
AI 기반 브랜드 공명 분석 → 공명 경제(Resonance Economy) 플랫폼

### 핵심 기능
- **Multi-Agent System**: 4개 자율 에이전트
- **NBRS 2.0 스코어링**: 5가지 공명 요소 분석
- **AI 협력 제안서**: Claude/Gemini 기반 자동 생성
- **실시간 브랜드 분석**: WIPO + KIS + News API

### NBRS 2.0 구성요소
| 요소 | 가중치 | 데이터 소스 |
|------|--------|-------------|
| Category Overlap | 30% | WIPO Nice Classification |
| Target Audience | 25% | KIS Financial Data |
| Media Co-Mention | 20% | News API |
| Market Positioning | 15% | Credit Rating |
| Geographic Overlap | 10% | Country Code |

### Multi-Agent Architecture
```
OrchestratorAgent (Master Planner)
    ↓
    ├─> MarketIntelAgent (Data Collection)
    ├─> ResonanceModelingAgent (NBRS 2.0)
    └─> ContentStrategyAgent (AI Briefs)
```

### 기술 스택
- FastAPI + Multi-Agent System
- Anthropic Claude / Google Gemini
- WIPO API + KIS API + Naver News API
- (Phase 2) Neo4j + Redis + MLflow

### 배포 정보
- **Port**: 8005
- **Railway Status**: 🔄 배포 준비 완료 (웹 대시보드 설정 대기)
- **Local Dev**: http://localhost:8005 (실행 중)

### 주요 엔드포인트
```
GET  /health
POST /api/v1/resonance/calculate
POST /api/v1/workflows/find-top-brands
POST /api/v1/collaborations/generate-brief
GET  /api/v1/dashboard/kpis
GET  /api/v1/dashboard/agents-status
```

---

## 🔗 시스템 간 통합 플로우

### Scenario 1: 신규 리드 발굴 → 회계 → 공명 분석

```
1. [Warm Lead Generation] 신규 TIER1 리드 발굴
   ↓
2. [Salesforce] 자동 동기화 (Platform Event)
   ↓
3. [영업팀] 계약 체결
   ↓
4. [Independent Accounting] 신규 고객 등록 (POST /api/v1/customers)
   ↓
5. [Project Sonar] 브랜드 공명 분석 (협력 기회 탐색)
   ↓
6. [ContentStrategyAgent] AI 협력 제안서 생성
```

### Scenario 2: 기존 고객 Upsell 기회 발굴

```
1. [Independent Accounting] 월간 리포트 생성
   ↓
2. [Project Sonar] 고객 브랜드 공명 분석
   ↓
3. [ResonanceModelingAgent] 상위 10% 파트너 브랜드 추천
   ↓
4. [ContentStrategyAgent] 맞춤형 협력 제안서 생성
   ↓
5. [영업팀] 추가 계약 체결
   ↓
6. [Independent Accounting] MRR 증가 반영
```

---

## 📈 KPI 프레임워크

### North Star Metric
**공명 조정 LTV/CAC 비율** ≥ 5.0

### System 1 KPIs (Independent Accounting)
- Total MRR: 전체 Cell MRR 합계
- Cell 평균 MRR: 8개 Cell 평균
- Active Customers: 활성 고객 수
- Monthly Churn Rate: 월간 이탈률

### System 2 KPIs (Warm Lead Generation)
- Leads Scored: 총 스코어링된 리드 수
- TIER1 Conversion Rate: TIER1 → 고객 전환율
- Salesforce Sync Rate: 자동 동기화 성공률
- Average NBRS 1.0 Score: 평균 NBRS 점수

### System 3 KPIs (Project Sonar)
- Resonance Index Avg: 평균 공명 지수
- Top 10% Brands Found: 상위 10% 브랜드 발굴 수
- AI Briefs Generated: 생성된 협력 제안서 수
- Agent Uptime: 에이전트 가동률

### Business Impact KPIs
- **Agent-Generated Revenue (MRR)**: 120M → 500M → 1000억 KRW
- **T2D3 Progress**: 60억 → 180억 (Year 1)

---

## 🚀 배포 상태

| System | Port | Railway Status | Database | Email |
|--------|------|----------------|----------|-------|
| Independent Accounting | 8003 | ✅ Production | PostgreSQL | Resend |
| Warm Lead Generation | 8004 | ✅ Production | PostgreSQL | - |
| Project Sonar | 8005 | 🔄 Ready to Deploy | (Phase 2) | - |

---

## 🔐 환경 변수 관리

### System 1 (Independent Accounting)
```bash
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_***
SMTP_FROM_EMAIL=reports@nerdx.com
```

### System 2 (Warm Lead Generation)
```bash
DATABASE_URL=postgresql://...
SALESFORCE_USERNAME=***
SALESFORCE_PASSWORD=***
SALESFORCE_SECURITY_TOKEN=***
HELIOS_API_KEY=***
```

### System 3 (Project Sonar)
```bash
WIPO_API_KEY=***
KIS_API_KEY=***
NEWS_API_CLIENT_ID=***
ANTHROPIC_API_KEY=***
```

---

## 📚 문서 구조

```
nerdx-apec-mvp/
├── NERDX_MASTER_PLAN.md           # Vision 2030, T2D3 전략
├── ARCHITECTURE_OVERVIEW.md        # 전체 아키텍처
├── ARCHITECTURE_DETAILED.md        # 기술 상세
├── SYSTEM_INTEGRATION_GUIDE.md     # 이 문서
│
├── independent-accounting-system/
│   ├── README.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── [배포 완료]
│
├── warm-lead-generation/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── [배포 완료]
│
└── project-sonar/
    ├── README.md
    ├── RAILWAY_DEPLOYMENT.md
    ├── RAILWAY_SETUP_STEPS.md
    └── [배포 준비 완료]
```

---

## 🎯 Next Steps

### Immediate (이번 주)
1. **Project Sonar Railway 배포**
   - Railway 웹 대시보드에서 프로젝트 생성
   - 환경 변수 설정
   - Health check 검증

2. **API 키 설정**
   - WIPO API 키 발급
   - KIS API 계정 생성
   - Naver News API 신청

3. **통합 테스트**
   - System 1 ↔ System 2 데이터 흐름 검증
   - System 2 ↔ System 3 워크플로우 테스트

### Short-term (이번 달)
1. **실제 데이터 연동**
   - Salesforce production 환경 연결
   - 실제 고객 데이터로 NBRS 계산
   - AI 협력 제안서 품질 검증

2. **모니터링 구축**
   - Railway 메트릭 대시보드
   - 에러 알림 설정
   - 로그 집계

3. **문서화 완성**
   - API 문서 완성 (Swagger)
   - 사용자 가이드
   - 운영 매뉴얼

### Mid-term (다음 분기)
1. **Phase 2 기능**
   - Neo4j 브랜드 관계 그래프
   - Redis 실시간 Feature Store
   - MLflow 모델 버전 관리
   - Continual Learning 구현

2. **확장성**
   - Database 샤딩
   - Redis 클러스터링
   - Load balancer

3. **보안 강화**
   - API 인증/인가 (JWT)
   - Rate limiting
   - 데이터 암호화

---

## 💡 운영 가이드

### 로컬 개발 환경 실행

```bash
# System 1 (Port 8003)
cd independent-accounting-system
python main.py

# System 2 (Port 8004)
cd warm-lead-generation
python main.py

# System 3 (Port 8005)
cd project-sonar
python main.py
```

### Railway 배포 확인

```bash
# System 1
curl https://nerdx-accounting-system-production.up.railway.app/health

# System 2
curl https://nerdx-apec-mvp-production.up.railway.app/health

# System 3 (배포 후)
curl https://project-sonar-production.up.railway.app/health
```

### 로그 모니터링

```bash
# Railway CLI
railway logs --service=independent-accounting-system
railway logs --service=warm-lead-generation
railway logs --service=project-sonar
```

---

## 🤝 기여 및 문의

**Tech Lead**: Claude Code
**Product Owner**: Sean (sean@koreafnbpartners.com)
**Repository**: https://github.com/KFP-SEAN/nerdx-apec-mvp

---

**작성자**: Claude Code
**최종 업데이트**: 2025-10-27
**버전**: 1.0.0-MVP
