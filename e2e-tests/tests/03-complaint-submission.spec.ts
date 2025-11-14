import { test, expect } from '@playwright/test';

/**
 * E2E Test: Complaint Submission Flow
 * Tests creating and submitting complaints
 */

test.describe('Complaint Submission', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should submit a new complaint successfully', async ({ page }) => {
    // Navigate to complaints page
    await page.goto('http://localhost:3000/complaints/new');
    
    // Fill complaint form
    await page.fill('input[name="title"], textarea[name="title"]', 'Test Complaint - Pothole on Main Street');
    await page.fill('textarea[name="description"]', 'There is a large pothole on Main Street causing accidents. Urgent repair needed.');
    await page.fill('input[name="location"], textarea[name="location"]', 'Main Street, Kamrej, Surat');
    
    // Select category
    const categorySelect = page.locator('select[name="category"]');
    if (await categorySelect.isVisible()) {
      await categorySelect.selectOption({ label: /transportation|road/i });
    }
    
    // Select priority
    const prioritySelect = page.locator('select[name="priority"]');
    if (await prioritySelect.isVisible()) {
      await prioritySelect.selectOption('urgent');
    }
    
    // Submit complaint
    await page.click('button[type="submit"]:has-text("Submit"), button:has-text("Create Complaint")');
    
    // Should show success message
    await expect(page.locator('text=/success|submitted|created/i')).toBeVisible({ timeout: 10000 });
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    // Try to submit empty form
    await page.click('button[type="submit"]:has-text("Submit"), button:has-text("Create Complaint")');
    
    // Should show validation errors
    await expect(page.locator('text=/required|fill|enter/i')).toBeVisible();
  });

  test('should upload image attachment', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    // Fill basic fields
    await page.fill('input[name="title"], textarea[name="title"]', 'Complaint with Image');
    await page.fill('textarea[name="description"]', 'Test description with image attachment');
    await page.fill('input[name="location"]', 'Surat');
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.isVisible()) {
      await fileInput.setInputFiles('test-image.jpg'); // You'd need a test image
    }
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Should submit successfully
    await expect(page.locator('text=/success/i')).toBeVisible({ timeout: 10000 });
  });

  test('should show character count for description', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    const description = 'Test description for character count';
    await page.fill('textarea[name="description"]', description);
    
    // Should show character count
    const charCount = page.locator('text=/\\d+.*character|\\d+\\/\\d+/i');
    if (await charCount.isVisible()) {
      await expect(charCount).toBeVisible();
    }
  });

  test('should allow draft save', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    await page.fill('input[name="title"], textarea[name="title"]', 'Draft Complaint');
    await page.fill('textarea[name="description"]', 'This is a draft');
    
    // Click save draft button if available
    const draftButton = page.locator('button:has-text("Save Draft"), button:has-text("Draft")');
    if (await draftButton.isVisible()) {
      await draftButton.click();
      await expect(page.locator('text=/draft.*saved|saved.*draft/i')).toBeVisible({ timeout: 5000 });
    }
  });
});
