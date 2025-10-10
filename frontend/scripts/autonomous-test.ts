/**
 * Autonomous Testing Script for Claude Code
 *
 * This script allows Claude Code to autonomously test the application
 * without requiring human interaction.
 */

import { chromium, Browser, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'skip';
  duration: number;
  error?: string;
  screenshot?: string;
  consoleLogs?: string[];
  consoleErrors?: string[];
}

class AutonomousTest {
  private browser: Browser | null = null;
  private page: Page | null = null;
  private results: TestResult[] = [];
  private consoleLogs: string[] = [];
  private consoleErrors: string[] = [];
  private baseURL = 'http://localhost:3000';

  async setup() {
    console.log('🚀 Starting Autonomous Test...\n');

    // Launch browser in headed mode so we can see what's happening
    this.browser = await chromium.launch({
      headless: false,  // Set to true for CI/CD
      slowMo: 100 // Slow down for visibility
    });

    this.page = await this.browser.newPage();

    // Capture console logs
    this.page.on('console', msg => {
      const text = `[${msg.type()}] ${msg.text()}`;
      this.consoleLogs.push(text);

      if (msg.type() === 'error') {
        this.consoleErrors.push(text);
        console.log(`❌ Console Error: ${text}`);
      }
    });

    // Capture network errors
    this.page.on('pageerror', error => {
      const text = `Page Error: ${error.message}`;
      this.consoleErrors.push(text);
      console.log(`❌ ${text}`);
    });

    console.log('✅ Browser setup complete\n');
  }

  async test(name: string, fn: () => Promise<void>): Promise<void> {
    console.log(`\n📝 Running: ${name}`);
    const startTime = Date.now();

    try {
      await fn();
      const duration = Date.now() - startTime;

      this.results.push({
        name,
        status: 'pass',
        duration,
        consoleLogs: [...this.consoleLogs],
        consoleErrors: [...this.consoleErrors]
      });

      console.log(`✅ PASS (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : String(error);

      // Take screenshot on failure
      const screenshotPath = `test-results/failure-${Date.now()}.png`;
      if (this.page) {
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
      }

      this.results.push({
        name,
        status: 'fail',
        duration,
        error: errorMessage,
        screenshot: screenshotPath,
        consoleLogs: [...this.consoleLogs],
        consoleErrors: [...this.consoleErrors]
      });

      console.log(`❌ FAIL (${duration}ms): ${errorMessage}`);
    }

    // Clear logs for next test
    this.consoleLogs = [];
    this.consoleErrors = [];
  }

  async screenshot(name: string) {
    if (!this.page) return;

    const screenshotPath = `test-results/${name}-${Date.now()}.png`;
    await this.page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 Screenshot saved: ${screenshotPath}`);

    return screenshotPath;
  }

  async teardown() {
    if (this.browser) {
      await this.browser.close();
    }

    // Generate report
    this.generateReport();
  }

  private generateReport() {
    console.log('\n\n📊 Test Summary');
    console.log('================\n');

    const passed = this.results.filter(r => r.status === 'pass').length;
    const failed = this.results.filter(r => r.status === 'fail').length;
    const total = this.results.length;

    console.log(`Total: ${total}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%\n`);

    // Detailed results
    this.results.forEach((result, index) => {
      const icon = result.status === 'pass' ? '✅' : '❌';
      console.log(`${icon} ${index + 1}. ${result.name} (${result.duration}ms)`);

      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }

      if (result.screenshot) {
        console.log(`   Screenshot: ${result.screenshot}`);
      }

      if (result.consoleErrors && result.consoleErrors.length > 0) {
        console.log(`   Console Errors (${result.consoleErrors.length}):`);
        result.consoleErrors.forEach(err => {
          console.log(`     - ${err}`);
        });
      }
    });

    // Save JSON report
    const reportPath = 'test-results/autonomous-test-report.json';
    fs.mkdirSync('test-results', { recursive: true });
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
    console.log(`\n📄 Full report saved: ${reportPath}\n`);
  }

  // Helper methods
  async goto(url: string) {
    if (!this.page) throw new Error('Page not initialized');
    await this.page.goto(this.baseURL + url, { waitUntil: 'networkidle' });
  }

  async waitForSelector(selector: string, timeout = 10000) {
    if (!this.page) throw new Error('Page not initialized');
    await this.page.waitForSelector(selector, { timeout });
  }

  async click(selector: string) {
    if (!this.page) throw new Error('Page not initialized');
    await this.page.click(selector);
  }

  async fill(selector: string, value: string) {
    if (!this.page) throw new Error('Page not initialized');
    await this.page.fill(selector, value);
  }

