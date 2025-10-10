/**
 * Add Product Images via URL
 * 
 * Adds appropriate product images to Shopify products using Admin API
 */

const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN || 'nerdx-apec-mvp.myshopify.com';
const ADMIN_API_TOKEN = process.env.SHOPIFY_ADMIN_API_TOKEN;

if (!ADMIN_API_TOKEN) {
  console.error('❌ SHOPIFY_ADMIN_API_TOKEN environment variable is required');
  process.exit(1);
}

// Product image mappings (using public domain/demo images)
const productImages = {
  '9018574471422': { // NERD Premium Makgeolli
    images: [
      {
        src: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800',
        alt: 'NERD Premium Makgeolli - Traditional Korean Rice Wine'
      }
    ]
  },
  '9018574504190': { // NERD Premium Soju
    images: [
      {
        src: 'https://images.unsplash.com/photo-1569963127451-64ca0cd4c5c9?w=800',
        alt: 'NERD Premium Soju - Korean Distilled Spirit'
      }
    ]
  },
  '9018574602494': { // NERDX APEC Limited Cheongju
    images: [
      {
        src: 'https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=800',
        alt: 'NERDX APEC Limited Cheongju - Premium Korean Clear Wine'
      }
    ]
  }
};

async function addProductImages() {
  console.log('🖼️  Adding product images...\n');

  for (const [productId, data] of Object.entries(productImages)) {
    console.log(`Processing product ${productId}...`);

    for (const image of data.images) {
      try {
        const response = await fetch(
          `https://${SHOPIFY_DOMAIN}/admin/api/2024-01/products/${productId}/images.json`,
          {
            method: 'POST',
            headers: {
              'X-Shopify-Access-Token': ADMIN_API_TOKEN,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              image: {
                src: image.src,
                alt: image.alt
              }
            })
          }
        );

        if (!response.ok) {
          const error = await response.text();
          console.error(`❌ Failed to add image: ${response.status} ${response.statusText}`);
          console.error(error);
          continue;
        }

        const result = await response.json();
        console.log(`✅ Added image: ${result.image.id}`);
        console.log(`   URL: ${result.image.src}`);
        console.log(`   Alt: ${result.image.alt}\n`);

      } catch (error) {
        console.error(`❌ Error adding image:`, error.message);
      }
    }
  }

  console.log('\n✅ Product images added successfully!\n');
}

addProductImages().catch(console.error);
