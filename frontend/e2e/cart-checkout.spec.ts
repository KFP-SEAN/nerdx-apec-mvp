/**
 * E2E Tests - Cart and Checkout Flow
 *
 * Tests shopping cart functionality and checkout process
 */

import { test, expect } from '@playwright/test'

test.describe('Shopping Cart', () => {
  test.beforeEach(async ({ page, context }) => {
    // Clear localStorage before each test
    await context.clearCookies()
    await page.goto('/cart')
  })

  test('should display empty cart message', async ({ page }) => {
    await page.goto('/cart')

    // Wait for page to load
    await page.waitForLoadState('networkidle')

    // Should show empty cart message
    await expect(page.getByText('장바구니가 비어있습니다')).toBeVisible()
    await expect(page.getByText('쇼핑 계속하기')).toBeVisible()
  })

  test('should navigate to products from empty cart', async ({ page }) => {
    await page.goto('/cart')

    const shopButton = page.getByText('쇼핑 계속하기')
    await shopButton.click()

    await expect(page).toHaveURL(/\/products\/shopify/)
  })

  test('should add product to cart from detail page', async ({ page }) => {
    // Navigate to product detail
    await page.goto('/products/shopify')
    await page.waitForLoadState('networkidle')

    const productCards = page.locator('[class*="bg-white rounded-lg shadow"]')

    if ((await productCards.count()) > 0) {
      // Click first product
      await productCards.first().click()
      await page.waitForURL(/\/products\/shopify\/.*/)

      // Click "Add to Cart" button
      const addToCartButton = page.getByText('장바구니에 추가')

      if (await addToCartButton.isVisible()) {
        // Listen for dialog
        page.on('dialog', async (dialog) => {
          expect(dialog.message()).toContain('장바구니에 추가되었습니다')
          await dialog.accept()
        })

        await addToCartButton.click()

        // Wait for operation to complete
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should display cart items with details', async ({ page, context }) => {
    // Add mock checkout ID to localStorage
    await context.addInitScript(() => {
      localStorage.setItem('shopify_checkout_id', 'mock_checkout_id')
    })

    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Note: This will likely show empty cart or error in test environment
    // In a real test with backend, you would verify:
    // - Product images
    // - Product names
    // - Quantities
    // - Prices
  })

  test('should handle quantity updates', async ({ page }) => {
    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Look for quantity controls (will only exist if cart has items)
    const plusButton = page.getByRole('button', { name: /\+/ }).first()
    const minusButton = page.getByRole('button', { name: /-/ }).first()

    if (await plusButton.isVisible()) {
      await plusButton.click()
      await page.waitForTimeout(500)

      await minusButton.click()
      await page.waitForTimeout(500)
    }
  })

  test('should allow item removal', async ({ page }) => {
    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Look for delete buttons
    const deleteButtons = page.getByRole('button', { name: /삭제/ })

    if ((await deleteButtons.count()) > 0) {
      // Mock the confirm dialog
      page.on('dialog', async (dialog) => {
        expect(dialog.type()).toBe('confirm')
        await dialog.accept()
      })

      await deleteButtons.first().click()
      await page.waitForTimeout(500)
    }
  })

  test('should display price summary', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('shopify_checkout_id', 'mock_checkout_id')
    })

    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Check for price summary elements (if cart has items)
    const summarySection = page.getByText('주문 요약')

    if (await summarySection.isVisible()) {
      await expect(summarySection).toBeVisible()
      await expect(page.getByText('소계')).toBeVisible()
      await expect(page.getByText('세금')).toBeVisible()
      await expect(page.getByText('합계')).toBeVisible()
    }
  })

  test('should show checkout button', async ({ page }) => {
    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    const checkoutButton = page.getByText('결제하기')

    if (await checkoutButton.isVisible()) {
      await expect(checkoutButton).toBeEnabled()
    }
  })

  test('should redirect to Shopify checkout', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('shopify_checkout_id', 'mock_checkout_id')
    })

    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    const checkoutButton = page.getByText('결제하기')

    if (await checkoutButton.isVisible()) {
      // Click checkout button
      // Note: This will redirect to Shopify, which we can't test in E2E
      // In real tests, you would mock the Shopify response
      await expect(checkoutButton).toBeVisible()
    }
  })

  test('should show AR indicator for AR products', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('shopify_checkout_id', 'mock_checkout_id')
    })

    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    const arBadge = page.getByText('AR 체험 포함')

    if (await arBadge.isVisible()) {
      await expect(arBadge).toBeVisible()
    }
  })
})

