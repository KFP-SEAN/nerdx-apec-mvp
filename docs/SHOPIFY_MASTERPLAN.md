# 🎯 NERDX APEC MVP: Shopify 전환 마스터플랜

## 📋 프로젝트 개요

**프로젝트명**: NERDX Commerce - Shopify Headless 전환
**목표**: 기존 Stripe 기반 Phase 3를 Shopify Headless Commerce로 전환
**기간**: 2-3주 (15-20 영업일)
**예산**: $10,000-15,000
**팀 규모**: 3명 (풀타임)

### 핵심 목표

1. ✅ Shopify Headless Commerce로 완전 마이그레이션
2. ✅ 기존 Phase 1 (World Model) + Phase 2 (CAMEO) 100% 유지
3. ✅ AR 잠금 해제 시스템 Shopify Custom App으로 통합
4. ✅ 프론트엔드 UX 완전 제어 유지
5. ✅ APEC 일정 맞춤 (10월 말 런칭)

---

## 🏗️ 새로운 시스템 아키텍처

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      NERDX Frontend                              │
│                 (Next.js 14 - 변경 없음)                          │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Product │  │   Chat   │  │  CAMEO   │  │ Checkout │       │
│  │ Discovery│  │  (Maeju) │  │  Studio  │  │   Flow   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        ├─────────────┼─────────────┤             │
        │             │             │             │
        v             v             v             v
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐
│  Phase 1   │  │  Phase 2   │  │  Shopify   │  │    Shopify     │
│   World    │  │   Sora     │  │ Storefront │  │    Checkout    │
│   Model    │  │   CAMEO    │  │  API (R/O) │  │  (Hosted UI)   │
│            │  │            │  │            │  │                │
│  Neo4j DB  │  │  Redis Q   │  │  GraphQL   │  │ Payment Gateway│
│  Maeju AI  │  │  S3 Video  │  │  Products  │  │ Shop Pay       │
└────────────┘  └────────────┘  └──────┬─────┘  └────────┬───────┘
     ▲                                  │                  │
     │                                  │                  │
     │            ┌─────────────────────┴──────────────────┘
     │            │
     │            v
     │       ┌────────────────────────────────┐
     │       │      Shopify Admin API         │
     │       │   (Product/Order Management)   │
     │       └────────────┬───────────────────┘
     │                    │
     │                    v
     │       ┌────────────────────────────────┐
     │       │    Shopify Custom App          │
     │       │    (AR Unlock Service)         │
     │       │                                │
     │       │  ┌──────────────────────────┐  │
     │       │  │  Webhook Handlers        │  │
     │       │  │  - orders/paid           │  │
     │       │  │  - orders/cancelled      │  │
     │       │  │  - refunds/create        │  │
     │       │  └────────────┬─────────────┘  │
     │       │               │                │
     │       │               v                │
     │       │  ┌──────────────────────────┐  │
     │       │  │  AR Access Manager       │  │
     │       │  │  - Token Generation      │  │
     │       │  │  - Access Verification   │  │
     │       │  │  - Neo4j Integration     │  │
     │       │  └──────────────────────────┘  │
     │       └────────────────┬───────────────┘
     │                        │
     └────────────────────────┘
```

### 데이터 흐름

#### 1. 제품 발견 (Product Discovery)
```
User → Frontend → Phase 1 (Maeju AI)
                ↓
        Shopify Storefront API (제품 정보)
                ↓
        Neo4j (추천 엔진)
                ↓
        Frontend (제품 카드 표시)
```

#### 2. CAMEO 생성
```
User → Frontend → Phase 2 (Sora API)
                ↓
        Redis Queue
                ↓
        S3 Storage
                ↓
        Frontend (비디오 표시)
```

#### 3. 구매 프로세스
```
User → Frontend → Shopify Storefront API
                ↓
        Checkout.create()
                ↓
        Shopify Checkout (Hosted)
                ↓
        Payment Success
                ↓
        Webhook → Custom App
                ↓
        AR Unlock + Neo4j Update
                ↓
        User Notification
