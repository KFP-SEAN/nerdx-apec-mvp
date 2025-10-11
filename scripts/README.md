# 🛠️ Shopify Setup Scripts

Automated scripts to set up your Shopify Development Store.

## 📋 Prerequisites

1. **Shopify Development Store** created
2. **Admin API Access Token** obtained
3. **Node.js 18+** installed

## 🚀 Quick Start

### Step 1: Get Your Admin API Token

1. Go to your Shopify Admin: `https://your-store.myshopify.com/admin`
2. Navigate to **Settings** → **Apps and sales channels** → **Develop apps**
3. Click **Create an app** (name it "Product Setup Script")
4. Go to **Configuration** tab
5. Under **Admin API**, click **Configure**
6. Enable these permissions:
   - ✅ `write_products`
   - ✅ `read_products`
7. Click **Save**
8. Go to **API credentials** tab
9. Click **Install app**
10. Copy the **Admin API access token** (starts with `shpat_`)

### Step 2: Run the Setup Script

```bash
# Set environment variables
export SHOPIFY_DOMAIN=your-store.myshopify.com
export SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx

# Run the script
node scripts/setup-shopify-products.js
```

Or run in one line:

```bash
SHOPIFY_DOMAIN=your-store.myshopify.com \
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx \
node scripts/setup-shopify-products.js
```

### Step 3: Verify

The script will create 3 test products:

1. ✅ **NERD Premium Makgeolli** ($29.99) - AR enabled, APEC limited
2. ✅ **NERD Premium Soju** ($15.99) - Standard product
3. ✅ **NERDX APEC Limited Cheongju** ($49.99) - AR enabled, APEC limited

## 📦 What This Script Does

### Creates Products

- Sets up 3 test products with complete information
- Adds product variants with pricing and SKUs
- Sets inventory quantities
- Adds product tags for filtering

### Adds Metafields

Each product gets custom metafields:

- `custom.ar_enabled` (Boolean) - Product has AR experience
- `custom.apec_limited` (Boolean) - APEC limited edition
- `custom.stock_remaining` (Integer) - Available stock count
- `custom.ar_asset_url` (String) - 3D model GLB file URL

### Features

- ✅ Automatic product creation via REST Admin API
- ✅ Metafields support
- ✅ Rate limiting (500ms between requests)
- ✅ Error handling and reporting
- ✅ Duplicate detection
- ✅ Detailed progress logging

## 📊 Expected Output

```
🚀 Shopify Product Setup Script
================================

Store: your-store.myshopify.com
API Version: 2024-01
Products to create: 3

🔍 Checking for existing products...
   Found 0 existing products

📦 Creating product: NERD Premium Makgeolli...
✅ Product created: NERD Premium Makgeolli (ID: 1234567890)
   - Price: $29.99
   - SKU: NERD-MAK-001
   - Inventory: 50
   📝 Adding 4 metafields...
      ✓ ar_enabled: true
      ✓ apec_limited: true
      ✓ stock_remaining: 50
      ✓ ar_asset_url: https://...

[... similar output for other products ...]

📊 Summary
==========
✅ Successfully created: 3 products
❌ Failed: 0 products

✅ Created Products:
   - NERD Premium Makgeolli (ID: 1234567890)
   - NERD Premium Soju (ID: 1234567891)
   - NERDX APEC Limited Cheongju (ID: 1234567892)

🎉 Setup complete!

Next steps:
1. Visit your Shopify Admin to verify products
2. Set up your frontend environment variables
3. Run: cd frontend && npm run dev
4. Visit: http://localhost:3000/products/shopify
```

## 🐛 Troubleshooting

### Error: "SHOPIFY_ADMIN_API_TOKEN environment variable is required"

**Solution:** Make sure you've set the environment variable:

```bash
export SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxx
```

### Error: "401 Unauthorized"

**Cause:** Invalid or expired API token

**Solution:**
1. Verify your token is correct
2. Check that the Custom App is installed
3. Ensure Admin API permissions are enabled

### Error: "422 Unprocessable Entity"

**Cause:** Invalid product data or missing required fields

**Solution:**
1. Check the error message in the output
2. Verify your store settings allow product creation
3. Make sure inventory tracking is enabled

### Error: "429 Too Many Requests"

**Cause:** Rate limit exceeded

**Solution:** The script already includes rate limiting (500ms delay). If you still see this error, increase the delay in the script.

### Products Created But Metafields Missing

**Cause:** Metafield definitions may need to be created first

**Solution:**
1. Go to Shopify Admin → Settings → Custom data
2. Add metafield definitions manually first
3. Run the script again

## 🔧 Configuration

### Customize Products

Edit `setup-shopify-products.js` and modify the `products` array:

```javascript
const products = [
  {
    title: 'Your Product Name',
    body_html: '<p>Product description</p>',
    vendor: 'Your Brand',
    product_type: 'Your Type',
    tags: ['tag1', 'tag2'],
    variants: [
      {
        price: '99.99',
        sku: 'YOUR-SKU-001',
        inventory_quantity: 100,
        // ...
      }
    ],
    metafields: [
      {
        namespace: 'custom',
        key: 'your_key',
        value: 'your_value',
        type: 'single_line_text_field'
      }
    ]
  }
];
```

### Metafield Types

Supported metafield types:

- `single_line_text_field` - Text
- `multi_line_text_field` - Long text
- `number_integer` - Integer number
- `number_decimal` - Decimal number
- `boolean` - True/False
- `date` - Date
- `date_time` - Date and time
- `url` - URL
- `json` - JSON data

## 📚 Resources

- [Shopify REST Admin API](https://shopify.dev/docs/api/admin-rest)
- [Product API Reference](https://shopify.dev/docs/api/admin-rest/latest/resources/product)
- [Metafields Guide](https://shopify.dev/docs/apps/build/custom-data/metafields)

## 🆘 Need Help?

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review the error message in the console output
3. Verify your API token and permissions
4. Check [Shopify's API documentation](https://shopify.dev/docs/api)

---

**Created by:** NERDX Development Team
**Last Updated:** 2025-10-11
