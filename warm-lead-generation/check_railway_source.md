# Railway 배포 소스 확인 필요

## 문제
Railway가 redeploy 후에도 여전히 구버전 코드를 실행하고 있습니다.

## 확인 사항

### Railway Dashboard에서 확인:

1. **Service Settings → Source**
   - Repository: `KFP-SEAN/nerdx-apec-mvp` 확인
   - Branch: `main` 확인
   - Root Directory: `warm-lead-generation` 확인

2. **Latest Deployment 정보**
   - 어떤 커밋을 배포했는지 확인
   - 커밋 해시가 최신 커밋(dc56b5d 또는 그 이후)인지 확인

3. **Build 로그 확인**
   - "Cloning repository..." 부분 확인
   - 어떤 커밋 해시를 체크아웃했는지 확인

## 예상 원인

1. **캐시된 이미지 사용**
   - Railway가 새로 빌드하지 않고 캐시된 이미지 재사용

2. **GitHub Webhook 미설정**
   - Railway가 GitHub push를 감지하지 못함
   - Manual trigger만 가능한 상태

3. **잘못된 브랜치/커밋 참조**
   - 오래된 커밋을 참조하고 있을 수 있음

## 해결 방법

### Option 1: Settings에서 강제 리빌드 설정

1. Service Settings → Deploy
2. "Build Cache" 비활성화 (또는 "Clear Build Cache")
3. 다시 Redeploy

### Option 2: 새로운 빌드 트리거

Deployment 상세 페이지에서:
- "Deploy from latest commit" 옵션 찾기
- 또는 특정 커밋 해시 입력: `dc56b5d`

### Option 3: Service 재생성 (최후 수단)

1. 현재 service의 environment variables 백업
2. New Service 생성
3. GitHub repo 연결
4. Root directory: `warm-lead-generation` 설정
5. Environment variables 복원
6. 배포

## 현재 GitHub 상태

최신 커밋들:
- dc56b5d: Add deployment status documentation
- a0394a1: Trigger Railway redeploy for NBRS fix
- 3627182: Trigger Railway redeploy with fixed NBRS model
- f2cfc90: Fix NBRS calculation logic for accurate lead scoring ← **핵심 수정**

변경된 파일:
- models/nbrs_models.py ← **완전히 재작성됨**
- test_fixed_nbrs.py

## 검증 방법

배포 후 Railway 로그에서 확인:
```
[NBRS] Calculated score for Premium Corp: NBRS=99.25, Tier=tier1, BA=100.0, MP=98.8, DP=98.8
```

현재 (구버전):
```
[NBRS] Calculated score for Premium Corp: NBRS=15.17, Tier=tier4, BA=20.6, MP=7.5, DP=17.2
```

## 다음 단계

Railway Dashboard → Service Settings에서:
1. Source 설정 재확인
2. Build cache 클리어
3. 특정 커밋(dc56b5d)으로 배포 시도
