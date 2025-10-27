# Project Sonar - Railway 배포 단계별 가이드

## 🚀 Railway 웹 대시보드를 통한 배포

### Step 1: Railway 프로젝트 생성

1. **Railway 대시보드 접속**
   - 브라우저에서 https://railway.app/dashboard 열기
   - 로그인 (GitHub 계정 연동)

2. **New Project 생성**
   - "New Project" 버튼 클릭
   - "Deploy from GitHub repo" 선택
   - "KFP-SEAN/nerdx-apec-mvp" 저장소 선택
   - 권한 승인 (필요시)

3. **Root Directory 설정**
   - Settings → General → Root Directory 항목
   - 값 입력: `project-sonar`
   - Save 클릭

### Step 2: 환경 변수 설정

Settings → Variables 메뉴에서 다음 변수 추가:

```bash
# 필수 환경 변수
API_ENVIRONMENT=production
API_HOST=0.0.0.0
PORT=${{PORT}}

# WIPO API (브랜드 데이터)
WIPO_API_URL=https://www.wipo.int/branddb/en/
WIPO_API_KEY=your_actual_wipo_api_key

# KIS API (한국 기업 재무 데이터)
KIS_API_URL=https://api.kis.co.kr
KIS_API_KEY=your_actual_kis_api_key
KIS_API_SECRET=your_actual_kis_secret

# Naver News API (뉴스 데이터)
NEWS_API_URL=https://openapi.naver.com/v1/search/news.json
NEWS_API_CLIENT_ID=your_actual_naver_client_id
NEWS_API_CLIENT_SECRET=your_actual_naver_client_secret

# AI Models (협력 제안서 생성)
ANTHROPIC_API_KEY=your_actual_anthropic_key
OPENAI_API_KEY=your_actual_openai_key  # (선택사항)
GEMINI_API_KEY=your_actual_gemini_key  # (선택사항)
```

**중요**: 각 API 키를 실제 값으로 교체하세요!

### Step 3: 배포 트리거

1. **자동 배포**
   - 환경 변수 저장 후 자동으로 배포 시작
   - Deployments 탭에서 진행 상황 확인

2. **수동 배포** (필요시)
   - Deployments → "Deploy" 버튼 클릭
   - 또는 GitHub에 새 커밋 푸시

### Step 4: 배포 확인

1. **로그 확인**
   ```
   Deployments → 최신 deployment 클릭 → View Logs
   ```

   다음 메시지 확인:
   ```
   Uvicorn running on http://0.0.0.0:$PORT
   Application startup complete
   ```

2. **도메인 확인**
   - Settings → Domains
   - Railway가 자동 생성한 URL 확인: `*.up.railway.app`

3. **Health Check**
   ```bash
   curl https://your-project-name.up.railway.app/health
   ```

   응답 예시:
   ```json
   {
     "status": "healthy",
     "environment": "production",
     "agents": { ... },
     "mas_operational": true
   }
   ```

### Step 5: API 테스트

```bash
# KPI 대시보드
curl https://your-app.up.railway.app/api/v1/dashboard/kpis

# 에이전트 상태
curl https://your-app.up.railway.app/api/v1/dashboard/agents-status

# 공명 지수 계산 테스트
curl -X POST "https://your-app.up.railway.app/api/v1/resonance/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_brand": {
      "brand_name": "TestBrand",
      "company_name": "Test Corp",
      "nice_classification": ["30", "43"],
      "country": "KR"
    }
  }'
```

## 🔧 트러블슈팅

### 빌드 실패

**증상**: "Error: Could not find a version that satisfies the requirement..."

**해결**:
1. `requirements.txt`가 `requirements-railway.txt`로 교체되었는지 확인
2. Railway 로그에서 Python 버전 확인
3. 필요시 `runtime.txt` 추가:
   ```
   python-3.11.0
   ```

### 환경 변수 누락

**증상**: API 호출 시 인증 오류

**해결**:
1. Railway Settings → Variables 확인
2. 모든 필수 API 키가 설정되었는지 검증
3. 변수 저장 후 재배포: Deployments → Restart

### 포트 바인딩 오류

**증상**: "Address already in use" 또는 응답 없음

**해결**:
1. `PORT` 환경 변수가 `${{PORT}}`로 설정되었는지 확인
2. `main.py`에서 `os.getenv("PORT", 8005)` 사용 확인
3. Railway.json의 startCommand 확인

## 📊 모니터링

### Railway 대시보드

- **Metrics**: CPU, 메모리, 네트워크 사용량
- **Logs**: 실시간 애플리케이션 로그
- **Deployments**: 배포 이력 및 롤백

### Custom API 엔드포인트

```bash
# 모델 버전 확인
curl https://your-app.up.railway.app/api/v1/dashboard/model-version

# 공명 지수 계산 이력
curl https://your-app.up.railway.app/api/v1/dashboard/prediction-history?limit=10
```

## 🎯 배포 완료 체크리스트

- [ ] Railway 프로젝트 생성
- [ ] Root Directory 설정 (`project-sonar`)
- [ ] 모든 필수 환경 변수 설정
- [ ] 배포 성공 확인 (로그)
- [ ] Health check 통과
- [ ] API 엔드포인트 테스트
- [ ] 도메인 URL 기록
- [ ] 모니터링 설정

## 📚 참고 자료

- [Railway 공식 문서](https://docs.railway.app/)
- [Project Sonar README](./README.md)
- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- [API 문서](https://your-app.up.railway.app/docs)

---

**배포 후 다음 단계**:
1. Production URL을 팀과 공유
2. Salesforce/CRM 연동 (Phase 2)
3. 실제 API 키로 데이터 수집 테스트
4. NBRS 모델 튜닝 및 학습

**작성일**: 2025-10-27
**버전**: 1.0.0-MVP
