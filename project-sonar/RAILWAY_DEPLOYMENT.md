# Project Sonar - Railway 배포 가이드

## 🚀 Railway 배포 단계

### 1. Railway CLI 설치 (이미 설치된 경우 생략)

```bash
npm install -g @railway/cli
```

### 2. Railway 로그인

```bash
railway login
```

### 3. 프로젝트 초기화 (project-sonar 디렉토리에서 실행)

```bash
cd C:\Users\seans\nerdx-apec-mvp\project-sonar
railway init
```

### 4. 환경 변수 설정

Railway 대시보드 (https://railway.app/dashboard)에서 다음 환경 변수를 설정하세요:

#### 필수 환경 변수

```bash
# API Configuration
API_ENVIRONMENT=production
API_HOST=0.0.0.0
PORT=8005  # Railway가 자동으로 할당한 포트 사용

# WIPO API (World Intellectual Property Organization)
WIPO_API_URL=https://www.wipo.int/branddb/en/
WIPO_API_KEY=your_wipo_api_key_here

# KIS API (한국신용평가정보)
KIS_API_URL=https://api.kis.co.kr
KIS_API_KEY=your_kis_api_key_here
KIS_API_SECRET=your_kis_api_secret_here

# 국내 뉴스 API (Naver News API)
NEWS_API_URL=https://openapi.naver.com/v1/search/news.json
NEWS_API_CLIENT_ID=your_naver_client_id_here
NEWS_API_CLIENT_SECRET=your_naver_client_secret_here

# AI Models
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
```

#### 선택적 환경 변수 (Phase 2)

```bash
# Database (PostgreSQL) - Railway 자동 생성 가능
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis (Feature Store) - Railway 플러그인
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379
REDIS_DB=2
REDIS_PASSWORD=

# Neo4j (Brand Relationship Graph)
NEO4J_URI=bolt://host:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# MLOps
MLFLOW_TRACKING_URI=http://localhost:5000
MODEL_REGISTRY_PATH=./models

# Google Cloud (NotebookLM, Docs)
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_PROJECT_ID=your_project_id
```

### 5. requirements.txt 변경 (Railway용)

Railway 배포 시 `requirements.txt` 대신 `requirements-railway.txt` 사용:

```bash
# 프로젝트 루트에서 실행
cp requirements-railway.txt requirements.txt
```

### 6. Git 커밋 및 배포

```bash
git add .
git commit -m "Configure Project Sonar for Railway deployment"
railway up
```

### 7. 배포 확인

```bash
# Railway 로그 확인
railway logs

# 배포된 URL 확인
railway status
```

### 8. Health Check

```bash
# Railway에서 할당된 URL로 헬스 체크
curl https://your-app-name.up.railway.app/health
```

## 📊 배포 후 테스트

### API 엔드포인트 테스트

```bash
# KPI 대시보드
curl https://your-app-name.up.railway.app/api/v1/dashboard/kpis

# 에이전트 상태
curl https://your-app-name.up.railway.app/api/v1/dashboard/agents-status

# 공명 지수 계산
curl -X POST "https://your-app-name.up.railway.app/api/v1/resonance/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {"brand_name": "NERD", "company_name": "NERDX"},
    "target_brand": {"brand_name": "TestBrand", "company_name": "Test Co"}
  }'
```

## 🔧 트러블슈팅

### 빌드 실패 (scikit-learn, prophet 등)

**문제**: C 컴파일러가 필요한 패키지 설치 실패

**해결**: `requirements-railway.txt` 사용 (ML 패키지 제외)

```bash
cp requirements-railway.txt requirements.txt
git add requirements.txt
git commit -m "Use simplified requirements for Railway"
railway up
```

### 환경 변수 누락

**문제**: API 키 관련 오류

**해결**: Railway 대시보드에서 환경 변수 추가 후 재배포

```bash
railway restart
```

### 포트 바인딩 오류

**문제**: `Address already in use`

**해결**: Railway의 `$PORT` 환경 변수 사용 (railway.json에 이미 설정됨)

## 📈 모니터링

### Railway 대시보드

- **Deployments**: 배포 이력 및 로그
- **Metrics**: CPU, 메모리, 네트워크 사용량
- **Environment**: 환경 변수 관리
- **Settings**: 도메인, 재시작 정책

### Custom Metrics (추후 구현)

- Prometheus + Grafana 연동
- OpenTelemetry 추적
- Custom KPI 대시보드

## 🔐 보안 고려사항

1. **API 키 보호**: 환경 변수만 사용, 코드에 하드코딩 금지
2. **HTTPS 사용**: Railway 자동 제공
3. **Rate Limiting**: FastAPI middleware 추가 (추후)
4. **인증/인가**: JWT 토큰 기반 API 인증 (추후)

## 📚 관련 문서

- [Railway 공식 문서](https://docs.railway.app/)
- [Project Sonar README](./README.md)
- [NERDX Master Plan](../NERDX_MASTER_PLAN.md)

---

**작성일**: 2025-10-27
**버전**: 1.0.0-MVP