```

#### 4. AR 경험
```
User → Frontend → Custom App API
                ↓
        Check Access (Neo4j)
                ↓
        Generate Token
                ↓
        AR Asset Delivery
```

---

## 📅 상세 일정 (3주 = 15일)

### Week 1: 준비 및 기본 통합 (5일)

#### Day 1-2: 환경 설정
- [ ] Shopify Plus 계정 생성
- [ ] Storefront API 액세스 토큰 발급
- [ ] Admin API 액세스 토큰 발급
- [ ] Custom App 개발 환경 구축
- [ ] Shopify CLI 설치 및 설정

**산출물**:
- Shopify 계정 (nerdx.myshopify.com)
- API 크리덴셜 문서
- 개발 환경 README

#### Day 3-4: 제품 데이터 마이그레이션
- [ ] 기존 제품 데이터 Export
- [ ] Shopify Admin API로 제품 Import
- [ ] Metafields 설정 (AR, APEC Limited 등)
- [ ] 이미지 업로드 및 최적화
- [ ] 재고 수량 설정

**산출물**:
- 제품 데이터 마이그레이션 스크립트
- Shopify 제품 카탈로그 (테스트)

#### Day 5: Frontend 기본 통합
- [ ] Shopify Buy SDK 설치
- [ ] Storefront API GraphQL 클라이언트 구성
- [ ] 제품 목록 페이지 Shopify 연동
- [ ] 제품 상세 페이지 Shopify 연동

**산출물**:
- `lib/shopify.ts` - Shopify 클라이언트
- 제품 페이지 (Shopify 데이터 기반)

---

### Week 2: Custom App 개발 (5일)

#### Day 6-7: Custom App 기본 구조
- [ ] Shopify App 프로젝트 생성
- [ ] OAuth 인증 구현
- [ ] Webhook 등록 시스템
- [ ] Admin API 통합

**산출물**:
- `shopify-ar-app/` - Custom App 프로젝트
- Webhook Handler 기본 구조

#### Day 8-9: AR Unlock Logic
- [ ] `orders/paid` Webhook Handler
- [ ] AR 액세스 토큰 생성 로직
- [ ] Neo4j 통합 (Phase 1 연동)
- [ ] Phase 1 API 호출 (사용자/제품 정보)

**산출물**:
- AR Unlock Service
- Neo4j 연동 코드

#### Day 10: Refund & Cancellation
- [ ] `refunds/create` Webhook Handler
- [ ] AR 액세스 취소 로직
- [ ] `orders/cancelled` Webhook Handler

**산출물**:
- Refund Handler
- Cancellation Handler

---

### Week 3: 통합 및 테스트 (5일)

#### Day 11-12: Frontend 완전 통합
- [ ] Checkout Flow 구현 (Shopify SDK)
- [ ] Order Status 페이지
- [ ] AR Unlock 알림 UI
- [ ] 사용자 대시보드 (주문 내역)

**산출물**:
- Checkout 페이지 (완성)
- Order Success 페이지
- My Orders 페이지

#### Day 13: Phase 1/2 통합 테스트
- [ ] Maeju AI + Shopify 제품 추천 테스트
- [ ] CAMEO 생성 후 제품 구매 플로우 테스트
- [ ] Neo4j 데이터 동기화 검증

**산출물**:
- Integration Test Suite
- 테스트 결과 보고서

#### Day 14: E2E 테스트
- [ ] 전체 사용자 여정 테스트
  - 제품 발견 (Maeju)
  - CAMEO 생성
  - 구매
  - AR 잠금 해제
  - AR 경험
- [ ] 결제 테스트 (Test Mode)
- [ ] Webhook 테스트 (Shopify CLI)

**산출물**:
- E2E Test Report
- 버그 리스트

#### Day 15: 배포 및 모니터링
- [ ] Production Shopify 계정 설정
- [ ] Custom App 배포
- [ ] DNS/도메인 설정
- [ ] 모니터링 대시보드 구성
- [ ] 롤백 계획 수립

**산출물**:
- Deployment Checklist
- Monitoring Dashboard
- Rollback Plan

---

## 🛠️ 기술 스택

### 새로 추가되는 컴포넌트

#### 1. Shopify Storefront API Client
```typescript
// lib/shopify-client.ts
import Client from 'shopify-buy';

