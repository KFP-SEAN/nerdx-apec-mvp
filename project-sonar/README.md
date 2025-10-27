# Project Sonar - AI 브랜드 공명 분석 시스템

> **프로젝트 소나 (Project Sonar)**: NERD12 AI-Native 시스템을 '공명 경제(Resonance Economy)' 창출을 위한 자율적, 자기 진화형 에이전트 플랫폼으로 전환

**버전**: 1.0.0-MVP
**포트**: 8005
**목표**: MRR 5억 → 1000억 (200x 성장)

---

## 🎯 Vision 2030

### 전략적 당위성
- **현재**: 5억 MRR (리드 생성 도구)
- **목표**: 1000억 MRR (B2B 플랫폼 & 공명 경제 엔진)
- **패러다임 전환**: SaaS 도구 제공업체 → 시장 창출(Market-Making) 플랫폼

---

## 🏗️ 시스템 아키텍처

### Multi-Agent System (MAS)

```
OrchestratorAgent (관리형 오케스트레이션)
    ↓
    ├─> MarketIntelAgent (WIPO, KIS, 뉴스 데이터 수집)
    ├─> ResonanceModelingAgent (NBRS 2.0 공명 모델)
    └─> ContentStrategyAgent (AI 협력 개요서 생성)
```

### 핵심 기술
- **FIPA-ACL 표준**: 에이전트 간 통신 프로토콜
- **공유 온톨로지**: 비즈니스 개념의 공식적 정의
- **Continual Learning**: 지속적 모델 학습
- **Multi-Armed Bandits**: 실시간 모델 최적화

---

## 🚀 Quick Start

### 1. 환경 설정

```bash
cd C:\Users\seans\nerdx-apec-mvp\project-sonar

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (API 키 입력)

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# 개발 모드
python main.py

# 또는
uvicorn main:app --reload --port 8005
```

### 3. API 문서 확인

```
http://localhost:8005/docs (Swagger UI)
http://localhost:8005/redoc (ReDoc)
```

---

## 📡 API 엔드포인트

### 1. Brands API (`/api/v1/brands`)
- `GET /`: 브랜드 목록 조회
- `GET /{brand_name}/profile`: 브랜드 종합 프로필
- `GET /{brand_name}/news`: 브랜드 뉴스 및 감성 분석

### 2. Resonance API (`/api/v1/resonance`)
- `POST /calculate`: 브랜드 간 공명 지수 계산
- `POST /rank`: 브랜드 공명 지수 순위 정렬
- `POST /retrain`: NBRS 모델 재학습
- `GET /model-performance`: 모델 성능 지표

### 3. Collaborations API (`/api/v1/collaborations`)
- `POST /generate-brief`: 협력 개요서 생성
- `POST /generate-batch-briefs`: 일괄 개요서 생성
- `POST /prepare-notebooklm`: NotebookLM 데이터 준비

### 4. Workflows API (`/api/v1/workflows`)
- `POST /execute`: 워크플로우 실행
- `POST /find-top-brands`: 상위 10% 공명 브랜드 발굴
- `POST /partnership-pipeline`: 전체 파트너십 파이프라인

### 5. Dashboard API (`/api/v1/dashboard`)
- `GET /agents-status`: 에이전트 상태 조회
- `GET /kpis`: 핵심 KPI 대시보드
- `GET /model-version`: NBRS 모델 버전
- `GET /prediction-history`: 공명 지수 계산 이력

---

## 🎯 핵심 기능

### 1. NBRS 2.0 공명 모델

**5가지 공명 요소 (0-100 점수)**:

| 요소 | 가중치 | 설명 |
|------|--------|------|
| **브랜드 카테고리 중복** | 30% | WIPO 니스 분류 기반 |
| **타겟 고객 유사성** | 25% | KIS 재무 데이터 기반 |
| **미디어 동시 언급** | 20% | 뉴스 API 기반 |
| **시장 포지셔닝** | 15% | 신용 등급 기반 |
| **지리적 중복** | 10% | 국가 코드 기반 |

**TIER 분류**:
- TIER1: 80-100 (상위 10%, 최우선)
- TIER2: 60-79 (우선)
- TIER3: 40-59 (일반)
- TIER4: 0-39 (저우선순위)

### 2. 자율 에이전트

#### OrchestratorAgent (Master Planner)
- 목표 분해 (Goal Decomposition)
- 작업 위임 (Task Assignment)
- 품질 평가 (Critic)

#### MarketIntelAgent
- WIPO 글로벌 브랜드 데이터베이스
- KIS (한국신용평가정보) 재무 데이터
- 국내 뉴스 API 실시간 수집

#### ResonanceModelingAgent
- NBRS 2.0 모델 실행
- 지속적 학습 (Continual Learning)
- Multi-Armed Bandits 최적화

#### ContentStrategyAgent
- LLM 기반 협력 개요서 생성 (Claude/Gemini)
- NotebookLM 데이터 준비
- Google Docs 내보내기

---

## 📊 KPI 프레임워크

### 북극성 지표
- **공명 조정 LTV/CAC 비율**: 목표 5.0 이상

### 자율성 KPI
- **자동화된 의사결정 비율**: 목표 95%
- **모델 학습 속도**: 목표 주간 5% AUC 향상

### 비즈니스 영향 KPI
- **에이전트 생성 수익 (MRR)**: 목표 5억 → 1000억

---

## 🔄 T2D3 로드맵

| 연차 | 단계 | 목표 ARR | GTM 전략 |
|------|------|---------|---------|
| 1-2 | Triple | 180억 | 직접 판매 확장 |
| 3 | Triple | 540억 | 인바운드 마케팅 |
| 4 | Double | 1,080억 | PLG (제품 주도 성장) |
| 5 | Double | 2,160억 | 파트너 생태계 |
| 6+ | Double | 4,320억+ | 플랫폼 네트워크 효과 |

---

## 🧪 테스트

### 단위 테스트
```bash
pytest tests/
```

### API 테스트
```bash
# Health Check
curl http://localhost:8005/health

# 브랜드 목록 조회
curl "http://localhost:8005/api/v1/brands/?country=KR&limit=10"

# 워크플로우 실행
curl -X POST "http://localhost:8005/api/v1/workflows/find-top-brands" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["33", "35", "43"],
      "country": "KR"
    },
    "target_country": "KR"
  }'
```

---

## 🚢 배포 (Railway)

### 환경 변수 설정

Railway 대시보드에서 다음 환경 변수 설정:

```
API_ENVIRONMENT=production
API_PORT=8005
WIPO_API_KEY=*******
KIS_API_KEY=*******
ANTHROPIC_API_KEY=*******
...
```

### 배포
```bash
railway up
```

---

## 📚 관련 문서

- [NERDX Master Plan](../NERDX_MASTER_PLAN.md)
- [Architecture Overview](../ARCHITECTURE_OVERVIEW.md)
- [Warm Lead Generation](../warm-lead-generation/SYSTEM_ARCHITECTURE.md)

---

## 🤝 기여

**문의**: sean@koreafnbpartners.com

---

**작성자**: Claude Code
**작성일**: 2025-10-27
**버전**: 1.0.0-MVP
