#!/usr/bin/env node

/**
 * Shopify Product Setup Script
 *
 * This script automatically creates test products in your Shopify Development Store
 * using the Shopify Admin API.
 *
 * Usage:
 *   node scripts/setup-shopify-products.js
 *
 * Required Environment Variables:
 *   SHOPIFY_DOMAIN - Your store domain (e.g., nerdx-test.myshopify.com)
 *   SHOPIFY_ADMIN_API_TOKEN - Admin API access token
 */

const https = require('https');

// Configuration
const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN || 'nerdx-apec-test.myshopify.com';
const SHOPIFY_ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;
const API_VERSION = '2024-01';

if (!SHOPIFY_ADMIN_API_TOKEN) {
  console.error('❌ Error: SHOPIFY_ADMIN_API_TOKEN environment variable is required');
  console.error('\nPlease set your Shopify Admin API token:');
  console.error('  export SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx');
  console.error('\nOr run:');
  console.error('  SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx node scripts/setup-shopify-products.js');
  process.exit(1);
}

// Test Products Data
const products = [
  {
    title: 'NERD Premium Makgeolli',
    body_html: `
      <h3>프리미엄 한국 전통 막걸리</h3>
      <p>부드럽고 달콤한 맛과 향긋한 쌀 향이 특징인 전통 방식으로 빚은 프리미엄 막걸리입니다.</p>
      <ul>
        <li><strong>알코올:</strong> 6%</li>
        <li><strong>용량:</strong> 750ml</li>
        <li><strong>원산지:</strong> 대한민국 경주</li>
        <li><strong>APEC 2024 한정판</strong></li>
      </ul>
      <p>AR로 제품을 미리 체험해보세요!</p>
    `,
    vendor: 'NERD',
    product_type: 'Beverage',
    tags: ['makgeolli', 'traditional', 'apec-limited', 'ar-enabled'],
    variants: [
      {
        price: '29.99',
        compare_at_price: '39.99',
        sku: 'NERD-MAK-001',
        inventory_quantity: 50,
        weight: 1.2,
        weight_unit: 'kg',
        inventory_management: 'shopify'
      }
    ],
    metafields: [
      {
        namespace: 'custom',
        key: 'ar_enabled',
        value: 'true',
        type: 'boolean'
      },
      {
        namespace: 'custom',
        key: 'apec_limited',
        value: 'true',
        type: 'boolean'
      },
      {
        namespace: 'custom',
        key: 'stock_remaining',
        value: '50',
        type: 'number_integer'
      },
      {
        namespace: 'custom',
        key: 'ar_asset_url',
        value: 'https://modelviewer.dev/shared-assets/models/NeilArmstrong.glb',
        type: 'url'
      }
    ]
  },
  {
    title: 'NERD Premium Soju',
    body_html: `
      <h3>프리미엄 한국 소주</h3>
      <p>깔끔하고 부드러운 맛이 특징인 프리미엄 소주입니다.</p>
      <ul>
        <li><strong>알코올:</strong> 16.9%</li>
        <li><strong>용량:</strong> 360ml</li>
        <li><strong>원산지:</strong> 대한민국 경주</li>
      </ul>
    `,
    vendor: 'NERD',
    product_type: 'Beverage',
    tags: ['soju', 'premium'],
    variants: [
      {
        price: '15.99',
        sku: 'NERD-SOJU-001',
        inventory_quantity: 100,
        weight: 0.5,
        weight_unit: 'kg',
        inventory_management: 'shopify'
      }
    ],
    metafields: [
      {
        namespace: 'custom',
        key: 'ar_enabled',
        value: 'false',
        type: 'boolean'
      },
      {
        namespace: 'custom',
        key: 'apec_limited',
        value: 'false',
        type: 'boolean'
      }
    ]
  },
  {
    title: 'NERDX APEC Limited Cheongju',
    body_html: `
      <h3>APEC 2024 한정판 청주</h3>
      <p>APEC 정상회의를 기념하여 특별 제작된 한정판 청주입니다.</p>
      <ul>
        <li><strong>알코올:</strong> 13%</li>
        <li><strong>용량:</strong> 500ml</li>
        <li><strong>원산지:</strong> 대한민국 경주</li>
        <li><strong>한정 수량:</strong> 단 20병만!</li>
      </ul>
      <p>AR로 제품을 미리 체험해보세요!</p>
    `,
    vendor: 'NERD',
    product_type: 'Beverage',
    tags: ['cheongju', 'apec-limited', 'ar-enabled', 'limited-edition'],
    variants: [
      {
        price: '49.99',
        compare_at_price: '69.99',
        sku: 'NERD-CHEONG-APEC',
        inventory_quantity: 20,
        weight: 0.8,
        weight_unit: 'kg',
        inventory_management: 'shopify'
      }
    ],
    metafields: [
      {
        namespace: 'custom',
        key: 'ar_enabled',
        value: 'true',
        type: 'boolean'
      },
      {
        namespace: 'custom',
        key: 'apec_limited',
        value: 'true',
        type: 'boolean'
      },
      {
        namespace: 'custom',
        key: 'stock_remaining',
        value: '20',
        type: 'number_integer'
      },
      {
        namespace: 'custom',
        key: 'ar_asset_url',
        value: 'https://modelviewer.dev/shared-assets/models/Astronaut.glb',
        type: 'url'
      }
    ]
  }
];

