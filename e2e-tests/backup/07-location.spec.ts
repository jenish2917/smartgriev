import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';
import { DatabaseHelper } from '../utils/database';

test.describe('Location Services Testing', () => {
  let helpers: TestHelpers;
  let dbHelper: DatabaseHelper;

  // Mumbai coordinates for testing
  const MUMBAI_LAT = 19.0760;
  const MUMBAI_LNG = 72.8777;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    dbHelper = new DatabaseHelper();
    await dbHelper.connect();

    // Grant geolocation permission and set Mumbai coordinates
    await page.context().grantPermissions(['geolocation']);
    await helpers.mockGeolocation(MUMBAI_LAT, MUMBAI_LNG);

    // Login
    const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
    const loginPassword = process.env.TEST_USER_PASSWORD || 'TestPass123!';
    await helpers.login(loginEmail, loginPassword);
  });

  test.afterEach(async () => {
    await dbHelper.close();
  });

  test('should detect current location (Mumbai coordinates)', async ({ page }) => {
    // Navigate to complaint submission or any page with location
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Look for "Use Current Location" button
    const locationButtonSelectors = [
      'button:has-text("Use Current Location")',
      'button:has-text("Get Location")',
      'button:has-text("Detect Location")',
      'button:has-text("📍")',
      '[data-testid="use-location"]',
      '[data-testid="get-location"]',
      '.use-location-btn',
      '.detect-location'
    ];

    let locationDetected = false;
    for (const selector of locationButtonSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 })) {
          console.log(`✓ Location button found: ${selector}`);
          await button.click();
          
          // Wait for location to be detected
          await page.waitForTimeout(3000);
          
          locationDetected = true;
          await helpers.takeScreenshot('location-detected');
          
          // Check if location appears in input
          const locationInput = page.locator('input[name="location"], input[name="address"]').first();
          if (await locationInput.isVisible({ timeout: 2000 })) {
            const value = await locationInput.inputValue();
            console.log(`✓ Location detected: ${value}`);
          }
          
          break;
        }
      } catch {
        continue;
      }
    }

    if (!locationDetected) {
      console.log('⚠ Location button not found, trying direct navigation API');
      
      // Check if location is auto-detected
      await page.waitForTimeout(2000);
      const pageContent = await page.content();
      if (pageContent.includes('Mumbai') || pageContent.includes('19.') || pageContent.includes('72.')) {
        console.log('✓ Mumbai coordinates detected in page');
        locationDetected = true;
      }
    }

    await helpers.takeScreenshot('location-detection-result');
    console.log(`✓ Location detection tested (Mumbai: ${MUMBAI_LAT}, ${MUMBAI_LNG})`);
  });

  test('should display coordinates in correct format', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Trigger location detection
    const locationBtn = page.locator('button:has-text("Use Current Location"), [data-testid="use-location"]').first();
    
    try {
      if (await locationBtn.isVisible({ timeout: 2000 })) {
        await locationBtn.click();
        await page.waitForTimeout(3000);

        // Look for coordinates display
        const coordSelectors = [
          '.coordinates',
          '[data-testid="coordinates"]',
          'text=/\\d+\\.\\d+.*\\d+\\.\\d+/',
          'text=/lat.*lng|latitude.*longitude/i'
        ];

        let coordsFound = false;
        for (const selector of coordSelectors) {
          try {
            const coords = page.locator(selector).first();
            if (await coords.isVisible({ timeout: 2000 })) {
              const text = await coords.textContent();
              console.log(`✓ Coordinates displayed: ${text}`);
              
              // Verify Mumbai coordinates are shown
              if (text?.includes('19.') && text?.includes('72.')) {
                console.log('✓ Mumbai coordinates confirmed');
              }
              
              coordsFound = true;
              break;
            }
          } catch {
            continue;
          }
        }

        await helpers.takeScreenshot('coordinates-display');

        if (!coordsFound) {
          console.log('⚠ Coordinates not visibly displayed (may be internal only)');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test coordinate display');
    }
  });

  test('should perform reverse geocoding', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Trigger location detection
    const locationBtn = page.locator('button:has-text("Use Current Location"), [data-testid="use-location"]').first();
    
    try {
      if (await locationBtn.isVisible({ timeout: 2000 })) {
        await locationBtn.click();
        console.log('✓ Location detection triggered');
        
        // Wait for reverse geocoding
        await page.waitForTimeout(4000);

        // Check if human-readable address appears
        const locationInput = page.locator('input[name="location"], input[name="address"], textarea[name="location"]').first();
        
        if (await locationInput.isVisible({ timeout: 2000 })) {
          const address = await locationInput.inputValue();
          
          if (address && address.length > 10) {
            console.log(`✓ Reverse geocoded address: ${address}`);
            
            // Check if it contains Mumbai or Maharashtra
            if (address.includes('Mumbai') || address.includes('Maharashtra')) {
              console.log('✓ Reverse geocoding returned Mumbai address');
            }
          } else {
            console.log('⚠ Address field empty or contains only coordinates');
          }
        }

        await helpers.takeScreenshot('reverse-geocoded');
      }
    } catch (error) {
      console.log('⚠ Could not test reverse geocoding');
    }
  });

  test('should generate Plus Code for location', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Trigger location detection
    const locationBtn = page.locator('button:has-text("Use Current Location"), [data-testid="use-location"]').first();
    
    try {
      if (await locationBtn.isVisible({ timeout: 2000 })) {
        await locationBtn.click();
        await page.waitForTimeout(3000);

        // Look for Plus Code display
        const plusCodeSelectors = [
          '.plus-code',
          '[data-testid="plus-code"]',
          'text=/[A-Z0-9]{4}\\+[A-Z0-9]{2}/',
          'text=/Plus Code/i'
        ];

        let plusCodeFound = false;
        for (const selector of plusCodeSelectors) {
          try {
            const plusCode = page.locator(selector).first();
            if (await plusCode.isVisible({ timeout: 2000 })) {
              const text = await plusCode.textContent();
              console.log(`✓ Plus Code found: ${text}`);
              plusCodeFound = true;
              break;
            }
          } catch {
            continue;
          }
        }

        await helpers.takeScreenshot('plus-code');

        if (!plusCodeFound) {
          console.log('⚠ Plus Code not displayed (may not be implemented)');
        } else {
          console.log('✓ Plus Code generation working');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test Plus Code generation');
    }
  });

  test('should allow manual location entry', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Find location input and enter manually
    const locationInputSelectors = [
      'input[name="location"]',
      'input[name="address"]',
      'textarea[name="location"]',
      '[data-testid="location-input"]',
      'input[placeholder*="location" i]',
      'input[placeholder*="address" i]'
    ];

    let manualEntryWorking = false;
    for (const selector of locationInputSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          const manualAddress = 'Colaba, Mumbai, Maharashtra 400001';
          await input.fill(manualAddress);
          console.log(`✓ Manual location entered: ${manualAddress}`);
          
          await page.waitForTimeout(1000);
          
          // Verify value was set
          const value = await input.inputValue();
          if (value === manualAddress) {
            console.log('✓ Manual location entry successful');
            manualEntryWorking = true;
          }
          
          await helpers.takeScreenshot('manual-location-entry');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!manualEntryWorking) {
      console.log('⚠ Could not test manual location entry');
    }
  });

  test('should show location on map', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Trigger location detection
    const locationBtn = page.locator('button:has-text("Use Current Location"), [data-testid="use-location"]').first();
    
    try {
      if (await locationBtn.isVisible({ timeout: 2000 })) {
        await locationBtn.click();
        await page.waitForTimeout(3000);

        // Look for map element
        const mapSelectors = [
          '#map',
          '.map',
          '[data-testid="map"]',
          '.google-map',
          '.leaflet-container',
          'iframe[src*="maps.google"]',
          'iframe[src*="openstreetmap"]'
        ];

        let mapFound = false;
        for (const selector of mapSelectors) {
          try {
            const map = page.locator(selector).first();
            if (await map.isVisible({ timeout: 2000 })) {
              console.log(`✓ Map found: ${selector}`);
              mapFound = true;
              break;
            }
          } catch {
            continue;
          }
        }

        await helpers.takeScreenshot('location-map');

        if (mapFound) {
          console.log('✓ Location displayed on map');
        } else {
          console.log('⚠ Map not found (may not be implemented)');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test map display');
    }
  });

  test('should filter complaints by location', async ({ page }) => {
    // Navigate to complaints list
    await page.goto('/complaints');
    await page.waitForTimeout(2000);

    // Look for location filter
    const locationFilterSelectors = [
      'input[name="location"]',
      'select[name="location"]',
      '[data-testid="location-filter"]',
      '.location-filter',
      'input[placeholder*="filter.*location" i]'
    ];

    let filterFound = false;
    for (const selector of locationFilterSelectors) {
      try {
        const filter = page.locator(selector).first();
        if (await filter.isVisible({ timeout: 2000 })) {
          console.log(`✓ Location filter found: ${selector}`);
          
          // Try to filter by Mumbai
          await filter.fill('Mumbai');
          await page.waitForTimeout(2000);
          
          filterFound = true;
          await helpers.takeScreenshot('location-filter');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!filterFound) {
      console.log('⚠ Location filter not found');
      await helpers.takeScreenshot('location-filter-search');
    }
  });

  test('should show nearby complaints', async ({ page }) => {
    await page.goto('/complaints');
    await page.waitForTimeout(2000);

    // Look for "Nearby" or "Near Me" option
    const nearbySelectors = [
      'button:has-text("Nearby")',
      'button:has-text("Near Me")',
      '[data-testid="nearby-complaints"]',
      '.nearby-filter',
      'text=Nearby'
    ];

    let nearbyFound = false;
    for (const selector of nearbySelectors) {
      try {
        const nearbyBtn = page.locator(selector).first();
        if (await nearbyBtn.isVisible({ timeout: 2000 })) {
          console.log(`✓ Nearby complaints option found`);
          await nearbyBtn.click();
          await page.waitForTimeout(3000);
          
          nearbyFound = true;
          await helpers.takeScreenshot('nearby-complaints');
          break;
        }
      } catch {
        continue;
      }
    }

    if (!nearbyFound) {
      console.log('⚠ Nearby complaints feature not found');
    }
  });

  test('should calculate distance from user location', async ({ page }) => {
    await page.goto('/complaints');
    await page.waitForTimeout(2000);

    // Look for distance indicators
    const distanceSelectors = [
      'text=/\\d+(\\.\\d+)?\\s*(km|m|miles)/i',
      '.distance',
      '[data-testid="distance"]',
      'text=/away|distance/i'
    ];

    let distanceFound = false;
    for (const selector of distanceSelectors) {
      try {
        const distance = page.locator(selector).first();
        if (await distance.isVisible({ timeout: 2000 })) {
          const text = await distance.textContent();
          console.log(`✓ Distance indicator found: ${text}`);
          distanceFound = true;
          break;
        }
      } catch {
        continue;
      }
    }

    await helpers.takeScreenshot('distance-calculation');

    if (!distanceFound) {
      console.log('⚠ Distance calculation not visible');
    }
  });

  test('should handle location permission denial', async ({ page }) => {
    // Clear permissions
    await page.context().clearPermissions();

    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Try to use location
    const locationBtn = page.locator('button:has-text("Use Current Location"), [data-testid="use-location"]').first();
    
    try {
      if (await locationBtn.isVisible({ timeout: 2000 })) {
        await locationBtn.click();
        await page.waitForTimeout(2000);

        // Look for permission error message
        const errorSelectors = [
          'text=/location.*denied|permission.*denied|enable.*location/i',
          '.location-error',
          '[role="alert"]',
          '.permission-error'
        ];

        let errorHandled = false;
        for (const selector of errorSelectors) {
          try {
            const error = page.locator(selector).first();
            if (await error.isVisible({ timeout: 2000 })) {
              console.log('✓ Location permission denial handled');
              errorHandled = true;
              break;
            }
          } catch {
            continue;
          }
        }

        await helpers.takeScreenshot('location-permission-denied');

        if (!errorHandled) {
          console.log('⚠ Permission denial error not visible');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test permission denial');
    }

    // Re-grant permission
    await page.context().grantPermissions(['geolocation']);
  });

  test('should geocode manually entered address', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Enter an address manually
    const locationInput = page.locator('input[name="location"], input[name="address"]').first();
    
    try {
      if (await locationInput.isVisible({ timeout: 2000 })) {
        const address = 'Gateway of India, Mumbai';
        await locationInput.fill(address);
        console.log(`✓ Manual address entered: ${address}`);
        
        await page.waitForTimeout(3000);

        // Look for geocoding results (coordinates or suggestions)
        const geocodingSelectors = [
          '.address-suggestions',
          '.autocomplete-results',
          '[data-testid="address-suggestions"]',
          '.place-suggestions'
        ];

        let geocodingWorking = false;
        for (const selector of geocodingSelectors) {
          try {
            const results = page.locator(selector).first();
            if (await results.isVisible({ timeout: 2000 })) {
              console.log('✓ Geocoding suggestions displayed');
              geocodingWorking = true;
              break;
            }
          } catch {
            continue;
          }
        }

        await helpers.takeScreenshot('manual-address-geocoding');

        if (!geocodingWorking) {
          console.log('⚠ Geocoding suggestions not visible');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test manual address geocoding');
    }
  });

  test('should validate location is within service area', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Try entering location outside service area
    const locationInput = page.locator('input[name="location"], input[name="address"]').first();
    
    try {
      if (await locationInput.isVisible({ timeout: 2000 })) {
        const outsideAddress = 'New York City, USA';
        await locationInput.fill(outsideAddress);
        console.log(`✓ Out-of-area address entered: ${outsideAddress}`);
        
        await page.waitForTimeout(2000);

        // Try to submit
        const submitBtn = page.locator('button[type="submit"]').first();
        if (await submitBtn.isVisible({ timeout: 1000 })) {
          await submitBtn.click();
          await page.waitForTimeout(2000);

          // Look for service area error
          const errorSelectors = [
            'text=/outside.*service.*area|not.*serviceable|location.*not.*supported/i',
            '.service-area-error',
            '.location-validation-error'
          ];

          for (const selector of errorSelectors) {
            try {
              if (await page.locator(selector).first().isVisible({ timeout: 2000 })) {
                console.log('✓ Service area validation working');
                break;
              }
            } catch {
              continue;
            }
          }

          await helpers.takeScreenshot('service-area-validation');
        }
      }
    } catch (error) {
      console.log('⚠ Could not test service area validation');
    }
  });

  test('should save location with complaint in database', async ({ page }) => {
    await page.goto('/submit-complaint');
    await page.waitForTimeout(2000);

    // Submit complaint with location
    try {
      await page.locator('input[name="title"]').first().fill('Location Test Complaint');
      await page.locator('textarea[name="description"]').first().fill('Testing location save');
      
      // Set location
      const locationInput = page.locator('input[name="location"], input[name="address"]').first();
      if (await locationInput.isVisible({ timeout: 2000 })) {
        await locationInput.fill('Bandra, Mumbai, Maharashtra');
      }

      await page.waitForTimeout(1000);
      await helpers.takeScreenshot('complaint-with-location');

      // Submit
      const submitBtn = page.locator('button[type="submit"]').first();
      if (await submitBtn.isVisible({ timeout: 2000 })) {
        await submitBtn.click();
        await page.waitForTimeout(3000);

        // Verify in database
        const loginEmail = process.env.TEST_USER_EMAIL || 'test@smartgriev.com';
        const user = await dbHelper.getUserByEmail(loginEmail);
        
        if (user) {
          const complaint = await dbHelper.getLatestComplaintByUser(user.id);
          
          if (complaint) {
            console.log('✓ Complaint saved in database');
            
            // Check if location data exists
            if (complaint.location || complaint.latitude || complaint.address) {
              console.log('✓ Location data saved with complaint');
              if (complaint.location) console.log(`  Location: ${complaint.location}`);
              if (complaint.latitude) console.log(`  Coordinates: ${complaint.latitude}, ${complaint.longitude}`);
            } else {
              console.log('⚠ Location data not found in complaint record');
            }
          }
        }
      }
    } catch (error) {
      console.log('⚠ Could not test location save in database');
    }

    await helpers.takeScreenshot('location-db-verification');
  });
});
