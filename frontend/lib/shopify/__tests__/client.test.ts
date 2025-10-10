/**
 * Unit Tests for Shopify Service Client
 */

import { ShopifyService, ShopifyProduct } from '../client'

// Mock shopify-buy
jest.mock('shopify-buy', () => ({
  buildClient: jest.fn(() => ({
    product: {
      fetchAll: jest.fn(),
      fetchByHandle: jest.fn(),
      fetch: jest.fn(),
    },
    checkout: {
      create: jest.fn(),
      addLineItems: jest.fn(),
      updateEmail: jest.fn(),
      updateLineItems: jest.fn(),
      removeLineItems: jest.fn(),
      fetch: jest.fn(),
    },
  })),
}))

describe('ShopifyService', () => {
  let service: ShopifyService
  let mockClient: any

  beforeEach(() => {
    service = new ShopifyService()
    mockClient = (service as any).client
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('getProducts', () => {
    it('should fetch and transform products', async () => {
      const mockProducts = [
        {
          id: 'gid://shopify/Product/1',
          handle: 'test-product',
          title: 'Test Product',
          description: 'Test Description',
          descriptionHtml: '<p>Test Description</p>',
          variants: [
            {
              id: 'gid://shopify/ProductVariant/1',
              title: 'Default',
              price: { amount: '29.99', currencyCode: 'USD' },
              available: true,
            },
          ],
          images: [
            {
              src: 'https://example.com/image.jpg',
              altText: 'Test Image',
            },
          ],
          metafields: [
            { key: 'ar_enabled', value: 'true' },
            { key: 'apec_limited', value: 'true' },
            { key: 'stock_remaining', value: '10' },
          ],
        },
      ]

      mockClient.product.fetchAll.mockResolvedValue(mockProducts)

      const result = await service.getProducts()

      expect(result).toHaveLength(1)
      expect(result[0]).toMatchObject({
        id: 'gid://shopify/Product/1',
        handle: 'test-product',
        title: 'Test Product',
      })
      expect(result[0].metafields).toMatchObject({
        arenabled: true,
        apeclimited: true,
        stockremaining: 10,
      })
    })

    it('should handle errors gracefully', async () => {
      mockClient.product.fetchAll.mockRejectedValue(new Error('API Error'))

      await expect(service.getProducts()).rejects.toThrow('API Error')
    })
  })

  describe('getProductByHandle', () => {
    it('should fetch product by handle', async () => {
      const mockProduct = {
        id: 'gid://shopify/Product/1',
        handle: 'test-product',
        title: 'Test Product',
        description: 'Test Description',
        descriptionHtml: '<p>Test Description</p>',
        variants: [
          {
            id: 'gid://shopify/ProductVariant/1',
            title: 'Default',
            price: { amount: '29.99', currencyCode: 'USD' },
            available: true,
          },
        ],
        images: [
          {
            src: 'https://example.com/image.jpg',
            altText: 'Test Image',
          },
        ],
      }

      mockClient.product.fetchByHandle.mockResolvedValue(mockProduct)

      const result = await service.getProductByHandle('test-product')

      expect(result).not.toBeNull()
      expect(result?.handle).toBe('test-product')
      expect(mockClient.product.fetchByHandle).toHaveBeenCalledWith('test-product')
    })

    it('should return null for non-existent product', async () => {
      mockClient.product.fetchByHandle.mockResolvedValue(null)

      const result = await service.getProductByHandle('non-existent')

      expect(result).toBeNull()
    })
  })

  describe('createCheckout', () => {
    it('should create checkout with line items', async () => {
      const mockCheckout = {
        id: 'gid://shopify/Checkout/1',
        webUrl: 'https://test-store.myshopify.com/checkout/1',
        subtotalPrice: { amount: '29.99' },
        totalTax: { amount: '2.50' },
        totalPrice: { amount: '32.49' },
        lineItems: [],
        ready: true,
      }

      mockClient.checkout.create.mockResolvedValue({ id: mockCheckout.id })
      mockClient.checkout.addLineItems.mockResolvedValue(mockCheckout)

      const lineItems = [
        {
          variantId: 'gid://shopify/ProductVariant/1',
          quantity: 1,
        },
      ]

      const result = await service.createCheckout(lineItems)

      expect(result.id).toBe(mockCheckout.id)
      expect(result.webUrl).toBe(mockCheckout.webUrl)
      expect(mockClient.checkout.create).toHaveBeenCalled()
      expect(mockClient.checkout.addLineItems).toHaveBeenCalledWith(
        mockCheckout.id,
        lineItems
      )
    })

    it('should create empty checkout when no line items', async () => {
      const mockCheckout = {
        id: 'gid://shopify/Checkout/1',
        webUrl: 'https://test-store.myshopify.com/checkout/1',
        subtotalPrice: { amount: '0' },
        totalTax: { amount: '0' },
        totalPrice: { amount: '0' },
        lineItems: [],
        ready: true,
      }

      mockClient.checkout.create.mockResolvedValue(mockCheckout)

      const result = await service.createCheckout([])

      expect(result.id).toBe(mockCheckout.id)
      expect(mockClient.checkout.addLineItems).not.toHaveBeenCalled()
    })

    it('should update email if provided', async () => {
      const mockCheckout = {
        id: 'gid://shopify/Checkout/1',
        webUrl: 'https://test-store.myshopify.com/checkout/1',
        subtotalPrice: { amount: '0' },
        totalTax: { amount: '0' },
        totalPrice: { amount: '0' },
        lineItems: [],
        ready: true,
      }

      mockClient.checkout.create.mockResolvedValue(mockCheckout)
      mockClient.checkout.updateEmail.mockResolvedValue(mockCheckout)

      await service.createCheckout([], { email: 'test@example.com' })

      expect(mockClient.checkout.updateEmail).toHaveBeenCalledWith(
        mockCheckout.id,
        'test@example.com'
      )
    })
  })

  describe('updateCheckoutLineItem', () => {
    it('should update line item quantity', async () => {
      const mockCheckout = {
        id: 'gid://shopify/Checkout/1',
        webUrl: 'https://test-store.myshopify.com/checkout/1',
        subtotalPrice: { amount: '59.98' },
        totalTax: { amount: '5.00' },
        totalPrice: { amount: '64.98' },
        lineItems: [],
        ready: true,
      }

      mockClient.checkout.updateLineItems.mockResolvedValue(mockCheckout)

      const result = await service.updateCheckoutLineItem(
        'gid://shopify/Checkout/1',
        'gid://shopify/CheckoutLineItem/1',
        2
      )

      expect(result.id).toBe(mockCheckout.id)
      expect(mockClient.checkout.updateLineItems).toHaveBeenCalledWith(
        'gid://shopify/Checkout/1',
        [{ id: 'gid://shopify/CheckoutLineItem/1', quantity: 2 }]
      )
    })
  })

  describe('removeFromCheckout', () => {
    it('should remove line item from checkout', async () => {
      const mockCheckout = {
        id: 'gid://shopify/Checkout/1',
        webUrl: 'https://test-store.myshopify.com/checkout/1',
        subtotalPrice: { amount: '0' },
        totalTax: { amount: '0' },
        totalPrice: { amount: '0' },
        lineItems: [],
        ready: true,
      }

      mockClient.checkout.removeLineItems.mockResolvedValue(mockCheckout)

      const result = await service.removeFromCheckout(
        'gid://shopify/Checkout/1',
        'gid://shopify/CheckoutLineItem/1'
      )

      expect(result.id).toBe(mockCheckout.id)
      expect(mockClient.checkout.removeLineItems).toHaveBeenCalledWith(
        'gid://shopify/Checkout/1',
        ['gid://shopify/CheckoutLineItem/1']
      )
    })
  })

  describe('transformProduct', () => {
    it('should correctly transform metafields', () => {
      const mockProduct = {
        id: 'gid://shopify/Product/1',
        handle: 'test-product',
        title: 'Test Product',
        description: 'Test',
        descriptionHtml: '<p>Test</p>',
        variants: [
          {
            id: 'gid://shopify/ProductVariant/1',
            title: 'Default',
            price: { amount: '29.99', currencyCode: 'USD' },
            available: true,
          },
        ],
        images: [],
        metafields: [
          { key: 'ar_enabled', value: 'true' },
          { key: 'ar_asset_url', value: 'https://example.com/model.glb' },
          { key: 'apec_limited', value: 'false' },
          { key: 'stock_remaining', value: '5' },
        ],
      }

      mockClient.product.fetchByHandle.mockResolvedValue(mockProduct)

      return service.getProductByHandle('test-product').then((result) => {
        expect(result?.metafields).toEqual({
          arenabled: true,
          arasseturl: 'https://example.com/model.glb',
          apeclimited: false,
          stockremaining: 5,
        })
      })
    })
  })
})