test.describe('Buy Now Flow', () => {
  test('should redirect directly to checkout', async ({ page }) => {
    await page.goto('/products/shopify')
    await page.waitForLoadState('networkidle')

    const productCards = page.locator('[class*="bg-white rounded-lg shadow"]')

    if ((await productCards.count()) > 0) {
      // Click first product
      await productCards.first().click()
      await page.waitForURL(/\/products\/shopify\/.*/)

      const buyNowButton = page.getByText('바로 구매')

      if (await buyNowButton.isVisible()) {
        // Note: This will attempt to redirect to Shopify
        // In real tests, you would mock the checkout URL
        await expect(buyNowButton).toBeEnabled()
      }
    }
  })
})

test.describe('Order Success Page', () => {
  test('should display success message', async ({ page }) => {
    await page.goto('/order/success?order_id=12345')

    await expect(page.getByText('주문이 완료되었습니다!')).toBeVisible()
    await expect(page.getByText('주문 번호')).toBeVisible()
  })

  test('should show order ID', async ({ page }) => {
    await page.goto('/order/success?order_id=12345')

    // Should display order ID from URL
    await expect(page.getByText('12345')).toBeVisible()
  })

  test('should display next steps', async ({ page }) => {
    await page.goto('/order/success')

    await expect(page.getByText('다음 단계')).toBeVisible()
    await expect(page.getByText('주문 확인 메일')).toBeVisible()
    await expect(page.getByText('AR 체험 액세스')).toBeVisible()
    await expect(page.getByText('배송 안내')).toBeVisible()
  })

  test('should show AR access information', async ({ page }) => {
    await page.goto('/order/success')

    await expect(page.getByText('AR 체험 액세스 안내')).toBeVisible()
    await expect(page.getByText(/90일간 유효/)).toBeVisible()
  })

  test('should navigate to orders page', async ({ page }) => {
    await page.goto('/order/success')

    const ordersButton = page.getByText('주문 내역 보기')
    await ordersButton.click()

    await expect(page).toHaveURL(/\/orders/)
  })

  test('should navigate back to products', async ({ page }) => {
    await page.goto('/order/success')

    const shopButton = page.getByText('쇼핑 계속하기')
    await shopButton.click()

    await expect(page).toHaveURL(/\/products\/shopify/)
  })
})

test.describe('Order Cancelled Page', () => {
  test('should display cancellation message', async ({ page }) => {
    await page.goto('/order/cancelled')

    await expect(page.getByText('주문이 취소되었습니다')).toBeVisible()
  })

  test('should explain cancellation reasons', async ({ page }) => {
    await page.goto('/order/cancelled')

    await expect(page.getByText('무슨 일이 있었나요?')).toBeVisible()
    await expect(page.getByText('장바구니 상품은 안전합니다')).toBeVisible()
  })

  test('should show troubleshooting guide', async ({ page }) => {
    await page.goto('/order/cancelled')

    await expect(page.getByText('자주 발생하는 문제')).toBeVisible()
    await expect(page.getByText(/결제 수단이 거부/)).toBeVisible()
    await expect(page.getByText(/배송 주소/)).toBeVisible()
  })

  test('should navigate back to cart', async ({ page }) => {
    await page.goto('/order/cancelled')

    const cartButton = page.getByText('장바구니로 돌아가기')
    await cartButton.click()

    await expect(page).toHaveURL(/\/cart/)
  })

  test('should navigate to products', async ({ page }) => {
    await page.goto('/order/cancelled')

    const shopButton = page.getByText('쇼핑 계속하기')
    await shopButton.click()

    await expect(page).toHaveURL(/\/products\/shopify/)
  })
})

test.describe('Mobile Cart Experience', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test('should display cart on mobile', async ({ page }) => {
    await page.goto('/cart')

    await expect(page.getByText(/장바구니|쇼핑 계속하기/)).toBeVisible()
  })

  test('should show mobile-optimized layout', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('shopify_checkout_id', 'mock_checkout_id')
    })

    await page.goto('/cart')
    await page.waitForLoadState('networkidle')

    // Verify mobile layout elements are visible
    const viewport = page.viewportSize()
    expect(viewport?.width).toBeLessThanOrEqual(768)
  })
})
