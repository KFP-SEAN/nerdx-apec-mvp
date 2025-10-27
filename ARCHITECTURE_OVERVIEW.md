# NERDX APEC MVP - 시스템 아키텍처 (요약본)

> **최종 업데이트**: 2025-10-27
> **버전**: 1.0
> **상태**: Production Ready

---

## 📊 시스템 개요

NERDX APEC MVP는 **CPG(소비재) 브랜드의 디지털 트랜스포메이션을 위한 통합 AI 플랫폼**입니다.

### 핵심 가치
- 💰 **매출 증대**: 웜리드 발굴로 MRR 500M KRW 달성
- 📊 **경영 가시성**: 셀별 독립채산제로 실시간 P&L 추적
- 🤖 **AI 자동화**: Agentic AI 기반 콘텐츠 생성 및 의사결정
- 🛒 **커머스 혁신**: Shopify Headless + AR 제품 경험

---

## 🏗️ 전체 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    NERDX APEC MVP PLATFORM                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐  ┌─────────────────────┐           │
│  │   Frontend Layer    │  │   Mobile/AR Layer   │           │
│  │   (Next.js 14)      │  │   (WebXR/AR.js)     │           │
│  │   Port: 3000        │  │                      │           │
│  └──────────┬──────────┘  └──────────┬──────────┘           │
│             │                         │                       │
│  ┌──────────┴─────────────────────────┴──────────┐           │
│  │          API Gateway / Load Balancer           │           │
│  └──────────┬─────────────────────────┬──────────┘           │
│             │                         │                       │
│  ┌──────────┴──────────┐  ┌──────────┴──────────┐           │
│  │  Business Services  │  │   AI/ML Services    │           │
│  ├─────────────────────┤  ├─────────────────────┤           │
│  │ • Accounting (8003) │  │ • Agentic AI (8002) │           │
│  │ • Lead Gen (8004)   │  │ • Sora Pipeline     │           │
│  │ • Shopify App (3001)│  │ • World Model (8000)│           │
│  └──────────┬──────────┘  └──────────┬──────────┘           │
│             │                         │                       │
│  ┌──────────┴─────────────────────────┴──────────┐           │
│  │              Data Layer                        │           │
│  ├────────────────────────────────────────────────┤           │
│  │ • PostgreSQL (관계형 데이터)                    │           │
│  │ • Neo4j (그래프 DB - 구매 관계)                │           │
│  │ • Redis (캐시 + 세션)                          │           │
│  └──────────┬─────────────────────────┬──────────┘           │
│             │                         │                       │
│  ┌──────────┴──────────┐  ┌──────────┴──────────┐           │
│  │  External Services  │  │   CI/CD Pipeline    │           │
│  ├─────────────────────┤  ├─────────────────────┤           │
│  │ • Salesforce CRM    │  │ • Railway (Deploy)  │           │
│  │ • Odoo ERP          │  │ • GitHub Actions    │           │
│  │ • Shopify           │  │ • Vercel (Frontend) │           │
│  │ • Resend (Email)    │  │                     │           │
│  └─────────────────────┘  └─────────────────────┘           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 핵심 서비스 (5개)

### 1️⃣ 프론트엔드 (Next.js 14)
- **포트**: 3000
- **역할**: 고객 대면 UI, Shopify Headless Commerce
- **기술**: Next.js 14 App Router, TypeScript, Tailwind CSS
- **배포**: Vercel

### 2️⃣ Agentic AI 시스템 (Port 8002)
- **포트**: 8002
- **역할**: AI 에이전트 기반 자동화 (콘텐츠 생성, 의사결정)
- **기술**: FastAPI, Claude Sonnet, Gemini, Sora 2
- **배포**: Railway

### 3️⃣ 독립채산제 시스템 (Port 8003)
- **포트**: 8003
- **역할**: 셀별 P&L 추적, 일간 재무 리포트 자동 발송
- **기술**: FastAPI, PostgreSQL, Salesforce/Odoo 통합
- **배포**: Railway

### 4️⃣ 웜리드 발굴 시스템 (Port 8004)
- **포트**: 8004
- **역할**: NBRS 스코어링, Lead 자동 분류 (TIER1-4)
- **기술**: FastAPI, Salesforce API, simple-salesforce
- **배포**: Railway

### 5️⃣ Shopify Custom App (Port 3001)
- **포트**: 3001
- **역할**: 주문 처리, AR 콘텐츠 액세스 관리
- **기술**: Node.js, Express, Neo4j, Redis
- **배포**: Railway

---

## 📡 서비스 간 통신

```
Frontend (3000)
    ↓ REST API
Shopify App (3001) ←→ Shopify (External)
    ↓ Webhook
Neo4j + Redis

Independent Accounting (8003)
    ↓ API Integration
Salesforce + Odoo (External)
    ↓ Daily Report
Email (Resend)

Warm Lead Gen (8004)
    ↓ OAuth2
Salesforce (External)
    ↓ Platform Events
Lead Assignment

Agentic AI (8002)
    ↓ API Calls
Claude + Gemini + Sora (External)
```

