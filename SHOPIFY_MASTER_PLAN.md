# Shopify 기반 백엔드 시스템 마스터플랜

**프로젝트**: NERDX APEC MVP - Shopify Headless Commerce
**작성일**: 2025년 10월 11일
**목표**: 4주 내 MVP 출시, 6개월 내 확장

---

## 📋 목차

1. [전체 아키텍처](#전체-아키텍처)
2. [Phase 1: MVP 출시 (2-4주)](#phase-1-mvp-출시-2-4주)
3. [Phase 2: 기능 확장 (4-12주)](#phase-2-기능-확장-4-12주)
4. [Phase 3: 최적화 (12-24주)](#phase-3-최적화-12-24주)
5. [Phase 4: 스케일업 (24주+)](#phase-4-스케일업-24주)
6. [타임라인 & 마일스톤](#타임라인--마일스톤)
7. [리소스 계획](#리소스-계획)

---

## 🏗️ 전체 아키텍처

### 시스템 다이어그램

```
┌──────────────────────────────────────────────────────────┐
│                      사용자                                │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│                Frontend (Next.js 14)                      │
│  - Vercel 호스팅                                          │
│  - Static Generation + SSR                               │
│  - 상품 페이지, 장바구니, 체크아웃                         │
└──┬───────────────┬───────────────┬────────────────────────┘
   │               │               │
   │               │               └──────────┐
   │               │                          │
┌──▼──────────┐  ┌─▼──────────────┐  ┌──────▼─────────────┐
│   Shopify   │  │ Custom Backend │  │  Third-party APIs  │
│             │  │   (Optional)   │  │                    │
├─────────────┤  ├────────────────┤  ├────────────────────┤
│ Storefront  │  │ Maeju AI Chat  │  │ OpenAI API         │
│ API         │  │ CAMEO Gen      │  │ Vercel AI SDK      │
│             │  │ Analytics      │  │ Stripe (backup)    │
├─────────────┤  ├────────────────┤  └────────────────────┘
│ Admin API   │  │ Express.js     │
│             │  │ PostgreSQL     │
├─────────────┤  │ Redis Cache    │
│ Webhooks    │  │ Bull Queue     │
│             │  │ WebSocket      │
└─────────────┘  └────────────────┘
```

### 데이터 플로우

```
1. 제품 조회
   사용자 → Frontend → Shopify Storefront API → 제품 데이터

2. 회원가입/로그인
   사용자 → Frontend → Shopify Customer API → 계정 생성

3. 주문
   사용자 → Frontend → Shopify Checkout → Shopify Orders → Webhook → 커스텀 백엔드

4. AI 채팅 (Maeju)
   사용자 → Frontend → 커스텀 백엔드 → OpenAI → Frontend

5. CAMEO 생성
   사용자 → Frontend → 커스텀 백엔드 → 비디오 생성 → S3/CDN → Frontend
```

---

## 🚀 Phase 1: MVP 출시 (2-4주)

### 목표
✅ Shopify 100% 활용으로 **최소 기능 제품** 출시
✅ 상품 판매 & 주문 처리 가능
✅ 실제 고객 대상 테스트 가능

### 기간: **2-4주**

---

### Week 1: Shopify 설정 & 통합 기초

#### Day 1-2: Shopify 스토어 설정
```bash
✅ 작업 항목:
├─ Shopify 계정 생성 (Basic Plan $29/월)
├─ 스토어 기본 정보 설정
│  ├─ 스토어 이름: NERDX APEC
│  ├─ 도메인 연결: nerdx-apec.com
│  └─ 통화 & 언어: KRW, 한국어/영어
├─ Shopify Payments 설정
│  ├─ 사업자 정보 입력
│  └─ 계좌 연결
└─ 배송 설정
   ├─ 국내 배송 요율
   └─ 배송 지역 설정

🛠️ 도구:
- Shopify Admin Dashboard
- 은행 계좌 정보

📊 완료 기준:
- Shopify Admin에 로그인 가능
- 테스트 주문 생성 가능
- 결제 게이트웨이 활성화
```

#### Day 3-4: 제품 데이터 마이그레이션
```bash
✅ 작업 항목:
├─ 현재 Shopify 제품 (3개) 확인
├─ 제품 정보 완성
│  ├─ 상세 설명 (한/영)
│  ├─ 고화질 이미지 업로드
│  ├─ 가격 & 비교가격 설정
│  └─ SEO 최적화 (제목, 설명, URL)
├─ Metafields 설정
│  ├─ ar_enabled (AR 가능 여부)
│  ├─ ar_asset_url (AR 모델 URL)
│  ├─ apec_limited (APEC 한정판)
│  ├─ stock_remaining (재고)
│  └─ video_url (제품 비디오)
└─ 컬렉션 생성
   ├─ "전통주" 컬렉션
   ├─ "APEC 한정판" 컬렉션
   └─ "AR 체험 가능" 컬렉션

🛠️ 도구:
- Shopify Admin
- Bulk Editor
- scripts/setup-shopify-products.js (기존)

📊 완료 기준:
- 3개 제품 완전히 설정됨
- Storefront API로 조회 가능
- Metafields 정상 반환
```

#### Day 5-7: 프론트엔드 Shopify 통합
```bash
✅ 작업 항목:
├─ 환경 변수 최종 확인
│  ├─ NEXT_PUBLIC_SHOPIFY_DOMAIN
│  ├─ NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN
│  └─ SHOPIFY_ADMIN_API_TOKEN (서버용)
├─ Shopify Client 개선
│  ├─ Error handling 강화
│  ├─ Retry logic 추가
│  ├─ TypeScript 타입 완성
│  └─ 캐싱 전략 구현
├─ 제품 페이지 최종 점검
│  ├─ 제품 목록 표시 ✅ (완료)
│  ├─ 제품 상세 페이지 구현
│  ├─ 필터링 & 정렬 검증
│  └─ 이미지 최적화
└─ 테스트
   ├─ Unit tests (ShopifyService)
   └─ Integration tests

🛠️ 도구:
- frontend/lib/shopify/client.ts
- Jest + Testing Library

📊 완료 기준:
- 모든 제품 페이지 정상 작동
- 테스트 커버리지 80%+
- Lighthouse 점수 90+
```

---

### Week 2: 회원 시스템 구현

#### Day 8-10: Shopify Customer API 통합
```typescript
// 구현 파일: lib/shopify/customer.ts

interface CustomerInput {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  phone?: string;
  acceptsMarketing?: boolean;
}

class ShopifyCustomerService {
  /**
   * 회원가입 (Customer 생성)
   */
  async createCustomer(input: CustomerInput): Promise<Customer> {
    const mutation = `
      mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
          customer {
            id
            email
            firstName
            lastName
          }
          customerUserErrors {
            field
            message
          }
        }
      }
    `;

    // Shopify Admin API 호출
    const response = await adminFetch(mutation, { input });

    if (response.customerUserErrors.length > 0) {
      throw new Error(response.customerUserErrors[0].message);
    }

    return response.customer;
  }

  /**
   * 로그인 (Customer Access Token 생성)
   */
  async customerAccessTokenCreate(
    email: string,
    password: string
  ): Promise<AccessToken> {
    const mutation = `
      mutation customerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) {
        customerAccessTokenCreate(input: $input) {
          customerAccessToken {
            accessToken
            expiresAt
          }
          customerUserErrors {
            field
            message
          }
        }
      }
    `;

    const response = await storefrontFetch(mutation, {
      input: { email, password }
    });

    if (response.customerUserErrors.length > 0) {
      throw new Error('이메일 또는 비밀번호가 올바르지 않습니다');
    }

    return response.customerAccessToken;
  }

  /**
   * 로그아웃 (Access Token 삭제)
   */
  async customerAccessTokenDelete(accessToken: string): Promise<void> {
    const mutation = `
      mutation customerAccessTokenDelete($customerAccessToken: String!) {
        customerAccessTokenDelete(customerAccessToken: $customerAccessToken) {
          deletedAccessToken
          deletedCustomerAccessTokenId
          userErrors {
            field
            message
          }
        }
      }
    `;

    await storefrontFetch(mutation, { customerAccessToken: accessToken });
  }

  /**
   * 고객 정보 조회
   */
  async getCustomer(accessToken: string): Promise<Customer> {
    const query = `
      query getCustomer($customerAccessToken: String!) {
        customer(customerAccessToken: $customerAccessToken) {
          id
          email
          firstName
          lastName
          phone
          defaultAddress {
            address1
            city
            country
            zip
          }
          orders(first: 10) {
            edges {
              node {
                id
                orderNumber
                totalPrice {
                  amount
                  currencyCode
                }
                createdAt
              }
            }
          }
        }
      }
    `;

    const response = await storefrontFetch(query, { customerAccessToken: accessToken });
    return response.customer;
  }

  /**
   * 비밀번호 재설정 요청
   */
  async customerRecover(email: string): Promise<void> {
    const mutation = `
      mutation customerRecover($email: String!) {
        customerRecover(email: $email) {
          customerUserErrors {
            field
            message
          }
        }
      }
    `;

    await storefrontFetch(mutation, { email });
  }
}
```

```bash
✅ 작업 항목:
├─ customer.ts 파일 생성
├─ CustomerService 클래스 구현
│  ├─ 회원가입
│  ├─ 로그인
│  ├─ 로그아웃
│  ├─ 정보 조회
│  ├─ 정보 수정
│  └─ 비밀번호 재설정
├─ Zustand Store 업데이트
│  ├─ accessToken 저장
│  ├─ customer 정보 저장
│  └─ 자동 로그인 (토큰 검증)
└─ 테스트 작성

📊 완료 기준:
- 모든 Customer API 메서드 작동
- Access Token 자동 갱신
- 에러 핸들링 완료
```

#### Day 11-14: 로그인 UI 구현
```bash
✅ 작업 항목:
├─ 로그인/회원가입 페이지 (app/auth/page.tsx)
│  ├─ 탭 UI (로그인/회원가입)
│  ├─ 폼 Validation (react-hook-form + zod)
│  ├─ 에러 메시지 표시
│  └─ Loading states
├─ 마이페이지 (app/account/page.tsx)
│  ├─ 사용자 정보 표시
│  ├─ 주문 내역
│  ├─ 주소 관리
│  └─ 정보 수정
├─ Navigation 업데이트
│  ├─ 로그인 상태 표시
│  ├─ User 아이콘 → 드롭다운 메뉴
│  └─ 로그아웃 버튼
└─ Protected Routes
   ├─ Middleware 설정
   └─ 로그인 리다이렉트

🛠️ 도구:
- react-hook-form
- zod (validation)
- Next.js Middleware

📊 완료 기준:
- 회원가입 → 로그인 플로우 완료
- 모든 폼 validation 작동
- Protected routes 정상 동작
```

---

### Week 3: 장바구니 & 체크아웃

#### Day 15-17: Shopify Cart API 통합
```typescript
// 구현 파일: lib/shopify/cart.ts

class ShopifyCartService {
  /**
   * 장바구니 생성
   */
  async cartCreate(items: CartLineInput[]): Promise<Cart> {
    const mutation = `
      mutation cartCreate($input: CartInput!) {
        cartCreate(input: $input) {
          cart {
            id
            checkoutUrl
            lines(first: 10) {
              edges {
                node {
                  id
                  quantity
                  merchandise {
                    ... on ProductVariant {
                      id
                      title
                      price {
                        amount
                        currencyCode
                      }
                      product {
                        id
                        title
                        featuredImage {
                          url
                        }
                      }
                    }
                  }
                }
              }
            }
            cost {
              totalAmount {
                amount
                currencyCode
              }
              subtotalAmount {
                amount
                currencyCode
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }
    `;

    const response = await storefrontFetch(mutation, {
      input: { lines: items }
    });

    return response.cart;
  }

  /**
   * 장바구니 조회
   */
  async getCart(cartId: string): Promise<Cart> {
    const query = `
      query getCart($cartId: ID!) {
        cart(id: $cartId) {
          id
          checkoutUrl
          lines(first: 10) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    price {
                      amount
                      currencyCode
                    }
                    product {
                      id
                      title
                      featuredImage {
                        url
                      }
                    }
                  }
                }
              }
            }
          }
          cost {
            totalAmount {
              amount
              currencyCode
            }
            subtotalAmount {
              amount
              currencyCode
            }
          }
        }
      }
    `;

    const response = await storefrontFetch(query, { cartId });
    return response.cart;
  }

  /**
   * 장바구니에 아이템 추가
   */
  async cartLinesAdd(
    cartId: string,
    lines: CartLineInput[]
  ): Promise<Cart> {
    const mutation = `
      mutation cartLinesAdd($cartId: ID!, $lines: [CartLineInput!]!) {
        cartLinesAdd(cartId: $cartId, lines: $lines) {
          cart {
            id
            lines(first: 10) {
              edges {
                node {
                  id
                  quantity
                  merchandise {
                    ... on ProductVariant {
                      id
                      title
                      price {
                        amount
                      }
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }
    `;

    const response = await storefrontFetch(mutation, { cartId, lines });
    return response.cart;
  }

  /**
   * 장바구니 아이템 수량 변경
   */
  async cartLinesUpdate(
    cartId: string,
    lines: CartLineUpdateInput[]
  ): Promise<Cart> {
    const mutation = `
      mutation cartLinesUpdate($cartId: ID!, $lines: [CartLineUpdateInput!]!) {
        cartLinesUpdate(cartId: $cartId, lines: $lines) {
          cart {
            id
            lines(first: 10) {
              edges {
                node {
                  id
                  quantity
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }
    `;

    const response = await storefrontFetch(mutation, { cartId, lines });
    return response.cart;
  }

  /**
   * 장바구니 아이템 제거
   */
  async cartLinesRemove(
    cartId: string,
    lineIds: string[]
  ): Promise<Cart> {
    const mutation = `
      mutation cartLinesRemove($cartId: ID!, $lineIds: [ID!]!) {
        cartLinesRemove(cartId: $cartId, lineIds: $lineIds) {
          cart {
            id
            lines(first: 10) {
              edges {
                node {
                  id
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }
    `;

    const response = await storefrontFetch(mutation, { cartId, lineIds });
    return response.cart;
  }
}
```

```bash
✅ 작업 항목:
├─ cart.ts 파일 생성
├─ CartService 클래스 구현
├─ Zustand Cart Store 업데이트
│  ├─ Shopify Cart ID 저장
│  ├─ 서버 동기화 로직
│  └─ Optimistic updates
└─ 테스트 작성

📊 완료 기준:
- 장바구니 CRUD 작동
- 로컬 상태 + 서버 동기화
- 에러 핸들링 완료
```

#### Day 18-21: 체크아웃 구현
```bash
✅ 작업 항목:
├─ 장바구니 페이지 (app/cart/page.tsx)
│  ├─ 장바구니 아이템 목록
│  ├─ 수량 변경 (+/-)
│  ├─ 아이템 제거
│  ├─ 가격 요약 (소계, 배송비, 합계)
│  └─ "결제하기" 버튼
├─ Shopify Checkout 통합
│  ├─ cart.checkoutUrl로 리다이렉트
│  ├─ 또는 Shopify Buy SDK 사용
│  └─ 결제 완료 후 리다이렉트 처리
├─ 주문 완료 페이지
│  ├─ /order/[id] 페이지
│  ├─ 주문 정보 표시
│  ├─ 주문 번호, 총액, 배송 정보
│  └─ 이메일 확인 안내
└─ 테스트
   ├─ 테스트 결제 진행
   └─ 주문 완료 플로우 검증

📊 완료 기준:
- 전체 결제 플로우 작동
- 테스트 주문 성공
- 주문 확인 이메일 수신
```

---

### Week 4: 테스트 & 배포

#### Day 22-24: 통합 테스트
```bash
✅ 작업 항목:
├─ E2E 테스트 (Playwright)
│  ├─ 회원가입 → 로그인
│  ├─ 제품 검색 → 상세 페이지
│  ├─ 장바구니 추가 → 결제
│  └─ 주문 완료 확인
├─ 성능 테스트
│  ├─ Lighthouse (모든 페이지)
│  ├─ Web Vitals 측정
│  └─ Load Testing (k6)
├─ 보안 점검
│  ├─ API 키 보안
│  ├─ XSS/CSRF 점검
│  └─ HTTPS 강제
└─ 접근성 테스트
   ├─ WCAG AA 준수
   └─ 스크린 리더 테스트

📊 완료 기준:
- E2E 테스트 100% 통과
- Lighthouse 점수 90+
- 보안 취약점 0건
```

#### Day 25-28: 배포 & 모니터링
```bash
✅ 작업 항목:
├─ 프로덕션 배포
│  ├─ Vercel 프로덕션 배포
│  ├─ 환경 변수 최종 확인
│  ├─ 도메인 연결
│  └─ SSL 인증서 확인
├─ Shopify 프로덕션 설정
│  ├─ Storefront 비밀번호 제거
│  ├─ 결제 게이트웨이 활성화
│  ├─ 배송 정책 확인
│  └─ 법적 페이지 (약관, 개인정보)
├─ 모니터링 설정
│  ├─ Vercel Analytics
│  ├─ Shopify Analytics
│  ├─ Google Analytics 4
│  └─ Sentry (에러 추적)
└─ 문서화
   ├─ 운영 매뉴얼
   ├─ 트러블슈팅 가이드
   └─ API 문서

📊 완료 기준:
- 프로덕션 배포 완료
- 실제 주문 테스트 성공
- 모니터링 대시보드 작동
- 문서 작성 완료
```

---

## Phase 1 완료 체크리스트

### 기능 완성도
```
✅ 제품 목록 & 상세 페이지
✅ 회원가입 & 로그인
✅ 마이페이지
✅ 장바구니
✅ 체크아웃 & 결제
✅ 주문 완료
✅ 주문 내역 조회
```

### 기술 완성도
```
✅ Shopify Storefront API 통합
✅ Shopify Customer API 통합
✅ Shopify Cart API 통합
✅ TypeScript 100% 적용
✅ 테스트 커버리지 80%+
✅ Lighthouse 점수 90+
✅ 보안 점검 완료
```

### 배포 완성도
```
✅ Vercel 프로덕션 배포
✅ 도메인 연결
✅ SSL 인증서
✅ 모니터링 설정
✅ 문서 작성
```

---

## 🔄 Phase 2: 기능 확장 (4-12주)

### 목표
✅ AI 기능 추가 (Maeju 채팅, CAMEO 생성)
✅ 커스텀 백엔드 구축
✅ 고급 기능 추가

### 기간: **2-3개월**

---

### Month 2: 커스텀 백엔드 구축

#### Week 5-6: 백엔드 인프라
```bash
✅ 작업 항목:
├─ 백엔드 프로젝트 설정
│  ├─ Express.js + TypeScript
│  ├─ PostgreSQL (Supabase)
│  ├─ Redis (Upstash)
│  └─ Docker Compose
├─ Shopify Webhooks 구독
│  ├─ orders/create
│  ├─ orders/updated
│  ├─ orders/paid
│  ├─ customers/create
│  └─ customers/updated
├─ Webhook 핸들러 구현
│  ├─ HMAC 서명 검증
│  ├─ Idempotency (Redis)
│  ├─ Queue 처리 (Bull)
│  └─ 데이터베이스 동기화
└─ API 엔드포인트
   ├─ GET /api/sync/products
   ├─ GET /api/sync/orders/:customerId
   └─ POST /api/webhooks/shopify

📊 완료 기준:
- Webhook 정상 수신
- DB 동기화 작동
- API 문서 완성
```

#### Week 7-8: Maeju AI 채팅
```bash
✅ 작업 항목:
├─ OpenAI API 통합
│  ├─ Chat Completions API
│  ├─ Function Calling (제품 검색)
│  └─ Streaming responses
├─ 채팅 세션 관리
│  ├─ Session 테이블 (PostgreSQL)
│  ├─ Message 테이블
│  └─ Context 관리 (Redis)
├─ 제품 검색 함수
│  ├─ Shopify Storefront API 쿼리
│  ├─ 필터링 로직
│  └─ 추천 알고리즘 (기본)
├─ Frontend 통합
│  ├─ WebSocket 연결 (선택)
│  ├─ SSE (Server-Sent Events)
│  └─ 채팅 UI 개선
└─ 테스트
   ├─ E2E 채팅 플로우
   └─ 제품 추천 정확도

📊 완료 기준:
- AI 채팅 정상 작동
- 제품 추천 가능
- 대화 이력 저장
```

---

### Month 3: CAMEO & 최적화

#### Week 9-10: CAMEO 비디오 생성
```bash
✅ 작업 항목:
├─ 비디오 생성 로직
│  ├─ 텍스트 → 스크립트 생성 (OpenAI)
│  ├─ 스크립트 → 비디오 (D-ID / HeyGen)
│  ├─ 제품 정보 삽입
│  └─ 비디오 렌더링
├─ 비디오 저장
│  ├─ AWS S3 / Cloudflare R2
│  ├─ CDN 설정
│  └─ 비디오 메타데이터 DB 저장
├─ 비동기 처리
│  ├─ Bull Queue
│  ├─ 진행 상태 추적
│  └─ 완료 알림 (이메일/푸시)
├─ Frontend 통합
│  ├─ CAMEO 요청 폼
│  ├─ 진행 상태 표시
│  ├─ 비디오 플레이어
│  └─ 다운로드/공유 기능
└─ 테스트
   ├─ CAMEO 생성 전체 플로우
   └─ 비디오 품질 검증

📊 완료 기준:
- CAMEO 생성 성공
- 비디오 품질 만족
- 평균 생성 시간 < 5분
```

#### Week 11-12: 성능 최적화
```bash
✅ 작업 항목:
├─ 캐싱 전략
│  ├─ Redis 캐시 레이어
│  ├─ Shopify 응답 캐싱
│  ├─ CDN 캐싱 (Vercel/Cloudflare)
│  └─ 브라우저 캐싱
├─ 데이터베이스 최적화
│  ├─ 인덱스 추가
│  ├─ 쿼리 최적화
│  └─ Connection pooling
├─ API 최적화
│  ├─ GraphQL 쿼리 최적화
│  ├─ Batch requests
│  ├─ Rate limit 관리
│  └─ Error retry 로직
└─ 모니터링
   ├─ APM (Application Performance Monitoring)
   ├─ Database monitoring
   └─ Cache hit rate 추적

📊 완료 기준:
- API 응답 시간 < 200ms
- 페이지 로드 < 2초
- Cache hit rate > 80%
```

---

## ⚡ Phase 3: 최적화 (12-24주)

### 목표
✅ 고급 기능 추가
✅ 사용자 경험 개선
✅ 비즈니스 메트릭 개선

### 주요 작업

#### 1. 개인화 엔진
```bash
✅ 추천 시스템
├─ 사용자 행동 추적
├─ 협업 필터링
├─ 콘텐츠 기반 필터링
└─ ML 모델 (TensorFlow.js)

✅ 동적 가격
├─ 세그먼트별 가격
├─ A/B 테스팅
└─ 프로모션 자동화
```

#### 2. 분석 & 인사이트
```bash
✅ 고급 분석
├─ 전환 깔때기 분석
├─ 코호트 분석
├─ RFM 분석
└─ 예측 분석

✅ 대시보드
├─ 실시간 메트릭
├─ 판매 리포트
├─ 고객 인사이트
└─ 제품 성과
```

#### 3. 마케팅 자동화
```bash
✅ 이메일 마케팅
├─ 환영 시리즈
├─ 장바구니 포기 복구
├─ 재구매 유도
└─ 윈백 캠페인

✅ SMS/푸시 알림
├─ 주문 상태 알림
├─ 배송 추적
├─ 프로모션 알림
└─ 재입고 알림
```

---

## 🚀 Phase 4: 스케일업 (24주+)

### 목표
✅ Shopify Plus로 업그레이드
✅ 글로벌 확장
✅ 엔터프라이즈 기능

### Shopify Plus 기능 활용

#### 1. Launchpad
```bash
✅ 플래시 세일 자동화
├─ 스케줄링
├─ 테마 전환
├─ 가격 변경
└─ 재고 관리
```

#### 2. Flow
```bash
✅ 워크플로우 자동화
├─ VIP 고객 태깅
├─ 재고 부족 알림
├─ 사기 주문 차단
└─ 환불 자동화
```

#### 3. Scripts
```bash
✅ 체크아웃 커스터마이징
├─ 동적 할인
├─ 배송 로직
├─ 결제 게이트 커스텀
└─ 번들 할인
```

#### 4. Multipass
```bash
✅ SSO (Single Sign-On)
├─ 커스텀 로그인
├─ 외부 인증 통합
├─ Seamless 전환
└─ 보안 강화
```

---

## 📅 타임라인 & 마일스톤

### 전체 타임라인

```
Month 1 (Week 1-4):   MVP 출시
Month 2 (Week 5-8):   커스텀 백엔드 & AI
Month 3 (Week 9-12):  CAMEO & 최적화
Month 4-6:            고급 기능 & 개인화
Month 7-12:           확장 & 최적화
Month 12+:            Shopify Plus & 글로벌
```

### 주요 마일스톤

| 마일스톤 | 기간 | 목표 | KPI |
|---------|------|------|-----|
| **M1: MVP Launch** | Week 4 | 판매 시작 | 첫 주문 |
| **M2: 100 Orders** | Week 8 | 제품-시장 적합성 | 100 주문 |
| **M3: AI Features** | Week 12 | AI 기능 완성 | 채팅 사용률 30% |
| **M4: 1,000 Orders** | Week 24 | 스케일업 준비 | 월 100만원 매출 |
| **M5: Shopify Plus** | Week 36 | 엔터프라이즈 | 월 1억원 매출 |

---

## 👥 리소스 계획

### 팀 구성

#### MVP (1-3개월)
```
✅ 풀스택 개발자 1명 (또는 AI 지원)
✅ 디자이너 0.5명 (파트타임)
✅ PM 0.5명 (파트타임)
```

#### 성장 (3-12개월)
```
✅ 프론트엔드 개발자 1명
✅ 백엔드 개발자 1명
✅ AI/ML 엔지니어 0.5명
✅ 디자이너 1명
✅ PM 1명
✅ QA 0.5명
```

#### 확장 (12개월+)
```
✅ 개발팀 5-10명
✅ 디자인팀 2-3명
✅ 제품팀 2-3명
✅ DevOps 1명
✅ 데이터 사이언티스트 1명
```

### 예산 계획

#### MVP (월간)
```
개발:           $0 (자체 개발) 또는 $5,000 (외주)
Shopify:        $29
Vercel:         $20
도메인:         $1
총계:           ~$50/월
```

#### 성장 (월간)
```
팀:             $15,000 (3-4명)
Shopify:        $79
인프라:         $200 (Vercel, AWS, Redis 등)
마케팅:         $5,000
총계:           ~$20,000/월
```

#### 확장 (월간)
```
팀:             $50,000+ (10-15명)
Shopify Plus:   $2,000
인프라:         $1,000
마케팅:         $50,000
총계:           ~$100,000+/월
```

---

## 🎯 성공 지표 (KPIs)

### Phase 1 (MVP)
```
✅ 출시: 4주 이내
✅ 첫 주문: 출시 후 1주
✅ 10 주문: 출시 후 1개월
✅ 전환율: > 1%
✅ 페이지 속도: < 2초
```

### Phase 2 (확장)
```
✅ 100 주문: 3개월
✅ 재구매율: > 20%
✅ 채팅 사용률: > 30%
✅ CAMEO 생성: 10개/주
✅ 전환율: > 2%
```

### Phase 3 (최적화)
```
✅ 1,000 주문: 6개월
✅ 월 매출: 1,000만원
✅ AOV (평균 주문 금액): 50,000원
✅ 재구매율: > 30%
✅ NPS: > 50
```

### Phase 4 (스케일업)
```
✅ 10,000 주문: 12개월
✅ 월 매출: 1억원
✅ AOV: 80,000원
✅ LTV/CAC: > 3
✅ 글로벌 진출: 2-3개국
```

---

## 📊 리스크 관리

### 기술 리스크

| 리스크 | 확률 | 영향 | 완화 전략 |
|-------|------|------|----------|
| Shopify API 장애 | 낮음 | 높음 | 캐싱, Fallback UI |
| 결제 실패 | 중간 | 높음 | 여러 결제 게이트웨이 |
| 성능 저하 | 중간 | 중간 | 모니터링, 자동 스케일링 |
| 데이터 손실 | 낮음 | 높음 | 자동 백업, Replication |

### 비즈니스 리스크

| 리스크 | 확률 | 영향 | 완화 전략 |
|-------|------|------|----------|
| 낮은 전환율 | 중간 | 높음 | A/B 테스팅, UX 개선 |
| 높은 CAC | 중간 | 중간 | 오가닉 채널, SEO |
| 재고 부족 | 낮음 | 중간 | 재고 알림, 사전 주문 |
| 경쟁 심화 | 높음 | 중간 | 차별화, 브랜딩 |

---

## 🚦 Go/No-Go 체크리스트

### Phase 1 → Phase 2
```
✅ 최소 50 주문 달성
✅ 전환율 > 1%
✅ 고객 만족도 > 4.0/5.0
✅ 기술 부채 < 20%
✅ 예산 확보
```

### Phase 2 → Phase 3
```
✅ 최소 500 주문 달성
✅ 재구매율 > 20%
✅ AI 기능 사용률 > 30%
✅ 월 매출 > 500만원
✅ 팀 확장 가능
```

### Phase 3 → Phase 4
```
✅ 최소 5,000 주문 달성
✅ 월 매출 > 5,000만원
✅ Shopify Plus ROI 검증
✅ 글로벌 시장 조사 완료
✅ 확장 자금 확보
```

---

## 🎓 학습 & 개선

### 정기 리뷰
```
주간: 진행 상황, 블로커
월간: KPI, 예산, 로드맵
분기: 전략, 방향성, 피벗
연간: 비전, 장기 목표
```

### 실험 & 테스트
```
A/B 테스팅: 주 2-3개 실험
사용자 인터뷰: 월 10명
분석: 일일 데이터 리뷰
회고: 스프린트마다
```

---

## 📞 지원 & 리소스

### Shopify 지원
```
공식 문서: https://shopify.dev
커뮤니티: https://community.shopify.com
파트너: Shopify Partners Program
지원팀: 24/7 이메일/채팅
```

### 개발 리소스
```
GitHub: shopify/* 레포지토리
템플릿: Shopify Theme Kit
예제: hydrogen (React framework)
도구: Shopify CLI
```

---

**마스터플랜 버전**: 1.0
**마지막 업데이트**: 2025년 10월 11일
**다음 문서**: [PRD →](SHOPIFY_PRD.md)
