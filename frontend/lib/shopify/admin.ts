/**
 * Shopify Admin API Helper
 * Server-side only - uses Admin API token
 */

const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN || process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN;
const SHOPIFY_ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;
const ADMIN_API_VERSION = '2024-01';

interface ShopifyAdminResponse<T = any> {
  data?: T;
  errors?: Array<{ message: string; extensions?: any }>;
}

/**
 * Make a request to Shopify Admin API
 */
export async function shopifyAdminFetch<T = any>(
  query: string,
  variables?: Record<string, any>
): Promise<T> {
  if (!SHOPIFY_DOMAIN || !SHOPIFY_ADMIN_API_TOKEN) {
    throw new Error('Missing Shopify Admin API credentials');
  }

  const url = `https://${SHOPIFY_DOMAIN}/admin/api/${ADMIN_API_VERSION}/graphql.json`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': SHOPIFY_ADMIN_API_TOKEN,
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Shopify Admin API error:', {
      status: response.status,
      statusText: response.statusText,
      body: errorText,
    });
    throw new Error(`Shopify Admin API error: ${response.statusText}`);
  }

  const json: ShopifyAdminResponse<T> = await response.json();

  if (json.errors && json.errors.length > 0) {
    console.error('Shopify GraphQL errors:', json.errors);
    throw new Error(json.errors[0].message);
  }

  return json.data as T;
}

/**
 * Create a customer in Shopify
 */
export async function createShopifyCustomer(input: {
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  acceptsMarketing?: boolean;
  tags?: string[];
}) {
  const mutation = `
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        customer {
          id
          email
          firstName
          lastName
          phone
          emailMarketingConsent {
            marketingState
            consentUpdatedAt
          }
          tags
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  const variables = {
    input: {
      email: input.email,
      firstName: input.firstName,
      lastName: input.lastName,
      phone: input.phone || null,
      emailMarketingConsent: input.acceptsMarketing
        ? {
            marketingState: 'SUBSCRIBED',
            marketingOptInLevel: 'SINGLE_OPT_IN',
          }
        : undefined,
      tags: input.tags || [],
    },
  };

  const response = await shopifyAdminFetch<{
    customerCreate: {
      customer: any;
      userErrors: Array<{ field: string[]; message: string }>;
    };
  }>(mutation, variables);

  if (response.customerCreate.userErrors.length > 0) {
    const error = response.customerCreate.userErrors[0];
    throw new Error(error.message);
  }

  return response.customerCreate.customer;
}

/**
 * Update customer marketing consent
 */
export async function updateCustomerMarketing(
  customerId: string,
  acceptsMarketing: boolean
) {
  const mutation = `
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        customer {
          id
          emailMarketingConsent {
            marketingState
            consentUpdatedAt
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  const variables = {
    input: {
      id: customerId,
      emailMarketingConsent: {
        marketingState: acceptsMarketing ? 'SUBSCRIBED' : 'UNSUBSCRIBED',
        marketingOptInLevel: 'SINGLE_OPT_IN',
      },
    },
  };

  const response = await shopifyAdminFetch<{
    customerUpdate: {
      customer: any;
      userErrors: Array<{ field: string[]; message: string }>;
    };
  }>(mutation, variables);

  if (response.customerUpdate.userErrors.length > 0) {
    throw new Error(response.customerUpdate.userErrors[0].message);
  }

  return response.customerUpdate.customer;
}

/**
 * Add tags to customer
 */
export async function addCustomerTags(customerId: string, tags: string[]) {
  const mutation = `
    mutation tagsAdd($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  const variables = {
    id: customerId,
    tags,
  };

  const response = await shopifyAdminFetch<{
    tagsAdd: {
      node: any;
      userErrors: Array<{ field: string[]; message: string }>;
    };
  }>(mutation, variables);

  if (response.tagsAdd.userErrors.length > 0) {
    throw new Error(response.tagsAdd.userErrors[0].message);
  }

  return response.tagsAdd.node;
}

/**
 * Search for customer by email
 */
export async function findCustomerByEmail(email: string) {
  const query = `
    query getCustomerByEmail($query: String!) {
      customers(first: 1, query: $query) {
        edges {
          node {
            id
            email
            firstName
            lastName
            phone
            emailMarketingConsent {
              marketingState
              consentUpdatedAt
            }
            tags
          }
        }
      }
    }
  `;

  const variables = {
    query: `email:${email}`,
  };

  const response = await shopifyAdminFetch<{
    customers: {
      edges: Array<{ node: any }>;
    };
  }>(query, variables);

  if (response.customers.edges.length === 0) {
    return null;
  }

  return response.customers.edges[0].node;
}

/**
 * Create discount code
 */
export async function createDiscountCode(input: {
  code: string;
  percentage: number;
  usageLimit?: number;
  startsAt?: string;
  endsAt?: string;
}) {
  const mutation = `
    mutation discountCodeBasicCreate($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              codes(first: 1) {
                edges {
                  node {
                    code
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  const variables = {
    basicCodeDiscount: {
      title: `Welcome ${input.code}`,
      code: input.code,
      startsAt: input.startsAt || new Date().toISOString(),
      endsAt: input.endsAt,
      customerSelection: {
        all: true,
      },
      customerGets: {
        value: {
          percentage: input.percentage / 100,
        },
        items: {
          all: true,
        },
      },
      appliesOncePerCustomer: true,
      usageLimit: input.usageLimit,
    },
  };

  const response = await shopifyAdminFetch<{
    discountCodeBasicCreate: {
      codeDiscountNode: any;
      userErrors: Array<{ field: string[]; message: string }>;
    };
  }>(mutation, variables);

  if (response.discountCodeBasicCreate.userErrors.length > 0) {
    const error = response.discountCodeBasicCreate.userErrors[0];
    // If code already exists, that's okay
    if (error.message.includes('taken')) {
      return { code: input.code, alreadyExists: true };
    }
    throw new Error(error.message);
  }

  return response.discountCodeBasicCreate.codeDiscountNode;
}
