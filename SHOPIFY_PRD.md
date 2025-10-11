# Product Requirements Document (PRD)
## NERDX APEC MVP - Shopify Headless Commerce

**버전**: 1.0
**작성일**: 2025년 10월 11일
**작성자**: Product Team
**상태**: Draft → Review → Approved

---

## 📋 문서 정보

### 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|-----|------|--------|----------|
| 1.0 | 2025-10-11 | Product Team | 초안 작성 |
| 1.1 | 2025-10-11 | Product Team | 뉴스레터 & 커뮤니티 기능 추가 (섹션 4) |

### 승인

| 역할 | 이름 | 서명 | 날짜 |
|-----|------|------|------|
| Product Owner | | | |
| Tech Lead | | | |
| Design Lead | | | |

---

## 🎯 제품 개요

### 비전
> "전통주를 사랑하는 젊은 세대를 위한 AI 기반 비디오 커머스 플랫폼"

### 미션
NERDX APEC은 전통주 구매를 단순한 거래를 넘어 **개인화되고 즐거운 경험**으로 만들어, 전통주 문화를 현대적으로 재해석하고 확산시킵니다.

### 목표 (6개월)
```
📊 비즈니스 목표:
├─ 월 매출: 1,000만원
├─ 주문 수: 1,000건
├─ 재구매율: 30%
└─ NPS: 50+

🎨 사용자 경험 목표:
├─ 전환율: 3%
├─ 장바구니 포기율: < 50%
├─ 페이지 로드: < 2초
└─ 모바일 트래픽: 70%

💡 혁신 목표:
├─ AI 채팅 사용률: 40%
├─ CAMEO 생성: 100개/월
├─ AR 체험: 500회/월
└─ 소셜 공유: 200회/월
```

---

## 👥 타겟 사용자

### Primary Persona: "지현" (25-35세, 여성, 서울 거주)

```yaml
인구통계:
  나이: 28세
  직업: 마케터
  소득: 4,000만원/년
  거주지: 서울 강남구
  학력: 대졸

행동 패턴:
  쇼핑 빈도: 주 2-3회 (온라인)
  평균 구매액: 50,000원
  선호 채널: Instagram, YouTube, 네이버
  쇼핑 시간: 저녁 9-11시, 주말 오후

니즈 & Pain Points:
  니즈:
    - "특별한 선물을 찾고 있어요"
    - "전통주에 관심이 생겼는데 어디서부터 시작해야 할지 모르겠어요"
    - "믿을 수 있는 곳에서 사고 싶어요"

  Pain Points:
    - 전통주 종류가 너무 많아 선택이 어려움
    - 맛을 미리 알 수 없음
    - 오프라인 매장 방문이 번거로움
    - 선물용 포장이 아쉬움

목표:
  - 친구 생일 선물로 특별한 전통주 찾기
  - 내 취향에 맞는 전통주 발견하기
  - 전통주에 대해 배우고 싶음

Quote:
  "전통주도 세련되게 즐길 수 있다는 걸 보여주고 싶어요"
```

### Secondary Persona: "민수" (30-40세, 남성, 수도권 거주)

```yaml
인구통계:
  나이: 35세
  직업: IT 회사 팀장
  소득: 8,000만원/년
  거주지: 경기도 분당
  학력: 대졸

행동 패턴:
  쇼핑 빈도: 월 2-3회
  평균 구매액: 100,000원
  선호 채널: YouTube, 쿠팡, 네이버
  쇼핑 시간: 주말, 출퇴근 시간

니즈 & Pain Points:
  니즈:
    - "프리미엄 전통주로 손님 접대하고 싶어요"
    - "희소성 있는 제품을 찾고 있어요"
    - "AR로 미리 보고 싶어요"

  Pain Points:
    - 프리미엄 전통주 정보 부족
    - 진품 여부 확인 어려움
    - 빠른 배송 필요
    - 재고 있는지 확인 번거로움

목표:
  - 회사 행사용 프리미엄 전통주 대량 구매
  - 컬렉션 만들기
  - 지인들에게 추천하기

Quote:
  "품질 좋은 전통주를 편하게 살 수 있으면 좋겠어요"
```

---

## 🌟 핵심 기능 (MVP)

### 1. 회원 시스템

#### 1.1 회원가입 (Sign Up)

**사용자 스토리**:
> "지현은 NERDX APEC에서 처음으로 전통주를 구매하려고 합니다. 간단하게 이메일로 회원가입하고 싶어합니다."

**기능 요구사항**:
```
FR-1.1.1: 이메일 회원가입
  - 이메일, 비밀번호, 이름, 전화번호 입력
  - 이메일 중복 확인
  - 비밀번호 강도 검증 (8자 이상, 영문+숫자)
  - 개인정보 처리방침, 이용약관 동의
  - 마케팅 수신 동의 (선택)

FR-1.1.2: 소셜 로그인 (Phase 2)
  - 카카오, 네이버, Google 로그인
  - OAuth 2.0 인증
  - 이메일 자동 연동

FR-1.1.3: 환영 이메일
  - 회원가입 완료 즉시 발송
  - 첫 구매 10% 할인 쿠폰 포함
  - 추천 제품 3개 포함
```

**수용 기준 (Acceptance Criteria)**:
```gherkin
Given 사용자가 회원가입 페이지에 있을 때
When 유효한 이메일, 비밀번호, 이름을 입력하고 "가입하기" 클릭
Then 회원가입 성공하고 환영 이메일이 발송됨
And 자동으로 로그인되어 마이페이지로 이동

Given 사용자가 이미 등록된 이메일로 가입 시도할 때
When "가입하기" 버튼 클릭
Then "이미 사용 중인 이메일입니다" 에러 메시지 표시

Given 사용자가 약한 비밀번호를 입력할 때
When 비밀번호 입력 필드에서 포커스 아웃
Then "비밀번호는 8자 이상, 영문과 숫자를 포함해야 합니다" 경고 표시
```

**기술 스펙**:
```typescript
// API: lib/shopify/customer.ts

interface SignUpInput {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
  acceptsMarketing?: boolean;
}

async function signUp(input: SignUpInput): Promise<Customer> {
  // Shopify Customer API 호출
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

  const response = await shopifyAdminFetch(mutation, { input });

  if (response.customerUserErrors.length > 0) {
    throw new ValidationError(response.customerUserErrors);
  }

  // 환영 이메일 발송 (Shopify 자동 or 커스텀)
  await sendWelcomeEmail(response.customer.email);

  return response.customer;
}
```

**UI 목업**:
```
┌──────────────────────────────────────────┐
│  NERDX APEC 회원가입                      │
├──────────────────────────────────────────┤
│                                          │
│  [ 카카오로 3초 만에 시작하기 ]            │
│  [ 네이버로 3초 만에 시작하기 ]            │
│                                          │
│  ────────── 또는 ──────────              │
│                                          │
│  이메일 *                                │
│  ┌────────────────────────────┐          │
│  │ example@email.com          │          │
│  └────────────────────────────┘          │
│                                          │
│  비밀번호 *                              │
│  ┌────────────────────────────┐          │
│  │ ••••••••                   │ 👁       │
│  └────────────────────────────┘          │
│  ✓ 8자 이상  ✓ 영문  ✓ 숫자              │
│                                          │
│  이름 *                                  │
│  ┌────────────────────────────┐          │
│  │ 홍길동                     │          │
│  └────────────────────────────┘          │
│                                          │
│  전화번호 (선택)                          │
│  ┌────────────────────────────┐          │
│  │ 010-1234-5678              │          │
│  └────────────────────────────┘          │
│                                          │
│  ☑ [필수] 개인정보 처리방침 동의          │
│  ☑ [필수] 이용약관 동의                  │
│  ☐ [선택] 마케팅 정보 수신 동의           │
│                                          │
│  [      가입하기      ]                  │
│                                          │
│  이미 계정이 있으신가요? 로그인           │
└──────────────────────────────────────────┘
```

**측정 지표 (Metrics)**:
```
- 회원가입 완료율: 목표 60%
- 소셜 로그인 비율: 목표 70%
- 환영 이메일 오픈율: 목표 40%
- 첫 구매 전환율: 목표 20%
```

---

#### 1.2 로그인 (Sign In)

**사용자 스토리**:
> "지현은 전에 가입한 적이 있어서 이메일과 비밀번호로 로그인하려고 합니다."

