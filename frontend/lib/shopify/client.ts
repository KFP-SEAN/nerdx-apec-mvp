/**
 * Shopify Storefront API Client
 *
 * Provides type-safe access to Shopify products and checkout with metafields support
 */

import Client from 'shopify-buy';

// Types
export interface ShopifyProduct {
  id: string;
  handle: string;
  title: string;
  description: string;
  descriptionHtml: string;
  priceRange: {
    minVariantPrice: {
      amount: string;
      currencyCode: string;
    };
  };
  images: Array<{
    url: string;
    altText?: string;
  }>;
  variants: Array<{
    id: string;
    title: string;
    price: string;
    available: boolean;
  }>;
  metafields?: {
    arEnabled?: boolean;
    arAssetUrl?: string;
    apecLimited?: boolean;
    stockRemaining?: number;
  };
}

// GraphQL query for products with metafields
const PRODUCTS_QUERY = `
  query getProducts($first: Int!) {
    products(first: $first) {
      edges {
        node {
          id
          handle
          title
          description
          descriptionHtml
          priceRange {
            minVariantPrice {
              amount
              currencyCode
            }
          }
          images(first: 10) {
            edges {
              node {
                url
                altText
              }
            }
          }
          variants(first: 10) {
            edges {
              node {
                id
                title
                price {
                  amount
                  currencyCode
                }
                availableForSale
              }
            }
          }
          arEnabled: metafield(namespace: "custom", key: "ar_enabled") {
            value
          }
          arAssetUrl: metafield(namespace: "custom", key: "ar_asset_url") {
            value
          }
          apecLimited: metafield(namespace: "custom", key: "apec_limited") {
            value
          }
          stockRemaining: metafield(namespace: "custom", key: "stock_remaining") {
            value
          }
        }
      }
    }
  }
`;

const PRODUCT_BY_HANDLE_QUERY = `
  query getProductByHandle($handle: String!) {
    productByHandle(handle: $handle) {
      id
      handle
      title
      description
      descriptionHtml
      priceRange {
        minVariantPrice {
          amount
          currencyCode
        }
      }
      images(first: 10) {
        edges {
          node {
            url
            altText
          }
        }
      }
      variants(first: 10) {
        edges {
          node {
            id
            title
            price {
              amount
              currencyCode
            }
            availableForSale
          }
        }
      }
      arEnabled: metafield(namespace: "custom", key: "ar_enabled") {
        value
      }
      arAssetUrl: metafield(namespace: "custom", key: "ar_asset_url") {
        value
      }
      apecLimited: metafield(namespace: "custom", key: "apec_limited") {
        value
      }
      stockRemaining: metafield(namespace: "custom", key: "stock_remaining") {
        value
      }
    }
  }
`;

export interface CheckoutLineItem {
  variantId: string;
  quantity: number;
  customAttributes?: Array<{
    key: string;
    value: string;
  }>;
}

export interface ShopifyCheckout {
  id: string;
  webUrl: string;
  lineItems: any[];
  subtotalPrice: string;
  totalTax: string;
  totalPrice: string;
  ready: boolean;
}

// Initialize Shopify Client
const shopifyClient = Client.buildClient({
  domain: process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN!,
  storefrontAccessToken: process.env.NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN!,
  apiVersion: '2024-01'
});

// GraphQL API configuration
const SHOPIFY_GRAPHQL_URL = `https://${process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN}/api/2024-01/graphql.json`;
const STOREFRONT_ACCESS_TOKEN = process.env.NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN!;

/**
 * Fetch data from Shopify Storefront API using GraphQL
 */
async function shopifyFetch<T = any>(query: string, variables: Record<string, any> = {}): Promise<T> {
  const response = await fetch(SHOPIFY_GRAPHQL_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': STOREFRONT_ACCESS_TOKEN,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    throw new Error(`Shopify API error: ${response.statusText}`);
  }

  const json = await response.json();

  if (json.errors) {
    throw new Error(json.errors.map((e: any) => e.message).join(', '));
  }

  return json.data;
}

/**
 * Shopify Service Class
 */
export class ShopifyService {
  private client: typeof shopifyClient;

  constructor() {
    this.client = shopifyClient;
  }

