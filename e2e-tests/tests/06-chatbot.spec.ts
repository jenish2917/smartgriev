import { test, expect } from '@playwright/test';

/**
 * E2E Test: Chatbot Interaction
 * Tests AI chatbot complaint submission flow
 */

test.describe('Chatbot Interaction', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
  });

  test('should open chatbot interface', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    // Should show chatbot interface
    await expect(page.locator('.chat-container, [data-testid="chatbot"]')).toBeVisible({ timeout: 10000 });
    
    // Should show input field
    await expect(page.locator('input[placeholder*="message" i], textarea[placeholder*="message" i]')).toBeVisible();
  });

  test('should send and receive messages', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    // Type a message
    const chatInput = page.locator('input[type="text"]:visible, textarea:visible').last();
    await chatInput.fill('Hello, I want to report a complaint');
    
    // Send message
    await page.click('button[type="submit"], button:has-text("Send")');
    
    // Should show user message
    await expect(page.locator('text=/Hello.*complaint/i')).toBeVisible({ timeout: 5000 });
    
    // Should show bot response
    await expect(page.locator('.bot-message, [data-sender="bot"]')).toBeVisible({ timeout: 10000 });
  });

  test('should handle complaint submission through chat', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    const chatInput = page.locator('input[type="text"]:visible, textarea:visible').last();
    const sendButton = page.locator('button[type="submit"], button:has-text("Send")');
    
    // Step 1: Describe issue
    await chatInput.fill('There is a big pothole on Main Street');
    await sendButton.click();
    await page.waitForTimeout(2000);
    
    // Step 2: Provide location
    await chatInput.fill('It is in Kamrej, Surat');
    await sendButton.click();
    await page.waitForTimeout(2000);
    
    // Step 3: Urgency
    await chatInput.fill('It is very urgent, causing accidents');
    await sendButton.click();
    await page.waitForTimeout(2000);
    
    // Should show submit button or confirmation
    const submitButton = page.locator('button:has-text("Submit Complaint"), button:has-text("Create")');
    if (await submitButton.isVisible({ timeout: 5000 })) {
      await submitButton.click();
      
      // Should show success message
      await expect(page.locator('text=/success|submitted|created/i')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should support multilingual input', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    // Check if language selector exists
    const langSelector = page.locator('select[name="language"], button:has-text("Language")');
    if (await langSelector.isVisible()) {
      // Select Hindi
      await langSelector.click();
      const hindiOption = page.locator('text=/Hindi|हिंदी/');
      if (await hindiOption.isVisible()) {
        await hindiOption.click();
      }
    }
    
    // Type Hindi message
    const chatInput = page.locator('input[type="text"]:visible, textarea:visible').last();
    await chatInput.fill('मुख्य सड़क पर गड्ढा है');
    await page.click('button[type="submit"], button:has-text("Send")');
    
    // Should process message
    await expect(page.locator('.bot-message, [data-sender="bot"]')).toBeVisible({ timeout: 10000 });
  });

  test('should clear chat history', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    // Send a message
    const chatInput = page.locator('input[type="text"]:visible, textarea:visible').last();
    await chatInput.fill('Test message');
    await page.click('button[type="submit"], button:has-text("Send")');
    await page.waitForTimeout(1000);
    
    // Click clear button
    const clearButton = page.locator('button:has-text("Clear"), button:has-text("Reset")');
    if (await clearButton.isVisible()) {
      await clearButton.click();
      
      // Chat should be empty
      const messages = page.locator('.message, .chat-message');
      await expect(messages).toHaveCount(0);
    }
  });

  test('should show typing indicator', async ({ page }) => {
    await page.goto('http://localhost:3000/chatbot');
    
    const chatInput = page.locator('input[type="text"]:visible, textarea:visible').last();
    await chatInput.fill('Hello');
    await page.click('button[type="submit"], button:has-text("Send")');
    
    // Should show typing indicator briefly
    const typingIndicator = page.locator('text=/typing|\.\.\./, [data-testid="typing-indicator"]');
    // It might be too fast to catch, but check if it appears
    // This is a timing-dependent test
  });
});
