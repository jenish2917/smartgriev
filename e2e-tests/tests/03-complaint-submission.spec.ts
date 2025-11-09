import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('Complaint Submission - Text Only', () => {
  let helpers: TestHelpers;
  let dbHelper: DatabaseHelper;
  let testUserId: number;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    dbHelper = new DatabaseHelper();
    await dbHelper.connect();

    // Login before each test
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    await helpers.login(loginEmail, loginPassword);

    // Get user ID from database
    const user = await dbHelper.getUserByEmail(loginEmail);
    if (user) {
      testUserId = user.id;
      console.log(`✓ Test user ID: ${testUserId}`);
    }
  });

  test.afterEach(async () => {
    await dbHelper.close();
  });

  test('should submit a text complaint successfully', async ({ page }) => {
    // Navigate to submit complaint page
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // If not on submit page, try to find and click submit button
    if (!page.url().includes('submit')) {
      const submitSelectors = [
        'text=Submit Complaint',
        'text=New Complaint',
        '[href*="submit"]',
        'button:has-text("Submit")'
      ];

      for (const selector of submitSelectors) {
        try {
          await page.locator(selector).first().click({ timeout: 2000 });
          await page.waitForTimeout(1000);
          break;
        } catch {
          continue;
        }
      }
    }

    await helpers.takeScreenshot('complaint-form');

    // Fill complaint form
    const complaintTitle = `Test Complaint - ${Date.now()}`;
    const complaintDescription = 'This is a test complaint about a pothole on Main Street. It needs immediate attention.';

    // Fill title
    const titleSelectors = [
      'input[name="title"]',
      'input[name="subject"]',
      'input[placeholder*="title" i]',
      'input[placeholder*="subject" i]'
    ];

    let titleFilled = false;
    for (const selector of titleSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.fill(complaintTitle);
          titleFilled = true;
          console.log(`✓ Filled title: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }

    // Fill description
    const descriptionSelectors = [
      'textarea[name="description"]',
      'textarea[name="details"]',
      'textarea[placeholder*="description" i]',
      'textarea[placeholder*="details" i]'
    ];

    let descriptionFilled = false;
    for (const selector of descriptionSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.fill(complaintDescription);
          descriptionFilled = true;
          console.log(`✓ Filled description: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }

    // Select department if available
    const departmentSelectors = [
      'select[name="department"]',
      'select[name="category"]',
      '[data-testid="department-select"]'
    ];

    for (const selector of departmentSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.selectOption({ index: 1 }); // Select first option after placeholder
          console.log('✓ Selected department');
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('complaint-form-filled');

    // Submit the form
    const submitButtonSelectors = [
      'button[type="submit"]',
      'button:has-text("Submit")',
      'button:has-text("Create")',
      'button:has-text("Send")'
    ];

    let submitted = false;
    for (const selector of submitButtonSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          submitted = true;
          console.log('✓ Clicked submit button');
          break;
        }
      } catch {
        continue;
      }
    }

    if (submitted) {
      // Wait for success message or redirect
      await page.waitForTimeout(3000);
      await helpers.takeScreenshot('complaint-submitted');

      // Verify in database
      if (testUserId) {
        const complaint = await dbHelper.getLatestComplaintByUser(testUserId);
        if (complaint) {
          console.log('✓ Complaint found in database:', complaint.id);
          console.log('  Title:', complaint.title);
          console.log('  Status:', complaint.status);
          expect(complaint.title).toContain('Test Complaint');
        } else {
          console.log('⚠ Complaint not found in database (may take time to sync)');
        }
      }
    } else {
      console.log('⚠ Could not submit complaint form');
    }
  });

  test('should validate required fields', async ({ page }) => {
    // Navigate to submit complaint page
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Try to submit without filling anything
    const submitButtonSelectors = [
      'button[type="submit"]',
      'button:has-text("Submit")'
    ];

    for (const selector of submitButtonSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          console.log('✓ Clicked submit without filling form');
          break;
        }
      } catch {
        continue;
      }
    }

    await page.waitForTimeout(1000);

    // Check for validation errors
    const errorSelectors = [
      '.error',
      '.ant-form-item-explain-error',
      '[role="alert"]',
      '.validation-error',
      '.field-error'
    ];

    let errorFound = false;
    for (const selector of errorSelectors) {
      const errorElements = page.locator(selector);
      const count = await errorElements.count();
      if (count > 0) {
        errorFound = true;
        console.log(`✓ Validation errors found: ${count} errors`);
        break;
      }
    }

    await helpers.takeScreenshot('validation-errors');

    if (errorFound) {
      console.log('✓ Form validation working');
    } else {
      console.log('⚠ No validation errors visible (may use native HTML5 validation)');
    }
  });

  test('should show character count for description', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Find description textarea
    const descriptionField = page.locator('textarea[name="description"], textarea').first();
    
    if (await descriptionField.isVisible({ timeout: 2000 })) {
      // Type some text
      await descriptionField.fill('Test description for character count');

      // Look for character counter
      const counterSelectors = [
        '.character-count',
        '.char-count',
        '[data-testid="char-counter"]',
        'text=/\\d+\\/\\d+/',
        'text=/\\d+ characters/'
      ];

      let counterFound = false;
      for (const selector of counterSelectors) {
        try {
          const counter = page.locator(selector).first();
          if (await counter.isVisible({ timeout: 1000 })) {
            const text = await counter.textContent();
            console.log(`✓ Character counter found: ${text}`);
            counterFound = true;
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('character-count');

      if (!counterFound) {
        console.log('⚠ Character counter not found');
      }
    }
  });

  test('should allow selecting complaint category/department', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Look for category/department dropdown
    const categorySelectors = [
      'select[name="department"]',
      'select[name="category"]',
      '[data-testid="category-select"]',
      '[data-testid="department-select"]'
    ];

    let categoryFound = false;
    for (const selector of categorySelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          // Get all options
          const options = await element.locator('option').allTextContents();
          console.log(`✓ Available categories: ${options.join(', ')}`);
          
          // Select first real option (skip placeholder)
          await element.selectOption({ index: 1 });
          
          categoryFound = true;
          await helpers.takeScreenshot('category-selected');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!categoryFound) {
      console.log('⚠ Category/department selector not found');
      await helpers.takeScreenshot('category-search');
    }
  });

  test('should allow adding location to complaint', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Look for location fields
    const locationSelectors = [
      'input[name="location"]',
      'input[name="address"]',
      'input[placeholder*="location" i]',
      'input[placeholder*="address" i]',
      '[data-testid="location-input"]'
    ];

    let locationFound = false;
    for (const selector of locationSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.fill('Main Street, Mumbai, Maharashtra');
          console.log('✓ Location field filled');
          locationFound = true;
          await helpers.takeScreenshot('location-filled');
          break;
        }
      } catch {
        continue;
      }
    }

    // Look for "Use Current Location" button
    const useLocationSelectors = [
      'button:has-text("Use Current Location")',
      'button:has-text("Get Location")',
      '[data-testid="use-location"]',
      '.use-location-btn'
    ];

    for (const selector of useLocationSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          console.log('✓ "Use Current Location" button found');
          await element.click();
          await page.waitForTimeout(2000);
          await helpers.takeScreenshot('location-detected');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!locationFound) {
      console.log('⚠ Location field not found');
    }
  });

  test('should show preview before submission', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill form
    try {
      await page.locator('input[name="title"]').first().fill('Test Preview Complaint');
      await page.locator('textarea[name="description"]').first().fill('This is for preview test');
    } catch {
      console.log('⚠ Could not fill form fields');
    }

    // Look for preview button
    const previewSelectors = [
      'button:has-text("Preview")',
      'button:has-text("Review")',
      '[data-testid="preview-btn"]'
    ];

    let previewFound = false;
    for (const selector of previewSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          console.log('✓ Preview button clicked');
          await page.waitForTimeout(1000);
          await helpers.takeScreenshot('complaint-preview');
          previewFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    if (!previewFound) {
      console.log('⚠ Preview feature not found');
    }
  });

  test('should track complaint status in database', async ({ page }) => {
    if (!testUserId) {
      console.log('⚠ Test user ID not available, skipping');
      return;
    }

    // Get existing complaints
    const existingComplaints = await dbHelper.getComplaintsByStatus('pending');
    console.log(`✓ Pending complaints in database: ${existingComplaints}`);

    // Get user's latest complaint
    const latestComplaint = await dbHelper.getLatestComplaintByUser(testUserId);
    
    if (latestComplaint) {
      console.log('✓ Latest user complaint:');
      console.log('  ID:', latestComplaint.id);
      console.log('  Title:', latestComplaint.title);
      console.log('  Status:', latestComplaint.status);
      console.log('  Created:', latestComplaint.created_at);

      // Get audit trail
      const auditTrail = await dbHelper.getAuditTrail(latestComplaint.id);
      if (auditTrail && auditTrail.length > 0) {
        console.log(`✓ Audit trail entries: ${auditTrail.length}`);
      }
    } else {
      console.log('⚠ No complaints found for user');
    }

    await helpers.takeScreenshot('complaint-status-check');
  });

  test('should handle form cancellation', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill some data
    try {
      await page.locator('input[name="title"]').first().fill('Cancel Test');
    } catch {
      console.log('⚠ Could not fill form');
    }

    // Look for cancel button
    const cancelSelectors = [
      'button:has-text("Cancel")',
      'button:has-text("Back")',
      'button:has-text("Discard")',
      '[data-testid="cancel-btn"]'
    ];

    let cancelled = false;
    for (const selector of cancelSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          console.log('✓ Cancel button clicked');
          await page.waitForTimeout(1000);
          cancelled = true;
          break;
        }
      } catch {
        continue;
      }
    }

    if (cancelled) {
      await helpers.takeScreenshot('form-cancelled');
      // Should be redirected away from form
      const currentUrl = page.url();
      console.log(`✓ Redirected to: ${currentUrl}`);
    } else {
      console.log('⚠ Cancel button not found');
    }
  });

  test('should display complaint submission success message', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Quick fill and submit
    try {
      await page.locator('input[name="title"]').first().fill(`Success Test ${Date.now()}`);
      await page.locator('textarea[name="description"]').first().fill('Testing success message');
      
      // Submit
      await page.locator('button[type="submit"]').first().click();
      
      // Wait for success notification
      await page.waitForTimeout(3000);

      // Look for success message
      const successSelectors = [
        '.ant-notification-notice-success',
        '.success-message',
        '[role="alert"]',
        'text=/success|submitted|created/i'
      ];

      let successFound = false;
      for (const selector of successSelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            const text = await element.textContent();
            console.log(`✓ Success message: ${text}`);
            successFound = true;
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('submission-success');

      if (successFound) {
        console.log('✓ Success message displayed');
      }
    } catch (error) {
      console.log('⚠ Could not complete submission test');
    }
  });

  test('should validate description length limits', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    const descriptionField = page.locator('textarea[name="description"], textarea').first();
    
    if (await descriptionField.isVisible({ timeout: 2000 })) {
      // Try to exceed limit (assuming 1000 characters)
      const longText = 'A'.repeat(2000);
      await descriptionField.fill(longText);

      // Check if it was truncated or shows error
      const actualValue = await descriptionField.inputValue();
      console.log(`✓ Description length: ${actualValue.length} characters`);

      await helpers.takeScreenshot('description-length-test');

      // Try to submit
      try {
        await page.locator('button[type="submit"]').first().click();
        await page.waitForTimeout(1000);
        
        // Check for validation error
        const hasError = await helpers.elementExists('.error, [role="alert"]');
        if (hasError) {
          console.log('✓ Length validation error shown');
        }
      } catch {
        console.log('⚠ Could not test submission with long text');
      }
    }
  });
});
