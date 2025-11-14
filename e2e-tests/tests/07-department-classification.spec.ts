import { test, expect } from '@playwright/test';

/**
 * E2E Test: Department Classification
 * Tests automatic department assignment
 */

test.describe('Department Classification', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should classify road complaint to Road & Transportation', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Large pothole on highway');
    await page.fill('textarea[name="description"]', 'There is a dangerous pothole on the main highway causing accidents');
    await page.fill('input[name="location"]', 'Surat');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // Navigate to view complaint
    await page.goto('http://localhost:3000/complaints');
    await page.locator('text=/pothole/i').first().click();
    
    // Check department
    await expect(page.locator('text=/Road.*Transportation|Road & Transportation/i')).toBeVisible({ timeout: 5000 });
  });

  test('should classify water complaint to Water Supply & Sewerage', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Water supply broken');
    await page.fill('textarea[name="description"]', 'Water pipe is leaking, no water supply for days');
    await page.fill('input[name="location"]', 'Surat');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    await page.goto('http://localhost:3000/complaints');
    await page.locator('text=/water/i').first().click();
    
    await expect(page.locator('text=/Water Supply|Sewerage/i')).toBeVisible({ timeout: 5000 });
  });

  test('should classify garbage complaint to Sanitation', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Garbage not collected');
    await page.fill('textarea[name="description"]', 'Trash is piling up, sanitation workers not coming');
    await page.fill('input[name="location"]', 'Surat');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    await page.goto('http://localhost:3000/complaints');
    await page.locator('text=/garbage/i').first().click();
    
    await expect(page.locator('text=/Sanitation|Cleanliness/i')).toBeVisible({ timeout: 5000 });
  });

  test('should classify electricity complaint to Electricity Board', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Power outage issue');
    await page.fill('textarea[name="description"]', 'Electricity is out, transformer not working');
    await page.fill('input[name="location"]', 'Surat');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    await page.goto('http://localhost:3000/complaints');
    await page.locator('text=/power|electricity/i').first().click();
    
    await expect(page.locator('text=/Electricity Board|Electricity/i')).toBeVisible({ timeout: 5000 });
  });

  test('should classify traffic complaint to Traffic Police', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Severe traffic jam');
    await page.fill('textarea[name="description"]', 'Traffic congestion, vehicles parking illegally');
    await page.fill('input[name="location"]', 'Surat');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    await page.goto('http://localhost:3000/complaints');
    await page.locator('text=/traffic/i').first().click();
    
    await expect(page.locator('text=/Traffic Police|Traffic/i')).toBeVisible({ timeout: 5000 });
  });
});
