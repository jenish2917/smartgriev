/**
 * Test Logger Utility
 * Provides consistent, structured logging for E2E tests
 * Usage: import { TestLogger } from '../utils/testLogger'
 */

export class TestLogger {
  private testName: string;
  private startTime: number;

  constructor(testName: string) {
    this.testName = testName;
    this.startTime = Date.now();
  }

  /**
   * Log test start
   */
  start() {
    console.log('\n' + '='.repeat(80));
    console.log(`🚀 STARTING TEST: ${this.testName}`);
    console.log(`⏰ Timestamp: ${new Date().toISOString()}`);
    console.log('='.repeat(80));
  }

  /**
   * Log a test step
   */
  step(stepNumber: number, description: string) {
    console.log(`\n📍 STEP ${stepNumber}: ${description}`);
  }

  /**
   * Log a detailed action
   */
  action(action: string, details?: any) {
    console.log(`   ➤ ${action}`);
    if (details) {
      console.log(`      Details:`, JSON.stringify(details, null, 2));
    }
  }

  /**
   * Log element found
   */
  elementFound(selector: string) {
    console.log(`   ✓ Element found: ${selector}`);
  }

  /**
   * Log element not found
   */
  elementNotFound(selector: string) {
    console.log(`   ✗ Element NOT found: ${selector}`);
  }

  /**
   * Log navigation
   */
  navigate(url: string) {
    console.log(`   🌐 Navigating to: ${url}`);
  }

  /**
   * Log page load
   */
  pageLoad(state: string, duration?: number) {
    const durationStr = duration ? ` (${duration}ms)` : '';
    console.log(`   📄 Page load state: ${state}${durationStr}`);
  }

  /**
   * Log API call
   */
  apiCall(method: string, endpoint: string, status?: number) {
    const statusStr = status ? ` - Status: ${status}` : '';
    console.log(`   🔌 API Call: ${method} ${endpoint}${statusStr}`);
  }

  /**
   * Log assertion
   */
  assert(condition: string, result: boolean) {
    const symbol = result ? '✓' : '✗';
    console.log(`   ${symbol} Assert: ${condition}`);
  }

  /**
   * Log success
   */
  success(message: string) {
    console.log(`\n✅ SUCCESS: ${message}`);
  }

  /**
   * Log warning
   */
  warn(message: string) {
    console.log(`\n⚠️  WARNING: ${message}`);
  }

  /**
   * Log error
   */
  error(message: string, error?: any) {
    console.log(`\n❌ ERROR: ${message}`);
    if (error) {
      console.log(`   Error details:`, error);
      if (error.stack) {
        console.log(`   Stack trace:`, error.stack);
      }
    }
  }

  /**
   * Log test completion
   */
  complete(passed: boolean) {
    const duration = Date.now() - this.startTime;
    const status = passed ? '✅ PASSED' : '❌ FAILED';
    console.log('\n' + '='.repeat(80));
    console.log(`${status}: ${this.testName}`);
    console.log(`⏱️  Duration: ${duration}ms (${(duration / 1000).toFixed(2)}s)`);
    console.log('='.repeat(80) + '\n');
  }

  /**
   * Log page state
   */
  async logPageState(page: any) {
    try {
      const url = page.url();
      const title = await page.title();
      console.log(`   📊 Page State:`);
      console.log(`      URL: ${url}`);
      console.log(`      Title: ${title}`);
    } catch (error) {
      console.log(`   ⚠️  Could not log page state:`, error);
    }
  }

  /**
   * Log network activity
   */
  logNetwork(type: 'request' | 'response', url: string, method?: string, status?: number) {
    if (type === 'request') {
      console.log(`   📤 Request: ${method} ${url}`);
    } else {
      console.log(`   📥 Response: ${url} - Status: ${status}`);
    }
  }

  /**
   * Log browser console messages
   */
  logConsole(type: string, message: string) {
    const icon = type === 'error' ? '🔴' : type === 'warning' ? '🟡' : '⚪';
    console.log(`   ${icon} Browser Console [${type}]: ${message}`);
  }

  /**
   * Log screenshot taken
   */
  screenshot(path: string) {
    console.log(`   📸 Screenshot saved: ${path}`);
  }

  /**
   * Log video recording
   */
  video(path: string) {
    console.log(`   🎥 Video saved: ${path}`);
  }

  /**
   * Log waiting
   */
  waiting(what: string, timeout?: number) {
    const timeoutStr = timeout ? ` (timeout: ${timeout}ms)` : '';
    console.log(`   ⏳ Waiting for: ${what}${timeoutStr}`);
  }

  /**
   * Log retry attempt
   */
  retry(attempt: number, maxAttempts: number, action: string) {
    console.log(`   🔄 Retry ${attempt}/${maxAttempts}: ${action}`);
  }
}

/**
 * Helper function to create a test logger
 */
export function createLogger(testName: string): TestLogger {
  return new TestLogger(testName);
}
