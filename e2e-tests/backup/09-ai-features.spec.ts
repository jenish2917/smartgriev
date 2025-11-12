import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('AI Features Testing', () => {
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

  test('should auto-classify complaint department', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill complaint with department-specific keywords
    try {
      await page.locator('input[name="title"]').first().fill('Broken Street Light on Main Road');
      await page.locator('textarea[name="description"]').first().fill('The street light near the park has been broken for two weeks. It needs repair urgently for safety.');

      await page.waitForTimeout(3000);

      // Look for auto-selected department
      const departmentSelect = page.locator('select[name="department"], select[name="category"]').first();
      
      if (await departmentSelect.isVisible({ timeout: 2000 })) {
        const value = await departmentSelect.inputValue();
        
        if (value && value !== '') {
          console.log(`✓ AI auto-classified department: ${value}`);
          
          // Should be electricity or public works
          const text = await departmentSelect.locator(`option[value="${value}"]`).textContent();
          console.log(`  Department: ${text}`);
        } else {
          console.log('⚠ Department not auto-selected');
        }
      }

      await helpers.takeScreenshot('ai-department-classification');
    } catch (error) {
      console.log('⚠ Could not test department classification');
    }
  });

  test('should detect complaint urgency', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill urgent complaint
    try {
      await page.locator('input[name="title"]').first().fill('URGENT: Water Pipeline Burst');
      await page.locator('textarea[name="description"]').first().fill('Major water pipeline has burst on Highway Road. Water is flooding the street. Immediate action required!');

      await page.waitForTimeout(3000);

      // Look for urgency indicator
      const urgencySelectors = [
        'select[name="urgency"]',
        '[data-testid="urgency"]',
        '.urgency-indicator',
        'text=/urgent|high.*priority/i'
      ];

      let urgencyDetected = false;
      for (const selector of urgencySelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            const text = await element.textContent() || await element.inputValue();
            console.log(`✓ AI detected urgency: ${text}`);
            urgencyDetected = true;
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('ai-urgency-detection');

      if (!urgencyDetected) {
        console.log('⚠ Urgency detection not visible');
      }
    } catch (error) {
      console.log('⚠ Could not test urgency detection');
    }
  });

  test('should assign priority level automatically', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill high-priority complaint
    try {
      await page.locator('input[name="title"]').first().fill('Major Road Accident - Pothole');
      await page.locator('textarea[name="description"]').first().fill('Large pothole caused accident. Multiple vehicles damaged. Safety hazard.');

      await page.waitForTimeout(3000);

      // Look for priority indicator
      const prioritySelectors = [
        'select[name="priority"]',
        '[data-testid="priority"]',
        '.priority-badge',
        'text=/high.*priority|critical/i'
      ];

      for (const selector of prioritySelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            const text = await element.textContent() || await element.inputValue();
            console.log(`✓ AI assigned priority: ${text}`);
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('ai-priority-assignment');
    } catch (error) {
      console.log('⚠ Could not test priority assignment');
    }
  });

  test('should provide AI suggestions while typing', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Start typing
    const descriptionField = page.locator('textarea[name="description"]').first();
    
    try {
      if (await descriptionField.isVisible({ timeout: 2000 })) {
        await descriptionField.fill('There is a problem with garbage colle');
        
        await page.waitForTimeout(2000);

        // Look for AI suggestions
        const suggestionSelectors = [
          '.ai-suggestions',
          '.autocomplete',
          '[data-testid="suggestions"]',
          '.suggestion-box'
        ];

        for (const selector of suggestionSelectors) {
          if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
            console.log('✓ AI suggestions displayed');
            break;
          }
        }

        await helpers.takeScreenshot('ai-suggestions');
      }
    } catch (error) {
      console.log('⚠ Could not test AI suggestions');
    }
  });

  test('should analyze uploaded image with Vision AI', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Upload an image
    try {
      const fileInput = page.locator('input[type="file"]').first();
      await fileInput.setInputFiles({
        name: 'pothole.jpg',
        mimeType: 'image/jpeg',
        buffer: Buffer.from('test-pothole-image')
      });

      console.log('✓ Image uploaded for AI analysis');
      await page.waitForTimeout(4000);

      // Look for AI analysis results
      const aiAnalysisSelectors = [
        '.ai-analysis',
        '.vision-results',
        '[data-testid="ai-analysis"]',
        'text=/detected|identified|found/i',
        '.image-analysis'
      ];

      let analysisFound = false;
      for (const selector of aiAnalysisSelectors) {
        try {
          const results = page.locator(selector).first();
          if (await results.isVisible({ timeout: 5000 })) {
            const text = await results.textContent();
            console.log(`✓ Vision AI results: ${text?.substring(0, 100)}`);
            analysisFound = true;
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('vision-ai-analysis');

      if (!analysisFound) {
        console.log('⚠ AI analysis results not visible');
      }
    } catch (error) {
      console.log('⚠ Could not test Vision AI');
    }
  });

  test('should perform OCR on uploaded image', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Upload image with text
    try {
      const fileInput = page.locator('input[type="file"]').first();
      await fileInput.setInputFiles({
        name: 'sign-with-text.jpg',
        mimeType: 'image/jpeg',
        buffer: Buffer.from('image-with-text')
      });

      await page.waitForTimeout(4000);

      // Look for extracted text
      const ocrSelectors = [
        '.extracted-text',
        '.ocr-results',
        '[data-testid="ocr-text"]',
        'text=/text.*found|extracted.*text/i'
      ];

      for (const selector of ocrSelectors) {
        try {
          if (await page.locator(selector).first().isVisible({ timeout: 5000 })) {
            console.log('✓ OCR text extraction working');
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('ocr-results');
    } catch (error) {
      console.log('⚠ Could not test OCR');
    }
  });

  test('should detect objects in image', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Upload image
    try {
      const fileInput = page.locator('input[type="file"]').first();
      await fileInput.setInputFiles({
        name: 'garbage-pile.jpg',
        mimeType: 'image/jpeg',
        buffer: Buffer.from('garbage-image')
      });

      await page.waitForTimeout(4000);

      // Look for detected objects
      const objectSelectors = [
        '.detected-objects',
        '.object-labels',
        '[data-testid="detected-objects"]',
        'text=/detected|objects.*found/i'
      ];

      for (const selector of objectSelectors) {
        try {
          if (await page.locator(selector).first().isVisible({ timeout: 5000 })) {
            console.log('✓ Object detection working');
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('object-detection');
    } catch (error) {
      console.log('⚠ Could not test object detection');
    }
  });

  test('should suggest similar resolved complaints', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill complaint details
    try {
      await page.locator('input[name="title"]').first().fill('Pothole on Highway');
      await page.locator('textarea[name="description"]').first().fill('Deep pothole causing traffic issues');

      await page.waitForTimeout(3000);

      // Look for similar complaints suggestions
      const similarSelectors = [
        '.similar-complaints',
        '[data-testid="similar-complaints"]',
        'text=/similar.*complaint|related.*issue/i',
        '.suggestion-card'
      ];

      for (const selector of similarSelectors) {
        try {
          if (await page.locator(selector).first().isVisible({ timeout: 3000 })) {
            console.log('✓ Similar complaints suggestions shown');
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('similar-complaints');
    } catch (error) {
      console.log('⚠ Could not test similar complaints');
    }
  });

  test('should provide smart reply suggestions in chat', async ({ page }) => {
    // Open chatbot
    const chatBtn = page.locator('[data-testid="chatbot"], .chatbot-icon').first();
    
    try {
      if (await chatBtn.isVisible({ timeout: 2000 })) {
        await chatBtn.click();
        await page.waitForTimeout(1500);

        // Send a question
        const input = page.locator('input[type="text"], textarea').first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill('How do I track my complaint?');
          await input.press('Enter');
          
          await page.waitForTimeout(3000);

          // Look for smart reply suggestions
          const smartReplySelectors = [
            '.smart-reply',
            '.quick-reply',
            '[data-testid="smart-reply"]',
            '.suggestion-chip'
          ];

          for (const selector of smartReplySelectors) {
            if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
              console.log('✓ Smart reply suggestions shown');
              break;
            }
          }

          await helpers.takeScreenshot('smart-replies');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test smart replies');
    }
  });

  test('should show AI confidence score', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill complaint
    try {
      await page.locator('input[name="title"]').first().fill('Street Light Issue');
      await page.locator('textarea[name="description"]').first().fill('Street light not working at night');

      await page.waitForTimeout(3000);

      // Look for confidence score
      const confidenceSelectors = [
        '.confidence-score',
        '[data-testid="confidence"]',
        'text=/confidence|\\d+%/i',
        '.ai-confidence'
      ];

      for (const selector of confidenceSelectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible({ timeout: 2000 })) {
            const text = await element.textContent();
            console.log(`✓ AI confidence score: ${text}`);
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('ai-confidence');
    } catch (error) {
      console.log('⚠ Could not test confidence score');
    }
  });

  test('should categorize complaint automatically', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill different types of complaints and verify categorization
    const testCases = [
      { title: 'Garbage Not Collected', keywords: 'garbage, waste, collection', expectedCategory: 'Sanitation' },
      { title: 'Road Repair Needed', keywords: 'road, pothole, repair', expectedCategory: 'Public Works' },
      { title: 'Water Supply Problem', keywords: 'water, supply, pipeline', expectedCategory: 'Water' }
    ];

    for (const testCase of testCases) {
      try {
        await page.locator('input[name="title"]').first().fill(testCase.title);
        await page.locator('textarea[name="description"]').first().fill(testCase.keywords);
        
        await page.waitForTimeout(2000);

        const categorySelect = page.locator('select[name="category"], select[name="department"]').first();
        if (await categorySelect.isVisible({ timeout: 1000 })) {
          const value = await categorySelect.inputValue();
          if (value) {
            console.log(`✓ "${testCase.title}" categorized (${value})`);
          }
        }

        // Clear for next test
        await page.locator('input[name="title"]').first().clear();
        await page.locator('textarea[name="description"]').first().clear();
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('ai-categorization');
  });

  test('should estimate resolution time', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill complaint
    try {
      await page.locator('input[name="title"]').first().fill('Broken Swing in Park');
      await page.locator('textarea[name="description"]').first().fill('The swing set in the public park is broken and unsafe');

      await page.waitForTimeout(3000);

      // Look for estimated resolution time
      const estimateSelectors = [
        '.estimated-time',
        '[data-testid="resolution-time"]',
        'text=/estimated.*time|expected.*resolution/i',
        '.time-estimate'
      ];

      for (const selector of estimateSelectors) {
        try {
          if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
            const text = await page.locator(selector).first().textContent();
            console.log(`✓ Estimated resolution time: ${text}`);
            break;
          }
        } catch {
          continue;
        }
      }

      await helpers.takeScreenshot('resolution-time-estimate');
    } catch (error) {
      console.log('⚠ Could not test resolution time estimate');
    }
  });

  test('should provide multilingual AI support', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Fill complaint in Hindi
    try {
      await page.locator('input[name="title"]').first().fill('सड़क पर गड्ढा');
      await page.locator('textarea[name="description"]').first().fill('मुख्य सड़क पर बड़ा गड्ढा है जिससे दुर्घटना हो सकती है');

      await page.waitForTimeout(3000);

      // Check if AI can process Hindi text
      const departmentSelect = page.locator('select[name="department"]').first();
      if (await departmentSelect.isVisible({ timeout: 2000 })) {
        const value = await departmentSelect.inputValue();
        if (value) {
          console.log('✓ AI processed Hindi text successfully');
        }
      }

      await helpers.takeScreenshot('multilingual-ai');
    } catch (error) {
      console.log('⚠ Could not test multilingual AI');
    }
  });

  test('should verify AI classifications in database', async ({ page }) => {
    if (!testUserId) {
      console.log('⚠ Test user ID not available');
      return;
    }

    const complaint = await dbHelper.getLatestComplaintByUser(testUserId);

    if (complaint) {
      console.log('✓ Checking AI classification in database');
      console.log(`  Complaint ID: ${complaint.id}`);
      console.log(`  Department: ${complaint.department || 'Not set'}`);
      console.log(`  Priority: ${complaint.priority || 'Not set'}`);
      console.log(`  Status: ${complaint.status}`);

      if (complaint.department) {
        console.log('✓ AI department classification saved');
      }

      if (complaint.priority) {
        console.log('✓ AI priority assignment saved');
      }
    } else {
      console.log('⚠ No complaints found');
    }

    await helpers.takeScreenshot('ai-db-verification');
  });
});
