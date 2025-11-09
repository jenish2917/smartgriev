# SmartGriev E2E Testing Suite

Comprehensive end-to-end testing suite for SmartGriev using Playwright with real-time database verification.

## Features

- ✅ **Visual Testing**: Watch tests run in real browsers
- ✅ **Real-time Database Verification**: See database changes during tests
- ✅ **Location Detection**: Tests use configured geolocation
- ✅ **Multi-browser Testing**: Chrome, Firefox, Safari, Edge, Mobile
- ✅ **Comprehensive Coverage**: 20 test scenarios covering all features
- ✅ **Video Recording**: Automatic video capture on failures
- ✅ **Screenshots**: Capture screenshots at key moments
- ✅ **Detailed Reports**: HTML, JSON, and JUnit reports
- ✅ **Easy Cleanup**: Delete all test files in one click

## Prerequisites

- Node.js 18+ installed
- Frontend running on http://localhost:5173
- Backend running on http://localhost:8000
- PostgreSQL database accessible

## Installation

1. **Install dependencies:**
   ```bash
   cd e2e-tests
   npm install
   ```

2. **Install Playwright browsers:**
   ```bash
   npx playwright install
   ```

3. **Configure environment:**
   ```bash
   # Copy example environment file
   copy .env.example .env
   
   # Edit .env with your database credentials
   notepad .env
   ```

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Tests with Browser Visible (Headed Mode)
```bash
npm run test:headed
```

### Run Tests in Interactive UI Mode
```bash
npm run test:ui
```

### Run Tests in Debug Mode
```bash
npm run test:debug
```

### Run Specific Test Categories

**Authentication Tests:**
```bash
npm run test:auth
```

**Dashboard Tests:**
```bash
npm run test:dashboard
```

**Complaint Submission Tests:**
```bash
npm run test:complaint
npm run test:multimodal
```

**Chatbot Tests:**
```bash
npm run test:chatbot
npm run test:voice
```

**Location Tests:**
```bash
npm run test:location
```

**Real-time Features:**
```bash
npm run test:realtime
```

**AI Features:**
```bash
npm run test:ai
```

**Admin Functions:**
```bash
npm run test:admin
```

**Run All Tests with Full Reporting:**
```bash
npm run test:all
```

## Viewing Reports

### View HTML Report
```bash
npm run report
```

Reports are generated in the `reports/` directory:
- **HTML Report**: `reports/html/index.html`
- **JSON Report**: `reports/test-results.json`
- **JUnit Report**: `reports/junit.xml`
- **Screenshots**: `reports/screenshots/`
- **Videos**: `reports/videos/`

## Test Structure

```
e2e-tests/
├── tests/                    # Test specification files
│   ├── 01-authentication.spec.ts
│   ├── 02-dashboard.spec.ts
│   ├── 03-complaint-submission.spec.ts
│   ├── 04-multimodal-complaint.spec.ts
│   ├── 05-chatbot.spec.ts
│   ├── 06-voice-input.spec.ts
│   ├── 07-location.spec.ts
│   ├── 08-realtime.spec.ts
│   ├── 09-ai-features.spec.ts
│   └── 10-admin.spec.ts
├── fixtures/                 # Test data files
│   ├── sample-image.jpg
│   ├── sample-audio.mp3
│   └── sample-video.mp4
├── utils/                    # Helper utilities
│   ├── database.ts          # Database verification
│   └── helpers.ts           # Test helpers
├── reports/                  # Test results
├── playwright.config.ts      # Playwright configuration
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
└── .env                     # Environment variables
```

## Test Coverage

### 1. User Authentication Flow
- ✅ User registration with OTP verification
- ✅ Email/mobile login
- ✅ Password validation
- ✅ Session management
- ✅ Logout functionality

### 2. Dashboard & Navigation
- ✅ Dashboard statistics
- ✅ Language switching (13 languages)
- ✅ Navigation menu
- ✅ User profile
- ✅ Responsive design

### 3. Complaint Submission
- ✅ Text-only complaints
- ✅ Image upload complaints
- ✅ Audio recording complaints
- ✅ Video upload complaints
- ✅ Form validation

