# E2E Testing - Quick Start Guide

## Prerequisites Check ✅

Before running tests, ensure:
- [ ] Frontend is running on http://localhost:5173
- [ ] Backend is running on http://localhost:8000
- [ ] PostgreSQL database is accessible
- [ ] Node.js 18+ is installed

## 5-Minute Setup

### Step 1: Configure Environment (1 minute)
```powershell
cd e2e-tests
notepad .env
```

Update these values in `.env`:
```env
POSTGRES_PASSWORD=your_actual_password
TEST_USER_EMAIL=your_test_email@example.com
TEST_USER_PASSWORD=YourTestPassword123!
```

### Step 2: Run Your First Test (2 minutes)

**Option A: Watch Tests Run Visually**
```powershell
npm run test:headed
```
This will open browser windows and you'll see tests executing in real-time!

**Option B: Interactive UI Mode**
```powershell
npm run test:ui
```
This opens a UI where you can:
- Pick specific tests to run
- Pause execution
- Step through tests
- Inspect elements
- See real-time results

**Option C: Run Silently (Headless)**
```powershell
npm test
```

### Step 3: View Results (1 minute)
```powershell
npm run report
```

This opens an HTML report showing:
- ✅ Tests passed
- ❌ Tests failed
- 📸 Screenshots
- 🎥 Videos
- ⏱️ Execution time

## What Tests Are Available?

### Authentication Tests (✅ READY)
```powershell
npm run test:auth
```
Tests include:
- User signup with OTP verification
- Login/logout
- Password validation
- Email validation
- Session management

### Dashboard Tests (⏳ COMING SOON)
```powershell
npm run test:dashboard
```

### Complaint Tests (⏳ COMING SOON)
```powershell
npm run test:complaint      # Text complaints
npm run test:multimodal     # Image/audio/video complaints
```

### Chatbot Tests (⏳ COMING SOON)
```powershell
npm run test:chatbot        # Text chat
npm run test:voice          # Voice input
```

### More Tests (⏳ COMING SOON)
```powershell
npm run test:location       # GPS, geocoding
npm run test:realtime       # Notifications, WebSocket
npm run test:ai             # AI classification
npm run test:admin          # Admin functions
```

## Real-Time Database Verification

When tests run, you'll see logs like:
```
✓ Database connected successfully
✓ User created in database: 123
✓ OTP retrieved from database: 654321
✓ Complaint found: Test Complaint Title
```

This confirms data is being saved to your database in real-time!

## Location Testing

Tests automatically use Mumbai coordinates:
- Latitude: 19.0760°N
- Longitude: 72.8777°E

Your location-based features will work as if you're in Mumbai!

## Troubleshooting

### "Cannot connect to database"
```powershell
# Check your .env file has correct credentials
notepad .env

# Test PostgreSQL connection manually
psql -h localhost -U postgres -d smartgriev
```

### "Tests timing out"
```powershell
# Make sure frontend and backend are running
# Frontend: http://localhost:5173
# Backend: http://localhost:8000

# Check they're accessible in browser
```

### "Browser not found"
```powershell
# Reinstall browsers
npx playwright install
```

## Test Modes Explained

### 1. Headed Mode (--headed)
- **Best for**: Watching tests run, debugging
- **Command**: `npm run test:headed`
- **You see**: Real browser windows, forms filling, clicks happening
- **Speed**: Slower (visual feedback)

### 2. UI Mode (--ui)
- **Best for**: Interactive testing, debugging specific tests
- **Command**: `npm run test:ui`
- **You see**: Playwright UI with controls to pause/step/inspect
- **Speed**: You control it

### 3. Headless Mode (default)
- **Best for**: CI/CD, fast execution
- **Command**: `npm test`
- **You see**: Console logs only
- **Speed**: Fastest

### 4. Debug Mode (--debug)
- **Best for**: Investigating failures
- **Command**: `npm run test:debug`
- **You see**: Playwright Inspector with step-by-step controls
- **Speed**: You control it

## Tips for Success

### 1. Start Small
```powershell
# Run just one test file
npm run test:auth
```

### 2. Watch First Time
```powershell
# See what's happening
npm run test:headed
```

### 3. Check Reports
```powershell
# After tests finish
npm run report
```

### 4. Clean Up When Done
```powershell
# Remove generated reports
npm run cleanup

# Or delete entire test directory
cd ..
Remove-Item -Recurse -Force e2e-tests
```

## Next Steps

1. **Run authentication tests** to verify setup:
   ```powershell
   npm run test:auth
   ```

2. **Check if they pass** - view the report:
   ```powershell
   npm run report
   ```

3. **Create more tests** - use 01-authentication.spec.ts as template

4. **Run full suite** when ready:
   ```powershell
   npm run test:all
   ```

## Visual Testing Demo

Want to see tests in action? Run:
```powershell
npm run test:ui
```

Then click any test and watch it execute step-by-step! 🎬

## Need Help?

- **Setup issues**: Check SETUP_COMPLETE.md
- **Writing tests**: Check README.md
- **Test failures**: Check reports/html/index.html
- **Database issues**: Check .env configuration

## Quick Reference Card

| Command | What It Does |
|---------|-------------|
| `npm test` | Run all tests (headless) |
| `npm run test:headed` | Run with visible browser |
| `npm run test:ui` | Interactive UI mode |
| `npm run test:auth` | Run authentication tests |
| `npm run report` | View HTML report |
| `npm run cleanup` | Delete reports |

---

**Ready to test?** Run `npm run test:auth` and watch the magic! ✨
