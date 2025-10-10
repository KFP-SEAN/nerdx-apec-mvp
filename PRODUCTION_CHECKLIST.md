# ✅ Production Deployment Checklist

## 📋 개요

Production 배포 전 필수 확인 사항입니다. 모든 항목을 확인 후 배포를 진행하세요.

**최종 업데이트**: 2025-10-11
**대상 환경**: Production

---

## 🔐 보안 (Security)

### 환경 변수

- [ ] 모든 비밀 키가 환경 변수로 설정됨
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] Production 환경 변수가 별도로 관리됨
- [ ] AWS Secrets Manager 또는 유사 서비스 사용 고려

### API 키 및 토큰

- [ ] Shopify Storefront API 토큰 생성
- [ ] Shopify Admin API 토큰 생성 (Custom App)
- [ ] Webhook Secret 설정
- [ ] JWT Private/Public 키 생성 (RS256)
- [ ] 모든 키가 32자 이상

### SSL/TLS

- [ ] Frontend SSL 인증서 설정 (Vercel 자동)
- [ ] Custom App SSL 인증서 (Let's Encrypt)
- [ ] Neo4j TLS 활성화
- [ ] 모든 통신이 HTTPS

### 보안 헤더

- [ ] Helmet.js 활성화
- [ ] CORS 설정 완료
- [ ] Rate Limiting 설정
- [ ] Content Security Policy (CSP)

---

## 🏗️ 인프라 (Infrastructure)

### Frontend (Vercel)

- [ ] Vercel 프로젝트 생성
- [ ] GitHub Repository 연결
- [ ] Build 명령어 설정
- [ ] 환경 변수 입력
- [ ] 도메인 연결
- [ ] CDN 설정 확인

### Custom Shopify App

- [ ] 서버 인스턴스 생성 (EC2/Heroku)
- [ ] Node.js 18+ 설치
- [ ] PM2 또는 유사 프로세스 관리자 설정
- [ ] Nginx 리버스 프록시 설정
- [ ] Auto-scaling 설정 (선택사항)

### 데이터베이스

- [ ] Neo4j Aura 인스턴스 생성
- [ ] Connection pooling 설정
- [ ] 백업 전략 수립
- [ ] 인덱스 생성

### 캐시

- [ ] Redis 인스턴스 생성
- [ ] Connection string 설정
- [ ] Persistence 설정 (선택사항)

---

## 🛒 Shopify 설정

### Store 설정

- [ ] Development Store → Production 전환
- [ ] Shopify 플랜 선택 및 결제
- [ ] 결제 게이트웨이 설정 (Shopify Payments/Stripe)
- [ ] 배송 정책 설정
- [ ] 환불 정책 설정
- [ ] 세금 설정

### 제품 데이터

- [ ] 모든 제품 정보 입력
- [ ] 제품 이미지 업로드 (고해상도)
- [ ] Metafields 설정:
  - [ ] `ar_enabled`
  - [ ] `ar_asset_url`
  - [ ] `apec_limited`
  - [ ] `stock_remaining`
- [ ] 재고 수량 설정
- [ ] 가격 확인

### API 설정

- [ ] Custom App 생성
- [ ] Storefront API 권한 설정
- [ ] Admin API 권한 설정
- [ ] Access Token 생성 및 저장

### Webhook 설정

- [ ] `orders/paid` → Custom App URL
- [ ] `orders/cancelled` → Custom App URL
- [ ] `refunds/create` → Custom App URL
- [ ] Webhook Secret 저장
- [ ] Test webhook 발송 확인

---

## 🧪 테스트 (Testing)

### Unit Tests

- [ ] Frontend 테스트 통과 (24/24)
- [ ] Shopify Service 테스트 통과
- [ ] 커버리지 60% 이상

### Integration Tests

- [ ] 구매 플로우 테스트
- [ ] AR 액세스 플로우 테스트
- [ ] 에러 핸들링 테스트

### E2E Tests

- [ ] Playwright 브라우저 설치
- [ ] 제품 목록 테스트
- [ ] 체크아웃 플로우 테스트
- [ ] AR 뷰어 테스트
- [ ] 모바일 반응형 테스트

### Performance Tests

- [ ] Lighthouse 스코어 90+ (Desktop)
- [ ] Lighthouse 스코어 80+ (Mobile)
- [ ] Core Web Vitals 확인
- [ ] API 응답 시간 < 500ms

### Security Tests

- [ ] OWASP Top 10 확인
- [ ] npm audit 실행 및 수정
- [ ] SSL Labs 테스트 A+ 등급
- [ ] Security headers 확인

---

## 🎨 Frontend

### 코드 품질

- [ ] TypeScript 타입 에러 없음
- [ ] ESLint 경고 없음
- [ ] 불필요한 console.log 제거
- [ ] 주석 정리

### 최적화

- [ ] 이미지 최적화 (Next.js Image)
- [ ] Code splitting 확인
- [ ] Lazy loading 적용
- [ ] Bundle size 확인 (<1MB)

### SEO

- [ ] Meta tags 설정
- [ ] Open Graph 설정
- [ ] Sitemap 생성
- [ ] robots.txt 설정

### Analytics

- [ ] Google Analytics 설정 (선택사항)
- [ ] Vercel Analytics 활성화
- [ ] Error tracking (Sentry 등)

---

## 🔧 Custom Shopify App

### 코드 품질

- [ ] 에러 처리 완료
- [ ] 로깅 설정 완료
- [ ] Winston 또는 유사 로깅 라이브러리
- [ ] 불필요한 console.log 제거

### Webhook 처리

- [ ] HMAC 서명 검증
- [ ] 멱등성 체크 (Redis)
- [ ] 재시도 로직 (Exponential Backoff)
- [ ] Dead Letter Queue

### AR 액세스

- [ ] JWT 토큰 생성
- [ ] 토큰 검증
- [ ] 90일 만료 설정
- [ ] Neo4j 관계 생성

### 모니터링

- [ ] Prometheus metrics 활성화
- [ ] Health check 엔드포인트
- [ ] Readiness probe
- [ ] Liveness probe

---

## 📊 모니터링 (Monitoring)

### 애플리케이션

- [ ] Uptime 모니터링 (UptimeRobot/Pingdom)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Log aggregation (CloudWatch/Papertrail)

### 인프라

- [ ] CPU/Memory 모니터링
- [ ] Disk 사용량 모니터링
- [ ] Network traffic 모니터링
- [ ] Database 성능 모니터링

### 알림

- [ ] Slack/Discord webhook 설정
- [ ] 이메일 알림 설정
- [ ] Critical 에러 즉시 알림
- [ ] Daily report 설정

---

## 💾 백업 (Backup)

### 데이터베이스

- [ ] Neo4j 자동 백업 설정
- [ ] 백업 주기: 일일
- [ ] 백업 보관 기간: 30일
- [ ] S3 또는 유사 저장소에 업로드

### 코드

- [ ] GitHub Repository 보호
- [ ] Branch protection rules
- [ ] Tag 릴리스 생성
- [ ] Release notes 작성

### 환경 설정

- [ ] 모든 환경 변수 문서화
- [ ] Secrets 백업 (안전한 위치)
- [ ] Infrastructure as Code (Terraform 등)

---

## 🌐 DNS 및 도메인

### 도메인 설정

- [ ] 도메인 구매 완료
- [ ] DNS 설정 완료:
  - [ ] Frontend (CNAME → Vercel)
  - [ ] Custom App (A → EC2)
  - [ ] API (선택사항)
- [ ] TTL 설정 (3600초)

### SSL 인증서

- [ ] Let's Encrypt 자동 갱신 설정
- [ ] Certbot 설치 및 설정
- [ ] SSL 만료 알림 설정

---

## 📧 통지 (Notifications)

### SMTP 설정

- [ ] SMTP 서버 설정 (Gmail/SendGrid)
- [ ] 발신 이메일 주소 확인
- [ ] SPF/DKIM 레코드 설정
- [ ] 테스트 이메일 발송 확인

### 이메일 템플릿

- [ ] AR 액세스 코드 이메일
- [ ] 주문 확인 이메일 (Shopify 기본)
- [ ] 환불 확인 이메일

---

## 📱 모바일

### 반응형 디자인

- [ ] iPhone 테스트
- [ ] Android 테스트
- [ ] Tablet 테스트
- [ ] 다양한 화면 크기 확인

### PWA (선택사항)

- [ ] manifest.json 설정
- [ ] Service Worker 설정
- [ ] 오프라인 지원

---

## 🚀 배포 (Deployment)

### Pre-Deployment

- [ ] 스테이징 환경 테스트
- [ ] 데이터 마이그레이션 계획
- [ ] 롤백 계획 수립
- [ ] 배포 일정 공지

### Deployment

- [ ] Frontend Vercel 배포
- [ ] Custom App 배포
- [ ] DNS 업데이트
- [ ] Webhook URL 업데이트

### Post-Deployment

- [ ] Smoke Tests 실행
- [ ] Health check 확인
- [ ] 성능 모니터링
- [ ] 에러 로그 확인

---

## 📄 문서 (Documentation)

### 기술 문서

- [ ] README.md 업데이트
- [ ] API 문서 작성
- [ ] 아키텍처 다이어그램
- [ ] 배포 가이드

### 운영 문서

- [ ] Runbook 작성
- [ ] 장애 대응 매뉴얼
- [ ] 롤백 절차
- [ ] 백업/복구 절차

### 사용자 문서

- [ ] 사용자 가이드 (선택사항)
- [ ] FAQ
- [ ] 고객 지원 정보

---

## 🎯 성능 목표

### Frontend

- [ ] First Contentful Paint < 1.8s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Time to Interactive < 3.8s
- [ ] Cumulative Layout Shift < 0.1

### Backend

- [ ] API 응답 시간 < 500ms (p95)
- [ ] Database 쿼리 시간 < 100ms
- [ ] Webhook 처리 시간 < 1s
- [ ] Uptime 99.9%

---

## 💰 비용 (Cost)

### 월간 예상 비용

- [ ] Vercel: ~$20
- [ ] Shopify: ~$79
- [ ] AWS EC2: ~$15
- [ ] Neo4j Aura: ~$65
- [ ] 도메인: ~$1
- [ ] **총계**: ~$180/월

### 예산 확인

- [ ] 예산 승인 완료
- [ ] 결제 수단 등록
- [ ] 비용 알림 설정

---

## 📞 연락처

### 긴급 연락망

- [ ] 개발팀 연락처
- [ ] DevOps 팀 연락처
- [ ] 고객 지원팀 연락처
- [ ] Shopify 지원팀

### 외부 서비스 지원

- [ ] Vercel Support
- [ ] AWS Support (선택사항)
- [ ] Shopify Partners Support
- [ ] Neo4j Support

---

## ✅ 최종 확인

### 배포 직전

- [ ] 모든 체크리스트 항목 완료
- [ ] 팀 전체 리뷰 완료
- [ ] 스테이크홀더 승인
- [ ] 배포 시간 확정

### 배포 직후

- [ ] 모니터링 대시보드 확인 (30분)
- [ ] 에러 로그 확인
- [ ] 사용자 피드백 수집
- [ ] Post-mortem 회의 일정

---

## 🎉 Go-Live!

**모든 항목을 확인하셨나요?**

✅ **Yes** → 배포를 진행하세요!
❌ **No** → 미완료 항목을 완료 후 다시 확인하세요.

---

**Checklist 버전**: 1.0
**마지막 업데이트**: 2025-10-11
**다음 리뷰**: 배포 후 1주일

---

*이 체크리스트를 모두 완료하면 안전하고 성공적인 Production 배포가 가능합니다.*
