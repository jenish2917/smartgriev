import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/register');
  });

  test('should display registration form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /register/i })).toBeVisible();
    await expect(page.getByLabel(/username/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText(/required/i).first()).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.getByLabel(/email/i).fill('invalid-email');
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText(/valid email/i)).toBeVisible();
  });

  test('should validate password strength', async ({ page }) => {
    await page.getByLabel(/password/i).first().fill('123');
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
  });

  test('should validate password confirmation match', async ({ page }) => {
    await page.getByLabel(/^password$/i).fill('Password123!');
    await page.getByLabel(/confirm password/i).fill('Different123!');
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText(/passwords do not match/i)).toBeVisible();
  });

  test('should register new user successfully', async ({ page }) => {
    const timestamp = Date.now();
    const username = `testuser${timestamp}`;
    const email = `test${timestamp}@example.com`;

    await page.getByLabel(/username/i).fill(username);
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/phone/i).fill('9876543210');
    await page.getByLabel(/^password$/i).fill('Password123!');
    await page.getByLabel(/confirm password/i).fill('Password123!');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    // Should redirect to OTP verification or login
    await expect(page).toHaveURL(/\/(verify-otp|login)/);
  });

  test('should show error for duplicate username', async ({ page }) => {
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/email/i).fill('newemail@example.com');
    await page.getByLabel(/phone/i).fill('9876543210');
    await page.getByLabel(/^password$/i).fill('Password123!');
    await page.getByLabel(/confirm password/i).fill('Password123!');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText(/username already exists/i)).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to login page', async ({ page }) => {
    await page.getByRole('link', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/login/);
  });
});
