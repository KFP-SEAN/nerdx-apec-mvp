/**
 * Fix Soju Product Image
 */

const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN || 'nerdx-apec-mvp.myshopify.com';
const ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;

if (!ADMIN_API_TOKEN) {
  console.error('❌ SHOPIFY_ADMIN_API_TOKEN environment variable is required');
  process.exit(1);
}

async function addSojuImage() {
  console.log('🖼️  Adding Soju product image...\n');

  const productId = '9018574504190';
  
  // Try alternative image URL
  const image = {
    src: 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800',
    alt: 'NERD Premium Soju - Korean Distilled Spirit'
  };

  try {
    const response = await fetch(
      `https://${SHOPIFY_DOMAIN}/admin/api/2024-01/products/${productId}/images.json`,
      {
        method: 'POST',
        headers: {
          'X-Shopify-Access-Token': ADMIN_API_TOKEN,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌ Failed: ${response.status}`);
      console.error(error);
      process.exit(1);
    }

    const result = await response.json();
    console.log(`✅ Added image: ${result.image.id}`);
    console.log(`   URL: ${result.image.src}`);
    console.log(`   Alt: ${result.image.alt}\n`);
    
  } catch (error) {
    console.error(`❌ Error:`, error.message);
    process.exit(1);
  }
}

addSojuImage();
