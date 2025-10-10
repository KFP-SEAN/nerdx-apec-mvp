# Autonomous Testing Guide

## Overview

This guide explains the autonomous testing system developed for Claude Code to enable self-testing and debugging without human interaction.

## What is Autonomous Testing?

Autonomous testing allows Claude Code to:
- Run end-to-end tests independently
- Capture screenshots automatically
- Monitor console errors and logs
- Generate detailed test reports
- Identify and diagnose issues autonomously

## Architecture

### Components

1. **Test Runner** (`scripts/autonomous-test.ts`)
   - Playwright-based browser automation
   - Screenshot capture on failure
   - Console log monitoring
   - JSON report generation

2. **Test Suite**
   - 10 comprehensive E2E tests
   - Product listing verification
   - Search and filter functionality
   - Stock badge validation
   - AR/APEC badge verification
   - Navigation and checkout flows

3. **Reporting System**
   - Real-time console output
   - Screenshot artifacts
   - JSON test results
   - Pass/fail statistics

## Running Autonomous Tests

### Prerequisites

```bash
npm install --save-dev @playwright/test
```

### Execute Tests

```bash
# Start dev server first
npm run dev

# In another terminal, run tests
npx tsx scripts/autonomous-test.ts
```

### Headless Mode (CI/CD)

Edit `scripts/autonomous-test.ts`:

```typescript
this.browser = await chromium.launch({
  headless: true,  // Change to true for CI/CD
  slowMo: 0        // Remove delay
});
```

## Test Structure

### Test Class

```typescript
class AutonomousTest {
  private browser: Browser | null = null;
  private page: Page | null = null;
  private results: TestResult[] = [];
  private consoleLogs: string[] = [];
  private consoleErrors: string[] = [];

  async setup() { /* ... */ }
  async test(name: string, fn: () => Promise<void>) { /* ... */ }
  async teardown() { /* ... */ }
}
```

### Available Helper Methods

- `goto(url: string)` - Navigate to URL
- `waitForSelector(selector: string)` - Wait for element
- `click(selector: string)` - Click element
- `fill(selector: string, value: string)` - Fill input
- `getText(selector: string)` - Get element text
- `getCount(selector: string)` - Count matching elements
- `screenshot(name: string)` - Capture screenshot

## Current Test Suite

### Test 1: Homepage loads successfully
Verifies the homepage renders without errors.

### Test 2: Navigate to Shopify products page
Confirms navigation to `/products/shopify` works.

### Test 3: Products are displayed
Validates that all 3 products appear on the page.

### Test 4: Product titles and prices are visible
Checks UI elements for product information.

### Test 5: Stock quantity badges are visible
Verifies all stock badges display correctly.

### Test 6: Search filter works
Tests the search functionality with filtering.

### Test 7: AR and APEC badges are visible
Confirms metafield-driven badges appear.

### Test 8: Product detail page loads
Tests navigation to individual product pages.

### Test 9: Checkout flow initiates
Verifies the "바로 구매" button works.

### Test 10: All 3 stock badges visible after fix
Regression test for stock badge display.

## Test Results

### Output Format

```
📊 Test Summary
================

Total: 10
✅ Passed: 9
❌ Failed: 1
Success Rate: 90.0%

✅ 1. Homepage loads successfully (5266ms)
✅ 2. Navigate to Shopify products page (3775ms)
...
```

### JSON Report

Located at `test-results/autonomous-test-report.json`:

```json
[
  {
    "name": "Homepage loads successfully",
    "status": "pass",
    "duration": 5266,
    "consoleLogs": [...],
    "consoleErrors": [...]
  },
  ...
]
```

### Screenshots

- Success: `test-results/{test-name}-{timestamp}.png`
- Failure: `test-results/failure-{timestamp}.png`

## Autonomous Debugging Workflow

### 1. Identify Issue
```bash
npx tsx scripts/autonomous-test.ts
```

### 2. Analyze Results
- Check test summary
- Review console errors
- Examine screenshots

### 3. Diagnose Problem
- Read JSON report
- Inspect failure screenshots
- Trace console logs

### 4. Fix Code
- Make necessary changes
- Verify fix locally

### 5. Re-test
```bash
npx tsx scripts/autonomous-test.ts
```

## Integration with Claude Code

### Autonomous Problem Solving

Claude Code can now:

1. **Run tests independently**
   ```bash
   npx tsx scripts/autonomous-test.ts
   ```

2. **Analyze results**
   - Parse JSON report
   - Read screenshots
   - Identify errors

3. **Make fixes**
   - Edit code autonomously
   - Verify changes

4. **Iterate until passing**
   - Re-run tests
   - Confirm fixes

### Example Session

```
User: "Check if products are displaying correctly"

Claude Code:
1. Runs autonomous test suite
2. Sees 9/10 tests passing
3. Identifies badge visibility issue
4. Examines screenshot
5. Confirms badges ARE visible
6. Concludes test selector needs update
7. Reports findings to user
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install
      - run: npm run dev &
      - run: sleep 5
      - run: npx tsx scripts/autonomous-test.ts
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: test-results
          path: test-results/
```

## Best Practices

### Writing Tests

1. **Clear test names**
   ```typescript
   await test.test('Product images load correctly', async () => {
     // ...
   });
   ```

2. **Wait for elements**
   ```typescript
   await test.waitForSelector('.product-card');
   ```

3. **Capture state**
   ```typescript
   await test.screenshot('before-click');
   await test.click('.button');
   await test.screenshot('after-click');
   ```

4. **Log findings**
   ```typescript
   const count = await test.getCount('.product');
   console.log(`   Found ${count} products`);
   ```

### Debugging Failed Tests

1. **Check screenshots first**
   - Visual confirmation of state
   - Identify UI issues quickly

2. **Review console errors**
   - Network failures
   - JavaScript exceptions
   - API errors

3. **Examine timing issues**
   - Increase waitForSelector timeout
   - Add delays if needed
   - Check for race conditions

## Troubleshooting

### Browser Doesn't Launch

```bash
# Install Playwright browsers
npx playwright install chromium
```

### Port Already in Use

```bash
# Find process on port 3000
netstat -ano | findstr :3000

# Kill process (Windows)
taskkill //PID <PID> //F
```

### Tests Timeout

Increase timeout in test configuration:

```typescript
await test.waitForSelector('.product', 30000); // 30 seconds
```

### Screenshots Not Saving

Ensure directory exists:

```typescript
fs.mkdirSync('test-results', { recursive: true });
```

## Future Enhancements

### Planned Features

- [ ] Parallel test execution
- [ ] Visual regression testing
- [ ] Performance metrics
- [ ] Accessibility audits
- [ ] Cross-browser testing
- [ ] API mocking
- [ ] Test coverage reporting
- [ ] Automatic retry on flaky tests

### Experimental

- [ ] AI-powered test generation
- [ ] Self-healing selectors
- [ ] Autonomous bug fixing
- [ ] Natural language test descriptions

## Metrics

### Current Performance

- **Test Suite Duration**: ~60 seconds
- **Success Rate**: 90%
- **Coverage**: 10 critical paths
- **Screenshot Size**: ~200KB each

### Reliability

- **Flaky Tests**: 1 (AR badge selector)
- **False Positives**: 0
- **False Negatives**: 1

## Conclusion

The autonomous testing system enables Claude Code to:
- Validate changes independently
- Catch regressions early
- Provide visual proof of functionality
- Reduce manual testing overhead

For questions or improvements, see the main project documentation.
