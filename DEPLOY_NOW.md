# 🚀 Project Sonar - 지금 바로 배포하기

**소요 시간**: 10분
**난이도**: 쉬움
**필요 항목**: Railway 계정, GitHub 계정

---

## ✅ 사전 준비 완료 상태

### 로컬 테스트 결과
```
✓ Project Sonar 로컬 실행 중 (http://localhost:8005)
✓ Multi-Agent System 작동 확인 (4 agents)
✓ NBRS 2.0 계산 성공 (50 brands → 5 top picks)
✓ 모든 API 엔드포인트 응답 정상
✓ 협력 제안서 5개 생성 완료
```

### GitHub 저장소
```
✓ 코드 커밋 완료
✓ 배포 설정 파일 준비 완료
✓ 문서화 100% 완료
✓ Repository: https://github.com/KFP-SEAN/nerdx-apec-mvp
```

---

## 🎯 Railway 배포 - 10분 가이드

### Step 1: Railway 대시보드 열기 (1분)

**브라우저에서 다음 URL 열기**:
```
https://railway.app/dashboard
```

**로그인**:
- GitHub 계정으로 로그인
- 처음이라면 "Sign up with GitHub" 클릭

---

### Step 2: 새 프로젝트 생성 (2분)

**화면 우측 상단**:
1. **"New Project"** 버튼 클릭 (보라색 버튼)

**배포 방식 선택**:
2. **"Deploy from GitHub repo"** 선택

**저장소 선택**:
3. Repository 목록에서 **"KFP-SEAN/nerdx-apec-mvp"** 찾기
4. 클릭하여 선택
5. (권한 요청 시) "Install & Authorize" 클릭

**프로젝트 생성 완료!**
- Railway가 자동으로 빌드 시작
- 하지만 잠깐! 먼저 Root Directory 설정 필요

---

### Step 3: Root Directory 설정 (1분)

**⚠️ 중요**: Project Sonar는 서브디렉토리에 있음!

**좌측 사이드바에서**:
1. **"Settings"** 클릭 (톱니바퀴 아이콘)

**General 탭에서**:
2. 아래로 스크롤하여 **"Root Directory"** 찾기
3. 입력 필드에 다음 입력:
   ```
   project-sonar
   ```
4. **"Deploy"** 버튼 클릭 (자동 재배포 시작)

---

### Step 4: 환경 변수 설정 (3분)

**Settings → Variables 탭으로 이동**:

**필수 환경 변수 추가** (하나씩 클릭 → 입력 → Add):

```bash
# 1. API Environment
변수명: API_ENVIRONMENT
값: production

# 2. API Host
변수명: API_HOST
값: 0.0.0.0

# 3. Port (Railway 자동 할당 사용)
변수명: PORT
값: ${{PORT}}

# 4. NBRS Model Version
변수명: NBRS_MODEL_VERSION
값: 2.0.0

# 5. Update Frequency
변수명: NBRS_UPDATE_FREQUENCY
값: daily
```

**선택 사항 - API 키** (나중에 추가 가능):

MVP는 Mock 데이터로 작동하므로 일단 생략 가능합니다.
실제 데이터를 사용하려면 다음 API 키 추가:

```bash
WIPO_API_KEY=your_key_here
KIS_API_KEY=your_key_here
NEWS_API_CLIENT_ID=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

**저장 후 자동 재배포**:
- 환경 변수 추가 시 자동으로 재배포 시작
- 좌측 "Deployments" 탭에서 진행 상황 확인

---

### Step 5: 배포 진행 상황 확인 (3분)

**Deployments 탭으로 이동**:
1. 좌측 사이드바에서 **"Deployments"** 클릭
2. 최신 deployment 클릭하여 상세 보기

**로그 확인**:
```
✓ Building...
✓ Installing dependencies...
✓ Starting application...
✓ Uvicorn running on http://0.0.0.0:$PORT
```

**성공 표시**:
- 초록색 체크마크 ✅
- "Active" 상태

**실패 시**:
- 빨간색 X 표시
- 로그에서 에러 메시지 확인
- [트러블슈팅 섹션](#troubleshooting) 참고

---

### Step 6: Production URL 확인 (1분)

**Settings → Domains 탭으로 이동**:

**Railway 자동 생성 URL 확인**:
```
예시: project-sonar-production.up.railway.app
```

**URL 복사**:
- 도메인 옆 복사 아이콘 클릭
- 또는 텍스트 선택하여 복사

---

### Step 7: Health Check 테스트 (<1분)

**터미널 또는 PowerShell 열기**:

```bash
# Windows PowerShell
curl https://your-project-name.up.railway.app/health