**기능 요구사항**:
```
FR-1.2.1: 이메일 로그인
  - 이메일, 비밀번호 입력
  - "로그인 상태 유지" 옵션 (30일)
  - 로그인 실패 시 에러 메시지
  - 5회 실패 시 계정 잠금 (15분)

FR-1.2.2: 비밀번호 재설정
  - "비밀번호를 잊으셨나요?" 링크
  - 이메일로 재설정 링크 발송
  - 링크 유효 시간: 1시간
  - 새 비밀번호 설정

FR-1.2.3: 자동 로그인
  - Access Token 저장 (localStorage)
  - Token 만료 시 자동 갱신
  - 만료 시 로그인 페이지로 리다이렉트
```

**수용 기준**:
```gherkin
Given 등록된 사용자가 로그인 페이지에 있을 때
When 올바른 이메일과 비밀번호 입력 후 "로그인" 클릭
Then 로그인 성공하고 이전 페이지 또는 홈으로 이동

Given 사용자가 잘못된 비밀번호를 입력할 때
When "로그인" 버튼 클릭
Then "이메일 또는 비밀번호가 올바르지 않습니다" 에러 표시

Given 사용자가 5번 연속 로그인 실패할 때
Then 계정이 15분간 잠기고 "계정이 일시적으로 잠겼습니다" 메시지 표시
And 비밀번호 재설정 링크 제공
```

**기술 스펙**:
```typescript
// API: lib/shopify/customer.ts

interface SignInInput {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface AccessToken {
  accessToken: string;
  expiresAt: string;
}

async function signIn(input: SignInInput): Promise<AccessToken> {
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

  const response = await shopifyStorefrontFetch(mutation, {
    input: {
      email: input.email,
      password: input.password
    }
  });

  if (response.customerUserErrors.length > 0) {
    throw new AuthenticationError('이메일 또는 비밀번호가 올바르지 않습니다');
  }

  const token = response.customerAccessToken;

  // Zustand Store에 저장
  useUserStore.getState().setUser({
    accessToken: token.accessToken,
    expiresAt: token.expiresAt
  });

  // LocalStorage에 저장 (remember me)
  if (input.rememberMe) {
    localStorage.setItem('customerAccessToken', token.accessToken);
  }

  return token;
}
```

---

### 2. 제품 카탈로그

#### 2.1 제품 목록

**사용자 스토리**:
> "지현은 NERDX APEC에서 어떤 전통주를 판매하는지 둘러보고 싶어합니다."

**기능 요구사항**:
```
FR-2.1.1: 제품 목록 표시
  - 제품 카드 (이미지, 이름, 가격, 간단한 설명)
  - Grid view (기본) / List view
  - 무한 스크롤 또는 페이지네이션
  - Loading skeleton

FR-2.1.2: 필터링
  - 카테고리 (막걸리, 소주, 청주, 과실주)
  - 가격대 (슬라이더)
  - 재고 있음만 보기
  - APEC 한정판
  - AR 체험 가능

FR-2.1.3: 정렬
  - 추천순 (기본)
  - 최신순
  - 낮은 가격순
  - 높은 가격순
  - 인기순 (판매량)
  - 리뷰 많은 순

FR-2.1.4: 검색
  - 제품명 검색
  - 자동완성 (3글자 이상)
  - 검색 기록 저장
  - 인기 검색어
```

**수용 기준**:
```gherkin
Given 사용자가 /products 페이지에 있을 때
When 페이지가 로드됨
Then 모든 제품이 Grid view로 표시됨
And 각 제품 카드는 이미지, 이름, 가격, "장바구니 담기" 버튼을 포함

Given 사용자가 "막걸리" 카테고리 필터를 선택할 때
When 필터 적용
Then 막걸리 카테고리 제품만 표시됨
And URL이 /products?category=makgeolli 로 변경됨

Given 사용자가 "낮은 가격순" 정렬을 선택할 때
When 정렬 옵션 변경
Then 제품이 가격 오름차순으로 재정렬됨
```

