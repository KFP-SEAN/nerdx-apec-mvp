# 🛒 Shopify Development Store 설정 가이드

## 📋 개요

NERDX APEC MVP를 위한 Shopify Development Store 설정 및 구성 가이드입니다.

**소요 시간**: 약 2-3시간
**필요 사항**: Shopify Partners 계정

---

## 1️⃣ Shopify Partners 계정 생성

### Step 1: Partners 계정 등록

1. [Shopify Partners](https://partners.shopify.com/) 접속
2. "Join now" 클릭
3. 정보 입력:
   - Email
   - Password
   - Country: South Korea
   - Business Type: Development Store
4. 이메일 인증 완료

---

## 2️⃣ Development Store 생성

### Step 1: 새 스토어 만들기

1. Partners Dashboard → **Stores** 클릭
2. **Add store** → **Development store** 선택
3. 스토어 정보 입력:
   ```
   Store name: NERDX APEC MVP
   Store URL: nerdx-apec-mvp.myshopify.com
   Purpose: Test an app or theme
   Store address: (한국 주소 입력)
   ```
4. **Create development store** 클릭

### Step 2: 스토어 접속

1. Store가 생성되면 **Go to store** 클릭
2. Admin 패널 접속
3. 비밀번호 설정 (처음 접속 시)

---

## 3️⃣ 제품 데이터 추가

### 제품 1: NERD Makgeolli (AR 가능)

**Admin → Products → Add product**

```yaml
Title: NERD Premium Makgeolli
Description: |
  프리미엄 한국 전통 막걸리

  부드럽고 달콤한 맛과 향긋한 쌀 향이 특징인
  전통 방식으로 빚은 프리미엄 막걸리입니다.

  - 알코올: 6%
  - 용량: 750ml
  - 원산지: 대한민국 경주

Product type: Beverage
Vendor: NERD
Collections: Featured Products, APEC Limited

Pricing:
  Price: $29.99
  Compare at price: $39.99

Inventory:
  SKU: NERD-MAK-001
  Barcode: 8809012345678
  Track quantity: Yes
  Quantity: 50

Shipping:
  Weight: 1.2 kg
  Requires shipping: Yes
```

**이미지**: 막걸리 병 이미지 업로드

**Metafields 추가**:
1. **Products** → 제품 클릭 → 하단의 **Metafields** 클릭
2. **Add definition** 클릭
3. 다음 Metafields 추가:

```yaml
Metafield 1:
  Namespace: custom
  Key: ar_enabled
  Type: Boolean
  Value: true

Metafield 2:
  Namespace: custom
  Key: ar_asset_url
  Type: Single line text
  Value: https://cdn.shopify.com/s/files/example/nerd-makgeolli.glb

Metafield 3:
  Namespace: custom
  Key: apec_limited
  Type: Boolean
  Value: true

Metafield 4:
  Namespace: custom
  Key: stock_remaining
  Type: Integer
  Value: 50
```

### 제품 2: NERD Soju (Non-AR)

```yaml
Title: NERD Premium Soju
Description: |
  프리미엄 한국 소주

  깔끔하고 부드러운 맛이 특징인 프리미엄 소주입니다.

  - 알코올: 16.9%
  - 용량: 360ml
  - 원산지: 대한민국 경주

Price: $15.99
SKU: NERD-SOJU-001
Quantity: 100

Metafields:
  ar_enabled: false
  apec_limited: false
```

### 제품 3: NERD Cheongju (AR 가능, APEC 한정)

```yaml
Title: NERDX APEC Limited Cheongju
Description: |
  APEC 2024 한정판 청주

  APEC 정상회의를 기념하여 특별 제작된 한정판 청주입니다.

  - 알코올: 13%
  - 용량: 500ml
  - 원산지: 대한민국 경주
  - 한정 수량: 100병

Price: $49.99
SKU: NERD-CHEONG-APEC
Quantity: 20

Metafields:
  ar_enabled: true
  ar_asset_url: https://cdn.shopify.com/s/files/example/nerd-cheongju.glb
  apec_limited: true
  stock_remaining: 20
```

---

## 4️⃣ Storefront API 설정

### Step 1: Custom App 생성

1. **Admin → Settings → Apps and sales channels**
2. **Develop apps** 클릭
3. **Create an app** 클릭
4. App name: `NERDX Frontend`
5. **Create app** 클릭

### Step 2: Storefront API 권한 설정

1. **Configuration** 탭 클릭
2. **Storefront API** 섹션 → **Configure** 클릭
3. 다음 권한 활성화:
   ```
   ✅ unauthenticated_read_product_listings
   ✅ unauthenticated_read_product_inventory
   ✅ unauthenticated_read_product_tags
   ✅ unauthenticated_write_checkouts
   ✅ unauthenticated_read_checkouts
   ```
4. **Save** 클릭

### Step 3: Access Token 생성

1. **API credentials** 탭 클릭
2. **Install app** 클릭 (확인)
3. **Storefront API access token** 복사
   ```
   형식: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. 안전한 곳에 저장

### Step 4: 환경 변수 설정

`frontend/.env.local` 파일 생성:

```env
NEXT_PUBLIC_SHOPIFY_DOMAIN=nerdx-apec-mvp.myshopify.com
NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=shpat_your_token_here
NEXT_PUBLIC_SHOPIFY_APP_URL=http://localhost:3001
```

---

## 5️⃣ Webhook 설정 (Custom App용)

### Step 1: Custom Shopify App 생성

1. **Admin → Settings → Apps and sales channels**
2. **Develop apps** → **Create an app**
3. App name: `NERDX Custom App`

### Step 2: Admin API 권한

1. **Configuration** → **Admin API** → **Configure**
2. 다음 권한 활성화:
   ```
   ✅ read_orders
   ✅ write_orders
   ✅ read_products
   ✅ read_customers
   ```
3. **Save** 클릭

### Step 3: Admin API Access Token

1. **API credentials** → **Install app**
2. **Admin API access token** 복사
3. Custom App `.env` 파일에 저장:
   ```env
   SHOPIFY_ADMIN_API_TOKEN=shpat_admin_token_here
   ```

### Step 4: Webhook 등록

Custom App이 배포된 후:

1. **Admin → Settings → Notifications**
2. **Webhooks** → **Create webhook**
3. 다음 Webhooks 추가:

**Webhook 1: Order Paid**
```
Event: orders/paid
URL: https://your-custom-app.com/webhooks/orders/paid
Format: JSON
API version: 2024-01
```

**Webhook 2: Order Cancelled**
```
Event: orders/cancelled
URL: https://your-custom-app.com/webhooks/orders/cancelled
Format: JSON
API version: 2024-01
```

**Webhook 3: Refund Created**
```
Event: refunds/create
URL: https://your-custom-app.com/webhooks/refunds/create
Format: JSON
API version: 2024-01
```

---

## 6️⃣ 결제 설정

### Development Store 결제

Development Store는 실제 결제를 받을 수 없지만, 테스트용 결제 게이트웨이를 사용할 수 있습니다.

### Step 1: Bogus Gateway 활성화

1. **Admin → Settings → Payments**
2. **Manage** (Payment providers 섹션)
3. **Add payment methods** → **Manual payment methods**
4. **Create custom payment method** 선택
5. Name: `Bogus Gateway (Test)`
6. **Activate** 클릭

### Step 2: 테스트 카드 번호

Bogus Gateway는 다음 카드 번호를 사용:
- **성공**: `1` (아무 1로 시작하는 숫자)
- **실패**: `2` (아무 2로 시작하는 숫자)

예시:
```
카드 번호: 1111 1111 1111 1111
만료일: 12/25
CVV: 123
```

---

## 7️⃣ 스토어 테마 설정

### Step 1: 기본 테마 활성화

1. **Admin → Online Store → Themes**
2. Dawn 테마 사용 (기본)
3. **Customize** 클릭

### Step 2: 헤드리스 모드 설정

**참고**: 우리는 헤드리스 커머스를 사용하므로 Shopify 테마는 체크아웃 페이지에서만 사용됩니다.

1. **Theme settings** → **Checkout**
2. 로고 및 브랜딩 설정
3. **Save** 클릭

---

## 8️⃣ 도메인 설정 (선택사항)

### Development Store 도메인

기본 도메인: `nerdx-apec-mvp.myshopify.com`

### 커스텀 도메인 (Production용)

1. **Admin → Online Store → Domains**
2. **Connect existing domain** 클릭
3. 도메인 입력 (예: `shop.nerdx.com`)
4. DNS 설정 업데이트
5. SSL 인증서 자동 발급

---

## 9️⃣ 테스트

### Frontend 테스트

1. Frontend 실행:
   ```bash
   cd frontend
   npm run dev
   ```

2. 제품 페이지 접속:
   ```
   http://localhost:3000/products/shopify
   ```

3. 확인 사항:
   - ✅ 제품 목록 표시
   - ✅ AR 뱃지 표시
   - ✅ APEC 한정판 뱃지
   - ✅ 재고 표시
   - ✅ 가격 정보

### Checkout 테스트

1. 제품 클릭 → "바로 구매"
2. Shopify Checkout 페이지로 리다이렉트 확인
3. 테스트 카드 정보 입력
4. 주문 완료

### Custom App 테스트

1. Custom App 실행:
   ```bash
   cd shopify-custom-app
   npm run dev
   ```

2. Webhook 테스트:
   - Shopify Admin에서 테스트 주문 생성
   - Custom App 로그 확인
   - Neo4j에서 관계 생성 확인

---

## 🔟 Production 배포 준비

### 체크리스트

- [ ] 모든 제품 데이터 입력 완료
- [ ] Metafields 정의 완료
- [ ] Storefront API 권한 설정
- [ ] Admin API 권한 설정
- [ ] Webhook 등록 완료
- [ ] 결제 게이트웨이 설정
- [ ] Frontend 환경 변수 설정
- [ ] Custom App 환경 변수 설정
- [ ] 테스트 주문 완료
- [ ] AR 액세스 플로우 확인

### Production Store로 전환

Development Store를 Production으로 전환:

1. **Admin → Settings → Plan**
2. **Choose a plan** 클릭
3. 플랜 선택 (Shopify Basic 이상)
4. 결제 정보 입력
5. 활성화

---

## 📚 참고 자료

- [Shopify Storefront API](https://shopify.dev/docs/api/storefront)
- [Shopify Admin API](https://shopify.dev/docs/api/admin)
- [Shopify Webhooks](https://shopify.dev/docs/api/webhooks)
- [Metafields Guide](https://shopify.dev/docs/apps/build/custom-data/metafields)
- [Shopify Buy SDK](https://shopify.github.io/js-buy-sdk/)

---

## 🐛 문제 해결

### 제품이 표시되지 않음

1. Products → Sales channels 확인
2. "Online Store" 채널 활성화 확인
3. Product availability 확인

### API 권한 에러

1. Custom App 권한 재확인
2. Access Token 재생성
3. 환경 변수 업데이트

### Webhook가 작동하지 않음

1. Webhook URL 확인 (https 필수)
2. HMAC 서명 검증 확인
3. Custom App 로그 확인

---

**설정 완료 시간**: 2-3시간
**다음 단계**: Frontend 연동 테스트 및 E2E 테스트

---

*이 가이드를 따라 Shopify Development Store를 완전히 설정하면, NERDX APEC MVP의 전체 기능을 테스트할 수 있습니다.*
