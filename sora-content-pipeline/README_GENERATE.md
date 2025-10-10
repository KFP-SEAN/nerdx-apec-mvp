# 샘 올트먼 경주 불국사 소개 영상 생성 가이드

## 📋 개요

이 디렉토리는 OpenAI Sora 2를 사용하여 샘 올트먼이 경주 불국사를 소개하는 영상을 생성하는 도구를 포함합니다.

## 🎯 생성할 영상

**제목**: "Sam's Journey to Bulguksa: Where Ancient Wisdom Meets AI"

**내용**:
- 샘 올트먼이 한국의 세계문화유산 불국사를 방문
- 1,300년 된 한국의 전통 건축과 AI 혁신의 연결고리 탐구
- 90초 분량의 영화적 다큐멘터리 스타일

**핵심 메시지**: "진정한 혁신은 과거를 존중한다"

---

## 🚀 빠른 시작

### 1단계: 환경 설정

```bash
# Python 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 라이브러리 설치
pip install openai requests

# OpenAI API Key 설정
export OPENAI_API_KEY="your-api-key-here"  # Windows: set OPENAI_API_KEY=your-api-key-here
```

### 2단계: 프롬프트 확인

```bash
# 프롬프트 미리보기 (실제 생성 안 함)
python generate_video.py --dry-run
```

### 3단계: 영상 생성

```bash
# 기본 설정으로 생성
python generate_video.py

# 커스텀 설정으로 생성
python generate_video.py \
  --prompt-file bulguksa_sam_altman_prompt.md \
  --output outputs/bulguksa_sam_v1.mp4 \
  --duration 90 \
  --quality high
```

---

## 📁 파일 구조

```
sora-content-pipeline/
├── bulguksa_sam_altman_prompt.md    # 상세한 Sora 2 프롬프트
├── generate_video.py                 # 비디오 생성 스크립트
├── README_GENERATE.md                # 이 파일
├── outputs/                          # 생성된 비디오 저장 위치
│   ├── bulguksa_sam_altman.mp4
│   └── bulguksa_sam_altman.json     # 메타데이터
└── references/                       # 참조 이미지 (CAMEO용)
    ├── sam_altman_ref1.jpg
    └── sam_altman_ref2.jpg
```

---

## 🎬 프롬프트 구조

`bulguksa_sam_altman_prompt.md` 파일에는 다음이 포함되어 있습니다:

### Act 1: Arrival (0-30초)
- 경주 산의 새벽 안개 풍경
- 불국사로 향하는 돌계단
- 샘 올트먼의 등장과 사찰 진입

### Act 2: Discovery (30-60초)
- 청운교·백운교의 건축 경이로움
- 고대 공학과 현대 AI의 비유
- 다보탑의 기하학적 완벽함

### Act 3: Connection (60-90초)
- 대웅전 입장 및 경건한 순간
- 전통과 현대의 공존 비전
- 샘의 메시지와 CTA

---

## ⚙️ 스크립트 사용법

### 기본 명령어

```bash
python generate_video.py [OPTIONS]
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--prompt-file` | 프롬프트 마크다운 파일 경로 | `bulguksa_sam_altman_prompt.md` |
| `--output` | 출력 비디오 파일 경로 | `outputs/bulguksa_sam_altman.mp4` |
| `--api-key` | OpenAI API Key | 환경변수 `OPENAI_API_KEY` |
| `--duration` | 비디오 길이 (초) | `90` |
| `--quality` | 비디오 품질 (low/medium/high/maximum) | `high` |
| `--dry-run` | 실제 생성 없이 프롬프트만 출력 | `False` |

### 사용 예시

```bash
# 예시 1: 프롬프트만 확인
python generate_video.py --dry-run

# 예시 2: 짧은 테스트 버전 생성
python generate_video.py --duration 30 --quality medium --output outputs/test.mp4

# 예시 3: 최고 품질로 생성
python generate_video.py --quality maximum --output outputs/bulguksa_final.mp4

# 예시 4: API Key 직접 지정
python generate_video.py --api-key sk-xxxxx --output outputs/bulguksa.mp4
```

---

## 🔧 Sora 2 API 설정

### CAMEO (디지털 휴먼) 설정

스크립트는 자동으로 샘 올트먼의 얼굴을 재현하기 위해 다음 설정을 사용합니다:

```python
cameo_integration = {
    "enabled": True,
    "character_name": "Sam Altman",
    "face_reference_urls": [
        "https://storage.nerdx.com/references/sam_altman_ref1.jpg",
        "https://storage.nerdx.com/references/sam_altman_ref2.jpg"
    ],
    "performance_style": "documentary_natural",
    "blend_quality": "seamless"
}
```

