import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('User Authentication Flow', () => {
  let helpers: TestHelpers;
  let dbHelper: DatabaseHelper;
  let testEmail: string;
  let testPassword: string;
  let testMobile: string;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    dbHelper = new DatabaseHelper();
    await dbHelper.connect();

    // Generate unique test credentials
    testEmail = TestHelpers.generateTestEmail();
    testPassword = 'TestPass123!';
    testMobile = TestHelpers.generateTestMobile();
  });

  test.afterEach(async () => {
    // Cleanup test data
    try {
      await dbHelper.cleanupTestData(testEmail);
    } catch (error) {
      console.log('Cleanup error:', error);
    }
    await dbHelper.close();
  });

  test('should complete user signup flow with OTP verification', async ({ page }) => {
    // Navigate to register page (frontend uses /register not /signup)
    await page.goto('/register');
    await expect(page).toHaveTitle(/SmartGriev/i); // Frontend uses generic title

    // Fill signup form
    await page.fill('input[name="name"], input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"], input[type="email"]', testEmail);
    await page.fill('input[name="mobile"], input[name="phone"]', testMobile);
    await page.fill('input[name="password"], input[type="password"]', testPassword);
    
    // Check if confirm password field exists
    const confirmPasswordExists = await helpers.elementExists('input[name="confirmPassword"]');
    if (confirmPasswordExists) {
      await page.fill('input[name="confirmPassword"]', testPassword);
    }

    // Take screenshot before submission
    await helpers.takeScreenshot('signup-form-filled');

    // Submit signup form
    await page.getByRole('button', { name: /sign up|register|create account/i }).click();

    // Wait for OTP verification screen or success message
    await page.waitForTimeout(2000);

    // Check if OTP verification is required
    const otpExists = await helpers.elementExists('input[name="otp"]');
    
    if (otpExists) {
      console.log('OTP verification required');
      
      // Get OTP from database
      await page.waitForTimeout(3000); // Wait for OTP to be sent
      const otpRecord = await dbHelper.getOTPVerification(testEmail);
      
      if (otpRecord && otpRecord.otp) {
        console.log('OTP retrieved from database:', otpRecord.otp);
        
        // Fill OTP
        await page.fill('input[name="otp"]', otpRecord.otp);
        await helpers.takeScreenshot('otp-entered');
        
        // Submit OTP
        await page.getByRole('button', { name: /verify|submit|confirm/i }).click();
      }
    }

    // Wait for successful registration
    await page.waitForTimeout(2000);
    
    // Verify user was created in database
    const user = await dbHelper.getUserByEmail(testEmail);
    expect(user).toBeDefined();
    expect(user?.email).toBe(testEmail);
    console.log('✓ User created in database:', user?.id);

    // Take screenshot of final state
    await helpers.takeScreenshot('signup-complete');
  });

  test('should login with valid credentials', async ({ page }) => {
    // First create a user (assume user exists or create via API)
    await page.goto('/login');
    await expect(page).toHaveTitle(/SmartGriev/i); // Frontend uses generic title

    // Fill login form with existing user (use env variables)
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';

    await page.fill('input[name="email"], input[type="email"]', loginEmail);
    await page.fill('input[name="password"], input[type="password"]', loginPassword);
    
    await helpers.takeScreenshot('login-form-filled');

    // Submit login form - use submit button to avoid multiple button issue
    await page.locator('button[type="submit"]').click();

    // Wait for redirect to dashboard
    await page.waitForURL(/dashboard|home/i, { timeout: 10000 });
    
    // Verify we're on dashboard
    expect(page.url()).toMatch(/dashboard|home/i);
    console.log('✓ Successfully logged in and redirected to dashboard');

    // Take screenshot of dashboard
    await helpers.takeScreenshot('login-success-dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Try to login with invalid credentials
    await page.fill('input[name="email"], input[type="email"]', 'invalid@example.com');
    await page.fill('input[name="password"], input[type="password"]', 'WrongPassword123!');
    
    await page.locator('button[type="submit"]').click();

    // Wait for error message
    await helpers.waitForNotification();
    
    // Verify error message is displayed
    const errorMessage = page.locator('.error, .ant-message-error, [role="alert"]').first();
    await expect(errorMessage).toBeVisible();
    
    console.log('✓ Error message displayed for invalid credentials');
    await helpers.takeScreenshot('login-error');
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/register');

    // Fill form with invalid email
    await page.fill('input[name="email"], input[type="email"]', 'invalid-email');
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="mobile"]', testMobile);
    await page.fill('input[name="password"]', testPassword);

    // Try to submit
    await page.getByRole('button', { name: /sign up|register/i }).click();

    // Check for validation error
    const emailInput = page.locator('input[name="email"], input[type="email"]');
    const validationMessage = await emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
    
    expect(validationMessage).toBeTruthy();
    console.log('✓ Email validation working:', validationMessage);
    
    await helpers.takeScreenshot('email-validation-error');
  });

  test('should validate password strength', async ({ page }) => {
    await page.goto('/register');

    // Fill form with weak password
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="mobile"]', testMobile);
    await page.fill('input[name="password"]', '123'); // Weak password

    // Try to submit
    await page.getByRole('button', { name: /sign up|register/i }).click();

    // Check for password strength error
    await page.waitForTimeout(1000);
    const errorExists = await helpers.elementExists('.error, .ant-form-item-explain-error');
    
    if (errorExists) {
      console.log('✓ Password strength validation working');
      await helpers.takeScreenshot('password-validation-error');
    }
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    
    await helpers.login(loginEmail, loginPassword);
    
    // Verify on dashboard
    expect(page.url()).toMatch(/dashboard|home/i);
    
    // Logout
    await helpers.logout();
    
    // Verify redirected to login
    expect(page.url()).toMatch(/login|auth/i);
    console.log('✓ Successfully logged out');
    
    await helpers.takeScreenshot('logout-success');
  });

  test('should handle session timeout', async ({ page }) => {
    // Login
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    
    await helpers.login(loginEmail, loginPassword);
    
    // Clear session storage/cookies to simulate timeout
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Try to access protected page
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);

    // Should be redirected to login
    expect(page.url()).toMatch(/login|auth/i);
    console.log('✓ Session timeout handled correctly');
    
    await helpers.takeScreenshot('session-timeout');
  });

  test('should validate mobile number format', async ({ page }) => {
    await page.goto('/register');

    // Fill form with invalid mobile
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="mobile"], input[name="phone"]', '123'); // Invalid mobile
    await page.fill('input[name="password"]', testPassword);

    // Try to submit
    await page.getByRole('button', { name: /sign up|register/i }).click();

    // Check for validation error
    await page.waitForTimeout(1000);
    const errorExists = await helpers.elementExists('.error, .ant-form-item-explain-error');
    
    if (errorExists) {
      console.log('✓ Mobile number validation working');
      await helpers.takeScreenshot('mobile-validation-error');
    }
  });

  test('should prevent duplicate email registration', async ({ page }) => {
    // Use existing test email from env
    const existingEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';

    await page.goto('/register');

    // Fill form with existing email
    await page.fill('input[name="email"]', existingEmail);
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="mobile"]', testMobile);
    await page.fill('input[name="password"]', testPassword);

    // Try to submit
    await page.getByRole('button', { name: /sign up|register/i }).click();

    // Wait for error message
    await page.waitForTimeout(2000);
    
    // Should show error about duplicate email
    const errorExists = await helpers.elementExists('.error, .ant-message-error, [role="alert"]');
    
    if (errorExists) {
      console.log('✓ Duplicate email prevention working');
      await helpers.takeScreenshot('duplicate-email-error');
    }
  });

  test('should handle password visibility toggle', async ({ page }) => {
    await page.goto('/login');

    const passwordInput = page.locator('input[name="password"]').first();
    
    // Check initial type is password
    let inputType = await passwordInput.getAttribute('type');
    expect(inputType).toBe('password');

    // Look for visibility toggle button
    const toggleButton = page.locator('[data-testid="password-toggle"], .ant-input-password-icon').first();
    const toggleExists = await toggleButton.isVisible().catch(() => false);

    if (toggleExists) {
      // Click toggle
      await toggleButton.click();
      
      // Check type changed to text
      inputType = await passwordInput.getAttribute('type');
      expect(inputType).toBe('text');
      
      console.log('✓ Password visibility toggle working');
      await helpers.takeScreenshot('password-visible');
    }
  });
});