### 4. Chatbot
- ✅ Text conversations (English, Hindi, Marathi)
- ✅ Voice input (12 languages)
- ✅ Context awareness
- ✅ Multi-turn conversations
- ✅ Complaint creation from chat

### 5. Location Services
- ✅ GPS location detection
- ✅ Reverse geocoding
- ✅ Plus Code generation
- ✅ Manual location entry
- ✅ Location-based filtering

### 6. Real-time Features
- ✅ WebSocket connections
- ✅ Live notifications
- ✅ Status updates
- ✅ Real-time chat

### 7. AI Features
- ✅ Department classification
- ✅ Urgency detection
- ✅ Priority assignment
- ✅ Vision AI image analysis
- ✅ OCR text extraction

### 8. Analytics & Reports
- ✅ Dashboard statistics
- ✅ Complaint trends
- ✅ Department metrics
- ✅ User activity reports

### 9. Admin/Officer Functions
- ✅ Complaint assignment
- ✅ Status updates
- ✅ Officer dashboard
- ✅ Bulk operations

### 10. Error Handling
- ✅ Form validation errors
- ✅ Network failures
- ✅ API errors
- ✅ Invalid inputs

### 11. Performance Testing
- ✅ Page load times
- ✅ API response times
- ✅ Concurrent user handling

### 12. Cross-browser Testing
- ✅ Chrome (Desktop)
- ✅ Firefox (Desktop)
- ✅ Safari (Desktop)
- ✅ Edge (Desktop)
- ✅ Mobile Chrome
- ✅ Mobile Safari

### 13. Accessibility Testing
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ ARIA labels
- ✅ Color contrast
- ✅ Focus management

## Real-time Database Verification

Tests include real-time database verification to ensure data consistency:

```typescript
// Example: Verify user creation
const dbHelper = new DatabaseHelper();
await dbHelper.connect();

// Get user from database
const user = await dbHelper.getUserByEmail('test@example.com');
expect(user).toBeDefined();
expect(user.email).toBe('test@example.com');

// Get latest complaint
const complaint = await dbHelper.getLatestComplaintByUser(user.id);
expect(complaint.title).toBe('Test Complaint');

await dbHelper.close();
```

## Location Testing

Tests use Mumbai coordinates by default (19.0760°N, 72.8777°E):

```typescript
// Geolocation is automatically configured
// Tests can verify location-based features work correctly
```

## Debugging Tests

### Debug Single Test
```bash
npx playwright test tests/01-authentication.spec.ts --debug
```

### Run with Trace Viewer
```bash
npx playwright test --trace on
npx playwright show-trace trace.zip
```

### Take Screenshots During Test
```typescript
await page.screenshot({ path: 'screenshot.png' });
```

## Cleanup

### Remove All Test Files
```bash
npm run cleanup
```

Or manually delete the entire `e2e-tests/` directory.

## Troubleshooting

### Tests Failing to Connect to Backend
- Ensure backend is running: `http://localhost:8000`
- Check backend logs for errors
- Verify database connection

### Tests Failing to Connect to Frontend
- Ensure frontend is running: `http://localhost:5173`
- Check frontend console for errors
- Try accessing in browser manually

### Database Connection Errors
- Check `.env` file has correct database credentials
- Verify PostgreSQL is running
- Test database connection manually

### Browser Installation Issues
```bash
npx playwright install --with-deps
```

### Tests Timing Out
- Increase timeout in `playwright.config.ts`
- Check network speed
- Ensure servers are responsive

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: cd e2e-tests && npm install

- name: Install Playwright browsers
  run: cd e2e-tests && npx playwright install --with-deps

- name: Run E2E tests
  run: cd e2e-tests && npm run test:all
  
- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: e2e-tests/reports/
```

## Best Practices

1. **Run tests sequentially** for database consistency
2. **Use unique test emails** to avoid conflicts
3. **Clean up test data** after tests complete
4. **Take screenshots** on failures for debugging
5. **Use meaningful test descriptions**
6. **Group related tests** together
7. **Mock external services** when possible
8. **Test happy and sad paths**

## Support

For issues or questions:
- Check test reports in `reports/html/index.html`
- Review screenshots in `reports/screenshots/`
- Watch videos in `reports/videos/`
- Check console logs in test output

## License

Part of SmartGriev project.
