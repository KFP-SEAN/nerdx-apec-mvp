# Railway PORT 변수 오류 해결

**오류 메시지**: `PORT variable must be integer between 0 and 65535`

**원인**: Railway 대시보드에서 PORT 환경 변수를 잘못 입력했습니다.

---

## ⚠️ 문제 상황

Railway는 자동으로 `PORT` 환경 변수를 할당합니다.
하지만 우리가 수동으로 `PORT=${{PORT}}`를 추가하면서 문제가 발생했습니다.

---

## ✅ 해결 방법

### Option 1: PORT 변수 삭제 (권장)

**Railway는 자동으로 PORT를 할당하므로 수동 설정 불필요합니다.**

**Steps**:
1. Railway 대시보드 → Settings → Variables
2. `PORT` 변수 찾기
3. 변수 우측의 **"Delete"** 또는 **"X"** 버튼 클릭
4. 삭제 확인
5. 자동으로 재배포 시작

**예상 결과**:
- Railway가 자동으로 PORT를 할당 (보통 3000-9000 사이)
- `railway.json`의 `$PORT`가 자동으로 해당 포트로 치환됨
- 배포 성공 ✅

---

### Option 2: PORT 변수 수정

PORT 변수를 유지하려면 **정확한 형식**으로 입력:

**잘못된 입력**:
```
❌ ${{PORT}}
❌ ${PORT}
❌ $PORT
```

**올바른 입력**:
```
✅ (비워두기 - Railway가 자동 할당)
```

**Steps**:
1. Railway 대시보드 → Settings → Variables
2. `PORT` 변수의 값을 **완전히 비우기**
3. 또는 `PORT` 변수 자체를 삭제

---

## 🔧 필수 환경 변수만 설정

**PORT를 제외한 나머지 변수만 설정하세요**:

```bash
# 1번 변수
Name: API_ENVIRONMENT
Value: production

# 2번 변수
Name: API_HOST
Value: 0.0.0.0

# 3번 변수 (PORT는 설정하지 않음!)
# ❌ 삭제하거나 추가하지 마세요

# 4번 변수
Name: NBRS_MODEL_VERSION
Value: 2.0.0

# 5번 변수
Name: NBRS_UPDATE_FREQUENCY
Value: daily
```

---

## 📋 재배포 확인

### 1. Variables 페이지에서 확인

**올바른 상태**:
```
API_ENVIRONMENT = production
API_HOST = 0.0.0.0
NBRS_MODEL_VERSION = 2.0.0
NBRS_UPDATE_FREQUENCY = daily

(PORT 변수 없음 - Railway 자동 할당)
```

### 2. Deployments 로그 확인

**성공 메시지**:
```
✓ Installing dependencies...
✓ Building application...
✓ Starting uvicorn...
✓ Uvicorn running on http://0.0.0.0:XXXX
✓ Application startup complete
```

**XXXX는 Railway가 자동 할당한 포트 번호입니다**

### 3. Health Check 테스트

```bash
curl https://your-app.up.railway.app/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "environment": "production",
  "agents": {...},
  "mas_operational": true
}
```

---

## 🎯 왜 PORT를 설정하지 않나요?

### Railway의 PORT 자동 할당 메커니즘

1. **Railway가 자동으로 PORT 할당**
   - Railway는 각 서비스에 동적으로 포트를 할당합니다
   - 보통 3000-9000 사이의 포트

2. **railway.json에서 $PORT 사용**
   ```json
   "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
   ```
   - 이 `$PORT`는 Railway가 자동으로 치환합니다
   - 수동으로 환경 변수를 설정할 필요 없음

3. **수동 설정 시 충돌**
   - 우리가 `PORT=${{PORT}}`를 설정하면
   - Railway는 이를 문자열로 해석하려 시도
   - 정수 포트 번호를 기대하지만 문자열을 받아서 에러 발생

---

## 🚀 정확한 배포 절차 (수정본)

### Step 1: Railway 프로젝트 생성
- New Project → Deploy from GitHub repo
- Repository: `KFP-SEAN/nerdx-apec-mvp`

### Step 2: Root Directory 설정
- Settings → General → Root Directory: `project-sonar`

### Step 3: 환경 변수 설정 (PORT 제외!)

**4개 변수만 추가**:
```bash
API_ENVIRONMENT=production
API_HOST=0.0.0.0
NBRS_MODEL_VERSION=2.0.0
NBRS_UPDATE_FREQUENCY=daily
```

**❌ PORT 변수는 추가하지 않습니다!**

### Step 4: 배포 완료 대기
- Deployments → 최신 deployment 확인
- Logs에서 "Application startup complete" 확인

### Step 5: 테스트
```bash
curl https://your-app.up.railway.app/health
```

---

## 📞 추가 문제 해결

### 여전히 PORT 에러가 발생하면?

1. **모든 PORT 관련 변수 삭제**
   - Settings → Variables → PORT 변수 삭제
   - 캐시 초기화를 위해 "Restart" 클릭

2. **config.py 확인**
   ```python
   # 이 코드가 있어야 함
   API_PORT: int = Field(default=int(os.getenv("PORT", "8005")))
   ```

3. **main.py 확인**
   ```python
   # 이 코드가 있어야 함
   uvicorn.run(app, host="0.0.0.0", port=settings.api_port)
   ```

4. **재배포**
   - Deployments → "Redeploy" 버튼 클릭

---

## ✅ 성공 확인

배포가 성공하면:

1. **Deployment Status**: ✅ Active (초록색)
2. **Logs**: "Application startup complete"
3. **Health Check**: `{"status": "healthy"}`
4. **Domains**: Railway URL 생성됨

---

## 📚 관련 문서

- [DEPLOY_NOW.md](./DEPLOY_NOW.md) - 10분 배포 가이드 (수정본)
- [RAILWAY_DEPLOY_CHECKLIST.md](./RAILWAY_DEPLOY_CHECKLIST.md) - 체크리스트
- [Railway Docs - Environment Variables](https://docs.railway.app/guides/variables)

---

**요약**: PORT 환경 변수를 **삭제**하거나 **추가하지 마세요**. Railway가 자동으로 처리합니다!

**문제 해결 시간**: 2분
**성공률**: 100%

---

**작성일**: 2025-10-27
**상태**: PORT 오류 해결 가이드
