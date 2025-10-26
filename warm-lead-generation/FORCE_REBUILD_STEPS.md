# Railway 강제 리빌드 방법

## 문제
Railway가 코드 변경사항을 감지하지 못하고 캐시된 이미지를 계속 사용하고 있습니다.

## 해결 방법 (우선순위 순)

### Option 1: Settings에서 Source 재연결

1. Railway Dashboard → `warm-lead-generation` service
2. **Settings** 탭 클릭
3. **Source** 섹션 찾기
4. **"Disconnect Source"** 클릭
5. **"Connect to GitHub"** 다시 클릭
6. Repository: `KFP-SEAN/nerdx-apec-mvp` 선택
7. Branch: `main` 선택
8. Root Directory: `warm-lead-generation` 입력
9. **"Deploy Now"** 클릭

### Option 2: Build Cache 강제 클리어

Railway Dashboard → Service Settings에서:

1. **"Settings"** 탭
2. Scroll down to **"Danger Zone"** 또는 **"Advanced"** 섹션
3. **"Clear Build Cache"** 또는 **"Rebuild"** 버튼 찾기
4. 클릭 후 확인

### Option 3: Environment Variable 변경으로 강제 리빌드

1. **Variables** 탭
2. 더미 변수 추가: `FORCE_REBUILD=2025-10-26-v2`
3. 자동으로 새 빌드 트리거됨
4. 배포 완료 후 이 변수 삭제 가능

### Option 4: Deployment 페이지에서 직접 재배포

1. **Deployments** 탭
2. 상단의 **"New Deployment"** 또는 **"Deploy"** 버튼 클릭
3. **"From Branch"** 선택
4. Branch: `main`
5. **"Deploy"** 클릭

### Option 5: CLI로 강제 배포 (현재 진행 중)

Railway CLI를 사용하여 직접 배포:
```bash
cd C:\Users\seans\nerdx-apec-mvp\warm-lead-generation
railway up --service warm-lead-generation
```

## 검증 방법

배포 후 다음 명령어로 확인:

```bash
curl -X POST "https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/calculate" ^
  -H "Content-Type: application/json" ^
  -d "{...}"
```

**성공 시:**
```json
{
  "nbrs_score": 99.25,  // ← 99, NOT 15.17!
  "tier": "tier1",      // ← tier1, NOT tier4!
  ...
}
```

## Railway 로그 확인

배포 후 로그에서 다음을 확인:
```
[NBRS] Calculated score: NBRS=99.25, Tier=tier1, BA=100.0, MP=98.8, DP=98.8
```

현재 (잘못된 버전):
```
[NBRS] Calculated score: NBRS=15.17, Tier=tier4, BA=20.6, MP=7.5, DP=17.2
```

## 빌드 로그 체크리스트

Deployment 상세 페이지 → Build Logs에서 확인:

- [ ] `Cloning repository KFP-SEAN/nerdx-apec-mvp`
- [ ] 커밋 해시: `dc56b5d` 또는 `f2cfc90` (최신 커밋)
- [ ] `Installing Python dependencies from requirements.txt`
- [ ] `models/nbrs_models.py` 파일이 포함되어 있는지
- [ ] 빌드 완료 메시지

## 가장 빠른 방법

**Option 3 (Environment Variable 변경)**이 가장 확실합니다:

1. Variables 탭
2. New Variable: `FORCE_REBUILD_V2=true`
3. Add → 자동으로 새 배포 시작
4. 1-2분 대기
5. 테스트

이 방법은 Railway가 변경사항을 감지하고 반드시 새 빌드를 트리거합니다.
