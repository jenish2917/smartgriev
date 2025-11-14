import { test, expect } from '@playwright/test';

/**
 * E2E Test: User Registration Flow
 * Tests the complete user registration process
 */

test.describe('User Registration', () => {
  
  test('should register a new user successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    
    // Fill registration form
    const timestamp = Date.now();
    const email = `testuser${timestamp}@example.com`;
    
    await page.fill('input[name="username"]', `testuser${timestamp}`);
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', 'Test@1234');
    await page.fill('input[name="confirmPassword"]', 'Test@1234');
    await page.fill('input[name="phone"]', '9876543210');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for success message or redirect
    await expect(page).toHaveURL(/login|dashboard/, { timeout: 10000 });
  });

  test('should show error for duplicate email', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    
    // Try to register with existing email
    await page.fill('input[name="username"]', 'existinguser');
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'Test@1234');
    await page.fill('input[name="confirmPassword"]', 'Test@1234');
    await page.fill('input[name="phone"]', '9876543210');
    
    await page.click('button[type="submit"]');
    
    // Should show error
    await expect(page.locator('text=/already exists|already registered/i')).toBeVisible({ timeout: 5000 });
  });

  test('should validate password strength', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    
    await page.fill('input[name="password"]', 'weak');
    await page.fill('input[name="confirmPassword"]', 'weak');
    
    // Should show validation error
    await expect(page.locator('text=/password must|too weak|at least/i')).toBeVisible();
  });

  test('should validate password match', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    
    await page.fill('input[name="password"]', 'Test@1234');
    await page.fill('input[name="confirmPassword"]', 'Different@1234');
    
    await page.click('button[type="submit"]');
    
    // Should show mismatch error
    await expect(page.locator('text=/password.*match|do not match/i')).toBeVisible();
  });

  test('should validate phone number format', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    
    await page.fill('input[name="phone"]', '123'); // Invalid
    await page.blur('input[name="phone"]');
    
    // Should show validation error
    await expect(page.locator('text=/invalid.*phone|valid phone/i')).toBeVisible();
  });
});
