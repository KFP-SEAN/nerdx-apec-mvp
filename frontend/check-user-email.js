/**
 * Check if a specific user email is registered in Shopify
 */

const email = process.argv[2];

if (!email) {
  console.log('Usage: node check-user-email.js <email>');
  console.log('Example: node check-user-email.js user@example.com');
  process.exit(1);
}

// Use the existing check script
const { execSync } = require('child_process');

console.log(`\n🔍 Checking if "${email}" is registered in Shopify...\n`);

try {
  const result = execSync(
    `node check-shopify-customer.js "${email}"`,
    { encoding: 'utf-8' }
  );
  console.log(result);
} catch (error) {
  console.log('Error checking email:', error.message);
}
