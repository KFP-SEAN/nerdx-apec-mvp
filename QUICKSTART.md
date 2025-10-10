# 🚀 NERDX APEC MVP - Quick Start Guide

전체 시스템을 5분 안에 실행하세요!

## Prerequisites

시작하기 전에 다음이 설치되어 있는지 확인하세요:

- Docker Desktop (Windows/Mac) 또는 Docker Engine (Linux)
- Git
- 텍스트 에디터 (VS Code 권장)

## Step 1: Clone & Configure (2분)

```bash
# 1. 프로젝트 디렉토리로 이동
cd C:\Users\seans\nerdx-apec-mvp

# 2. 환경 변수 파일 생성
cp .env.example .env

# 3. .env 파일 편집 (필수!)
notepad .env
```

최소한 다음 값들을 설정하세요:

```env
# 필수 설정
OPENAI_API_KEY=sk-your-actual-openai-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key

# AWS는 선택사항 (로컬 스토리지로 시작 가능)
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

## Step 2: Start All Services (2분)

```bash
# 전체 스택 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

서비스들이 시작되는 것을 확인하세요:
- ✅ Neo4j (7474, 7687)
- ✅ Redis (6379)
- ✅ Phase 1 API (8001)
- ✅ Phase 2 API (8002)
- ✅ Phase 3 API (8003)
- ✅ Frontend (3000)
- ✅ Nginx (80)
- ✅ Prometheus (9090)
- ✅ Grafana (3001)

## Step 3: Verify & Test (1분)

### 브라우저에서 확인:

1. **Frontend**: http://localhost:3000
   - 샘 올트먼 소개 영상이 보여야 함
   - 제품 카탈로그 탐색 가능

2. **API 문서**:
   - Phase 1: http://localhost:8001/docs
   - Phase 2: http://localhost:8002/docs
   - Phase 3: http://localhost:8003/health

3. **Neo4j Browser**: http://localhost:7474
   - Username: `neo4j`
   - Password: `nerdxpassword`

4. **Grafana**: http://localhost:3001
   - Username: `admin`
   - Password: `admin` (또는 .env에 설정한 값)

### API 테스트:

```bash
# Phase 1: Products
curl http://localhost:8001/api/v1/products

# Phase 1: Chat with Maeju
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "Tell me about NERD12"}'

# Phase 2: CAMEO Status
curl http://localhost:8002/api/v1/cameo/queue/status

# Phase 3: Health
curl http://localhost:8003/health
```

## 🎉 You're Ready!

이제 다음을 시도해보세요:

1. **제품 탐색**: http://localhost:3000/products
2. **Maeju AI와 채팅**: http://localhost:3000/chat
3. **CAMEO 비디오 생성**: http://localhost:3000/cameo
4. **주문하기**: 제품 선택 → 장바구니 → 체크아웃

## 🛑 Stopping Services

```bash
# 모든 서비스 중지
docker-compose down

# 데이터까지 삭제 (주의!)
docker-compose down -v
```

## 🔧 Troubleshooting

### 포트 충돌

다른 프로그램이 포트를 사용 중이면:

```bash
# Windows
netstat -ano | findstr :8001

# 포트 변경 (docker-compose.yml 수정)
ports:
  - "8011:8001"  # 8001 대신 8011 사용
```

### 서비스가 시작되지 않음

```bash
# 로그 확인
docker-compose logs phase1-api
docker-compose logs phase2-api

# 특정 서비스 재시작
docker-compose restart phase1-api
```

### Neo4j 연결 실패

```bash
# Neo4j 컨테이너 확인
docker-compose ps neo4j

# 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs neo4j
```

## 📚 Next Steps

- [README.md](./README.md) - 전체 프로젝트 문서
- [Phase 1 README](./phase1-world-model/README.md) - World Model 상세
- [Phase 2 README](./phase2-agentic-system/README.md) - CAMEO 시스템 상세
- [Phase 3 README](./phase3-conversion/README.md) - Commerce & AR 상세
- [Frontend README](./frontend/README.md) - 프론트엔드 상세

## 💡 Tips

1. **개발 모드로 실행**: 각 서비스를 개별적으로 실행하면 hot-reload 가능
2. **데이터 초기화**: `scripts/init_data.py`로 샘플 데이터 추가
3. **Stripe 테스트**: Stripe CLI로 webhook 테스트 가능
4. **모니터링**: Grafana에서 실시간 메트릭 확인

## 🆘 Need Help?

- GitHub Issues: https://github.com/nerdx/apec-mvp/issues
- Slack: #nerdx-apec-mvp
- Email: apec-support@nerdx.com

---

**Built with ❤️ by NERDX Team | Powered by OpenAI Sora 2**
