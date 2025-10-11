/**
 * Shopify Cart API Module
 * Handles cart operations using Shopify Cart API
 */

import { shopifyStorefrontFetch } from './client';

// Types
export interface Cart {
  id: string;
  checkoutUrl: string;
  lines: CartLine[];
  cost: {
    subtotalAmount: {
      amount: string;
      currencyCode: string;
    };
    totalAmount: {
      amount: string;
      currencyCode: string;
    };
    totalTaxAmount?: {
      amount: string;
      currencyCode: string;
    };
  };
  totalQuantity: number;
  discountCodes?: Array<{
    code: string;
    applicable: boolean;
  }>;
}

export interface CartLine {
  id: string;
  quantity: number;
  merchandise: {
    id: string;
    title: string;
    product: {
      id: string;
      title: string;
      handle: string;
      featuredImage?: {
        url: string;
        altText?: string;
      };
    };
    price: {
      amount: string;
      currencyCode: string;
    };
  };
  cost: {
    totalAmount: {
      amount: string;
      currencyCode: string;
    };
  };
}

export interface CartInput {
  merchandiseId: string;
  quantity: number;
  attributes?: Array<{
    key: string;
    value: string;
  }>;
}

/**
 * Create new cart
 */
export async function cartCreate(lines: CartInput[] = []): Promise<Cart> {
  const mutation = `
    mutation cartCreate($input: CartInput!) {
      cartCreate(input: $input) {
        cart {
          id
          checkoutUrl
          totalQuantity
          lines(first: 100) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    product {
                      id
                      title
                      handle
                      featuredImage {
                        url(transform: { maxWidth: 200 })
                        altText
                      }
                    }
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
                cost {
                  totalAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          cost {
            subtotalAmount {
              amount
              currencyCode
            }
            totalAmount {
              amount
              currencyCode
            }
            totalTaxAmount {
              amount
              currencyCode
            }
          }
          discountCodes {
            code
            applicable
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      input: {
        lines: lines.map((line) => ({
          merchandiseId: line.merchandiseId,
          quantity: line.quantity,
          attributes: line.attributes,
        })),
      },
    });

    if (response.cartCreate.userErrors && response.cartCreate.userErrors.length > 0) {
      throw new Error(response.cartCreate.userErrors[0].message);
    }

    const cart = response.cartCreate.cart;

    // Save cart ID to localStorage
    if (typeof window !== 'undefined' && cart.id) {
      localStorage.setItem('cartId', cart.id);
    }

    return transformCart(cart);
  } catch (error) {
    console.error('Cart create error:', error);
    throw error;
  }
}

/**
 * Get cart by ID
 */
export async function cartGet(cartId: string): Promise<Cart> {
  const query = `
    query cartQuery($cartId: ID!) {
      cart(id: $cartId) {
        id
        checkoutUrl
        totalQuantity
        lines(first: 100) {
          edges {
            node {
              id
              quantity
              merchandise {
                ... on ProductVariant {
                  id
                  title
                  product {
                    id
                    title
                    handle
                    featuredImage {
                      url(transform: { maxWidth: 200 })
                      altText
                    }
                  }
                  price {
                    amount
                    currencyCode
                  }
                }
              }
              cost {
                totalAmount {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        cost {
          subtotalAmount {
            amount
            currencyCode
          }
          totalAmount {
            amount
            currencyCode
          }
          totalTaxAmount {
            amount
            currencyCode
          }
        }
        discountCodes {
          code
          applicable
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(query, {
      cartId,
    });

    if (!response.cart) {
      throw new Error('Cart not found');
    }

    return transformCart(response.cart);
  } catch (error) {
    console.error('Cart get error:', error);
    throw error;
  }
}

/**
 * Add lines to cart
 */
export async function cartLinesAdd(cartId: string, lines: CartInput[]): Promise<Cart> {
  const mutation = `
    mutation cartLinesAdd($cartId: ID!, $lines: [CartLineInput!]!) {
      cartLinesAdd(cartId: $cartId, lines: $lines) {
        cart {
          id
          checkoutUrl
          totalQuantity
          lines(first: 100) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    product {
                      id
                      title
                      handle
                      featuredImage {
                        url(transform: { maxWidth: 200 })
                        altText
                      }
                    }
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
                cost {
                  totalAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          cost {
            subtotalAmount {
              amount
              currencyCode
            }
            totalAmount {
              amount
              currencyCode
            }
            totalTaxAmount {
              amount
              currencyCode
            }
          }
          discountCodes {
            code
            applicable
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      cartId,
      lines: lines.map((line) => ({
        merchandiseId: line.merchandiseId,
        quantity: line.quantity,
        attributes: line.attributes,
      })),
    });

    if (response.cartLinesAdd.userErrors && response.cartLinesAdd.userErrors.length > 0) {
      throw new Error(response.cartLinesAdd.userErrors[0].message);
    }

    return transformCart(response.cartLinesAdd.cart);
  } catch (error) {
    console.error('Cart lines add error:', error);
    throw error;
  }
}

/**
 * Update cart lines
 */
export async function cartLinesUpdate(
  cartId: string,
  lines: Array<{ id: string; quantity: number }>
): Promise<Cart> {
  const mutation = `
    mutation cartLinesUpdate($cartId: ID!, $lines: [CartLineUpdateInput!]!) {
      cartLinesUpdate(cartId: $cartId, lines: $lines) {
        cart {
          id
          checkoutUrl
          totalQuantity
          lines(first: 100) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    product {
                      id
                      title
                      handle
                      featuredImage {
                        url(transform: { maxWidth: 200 })
                        altText
                      }
                    }
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
                cost {
                  totalAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          cost {
            subtotalAmount {
              amount
              currencyCode
            }
            totalAmount {
              amount
              currencyCode
            }
            totalTaxAmount {
              amount
              currencyCode
            }
          }
          discountCodes {
            code
            applicable
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      cartId,
      lines,
    });

    if (response.cartLinesUpdate.userErrors && response.cartLinesUpdate.userErrors.length > 0) {
      throw new Error(response.cartLinesUpdate.userErrors[0].message);
    }

    return transformCart(response.cartLinesUpdate.cart);
  } catch (error) {
    console.error('Cart lines update error:', error);
    throw error;
  }
}

/**
 * Remove lines from cart
 */
export async function cartLinesRemove(cartId: string, lineIds: string[]): Promise<Cart> {
  const mutation = `
    mutation cartLinesRemove($cartId: ID!, $lineIds: [ID!]!) {
      cartLinesRemove(cartId: $cartId, lineIds: $lineIds) {
        cart {
          id
          checkoutUrl
          totalQuantity
          lines(first: 100) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    product {
                      id
                      title
                      handle
                      featuredImage {
                        url(transform: { maxWidth: 200 })
                        altText
                      }
                    }
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
                cost {
                  totalAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          cost {
            subtotalAmount {
              amount
              currencyCode
            }
            totalAmount {
              amount
              currencyCode
            }
            totalTaxAmount {
              amount
              currencyCode
            }
          }
          discountCodes {
            code
            applicable
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      cartId,
      lineIds,
    });

    if (response.cartLinesRemove.userErrors && response.cartLinesRemove.userErrors.length > 0) {
      throw new Error(response.cartLinesRemove.userErrors[0].message);
    }

    return transformCart(response.cartLinesRemove.cart);
  } catch (error) {
    console.error('Cart lines remove error:', error);
    throw error;
  }
}

/**
 * Apply discount code to cart
 */
export async function cartDiscountCodesUpdate(cartId: string, discountCodes: string[]): Promise<Cart> {
  const mutation = `
    mutation cartDiscountCodesUpdate($cartId: ID!, $discountCodes: [String!]!) {
      cartDiscountCodesUpdate(cartId: $cartId, discountCodes: $discountCodes) {
        cart {
          id
          checkoutUrl
          totalQuantity
          lines(first: 100) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    product {
                      id
                      title
                      handle
                      featuredImage {
                        url(transform: { maxWidth: 200 })
                        altText
                      }
                    }
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
                cost {
                  totalAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          cost {
            subtotalAmount {
              amount
              currencyCode
            }
            totalAmount {
              amount
              currencyCode
            }
            totalTaxAmount {
              amount
              currencyCode
            }
          }
          discountCodes {
            code
            applicable
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      cartId,
      discountCodes,
    });

    if (
      response.cartDiscountCodesUpdate.userErrors &&
      response.cartDiscountCodesUpdate.userErrors.length > 0
    ) {
      throw new Error(response.cartDiscountCodesUpdate.userErrors[0].message);
    }

    return transformCart(response.cartDiscountCodesUpdate.cart);
  } catch (error) {
    console.error('Cart discount codes update error:', error);
    throw error;
  }
}

/**
 * Transform cart response to Cart type
 */
function transformCart(cart: any): Cart {
  return {
    id: cart.id,
    checkoutUrl: cart.checkoutUrl,
    totalQuantity: cart.totalQuantity,
    lines: cart.lines.edges.map((edge: any) => ({
      id: edge.node.id,
      quantity: edge.node.quantity,
      merchandise: edge.node.merchandise,
      cost: edge.node.cost,
    })),
    cost: cart.cost,
    discountCodes: cart.discountCodes || [],
  };
}

/**
 * Get or create cart
 */
export async function getOrCreateCart(): Promise<Cart> {
  if (typeof window === 'undefined') {
    // Server-side: create new cart
    return cartCreate([]);
  }

  const cartId = localStorage.getItem('cartId');

  if (cartId) {
    try {
      return await cartGet(cartId);
    } catch (error) {
      // Cart not found or expired, create new one
      console.warn('Cart not found, creating new cart');
      localStorage.removeItem('cartId');
      return cartCreate([]);
    }
  }

  // No cart ID, create new one
  return cartCreate([]);
}