  /**
   * Fetch all products with optional filters
   */
  async getProducts(options?: {
    first?: number;
    after?: string;
    query?: string;
  }): Promise<ShopifyProduct[]> {
    try {
      const data = await shopifyFetch(PRODUCTS_QUERY, {
        first: options?.first || 50
      });

      // Transform GraphQL response to our type
      return data.products.edges.map((edge: any) => this.transformGraphQLProduct(edge.node));
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  }

  /**
   * Fetch single product by handle
   */
  async getProductByHandle(handle: string): Promise<ShopifyProduct | null> {
    try {
      const data = await shopifyFetch(PRODUCT_BY_HANDLE_QUERY, { handle });

      if (!data.productByHandle) return null;

      return this.transformGraphQLProduct(data.productByHandle);
    } catch (error) {
      console.error(`Error fetching product ${handle}:`, error);
      throw error;
    }
  }

  /**
   * Fetch product by ID
   */
  async getProductById(id: string): Promise<ShopifyProduct | null> {
    try {
      const product = await this.client.product.fetch(id);

      if (!product) return null;

      return this.transformProduct(product);
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create checkout
   */
  async createCheckout(
    lineItems: CheckoutLineItem[],
    options?: {
      email?: string;
      note?: string;
    }
  ): Promise<ShopifyCheckout> {
    try {
      // Create empty checkout
      let checkout = await this.client.checkout.create();

      // Add line items
      if (lineItems.length > 0) {
        checkout = await this.client.checkout.addLineItems(
          checkout.id,
          lineItems
        );
      }

      // Update customer info if provided
      if (options?.email) {
        checkout = await this.client.checkout.updateEmail(
          checkout.id,
          options.email
        );
      }

      return this.transformCheckout(checkout);
    } catch (error) {
      console.error('Error creating checkout:', error);
      throw error;
    }
  }

  /**
   * Add items to existing checkout
   */
  async addToCheckout(
    checkoutId: string,
    lineItems: CheckoutLineItem[]
  ): Promise<ShopifyCheckout> {
    try {
      const checkout = await this.client.checkout.addLineItems(
        checkoutId,
        lineItems
      );

      return this.transformCheckout(checkout);
    } catch (error) {
      console.error('Error adding to checkout:', error);
      throw error;
    }
  }

  /**
   * Update checkout line item quantity
   */
  async updateCheckoutLineItem(
    checkoutId: string,
    lineItemId: string,
    quantity: number
  ): Promise<ShopifyCheckout> {
    try {
      const checkout = await this.client.checkout.updateLineItems(checkoutId, [
        { id: lineItemId, quantity }
      ]);

      return this.transformCheckout(checkout);
    } catch (error) {
      console.error('Error updating checkout line item:', error);
      throw error;
    }
  }

  /**
   * Remove line item from checkout
   */
  async removeFromCheckout(
    checkoutId: string,
    lineItemId: string
  ): Promise<ShopifyCheckout> {
    try {
      const checkout = await this.client.checkout.removeLineItems(
        checkoutId,
        [lineItemId]
      );

      return this.transformCheckout(checkout);
    } catch (error) {
      console.error('Error removing from checkout:', error);
      throw error;
    }
  }

  /**
   * Fetch checkout by ID
   */
  async getCheckout(checkoutId: string): Promise<ShopifyCheckout> {
    try {
      const checkout = await this.client.checkout.fetch(checkoutId);
      return this.transformCheckout(checkout);
    } catch (error) {
      console.error('Error fetching checkout:', error);
      throw error;
    }
  }

  /**
   * Transform GraphQL product response to our type
   */
  private transformGraphQLProduct(product: any): ShopifyProduct {
    // Extract metafields from GraphQL response
    const metafields: any = {};

    // Parse metafield values
    if (product.arEnabled?.value !== undefined) {
      metafields.arEnabled = product.arEnabled.value === 'true';
    }
    if (product.arAssetUrl?.value) {
      metafields.arAssetUrl = product.arAssetUrl.value;
    }
    if (product.apecLimited?.value !== undefined) {
      metafields.apecLimited = product.apecLimited.value === 'true';
    }
    if (product.stockRemaining?.value !== undefined) {
      metafields.stockRemaining = parseInt(product.stockRemaining.value, 10);
    }

    return {
      id: product.id,
      handle: product.handle,
      title: product.title,
      description: product.description,
      descriptionHtml: product.descriptionHtml,
      priceRange: product.priceRange,
      images: product.images.edges.map((edge: any) => ({
        url: edge.node.url,
        altText: edge.node.altText
      })),
      variants: product.variants.edges.map((edge: any) => ({
        id: edge.node.id,
        title: edge.node.title,
        price: edge.node.price.amount,
        available: edge.node.availableForSale
      })),
      metafields
    };
  }

  /**
   * Transform Shopify product to our type (for Buy SDK - legacy)
   */
  private transformProduct(product: any): ShopifyProduct {
    // Extract metafields if available
    const metafields: any = {};

    if (product.metafields) {
      product.metafields.forEach((field: any) => {
        const key = field.key.replace(/_/g, '');
        metafields[key] = field.value === 'true' ? true :
                          field.value === 'false' ? false :
                          !isNaN(field.value) ? Number(field.value) :
                          field.value;
      });
    }

    return {
      id: product.id,
      handle: product.handle,
      title: product.title,
      description: product.description,
      descriptionHtml: product.descriptionHtml,
      priceRange: {
        minVariantPrice: {
          amount: product.variants[0]?.price?.amount || '0',
          currencyCode: product.variants[0]?.price?.currencyCode || 'USD'
        }
      },
      images: product.images.map((img: any) => ({
        url: img.src,
        altText: img.altText
      })),
      variants: product.variants.map((variant: any) => ({
        id: variant.id,
        title: variant.title,
        price: variant.price.amount,
        available: variant.available
      })),
      metafields
    };
  }

  /**
   * Transform Shopify checkout to our type
   */
  private transformCheckout(checkout: any): ShopifyCheckout {
    return {
      id: checkout.id,
      webUrl: checkout.webUrl,
      lineItems: checkout.lineItems,
      subtotalPrice: checkout.subtotalPrice?.amount || '0',
      totalTax: checkout.totalTax?.amount || '0',
      totalPrice: checkout.totalPrice?.amount || '0',
      ready: checkout.ready
    };
  }
}

// Singleton instance
export const shopifyService = new ShopifyService();

// Export default
export default shopifyService;
