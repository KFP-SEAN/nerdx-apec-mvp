/**
 * Create Shopify Metafield Definitions with Storefront API Access
 *
 * This script creates metafield definitions that are accessible via Storefront API.
 * Run this BEFORE creating products.
 */

const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN;
const ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;

if (!SHOPIFY_DOMAIN || !ADMIN_API_TOKEN) {
  console.error('❌ Error: Required environment variables not set');
  console.log('\nUsage:');
  console.log('  SHOPIFY_DOMAIN=your-store.myshopify.com \\');
  console.log('  SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx \\');
  console.log('  node scripts/create-metafield-definitions.js');
  process.exit(1);
}

const API_VERSION = '2024-01';
const API_URL = `https://${SHOPIFY_DOMAIN}/admin/api/${API_VERSION}/graphql.json`;

/**
 * GraphQL mutation to create metafield definition
 */
const CREATE_METAFIELD_DEFINITION = `
  mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $definition) {
      createdDefinition {
        id
        name
        namespace
        key
        type {
          name
        }
        ownerType
        access {
          storefront
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
 * Metafield definitions to create
 */
const metafieldDefinitions = [
  {
    name: 'AR Enabled',
    namespace: 'custom',
    key: 'ar_enabled',
    description: 'Indicates if this product has AR experience available',
    type: 'boolean',
    ownerType: 'PRODUCT',
    access: {
      storefront: 'PUBLIC_READ'
    }
  },
  {
    name: 'AR Asset URL',
    namespace: 'custom',
    key: 'ar_asset_url',
    description: 'URL to the 3D model GLB file for AR experience',
    type: 'url',
    ownerType: 'PRODUCT',
    access: {
      storefront: 'PUBLIC_READ'
    }
  },
  {
    name: 'APEC Limited Edition',
    namespace: 'custom',
    key: 'apec_limited',
    description: 'Indicates if this is an APEC limited edition product',
    type: 'boolean',
    ownerType: 'PRODUCT',
    access: {
      storefront: 'PUBLIC_READ'
    }
  },
  {
    name: 'Stock Remaining',
    namespace: 'custom',
    key: 'stock_remaining',
    description: 'Number of items remaining in stock',
    type: 'number_integer',
    ownerType: 'PRODUCT',
    access: {
      storefront: 'PUBLIC_READ'
    }
  }
];

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
 * Create a metafield definition
 */
async function createMetafieldDefinition(definition) {
  console.log(`\n📝 Creating metafield definition: ${definition.name}`);
  console.log(`   Namespace: ${definition.namespace}`);
  console.log(`   Key: ${definition.key}`);
  console.log(`   Type: ${definition.type}`);

  try {
    const data = await shopifyGraphQL(CREATE_METAFIELD_DEFINITION, {
      definition: {
        name: definition.name,
        namespace: definition.namespace,
        key: definition.key,
        description: definition.description,
        type: definition.type,
        ownerType: definition.ownerType,
        access: definition.access
      }
    });

    const result = data.metafieldDefinitionCreate;

    if (result.userErrors && result.userErrors.length > 0) {
      const errors = result.userErrors.map(e => e.message).join(', ');

      // Check if it's a "already exists" error
      if (errors.includes('already exists') || errors.includes('taken')) {
        console.log(`   ℹ️  Already exists: ${definition.key}`);
        return { success: true, alreadyExists: true };
      }

      throw new Error(errors);
    }

    if (result.createdDefinition) {
      console.log(`   ✅ Created successfully`);
      console.log(`      ID: ${result.createdDefinition.id}`);
      console.log(`      Storefront Access: ${result.createdDefinition.access.storefront}`);
      return { success: true, definition: result.createdDefinition };
    }

    throw new Error('Unknown error creating metafield definition');
  } catch (error) {
    console.error(`   ❌ Failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🚀 Shopify Metafield Definition Setup');
  console.log('=====================================\n');
  console.log(`Store: ${SHOPIFY_DOMAIN}`);
  console.log(`API Version: ${API_VERSION}`);
  console.log(`Definitions to create: ${metafieldDefinitions.length}`);

  const results = {
    success: 0,
    alreadyExists: 0,
    failed: 0
  };

  for (const definition of metafieldDefinitions) {
    const result = await createMetafieldDefinition(definition);

    if (result.success) {
      if (result.alreadyExists) {
        results.alreadyExists++;
      } else {
        results.success++;
      }
    } else {
      results.failed++;
    }

    // Rate limiting: wait 500ms between requests
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Summary
  console.log('\n📊 Summary');
  console.log('==========');
  console.log(`✅ Successfully created: ${results.success}`);
  console.log(`ℹ️  Already existed: ${results.alreadyExists}`);
  console.log(`❌ Failed: ${results.failed}`);

  if (results.failed === 0) {
    console.log('\n✅ Setup complete!');
    console.log('\nNext steps:');
    console.log('1. Run the product setup script:');
    console.log('   node scripts/setup-shopify-products.js');
    console.log('2. Refresh your frontend to see metafields');
  } else {
    console.log('\n⚠️  Some definitions failed to create. Check errors above.');
    process.exit(1);
  }
}

// Run the script
main().catch(error => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
