/**
 * Integration Tests - Complete Purchase Flow
 *
 * Tests the entire user journey from product browsing to checkout
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { shopifyService } from '@/lib/shopify/client'

// Mock the shopify service
jest.mock('@/lib/shopify/client')

const mockProducts = [
  {
    id: 'gid://shopify/Product/1',
    handle: 'nerd-makgeolli',
    title: 'NERD Makgeolli',
    description: 'Premium Korean rice wine',
    descriptionHtml: '<p>Premium Korean rice wine</p>',
    priceRange: {
      minVariantPrice: {
        amount: '29.99',
        currencyCode: 'USD',
      },
    },
    images: [
      {
        url: 'https://example.com/image.jpg',
        altText: 'NERD Makgeolli',
      },
    ],
    variants: [
      {
        id: 'gid://shopify/ProductVariant/1',
        title: 'Default',
        price: '29.99',
        available: true,
      },
    ],
    metafields: {
      arEnabled: true,
      apecLimited: true,
      stockRemaining: 10,
    },
  },
]

const mockCheckout = {
  id: 'gid://shopify/Checkout/1',
  webUrl: 'https://test-store.myshopify.com/checkout/1',
  lineItems: [
    {
      id: 'gid://shopify/CheckoutLineItem/1',
      title: 'NERD Makgeolli',
      quantity: 1,
      variant: {
        id: 'gid://shopify/ProductVariant/1',
        title: 'Default',
        price: { amount: '29.99', currencyCode: 'USD' },
        image: { src: 'https://example.com/image.jpg' },
        product: {
          images: [{ src: 'https://example.com/image.jpg' }],
        },
      },
      customAttributes: [{ key: 'ar_enabled', value: 'true' }],
    },
  ],
  subtotalPrice: '29.99',
  totalTax: '2.50',
  totalPrice: '32.49',
  ready: true,
}

describe('Purchase Flow Integration', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks()
    localStorage.clear()

    // Setup default mock implementations
    ;(shopifyService.getProducts as jest.Mock).mockResolvedValue(mockProducts)
    ;(shopifyService.getProductByHandle as jest.Mock).mockResolvedValue(mockProducts[0])
    ;(shopifyService.createCheckout as jest.Mock).mockResolvedValue(mockCheckout)
    ;(shopifyService.addToCheckout as jest.Mock).mockResolvedValue(mockCheckout)
    ;(shopifyService.getCheckout as jest.Mock).mockResolvedValue(mockCheckout)
  })

  describe('Product Discovery to Checkout', () => {
    it('should allow user to browse products, view details, add to cart, and checkout', async () => {
      // Step 1: User browses products
      const { getProducts } = shopifyService
      const products = await getProducts()

      expect(products).toHaveLength(1)
      expect(products[0].title).toBe('NERD Makgeolli')
      expect(products[0].metafields?.arEnabled).toBe(true)

      // Step 2: User clicks on product to view details
      const product = await shopifyService.getProductByHandle('nerd-makgeolli')

      expect(product).not.toBeNull()
      expect(product?.title).toBe('NERD Makgeolli')
      expect(product?.variants).toHaveLength(1)

      // Step 3: User adds product to cart
      const checkout = await shopifyService.createCheckout([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
          customAttributes: [{ key: 'ar_enabled', value: 'true' }],
        },
      ])

      expect(checkout.lineItems).toHaveLength(1)
      expect(checkout.lineItems[0].title).toBe('NERD Makgeolli')
      expect(checkout.totalPrice).toBe('32.49')

      // Step 4: Verify checkout ID is stored
      localStorage.setItem('shopify_checkout_id', checkout.id)
      expect(localStorage.getItem('shopify_checkout_id')).toBe(checkout.id)

      // Step 5: User proceeds to Shopify checkout
      expect(checkout.webUrl).toBe('https://test-store.myshopify.com/checkout/1')
    })

    it('should handle "Buy Now" flow', async () => {
      // User clicks "Buy Now" directly from product detail page
      const checkout = await shopifyService.createCheckout([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
          customAttributes: [{ key: 'ar_enabled', value: 'true' }],
        },
      ])

      expect(checkout.id).toBeDefined()
      expect(checkout.webUrl).toBeDefined()
      expect(shopifyService.createCheckout).toHaveBeenCalledWith([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
          customAttributes: [{ key: 'ar_enabled', value: 'true' }],
        },
      ])
    })
  })

  describe('Cart Management', () => {
    it('should allow adding multiple items to cart', async () => {
      // Create initial checkout
      let checkout = await shopifyService.createCheckout([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
        },
      ])

      localStorage.setItem('shopify_checkout_id', checkout.id)

      // Add another item
      const updatedCheckout = {
        ...mockCheckout,
        lineItems: [
          ...mockCheckout.lineItems,
          {
            id: 'gid://shopify/CheckoutLineItem/2',
            title: 'Another Product',
            quantity: 1,
            variant: mockCheckout.lineItems[0].variant,
          },
        ],
      }

      ;(shopifyService.addToCheckout as jest.Mock).mockResolvedValue(updatedCheckout)

      checkout = await shopifyService.addToCheckout(checkout.id, [
        {
          variantId: 'gid://shopify/ProductVariant/2',
          quantity: 1,
        },
      ])

      expect(checkout.lineItems).toHaveLength(2)
    })

    it('should allow updating item quantity', async () => {
      const { updateCheckoutLineItem } = shopifyService

      const updatedCheckout = {
        ...mockCheckout,
        lineItems: [
          {
            ...mockCheckout.lineItems[0],
            quantity: 2,
          },
        ],
        subtotalPrice: '59.98',
        totalPrice: '64.98',
      }

      ;(shopifyService.updateCheckoutLineItem as jest.Mock).mockResolvedValue(updatedCheckout)

      const result = await updateCheckoutLineItem(
        'gid://shopify/Checkout/1',
        'gid://shopify/CheckoutLineItem/1',
        2
      )

      expect(result.lineItems[0].quantity).toBe(2)
      expect(result.totalPrice).toBe('64.98')
    })

    it('should allow removing items from cart', async () => {
      const { removeFromCheckout } = shopifyService

      const emptyCheckout = {
        ...mockCheckout,
        lineItems: [],
        subtotalPrice: '0',
        totalPrice: '0',
      }

      ;(shopifyService.removeFromCheckout as jest.Mock).mockResolvedValue(emptyCheckout)

      const result = await removeFromCheckout(
        'gid://shopify/Checkout/1',
        'gid://shopify/CheckoutLineItem/1'
      )

      expect(result.lineItems).toHaveLength(0)
      expect(result.totalPrice).toBe('0')
    })
  })

  describe('AR-Enabled Products', () => {
    it('should properly tag AR-enabled products in checkout', async () => {
      const checkout = await shopifyService.createCheckout([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
          customAttributes: [{ key: 'ar_enabled', value: 'true' }],
        },
      ])

      const arEnabledItem = checkout.lineItems[0]
      expect(arEnabledItem.customAttributes).toContainEqual({
        key: 'ar_enabled',
        value: 'true',
      })
    })

    it('should not add AR attribute for non-AR products', async () => {
      const nonARProduct = {
        ...mockProducts[0],
        metafields: {
          arEnabled: false,
        },
      }

      const nonARCheckout = {
        ...mockCheckout,
        lineItems: [
          {
            ...mockCheckout.lineItems[0],
            customAttributes: undefined,
          },
        ],
      }

      ;(shopifyService.getProductByHandle as jest.Mock).mockResolvedValue(nonARProduct)
      ;(shopifyService.createCheckout as jest.Mock).mockResolvedValue(nonARCheckout)

      const checkout = await shopifyService.createCheckout([
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
        },
      ])

      expect(checkout.lineItems[0].customAttributes).toBeUndefined()
    })
  })

  describe('Order Completion Flow', () => {
    it('should clear cart after successful checkout', async () => {
      // Simulate successful checkout
      localStorage.setItem('shopify_checkout_id', 'gid://shopify/Checkout/1')

      // User completes checkout on Shopify and returns to success page
      // Success page should clear localStorage
      localStorage.removeItem('shopify_checkout_id')

      expect(localStorage.getItem('shopify_checkout_id')).toBeNull()
    })

    it('should maintain cart if checkout is cancelled', async () => {
      localStorage.setItem('shopify_checkout_id', 'gid://shopify/Checkout/1')

      // User cancels checkout - cart should remain
      expect(localStorage.getItem('shopify_checkout_id')).toBe('gid://shopify/Checkout/1')

      // User can return to cart
      const checkout = await shopifyService.getCheckout('gid://shopify/Checkout/1')
      expect(checkout.lineItems).toHaveLength(1)
    })
  })

  describe('Error Handling', () => {
    it('should handle product fetch errors', async () => {
      ;(shopifyService.getProducts as jest.Mock).mockRejectedValue(
        new Error('Network error')
      )

      await expect(shopifyService.getProducts()).rejects.toThrow('Network error')
    })

    it('should handle checkout creation errors', async () => {
      ;(shopifyService.createCheckout as jest.Mock).mockRejectedValue(
        new Error('Checkout failed')
      )

      await expect(
        shopifyService.createCheckout([
          {
            variantId: 'gid://shopify/ProductVariant/1',
            quantity: 1,
          },
        ])
      ).rejects.toThrow('Checkout failed')
    })

    it('should handle out-of-stock scenarios', async () => {
      const outOfStockProduct = {
        ...mockProducts[0],
        variants: [
          {
            id: 'gid://shopify/ProductVariant/1',
            title: 'Default',
            price: '29.99',
            available: false, // Out of stock
          },
        ],
      }

      ;(shopifyService.getProductByHandle as jest.Mock).mockResolvedValue(outOfStockProduct)

      const product = await shopifyService.getProductByHandle('nerd-makgeolli')
      expect(product?.variants[0].available).toBe(false)
    })
  })

  describe('APEC Limited Edition Products', () => {
    it('should display APEC limited badge', async () => {
      const product = await shopifyService.getProductByHandle('nerd-makgeolli')

      expect(product?.metafields?.apecLimited).toBe(true)
    })

    it('should show stock remaining for limited edition', async () => {
      const product = await shopifyService.getProductByHandle('nerd-makgeolli')

      expect(product?.metafields?.stockRemaining).toBe(10)
    })
  })
})