# 또는 브라우저에서 직접 열기
https://your-project-name.up.railway.app/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "environment": "production",
  "agents": {
    "orchestrator": {"state": "idle", ...},
    "market_intel": {"state": "idle", ...},
    "resonance_modeling": {"state": "idle", ...},
    "content_strategy": {"state": "idle", ...}
  },
  "mas_operational": true
}
```

**✅ 성공!** `"status": "healthy"` 이면 배포 완료!

---

## 🎉 배포 완료! 이제 뭐하지?

### 즉시 테스트 가능한 것들

**1. API 문서 확인**:
```
https://your-app.up.railway.app/docs
```
Swagger UI에서 모든 API를 브라우저에서 직접 테스트 가능!

**2. KPI 대시보드**:
```bash
curl https://your-app.up.railway.app/api/v1/dashboard/kpis
```

**3. 공명 지수 계산**:
```bash
curl -X POST "https://your-app.up.railway.app/api/v1/resonance/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35"],
      "country": "KR"
    },
    "target_brand": {
      "brand_name": "Starbucks",
      "company_name": "Starbucks Korea",
      "nice_classification": ["43"],
      "country": "KR"
    }
  }'
```

**4. Top 10% 브랜드 발굴**:
```bash
curl -X POST "https://your-app.up.railway.app/api/v1/workflows/find-top-brands" \
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

---

## 📋 배포 후 체크리스트

### 즉시 (배포 완료 후)
- [ ] Health check 통과 확인
- [ ] `/docs` 페이지 접속 확인
- [ ] 최소 3개 API 엔드포인트 테스트
- [ ] Production URL 메모장에 기록

### 1시간 내
- [ ] README.md에 Production URL 업데이트
- [ ] 팀에게 배포 완료 알림
- [ ] 간단한 스모크 테스트 실행

### 24시간 내
- [ ] Railway 모니터링 확인 (메트릭, 로그)
- [ ] 실제 브랜드 데이터로 테스트
- [ ] System 2와 통합 테스트

---

## 🔧 Troubleshooting {#troubleshooting}

### 문제 1: 빌드 실패

**증상**: Build failed, dependencies error

**해결**:
1. Settings → General → Root Directory가 `project-sonar`인지 확인
2. Deployments → 최신 배포 → View Logs에서 에러 확인
3. `requirements.txt` 문제라면 Railway에서 재배포 시도

### 문제 2: Health Check 실패 (503/504)

**증상**: `/health` 접근 시 에러

**해결**:
1. Deployments → 최신 배포 상태 확인 (Active여야 함)
2. Logs에서 "Uvicorn running" 메시지 확인
3. 환경 변수 `PORT=${{PORT}}` 확인
4. Railway 대시보드에서 "Restart" 클릭

### 문제 3: Agents Not Operational

**증상**: `"mas_operational": false`

**해결**:
1. Logs에서 agent 초기화 에러 확인
2. Memory limit 확인 (Railway 무료 플랜: 512MB)
3. 필요시 Railway 플랜 업그레이드

### 문제 4: 배포는 되는데 느림

**증상**: API 응답 시간 > 2초

**해결**:
1. Railway Metrics 확인 (CPU, Memory 사용률)
2. Cold start 이슈일 수 있음 (첫 요청은 느릴 수 있음)
3. 실제 사용 시 개선됨 (warm instance)

---

## 📞 도움이 필요하면?

### Railway 관련
- **공식 문서**: https://docs.railway.app/
- **Discord**: https://discord.gg/railway
- **Status Page**: https://status.railway.app/

### NERDX Project 관련
- **Email**: sean@koreafnbpartners.com
- **GitHub Issues**: https://github.com/KFP-SEAN/nerdx-apec-mvp/issues
- **문서**: [DEPLOYMENT_INSTRUCTIONS.md](./DEPLOYMENT_INSTRUCTIONS.md)

---

## 🎯 Production URL 업데이트 방법

배포 완료 후 Production URL을 문서에 기록하세요:

**1. README.md 업데이트**:
```markdown
### System 3: Project Sonar (NBRS 2.0)
- **Status**: ✅ Production
- **URL**: https://your-actual-url.up.railway.app
- **Port**: 8005
```

**2. SYSTEM_INTEGRATION_GUIDE.md 업데이트**:
```markdown
| System 3 | Port 8005 | ✅ Production | https://your-url |
```

**3. Git 커밋**:
```bash
cd /c/Users/seans/nerdx-apec-mvp
git add README.md SYSTEM_INTEGRATION_GUIDE.md
git commit -m "Update Project Sonar production URL"
git push origin main
```

---

## 🌟 축하합니다!

**3개 시스템 모두 Production 배포 완료!**

```
✅ System 1 - Independent Accounting
✅ System 2 - Warm Lead Generation
✅ System 3 - Project Sonar (이제 막 배포 완료!)
```

**NERDX Resonance Economy Platform** 완성! 🎊

---

## 📚 다음 단계

### Phase 2 기능 (다음 분기)
1. 실제 API 키 연동 (WIPO, KIS, Naver)
2. Neo4j 브랜드 관계 그래프
3. Redis 실시간 Feature Store
4. MLflow 모델 버전 관리
5. Continual Learning 구현

### 비즈니스 성장
1. 실제 고객 데이터로 테스트
2. NBRS 2.0 정확도 검증
3. 첫 AI 협력 제안서 생성
4. 스테이크홀더 데모

---

**배포 준비 완료!**
**시작하세요**: https://railway.app/dashboard

🚀 **Let's deploy and make it live!**

---

**작성일**: 2025-10-27
**소요 시간**: 10분
**난이도**: ⭐ 쉬움