export const shopifyClient = Client.buildClient({
  domain: process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN!,
  storefrontAccessToken: process.env.NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN!
});
```

#### 2. Shopify Custom App (Node.js/Express)
```javascript
// shopify-ar-app/server.js
const express = require('express');
const { Shopify } = require('@shopify/shopify-api');
const neo4j = require('neo4j-driver');

const app = express();

// Webhook: Order Paid
app.post('/webhooks/orders/paid', async (req, res) => {
  const { order } = req.body;

  // Unlock AR for eligible products
  await unlockARExperience(order);

  res.sendStatus(200);
});

// AR Unlock Logic
async function unlockARExperience(order) {
  const { customer, line_items } = order;

  for (const item of line_items) {
    const arEnabled = item.properties?.find(p => p.name === 'ar_enabled')?.value;

    if (arEnabled === 'true') {
      // Generate access token
      const token = generateARToken(customer.id, item.product_id);

      // Store in Neo4j
      await neo4jService.createARAccess({
        userId: customer.id,
        productId: item.product_id,
        token,
        orderId: order.id
      });

      // Notify user
      await sendARUnlockNotification(customer.email, item.product_id);
    }
  }
}
```

#### 3. GraphQL Queries
```graphql
# queries/products.graphql

query GetProducts($first: Int!) {
  products(first: $first) {
    edges {
      node {
        id
        title
        description
        handle
        priceRange {
          minVariantPrice {
            amount
            currencyCode
          }
        }
        images(first: 5) {
          edges {
            node {
              url
              altText
            }
          }
        }
        metafields(identifiers: [
          {namespace: "custom", key: "ar_enabled"}
          {namespace: "custom", key: "ar_asset_url"}
          {namespace: "custom", key: "apec_limited"}
          {namespace: "custom", key: "stock_remaining"}
        ]) {
          key
          value
        }
      }
    }
  }
}
```

---

## 👥 팀 구성 및 역할

### 필요 인력 (3명, 3주 풀타임)

#### 1. **Tech Lead / Backend Developer**
**역할**:
- Shopify Custom App 개발
- Webhook Handler 구현
- Neo4j 통합
- Phase 1 API 연동

**필요 스킬**:
- Node.js/Express
- Shopify App Development
- Neo4j/Cypher
- REST/GraphQL API

**시간 배분**:
- Week 1: Custom App 구조 (40h)
- Week 2: AR Unlock Logic (40h)
- Week 3: 테스트 및 배포 (40h)

#### 2. **Frontend Developer**
**역할**:
- Shopify Storefront API 통합
- Checkout Flow UI
- Order Status 페이지
- AR Unlock 알림 UI

**필요 스킬**:
- Next.js 14
- TypeScript
- Shopify Buy SDK
- GraphQL

**시간 배분**:
- Week 1: 제품 페이지 통합 (40h)
- Week 2: Checkout Flow (40h)
- Week 3: UI 완성 및 테스트 (40h)

#### 3. **DevOps / QA Engineer**
**역할**:
- Shopify 계정 설정
- Custom App 배포
- 테스트 자동화
- 모니터링 구성

**필요 스킬**:
- Docker/Kubernetes
- Shopify CLI
- Testing (E2E)
- Monitoring (Prometheus/Grafana)

**시간 배분**:
- Week 1: 환경 설정 (40h)
- Week 2: CI/CD 파이프라인 (40h)
- Week 3: 테스트 및 배포 (40h)

---

## 💰 예산 분석

### 개발 비용
```
인력 비용:
- Tech Lead: $5,000/week × 3 weeks = $15,000
- Frontend Dev: $4,000/week × 3 weeks = $12,000
- DevOps/QA: $3,000/week × 3 weeks = $9,000

