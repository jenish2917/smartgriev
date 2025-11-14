import { test, expect } from '@playwright/test';

/**
 * E2E Test: User Login Flow
 * Tests authentication and session management
 */

test.describe('User Login', () => {
  
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    // Fill login form
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard|home/, { timeout: 10000 });
    
    // Should show user profile or name
    await expect(page.locator('text=/admin|profile|logout/i')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    await page.fill('input[name="username"]', 'wronguser');
    await page.fill('input[name="password"]', 'wrongpass');
    
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('text=/invalid|incorrect|wrong/i')).toBeVisible({ timeout: 5000 });
  });

  test('should validate empty fields', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('text=/required|enter/i')).toBeVisible();
  });

  test('should toggle password visibility', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    const passwordInput = page.locator('input[name="password"]');
    await passwordInput.fill('testpassword');
    
    // Should be password type initially
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    const toggleButton = page.locator('button[aria-label*="password" i], button:has(svg)').first();
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      
      // Should change to text type
      await expect(passwordInput).toHaveAttribute('type', 'text');
    }
  });

  test('should persist session after login', async ({ page, context }) => {
    await page.goto('http://localhost:3000/login');
    
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
    
    // Check if token is stored
    const cookies = await context.cookies();
    const localStorage = await page.evaluate(() => JSON.stringify(localStorage));
    
    expect(localStorage.includes('token') || cookies.some(c => c.name.includes('token'))).toBeTruthy();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
    
    // Click logout
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout"), button:has-text("Sign Out")');
    await logoutButton.click();
    
    // Should redirect to login
    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });
});
