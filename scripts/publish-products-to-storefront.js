/**
 * Publish Products to Storefront API
 *
 * This script publishes existing products to the Headless sales channel
 * so they're accessible via Storefront API.
 */

const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN;
const ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;

if (!SHOPIFY_DOMAIN || !ADMIN_API_TOKEN) {
  console.error('❌ Error: Required environment variables not set');
  console.log('\nUsage:');
  console.log('  SHOPIFY_DOMAIN=your-store.myshopify.com \\');
  console.log('  SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx \\');
  console.log('  node scripts/publish-products-to-storefront.js');
  process.exit(1);
}

const API_VERSION = '2024-01';
const API_URL = `https://${SHOPIFY_DOMAIN}/admin/api/${API_VERSION}/graphql.json`;

/**
 * GraphQL mutation to publish product
 */
const PUBLISH_PRODUCT_MUTATION = `
  mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
    publishablePublish(id: $id, input: $input) {
      publishable {
        availablePublicationsCount {
          count
        }
      }
      userErrors {
        field
        message
      }
    }
  }
`;

/**
 * GraphQL query to get products
 */
const GET_PRODUCTS_QUERY = `
  query {
    products(first: 50) {
      edges {
        node {
          id
          title
          handle
          status
        }
      }
    }
  }
`;

/**
 * Call Shopify Admin GraphQL API
 */
async function shopifyGraphQL(query, variables = {}) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': ADMIN_API_TOKEN
    },
    body: JSON.stringify({ query, variables })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const json = await response.json();

  if (json.errors) {
    throw new Error(json.errors.map(e => e.message).join(', '));
  }

  return json.data;
}

/**
 * Get all products
 */
async function getProducts() {
  const data = await shopifyGraphQL(GET_PRODUCTS_QUERY);
  return data.products.edges.map(edge => edge.node);
}

/**
 * Publish product to Online Store (which makes it available to Storefront API)
 */
async function publishProduct(productId, productTitle) {
  console.log(`\n📤 Publishing: ${productTitle}`);
  console.log(`   ID: ${productId}`);

  try {
    // Publish to Online Store publication (which includes Storefront API)
    const data = await shopifyGraphQL(PUBLISH_PRODUCT_MUTATION, {
      id: productId,
      input: [
        {
          publicationId: "gid://shopify/Publication/166708707582" // Online Store
        }
      ]
    });

    const result = data.publishablePublish;

    if (result.userErrors && result.userErrors.length > 0) {
      const errors = result.userErrors.map(e => e.message).join(', ');
      console.log(`   ⚠️  ${errors}`);
      return { success: false, error: errors };
    }

    console.log(`   ✅ Published successfully`);
    return { success: true };
  } catch (error) {
    console.error(`   ❌ Failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🚀 Publish Products to Storefront API');
  console.log('====================================\n');
  console.log(`Store: ${SHOPIFY_DOMAIN}`);
  console.log(`API Version: ${API_VERSION}`);

  // Get all products
  console.log('\n🔍 Fetching products...');
  const products = await getProducts();
  console.log(`   Found ${products.length} products`);

  // Filter NERD products
  const nerdProducts = products.filter(p =>
    p.title.includes('NERD') || p.handle.includes('nerd')
  );
  console.log(`   ${nerdProducts.length} NERD products to publish`);

  const results = {
    success: 0,
    failed: 0
  };

  for (const product of nerdProducts) {
    const result = await publishProduct(product.id, product.title);

    if (result.success) {
      results.success++;
    } else {
      results.failed++;
    }

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Summary
  console.log('\n📊 Summary');
  console.log('==========');
  console.log(`✅ Successfully published: ${results.success}`);
  console.log(`❌ Failed: ${results.failed}`);

  if (results.failed === 0) {
    console.log('\n✅ All products published!');
    console.log('\nNext steps:');
    console.log('1. Wait 30 seconds for Storefront API to index');
    console.log('2. Refresh your frontend: http://localhost:3000/products/shopify');
  }
}

// Run the script
main().catch(error => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
