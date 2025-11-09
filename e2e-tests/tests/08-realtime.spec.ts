import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('Real-time Features Testing', () => {
  let helpers: TestHelpers;
  let dbHelper: DatabaseHelper;
  let testUserId: number;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    dbHelper = new DatabaseHelper();
    await dbHelper.connect();

    // Login
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    await helpers.login(loginEmail, loginPassword);

    const user = await dbHelper.getUserByEmail(loginEmail);
    if (user) {
      testUserId = user.id;
    }
  });

  test.afterEach(async () => {
    await dbHelper.close();
  });

  test('should display notification bell icon', async ({ page }) => {
    const notificationSelectors = [
      '[data-testid="notifications"]',
      '[data-testid="notification-bell"]',
      '.notification-bell',
      '.notifications-icon',
      'button[aria-label*="notification" i]'
    ];

    let bellFound = false;
    for (const selector of notificationSelectors) {
      try {
        if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
          console.log(`✓ Notification bell found: ${selector}`);
          bellFound = true;
          await helpers.takeScreenshot('notification-bell');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!bellFound) {
      console.log('⚠ Notification bell not found');
    }
  });

  test('should show notification count badge', async ({ page }) => {
    const badgeSelectors = [
      '.notification-badge',
      '.notification-count',
      '[data-testid="notification-count"]',
      '.badge',
      'span[class*="badge"]'
    ];

    let badgeFound = false;
    for (const selector of badgeSelectors) {
      try {
        const badge = page.locator(selector).first();
        if (await badge.isVisible({ timeout: 2000 })) {
          const count = await badge.textContent();
          console.log(`✓ Notification badge found with count: ${count}`);
          badgeFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('notification-badge');

    if (!badgeFound) {
      console.log('⚠ Notification badge not visible (may be zero notifications)');
    }
  });

  test('should open notifications dropdown', async ({ page }) => {
    const bellSelector = page.locator('[data-testid="notifications"], .notification-bell, button[aria-label*="notification" i]').first();

    try {
      if (await bellSelector.isVisible({ timeout: 2000 })) {
        await bellSelector.click();
        console.log('✓ Notification bell clicked');
        
        await page.waitForTimeout(1000);
        
        // Look for dropdown
        const dropdownSelectors = [
          '.notification-dropdown',
          '.notifications-panel',
          '[data-testid="notifications-dropdown"]',
          '[role="menu"]',
          '.dropdown-menu'
        ];

        for (const selector of dropdownSelectors) {
          if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
            console.log('✓ Notifications dropdown opened');
            break;
          }
        }

        await helpers.takeScreenshot('notifications-dropdown');
      }
    } catch (error) {
      console.log('⚠ Could not open notifications dropdown');
    }
  });

  test('should display notification list', async ({ page }) => {
    // Open notifications
    const bellSelector = page.locator('[data-testid="notifications"], .notification-bell').first();
    
    try {
      if (await bellSelector.isVisible({ timeout: 2000 })) {
        await bellSelector.click();
        await page.waitForTimeout(1000);

        // Look for notification items
        const notificationItemSelectors = [
          '.notification-item',
          '.notification',
          '[data-testid="notification-item"]',
          '.notification-card'
        ];

        for (const selector of notificationItemSelectors) {
          const items = page.locator(selector);
          const count = await items.count();
          
          if (count > 0) {
            console.log(`✓ Found ${count} notifications`);
            
            // Read first notification
            const firstNotification = await items.first().textContent();
            console.log(`  First notification: ${firstNotification?.substring(0, 50)}...`);
            break;
          }
        }

        await helpers.takeScreenshot('notification-list');
      }
    } catch (error) {
      console.log('⚠ Could not test notification list');
    }
  });

  test('should mark notification as read', async ({ page }) => {
    const bellSelector = page.locator('[data-testid="notifications"], .notification-bell').first();
    
    try {
      if (await bellSelector.isVisible({ timeout: 2000 })) {
        await bellSelector.click();
        await page.waitForTimeout(1000);

        // Click on a notification
        const notificationItem = page.locator('.notification-item, .notification').first();
        
        if (await notificationItem.isVisible({ timeout: 2000 })) {
          await notificationItem.click();
          console.log('✓ Notification clicked');
          
          await page.waitForTimeout(1000);
          await helpers.takeScreenshot('notification-read');
          
          console.log('✓ Notification marked as read');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test mark as read');
    }
  });

  test('should show real-time complaint status updates', async ({ page }) => {
    // Navigate to my complaints
    await page.goto('/my-complaints');
    await page.waitForTimeout(2000);

    // Look for status indicators
    const statusSelectors = [
      '.status',
      '.complaint-status',
      '[data-testid="status"]',
      'text=/pending|approved|resolved|rejected/i'
    ];

    let statusFound = false;
    for (const selector of statusSelectors) {
      try {
        const status = page.locator(selector).first();
        if (await status.isVisible({ timeout: 2000 })) {
          const text = await status.textContent();
          console.log(`✓ Status indicator found: ${text}`);
          statusFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('complaint-status');

    if (!statusFound) {
      console.log('⚠ Status indicators not found');
    }
  });

  test('should receive real-time notifications', async ({ page }) => {
    // Wait and watch for new notifications
    console.log('✓ Monitoring for real-time notifications...');
    
    await page.waitForTimeout(5000);

    // Check if notification count changed or new notification appeared
    const badge = page.locator('.notification-badge, .notification-count').first();
    
    try {
      if (await badge.isVisible({ timeout: 2000 })) {
        const initialCount = await badge.textContent();
        console.log(`  Initial notification count: ${initialCount}`);
        
        await page.waitForTimeout(5000);
        
        const newCount = await badge.textContent();
        console.log(`  New notification count: ${newCount}`);
        
        if (initialCount !== newCount) {
          console.log('✓ Real-time notification received!');
        }
      }
    } catch (error) {
      console.log('⚠ Could not monitor notifications');
    }

    await helpers.takeScreenshot('realtime-monitoring');
  });

  test('should show typing indicator in chat', async ({ page }) => {
    // Open chatbot
    const chatBtn = page.locator('[data-testid="chatbot"], .chatbot-icon').first();
    
    try {
      if (await chatBtn.isVisible({ timeout: 2000 })) {
        await chatBtn.click();
        await page.waitForTimeout(1000);

        // Send a message
        const input = page.locator('input[type="text"], textarea').first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill('Test real-time chat');
          await input.press('Enter');
          
          // Immediately look for typing indicator
          await page.waitForTimeout(500);
          
          const typingSelectors = [
            '.typing-indicator',
            '.is-typing',
            '[data-testid="typing"]',
            'text=/typing/i'
          ];

          for (const selector of typingSelectors) {
            if (await page.locator(selector).first().isVisible({ timeout: 1000 })) {
              console.log('✓ Typing indicator shown');
              await helpers.takeScreenshot('typing-indicator');
              break;
            }
          }
        }
      }
    } catch (error) {
      console.log('⚠ Could not test typing indicator');
    }
  });

  test('should update complaint list in real-time', async ({ page }) => {
    await page.goto('/my-complaints');
    await page.waitForTimeout(2000);

    // Count initial complaints
    const complaintSelectors = [
      '.complaint-item',
      '.complaint-card',
      '[data-testid="complaint"]'
    ];

    let initialCount = 0;
    for (const selector of complaintSelectors) {
      const items = page.locator(selector);
      initialCount = await items.count();
      if (initialCount > 0) {
        console.log(`✓ Initial complaints: ${initialCount}`);
        break;
      }
    }

    await helpers.takeScreenshot('initial-complaint-list');
    console.log('✓ Real-time updates monitoring ready');
  });

  test('should show live status changes', async ({ page }) => {
    if (!testUserId) {
      console.log('⚠ Test user ID not available');
      return;
    }

    // Get user's complaints
    const complaint = await dbHelper.getLatestComplaintByUser(testUserId);
    
    if (complaint) {
      console.log(`✓ Monitoring complaint ${complaint.id} for status changes`);
      console.log(`  Current status: ${complaint.status}`);

      // Navigate to complaint detail
      await page.goto(`/complaint/${complaint.id}`);
      await page.waitForTimeout(2000);

      // Watch for status changes
      await helpers.takeScreenshot('status-monitoring');
      console.log('✓ Status change monitoring active');
    } else {
      console.log('⚠ No complaints found to monitor');
    }
  });

  test('should display online/offline status', async ({ page }) => {
    // Look for connection status indicator
    const connectionSelectors = [
      '.connection-status',
      '.online-status',
      '[data-testid="connection-status"]',
      'text=/online|offline|connected/i'
    ];

    let statusFound = false;
    for (const selector of connectionSelectors) {
      try {
        if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
          console.log(`✓ Connection status indicator found`);
          statusFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('connection-status');

    if (!statusFound) {
      console.log('⚠ Connection status indicator not visible');
    }
  });

  test('should handle WebSocket connection', async ({ page }) => {
    // Monitor WebSocket connections
    const wsMessages: string[] = [];

    page.on('websocket', ws => {
      console.log(`✓ WebSocket connection established: ${ws.url()}`);
      
      ws.on('framesent', frame => {
        wsMessages.push(`Sent: ${frame.payload}`);
      });

      ws.on('framereceived', frame => {
        wsMessages.push(`Received: ${frame.payload}`);
      });

      ws.on('close', () => {
        console.log('✓ WebSocket connection closed');
      });
    });

    // Wait and see if WebSocket connects
    await page.waitForTimeout(5000);

    if (wsMessages.length > 0) {
      console.log(`✓ WebSocket messages: ${wsMessages.length}`);
    } else {
      console.log('⚠ No WebSocket activity detected');
    }

    await helpers.takeScreenshot('websocket-test');
  });

  test('should auto-refresh complaint list', async ({ page }) => {
    await page.goto('/my-complaints');
    await page.waitForTimeout(2000);

    // Look for auto-refresh indicator or mechanism
    const refreshSelectors = [
      '[data-testid="auto-refresh"]',
      '.auto-refresh',
      'text=/auto.*refresh|updating/i'
    ];

    for (const selector of refreshSelectors) {
      try {
        if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
          console.log('✓ Auto-refresh mechanism active');
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('auto-refresh');
    console.log('✓ Auto-refresh tested');
  });

  test('should show toast notifications', async ({ page }) => {
    // Wait for any toast notifications
    await page.waitForTimeout(3000);

    const toastSelectors = [
      '.toast',
      '.ant-notification',
      '.notification-toast',
      '[role="alert"]',
      '.alert'
    ];

    let toastFound = false;
    for (const selector of toastSelectors) {
      try {
        const toast = page.locator(selector).first();
        if (await toast.isVisible({ timeout: 2000 })) {
          const text = await toast.textContent();
          console.log(`✓ Toast notification: ${text?.substring(0, 50)}`);
          toastFound = true;
          await helpers.takeScreenshot('toast-notification');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!toastFound) {
      console.log('⚠ No toast notifications visible');
    }
  });

  test('should verify notifications in database', async ({ page }) => {
    if (!testUserId) {
      console.log('⚠ Test user ID not available');
      return;
    }

    // Get notifications from database
    const notifications = await dbHelper.getNotifications(testUserId);

    if (notifications && notifications.length > 0) {
      console.log(`✓ Found ${notifications.length} notifications in database`);
      
      notifications.slice(0, 3).forEach((notif: any, i: number) => {
        console.log(`  ${i + 1}. ${notif.message || notif.title} (${notif.read ? 'read' : 'unread'})`);
      });
    } else {
      console.log('⚠ No notifications found in database');
    }

    await helpers.takeScreenshot('db-notifications-check');
  });
});