/**
 * Make HTTP request to Shopify Admin API
 */
function shopifyRequest(method, path, data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: SHOPIFY_DOMAIN,
      port: 443,
      path: `/admin/api/${API_VERSION}${path}`,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': SHOPIFY_ADMIN_API_TOKEN
      }
    };

    const req = https.request(options, (res) => {
      let body = '';

      res.on('data', (chunk) => {
        body += chunk;
      });

      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve(body);
          }
        } else {
          reject({
            statusCode: res.statusCode,
            body: body
          });
        }
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

/**
 * Create a product with metafields
 */
async function createProduct(productData) {
  console.log(`\n📦 Creating product: ${productData.title}...`);

  try {
    // Create product
    const response = await shopifyRequest('POST', '/products.json', {
      product: productData
    });

    const product = response.product;
    console.log(`✅ Product created: ${product.title} (ID: ${product.id})`);
    console.log(`   - Price: $${product.variants[0].price}`);
    console.log(`   - SKU: ${product.variants[0].sku}`);
    console.log(`   - Inventory: ${product.variants[0].inventory_quantity}`);

    // Add metafields if they exist
    if (productData.metafields && productData.metafields.length > 0) {
      console.log(`   📝 Adding ${productData.metafields.length} metafields...`);

      for (const metafield of productData.metafields) {
        try {
          await shopifyRequest('POST', `/products/${product.id}/metafields.json`, {
            metafield: metafield
          });
          console.log(`      ✓ ${metafield.key}: ${metafield.value}`);
        } catch (error) {
          console.error(`      ✗ Failed to add metafield ${metafield.key}:`, error.body);
        }
      }
    }

    return product;
  } catch (error) {
    console.error(`❌ Failed to create product ${productData.title}:`);
    if (error.body) {
      console.error(`   Status: ${error.statusCode}`);
      console.error(`   Response: ${error.body}`);
    } else {
      console.error(`   Error:`, error);
    }
    throw error;
  }
}

/**
 * Check if products already exist
 */
async function checkExistingProducts() {
  console.log('\n🔍 Checking for existing products...');

  try {
    const response = await shopifyRequest('GET', '/products.json?limit=250');
    const existingProducts = response.products;

    console.log(`   Found ${existingProducts.length} existing products`);

    // Check if our test products already exist
    const existingSKUs = existingProducts.map(p =>
      p.variants.map(v => v.sku)
    ).flat();

    const ourSKUs = products.map(p => p.variants[0].sku);
    const alreadyExists = ourSKUs.some(sku => existingSKUs.includes(sku));

    if (alreadyExists) {
      console.log('\n⚠️  Warning: Some test products may already exist');
      console.log('   Existing SKUs:', existingSKUs.filter(sku => ourSKUs.includes(sku)));
      console.log('   Proceeding anyway...\n');
    }

    return existingProducts;
  } catch (error) {
    console.error('❌ Failed to check existing products:', error);
    return [];
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🚀 Shopify Product Setup Script');
  console.log('================================');
  console.log(`\nStore: ${SHOPIFY_DOMAIN}`);
  console.log(`API Version: ${API_VERSION}`);
  console.log(`Products to create: ${products.length}`);

  // Check existing products
  await checkExistingProducts();

  // Create each product
  const results = {
    success: [],
    failed: []
  };

  for (const productData of products) {
    try {
      const product = await createProduct(productData);
      results.success.push(product);

      // Rate limiting - wait 500ms between requests
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      results.failed.push({
        title: productData.title,
        error: error
      });
    }
  }

  // Summary
  console.log('\n\n📊 Summary');
  console.log('==========');
  console.log(`✅ Successfully created: ${results.success.length} products`);
  console.log(`❌ Failed: ${results.failed.length} products`);

  if (results.success.length > 0) {
    console.log('\n✅ Created Products:');
    results.success.forEach(p => {
      console.log(`   - ${p.title} (ID: ${p.id})`);
    });
  }

  if (results.failed.length > 0) {
    console.log('\n❌ Failed Products:');
    results.failed.forEach(p => {
      console.log(`   - ${p.title}`);
    });
  }

  console.log('\n🎉 Setup complete!');
  console.log('\nNext steps:');
  console.log('1. Visit your Shopify Admin to verify products');
  console.log('2. Set up your frontend environment variables');
  console.log('3. Run: cd frontend && npm run dev');
  console.log('4. Visit: http://localhost:3000/products/shopify\n');
}

// Run the script
main().catch(error => {
  console.error('\n💥 Fatal error:', error);
  process.exit(1);
});