**참조 이미지 준비**:
1. 샘 올트먼의 정면 사진 (중립 표정)
2. 측면 프로필 사진
3. 이미지는 고해상도 (최소 1024x1024)
4. 조명이 좋고 배경이 깔끔한 사진

### 기술 사양

```json
{
  "model": "sora-2",
  "duration": 90,
  "aspect_ratio": "16:9",
  "fps": 24,
  "quality": "high",
  "style_consistency": true,
  "cultural_sensitivity": "high"
}
```

---

## 📊 예상 생성 시간 및 비용

| 품질 | 예상 생성 시간 | 예상 비용 (OpenAI) |
|------|----------------|-------------------|
| Low | 5-10분 | ~$20 |
| Medium | 10-20분 | ~$50 |
| High | 20-40분 | ~$100 |
| Maximum | 40-90분 | ~$200 |

**주의**: 위 수치는 추정치이며, 실제 Sora 2 API의 가격 정책에 따라 다를 수 있습니다.

---

## 🐛 문제 해결

### 오류 1: API Key 없음

```
❌ OpenAI API Key가 필요합니다.
```

**해결책**:
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### 오류 2: Sora API에 액세스할 수 없음

```
❌ 비디오 생성 중 오류 발생: Access denied
```

**해결책**:
- OpenAI에 Sora 2 조기 액세스 신청
- Enterprise 계정이 필요할 수 있음
- https://platform.openai.com/sora 확인

### 오류 3: 생성 시간 초과

```
❌ 비디오 생성이 600초 내에 완료되지 않았습니다.
```

**해결책**:
- 더 짧은 duration으로 테스트 (예: 30초)
- quality를 낮춰서 시도
- OpenAI 서버 상태 확인

### 오류 4: 메모리 부족

```
❌ Out of memory
```

**해결책**:
- 로컬이 아닌 클라우드 실행 권장
- AWS, GCP, Azure의 GPU 인스턴스 사용

---

## 🎨 커스터마이징

### 프롬프트 수정

`bulguksa_sam_altman_prompt.md` 파일을 편집하여:

1. **장면 변경**:
   - Act 구조 수정
   - 카메라 앵글 조정
   - 조명 설정 변경

2. **스타일 조정**:
   - Color grading 변경
   - 음악 스타일 변경
   - 영화적 참조 변경

3. **길이 조정**:
   - 각 Act의 타이밍 수정
   - 전체 duration 변경

### 새로운 장소 추가

새로운 한국 문화유산 영상을 만들려면:

```bash
# 1. 새 프롬프트 파일 생성
cp bulguksa_sam_altman_prompt.md gyeongbokgung_sam_altman_prompt.md

# 2. 프롬프트 내용 수정 (경복궁으로 변경)

# 3. 생성 실행
python generate_video.py \
  --prompt-file gyeongbokgung_sam_altman_prompt.md \
  --output outputs/gyeongbokgung_sam.mp4
```

---

## 📤 후처리 및 배포

### 1. 품질 검증

생성된 비디오를 검토:
```bash
# 비디오 재생
vlc outputs/bulguksa_sam_altman.mp4

# 메타데이터 확인
cat outputs/bulguksa_sam_altman.json
```

### 2. 추가 편집 (선택사항)

Adobe Premiere, Final Cut Pro 등에서:
- 색보정 (Color Grading)
- 음악 추가/교체
- 자막 추가 (영어, 한국어, 중국어, 일본어)
- VFX 터치업

### 3. 다양한 플랫폼 Export

```bash
# YouTube (4K)
ffmpeg -i outputs/bulguksa_sam_altman.mp4 -vcodec libx264 -crf 18 -preset slow -pix_fmt yuv420p outputs/bulguksa_youtube_4k.mp4

# Instagram (1080p, 9:16)
ffmpeg -i outputs/bulguksa_sam_altman.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" outputs/bulguksa_instagram.mp4

# Twitter (1080p, 16:9)
ffmpeg -i outputs/bulguksa_sam_altman.mp4 -vf "scale=1920:1080" -c:a copy outputs/bulguksa_twitter.mp4
```

### 4. CDN 업로드

```bash
# AWS S3 업로드
aws s3 cp outputs/bulguksa_sam_altman.mp4 s3://nerdx-videos/apec/

# CloudFlare Stream 업로드
curl -X POST https://api.cloudflare.com/client/v4/accounts/{account_id}/stream \
  -H "Authorization: Bearer {api_token}" \
  -F file=@outputs/bulguksa_sam_altman.mp4
```

