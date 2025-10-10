# Testing Guide - NERDX Frontend

## 📋 개요

이 문서는 NERDX APEC MVP Frontend의 테스트 전략과 실행 방법을 설명합니다.

**테스트 프레임워크**:
- **Unit & Integration Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright
- **Coverage Target**: 70%+

---

## 🏗️ 테스트 구조

```
frontend/
├── __tests__/
│   └── integration/           # Integration tests
│       └── purchase-flow.test.tsx
├── lib/shopify/__tests__/     # Unit tests
│   └── client.test.ts
├── e2e/                       # E2E tests
│   ├── product-browsing.spec.ts
│   ├── cart-checkout.spec.ts
│   └── ar-experience.spec.ts
├── jest.config.js
├── jest.setup.js
└── playwright.config.ts
```

---

## 🚀 설치

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. Playwright 설치

```bash
npm run playwright:install
```

이 명령은 Playwright 브라우저 바이너리를 설치합니다 (Chromium, Firefox, WebKit).

---

## 🧪 테스트 실행

### Unit Tests & Integration Tests

```bash
# 모든 Jest 테스트 실행
npm test

# Watch 모드 (개발 중)
npm run test:watch

# 커버리지 리포트 생성
npm run test:coverage
```

### E2E Tests

```bash
# 모든 E2E 테스트 실행 (headless)
npm run test:e2e

# UI 모드 (interactive)
npm run test:e2e:ui

# Headed 모드 (브라우저 표시)
npm run test:e2e:headed

# Debug 모드
npm run test:e2e:debug
```

### 모든 테스트 실행

```bash
npm run test:all
```

---

## 📝 테스트 카테고리

### 1. Unit Tests

**위치**: `lib/shopify/__tests__/`

**테스트 대상**:
- ShopifyService 클래스
- 제품 조회 메서드
- 체크아웃 생성/관리
- 메타필드 파싱

**예시**:
```typescript
describe('ShopifyService', () => {
  it('should fetch and transform products', async () => {
    const products = await service.getProducts()
    expect(products).toHaveLength(1)
    expect(products[0].title).toBe('Test Product')
  })
})
```

### 2. Integration Tests

**위치**: `__tests__/integration/`

**테스트 대상**:
- 전체 구매 플로우
- 장바구니 관리
- AR 제품 처리
- 에러 핸들링

**예시**:
```typescript
describe('Purchase Flow Integration', () => {
  it('should allow user to browse, add to cart, and checkout', async () => {
    const products = await getProducts()
    const checkout = await createCheckout([...])
    expect(checkout.webUrl).toBeDefined()
  })
})
```

### 3. E2E Tests

**위치**: `e2e/`

**테스트 파일**:

#### `product-browsing.spec.ts`
- 제품 목록 표시
- 필터 및 정렬
- 제품 상세 페이지 이동
- 모바일 반응형

#### `cart-checkout.spec.ts`
- 장바구니 추가/제거
- 수량 조절
- 체크아웃 플로우
- 주문 완료/취소 페이지

#### `ar-experience.spec.ts`
- AR 뷰어 표시
- AR 액세스 검증
- 주문 내역 페이지
- AR 토큰 플로우

---

## 🎯 테스트 커버리지

### 현재 커버리지 목표

| 카테고리 | 목표 | 현재 |
|----------|------|------|
| Branches | 70%+ | TBD |
| Functions | 70%+ | TBD |
| Lines | 70%+ | TBD |
| Statements | 70%+ | TBD |

### 커버리지 확인

```bash
npm run test:coverage
```

커버리지 리포트는 `coverage/` 디렉토리에 생성됩니다:
- HTML 리포트: `coverage/lcov-report/index.html`
- JSON 리포트: `coverage/coverage-final.json`

---

## 🔧 테스트 설정

### Jest 설정 (`jest.config.js`)

```javascript
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
}
```

### Playwright 설정 (`playwright.config.ts`)

```typescript
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium' },
    { name: 'firefox' },
    { name: 'webkit' },
    { name: 'Mobile Chrome' },
    { name: 'Mobile Safari' },
  ],
})
```

---

## 🧩 Mock 설정

### Jest Setup (`jest.setup.js`)

자동으로 Mock되는 항목:
- `next/navigation` (useRouter, useSearchParams)
- `next/image`
- `localStorage`
- `window.location`
- `fetch` API

### Shopify Service Mock

```typescript
jest.mock('@/lib/shopify/client', () => ({
  shopifyService: {
    getProducts: jest.fn(),
    createCheckout: jest.fn(),
    // ... other methods
  },
}))
```

---

## 📊 테스트 시나리오

### 핵심 사용자 플로우