---

## 💾 데이터 스토어

| 스토어 | 용도 | 서비스 |
|--------|------|--------|
| **PostgreSQL** | 관계형 데이터 (매출, 비용, Lead) | Accounting, Lead Gen |
| **Neo4j** | 그래프 DB (구매 관계) | Shopify App |
| **Redis** | 캐시, 세션, 멱등성 | Shopify App, Agentic AI |
| **Salesforce** | CRM (Lead, Opportunity) | Accounting, Lead Gen |
| **Odoo** | ERP (재고, 원가) | Accounting |

---

## 🔐 인증 & 보안

### API 인증
- **JWT Tokens**: AR 콘텐츠 액세스 (90일 유효)
- **OAuth2**: Salesforce 통합
- **HMAC**: Shopify Webhook 검증

### 보안 정책
- ✅ HTTPS Only (TLS 1.3)
- ✅ 환경 변수 기반 시크릿 관리
- ✅ Rate Limiting (Redis)
- ✅ CORS 정책 (화이트리스트)

---

## 🚀 배포 환경

| 환경 | 프론트엔드 | 백엔드 서비스 | 데이터베이스 |
|------|-----------|--------------|-------------|
| **Production** | Vercel | Railway (4 services) | Railway PostgreSQL |
| **Development** | localhost:3000 | localhost:8002-8004 | Local PostgreSQL |

### Railway 배포 서비스
1. `nerdx-accounting-system` (Port 8003)
2. `warm-lead-generation` (Port 8004)
3. `phase2-agentic-system` (Port 8002)
4. `shopify-custom-app` (Port 3001)

---

## 📊 모니터링 & 알림

### 자동화된 일일 리포트
- ⏰ **매일 오전 6시 (KST)** 자동 발송
- 📧 **수신자**: sean@koreafnbpartners.com
- 📋 **내용**:
  - 독립채산제: 셀별 P&L, MTD 실적
  - Lead 리포트: TIER별 Lead 현황 (예정)

### GitHub Actions
- ✅ Daily Report Automation (Cron: `0 21 * * *`)
- ✅ CI/CD Pipeline (Railway auto-deploy)

---

## 🎯 비즈니스 KPI

| 지표 | 현재 | 목표 | 서비스 |
|------|------|------|--------|
| **MRR** | - | 500M KRW | Warm Lead Gen |
| **Lead Conversion** | - | Top 10% (TIER1) | Warm Lead Gen |
| **Gross Profit** | 추적 중 | 매월 증가 | Accounting |
| **AR Engagement** | - | 60% 활성화 | Shopify App |

---

## 🔄 데이터 플로우 (주요 시나리오)

### 시나리오 1: 고객 구매 → AR 액세스
```
1. 고객이 Shopify에서 제품 구매
2. Shopify Webhook → Shopify App
3. Shopify App: Neo4j에 관계 저장
4. JWT Token 생성 (90일)
5. 이메일로 AR 링크 발송
6. 고객이 AR 콘텐츠 접근
```

### 시나리오 2: 일간 재무 리포트
```
1. GitHub Actions Cron 트리거 (매일 21:00 UTC)
2. Accounting API 호출 (/api/v1/reports/daily)
3. Salesforce에서 매출 데이터 조회
4. Odoo에서 원가 데이터 조회
5. Gross Profit 계산
6. HTML 리포트 생성
7. Resend로 이메일 발송
```

### 시나리오 3: Lead 스코어링
```
1. Salesforce에 새 Lead 생성
2. Warm Lead API 호출
3. NBRS 계산 (Brand Affinity + Market Positioning + Digital Presence)
4. TIER 분류 (TIER1-4)
5. Salesforce Lead 업데이트
6. Platform Event 발행
7. 자동 할당 규칙 트리거
```

---

## 📚 관련 문서

- 📖 [상세 아키텍처](ARCHITECTURE_DETAILED.md) - 각 서비스의 상세 설계
- 🔧 [배포 가이드](RAILWAY_DEPLOY_FIX.md) - Railway 배포 문제 해결
- 🧪 [API 문서](http://localhost:8003/docs) - FastAPI Swagger UI
- 📊 [데이터 모델](independent-accounting-system/models/) - SQLAlchemy 모델

---

## 🎓 기술 스택 요약

### Frontend
- Next.js 14, TypeScript, Tailwind CSS
- React 18, model-viewer (WebXR)

### Backend
- FastAPI 0.104+, Python 3.11+
- Pydantic, SQLAlchemy, Alembic

### AI/ML
- Claude Sonnet 4.5, Gemini 2.0, Sora 2
- simple-salesforce, requests

### Data
- PostgreSQL 15+, Neo4j 5+, Redis 7+

### DevOps
- Railway, Vercel, GitHub Actions
- Docker, Git

---

**작성자**: Claude Code
**날짜**: 2025-10-27
**버전**: 1.0
