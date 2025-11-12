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
   * Generate test mobile number with country code
   * For India (+91): Must be 10 digits starting with 6-9
   */
  static generateTestMobile(): string {
    // Generate 9 random digits
    const remaining9Digits = Math.floor(Math.random() * 1000000000).toString().padStart(9, '0');
    // Start with 6, 7, 8, or 9 (valid Indian mobile prefixes)
    const firstDigit = [6, 7, 8, 9][Math.floor(Math.random() * 4)];
    return `+91${firstDigit}${remaining9Digits}`;
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
    const notification = this.page.locator('.ant-notification, .toast, [role="alert"], .ant-alert').first();
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
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"], input[type="password"]', password);
    await this.page.locator('button[type="submit"]').click();

    // Wait for redirect to dashboard or home page
    try {
      await this.page.waitForURL(/(home|dashboard)/i, { timeout: 15000 });
    } catch (error) {
      // If not redirected, might be on verification page or error
      const currentUrl = this.page.url();
      console.log('Login redirect failed. Current URL:', currentUrl);
      throw error;
    }
  }

  /**
   * Register a new user (with OTP handling)
   */
  async registerUser(userData: {
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    password: string;
    address?: string;
  }, dbHelper?: any) {
    await this.page.goto('/register');
    await this.page.waitForLoadState('domcontentloaded');

    // Generate username from email if not provided
    const username = userData.email.split('@')[0];
    console.log('Registering user with username:', username, 'email:', userData.email);

    // Fill registration form
    await this.page.fill('input[name="firstName"]', userData.firstName);
    await this.page.fill('input[name="lastName"]', userData.lastName);
    await this.page.fill('input[name="email"]', userData.email);
    
    // Fill username if field exists (backend requires it)
    const usernameExists = await this.elementExists('input[name="username"]');
    if (usernameExists) {
      await this.page.fill('input[name="username"]', username);
      console.log('✓ Username field filled');
    }
    
    // Handle country code selector if it exists
    const countryCodeExists = await this.elementExists('select[name="countryCode"]');
    if (countryCodeExists) {
      await this.page.selectOption('select[name="countryCode"]', '+91'); // Default to India
      console.log('✓ Country code set to +91');
    }
    
    // Fill phone number (without country code as it's in separate field)
    const phoneNumber = userData.phone.startsWith('+91') ? userData.phone.substring(3) : userData.phone;
    await this.page.fill('input[name="phone"]', phoneNumber);
    console.log('✓ Phone number filled:', phoneNumber);
    await this.page.fill('input[name="password"]', userData.password);

    // Fill confirm password if it exists
    const confirmPasswordExists = await this.elementExists('input[name="confirmPassword"]');
    if (confirmPasswordExists) {
      await this.page.fill('input[name="confirmPassword"]', userData.password);
    }

    // Fill address if provided and field exists
    if (userData.address) {
      const addressExists = await this.elementExists('input[name="address"]');
      if (addressExists) {
        await this.page.fill('input[name="address"]', userData.address);
      }
    }

    // Accept terms and conditions (REQUIRED)
    const termsExists = await this.elementExists('input[name="acceptTerms"]');
    if (termsExists) {
      await this.page.check('input[name="acceptTerms"]');
      console.log('✓ Terms accepted');
    } else {
      console.warn('⚠️ Terms checkbox not found');
    }

    // Submit form and wait for API response
    console.log('Submitting registration form...');
    const responsePromise = this.page.waitForResponse(
      response => response.url().includes('/api/auth/register') && response.status() !== 0,
      { timeout: 10000 }
    );
    
    await this.page.locator('button[type="submit"]').first().click();
    
    // Wait for API response
    try {
      const response = await responsePromise;
      const status = response.status();
      console.log('Registration API response status:', status);
      
      if (status >= 200 && status < 300) {
        console.log('✓ Registration API call successful');
        const body = await response.json();
        console.log('Registration response:', JSON.stringify(body).substring(0, 200));
      } else {
        console.error('❌ Registration API call failed with status:', status);
        const errorBody = await response.text();
        console.error('Error response:', errorBody.substring(0, 500));
      }
    } catch (error) {
      console.warn('Could not capture registration API response:', error);
    }
    
    // Wait for response to process
    await this.page.waitForTimeout(2000);

    // Handle OTP verification if required
    const otpExists = await this.elementExists('input[name="otp"]');
    if (otpExists && dbHelper) {
      console.log('OTP verification required');
      await this.page.waitForTimeout(2000); // Wait for OTP to be sent
      
      try {
        const otpRecord = await dbHelper.getOTPVerification(userData.email);
        if (otpRecord && otpRecord.otp) {
          console.log('OTP retrieved:', otpRecord.otp);
          await this.page.fill('input[name="otp"]', otpRecord.otp);
          await this.page.locator('button[type="submit"]').click();
          await this.page.waitForTimeout(2000);
        }
      } catch (error) {
        console.warn('Could not retrieve OTP:', error);
      }
    }

    return true;
  }

  /**
   * Logout helper
   */
  async logout() {
    // Look for logout button (might be in dropdown)
    try {
      // First try direct logout button
      const directLogout = this.page.getByRole('button', { name: /logout|sign out/i });
      await directLogout.click({ timeout: 2000 });
    } catch {
      try {
        // Try clicking profile menu/user menu first
        const profileMenu = this.page.locator('[data-testid="user-menu"], .user-profile, .user-dropdown').first();
        await profileMenu.click({ timeout: 2000 });
        await this.page.waitForTimeout(500);
        await this.page.getByRole('menuitem', { name: /logout|sign out/i }).click();
      } catch (error) {
        console.warn('Could not find logout button:', error);
        // As fallback, clear session and navigate to login
        await this.page.context().clearCookies();
        await this.page.evaluate(() => {
          localStorage.clear();
          sessionStorage.clear();
        });
        await this.page.goto('/login');
        return;
      }
    }
    
    // Wait for redirect to login
    await this.page.waitForURL(/login|auth|^\/$/i, { timeout: 5000 });
  }

  /**
   * Ensure test user exists (create if doesn't exist)
   */
  async ensureUserExists(email: string, password: string, mobile: string, dbHelper: any) {
    try {
      const user = await dbHelper.getUserByEmail(email);
      if (user && user.is_active) {
        console.log('✓ Test user exists and is active:', email);
        return true;
      }

      if (user && !user.is_active) {
        console.log('⚠️ Test user exists but is inactive, activating:', email);
        // Activate the user directly in database
        try {
          const result = await dbHelper.query(
            'UPDATE authentication_user SET is_active = true WHERE email = $1 RETURNING id, email, is_active',
            [email]
          );
          console.log('SQL Update Result:', result);
          console.log('✓ Test user activated');
          return true;
        } catch (sqlError) {
          console.error('Failed to activate user via SQL:', sqlError);
          // Try alternative: clear and recreate
          console.log('Attempting to delete and recreate user...');
          await dbHelper.query('DELETE FROM authentication_user WHERE email = $1', [email]);
        }
      }

      console.log('⚠️ Test user does not exist, creating:', email);
      
      // Create user via registration
      await this.registerUser({
        firstName: 'Test',
        lastName: 'User',
        email: email,
        phone: mobile,
        password: password,
        address: '123 Test Street'
      }, dbHelper);

      // Wait for user to be saved in DB
      console.log('Waiting for user to be saved in database...');
      await this.page.waitForTimeout(3000);
      
      // Verify user was created
      const newUser = await dbHelper.getUserByEmail(email);
      if (!newUser) {
        console.error('❌ User was not created in database!');
        return false;
      }
      
      console.log('User found in DB:', newUser);

      // Activate the newly created user immediately (bypass email verification for tests)
      if (!newUser.is_active) {
        console.log('Activating newly created test user via SQL...');
        try {
          const activateResult = await dbHelper.query(
            'UPDATE authentication_user SET is_active = true WHERE email = $1 RETURNING id, is_active',
            [email]
          );
          console.log('Activation result:', activateResult);
          
          // Verify activation worked
          const verifyUser = await dbHelper.getUserByEmail(email);
          console.log('User after activation:', verifyUser);
          
          if (verifyUser && verifyUser.is_active) {
            console.log('✓ Test user created and activated successfully');
            return true;
          } else {
            console.error('❌ User activation failed - is_active still false');
            return false;
          }
        } catch (activateError) {
          console.error('Failed to activate user:', activateError);
          return false;
        }
      } else {
        console.log('✓ Test user was created and is already active');
        return true;
      }
    } catch (error) {
      console.error('Failed to ensure user exists:', error);
      return false;
    }
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
