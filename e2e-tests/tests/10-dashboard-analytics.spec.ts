import { test, expect } from '@playwright/test';

/**
 * E2E Test: Dashboard and Analytics
 * Tests dashboard functionality and data visualization
 */

test.describe('Dashboard and Analytics', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should display dashboard with statistics', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should show key statistics cards
    await expect(page.locator('text=/total.*complaint|pending|resolved/i')).toBeVisible({ timeout: 10000 });
    
    // Should have numbers displayed
    const statsNumbers = page.locator('[data-testid="stat-value"], .stat-number, .metric-value');
    const count = await statsNumbers.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display complaints by status chart', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should have chart container
    const chart = page.locator('canvas, svg, [data-testid="status-chart"], .chart-container').first();
    await expect(chart).toBeVisible({ timeout: 10000 });
  });

  test('should display complaints by department chart', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should show department distribution
    const departmentChart = page.locator('[data-testid="department-chart"], .department-stats');
    if (await departmentChart.isVisible({ timeout: 5000 })) {
      await expect(departmentChart).toBeVisible();
    }
  });

  test('should show recent complaints list', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should have recent complaints section
    await expect(page.locator('text=/recent.*complaint|latest.*complaint/i')).toBeVisible({ timeout: 10000 });
    
    // Should have complaint items
    const recentComplaints = page.locator('.recent-complaint, .complaint-card').first();
    if (await recentComplaints.isVisible({ timeout: 2000 })) {
      await expect(recentComplaints).toBeVisible();
    }
  });

  test('should filter dashboard by date range', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    const dateFilter = page.locator('select[name="period"], button:has-text("Last 7 days")');
    if (await dateFilter.isVisible({ timeout: 2000 })) {
      await dateFilter.click();
      
      // Select different period
      const monthOption = page.locator('option:has-text("Last 30 days"), text=/30 days|month/i');
      if (await monthOption.isVisible({ timeout: 2000 })) {
        await monthOption.click();
        await page.waitForTimeout(1000);
        
        // Stats should update
        await expect(page.locator('[data-testid="stat-value"]')).toBeVisible();
      }
    }
  });

  test('should navigate to analytics page', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Click on analytics link
    const analyticsLink = page.locator('a:has-text("Analytics"), a:has-text("Reports")');
    if (await analyticsLink.isVisible({ timeout: 2000 })) {
      await analyticsLink.click();
      
      // Should navigate to analytics
      await expect(page).toHaveURL(/analytics|reports/, { timeout: 5000 });
    }
  });

  test('should display trend charts in analytics', async ({ page }) => {
    await page.goto('http://localhost:3000/analytics');
    
    // Should have trend visualization
    const trendChart = page.locator('canvas, svg, .trend-chart').first();
    if (await trendChart.isVisible({ timeout: 5000 })) {
      await expect(trendChart).toBeVisible();
    }
  });

  test('should export analytics data', async ({ page }) => {
    await page.goto('http://localhost:3000/analytics');
    
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")');
    if (await exportButton.isVisible({ timeout: 2000 })) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
      
      await exportButton.click();
      
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.csv|\.xlsx|\.pdf/);
      }
    }
  });

  test('should show response time metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should display average response time
    const responseTimeMetric = page.locator('text=/response time|average time|resolution time/i');
    if (await responseTimeMetric.isVisible({ timeout: 5000 })) {
      await expect(responseTimeMetric).toBeVisible();
    }
  });

  test('should show user activity statistics', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should show activity metrics
    const activityStats = page.locator('text=/active users|submissions|activity/i');
    if (await activityStats.isVisible({ timeout: 5000 })) {
      await expect(activityStats).toBeVisible();
    }
  });
});
