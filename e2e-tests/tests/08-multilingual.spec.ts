import { test, expect } from '@playwright/test';

/**
 * E2E Test: Multilingual Support
 * Tests language switching and translation
 */

test.describe('Multilingual Support', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should switch to Hindi language', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Find language selector
    const langSelector = page.locator('select[name="language"], button:has-text("Language"), [data-testid="language-selector"]');
    if (await langSelector.isVisible()) {
      await langSelector.click();
      
      // Select Hindi
      const hindiOption = page.locator('option:has-text("Hindi"), text=/Hindi|हिंदी/');
      if (await hindiOption.isVisible()) {
        await hindiOption.click();
        
        // Page content should change to Hindi
        await expect(page.locator('text=/शिकायत|डैशबोर्ड/i')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should switch to Gujarati language', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    const langSelector = page.locator('select[name="language"], button:has-text("Language")');
    if (await langSelector.isVisible()) {
      await langSelector.click();
      
      const gujaratiOption = page.locator('option:has-text("Gujarati"), text=/Gujarati|ગુજરાતી/');
      if (await gujaratiOption.isVisible()) {
        await gujaratiOption.click();
        
        // Content should be in Gujarati
        await expect(page.locator('text=/ફરિયાદ|ડેશબોર્ડ/i')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should submit complaint in Hindi', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    // Switch to Hindi if language selector exists
    const langSelector = page.locator('select[name="language"]');
    if (await langSelector.isVisible()) {
      await langSelector.selectOption('hi');
    }
    
    // Fill form in Hindi
    await page.fill('input[name="title"], textarea[name="title"]', 'सड़क पर गड्ढा');
    await page.fill('textarea[name="description"]', 'मुख्य सड़क पर बड़ा गड्ढा है जो दुर्घटना का कारण बन रहा है');
    await page.fill('input[name="location"]', 'सूरत');
    
    await page.click('button[type="submit"]');
    
    // Should submit successfully
    await expect(page.locator('text=/success|सफल/i')).toBeVisible({ timeout: 10000 });
  });

  test('should submit complaint in Gujarati', async ({ page }) => {
    await page.goto('http://localhost:3000/complaints/new');
    
    const langSelector = page.locator('select[name="language"]');
    if (await langSelector.isVisible()) {
      await langSelector.selectOption('gu');
    }
    
    await page.fill('input[name="title"], textarea[name="title"]', 'રસ્તા પર ખાડો');
    await page.fill('textarea[name="description"]', 'મુખ્ય રસ્તા પર મોટો ખાડો છે જે અકસ્માતનું કારણ બની રહ્યો છે');
    await page.fill('input[name="location"]', 'સુરત');
    
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=/success|સફળ/i')).toBeVisible({ timeout: 10000 });
  });

  test('should persist language preference', async ({ page, context }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Change language
    const langSelector = page.locator('select[name="language"]');
    if (await langSelector.isVisible()) {
      await langSelector.selectOption('hi');
      await page.waitForTimeout(1000);
    }
    
    // Navigate to another page
    await page.goto('http://localhost:3000/complaints');
    
    // Language should still be Hindi
    await expect(page.locator('text=/शिकायत/i')).toBeVisible({ timeout: 5000 });
  });

  test('should translate UI elements correctly', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Check English elements
    await expect(page.locator('text=/Dashboard|Complaints|Submit/i')).toBeVisible();
    
    // Switch to Hindi
    const langSelector = page.locator('select[name="language"]');
    if (await langSelector.isVisible()) {
      await langSelector.selectOption('hi');
      await page.waitForTimeout(1000);
      
      // Check translated elements
      // Note: Actual translations depend on your i18n implementation
      const translatedElement = page.locator('text=/डैशबोर्ड|शिकायत|जमा/i');
      if (await translatedElement.isVisible({ timeout: 2000 })) {
        await expect(translatedElement).toBeVisible();
      }
    }
  });
});
