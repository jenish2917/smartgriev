import { Page, expect } from '@playwright/test';

/**
 * Test Helper Functions
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Generate unique test email
   */
  static generateTestEmail(): string {
    const timestamp = Date.now();
    return `test.user.${timestamp}@smartgriev.test`;
  }

  /**
   * Generate test mobile number
   */
  static generateTestMobile(): string {
    const random = Math.floor(Math.random() * 1000000000);
    return `91${random.toString().padStart(10, '0')}`;
  }

  /**
   * Wait for API response
   */
  async waitForAPIResponse(urlPattern: string | RegExp, timeout: number = 10000) {
    return await this.page.waitForResponse(
      response => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  }

  /**
   * Fill form and submit
   */
  async fillAndSubmitForm(formData: Record<string, string>, submitButtonText: string = 'Submit') {
    for (const [name, value] of Object.entries(formData)) {
      const input = this.page.locator(`input[name="${name}"], textarea[name="${name}"], select[name="${name}"]`).first();
      await input.fill(value);
    }
    await this.page.getByRole('button', { name: submitButtonText }).click();
  }

  /**
   * Take screenshot with timestamp
   */
  async takeScreenshot(name: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({ 
      path: `reports/screenshots/${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Wait for toast/notification
   */
  async waitForNotification(message?: string) {
    const notification = this.page.locator('.ant-notification, .toast, [role="alert"]').first();
    await notification.waitFor({ state: 'visible', timeout: 5000 });
    
    if (message) {
      await expect(notification).toContainText(message);
    }
    
    return notification;
  }

  /**
   * Get browser location permission
   */
  async mockGeolocation(latitude: number = 19.0760, longitude: number = 72.8777) {
    await this.page.context().setGeolocation({ latitude, longitude });
    await this.page.context().grantPermissions(['geolocation']);
  }

  /**
   * Upload file
   */
  async uploadFile(selectorOrLabel: string, filePath: string) {
    const fileInput = this.page.locator(`input[type="file"]${selectorOrLabel.startsWith('#') || selectorOrLabel.startsWith('.') ? selectorOrLabel : ''}`).first();
    await fileInput.setInputFiles(filePath);
  }

  /**
   * Wait for element and click
   */
  async clickElement(selector: string) {
    const element = this.page.locator(selector).first();
    await element.waitFor({ state: 'visible' });
    await element.click();
  }

  /**
   * Check if element exists
   */
  async elementExists(selector: string): Promise<boolean> {
    try {
      await this.page.locator(selector).first().waitFor({ state: 'attached', timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get element text
   */
  async getElementText(selector: string): Promise<string> {
    const element = this.page.locator(selector).first();
    return await element.textContent() || '';
  }

  /**
   * Wait for loading to finish
   */
  async waitForLoadingComplete() {
    // Wait for common loading indicators to disappear
    const loadingSelectors = [
      '.loading',
      '.spinner',
      '.ant-spin',
      '[data-testid="loading"]',
      '.skeleton'
    ];

    for (const selector of loadingSelectors) {
      try {
        await this.page.locator(selector).waitFor({ state: 'hidden', timeout: 2000 });
      } catch {
        // Ignore if selector doesn't exist
      }
    }
  }

  /**
   * Switch language
   */
  async switchLanguage(languageCode: string) {
    // Look for language switcher
    const languageSwitcher = this.page.locator('[data-testid="language-switcher"], .language-selector').first();
    await languageSwitcher.click();
    
    // Select language
    await this.page.locator(`[data-lang="${languageCode}"]`).click();
    
    // Wait for page to update
    await this.page.waitForTimeout(1000);
  }

  /**
   * Login helper
   */
  async login(email: string, password: string) {
    await this.page.goto('/login');
    await this.page.fill('input[name="email"], input[type="email"]', email);
    await this.page.fill('input[name="password"], input[type="password"]', password);
    await this.page.locator('button[type="submit"]').click();
    
    // Wait for redirect to home page (user confirmed redirect goes to /home)
    await this.page.waitForURL(/home/i, { timeout: 10000 });
  }

  /**
   * Logout helper
   */
  async logout() {
    // Look for logout button (might be in dropdown)
    const logoutButton = this.page.getByRole('button', { name: /logout|sign out/i });
    
    try {
      await logoutButton.click({ timeout: 2000 });
    } catch {
      // Try clicking profile menu first
      await this.page.locator('[data-testid="user-menu"], .user-profile').first().click();
      await this.page.getByRole('menuitem', { name: /logout|sign out/i }).click();
    }
    
    // Wait for redirect to login
    await this.page.waitForURL(/login|auth/i, { timeout: 5000 });
  }

  /**
   * Get current URL path
   */
  getCurrentPath(): string {
    return new URL(this.page.url()).pathname;
  }

  /**
   * Wait for network idle
   */
  async waitForNetworkIdle(timeout: number = 5000) {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Console log capture
   */
  setupConsoleCapture() {
    const logs: { type: string; message: string }[] = [];
    
    this.page.on('console', msg => {
      logs.push({
        type: msg.type(),
        message: msg.text()
      });
    });

    return logs;
  }

  /**
   * Check for JavaScript errors
   */
  setupErrorCapture() {
    const errors: string[] = [];
    
    this.page.on('pageerror', error => {
      errors.push(error.message);
    });

    return errors;
  }
}

/**
 * API Helper for direct API calls
 */
export class APIHelper {
  constructor(private baseURL: string = 'http://localhost:8000') {}

  async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    return {
      status: response.status,
      ok: response.ok,
      data: await response.json().catch(() => null),
    };
  }

  async get(endpoint: string, token?: string) {
    return this.request(endpoint, {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async post(endpoint: string, data: any, token?: string) {
    return this.request(endpoint, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: JSON.stringify(data),
    });
  }
}