#### 1. 제품 검색 및 구매
```
1. 제품 목록 페이지 접속
2. 검색/필터 사용
3. 제품 클릭 → 상세 페이지
4. "바로 구매" 또는 "장바구니에 추가"
5. 장바구니 확인
6. 체크아웃 진행
7. 주문 완료
```

#### 2. AR 체험 플로우
```
1. AR 가능 제품 구매
2. 주문 내역 페이지 접속
3. 이메일 입력
4. "AR 체험" 버튼 클릭
5. AR 뷰어 팝업
6. 3D 모델 조작
7. AR 모드 실행 (모바일)
```

#### 3. 장바구니 관리
```
1. 여러 제품 장바구니 추가
2. 수량 조절
3. 제품 삭제
4. 가격 확인
5. 결제 진행
```

---

## 🐛 테스트 디버깅

### Jest 디버깅

```bash
# 특정 테스트 파일만 실행
npm test -- client.test.ts

# 특정 테스트 케이스만 실행
npm test -- -t "should fetch and transform products"

# Watch 모드로 디버깅
npm run test:watch
```

### Playwright 디버깅

```bash
# Debug 모드 (step-by-step)
npm run test:e2e:debug

# Headed 모드 (브라우저 보기)
npm run test:e2e:headed

# 특정 테스트만 실행
npx playwright test e2e/product-browsing.spec.ts

# 특정 브라우저만 테스트
npx playwright test --project=chromium
```

### Playwright Trace Viewer

실패한 테스트의 trace 확인:

```bash
npx playwright show-trace test-results/[test-name]/trace.zip
```

---

## 📸 스크린샷 및 비디오

### 자동 캡처

Playwright는 자동으로 다음을 캡처합니다:
- **스크린샷**: 실패한 테스트만
- **비디오**: 실패한 테스트만
- **Trace**: 첫 번째 재시도 시

### 위치

```
test-results/
├── [test-name]/
│   ├── test-failed-1.png
│   ├── video.webm
│   └── trace.zip
```

---

## 🔄 CI/CD 통합

### GitHub Actions 예시

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Install Playwright
        run: npm run playwright:install

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## 📋 테스트 체크리스트

### 배포 전 확인사항

- [ ] 모든 Unit Tests 통과
- [ ] 모든 Integration Tests 통과
- [ ] 모든 E2E Tests 통과 (주요 브라우저)
- [ ] 코드 커버리지 70% 이상
- [ ] 모바일 반응형 테스트 통과
- [ ] 에러 시나리오 테스트 통과
- [ ] AR 플로우 테스트 통과

---

## 🛠️ 테스트 작성 가이드

### Unit Test 예시

```typescript
import { ShopifyService } from '../client'

describe('ShopifyService', () => {
  let service: ShopifyService

  beforeEach(() => {
    service = new ShopifyService()
  })

  it('should handle errors gracefully', async () => {
    mockClient.product.fetchAll.mockRejectedValue(new Error('API Error'))
    await expect(service.getProducts()).rejects.toThrow('API Error')
  })
})
```

### E2E Test 예시

```typescript
import { test, expect } from '@playwright/test'

test('should display product listing', async ({ page }) => {
  await page.goto('/products/shopify')
  await expect(page.getByRole('heading', { name: 'NERD 제품' })).toBeVisible()
})
```

---

## 🚨 알려진 제한사항

### 테스트 환경에서 작동하지 않는 기능

1. **실제 Shopify API 호출**
   - Mock 데이터 사용 필요
   - Integration 테스트는 실제 API 없이 로직만 검증

2. **실제 Shopify Checkout**
   - E2E 테스트에서 Shopify로 리다이렉트되는 부분은 검증 불가
   - Checkout 생성까지만 테스트

3. **AR 뷰어 3D 렌더링**
   - model-viewer 라이브러리는 실제 렌더링 검증 불가
   - DOM 구조와 이벤트만 테스트

4. **Custom Shopify App API**
   - Backend가 실행 중이어야 통합 테스트 가능
   - Mock 데이터로 Frontend 로직만 검증

---

## 📚 추가 리소스

- [Jest 공식 문서](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright 공식 문서](https://playwright.dev/)
- [Next.js Testing 가이드](https://nextjs.org/docs/testing)

---

## 🤝 기여

테스트 추가 시:
1. 적절한 카테고리 선택 (Unit/Integration/E2E)
2. 명확한 테스트 설명 작성
3. Edge case 포함
4. 커버리지 확인

---

**마지막 업데이트**: 2025-10-11
**테스트 프레임워크**: Jest 29.7.0, Playwright 1.40.0
**커버리지 목표**: 70%+
