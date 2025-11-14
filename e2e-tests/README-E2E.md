# E2E Test Suite - SmartGriev

Comprehensive end-to-end tests using Playwright covering all features.

## Test Modules

### Core Authentication (Tests 1-2)
- **01-registration.spec.ts** - User registration flow
  - ✓ Successful registration
  - ✓ Duplicate email validation
  - ✓ Password strength validation
  - ✓ Password match validation
  - ✓ Phone number validation

- **02-login.spec.ts** - Login and session management
  - ✓ Valid credentials login
  - ✓ Invalid credentials error
  - ✓ Empty fields validation
  - ✓ Password visibility toggle
  - ✓ Session persistence
  - ✓ Logout functionality

### Complaint Management (Tests 3-5)
- **03-complaint-submission.spec.ts** - Creating complaints
  - ✓ Submit new complaint successfully
  - ✓ Required fields validation
  - ✓ Image attachment upload
  - ✓ Character count display
  - ✓ Draft save functionality

- **04-admin-panel.spec.ts** - Admin interface
  - ✓ Admin login
  - ✓ Department management
  - ✓ User management
  - ✓ Complaint moderation

- **05-complaints-list.spec.ts** - Viewing and managing
  - ✓ Display complaints list
  - ✓ Filter by status
  - ✓ Search by title
  - ✓ Pagination
  - ✓ View details
  - ✓ Sort by date

### AI Features (Tests 6-7)
- **06-chatbot.spec.ts** - AI chatbot interaction
  - ✓ Open chatbot interface
  - ✓ Send/receive messages
  - ✓ Complaint submission through chat
  - ✓ Multilingual input support
  - ✓ Clear chat history
  - ✓ Typing indicator

- **07-department-classification.spec.ts** - Auto classification
  - ✓ Road → Road & Transportation
  - ✓ Water → Water Supply & Sewerage
  - ✓ Garbage → Sanitation & Cleanliness
  - ✓ Electricity → Electricity Board
  - ✓ Traffic → Traffic Police

### Internationalization (Test 8)
- **08-multilingual.spec.ts** - Language support
  - ✓ Switch to Hindi
  - ✓ Switch to Gujarati
  - ✓ Submit complaint in Hindi
  - ✓ Submit complaint in Gujarati
  - ✓ Language preference persistence
  - ✓ UI element translation

### System Features (Tests 9-10)
- **09-notifications.spec.ts** - Notification system
  - ✓ Show notification icon
  - ✓ Notification count badge
  - ✓ Open notifications panel
  - ✓ Display notification list
  - ✓ Mark as read
  - ✓ Mark all as read
  - ✓ Delete notification
  - ✓ Filter by type
  - ✓ Navigate to related complaint

- **10-dashboard-analytics.spec.ts** - Dashboard and analytics
  - ✓ Display statistics
  - ✓ Status chart
  - ✓ Department chart
  - ✓ Recent complaints
  - ✓ Date range filter
  - ✓ Navigate to analytics
  - ✓ Trend charts
  - ✓ Export data
  - ✓ Response time metrics
  - ✓ User activity stats

## Running Tests

### Run all tests
```bash
cd e2e-tests
npm test
```

### Run specific test file
```bash
npx playwright test tests/01-registration.spec.ts
```

### Run tests in headed mode (see browser)
```bash
npx playwright test --headed
```

### Run tests in specific browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Run tests with UI mode
```bash
npx playwright test --ui
```

### Debug specific test
```bash
npx playwright test --debug tests/06-chatbot.spec.ts
```

### View test report
```bash
npx playwright show-report
```

## Test Coverage

- **Total Test Files**: 10
- **Total Test Cases**: ~70+
- **Coverage Areas**:
  - Authentication & Authorization
  - CRUD Operations
  - AI/ML Features
  - Internationalization
  - Real-time Features
  - Data Visualization
  - File Upload
  - Notifications
  - Search & Filter
  - Pagination

## Prerequisites

1. Backend server running on `localhost:8000`
2. Frontend server running on `localhost:3000`
3. Database populated with test data
4. Admin user: `admin` / `admin123`

## CI/CD Integration

Tests can be run in CI/CD pipelines:

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: cd e2e-tests && npm ci
      - name: Install Playwright
        run: cd e2e-tests && npx playwright install --with-deps
      - name: Run tests
        run: cd e2e-tests && npm test
      - name: Upload report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: e2e-tests/playwright-report/
```

## Best Practices

1. **Isolation**: Each test is independent
2. **Setup/Teardown**: Use `beforeEach` for common setup
3. **Assertions**: Use explicit expectations
4. **Timeouts**: Set appropriate timeouts for async operations
5. **Selectors**: Use semantic selectors (text, role, label)
6. **Wait Strategies**: Use `waitForSelector` instead of fixed delays
7. **Data-driven**: Use test data constants
8. **Screenshots**: Automatic on failure
9. **Videos**: Recorded for failed tests
10. **Parallel Execution**: Tests run in parallel by default

## Troubleshooting

### Tests failing due to timeout
- Increase timeout in playwright.config.ts
- Check if servers are running
- Verify network connectivity

### Element not found errors
- Check if selectors match current UI
- Add explicit waits
- Verify element is visible and enabled

### Flaky tests
- Add proper wait conditions
- Avoid fixed timeouts
- Use network idle states
- Check for race conditions

## Maintenance

- Update selectors when UI changes
- Add tests for new features
- Remove obsolete tests
- Keep test data fresh
- Review and update assertions