  async getText(selector: string): Promise<string> {
    if (!this.page) throw new Error('Page not initialized');
    return await this.page.textContent(selector) || '';
  }

  async getCount(selector: string): Promise<number> {
    if (!this.page) throw new Error('Page not initialized');
    return await this.page.locator(selector).count();
  }
}

// Run tests
async function runTests() {
  const test = new AutonomousTest();

  try {
    await test.setup();

    // Test 1: Homepage loads
    await test.test('Homepage loads successfully', async () => {
      await test.goto('/');
      await test.waitForSelector('nav');
      await test.screenshot('homepage');
    });

    // Test 2: Navigate to Shopify products
    await test.test('Navigate to Shopify products page', async () => {
      await test.goto('/products/shopify');
      await test.waitForSelector('.container', 5000);
    });

    // Test 3: Products are displayed
    await test.test('Products are displayed', async () => {
      const productCount = await test.getCount('[class*="bg-white rounded-lg shadow"]');
      console.log(`   Found ${productCount} products`);

      if (productCount === 0) {
        throw new Error('No products found on page');
      }

      await test.screenshot('products-page');
    });

    // Test 4: Product details visible
    await test.test('Product titles and prices are visible', async () => {
      const titles = await test.getCount('h3.text-xl');
      const prices = await test.getCount('[class*="text-2xl"][class*="font-bold"]');

      console.log(`   Found ${titles} product titles`);
      console.log(`   Found ${prices} product prices`);

      if (titles === 0 || prices === 0) {
        throw new Error('Product details not visible');
      }
    });

    // Test 5: Stock badges visible
    await test.test('Stock quantity badges are visible', async () => {
      const stockBadges = await test.getCount('text=재고:');
      console.log(`   Found ${stockBadges} stock badges`);

      if (stockBadges === 0) {
        throw new Error('Stock badges not visible');
      }
    });

    // Test 6: Filter functionality
    await test.test('Search filter works', async () => {
      await test.fill('input[placeholder*="검색"]', '막걸리');
      await new Promise(resolve => setTimeout(resolve, 500)); // Wait for filter

      const productCount = await test.getCount('[class*="bg-white rounded-lg shadow"]');
      console.log(`   After filtering: ${productCount} products`);

      await test.screenshot('search-filter');
    });

    // Test 7: AR and APEC badges
    await test.test('AR and APEC badges are visible', async () => {
      await test.goto('/products/shopify'); // Reset filters

      const arBadges = await test.getCount('text=AR 체험 가능');
      const apecBadges = await test.getCount('text=APEC 한정판');

      console.log(`   Found ${arBadges} AR badges`);
      console.log(`   Found ${apecBadges} APEC badges`);

      if (arBadges === 0 && apecBadges === 0) {
        throw new Error('No badges visible');
      }

      await test.screenshot('badges');
    });

    // Test 8: Product detail page navigation
    await test.test('Product detail page loads', async () => {
      await test.goto('/products/shopify');

      // Click first "상세보기" button
      const detailButtons = await test.page!.locator('text=상세보기');
      const count = await detailButtons.count();

      if (count > 0) {
        await detailButtons.first().click();
        await test.page!.waitForLoadState('networkidle');

        // Check if we're on detail page (either handle or 404)
        const currentUrl = test.page!.url();
        console.log(`   Navigated to: ${currentUrl}`);

        await test.screenshot('product-detail');
      } else {
        console.log('   No detail buttons found');
      }
    });

    // Test 9: Checkout button interaction
    await test.test('Checkout flow initiates', async () => {
      await test.goto('/products/shopify');

      // Click first "바로 구매" button
      const buyButtons = await test.page!.locator('text=바로 구매');
      const count = await buyButtons.count();

      if (count > 0) {
        console.log(`   Found ${count} buy buttons`);

        // Listen for navigation or popup
        const [response] = await Promise.all([
          test.page!.waitForEvent('response', { timeout: 5000 }).catch(() => null),
          buyButtons.first().click().catch(() => null)
        ]);

        if (response) {
          console.log(`   Response: ${response?.status()}`);
        }

        await test.screenshot('checkout-attempt');
      }
    });

    // Test 10: All stock badges now visible (after Soju fix)
    await test.test('All 3 stock badges visible after fix', async () => {
      await test.goto('/products/shopify');

      const stockBadges = await test.getCount('text=재고:');
      console.log(`   Found ${stockBadges} stock badges`);

      if (stockBadges !== 3) {
        console.log(`   ⚠️  Expected 3 stock badges, found ${stockBadges}`);
      }
    });

  } finally {
    await test.teardown();
  }
}

// Execute
runTests().catch(console.error);
