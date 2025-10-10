/**
 * Shopify GraphQL Queries
 *
 * Direct GraphQL queries for more control over data fetching
 */

export const PRODUCTS_QUERY = `
  query GetProducts($first: Int!, $after: String, $query: String) {
    products(first: $first, after: $after, query: $query) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          handle
          title
          description
          descriptionHtml
          productType
          tags
          vendor
          createdAt
          updatedAt
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
                id
                url
                altText
                width
                height
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
                compareAtPrice {
                  amount
                  currencyCode
                }
                available
                quantityAvailable
                sku
                weight
                weightUnit
              }
            }
          }
          metafields(identifiers: [
            {namespace: "custom", key: "ar_enabled"},
            {namespace: "custom", key: "ar_asset_url"},
            {namespace: "custom", key: "apec_limited"},
            {namespace: "custom", key: "stock_remaining"}
          ]) {
            namespace
            key
            value
            type
          }
        }
      }
    }
  }
`;

export const PRODUCT_BY_HANDLE_QUERY = `
  query GetProductByHandle($handle: String!) {
    productByHandle(handle: $handle) {
      id
      handle
      title
      description
      descriptionHtml
      productType
      tags
      vendor
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
            id
            url
            altText
            width
            height
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
            compareAtPrice {
              amount
              currencyCode
            }
            available
            quantityAvailable
            sku
            selectedOptions {
              name
              value
            }
          }
        }
      }
      metafields(identifiers: [
        {namespace: "custom", key: "ar_enabled"},
        {namespace: "custom", key: "ar_asset_url"},
        {namespace: "custom", key: "apec_limited"},
        {namespace: "custom", key: "stock_remaining"}
      ]) {
        namespace
        key
        value
        type
      }
    }
  }
`;

export const CHECKOUT_CREATE_MUTATION = `
  mutation CheckoutCreate($input: CheckoutCreateInput!) {
    checkoutCreate(input: $input) {
      checkout {
        id
        webUrl
        subtotalPrice {
          amount
          currencyCode
        }
        totalTax {
          amount
          currencyCode
        }
        totalPrice {
          amount
          currencyCode
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              title
              quantity
              variant {
                id
                title
                price {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
      checkoutUserErrors {
        field
        message
      }
    }
  }
`;

export const CHECKOUT_LINE_ITEMS_ADD_MUTATION = `
  mutation CheckoutLineItemsAdd($checkoutId: ID!, $lineItems: [CheckoutLineItemInput!]!) {
    checkoutLineItemsAdd(checkoutId: $checkoutId, lineItems: $lineItems) {
      checkout {
        id
        webUrl
        lineItems(first: 10) {
          edges {
            node {
              id
              title
              quantity
            }
          }
        }
      }
      checkoutUserErrors {
        field
        message
      }
    }
  }
`;

/**
 * GraphQL Client for direct queries
 */
export class ShopifyGraphQLClient {
  private endpoint: string;
  private headers: HeadersInit;

  constructor() {
    this.endpoint = `https://${process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN}/api/2024-01/graphql.json`;
    this.headers = {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': process.env.NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN!
    };
  }

  /**
   * Execute GraphQL query
   */
  async query<T = any>(query: string, variables?: Record<string, any>): Promise<T> {
    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          query,
          variables
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        throw new Error(result.errors[0]?.message || 'GraphQL query failed');
      }

      return result.data;
    } catch (error) {
      console.error('GraphQL query error:', error);
      throw error;
    }
  }

  /**
   * Fetch products with GraphQL
   */
  async getProducts(variables: {
    first: number;
    after?: string;
    query?: string;
  }) {
    return this.query(PRODUCTS_QUERY, variables);
  }

  /**
   * Fetch product by handle
   */
  async getProductByHandle(handle: string) {
    return this.query(PRODUCT_BY_HANDLE_QUERY, { handle });
  }

  /**
   * Create checkout
   */
  async createCheckout(input: {
    lineItems: Array<{
      variantId: string;
      quantity: number;
      customAttributes?: Array<{ key: string; value: string }>;
    }>;
    email?: string;
    note?: string;
  }) {
    return this.query(CHECKOUT_CREATE_MUTATION, { input });
  }
}

// Singleton instance
export const shopifyGraphQL = new ShopifyGraphQLClient();

export default shopifyGraphQL;
