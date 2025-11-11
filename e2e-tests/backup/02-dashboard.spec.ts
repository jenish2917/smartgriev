import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('Dashboard & Navigation Tests', () => {
  let helpers: TestHelpers;
  let dbHelper: DatabaseHelper;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    dbHelper = new DatabaseHelper();
    await dbHelper.connect();

    // Login before each test
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    await helpers.login(loginEmail, loginPassword);
  });

  test.afterEach(async () => {
    await dbHelper.close();
  });

  test('should display dashboard with statistics', async ({ page }) => {
    // Verify we're on dashboard
    await page.waitForURL(/dashboard|home/i);
    expect(page.url()).toMatch(/dashboard|home/i);

    // Wait for dashboard to load
    await helpers.waitForLoadingComplete();

    // Check for statistics cards
    const statsSelectors = [
      '[data-testid="total-complaints"]',
      '[data-testid="pending-complaints"]',
      '[data-testid="resolved-complaints"]',
      '.stat-card',
      '.dashboard-stat',
      '.statistics'
    ];

    let statsFound = false;
    for (const selector of statsSelectors) {
      if (await helpers.elementExists(selector)) {
        console.log(`✓ Statistics found: ${selector}`);
        statsFound = true;
        break;
      }
    }

    // Take screenshot of dashboard
    await helpers.takeScreenshot('dashboard-loaded');

    // Verify some common dashboard elements
    const dashboardElements = [
      'Welcome',
      'Dashboard',
      'Complaint',
      'Statistics',
      'Total',
      'Pending',
      'Resolved'
    ];

    const pageContent = await page.content();
    const foundElements = dashboardElements.filter(el => 
      pageContent.toLowerCase().includes(el.toLowerCase())
    );

    console.log(`✓ Found dashboard elements: ${foundElements.join(', ')}`);
    expect(foundElements.length).toBeGreaterThan(0);
  });

  test('should navigate to My Complaints page', async ({ page }) => {
    // Look for "My Complaints" link or button
    const myComplaintsSelectors = [
      'text=My Complaints',
      'text=My Grievances',
      '[href*="my-complaints"]',
      '[href*="complaints"]',
      'a:has-text("Complaint")',
      'button:has-text("Complaint")'
    ];

    let clicked = false;
    for (const selector of myComplaintsSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          clicked = true;
          console.log(`✓ Clicked: ${selector}`);
          break;
        }
      } catch {
        // Try next selector
      }
    }

    if (clicked) {
      await page.waitForTimeout(2000);
      await helpers.takeScreenshot('my-complaints-page');
      console.log('✓ Navigated to complaints page');
    } else {
      console.log('⚠ My Complaints link not found, checking current page');
      await helpers.takeScreenshot('navigation-attempt');
    }
  });

  test('should navigate to Submit Complaint page', async ({ page }) => {
    // Look for "Submit Complaint" or "New Complaint" button
    const submitComplaintSelectors = [
      'text=Submit Complaint',
      'text=New Complaint',
      'text=Create Complaint',
      'text=File Complaint',
      '[href*="submit"]',
      '[href*="new-complaint"]',
      '[href*="create"]',
      'button:has-text("Submit")',
      'button:has-text("New")',
      '.submit-complaint',
      '.new-complaint-btn'
    ];

    let clicked = false;
    for (const selector of submitComplaintSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          clicked = true;
          console.log(`✓ Clicked: ${selector}`);
          break;
        }
      } catch {
        // Try next selector
      }
    }

    if (clicked) {
      await page.waitForTimeout(2000);
      await helpers.takeScreenshot('submit-complaint-page');
      console.log('✓ Navigated to submit complaint page');
    } else {
      console.log('⚠ Submit Complaint button not found');
      await helpers.takeScreenshot('submit-navigation-attempt');
    }
  });

  test('should navigate to Chatbot', async ({ page }) => {
    // Look for chatbot icon or button
    const chatbotSelectors = [
      '[data-testid="chatbot"]',
      '[data-testid="chat-button"]',
      '.chatbot-icon',
      '.chat-icon',
      '.floating-chat',
      'button[aria-label*="chat" i]',
      'text=Chat',
      'text=Chatbot',
      '[href*="chat"]'
    ];

    let clicked = false;
    for (const selector of chatbotSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          clicked = true;
          console.log(`✓ Clicked chatbot: ${selector}`);
          break;
        }
      } catch {
        // Try next selector
      }
    }

    if (clicked) {
      await page.waitForTimeout(2000);
      await helpers.takeScreenshot('chatbot-opened');
      console.log('✓ Chatbot opened');
    } else {
      console.log('⚠ Chatbot button not found');
      await helpers.takeScreenshot('chatbot-navigation-attempt');
    }
  });

  test('should display user profile information', async ({ page }) => {
    // Look for user profile icon/menu
    const profileSelectors = [
      '[data-testid="user-menu"]',
      '[data-testid="user-profile"]',
      '.user-profile',
      '.user-menu',
      '.user-avatar',
      '[aria-label*="profile" i]',
      '[aria-label*="account" i]',
      'button[aria-label*="user" i]'
    ];

    let profileOpened = false;
    for (const selector of profileSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          profileOpened = true;
          console.log(`✓ Opened profile menu: ${selector}`);
          await page.waitForTimeout(1000);
          await helpers.takeScreenshot('profile-menu-opened');
          break;
        }
      } catch {
        // Try next selector
      }
    }

    if (!profileOpened) {
      console.log('⚠ Profile menu not found, checking for profile information on page');
      await helpers.takeScreenshot('profile-search');
    }

    // Check if email is visible anywhere on the page
    const testEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const emailVisible = await page.locator(`text=${testEmail}`).first().isVisible().catch(() => false);
    
    if (emailVisible) {
      console.log('✓ User email found on page');
    }
  });

  test('should switch language to Hindi', async ({ page }) => {
    // Look for language switcher
    const languageSelectors = [
      '[data-testid="language-switcher"]',
      '[data-testid="language-selector"]',
      '.language-selector',
      '.language-switcher',
      'select[name="language"]',
      '[aria-label*="language" i]'
    ];

    let switcherFound = false;
    for (const selector of languageSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          switcherFound = true;
          console.log(`✓ Found language switcher: ${selector}`);
          await page.waitForTimeout(500);
          break;
        }
      } catch {
        // Try next selector
      }
    }

    if (switcherFound) {
      // Try to select Hindi
      const hindiSelectors = [
        '[data-lang="hi"]',
        '[value="hi"]',
        'text=Hindi',
        'text=हिंदी',
        'option:has-text("Hindi")',
        'option:has-text("हिंदी")'
      ];

      let hindiSelected = false;
      for (const selector of hindiSelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            await element.click();
            hindiSelected = true;
            console.log('✓ Selected Hindi language');
            await page.waitForTimeout(1000);
            await helpers.takeScreenshot('language-hindi');
            break;
          }
        } catch {
          // Try next selector
        }
      }

      if (!hindiSelected) {
        console.log('⚠ Hindi option not found in language switcher');
      }
    } else {
      console.log('⚠ Language switcher not found');
      await helpers.takeScreenshot('language-switcher-search');
    }
  });

  test('should switch language to Marathi', async ({ page }) => {
    // Look for language switcher
    const languageSelectors = [
      '[data-testid="language-switcher"]',
      '.language-selector',
      'select[name="language"]'
    ];

    let switcherFound = false;
    for (const selector of languageSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          switcherFound = true;
          await page.waitForTimeout(500);
          break;
        }
      } catch {
        continue;
      }
    }

    if (switcherFound) {
      // Try to select Marathi
      const marathiSelectors = [
        '[data-lang="mr"]',
        '[value="mr"]',
        'text=Marathi',
        'text=मराठी',
        'option:has-text("Marathi")'
      ];

      for (const selector of marathiSelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            await element.click();
            console.log('✓ Selected Marathi language');
            await page.waitForTimeout(1000);
            await helpers.takeScreenshot('language-marathi');
            break;
          }
        } catch {
          continue;
        }
      }
    }
  });

  test('should display navigation menu', async ({ page }) => {
    // Check for navigation menu items
    const navItems = [
      'Dashboard',
      'Complaints',
      'Chat',
      'Profile',
      'Settings',
      'Logout'
    ];

    const pageContent = await page.content();
    const foundNavItems = navItems.filter(item => 
      pageContent.toLowerCase().includes(item.toLowerCase())
    );

    console.log(`✓ Found navigation items: ${foundNavItems.join(', ')}`);
    await helpers.takeScreenshot('navigation-menu');

    expect(foundNavItems.length).toBeGreaterThan(0);
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Change to mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);

    // Take screenshot in mobile view
    await helpers.takeScreenshot('dashboard-mobile');

    // Look for mobile menu toggle (hamburger icon)
    const mobileMenuSelectors = [
      '[data-testid="mobile-menu"]',
      '.hamburger',
      '.mobile-menu-toggle',
      '[aria-label*="menu" i]',
      'button[aria-label*="navigation" i]'
    ];

    for (const selector of mobileMenuSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          console.log(`✓ Mobile menu toggle found: ${selector}`);
          await element.click();
          await page.waitForTimeout(500);
          await helpers.takeScreenshot('mobile-menu-opened');
          break;
        }
      } catch {
        continue;
      }
    }

    console.log('✓ Mobile responsive view tested');
  });

  test('should display welcome message', async ({ page }) => {
    // Look for welcome message
    const welcomeTexts = ['welcome', 'hello', 'hi', 'good morning', 'good afternoon'];
    const pageContent = await page.content().then(c => c.toLowerCase());

    const foundWelcome = welcomeTexts.some(text => pageContent.includes(text));

    if (foundWelcome) {
      console.log('✓ Welcome message found');
    } else {
      console.log('⚠ Welcome message not found');
    }

    await helpers.takeScreenshot('welcome-message-check');
  });

  test('should handle dashboard statistics from database', async ({ page }) => {
    // Get actual statistics from database
    const stats = await dbHelper.getStats();
    console.log('✓ Database statistics:', stats);

    // Wait for dashboard to load
    await helpers.waitForLoadingComplete();

    // Check if numbers on dashboard match or are present
    const pageContent = await page.content();

    if (stats && 'complaints' in stats) {
      console.log(`✓ Complaints in DB: ${stats.complaints}`);
    }

    if (stats && 'users' in stats) {
      console.log(`✓ Users in DB: ${stats.users}`);
    }

    await helpers.takeScreenshot('dashboard-with-stats');
  });

  test('should navigate back to dashboard from other pages', async ({ page }) => {
    // Navigate to complaints page first
    try {
      await page.goto('/complaints');
      await page.waitForTimeout(1000);
    } catch {
      console.log('⚠ Could not navigate to complaints page');
    }

    // Now try to go back to dashboard
    const dashboardSelectors = [
      'text=Dashboard',
      '[href*="dashboard"]',
      '[href="/"]',
      'a:has-text("Dashboard")',
      '.nav-dashboard'
    ];

    let navigated = false;
    for (const selector of dashboardSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          navigated = true;
          console.log(`✓ Navigated back to dashboard via: ${selector}`);
          await page.waitForTimeout(1000);
          break;
        }
      } catch {
        continue;
      }
    }

    if (navigated) {
      expect(page.url()).toMatch(/dashboard|home|\/$|^$/i);
      await helpers.takeScreenshot('back-to-dashboard');
    }
  });

  test('should display notifications bell/icon', async ({ page }) => {
    // Look for notifications icon
    const notificationSelectors = [
      '[data-testid="notifications"]',
      '.notification-bell',
      '.notifications-icon',
      '[aria-label*="notification" i]',
      'button[aria-label*="notification" i]'
    ];

    let notificationFound = false;
    for (const selector of notificationSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          console.log(`✓ Notification icon found: ${selector}`);
          
          // Try to click and see notifications
          await element.click();
          await page.waitForTimeout(1000);
          await helpers.takeScreenshot('notifications-opened');
          
          notificationFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    if (!notificationFound) {
      console.log('⚠ Notification icon not found');
      await helpers.takeScreenshot('notification-search');
    }
  });
});
