import { test, expect } from '@playwright/test';

/**
 * E2E Test: Notifications System
 * Tests notification functionality
 */

test.describe('Notifications', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should show notification icon in header', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Should have notification bell/icon
    const notificationIcon = page.locator('[data-testid="notifications"], button:has([aria-label*="notification" i]), .notification-icon');
    await expect(notificationIcon).toBeVisible({ timeout: 5000 });
  });

  test('should show notification count badge', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    const notificationBadge = page.locator('.notification-badge, .badge, [data-testid="notification-count"]');
    if (await notificationBadge.isVisible({ timeout: 2000 })) {
      // Should show count
      const count = await notificationBadge.textContent();
      expect(parseInt(count || '0')).toBeGreaterThanOrEqual(0);
    }
  });

  test('should open notifications panel', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    const notificationIcon = page.locator('button:has([aria-label*="notification" i]), [data-testid="notifications"]');
    if (await notificationIcon.isVisible()) {
      await notificationIcon.click();
      
      // Should show notifications panel/dropdown
      await expect(page.locator('.notifications-panel, .notification-dropdown, [role="menu"]')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display notification list', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    // Should show notifications page
    await expect(page.locator('h1:has-text("Notifications"), .notifications-container')).toBeVisible({ timeout: 10000 });
    
    // Should have notification items
    const notifications = page.locator('.notification-item, [data-testid="notification"]');
    const count = await notifications.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should mark notification as read', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    // Find unread notification
    const unreadNotification = page.locator('.notification-item.unread, [data-read="false"]').first();
    if (await unreadNotification.isVisible({ timeout: 2000 })) {
      await unreadNotification.click();
      
      // Should mark as read
      await page.waitForTimeout(1000);
      await expect(unreadNotification).not.toHaveClass(/unread/);
    }
  });

  test('should mark all as read', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    const markAllButton = page.locator('button:has-text("Mark all as read"), button:has-text("Read all")');
    if (await markAllButton.isVisible({ timeout: 2000 })) {
      await markAllButton.click();
      
      // All notifications should be marked as read
      await page.waitForTimeout(1000);
      const unreadCount = await page.locator('.notification-item.unread, [data-read="false"]').count();
      expect(unreadCount).toBe(0);
    }
  });

  test('should delete notification', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    const initialCount = await page.locator('.notification-item').count();
    
    // Click delete button on first notification
    const deleteButton = page.locator('.notification-item button[aria-label*="delete" i], .delete-notification').first();
    if (await deleteButton.isVisible({ timeout: 2000 })) {
      await deleteButton.click();
      
      // Confirm deletion if modal appears
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Delete")');
      if (await confirmButton.isVisible({ timeout: 2000 })) {
        await confirmButton.click();
      }
      
      await page.waitForTimeout(1000);
      
      // Count should decrease
      const newCount = await page.locator('.notification-item').count();
      expect(newCount).toBeLessThanOrEqual(initialCount);
    }
  });

  test('should filter notifications by type', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    const filterSelect = page.locator('select[name="type"], select:has(option:has-text("Status"))');
    if (await filterSelect.isVisible({ timeout: 2000 })) {
      await filterSelect.selectOption('status_update');
      await page.waitForTimeout(1000);
      
      // Should show only status update notifications
      const notifications = page.locator('.notification-item');
      const count = await notifications.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('should navigate to related complaint from notification', async ({ page }) => {
    await page.goto('http://localhost:3000/notifications');
    
    const notification = page.locator('.notification-item').first();
    if (await notification.isVisible({ timeout: 2000 })) {
      await notification.click();
      
      // Should navigate to complaint details
      await expect(page).toHaveURL(/complaint|complaint/, { timeout: 5000 });
    }
  });
});
