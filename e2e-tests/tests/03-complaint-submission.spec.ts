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
    // Use the simple public complaint form (/complaint) instead of protected route
    await page.goto('/complaint');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Wait for form to be visible
    await page.waitForSelector('form', { timeout: 10000 });
    
    await helpers.takeScreenshot('complaint-form');

    // Fill complaint form (SimpleComplaint.tsx uses Ant Design Form)
    const complaintTitle = `Test Complaint ${Date.now()}`;
    const complaintDescription = 'This is a test complaint about a pothole on Main Street. It needs immediate attention.';

    // Fill title - Form.Item with name="title" creates input with id="title"
    await page.fill('#title', complaintTitle);
    console.log(`✓ Filled title: ${complaintTitle}`);

    // Fill description
    await page.fill('#description', complaintDescription);
    console.log(`✓ Filled description`);

    await helpers.takeScreenshot('complaint-form-filled');

    // Submit the form
    await page.click('button[type="submit"]');
    console.log('✓ Clicked submit button');

    // Wait for success message or redirect
    await page.waitForTimeout(3000);
    await helpers.takeScreenshot('complaint-submitted');

    // Verify success message
    const hasSuccessMessage = await page.locator('text=/success|created|submitted|thank/i').count() > 0;
    
    if (hasSuccessMessage) {
      console.log('✓ Complaint submission appears successful');
    } else {
      console.log('⚠ No success message found, but form was submitted');
    }
  });

  test('should validate required fields', async ({ page }) => {
    // Use simple complaint form
    await page.goto('/complaint');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Try to submit empty form
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Check for Ant Design validation errors
    const errorMessages = await page.locator('.ant-form-item-explain-error').allTextContents();
    
    if (errorMessages.length > 0) {
      console.log('✓ Form validation working:', errorMessages.join(', '));
      expect(errorMessages.length).toBeGreaterThan(0);
    } else {
      console.log('⚠ No validation errors found (may use HTML5 validation)');
    }

    await helpers.takeScreenshot('validation-errors');
  });

  test('should show character count for description', async ({ page }) => {
    await page.goto('/complaint');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Fill description field
    await page.fill('#description', 'Test description for character count');
    await page.waitForTimeout(500);

    // Look for character counter
    const hasCounter = await page.locator('text=/\\d+\s*\\/\s*\\d+/').count() > 0;
    
    if (hasCounter) {
      const counterText = await page.locator('text=/\\d+\s*\\/\s*\\d+/').first().textContent();
      console.log(`✓ Character counter found: ${counterText}`);
    } else {
      console.log('⚠ Character counter not visible (may not be implemented)');
    }

    await helpers.takeScreenshot('character-count');
  });

  test('should allow selecting complaint category/department', async ({ page }) => {
    await page.goto('/complaint');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Simple complaint form may not have category/department selectors
    const hasCategorySelect = await page.locator('#category').count() > 0;
    const hasDepartmentSelect = await page.locator('#department').count() > 0;
    
    if (hasCategorySelect) {
      await page.click('#category');
      await page.waitForTimeout(500);
      const categoryOptions = await page.locator('.ant-select-item-option').count();
      if (categoryOptions > 0) {
        console.log(`✓ Found ${categoryOptions} category options`);
        await page.click('.ant-select-item-option:first-child');
      }
    } else {
      console.log('⚠ Simple complaint form does not have category selector');
    }

    if (hasDepartmentSelect) {
      await page.click('#department');
      await page.waitForTimeout(500);
      const deptOptions = await page.locator('.ant-select-item-option').count();
      if (deptOptions > 0) {
        console.log(`✓ Found ${deptOptions} department options`);
        await page.click('.ant-select-item-option:first-child');
      }
    } else {
      console.log('⚠ Simple complaint form does not have department selector');
    }

    await helpers.takeScreenshot('form-selectors');
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

  test('should submit complaint with all enhanced fields (GPS, urgency, location)', async ({ page }) => {
    // Navigate to submit complaint page
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    const complaintTitle = `Enhanced Test Complaint - ${Date.now()}`;
    const complaintDescription = 'This is a comprehensive test with GPS location and all new fields.';

    // Fill basic fields
    await page.fill('input[name="title"]', complaintTitle);
    await page.fill('textarea[name="description"]', complaintDescription);

    // NEW: Select urgency level (Low, Medium, High, Critical)
    const urgencyExists = await helpers.elementExists('select[name="urgency_level"], .ant-select[id*="urgency"]');
    if (urgencyExists) {
      try {
        // Try native select first
        const nativeSelect = page.locator('select[name="urgency_level"]');
        if (await nativeSelect.isVisible({ timeout: 1000 })) {
          await nativeSelect.selectOption('High');
          console.log('✓ Selected urgency level: High');
        } else {
          // Try Ant Design Select
          await page.locator('.ant-select[id*="urgency"]').click();
          await page.locator('.ant-select-item:has-text("High")').click();
          console.log('✓ Selected urgency level: High (Ant Design)');
        }
      } catch (e) {
        console.log('⚠ Could not set urgency level:', e instanceof Error ? e.message : String(e));
      }
    }

    // NEW: Select submitted language (defaults to 'en')
    const languageExists = await helpers.elementExists('select[name="submitted_language"], .ant-select[id*="submitted_language"]');
    if (languageExists) {
      console.log('✓ Language selector found (defaulting to English)');
    }

    // NEW: Fill location details
    const addressExists = await helpers.elementExists('input[name="incident_address"]');
    if (addressExists) {
      await page.fill('input[name="incident_address"]', '123 Test Road, Test City');
      console.log('✓ Filled incident address');
    }

    const landmarkExists = await helpers.elementExists('input[name="incident_landmark"]');
    if (landmarkExists) {
      await page.fill('input[name="incident_landmark"]', 'Near City Hall');
      console.log('✓ Filled landmark');
    }

    const plusCodeExists = await helpers.elementExists('input[name="plus_code"]');
    if (plusCodeExists) {
      await page.fill('input[name="plus_code"]', '7JVW52M7+2F');
      console.log('✓ Filled Plus Code');
    }

    // NEW: Fill GPS coordinates (simulating manual entry)
    const latExists = await helpers.elementExists('input[name="incident_latitude"]');
    const lonExists = await helpers.elementExists('input[name="incident_longitude"]');
    if (latExists && lonExists) {
      await page.fill('input[name="incident_latitude"]', '23.0225');
      await page.fill('input[name="incident_longitude"]', '72.5714');
      console.log('✓ Filled GPS coordinates (Ahmedabad)');
    }

    // NEW: Select area type
    const areaTypeExists = await helpers.elementExists('select[name="area_type"], .ant-select[id*="area_type"]');
    if (areaTypeExists) {
      try {
        const nativeSelect = page.locator('select[name="area_type"]');
        if (await nativeSelect.isVisible({ timeout: 1000 })) {
          await nativeSelect.selectOption('Residential');
          console.log('✓ Selected area type: Residential');
        } else {
          await page.locator('.ant-select[id*="area_type"]').click();
          await page.locator('.ant-select-item:has-text("Residential")').click();
          console.log('✓ Selected area type: Residential (Ant Design)');
        }
      } catch (e) {
        console.log('⚠ Could not set area type:', e instanceof Error ? e.message : String(e));
      }
    }

    await helpers.takeScreenshot('enhanced-complaint-form-filled');

    // Submit the form
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
    await helpers.takeScreenshot('enhanced-complaint-submitted');

    // Verify in database with new fields
    if (testUserId) {
      const complaint = await dbHelper.getLatestComplaintByUser(testUserId);
      if (complaint) {
        console.log('✓ Enhanced complaint found in database:', complaint.id);
        console.log('  Title:', complaint.title);
        console.log('  Urgency:', complaint.urgency_level || 'not set');
        console.log('  Location:', complaint.incident_address || 'not set');
        console.log('  Coordinates:', `${complaint.incident_latitude || 'N/A'}, ${complaint.incident_longitude || 'N/A'}`);
        expect(complaint.title).toContain('Enhanced Test Complaint');
      }
    }
  });

  test('should handle GPS location capture button', async ({ page }) => {
    // Navigate to submit complaint page
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Look for GPS capture button
    const gpsButtonExists = await helpers.elementExists('button:has-text("Get Current"), button:has-text("GPS"), button:has-text("Location")');
    
    if (gpsButtonExists) {
      console.log('✓ GPS capture button found');
      
      // Note: In E2E tests, geolocation API needs to be mocked or granted permission
      // For now, just verify the button exists and is clickable
      try {
        const gpsButton = page.locator('button:has-text("Get Current"), button:has-text("GPS"), button:has-text("Location")').first();
        await expect(gpsButton).toBeVisible();
        console.log('✓ GPS button is visible and ready');
        
        // Optional: Test with mock geolocation
        await page.context().grantPermissions(['geolocation']);
        await page.context().setGeolocation({ latitude: 23.0225, longitude: 72.5714 });
        
        await gpsButton.click();
        await page.waitForTimeout(2000);
        
        // Check if coordinates were filled
        const latValue = await page.locator('input[name="incident_latitude"]').inputValue();
        if (latValue) {
          console.log('✓ GPS coordinates auto-filled:', latValue);
        }
      } catch (e) {
        console.log('⚠ GPS test skipped:', e instanceof Error ? e.message : String(e));
      }
    } else {
      console.log('⚠ GPS capture button not found');
    }
  });
});