**기술 스펙**:
```typescript
// API: lib/shopify/client.ts

interface ProductsQuery {
  first?: number;
  after?: string;
  query?: string;
  sortKey?: 'RELEVANCE' | 'PRICE' | 'CREATED_AT' | 'BEST_SELLING';
  reverse?: boolean;
}

async function getProducts(query: ProductsQuery): Promise<Product[]> {
  const graphql = `
    query getProducts(
      $first: Int!
      $after: String
      $query: String
      $sortKey: ProductSortKeys
      $reverse: Boolean
    ) {
      products(
        first: $first
        after: $after
        query: $query
        sortKey: $sortKey
        reverse: $reverse
      ) {
        edges {
          node {
            id
            handle
            title
            description
            priceRange {
              minVariantPrice {
                amount
                currencyCode
              }
            }
            featuredImage {
              url(transform: { maxWidth: 600 })
              altText
            }
            tags
            availableForSale
            metafields(identifiers: [
              { namespace: "custom", key: "ar_enabled" }
              { namespace: "custom", key: "apec_limited" }
              { namespace: "custom", key: "stock_remaining" }
            ]) {
              key
              value
            }
          }
          cursor
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  `;

  const response = await shopifyStorefrontFetch(graphql, {
    first: query.first || 20,
    after: query.after,
    query: query.query,
    sortKey: query.sortKey || 'RELEVANCE',
    reverse: query.reverse || false
  });

  return response.products.edges.map(edge => transformProduct(edge.node));
}
```

**UI 목업**:
```
┌──────────────────────────────────────────────────────────────┐
│ NERDX APEC > 제품                                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Discover Amazing Products                                   │
│ Browse our curated collection of Korean traditional alcohol │
│                                                              │
│ ┌──────────────────────────┐  [Filters ▼]  [Most Popular ▼] │
│ │ 🔍 Search products...    │   [Grid]  [List]               │
│ └──────────────────────────┘                                │
│                                                              │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                         │
│ │ [img]│ │ [img]│ │ [img]│ │ [img]│                         │
│ │      │ │      │ │      │ │      │                         │
│ │ NERD │ │ NERD │ │NERDX │ │ NERD │                         │
│ │Makge │ │ Soju │ │Cheong│ │ Fruit│                         │
│ │      │ │      │ │  ju  │ │ Wine │                         │
│ │$30.00│ │$16.00│ │$50.00│ │$25.00│                         │
│ │      │ │      │ │      │ │      │                         │
│ │[+Cart│ │[+Cart│ │[+Cart│ │[+Cart│                         │
│ └──────┘ └──────┘ └──────┘ └──────┘                         │
│                                                              │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                         │
│ │ ...  │ │ ...  │ │ ...  │ │ ...  │                         │
│ └──────┘ └──────┘ └──────┘ └──────┘                         │
│                                                              │
│             [Load More Products]                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**측정 지표**:
```
- 제품 목록 조회수: 전체 트래픽의 80%
- 필터 사용률: 40%
- 검색 사용률: 30%
- 제품 카드 클릭율: 15%
- 장바구니 담기 전환율: 5%
```

---

#### 2.2 제품 상세

**사용자 스토리**:
> "지현은 'NERD Premium Makgeolli'가 궁금해서 클릭했습니다. 상세 정보와 리뷰를 보고 싶어합니다."

**기능 요구사항**:
```
FR-2.2.1: 제품 정보 표시
  - 고화질 이미지 갤러리 (확대/축소)
  - 제품명, 가격
  - 상세 설명 (원재료, 도수, 용량 등)
  - 재고 상태
  - 배송 정보
  - 반품/교환 정책

FR-2.2.2: 옵션 선택
  - 수량 선택 (1-10)
  - 옵션 선택 (있을 경우)
  - 선물 포장 옵션
  - 수량에 따른 가격 자동 계산

FR-2.2.3: 구매 액션
  - "장바구니 담기" 버튼
  - "바로 구매" 버튼
  - "찜하기" 버튼
  - "공유하기" 버튼 (카카오톡, 링크 복사)

FR-2.2.4: 추가 정보
  - 추천 제품 (함께 본 제품, 비슷한 제품)
  - 리뷰 (Phase 2)
  - Q&A (Phase 2)
  - AR 체험 버튼 (if ar_enabled)

FR-2.2.5: 메타 정보
  - Metafields 표시 (APEC 한정, 재고 개수 등)
  - SEO 최적화 (title, description, og:image)
```

**수용 기준**:
```gherkin
Given 사용자가 제품 카드를 클릭할 때
When /products/nerd-premium-makgeolli 페이지로 이동
Then 제품 상세 정보가 표시됨
And 이미지 갤러리, 가격, 설명, 옵션이 모두 보임

Given 사용자가 수량을 3개로 변경할 때
When 수량 증가 버튼을 2번 클릭
Then 수량이 3으로 변경되고 총 가격이 $90.00으로 업데이트됨

Given 사용자가 "장바구니 담기" 버튼을 클릭할 때
When 버튼 클릭
Then 장바구니에 제품이 추가되고 토스트 메시지 "장바구니에 담았습니다" 표시
And 장바구니 아이콘의 숫자가 1 증가

Given 재고가 없는 제품일 때
Then "품절" 배지 표시
And "장바구니 담기" 버튼이 비활성화됨
And "재입고 알림 신청" 버튼이 표시됨
```

**기술 스펙**:
```typescript
// API: lib/shopify/client.ts

async function getProductByHandle(handle: string): Promise<Product> {
  const query = `
    query getProductByHandle($handle: String!) {
      productByHandle(handle: $handle) {
        id
        title
        description
        descriptionHtml
        handle
        tags
        priceRange {
          minVariantPrice {
            amount
            currencyCode
          }
          maxVariantPrice {
            amount
            currencyCode
          }
        }
        images(first: 10) {
          edges {
            node {
              url(transform: { maxWidth: 1200 })
              altText
            }
          }
        }
        variants(first: 20) {
          edges {
            node {
              id
              title
              price {
                amount
                currencyCode
              }
              availableForSale
              quantityAvailable
              selectedOptions {
                name
                value
              }
            }
          }
        }
        seo {
          title
          description
        }
        metafields(identifiers: [
          { namespace: "custom", key: "ar_enabled" }
          { namespace: "custom", key: "ar_asset_url" }
          { namespace: "custom", key: "apec_limited" }
          { namespace: "custom", key: "stock_remaining" }
          { namespace: "custom", key: "alcohol_content" }
          { namespace: "custom", key: "volume" }
          { namespace: "custom", key: "ingredients" }
        ]) {
          key
          value
        }
      }
    }
  `;

  const response = await shopifyStorefrontFetch(query, { handle });

  if (!response.productByHandle) {
    throw new NotFoundError('제품을 찾을 수 없습니다');
  }

  return transformProduct(response.productByHandle);
}
```

---

### 3. 장바구니 & 체크아웃

#### 3.1 장바구니

**사용자 스토리**:
> "지현은 여러 제품을 장바구니에 담고 한 번에 결제하고 싶어합니다."

**기능 요구사항**:
```
FR-3.1.1: 장바구니 관리
  - 장바구니 아이템 목록
  - 수량 변경 (+/- 버튼)
  - 아이템 제거 (X 버튼)
  - 가격 요약 (소계, 배송비, 할인, 총액)
  - 쿠폰 코드 입력

FR-3.1.2: 실시간 동기화
  - Shopify Cart API와 동기화
  - 재고 부족 시 경고
  - 가격 변동 시 알림
  - 다중 기기 동기화 (로그인 시)

FR-3.1.3: 장바구니 유지
  - 로그아웃해도 유지 (30일)
  - 브라우저 닫아도 유지
  - 장바구니 공유 (URL)

FR-3.1.4: 추가 기능
  - 추천 제품 ("이 제품은 어때요?")
  - 무료 배송까지 남은 금액 표시
  - "나중에 보기" (Wishlist로 이동)
```

**수용 기준**:
```gherkin
Given 사용자가 장바구니 페이지에 있을 때
When 페이지 로드
Then 장바구니에 담긴 모든 제품이 표시됨
And 각 제품은 이미지, 이름, 가격, 수량, 소계를 포함

Given 사용자가 제품 수량을 3으로 변경할 때
When 수량 입력 필드에 3 입력 또는 + 버튼 클릭
Then 수량이 3으로 변경되고 소계가 업데이트됨
And 총액이 자동으로 재계산됨

Given 사용자가 제품 제거 버튼(X)을 클릭할 때
When 버튼 클릭 후 확인
Then 제품이 장바구니에서 제거됨
And "제품이 장바구니에서 제거되었습니다" 토스트 메시지 표시

Given 장바구니가 비어있을 때
Then "장바구니가 비어있습니다" 메시지 표시
And "쇼핑 계속하기" 버튼 표시
```

**기술 스펙**:
```typescript
// API: lib/shopify/cart.ts

// Zustand Store
interface CartStore {
  cart: Cart | null;
  isLoading: boolean;
  addItem: (variantId: string, quantity: number) => Promise<void>;
  updateItem: (lineId: string, quantity: number) => Promise<void>;
  removeItem: (lineId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  syncWithServer: () => Promise<void>;
}

export const useCart = create<CartStore>((set, get) => ({
  cart: null,
  isLoading: false,

  addItem: async (variantId, quantity) => {
    set({ isLoading: true });
    try {
      const currentCart = get().cart;

      if (!currentCart) {
        // Create new cart
        const newCart = await cartService.create([
          { merchandiseId: variantId, quantity }
        ]);
        set({ cart: newCart, isLoading: false });
      } else {
        // Add to existing cart
        const updatedCart = await cartService.addLines(
          currentCart.id,
          [{ merchandiseId: variantId, quantity }]
        );
        set({ cart: updatedCart, isLoading: false });
      }

      toast.success('장바구니에 담았습니다');
    } catch (error) {
      set({ isLoading: false });
      toast.error('장바구니 추가 실패');
      throw error;
    }
  },

  updateItem: async (lineId, quantity) => {
    set({ isLoading: true });
    try {
      const currentCart = get().cart;
      if (!currentCart) return;

      const updatedCart = await cartService.updateLines(
        currentCart.id,
        [{ id: lineId, quantity }]
      );
      set({ cart: updatedCart, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      toast.error('수량 변경 실패');
      throw error;
    }
  },

  removeItem: async (lineId) => {
    set({ isLoading: true });
    try {
      const currentCart = get().cart;
      if (!currentCart) return;

      const updatedCart = await cartService.removeLines(
        currentCart.id,
        [lineId]
      );
      set({ cart: updatedCart, isLoading: false });
      toast.success('제품이 제거되었습니다');
    } catch (error) {
      set({ isLoading: false });
      toast.error('제품 제거 실패');
      throw error;
    }
  },

  syncWithServer: async () => {
    const cartId = localStorage.getItem('cartId');
    if (!cartId) return;

    try {
      const cart = await cartService.get(cartId);
      set({ cart });
    } catch (error) {
      // Cart not found or expired
      localStorage.removeItem('cartId');
      set({ cart: null });
    }
  }
}));
```

---

#### 3.2 체크아웃

**사용자 스토리**:
> "지현은 장바구니에 담은 제품들을 구매하려고 합니다. 간편하게 결제하고 싶어합니다."

**기능 요구사항**:
```
FR-3.2.1: 배송 정보 입력
  - 수령인 이름, 전화번호
  - 배송 주소 (우편번호 검색)
  - 배송 메모
  - 최근 배송지 저장 (로그인 시)

FR-3.2.2: 결제 수단 선택
  - Shopify Payments (카드)
  - 네이버페이
  - 카카오페이
  - 토스페이
  - 가상계좌 (Phase 2)

FR-3.2.3: 주문 확인
  - 주문 제품 요약
  - 배송 정보 확인
  - 결제 금액 확인
  - 개인정보 수집 동의
  - 환불/교환 정책 동의

FR-3.2.4: 결제 완료
  - 주문 번호 발급
  - 주문 완료 페이지로 리다이렉트
  - 주문 확인 이메일 발송
  - SMS 알림 (선택)

FR-3.2.5: 게스트 체크아웃
  - 로그인 없이 주문 가능
  - 이메일로 주문 조회 가능
  - 회원 전환 유도
```

**수용 기준**:
```gherkin
Given 사용자가 장바구니에서 "결제하기" 클릭할 때
When Shopify Checkout 페이지로 리다이렉트
Then 장바구니 아이템이 모두 표시됨
And 배송 정보 입력 폼이 표시됨

Given 사용자가 모든 필수 정보를 입력하고 "결제하기" 클릭할 때
When 결제 진행
Then Shopify Payments로 결제 처리됨
And 결제 성공 시 주문 완료 페이지로 리다이렉트

Given 결제가 완료되었을 때
Then 주문 번호가 발급되고 표시됨
And 주문 확인 이메일이 발송됨
And 장바구니가 비워짐

Given 결제가 실패했을 때
Then "결제에 실패했습니다" 에러 메시지 표시
And 다시 시도할 수 있도록 결제 페이지 유지
```

**기술 스펙**:
```typescript
// Shopify Checkout 사용
// cart.checkoutUrl로 리다이렉트하면 Shopify가 모든 걸 처리

async function redirectToCheckout(cartId: string): Promise<void> {
  const cart = await cartService.get(cartId);

  if (!cart.checkoutUrl) {
    throw new Error('Checkout URL not found');
  }

  // Shopify Checkout으로 리다이렉트
  window.location.href = cart.checkoutUrl;
}

// 또는 Shopify Buy SDK 사용
async function createCheckout(lineItems: LineItem[]): Promise<Checkout> {
  const checkout = await client.checkout.create();

  const checkoutWithItems = await client.checkout.addLineItems(
    checkout.id,
    lineItems
  );

  return checkoutWithItems;
}
```

---

### 4. 뉴스레터 & 커뮤니티

#### 4.1 뉴스레터 구독

**사용자 스토리**:
> "지현은 NERDX APEC의 신제품과 특별 혜택을 놓치고 싶지 않아서 뉴스레터를 구독하려고 합니다. 커뮤니티에 소속되고 싶어합니다."

**기능 요구사항**:
```
FR-4.1.1: 뉴스레터 구독 폼
  - 푸터 구독 폼 (모든 페이지)
  - 이메일 입력 필드
  - "구독하기" 버튼
  - 실시간 이메일 유효성 검사
  - 개인정보 처리방침 동의 안내

FR-4.1.2: 구독 인센티브 표시
  - ✨ 첫 구매 15% 할인
  - 🎁 APEC 한정판 우선 구매권
  - 📚 전통주 가이드 & 레시피
  - 🎬 월 1회 무료 CAMEO 크레딧
  - 현재 구독자 수 표시 (소셜 프루프)

FR-4.1.3: 환영 팝업 (첫 방문 시)
  - 30초 후 또는 이탈 의도 감지 시 표시
  - 구독 혜택 강조
  - "나중에 가입하기" 옵션
  - 쿠키로 재표시 방지 (30일)

FR-4.1.4: 체크아웃 완료 구독
  - 주문 완료 페이지에 구독 폼
  - "다음 주문 시 10% 할인" 인센티브
  - 원클릭 구독 (이메일 자동 입력)

FR-4.1.5: 구독 확인 & 리워드
  - 즉시 웰컴 이메일 발송
  - 쿠폰 코드 자동 발급 (WELCOME15)
  - 쿠폰 모달 표시
  - 추천 제품 3개 안내
```

**수용 기준 (Acceptance Criteria)**:
```gherkin
Given 사용자가 푸터 뉴스레터 폼에 있을 때
When 유효한 이메일을 입력하고 "구독하기" 클릭
Then 구독이 완료되고 "🎉 환영합니다! 이메일을 확인해주세요" 토스트 표시
And Shopify Customer의 acceptsMarketing이 true로 설정됨
And 웰컴 이메일이 즉시 발송됨
And WELCOME15 쿠폰이 자동 발급됨

Given 사용자가 이미 구독한 이메일로 재구독 시도할 때
When "구독하기" 버튼 클릭
Then "이미 구독 중입니다" 메시지 표시
And 마케팅 동의 상태가 업데이트됨

Given 사용자가 첫 방문일 때
When 페이지 로드 후 30초 경과
Then 뉴스레터 팝업 모달이 표시됨
And 팝업은 닫힌 후 30일간 재표시되지 않음

Given 사용자가 주문을 완료했을 때
When 주문 완료 페이지 로드
Then 뉴스레터 구독 폼이 표시됨
And 이메일 필드가 주문 이메일로 자동 입력됨
And "다음 주문 시 10% 할인" 인센티브 표시
```

**기술 스펙**:
```typescript
// lib/shopify/newsletter.ts

interface NewsletterInput {
  email: string;
  firstName?: string;
  source?: 'footer' | 'popup' | 'checkout';
}

interface NewsletterResponse {
  success: boolean;
  couponCode?: string;
  message: string;
}

/**
 * 뉴스레터 구독
 * Shopify Customer API의 acceptsMarketing 필드 활용
 */
async function subscribeToNewsletter(
  input: NewsletterInput
): Promise<NewsletterResponse> {
  // 1. Shopify Customer 생성 or 업데이트
  const mutation = `
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        customer {
          id
          email
          acceptsMarketing
        }
        customerUserErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyAdminFetch(mutation, {
      input: {
        email: input.email,
        firstName: input.firstName,
        acceptsMarketing: true,
        acceptsMarketingUpdatedAt: new Date().toISOString(),
        tags: ['newsletter', `source:${input.source}`, 'community']
      }
    });

    if (response.customerUserErrors.length > 0) {
      const error = response.customerUserErrors[0];

      // 이미 존재하는 고객이면 마케팅 동의 업데이트
      if (error.message.includes('taken')) {
        await updateMarketingConsent(input.email, true);
        return {
          success: true,
          message: '구독 설정이 업데이트되었습니다'
        };
      }

      throw new ValidationError(error.message);
    }

    // 2. 웰컴 쿠폰 발급
    const couponCode = `WELCOME15-${generateUniqueCode()}`;
    await createDiscountCode({
      code: couponCode,
      type: 'PERCENTAGE',
      value: 15,
      usageLimit: 1,
      customerEmail: input.email,
      expiresAt: addDays(new Date(), 30) // 30일 유효
    });

    // 3. 웰컴 이메일 트리거 (Shopify Email or Klaviyo)
    await triggerWelcomeEmail({
      email: input.email,
      firstName: input.firstName,
      couponCode
    });

    // 4. 분석 이벤트 트래킹
    await trackEvent('newsletter_subscribed', {
      email: input.email,
      source: input.source,
      timestamp: new Date().toISOString()
    });

    return {
      success: true,
      couponCode,
      message: '구독이 완료되었습니다!'
    };

  } catch (error) {
    console.error('Newsletter subscription error:', error);
    throw error;
  }
}

/**
 * 마케팅 동의 업데이트 (기존 고객)
 */
async function updateMarketingConsent(
  email: string,
  acceptsMarketing: boolean
): Promise<void> {
  const mutation = `
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        customer {
          id
          email
          acceptsMarketing
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  await shopifyAdminFetch(mutation, {
    input: {
      email,
      acceptsMarketing,
      acceptsMarketingUpdatedAt: new Date().toISOString()
    }
  });
}

/**
 * 웰컴 이메일 트리거
 */
async function triggerWelcomeEmail(params: {
  email: string;
  firstName?: string;
  couponCode: string;
}): Promise<void> {
  // Shopify Email 또는 Klaviyo API 호출
  if (process.env.KLAVIYO_API_KEY) {
    // Klaviyo 사용
    await klaviyo.track('Newsletter Subscribed', {
      email: params.email,
      firstName: params.firstName,
      couponCode: params.couponCode
    });
  } else {
    // Shopify Email 사용
    await shopifyEmailAPI.send({
      to: params.email,
      template: 'welcome-email',
      data: {
        firstName: params.firstName || '고객님',
        couponCode: params.couponCode,
        recommendedProducts: await getRecommendedProducts(3)
      }
    });
  }
}

/**
 * 할인 코드 생성
 */
async function createDiscountCode(params: {
  code: string;
  type: 'PERCENTAGE' | 'FIXED_AMOUNT';
  value: number;
  usageLimit: number;
  customerEmail: string;
  expiresAt: Date;
}): Promise<void> {
  const mutation = `
    mutation priceRuleCreate($priceRule: PriceRuleInput!, $priceRuleDiscountCode: PriceRuleDiscountCodeInput!) {
      priceRuleCreate(priceRule: $priceRule, priceRuleDiscountCode: $priceRuleDiscountCode) {
        priceRule {
          id
        }
        priceRuleDiscountCode {
          id
          code
        }
        priceRuleUserErrors {
          field
          message
        }
      }
    }
  `;

  await shopifyAdminFetch(mutation, {
    priceRule: {
      title: `Welcome Discount - ${params.customerEmail}`,
      valueType: params.type === 'PERCENTAGE' ? 'PERCENTAGE' : 'FIXED_AMOUNT',
      value: params.value,
      customerSelection: {
        forAllCustomers: false
      },
      target: {
        targetType: 'LINE_ITEM',
        targetAllLineItems: true
      },
      allocationMethod: 'ACROSS',
      usageLimit: params.usageLimit,
      startsAt: new Date().toISOString(),
      endsAt: params.expiresAt.toISOString()
    },
    priceRuleDiscountCode: {
      code: params.code
    }
  });
}

/**
 * 유니크 코드 생성
 */
function generateUniqueCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 8; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}
```

**프론트엔드 컴포넌트**:
```typescript
// components/NewsletterSignup.tsx

'use client';

import { useState } from 'react';
import { Mail, Sparkles, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface NewsletterSignupProps {
  source: 'footer' | 'popup' | 'checkout';
  variant?: 'default' | 'compact';
  onSuccess?: () => void;
}

export default function NewsletterSignup({
  source,
  variant = 'default',
  onSuccess
}: NewsletterSignupProps) {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [couponCode, setCouponCode] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      toast.error('올바른 이메일 주소를 입력해주세요');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || '구독 실패');
      }

      setIsSubscribed(true);
      setCouponCode(data.couponCode);
      toast.success('🎉 환영합니다! 이메일을 확인해주세요.');

      // 쿠폰 모달 표시
      setTimeout(() => {
        showCouponModal(data.couponCode);
      }, 1000);

      onSuccess?.();

    } catch (error) {
      console.error('Subscription error:', error);
      toast.error(error.message || '구독에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  }

  function showCouponModal(code: string) {
    // Show modal with coupon code
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white rounded-2xl p-8 max-w-md mx-4 text-center">
          <div class="text-4xl mb-4">🎉</div>
          <h3 class="text-2xl font-bold mb-2">환영합니다!</h3>
          <p class="text-gray-600 mb-4">첫 구매 15% 할인 쿠폰을 받으셨어요</p>
          <div class="bg-primary-50 rounded-lg p-4 mb-4">
            <div class="text-sm text-gray-600 mb-1">쿠폰 코드</div>
            <div class="text-2xl font-bold text-primary-600">${code}</div>
          </div>
          <button onclick="this.parentElement.parentElement.remove()" class="btn-primary w-full">
            쇼핑 시작하기
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  if (isSubscribed) {
    return (
      <div className="text-center py-8">
        <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary-600" />
        <h3 className="text-xl font-bold mb-2">구독 완료!</h3>
        <p className="text-gray-600 mb-4">
          이메일로 15% 할인 쿠폰을 보내드렸어요
        </p>
        {couponCode && (
          <div className="inline-block bg-primary-50 rounded-lg px-6 py-3">
            <div className="text-sm text-gray-600 mb-1">쿠폰 코드</div>
            <div className="text-xl font-bold text-primary-600">{couponCode}</div>
          </div>
        )}
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="이메일 주소"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary whitespace-nowrap"
        >
          {isLoading ? '구독 중...' : '구독'}
        </button>
      </form>
    );
  }

  return (
    <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-2xl p-8">
      <div className="max-w-xl mx-auto text-center">
        <Mail className="w-12 h-12 mx-auto mb-4 text-primary-600" />

        <h3 className="text-2xl font-bold mb-2">
          🍶 Join the NERDX Community
        </h3>

        <p className="text-gray-700 mb-6">
          전통주를 사랑하는 커뮤니티에 가입하고 특별한 혜택을 받아보세요
        </p>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">✨</div>
            <div className="text-sm font-semibold">첫 구매 15% 할인</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">🎁</div>
            <div className="text-sm font-semibold">한정판 우선 구매</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">📚</div>
            <div className="text-sm font-semibold">전통주 가이드</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-1">🎬</div>
            <div className="text-sm font-semibold">무료 CAMEO</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary px-8 py-3 text-lg whitespace-nowrap"
          >
            {isLoading ? '구독 중...' : '구독하기'}
          </button>
        </form>

        <p className="text-sm text-gray-500">
          12,453명이 이미 참여하고 있어요 💜
        </p>

        <p className="text-xs text-gray-400 mt-2">
          구독 시 개인정보 처리방침에 동의하게 됩니다
        </p>
      </div>
    </div>
  );
}
```

**UI 목업**:

1. **푸터 뉴스레터 섹션**:
```
┌────────────────────────────────────────────────────────┐
│                    Footer                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  🍶 Join the NERDX Community                    │  │
│  │                                                 │  │
│  │  전통주를 사랑하는 커뮤니티에 가입하고          │  │
│  │  특별한 혜택을 받아보세요                       │  │
│  │                                                 │  │
│  │  ✨ 첫 구매 15% 할인                            │  │
│  │  🎁 APEC 한정판 우선 구매권                     │  │
│  │  📚 전통주 가이드 & 레시피                      │  │
│  │  🎬 월 1회 무료 CAMEO 크레딧                   │  │
│  │                                                 │  │
│  │  ┌──────────────────────────────┐  [구독하기]   │  │
│  │  │ 📧 your@email.com            │              │  │
│  │  └──────────────────────────────┘              │  │
│  │                                                 │  │
│  │  12,453명이 이미 참여하고 있어요 💜             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

2. **팝업 모달 (첫 방문 시)**:
```
┌────────────────────────────────────────────┐
│                 [X]                        │
│                                            │
│         🍶                                 │
│                                            │
│     Welcome to NERDX APEC!                │
│                                            │
│   전통주 여정을 시작해보세요                 │
│                                            │
│   지금 커뮤니티에 가입하시면:                │
│   ✅ 첫 주문 15% 할인                       │
│   ✅ 무료 배송 쿠폰 (5만원 이상)             │
│   ✅ 전통주 초보자 가이드 PDF               │
│                                            │
│   ┌──────────────────────────┐            │
│   │ 이메일 입력                │            │
│   └──────────────────────────┘            │
│                                            │
│   [  커뮤니티 가입하고 혜택 받기  ]         │
│                                            │
│   나중에 가입하기                           │
│                                            │
└────────────────────────────────────────────┘
```

3. **체크아웃 완료 페이지**:
```
┌────────────────────────────────────────────┐
│  ✅ 주문이 완료되었습니다!                   │
│                                            │
│  주문 번호: #12345                         │
│  총 결제 금액: 47,000원                     │
│                                            │
│  ─────────────────────────────────         │
│                                            │
│  💡 한 가지 더!                             │
│                                            │
│  뉴스레터를 구독하시고                       │
│  다음 주문 시 10% 할인 받으세요              │
│                                            │
│  ┌────────────────────┐  [구독하기]        │
│  │ your@email.com     │                   │
│  └────────────────────┘                   │
│                                            │
└────────────────────────────────────────────┘
```

**측정 지표 (Metrics)**:
```
구독 전환율:
- 푸터: 목표 2-3%
- 팝업: 목표 5-10%
- 체크아웃: 목표 15-20%

구독자 성장:
- Month 1: 500명
- Month 3: 2,000명
- Month 6: 5,000명

이메일 오픈율:
- 웰컴 이메일: 목표 60%+
- 정기 뉴스레터: 목표 25%+
- 트리거 이메일: 목표 40%+

이메일 클릭율:
- 웰컴 이메일: 목표 30%+
- 정기 뉴스레터: 목표 5%+
- 트리거 이메일: 목표 15%+

쿠폰 사용률:
- WELCOME15: 목표 20%+
- 재구매 쿠폰: 목표 15%+
```

---

#### 4.2 이메일 마케팅 자동화

**사용자 스토리**:
> "지현은 뉴스레터 구독 후 정기적으로 신제품 정보와 전통주 이야기를 받고 싶어합니다. 또한 장바구니에 담았던 제품을 잊었을 때 리마인더를 받고 싶어합니다."

**기능 요구사항**:
```
FR-4.2.1: 웰컴 이메일 (즉시)
  - 구독 완료 즉시 자동 발송
  - 15% 쿠폰 코드 포함
  - 베스트셀러 3개 추천
  - 소셜 미디어 링크
  - 개인화된 인사말

FR-4.2.2: 정기 뉴스레터 (주 1회)
  - 매주 목요일 오후 7시 발송
  - 신제품 소개
  - 전통주 교육 컨텐츠
  - CAMEO 우수 작품 소개
  - AI 기반 개인화 추천

FR-4.2.3: 장바구니 포기 이메일 (1시간 후)
  - 장바구니 남은 제품 표시
  - 10% 추가 할인 제공
  - 긴급성 표현 (재고 부족)
  - "장바구니로 돌아가기" CTA

FR-4.2.4: 첫 구매 후 이메일 (3일 후)
  - 리뷰 작성 요청
  - 500원 적립금 인센티브
  - 관련 제품 추천
  - 전통주 즐기는 팁

FR-4.2.5: 재구매 유도 이메일 (30일 후)
  - 재구매 특별 할인 15%
  - 최근 구매 제품 리마인드
  - 새로운 추천 제품
  - "다시 만나서 반가워요" 메시지

FR-4.2.6: 비활성 고객 윈백 (90일 후)
  - 20% 윈백 쿠폰
  - 신제품 하이라이트
  - "보고 싶었어요" 메시지
  - 구독 유지 인센티브

FR-4.2.7: 생일 축하 이메일 (생일 당일)
  - 25% 생일 쿠폰
  - 무료 배송
  - 개인화된 축하 메시지
  - 선물 추천
```

**수용 기준**:
```gherkin
Given 사용자가 뉴스레터를 구독했을 때
When 구독 완료
Then 5분 이내 웰컴 이메일이 발송됨
And 이메일에 WELCOME15 쿠폰 코드가 포함됨
And 베스트셀러 3개가 포함됨

Given 매주 목요일 오후 7시일 때
When 뉴스레터 발송 스케줄 실행
Then 모든 구독자에게 정기 뉴스레터가 발송됨
And 각 사용자의 구매 이력 기반 개인화된 추천 포함

Given 사용자가 장바구니에 제품을 담고 1시간 경과했을 때
When 체크아웃하지 않음
Then 장바구니 포기 이메일이 자동 발송됨
And 10% 추가 할인 쿠폰이 포함됨

Given 사용자가 첫 구매 후 3일이 경과했을 때
When 리뷰를 작성하지 않음
Then 리뷰 요청 이메일이 발송됨
And 500원 적립금 인센티브가 제공됨

Given 사용자가 마지막 구매 후 30일이 경과했을 때
Then 재구매 유도 이메일이 발송됨
And 15% 할인 쿠폰이 포함됨

Given 사용자가 90일간 활동이 없을 때
Then 윈백 이메일이 발송됨
And 20% 특별 할인 쿠폰이 포함됨

Given 사용자의 생일일 때
Then 생일 축하 이메일이 발송됨
And 25% 생일 쿠폰과 무료 배송이 제공됨
```

**기술 스펙**:
```typescript
// lib/email/automation.ts

/**
 * 이메일 자동화 워크플로우
 */

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  trigger: TriggerType;
  delay?: number; // minutes
}

type TriggerType =
  | 'newsletter_subscribed'
  | 'cart_abandoned'
  | 'order_created'
  | 'order_delivered'
  | 'customer_birthday'
  | 'customer_inactive';

/**
 * Klaviyo를 사용한 자동화 플로우
 */
class EmailAutomation {
  private klaviyo: KlaviyoClient;

  constructor() {
    this.klaviyo = new KlaviyoClient(process.env.KLAVIYO_API_KEY);
  }

  /**
   * 웰컴 이메일 플로우
   */
  async sendWelcomeEmail(params: {
    email: string;
    firstName?: string;
    couponCode: string;
  }): Promise<void> {
    await this.klaviyo.track({
      event: 'Newsletter Subscribed',
      customerProperties: {
        $email: params.email,
        $first_name: params.firstName || '고객님'
      },
      properties: {
        coupon_code: params.couponCode,
        subscribed_at: new Date().toISOString()
      }
    });

    // Klaviyo 플로우가 자동으로 웰컴 이메일 발송
  }

  /**
   * 장바구니 포기 이메일
   */
  async sendCartAbandonmentEmail(params: {
    email: string;
    cartId: string;
    items: CartItem[];
    totalPrice: number;
  }): Promise<void> {
    // 1시간 후 발송되도록 스케줄
    await this.klaviyo.track({
      event: 'Abandoned Cart',
      customerProperties: {
        $email: params.email
      },
      properties: {
        cart_id: params.cartId,
        items: params.items,
        total_price: params.totalPrice,
        recovery_discount: 10, // 10% 추가 할인
        abandoned_at: new Date().toISOString()
      },
      time: Date.now() / 1000
    });

    // 10% 복구 쿠폰 발급
    const recoveryCoupon = await createDiscountCode({
      code: `RECOVER10-${generateUniqueCode()}`,
      type: 'PERCENTAGE',
      value: 10,
      usageLimit: 1,
      customerEmail: params.email,
      expiresAt: addHours(new Date(), 48) // 48시간 유효
    });
  }

  /**
   * 첫 구매 후 이메일 (리뷰 요청)
   */
  async sendFirstPurchaseFollowUp(params: {
    email: string;
    orderId: string;
    orderDate: string;
  }): Promise<void> {
    // 3일 후 발송
    const sendAt = addDays(new Date(params.orderDate), 3);

    await this.klaviyo.track({
      event: 'First Purchase Follow Up',
      customerProperties: {
        $email: params.email
      },
      properties: {
        order_id: params.orderId,
        order_date: params.orderDate,
        review_incentive: 500 // 500원 적립금
      },
      time: sendAt.getTime() / 1000
    });
  }

  /**
   * 재구매 유도 이메일
   */
  async sendRepurchaseEmail(params: {
    email: string;
    lastOrderDate: string;
    lastOrderProducts: string[];
  }): Promise<void> {
    // 30일 후 발송
    const sendAt = addDays(new Date(params.lastOrderDate), 30);

    const repurchaseCoupon = await createDiscountCode({
      code: `COMEBACK15-${generateUniqueCode()}`,
      type: 'PERCENTAGE',
      value: 15,
      usageLimit: 1,
      customerEmail: params.email,
      expiresAt: addDays(new Date(), 14) // 14일 유효
    });

    await this.klaviyo.track({
      event: 'Repurchase Reminder',
      customerProperties: {
        $email: params.email
      },
      properties: {
        last_order_date: params.lastOrderDate,
        last_products: params.lastOrderProducts,
        coupon_code: repurchaseCoupon,
        discount: 15
      },
      time: sendAt.getTime() / 1000
    });
  }

  /**
   * 비활성 고객 윈백 이메일
   */
  async sendWinbackEmail(params: {
    email: string;
    firstName?: string;
    lastActivityDate: string;
  }): Promise<void> {
    // 90일 후 발송
    const sendAt = addDays(new Date(params.lastActivityDate), 90);

    const winbackCoupon = await createDiscountCode({
      code: `WINBACK20-${generateUniqueCode()}`,
      type: 'PERCENTAGE',
      value: 20,
      usageLimit: 1,
      customerEmail: params.email,
      expiresAt: addDays(new Date(), 30) // 30일 유효
    });

    await this.klaviyo.track({
      event: 'Customer Winback',
      customerProperties: {
        $email: params.email,
        $first_name: params.firstName || '고객님'
      },
      properties: {
        last_activity: params.lastActivityDate,
        inactive_days: 90,
        coupon_code: winbackCoupon,
        discount: 20
      },
      time: sendAt.getTime() / 1000
    });
  }

  /**
   * 생일 축하 이메일
   */
  async sendBirthdayEmail(params: {
    email: string;
    firstName: string;
    birthday: string;
  }): Promise<void> {
    const birthdayCoupon = await createDiscountCode({
      code: `BDAY25-${generateUniqueCode()}`,
      type: 'PERCENTAGE',
      value: 25,
      usageLimit: 1,
      customerEmail: params.email,
      expiresAt: addDays(new Date(), 7) // 7일 유효
    });

    await this.klaviyo.track({
      event: 'Birthday',
      customerProperties: {
        $email: params.email,
        $first_name: params.firstName
      },
      properties: {
        birthday: params.birthday,
        coupon_code: birthdayCoupon,
        discount: 25,
        free_shipping: true
      }
    });
  }

  /**
   * 정기 뉴스레터 발송
   */
  async sendWeeklyNewsletter(subscribers: {
    email: string;
    firstName?: string;
    preferences?: string[];
  }[]): Promise<void> {
    // 매주 목요일 오후 7시 발송
    const campaign = await this.klaviyo.campaigns.create({
      name: `Weekly Newsletter - ${new Date().toISOString()}`,
      subject: '이번 주 NERDX 소식 🍶',
      fromEmail: 'newsletter@nerdx-apec.com',
      fromName: 'NERDX APEC',
      templateId: 'weekly-newsletter',
      listIds: ['newsletter-subscribers']
    });

    await this.klaviyo.campaigns.send(campaign.id, {
      scheduledAt: getNextThursday7PM()
    });
  }
}

/**
 * 유틸리티 함수
 */
function getNextThursday7PM(): Date {
  const now = new Date();
  const daysUntilThursday = (4 - now.getDay() + 7) % 7 || 7;
  const nextThursday = new Date(now);
  nextThursday.setDate(now.getDate() + daysUntilThursday);
  nextThursday.setHours(19, 0, 0, 0);
  return nextThursday;
}

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function addHours(date: Date, hours: number): Date {
  const result = new Date(date);
  result.setHours(result.getHours() + hours);
  return result;
}
```

**Shopify Webhooks 통합**:
```typescript
// app/api/webhooks/shopify/route.ts

import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

/**
 * Shopify Webhook 핸들러
 * 주문, 장바구니, 고객 이벤트 수신
 */
export async function POST(req: NextRequest) {
  const body = await req.text();
  const hmac = req.headers.get('x-shopify-hmac-sha256');
  const topic = req.headers.get('x-shopify-topic');

  // HMAC 검증
  if (!verifyWebhook(body, hmac)) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
  }

  const data = JSON.parse(body);

  // 이벤트 타입별 처리
  switch (topic) {
    case 'orders/create':
      await handleOrderCreated(data);
      break;

    case 'orders/paid':
      await handleOrderPaid(data);
      break;

    case 'orders/fulfilled':
      await handleOrderFulfilled(data);
      break;

    case 'carts/create':
      await handleCartCreated(data);
      break;

    case 'carts/update':
      await handleCartUpdated(data);
      break;

    case 'customers/create':
      await handleCustomerCreated(data);
      break;

    default:
      console.log('Unhandled webhook topic:', topic);
  }

  return NextResponse.json({ received: true });
}

/**
 * HMAC 서명 검증
 */
function verifyWebhook(body: string, hmac: string | null): boolean {
  if (!hmac) return false;

  const hash = crypto
    .createHmac('sha256', process.env.SHOPIFY_WEBHOOK_SECRET!)
    .update(body, 'utf8')
    .digest('base64');

  return hash === hmac;
}

/**
 * 주문 생성 시 (체크아웃 완료)
 */
async function handleOrderCreated(order: any) {
  const email = order.email;
  const isFirstOrder = order.customer?.orders_count === 1;

  if (isFirstOrder) {
    // 첫 구매 후 이메일 스케줄 (3일 후)
    await emailAutomation.sendFirstPurchaseFollowUp({
      email,
      orderId: order.id,
      orderDate: order.created_at
    });
  } else {
    // 재구매 유도 이메일 스케줄 (30일 후)
    await emailAutomation.sendRepurchaseEmail({
      email,
      lastOrderDate: order.created_at,
      lastOrderProducts: order.line_items.map((item: any) => item.title)
    });
  }
}

/**
 * 장바구니 업데이트 시
 */
async function handleCartUpdated(cart: any) {
  // 장바구니 포기 감지 로직
  const lastUpdated = new Date(cart.updated_at);
  const now = new Date();
  const hoursSinceUpdate = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);

  if (hoursSinceUpdate >= 1 && cart.line_items.length > 0) {
    // 장바구니 포기 이메일 발송
    await emailAutomation.sendCartAbandonmentEmail({
      email: cart.email,
      cartId: cart.id,
      items: cart.line_items,
      totalPrice: parseFloat(cart.total_price)
    });
  }
}

/**
 * 고객 생성 시 (회원가입 or 뉴스레터 구독)
 */
async function handleCustomerCreated(customer: any) {
  if (customer.accepts_marketing) {
    // 뉴스레터 구독자로 추가
    await emailAutomation.sendWelcomeEmail({
      email: customer.email,
      firstName: customer.first_name,
      couponCode: `WELCOME15-${generateUniqueCode()}`
    });
  }
}
```

**측정 지표 (Metrics)**:
```
이메일 발송량:
- 웰컴 이메일: 구독자 수 × 1
- 정기 뉴스레터: 구독자 수 × 52 (주간)
- 트리거 이메일: 월 100-500건

이메일 성과:
- 오픈율: 목표 30%+ (평균)
- 클릭율: 목표 10%+ (평균)
- 전환율: 목표 5%+ (평균)
- 구독 해지율: 목표 < 0.5%

비즈니스 임팩트:
- 이메일 기여 매출: 목표 20-30%
- 장바구니 복구율: 목표 10%+
- 재구매율: 목표 15%+ 증가
- 고객 생애 가치: 목표 60%+ 증가
```

---

## 📊 비기능 요구사항 (Non-Functional Requirements)

### 성능 (Performance)

```yaml
응답 시간:
  홈페이지 로드: < 2초 (First Contentful Paint)
  제품 목록 로드: < 1.5초
  제품 상세 로드: < 1초
  장바구니 업데이트: < 500ms
  검색 응답: < 300ms

Lighthouse 점수:
  Performance: > 90
  Accessibility: > 90
  Best Practices: > 90
  SEO: > 95

Core Web Vitals:
  LCP (Largest Contentful Paint): < 2.5s
  FID (First Input Delay): < 100ms
  CLS (Cumulative Layout Shift): < 0.1

API 성능:
  Shopify Storefront API: < 200ms (평균)
  Shopify Admin API: < 300ms (평균)
  커스텀 API: < 100ms (평균)
```

### 확장성 (Scalability)

```yaml
동시 사용자:
  MVP (Month 1-3): 100 명
  Growth (Month 4-6): 1,000 명
  Scale (Month 7-12): 10,000 명

트랜잭션:
  주문/일: 100건 (MVP) → 1,000건 (Scale)
  API 요청/분: 1,000 req/min (MVP) → 10,000 req/min (Scale)

데이터베이스:
  제품 수: 10개 (MVP) → 1,000개 (Scale)
  고객 수: 100명 (MVP) → 100,000명 (Scale)
  주문 수: 100건 (MVP) → 100,000건 (Scale)
```

### 보안 (Security)

```yaml
인증 & 인가:
  - Shopify Customer Access Token (JWT-like)
  - Token 만료: 2주
  - Refresh mechanism
  - Rate limiting: 100 req/min per IP

데이터 보호:
  - HTTPS 강제 (TLS 1.3)
  - API 키 환경 변수 관리
  - PII (개인정보) 암호화
  - PCI DSS Level 1 준수 (Shopify)

취약점 방어:
  - XSS (Cross-Site Scripting) 방어
  - CSRF (Cross-Site Request Forgery) 토큰
  - SQL Injection 방어 (N/A, Shopify managed)
  - Rate limiting & DDoS 방어

컴플라이언스:
  - GDPR 준수 (유럽)
  - 개인정보 보호법 준수 (한국)
  - 전자상거래법 준수
```

### 가용성 (Availability)

```yaml
업타임:
  Shopify 플랫폼: 99.99% (SLA)
  프론트엔드 (Vercel): 99.99%
  커스텀 백엔드: 99.9% (목표)

장애 복구:
  RTO (Recovery Time Objective): 1시간
  RPO (Recovery Point Objective): 5분
  자동 Failover: 30초 이내

백업:
  Shopify 데이터: 자동 백업 (일일)
  커스텀 데이터: 일일 백업 + 시간별 스냅샷
  보관 기간: 30일
```

### 호환성 (Compatibility)

```yaml
브라우저:
  - Chrome/Edge (latest, latest-1)
  - Firefox (latest, latest-1)
  - Safari (latest, latest-1)
  - Samsung Internet (latest)
  - iOS Safari 14+
  - Android Chrome 90+

디바이스:
  - Desktop: 1920x1080, 1366x768
  - Tablet: iPad (768x1024), Galaxy Tab
  - Mobile: iPhone 12+, Galaxy S20+
  - Responsive: 320px ~ 2560px

접근성 (Accessibility):
  - WCAG 2.1 Level AA 준수
  - 키보드 네비게이션 지원
  - 스크린 리더 호환
  - 색상 대비 4.5:1 이상
  - Alt text for all images
```

---

## 🧪 테스트 계획

### 단위 테스트 (Unit Tests)

```yaml
커버리지 목표: 80%

테스트 프레임워크:
  - Jest
  - Testing Library (React)
  - MSW (Mock Service Worker)

주요 테스트 항목:
  Shopify Client:
    - ✅ getProducts() 성공
    - ✅ getProducts() 에러 처리
    - ✅ getProductByHandle() 성공
    - ✅ createCustomer() 성공
    - ✅ customerAccessTokenCreate() 성공

  Cart Store:
    - ✅ addItem() 성공
    - ✅ updateItem() 수량 변경
    - ✅ removeItem() 제거
    - ✅ 재고 부족 시 에러

  Utilities:
    - ✅ formatPrice() 포맷팅
    - ✅ validateEmail() validation
    - ✅ validatePassword() validation
```

### 통합 테스트 (Integration Tests)

```yaml
주요 플로우:
  회원가입 → 로그인:
    - 회원가입 폼 작성
    - 이메일 중복 확인
    - 회원가입 성공
    - 자동 로그인
    - 마이페이지 이동

  제품 검색 → 장바구니:
    - 제품 목록 로드
    - 검색어 입력
    - 필터 적용
    - 제품 상세 클릭
    - 장바구니 담기

  장바구니 → 결제:
    - 장바구니 확인
    - 수량 변경
    - 체크아웃 클릭
    - Shopify Checkout 리다이렉트

도구:
  - Playwright
  - Cypress (대안)
```

### E2E 테스트 (End-to-End Tests)

```yaml
주요 시나리오:
  완전한 구매 플로우:
    1. 홈페이지 방문
    2. 제품 검색
    3. 제품 상세 조회
    4. 장바구니 담기
    5. 장바구니 확인
    6. 로그인/회원가입
    7. 체크아웃
    8. 배송 정보 입력
    9. 결제 (테스트 모드)
    10. 주문 완료 확인

  모바일 구매 플로우:
    - 위와 동일 (모바일 뷰포트)

도구:
  - Playwright
  - BrowserStack (크로스 브라우저)

실행 빈도:
  - PR마다 (Smoke tests)
  - 배포 전 (Full E2E suite)
  - 주간 (Regression tests)
```

### 성능 테스트

```yaml
Load Testing:
  도구: k6, Artillery
  시나리오:
    - 동시 사용자 100명
    - 5분간 지속
    - 주요 페이지 순회

  측정 지표:
    - 응답 시간 (p95, p99)
    - 처리량 (requests/sec)
    - 에러율
    - CPU/Memory 사용률

Lighthouse CI:
  - PR마다 자동 실행
  - 점수 하락 시 경고
  - 목표: 모든 지표 90+

Real User Monitoring (RUM):
  - Vercel Analytics
  - Core Web Vitals 추적
  - 사용자별 성능 분석
```

---

## 📈 성공 지표 & 모니터링

### 비즈니스 KPIs

```yaml
주요 지표 (Primary Metrics):
  월 매출 (MRR):
    목표: 1,000만원 (Month 6)
    측정: Shopify Analytics

  주문 수:
    목표: 1,000건 (Month 6)
    측정: Shopify Orders

  전환율 (Conversion Rate):
    목표: 3%
    측정: Google Analytics 4
    계산: (주문 수 / 방문자 수) * 100

  평균 주문 금액 (AOV):
    목표: 50,000원
    측정: Shopify Analytics
    계산: 총 매출 / 주문 수

보조 지표 (Secondary Metrics):
  재구매율:
    목표: 30%
    측정: Shopify + Custom
    계산: (재구매 고객 / 전체 고객) * 100

  고객 생애 가치 (LTV):
    목표: 150,000원
    계산: AOV * 구매 빈도 * 고객 수명

  고객 획득 비용 (CAC):
    목표: 30,000원
    계산: 마케팅 비용 / 신규 고객 수

  LTV/CAC 비율:
    목표: > 3
    계산: LTV / CAC

  장바구니 포기율:
    목표: < 50%
    측정: Shopify Analytics
    계산: (포기한 장바구니 / 생성된 장바구니) * 100
```

### 사용자 참여 KPIs

```yaml
트래픽:
  월 방문자 (UV):
    목표: 10,000명 (Month 6)

  페이지뷰 (PV):
    목표: 50,000 (Month 6)

  평균 세션 시간:
    목표: 3분

  Bounce Rate:
    목표: < 40%

기능 사용률:
  AI 채팅 사용률:
    목표: 40%
    계산: (채팅 시작 / 전체 방문자) * 100

  CAMEO 생성률:
    목표: 5%
    계산: (CAMEO 생성 / 전체 방문자) * 100

  AR 체험률:
    목표: 10%
    계산: (AR 클릭 / 제품 조회) * 100

  소셜 공유율:
    목표: 3%
    계산: (공유 클릭 / 제품 조회) * 100

  뉴스레터 구독률:
    목표: 5%
    계산: (구독자 수 / 전체 방문자) * 100

뉴스레터 성과:
  구독자 수:
    Month 1: 500명
    Month 3: 2,000명
    Month 6: 5,000명

  이메일 오픈율:
    웰컴 이메일: > 60%
    정기 뉴스레터: > 25%
    트리거 이메일: > 40%

  이메일 클릭율:
    웰컴 이메일: > 30%
    정기 뉴스레터: > 5%
    트리거 이메일: > 15%

  이메일 기여 매출:
    목표: 전체 매출의 20-30%

  장바구니 복구율:
    목표: > 10%
    계산: (복구된 장바구니 / 포기된 장바구니) * 100
```

### 기술 KPIs

```yaml
성능:
  평균 페이지 로드:
    목표: < 2초
    측정: Vercel Analytics

  Lighthouse 점수:
    목표: > 90 (모든 카테고리)
    측정: Lighthouse CI

  Core Web Vitals:
    LCP: < 2.5s
    FID: < 100ms
    CLS: < 0.1

가용성:
  업타임:
    목표: 99.9%
    측정: UptimeRobot

  에러율:
    목표: < 0.1%
    측정: Sentry

  API 응답 시간:
    목표: < 200ms (p95)
    측정: Custom monitoring
```

---

## 🎨 디자인 시스템

### 색상 팔레트

```css
/* Primary Colors */
--primary-50: #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* Main primary */
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;

/* Secondary Colors */
--secondary-500: #d946ef;  /* Purple */
--secondary-600: #c026d3;

/* Neutral */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;

/* Semantic Colors */
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

### 타이포그래피

```css
/* Font Families */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-korean: 'Noto Sans KR', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### 간격 (Spacing)

```css
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
--spacing-12: 3rem;     /* 48px */
--spacing-16: 4rem;     /* 64px */
```

### 컴포넌트

```css
/* Buttons */
.btn-primary {
  background: var(--primary-600);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-700);
  transform: translateY(-1px);
}

/* Cards */
.card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

/* Inputs */
.input-field {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--gray-300);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-500);
  ring: 2px solid var(--primary-200);
}
```

---

## 📱 반응형 디자인

### 브레이크포인트

```css
/* Mobile First Approach */
--screen-sm: 640px;   /* Tablet */
--screen-md: 768px;   /* Small Desktop */
--screen-lg: 1024px;  /* Desktop */
--screen-xl: 1280px;  /* Large Desktop */
--screen-2xl: 1536px; /* Extra Large */
```

### 주요 화면별 레이아웃

```yaml
Mobile (< 640px):
  - Single column
  - Hamburger menu
  - Full-width images
  - Touch-optimized buttons (min 44x44px)

Tablet (640px - 1024px):
  - 2 columns (product grid)
  - Collapsible sidebar
  - Larger touch targets

Desktop (> 1024px):
  - 3-4 columns (product grid)
  - Fixed sidebar
  - Hover interactions
  - Keyboard shortcuts
```

---

## 🚀 출시 계획

### Phase 1: MVP (Week 1-4)

```yaml
Week 1:
  - Shopify 설정
  - 제품 데이터 마이그레이션
  - 프론트엔드 Shopify 통합

Week 2:
  - 회원 시스템 구현
  - 로그인/회원가입 UI
  - 뉴스레터 구독 폼 (푸터)
  - 웰컴 이메일 설정 (Shopify Email)

Week 3:
  - 장바구니 & 체크아웃
  - Shopify Cart API 통합
  - 뉴스레터 팝업 모달
  - 체크아웃 완료 페이지 구독 폼

Week 4:
  - 테스트 & 버그 수정
  - 이메일 자동화 설정
  - 프로덕션 배포
  - Soft Launch

출시 기준:
  ✅ 제품 조회 가능
  ✅ 회원가입/로그인 작동
  ✅ 장바구니 담기 가능
  ✅ 체크아웃 & 결제 완료
  ✅ 주문 완료 이메일 발송
  ✅ 뉴스레터 구독 작동
  ✅ 웰컴 이메일 자동 발송
  ✅ 쿠폰 자동 발급
  ✅ 모든 E2E 테스트 통과
  ✅ Lighthouse 점수 90+
```

### Phase 2: 기능 확장 (Week 5-12)

```yaml
Month 2 (Week 5-8):
  - 커스텀 백엔드 구축
  - Shopify Webhooks 구독
  - Maeju AI 채팅 구현
  - 이메일 자동화 고도화
    - 장바구니 포기 이메일
    - 재구매 유도 이메일
    - 생일 축하 이메일

Month 3 (Week 9-12):
  - CAMEO 비디오 생성
  - 성능 최적화
  - 캐싱 전략 구현
  - Klaviyo 마이그레이션 (선택)
  - 고급 세그먼테이션
  - A/B 테스팅 설정

출시 기준:
  ✅ AI 채팅 정상 작동
  ✅ CAMEO 생성 가능
  ✅ API 응답 < 200ms
  ✅ 이메일 자동화 플로우 작동
  ✅ 장바구니 복구율 10%+
```

---

## 📞 지원 & 문의

### 개발팀 연락처

```
Product Owner: [이름]
Email: product@nerdx-apec.com

Tech Lead: [이름]
Email: tech@nerdx-apec.com

Design Lead: [이름]
Email: design@nerdx-apec.com
```

### 관련 문서

- [타당성 검토](SHOPIFY_BACKEND_FEASIBILITY.md)
- [마스터플랜](SHOPIFY_MASTER_PLAN.md)
- [뉴스레터 분석](NEWSLETTER_ANALYSIS.md)
- [API 문서](docs/API.md)
- [디자인 가이드](docs/DESIGN_GUIDE.md)

---

**PRD 버전**: 1.1
**최종 업데이트**: 2025년 10월 11일
**주요 변경사항**: 뉴스레터 & 커뮤니티 기능 추가 (섹션 4)
**승인 상태**: Draft
**다음 리뷰**: 2025년 10월 15일