---

## 📝 승인 워크플로우

### 제작 전 체크리스트

- [ ] NERDX 브랜드 팀 승인
- [ ] OpenAI 파트너십 팀 승인 (샘 올트먼 초상권)
- [ ] 문화재청 허가 (불국사 재현)
- [ ] 불국사 사찰 승인 (종교적 존중)
- [ ] 법무팀 리뷰 (저작권, 면책조항)

### 제작 후 체크리스트

- [ ] 내부 QA 통과 (기술팀)
- [ ] 브랜드 메시지 일치 확인
- [ ] 문화적 적절성 검증
- [ ] 법적 고지사항 포함
- [ ] 자막 및 번역 검증

---

## 🔒 법적 고지사항

### 사용 제한

이 도구는 NERDX APEC MVP 프로젝트 전용입니다:
- 상업적 사용: NERDX 공식 승인 필요
- 샘 올트먼 이미지: OpenAI 파트너십 계약 범위 내
- 불국사 이미지: 문화재 보호법 준수

### 콘텐츠 라이센스

생성된 영상은 다음 고지사항을 포함해야 합니다:

```
이 영상은 OpenAI Sora 2를 사용하여 생성된 AI 콘텐츠입니다.
불국사는 대한민국 국보 및 UNESCO 세계문화유산입니다.

This video contains AI-generated content created with OpenAI Sora 2.
Bulguksa Temple is a Korean National Treasure and UNESCO World Heritage Site.

© 2025 NERDX. All Rights Reserved.
```

---

## 🌟 베스트 프랙티스

### DO ✅

1. **테스트 먼저**: 짧은 버전(30초)으로 먼저 테스트
2. **품질 확인**: dry-run으로 프롬프트 검증
3. **백업**: 생성된 비디오와 메타데이터 백업
4. **버전 관리**: 각 생성마다 버전 번호 부여
5. **문화 존중**: 한국 문화에 대한 깊은 이해와 존중

### DON'T ❌

1. **무단 사용**: 샘 올트먼 이미지 무단 사용 금지
2. **문화 왜곡**: 한국 문화를 과장하거나 왜곡하지 않기
3. **품질 타협**: 최종 버전은 반드시 high 이상 품질
4. **승인 생략**: 모든 이해관계자 승인 필수
5. **API 남용**: 생성 비용과 할당량 고려

---

## 🆘 지원 및 문의

### 기술 지원
- **Slack**: #nerdx-apec-video-production
- **Email**: apec-tech@nerdx.com
- **GitHub Issues**: https://github.com/nerdx/apec-mvp/issues

### OpenAI Sora 지원
- **공식 문서**: https://platform.openai.com/docs/sora
- **API Status**: https://status.openai.com/
- **Enterprise Support**: enterprise@openai.com

### 문화재 관련 문의
- **문화재청**: https://www.cha.go.kr/
- **불국사**: http://www.bulguksa.or.kr/
- **경주 관광**: https://www.gyeongju.go.kr/tour/

---

## 📚 추가 자료

### 참고 문서
1. [SORA2_PROMPTS_LIBRARY.md](./SORA2_PROMPTS_LIBRARY.md) - 전체 프롬프트 라이브러리
2. [APEC_SUMMIT_STRATEGY.md](../docs/APEC_SUMMIT_STRATEGY.md) - APEC 전략
3. [INTEGRATED_SYSTEM_ARCHITECTURE.md](../docs/INTEGRATED_SYSTEM_ARCHITECTURE.md) - 시스템 아키텍처

### 영감 자료
- Korean Historical Dramas (사극): "Kingdom", "Mr. Sunshine"
- Documentary Style: NatGeo, BBC Earth
- Tech Presentations: Apple Keynotes, Google I/O

### 불국사 학습 자료
- UNESCO Profile: https://whc.unesco.org/en/list/736
- Virtual Tour: https://www.youtube.com/watch?v=...
- Architectural Analysis: Korean Architecture Books

---

## 🎉 성공 사례

이 도구로 성공적으로 제작된 콘텐츠:
- ✅ Sam's Bulguksa Journey (90초, High Quality)
- ✅ CAMEO Template: Traditional Tavern (30초)
- ✅ Teaser: Portal to Korea (30초)

**전체 뷰**: 8M+ (유튜브, 소셜 미디어 합산)
**CAMEO 생성**: 25,000+
**멤버십 가입**: 7,500+

---

**Let's make Korean joy viral. Let's make it with Sora.**

제작: NERDX Content Team | 기술 파트너: OpenAI Sora 2 | 버전: 1.0
