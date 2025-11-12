import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

/**
 * SmartGriev E2E Test Configuration
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  
  /* Run tests in files in parallel */
  fullyParallel: true, // Enable full parallelization
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Run tests in parallel - 4 workers is safer for database operations */
  workers: process.env.CI ? 2 : 4, // 4 workers locally, 2 on CI (safer for DB)
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'reports/html', open: 'never' }],
    ['json', { outputFile: 'reports/test-results.json' }],
    ['list'],
    ['junit', { outputFile: 'reports/junit-results.xml' }]
  ],
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    /* API base URL */
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video on failure */
    video: 'retain-on-failure',
    
    /* Geolocation permission for location tests */
    geolocation: { longitude: 72.8777, latitude: 19.0760 }, // Mumbai coordinates
    permissions: ['geolocation', 'notifications', 'microphone'],
    
    /* Browser context options */
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Firefox-specific baseURL using 127.0.0.1 instead of localhost
        baseURL: 'http://127.0.0.1:3000',
        // Firefox doesn't support microphone permission in Playwright
        // Remove microphone from permissions for Firefox only
        permissions: ['geolocation', 'notifications'],
        // Relax Firefox security for testing
        launchOptions: {
          firefoxUserPrefs: {
            // Disable strict file URI policy
            'security.fileuri.strict_origin_policy': false,
            // Allow mixed content (HTTP on HTTPS)
            'security.mixed_content.block_active_content': false,
            // Allow insecure WebSocket from HTTPS
            'network.websocket.allowInsecureFromHTTPS': true,
            // Disable HTTPS-first mode
            'dom.security.https_first': false,
            // Disable CSP for testing (allows all connections)
            'security.csp.enable': false,
            // Disable DNS prefetching issues
            'network.dns.disablePrefetch': false,
            // Set localhost resolution
            'network.proxy.type': 0,
          }
        }
      },
    },

    // WEBKIT/SAFARI DISABLED - Microphone permission not supported
    // Webkit doesn't support 'microphone' in permissions API
    // This causes all tests to fail with: "Unknown permission: microphone"
    // User decision: Don't fix Safari/Webkit tests
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    // MOBILE SAFARI DISABLED - Same reason as Desktop Safari
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
  ],

  /* Run your local dev server before starting the tests */
  // Commented out - servers already running manually
  // webServer: process.env.CI ? undefined : [
  //   {
  //     command: 'cd ../frontend && npm run dev',
  //     url: 'http://localhost:5173',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120 * 1000,
  //   },
  //   {
  //     command: 'cd ../backend && python manage.py runserver',
  //     url: 'http://localhost:8000/api/health/',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120 * 1000,
  //   },
  // ],
  
  /* Global timeout */
  timeout: 60 * 1000,
  expect: {
    timeout: 10 * 1000,
  },
});