소계: $36,000

(할인된 팀 비율 적용 시: $25,000)
```

### Shopify 비용
```
- Shopify Plus: $299/month (연간 $3,588)
- Custom App 호스팅: $50/month (AWS) (연간 $600)

소계: $4,188/year
```

### 총 투자
```
- 초기 개발: $25,000
- 1년차 운영: $4,188

총: $29,188
```

### 절감 효과
```
Stripe 기반 (현재):
- 인프라: $200/month = $2,400/year
- 개발/유지보수: $3,000/month = $36,000/year
- 총: $38,400/year

Shopify 기반 (신규):
- Shopify + 호스팅: $4,188/year
- 유지보수: $500/month = $6,000/year
- 총: $10,188/year

절감: $28,212/year (73% 절감!)
```

### ROI
```
투자: $29,188 (1년차)
절감: $28,212 (매년)

Break-even: 13개월
2년차 ROI: 197%
```

---

## 📊 성공 지표 (KPI)

### 기술 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **개발 완료** | 15일 이내 | 프로젝트 타임라인 |
| **API 응답 시간** | < 200ms | Shopify Storefront API |
| **Checkout 전환율** | > 5% | Shopify Analytics |
| **AR Unlock 성공률** | > 99% | Custom App Logs |
| **시스템 Uptime** | > 99.9% | Shopify + Custom App |
| **페이지 로딩 속도** | < 2초 | Lighthouse Score |

### 비즈니스 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **운영 효율성** | 80% 개선 | 수동 작업 시간 감소 |
| **비용 절감** | $28K/year | 실제 인프라 비용 |
| **주문 처리 시간** | < 5분 | 자동화 |
| **고객 만족도** | > 4.5/5 | NPS Score |
| **재구매율** | > 30% | Shopify CRM |

---

## 🧪 테스트 전략

### 1. Unit Tests
```javascript
// Tests for Custom App
describe('AR Unlock Service', () => {
  test('should unlock AR on paid order', async () => {
    const order = mockPaidOrder();
    await unlockARExperience(order);
    expect(neo4jService.createARAccess).toHaveBeenCalled();
  });

  test('should revoke AR on refund', async () => {
    const refund = mockRefund();
    await revokeARAccess(refund);
    expect(neo4jService.deleteARAccess).toHaveBeenCalled();
  });
});
```

### 2. Integration Tests
- Shopify Storefront API → Frontend
- Shopify Webhook → Custom App
- Custom App → Neo4j
- Custom App → Phase 1 API

### 3. E2E Tests (Playwright)
```typescript
test('complete purchase flow', async ({ page }) => {
  // 1. Browse products
  await page.goto('/products');
  await page.click('[data-testid="product-card"]');

  // 2. Add to cart
  await page.click('[data-testid="add-to-cart"]');

  // 3. Checkout
  await page.click('[data-testid="checkout"]');

  // 4. Complete payment (test mode)
  await page.fill('[data-testid="card-number"]', '4242424242424242');
  await page.click('[data-testid="pay"]');

  // 5. Verify success
  await expect(page.locator('text=Order Successful')).toBeVisible();

  // 6. Check AR unlock
  await page.goto('/my-orders');
  await expect(page.locator('[data-testid="ar-unlocked"]')).toBeVisible();
});
```

---

## 🚨 리스크 관리

### High Risk

#### 1. Shopify API Rate Limiting
**위험**: Storefront API 호출 제한 초과
**완화**:
- GraphQL 쿼리 최적화
- Redis 캐싱
- Batch 요청

#### 2. Webhook 신뢰성
**위험**: Webhook 실패 시 AR 미잠금 해제
**완화**:
- Webhook 재시도 로직
- Dead Letter Queue
- 수동 복구 스크립트

### Medium Risk

#### 3. Neo4j 동기화 지연
**위험**: Shopify와 Neo4j 데이터 불일치
**완화**:
- Eventual consistency 패턴
- 동기화 검증 스크립트
- 모니터링 알림

#### 4. Custom App 호스팅 문제
**위험**: Custom App 다운타임
**완화**:
- AWS/GCP 고가용성 설정
- Auto-scaling
- Health checks

### Low Risk

#### 5. 데이터 마이그레이션 오류
**위험**: 제품 데이터 누락/오류
**완화**:
- 마이그레이션 스크립트 테스트
- Rollback 계획
- 데이터 검증 스크립트

---

## 🎯 성공 기준

### Phase 1 완료 기준 (Week 1)
- ✅ Shopify 계정 활성화
- ✅ 모든 제품 데이터 마이그레이션 완료
- ✅ Frontend에서 Shopify 제품 표시

### Phase 2 완료 기준 (Week 2)
- ✅ Custom App 배포 완료
- ✅ Webhook Handler 작동
- ✅ AR Unlock 로직 테스트 통과

### Phase 3 완료 기준 (Week 3)
- ✅ E2E 테스트 100% 통과
- ✅ Production 배포 완료
- ✅ 모니터링 대시보드 구성
- ✅ Rollback 계획 문서화

### 최종 런칭 기준
- ✅ APEC 일정 맞춤 (10월 말)
- ✅ 모든 KPI 목표 달성
- ✅ 경영진 승인

---

## 📞 커뮤니케이션 계획

### 일일 스탠드업
- **시간**: 매일 오전 10:00
- **소요**: 15분
- **참석**: 전체 팀
- **내용**: 어제 완료, 오늘 계획, 블로커

### 주간 리뷰
- **시간**: 매주 금요일 오후 4:00
- **소요**: 1시간
- **참석**: 팀 + 이해관계자
- **내용**: 주간 성과, 다음 주 계획, 리스크

### 이해관계자 업데이트
- **빈도**: 주 2회 (월, 목)
- **형식**: 이메일 + 슬랙
- **내용**: 진행률, 주요 성과, 이슈

---

## 📚 문서화

### 필수 문서

1. **Technical Design Document** (TDD)
   - 시스템 아키텍처
   - API 스펙
   - 데이터 모델

2. **API Documentation**
   - Shopify Storefront API 사용법
   - Custom App API 엔드포인트
   - Webhook 스펙

3. **Deployment Guide**
   - Custom App 배포 절차
   - Shopify 설정 가이드
   - Rollback 절차

4. **Operations Manual**
   - 모니터링 대시보드 사용법
   - 일반적인 이슈 해결
   - 긴급 대응 절차

---

## ✅ 체크리스트

### 시작 전
- [ ] Shopify Plus 계정 승인
- [ ] 예산 승인
- [ ] 팀 구성 완료
- [ ] 개발 환경 준비

### Week 1
- [ ] Shopify 환경 설정
- [ ] 제품 데이터 마이그레이션
- [ ] Frontend 기본 통합

### Week 2
- [ ] Custom App 개발
- [ ] AR Unlock Logic
- [ ] Webhook Handlers

### Week 3
- [ ] Frontend 완전 통합
- [ ] E2E 테스트
- [ ] Production 배포

### 런칭 후
- [ ] 모니터링 확인
- [ ] 사용자 피드백 수집
- [ ] 성능 최적화

---

## 🚀 다음 단계

1. **경영진 승인** - 이 마스터플랜 검토 및 승인
2. **PRD 작성** - 상세 제품 요구사항 문서
3. **팀 구성** - 개발자 채용/배정
4. **킥오프 미팅** - 프로젝트 시작
5. **Sprint 1 시작** - Week 1 작업 착수

---

**마스터플랜 작성**: NERDX Tech Team
**날짜**: 2025-10-11
**버전**: 1.0
**다음 리뷰**: PRD 작성 후
