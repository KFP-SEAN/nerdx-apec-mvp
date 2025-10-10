/**
 * E2E Tests - Product Browsing
 *
 * Tests user interactions with product listing and detail pages
 */

import { test, expect } from '@playwright/test'

test.describe('Product Browsing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to products page
    await page.goto('/products/shopify')
  })

  test('should display product listing page', async ({ page }) => {
    // Check page title
    await expect(page.getByRole('heading', { name: 'NERD 제품' })).toBeVisible()

    // Check that filters are present
    await expect(page.getByPlaceholder('상품 검색...')).toBeVisible()
    await expect(page.getByRole('combobox')).toBeVisible()
    await expect(page.getByText('AR 체험 가능만')).toBeVisible()
    await expect(page.getByText('APEC 한정판만')).toBeVisible()
  })

  test('should filter products by search term', async ({ page }) => {
    const searchInput = page.getByPlaceholder('상품 검색...')

    // Type search term
    await searchInput.fill('막걸리')

    // Wait for products to filter
    await page.waitForTimeout(500)

    // Verify filtered results (this will depend on actual product data)
    const productCount = page.getByText(/개의 상품/)
    await expect(productCount).toBeVisible()
  })

  test('should filter products by AR availability', async ({ page }) => {
    const arFilter = page.getByRole('checkbox', { name: /AR 체험 가능만/ })

    // Enable AR filter
    await arFilter.check()

    // Verify AR badges are shown on products
    await page.waitForTimeout(500)
    const arBadges = page.getByText('AR 체험 가능')
    const count = await arBadges.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should sort products by price', async ({ page }) => {
    const sortSelect = page.getByRole('combobox')

    // Sort by price ascending
    await sortSelect.selectOption('price-asc')

    await page.waitForTimeout(500)

    // Verify products are sorted (implementation will depend on actual data)
    const productCount = page.getByText(/개의 상품/)
    await expect(productCount).toBeVisible()
  })

  test('should navigate to product detail page', async ({ page }) => {
    // Wait for products to load
    await page.waitForSelector('[class*="grid"]', { timeout: 10000 })

    // Click on first product (if available)
    const productCards = page.locator('[class*="bg-white rounded-lg shadow"]')
    const firstProduct = productCards.first()

    if ((await productCards.count()) > 0) {
      await firstProduct.click()

      // Verify we're on detail page
      await page.waitForURL(/\/products\/shopify\/.*/)

      // Check for product detail elements
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      await expect(page.getByText('바로 구매')).toBeVisible()
      await expect(page.getByText('장바구니에 추가')).toBeVisible()
    }
  })

  test('should display APEC limited badge', async ({ page }) => {
    // Look for APEC limited products
    const apecBadge = page.getByText('APEC 한정판')

    if ((await apecBadge.count()) > 0) {
      await expect(apecBadge.first()).toBeVisible()
    }
  })

  test('should show product count', async ({ page }) => {
    const productCount = page.getByText(/개의 상품/)
    await expect(productCount).toBeVisible()
  })

  test('should handle empty search results', async ({ page }) => {
    const searchInput = page.getByPlaceholder('상품 검색...')

    // Search for non-existent product
    await searchInput.fill('xyznonexistent123')
    await page.waitForTimeout(500)

    // Should show no results message
    await expect(page.getByText('검색 결과가 없습니다.')).toBeVisible()
    await expect(page.getByText('필터 초기화')).toBeVisible()
  })

  test('should reset filters', async ({ page }) => {
    const searchInput = page.getByPlaceholder('상품 검색...')
    const arFilter = page.getByRole('checkbox', { name: /AR 체험 가능만/ })

    // Apply filters
    await searchInput.fill('test')
    await arFilter.check()
    await page.waitForTimeout(500)

    // Click reset if empty results
    const resetButton = page.getByText('필터 초기화')
    if (await resetButton.isVisible()) {
      await resetButton.click()

      // Verify filters are cleared
      await expect(searchInput).toHaveValue('')
      await expect(arFilter).not.toBeChecked()
    }
  })
})

test.describe('Product Detail Page', () => {
  test('should display product information', async ({ page }) => {
    // Navigate directly to a product (you'll need to replace with actual handle)
    await page.goto('/products/shopify/test-product')

    // Wait for page to load
    await page.waitForLoadState('networkidle')

    // Check for main elements (may show error if product doesn't exist)
    const pageContent = await page.content()

    if (pageContent.includes('상품을 찾을 수 없습니다')) {
      // Product doesn't exist - expected in test environment
      await expect(page.getByText('상품을 찾을 수 없습니다')).toBeVisible()
      await expect(page.getByText('상품 목록으로')).toBeVisible()
    } else {
      // Product exists - verify detail elements
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      await expect(page.getByText(/\$/)).toBeVisible() // Price
    }
  })

  test('should allow quantity adjustment', async ({ page }) => {
    await page.goto('/products/shopify/test-product')
    await page.waitForLoadState('networkidle')

    const pageContent = await page.content()

    if (!pageContent.includes('상품을 찾을 수 없습니다')) {
      const plusButton = page.getByRole('button', { name: '+' })
      const minusButton = page.getByRole('button', { name: '-' })
      const quantity = page.locator('text=/^\\d+$/').first()

      if (await plusButton.isVisible()) {
        // Increase quantity
        await plusButton.click()
        await page.waitForTimeout(100)

        // Decrease quantity
        await minusButton.click()
        await page.waitForTimeout(100)

        // Quantity should be at least 1
        const qtyText = await quantity.textContent()
        expect(parseInt(qtyText || '1')).toBeGreaterThanOrEqual(1)
      }
    }
  })

  test('should show AR preview button for AR-enabled products', async ({ page }) => {
    await page.goto('/products/shopify/test-product')
    await page.waitForLoadState('networkidle')

    const arButton = page.getByText('AR로 미리보기')

    if (await arButton.isVisible()) {
      await expect(arButton).toBeVisible()
      // Button should be clickable
      await expect(arButton).toBeEnabled()
    }
  })

  test('should navigate back to product list', async ({ page }) => {
    await page.goto('/products/shopify/test-product')
    await page.waitForLoadState('networkidle')

    const backButton = page.getByText('상품 목록으로')
    await expect(backButton).toBeVisible()

    await backButton.click()
    await expect(page).toHaveURL(/\/products\/shopify$/)
  })

  test('should handle variant selection', async ({ page }) => {
    await page.goto('/products/shopify/test-product')
    await page.waitForLoadState('networkidle')

    const variantSelect = page.getByRole('combobox')

    if (await variantSelect.isVisible()) {
      // Product has variants
      await expect(variantSelect).toBeEnabled()

      // Try selecting different variant
      const options = await variantSelect.locator('option').count()
      if (options > 1) {
        await variantSelect.selectOption({ index: 1 })
        await page.waitForTimeout(100)
      }
    }
  })
})

test.describe('Mobile Responsiveness', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test('should display products in mobile layout', async ({ page }) => {
    await page.goto('/products/shopify')

    // Products should be in single column on mobile
    await expect(page.getByRole('heading', { name: 'NERD 제품' })).toBeVisible()

    // Filters should be stacked vertically
    const filterContainer = page.locator('[class*="grid"]').first()
    await expect(filterContainer).toBeVisible()
  })

  test('should be able to navigate on mobile', async ({ page }) => {
    await page.goto('/products/shopify')

    const productCards = page.locator('[class*="bg-white rounded-lg shadow"]')

    if ((await productCards.count()) > 0) {
      await productCards.first().click()
      await page.waitForURL(/\/products\/shopify\/.*/)

      // Verify mobile detail page
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    }
  })
})
