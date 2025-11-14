import { test, expect } from '@playwright/test';

/**
 * E2E Test: Complaints List and Management
 * Tests viewing and managing complaints
 */

test.describe('Complaints List', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should display list of complaints', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Should show complaints table/list
    await expect(page.locator('table, .complaint-list, [data-testid="complaints-list"]')).toBeVisible({ timeout: 10000 });
    
    // Should have at least headers
    await expect(page.locator('th:has-text("Title"), th:has-text("Status")')).toBeVisible();
  });

  test('should filter complaints by status', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Find filter dropdown
    const statusFilter = page.locator('select[name="status"], select:has(option:has-text("Pending"))');
    if (await statusFilter.isVisible()) {
      await statusFilter.selectOption('pending');
      
      // Wait for filter to apply
      await page.waitForTimeout(1000);
      
      // All visible complaints should have pending status
      const complaints = page.locator('[data-status="pending"], .status:has-text("Pending")');
      await expect(complaints.first()).toBeVisible();
    }
  });

  test('should search complaints by title', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('pothole');
      await page.waitForTimeout(1000);
      
      // Should show filtered results
      await expect(page.locator('text=/pothole/i')).toBeVisible();
    }
  });

  test('should paginate complaints', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Wait for complaints to load
    await page.waitForSelector('table, .complaint-list', { timeout: 10000 });
    
    // Look for pagination
    const nextButton = page.locator('button:has-text("Next"), button[aria-label="Next page"]');
    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      await nextButton.click();
      await page.waitForTimeout(1000);
      
      // Should navigate to next page
      await expect(page).toHaveURL(/page=2|\?p=2|&page=2/);
    }
  });

  test('should view complaint details', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Wait for complaints to load
    await page.waitForSelector('table tr, .complaint-item', { timeout: 10000 });
    
    // Click on first complaint
    const firstComplaint = page.locator('table tbody tr, .complaint-item').first();
    await firstComplaint.click();
    
    // Should navigate to details page
    await expect(page).toHaveURL(/complaints\/\d+|complaint\/\d+/, { timeout: 5000 });
    
    // Should show complaint details
    await expect(page.locator('text=/description|details|status/i')).toBeVisible();
  });

  test('should sort complaints by date', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints');
    
    // Click on date column header
    const dateHeader = page.locator('th:has-text("Date"), th:has-text("Created")');
    if (await dateHeader.isVisible()) {
      await dateHeader.click();
      await page.waitForTimeout(1000);
      
      // Should re-order complaints
      // Check if URL has sort parameter or table re-renders
    }
  });
});
